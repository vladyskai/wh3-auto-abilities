"""Assemble harness113.lua from harness112.lua + the round-113 section.

THREE THINGS HAPPEN HERE, and each is printed so the run is auditable:

1. THE MOCK GAINS THE TWO READS the round-113 rule uses, both documented in the
   battle_unit dump the file was written against:
     * ordered_width()          - "the width of the position to which the unit has
                                  been ordered in metres"
     * initial_number_of_men()  - "the number of soldiers the unit started the
                                  battle with"
   The defaults are chosen so EVERY pre-113 world keeps its exact old geometry
   and its exact old decisions: ordered_width() answers 0 (rejected as insane by
   the mod, which then follows the model count) and initial_number_of_men()
   answers 20 (a multi-model unit, so no world is skipped by the new guard).
   That is not a loosening: a world that wants the new paths sets def.width /
   def.initial_men explicitly, and the new section does.

2. FORMAT / RULE SUPERSESSION. The rule change deliberately retires the
   point-to-point gate, so the checks that pinned it are RE-SPELLED, each with
   the reason and the new quantity in its own label, prefixed `(v113 ...)`.
   Nothing is deleted, and every superseded check still asserts the same KIND of
   thing it always did.

3. The round-113 section is appended and run AFTER 109/110/111/112, so the
   printed total covers all five suites.
"""
import io

BASE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261024_airdrop_enemylead_harness112/harness112.lua"
DST = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261025_airdrop_pathtest_harness113/harness113.lua"
SEC = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261025_airdrop_pathtest_harness113/h113_section.lua"

s = io.open(BASE, encoding="utf-8", newline="").read()
assert "\r" not in s
before_len = len(s)

# ---------------------------------------------------------------- 1. the mock
MOCK_ANCHOR = """      if def.men_alive ~= nil then return def.men_alive end
      return 1
    end
"""

MOCK_NEW = MOCK_ANCHOR + """    -- HARNESS 113: THE TWO READS THE PATH TEST USES, both documented in
    -- battle_unit.lua.
    --   def.width           ordered_width() in metres; ABSENT -> 0, which the mod
    --                       rejects as insane and replaces with the model-count
    --                       derivation, so every pre-113 world keeps its geometry
    --   def.width_raises    the read cannot be taken (the unreadable fallback)
    --   def.initial_men     the STARTING size; ABSENT -> 20 (multi-model), so no
    --                       pre-113 world is skipped by the single-entity guard
    --   def.initial_raises  the read cannot be taken (the fail-closed world)
    function u:ordered_width()
      touch()
      if def.width_raises then error("mock: ordered_width refused", 0) end
      if def.width ~= nil then return def.width end
      return 0
    end
    function u:initial_number_of_men()
      touch()
      if def.initial_raises then error("mock: initial_number_of_men refused", 0) end
      if def.initial_men ~= nil then return def.initial_men end
      return 20
    end
"""
assert s.count(MOCK_ANCHOR) == 1, s.count(MOCK_ANCHOR)
s = s.replace(MOCK_ANCHOR, MOCK_NEW)

# ------------------------------------------------------- 2. superseded checks
# The harness pins some fragments that CONTAIN a backslash-escaped quote (the
# Lua source writes them that way). The two characters are built here so this
# script never has to spell a backslash itself.
BQ = chr(92) + '"'

PAIRS = []

# (a) harness-109 0aa: the picker's GATE. The centre distance no longer decides
#     anything; the PERPENDICULAR distance to the enemy's path does.
PAIRS.append((
    r'''    check("0aa " .. nm .. ": the picker's GATE is the centre distance (one edge read, diagnostic only)",''',
    r'''    -- (v113 RULE SUPERSESSION: the gate is the SEGMENT test now - the centre
    -- distance is a printed diagnostic and decides nothing.)
    check("0aa " .. nm .. ": the picker's GATE is the PERPENDICULAR distance to the enemy's path"
      .. " (v113: was the centre distance; the edge read stays diagnostic-only)",'''))
PAIRS.append((
    r'''      pick ~= nil and raw_find(pick, "gap <= bound", 1, true) ~= nil''',
    r'''      pick ~= nil and raw_find(pick, "perp <= eff", 1, true) ~= nil
      and raw_find(pick, "FOURTH.ad_seg_dist", 1, true) ~= nil'''))

# (b) harness-109 0aa live: the target line pinned `radius=none`. It now names
#     the per-model radius constant AND the frontage credit derived from it.
OLD_B = ('        and raw_find(s2, "' + BQ + ' centre=' + BQ
         + ' .. string.format(' + BQ + '%.1f' + BQ + ', best_gap)", 1, true) ~= nil\n'
         + '        and raw_find(s2, "radius=none", 1, true) ~= nil')
NEW_B = ('        and raw_find(s2, "' + BQ + ' centre=' + BQ
         + ' .. string.format(' + BQ + '%.1f' + BQ + ', best_pgap)", 1, true) ~= nil\n'
         + '        -- (v113 FORMAT SUPERSESSION: `radius=none` was true while the 6 m\n'
         + '        -- constant stood in for the whole footprint. The line now names the\n'
         + '        -- PER-MODEL radius constant, the frontage credit derived from it and\n'
         + '        -- the threshold it produced.)\n'
         + '        and raw_find(s2, "per_model_radius=", 1, true) ~= nil\n'
         + '        and raw_find(s2, "frontage=", 1, true) ~= nil\n'
         + '        and raw_find(s2, "threshold=", 1, true) ~= nil')
PAIRS.append((OLD_B, NEW_B))

# (c) harness-109 0aa ann: the same retired token, pinned ABSENT in the reading copy.
PAIRS.append((
    r'''      check("0aa " .. nm .. ": the position formatter exists in the logic copy too",
        raw_find(s2, "function FOURTH.ad_pos(x, z)", 1, true) ~= nil
        and raw_find(s2, "radius=none", 1, true) == nil)''',
    r'''      check("0aa " .. nm .. ": the position formatter exists in the logic copy too"
        .. " (v113: and the frontage helper with it; `radius=none` is retired)",
        raw_find(s2, "function FOURTH.ad_pos(x, z)", 1, true) ~= nil
        and raw_find(s2, "function FOURTH.ad_frontage(unit, men_now)", 1, true) ~= nil
        and raw_find(s2, "radius=none", 1, true) == nil)'''))

# (d) harness-109 B4c: the log stated `radius=none`; it now states the derived
#     frontage and its PER-MODEL radius source.
PAIRS.append((
    r'''      check(TAG .. "B4c: and the log states radius=none [live log]",
        lg109((TAG ~= "[live] ") or count_log(W, "radius=none") >= 1))''',
    r'''      check(TAG .. "B4c (v113: the frontage credit is DERIVED, not stated absent):"
        .. " the log names the per-model radius constant and the frontage it produced [live log]",
        lg109((TAG ~= "[live] ") or (count_log(W, "per_model_radius=0.60m") >= 1
          and count_log(W, "frontage=0.00m (single, men=1") >= 1)))'''))

# (e) harness-109 0aa: the re-check pinned `FOURTH.ad_project(enemy, ...)`. It now
#     takes ONE ad_lead call - the segment needs the CURRENT point too - and runs
#     the perpendicular test.
PAIRS.append((
    r'''    check("0aa " .. nm .. ": the PRE-CAST re-check runs the SAME centre test",
      rech ~= nil and raw_find(rech, "FOURTH.ad_centre_gap", 1, true) ~= nil
      and raw_find(rech, "FOURTH.eg_enemy_gap", 1, true) == nil)''',
    r'''    check("0aa " .. nm .. ": the PRE-CAST re-check runs the SAME path test"
      .. " (v113: it rebuilds the enemy's SEGMENT and measures the perpendicular distance)",
      rech ~= nil and raw_find(rech, "FOURTH.ad_centre_gap", 1, true) ~= nil
      and raw_find(rech, "FOURTH.ad_seg_dist", 1, true) ~= nil
      and raw_find(rech, "FOURTH.eg_enemy_gap", 1, true) == nil)'''))

# (f) harness-112 0: the picker "gates on the projection".
PAIRS.append((
    r'''      and raw_find(pick, "pgap <= bound", 1, true) ~= nil)''',
    r'''      and raw_find(pick, "perp <= eff", 1, true) ~= nil
      and raw_find(pick, "FOURTH.ad_frontage(enemy, alive)", 1, true) ~= nil)''', 2))
PAIRS.append((
    r'''    check("0 " .. nm .. ": the picker still projects both bodies through ONE helper and gates on the projection",''',
    r'''    check("0 " .. nm .. ": the picker still projects both bodies through ONE helper and gates on the"
      .. " PERPENDICULAR distance to the enemy's path (v113: was the projected centre)",'''))

# (g) harness-112 0: the re-check "re-projects both bodies".
PAIRS.append((
    r'''    check("0 " .. nm .. ": the pre-cast re-check re-projects through the SAME helper (same four dials)",
      rech ~= nil
      and raw_find(rech, "FOURTH.ad_lead(unit, ad_t_now, true)", 1, true) ~= nil
      and raw_find(rech, "FOURTH.ad_project(enemy, ad_t_now)", 1, true) ~= nil)''',
    r'''    check("0 " .. nm .. ": the pre-cast re-check re-projects through the SAME helper (same four dials)"
      .. " AND re-runs the SEGMENT test (v113)",
      rech ~= nil
      and raw_find(rech, "FOURTH.ad_lead(unit, ad_t_now, true)", 1, true) ~= nil
      and raw_find(rech, "FOURTH.ad_lead(enemy, ad_t_now, false)", 1, true) ~= nil
      and raw_find(rech, "FOURTH.ad_seg_dist", 1, true) ~= nil
      and raw_find(rech, "FOURTH.ad_frontage(enemy,", 1, true) ~= nil)'''))

# (h) harness-110 "0ab": the watch line's shape now carries perp + threshold,
#     and its bracket opens on perp rather than on the projected separation.
PAIRS.append((
    r'''        raw_find(s2, '" [projected sep="', 1, true) ~= nil''',
    r'''        -- (v113 FORMAT SUPERSESSION: the bracket now opens on the DECIDING
        -- number - the perpendicular distance - and the point separation is
        -- printed inside it as a diagnostic.)
        raw_find(s2, '" [perp="', 1, true) ~= nil
        and raw_find(s2, '" projected sep="', 1, true) ~= nil'''))
PAIRS.append((
    r'''        and raw_find(s2, "near_gap < 15", 1, true) ~= nil)''',
    r'''        and raw_find(s2, "near_gap < 15", 1, true) ~= nil
        and raw_find(s2, "vs threshold=", 1, true) ~= nil)'''))

# (h2) harness-110 0ab ann: the reading copy's "same logic" test.
PAIRS.append((
    r'''        raw_find(s2, '" (PROJECTED "', 1, true) == nil
        and raw_find(s2, "pgap <= bound", 1, true) ~= nil)''',
    r'''        raw_find(s2, '" (PROJECTED "', 1, true) == nil
        -- (v113 RULE SUPERSESSION: the annotated copy carries the same PATH test -
        -- the segment helper, the frontage helper and the perp gate.)
        and raw_find(s2, "FOURTH.ad_seg_dist(best_ipx, best_ipz, ex, ez, epx, epz)", 1, true) ~= nil
        and raw_find(s2, "FOURTH.ad_frontage(enemy, alive)", 1, true) ~= nil
        and raw_find(s2, "perp <= eff", 1, true) ~= nil)'''))

# (h3) harness-111 0ac: the re-check's fresh projection, again.
PAIRS.append((
    r'''    check("0ac " .. nm .. ": the pre-cast re-check re-projects through the SAME helper (same dials)",
      rech ~= nil
      and raw_find(rech, "FOURTH.ad_lead(unit, ad_t_now, true)", 1, true) ~= nil
      and raw_find(rech, "FOURTH.ad_project(enemy, ad_t_now)", 1, true) ~= nil)''',
    r'''    check("0ac " .. nm .. ": the pre-cast re-check re-projects through the SAME helper (same dials)"
      .. " and rebuilds the SEGMENT (v113)",
      rech ~= nil
      and raw_find(rech, "FOURTH.ad_lead(unit, ad_t_now, true)", 1, true) ~= nil
      and raw_find(rech, "FOURTH.ad_lead(enemy, ad_t_now, false)", 1, true) ~= nil
      and raw_find(rech, "FOURTH.ad_seg_dist(upx, upz, ex2, ez2, epx, epz)", 1, true) ~= nil)'''))

# (i) harness-107 0y: the re-check's own bound test. Same line, new quantity.
PAIRS.append((
    r'''        and raw_find(s2, "local in_bound_now = (gap_now ~= nil and gap_now <= ad_bound_now)", 1, true) ~= nil''',
    r'''        -- (v113 RULE SUPERSESSION: the bound test is the perpendicular distance to
        -- the enemy's path against bound + frontage, not the projected centre.)
        and raw_find(s2, "local in_bound_now = (perp_now ~= nil and perp_now <= eff_now)", 1, true) ~= nil'''))

# (j) harness-110 0ab: the picker's old projected-separation gate.
PAIRS.append((
    r'''    check("0ab " .. nm .. ": the picker projects BOTH bodies and gates on the PROJECTED separation",
      pick ~= nil
      and raw_find(pick, "FOURTH.ad_lead(unit, ad_t, true)", 1, true) ~= nil
      and raw_find(pick, "FOURTH.ad_lead(enemy, ad_t, false)", 1, true) ~= nil
      and raw_find(pick, "FOURTH.ad_sep(best_ipx, best_ipz, epx, epz)", 1, true) ~= nil
      and raw_find(pick, "pgap <= bound", 1, true) ~= nil
      and raw_find(pick, "FOURTH.AIR_DROP_DELAY_S", 1, true) ~= nil)''',
    r'''    check("0ab " .. nm .. ": the picker projects BOTH bodies and gates on the PATH"
      .. " (v113: the perpendicular distance to the enemy's segment vs bound + frontage)",
      pick ~= nil
      and raw_find(pick, "FOURTH.ad_lead(unit, ad_t, true)", 1, true) ~= nil
      and raw_find(pick, "FOURTH.ad_lead(enemy, ad_t, false)", 1, true) ~= nil
      and raw_find(pick, "FOURTH.ad_seg_dist(best_ipx, best_ipz, ex, ez, epx, epz)", 1, true) ~= nil
      and raw_find(pick, "FOURTH.ad_sep(best_ipx, best_ipz, epx, epz)", 1, true) ~= nil
      and raw_find(pick, "perp <= eff", 1, true) ~= nil
      and raw_find(pick, "FOURTH.AIR_DROP_DELAY_S", 1, true) ~= nil)'''))

# (k) harness-110 0ab: the re-check's fresh projection.
PAIRS.append((
    r'''    check("0ab " .. nm .. ": the PRE-CAST re-check RE-PROJECTS both bodies",
      rech ~= nil
      and raw_find(rech, "FOURTH.ad_lead(unit, ad_t_now, true)", 1, true) ~= nil
      and raw_find(rech, "FOURTH.ad_project(enemy, ad_t_now)", 1, true) ~= nil
      and raw_find(rech, "FOURTH.ad_sep(upx, upz, epx, epz)", 1, true) ~= nil
      and raw_find(rech, "FOURTH.AIR_DROP_DELAY_S", 1, true) ~= nil)''',
    r'''    check("0ab " .. nm .. ": the PRE-CAST re-check RE-PROJECTS both bodies AND rebuilds the SEGMENT"
      .. " (v113)",
      rech ~= nil
      and raw_find(rech, "FOURTH.ad_lead(unit, ad_t_now, true)", 1, true) ~= nil
      and raw_find(rech, "FOURTH.ad_lead(enemy, ad_t_now, false)", 1, true) ~= nil
      and raw_find(rech, "FOURTH.ad_seg_dist(upx, upz, ex2, ez2, epx, epz)", 1, true) ~= nil
      and raw_find(rech, "FOURTH.ad_sep(upx, upz, epx, epz)", 1, true) ~= nil
      and raw_find(rech, "FOURTH.AIR_DROP_DELAY_S", 1, true) ~= nil)'''))

# (l) harness-110 0ab: the target line's centre number is now best_pgap (the
#     point separation is a diagnostic; the PATH numbers were added beside it).
PAIRS.append((
    r'''        and raw_find(s2, '" centre=" .. string.format("%.1f", best_gap)', 1, true) ~= nil
        and raw_find(s2, '" now="', 1, true) ~= nil)''',
    r'''        and raw_find(s2, '" centre=" .. string.format("%.1f", best_pgap)', 1, true) ~= nil
        and raw_find(s2, '" now="', 1, true) ~= nil
        -- (v113: the path numbers the rule now decides on)
        and raw_find(s2, '" segment="', 1, true) ~= nil
        and raw_find(s2, '" perp="', 1, true) ~= nil
        and raw_find(s2, '" frontage="', 1, true) ~= nil
        and raw_find(s2, '" threshold="', 1, true) ~= nil)'''))

# (m) harness-110 C2: a RECEDING enemy. The point test refused it (6.80 m at
#     impact); the PATH test fires, because the path's closest approach to the
#     caster's projected point is the enemy's CURRENT 5.00 m - the path STARTS
#     inside the 6 m bound. This is the round-109 answer restored, and it is the
#     user's chosen rule (the segment includes the current point), so the world is
#     REBASED and pinned rather than weakened.
PAIRS.append((
    r'''        check(TAG .. "C2a: 5 m NOW but 11 m at impact - no fire (" .. #W.fires .. ")", #W.fires == 0)
        -- REBASED v112: 5 m + 4 m/s * 0.45 s = 6.80 m projected (was 11 m).
        check(TAG .. "C2b (REBASED v112): the why-not line shows projected 6.80 m from now=5.00 m [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "is centre=5.00m vs bound=6m") == 1
              and count_log(W, "projected sep=6.80m after delay=1.50s") == 1)))''',
    r'''        -- REBASED v113 (the PATH test, the user's ruling): the segment runs from
        -- the enemy's CURRENT point (0, 5) to its projected one (0, 6.8). Its
        -- closest approach to the caster's projected point (0, 0) is the segment's
        -- START - 5.00 m - which is inside bound 6 m + frontage 0 m (a one-model
        -- mock), so the drop FIRES. Under the round-110/112 point test the number
        -- that decided was the PROJECTED 6.80 m and this world stayed silent; the
        -- path rule restores the round-109 answer for an enemy that is inside the
        -- bound RIGHT NOW, and that is exactly what was asked for.
        check(TAG .. "C2a (REBASED v113): the enemy is 5.00 m from the drop point NOW, so its PATH starts"
          .. " inside the bound - FIRES (" .. #W.fires .. ")", #W.fires == 1)
        check(TAG .. "C2b (REBASED v113): the decision line shows perp=5.00m against threshold=6.00m and the"
          .. " old point separation 6.80m as the diagnostic [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "perp=5.00m") >= 1
              and count_log(W, "threshold=6.00m (bound=6m + frontage=0.00m)") >= 1
              and count_log(W, "centre=6.8m (the PROJECTED POINT separation - no longer the test)") >= 1)))'''))

# (n) harness-112 section 0: the ui-id tag is now on FIVE log sites (one
#     definition + five uses: ad_say, target, watch, skip, single-entity skip,
#     re-check).
PAIRS.append((
    r'''      check("0 " .. nm .. ": EVERY air-drop log line is prefixed with the unit's ui id (ad_say + target + skip + re-check)",
        cp112(s2, "FOURTH.ad_tag(unit)") == 5''',
    r'''      check("0 " .. nm .. ": EVERY air-drop log line is prefixed with the unit's ui id"
        .. " (v113: ad_say + target + watch + skip + single-entity skip + re-check = 6 mentions)",
        cp112(s2, "FOURTH.ad_tag(unit)") == 6'''))

# (o) harness-112 A1: the CONTROL world of round 112. Under the point test the 5 m
#     lateral pass projected 6.07 m and stayed SILENT; under the PATH test the
#     segment's closest approach to the caster's projected point is 5.00 m - the
#     enemy's own current point - inside the 6 m bound, so it FIRES. That is the
#     round-113 rule working as asked, so the world is REBASED, not weakened.
PAIRS.append((
    r'''        check(TAG .. "A1a (CONTROL, enemy lead 1.0 = the reported bug): a 5 m lateral pass projects 6.07 m - SILENT ("
          .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "A1b: the log proves the over-carry - projected 6.07 m from 5.00 m now, at enemy_lead=1.00 [live log]",
          lg112((TAG ~= "[live] ")
            or (count_log(W, "projected sep=6.07m after delay=1.50s") >= 1
              and count_log(W, "is centre=5.00m vs bound=6m") >= 1
              and count_log(W, "delay=1.50s enemy_lead=1.00 delay_caster=1.50s caster_lead=0.50") >= 1)))''',
    r'''        -- REBASED v113 (the PATH test): the OVER-CARRY is still there - the
        -- projected CENTRE is 6.07 m, outside the 6 m bound - but the segment
        -- from (105, 200) to (105, 203.45) passes 5.00 m from the caster's
        -- projected point (100, 200), and 5.00 <= 6.00 + 0.00 (a one-model mock
        -- gets no frontage credit), so it FIRES. Under the point test this world
        -- reproduced the miss; under the path test it is the fix. Both numbers
        -- are still printed, so the change stays auditable.
        check(TAG .. "A1a (REBASED v113, the path test): the projected CENTRE is still 6.07 m - outside the"
          .. " 6 m bound - but the path passes 5.00 m from the drop point - FIRES (" .. #W.fires .. ")",
          #W.fires == 1)
        check(TAG .. "A1b (REBASED v113): the decision line shows perp=5.00m vs threshold=6.00m AND the"
          .. " over-carried centre=6.1m beside it, at enemy_lead=1.00 [live log]",
          lg112((TAG ~= "[live] ")
            or (count_log(W, "perp=5.00m") >= 1
              and count_log(W, "threshold=6.00m (bound=6m + frontage=0.00m)") >= 1
              and count_log(W, "centre=6.1m (the PROJECTED POINT separation") >= 1
              and count_log(W, "delay=1.50s enemy_lead=1.00 delay_caster=1.50s caster_lead=0.50") >= 1)))'''))

for item in PAIRS:
    old, new = item[0], item[1]
    want = item[2] if len(item) > 2 else 1
    got = s.count(old)
    assert got == want, (got, want, old[:200])
    s = s.replace(old, new)

# ------------------------------------------------------------- 3. the section
sec = io.open(SEC, encoding="utf-8", newline="").read()
assert "\r" not in sec

ANCHOR = """run_h112()
print("checks: " .. checks .. ", failures: " .. failures)
"""
assert s.count(ANCHOR) == 1, s.count(ANCHOR)
s = s.replace(ANCHOR, sec + "\nrun_h112()\nrun_h113()\n\nprint(\"checks: \" .. checks .. \", failures: \" .. failures)\n")
assert "run_h113()" in sec

io.open(DST, "w", encoding="utf-8", newline="\n").write(s)
print("wrote", DST, len(s), "(from", before_len, "bytes)")
print("superseded check fragments:", len(PAIRS))
