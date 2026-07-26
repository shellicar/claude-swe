#!/usr/bin/env python3
"""Corpus-driven usage stats for the AST-execution scoped-grammar feasibility question.

Walks every runs/**/*.traj.json, pulls the raw free-text bash Claude actually wrote
(the `command`/`script` string fields — not the structured JSON-argv arms, which
never contain shell operators to count), and tallies which constructs appear.
"""
import json
import glob
import re
import collections

ROOT = "/Users/stephen/repos/shellicar/claude-swe/runs"

FREE_TEXT_KEYS = ("command", "script")

total_calls = 0
bash_text_calls = 0
per_arm_counts = collections.Counter()

# feature regexes, applied per top-level command string
FEATURES = {
    "pipe |":            re.compile(r"(?<!\|)\|(?!\|)"),
    "and &&":            re.compile(r"&&"),
    "or ||":              re.compile(r"\|\|"),
    "semicolon ;":       re.compile(r";"),
    "background &":      re.compile(r"(?<![&<>0-9])&(?!&)"),
    "redirect >":        re.compile(r"(?<!>)>(?!>|&)"),
    "redirect >>":       re.compile(r">>"),
    "redirect <":         re.compile(r"(?<!<)<(?!<|&)"),
    "redirect <<heredoc": re.compile(r"<<[-~]?\s*['\"]?\w"),
    "redirect <<<":      re.compile(r"<<<"),
    "fd dup >&/<& or 2>&1": re.compile(r"\d*[<>]&\d*"),
    "cmd subst $(...)":  re.compile(r"\$\("),
    "cmd subst backtick": re.compile(r"`"),
    "arithmetic $((":    re.compile(r"\$\(\("),
    "arithmetic (( ))":  re.compile(r"(?<!\$)\(\("),
    "param expand ${":   re.compile(r"\$\{"),
    "subshell ( )":      re.compile(r"(?<![$(])\((?!\()"),
    "for":               re.compile(r"\bfor\b"),
    "while":             re.compile(r"\bwhile\b"),
    "if":                re.compile(r"\bif\b"),
    "case":              re.compile(r"\bcase\b"),
    "until":             re.compile(r"\buntil\b"),
    "function def":      re.compile(r"\bfunction\b|\)\s*\{"),
    "brace group { }":   re.compile(r"\{[^}]*;\s*\}"),
    "negation !":        re.compile(r"(?:^|\s)!\s"),
    "double bracket [[": re.compile(r"\[\["),
    "process subst <(":  re.compile(r"<\("),
    "process subst >(":  re.compile(r">\("),
    "here-string": re.compile(r"<<<"),
    "variable assignment": re.compile(r"^\s*[A-Za-z_][A-Za-z0-9_]*="),
}

feature_hits = collections.Counter()
nest_depth_counter = collections.Counter()


def max_dollarparen_depth(s):
    depth = 0
    maxd = 0
    i = 0
    n = len(s)
    while i < n:
        if s[i] == "$" and i + 1 < n and s[i + 1] == "(":
            depth += 1
            maxd = max(maxd, depth)
            i += 2
            continue
        if s[i] == ")" and depth > 0:
            depth -= 1
            i += 1
            continue
        i += 1
    return maxd


commands = []

for f in glob.glob(f"{ROOT}/**/*.traj.json", recursive=True):
    arm = f.split("/runs/")[1].split("/")[0]
    try:
        d = json.load(open(f))
    except Exception:
        continue
    for m in d.get("messages", []):
        extra = m.get("extra")
        if not extra:
            continue
        choices = extra.get("response", {}).get("choices")
        if not choices:
            continue
        for ch in choices:
            tcs = ch.get("message", {}).get("tool_calls") or []
            for tc in tcs:
                total_calls += 1
                fn = tc.get("function", {})
                args_raw = fn.get("arguments", "")
                try:
                    args = json.loads(args_raw)
                except Exception:
                    continue
                if not isinstance(args, dict):
                    continue
                for key in FREE_TEXT_KEYS:
                    if key in args and isinstance(args[key], str):
                        text = args[key]
                        if arm == "exec-arm-6" and text.startswith("run "):
                            text = text[4:]
                        bash_text_calls += 1
                        per_arm_counts[arm] += 1
                        commands.append(text)
                        break

for text in commands:
    for name, rx in FEATURES.items():
        if rx.search(text):
            feature_hits[name] += 1
    d = max_dollarparen_depth(text)
    nest_depth_counter[d] += 1

print(f"total tool calls: {total_calls}")
print(f"free-text bash calls (command/script string): {bash_text_calls}")
print()
print("per-arm free-text call counts:")
for arm, c in sorted(per_arm_counts.items(), key=lambda kv: -kv[1]):
    print(f"  {arm}: {c}")
print()
print(f"feature prevalence (of {bash_text_calls} free-text calls):")
for name, c in sorted(feature_hits.items(), key=lambda kv: -kv[1]):
    print(f"  {name}: {c} ({100*c/bash_text_calls:.1f}%)")
print()
print("$(...) nesting depth distribution (0 = none):")
for depth, c in sorted(nest_depth_counter.items()):
    print(f"  depth {depth}: {c} ({100*c/bash_text_calls:.1f}%)")

# scoped-subset coverage estimate: simple commands + connections (&&,||,|,;,&) +
# common redirects (>,>>,<,<<<,fd-dup) + subshell/group + deferred-opaque $()/``/${}/(())
# EXCLUDED from the scoped subset: for/while/if/case/until/function/[[ ]]/process-subst
EXCLUDED_FEATURES = [
    "for", "while", "if", "case", "until", "function def",
    "double bracket [[", "process subst <(", "process subst >(",
]

excluded_count = 0
for text in commands:
    hit = False
    for name in EXCLUDED_FEATURES:
        if FEATURES[name].search(text):
            hit = True
            break
    if hit:
        excluded_count += 1

covered = bash_text_calls - excluded_count
print()
print(f"scoped-subset (simple cmds + connections + redirects + subshells + deferred substitution,")
print(f"no compound control-flow keywords or [[ ]] or process substitution):")
print(f"  covered: {covered} / {bash_text_calls} ({100*covered/bash_text_calls:.1f}%)")
print(f"  outside scope: {excluded_count} / {bash_text_calls} ({100*excluded_count/bash_text_calls:.1f}%)")

# Executor-side inventory: state-mutating builtins as argv[0] of any simple
# command segment. These need first-class walker logic no matter how the AST
# is sourced (a child process can't mutate its parent's cwd/env/variables), so
# this is a distinct feasibility question from grammar coverage above.
STATE_MUTATING_BUILTINS = {
    "cd", "export", "read", "local", "declare", "typeset", "set", "shift",
    "trap", "source", ".", "exit", "return", "unset", "alias", "pushd", "popd",
    "readonly", "eval",
}
ASSIGNMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
# split on connectors the same way the grammar does: &&, ||, |, ;, &, newline
SPLIT_RE = re.compile(r"&&|\|\||\||;|(?<![&<>0-9])&(?!&)|\n")

builtin_hits = collections.Counter()
builtin_call_count = 0  # calls containing >=1 state-mutating builtin anywhere
assignment_hits = 0

for text in commands:
    segments = [s.strip() for s in SPLIT_RE.split(text) if s.strip()]
    hit_this_call = False
    for seg in segments:
        # strip leading VAR=val VAR2=val2 ... prefix assignments before argv[0]
        toks = seg.split()
        i = 0
        saw_assignment = False
        while i < len(toks) and ASSIGNMENT_RE.match(toks[i]):
            saw_assignment = True
            i += 1
        if saw_assignment:
            assignment_hits += 1
            hit_this_call = True
        if i < len(toks):
            argv0 = toks[i].strip("()")
            if argv0 in STATE_MUTATING_BUILTINS:
                builtin_hits[argv0] += 1
                hit_this_call = True
    if hit_this_call:
        builtin_call_count += 1

print()
print(f"state-mutating builtins as argv[0] (of {bash_text_calls} free-text calls):")
print(f"  bare variable assignment (VAR=val prefix): {assignment_hits} ({100*assignment_hits/bash_text_calls:.1f}%)")
for name, c in sorted(builtin_hits.items(), key=lambda kv: -kv[1]):
    print(f"  {name}: {c} ({100*c/bash_text_calls:.1f}%)")
print(f"  ANY state-mutating construct (assignment or builtin), per call: {builtin_call_count} ({100*builtin_call_count/bash_text_calls:.1f}%)")
