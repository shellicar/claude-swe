#!/bin/sh
# THE evaluation: marks every leg that has produced predictions.
# Local Docker, no API cost. Resumable: already-marked instances are skipped,
# so rerun as often as you like (including while the experiment is running).
#
# Reports land in the repo root as <model>.<run_id>.json; detailed test logs
# under logs/run_evaluation/<run_id>/.
set -e
cd "$(dirname "$0")"

for d in runs/*/*/*/; do
    d="${d%/}"
    [ -f "$d/preds.json" ] || continue
    RUN_ID=$(echo "$d" | tr '/' '_')   # run_id becomes a directory name; no slashes
    # --namespace swebench: pull the official prebuilt instance images.
    .venv/bin/python -m swebench.harness.run_evaluation --dataset_name princeton-nlp/SWE-bench_Verified --predictions_path "$d/preds.json" --max_workers 3 --namespace swebench --run_id "$RUN_ID"
done
echo "Evaluation complete."
