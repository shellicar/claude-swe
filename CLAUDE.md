# claude-swe

SWE-bench A/B benchmarking rig. Current experiment: Claude Opus 4.8 vs Claude Fable 5 on SWE-bench Verified, scored on resolve rate and cost-per-resolved-task. The rig is model-agnostic and scaffold-agnostic by design — future experiments swap the model (any Messages API model) or the scaffold (own CLI vs Claude Code) against the same marking pipeline.

## Setup

Requirements: Docker, uv. The SWE-bench instance images are x86_64; they run fine under Apple Silicon emulation.

The patched scaffold is vendored as a git submodule, so clone with submodules (or init after cloning):

```bash
git clone --recurse-submodules <repo-url>
# already cloned:  git submodule update --init
```

Then the environment:

```bash
uv venv
uv pip install -e vendor/mini-swe-agent   # patched scaffold (submodule)
uv pip install sb-cli swebench
```

`vendor/mini-swe-agent` is a submodule pinned to the patched fork (`shellicar/mini-swe-agent`, branch `feature/claude-swe-patches`). The patches vs upstream:

- `agents/default.py`: `system_identity` config field; when set, the system message is built as two content blocks (identity + scaffold prompt), each with a `cache_control` marker.
- `models/utils/cache_control.py`: the `default_end` processor skips system messages, so explicit markers on them survive.

Note: an editable install (`-e`) means the submodule's source is used live. To change the scaffold, edit in the submodule, commit/push to the fork, then bump the submodule pointer here.

`.env`:

```env
SWEBENCH_API_KEY=...
ANTHROPIC_AUTH_TOKEN=...
SSL_CERT_FILE=./ca-bundle.pem
REQUESTS_CA_BUNDLE=./ca-bundle.pem
```

Corporate TLS (Zscaler): `ca-bundle.pem` = certifi's bundle + the Zscaler root (exported from the macOS Keychain). The two env vars above cover Python's HTTP stacks. For uv itself: `UV_SYSTEM_CERTS=true`.

All scripts assume cwd = this directory and call `.venv/bin/` binaries directly — no venv activation needed.

## Workflow

Two decoupled halves, connected only by `preds.json`:

1. **The work** — `mini-extra swebench` runs one fresh agent per instance in its own Docker container; writes per-instance trajectories and `preds.json` (instance id + model name + diff) to the output dir. Batch mode is unattended; confirmation prompts exist only in `swebench-single` interactive mode.
2. **The marking** — `python -m swebench.harness.run_evaluation` applies each patch to a pristine repo and runs that instance's tests, locally in Docker. Writes a report JSON (resolved/unresolved per instance) and full test logs under `logs/run_evaluation/`. Deterministic, model-free, no API cost.

The marker does not care what produced the patches — anything that emits a valid `preds.json` can be scored. That contract is the seam for benchmarking other scaffolds.

Note: sb-cli (cloud marking) requires per-subset authorization; this key has no `swe-bench_verified` quota, which manifests as runs "failing" with no error detail. Local marking is canonical here.

## Concepts

- **Instance** — one benchmark task: a real GitHub issue + repo snapshot + hidden marking tests. `verified` = the 500-instance human-validated subset.
- **Resolved** — the instance's failing tests now pass *and* the previously passing tests still pass. Plausible-looking patches that don't satisfy the tests mark as unresolved.
- **Trajectory** — full message/action history of one agent run (`*.traj.json`), including per-step cost and token usage.
- **Repeats** — the same frozen instance set run multiple times per model; separates "model is better" from "run got lucky", and exposes flakiness.
- **Detection floor** — the smallest score gap a sample size can distinguish from noise (~±1.5/10 at n=10; shrinks with n). Identical scores at small n mean "below the floor", not "identical models".
- **Frozen set** — instance selection is fixed (seeded stratified-random across repos) before any paid run and identical for every leg; otherwise the comparison is void.
- **Prompt caching** — Anthropic caching is opt-in per request via `cache_control` markers; a marker caches everything before it. Config `set_cache_control: default_end` gives each trajectory a rolling whole-prefix cache; the identity/system-block markers additionally create one cache entry shared by all parallel workers. Cache reads cost 0.1× input price.
- **system_identity** — the constant identity prompt, configured separately from the scaffold's task prompt and cached as its own block. Mirrors how the production harness composes requests.
- **Cost registry** — models newer than litellm's bundled price table need a JSON registry entry (see `fable-5.litellm.json`, wired via `litellm_model_registry` in the yaml); the alternative (`cost_tracking: ignore_errors`) zeroes costs and disarms the `cost_limit` guard — avoid.
- **yolo** — mini's name for auto-confirm in interactive mode. It removes the per-action prompt and nothing else; cost/step/time limits and Docker isolation are independent of it.

## Cost intuition (micro-batch, 3 instances, cached)

Opus 4.8 ~ $0.22/instance; Fable 5 ~ $0.56/instance. Fable is 2× per-token but spends differently (often fewer steps on hard instances, more on careful ones). The comparison metric is cost per *resolved* task, not cost per run.
