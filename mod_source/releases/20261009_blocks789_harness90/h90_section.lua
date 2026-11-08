
-- ============================================================================
-- HARNESS 90 (this round): BLOCKS 7-9 - the NEW trigger types and the
--   redesigned pair, plus the grown table.
--   New triggers (each its own FOURTH evaluator):
--     charge_only           Ferocious Battle Howl - the charge window WITHOUT
--                           the melee arm (the melee arm is PROVEN absent).
--     wavering_self         Ferocious Fury of Ulric / Helm of Yvresse / Vial of
--                           Troll Blood - the OWNER wavering (fail-closed).
--     wavering_self_or_ally Fury of Ulric / the redesigned Commanding Presence
--                           - owner wavering OR an in-melee wavering ally
--                           within the conservative 25 m FOURTH.WAVERING_RANGE_M.
--     charge_or_wavering    Bangers & Smash - the charge window OR wavering.
--     wavering_ally_range   "Stay Here, I'll Get Help!" - a wavering ally in
--                           range (the owner need not waver and the ally need
--                           NOT be in melee: the Verminking shape with the
--                           ally-melee requirement REMOVED).
--   The table grows 193 -> 262 entries (199 -> 272 keys). The new section's 0n
--   tokens + the N worlds are appended before the final find check; the
--   adapted count pins are the SAME table-size pins the earlier sections read
--   (now 262/272).
--   RED CONTROL: with H90_LIVE / H90_ANN pointing at the pre-edit snapshot (the
--   shipped harness-89 build, 193 entries), the grown-table pins and this
--   HARNESS-90 section fail; the SILENT / SKIP worlds pass trivially because
--   the new abilities are simply absent on the snapshot.
-- ============================================================================
function run_h90()
  -- the ability keys of the five new triggers (+ the redesigned pair)
  local F_BH  = "wh3_dlc29_spell_bound_prayer_ferocious_battle_howl"       -- charge_only
  local W_FFU = "wh3_dlc29_spell_bound_prayer_ferocious_fury_of_ulric"     -- wavering_self
  local W_HYV = "wh2_dlc15_item_abilities_helm_of_yvresse"                 -- wavering_self
  local W_VTB = "wh_dlc08_item_abilities_vial_of_troll_blood"              -- wavering_self
  local WA_FU = "wh3_dlc29_spell_bound_prayer_fury_of_ulric"               -- wavering_self_or_ally
  local WA_CP = "wh3_dlc29_lord_active_commanding_presence"                -- wavering_self_or_ally (redesigned #36)
  local CW_BS = "wh2_dlc15_character_abilities_sausage_busta"              -- charge_or_wavering
  local WA_SH = "wh2_dlc09_character_abilities_stay_here_ill_get_help"     -- wavering_ally_range
  local T_DS1 = "wh3_main_character_abilities_dazs_song_of_winter_sunlight" -- tired (redesigned #46)
  local T_DS2 = "wh3_twa06_unit_abilities_dazs_song_of_winter_sunlight"     -- tired (redesigned #46)

  local live_src90 = read_file(LIVE)
  local ann_src90  = read_file(ANN)
  local RED90 = { fires = 0, claims = 0, ui = 0 }
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
  local function note90(W, TAG)
    RED90.ui = RED90.ui + (W.ui_failures or 0)
    if TAG == "[live] " then
      RED90.fires = RED90.fires + #W.fires
      RED90.claims = RED90.claims + count_log(W, "claim: ")
    end
  end
  -- the shared arming prologue: load, select, arm the badge, go to conflict
  local function boot(W, PATH, TAG, uid, marker, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, badd(marker)); ui(W)
    W.conflict = true
    return true
  end

  -- --------------------------------------------------- 0n: tokens (both files)
  print("== HARNESS 90 - section 0n: the NEW triggers + grown table (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src90 }, { name = "ann", src = ann_src90 } }) do
    local nm, s = f.name, f.src
    check("0n " .. nm .. ": the five new evaluators exist",
      raw_find(s, "function FOURTH.evaluate_charge_only(unit, routing)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.evaluate_wavering_self(unit, routing)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.evaluate_wavering_self_or_ally(unit, routing)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.evaluate_charge_or_wavering(unit, routing)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.evaluate_wavering_ally_range(unit, routing)", 1, true) ~= nil)
    check("0n " .. nm .. ": the five new trigger names are wired in the map",
      raw_find(s, "charge_only = FOURTH.evaluate_charge_only,", 1, true) ~= nil
      and raw_find(s, "wavering_self = FOURTH.evaluate_wavering_self,", 1, true) ~= nil
      and raw_find(s, "wavering_self_or_ally = FOURTH.evaluate_wavering_self_or_ally,", 1, true) ~= nil
      and raw_find(s, "charge_or_wavering = FOURTH.evaluate_charge_or_wavering,", 1, true) ~= nil
      and raw_find(s, "wavering_ally_range = FOURTH.evaluate_wavering_ally_range,", 1, true) ~= nil)
    check("0n " .. nm .. ": the trigger counts are right (melee_unwavering 216, charge_or_melee 15, charge_only 1, "
      .. "wavering_self 3, wavering_self_or_ally 2, charge_or_wavering 1, wavering_ally_range 1, tired 2)",
      cp(s, 'trigger = "melee_unwavering"') == 216 and cp(s, 'trigger = "charge_or_melee"') == 15
      and cp(s, 'trigger = "charge_only"') == 1 and cp(s, 'trigger = "wavering_self"') == 3
      and cp(s, 'trigger = "wavering_self_or_ally"') == 2 and cp(s, 'trigger = "charge_or_wavering"') == 1
      and cp(s, 'trigger = "wavering_ally_range"') == 1 and cp(s, 'trigger = "tired"') == 2)
    check("0n " .. nm .. ": the wavering trigger range is a DELIBERATELY CONSERVATIVE 25 m (FOURTH.WAVERING_RANGE_M = 25), "
      .. "the game-data 35 m aura named in the comment",
      raw_find(s, "FOURTH.WAVERING_RANGE_M = 25", 1, true) ~= nil
      and raw_find(s, "effect_range", 1, true) ~= nil and raw_find(s, "35 m", 1, true) ~= nil)
    check("0n " .. nm .. ": the two new range helpers exist (ws_ally / wa_ally gap + in_range)",
      raw_find(s, "function FOURTH.ws_ally_gap(unit, ally)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.ws_ally_in_range(unit, ally)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.wa_ally_gap(unit, ally)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.wa_ally_in_range(unit, ally)", 1, true) ~= nil)
    check("0n " .. nm .. ": the chosen-ally fields are only ever set by their arm (ws_ally = nil x3, wa_ally = nil x3)",
      cp(s, "FOURTH.ws_ally = nil") == 3 and cp(s, "FOURTH.wa_ally = nil") == 3)
    check("0n " .. nm .. ": the casts stay on the DEFAULT (target or unit) - no cast_target write for the new triggers "
      .. "(FOURTH.cast_target = unit still x2)",
      cp(s, "FOURTH.cast_target = unit") == 2)
    check("0n " .. nm .. ": the wavering_self trigger is FAIL-CLOSED (only an exact true morale answer fires)",
      raw_find(s, "FOURTH.wavering(unit) == true", 1, true) ~= nil)
    check("0n " .. nm .. ": the self-or-ally ALLY arm requires the ally in melee AND wavering "
      .. "(other:is_in_melee() and not unit_is_routing(other) and FOURTH.wavering(other) == true)",
      raw_find(s, "other:is_in_melee() and not unit_is_routing(other)", 1, true) ~= nil
      and raw_find(s, "and FOURTH.wavering(other) == true", 1, true) ~= nil)
    check("0n " .. nm .. ": NO army-bar key is in the mod (standing exclusion)",
      raw_find(s, "army_abilities", 1, true) == nil)
  end
  -- the wavering_ally_range evaluator must NOT contain an is_in_melee call in its scan
  do
    local function scan_body(s)
      local a = raw_find(s, "function FOURTH.evaluate_wavering_ally_range(unit, routing)", 1, true)
      if a == nil then return nil end
      local b = raw_find(s, "function FOURTH.evaluate_", a + 1, true)
      if b == nil then b = #s end
      return string.sub(s, a, b)
    end
    local body = scan_body(live_src90)
    check("0n live: the wavering_ally_range body has NO unit:is_in_melee() call (the ally need not be in melee)",
      body ~= nil and raw_find(body, "is_in_melee", 1, true) == nil)
  end
  check("0n live: the charge-only reason exists", raw_find(live_src90, 'reason = string.format("charging (charge only)', 1, true) ~= nil)
  check("0n live: the wavering-self reason exists", raw_find(live_src90, 'reason = "wavering (self)"', 1, true) ~= nil)
  check("0n live: the self-or-ally reasons exist",
    raw_find(live_src90, 'reason = "wavering (self-or-ally)"', 1, true) ~= nil
    and raw_find(live_src90, 'reason = "wavering in-melee ally (self-cast, self-or-ally)"', 1, true) ~= nil)
  check("0n live: the charge-or-wavering reasons exist",
    raw_find(live_src90, 'reason = string.format("charging (charge or wavering)', 1, true) ~= nil
    and raw_find(live_src90, 'reason = "wavering (charge or wavering)"', 1, true) ~= nil)
  check("0n live: the wavering-ally-in-range reason exists",
    raw_find(live_src90, 'reason = "wavering ally in range (self-cast)"', 1, true) ~= nil)
  check("0n live: the two drift skips are reported",
    raw_find(live_src90, "wavering_self_or_ally SKIPPED:", 1, true) ~= nil
    and raw_find(live_src90, "wavering_ally_range SKIPPED:", 1, true) ~= nil)
  check("0n ann: the reading copy stays log-free and find-free",
    raw_find(ann_src90, "log(", 1, true) == nil and raw_find(ann_src90, "string.find(", 1, true) == nil)

  -- ==========================================================================
  -- N1. CHARGE ONLY: a charging unit (fast + target in charge range) FIRES on
  --     the charge window; the reason is the charge-only reason.
  -- ==========================================================================
  local function world_n1(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "howler", uid = 9001, owns = { F_BH }, fast = true, melee = false, target = true, dist = 20, wavering = false },
    }, cards = { { id = "9001", state = "active", vis = true } }, bar = { { id = "b1", key = F_BH } } })
    print("== " .. TAG .. "N1. CHARGE ONLY: charging -> FIRES (charge-only reason) == ")
    if not boot(W, PATH, TAG, 9001, "ferocious_battle_howl", "N1") then return nil end
    polln(W, 1)
    local a = (#W.fires == 1 and W.fires[1].uid == 9001 and W.fires[1].key == F_BH)
    check(TAG .. "N1a: the charging unit fired ferocious_battle_howl once (" .. fire_detail(W) .. ")", a)
    local b = (fire_target_for(W, 9001) == unit_of(W, 9001))
    check(TAG .. "N1b: the cast target is the OWNER itself (self-cast)", b)
    local c = (count_log(W, "reason: charging (charge only)") == 1)
    check(TAG .. "N1c: the reason is the charge-only reason [live log]", lg(TAG, c))
    note90(W, TAG); tally(W)
    return a and b and lg(TAG, c)
  end

  -- ==========================================================================
  -- N2. CHARGE ONLY, SILENT: the unit is in melee but NOT charging -> the melee
  --     arm is PROVEN absent (a charge-only ability must not fire in melee).
  -- ==========================================================================
  local function world_n2(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "howler", uid = 9002, owns = { F_BH }, fast = false, melee = true, wavering = false },
    }, cards = { { id = "9002", state = "active", vis = true } }, bar = { { id = "b1", key = F_BH } } })
    print("== " .. TAG .. "N2. CHARGE ONLY: in melee, not charging -> NO fire (no melee arm) == ")
    if not boot(W, PATH, TAG, 9002, "ferocious_battle_howl", "N2") then return nil end
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "N2a: in melee but not charging -> the charge-only ability stays SILENT (" .. fire_detail(W) .. ")", a)
    note90(W, TAG); tally(W)
    return a
  end

  -- ==========================================================================
  -- N3. WAVERING SELF: the owner is wavering -> FIRES; not wavering -> SILENT;
  --     an UNREADABLE morale -> SILENT (fail-closed). All three in one world
  --     would need three abilities; use one unit, re-polled with a settable
  --     morale via three separate worlds is cleaner - here we prove the fire.
  -- ==========================================================================
  local function world_n3(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "fury", uid = 9003, owns = { W_FFU }, wavering = true, melee = false },
    }, cards = { { id = "9003", state = "active", vis = true } }, bar = { { id = "b1", key = W_FFU } } })
    print("== " .. TAG .. "N3. WAVERING SELF: the owner is wavering -> FIRES == ")
    if not boot(W, PATH, TAG, 9003, "ferocious_fury_of_ulric", "N3") then return nil end
    polln(W, 1)
    local a = (#W.fires == 1 and W.fires[1].key == W_FFU)
    check(TAG .. "N3a: the wavering owner fired ferocious_fury_of_ulric (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "reason: wavering (self) | armed") == 1)
    check(TAG .. "N3b: the reason is the wavering-self reason [live log]", lg(TAG, b))
    note90(W, TAG); tally(W)
    return a and lg(TAG, b)
  end

  -- ==========================================================================
  -- N4. WAVERING SELF, SILENT: not wavering -> SILENT; morale read raising ->
  --     SILENT (fail-closed, no fire on an unreadable morale).
  -- ==========================================================================
  local function world_n4(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "steady",   uid = 9004, owns = { W_HYV }, wavering = false },
      { name = "unreadable", uid = 9005, owns = { W_VTB }, wavering_raises = true },
    }, cards = { { id = "9004", state = "active", vis = true }, { id = "9005", state = "active", vis = true } },
       bar = { { id = "b1", key = W_HYV }, { id = "b2", key = W_VTB } } })
    print("== " .. TAG .. "N4. WAVERING SELF: steady + unreadable morale -> NO fire (fail-closed) == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "N4: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9004, true); ui(W); ui(W); click(W, badd("helm_of_yvresse")); ui(W)
    sel_event(W, 9005, true); ui(W); ui(W); click(W, badd("vial_of_troll_blood")); ui(W)
    W.conflict = true
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "N4a: a steady owner and an unreadable morale stay SILENT (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "reason: wavering (self)") == 0)
    check(TAG .. "N4b: no wavering-self reason was ever emitted [live log]", lg(TAG, b))
    note90(W, TAG); tally(W)
    return a and lg(TAG, b)
  end

  -- ==========================================================================
  -- N5. WAVERING SELF-OR-ALLY, SELF ARM: the owner is wavering -> FIRES.
  -- ==========================================================================
  local function world_n5(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "ulric", uid = 9006, owns = { WA_FU }, wavering = true },
    }, cards = { { id = "9006", state = "active", vis = true } }, bar = { { id = "b1", key = WA_FU } } })
    print("== " .. TAG .. "N5. WAVERING SELF-OR-ALLY: the owner itself is wavering -> FIRES (self arm) == ")
    if not boot(W, PATH, TAG, 9006, "fury_of_ulric", "N5") then return nil end
    polln(W, 1)
    local a = (#W.fires == 1 and W.fires[1].key == WA_FU)
    check(TAG .. "N5a: the wavering owner fired fury_of_ulric (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "reason: wavering (self-or-ally) | armed") == 1)
    check(TAG .. "N5b: the reason is the self arm of the self-or-ally trigger [live log]", lg(TAG, b))
    note90(W, TAG); tally(W)
    return a and lg(TAG, b)
  end

  -- ==========================================================================
  -- N6. WAVERING SELF-OR-ALLY, ALLY ARM: the owner is NOT wavering but an
  --     in-melee wavering ally is within 20 m -> FIRES, cast ON SELF.
  -- ==========================================================================
  local function world_n6(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "ulric",  uid = 9007, owns = { WA_FU }, wavering = false, melee = false },
      { name = "broken", uid = 9008, owns = {},         wavering = true,  melee = true, dist = 20 },
    }, cards = { { id = "9007", state = "active", vis = true }, { id = "9008", state = "active", vis = true } },
       bar = { { id = "b1", key = WA_FU } } })
    print("== " .. TAG .. "N6. WAVERING SELF-OR-ALLY: an in-melee wavering ally within 20 m -> FIRES (self-cast) == ")
    if not boot(W, PATH, TAG, 9007, "fury_of_ulric", "N6") then return nil end
    polln(W, 1)
    local caster = unit_of(W, 9007); local ally = unit_of(W, 9008)
    local a = (#W.fires == 1 and W.fires[1].key == WA_FU)
    check(TAG .. "N6a: the owner fired fury_of_ulric once (" .. fire_detail(W) .. ")", a)
    local b = (fire_target_for(W, 9007) == caster and fire_target_for(W, 9007) ~= ally)
    check(TAG .. "N6b: the cast target is the OWNER itself, never the ally (self-cast)", b)
    local c = (count_log(W, "reason: wavering in-melee ally (self-cast, self-or-ally)") == 1)
    check(TAG .. "N6c: the reason is the ally arm of the self-or-ally trigger [live log]", lg(TAG, c))
    note90(W, TAG); tally(W)
    return a and b and lg(TAG, c)
  end

  -- ==========================================================================
  -- N7. WAVERING SELF-OR-ALLY, RANGE: the in-melee wavering ally is BEYOND the
  --     conservative 25 m (55 m) -> SILENT.
  -- ==========================================================================
  local function world_n7(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "ulric",  uid = 9009, owns = { WA_FU }, wavering = false, melee = false },
      { name = "broken", uid = 9010, owns = {},         wavering = true,  melee = true, dist = 55 },
    }, cards = { { id = "9009", state = "active", vis = true }, { id = "9010", state = "active", vis = true } },
       bar = { { id = "b1", key = WA_FU } } })
    print("== " .. TAG .. "N7. WAVERING SELF-OR-ALLY: the in-melee wavering ally is BEYOND 25 m (55 m) -> SILENT == ")
    if not boot(W, PATH, TAG, 9009, "fury_of_ulric", "N7") then return nil end
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "N7a: the 55 m ally is OUT of the 25 m trigger range -> NO cast (" .. fire_detail(W) .. ")", a)
    note90(W, TAG); tally(W)
    return a
  end

  -- ==========================================================================
  -- N8. WAVERING ALLY IN RANGE: the owner is NOT wavering and the wavering ally
  --     is NOT in melee, within 20 m -> FIRES (no ally-melee requirement).
  -- ==========================================================================
  local function world_n8(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "leader", uid = 9011, owns = { WA_SH }, wavering = false, melee = false },
      { name = "broken", uid = 9012, owns = {},         wavering = true,  melee = false, dist = 20 },
    }, cards = { { id = "9011", state = "active", vis = true }, { id = "9012", state = "active", vis = true } },
       bar = { { id = "b1", key = WA_SH } } })
    print("== " .. TAG .. "N8. WAVERING ALLY IN RANGE: a wavering (not-in-melee) ally within 20 m -> FIRES (self-cast) == ")
    if not boot(W, PATH, TAG, 9011, "stay_here_ill_get_help", "N8") then return nil end
    polln(W, 1)
    local a = (#W.fires == 1 and W.fires[1].key == WA_SH)
    check(TAG .. "N8a: the owner fired stay_here_ill_get_help (" .. fire_detail(W) .. ")", a)
    local b = (fire_target_for(W, 9011) == unit_of(W, 9011))
    check(TAG .. "N8b: the cast target is the OWNER itself (self-cast)", b)
    local c = (count_log(W, "reason: wavering ally in range (self-cast)") == 1)
    check(TAG .. "N8c: the reason is the wavering-ally-in-range reason [live log]", lg(TAG, c))
    note90(W, TAG); tally(W)
    return a and b and lg(TAG, c)
  end

  -- ==========================================================================
  -- N9. WAVERING ALLY IN RANGE, RANGE: the wavering ally is BEYOND 25 m -> SILENT.
  --     Also proves the owner need NOT be wavering (it is not) for a silent case.
  -- ==========================================================================
  local function world_n9(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "leader", uid = 9013, owns = { WA_SH }, wavering = false },
      { name = "broken", uid = 9014, owns = {},         wavering = true, melee = false, dist = 55 },
    }, cards = { { id = "9013", state = "active", vis = true }, { id = "9014", state = "active", vis = true } },
       bar = { { id = "b1", key = WA_SH } } })
    print("== " .. TAG .. "N9. WAVERING ALLY IN RANGE: the wavering ally is BEYOND 25 m (55 m) -> SILENT == ")
    if not boot(W, PATH, TAG, 9013, "stay_here_ill_get_help", "N9") then return nil end
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "N9a: the 55 m ally is OUT of the 25 m range -> NO cast (" .. fire_detail(W) .. ")", a)
    note90(W, TAG); tally(W)
    return a
  end

  -- ==========================================================================
  -- N10. DRIFT: the in-melee wavering ally is in range at DECIDE (20 m) but out
  --      at CAST (55 m) -> the cast is SKIPPED rather than wasted.
  -- ==========================================================================
  local function world_n10(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "ulric",  uid = 9015, owns = { WA_FU }, wavering = false, melee = false },
      { name = "broken", uid = 9016, owns = {},         wavering = true,  melee = true, dist_seq = { 20, 55 } },
    }, cards = { { id = "9015", state = "active", vis = true }, { id = "9016", state = "active", vis = true } },
       bar = { { id = "b1", key = WA_FU } } })
    print("== " .. TAG .. "N10. DRIFT: the wavering ally drifts out of range between decide and cast -> SKIP == ")
    if not boot(W, PATH, TAG, 9015, "fury_of_ulric", "N10") then return nil end
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "N10a: the ally was in range at decide but out at cast -> the cast is SKIPPED (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "wavering_self_or_ally SKIPPED") == 1)
    check(TAG .. "N10b: the drift skip is reported [live log]", lg(TAG, b))
    note90(W, TAG); tally(W)
    return a and lg(TAG, b)
  end

  -- ==========================================================================
  -- N11. CHARGE OR WAVERING: (a) a charging unit fires the charge arm;
  --      (b) a wavering non-charging unit fires the wavering arm.
  -- ==========================================================================
  local function world_n11(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "bangers", uid = 9017, owns = { CW_BS }, fast = true, melee = false, target = true, dist = 20, wavering = false },
    }, cards = { { id = "9017", state = "active", vis = true } }, bar = { { id = "b1", key = CW_BS } } })
    print("== " .. TAG .. "N11. CHARGE OR WAVERING: a charging unit fires (charge arm) == ")
    if not boot(W, PATH, TAG, 9017, "sausage_busta", "N11") then return nil end
    polln(W, 1)
    local a = (#W.fires == 1 and W.fires[1].key == CW_BS)
    check(TAG .. "N11a: the charging unit fired sausage_busta once (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "reason: charging (charge or wavering)") == 1)
    check(TAG .. "N11b: the reason is the charge arm [live log]", lg(TAG, b))
    note90(W, TAG); tally(W)
    return a and lg(TAG, b)
  end

  local function world_n12(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "bangers", uid = 9018, owns = { CW_BS }, fast = false, melee = false, wavering = true },
    }, cards = { { id = "9018", state = "active", vis = true } }, bar = { { id = "b1", key = CW_BS } } })
    print("== " .. TAG .. "N12. CHARGE OR WAVERING: a wavering non-charging unit fires (wavering arm) == ")
    if not boot(W, PATH, TAG, 9018, "sausage_busta", "N12") then return nil end
    polln(W, 1)
    local a = (#W.fires == 1 and W.fires[1].key == CW_BS)
    check(TAG .. "N12a: the wavering unit fired sausage_busta once (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "reason: wavering (charge or wavering)") == 1)
    check(TAG .. "N12b: the reason is the wavering arm [live log]", lg(TAG, b))
    local c = (count_log(W, "reason: charging (charge or wavering)") == 0)
    check(TAG .. "N12c: the charge arm did NOT fire (not charging) [live log]", lg(TAG, c))
    note90(W, TAG); tally(W)
    return a and lg(TAG, b) and lg(TAG, c)
  end

  -- ==========================================================================
  -- N13. THE REDESIGNED PAIR + the grown table (262 entries / 272 keys):
  --      (a) Dazh's Song of Winter Sunlight fires on the EXISTING tired
  --          trigger (both keys ride ONE entry);
  --      (b) Commanding Presence fires via the wavering_self_or_ally trigger.
  -- ==========================================================================
  local function world_n13(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "dazh", uid = 9019, owns = { T_DS1 }, fatigue = "threshold_tired" },
      { name = "cp",   uid = 9020, owns = { WA_CP }, wavering = true },
    }, cards = { { id = "9019", state = "active", vis = true }, { id = "9020", state = "active", vis = true } },
       bar = { { id = "b1", key = T_DS1 }, { id = "b2", key = WA_CP } } })
    print("== " .. TAG .. "N13. REDESIGNED: Dazh's Song fires on 'tired'; Commanding Presence fires on wavering == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "N13: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9019, true); ui(W); ui(W); click(W, badd("dazs_song_of_winter_sunlight")); ui(W)
    sel_event(W, 9020, true); ui(W); ui(W); click(W, badd("commanding_presence")); ui(W)
    W.conflict = true
    polln(W, 1)
    local a = (#W.fires == 2)
    check(TAG .. "N13a: both redesigned abilities fired (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "reason: tired or worse") >= 1)
    check(TAG .. "N13b: Dazh's Song used the EXISTING tired reason [live log]", lg(TAG, b))
    local c = (count_log(W, "reason: wavering (self-or-ally) | armed") == 1)
    check(TAG .. "N13c: Commanding Presence used the self-or-ally trigger [live log]", lg(TAG, c))
    local roots = { CUR_UI_FN, POLL_BODY_FN, W.ui_fn, W.poll_fn }
    for _, l in ipairs(W.listeners) do roots[#roots + 1] = l.cb end
    for _, c2 in ipairs(W.phase_cbs.Deployment or {}) do roots[#roots + 1] = c2 end
    for _, c2 in ipairs(W.phase_cbs.Deployed or {}) do roots[#roots + 1] = c2 end
    for _, r in ipairs(W.sel_registrations) do roots[#roots + 1] = r.cb end
    local ABIL = upvalue_from_roots(roots, "ABILITIES", "table")
    local MK   = upvalue_from_roots(roots, "marker_by_key", "table")
    local n_e = (ABIL ~= nil and #ABIL or -1)
    local n_k = -1
    if MK ~= nil then n_k = 0; for _ in pairs(MK) do n_k = n_k + 1 end end
    check(TAG .. "N13d: the abilities table has 262 entries (" .. n_e .. ")", n_e == 262)
    check(TAG .. "N13e: the static key->marker map has 272 keys (" .. n_k .. ")", n_k == 272)
    note90(W, TAG); tally(W)
    return a and lg(TAG, b) and lg(TAG, c) and (n_e == 262) and (n_k == 272)
  end

  -- ==========================================================================
  -- N14. CHARGE OR WAVERING, SILENT: neither charging NOR wavering -> SILENT.
  -- ==========================================================================
  local function world_n14(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "bangers", uid = 9021, owns = { CW_BS }, fast = false, melee = false, wavering = false },
    }, cards = { { id = "9021", state = "active", vis = true } }, bar = { { id = "b1", key = CW_BS } } })
    print("== " .. TAG .. "N14. CHARGE OR WAVERING: neither charging nor wavering -> SILENT == ")
    if not boot(W, PATH, TAG, 9021, "sausage_busta", "N14") then return nil end
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "N14a: neither arm met -> NO fire (" .. fire_detail(W) .. ")", a)
    note90(W, TAG); tally(W)
    return a
  end

  -- ==========================================================================
  -- N15. WAVERING ALLY IN RANGE, DRIFT: the wavering ally is in range at DECIDE
  --      (20 m) but out at CAST (55 m) -> the cast is SKIPPED rather than wasted.
  -- ==========================================================================
  local function world_n15(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "leader", uid = 9022, owns = { WA_SH }, wavering = false },
      { name = "broken", uid = 9023, owns = {},         wavering = true, melee = false, dist_seq = { 20, 55 } },
    }, cards = { { id = "9022", state = "active", vis = true }, { id = "9023", state = "active", vis = true } },
       bar = { { id = "b1", key = WA_SH } } })
    print("== " .. TAG .. "N15. WAVERING ALLY IN RANGE: the ally drifts out of range between decide and cast -> SKIP == ")
    if not boot(W, PATH, TAG, 9022, "stay_here_ill_get_help", "N15") then return nil end
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "N15a: the ally was in range at decide but out at cast -> the cast is SKIPPED (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "wavering_ally_range SKIPPED") == 1)
    check(TAG .. "N15b: the drift skip is reported [live log]", lg(TAG, b))
    note90(W, TAG); tally(W)
    return a and lg(TAG, b)
  end

  -- ==========================================================================
  -- N16. CHARGE ONLY, BOUNDARY: fast with a target but the gap is BELOW the
  --      charge run-up minimum (5 m < CHARGE_MIN_DISTANCE_M 12) -> not charging
  --      -> SILENT.
  -- ==========================================================================
  local function world_n16(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "howler", uid = 9024, owns = { F_BH }, fast = true, melee = false, target = true, dist = 5, wavering = false },
    }, cards = { { id = "9024", state = "active", vis = true } }, bar = { { id = "b1", key = F_BH } } })
    print("== " .. TAG .. "N16. CHARGE ONLY: a 5 m gap is below the charge run-up minimum -> SILENT == ")
    if not boot(W, PATH, TAG, 9024, "ferocious_battle_howl", "N16") then return nil end
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "N16a: a 5 m target distance is not a charge (run-up too short) -> NO fire (" .. fire_detail(W) .. ")", a)
    note90(W, TAG); tally(W)
    return a
  end

  print()
  print("== HARNESS 90 - the NEW triggers and the redesigned pair (blocks 7-9) ==")
  local n01a = world_n1(ANN, "[annotated] ");  local n01b = world_n1(LIVE, "[live] ")
  local n02a = world_n2(ANN, "[annotated] ");  local n02b = world_n2(LIVE, "[live] ")
  local n03a = world_n3(ANN, "[annotated] ");  local n03b = world_n3(LIVE, "[live] ")
  local n04a = world_n4(ANN, "[annotated] ");  local n04b = world_n4(LIVE, "[live] ")
  local n05a = world_n5(ANN, "[annotated] ");  local n05b = world_n5(LIVE, "[live] ")
  local n06a = world_n6(ANN, "[annotated] ");  local n06b = world_n6(LIVE, "[live] ")
  local n07a = world_n7(ANN, "[annotated] ");  local n07b = world_n7(LIVE, "[live] ")
  local n08a = world_n8(ANN, "[annotated] ");  local n08b = world_n8(LIVE, "[live] ")
  local n09a = world_n9(ANN, "[annotated] ");  local n09b = world_n9(LIVE, "[live] ")
  local n10a = world_n10(ANN, "[annotated] "); local n10b = world_n10(LIVE, "[live] ")
  local n11a = world_n11(ANN, "[annotated] "); local n11b = world_n11(LIVE, "[live] ")
  local n12a = world_n12(ANN, "[annotated] "); local n12b = world_n12(LIVE, "[live] ")
  local n13a = world_n13(ANN, "[annotated] "); local n13b = world_n13(LIVE, "[live] ")
  local n14a = world_n14(ANN, "[annotated] "); local n14b = world_n14(LIVE, "[live] ")
  local n15a = world_n15(ANN, "[annotated] "); local n15b = world_n15(LIVE, "[live] ")
  local n16a = world_n16(ANN, "[annotated] "); local n16b = world_n16(LIVE, "[live] ")

  local results = { n01a, n01b, n02a, n02b, n03a, n03b, n04a, n04b, n05a, n05b, n06a, n06b,
                    n07a, n07b, n08a, n08b, n09a, n09b, n10a, n10b, n11a, n11b, n12a, n12b, n13a, n13b,
                    n14a, n14b, n15a, n15b, n16a, n16b }
  local n_ok = 0
  for _, r in ipairs(results) do if posv(r) then n_ok = n_ok + 1 end end

  check("every ui tick ran clean across the HARNESS-90 worlds (" .. RED90.ui .. " failures)", RED90.ui == 0)

  if not RED_MODE then
    check("the HARNESS-90 worlds all behaved (live+annotated: N1..N16) - " .. n_ok .. "/32", n_ok == 32)
    check("HEADLINE (harness 90): BLOCKS 7-9 ship FIVE new triggers - charge_only (Ferocious Battle Howl: the "
      .. "charge window WITHOUT the melee arm), wavering_self (the owner wavering, fail-closed), wavering_self_or_ally "
      .. "(the owner wavering OR an in-melee wavering ally within the conservative 25 m FOURTH.WAVERING_RANGE_M - the "
      .. "game-data 35 m aura), charge_or_wavering (the charge window OR wavering), and wavering_ally_range (a wavering "
      .. "ally in range with NO ally-melee requirement - the Verminking shape minus its melee gate). All cast ON SELF "
      .. "with the pre-cast gap re-check / drift skip. The redesigned pair rides wavering_self_or_ally (#36 Commanding "
      .. "Presence) and the existing tired trigger (#46 Dazh's Song). The table grows 193 -> 262 entries (199 -> 272 "
      .. "keys); no new chunk locals.", n_ok == 32)
  else
    check("RED CONTROL (harness 90): on the pre-edit snapshot (the shipped harness-89 build, 193 entries) the "
      .. "grown-table pins and this HARNESS-90 section fail; the SILENT worlds pass trivially because the new "
      .. "abilities are simply absent on the snapshot (N2 / N4 / N7 / N9 / N14 / N16 both files = 12, plus the "
      .. "ANNOTATED drift worlds N10 / N15 (their log legs are live-only, so they pass vacuously in the reading copy) "
      .. "= 2) - " .. n_ok
      .. "/32 world results pass (want 14), fires " .. RED90.fires
      .. ", claims " .. RED90.claims, n_ok == 14)
  end
end
run_h90()
