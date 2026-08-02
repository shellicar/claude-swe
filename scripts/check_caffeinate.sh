#!/bin/sh
# Do the flags swe.mjs uses actually register the assertions that matter?
# -s alone held only on mains power, so a run died ten seconds after the
# charger came out. This checks all three are asserted.
caffeinate -dis -w $$ &
sleep 1
pmset -g assertions | grep -E \
  'PreventUserIdleSystemSleep|PreventSystemSleep|PreventUserIdleDisplaySleep'
