"""What a selection contains — always asked as (dataset, name).

A selection name is not an identity. `cpp` is 20 instances in multi and 11
different ones in multilingual; `rust` is 20 and 43; `go` is 42 in multilingual
and 25 in pro. The identity is the pair, and code that resolves a name alone is
guessing correctly only until two datasets happen to overlap.

That guess has already produced five defects, each fixed at its point of use:
trajectories written into another dataset's directory; four analysers costing a
leg from whatever sat on disk; a bare dataset target pulling seven multilingual
legs into `status multi/cpp`; the coverage card sizing `cpp` at whichever
dataset it read last. The type stayed `str` every time, so the next consumer
inherits the bug.

Both arguments are required. There is no way to ask what `cpp` means without
saying whose.
"""
import functools
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


@functools.cache
def _dataset(dataset):
    with open(f"{ROOT}/datasets/{dataset}.json") as f:
        return json.load(f)


def declaration(dataset, name):
    """The dataset's own declaration for this selection."""
    selections = _dataset(dataset)["selections"]
    if name not in selections:
        raise KeyError(
            f"{dataset} declares no selection {name!r} "
            f"(has {', '.join(sorted(selections))})")
    return selections[name]


def instance_file(dataset, name):
    return declaration(dataset, name)["file"]


@functools.cache
def ids(dataset, name):
    """The instance ids this selection contains."""
    path = f"{ROOT}/{instance_file(dataset, name)}"
    with open(path) as f:
        found = {line.strip() for line in f if line.strip()}
    expected = declaration(dataset, name).get("expected")
    if expected is not None and len(found) != expected:
        raise SystemExit(
            f"{dataset}/{name}: {instance_file(dataset, name)} holds {len(found)} "
            f"instances, but the dataset declares {expected}")
    return found


def expected(dataset, name):
    """How many instances the selection should have."""
    return declaration(dataset, name).get("expected") or len(ids(dataset, name))


def dataset_of(combination):
    """The dataset a combination competes in \u2014 which is what makes a selection
    name in a run path unambiguous."""
    with open(f"{ROOT}/combinations/{combination}.json") as f:
        return json.load(f)["dataset"]
