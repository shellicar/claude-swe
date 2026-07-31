#!/usr/bin/env python3
"""Itemise upstream commits by whether they can touch a measurement.

"It might break things" is not an assessment. Every commit is classified by
the files it changes:

  MEASUREMENT  the agent loop, model wrappers, environments, cost accounting,
               or the swebench runner — anything that can change a patch, a
               verdict, or a cost figure
  RUNNER       other entrypoints and configs this rig does not use
  INERT        docs, CI, tests, packaging

    python scripts/upstream_impact.py vendor/mini-swe-agent
"""
import re
import subprocess
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "vendor/mini-swe-agent"

MEASUREMENT = re.compile(
    r"^src/minisweagent/(agents|models|environments)/"
    r"|^src/minisweagent/run/benchmarks/swebench\.py"
    r"|^swebench/harness/(utils|constants|log_parsers|test_spec|docker_build|"
    r"run_evaluation|grading)"
)
RUNNER = re.compile(
    r"^src/minisweagent/run/|^src/minisweagent/config/|^swebench/(collect|inference|versioning)/"
)

SEP = "@@@"
out = subprocess.run(
    ["git", "-C", ROOT, "log", "--reverse", f"--format={SEP}%h {SEP}%s", "--name-only",
     "HEAD..upstream/main"],
    capture_output=True, text=True, check=True,
).stdout

buckets = {"MEASUREMENT": [], "RUNNER": [], "INERT": []}
sha = subject = None
files: list[str] = []


def flush():
    if not sha:
        return
    hits = [f for f in files if MEASUREMENT.search(f)]
    if hits:
        buckets["MEASUREMENT"].append((sha, subject, hits))
    elif any(RUNNER.search(f) for f in files):
        buckets["RUNNER"].append((sha, subject, files))
    else:
        buckets["INERT"].append((sha, subject, files))


for line in out.splitlines():
    if line.startswith(SEP):
        flush()
        sha, subject = line[len(SEP):].split(f" {SEP}", 1)
        files = []
    elif line.strip():
        files.append(line.strip())
flush()

for kind in ("MEASUREMENT", "RUNNER", "INERT"):
    rows = buckets[kind]
    print(f"\n=== {kind}: {len(rows)} commit(s) ===")
    for sha, subject, files in rows:
        print(f"  {sha} {subject[:96]}")
        if kind == "MEASUREMENT":
            for f in files:
                print(f"        {f}")
