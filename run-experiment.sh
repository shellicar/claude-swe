#!/bin/sh
# Shim: the experiment now lives in run-experiment.mjs (per-leg timing proxies,
# per-leg logs, aggregated shutdown). This keeps the documented entry point.
cd "$(dirname "$0")"
exec node run-experiment.mjs "$@"
