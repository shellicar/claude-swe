#!/bin/sh
# Fable 5 repeat run (2026-07-02): "has Fable 5 changed since the first run?"
# Same experiment as the main Fable 5 leg — same frozen instance sets, same
# swebench-local.yaml + thinking-adaptive.yaml, 3 workers — run again under a
# new name so it sits alongside the original instead of being skipped.
#
# One deliberate difference from the first run: effort is pinned to `high`
# EXPLICITLY. The API default is `high` (and effort=high is identical to
# omitting it), so behaviour matches the first run today — but pinning removes
# the risk that a shifted server-side default would silently confound a
# comparison whose entire point is detecting a model change. The first run
# didn't pin it because it wasn't trying to detect a change; this one is.
#
# Output: runs/main/fable-5-high-2026-07-02/<set>/   Console log: logs/fable-5-high-2026-07-02.log
# Mark it with ./eval-experiment.sh (scans runs/*/*/*/, picks this leg up).
#
# Interrupt-safe and resumable: rerun after any crash/cancel and finished
# instances are skipped. Ctrl-C kills the leg and its children — no orphaned
# runs spending in the background (learned the hard way, 2026-06-10).
set -e
cd "$(dirname "$0")"
mkdir -p logs

MODEL="anthropic/claude-fable-5"
OUT="runs/main/fable-5-high-2026-07-02"
filter() { printf '^(%s)$' "$(tr '\n' '|' < "instances-$1.txt" | sed 's/|$//')"; }

run() {
    .venv/bin/mini-extra swebench --subset verified --split test --filter "$(filter standard)" -m "$MODEL" -c swebench-local.yaml -c thinking-adaptive.yaml -c "model.model_kwargs.output_config.effort=high" -o "$OUT/standard" -w 3
    .venv/bin/mini-extra swebench --subset verified --split test --filter "$(filter hard)" -m "$MODEL" -c swebench-local.yaml -c thinking-adaptive.yaml -c "model.model_kwargs.output_config.effort=high" -o "$OUT/hard" -w 3
}

run > "logs/fable-5-high-2026-07-02.log" 2>&1 &
PID=$!
trap 'echo "Stopping..."; pkill -P "$PID" 2>/dev/null; kill "$PID" 2>/dev/null; wait; exit 130' INT TERM

echo "Fable 5 repeat running (PID $PID, log: logs/fable-5-high-2026-07-02.log)"
wait "$PID"
echo "Run complete. Mark it with ./eval-experiment.sh"
