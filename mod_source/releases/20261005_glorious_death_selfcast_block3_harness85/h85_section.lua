-- ============================================================================
-- HARNESS 85 - GLORIOUS DEATH SELF-CAST (job 1) + BLOCK 3 (job 2).
--   JOB 1: Glorious Death's TRIGGER is unchanged (the Slayer-only candidate
--     set from harness 84), but THE CAST TARGET IS NOW ALWAYS THE OWNER
--     ITSELF - the ability is self-centred, so the caster is never ordered to
--     walk to the Slayer ally. The old write of the ally into
--     FOURTH.cast_target is GONE; the reasons are 'slayer in melee
--     (self-cast)' / 'self in melee (self-cast)'.
--   JOB 2: BLOCK 3 - 38 approved entries (the explicit task list carries 35
--     in-melee-self keys + 3 charge-or-melee keys). The 35 ride the EXISTING
--     shared melee_unwavering evaluator; the 3 ride the EXISTING
--     charge_or_melee evaluator. No new evaluator, no new chunk locals.
--   RED CONTROL: with H85_LIVE / H85_ANN pointing at the pre-edit snapshot
--     (the shipped harness-84 build), the block-3 entries are absent, the
--     Glorious Death cast target is still the ally, and the count pins
--     (A4 204, B4 102, H68 102/108, C6c 102) still read the old 64/70. Every
--     other harness-84-era check re-runs unchanged.
-- ============================================================================

if not RED_MODE then
  check("the WHOLE harness-84 suite (2038 checks before the final find check) still re-ran unchanged (checks so far = " .. checks .. ")",
    checks == 2038)
else
  print("   (red mode: the harness-84 suite boundary check is green-only - the red build skips some" ..
    " RED_MODE-gated checks, so its running count is lowered by design)")
end

local function run_h85()
  -- the 35 block-3 in-melee-self entries (marker, key): trigger melee_unwavering
  local B3_SELF = {
    { "legbiter", "wh3_dlc29_weapon_abilities_legbiter" },
    { "hellfire_sword", "wh_main_weapon_abilities_hellfire_sword" },
    { "helm_of_discord", "wh_main_weapon_abilities_helm_of_discord" },
    { "helm_of_many_eyes", "wh_dlc01_item_passive_helm_of_many_eyes" },
    { "heroic_killing_blow_2", "wh3_main_pro_character_abilities_heroic_killing_blow_2" },
    { "heroic_killing_blow_dlc07", "wh_dlc07_character_abilities_heroic_killing_blow" },
    { "heroic_killing_blow_main", "wh_main_character_abilities_heroic_killing_blow" },
    { "hydra_blade", "wh2_main_weapon_abilities_hydra_blade" },
    { "inevitable_horror", "wh3_dlc26_character_abilities_inevitable_horror" },
    { "karaghul", "wh2_pro08_weapon_abilities_karaghul" },
    { "killing_blow_1", "wh3_main_pro_character_abilities_heroic_killing_blow_1" },
    { "killing_blow", "wh_main_unit_abilities_killing_blow" },
    { "liarsbane", "wh3_dlc25_weapon_abilities_liarsbane" },
    { "lightning_reflexes", "wh2_dlc11_lord_abilities_lightning_reflexes" },
    { "locus_of_beguilement", "wh3_main_character_abilities_locus_of_beguilement" },
    { "locus_of_grace", "wh3_main_character_abilities_locus_of_grace" },
    { "locus_of_wrath", "wh3_main_character_abilities_locus_of_wrath" },
    { "lucky_banner", "wh2_dlc15_item_abilities_lucky_banner" },
    { "mace_of_ulumak", "wh2_dlc13_weapon_abilities_mace_of_ulumak" },
    { "mananns_luck", "wh2_dlc11_lord_abilities_mananns_luck" },
    { "master_of_the_skies", "wh2_dlc12_lord_abilities_master_of_the_skies" },
    { "mimic_waaagh", "wh2_dlc15_unit_abilities_mimic_waaagh" },
    { "mimic_grom_waaagh", "wh2_dlc15_unit_abilities_mimic_grom_waaagh" },
    { "monstrous_strength", "wh2_dlc13_lord_abilities_monstrous_strength" },
    { "mortal_blow", "wh3_main_daemon_arms_abilities_mortal_blow" },
    { "mortal_blow_upgraded", "wh3_main_daemon_arms_abilities_mortal_blow_upgraded" },
    { "mumbo_jumbo_chant", "wh3_dlc26_character_abilities_mumbo_jumbo_chant" },
    { "strike_of_nagash", "wh2_dlc09_character_abilities_strike_of_nagash" },
    { "nurgles_favoured_son", "wh3_dlc25_lord_abilities_nurgles_favoured_son" },
    { "opal_amulet", "wh_main_item_abilities_opal_amulet" },
    { "oracle_of_eternity", "wh3_main_lord_abilities_oracle_of_eternity" },
    { "pendant_of_slaanesh", "wh_main_item_abilities_pendant_of_slaanesh" },
    { "plaguefathers_oration", "wh3_main_lord_abilities_plaguefathers_oration" },
    { "primal_roar", "wh2_dlc13_lord_abilities_primal_roar" },
    { "puncture", "wh3_dlc26_character_abilities_puncture" },
  }
  -- the 3 block-3 charge-or-melee entries (marker, key): trigger charge_or_melee
  local B3_CHARGE = {
    { "heart_piercing", "wh2_dlc11_lord_abilities_heart_piercing" },
    { "horn_of_the_first_beast", "wh_dlc03_item_abilities_horn_of_the_first_beast" },
    { "morglor_the_mangler", "wh3_dlc26_weapon_abilities_morglor_the_mangler" },
  }
  local SL_DAEMON = "wh3_dlc25_dwf_cha_daemon_slayer"
  local SL_UNIT   = "wh_main_dwf_inf_slayers"
  local NON_SLAYER = "wh_main_emp_inf_swordsmen"
  local GLAD = "wh3_dlc25_lord_abilities_glorious_death"

  local live_src85 = read_file(LIVE)
  local ann_src85  = read_file(ANN)
  local RED85 = { fires = 0, claims = 0, badges = 0, ui = 0 }
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
  local function note85(W, TAG)
    RED85.ui = RED85.ui + (W.ui_failures or 0)
    if TAG == "[live] " then
      RED85.fires = RED85.fires + #W.fires
      RED85.claims = RED85.claims + count_log(W, "claim: ")
      RED85.badges = RED85.badges + ((W.created_n or 0) > 0 and 1 or 0)
    end
  end

  -- --------------------------------------------------------- 0h: tokens (both files)
  print("== HARNESS 85 - section 0h: the BLOCK-3 entries + the self-cast in BOTH files ==")
  for _, f in ipairs({ { name = "live", src = live_src85 }, { name = "ann", src = ann_src85 } }) do
    local nm, s = f.name, f.src
    local n_self = 0
    for _, e in ipairs(B3_SELF) do
      if raw_find(s, 'marker = "' .. e[1] .. '"', 1, true) ~= nil
        and raw_find(s, 'badge = "zz_auto_badge_' .. e[1] .. '"', 1, true) ~= nil
        and raw_find(s, '"' .. e[2] .. '"', 1, true) ~= nil then n_self = n_self + 1 end
    end
    check("0h " .. nm .. ": every BLOCK-3 in-melee-self entry is present (marker+badge+key: " .. n_self .. "/35)",
      n_self == 35)
    local n_ch = 0
    for _, e in ipairs(B3_CHARGE) do
      if raw_find(s, 'marker = "' .. e[1] .. '"', 1, true) ~= nil
        and raw_find(s, 'badge = "zz_auto_badge_' .. e[1] .. '"', 1, true) ~= nil
        and raw_find(s, '"' .. e[2] .. '"', 1, true) ~= nil then n_ch = n_ch + 1 end
    end
    check("0h " .. nm .. ": every BLOCK-3 charge-or-melee entry is present (marker+badge+key: " .. n_ch .. "/3)",
      n_ch == 3)
    check("0h " .. nm .. ": the block-3 entries REUSE the existing evaluators (no new evaluator function)",
      raw_find(s, "function FOURTH.evaluate_in_melee_self(unit, routing)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.evaluate_charge_or_melee(unit, routing)", 1, true) ~= nil)
    local mu = cp(s, 'trigger = "melee_unwavering"')
    check("0h " .. nm .. ": the melee_unwavering entry count grew to 91 (got " .. mu .. ")",
      mu == 91)
    local cm = cp(s, 'trigger = "charge_or_melee"')
    check("0h " .. nm .. ": the charge_or_melee entry count grew to 4 (got " .. cm .. ")",
      cm == 4)
    -- JOB 1: the cast target is the owner, the ally write is gone, the trigger stays
    check("0h " .. nm .. ": the Glorious Death cast target is ALWAYS the owner (FOURTH.cast_target = unit x"
      .. cp(s, "FOURTH.cast_target = unit") .. ", want 2)",
      cp(s, "FOURTH.cast_target = unit") == 2)
    check("0h " .. nm .. ": the OLD ally write is GONE (no FOURTH.cast_target = best_unit)",
      raw_find(s, "FOURTH.cast_target = best_unit", 1, true) == nil)
    check("0h " .. nm .. ": the Slayer TRIGGER tokens are unchanged (list + reader + scan + self gate)",
      raw_find(s, "FOURTH.slayer_keys = {", 1, true) ~= nil
      and raw_find(s, "function FOURTH.is_slayer(unit)", 1, true) ~= nil
      and raw_find(s, "and FOURTH.is_slayer(other) then", 1, true) ~= nil
      and raw_find(s, "FOURTH.is_slayer(unit) and unit:is_in_melee()", 1, true) ~= nil)
  end
  check("0h live: the self-cast reasons exist (slayer in melee (self-cast) / self in melee (self-cast))",
    raw_find(live_src85, 'reason = "slayer in melee (self-cast)"', 1, true) ~= nil
    and raw_find(live_src85, 'reason = "self in melee (self-cast)"', 1, true) ~= nil)
  check("0h live: the OLD ally-target reasons are GONE",
    raw_find(live_src85, 'reason = "slayer ally in melee (priority)"', 1, true) == nil
    and raw_find(live_src85, 'reason = "self slayer fallback (in melee)"', 1, true) == nil)
  check("0h ann: the reading copy stays log-free and find-free",
    raw_find(ann_src85, "log(", 1, true) == nil and raw_find(ann_src85, "string.find", 1, true) == nil)

  -- ==========================================================================
  -- X1. GLORIOUS DEATH - THE SELF-CAST ASSERTION. The caster (a Slayer) is in
  --     melee with an in-melee SLAYER ally: the trigger fires, and the CAST
  --     TARGET IS THE OWNER ITSELF - the ally is NEVER passed (the field-test
  --     defect: the Lord was ordered to walk to the Slayer ally).
  -- ==========================================================================
  local function world_x1(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = SL_DAEMON, uid = 9601, owns = { GLAD }, melee = true, wavering = false },
      { name = SL_UNIT,   uid = 9602, owns = {}, melee = true, health_percent = 60 },
    }, cards = {
      { id = "9601", state = "active", vis = true }, { id = "9602", state = "active", vis = true },
    }, bar = { { id = "b1", key = GLAD } } })
    print("== " .. TAG .. "X1. GLORIOUS DEATH: the cast target is ALWAYS the OWNER, never the Slayer ally == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "X1: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9601, true); ui(W); ui(W)
    click(W, badd("glorious_death")); ui(W)
    W.conflict = true
    polln(W, 1)
    local caster = unit_of(W, 9601)
    local ally = unit_of(W, 9602)
    local a = (#W.fires == 1 and W.fires[1].uid == 9601 and W.fires[1].key == GLAD)
    check(TAG .. "X1a: the caster fired glorious_death exactly once (" .. fire_detail(W) .. ")", a)
    local tgt = fire_target_for(W, 9601)
    local b = (tgt ~= nil and tgt == caster)
    check(TAG .. "X1b: the CAST TARGET IS THE OWNER itself (target is caster " .. tostring(tgt == caster) .. ")", b)
    local c = (ally ~= nil and tgt ~= ally)
    check(TAG .. "X1c: the in-melee Slayer ally is NEVER passed as the cast target (target is ally "
      .. tostring(tgt == ally) .. ")", c)
    local d = (count_log(W, "reason: slayer in melee (self-cast)") == 1)
    check(TAG .. "X1d: the reason says self-cast ('slayer in melee (self-cast)') [live log]", lg(TAG, d))
    note85(W, TAG)
    tally(W)
    return a and b and c and lg(TAG, d)
  end

  -- ==========================================================================
  -- X2. THE SLAYER-IN-MELEE TRIGGER WITH SELF-CAST (the exact field defect).
  --     The owner is NOT in melee; a SLAYER ally is. The trigger still fires
  --     (the candidate set is unchanged) but the cast goes to the OWNER, so
  --     the Lord is never ordered to walk to the ally.
  -- ==========================================================================
  local function world_x2(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = SL_DAEMON, uid = 9611, owns = { GLAD }, melee = false, wavering = false },
      { name = SL_UNIT,   uid = 9612, owns = {}, melee = true, health_percent = 50 },
    }, cards = {
      { id = "9611", state = "active", vis = true }, { id = "9612", state = "active", vis = true },
    }, bar = { { id = "b1", key = GLAD } } })
    print("== " .. TAG .. "X2. GLORIOUS DEATH: a Slayer ally in melee arms it, but the cast is on SELF == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "X2: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9611, true); ui(W); ui(W)
    click(W, badd("glorious_death")); ui(W)
    W.conflict = true
    polln(W, 1)
    local caster = unit_of(W, 9611)
    local ally = unit_of(W, 9612)
    local a = (#W.fires == 1 and W.fires[1].uid == 9611 and W.fires[1].key == GLAD)
    check(TAG .. "X2a: the owner (NOT itself in melee) fired because a Slayer ally is in melee ("
      .. fire_detail(W) .. ")", a)
    local tgt = fire_target_for(W, 9611)
    local b = (tgt == caster and tgt ~= ally)
    check(TAG .. "X2b: the cast target is the OWNER, NOT the Slayer that armed it (caster " .. tostring(tgt == caster)
      .. ", ally " .. tostring(tgt == ally) .. ")", b)
    local c = (count_log(W, "reason: slayer in melee (self-cast)") == 1)
    check(TAG .. "X2c: the reason says self-cast [live log]", lg(TAG, c))
    note85(W, TAG)
    tally(W)
    return a and b and lg(TAG, c)
  end

  -- ==========================================================================
  -- X3. SELF IN MELEE, NO SLAYER ALLY: the owner (a Slayer) is in melee with a
  --     NON-Slayer ally only -> the self arm fires, cast on SELF, reason
  --     'self in melee (self-cast)'. The non-Slayer ally is never targeted.
  -- ==========================================================================
  local function world_x3(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = SL_DAEMON,  uid = 9621, owns = { GLAD }, melee = true, wavering = false },
      { name = NON_SLAYER, uid = 9622, owns = {}, melee = true, health_percent = 20 },
    }, cards = {
      { id = "9621", state = "active", vis = true }, { id = "9622", state = "active", vis = true },
    }, bar = { { id = "b1", key = GLAD } } })
    print("== " .. TAG .. "X3. GLORIOUS DEATH: Slayer owner in melee, no Slayer ally -> self-cast == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "X3: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9621, true); ui(W); ui(W)
    click(W, badd("glorious_death")); ui(W)
    W.conflict = true
    polln(W, 1)
    local caster = unit_of(W, 9621)
    local ally = unit_of(W, 9622)
    local tgt = fire_target_for(W, 9621)
    local a = (#W.fires == 1 and W.fires[1].uid == 9621 and tgt == caster and tgt ~= ally)
    check(TAG .. "X3a: the Slayer owner self-casts (target is caster " .. tostring(tgt == caster)
      .. "); the in-melee NON-Slayer ally is NOT targeted (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "reason: self in melee (self-cast)") == 1)
    check(TAG .. "X3b: the reason says self-cast ('self in melee (self-cast)') [live log]", lg(TAG, b))
    note85(W, TAG)
    tally(W)
    return a and lg(TAG, b)
  end

  -- ==========================================================================
  -- S3. THE 35 BLOCK-3 IN-MELEE-SELF ENTRIES FIRE ON IN-MELEE ALONE. 35 units,
  --     each owning one block-3 key, all in melee, all armed; ONE poll fires
  --     all 35 with the EXISTING shared in-melee reason. A 36th unit owning a
  --     key but NOT in melee stays silent.
  -- ==========================================================================
  local function world_s3(PATH, TAG)
    local units, cards, bar, uids, ids = {}, {}, {}, {}, {}
    for i = 1, 35 do
      local marker, key = B3_SELF[i][1], B3_SELF[i][2]
      units[i] = { name = "b3_" .. marker, uid = 9700 + i, owns = { key }, melee = true, wavering = false }
      cards[i] = { id = tostring(9700 + i), state = "active", vis = true }
      bar[i] = { id = "b" .. i, key = key }
      uids[i] = 9700 + i
      ids[i] = badd(marker)
    end
    units[36] = { name = "b3_idle", uid = 9799, owns = { B3_SELF[1][2] }, melee = false }
    cards[36] = { id = "9799", state = "active", vis = true }
    bar[36] = { id = "b36", key = B3_SELF[1][2] }
    uids[36] = 9799
    local W = make_world({ can_perform = true, units = units, cards = cards, bar = bar })
    print("== " .. TAG .. "S3. THE 35 BLOCK-3 IN-MELEE-SELF ENTRIES FIRE ON IN-MELEE ALONE == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "S3: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W); ui(W)
    sel_group(W, uids); ui(W); ui(W)
    for i = 1, 35 do click(W, ids[i]); ui(W) end
    local armed_n = 0
    for i = 1, 35 do if badge_text(W, ids[i]) == "A" then armed_n = armed_n + 1 end end
    check(TAG .. "S3a: all 35 badges armed to A on their own clicks (" .. armed_n .. "/35)", armed_n == 35)
    W.conflict = true
    polln(W, 1)
    local fired, fired_keys = {}, {}
    for i = 1, #W.fires do fired[W.fires[i].uid] = true; fired_keys[W.fires[i].key] = true end
    local all_fired = (#W.fires == 35)
    local dk = 0
    for _ in pairs(fired_keys) do dk = dk + 1 end
    for i = 1, 35 do
      if fired[9700 + i] ~= true or fired_keys[B3_SELF[i][2]] ~= true then all_fired = false end
    end
    check(TAG .. "S3b: ALL 35 block-3 entries FIRED on in-melee alone (" .. #W.fires .. " fires, " .. dk
      .. " distinct keys - want 35/35)", all_fired and dk == 35)
    local reasons = count_log(W, "reason: in melee, morale not wavering")
    check(TAG .. "S3c: they carry the EXISTING shared in-melee reason (x" .. reasons .. ", want 35) [live log]",
      lg(TAG, reasons == 35))
    local idle_fired = false
    for i = 1, #W.fires do if W.fires[i].uid == 9799 then idle_fired = true end end
    check(TAG .. "S3d: the 36th unit (owns a key but is NOT in melee) stayed silent (fires " .. #W.fires .. ")",
      idle_fired == false and #W.fires == 35)
    check(TAG .. "S3e: exactly 35 components were created - one badge per marker, the duplicate adds none "
      .. "(created " .. W.created_n .. ")", W.created_n == 35)
    note85(W, TAG)
    tally(W)
    return armed_n == 35 and all_fired and lg(TAG, reasons == 35) and not idle_fired and W.created_n == 35
  end

  -- ==========================================================================
  -- F3. THE 3 BLOCK-3 CHARGE-OR-MELEE ENTRIES FIRE ON BOTH ARMS. For each key:
  --     a charging unit -> 'charging', an in-melee unit and a fast-in-melee
  --     unit -> the DISTINCT melee reason, an idle unit -> silent.
  -- ==========================================================================
  local function world_f3(PATH, TAG)
    local units, cards, bar, uids, ids = {}, {}, {}, {}, {}
    local n = 0
    for j = 1, 3 do
      local marker, key = B3_CHARGE[j][1], B3_CHARGE[j][2]
      local base = 9800 + (j - 1) * 10
      units[#units + 1] = { name = "ch_charge_" .. marker, uid = base + 1, owns = { key }, fast = true, melee = false, target = "e", dist = 20 }
      units[#units + 1] = { name = "ch_melee_" .. marker,  uid = base + 2, owns = { key }, fast = false, melee = true }
      units[#units + 1] = { name = "ch_both_" .. marker,   uid = base + 3, owns = { key }, fast = true, melee = true, target = "e", dist = 20 }
      units[#units + 1] = { name = "ch_idle_" .. marker,   uid = base + 4, owns = { key }, fast = false, melee = false }
      uids[#uids + 1] = base + 1; uids[#uids + 1] = base + 2
      uids[#uids + 1] = base + 3; uids[#uids + 1] = base + 4
      cards[#cards + 1] = { id = tostring(base + 1), state = "active", vis = true }
      cards[#cards + 1] = { id = tostring(base + 2), state = "active", vis = true }
      cards[#cards + 1] = { id = tostring(base + 3), state = "active", vis = true }
      cards[#cards + 1] = { id = tostring(base + 4), state = "active", vis = true }
      bar[#bar + 1] = { id = "bc" .. j, key = key }
      ids[#ids + 1] = badd(marker)
    end
    local W = make_world({ can_perform = true, units = units, cards = cards, bar = bar })
    print("== " .. TAG .. "F3. THE 3 BLOCK-3 CHARGE-OR-MELEE ENTRIES FIRE ON BOTH ARMS == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "F3: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_group(W, uids); ui(W); ui(W)
    for j = 1, 3 do click(W, ids[j]); ui(W) end
    W.conflict = true
    polln(W, 1)
    local fired = {}
    for i = 1, #W.fires do fired[W.fires[i].uid] = true end
    local all3 = true
    for j = 1, 3 do
      local base = 9800 + (j - 1) * 10
      if not (fired[base + 1] == true and fired[base + 2] == true and fired[base + 3] == true
        and fired[base + 4] ~= true) then all3 = false end
    end
    check(TAG .. "F3a: per key the charging, in-melee and fast-in-melee units fired; the idle stayed silent ("
      .. fire_detail(W) .. ")", all3 and #W.fires == 9)
    local chg = count_log(W, "reason: charging")
    check(TAG .. "F3b: THREE charge-window fires ('reason: charging...' x" .. chg .. ", want 3) [live log]",
      lg(TAG, chg == 3))
    local ml = count_log(W, "reason: in melee (charge or melee)")
    check(TAG .. "F3c: SIX melee fires carry the DISTINCT charge-or-melee reason (x" .. ml .. ", want 6) [live log]",
      lg(TAG, ml == 6))
    note85(W, TAG)
    tally(W)
    return all3 and #W.fires == 9 and lg(TAG, chg == 3) and lg(TAG, ml == 6)
  end

  print()
  print("== HARNESS 85 - GLORIOUS DEATH SELF-CAST + BLOCK 3 (38 approved entries) ==")
  local x1a = world_x1(ANN, "[annotated] "); local x1b = world_x1(LIVE, "[live] ")
  local x2a = world_x2(ANN, "[annotated] "); local x2b = world_x2(LIVE, "[live] ")
  local x3a = world_x3(ANN, "[annotated] "); local x3b = world_x3(LIVE, "[live] ")
  local s3a = world_s3(ANN, "[annotated] "); local s3b = world_s3(LIVE, "[live] ")
  local f3a = world_f3(ANN, "[annotated] "); local f3b = world_f3(LIVE, "[live] ")

  local results = { x1a, x1b, x2a, x2b, x3a, x3b, s3a, s3b, f3a, f3b }
  local n_ok = 0
  for _, r in ipairs(results) do if posv(r) then n_ok = n_ok + 1 end end

  check("every ui tick ran clean across the HARNESS-85 worlds (" .. RED85.ui .. " failures)", RED85.ui == 0)

  if not RED_MODE then
    check("the HARNESS-85 worlds all behaved (live+annotated: X1/X2/X3/S3/F3) - " .. n_ok .. "/10", n_ok == 10)
    check("HEADLINE (harness 85): GLORIOUS DEATH is FIXED - the TRIGGER keeps the harness-84 Slayer-only "
      .. "candidate set, but the CAST TARGET IS ALWAYS THE OWNER ITSELF, so the caster is never ordered to walk "
      .. "to the Slayer ally (reasons: 'slayer in melee (self-cast)' / 'self in melee (self-cast)'; the old ally "
      .. "write of FOURTH.cast_target is gone). BLOCK 3 ships 38 approved entries - the 35 in-melee-self keys "
      .. "ride the EXISTING shared melee_unwavering evaluator and the 3 charge-or-melee keys ride the EXISTING "
      .. "charge_or_melee evaluator (no new evaluator, no new chunk locals). Every earlier check re-ran unchanged "
      .. "except the forced count pins (A4 128->204, B4/H68/C6c 64->102, H68 key map 70->108) and the rewritten "
      .. "Glorious-Death worlds/reason tokens.", n_ok == 10)
  else
    check("RED CONTROL (harness 85): on the pre-edit snapshot the round's changes are ABSENT - the block-3 "
      .. "entries are missing (S3/F3 fail), Glorious Death still casts on the Slayer ally (X1/X2 fail, and X3's "
      .. "live reason), and the count pins still read 64/70 while the adapted pins expect 102/108. X3's ANNOTATED "
      .. "result passes by design (the pre-edit self arm already self-cast) - " .. n_ok
      .. "/10 world results pass (want 1), new fires " .. RED85.fires .. ", new claims " .. RED85.claims,
      n_ok == 1)
  end
end
run_h85()
