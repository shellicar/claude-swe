"""The pair is the identity — the property every one of the five defects broke.

Run: .venv/bin/python selections_test.py
"""
import selections

failures = []


def check(what, actual, expected):
    if actual != expected:
        failures.append(f"{what}: expected {expected!r}, got {actual!r}")


# The collision itself. Same name, three datasets, three different populations.
check("multi/cpp size", len(selections.ids("multi", "cpp")), 20)
check("multilingual/cpp size", len(selections.ids("multilingual", "cpp")), 11)
check("multi/cpp vs multilingual/cpp overlap",
      selections.ids("multi", "cpp") & selections.ids("multilingual", "cpp"), set())

check("multi/rust size", len(selections.ids("multi", "rust")), 20)
check("multilingual/rust size", len(selections.ids("multilingual", "rust")), 43)

check("multilingual/go size", len(selections.ids("multilingual", "go")), 42)
check("pro/go size", len(selections.ids("pro", "go")), 25)

# Files differ too, since the id sets come from them.
check("cpp files differ",
      selections.instance_file("multi", "cpp") != selections.instance_file("multilingual", "cpp"),
      True)

# A selection that does not exist in a dataset must fail loudly, not fall back
# to another dataset's answer.
try:
    selections.ids("verified", "cpp")
    failures.append("verified/cpp: expected KeyError, got a result")
except KeyError:
    pass

# The declared count and the file must agree — a silent mismatch is how a leg
# reports complete while short of instances.
for dataset, names in (("verified", ("standard", "hard")),
                       ("multi", ("cpp", "rust", "tokio")),
                       ("multilingual", ("rust", "cpp", "go")),
                       ("pro", ("pro", "nodebb", "element", "go"))):
    for name in names:
        check(f"{dataset}/{name} declared == file",
              len(selections.ids(dataset, name)), selections.expected(dataset, name))

# A combination resolves to its dataset, which is what makes a selection name
# in runs/<combo>/<leg>/<sel> unambiguous.
check("multi combination", selections.dataset_of("multi"), "multi")
check("cpp-variation combination", selections.dataset_of("cpp-variation"), "multi")
check("fmt-variation combination", selections.dataset_of("fmt-variation"), "multilingual")

if failures:
    for f in failures:
        print(f"FAIL  {f}")
    raise SystemExit(1)
print("selections: ok")
