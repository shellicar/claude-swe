# claude-swe

> A rig for benchmarking Claude models on SWE-bench Verified, by resolve rate and by cost per resolved task.

*Developed with assistance from Claude.*
ww
## Features

- 📊 **Two-axis scoring** - Reports resolve rate alongside cost, tokens, and time, not resolve rate alone.
- 🧪 **Local marking** - Applies each patch to a pristine repo and runs the held-back tests in Docker. Deterministic, no model, no API cost.
- 🔌 **Scaffold-agnostic** - Generation and marking are joined only by a `preds.json` of patches, so any model or scaffold that emits one can be scored.
- 📌 **Frozen instance sets** - A seeded, stratified selection, fixed before any run and identical across every model and effort level.
- ⏱️ **Wire-level capture** - An optional proxy records per-request timing and token usage.
- ♻️ **Resumable runs** - Interrupt and re-run; completed instances are skipped.

## Installation & Quick Start

Requires Docker and [uv](https://docs.astral.sh/uv/). The agent scaffold is a git submodule.

```sh
git clone --recurse-submodules <repo-url>
cd claude-swe
uv venv
uv pip install -e vendor/mini-swe-agent sb-cli swebench
```

Create a `.env` with `ANTHROPIC_AUTH_TOKEN` (and `SWEBENCH_API_KEY` for cloud marking), then:

```sh
./run-experiment.sh    # generate patches (uses the API)
./eval-experiment.sh   # mark them locally (free)
```

See `CLAUDE.md` for the full setup, including the corporate-TLS workaround.

## Motivation

Coding benchmarks report how many issues a model resolves, but not what it cost to get there. I wanted both, so this scores resolve rate against cost per resolved task, and holds the scaffold constant so the model is the only variable. It also runs a single model across effort levels, to see what more thinking actually buys.

## Usage

- **Run the benchmark.** One patch per issue, each in its own Docker sandbox.

```sh
./run-experiment.sh
```

- **Mark the results.** Local and free; safe to run while generation is still going.

```sh
./eval-experiment.sh
```

- **Rebuild the report tables** from the marked results.

```sh
python analyse.py
```

- **Sweep effort levels** for a single model, low to max.

```sh
./run-effort-sweep.sh && ./eval-effort-sweep.sh
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

SWE-bench Verified is Python only: mature, well-tested repositories with clearly-specified issues. It measures diagnosis-style bug fixing, not feature building or other languages, so the numbers bound well-specified problems on well-tested code. Figures are estimates, single-pass unless noted.

## Credits & Inspiration

- [SWE-bench](https://www.swebench.com/) - the benchmark and its evaluation harness.
- [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) - the agent scaffold, used via a patched fork.
