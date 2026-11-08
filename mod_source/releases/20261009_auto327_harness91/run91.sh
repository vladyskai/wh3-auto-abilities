#!/usr/bin/env bash
# Run harness91 GREEN (live+ann) then RED (pre91 snapshot) and report tails.
set -u
D="C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261009_auto327_harness91"
cd "$LOCALAPPDATA/Temp"
echo "=== GREEN (no env) ==="
env -u H91_LIVE -u H91_ANN uv run --quiet --with lupa python run_mock.py "$D/harness91.lua" > "$D/h91_green.txt" 2>&1
tail -3 "$D/h91_green.txt" | head -2
echo "=== RED (pre91 snapshot) ==="
H91_LIVE="$D/pre91_live.lua" H91_ANN="$D/pre91_ann.lua" uv run --quiet --with lupa python run_mock.py "$D/harness91.lua" > "$D/h91_red.txt" 2>&1
tail -3 "$D/h91_red.txt" | head -2
echo "=== RED FAIL lines by category ==="
grep -c "   FAIL" "$D/h91_red.txt"
