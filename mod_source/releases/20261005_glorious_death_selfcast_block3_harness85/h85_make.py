# -*- coding: utf-8 -*-
"""Assemble harness85.lua from harness84.lua (the shipped harness-84 build).

Adaptations this round (job 1 = Glorious Death self-cast; job 2 = block 3):
  P1  env rename H84 -> H85
  P2  the red-mode banner re-pointed at this round
  P3  the h83 GLORIOUS-DEATH worlds G1/G2 rewritten for self-cast (same check counts)
  P4  the h83 0y glorious-death reason token -> the self-cast reasons
  P5  the h84 W1/W2/W4 worlds rewritten for self-cast (same check counts)
  P6  the h84 0z glorious-death reason tokens -> the self-cast reasons
  P7  the count pins: A4 128->204 / 64->102, B4 64->102, H68 64->102 & 70->108,
      C6c 64->102
  P8  the h83 red branch re-based (n_ok == 10); the h84 red branch (n_ok == 6)
  P9  the h83 + h84 headline/red wording
  P10 splice the new HARNESS 85 section before the final find check
"""
import io, os

TMP = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "h85work")
src = io.open(os.path.join(TMP, "harness84_base.lua"), encoding="utf-8").read()
section = io.open(os.path.join(TMP, "h85_section.lua"), encoding="utf-8").read()

def sub(old, new, label, count=1):
    global src
    n = src.count(old)
    assert n == count, "patch %s: %d matches (want %d)" % (label, n, count)
    src = src.replace(old, new, count)
    print("patch %s: applied" % label)

def cut(start, end, new, label):
    global src
    a = src.count(start)
    assert a == 1, "%s: start x%d" % (label, a)
    i = src.index(start)
    j = src.index(end, i)
    src = src[:i] + new + src[j:]
    print("patch %s: applied (cut %d chars)" % (label, j - i))

# ---- P1 env
sub('-- HARNESS 84 (this round): the env pair is now H84_LIVE / H84_ANN.\n'
    'local LIVE = os.getenv("H84_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"\n'
    'local ANN  = os.getenv("H84_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"\n'
    'local RED_MODE = (os.getenv("H84_LIVE") ~= nil) or (os.getenv("H84_ANN") ~= nil)',
    '-- HARNESS 85 (this round): the env pair is now H85_LIVE / H85_ANN.\n'
    'local LIVE = os.getenv("H85_LIVE") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"\n'
    'local ANN  = os.getenv("H85_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"\n'
    'local RED_MODE = (os.getenv("H85_LIVE") ~= nil) or (os.getenv("H85_ANN") ~= nil)',
    "P1 env")

# ---- P2 banner
banner = (
'if RED_MODE then\n'
'  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - the GLORIOUS-DEATH SELF-CAST + BLOCK-3 (harness-85) checks are")\n'
'  print("   *** the ones EXPECTED to fail: the section-0h source tokens (both files: the 38 block-3 entries, the 91")\n'
'  print("   *** melee_unwavering / 4 charge_or_melee counts, the self-cast cast target, the self-cast reasons), the ADAPTED")\n'
'  print("   *** count pins (A4 204, B4/H68/C6c 102, H68 key map 108), the rewritten Glorious-Death worlds (h83 G1/G2,")\n'
'  print("   *** h84 W1/W2/W4 cast on self) and every X1/X2/X3/S3/F3 world. Every other harness-84-era check PASSES: the")\n'
'  print("   *** snapshot already carries the Slayer list, the grown 64-entry table and the no-hysteresis Ushoran rule. ***")'
)
cut('if RED_MODE then\n  print("   *** RED CONTROL MODE:', '\nend\nprint()\n', banner, "P2 banner")

# ---- P3 h83 G1 + G2 (rewritten for self-cast; check counts preserved)
G = (
"  -- G1. GLORIOUS DEATH - THE SELF-CAST ASSERTION (harness 85). The caster (a\n"
"  --     Slayer) stands in melee with an in-melee SLAYER ally: the trigger\n"
"  --     fires, and the CAST TARGET IS THE OWNER ITSELF - no ally (Slayer or\n"
"  --     otherwise) is EVER passed (the field-test defect was the Lord being\n"
"  --     ordered to walk to the Slayer ally).\n"
"  -- ==========================================================================\n"
"  local function world_g1(PATH, TAG)\n"
"    local W = make_world({ can_perform = true, units = {\n"
"      { name = \"wh3_dlc25_dwf_cha_daemon_slayer\", uid = 9231, owns = { GLAD }, melee = true, wavering = false },\n"
"      { name = \"wh_main_dwf_inf_slayers\", uid = 9232, owns = {}, melee = true, health_percent = 70 },\n"
"      { name = \"wh_main_emp_inf_swordsmen\", uid = 9233, owns = {}, melee = true, health_percent = 40 },\n"
"    }, cards = {\n"
"      { id = \"9231\", state = \"active\", vis = true }, { id = \"9232\", state = \"active\", vis = true },\n"
"      { id = \"9233\", state = \"active\", vis = true },\n"
"    }, bar = { { id = \"b1\", key = GLAD } } })\n"
"    print(\"== \" .. TAG .. \"G1. GLORIOUS DEATH: the cast target is ALWAYS the OWNER, never the Slayer ally == \")\n"
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
"    local b = (tgt ~= nil and tgt == caster and tgt ~= ally_slayer and tgt ~= ally_plain)\n"
"    check(TAG .. \"G1b: the CAST TARGET IS THE OWNER itself, never an ally (caster \" .. tostring(tgt == caster)\n"
"      .. \", slayer ally \" .. tostring(tgt == ally_slayer) .. \", plain ally \" .. tostring(tgt == ally_plain) .. \")\", b)\n"
"    local c = (count_log(W, \"reason: slayer in melee (self-cast)\") == 1)\n"
"    check(TAG .. \"G1c: the reason says self-cast ('slayer in melee (self-cast)') [live log]\", lg(TAG, c))\n"
"    local d = (count_log(W, \"reason: slayer ally in melee (priority)\") == 0)\n"
"    check(TAG .. \"G1d: the OLD ally-target reason never appears [live log]\", lg(TAG, d))\n"
"    note83(W, TAG)\n"
"    tally(W)\n"
"    return a and b and lg(TAG, c) and lg(TAG, d)\n"
"  end\n"
"\n"
"  -- ==========================================================================\n"
"  -- G2. GLORIOUS DEATH - THE SELF ARM (harness 85). The caster (a Slayer) is\n"
"  --     in melee with only a NON-Slayer ally: the self arm fires, cast on\n"
"  --     SELF, reason 'self in melee (self-cast)'; the non-Slayer ally is\n"
"  --     never targeted.\n"
"  -- ==========================================================================\n"
"  local function world_g2(PATH, TAG)\n"
"    local W = make_world({ can_perform = true, units = {\n"
"      { name = \"wh3_dlc25_dwf_cha_daemon_slayer\", uid = 9241, owns = { GLAD }, melee = true, wavering = false },\n"
"      { name = \"wh_main_emp_inf_swordsmen\",       uid = 9242, owns = {}, melee = true, health_percent = 20 },\n"
"    }, cards = {\n"
"      { id = \"9241\", state = \"active\", vis = true }, { id = \"9242\", state = \"active\", vis = true },\n"
"    }, bar = { { id = \"b1\", key = GLAD } } })\n"
"    print(\"== \" .. TAG .. \"G2. GLORIOUS DEATH: Slayer owner in melee, no Slayer ally -> self-cast == \")\n"
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
"    check(TAG .. \"G2a: the Slayer owner self-casts, and the in-melee NON-Slayer ally is NOT targeted (\"\n"
"      .. fire_detail(W) .. \"; target is caster \" .. tostring(tgt == caster) .. \")\", a)\n"
"    local b = (count_log(W, \"reason: self in melee (self-cast)\") == 1)\n"
"    check(TAG .. \"G2b: the reason says self-cast ('self in melee (self-cast)') [live log]\", lg(TAG, b))\n"
"    note83(W, TAG)\n"
"    tally(W)\n"
"    return a and lg(TAG, b)\n"
"  end\n"
"\n"
)
cut("  -- G1. GLORIOUS DEATH - THE ALLY-TARGET ASSERTION.",
    '  print()\n  print("== HARNESS 83 - BLOCK 2', G, "P3 h83 G1/G2")

# ---- P4 the h83 0y reason token
sub('  check("0y live: the glorious-death reasons exist (Slayer ally + Slayer self fallback)",\n'
    '    raw_find(live_src83, \'reason = "slayer ally in melee (priority)"\', 1, true) ~= nil\n'
    '    and raw_find(live_src83, \'reason = "self slayer fallback (in melee)"\', 1, true) ~= nil)',
    '  check("0y live: the glorious-death reasons exist (both self-cast)",\n'
    '    raw_find(live_src83, \'reason = "slayer in melee (self-cast)"\', 1, true) ~= nil\n'
    '    and raw_find(live_src83, \'reason = "self in melee (self-cast)"\', 1, true) ~= nil)',
    "P4 0y reasons")

# ---- P5 the h84 W1/W2/W4 worlds
W1 = (
"  local function world_w1(PATH, TAG)\n"
"    local W = make_world({ can_perform = true, units = {\n"
"      { name = SL_DAEMON, uid = 9401, owns = { GLAD }, melee = false, wavering = false },\n"
"      { name = SL_UNIT,   uid = 9402, owns = {}, melee = true, health_percent = 50 },\n"
"    }, cards = {\n"
"      { id = \"9401\", state = \"active\", vis = true }, { id = \"9402\", state = \"active\", vis = true },\n"
"    }, bar = { { id = \"b1\", key = GLAD } } })\n"
"    print(\"== \" .. TAG .. \"W1. GLORIOUS DEATH: owner NOT in melee + an in-melee SLAYER ally arms it, but the cast is on SELF == \")\n"
"    local ok = pcall(load_world, W, PATH)\n"
"    check(TAG .. \"W1: the file loads\", ok)\n"
"    if not ok then tally(W); return nil end\n"
"    deploy_phases(W); ui(W)\n"
"    sel_event(W, 9401, true); ui(W); ui(W)\n"
"    click(W, badd(\"glorious_death\")); ui(W)\n"
"    W.conflict = true\n"
"    polln(W, 1)\n"
"    local caster = unit_of(W, 9401)\n"
"    local ally = unit_of(W, 9402)\n"
"    local a = (#W.fires == 1 and W.fires[1].uid == 9401 and W.fires[1].key == GLAD)\n"
"    check(TAG .. \"W1a: the owner fired glorious_death exactly once while itself NOT in melee (\"\n"
"      .. fire_detail(W) .. \")\", a)\n"
"    local tgt = fire_target_for(W, 9401)\n"
"    local b = (tgt ~= nil and tgt == caster and tgt ~= ally)\n"
"    check(TAG .. \"W1b: the CAST TARGET IS THE OWNER, not the in-melee SLAYER ally (caster \" .. tostring(tgt == caster)\n"
"      .. \", ally \" .. tostring(tgt == ally) .. \")\", b)\n"
"    local c = (count_log(W, \"reason: slayer in melee (self-cast)\") == 1)\n"
"    check(TAG .. \"W1c: the reason says self-cast [live log]\", lg(TAG, c))\n"
"    note84(W, TAG)\n"
"    tally(W)\n"
"    return a and b and lg(TAG, c)\n"
"  end\n\n"
)
cut("  local function world_w1(PATH, TAG)", '  -- W2 (case b).', W1, "P5 h84 W1")

W2 = (
"  local function world_w2(PATH, TAG)\n"
"    local W = make_world({ can_perform = true, units = {\n"
"      { name = SL_DAEMON,  uid = 9411, owns = { GLAD }, melee = true, wavering = false },\n"
"      { name = NON_SLAYER, uid = 9412, owns = {}, melee = true, health_percent = 20 },\n"
"    }, cards = {\n"
"      { id = \"9411\", state = \"active\", vis = true }, { id = \"9412\", state = \"active\", vis = true },\n"
"    }, bar = { { id = \"b1\", key = GLAD } } })\n"
"    print(\"== \" .. TAG .. \"W2. GLORIOUS DEATH: Slayer owner in melee, no Slayer ally -> self-cast (non-Slayer never targeted) == \")\n"
"    local ok = pcall(load_world, W, PATH)\n"
"    check(TAG .. \"W2: the file loads\", ok)\n"
"    if not ok then tally(W); return nil end\n"
"    deploy_phases(W); ui(W)\n"
"    sel_event(W, 9411, true); ui(W); ui(W)\n"
"    click(W, badd(\"glorious_death\")); ui(W)\n"
"    W.conflict = true\n"
"    polln(W, 1)\n"
"    local caster = unit_of(W, 9411)\n"
"    local ally = unit_of(W, 9412)\n"
"    local tgt = fire_target_for(W, 9411)\n"
"    local a = (#W.fires == 1 and W.fires[1].uid == 9411 and tgt == caster)\n"
"    check(TAG .. \"W2a: with no Slayer ally the Slayer owner casts on SELF (\" .. fire_detail(W)\n"
"      .. \"; target is caster \" .. tostring(tgt == caster) .. \")\", a)\n"
"    local b = (tgt ~= ally)\n"
"    check(TAG .. \"W2b: the in-melee NON-Slayer ally was NOT targeted, even at 20% health\", b)\n"
"    local c = (count_log(W, \"reason: self in melee (self-cast)\") == 1)\n"
"    check(TAG .. \"W2c: the reason says self-cast [live log]\", lg(TAG, c))\n"
"    note84(W, TAG)\n"
"    tally(W)\n"
"    return a and b and lg(TAG, c)\n"
"  end\n\n"
)
cut("  local function world_w2(PATH, TAG)", '  -- W3 (case c).', W2, "P5 h84 W2")

W4 = (
"  local function world_w4(PATH, TAG)\n"
"    local W = make_world({ can_perform = true, units = {\n"
"      { name = SL_DAEMON,  uid = 9431, owns = { GLAD }, melee = true, wavering = false },\n"
"      { name = SL_DOOMR,   uid = 9432, owns = {}, melee = true, health_percent = 90 },\n"
"      { name = NON_SLAYER, uid = 9433, owns = {}, melee = true, health_percent = 20 },\n"
"    }, cards = {\n"
"      { id = \"9431\", state = \"active\", vis = true }, { id = \"9432\", state = \"active\", vis = true },\n"
"      { id = \"9433\", state = \"active\", vis = true },\n"
"    }, bar = { { id = \"b1\", key = GLAD } } })\n"
"    print(\"== \" .. TAG .. \"W4. GLORIOUS DEATH: with TWO in-melee allies the cast still goes to SELF == \")\n"
"    local ok = pcall(load_world, W, PATH)\n"
"    check(TAG .. \"W4: the file loads\", ok)\n"
"    if not ok then tally(W); return nil end\n"
"    deploy_phases(W); ui(W)\n"
"    sel_event(W, 9431, true); ui(W); ui(W)\n"
"    click(W, badd(\"glorious_death\")); ui(W)\n"
"    W.conflict = true\n"
"    polln(W, 1)\n"
"    local caster = unit_of(W, 9431)\n"
"    local slayer = unit_of(W, 9432)\n"
"    local plain = unit_of(W, 9433)\n"
"    local tgt = fire_target_for(W, 9431)\n"
"    local a = (#W.fires == 1 and tgt == caster and tgt ~= slayer and tgt ~= plain)\n"
"    check(TAG .. \"W4a: with a Slayer ally at 90% and a non-Slayer at 20% both in melee, the cast target is still \"\n"
"      .. \"the OWNER (target is caster \" .. tostring(tgt == caster) .. \"; \" .. fire_detail(W) .. \")\", a)\n"
"    local b = (count_log(W, \"reason: slayer in melee (self-cast)\") == 1)\n"
"    check(TAG .. \"W4b: the reason is the self-cast Slayer-arm reason [live log]\", lg(TAG, b))\n"
"    local c = (count_log(W, \"reason: slayer ally in melee (priority)\") == 0)\n"
"    check(TAG .. \"W4c: the OLD ally-target reason never appears [live log]\", lg(TAG, c))\n"
"    note84(W, TAG)\n"
"    tally(W)\n"
"    return a and lg(TAG, b) and lg(TAG, c)\n"
"  end\n\n"
)
cut("  local function world_w4(PATH, TAG)", '  -- W5 (case c, non-Slayer never targeted).', W4, "P5 h84 W4")

# ---- P6 the h84 0z reason tokens
sub('  check("0z live: the Slayer-ally reason exists (\'slayer ally in melee (priority)\')",\n'
    '    raw_find(live_src84, \'reason = "slayer ally in melee (priority)"\', 1, true) ~= nil)\n'
    '  check("0z live: the Slayer self-fallback reason exists (\'self slayer fallback (in melee)\')",\n'
    '    raw_find(live_src84, \'reason = "self slayer fallback (in melee)"\', 1, true) ~= nil)',
    '  check("0z live: the self-cast Slayer reason exists (\'slayer in melee (self-cast)\')",\n'
    '    raw_find(live_src84, \'reason = "slayer in melee (self-cast)"\', 1, true) ~= nil)\n'
    '  check("0z live: the self-cast self reason exists (\'self in melee (self-cast)\')",\n'
    '    raw_find(live_src84, \'reason = "self in melee (self-cast)"\', 1, true) ~= nil)',
    "P6 0z reasons")

# ---- P7 count pins
sub('    a = (it == 128)\n'
    '    check(TAG .. "A4a: with no information the badge paths walked the FULL 64-entry table ("\n'
    '      .. it .. " iterations, 64 per pass - BLOCK 2 grew the table again)", a)\n'
    '    b = ((it / 2) == 64)\n'
    '    check(TAG .. "A4b: 64 abilities per pass, no shortened set (per pass = " .. (it / 2) .. ")", b)',
    '    a = (it == 204)\n'
    '    check(TAG .. "A4a: with no information the badge paths walked the FULL 102-entry table ("\n'
    '      .. it .. " iterations, 102 per pass - BLOCK 3 grew the table again)", a)\n'
    '    b = ((it / 2) == 102)\n'
    '    check(TAG .. "A4b: 102 abilities per pass, no shortened set (per pass = " .. (it / 2) .. ")", b)',
    "P7 A4")
sub('    a = (POLL_ITERS == 64)\n'
    '    check(TAG .. "B4a: an UNKNOWN owned-key cache falls back to the FULL table (got " .. POLL_ITERS\n'
    '      .. ", want 64 - the FULL 64-entry table after BLOCK 2)", a)',
    '    a = (POLL_ITERS == 102)\n'
    '    check(TAG .. "B4a: an UNKNOWN owned-key cache falls back to the FULL table (got " .. POLL_ITERS\n'
    '      .. ", want 102 - the FULL 102-entry table after BLOCK 3)", a)',
    "P7 B4")
sub('  check(TAG .. "H68: the abilities table is reachable (" ..\n'
    '    (ABIL and #ABIL or -1) .. " entries)", ABIL ~= nil and #ABIL == 64)',
    '  check(TAG .. "H68: the abilities table is reachable (" ..\n'
    '    (ABIL and #ABIL or -1) .. " entries)", ABIL ~= nil and #ABIL == 102)',
    "P7 H68 table")
sub('  check(TAG .. "H68: the static key->marker map has all 70 keys (marker_by_key, " .. n_mk .. ")",\n'
    '    MK ~= nil and n_mk == 70)',
    '  check(TAG .. "H68: the static key->marker map has all 108 keys (marker_by_key, " .. n_mk .. ")",\n'
    '    MK ~= nil and n_mk == 108)',
    "P7 H68 map")
sub('    AKEYS == nil or #AKEYS == 70)',
    '    AKEYS == nil or #AKEYS == 108)',
    "P7 H68 array")
sub('  check(TAG .. "C6c: EVERY entry in the table is wired to an evaluate function (" .. wired_n .. "/" .. total\n'
    '      .. ", table of 64 after BLOCK 2)", ABIL ~= nil and wired_n == 64 and total == 64)',
    '  check(TAG .. "C6c: EVERY entry in the table is wired to an evaluate function (" .. wired_n .. "/" .. total\n'
    '      .. ", table of 102 after BLOCK 3)", ABIL ~= nil and wired_n == 102 and total == 102)',
    "P7 C6c")
sub('    return exists == 6 and m_n == 6 and a_n == 2 and m2_n == 4 and wired_n == 64 and two and four',
    '    return exists == 6 and m_n == 6 and a_n == 2 and m2_n == 4 and wired_n == 102 and two and four',
    "P7 C6 return")

# ---- P8 red branches
sub('    -- LINEAGE ADAPTATION (harness 84): this round\'s red snapshot (pre84)\n'
'    -- already carries BLOCK 2, so S1/E1/F1/S2 pass by design - but the\n'
'    -- REWRITTEN U1/G1/G2 worlds (the round\'s own changes) FAIL on it (the old\n'
'    -- Ushoran hysteresis + the old any-in-melee-ally Glorious Death fallback).\n'
'    check("RED CONTROL (harness 83): N/A for the harness-84 round - the pre-edit snapshot already carries "\n'
'      .. "block 2, so S1/E1/F1/S2 pass by design while the REWRITTEN U1/G1/G2 fail: " .. n_ok\n'
'      .. "/14 world results pass (want 8); the round\'s section-0z checks and the adapted 0c/0y pins also fail",\n'
'      n_ok == 8)',
    '    -- LINEAGE ADAPTATION (harness 85): this round\'s red snapshot (pre85)\n'
    '    -- already carries BLOCK 2 + the harness-84 corrections, so S1/E1/F1/S2/U1\n'
    '    -- pass by design and G2\'s ANNOTATED self arm already self-cast - only the\n'
    '    -- rewritten self-cast G1 and the LIVE half of G2 fail.\n'
    '    check("RED CONTROL (harness 83): N/A for the harness-85 round - the pre-edit snapshot already carries "\n'
    '      .. "block 2 + the harness-84 corrections, so S1/E1/F1/S2/U1 pass by design and G2\'s annotated self arm "\n'
    '      .. "already self-cast, while the rewritten self-cast G1 and the live half of G2 fail: " .. n_ok\n'
    '      .. "/14 world results pass (want 11); the round\'s section-0h checks and the adapted count/reason pins also fail",\n'
    '      n_ok == 11)',
    "P8 h83 red")
sub('    -- LINEAGE ADAPTATION (harness 84): this round\'s red snapshot (pre84)\n'
    '    -- already carries the block-1 batch + item 8 AND block 2\'s grown 64-entry\n'
    '    -- table, so every C-world passes by design.\n'
    '    check("RED CONTROL (harness 82): N/A for the harness-84 round - the pre-edit snapshot already carries the "\n'
    '      .. "block-1 batch + item 8 and block 2\'s grown table, so every C-world passes by design (" .. n_ok\n'
    '      .. "/16 world results)", n_ok == 16)',
    '    -- LINEAGE ADAPTATION (harness 85): this round\'s red snapshot (pre85)\n'
    '    -- already carries the block-1 batch + item 8 and the grown table, so every\n'
    '    -- C-world passes by design EXCEPT C6 (whose full-table count pin moved\n'
    '    -- 64 -> 102, so its world result is false on the snapshot).\n'
    '    check("RED CONTROL (harness 82): N/A for the harness-85 round - the pre-edit snapshot already carries the "\n'
    '      .. "block-1 batch + item 8 and the grown table, so every C-world passes by design except C6 (its count "\n'
    '      .. "pin moved 64 -> 102) (" .. n_ok .. "/16 world results, want 14)", n_ok == 14)',
    "P8 h82 red")
sub('    check("RED CONTROL (harness 84): on the pre-edit snapshot the round\'s changes are ABSENT - no Slayer list "\n'
    '      .. "(W0 fails), the old any-in-melee-ally fallback still targets NON-Slayers (W2/W4/W5 fail) and the old Ushoran "\n'
    '      .. "hysteresis still stops the re-fire; only the shared-SILENT world W3 passes by design - " .. n_ok\n'
    '      .. "/12 world results pass (want 2), new fires " .. RED84.fires .. ", new claims " .. RED84.claims,\n'
    '      n_ok == 2)',
    '    check("RED CONTROL (harness 84): on the pre-edit snapshot the Slayer list + the no-hysteresis Ushoran rule "\n'
    '      .. "ALREADY SHIP, so W0 and the shared-SILENT worlds W3/W5 pass by design, and W2\'s annotated self arm already "\n'
    '      .. "self-cast - only the REWRITTEN self-cast W1/W4 and the live half of W2 fail - " .. n_ok\n'
    '      .. "/12 world results pass (want 7), new fires " .. RED84.fires .. ", new claims " .. RED84.claims,\n'
    '      n_ok == 7)',
    "P8 h84 red")

# ---- P9 headlines
sub('    check("HEADLINE (harness 83): BLOCK 2 - the 27 approved in-melee-self entries ride the ONE shared "\n'
    '      .. "evaluator (all fire on the in-melee condition alone), and the FIVE new triggers each carry their "\n'
    '      .. "OWN evaluator with a DISTINCT reason. CORRECTED (harness 84): Glorious Death is SLAYER-ONLY - the "\n'
    '      .. "cast goes to an in-melee SLAYER ally (the land_units type-key list decides), else to the owner itself "\n'
    '      .. "only when the owner is a Slayer and in melee, else silent (a non-Slayer ally is never targeted); and "\n'
    '      .. "the Ghoul King of Ushoran hysteresis is GONE (plain own health <= 75%, limited only by the readiness "\n'
    '      .. "gate + cooldown + back-off). Every earlier suite re-ran unchanged, the count pins adapted for the "\n'
    '      .. "grown 64-entry / 70-key table", n_ok == 14)',
    '    check("HEADLINE (harness 83): BLOCK 2 - the 27 approved in-melee-self entries ride the ONE shared "\n'
    '      .. "evaluator (all fire on the in-melee condition alone), and the FIVE new triggers each carry their "\n'
    '      .. "OWN evaluator with a DISTINCT reason. FIXED (harness 85): Glorious Death keeps the harness-84 "\n'
    '      .. "Slayer-only TRIGGER but now ALWAYS CASTS ON THE OWNER ITSELF (the caster is never ordered to walk to "\n'
    '      .. "an ally); the Ghoul King of Ushoran has no hysteresis (plain own health <= 75%). Every earlier suite "\n'
    '      .. "re-ran unchanged, the count pins adapted for the grown 102-entry / 108-key table", n_ok == 14)',
    "P9 h83 headline")
sub('    check("HEADLINE (harness 84): GLORIOUS DEATH is now SLAYER-ONLY - it fires when a Slayer unit (a Slayer ally, "\n'
    '      .. "preferred; else the owner itself when the owner is a Slayer and in melee) is in melee, decided by the land_units "\n'
    '      .. "type-key list DERIVED FROM THE GAME\'S OWN DATA (exact whole-key equality, no string search); a NON-Slayer ally is "\n'
    '      .. "never targeted and the old any-ally fallback is gone. The GHOUL KING OF USHORAN hysteresis is REMOVED (plain own "\n'
    '      .. "health <= 75%; the readiness gate + engine cooldown + back-off are the only limiters). Every other harness-83-era "\n'
    '      .. "check re-ran unchanged except the forced count/token pins (0c 7 -> 6; the 0y reasons reworded; 0y hysteresis-gone).",\n'
    '      n_ok == 12)',
    '    check("HEADLINE (harness 84): GLORIOUS DEATH keeps the SLAYER-ONLY TRIGGER (the land_units type-key list, exact "\n'
    '      .. "whole-key equality) but FIXED (harness 85) now CASTS ON THE OWNER ITSELF - the caster is never ordered to walk "\n'
    '      .. "to the Slayer ally; a NON-Slayer ally is never targeted. The GHOUL KING OF USHORAN hysteresis is REMOVED "\n'
    '      .. "(plain own health <= 75%). Every other harness-83-era check re-ran unchanged except the forced count/token pins "\n'
    '      .. "(0c 7 -> 6; the 0y reasons reworded; 0y hysteresis-gone).", n_ok == 12)',
    "P9 h84 headline")

# ---- P10 splice the new section
sub('run_h84()\n\ncheck("ZERO search calls by the mod across everything',
    'run_h84()\n\n' + section + '\ncheck("ZERO search calls by the mod across everything',
    "P10 splice")

out = os.path.join(TMP, "harness85.lua")
io.open(out, "w", encoding="utf-8", newline="\n").write(src)
print("harness85.lua written:", len(src), "bytes,", src.count("\n"), "lines")
