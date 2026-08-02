"""Split an eval report filename into (model, run_id).

Reports are named `<model>.<run_id>.json`, and BOTH halves can contain dots:
`moonshot__kimi-k2.7-code.runs_main_kimi-k2.7-code_hard.json`. Splitting on the
first dot produced the run id "7-code.runs_main_kimi-k2.7-code_hard", which
then named a provenance file that no marking run would ever overwrite — so
Kimi's records silently duplicated instead of updating.

Nearly every run id begins "runs_", which disambiguates. A few older ones do
not (`anthropic__claude-sonnet-5.exec-arm-1-recover.json`), but those have no
dots in the model half, so the first dot is right for them.
"""


def split_report(name):
    stem = name[:-len(".json")] if name.endswith(".json") else name
    if ".runs_" in stem:
        i = stem.index(".runs_")
        return stem[:i], stem[i + 1:]
    model, _, run_id = stem.partition(".")
    return model, run_id
