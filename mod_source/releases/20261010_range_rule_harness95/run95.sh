#!/usr/bin/env bash
# Run harness95 GREEN (live+ann) then RED (pre95 snapshot) and report tails.
set -u
D="C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261010_range_rule_harness95"
cd "$LOCALAPPDATA/Temp"
echo "=== GREEN (no env) ==="
env -u H95_LIVE -u H95_ANN uv run --quiet --with lupa python run_mock.py "$D/harness95.lua" > "$D/h95_green.txt" 2>&1
tail -3 "$D/h95_green.txt" | head -2
echo "=== RED (pre95 snapshot) ==="
H95_LIVE="$D/pre95_live.lua" H95_ANN="$D/pre95_ann.lua" uv run --quiet --with lupa python run_mock.py "$D/harness95.lua" > "$D/h95_red.txt" 2>&1
tail -3 "$D/h95_red.txt" | head -2
echo "=== RED FAIL lines count ==="
grep -c "   FAIL" "$D/h95_red.txt"
