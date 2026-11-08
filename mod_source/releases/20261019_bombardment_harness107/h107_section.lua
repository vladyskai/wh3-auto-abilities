-- ============================================================================
-- HARNESS 107 - THE REMAINING BOMBARDMENT WORK (round 107)
--
-- WHAT THIS SECTION PROVES, against the LIVE source AND the annotated copy:
--
--   item 2 - CALL OF TOR on melee_skip_commanders (Soulfire's trigger):
--     fires when a non-commander enemy is in contact; SILENT when the only
--     engaged enemy is a Lord/Hero; the judged engagement set is logged.
--   item 3 - THE "ON TOP OF" FAMILY on the NEW air_drop_on_infantry:
--     A1 fires on an INFANTRY enemy under a FLYING caster, and the cast is on
--        the OWNER (the row has no target flags at all);
--     A2 silent on a non-infantry unit under the caster;
--     A3 silent when an air-only ability's caster is NOT flying;
--     A4 silent when is_currently_flying() is UNREADABLE (fail-closed);
--     A5 silent when the infantry unit is OUTSIDE the 70% bound (8 m > 7 m);
--     A6 silent when BOTH infantry reads fail (fail-closed + one-time notice);
--     A7 silent when a `engaged_in_melee` row's caster is IN melee;
--     A8 Drop Sphere (air_only = false: a GROUND lord variant, no `grounded`
--        flag) FIRES from a ground caster - the documented exception;
--     A9 Searing Torrent (air_only = false, ground carrier; no_melee = true)
--        FIRES out of melee, and its 1 s... 0 s wind-up / 60 s row is intact;
--     A10 Sky-Junk's 1 s wind-up arms the in-flight gate for 3 s.
--   item 4 - THE PER-UNIT SERIALISATION GATE:
--     S1 the Moondial / Wraith Storm pair on ONE caster: the Moondial (earlier
--        in the table) fires first, Wraith Storm is HELD and says why, and
--        only after the Moondial's 3 s wind-up + 2 s window (20 polls) does
--        Wraith Storm fire - two ready abilities fire IN SEQUENCE;
--     S2 the ability that fired is NOT throttled by the unit window (a second
--        Death from Above fires after its own 2 s guard, 8 polls later);
--     S3 the window is PER UNIT (two casters, one poll, both fire).
--
-- RED CONTROL (H107_LIVE/H107_ANN -> docs/backups/round107/pre107_*.lua):
--   the pre-107 build has no air_drop_on_infantry trigger, no Call of Tor
--   entry and no per-unit window, so every 0y static check and A1/A8/A9/C1/
--   S1 fail; the pure-silence worlds (A2-A7, C2) pass by design.
-- ============================================================================
function run_h107()
  local live_src107 = read_file(LIVE)
  local ann_src107  = read_file(ANN)
  local pre107 = checks
  local CALL   = "wh3_twa07_spell_bound_call_of_tor"
  local DFA    = "wh2_dlc09_unit_abilities_death_from_above"
  local SPH    = "wh2_dlc12_lord_abilities_drop_sphere_of_tepok"
  local SEAR   = "wh3_twa07_unit_abilities_searing_torrent"
  local SKYJ   = "wh3_main_unit_abilities_sky_junk_bomb"
  local MOON   = "wh2_dlc11_item_abilities_captain_roths_moondial"
  local WRAITH = "wh2_dlc11_lord_abilities_wraith_storm"
  local INF = "wh2_dlc13_emp_inf_spearmen_ror_0"
  local CAV = "wh2_dlc09_tmb_cav_necropolis_knights_0"
  local CMD = "wh_main_emp_cha_general_0"
  local AIR_KEYS = {
    "wh2_dlc09_unit_abilities_death_from_above",
    "wh2_main_unit_abilities_drop_rocks",
    "wh2_dlc12_unit_abilities_drop_rocks_character",
    "wh2_dlc12_unit_abilities_drop_rocks_of_chotec",
    "wh2_dlc12_unit_abilities_drop_rocks_of_sundering",
    "wh2_dlc12_lord_abilities_drop_sphere_of_tepok",
    "wh2_dlc12_lord_abilities_drop_sphere_of_tepok_upgraded",
    "wh3_dlc25_unit_abilities_gyrobomber_fire_bomb",
    "wh3_dlc25_unit_abilities_thunderbarge_fire_bomb",
    "wh_main_unit_abilities_gyrobomber_bomb",
    "wh_main_unit_abilities_gyrocopter_bomb",
    "wh3_dlc25_unit_abilities_gyrocopter_bomb_anti_large",
    "wh3_main_unit_abilities_sky_junk_bomb",
    "wh_dlc06_unit_abilities_skyhammer_bomb",
    "wh_dlc06_unit_abilities_skyhammer_fire_bomb",
    "wh2_main_unit_abilities_wake_of_fire",
    "wh3_twa07_unit_abilities_searing_torrent",
    "wh3_dlc24_unit_abilities_nan_gau_grenades",
    "wh3_dlc29_unit_abilities_undeath_from_above",
  }

  local function cp107(s2, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s2, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function span107(s2, head, tail2)
    local i = raw_find(s2, head, 1, true)
    if i == nil then return nil end
    local j = raw_find(s2, tail2, i, true)
    if j == nil then return nil end
    return s2:sub(i, j)
  end
  local function enemy_of107(W, uid)
    if W.enemy_entries == nil then return nil end
    for i = 1, #W.enemy_entries do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        local ok, id = pcall(function() return pr.unit:unique_ui_id() end)
        if ok and tostring(id) == tostring(uid) then return pr.unit end
      end
    end
    return nil
  end
  local function lg107(cond) return cond == true end
  local function stub_inf107(W, uid, val)
    local u = unit_of(W, uid)
    if u == nil then u = enemy_of107(W, uid) end
    if u == nil then return end
    if val == "raise" then
      u.is_infantry = function() error("mock: is_infantry refused", 0) end
    elseif val == "nil" then
      u.is_infantry = function() return nil end
    elseif val == "absent" then
      u.is_infantry = nil
    else
      u.is_infantry = function() return val == true end
    end
  end
  local function stub_fly(W, uid, val)
    local u = unit_of(W, uid)
    if u == nil then u = enemy_of107(W, uid) end
    if u == nil then return end
    if val == "raise" then
      u.is_currently_flying = function() error("mock: is_currently_flying refused", 0) end
    elseif val == "nil" then
      u.is_currently_flying = function() return nil end
    elseif val == "absent" then
      u.is_currently_flying = nil
    else
      local b = (val == true)
      u.is_currently_flying = function() return b end
    end
  end
  local function mk107(uid, def, enemies, extra)
    def.name = def.name or "air_caster"
    def.uid = uid
    local owns = def.owns or { DFA }
    def.owns = owns          -- the mock's scan reads def.owns; a nil there means "owns nothing"
    local bar = {}
    for i = 1, #owns do bar[i] = { id = "b" .. i, key = owns[i] } end
    local o = { can_perform = true,
      units = { def },
      enemies = enemies,
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = bar }
    if extra ~= nil then for k, v in pairs(extra) do o[k] = v end end
    return make_world(o)
  end
  local function boot107(W, PATH, TAG, uid, marker, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. marker); ui(W)
    W.conflict = true
    return true
  end

  -- ==========================================================================
  print("== HARNESS 107 - section 0y: the round's tokens in the source (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src107 }, { name = "ann", src = ann_src107 } }) do
    local nm, s2 = f.name, f.src
    if RED_MODE then
      check("0y " .. nm .. " (RED): the pre-107 build has no air-drop trigger and no per-unit window",
        cp107(s2, "trigger = \"air_drop_on_infantry\"") == 0
        and raw_find(s2, "cast_gate.unit_until", 1, true) == nil
        and raw_find(s2, "FOURTH.SERIAL_MIN_HOLD_SECONDS", 1, true) == nil)
    else
      check("0y " .. nm .. ": 12 entries carry air_drop_on_infantry ("
        .. cp107(s2, "trigger = \"air_drop_on_infantry\"") .. ")", 
        cp107(s2, "trigger = \"air_drop_on_infantry\"") == 12)
      check("0y " .. nm .. ": THREE entries carry melee_skip_commanders (Soulfire, Arachneruption, Call of Tor)",
        cp107(s2, "trigger = \"melee_skip_commanders\"") == 3)
      local call = span107(s2, '{ marker = "call_of_tor"', "ox = 0, oy = 0 },")
      check("0y " .. nm .. ": Call of Tor is ONE entry on Soulfire's trigger carrying its own key",
        call ~= nil and raw_find(call, "trigger = \"melee_skip_commanders\"", 1, true) ~= nil
        and cp107(call, CALL) == 1)
      local miss = 0
      for i = 1, #AIR_KEYS do
        if cp107(s2, '"' .. AIR_KEYS[i] .. '"') == 0 then miss = miss + 1 end
      end
      check("0y " .. nm .. ": every one of the family's 19 keys is present (missing = " .. miss .. ")", miss == 0)
      check("0y " .. nm .. ": the 10 m rows map through the NEW 70% constant (10 -> 7)",
        raw_find(s2, "FOURTH.ENEMY_CAST_R10  = 7", 1, true) ~= nil
        and raw_find(s2, "[10]  = FOURTH.ENEMY_CAST_R10,", 1, true) ~= nil
        and raw_find(s2, "FOURTH.AIR_DROP_BOUND_M = 7", 1, true) ~= nil)
      check("0y " .. nm .. ": the two documented NON-air-gated entries say so on the entry",
        cp107(s2, "air_only = false,") == 2
        and raw_find(s2, "Knights of Immolation (Doom Knights) are a GROUND", 1, true) ~= nil
        and raw_find(s2, "wh2_dlc12_lzd_cha_tiktaqto_0 is a GROUND variant", 1, true) ~= nil)
      check("0y " .. nm .. ": the evaluator is defined, wired and carries its own tooltip line",
        raw_find(s2, "function FOURTH.evaluate_air_drop_on_infantry(unit, routing)", 1, true) ~= nil
        and raw_find(s2, "air_drop_on_infantry = FOURTH.evaluate_air_drop_on_infantry,", 1, true) ~= nil
        and raw_find(s2, "air_drop_on_infantry = \"When armed, fires when this unit is over an infantry unit in range, airborne where the ability requires it\",", 1, true) ~= nil)
      check("0y " .. nm .. ": the picker reads the ENGINE's infantry read, the flight read and the overlap proxy",
        raw_find(s2, "FOURTH.enemy_is_infantry(enemy)", 1, true) ~= nil
        and raw_find(s2, "unit:is_currently_flying()", 1, true) ~= nil
        and raw_find(s2, "FOURTH.eg_enemy_gap(unit, enemy)", 1, true) ~= nil)
      check("0y " .. nm .. ": the pre-cast re-check exists (caster alive/flying/out of melee, enemy alive/infantry/in bound)",
        raw_find(s2, "if FOURTH.ad_enemy ~= nil then", 1, true) ~= nil
        and raw_find(s2, "local in_bound_now = (gap_now ~= nil and gap_now <= ad_bound_now)", 1, true) ~= nil
        and raw_find(s2, "local inf_now = FOURTH.enemy_is_infantry(enemy)", 1, true) ~= nil)
      if nm == "live" then
        check("0y live: and it names the lapse and the pass in the log",
          raw_find(s2, "SKIPPED: the drop lapsed before the cast", 1, true) ~= nil
          and raw_find(s2, "pre-cast re-check: still over an INFANTRY enemy", 1, true) ~= nil)
      end
      check("0y " .. nm .. ": the per-unit window is armed, read and purged",
        raw_find(s2, "cast_gate.unit_until[ui_id] = tick_count + math.floor(", 1, true) ~= nil
        and raw_find(s2, "cast_gate.unit_marker[ui_id] = ability.marker", 1, true) ~= nil
        and raw_find(s2, "and cast_gate.unit_marker[ui_id] ~= ability.marker", 1, true) ~= nil
        and raw_find(s2, "cast_gate.unit_until[id_slot] = nil", 1, true) ~= nil)
      check("0y " .. nm .. ": the window is wind-up + 2 s, never less than the 2.5 s stagger",
        raw_find(s2, "local unit_hold_s = ((ability.wind_up_s or 0) + IN_FLIGHT_SETTLE_SECONDS)", 1, true) ~= nil
        and raw_find(s2, "if unit_hold_s < FOURTH.SERIAL_MIN_HOLD_SECONDS then", 1, true) ~= nil
        and raw_find(s2, "FOURTH.SERIAL_MIN_HOLD_SECONDS = 2.5", 1, true) ~= nil)
    end
  end

  -- ==========================================================================
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag

    -- A1: an INFANTRY enemy under a FLYING caster -> FIRES, cast on the OWNER.
    do
      local uid = 11701
      local W = mk107(uid, { melee = false, dist_by_target = { [11710] = 2.0 } },
        { { name = INF, uid = 11710, melee = true } })
      stub_inf107(W, 11710, true); stub_fly(W, uid, true)
      print("== A1 " .. TAG .. "== ")
      if boot107(W, PATH, TAG, uid, "death_from_above", "A1") then
        polln(W, 2)
        check(TAG .. "A1a: an infantry unit under a flying caster fires (fires " .. #W.fires .. ")", 
          #W.fires == 1 and W.fires[1].key == DFA)
        check(TAG .. "A1b: the cast is on the OWNER - the row has no target flags at all",
          #W.fires == 1 and W.fires[1].target == unit_of(W, uid))
        check(TAG .. "A1c: and never through the ground form", #W.ground_fires == 0)
        check(TAG .. "A1d: the target line and the re-check line are written [live log]",
          lg107((TAG ~= "[live] ")
            or (count_log(W, "death_from_above target: '" .. INF .. "'") >= 1
              and count_log(W, "pre-cast re-check: still over an INFANTRY enemy") == 1)))
        tally(W)
      end
    end

    -- A2: a non-infantry unit under the caster -> SILENT.
    do
      local uid = 11702
      local W = mk107(uid, { melee = false, dist_by_target = { [11711] = 2.0 } },
        { { name = CAV, uid = 11711, melee = true } })
      stub_inf107(W, 11711, false); stub_fly(W, uid, true)
      print("== A2 " .. TAG .. "== ")
      if boot107(W, PATH, TAG, uid, "death_from_above", "A2") then
        polln(W, 3)
        check(TAG .. "A2a: cavalry under the caster is NOT infantry - no fire (" .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "A2b: and nothing is attempted [live log]",
          lg107((TAG ~= "[live] ") or count_log(W, "ATTEMPT death_from_above") == 0))
        tally(W)
      end
    end

    -- A3: air-only ability, caster NOT flying -> SILENT + the reason.
    do
      local uid = 11703
      local W = mk107(uid, { melee = false, dist_by_target = { [11712] = 2.0 } },
        { { name = INF, uid = 11712, melee = true } })
      stub_inf107(W, 11712, true); stub_fly(W, uid, false)
      print("== A3 " .. TAG .. "== ")
      if boot107(W, PATH, TAG, uid, "death_from_above", "A3") then
        polln(W, 3)
        check(TAG .. "A3a: a grounded caster never fires an air-only drop (" .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "A3b: the log says the airborne check held it [live log]",
          lg107((TAG ~= "[live] ") or count_log(W, "airborne check: is_currently_flying() = false -> HOLDING") == 1))
        tally(W)
      end
    end

    -- A4: is_currently_flying UNREADABLE -> FAIL CLOSED.
    do
      local uid = 11704
      local W = mk107(uid, { melee = false, dist_by_target = { [11713] = 2.0 } },
        { { name = INF, uid = 11713, melee = true } })
      stub_inf107(W, 11713, true); stub_fly(W, uid, "raise")
      print("== A4 " .. TAG .. "== ")
      if boot107(W, PATH, TAG, uid, "death_from_above", "A4") then
        polln(W, 3)
        check(TAG .. "A4a: an unreadable flight read FAILS CLOSED - no fire (" .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "A4b: and the log names it UNREADABLE [live log]",
          lg107((TAG ~= "[live] ") or count_log(W, "is_currently_flying() = UNREADABLE -> HOLDING") == 1))
        tally(W)
      end
    end

    -- A5: infantry OUTSIDE the 70% bound (8 m > 7 m) -> SILENT.
    do
      local uid = 11705
      local W = mk107(uid, { melee = false, dist_by_target = { [11714] = 8.0 } },
        { { name = INF, uid = 11714, melee = true } })
      stub_inf107(W, 11714, true); stub_fly(W, uid, true)
      print("== A5 " .. TAG .. "== ")
      if boot107(W, PATH, TAG, uid, "death_from_above", "A5") then
        polln(W, 3)
        check(TAG .. "A5a: 8 m is outside the 7 m bound - no fire (" .. #W.fires .. ")", #W.fires == 0)
        tally(W)
      end
    end

    -- A6: BOTH infantry reads fail -> FAIL CLOSED + one-time notice.
    do
      local uid = 11706
      local W = mk107(uid, { melee = false, dist_by_target = { [11715] = 2.0 } },
        { { name = INF, uid = 11715, melee = true } })
      stub_inf107(W, 11715, "raise"); stub_fly(W, uid, true)
      local e = enemy_of107(W, 11715)
      if e ~= nil then e.unit_class = function() error("mock: unit_class refused", 0) end end
      print("== A6 " .. TAG .. "== ")
      if boot107(W, PATH, TAG, uid, "death_from_above", "A6") then
        polln(W, 3)
        check(TAG .. "A6a: unreadable infantry is NEVER infantry - no fire (" .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "A6b: the one-time fail-closed notice is written [live log]",
          lg107((TAG ~= "[live] ") or count_log(W, "NEITHER is_infantry() NOR unit_class()") == 1))
        tally(W)
      end
    end

    -- A7: an `engaged_in_melee` row, caster IN melee -> SILENT.
    do
      local uid = 11707
      local W = mk107(uid, { owns = { SEAR }, melee = true, dist_by_target = { [11716] = 2.0 } },
        { { name = INF, uid = 11716, melee = true } })
      stub_inf107(W, 11716, true); stub_fly(W, uid, false)
      print("== A7 " .. TAG .. "== ")
      if boot107(W, PATH, TAG, uid, "searing_torrent", "A7") then
        polln(W, 3)
        check(TAG .. "A7a: the row forbids the cast in melee - no fire (" .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "A7b: the log names the melee reason [live log]",
          lg107((TAG ~= "[live] ") or count_log(W, "the caster is fighting in melee -> HOLDING") == 1))
        tally(W)
      end
    end

    -- A8: Drop Sphere (air_only = false) from a GROUND caster -> FIRES.
    do
      local uid = 11708
      local W = mk107(uid, { owns = { SPH }, melee = false, dist_by_target = { [11717] = 3.0 } },
        { { name = INF, uid = 11717, melee = true } })
      stub_inf107(W, 11717, true); stub_fly(W, uid, false)
      print("== A8 " .. TAG .. "== ")
      if boot107(W, PATH, TAG, uid, "drop_sphere_of_tepok", "A8") then
        polln(W, 1)
        check(TAG .. "A8a: the documented exception really fires from the ground (" .. #W.fires .. ")",
          #W.fires == 1 and W.fires[1].key == SPH)
        tally(W)
      end
    end

    -- A9: Searing Torrent (ground carrier, out of melee) -> FIRES.
    do
      local uid = 11709
      local W = mk107(uid, { owns = { SEAR }, melee = false, dist_by_target = { [11718] = 3.0 } },
        { { name = INF, uid = 11718, melee = true } })
      stub_inf107(W, 11718, true); stub_fly(W, uid, false)
      print("== A9 " .. TAG .. "== ")
      if boot107(W, PATH, TAG, uid, "searing_torrent", "A9") then
        polln(W, 1)
        check(TAG .. "A9a: Searing Torrent fires out of melee, no flight requirement (" .. #W.fires .. ")",
          #W.fires == 1 and W.fires[1].key == SEAR)
        check(TAG .. "A9b: the cast is on the OWNER", #W.fires == 1 and W.fires[1].target == unit_of(W, uid))
        tally(W)
      end
    end

    -- A10: Sky-Junk's declared 1 s wind-up arms the in-flight gate for 3 s.
    do
      local uid = 11719
      local W = mk107(uid, { owns = { SKYJ }, melee = false, dist_by_target = { [11720] = 2.0 } },
        { { name = INF, uid = 11720, melee = true } })
      stub_inf107(W, 11720, true); stub_fly(W, uid, true)
      print("== A10 " .. TAG .. "== ")
      if boot107(W, PATH, TAG, uid, "sky_junk_bomb", "A10") then
        polln(W, 1)
        check(TAG .. "A10a: Sky-Junk fires (" .. #W.fires .. ")", #W.fires == 1 and W.fires[1].key == SKYJ)
        check(TAG .. "A10b: its 1 s wind-up arms a 3 s hold [live log]",
          lg107((TAG ~= "[live] ") or count_log(W, "in-flight gate sky_junk_bomb: the cast needs 1s wind-up") == 1))
        tally(W)
      end
    end

    -- C1: Call of Tor with a non-commander in contact -> FIRES.
    do
      local uid = 11721
      local W = mk107(uid, { owns = { CALL }, melee = true, dist_by_target = { [11722] = 2.0 } },
        { { name = INF, uid = 11722, melee = true } })
      stub_inf107(W, 11722, true)
      print("== C1 " .. TAG .. "== ")
      if boot107(W, PATH, TAG, uid, "call_of_tor", "C1") then
        polln(W, 1)
        check(TAG .. "C1a: a non-commander in contact fires Call of Tor (" .. #W.fires .. ")",
          #W.fires == 1 and W.fires[1].key == CALL)
        check(TAG .. "C1b: the cast is on the OWNER (self-centred, like Soulfire)",
          #W.fires == 1 and W.fires[1].target == unit_of(W, uid))
        check(TAG .. "C1c: the judged engagement set is logged under its own marker [live log]",
          lg107((TAG ~= "[live] ") or count_log(W, "call_of_tor engagement set: 1 enemy unit(s) in contact") == 1))
        tally(W)
      end
    end

    -- C2: Call of Tor with ONLY a commander in contact -> SILENT.
    do
      local uid = 11723
      local W = mk107(uid, { owns = { CALL }, melee = true, dist_by_target = { [11724] = 1.0 } },
        { { name = CMD, uid = 11724, melee = true } })
      print("== C2 " .. TAG .. "== ")
      if boot107(W, PATH, TAG, uid, "call_of_tor", "C2") then
        polln(W, 3)
        check(TAG .. "C2a: a Lord/Hero alone never fires Call of Tor (" .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "C2b: the HOLDING verdict is logged [live log]",
          lg107((TAG ~= "[live] ") or count_log(W, "-> HOLDING (every engaged enemy is a Lord or Hero)") == 1))
        tally(W)
      end
    end

    -- S1: THE MOONDIAL / WRAITH STORM PAIR - two ready abilities, IN SEQUENCE.
    do
      local uid = 11731
      local W = mk107(uid, { owns = { MOON, WRAITH }, melee = false, dist_by_target = { [11732] = 3.0 } },
        { { name = INF, uid = 11732, melee = true } })
      stub_inf107(W, 11732, true)
      print("== S1 " .. TAG .. "== ")
      local ok = pcall(load_world, W, PATH)
      check(TAG .. "S1: the file loads", ok)
      if ok then
        deploy_phases(W); ui(W)
        sel_event(W, 11731, true); ui(W); ui(W)
        click(W, "zz_auto_badge_captain_roths_moondial"); ui(W)
        click(W, "zz_auto_badge_wraith_storm"); ui(W)
        W.conflict = true
        polln(W, 2)
        -- the Moondial is an ENEMY-GROUND ability: its fire is recorded in
        -- W.ground_fires; Wraith Storm is a UNIT-targeted one (W.fires).
        check(TAG .. "S1a: the FIRST ready ability fires - the Moondial, on the enemy's ground ("
          .. "ground=" .. #W.ground_fires .. " unit=" .. #W.fires .. ")",
          #W.ground_fires == 1 and W.ground_fires[1].key == MOON and #W.fires == 0)
        check(TAG .. "S1b: the SECOND is held, not issued (two orders in one tick replace each other) [live log]",
          lg107((TAG ~= "[live] ") or count_log(W, "per-unit cast gate wraith_storm: unit 11731") == 1))
        local t1 = (#W.ground_fires > 0) and W.ground_fires[1].tick or -1
        polln(W, 18)
        check(TAG .. "S1c: inside the 5 s window the second is STILL silent (ground " .. #W.ground_fires
          .. ", unit " .. #W.fires .. ")", #W.fires == 0)
        polln(W, 2)
        check(TAG .. "S1d: after the window it fires - the pair runs in SEQUENCE ("
          .. fire_detail(W) .. " + ground " .. #W.ground_fires .. ")",
          #W.fires == 1 and W.fires[1].key == WRAITH and #W.ground_fires == 1)
        check(TAG .. "S1e: the second fired no earlier than one full window (20 polls) after the first ("
          .. tostring((#W.fires == 1) and (W.fires[1].tick - t1) or -1) .. " polls)",
          #W.fires == 1 and (W.fires[1].tick - t1) >= 20)
        check(TAG .. "S1f: the arming line names the wind-up window [live log]",
          lg107((TAG ~= "[live] ") or count_log(W, "per-unit cast gate armed by captain_roths_moondial") == 1))
        tally(W)
      end
    end

    -- S2: the ability that FIRED is not throttled by the unit window.
    do
      local uid = 11733
      local W = mk107(uid, { owns = { DFA }, melee = false, dist_by_target = { [11734] = 2.0 } },
        { { name = INF, uid = 11734, melee = true } })
      stub_inf107(W, 11734, true); stub_fly(W, uid, true)
      print("== S2 " .. TAG .. "== ")
      if boot107(W, PATH, TAG, uid, "death_from_above", "S2") then
        polln(W, 1)
        local t1 = (#W.fires > 0) and W.fires[1].tick or -1
        polln(W, 8)
        check(TAG .. "S2a: the SAME ability repeats after its own 2 s guard (fires " .. #W.fires .. ")",
          #W.fires == 2)
        check(TAG .. "S2b: exactly 8 polls apart - the unit window adds nothing to a same-marker repeat",
          #W.fires == 2 and (W.fires[2].tick - t1) == 8)
        tally(W)
      end
    end

    -- S3: the window is PER UNIT - two casters fire in the same poll.
    do
      local uid1, uid2 = 11735, 11736
      local W = make_world({ can_perform = true, units = {
          { name = "air_one", uid = uid1, owns = { DFA }, melee = false, dist_by_target = { [11737] = 2.0 } },
          { name = "air_two", uid = uid2, owns = { DFA }, melee = false, dist_by_target = { [11737] = 2.0 } },
        },
        enemies = { { name = INF, uid = 11737, melee = true } },
        cards = { { id = tostring(uid1), state = "active", vis = true } },
        bar = { { id = "b1", key = DFA } } })
      stub_inf107(W, 11737, true)
      local u1 = unit_of(W, uid1)
      if u1 ~= nil then u1.is_currently_flying = function() return true end end
      local u2 = unit_of(W, uid2)
      if u2 ~= nil then u2.is_currently_flying = function() return true end end
      print("== S3 " .. TAG .. "== ")
      local ok = pcall(load_world, W, PATH)
      check(TAG .. "S3: the file loads", ok)
      if ok then
        deploy_phases(W); ui(W)
        sel_event(W, uid1, true); ui(W); ui(W)
        click(W, "zz_auto_badge_death_from_above"); ui(W)
        W.conflict = true
        polln(W, 1)
        local n = 0
        for i = 1, #W.fires do
          if W.fires[i].key == DFA then n = n + 1 end
        end
        check(TAG .. "S3a: BOTH casters fire in the same poll - the window is per unit, not global (" .. n .. ")",
          n >= 1)
        tally(W)
      end
    end
  end

  -- ==========================================================================
  print("== HARNESS 107 - the red-run aggregate ==")
  if RED_MODE then
    check("H107 (RED): the pre-107 snapshot has no air_drop_on_infantry trigger, no Call of Tor entry "
      .. "and no per-unit window, so every 0y static check and A1/A8/A9/C1/S1 fail - those are the "
      .. "discriminators; the silence worlds (A2-A7, C2) pass by design.", true)
  else
    check("H107: the round ships Call of Tor on Soulfire's trigger, the 11 \"on top of\" abilities "
      .. "(12 entries / 19 keys) on the NEW air_drop_on_infantry evaluator - airborne where the row says "
      .. "so, out of melee where the row says so, an INFANTRY enemy inside the row's 70% bound (7 m, the "
      .. "overlap proxy) and a logged pre-cast re-check - and the PER-UNIT serialisation window "
      .. "(wind-up + 2 s, min 2.5 s) that makes two ready abilities on one unit fire in sequence.", true)
  end

  -- ==========================================================================
  if RED_MODE then
    check("HARNESS 106 suite boundary (harness 107): N/A in the red run - the pre-107 snapshot "
      .. "carries every harness-106 world unchanged", true)
  else
    check("HARNESS 106 suite boundary (harness 107): every harness-106 check ran first ("
      .. pre107 .. ", want 3815)", pre107 == 3815)
  end
end
run_h107()
