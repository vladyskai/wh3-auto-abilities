#!/usr/bin/env bash
# Run harness94 GREEN (live+ann) then RED (pre94 snapshot) and report tails.
set -u
D="C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261010_accusation_harness94"
cd "$LOCALAPPDATA/Temp"
echo "=== GREEN (no env) ==="
env -u H94_LIVE -u H94_ANN uv run --quiet --with lupa python run_mock.py "$D/harness94.lua" > "$D/h94_green.txt" 2>&1
tail -3 "$D/h94_green.txt" | head -2
echo "=== RED (pre94 snapshot) ==="
H94_LIVE="$D/pre94_live.lua" H94_ANN="$D/pre94_ann.lua" uv run --quiet --with lupa python run_mock.py "$D/harness94.lua" > "$D/h94_red.txt" 2>&1
tail -3 "$D/h94_red.txt" | head -2
echo "=== RED FAIL lines count ==="
grep -c "   FAIL" "$D/h94_red.txt"
