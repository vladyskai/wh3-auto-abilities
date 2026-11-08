-- ============================================================================
-- HARNESS 88 - THE BIG IMPLEMENTATION ROUND: BLOCKS 4, 5 AND 6 + THE TWO
--   NEW TRIGGER TYPES.
--   * 87 new ability entries. 80 ride the SHARED melee_unwavering evaluator
--     (54 block-4/5 approved in-melee-self + 26 auto-accepted trivial
--     self-buffs: 15 from block 5 and 11 from block 6's standing rule 9) and
--     5 ride the EXISTING charge_or_melee evaluator (the block-4/5
--     charge-and-in-melee approvals) - NO new evaluator, NO new chunk locals.
--     The table grows 102 -> 189 entries (108 -> 195 keys).
--   * TWO NEW TRIGGER TYPES (the user's just-designed decisions):
--       WILL OF THE VERMINKING (trigger verminking_wavering) - fire when ANY
--         friendly unit other than the caster is IN MELEE and WAVERING and
--         within a DELIBERATELY CONSERVATIVE FOURTH.VERMINKING_RANGE_M
--         (25 m; the ability's game data gives a 35 m ally aura) of the
--         owner; CAST ON SELF. The SAME safety pattern as Glorious Death:
--         the CLOSEST qualifying ally is chosen, the gap is RE-CHECKED
--         immediately before the cast, and the cast is SKIPPED on drift.
--       POTION OF TOUGHNESS (trigger melee_health75) - a ONE-TIME activation
--         treated as a heal: fire when the OWNER is IN MELEE and its own
--         health is <= 75% (the SAME live health read and plain hysteresis-
--         free threshold style as Ghoul King of Ushoran; no second threshold).
--   ADAPTED COUNT PINS (the table grew, in the earlier body sections):
--     A4 204 -> 378 (102 -> 189 per pass), B4 102 -> 189, H68 #ABIL
--     102 -> 189 / marker map 108 -> 195 / key array 108 -> 195, C6c
--     102 -> 189 (both the check and the C6 world return), 0h
--     melee_unwavering 91 -> 171 / charge_or_melee 4 -> 9, 0c not-routing
--     guards 6 -> 7 (the potion evaluator adds the one in-melee guard).
--   RED CONTROL: with H88_LIVE / H88_ANN pointing at the pre-edit snapshot
--     (the shipped harness-87 build, 102 entries) ONLY the adapted count pins
--     and this HARNESS-88 section fail; every earlier world passes by design.
-- ============================================================================

if not RED_MODE then
  check("the WHOLE harness-87 suite (2189 checks before the final find check) still re-ran unchanged (checks so far = " .. checks .. ")",
    checks == 2189)
else
  print("   (red mode: the harness-87 suite boundary check is green-only - the red build skips some"
    .. " RED_MODE-gated checks, so its running count is lowered by design)")
end

local function run_h88()
  local VM  = "wh3_dlc29_lord_abilities_will_of_the_verminking"
  local POT = "wh_main_item_abilities_potion_of_toughness"

  local live_src88 = read_file(LIVE)
  local ann_src88  = read_file(ANN)
  local RED88 = { fires = 0, claims = 0, ui = 0 }
  local function posv(v) return (v == true) or (type(v) == "number") end
  local function lg(tag, v) return (tag ~= "[live] ") or posv(v) end
  local function badd(marker) return "zz_auto_badge_" .. marker end
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function note88(W, TAG)
    RED88.ui = RED88.ui + (W.ui_failures or 0)
    if TAG == "[live] " then
      RED88.fires = RED88.fires + #W.fires
      RED88.claims = RED88.claims + count_log(W, "claim: ")
    end
  end

  -- a SAMPLE of the newly added entries (marker, key), one per group.
  local SAMPLE_SELF = {
    { "quickblood",       "wh3_dlc29_lord_abilities_lightning_reflexes" },
    { "the_eternal_blade","wh3_main_weapon_abilities_the_eternal_blade" },
    { "the_slayer_sword", "wh3_dlc26_weapon_abilities_the_slayer_sword" },
    { "runefang",         "wh_main_weapon_abilities_runefang" },
  }
  local SAMPLE_CHARGE = {
    { "star_lance",       "wh2_dlc15_weapon_abilities_star_lance" },
  }
  local SAMPLE_AUTO = {
    { "potion_of_strength", "wh_main_item_abilities_potion_of_strength" },
    { "doom_glaive",        "wh3_dlc29_item_abilities_doom_glaive" },
  }

  -- --------------------------------------------------------- 0m: tokens (both files)
  print("== HARNESS 88 - section 0m: the BLOCK 4/5/6 entries + the two new triggers (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src88 }, { name = "ann", src = ann_src88 } }) do
    local nm, s = f.name, f.src
    -- the sample entries of every new group are present (marker + badge + key)
    local n_s, n_c, n_a = 0, 0, 0
    for _, e in ipairs(SAMPLE_SELF) do
      if raw_find(s, 'marker = "' .. e[1] .. '"', 1, true) ~= nil
        and raw_find(s, 'badge = "zz_auto_badge_' .. e[1] .. '"', 1, true) ~= nil
        and raw_find(s, '"' .. e[2] .. '"', 1, true) ~= nil then n_s = n_s + 1 end
    end
    for _, e in ipairs(SAMPLE_CHARGE) do
      if raw_find(s, 'marker = "' .. e[1] .. '"', 1, true) ~= nil
        and raw_find(s, '"' .. e[2] .. '"', 1, true) ~= nil then n_c = n_c + 1 end
    end
    for _, e in ipairs(SAMPLE_AUTO) do
      if raw_find(s, 'marker = "' .. e[1] .. '"', 1, true) ~= nil
        and raw_find(s, '"' .. e[2] .. '"', 1, true) ~= nil then n_a = n_a + 1 end
    end
    check("0m " .. nm .. ": the newly added in-melee-self entries are present (marker+badge+key: "
      .. n_s .. "/" .. #SAMPLE_SELF .. ")", n_s == #SAMPLE_SELF)
    check("0m " .. nm .. ": the newly added charge-or-melee entries are present (" .. n_c
      .. "/" .. #SAMPLE_CHARGE .. ")", n_c == #SAMPLE_CHARGE)
    check("0m " .. nm .. ": the block-6 auto-accepted entries are present (" .. n_a
      .. "/" .. #SAMPLE_AUTO .. ")", n_a == #SAMPLE_AUTO)
    -- the trigger counts (the adapted pins H68/C6c/0h check totals too)
    check("0m " .. nm .. ": the melee_unwavering entry count is 171 (got " .. cp(s, 'trigger = "melee_unwavering"') .. ")",
      cp(s, 'trigger = "melee_unwavering"') == 171)
    check("0m " .. nm .. ": the charge_or_melee entry count is 9 (got " .. cp(s, 'trigger = "charge_or_melee"') .. ")",
      cp(s, 'trigger = "charge_or_melee"') == 9)
    -- NEW TRIGGER 1: Will of the Verminking
    check("0m " .. nm .. ": Will of the Verminking is in the table (marker+badge+key+trigger)",
      raw_find(s, 'marker = "will_of_the_verminking"', 1, true) ~= nil
      and raw_find(s, 'badge = "zz_auto_badge_will_of_the_verminking"', 1, true) ~= nil
      and raw_find(s, '"' .. VM .. '"', 1, true) ~= nil
      and raw_find(s, 'trigger = "verminking_wavering"', 1, true) ~= nil)
    check("0m " .. nm .. ": the Verminking range is a DELIBERATELY CONSERVATIVE 25 m (FOURTH.VERMINKING_RANGE_M = 25)",
      raw_find(s, "FOURTH.VERMINKING_RANGE_M = 25", 1, true) ~= nil)
    check("0m " .. nm .. ": the range constant's comment names the game-data 35 m aura (the source of the number)",
      raw_find(s, "effect_range =", 1, true) ~= nil
      and raw_find(s, "35 m", 1, true) ~= nil)
    check("0m " .. nm .. ": the Verminking evaluator + the two gap helpers exist",
      raw_find(s, "function FOURTH.evaluate_verminking_wavering(unit, routing)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.vm_ally_gap(unit, ally)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.vm_ally_in_range(unit, ally)", 1, true) ~= nil)
    check("0m " .. nm .. ": the Verminking chosen-ally field is only ever set by the ally arm (vm_ally = nil x3)",
      cp(s, "FOURTH.vm_ally = nil") == 3)
    check("0m " .. nm .. ": the Verminking gate uses the ONE named range constant",
      raw_find(s, "gap <= FOURTH.VERMINKING_RANGE_M", 1, true) ~= nil)
    check("0m " .. nm .. ": the Verminking cast target rides the DEFAULT (target or unit) - no cast_target write (still x2)",
      cp(s, "FOURTH.cast_target = unit") == 2)
    -- NEW TRIGGER 2: Potion of Toughness
    check("0m " .. nm .. ": Potion of Toughness is in the table (marker+badge+key+trigger)",
      raw_find(s, 'marker = "potion_of_toughness"', 1, true) ~= nil
      and raw_find(s, 'badge = "zz_auto_badge_potion_of_toughness"', 1, true) ~= nil
      and raw_find(s, '"' .. POT .. '"', 1, true) ~= nil
      and raw_find(s, 'trigger = "melee_health75"', 1, true) ~= nil)
    check("0m " .. nm .. ": the Potion evaluator exists and reuses the live health read + the <= 75% threshold",
      raw_find(s, "function FOURTH.evaluate_potion_health(unit, routing)", 1, true) ~= nil
      and raw_find(s, 'FOURTH.context_value(unit, "HealthPercent")', 1, true) ~= nil
      and raw_find(s, "hp <= 75 then", 1, true) ~= nil)
    check("0m " .. nm .. ": the two new triggers are wired in the evaluator map",
      raw_find(s, "verminking_wavering = FOURTH.evaluate_verminking_wavering,", 1, true) ~= nil
      and raw_find(s, "melee_health75 = FOURTH.evaluate_potion_health,", 1, true) ~= nil)
    -- the ARMY-BAR standard: no army-bar key may ever enter the mod
    check("0m " .. nm .. ": NO army-bar key is in the mod (the standing exclusion rule)",
      raw_find(s, "army_abilities", 1, true) == nil)
  end
  check("0m live: the Verminking drift skip is reported ('will_of_the_verminking SKIPPED:')",
    raw_find(live_src88, "will_of_the_verminking SKIPPED:", 1, true) ~= nil)
  check("0m live: the Verminking chosen-ally line exists ('will_of_the_verminking ally: ui')",
    raw_find(live_src88, "will_of_the_verminking ally: ui", 1, true) ~= nil)
  check("0m live: the Verminking self-cast reason exists",
    raw_find(live_src88, 'reason = "wavering ally in melee (self-cast)"', 1, true) ~= nil)
  check("0m live: the Potion in-melee health reason exists",
    raw_find(live_src88, 'string.format("in melee, health %d%% (<= 75%%)"', 1, true) ~= nil)
  check("0m ann: the reading copy stays log-free and find-free",
    raw_find(ann_src88, "log(", 1, true) == nil and raw_find(ann_src88, "string.find(", 1, true) == nil)

  -- ==========================================================================
  -- V1. WILL OF THE VERMINKING: an ally WITHIN range is in melee and WAVERING
  --     -> the owner fires, CAST ON SELF (the owner is NOT in melee).
  -- ==========================================================================
  local function world_v1(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "skreech", uid = 9701, owns = { VM }, melee = false, wavering = false },
      { name = "clanrats", uid = 9702, owns = {}, melee = true, wavering = true, dist = 20 },
    }, cards = {
      { id = "9701", state = "active", vis = true }, { id = "9702", state = "active", vis = true },
    }, bar = { { id = "b1", key = VM } } })
    print("== " .. TAG .. "V1. VERMINKING: a wavering in-melee ally WITHIN 25 m (20 m) arms it (owner NOT in melee) == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "V1: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9701, true); ui(W); ui(W)
    click(W, badd("will_of_the_verminking")); ui(W)
    W.conflict = true
    polln(W, 1)
    local caster = unit_of(W, 9701)
    local ally = unit_of(W, 9702)
    local a = (#W.fires == 1 and W.fires[1].uid == 9701 and W.fires[1].key == VM)
    check(TAG .. "V1a: the owner fired will_of_the_verminking exactly once (" .. fire_detail(W) .. ")", a)
    local tgt = fire_target_for(W, 9701)
    local b = (tgt ~= nil and tgt == caster and tgt ~= ally)
    check(TAG .. "V1b: the cast target is the OWNER itself (caster " .. tostring(tgt == caster)
      .. ", ally " .. tostring(tgt == ally) .. ")", b)
    local c = (count_log(W, "reason: wavering ally in melee (self-cast)") == 1)
    check(TAG .. "V1c: the reason is the wavering-ally self-cast reason [live log]", lg(TAG, c))
    local d = (count_log(W, "will_of_the_verminking ally: ui 9702 at 20.0m") == 1)
    check(TAG .. "V1d: the chosen-ally line names ui 9702 at 20.0m [live log]", lg(TAG, d))
    note88(W, TAG)
    tally(W)
    return a and b and lg(TAG, c) and lg(TAG, d)
  end

  -- ==========================================================================
  -- V2. The wavering ally is BEYOND the conservative 25 m (55 m) -> SILENT.
  -- ==========================================================================
  local function world_v2(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "skreech", uid = 9711, owns = { VM }, melee = false, wavering = false },
      { name = "clanrats", uid = 9712, owns = {}, melee = true, wavering = true, dist = 55 },
    }, cards = {
      { id = "9711", state = "active", vis = true }, { id = "9712", state = "active", vis = true },
    }, bar = { { id = "b1", key = VM } } })
    print("== " .. TAG .. "V2. VERMINKING: a wavering in-melee ally BEYOND 25 m (55 m) -> NOTHING fires == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "V2: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9711, true); ui(W); ui(W)
    click(W, badd("will_of_the_verminking")); ui(W)
    W.conflict = true
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "V2a: the 55 m ally is OUT of the 25 m trigger range -> NO cast (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "will_of_the_verminking ally: ui") == 0)
    check(TAG .. "V2b: no ally is chosen (no chosen-ally line) [live log]", lg(TAG, b))
    note88(W, TAG)
    tally(W)
    return a and lg(TAG, b)
  end

  -- ==========================================================================
  -- V3. The ally is in melee but NOT WAVERING -> SILENT (the wavering test).
  -- ==========================================================================
  local function world_v3(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "skreech", uid = 9721, owns = { VM }, melee = false, wavering = false },
      { name = "clanrats", uid = 9722, owns = {}, melee = true, wavering = false, dist = 20 },
    }, cards = {
      { id = "9721", state = "active", vis = true }, { id = "9722", state = "active", vis = true },
    }, bar = { { id = "b1", key = VM } } })
    print("== " .. TAG .. "V3. VERMINKING: an in-melee ally that is NOT wavering -> SILENT == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "V3: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9721, true); ui(W); ui(W)
    click(W, badd("will_of_the_verminking")); ui(W)
    W.conflict = true
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "V3a: an in-melee ally whose morale is NOT wavering never arms it (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "will_of_the_verminking ally: ui") == 0)
    check(TAG .. "V3b: no ally is chosen [live log]", lg(TAG, b))
    note88(W, TAG)
    tally(W)
    return a and lg(TAG, b)
  end

  -- ==========================================================================
  -- V4. DRIFT: the wavering ally is in range at DECIDE (20 m) but out at CAST
  --     (55 m) -> the cast is SKIPPED rather than wasted.
  -- ==========================================================================
  local function world_v4(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "skreech", uid = 9731, owns = { VM }, melee = false, wavering = false },
      { name = "clanrats", uid = 9732, owns = {}, melee = true, wavering = true, dist_seq = { 20, 55 } },
    }, cards = {
      { id = "9731", state = "active", vis = true }, { id = "9732", state = "active", vis = true },
    }, bar = { { id = "b1", key = VM } } })
    print("== " .. TAG .. "V4. VERMINKING: the wavering ally DRIFTS out of range between decide and cast -> SKIP == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "V4: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9731, true); ui(W); ui(W)
    click(W, badd("will_of_the_verminking")); ui(W)
    W.conflict = true
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "V4a: the ally was in range at decide but out at cast -> the cast is SKIPPED ("
      .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "will_of_the_verminking SKIPPED") == 1)
    check(TAG .. "V4b: the drift skip is reported [live log]", lg(TAG, b))
    local c = (count_log(W, "will_of_the_verminking ally: ui 9732 at 20.0m") == 1)
    check(TAG .. "V4c: the decision DID see the ally at 20.0m before the re-check [live log]", lg(TAG, c))
    note88(W, TAG)
    tally(W)
    return a and lg(TAG, b) and lg(TAG, c)
  end

  -- ==========================================================================
  -- V5. TWO wavering in-melee allies, one NEARER -> the CLOSEST is chosen.
  --     The FARTHER is defined FIRST, so a naive first-match scan picks it.
  -- ==========================================================================
  local function world_v5(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "skreech", uid = 9741, owns = { VM }, melee = false, wavering = false },
      { name = "clanrats", uid = 9742, owns = {}, melee = true, wavering = true, dist = 22 }, -- farther, first
      { name = "stormvermin", uid = 9743, owns = {}, melee = true, wavering = true, dist = 8 }, -- nearer
    }, cards = {
      { id = "9741", state = "active", vis = true }, { id = "9742", state = "active", vis = true },
      { id = "9743", state = "active", vis = true },
    }, bar = { { id = "b1", key = VM } } })
    print("== " .. TAG .. "V5. VERMINKING: two wavering in-melee allies, the NEARER one is chosen == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "V5: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9741, true); ui(W); ui(W)
    click(W, badd("will_of_the_verminking")); ui(W)
    W.conflict = true
    polln(W, 1)
    local a = (#W.fires == 1 and W.fires[1].uid == 9741 and W.fires[1].key == VM)
    check(TAG .. "V5a: a wavering in-melee ally arms it (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "will_of_the_verminking ally: ui 9743") == 1)
    check(TAG .. "V5b: the NEARER ally (ui 9743 at 8.0m) is CHOSEN [live log]", lg(TAG, b))
    local c = (count_log(W, "will_of_the_verminking ally: ui 9742") == 0)
    check(TAG .. "V5c: the FARTHER ally (ui 9742 at 22.0m) is never chosen [live log]", lg(TAG, c))
    note88(W, TAG)
    tally(W)
    return a and lg(TAG, b) and lg(TAG, c)
  end

  -- ==========================================================================
  -- Q1. POTION OF TOUGHNESS: in melee + 70% health -> FIRES.
  -- ==========================================================================
  local function world_q1(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "potionier", uid = 9801, owns = { POT }, melee = true, wavering = false, health_percent = 70 },
    }, cards = {
      { id = "9801", state = "active", vis = true },
    }, bar = { { id = "b1", key = POT } } })
    print("== " .. TAG .. "Q1. POTION OF TOUGHNESS: in melee + 70% health -> FIRES == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "Q1: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9801, true); ui(W); ui(W)
    click(W, badd("potion_of_toughness")); ui(W)
    W.conflict = true
    polln(W, 1)
    local a = (#W.fires == 1 and W.fires[1].uid == 9801 and W.fires[1].key == POT)
    check(TAG .. "Q1a: in melee at 70% health the potion FIRES (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "reason: in melee, health 70% (<= 75%)") == 1)
    check(TAG .. "Q1b: the reason is the in-melee health reason [live log]", lg(TAG, b))
    note88(W, TAG)
    tally(W)
    return a and lg(TAG, b)
  end

  -- ==========================================================================
  -- Q2. POTION: in melee but 90% health -> SILENT.
  -- ==========================================================================
  local function world_q2(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "potionier", uid = 9811, owns = { POT }, melee = true, wavering = false, health_percent = 90 },
    }, cards = {
      { id = "9811", state = "active", vis = true },
    }, bar = { { id = "b1", key = POT } } })
    print("== " .. TAG .. "Q2. POTION OF TOUGHNESS: in melee + 90% health -> SILENT == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "Q2: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9811, true); ui(W); ui(W)
    click(W, badd("potion_of_toughness")); ui(W)
    W.conflict = true
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "Q2a: at 90% health the potion stays SILENT (" .. fire_detail(W) .. ")", a)
    note88(W, TAG)
    tally(W)
    return a
  end

  -- ==========================================================================
  -- Q3. POTION: 70% health but NOT in melee -> SILENT.
  -- ==========================================================================
  local function world_q3(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "potionier", uid = 9821, owns = { POT }, melee = false, wavering = false, health_percent = 70 },
    }, cards = {
      { id = "9821", state = "active", vis = true },
    }, bar = { { id = "b1", key = POT } } })
    print("== " .. TAG .. "Q3. POTION OF TOUGHNESS: 70% health but NOT in melee -> SILENT == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "Q3: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9821, true); ui(W); ui(W)
    click(W, badd("potion_of_toughness")); ui(W)
    W.conflict = true
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "Q3a: not in melee, the potion stays SILENT (" .. fire_detail(W) .. ")", a)
    note88(W, TAG)
    tally(W)
    return a
  end

  -- ==========================================================================
  -- S1. A SAMPLE of the newly added entries FIRES on their rule: four sample
  --     in-melee-self entries, one charge-or-melee entry (in melee) and two
  --     block-6 auto-accepted entries, all in melee, all armed -> 7 fires.
  --     Also asserts the grown table: 189 entries, 195 keys.
  -- ==========================================================================
  local function world_s1(PATH, TAG)
    local samples = {}
    for _, e in ipairs(SAMPLE_SELF) do samples[#samples + 1] = e end
    for _, e in ipairs(SAMPLE_CHARGE) do samples[#samples + 1] = e end
    for _, e in ipairs(SAMPLE_AUTO) do samples[#samples + 1] = e end
    local units, cards, bar = {}, {}, {}
    for i, e in ipairs(samples) do
      units[i] = { name = "sample" .. i, uid = 9900 + i, owns = { e[2] }, melee = true, wavering = false }
      cards[i] = { id = tostring(9900 + i), state = "active", vis = true }
      bar[i] = { id = "s" .. i, key = e[2] }
    end
    local W = make_world({ can_perform = true, units = units, cards = cards, bar = bar })
    print("== " .. TAG .. "S1. BLOCK 4/5/6 SAMPLE: " .. #samples .. " newly added entries fire on their rule == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "S1: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    local armed_n = 0
    for i, e in ipairs(samples) do
      sel_event(W, 9900 + i, true); ui(W); ui(W)
      click(W, badd(e[1])); ui(W)
      if badge_text(W, badd(e[1])) == "A" then armed_n = armed_n + 1 end
    end
    W.conflict = true
    polln(W, 1)
    local all_fired = (#W.fires == #samples)
    check(TAG .. "S1a: all " .. #samples .. " sample badges armed to A (" .. armed_n .. "/" .. #samples .. ")",
      armed_n == #samples)
    check(TAG .. "S1b: ALL " .. #samples .. " newly added sample entries FIRED on in-melee alone ("
      .. #W.fires .. " fires)", all_fired)
    -- the grown table reached THROUGH the mod's own closures (the SAME root
    -- set the H68 world uses, so every shared upvalue is reachable in both files)
    local roots = { CUR_UI_FN, POLL_BODY_FN, W.ui_fn, W.poll_fn }
    for _, l in ipairs(W.listeners) do roots[#roots + 1] = l.cb end
    for _, c in ipairs(W.phase_cbs.Deployment or {}) do roots[#roots + 1] = c end
    for _, c in ipairs(W.phase_cbs.Deployed or {}) do roots[#roots + 1] = c end
    for _, r in ipairs(W.sel_registrations) do roots[#roots + 1] = r.cb end
    local ABIL = upvalue_from_roots(roots, "ABILITIES", "table")
    local MK   = upvalue_from_roots(roots, "marker_by_key", "table")
    local n_e = (ABIL ~= nil and #ABIL or -1)
    local n_k = -1
    if MK ~= nil then
      n_k = 0
      for _ in pairs(MK) do n_k = n_k + 1 end
    end
    check(TAG .. "S1c: the abilities table has 189 entries (" .. n_e .. ")", n_e == 189)
    check(TAG .. "S1d: the static key->marker map has 195 keys (" .. n_k .. ")", n_k == 195)
    note88(W, TAG)
    tally(W)
    return armed_n == #samples and all_fired and (n_e == 189) and (n_k == 195)
  end

  print()
  print("== HARNESS 88 - BLOCKS 4/5/6 (87 entries) + the two new triggers ==")
  local v1a = world_v1(ANN, "[annotated] "); local v1b = world_v1(LIVE, "[live] ")
  local v2a = world_v2(ANN, "[annotated] "); local v2b = world_v2(LIVE, "[live] ")
  local v3a = world_v3(ANN, "[annotated] "); local v3b = world_v3(LIVE, "[live] ")
  local v4a = world_v4(ANN, "[annotated] "); local v4b = world_v4(LIVE, "[live] ")
  local v5a = world_v5(ANN, "[annotated] "); local v5b = world_v5(LIVE, "[live] ")
  local q1a = world_q1(ANN, "[annotated] "); local q1b = world_q1(LIVE, "[live] ")
  local q2a = world_q2(ANN, "[annotated] "); local q2b = world_q2(LIVE, "[live] ")
  local q3a = world_q3(ANN, "[annotated] "); local q3b = world_q3(LIVE, "[live] ")
  local s1a = world_s1(ANN, "[annotated] "); local s1b = world_s1(LIVE, "[live] ")

  local results = { v1a, v1b, v2a, v2b, v3a, v3b, v4a, v4b, v5a, v5b,
                    q1a, q1b, q2a, q2b, q3a, q3b, s1a, s1b }
  local n_ok = 0
  for _, r in ipairs(results) do if posv(r) then n_ok = n_ok + 1 end end

  check("every ui tick ran clean across the HARNESS-88 worlds (" .. RED88.ui .. " failures)", RED88.ui == 0)

  if not RED_MODE then
    check("the HARNESS-88 worlds all behaved (live+annotated: V1/V2/V3/V4/V5/Q1/Q2/Q3/S1) - " .. n_ok .. "/18", n_ok == 18)
    check("HEADLINE (harness 88): BLOCKS 4, 5 AND 6 ship 87 new ability entries - 80 on the SHARED "
      .. "melee_unwavering evaluator (54 block-4/5 approved in-melee-self + 26 auto-accepted trivial self-buffs: "
      .. "15 block-5 + 11 block-6 rule-9) and 5 on the EXISTING charge_or_melee evaluator (no new evaluator, no new "
      .. "chunk locals); the table grows 102 -> 189 entries (108 -> 195 keys). TWO NEW TRIGGER TYPES: WILL OF THE "
      .. "VERMINKING fires when any friendly unit other than the caster is in melee and wavering within the "
      .. "conservative 25 m FOURTH.VERMINKING_RANGE_M (game data 35 m aura) of the owner, cast ON SELF, with the "
      .. "Glorious-Death safety pattern (closest ally, pre-cast gap re-check, skip on drift); POTION OF TOUGHNESS "
      .. "fires when the owner is in melee at <= 75% health (the shared health read, no second threshold). "
      .. "ARMY-BAR abilities are a STANDING EXCLUSION - no army_abilities key is in the mod.", n_ok == 18)
  else
    check("RED CONTROL (harness 88): on the pre-edit snapshot (the shipped harness-87 build, 102 entries) the "
      .. "adapted count pins and this HARNESS-88 section fail; the SILENT worlds pass trivially because the "
      .. "ability is simply absent on the snapshot (V2/V3/Q2/Q3 both files + the annotated drift world V4) - "
      .. n_ok .. "/18 world results pass (want 9), fires " .. RED88.fires
      .. ", claims " .. RED88.claims, n_ok == 9)
  end
end
run_h88()

