#!/bin/sh
# THE experiment: 6 models x 2 sets (standard, hard), one pass, one invocation.
# Completed legs are skipped on rerun, so adding a model only runs the new one.
# Models run in parallel (each has its own API rate-limit bucket); within a
# model, standard runs then hard. 3 workers per model = 12 containers peak.
#
# Interrupt-safe and resumable: rerun this script after any crash/cancel and
# every leg picks up where it left off, skipping finished instances.
#
# Output: runs/main/<model>/<set>/   Console logs: logs/<model>.log
set -e
cd "$(dirname "$0")"
mkdir -p logs

filter() { printf '^(%s)$' "$(tr '\n' '|' < "instances-$1.txt" | sed 's/|$//')"; }

run_model() {
    MODEL="$1"
    SHORT=$(basename "$MODEL" | sed 's/^claude-//')
    # Adaptive thinking for every model except Haiku 4.5, which rejects it
    # ("adaptive thinking is not supported on this model", proven 2026-06-10).
    THINKING="-c thinking-adaptive.yaml"
    case "$MODEL" in *haiku*) THINKING="" ;; esac

    .venv/bin/mini-extra swebench --subset verified --split test --filter "$(filter standard)" -m "$MODEL" -c swebench-local.yaml $THINKING -o "runs/main/$SHORT/standard" -w 3
    .venv/bin/mini-extra swebench --subset verified --split test --filter "$(filter hard)" -m "$MODEL" -c swebench-local.yaml $THINKING -o "runs/main/$SHORT/hard" -w 3
}

PIDS=""
for MODEL in anthropic/claude-opus-4-6 anthropic/claude-opus-4-7 anthropic/claude-opus-4-8 anthropic/claude-fable-5 anthropic/claude-haiku-4-5 anthropic/claude-sonnet-4-6; do
    SHORT=$(basename "$MODEL" | sed 's/^claude-//')
    run_model "$MODEL" > "logs/$SHORT.log" 2>&1 &
    PIDS="$PIDS $!"
done

# Ctrl-C / kill must take every leg down with it — no orphaned legs spending
# money in the background (learned the hard way, 2026-06-10).
# In-flight instances are wiped and redone cleanly on the next resume; the
# instance containers self-expire (docker run --rm ... sleep 2h).
trap 'echo "Stopping all legs..."; for p in $PIDS; do pkill -P "$p" 2>/dev/null; kill "$p" 2>/dev/null; done; wait; exit 130' INT TERM

wait
echo "Experiment complete. Mark it with ./eval-experiment.sh"
