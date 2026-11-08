"""Generate build_and_install113.py from the round-112 builder.

WHAT CHANGES, and nothing else:
  * the docstring gains the round-113 paragraph;
  * SEVEN superseded gates are REPLACED, not removed - each one now demands the
    round-113 reality (the segment gate, the frontage credit, the fresh ad_lead
    read in the re-check) and several of them are STRICTER than before;
  * a round-113 paragraph + assertion block is added before the "main mod must
    be byte-identical" check.

Everything else - the WebSocket client, the five ship files, the Movie pack
type, the content hashes, the install - is carried over untouched.
"""
import io
import os

OLD = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261024_airdrop_enemylead_harness112/build_and_install112.py"
NEW = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261025_airdrop_pathtest_harness113/build_and_install113.py"

s = io.open(OLD, encoding="utf-8", newline="").read()
assert "\r" not in s

PAIRS = []

# 1. the "no radius read" gate -> the DERIVED frontage gate (stricter: it now
#    demands the constant, the helper and the printed source).
PAIRS.append((
    'assert "radius=none" in script_txt, "the target line does not state that no radius read exists"',
    '# SUPERSEDED IN ROUND 113 (tightened, not removed): `radius=none` was true while\n'
    '# the 6 m constant stood in for the whole footprint. The line now names the\n'
    '# PER-MODEL radius constant, the frontage credit derived from it and the\n'
    '# threshold, so the gate demands all four.\n'
    'assert "per_model_radius=" in script_txt, \\\n'
    '    "the target line does not name the per-model radius constant"\n'
    'assert "frontage=" in script_txt and "threshold=" in script_txt, \\\n'
    '    "the target line does not print the frontage credit and the threshold"\n'
    'assert "function FOURTH.ad_frontage(unit, men_now)" in script_txt, \\\n'
    '    "the frontage helper is missing"'))

# 2. the picker gate: the projected-separation gate -> the segment gate.
PAIRS.append((
    'assert "FOURTH.ad_sep(best_ipx, best_ipz, epx, epz)" in _pk and "pgap <= bound" in _pk, \\',
    '# SUPERSEDED IN ROUND 113: the picker gates on the PERPENDICULAR distance from\n'
    '# the enemy\'s path segment to the caster\'s projected point, plus the frontage.\n'
    'assert "FOURTH.ad_sep(best_ipx, best_ipz, epx, epz)" in _pk and "perp <= eff" in _pk, \\'))

# 3. the re-check's fresh read: ad_project -> one ad_lead + the segment test.
PAIRS.append((
    'assert "FOURTH.ad_lead(unit, ad_t_now, true)" in _rc and "FOURTH.ad_project(enemy, ad_t_now)" in _rc, \\',
    '# SUPERSEDED IN ROUND 113: the re-check takes ONE ad_lead call for the enemy (it\n'
    '# needs the CURRENT point as well as the projected one, to rebuild the segment).\n'
    'assert "FOURTH.ad_lead(unit, ad_t_now, true)" in _rc \\\n'
    '    and "FOURTH.ad_lead(enemy, ad_t_now, false)" in _rc and "FOURTH.ad_seg_dist" in _rc, \\'))

# 4. the re-check's own bound line.
PAIRS.append((
    '"local in_bound_now = (gap_now ~= nil and gap_now <= ad_bound_now)" in _rc, \\',
    '"local in_bound_now = (perp_now ~= nil and perp_now <= eff_now)" in _rc, \\'))

# 5. the printed centre number is the point separation (a diagnostic now).
PAIRS.append((
    'assert \'" centre=" .. string.format("%.1f", best_gap)\' in script_txt, \\',
    'assert \'" centre=" .. string.format("%.1f", best_pgap)\' in script_txt, \\'))

# 6. the ui-id tag now has SIX mentions (one definition + five call sites).
PAIRS.append((
    'assert script_txt.count("FOURTH.ad_tag(unit)") == 5, \\',
    'assert script_txt.count("FOURTH.ad_tag(unit)") == 6, \\'))

# 7. the re-check's `gap_now` now CARRIES the perpendicular distance: the name
#    survives so the bound line reads the same, the quantity does not.
PAIRS.append(("assert \"local gap_now = pgap_now\" in _rc and ",
             "assert \"local gap_now = perp_now\" in _rc and "))

# 8. the watch line's bracket now opens on the deciding number (perp).
PAIRS.append(('assert \'" [projected sep="\' in script_txt',
             'assert \'" [perp="\' in script_txt and \'" projected sep="\' in script_txt'))

# 9. the harness-112 gate on the same token.
PAIRS.append(('assert "pgap <= bound" in _pk, "the picker no longer gates on the projected separation"',
             'assert "perp <= eff" in _pk, "the picker no longer gates on the PERPENDICULAR distance to the enemy path"'))

for old, new in PAIRS:
    n = s.count(old)
    assert n >= 1, (n, old[:120])
    s = s.replace(old, new)

# ---------------------------------------------------------------- the docstring
DOC_ANCHOR = """    air_drop_on_infantry 12 / 19.
\"\"\"
"""
DOC_NEW = """    air_drop_on_infantry 12 / 19.

ROUND 113 (2026-10-25): THE PATH TEST, THE DERIVED FRONTAGE AND THE
SINGLE-ENTITY EXCLUSION (the user's sixth air-drop report: a hovering Sky-junk
BESIDE a 20-model zombie block never fired while the block walked past - the
enemy's CENTRE stayed 10+ m away even though its models swept under the caster;
and one fired at a LORD).
    (1) THE TEST IS THE ENEMY'S PATH, NOT ITS POINT. The segment is
        enemy_current -> enemy_projected (the enemy's own dials, unchanged) and
        the number that decides is the SHORTEST HORIZONTAL DISTANCE FROM THAT
        SEGMENT TO THE CASTER'S PROJECTED POINT (point-to-segment arithmetic on
        x/z, parameter clamped to 0..1). A point cannot describe a block: a
        20-model formation is 10 m wide in two ranks, so its centre stays 10 m
        away while a MODEL of it passes under the flyer.
    (2) THE FRONTAGE CREDIT IS DERIVED, NOT GUESSED: fire when
        perp <= AIR_DROP_CENTER_M + FOURTH.ad_frontage(enemy), where
        ad_frontage returns a HALF-width - ordered_width()/2 when that read is
        sane, otherwise ceil(men/2) * radius under ONE documented assumption
        (two ranks), clamped to 1..12 m, failing closed to 0.
    (3) THE PER-MODEL RADIUS IS A CONSTANT (0.6 m): battle Lua cannot join
        land_units.man_entity -> battle_entities.radius at battle time, so the
        value comes from the extracted tables (modal 0.6 m over the 942 infantry
        rows, median 0.7 m). One dial, documented.
    (4) THE SINGLE-ENTITY EXCLUSION: a candidate whose
        initial_number_of_men() == 1 is skipped, once per episode, as
        "single entity (1 model)". EXACT equality (zero models cannot exist), and
        INITIAL not current (a depleted 20-model block is still a block). The
        commander key set is deliberately NOT consulted here - every
        infantry-class lord/hero in the data is one model, so the count covers it.
    (5) The pre-cast re-check RE-RUNS the same segment test on fresh reads.
    KEPT EXACTLY: the four dials, the 6 m bound, AIR_DROP_INHERIT, air_only /
    no_melee, the self-centred cast and every fail-closed read. Counts UNCHANGED:
    689 entries / 742 keys, air_drop_on_infantry 12 / 19.
\"\"\"
"""
assert s.count(DOC_ANCHOR) == 1
s = s.replace(DOC_ANCHOR, DOC_NEW)

# ---------------------------------------------------------------- the new block
BLOCK = r'''# ============================================================================
# ROUND 113 (2026-10-25): THE PATH TEST, THE DERIVED FRONTAGE AND THE
# SINGLE-ENTITY EXCLUSION.
#
#   THE FIELD REPORT (the user, with a screenshot): a Sky-junk hovering BESIDE a
#   20-model zombie block never fired while the block walked past - the enemy's
#   CENTRE stayed 10+ m away even though its models swept under the caster; and
#   separately one fired at a LORD.
#   THE USER'S RULINGS, verbatim: "1. Why combine? The started with one model
#   would cover the other case, woudn't it? Also, why comparison is 1 or less? It
#   cannot be less, then the unit does not exist. So comparion should be equal to
#   1. Am I forgetting something? If you agree, start implementing with point 2."
#   and "2. Let's implement the the path test with a derived frontage that you
#   suggest."
#
#   (1) THE PATH: segment = enemy_current -> enemy_projected; the deciding number
#       is the shortest horizontal distance from that SEGMENT to the CASTER'S
#       PROJECTED point. A 20-model block is 10 m wide in two ranks, so its
#       centre can stay 10 m away while one of its models passes underneath.
#   (2) THE FRONTAGE CREDIT: perp <= AIR_DROP_CENTER_M + ad_frontage(enemy).
#       ad_frontage returns a HALF-width: ordered_width()/2 when sane, otherwise
#       ceil(men/2) * radius (TWO RANKS - the wide end of the game's own
#       formations), clamped to 1..12 m, failing closed to 0. A one-model unit
#       gets 0: a point has no width.
#   (3) THE RADIUS IS A DOCUMENTED CONSTANT (0.6 m) because battle Lua cannot read
#       land_units.man_entity -> battle_entities.radius; the value is the MODAL
#       infantry radius in the extracted tables (168 of 942 rows), conservative
#       against the 0.7 m median.
#   (4) THE SINGLE-ENTITY EXCLUSION: initial_number_of_men() == 1 is skipped, once
#       per episode, as "single entity (1 model)". EXACT equality, INITIAL not
#       current, and the commander key set is NOT consulted here - every
#       infantry-class lord/hero in the data is one model.
#   (5) The pre-cast re-check RE-RUNS the segment test on fresh reads.
#   KEPT: the four dials, the 6 m bound, AIR_DROP_INHERIT, air_only / no_melee,
#       the self-centred cast, every fail-closed read.
#   Counts UNCHANGED: 689 entries / 742 keys, air_drop_on_infantry 12 / 19.
# ============================================================================
assert script_txt.count("\nFOURTH.AIR_DROP_MODEL_RADIUS_M = 0.6\n") == 1, \
    "the per-model radius constant is not defined exactly once at 0.6"
assert script_txt.count("\nFOURTH.AIR_DROP_RANKS = 2\n") == 1, \
    "the two-rank assumption is not defined exactly once"
assert script_txt.count("\nFOURTH.AIR_DROP_FRONTAGE_MIN_M = 1\n") == 1 \
    and script_txt.count("\nFOURTH.AIR_DROP_FRONTAGE_MAX_M = 12\n") == 1, \
    "the frontage clamp is not 1 .. 12 m, defined exactly once each"
assert script_txt.count("\nFOURTH.AIR_DROP_CENTER_M = 6\n") == 1 \
    and script_txt.count("\nFOURTH.AIR_DROP_DELAY_S = 1.5\n") == 1 \
    and script_txt.count("\nFOURTH.AIR_DROP_ENEMY_LEAD = 0.3\n") == 1 \
    and script_txt.count("\nFOURTH.AIR_DROP_CASTER_DELAY_S = 1.5\n") == 1 \
    and script_txt.count("\nFOURTH.AIR_DROP_CASTER_LEAD = 0.5\n") == 1 \
    and script_txt.count("\nFOURTH.AIR_DROP_INHERIT = false\n") == 1, \
    "one of the SIX older pins moved or was redefined"
_fr0 = script_txt.find("function FOURTH.ad_frontage(unit, men_now)")
_fr1 = script_txt.find("\nfunction FOURTH.ad_frontage_text", _fr0)
_fr = script_txt[_fr0:_fr1]
assert _fr0 > 0 and _fr1 > _fr0, "the frontage helper is missing"
assert "unit:ordered_width()" in _fr and "local half = w * 0.5" in _fr, \
    "the frontage helper does not prefer ordered_width() (halved)"
assert "math.ceil(men / FOURTH.AIR_DROP_RANKS)" in _fr and "FOURTH.AIR_DROP_MODEL_RADIUS_M" in _fr, \
    "the frontage helper does not derive the width from the model count and the radius"
assert "if men < 2 then" in _fr and 'return 0, "single"' in _fr, \
    "a one-model unit is not given zero frontage"
assert 'return 0, "unreadable"' in _fr, "the frontage helper is not fail-closed"
assert _fr.count('return clamped, "clamped"') == 1, "the clamp branch is missing"
_sg0 = script_txt.find("function FOURTH.ad_seg_dist(px, pz, ax, az, bx, bz)")
_sg1 = script_txt.find("\nend", _sg0)
_sg = script_txt[_sg0:_sg1]
assert _sg0 > 0 and _sg1 > _sg0, "the point-to-segment helper is missing"
assert "local t = ((px - ax) * dx + (pz - az) * dz) / len2" in _sg, \
    "the segment helper does not project the point onto the segment"
assert "if t < 0 then" in _sg and "elseif t > 1 then" in _sg, \
    "the segment parameter is not clamped to 0..1 (an END-point miss would read as a hit)"
_pk0 = script_txt.find("function FOURTH.ad_pick(unit, routing)")
_pk1 = script_txt.find("\nfunction FOURTH.evaluate_air_drop_on_infantry", _pk0)
_pk = script_txt[_pk0:_pk1]
assert "local perp = FOURTH.ad_seg_dist(best_ipx, best_ipz, ex, ez, epx, epz)" in _pk, \
    "the picker does not measure the perpendicular distance to the enemy's path"
assert "local eff = bound + half" in _pk and "if perp <= eff and" in _pk, \
    "the picker does not gate on perp vs bound + frontage"
assert "FOURTH.ad_frontage(enemy, alive)" in _pk, \
    "the picker does not credit the candidate's half-frontage"
assert "enemy:initial_number_of_men()" in _pk and "elseif im == 1 then" in _pk, \
    "the picker has no single-entity exclusion (exact equality on the INITIAL size)"
assert "im <= 1" not in _pk, "the single-entity guard is a range test again"
assert "FOURTH.enemy_is_commander" not in _pk, \
    "the commander key set is consulted by this evaluator (the model count covers it)"
_rc0 = script_txt.find("if FOURTH.ad_enemy ~= nil then")
_rc1 = script_txt.find("-- SELF-SUMMON RE-CHECK", _rc0)
_rc = script_txt[_rc0:_rc1]
assert "FOURTH.ad_lead(enemy, ad_t_now, false)" in _rc and "FOURTH.ad_seg_dist(upx, upz, ex2, ez2, epx, epz)" in _rc, \
    "the pre-cast re-check does not rebuild the segment from FRESH reads"
assert "FOURTH.ad_frontage(enemy, (ok_ea and ea) or nil)" in _rc, \
    "the pre-cast re-check does not re-derive the frontage"
assert "local in_bound_now = (perp_now ~= nil and perp_now <= eff_now)" in _rc, \
    "the pre-cast re-check still gates on the projected centre rather than the path"
assert "TWO RANKS DEEP" in script_txt and "battle_entities.radius is 0.6 m (168 rows)" in script_txt, \
    "the formation assumption / the radius evidence is not documented in the source"
assert "1 .. 12 m HALF-width" in script_txt, "the clamp is not documented in the source"
assert "THE COMMANDER KEY SET IS DELIBERATELY NOT USED HERE" in script_txt, \
    "the source does not state that the commander key set is not consulted"
assert 'SKIPPED: " .. why' in script_txt and 'single entity (1 model)' in script_txt, \
    "the once-per-episode single-entity skip line is missing"
assert "FOURTH.ad_se_logged" in script_txt, "the once-per-episode skip bookkeeping is missing"
assert "AIR_DROP_FRONTAGE_MAX_M (12 -> 15 -> 20)" in script_txt, \
    "the tuning guide does not say how to widen the frontage credit"
assert script_txt.count('trigger = "air_drop_on_infantry"') == 12, \
    "the air-drop family is no longer 12 entries"
assert script_txt.count("\t{ marker = ") == 689, "the abilities table is not 689 entries"
assert script_txt.count("FOURTH.ad_dial_text") == 5, \
    "the dial-text helper must be defined once and called four times"
assert script_txt.count("FOURTH.ad_tag(unit)") == 6, \
    "the tag must be defined once and prepended to the five air-drop log sites"
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
