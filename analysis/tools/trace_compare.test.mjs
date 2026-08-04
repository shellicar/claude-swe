import { test } from "node:test";
import assert from "node:assert/strict";

import { compareTraces, traceLines } from "./trace_compare.mjs";

test("identical traces are equal", () => {
  const expected = true;

  const actual = compareTraces(["+ a", "+ b"], ["+ a", "+ b"]).equal;

  assert.equal(actual, expected);
});

test("a swapped pair inside a two-stage pipeline is equal", () => {
  const expected = true;

  const actual = compareTraces(["+ echo one", "+ grep one"], ["+ grep one", "+ echo one"], 2).equal;

  assert.equal(actual, expected);
});

test("a swapped pair is a difference when the command has no pipeline", () => {
  const expected = false;

  const actual = compareTraces(["+ a", "+ b"], ["+ b", "+ a"], 1).equal;

  assert.equal(actual, expected);
});

test("a swap wider than the pipeline is a difference", () => {
  const expected = false;

  const actual = compareTraces(["+ a", "+ b", "+ c"], ["+ c", "+ b", "+ a"], 2).equal;

  assert.equal(actual, expected);
});

test("a three-stage pipeline may permute across all three", () => {
  const expected = true;

  const actual = compareTraces(["+ a", "+ b", "+ c"], ["+ c", "+ b", "+ a"], 3).equal;

  assert.equal(actual, expected);
});

test("a changed line is a difference even at pipeline width", () => {
  const expected = false;

  const actual = compareTraces(["+ echo one", "+ grep one"], ["+ echo one", "+ grep two"], 2).equal;

  assert.equal(actual, expected);
});

test("the first differing line is reported", () => {
  const expected = 1;

  const actual = compareTraces(["+ a", "+ b"], ["+ a", "+ c"]).at;

  assert.equal(actual, expected);
});

test("a missing trailing line is a difference", () => {
  const expected = false;

  const actual = compareTraces(["+ a", "+ b"], ["+ a"]).equal;

  assert.equal(actual, expected);
});

test("ordinary stderr is not read as a trace line", () => {
  const expected = ["+ cd /tmp", "++ echo sub"];

  const actual = traceLines("+ cd /tmp\nls: no such file\n++ echo sub\n");

  assert.deepEqual(actual, expected);
});
