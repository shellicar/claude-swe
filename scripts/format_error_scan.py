#!/usr/bin/env python3
"""Have format errors actually happened in our runs, and were they resolved?

Upstream's max_consecutive_format_errors (default 3) only changes an outcome
where a run ALREADY produced that many in a row. That is a fact about the
trajectories on disk.

A format error is marked in the trajectory itself — extra.interrupt_type ==
"FormatError" — so there is no need to guess at message text. `n_actions`
separates the two kinds, which matter differently:

    n_actions == 0   the reply carried NO tool call (prose, or truncated
                     before the call was emitted)
    n_actions  > 0   a tool call WAS made but was rejected: unknown tool, or
                     arguments that did not parse

Both raise FormatError, so both would count toward a cap.
"""
import collections
import glob
import json

CAP = 3

verdicts = {}
for rep in glob.glob("evals/*.json"):
    try:
        d = json.load(open(rep))
    except Exception:
        continue
    name = rep.split("/")[-1]
    run_id = name[name.index(".") + 1:-len(".json")]
    for iid in d.get("resolved_ids", []):
        verdicts[(run_id, iid)] = "RESOLVED"
    for iid in d.get("unresolved_ids", []):
        verdicts.setdefault((run_id, iid), "no")


def verdict_for(tf):
    parts = tf.split("/")
    run_id = "_".join(parts[:-2])
    return verdicts.get((run_id, parts[-2]), "unmarked")


rows = []
kinds = collections.Counter()
for tf in glob.glob("runs/**/*.traj.json", recursive=True):
    try:
        t = json.load(open(tf))
    except Exception:
        continue
    streak = best = total = 0
    no_call = bad_call = 0
    for m in t.get("messages", []):
        extra = m.get("extra") or {}
        if extra.get("interrupt_type") == "FormatError":
            streak += 1
            total += 1
            best = max(best, streak)
            if extra.get("n_actions"):
                bad_call += 1
            else:
                no_call += 1
        elif m.get("role") == "user":
            streak = 0
    if total:
        kinds["no tool call"] += no_call
        kinds["malformed tool call"] += bad_call
        rows.append((best, total, no_call, bad_call, tf, t["info"]))

print(f"trajectories with at least one format error: {len(rows)}")
print(f"  format errors by kind: {dict(kinds)}")
print(f"\ntrajectories that bounced more than {CAP} times in a row:")
hit = [r for r in rows if r[0] > CAP]
for best, total, no_call, bad_call, tf, info in sorted(hit, reverse=True):
    st = info["model_stats"]
    print(f"  streak={best:>4} (no-call {no_call}, malformed {bad_call})"
          f" calls={st['api_calls']:>4} cost=${st['instance_cost']:>7.3f}"
          f" exit={info.get('exit_status'):<14} verdict={verdict_for(tf):<9}"
          f" {'/'.join(tf.split('/')[1:4])}")
print(f"\n{len(hit)} trajectories, ${sum(r[5]['model_stats']['instance_cost'] for r in hit):.2f} spent,"
      f" {sum(1 for r in hit if verdict_for(r[4]) == 'RESOLVED')} of them resolved")
