
-- ============================================================================
-- HARNESS 91 (this round): THE 327 AUTO-ACCEPTED ABILITIES - a BULK DATA
--   APPEND riding THREE EXISTING evaluators (no new trigger types):
--     in-melee self              -> melee_unwavering   261 entries / 274 keys
--     health<=75 (no melee gate) -> ushoran_health      36 entries /  37 keys
--     charge and in-melee        -> charge_or_melee     14 entries /  16 keys
--   The table grows 262 -> 573 entries (272 -> 599 keys). The rows were derived
--   PROGRAMMATICALLY from WH3_ability_tracker.md section 3a (every row marked
--   `approved (auto: <trigger>)`; provenance _classify_wh3.py). Base + DLC /
--   summoned twin keys ride ONE entry (the Foe-Seeker convention).
--   The new section's 0o tokens + the O worlds are appended before the final
--   find check; the adapted count pins are the SAME table-size pins the earlier
--   sections read (now 573/599).
--   RED CONTROL: with H91_LIVE / H91_ANN pointing at the pre-edit snapshot (the
--   shipped harness-90 build, 262 entries), the grown-table pins and this
--   HARNESS-91 section fail; the SILENT worlds pass trivially because the new
--   abilities are simply absent on the snapshot.
-- ============================================================================
function run_h91()
  -- the keys of the three new-member spot checks (+ a twin-key pair each)
  local M_MU1  = "wh2_twa03_weapon_abilities_whip_of_agony"          -- melee_unwavering (Whip of Agony)
  local M_MU2  = "wh3_dlc26_unit_abilities_waaagh_in_combat"         -- melee_unwavering (Waaagh! key 1)
  local M_MU2B = "wh_main_character_abilities_waaagh"                -- melee_unwavering (Waaagh! TWIN key 2)
  local M_U1   = "wh_main_item_abilities_potion_of_healing"          -- ushoran_health (Potion of Healing)
  local M_U2   = "wh2_dlc16_spell_bound_earth_blood"                 -- ushoran_health (Earth Blood key 1)
  local M_U2B  = "wh3_main_spell_bound_earth_blood"                  -- ushoran_health (Earth Blood TWIN key 2)
  local M_C1   = "wh3_dlc24_character_abilities_colossal_strike"     -- charge_or_melee (Colossal Strike base)
  local M_C1S  = "wh3_dlc24_character_abilities_colossal_strike_summoned" -- charge_or_melee (TWIN key)

  local live_src91 = read_file(LIVE)
  local ann_src91  = read_file(ANN)
  local RED91 = { fires = 0, claims = 0, ui = 0 }
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
  local function note91(W, TAG)
    RED91.ui = RED91.ui + (W.ui_failures or 0)
    if TAG == "[live] " then
      RED91.fires = RED91.fires + #W.fires
      RED91.claims = RED91.claims + count_log(W, "claim: ")
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

  -- --------------------------------------------------- 0o: tokens (both files)
  print("== HARNESS 91 - section 0o: the 327 auto-accepted abilities + grown table (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src91 }, { name = "ann", src = ann_src91 } }) do
    local nm, s = f.name, f.src
    check("0o " .. nm .. ": the three shared evaluators still exist (no new evaluator this round)",
      raw_find(s, "function FOURTH.evaluate_in_melee_self(unit, routing)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.evaluate_charge_or_melee(unit, routing)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.evaluate_ushoran_health(unit, routing)", 1, true) ~= nil)
    check("0o " .. nm .. ": the three trigger names are still wired in the map",
      raw_find(s, "melee_unwavering = FOURTH.evaluate_in_melee_self,", 1, true) ~= nil
      and raw_find(s, "charge_or_melee = FOURTH.evaluate_charge_or_melee,", 1, true) ~= nil
      and raw_find(s, "ushoran_health = FOURTH.evaluate_ushoran_health,", 1, true) ~= nil)
    check("0o " .. nm .. ": the grown table is 573 entries (each with a badge field)",
      cp(s, "\t{ marker = ") == 573 and cp(s, 'badge = "') == 573)
    check("0o " .. nm .. ": the trigger counts grew to (melee_unwavering 477, ushoran_health 41, charge_or_melee 29) "
      .. "and every other trigger is UNCHANGED (charge_only 1, wavering_self 3, wavering_self_or_ally 2, "
      .. "charge_or_wavering 1, wavering_ally_range 1, tired 2, metallurgy_melee 8, melee_health75 2)",
      cp(s, 'trigger = "melee_unwavering"') == 477 and cp(s, 'trigger = "ushoran_health"') == 41
      and cp(s, 'trigger = "charge_or_melee"') == 29 and cp(s, 'trigger = "charge_only"') == 1
      and cp(s, 'trigger = "wavering_self"') == 3 and cp(s, 'trigger = "wavering_self_or_ally"') == 2
      and cp(s, 'trigger = "charge_or_wavering"') == 1 and cp(s, 'trigger = "wavering_ally_range"') == 1
      and cp(s, 'trigger = "tired"') == 2 and cp(s, 'trigger = "metallurgy_melee"') == 8
      and cp(s, 'trigger = "melee_health75"') == 2)
    check("0o " .. nm .. ": every spot-check entry is present (marker + badge + key)",
      raw_find(s, 'marker = "whip_of_agony"', 1, true) ~= nil
      and raw_find(s, 'badge = "zz_auto_badge_whip_of_agony"', 1, true) ~= nil
      and raw_find(s, '"' .. M_MU1 .. '"', 1, true) ~= nil
      and raw_find(s, 'marker = "waaagh_in_combat"', 1, true) ~= nil
      and raw_find(s, '"' .. M_MU2B .. '"', 1, true) ~= nil
      and raw_find(s, 'marker = "potion_of_healing"', 1, true) ~= nil
      and raw_find(s, 'marker = "colossal_strike"', 1, true) ~= nil
      and raw_find(s, '"' .. M_C1S .. '"', 1, true) ~= nil)
    check("0o " .. nm .. ": the two NAME-collision fallback markers are used, so no marker is duplicated "
      .. "(horn_of_vaul + whip_of_misery present; the naive key markers are NOT duplicated)",
      raw_find(s, 'marker = "horn_of_vaul"', 1, true) ~= nil
      and raw_find(s, 'marker = "whip_of_misery"', 1, true) ~= nil
      and cp(s, 'marker = "dragonhorn"') == 1 and cp(s, 'marker = "whip_of_agony"') == 1)
    check("0o " .. nm .. ": NO army-bar key is in the mod (standing exclusion)", 
      raw_find(s, "army_abilities", 1, true) == nil)
  end
  check("0o ann: the reading copy stays log-free and find-free",
    raw_find(ann_src91, "log(", 1, true) == nil and raw_find(ann_src91, "string.find(", 1, true) == nil)
  check("0o live: the new bulk block is documented as a DATA append (311 entries / 327 keys)",
    raw_find(live_src91, "THE 327 AUTO-ACCEPTED ABILITIES (this round)", 1, true) ~= nil
    and raw_find(live_src91, "311 entries /", 1, true) ~= nil
    and raw_find(live_src91, "327 database keys", 1, true) ~= nil)

  -- ==========================================================================
  -- O1. MELEE_UNWAVERING: a NEW in-melee-self member (Whip of Agony) FIRES in
  --     melee with the shared in-melee-self reason, self-cast.
  -- ==========================================================================
  local function world_o1(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "whip", uid = 9201, owns = { M_MU1 }, melee = true, wavering = false },
    }, cards = { { id = "9201", state = "active", vis = true } }, bar = { { id = "b1", key = M_MU1 } } })
    print("== " .. TAG .. "O1. MELEE_UNWAVERING member: in melee -> FIRES (whip_of_agony) == ")
    if not boot(W, PATH, TAG, 9201, "whip_of_agony", "O1") then return nil end
    polln(W, 1)
    local a = (#W.fires == 1 and W.fires[1].uid == 9201 and W.fires[1].key == M_MU1)
    check(TAG .. "O1a: the in-melee unit fired whip_of_agony once (" .. fire_detail(W) .. ")", a)
    local b = (fire_target_for(W, 9201) == unit_of(W, 9201))
    check(TAG .. "O1b: the cast target is the OWNER itself (self-cast)", b)
    local c = (count_log(W, "reason: in melee, morale not wavering") == 1)
    check(TAG .. "O1c: the shared in-melee-self reason is used [live log]", lg(TAG, c))
    note91(W, TAG); tally(W)
    return a and b and lg(TAG, c)
  end

  -- ==========================================================================
  -- O2. MELEE_UNWAVERING, SILENT: a NEW member NOT in melee -> SILENT.
  -- ==========================================================================
  local function world_o2(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "whip", uid = 9202, owns = { M_MU1 }, melee = false, wavering = false },
    }, cards = { { id = "9202", state = "active", vis = true } }, bar = { { id = "b1", key = M_MU1 } } })
    print("== " .. TAG .. "O2. MELEE_UNWAVERING member: NOT in melee -> SILENT == ")
    if not boot(W, PATH, TAG, 9202, "whip_of_agony", "O2") then return nil end
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "O2a: the out-of-melee unit stays SILENT (" .. fire_detail(W) .. ")", a)
    note91(W, TAG); tally(W)
    return a
  end

  -- ==========================================================================
  -- O3. TWIN KEYS RIDE ONE ENTRY: the Waaagh! entry carries BOTH its base and
  --     DLC keys, so a unit owning ONLY the twin key still fires it once.
  -- ==========================================================================
  local function world_o3(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "waaagh", uid = 9203, owns = { M_MU2B }, melee = true, wavering = false },
    }, cards = { { id = "9203", state = "active", vis = true } }, bar = { { id = "b1", key = M_MU2B } } })
    print("== " .. TAG .. "O3. TWIN KEYS: the DLC/base twin key fires the SAME entry (Waaagh!) == ")
    if not boot(W, PATH, TAG, 9203, "waaagh_in_combat", "O3") then return nil end
    polln(W, 1)
    local a = (#W.fires == 1 and W.fires[1].uid == 9203 and W.fires[1].key == M_MU2B)
    check(TAG .. "O3a: a unit owning only the TWIN key fired the shared entry (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "reason: in melee, morale not wavering") == 1)
    check(TAG .. "O3b: it rode the shared in-melee-self evaluator [live log]", lg(TAG, b))
    note91(W, TAG); tally(W)
    return a and lg(TAG, b)
  end

  -- ==========================================================================
  -- U1. USHORAN_HEALTH: a NEW heal member fires at own health <= 75% with NO
  --     melee requirement (the "no melee gate" rule), self-cast.
  -- ==========================================================================
  local function world_u1(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "healer", uid = 9204, owns = { M_U1 }, melee = false, health_percent = 70 },
    }, cards = { { id = "9204", state = "active", vis = true } }, bar = { { id = "b1", key = M_U1 } } })
    print("== " .. TAG .. "U1. USHORAN_HEALTH member: health 70%, NOT in melee -> FIRES (no melee gate) == ")
    if not boot(W, PATH, TAG, 9204, "potion_of_healing", "U1") then return nil end
    polln(W, 1)
    local a = (#W.fires == 1 and W.fires[1].uid == 9204 and W.fires[1].key == M_U1)
    check(TAG .. "U1a: the <=75%-health unit fired potion_of_healing WITHOUT being in melee (" .. fire_detail(W) .. ")", a)
    local b = (fire_target_for(W, 9204) == unit_of(W, 9204))
    check(TAG .. "U1b: the cast target is the OWNER itself (self-cast)", b)
    local c = (count_log(W, "reason: health 70% (<= 75%)") == 1)
    check(TAG .. "U1c: the health reason names the live percent [live log]", lg(TAG, c))
    note91(W, TAG); tally(W)
    return a and b and lg(TAG, c)
  end

  -- ==========================================================================
  -- U2. USHORAN_HEALTH, SILENT: health above 75% -> SILENT.
  -- ==========================================================================
  local function world_u2(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "healthy", uid = 9205, owns = { M_U1 }, melee = false, health_percent = 90 },
    }, cards = { { id = "9205", state = "active", vis = true } }, bar = { { id = "b1", key = M_U1 } } })
    print("== " .. TAG .. "U2. USHORAN_HEALTH member: health 90% -> SILENT == ")
    if not boot(W, PATH, TAG, 9205, "potion_of_healing", "U2") then return nil end
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "U2a: the 90%-health unit stays SILENT (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "reason: health 9") == 0)
    check(TAG .. "U2b: no health reason was emitted [live log]", lg(TAG, b))
    note91(W, TAG); tally(W)
    return a and lg(TAG, b)
  end

  -- ==========================================================================
  -- U3. USHORAN_HEALTH TWIN KEYS: the Earth Blood entry carries both its wh2
  --     and wh3 keys, so a unit owning ONLY the wh3 twin still fires it once.
  -- ==========================================================================
  local function world_u3(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "earth", uid = 9206, owns = { M_U2B }, melee = false, health_percent = 60 },
    }, cards = { { id = "9206", state = "active", vis = true } }, bar = { { id = "b1", key = M_U2B } } })
    print("== " .. TAG .. "U3. USHORAN_HEALTH TWIN: the wh3 twin key fires the Earth Blood entry == ")
    if not boot(W, PATH, TAG, 9206, "earth_blood", "U3") then return nil end
    polln(W, 1)
    local a = (#W.fires == 1 and W.fires[1].uid == 9206 and W.fires[1].key == M_U2B)
    check(TAG .. "U3a: a unit owning only the wh3 twin key fired the shared Earth Blood entry (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "reason: health 60% (<= 75%)") == 1)
    check(TAG .. "U3b: it rode the shared ushoran_health evaluator [live log]", lg(TAG, b))
    note91(W, TAG); tally(W)
    return a and lg(TAG, b)
  end

  -- ==========================================================================
  -- C1. CHARGE_OR_MELEE: a NEW charge member (Colossal Strike) FIRES on the
  --     charge window, self-cast.
  -- ==========================================================================
  local function world_c1(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "striker", uid = 9207, owns = { M_C1 }, fast = true, melee = false, target = true, dist = 20, wavering = false },
    }, cards = { { id = "9207", state = "active", vis = true } }, bar = { { id = "b1", key = M_C1 } } })
    print("== " .. TAG .. "C1. CHARGE_OR_MELEE member: charging -> FIRES (colossal_strike) == ")
    if not boot(W, PATH, TAG, 9207, "colossal_strike", "C1") then return nil end
    polln(W, 1)
    local a = (#W.fires == 1 and W.fires[1].uid == 9207 and W.fires[1].key == M_C1)
    check(TAG .. "C1a: the charging unit fired colossal_strike once (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "reason: charging (") == 1)
    check(TAG .. "C1b: the charge reason is used [live log]", lg(TAG, b))
    note91(W, TAG); tally(W)
    return a and lg(TAG, b)
  end

  -- ==========================================================================
  -- C2. CHARGE_OR_MELEE, MELEE ARM + TWIN KEY: a unit owning ONLY the summoned
  --     twin key, in melee (not charging), fires the SAME entry off the melee arm.
  -- ==========================================================================
  local function world_c2(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "summoned", uid = 9208, owns = { M_C1S }, fast = false, melee = true, wavering = false },
    }, cards = { { id = "9208", state = "active", vis = true } }, bar = { { id = "b1", key = M_C1S } } })
    print("== " .. TAG .. "C2. CHARGE_OR_MELEE twin key: in melee, not charging -> FIRES (melee arm) == ")
    if not boot(W, PATH, TAG, 9208, "colossal_strike", "C2") then return nil end
    polln(W, 1)
    local a = (#W.fires == 1 and W.fires[1].uid == 9208 and W.fires[1].key == M_C1S)
    check(TAG .. "C2a: the summoned twin key met the charge-or-melee entry (" .. fire_detail(W) .. ")", a)
    local b = (fire_target_for(W, 9208) == unit_of(W, 9208))
    check(TAG .. "C2b: the cast target is the OWNER itself (self-cast)", b)
    local c = (count_log(W, "reason: in melee (charge or melee)") == 1)
    check(TAG .. "C2c: the melee arm of the charge-or-melee trigger is used [live log]", lg(TAG, c))
    note91(W, TAG); tally(W)
    return a and b and lg(TAG, c)
  end

  print()
  print("== HARNESS 91 - the 327 auto-accepted abilities riding three existing evaluators ==")
  local o01a = world_o1(ANN, "[annotated] ");  local o01b = world_o1(LIVE, "[live] ")
  local o02a = world_o2(ANN, "[annotated] ");  local o02b = world_o2(LIVE, "[live] ")
  local o03a = world_o3(ANN, "[annotated] ");  local o03b = world_o3(LIVE, "[live] ")
  local u01a = world_u1(ANN, "[annotated] ");  local u01b = world_u1(LIVE, "[live] ")
  local u02a = world_u2(ANN, "[annotated] ");  local u02b = world_u2(LIVE, "[live] ")
  local u03a = world_u3(ANN, "[annotated] ");  local u03b = world_u3(LIVE, "[live] ")
  local c01a = world_c1(ANN, "[annotated] ");  local c01b = world_c1(LIVE, "[live] ")
  local c02a = world_c2(ANN, "[annotated] ");  local c02b = world_c2(LIVE, "[live] ")

  local results = { o01a, o01b, o02a, o02b, o03a, o03b, u01a, u01b, u02a, u02b, u03a, u03b, c01a, c01b, c02a, c02b }
  local n_ok = 0
  for _, r in ipairs(results) do if posv(r) then n_ok = n_ok + 1 end end

  check("every ui tick ran clean across the HARNESS-91 worlds (" .. RED91.ui .. " failures)", RED91.ui == 0)

  if not RED_MODE then
    check("the HARNESS-91 worlds all behaved (live+annotated: O1..C2) - " .. n_ok .. "/16", n_ok == 16)
    check("HEADLINE (harness 91): THE 327 AUTO-ACCEPTED ABILITIES ship as a BULK DATA APPEND - 311 entries / " 
      .. "327 database keys riding THREE EXISTING evaluators (274 in-melee-self rows -> melee_unwavering; 37 " 
      .. "health<=75 (no melee gate) rows -> ushoran_health; 16 charge-and-in-melee rows -> charge_or_melee). " 
      .. "Base + DLC/summoned twin keys ride ONE entry (the Foe-Seeker convention); two NAME-collision entries " 
      .. "(Horn of Vaul, Whip of Misery) take a name-derived marker so no marker repeats. The table grows 262 -> " 
      .. "573 entries (272 -> 599 keys); no new trigger types, no new chunk locals.", n_ok == 16)
  else
    check("RED CONTROL (harness 91): on the pre-edit snapshot (the shipped harness-90 build, 262 entries) the " 
      .. "grown-table pins and this HARNESS-91 section fail; the SILENT worlds pass trivially because the new " 
      .. "abilities are simply absent on the snapshot (O2 / U2 both files = 4, plus the ANNOTATED legs of the " 
      .. "live-only log checks) - " .. n_ok .. "/16 world results pass (want 6), fires " .. RED91.fires 
      .. ", claims " .. RED91.claims, n_ok == 6)
  end
end
run_h91()
