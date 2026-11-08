#!/usr/bin/env bash
# Run harness93 GREEN (live+ann) then RED (pre93 snapshot) and report tails.
set -u
D="C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261009_tooltip_lines_harness93"
cd "$LOCALAPPDATA/Temp"
echo "=== GREEN (no env) ==="
env -u H93_LIVE -u H93_ANN -u H93_TWUI uv run --quiet --with lupa python run_mock.py "$D/harness93.lua" > "$D/h93_green.txt" 2>&1
tail -3 "$D/h93_green.txt" | head -2
echo "=== RED (pre93 snapshot) ==="
H93_LIVE="$D/pre93_live.lua" H93_ANN="$D/pre93_ann.lua" H93_TWUI="$D/pre93_twui.xml" uv run --quiet --with lupa python run_mock.py "$D/harness93.lua" > "$D/h93_red.txt" 2>&1
tail -3 "$D/h93_red.txt" | head -2
echo "=== RED FAIL lines count ==="
grep -c "   FAIL" "$D/h93_red.txt"
