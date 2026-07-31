#!/bin/sh
# How far each vendored fork has drifted from the project it forked.
#
# Every submodule here is a fork carrying local patches, and the runs depend on
# their exact behaviour — so an upstream merge is an experiment-affecting
# decision, not routine hygiene. This only measures; it never merges.
#
# Adds an `upstream` remote where missing (parents resolved from GitHub).
set -eu
cd "$(dirname "$0")/.."

drift() {
  path=$1
  upstream=$2
  printf '\n=== %s  (upstream %s) ===\n' "$path" "$upstream"
  git -C "$path" remote get-url upstream >/dev/null 2>&1 \
    || git -C "$path" remote add upstream "https://github.com/$upstream.git"
  git -C "$path" fetch --quiet upstream 2>/dev/null || {
    echo "  fetch failed (private or unreachable)"; return 0; }
  head=$(git -C "$path" rev-parse --abbrev-ref HEAD)
  base=$(git -C "$path" symbolic-ref --quiet --short refs/remotes/upstream/HEAD 2>/dev/null \
    || echo upstream/main)
  ahead=$(git -C "$path" rev-list --count "$base..HEAD" 2>/dev/null || echo '?')
  behind=$(git -C "$path" rev-list --count "HEAD..$base" 2>/dev/null || echo '?')
  echo "  on $head: $ahead ours, $behind theirs (behind $base)"
  if [ "$behind" != "0" ] && [ "$behind" != "?" ]; then
    echo "  most recent upstream commits:"
    git -C "$path" log --oneline -5 "HEAD..$base" | sed 's/^/    /'
  fi
}

drift vendor/mini-swe-agent SWE-agent/mini-swe-agent
drift vendor/swebench SWE-bench/SWE-bench
drift vendor/swe-bench-pro scaleapi/SWE-bench_Pro-os
drift vendor/multi-swe-bench multi-swe-bench/multi-swe-bench
drift vendor/claude-cli shellicar/claude-cli
