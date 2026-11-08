"""Generate build_and_install112.py from the round-111 builder.

Two edits only:
  * ONE superseded FORMAT gate is replaced, not removed: the watch line used to
    be banded at 5 m, so the old gate looked for `" [projected sep=~"`; it now
    demands the exact-metre form AND the 15 m boundary, which is STRICTER;
  * the round-112 paragraph and assertion block are added (the fourth dial, the
    ui-id tag, the exact-metre watch line, the four-dial log text).
Everything else above is carried over untouched - nothing is loosened.
"""
import io
import os

OLD = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261023_airdrop_movingcaster_harness111/build_and_install111.py"
NEW = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261024_airdrop_enemylead_harness112/build_and_install112.py"

s = io.open(OLD, encoding="utf-8", newline="").read()
assert "\r" not in s

# ---------------------------------------------------------------- 1. the gate
OLD_GATE = """assert '" [projected sep=~"' in script_txt and '"m after delay="' in script_txt, \\
    "the watch line does not print the projected band / delay"
"""
NEW_GATE = """# SUPERSEDED IN ROUND 112 (a FORMAT gate, tightened not removed): the watch line
# no longer bands below 15 m - the deciding number is printed exactly - so the gate
# now demands the exact-metre branch AND the 15 m band boundary that keeps the log
# short above it.
assert '" [projected sep="' in script_txt and '" after delay="' in script_txt, \\
    "the watch line does not print the projected distance / delay"
assert 'if near_gap < 15 then' in script_txt and 'string.format("%.2f", near_gap)' in script_txt \\
    and 'math.floor(near_gap / 5) * 5' in script_txt, \\
    "the watch line does not print EXACT metres below 15 m (and a band above it)"
"""
assert s.count(OLD_GATE) == 1
s = s.replace(OLD_GATE, NEW_GATE)

# ---------------------------------------------------------------- 2. docstring
DOC_ANCHOR = """45 -> 46 evaluators.
\"\"\"
"""
DOC_NEW = """45 -> 46 evaluators.

ROUND 112 (2026-10-24): THE ENEMY-SIDE LEAD DIAL + THE TWO DIAGNOSTIC FIXES.
    The Sky-junk diagnosis (docs/WH3_skyjunk_diagnosis.md): four armed, airborne,
    every-poll-evaluated bombers let the zombies walk THROUGH underneath and did
    not fire, because the enemy's projected centre was carried the FULL 1.5 s
    ahead (3.45 m at 2.3 m/s) PAST the hoverer - the projected gap bottomed at
    ~5 m and GREW to 10 m, largest exactly when the enemy was underneath.
    (1) FOURTH.AIR_DROP_ENEMY_LEAD = 0.3 scales ONLY the enemy's velocity term:
        enemy_projected = enemy + v_enemy * AIR_DROP_DELAY_S * AIR_DROP_ENEMY_LEAD.
        0.0 = the enemy's current position; 1.0 = the old full carry; 0.3 ships
        because the release is not instantaneous but 1.5 s is far too much.
    (2) The watch line prints EXACT distances below 15 m (the 6 m bound sat
        inside a 5 m band, so the deciding number was destroyed).
    (3) Every air-drop line is prefixed with the unit's ui id ("[1003] ..."),
        because four identical Sky-junks made the diagnosis a 231 MB log dive.
    (4) The decision/watch/skip/re-check lines print ALL FOUR dials.
    The caster dials, the 6 m bound, AIR_DROP_INHERIT, air_only / no_melee, the
    self-centred cast, the fail-closed reads and the re-projecting pre-cast
    re-check are UNCHANGED. Counts UNCHANGED: 689 entries / 742 keys,
    air_drop_on_infantry 12 / 19.
\"\"\"
"""
assert s.count(DOC_ANCHOR) == 1
s = s.replace(DOC_ANCHOR, DOC_NEW)

# ---------------------------------------------------------------- 3. the block
BLOCK = r'''# ============================================================================
# ROUND 112 (2026-10-24): THE ENEMY-SIDE LEAD DIAL, THE EXACT WATCH DISTANCE AND
# THE UI-ID TAG.
#
#   THE EVIDENCE (docs/WH3_skyjunk_diagnosis.md, pack 651f12e61284cae472bb06bf3a66b87d,
#   session lines 947215-952480): four Sky-junk bombers (ui ids 1002-1005), all
#   armed in one click, all airborne, all evaluated on every poll, infantry
#   candidates present every poll - and three of them NEVER fired while the
#   zombies walked underneath. The rule was satisfied only at a projected centre
#   separation <= 6 m and the projected number bottomed in the 5-10 m band:
#   the enemy's centre was carried v_enemy * 1.5 s = 3.45 m PAST the hoverer, so
#   the projected gap was LARGEST exactly when the enemy was underneath (5 m at
#   the pass, 10 m one second later).
#
#   (1) THE FOURTH DIAL - enemy_projected = enemy + v_enemy * AIR_DROP_DELAY_S
#       * AIR_DROP_ENEMY_LEAD, with FOURTH.AIR_DROP_ENEMY_LEAD = 0.3 shipped.
#       0.0 = the enemy's CURRENT position (impact straight down on where it is);
#       1.0 = the round-110/111 full carry that produced the misses; 0.3 = 0.45 s
#       of lead (~1.0 m at 2.3 m/s, not 3.45 m), because the release is not
#       instantaneous but a full 1.5 s of enemy travel is far too much. It scales
#       the ENEMY's velocity term ONLY.
#   (2) THE WATCH LINE prints EXACT distances (%.2f) below 15 m; the 5 m band
#       survives above 15 m, where the number is context only. Diagnosis D1.
#   (3) EVERY air-drop line carries the unit's ui id - "[1003] sky_junk_bomb
#       watch: ..." - via FOURTH.ad_tag, on the decision line, the watch line,
#       the skip line and both pre-cast lines. Diagnosis D2.
#   (4) The dial text is the FOUR-dial form on every one of those lines:
#       delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=0.50.
#   UNCHANGED: AIR_DROP_DELAY_S = 1.5, AIR_DROP_CASTER_DELAY_S = 1.5,
#       AIR_DROP_CASTER_LEAD = 0.5, AIR_DROP_CENTER_M = 6, AIR_DROP_INHERIT =
#       false, air_only / no_melee, the self-centred cast, every fail-closed read
#       and the pre-cast re-check (same helper => same four dials).
#   Counts UNCHANGED: 689 entries / 742 keys, air_drop_on_infantry 12 / 19.
# ============================================================================
assert script_txt.count("\nFOURTH.AIR_DROP_ENEMY_LEAD = 0.3\n") == 1, \
    "the enemy lead factor is not defined exactly once at 0.3"
assert script_txt.count("\nFOURTH.AIR_DROP_DELAY_S = 1.5\n") == 1, \
    "the shared fall delay moved - the enemy's lead TIME must stay 1.5 s"
assert script_txt.count("\nFOURTH.AIR_DROP_CASTER_DELAY_S = 1.5\n") == 1, \
    "the caster's own lead time moved"
assert script_txt.count("\nFOURTH.AIR_DROP_CASTER_LEAD = 0.5\n") == 1, \
    "the caster lead factor moved"
assert script_txt.count("\nFOURTH.AIR_DROP_CENTER_M = 6\n") == 1, \
    "the 6 m centre bound moved (it must stay exactly one definition)"
assert script_txt.count("\nFOURTH.AIR_DROP_INHERIT = false\n") == 1, \
    "the momentum flag moved or no longer ships FALSE"
_ld0 = script_txt.find("function FOURTH.ad_lead(unit, t, allow_bearing)")
_ld1 = script_txt.find("\nend", _ld0)
_ld = script_txt[_ld0:_ld1]
assert _ld0 > 0 and _ld1 > _ld0, "the projection helper is missing"
assert "local lead_enemy = 1" in _ld and "if allow_bearing ~= true then" in _ld, \
    "the enemy lead is not read on the enemy arm"
assert "FOURTH.AIR_DROP_ENEMY_LEAD" in _ld, "the enemy dial is not used in the projection"
assert "px = x + vx * t * lead_enemy" in _ld and "pz = z + vz * t * lead_enemy" in _ld, \
    "the enemy is not projected as position + v * delay * enemy_lead"
assert 'if type(l_enemy) == "number" and l_enemy >= 0 then lead_enemy = l_enemy end' in _ld, \
    "an unreadable enemy lead does not fall back to the full carry (never to a guess)"
assert "local t_caster, lead_caster = t, 1" in _ld, \
    "the caster's lead locals are missing"
assert "px = x + vx * t_caster * lead_caster" in _ld, \
    "the caster is no longer projected by its own delay x lead (x axis)"
assert "pz = z + vz * t_caster * lead_caster" in _ld, \
    "the caster is no longer projected by its own delay x lead (z axis)"
assert "if allow_bearing and FOURTH.AIR_DROP_INHERIT == true then" in _ld, \
    "the ONE momentum flag no longer adds the caster's lead term a second time"
assert "function FOURTH.ad_dial_text(moving)" in script_txt, "the dial-text helper is missing"
assert '"enemy_lead="' in script_txt and '"delay="' in script_txt, \
    "the dial text does not name the enemy lead and the shared delay"
assert '"delay_caster="' in script_txt and '"caster_lead="' in script_txt, \
    "the dial text does not name both caster dials"
assert script_txt.count("FOURTH.ad_dial_text") == 5, \
    "the dial-text helper must be defined once and called four times (target, watch, skip, re-check)"
assert '.. " from " .. FOURTH.ad_dial_text(best_uspd > 0)' in script_txt, \
    "the decision line does not print the four dials"
assert '" moving caster: lead="' in script_txt, \
    "the moving-caster log fragment is missing"
assert '.. " (" .. FOURTH.ad_dial_text(best_uspd > 0) .. "); enemy v="' in script_txt, \
    "the why-not line does not print the dials beside the caster velocity"
assert "function FOURTH.ad_tag(unit)" in script_txt, "the ui-id tag helper is missing"
assert script_txt.count("FOURTH.ad_tag(unit)") == 5, \
    "the tag must be defined once and prepended to the four air-drop log lines"
assert 'log("  " .. FOURTH.ad_tag(unit) .. marker .. " target: ' in script_txt, \
    "the decision line does not carry the unit tag"
assert 'log("  " .. FOURTH.ad_tag(unit) .. ad_marker_now .. " SKIPPED: ' in script_txt, \
    "the skip line does not carry the unit tag"
assert 'log("  " .. FOURTH.ad_tag(unit) .. ad_marker_now .. " pre-cast re-check: ' in script_txt, \
    "the pre-cast re-check line does not carry the unit tag"
_pk0 = script_txt.find("function FOURTH.ad_pick(unit, routing)")
_pk1 = script_txt.find("\nfunction FOURTH.evaluate_air_drop_on_infantry", _pk0)
_pk = script_txt[_pk0:_pk1]
assert "if near_gap < 15 then" in _pk and 'string.format("%.2f", near_gap)' in _pk, \
    "the watch line does not print the EXACT projected distance below 15 m"
assert 'string.format("%.2f", near_now)' in _pk, \
    "the watch line does not print the EXACT instant distance below 15 m"
assert "math.floor(near_gap / 5) * 5" in _pk and "math.floor(near_now / 5) * 5" in _pk, \
    "the 5 m band above 15 m is gone (the log must not grow per 0.1 m there)"
assert "FOURTH.ad_lead(unit, ad_t, true)" in _pk and "FOURTH.ad_lead(enemy, ad_t, false)" in _pk, \
    "the picker no longer projects both bodies"
assert "pgap <= bound" in _pk, "the picker no longer gates on the projected separation"
assert "FOURTH.AIR_DROP_ENEMY_LEAD" not in _pk, \
    "the picker reads the enemy dial directly instead of the one helper"
_rc0 = script_txt.find("if FOURTH.ad_enemy ~= nil then")
_rc1 = script_txt.find("-- SELF-SUMMON RE-CHECK", _rc0)
_rc = script_txt[_rc0:_rc1]
assert "FOURTH.ad_lead(unit, ad_t_now, true)" in _rc and "FOURTH.ad_project(enemy, ad_t_now)" in _rc, \
    "the pre-cast re-check no longer re-projects both bodies"
assert "FOURTH.AIR_DROP_ENEMY_LEAD" not in _rc and "FOURTH.AIR_DROP_CASTER_LEAD" not in _rc, \
    "the re-check re-derives the dials instead of using the shared helper"
assert "AIR_DROP_ENEMY_LEAD 0.3 -> 0.0" in script_txt, \
    "the tuning guide does not state the enemy-lead fix for a walk-through"
assert "THE FOUR DIALS" in script_txt and "THE DEFAULTS THAT SHIP" in script_txt, \
    "the four-dial tuning table is not in the source"
assert "Only ONE dial changes per test" in script_txt, \
    "the source does not say to change one dial per test"
assert "LOWER the lead: 0.5 -> 0.3 -> 0.0" in script_txt, \
    "the caster-lead tuning order is gone"
assert "fires EARLY while MOVING" in script_txt and "NEVER fires while MOVING" in script_txt \
    and "still EARLY while STATIONARY" in script_txt, \
    "the symptom tuning guide is not in the source"
assert script_txt.count('trigger = "air_drop_on_infantry"') == 12, \
    "the air-drop family is no longer 12 entries"
assert script_txt.count("\t{ marker = ") == 689, "the abilities table is not 689 entries"
assert script_txt.count("ability.range_m = FOURTH.AIR_DROP_CENTER_M") == 1, \
    "the 70% bypass lost its single wiring"
assert "string.find(" not in script_txt, "a string.find call is back in the script"
assert "unit_in_range(" not in script_txt, "an engine unit_in_range call is back"

'''
ANCHOR = "# the main mod must be byte-identical (untouched by this work)\n"
assert s.count(ANCHOR) == 1
s = s.replace(ANCHOR, BLOCK + ANCHOR)

io.open(NEW, "w", encoding="utf-8", newline="\n").write(s)
print("wrote", NEW, os.path.getsize(NEW))
