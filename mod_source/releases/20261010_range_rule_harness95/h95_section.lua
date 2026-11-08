-- ============================================================================
-- HARNESS 95 - THE STANDING 70% RANGE RULE (this round).
--   The user's rule: EVERY trigger-range constant = AT MOST 70% of the ability's
--   REAL game-data range, rounded DOWN to a whole metre, with NO exceptions
--   ("...No exceptions."). The symptom it removes: the caster WALKING toward a
--   target inside the ability's reach but outside a comfortable cast range.
--   Re-derived (real -> floor(real * 0.70)):
--     GLORIOUS DEATH 55 -> 38 ; VERMINKING 35 -> 24 ; METALLURGY 35 -> 24 ;
--     WAVERING 35 -> 24 ; BLOOD SACRIFICE 100 -> 70 ; EAT DA RUNTS 100 -> 70 ;
--     ACCUSATION 75 -> 52.
--   BOUNDARY WORLDS (each live + annotated): for EACH changed constant, an
--   ALLY/ENEMY just inside the NEW 70% bound FIRES, and a target between 70%
--   and 100% of the REAL range (the movement-prone zone) stays SILENT.
--   RED CONTROL: with H95_LIVE / H95_ANN pointing at the pre-edit snapshot (the
--   shipped harness-94 build: GD 25, VM 25, MT 25, WV 25, BS 25, EDR 25, ACC 75)
--   the 0s tokens and the half of the boundary worlds that sit INSIDE the new
--   bound fail by design (14/28 pass), every earlier pin that moved fails, and
--   every earlier world passes.
-- ============================================================================
function run_h95()
  local GDK = "wh3_dlc25_lord_abilities_glorious_death"
  local VMK = "wh3_dlc29_lord_abilities_will_of_the_verminking"
  local MTK = "wh3_main_character_abilities_enchanted_metallurgy"
  local WUK = "wh3_dlc29_spell_bound_prayer_fury_of_ulric"
  local BSK = "wh3_dlc26_lord_abilities_blood_sacrifice"
  local EDK = "wh3_dlc26_unit_abilities_eat_da_runts"
  local ACK = "wh_main_hero_abilities_accusation"
  local SL_DAEMON = "wh3_dlc25_dwf_cha_daemon_slayer"
  local SL_UNIT   = "wh_main_dwf_inf_slayers"

  local live_src95 = read_file(LIVE)
  local ann_src95  = read_file(ANN)
  local RED95 = { fires = 0, claims = 0, ui = 0 }
  local function posv(v) return (v == true) or (type(v) == "number") end
  local function lg(tag, v) return (tag ~= "[live] ") or posv(v) end
  local function badd95(marker) return "zz_auto_badge_" .. marker end
  local function cp95(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function note95(W, TAG)
    RED95.ui = RED95.ui + (W.ui_failures or 0)
    if TAG == "[live] " then
      RED95.fires = RED95.fires + #W.fires
      RED95.claims = RED95.claims + count_log(W, "claim: ")
    end
  end
  local function boot95(W, PATH, TAG, uid, marker, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, badd95(marker)); ui(W)
    W.conflict = true
    return true
  end

  -- --------------------------------------------------- 0s: tokens (both files)
  print("== HARNESS 95 - section 0s: the standing 70% range rule (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src95 }, { name = "ann", src = ann_src95 } }) do
    local nm, s = f.name, f.src
    check("0s " .. nm .. ": the rule constant FOURTH.RANGE_FRACTION = 0.70 exists",
      raw_find(s, "FOURTH.RANGE_FRACTION = 0.70", 1, true) ~= nil)
    check("0s " .. nm .. ": GLORIOUS DEATH = 38 (55 * 0.70, floored)",
      raw_find(s, "local GLORIOUS_DEATH_RANGE_M = 38", 1, true) ~= nil)
    check("0s " .. nm .. ": the old field-tuned 25 m Glorious Death gate is GONE (no exceptions)",
      raw_find(s, "local GLORIOUS_DEATH_RANGE_M = 25", 1, true) == nil)
    check("0s " .. nm .. ": VERMINKING = 24 (35 * 0.70, floored)",
      raw_find(s, "FOURTH.VERMINKING_RANGE_M = 24", 1, true) ~= nil)
    check("0s " .. nm .. ": METALLURGY = 24 (35 * 0.70, floored)",
      raw_find(s, "FOURTH.METALLURGY_RANGE_M = 24", 1, true) ~= nil)
    check("0s " .. nm .. ": WAVERING = 24 (35 * 0.70, floored)",
      raw_find(s, "FOURTH.WAVERING_RANGE_M = 24", 1, true) ~= nil)
    check("0s " .. nm .. ": BLOOD SACRIFICE = 70 (100 * 0.70)",
      raw_find(s, "FOURTH.BLOOD_SACRIFICE_RANGE_M = 70", 1, true) ~= nil)
    check("0s " .. nm .. ": EAT DA RUNTS = 70 (100 * 0.70)",
      raw_find(s, "FOURTH.EAT_DA_RUNTS_RANGE_M = 70", 1, true) ~= nil)
    check("0s " .. nm .. ": ACCUSATION = 52 (75 * 0.70, floored)",
      raw_find(s, "FOURTH.ACCUSATION_RANGE_M = 52", 1, true) ~= nil)
    check("0s " .. nm .. ": the old ACCUSATION 75 m constant is GONE",
      raw_find(s, "FOURTH.ACCUSATION_RANGE_M = 75", 1, true) == nil)
    check("0s " .. nm .. ": the per-constant comments carry the real range and the 70% derivation",
      raw_find(s, "55 * 0.70 = 38.5 -> 38", 1, true) ~= nil
      and raw_find(s, "35 * 0.70 = 24.5 -> 24", 1, true) ~= nil
      and raw_find(s, "100 * 0.70 = 70.0 -> 70", 1, true) ~= nil
      and raw_find(s, "75 * 0.70 = 52.5 -> 52", 1, true) ~= nil)
    check("0s " .. nm .. ": the charge-window pair is NOT an ability range and is UNCHANGED (12 / 60)",
      raw_find(s, "CHARGE_MIN_DISTANCE_M    = 12", 1, true) ~= nil
      and raw_find(s, "CHARGE_MAX_DISTANCE_M    = 60", 1, true) ~= nil)
    check("0s " .. nm .. ": the ability table is UNCHANGED (579 entries)",
      cp95(s, "\t{ marker = ") == 579)
  end

  -- ---------------------------------------------------------------- the worlds
  -- Each world: a friendly owner that owns the key, the marker's badge ARMED,
  -- and a candidate at a chosen distance. 'expect' = true when the ability
  -- should FIRE, false when it must stay SILENT. Bounds: GD 38 / VM 24 /
  -- MT 24 / WV 24 / BS 70 / EDR 70 / ACC 52.

  -- GLORIOUS DEATH: an in-melee Slayer ALLY at 'dist' m (owner NOT a Slayer-in-melee)
  local function world_gd(PATH, TAG, dist, expect, wname)
    local W = make_world({ can_perform = true, units = {
      { name = SL_DAEMON, uid = 9801, owns = { GDK }, melee = false, wavering = false },
      { name = SL_UNIT,   uid = 9802, owns = {}, melee = true, dist = dist },
    }, cards = {
      { id = "9801", state = "active", vis = true }, { id = "9802", state = "active", vis = true },
    }, bar = { { id = "b1", key = GDK } } })
    print("== " .. TAG .. wname .. ". GLORIOUS DEATH: an in-melee Slayer ally at " .. dist .. " m (bound 38) ==")
    if not boot95(W, PATH, TAG, 9801, "glorious_death", wname) then return nil end
    polln(W, 1)
    local fired = (#W.fires == 1 and W.fires[1].key == GDK)
    check(TAG .. wname .. "a: at " .. dist .. " m the ability " .. (expect and "FIRES" or "stays SILENT")
      .. " (" .. fire_detail(W) .. ")", fired == expect)
    note95(W, TAG); tally(W)
    return (fired == expect)
  end

  -- WILL OF THE VERMINKING: an in-melee WAVERING ally at 'dist' m
  local function world_vm(PATH, TAG, dist, expect, wname)
    local W = make_world({ can_perform = true, units = {
      { name = "skreech",  uid = 9811, owns = { VMK }, melee = false, wavering = false },
      { name = "clanrats", uid = 9812, owns = {}, melee = true, wavering = true, dist = dist },
    }, cards = {
      { id = "9811", state = "active", vis = true }, { id = "9812", state = "active", vis = true },
    }, bar = { { id = "b1", key = VMK } } })
    print("== " .. TAG .. wname .. ". VERMINKING: a wavering in-melee ally at " .. dist .. " m (bound 24) ==")
    if not boot95(W, PATH, TAG, 9811, "will_of_the_verminking", wname) then return nil end
    polln(W, 1)
    local fired = (#W.fires == 1 and W.fires[1].key == VMK)
    check(TAG .. wname .. "a: at " .. dist .. " m the ability " .. (expect and "FIRES" or "stays SILENT")
      .. " (" .. fire_detail(W) .. ")", fired == expect)
    note95(W, TAG); tally(W)
    return (fired == expect)
  end

  -- ENCHANTED METALLURGY: an in-melee ally at 'dist' m (owner NOT in melee)
  local function world_mt(PATH, TAG, dist, expect, wname)
    local W = make_world({ can_perform = true, units = {
      { name = "lord",     uid = 9821, owns = { MTK }, melee = false },
      { name = "infantry", uid = 9822, owns = {}, melee = true, dist = dist },
    }, cards = {
      { id = "9821", state = "active", vis = true }, { id = "9822", state = "active", vis = true },
    }, bar = { { id = "b1", key = MTK } } })
    print("== " .. TAG .. wname .. ". METALLURGY: an in-melee ally at " .. dist .. " m (bound 24) ==")
    if not boot95(W, PATH, TAG, 9821, "enchanted_metallurgy", wname) then return nil end
    polln(W, 1)
    local fired = (#W.fires == 1 and W.fires[1].key == MTK)
    check(TAG .. wname .. "a: at " .. dist .. " m the ability " .. (expect and "FIRES" or "stays SILENT")
      .. " (" .. fire_detail(W) .. ")", fired == expect)
    note95(W, TAG); tally(W)
    return (fired == expect)
  end

  -- WAVERING SELF-OR-ALLY (Fury of Ulric): an in-melee WAVERING ally at 'dist' m
  local function world_wv(PATH, TAG, dist, expect, wname)
    local W = make_world({ can_perform = true, units = {
      { name = "ulric",  uid = 9831, owns = { WUK }, melee = false, wavering = false },
      { name = "broken", uid = 9832, owns = {}, melee = true, wavering = true, dist = dist },
    }, cards = {
      { id = "9831", state = "active", vis = true }, { id = "9832", state = "active", vis = true },
    }, bar = { { id = "b1", key = WUK } } })
    print("== " .. TAG .. wname .. ". WAVERING: an in-melee wavering ally at " .. dist .. " m (bound 24) ==")
    if not boot95(W, PATH, TAG, 9831, "fury_of_ulric", wname) then return nil end
    polln(W, 1)
    local fired = (#W.fires == 1 and W.fires[1].key == WUK)
    check(TAG .. wname .. "a: at " .. dist .. " m the ability " .. (expect and "FIRES" or "stays SILENT")
      .. " (" .. fire_detail(W) .. ")", fired == expect)
    note95(W, TAG); tally(W)
    return (fired == expect)
  end

  -- BLOOD SACRIFICE: a hurt ally (40% health) at 'dist' m
  local function world_bs(PATH, TAG, dist, expect, wname)
    local W = make_world({ can_perform = true, units = {
      { name = "lord", uid = 9841, owns = { BSK }, melee = false, health_percent = 100 },
      { name = "ally", uid = 9842, owns = {}, melee = false, health_percent = 40, dist = dist },
    }, cards = {
      { id = "9841", state = "active", vis = true }, { id = "9842", state = "active", vis = true },
    }, bar = { { id = "b1", key = BSK } } })
    print("== " .. TAG .. wname .. ". BLOOD SACRIFICE: a 40% ally at " .. dist .. " m (bound 70) ==")
    if not boot95(W, PATH, TAG, 9841, "blood_sacrifice", wname) then return nil end
    polln(W, 1)
    local fired = (#W.fires == 1 and W.fires[1].key == BSK)
    check(TAG .. wname .. "a: at " .. dist .. " m the ability " .. (expect and "FIRES" or "stays SILENT")
      .. " (" .. fire_detail(W) .. ")", fired == expect)
    note95(W, TAG); tally(W)
    return (fired == expect)
  end

  -- EAT DA RUNTS!: a hurt ally (50% health) at 'dist' m (owner healthy)
  local function world_ed(PATH, TAG, dist, expect, wname)
    local W = make_world({ can_perform = true, units = {
      { name = "unit", uid = 9851, owns = { EDK }, melee = false, health_percent = 100 },
      { name = "ally", uid = 9852, owns = {}, melee = false, health_percent = 50, dist = dist },
    }, cards = {
      { id = "9851", state = "active", vis = true }, { id = "9852", state = "active", vis = true },
    }, bar = { { id = "b1", key = EDK } } })
    print("== " .. TAG .. wname .. ". EAT DA RUNTS: a 50% ally at " .. dist .. " m (bound 70) ==")
    if not boot95(W, PATH, TAG, 9851, "eat_da_runts", wname) then return nil end
    polln(W, 1)
    local fired = (#W.fires == 1 and W.fires[1].key == EDK)
    check(TAG .. wname .. "a: at " .. dist .. " m the ability " .. (expect and "FIRES" or "stays SILENT")
      .. " (" .. fire_detail(W) .. ")", fired == expect)
    note95(W, TAG); tally(W)
    return (fired == expect)
  end

  -- ACCUSATION: an in-melee ENEMY at 'dist' m (distance fallback; no unit_in_range)
  local function world_acc(PATH, TAG, dist, expect, wname)
    local W = make_world({ can_perform = true,
      units = { { name = "witch_hunter", uid = 9861, owns = { ACK }, melee = false,
                  dist_by_target = { [9862] = dist } } },
      enemies = { { name = "orc_boyz", uid = 9862, melee = true } },
      cards = { { id = "9861", state = "active", vis = true } },
      bar = { { id = "b1", key = ACK } } })
    print("== " .. TAG .. wname .. ". ACCUSATION: an in-melee enemy at " .. dist .. " m (bound 52) ==")
    if not boot95(W, PATH, TAG, 9861, "accusation", wname) then return nil end
    polln(W, 1)
    local fired = (#W.fires == 1 and W.fires[1].key == ACK)
    check(TAG .. wname .. "a: at " .. dist .. " m the ability " .. (expect and "FIRES" or "stays SILENT")
      .. " (" .. fire_detail(W) .. ")", fired == expect)
    note95(W, TAG); tally(W)
    return (fired == expect)
  end

  print()
  print("== HARNESS 95 - the 70% boundary worlds (each live + annotated) ==")
  local res = {}
  local function run_all(fn, dist, expect, wname)
    res[#res + 1] = fn(LIVE, "[live] ", dist, expect, wname)
    res[#res + 1] = fn(ANN,  "[ann]  ", dist, expect, wname)
  end
  run_all(world_gd,  38, true,  "G1")   -- just inside the new 38 m bound -> FIRES
  run_all(world_gd,  45, false, "G2")   -- between 38 and 55 (the movement zone) -> SILENT
  run_all(world_vm,  24, true,  "V1")   -- just inside 24 -> FIRES
  run_all(world_vm,  25, false, "V2")   -- between 24 and 35 -> SILENT
  run_all(world_mt,  24, true,  "M1")
  run_all(world_mt,  25, false, "M2")
  run_all(world_wv,  24, true,  "W1")
  run_all(world_wv,  25, false, "W2")
  run_all(world_bs,  70, true,  "B1")   -- just inside 70 -> FIRES
  run_all(world_bs,  71, false, "B2")   -- between 70 and 100 -> SILENT
  run_all(world_ed,  70, true,  "E1")
  run_all(world_ed,  71, false, "E2")
  run_all(world_acc, 52, true,  "A1")   -- just inside 52 -> FIRES
  run_all(world_acc, 70, false, "A2")   -- between 52 and 75 (the reported WALK zone) -> SILENT

  local n_ok = 0
  for _, r in ipairs(res) do if posv(r) then n_ok = n_ok + 1 end end
  print("== HARNESS 95 - boundary worlds: " .. n_ok .. "/" .. #res .. " passed; fires " .. RED95.fires .. " ==")

  check("every ui tick ran clean across the HARNESS-95 worlds (" .. RED95.ui .. " failures)", RED95.ui == 0)

  if not RED_MODE then
    check("HEADLINE (harness 95): the user's STANDING 70% RANGE RULE ships - EVERY trigger-range constant is "
      .. "floor(0.70 * the ability's REAL game-data range): GLORIOUS DEATH 55->38, VERMINKING 35->24, METALLURGY "
      .. "35->24, WAVERING 35->24, BLOOD SACRIFICE 100->70, EAT DA RUNTS 100->70, ACCUSATION 75->52 - with NO "
      .. "exceptions (the old field-tuned 25 m Glorious Death gate is replaced by 38 m at the user's direction). "
      .. "For each constant an ally/enemy just INSIDE the new bound FIRES and one between 70% and 100% (the "
      .. "movement-prone zone) stays SILENT; all " .. #res .. " boundary worlds passed.",
      n_ok == #res)
  else
    check("RED CONTROL (harness 95): on the pre-edit snapshot (the shipped harness-94 build: GD 25, VM 25, MT 25, "
      .. "WV 25, BS 25, EDR 25, ACC 75) the 0s tokens fail and only the worlds whose target sits OUTSIDE the OLD "
      .. "bound pass by design (G2/V1/M1/W1/B2/E2/A1) - the worlds INSIDE the new bound fire nothing on the "
      .. "snapshot: " .. n_ok .. "/" .. #res .. " world results pass (want 14), fires "
      .. RED95.fires .. ", claims " .. RED95.claims, n_ok == 14)
  end
end
run_h95()
