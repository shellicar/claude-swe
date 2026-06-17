#!/bin/sh
# Opus 4.8 effort sweep: low, medium, xhigh, max — four new legs.
# The 'high' anchor already exists at runs/main/opus-4-8/; no need to re-run it.
#
# All legs are Opus 4.8, so they share one rate-limit bucket — run sequentially
# to avoid 429 storms. Each leg: standard then hard, 3 workers.
#
# Output: runs/effort-sweep/opus-4-8-<level>/<set>/
# Logs:   logs/effort-<level>.log
#
# Interrupt-safe: Ctrl-C kills the current leg and stops. Rerun to resume —
# completed instances are skipped, so the run picks up where it left off.
set -e
cd "$(dirname "$0")"
mkdir -p logs

MODEL="anthropic/claude-opus-4-8"
filter() { printf '^(%s)$' "$(tr '\n' '|' < "instances-$1.txt" | sed 's/|$//')"; }

run_effort() {
    LEVEL="$1"
    OUT="runs/effort-sweep/opus-4-8-$LEVEL"
    echo "=== effort: $LEVEL ==="
    .venv/bin/mini-extra swebench --subset verified --split test --filter "$(filter standard)" -m "$MODEL" -c swebench-local.yaml -c thinking-adaptive.yaml -c "model.model_kwargs.output_config.effort=$LEVEL" -o "$OUT/standard" -w 3
    .venv/bin/mini-extra swebench --subset verified --split test --filter "$(filter hard)" -m "$MODEL" -c swebench-local.yaml -c thinking-adaptive.yaml -c "model.model_kwargs.output_config.effort=$LEVEL" -o "$OUT/hard" -w 3
}

CURRENT_PID=""
trap 'echo "[sweep] Ctrl-C received — killing PID $CURRENT_PID and children..."; [ -n "$CURRENT_PID" ] && pkill -P "$CURRENT_PID" 2>/dev/null; kill "$CURRENT_PID" 2>/dev/null; wait; echo "[sweep] Stopped cleanly."; exit 130' INT TERM

for LEVEL in max xhigh medium low; do
    echo "[sweep] Starting effort=$LEVEL (log: logs/effort-$LEVEL.log)"
    run_effort "$LEVEL" > "logs/effort-$LEVEL.log" 2>&1 &
    CURRENT_PID=$!
    echo "[sweep] PID $CURRENT_PID running effort=$LEVEL"
    wait "$CURRENT_PID"
    STATUS=$?
    if [ $STATUS -eq 0 ]; then
        echo "[sweep] PID $CURRENT_PID (effort=$LEVEL) finished OK"
    else
        echo "[sweep] PID $CURRENT_PID (effort=$LEVEL) exited with status $STATUS"
    fi
    CURRENT_PID=""
done

echo "Effort sweep complete. Mark it with ./eval-effort-sweep.sh"
echo "The 'high' anchor is at runs/main/opus-4-8/ — include it in analysis."
