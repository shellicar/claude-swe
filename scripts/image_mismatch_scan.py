#!/usr/bin/env python3
"""Did the worker-thread config race ever put an instance in the wrong image?

get_sb_environment mutates the SHARED config dict:

    env_config = config.setdefault("environment", {})
    env_config["image"] = image_name

With N workers that is a race — one thread can overwrite another's image
between the write and the environment being built, so an instance could run
against a different repo's container entirely and produce a patch for the
wrong codebase.

Each trajectory persists the config it ran with, so the image it actually used
is on disk and can be compared with the image its instance should have had.
"""
import glob
import json

BAD = []
CHECKED = 0
NO_IMAGE = 0


def expected_image(instance_id):
    return f"docker.io/swebench/sweb.eval.x86_64.{instance_id.replace('__', '_1776_')}:latest".lower()


for tf in glob.glob("runs/**/*.traj.json", recursive=True):
    try:
        t = json.load(open(tf))
    except Exception:
        continue
    image = (t.get("info", {}).get("config", {}).get("environment", {}) or {}).get("image")
    iid = tf.split("/")[-2]
    if not image:
        NO_IMAGE += 1
        continue
    CHECKED += 1
    # Only the swebench-style images can be checked this way; multi-swe and
    # pro use their own naming from row fields not present here.
    if "sweb.eval" not in image:
        continue
    if image != expected_image(iid):
        BAD.append((tf, iid, image))

print(f"trajectories checked: {CHECKED} (no image recorded: {NO_IMAGE})")
print(f"image did NOT match the instance: {len(BAD)}")
for tf, iid, image in BAD[:20]:
    print(f"  {iid}\n    ran in {image}\n    {tf}")
