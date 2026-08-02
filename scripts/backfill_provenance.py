#!/usr/bin/env python3
"""Reconstruct provenance for verdicts marked before it was recorded.

Marked INFERRED, never presented as recorded: it is reconstructed from the
repository's own history, not observed at the time.

What makes it well founded, and where it stops:

* The marker. `vendor/swebench` is an editable install, so its commit IS the
  grader. That submodule pointer was set once (2026-07-09 18:39) and never
  moved, while the oldest verdict is 2026-07-09 23:06 — so every existing
  verdict was graded by that commit. Solid.
* The dataset snapshot and image manifest DID change over time, so a single
  hash would be wrong. Each verdict's mtime picks the commit that was current
  when it was written, and the file is hashed as it was in that commit.
* What cannot be recovered: whether a working tree was dirty at the time, and
  any marking done against uncommitted files. Those are recorded as unknown
  rather than guessed.

    python scripts/backfill_provenance.py [--write]
"""
import glob
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from report_name import split_report  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKER = "vendor/swebench"
WRITE = "--write" in sys.argv


def git(*args, binary=False):
    r = subprocess.run(["git", "-C", ROOT, *args], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout if binary else r.stdout.decode().strip()


def commit_at(when):
    """The repo commit current at a moment."""
    return git("log", "-1", "--format=%H", f"--before={when.isoformat()}")


def blob_sha(commit, path):
    """sha256 of a file AS IT WAS in that commit, matching writeProvenance."""
    data = git("show", f"{commit}:{path}", binary=True)
    return hashlib.sha256(data).hexdigest()[:16] if data else None


marker_commit = git("-C", MARKER, "rev-parse", "HEAD") or git(
    "rev-parse", f"HEAD:{MARKER}",
)
out_dir = os.path.join(ROOT, "evals", "provenance")
os.makedirs(out_dir, exist_ok=True)

written = skipped = 0
for report in sorted(glob.glob(os.path.join(ROOT, "evals", "*.json"))):
    name = os.path.basename(report)
    _model, run_id = split_report(name)
    target = os.path.join(out_dir, f"{run_id}.json")
    if os.path.exists(target):
        skipped += 1
        continue
    marked_at = datetime.fromtimestamp(os.path.getmtime(report), tz=timezone.utc)
    at = commit_at(marked_at)
    record = {
        "marked_at": marked_at.isoformat(),
        "inferred": True,
        "inferred_note": (
            "Reconstructed from repository history, not recorded at mark time. "
            "The marker is certain (its pointer never moved and predates every "
            "verdict); dataset and manifest hashes are taken from the commit "
            "current when the verdict file was written; dirtiness is unknowable."
        ),
        "selection": run_id.rsplit("_", 1)[-1],
        "marker": {
            "type": "swebench", "path": MARKER,
            "commit": marker_commit, "dirty": None,
        },
        "repo_commit_at_mark_time": at,
        "dataset": {
            "snapshot": "datasets/swe-bench-verified.jsonl",
            "sha256": blob_sha(at, "datasets/swe-bench-verified.jsonl") if at else None,
        },
        "image_manifest_sha256": blob_sha(at, "image-manifest.txt") if at else None,
    }
    if WRITE:
        with open(target, "w") as f:
            json.dump(record, f, indent=2)
    written += 1

print(f"{written} to backfill, {skipped} already have provenance"
      + ("" if WRITE else "  (dry run — pass --write)"))
