# Bug hunt brief

A second pair of eyes on this rig. Report findings; change nothing without
being asked.

The bugs found here have almost all been of one kind: **something was assumed
rather than observed, and the wrong result looked exactly like the right one.**
Nothing crashed. The numbers stayed plausible. Look for that shape.

Worked examples, all real, all found late:

- `pyproject.toml` declared `swebench` as an editable install from `vendor/`.
  The venv actually held the PyPI package. Every verdict for weeks came from
  unpatched code, and the provenance recorded the submodule's commit anyway.
- An effort leg was configured `reasoning_effort=low`. litellm does not list
  that parameter for Moonshot, and `drop_params: true` removed it silently, so
  the leg ran at the model's default (max) and was recorded as "low".
- The grading harness reset the whole working tree before testing any instance
  whose test patch only adds files — destroying the patch it was about to
  grade. That instance was unresolvable by anyone for months.
- Two generators wrote the same card; whichever ran last won. One of them also
  wrote `data.json` in a shape the overview could not read, and dropped the
  `covers` key that the completeness gate depends on, disabling it.
- Report filenames are `<model>.<run_id>.json` and both halves can contain
  dots. Splitting on the first dot mangled the run id for Kimi, so its
  provenance files duplicated instead of updating.

## Where to look

**Resume and skip logic.** Several layers decide "already done": `preds.json`
keys, `evals/logs/run_evaluation/*` directories, `analysedDatasets`. Each can
skip work that actually needs redoing, and the symptom is a stale result, not
an error. An instance that died with an empty patch is recorded as complete.

**Producer/consumer shape mismatches.** `analysis/*/data.json` is written by
`analyse.py` and read by `analyse-overview.py` and `swe.mjs`. Keys, nesting and
required fields are agreed nowhere. Check every reader against every writer.

**Silently dropped configuration.** Anything set in a yaml or via `-c` that a
provider does not accept. `drop_params` is now `false`, but check the paths
that bypass validation (`extra_body` is forwarded verbatim and unchecked), and
that what a leg records matches what went over the wire
(`runs/*/api-timing.jsonl` has `request_params` per call).

**Concurrency.** Marking at high worker counts flips timing-sensitive tests
(django's file-cache expiry, sympy's seeds). Contention causes false FAILURES,
never false passes. Check for anything that treats a first-pass failure as
final.

**Cost and token accounting.** Costs come from litellm rather than being
computed from the recorded token counts. Prices live in
`fable-5.litellm.json`; a missing entry means a silent zero, which also
disarms the `cost_limit` guard.

**Anything asserting an environment fact.** Paths, installed versions, image
digests, submodule commits. Ask whether the code checks or assumes, and what a
wrong answer would look like — if it looks like a normal result, that is the
bug.

## How to report

For each finding: what is wrong, how it was verified (a command and its
output), what a wrong result looks like from outside, and what it would take to
fix. Do not fix anything yet.
