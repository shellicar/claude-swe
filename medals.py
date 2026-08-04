"""One medal system: every instance is an event, and the cheapest solver wins it.

There is exactly one way a card awards medals. Resolving is the entry ticket —
a competitor that failed cannot place however cheap it was — and among the
finishers the cheapest takes gold. An instance nobody resolved awards nothing.

This shows what an average hides: a model can post the best $/resolved while
rarely being cheapest on any single instance, if it is cheap on the easy
majority.

The only thing that differs between cards is how to find a leg's resolved set,
because the three markers write different files. So a card supplies
`resolved_of(base, sel) -> set[instance_id] | None`, and everything else —
cost per instance, the podium, the tally, the heading — is shared. Returning
None means the leg was never marked, which is not the same as resolving
nothing.
"""
import glob
import json
import os

GOLD, SILVER, BRONZE = "\U0001F947", "\U0001F948", "\U0001F949"
MEDALS = (GOLD, SILVER, BRONZE)


def instance_costs(root, base, sel, ids=None):
    """{instance_id: cost} for one leg, restricted to the selection's members.

    A stray trajectory cannot appear in a resolved set so it never places, but
    it would still swell the event count and the "unsolved by everyone" figure
    in the tally heading. Both would read high.
    """
    out = {}
    for p in glob.glob(f"{root}/runs/{base}/{sel}/*/*.traj.json"):
        iid = os.path.basename(p)[: -len(".traj.json")]
        if ids is not None and iid not in ids:
            continue
        out[iid] = json.load(open(p))["info"]["model_stats"].get(
            "instance_cost") or 0.0
    return out


def tally(root, bases, sels, resolved_of, ids_of=None):
    """(counts, unsolved, events) — counts is {base: [gold, silver, bronze]}.

    `bases` are run out-paths ("main/opus-5", "exec-arm-1/sonnet-5"), so the
    same contest works for model divisions, scaffolding arms and experiments.
    """
    per = {}
    for b in bases:
        acc = {}
        for s in sels:
            resolved = resolved_of(b, s)
            if resolved is None:
                continue  # never marked — cannot compete, and is not a loss
            ids = ids_of(s) if ids_of else None
            for iid, cost in instance_costs(root, b, s, ids).items():
                acc[iid] = (iid in resolved, cost)
        per[b] = acc

    counts = {b: [0, 0, 0] for b in bases}
    unsolved = 0
    every = {i for b in bases for i in per[b]}
    for iid in sorted(every):
        finishers = sorted((per[b][iid][1], b) for b in bases
                           if per[b].get(iid, (False, 0.0))[0])
        if not finishers:
            unsolved += 1
            continue
        for rank, (_cost, b) in enumerate(finishers[:3]):
            counts[b][rank] += 1
    return counts, unsolved, len(every)


def heading(what, events, unsolved):
    """The one tally heading. It said three different things in three places."""
    return (f"Medal tally — per instance ({events} events, "
            f"{unsolved} unsolved by every {what})")


def rows(counts, keys, placing=True):
    """The tally body: three medal rows, and the Olympic placing beneath.

    Placing is golds first, silvers then bronzes only as tie-breakers — one
    gold outranks any number of silvers. Gold means "solved it cheapest", so
    it is the column carrying the contest; a total-medals count would mostly
    restate Resolved.
    """
    body = [("## medals", [])]
    for i, word in enumerate(("gold", "silver", "bronze")):
        body.append((f"{MEDALS[i]} {word}",
                     [str(counts[k][i]) for k in keys]))
    if not placing:
        return body

    order = sorted(keys, key=lambda k: tuple(-n for n in counts[k]))
    rank_of, rank = {}, 0
    for i, k in enumerate(order):
        if i and counts[k] != counts[order[i - 1]]:
            rank = i
        rank_of[k] = rank
    body.append(("placing", [
        f"{MEDALS[rank_of[k]]}\u00a0**{rank_of[k] + 1}**" if rank_of[k] < 3
        else str(rank_of[k] + 1) for k in keys]))
    return body
