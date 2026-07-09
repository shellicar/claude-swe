#!/bin/sh
# Mark every completed effort-sweep leg.
# Resumable: already-marked instances are skipped on rerun.
# Reports land in the repo root alongside the main experiment reports.
set -e
cd "$(dirname "$0")"

for d in runs/effort-sweep/*/*/; do
    d="${d%/}"
    [ -f "$d/preds.json" ] || continue
    RUN_ID=$(echo "$d" | tr '/' '_')
    # --namespace swebench: pull the official prebuilt instance images.
    .venv/bin/python -m swebench.harness.run_evaluation --dataset_name princeton-nlp/SWE-bench_Verified --predictions_path "$d/preds.json" --max_workers 3 --namespace swebench --run_id "$RUN_ID"
done
echo "Evaluation complete."
