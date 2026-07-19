# claude-swe

> A rig for benchmarking Claude models on SWE-bench Verified, by resolve rate and by cost per resolved task.

*Developed with assistance from Claude.*

## Features

- 📊 **Two-axis scoring** - Reports resolve rate alongside cost, tokens, and time, not resolve rate alone.
- 🧪 **Local marking** - Applies each patch to a pristine repo and runs the held-back tests in Docker. Deterministic, no model, no API cost.
- 🔌 **Scaffold-agnostic** - Generation and marking are joined only by a `preds.json` of patches, so any model or scaffold that emits one can be scored.
- 📌 **Frozen instance sets** - A seeded, stratified selection, fixed before any run and identical across every model and effort level.
- ⏱️ **Wire-level capture** - An optional proxy records per-request timing and token usage.
- ♻️ **Resumable runs** - Interrupt and re-run; completed instances are skipped.

## Installation & Quick Start

Requires Docker and [uv](https://docs.astral.sh/uv/) (`brew bundle` installs uv; or `curl -LsSf https://astral.sh/uv/install.sh | sh`). The agent scaffold is a git submodule.

```sh
git clone --recurse-submodules <repo-url>
cd claude-swe
brew bundle   # installs uv
uv sync       # creates .venv and installs the scaffold (editable), sb-cli, swebench
```

Create a `.env` with `ANTHROPIC_AUTH_TOKEN` (and `SWEBENCH_API_KEY` for cloud marking), then:

```sh
./swe.mjs main run                     # generate patches (uses the API)
./swe.mjs main mark audit analyse      # mark locally (free), audit, write analysis
```

See `CLAUDE.md` for the full setup, including the corporate-TLS workaround.

## Motivation

Coding benchmarks report how many issues a model resolves, but not what it cost to get there. I wanted both, so this scores resolve rate against cost per resolved task, and holds the scaffold constant so the model is the only variable. It also runs a single model across effort levels, to see what more thinking actually buys.

## Usage

Everything runs through one entry point: `./swe.mjs [verb...] [target...]` — verbs × targets, either axis omitted meaning all of it. Targets are declared combination sets (`combinations/*.json`) or `dataset[/selection]`; verbs chain in order per target and every verb resumes where it left off.

```sh
./swe.mjs                                # the dashboard: status of every meet
./swe.mjs analyse                        # analyse everything
./swe.mjs main                           # where the main experiment stands, verb by verb
./swe.mjs main run                       # generate patches (uses the API)
./swe.mjs main mark audit analyse        # mark locally (free), audit completeness, write analysis/
./swe.mjs effort-sweep run mark audit    # the effort sweep, same verbs
./swe.mjs pro draw resolve ensure run mark audit analyse   # a whole paper, end to end
```

## Configuration

- `swebench-local.yaml` - model, limits, prompt, and caching for a run.
- `thinking-adaptive.yaml` - overlay enabling adaptive thinking, merged per model.
- `fable-5.litellm.json` - price registry for models newer than litellm's table.
- `instances-standard.txt`, `instances-hard.txt` - the frozen problem sets.
- `draw-instances.py` - regenerates those sets from a fixed seed.

## Results

- `report.md` - model comparison (Fable 5, Opus 4.8 / 4.7 / 4.6, Sonnet 4.6, Haiku 4.5) over 105 problems.
- `report-effort.md` - Opus 4.8 across effort levels over the same set.
- `analysis/exec/table.md` - structured-execution division (Sonnet 5, hard set): bash vs the ExecV1/V2/V3 tool-grammar ladder. Tool structure never beats bash control - it plateaus at parity, since Sonnet 5 rarely hits the failure modes structure would prevent.
- `analysis/scaffold/table.md` - prompt-scaffolding division (Sonnet 5, hard set, bash only): dropping mini's forced submission ritual for a "pen-down" agent (stops when done, harness reads the patch off disk) beats the ritual-bound control outright - 38/45 resolved vs 34/45, and cheaper per resolve. Layering the exec tool on top of pen-down does not add to this win.

SWE-bench Verified is Python only: mature, well-tested repositories with clearly-specified issues. It measures diagnosis-style bug fixing, not feature building or other languages, so the numbers bound well-specified problems on well-tested code. Figures are estimates, single-pass unless noted.

## Credits & Inspiration

- [SWE-bench](https://www.swebench.com/) - the benchmark and its evaluation harness.
- [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) - the agent scaffold, used via a patched fork.
