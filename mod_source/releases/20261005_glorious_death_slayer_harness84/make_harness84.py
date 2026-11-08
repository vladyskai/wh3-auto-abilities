# -*- coding: utf-8 -*-
"""Assemble harness84.lua from harness83.lua.

Adaptations this round:
  P1  env rename H83 -> H84
  P2  the red-mode banner re-pointed at this round
  P3  section 0c: the "and not routing" count pin 7 -> 6 (the trigger change)
  P4  section 0y: the Glorious-Death reasons reworded (Slayer ally / Slayer self)
  P5  section 0y: the ushoran_high token check becomes "hysteresis field GONE"
  P6  world_u1 REWRITTEN (no hysteresis: re-fire + the readiness gate limits)
  P7  world_g1 REWRITTEN (Slayer-only targeting)
  P8  world_g2 REWRITTEN (Slayer self fallback, non-Slayer never targeted)
  P9  run_h83's red branch re-based for the pre84 snapshot (n_ok == 8)
  P10 run_h82's red branch re-based for the pre84 snapshot (n_ok == 16)
  P11 header print rename
  P12 run_h83's green HEADLINE re-worded for the corrected rule
  P13 splice the new HARNESS 84 section before the final find check
"""
import io, os

TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "h84work")
src = io.open(os.path.join(TMP, "harness83.lua"), encoding="utf-8").read()
section = io.open(os.path.join(TMP, "h84_section.lua"), encoding="utf-8").read()

def sub(old, new, label, count=1):
    global src
    n = src.count(old)
    assert n == count, "patch %s: %d matches (want %d)" % (label, n, count)
    src = src.replace(old, new, count)
    print("patch %s: applied" % label)

def cut(start, end, new, label, keep_end=True):
    global src
    a = src.count(start)
    assert a == 1, "%s: start x%d" % (label, a)
    i = src.index(start)
    j = src.index(end, i)
    if keep_end:
        region = src[i:j]
        src = src[:i] + new + src[j:]
    print("patch %s: applied (cut %d chars)" % (label, j - i))
    return region if keep_end else None

# ---- P1 env
sub('-- HARNESS 83 (this round): the env pair is now H83_LIVE / H83_ANN.\n'
    'local LIVE = os.getenv("H83_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"\n'
    'local ANN  = os.getenv("H83_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"\n'
    'local RED_MODE = (os.getenv("H83_LIVE") ~= nil) or (os.getenv("H83_ANN") ~= nil)',
    '-- HARNESS 84 (this round): the env pair is now H84_LIVE / H84_ANN.\n'
    'local LIVE = os.getenv("H84_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"\n'
    'local ANN  = os.getenv("H84_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"\n'
    'local RED_MODE = (os.getenv("H84_LIVE") ~= nil) or (os.getenv("H84_ANN") ~= nil)',
    "P1 env")

# ---- P2 banner
banner = (
'if RED_MODE then\n'
'  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - the SLAYER-ONLY TRIGGER + NO-HYSTERESIS (harness-84) checks are")\n'
'  print("   *** the ones EXPECTED to fail: the section-0z source tokens (both files: the Slayer type-key list, the")\n'
'  print("   *** is_slayer reader, the Slayer-filtered ally scan, the Slayer-gated self cast, and the ABSENCE of the")\n'
'  print("   *** hysteresis field), the ADAPTED pins (0c: the and-not-routing count 7 -> 6; 0y: the reworded Glorious-")\n'
'  print("   *** Death reasons and the hysteresis-gone token), the REWRITTEN worlds (U1: no hysteresis; G1/G2: Slayer-only")\n'
'  print("   *** targeting) and every W0-W5 world (no Slayer list; the old any-ally fallback still fires). Every other")\n'
'  print("   *** harness-83-era check PASSES: the snapshot already carries block 2. ***")')
cut('if RED_MODE then\n  print("   *** RED CONTROL MODE:', '\nend\nprint()\n', banner, "P2 banner")

# ---- P3 section 0c guards pin
c0c = (
'  -- HARNESS 84 ADAPTED: the Glorious Death trigger no longer requires the\n'
'  -- OWNER to be in melee, so its own old "... and not routing" outer guard is\n'
'  -- GONE and the count falls 7 -> 6. This is a COUNT PIN the trigger change\n'
'  -- forces; the other trigger paths are untouched (on the pre-edit snapshot\n'
'  -- this pin still reads 7 - see the red control).\n'
'  local guards = count_plain(s, "and not routing")\n'
'  check(nm .. "the not-routing condition sits on every trigger path (and not routing x " .. guards .. ", want 6)", guards == 6)')
cut('  -- BLOCK 2 ADAPTED (harness 83): the count rose 6 -> 7',
    '\n  local timers_a = count_plain(s, "bm:repeat_callback(")', c0c, "P3 0c")

# ---- P4 section 0y glorious-death reasons
y4 = (
'  -- HARNESS 84 ADAPTED: the Glorious Death reasons were REWORDED for the\n'
'  -- Slayer-only candidate set (a Slayer ally, else a SELF cast that is itself\n'
'  -- a Slayer). The old any-in-melee-ally reasons are gone.\n'
'  check("0y live: the glorious-death reasons exist (Slayer ally + Slayer self fallback)",\n'
'    raw_find(live_src83, \'reason = "slayer ally in melee (priority)"\', 1, true) ~= nil\n'
'    and raw_find(live_src83, \'reason = "self slayer fallback (in melee)"\', 1, true) ~= nil)')
cut('  check("0y live: the glorious-death reasons exist (ally priority + self fallback)",',
    '\n  check("0y ann: the reading copy stays log-free and find-free",', y4, "P4 0y reasons")

# ---- P5 section 0y ushoran field
y5 = (
'    -- HARNESS 84 ADAPTED: the Ushoran HYSTERESIS was removed (plain <=75%\n'
'    -- rule), so the old flag field is GONE; the ally-target slot + the\n'
'    -- target-carrying cast stay.\n'
'    check("0y " .. nm .. ": the ally-target slot + the target-carrying cast exist, the Ushoran hysteresis field is GONE",\n'
'      raw_find(s, "FOURTH.cast_target =", 1, true) ~= nil\n'
'      and raw_find(s, "ushoran_high", 1, true) == nil\n'
'      and raw_find(s, "uc:perform_special_ability(ability_key, target or unit)", 1, true) ~= nil)')
cut('    check("0y " .. nm .. ": the ally-target slot + the Ushoran hysteresis field + the target-carrying cast exist",',
    '\n    check("0y " .. nm .. ": the dispatch clears the ally slot before each evaluate', y5, "P5 0y ushoran")

# ---- P6 world_u1
U1 = (
"  local function world_u1(PATH, TAG)\n"
"    local W = make_world({ can_perform = true, units = {\n"
"      { name = \"ushoran_low\", uid = 9221, owns = { USH }, health_percent = 70 },\n"
"      { name = \"ushoran_80\",  uid = 9222, owns = { USH }, health_percent = 80 },\n"
"    }, cards = {\n"
"      { id = \"9221\", state = \"active\", vis = true }, { id = \"9222\", state = \"active\", vis = true },\n"
"    }, bar = { { id = \"b1\", key = USH } } })\n"
"    print(\"== \" .. TAG .. \"U1. GHOUL KING OF USHORAN: health <= 75%, NO hysteresis == \")\n"
"    local ok = pcall(load_world, W, PATH)\n"
"    check(TAG .. \"U1: the file loads\", ok)\n"
"    if not ok then tally(W); return nil end\n"
"    deploy_phases(W); ui(W)\n"
"    sel_group(W, { 9221, 9222 }); ui(W); ui(W)\n"
"    click(W, badd(\"ghoul_king_of_ushoran\")); ui(W)\n"
"    W.conflict = true\n"
"    polln(W, 1)\n"
"    local a = (#W.fires == 1 and W.fires[1].uid == 9221)\n"
"    check(TAG .. \"U1a: only the <=75% unit fired (\" .. fire_detail(W) .. \")\", a)\n"
"    local b = (count_log(W, \"reason: health 70% (<= 75%)\") == 1)\n"
"    check(TAG .. \"U1b: the reason names the live percent ('health 70% (<= 75%)') [live log]\", lg(TAG, b))\n"
"    -- NO HYSTERESIS: health parked at 60%, past the 2 s guard the trigger\n"
"    -- STILL meets its condition and RE-FIRES (the removed hysteresis stopped).\n"
"    set_state(W, 1, { health_percent = 60 })\n"
"    polln(W, 12)\n"
"    local c = (#W.fires == 2 and W.fires[2].uid == 9221)\n"
"    check(TAG .. \"U1c: NO HYSTERESIS - parked at 60% it RE-FIRES after the guard (fires \"\n"
"      .. #W.fires .. \", want 2; the removed hysteresis stopped at 1)\", c)\n"
"    local d = (count_log(W, \"reason: health 60% (<= 75%)\") == 1)\n"
"    check(TAG .. \"U1d: the 60% re-fire names its own percent [live log]\", lg(TAG, d))\n"
"    -- the limiter is the readiness gate, NOT a second health threshold: with\n"
"    -- the engine refusing, no further fire happens across a long window.\n"
"    W.opts.can_perform = false\n"
"    local before = #W.fires\n"
"    polln(W, 12)\n"
"    local e = (#W.fires == before)\n"
"    check(TAG .. \"U1e: the ENGINE refusal holds it - the readiness gate (not a health threshold) limits the \"\n"
"      .. \"repeats (fires \" .. #W.fires .. \", want \" .. before .. \")\", e)\n"
"    local f = (count_log(W, \"health 80%\") == 0)\n"
"    check(TAG .. \"U1f: the 80%-health owner NEVER fired (no 'health 80%' reason anywhere) [live log]\", lg(TAG, f))\n"
"    note83(W, TAG)\n"
"    tally(W)\n"
"    return a and lg(TAG, b) and c and lg(TAG, d) and e and lg(TAG, f)\n"
"  end\n\n")
cut('  local function world_u1(PATH, TAG)',
    '  -- ==========================================================================\n  -- G1. GLORIOUS DEATH', U1, "P6 world_u1")

# ---- P7 world_g1
G1 = (
"  local function world_g1(PATH, TAG)\n"
"    local W = make_world({ can_perform = true, units = {\n"
"      { name = \"wh3_dlc25_dwf_cha_daemon_slayer\", uid = 9231, owns = { GLAD }, melee = true, wavering = false },\n"
"      { name = \"wh_main_dwf_inf_slayers\", uid = 9232, owns = {}, melee = true, health_percent = 70 },\n"
"      { name = \"wh_main_emp_inf_swordsmen\", uid = 9233, owns = {}, melee = true, health_percent = 40 },\n"
"    }, cards = {\n"
"      { id = \"9231\", state = \"active\", vis = true }, { id = \"9232\", state = \"active\", vis = true },\n"
"      { id = \"9233\", state = \"active\", vis = true },\n"
"    }, bar = { { id = \"b1\", key = GLAD } } })\n"
"    print(\"== \" .. TAG .. \"G1. GLORIOUS DEATH: the cast goes to the in-melee SLAYER ALLY, never a non-Slayer == \")\n"
"    local ok = pcall(load_world, W, PATH)\n"
"    check(TAG .. \"G1: the file loads\", ok)\n"
"    if not ok then tally(W); return nil end\n"
"    deploy_phases(W); ui(W)\n"
"    sel_event(W, 9231, true); ui(W); ui(W)\n"
"    click(W, badd(\"glorious_death\")); ui(W)\n"
"    W.conflict = true\n"
"    polln(W, 1)\n"
"    local caster = unit_of(W, 9231)\n"
"    local ally_slayer = unit_of(W, 9232)\n"
"    local ally_plain = unit_of(W, 9233)\n"
"    local a = (#W.fires == 1 and W.fires[1].uid == 9231 and W.fires[1].key == GLAD)\n"
"    check(TAG .. \"G1a: the caster fired glorious_death exactly once (\" .. fire_detail(W) .. \")\", a)\n"
"    local tgt = fire_target_for(W, 9231)\n"
"    local b = (tgt ~= nil and tgt == ally_slayer and tgt ~= caster)\n"
"    check(TAG .. \"G1b: the cast target is the SLAYER ALLY (slayer ally \" .. tostring(tgt == ally_slayer)\n"
"      .. \", caster \" .. tostring(tgt == caster) .. \")\", b)\n"
"    local c = (tgt ~= ally_plain)\n"
"    check(TAG .. \"G1c: the NON-Slayer ally was NOT targeted (its health is lower but it is not a Slayer)\", c)\n"
"    local d = (count_log(W, \"reason: slayer ally in melee (priority)\") == 1)\n"
"    check(TAG .. \"G1d: the reason names the Slayer-ally path [live log]\", lg(TAG, d))\n"
"    note83(W, TAG)\n"
"    tally(W)\n"
"    return a and b and c and lg(TAG, d)\n"
"  end\n\n")
cut('  local function world_g1(PATH, TAG)',
    '  -- ==========================================================================\n  -- G2. GLORIOUS DEATH', G1, "P7 world_g1")

# ---- P8 world_g2 (kept at exactly THREE checks so the harness-83 suite count holds)
G2 = (
"  local function world_g2(PATH, TAG)\n"
"    local W = make_world({ can_perform = true, units = {\n"
"      { name = \"wh3_dlc25_dwf_cha_daemon_slayer\", uid = 9241, owns = { GLAD }, melee = true, wavering = false },\n"
"      { name = \"wh_main_emp_inf_swordsmen\",       uid = 9242, owns = {}, melee = true, health_percent = 20 },\n"
"    }, cards = {\n"
"      { id = \"9241\", state = \"active\", vis = true }, { id = \"9242\", state = \"active\", vis = true },\n"
"    }, bar = { { id = \"b1\", key = GLAD } } })\n"
"    print(\"== \" .. TAG .. \"G2. GLORIOUS DEATH: no Slayer ally -> the Slayer owner self-casts; non-Slayers never targeted == \")\n"
"    local ok = pcall(load_world, W, PATH)\n"
"    check(TAG .. \"G2: the file loads\", ok)\n"
"    if not ok then tally(W); return nil end\n"
"    deploy_phases(W); ui(W)\n"
"    sel_event(W, 9241, true); ui(W); ui(W)\n"
"    click(W, badd(\"glorious_death\")); ui(W)\n"
"    W.conflict = true\n"
"    polln(W, 1)\n"
"    local caster = unit_of(W, 9241)\n"
"    local ally_plain = unit_of(W, 9242)\n"
"    local tgt = fire_target_for(W, 9241)\n"
"    local a = (#W.fires == 1 and W.fires[1].uid == 9241 and tgt == caster and tgt ~= ally_plain)\n"
"    check(TAG .. \"G2a: with no Slayer ally the Slayer owner casts on SELF, and the in-melee NON-Slayer ally is NOT \"\n"
"      .. \"targeted (\" .. fire_detail(W) .. \"; target is caster \" .. tostring(tgt == caster) .. \")\", a)\n"
"    local b = (count_log(W, \"reason: self slayer fallback (in melee)\") == 1)\n"
"    check(TAG .. \"G2b: the reason names the Slayer self fallback [live log]\", lg(TAG, b))\n"
"    note83(W, TAG)\n"
"    tally(W)\n"
"    return a and lg(TAG, b)\n"
"  end\n\n")
cut('  local function world_g2(PATH, TAG)',
    '  print()\n  print("== HARNESS 83 - BLOCK 2', G2, "P8 world_g2")

# ---- P9 run_h83 red branch
r83 = (
'    -- LINEAGE ADAPTATION (harness 84): this round\'s red snapshot (pre84)\n'
'    -- already carries BLOCK 2, so S1/E1/F1/S2 pass by design - but the\n'
'    -- REWRITTEN U1/G1/G2 worlds (the round\'s own changes) FAIL on it (the old\n'
'    -- Ushoran hysteresis + the old any-in-melee-ally Glorious Death fallback).\n'
'    check("RED CONTROL (harness 83): N/A for the harness-84 round - the pre-edit snapshot already carries "\n'
'      .. "block 2, so S1/E1/F1/S2 pass by design while the REWRITTEN U1/G1/G2 fail: " .. n_ok\n'
'      .. "/14 world results pass (want 8); the round\'s section-0z checks and the adapted 0c/0y pins also fail",\n'
'      n_ok == 8)')
cut('    check("RED CONTROL (harness 83): on the pre-BLOCK-2 snapshot the block-2 entries are ABSENT - new "',
    '\n  end\nend\nrun_h83()', r83, "P9 h83 red")

# ---- P10 run_h82 red branch
r82 = (
'    -- LINEAGE ADAPTATION (harness 84): this round\'s red snapshot (pre84)\n'
'    -- already carries the block-1 batch + item 8 AND block 2\'s grown 64-entry\n'
'    -- table, so every C-world passes by design.\n'
'    check("RED CONTROL (harness 82): N/A for the harness-84 round - the pre-edit snapshot already carries the "\n'
'      .. "block-1 batch + item 8 and block 2\'s grown table, so every C-world passes by design (" .. n_ok\n'
'      .. "/16 world results)", n_ok == 16)')
cut('    -- BLOCK 2 ADAPTED (harness 83): the red snapshot for THIS round is the',
    '\n  end\nend\nrun_h82()', r82, "P10 h82 red")

# ---- P11 header print
sub('print("== harness 82: file mode ==")', 'print("== harness 84: file mode ==")', "P11 header")

# ---- P12 run_h83 green HEADLINE
head = (
'    check("HEADLINE (harness 83): BLOCK 2 - the 27 approved in-melee-self entries ride the ONE shared "\n'
'      .. "evaluator (all fire on the in-melee condition alone), and the FIVE new triggers each carry their "\n'
'      .. "OWN evaluator with a DISTINCT reason. CORRECTED (harness 84): Glorious Death is SLAYER-ONLY - the "\n'
'      .. "cast goes to an in-melee SLAYER ally (the land_units type-key list decides), else to the owner itself "\n'
'      .. "only when the owner is a Slayer and in melee, else silent (a non-Slayer ally is never targeted); and "\n'
'      .. "the Ghoul King of Ushoran hysteresis is GONE (plain own health <= 75%, limited only by the readiness "\n'
'      .. "gate + cooldown + back-off). Every earlier suite re-ran unchanged, the count pins adapted for the "\n'
'      .. "grown 64-entry / 70-key table"')
cut('    check("HEADLINE (harness 83): BLOCK 2', ', n_ok == 14)', head, "P12 headline")

# ---- P13 splice the new section
sub('run_h83()\n\n\ncheck("ZERO search calls by the mod across everything',
    'run_h83()\n\n\n' + section + '\ncheck("ZERO search calls by the mod across everything',
    "P13 splice")

out = os.path.join(TMP, "harness84.lua")
io.open(out, "w", encoding="utf-8", newline="\n").write(src)
print("harness84.lua written:", len(src), "bytes,", src.count("\n"), "lines")
