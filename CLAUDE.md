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

**A scaffold change is one unit of work, not three.** Editing in the submodule takes effect immediately for you (editable install) and for nobody else, so a half-finished sequence is worse than not starting: this repo's configs assume scaffold behaviour that no other clone has. Do all of it, in order, without stopping in between:

```sh
git -C vendor/mini-swe-agent add <files> && git -C vendor/mini-swe-agent commit
git -C vendor/mini-swe-agent push origin feature/claude-swe-patches
git add vendor/mini-swe-agent   # the pointer, committed with the changes that need it
```

The order matters and only that order is safe. Bumping the pointer before the push records a commit nobody can fetch, so a fresh clone fails at `git submodule update`. Pushing without bumping leaves this repo on the old scaffold while its configs expect the new one — which is exactly how a leg dies at turn 2 with a 400 rather than at startup with an obvious error.

`.env`:

```env
SWEBENCH_API_KEY=...
ANTHROPIC_AUTH_TOKEN=...
SSL_CERT_FILE=./ca-bundle.pem
REQUESTS_CA_BUNDLE=./ca-bundle.pem
```

**uv notes:** a uv-made venv has no `pip` — install with `uv pip …`, and the CLIs land in `.venv/bin/` (the scripts call them directly, no activation needed).

**Corporate TLS (Zscaler) — only behind the proxy:** it re-signs TLS with a root the bundled cert stores don't trust, so `uv` fails with `CERTIFICATE_VERIFY_FAILED` / `invalid peer certificate: UnknownIssuer`, and Python HTTP (litellm, sb-cli) fails the same way.

- **uv:** add `--system-certs`, or set `UV_SYSTEM_CERTS=1` (e.g. `UV_SYSTEM_CERTS=1 uv pip install …`). `uv --allow-insecure-host <host>` is the blunt fallback.
- **Python:** `ca-bundle.pem` = certifi's bundle + the Zscaler root (exported from the macOS Keychain); the `SSL_CERT_FILE` / `REQUESTS_CA_BUNDLE` vars above point Python's HTTP stacks at it. To build it:

  ```sh
  security find-certificate -a -c Zscaler -p /Library/Keychains/System.keychain > zscaler.pem
  cat "$(.venv/bin/python -m certifi)" zscaler.pem > ca-bundle.pem
  ```

Off the corporate network, none of this is needed — and the `.env` lines must then be REMOVED, not just ignored: a path pointing at a missing bundle breaks every Python HTTPS call in tools that load `.env` (litellm, the swebench harness), with misleading errors ("could not find requirements.txt") rather than a TLS complaint. Learned 2026-07-09 on a machine where `.env` still pointed at the old machine's absolute path.

All scripts assume cwd = this directory and call `.venv/bin/` binaries directly — no venv activation needed.

## Long jobs need the machine awake

Runs, marking and replay take hours. If the machine sleeps, the Docker VM
suspends with it and the harness is left waiting on containers that no longer
exist — it does not error, it hangs, and its progress bar keeps showing the
last frame it drew. A full re-mark once sat at "41 seconds remaining" for
thirteen hours.

Prefix anything long-running:

```sh
caffeinate -s node swe.mjs mark analyse
```

`-s` prevents system sleep while on mains power. Closing the lid still sleeps
regardless, so an unattended overnight job wants the lid open.

`mark` also prints a warning every five minutes when nothing new has been
graded, so a stall announces itself rather than being discovered the next day.

## Running and reporting

A change is not done when the diff reads correctly. It is done when you have run
it and looked at what came out. A missing import, a card whose `data.json` holds
no figures, a lookup that quietly takes in a second dataset: each of these reads
correctly in a diff and dies on the first command that touches it.

So run what you changed. `node --check` is not running it. Three things, in
order:

1. **Execute the path you changed.** `./swe.mjs status verified/micro` exercises
   argument parsing, the declarations, the manifest and every reading verb, in
   seconds.
2. **Read the output, not the exit code.** A generator exits 0 having written a
   card with no figures in it; a table renders clean with every glyph wrong.
3. **Try a case that is not the one you fixed.** Selection names collide across
   datasets, so a lookup that is right for `verified/micro` is wrong for
   `multi/cpp`. The same per-leg computation lives in four analysers, so a fix
   in one leaves three. Exercising a fix only on the example it came from is not
   exercising it: grep for the shape elsewhere.

`verified/micro` (4 instances) and ad-hoc legs (`--model` outside a combination,
landing in `runs/adhoc/`) are the bench: small enough that proving a change
works costs almost nothing. `run` and `mark` are yours on those.

`run` and `mark` on anything else spend the Supreme Commander's money and hours,
and produce the record every card is built from. Those are his. Give three
things — **the command, what it does, and where its results appear** — then
stop.

> Marks every unmarked leg, checks the record is complete, regenerates the
> cards.
>
> ```sh
> node swe.mjs mark main audit analyse
> ```
>
> Results: `analysis/verified/table.md`, `analysis/coverage/table.md`

The reading verbs — `status`, `audit`, `analyse` — and the analysers are always
yours to run. Scratch scripts go in `/tmp`, never the repo, and only read: never
into `runs/`, `evals/`, `image-manifest.txt` or `instances-*.txt`, which is the
record.

If answering needs a figure the pipeline cannot produce, change the analyser
that should produce it and point at the card. Not a script on the side.

Why: `swe.mjs` and the cards in `analysis/*/` exist because this was once done
ad-hoc — one-off scripts, numbers quoted from nowhere, nothing regenerable. A
number in prose is indistinguishable from a generated one, so it cannot be
checked, diffed, or trusted a week later. Investigating with a scratch script
is fine; quoting its output as a result is what recreates the problem.

## Workflow

One entry point: `./swe.mjs [verb...] [target...] [flags]` — verbs × targets given in any order (each token is classified as a verb or a target), either axis omitted meaning all of it. Verbs `draw resolve ensure run mark status audit analyse` run in the order given, per target; targets are `combinations/*.json` names or `dataset[/selection]`. Bare `./swe.mjs` is the whole dashboard; `./swe.mjs analyse` analyses everything; `./swe.mjs exec-arm-2 run mark` runs then marks that combination. Every verb resumes; `audit` blocks `analyse` on incomplete records. Conceptual model: `docs/diagrams/operations.d2`. Superseded per-experiment scripts live in `archive/` for reference.

Two decoupled halves underneath, connected only by `preds.json`:

1. **The work** (`run`) — drives `mini-extra swebench`: one fresh agent per instance in its own Docker container; writes per-instance trajectories, wire captures, and `preds.json` (instance id + model name + diff) to the leg's output dir.
2. **The marking** (`mark`) — applies each patch to a pristine container and runs that instance's tests, locally in Docker, via the dataset's declared marker (swebench for Verified, Scale's harness for Pro). Inputs are declared in the repo: `image-manifest.txt` (instance → image digest), `datasets/*.jsonl` (snapshots), `uv.lock` (harness). Outputs land under `evals/`: verdicts (committed) and per-instance test logs (ignored). Deterministic, model-free, no API cost.

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

## SWE-bench — underlying design issues

These are upstream properties of swebench itself, not artefacts of this rig's scripts. Found 2026-07-07–09. End-to-end data flow: `docs/diagrams/eval-pipeline.d2` (render with `docs/diagrams/render.sh`).

**It is an image-builder with evaluation grafted on.** The original design: every user builds every environment locally — clone the project repo, fetch its dependency recipes at a historical commit, install, then test. Prebuilt registry images (`--namespace`) were bolted on later as a different way to *obtain* images, but spec construction was never split into "what building needs" vs "what evaluating needs": one eager `TestSpec` constructor serves both, so evaluation still executes build-era work — including live network fetches whose output (env-setup and repo-setup scripts) the evaluator never runs. Marking genuinely needs only image + patch + eval script; the code cannot currently be told that.

**Environment definitions live outside the benchmark.** The dataset row carries `repo` + `environment_setup_commit`, but the *content* of the dependency recipe is never shipped — it is fetched from the third-party project's GitHub at use time — and the *path* to it lives in lookup tables inside the installed package. The recipe's full identity is therefore late-bound (dataset × package version × GitHub availability), assembled per invocation, stored nowhere. Its only materialisation is inside the prebuilt images.

**No reproducibility surface is published.** Images are pushed as mutable `:latest` tags with no digest manifest; the HF dataset revision floats; and the verdict semantics themselves (per-repo log parsers + grading rules) live in the package code, unversioned relative to the dataset — so the harness version is silently part of any experiment. Consumers must construct their own pins: rig-side these are `image-manifest.txt` (declared instance→digest, resolved from the registry per epoch), `uv.lock`, and `datasets/*.jsonl`; upstream publishes none of them.

**Errors discard their causes.** A failed recipe fetch — any status, any transport error — surfaces as `ValueError: Could not find requirements.txt at <paths>…`. The HTTP status and body are thrown away, so wildly different faults (broken local TLS config, genuine 404 from a path-table mismatch) produce the same message. Diagnose at the wire, never from the exception text.

**Images are per-instance monoliths.** All instances share exactly 6 base layers (Ubuntu + Miniconda); beyond that, nothing — even two django instances share no layers. Each image carries its own ~1 GB conda env and its own checkout. Inside, the project's git history is squashed to a single synthetic `SWE-bench` commit: the dataset's `base_commit` sha does not exist in the image. The build scripts as-executed are baked at `/root/setup_env.sh` / `setup_repo.sh` — the image documents its own build; nothing else does.

**Operational roughness.** All outputs are cwd-relative: report JSONs dumped into cwd (`<model>.<run_id>.json`), instance logs under `cwd/logs/run_evaluation/`; resume-skip reads those log dirs, so cwd must stay constant. A scoped `--instance_ids` run REWRITES the leg's aggregate report to just those instances. The process can hang indefinitely after a completed leg. A run killed mid-instance leaves a named eval container behind; the next run 409s until it is removed. And the benchmark's own PASS_TO_PASS selections include timing-flaky tests (django's `test_touch` file-cache expiry), giving marking a noise floor of ~1 flip per ≈1,300 verdicts under emulation load.

## Learnings

Methodology lessons from the runs so far — read before designing the next experiment.

- **Cost caps censor the cost variable.** The scaffold's default `cost_limit: 3.0` produced empty patches concentrated on the thinking-heavy models, biasing the exact thing being measured. Set the cap as a pathological-loop guard (e.g. $25 / 250 steps), never near real spend — then audit for empty patches before trusting the numbers.
- **Single pass = n=1 per cell.** An individual instance verdict is one observation — a "solved" can be a coin flip. Only aggregate rates are meaningful; use repeats to separate stable capability from luck.
- **Effort is flat above `high`** (Opus 4.8, this benchmark): `high` / `xhigh` / `max` resolved the same set at ~1× / 2.5× / 6× the cost and time. Effort converts near-misses, not out-of-reach problems, so this is bounded to this distribution (easy-medium, in-reach-or-not); a near-miss-thick distribution might differ. Don't pay for `xhigh`/`max` on work shaped like this.
- **Unattended parallel runs need a kill-trap and a single capture owner.** Ctrl-C on the runner once orphaned background legs that kept spending (~$100 of zombie runs) — the runner now traps signals. And running legs concurrently through one shared proxy contaminates wire-log attribution (per-model thinking on the standard set became unrecoverable). One proxy per run, started/stopped by the run script, writing into the run dir.
- **Frozen paper, identical both legs.** The instance set (seed, difficulty×repo strata) is fixed before any paid run and identical across every model/effort, or the comparison is void.


## bash-walker — the AST-execution bash tool

A from-scratch bash interpreter (`rust/crates/bash-parser` + `bash-walker`) built to replace unconstrained real bash as the tool a fleet Claude runs commands through: the AST is inspectable and gateable by policy before anything executes, the way a raw `bash -c` string never is. Full design in `docs/ast-execution.md` (uncommitted by standing rule — local-only). Validated by two mechanisms: a corpus differential (bash-parser vs bash 5.3 over 106k real commands) and sequence replay (`analysis/tools/sequence_replay.mjs`) — whole recorded trajectories replayed step-by-step in twin containers, the image's own bash vs the walker, comparing output and status at every step.

**Known gap, deliberately parked (2026-07-28): no byte-fidelity for invalid-UTF8 text.** Bash treats all shell text as opaque bytes throughout; the walker's lexer/parser/expander are built on Rust `String` (valid UTF-8 required). A filename or argument containing a raw non-UTF8 byte (e.g. 0xFF) round-trips differently between the two — found via sequence replay (`ls -la | grep funky` on a byte-invalid filename). This is a data-representation gap, not a logic/control-flow bug: nothing about what the shell *decides* changes, only how that one edge-case byte prints. Fixing it properly means reworking word/text handling to a byte-oriented representation (`Vec<u8>` or similar) through the whole pipeline — parser, lexer, expander, every builtin that touches text — then re-validating everything built on top (full differential + sequence replay rerun), since a representation change this deep can silently shift behaviour anywhere text is sliced, compared, or pattern-matched. Estimated effort ~7-8/10 (a project, not a patch), versus ~3/10 for a typical contained bug fix in this codebase. The SC's call (2026-07-28): worth doing eventually — it's a genuinely niche case (only surfaced once in ~2,700 replayed trajectories, and only because that task was deliberately testing a byte-hostile filename), but real and not permanently out of scope. Deferred, not decided against.
