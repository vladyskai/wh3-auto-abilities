#!/usr/bin/env bash
# Run harness92 GREEN (live+ann) then RED (pre92 snapshot) and report tails.
set -u
D="C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261009_final_roster_harness92"
cd "$LOCALAPPDATA/Temp"
echo "=== GREEN (no env) ==="
env -u H92_LIVE -u H92_ANN uv run --quiet --with lupa python run_mock.py "$D/harness92.lua" > "$D/h92_green.txt" 2>&1
tail -3 "$D/h92_green.txt" | head -2
echo "=== RED (pre92 snapshot) ==="
H92_LIVE="$D/pre92_live.lua" H92_ANN="$D/pre92_ann.lua" uv run --quiet --with lupa python run_mock.py "$D/harness92.lua" > "$D/h92_red.txt" 2>&1
tail -3 "$D/h92_red.txt" | head -2
echo "=== RED FAIL lines count ==="
grep -c "   FAIL" "$D/h92_red.txt"
