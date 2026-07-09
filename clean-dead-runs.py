#!/usr/bin/env python3
"""Remove instance dirs for the two known dead-run types.

Exactly these exit statuses, nothing broader:

  - AuthenticationError   (run started without a valid API key)
  - InternalServerError   (litellm's label for connection-refused / 500s)

Both are poison: mini-extra records them as completed instances, so resume
skips them forever and they mark as unresolved garbage. Verified to die on
their first call ($0 spent), so deletion loses nothing; the next run redoes
the instance for real. Any other exit status is left strictly alone.

Also prunes each set's preds.json: completeness is judged from preds, not
instance dirs, so entries whose dir is gone must go too — otherwise a rerun
sees every instance answered and exits without redoing anything (learned
2026-07-07: deleted dirs, stale preds, run declared itself complete).

Dry-run by default — prints what would go. Pass --delete to actually delete.

Usage:
    python3 clean-dead-runs.py runs/main/sonnet-5            # preview
    python3 clean-dead-runs.py runs/main/sonnet-5 --delete   # do it
"""
import json
import shutil
import sys
from pathlib import Path

DEAD_EXIT_STATUSES = {'AuthenticationError', 'InternalServerError'}

args = [a for a in sys.argv[1:] if a != '--delete']
delete = '--delete' in sys.argv[1:]
if len(args) != 1:
    sys.exit(__doc__)

root = Path(args[0])
if not root.is_dir():
    sys.exit(f'not a directory: {root}')

victims = []
for traj in sorted(root.glob('*/*/*.traj.json')):
    try:
        info = json.loads(traj.read_text()).get('info', {})
    except (json.JSONDecodeError, UnicodeDecodeError):
        continue  # not a parseable trajectory (e.g. an unpulled LFS stub) — leave it alone
    if info.get('exit_status') in DEAD_EXIT_STATUSES:
        victims.append((traj.parent, info.get('exit_status')))

for d, status in victims:
    print(f'{status:20s} {d}')
print(f'{len(victims)} dead instance dirs', 'deleted' if delete else '(dry run — pass --delete to remove)')

if delete:
    for d, _ in victims:
        shutil.rmtree(d)

# Prune preds.json entries whose instance dir is gone (including dirs just
# deleted above, and any removed by hand before this run).
for preds_path in sorted(root.glob('*/preds.json')):
    preds = json.loads(preds_path.read_text())
    set_dir = preds_path.parent
    stale = sorted(iid for iid in preds if not (set_dir / iid).is_dir())
    for iid in stale:
        print(f'{"stale preds entry":20s} {set_dir.name}/{iid}')
    if not stale:
        continue
    if delete:
        for iid in stale:
            del preds[iid]
        preds_path.write_text(json.dumps(preds, indent=2))
    print(f'{len(stale)} stale entries in {preds_path}', 'pruned' if delete else '(dry run)')
