// Compares two `set -x` traces, which is what the shell actually decided,
// rather than what the programs it ran happened to print.
//
// Order is semantics: `a; b` traced as `b; a` is a different program. The one
// exception is a pipeline, where the stages are concurrent children racing to
// write their own line, and bash disagrees with itself about once in thirty.
// So the tolerance is scoped to exactly that: up to `width` adjacent lines may
// appear in any order, where `width` is the widest pipeline in the command as
// bash-parser reports it. Everything else compares strictly, in order.

const key = (lines) => [...lines].sort().join("\n");

/// `{ equal, permutations }` when the traces agree, or `{ equal: false, at,
/// bash, walker }` naming the first line that genuinely differs.
export function compareTraces(bash, walker, width = 1) {
  let i = 0;
  let permutations = 0;
  while (i < bash.length && i < walker.length) {
    if (bash[i] === walker[i]) {
      i++;
      continue;
    }
    // A pipeline's stages may have raced. Accept only a block that is the
    // same set of lines on both sides, and no wider than this command's
    // widest pipeline.
    let matched = 0;
    for (let k = 2; k <= width && i + k <= bash.length && i + k <= walker.length; k++) {
      if (key(bash.slice(i, i + k)) === key(walker.slice(i, i + k))) {
        matched = k;
        break;
      }
    }
    if (matched === 0) {
      return { equal: false, at: i, bash: bash[i], walker: walker[i] };
    }
    permutations++;
    i += matched;
  }
  if (bash.length !== walker.length) {
    const at = Math.min(bash.length, walker.length);
    return { equal: false, at, bash: bash[at] ?? null, walker: walker[at] ?? null };
  }
  return { equal: true, permutations };
}

/// Trace lines are the ones bash marks with its `+` prefix. Anything else on
/// the stream is the command's own stderr and is not part of the comparison.
export function traceLines(text) {
  return text.split("\n").filter((l) => /^\++ /.test(l));
}
