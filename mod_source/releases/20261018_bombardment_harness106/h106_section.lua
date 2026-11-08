-- ============================================================================
-- HARNESS 106 - THE BOMBARDMENT ROUND (two approved families)
--
-- FAMILY 1 - melee_skip_commanders (Soulfire x2 keys, Arachneruption):
--   fire when the CASTER is in melee, but SKIP when every enemy it is fighting
--   is a Lord or a Hero. The engagement set comes from the enemy enumerator:
--   alive + is_in_melee() + edge-to-edge unit_distance <= 12 m, each member
--   classified by the 1,409-key commander set (unit_class fallback, fail
--   closed). The judged set is logged (type + flag + real distance), deduped
--   by note text. No enemy readable -> current_target() fallback -> plain
--   in-melee rule.
--
-- FAMILY 2 - enemy_ground_melee_infantry (the 30 of the approved 32):
--   the CLOSEST enemy inside the ability's own 70% bound that is IN MELEE and
--   IS INFANTRY (battle_unit:is_infantry(), unit_class exact-match fallback,
--   fail closed). Ground-targeted keys place the strike on the enemy's own
--   ground; unit-targeted keys cast on the enemy unit.
--
-- WORLDS (every world runs against the live source AND the annotated copy):
--   S1 non-commander in contact      -> fires, judged set logged with its type
--   S2 ONLY a commander in contact   -> SILENT, "every engaged enemy is a Lord or Hero"
--   S3 caster NOT in melee           -> SILENT (not even attempted)
--   S4 commander + infantry          -> fires (a non-commander IS engaged)
--   S5 nothing in contact, current_target is a commander -> SILENT
--   S6 nothing in contact, no current target            -> fires (plain melee)
--   F1 closer CAVALRY vs farther INFANTRY -> the INFANTRY is chosen
--   F2 the only in-melee enemy is a commander -> SILENT
--   F3 the only infantry is beyond the 70% bound -> SILENT
--   F4 infantry UNREADABLE (both reads fail) -> SILENT (fail-closed)
--   F5 a UNIT-targeted key -> perform_special_ability(key, enemy)
--   F6 a GROUND-targeted key -> perform_special_ability_ground on the enemy's
--      own position vector
--   F7 is_infantry() unreadable but unit_class == "inf_mel" -> fires (the
--      fallback is real, not a hard-coded "no")
--
-- RED CONTROL (H106_LIVE/H106_ANN -> docs/backups/round106/pre106_*.lua): the
--   pre-106 build has neither trigger, no entry and no helpers, so every
--   static block fails and S1/S4/S5/S6/F1/F5/F6/F7 never fire - those are the
--   discriminators; the pure-silence worlds pass by design.
-- ============================================================================
function run_h106()
  local live_src106 = read_file(LIVE)
  local ann_src106  = read_file(ANN)
  local pre106 = checks
  local SOUL = { "wh_main_spell_bound_soulfire", "wh_dlc04_spell_bound_soulfire_upgraded" }
  local ARACH = "wh2_dlc15_unit_abilities_arachneruption"
  local ASSAULT = "wh2_dlc10_item_bound_assault_of_stone"
  local DOOMBOLT = "wh2_dlc10_spell_bound_lesser_doombolt"
  local INF = "wh2_dlc13_emp_inf_spearmen_ror_0"
  local CAV = "wh2_dlc09_tmb_cav_necropolis_knights_0"
  local CMD = "wh_main_emp_cha_general_0"

  local function cp106(s2, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s2, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function span106(s2, head, tail2)
    local i = raw_find(s2, head, 1, true)
    if i == nil then return nil end
    local j = raw_find(s2, tail2, i, true)
    if j == nil then return nil end
    return s2:sub(i, j)
  end
  local function enemy_of106(W, uid)
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
  local function lg106(cond) return cond == true end
  local function boot106(W, PATH, TAG, uid, marker, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. marker); ui(W)
    W.conflict = true
    return true
  end
  -- the engine's infantry read, stubbed per unit: true / false / "nil" / "raise"
  local function stub_inf(W, uid, val)
    local u = unit_of(W, uid)
    if u == nil then u = enemy_of106(W, uid) end
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

  -- ==========================================================================
  print("== HARNESS 106 - section 0x: the two families in the source (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src106 }, { name = "ann", src = ann_src106 } }) do
    local nm, s2 = f.name, f.src
    if RED_MODE then
      check("0x " .. nm .. " (RED): the pre-106 build has no bombardment entries",
        cp106(s2, "trigger = \"enemy_ground_melee_infantry\"") == 0
        and cp106(s2, "trigger = \"melee_skip_commanders\"") == 0)
      check("0x " .. nm .. " (RED): and no infantry reader and no engagement set",
        raw_find(s2, "function FOURTH.enemy_is_infantry", 1, true) == nil
        and raw_find(s2, "function FOURTH.engagement_set", 1, true) == nil)
    else
      check("0x " .. nm .. ": the 30 bombardment entries carry the new trigger ("
        .. cp106(s2, "trigger = \"enemy_ground_melee_infantry\"") .. ")",
        cp106(s2, "trigger = \"enemy_ground_melee_infantry\"") == 30)
      check("0x " .. nm .. ": TWO entries carry melee_skip_commanders (Soulfire + Arachneruption)",
        cp106(s2, "trigger = \"melee_skip_commanders\"") == 2)
      local soul = span106(s2, '{ marker = "soulfire"', "ox = 0, oy = 0 },")
      check("0x " .. nm .. ": Soulfire is ONE entry carrying BOTH soulfire keys",
        soul ~= nil and cp106(soul, "wh_main_spell_bound_soulfire") == 1
        and raw_find(soul, "wh_dlc04_spell_bound_soulfire_upgraded", 1, true) ~= nil)
      local ara = span106(s2, '{ marker = "arachneruption"', "ox = 0, oy = 0 },")
      check("0x " .. nm .. ": Arachneruption is one entry on the same trigger",
        ara ~= nil and raw_find(ara, ARACH, 1, true) ~= nil)
      check("0x " .. nm .. ": the 300 m range maps to the 210 m bound (the 70% rule)",
        raw_find(s2, "FOURTH.ENEMY_CAST_R300 = 210", 1, true) ~= nil
        and raw_find(s2, "[300] = FOURTH.ENEMY_CAST_R300,", 1, true) ~= nil)
      check("0x " .. nm .. ": both triggers are wired in FOURTH.evaluators",
        raw_find(s2, "melee_skip_commanders = FOURTH.evaluate_melee_skip_commanders,", 1, true) ~= nil
        and raw_find(s2, "enemy_ground_melee_infantry = FOURTH.evaluate_enemy_ground_melee_infantry,", 1, true) ~= nil)
      check("0x " .. nm .. ": and both carry their own tooltip sentence",
        raw_find(s2, 'melee_skip_commanders = "When armed, fires when this unit is in melee, unless every enemy it is fighting is a Lord or Hero",', 1, true) ~= nil
        and raw_find(s2, 'enemy_ground_melee_infantry = "When armed, fires on the closest infantry unit in range that is fighting in melee",', 1, true) ~= nil)
      local inf = span106(s2, "function FOURTH.enemy_is_infantry(enemy)", "\nend")
      check("0x " .. nm .. ": the infantry read prefers the ENGINE (is_infantry) and falls back to the class set",
        inf ~= nil and raw_find(inf, "enemy:is_infantry()", 1, true) ~= nil
        and raw_find(inf, 'cls == "inf_mel"', 1, true) ~= nil
        and raw_find(inf, 'cls == "inf_mis"', 1, true) ~= nil
        and raw_find(inf, 'cls == "inf_spr"', 1, true) ~= nil)
      local pick = span106(s2, "function FOURTH.enc_pick_enemy(unit, routing, ground, mode)", "\nend")
      check("0x " .. nm .. ": the picker has the infantry mode and re-checks it before the cast",
        pick ~= nil and raw_find(pick, 'elseif mode == "infantry" then', 1, true) ~= nil
        and raw_find(pick, "FOURTH.enemy_is_infantry(enemy)", 1, true) ~= nil
        and raw_find(s2, "if FOURTH.eg_infantry then", 1, true) ~= nil)
      check("0x " .. nm .. ": the engagement contact constant and the dedupe table exist",
        raw_find(s2, "FOURTH.ENGAGE_CONTACT_M = 12", 1, true) ~= nil
        and raw_find(s2, "FOURTH.engage_note = {}", 1, true) ~= nil)
      check("0x " .. nm .. ": all 24 ground-targeted bombardment keys are in enemy_ground_keys",
        cp106(s2, '["wh2_dlc10_item_bound_assault_of_stone"] = true,') == 1
        and cp106(s2, '["wh3_main_mount_bound_celestial_lightning"] = true,') == 1
        and cp106(s2, '["wh3_main_weapon_abilities_the_traitors_sword"] = true,') == 0)
      check("0x " .. nm .. ": every one of the 30 entries declares its real range",
        cp106(s2, "trigger = \"enemy_ground_melee_infantry\"") == 30
        and cp106(s2, "range_real = 200,") >= 15)
    end
  end

  -- ==========================================================================
  -- FAMILY 1 WORLDS
  local function soul_world(uid, def, enemies, extra)
    def.name = def.name or "bombardment_caster"
    def.uid = uid
    def.owns = def.owns or { SOUL[1] }
    local o = { can_perform = true,
      units = { def },
      enemies = enemies,
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = (def.owns or { SOUL[1] })[1] } } }
    if extra ~= nil then for k, v in pairs(extra) do o[k] = v end end
    return make_world(o)
  end

  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag

    -- S1: a non-commander in contact -> FIRES and names the set.
    do
      local uid = 11601
      local W = soul_world(uid, { melee = true, dist_by_target = { [11610] = 2.0 } },
        { { name = INF, uid = 11610, melee = true } })
      stub_inf(W, 11610, true)
      print("== S1 " .. TAG .. "== ")
      if boot106(W, PATH, TAG, uid, "soulfire", "S1") then
        polln(W, 1)
        check(TAG .. "S1a: a caster in melee with a non-commander in contact fires (" .. #W.fires .. ")",
          #W.fires == 1 and W.fires[1].key == SOUL[1])
        check(TAG .. "S1b: the cast is on the OWNER (a self-centred ability)", #W.fires == 1
          and W.fires[1].target == unit_of(W, uid))
        check(TAG .. "S1c: the judged engagement set is logged with the type and the flag [live log]",
          lg106((TAG ~= "[live] ")
            or (count_log(W, "soulfire engagement set: 1 enemy unit(s) in contact") == 1
              and count_log(W, "'" .. INF .. "' non-commander") == 1)))
        check(TAG .. "S1d: and the verdict says FIRING [live log]",
          lg106((TAG ~= "[live] ") or count_log(W, "-> FIRING (a non-commander is engaged)") == 1))
        tally(W)
      end
    end

    -- S2: ONLY a commander in contact -> SILENT.
    do
      local uid = 11602
      local W = soul_world(uid, { melee = true, dist_by_target = { [11611] = 1.2 } },
        { { name = CMD, uid = 11611, melee = true } })
      print("== S2 " .. TAG .. "== ")
      if boot106(W, PATH, TAG, uid, "soulfire", "S2") then
        polln(W, 3)
        check(TAG .. "S2a: a caster fighting ONLY a Lord/Hero never fires (" .. #W.fires .. ")",
          #W.fires == 0)
        check(TAG .. "S2b: and no ATTEMPT is written for it [live log]",
          lg106((TAG ~= "[live] ") or count_log(W, "ATTEMPT soulfire") == 0))
        check(TAG .. "S2c: the log names the commander and the HOLDING verdict [live log]",
          lg106((TAG ~= "[live] ")
            or (count_log(W, "'" .. CMD .. "' COMMANDER") == 1
              and count_log(W, "-> HOLDING (every engaged enemy is a Lord or Hero)") == 1)))
        tally(W)
      end
    end

    -- S3: the caster is NOT in melee -> SILENT.
    do
      local uid = 11603
      local W = soul_world(uid, { melee = false, dist_by_target = { [11612] = 1.0 } },
        { { name = INF, uid = 11612, melee = true } })
      stub_inf(W, 11612, true)
      print("== S3 " .. TAG .. "== ")
      if boot106(W, PATH, TAG, uid, "soulfire", "S3") then
        polln(W, 3)
        check(TAG .. "S3a: out of melee the entry never fires (" .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "S3b: and nothing is attempted [live log]",
          lg106((TAG ~= "[live] ") or count_log(W, "ATTEMPT soulfire") == 0))
        tally(W)
      end
    end

    -- S4: commander AND infantry in contact -> FIRES (a non-commander is engaged).
    do
      local uid = 11604
      local W = soul_world(uid, { melee = true, dist_by_target = { [11613] = 1.0, [11614] = 3.0 } },
        { { name = CMD, uid = 11613, melee = true }, { name = INF, uid = 11614, melee = true } })
      stub_inf(W, 11614, true)
      print("== S4 " .. TAG .. "== ")
      if boot106(W, PATH, TAG, uid, "soulfire", "S4") then
        polln(W, 1)
        check(TAG .. "S4a: one commander plus one infantry -> the ability fires (" .. #W.fires .. ")",
          #W.fires == 1)
        check(TAG .. "S4b: the logged set names BOTH units and their flags [live log]",
          lg106((TAG ~= "[live] ")
            or (count_log(W, "engagement set: 2 enemy unit(s) in contact") == 1
              and count_log(W, "'" .. CMD .. "' COMMANDER") == 1
              and count_log(W, "'" .. INF .. "' non-commander") == 1)))
        tally(W)
      end
    end

    -- S5: nothing in contact, current_target is a commander -> SILENT.
    do
      local uid = 11605
      local W = soul_world(uid, { melee = true, target = nil, dist_by_target = { [11615] = 30.0, [11616] = 30.0 } },
        { { name = CMD, uid = 11615, melee = false }, { name = INF, uid = 11616, melee = false } })
      stub_inf(W, 11616, true)
      W.mock_units[1].current_target = function() return enemy_of106(W, 11615) end
      print("== S5 " .. TAG .. "== ")
      if boot106(W, PATH, TAG, uid, "soulfire", "S5") then
        polln(W, 3)
        check(TAG .. "S5a: no enemy in contact and a commander current_target -> SILENT (" .. #W.fires .. ")",
          #W.fires == 0)
        check(TAG .. "S5b: the fallback names the current target as a commander [live log]",
          lg106((TAG ~= "[live] ")
            or count_log(W, "current_target '" .. CMD .. "' is a COMMANDER") == 1))
        tally(W)
      end
    end

    -- S6: nothing in contact and no current target -> plain in-melee (fires).
    do
      local uid = 11606
      local W = soul_world(uid, { melee = true, dist_by_target = { [11617] = 30.0 } },
        { { name = INF, uid = 11617, melee = false } })
      stub_inf(W, 11617, true)
      W.mock_units[1].current_target = function() return nil end
      print("== S6 " .. TAG .. "== ")
      if boot106(W, PATH, TAG, uid, "soulfire", "S6") then
        polln(W, 1)
        check(TAG .. "S6a: no enemy readable at all -> the plain in-melee rule still fires (" .. #W.fires .. ")",
          #W.fires == 1)
        check(TAG .. "S6b: and says the engagement set was unreadable [live log]",
          lg106((TAG ~= "[live] ") or count_log(W, "no enemy readable in contact and no current target - plain in-melee rule") == 1))
        tally(W)
      end
    end

    -- F1: a closer CAVALRY and a farther INFANTRY -> the INFANTRY is chosen.
    do
      local uid = 11607
      local W = soul_world(uid, { owns = { ASSAULT }, melee = false,
        dist_by_target = { [11618] = 5.0, [11619] = 15.0 } },
        { { name = CAV, uid = 11618, melee = true }, { name = INF, uid = 11619, melee = true } })
      stub_inf(W, 11618, false)
      stub_inf(W, 11619, true)
      print("== F1 " .. TAG .. "== ")
      if boot106(W, PATH, TAG, uid, "assault_of_stone", "F1") then
        polln(W, 1)
        check(TAG .. "F1a: the closest INFANTRY wins over a closer cavalry unit (fires "
          .. #W.fires .. ", ground " .. #W.ground_fires .. ")",
          #W.ground_fires == 1 and W.ground_fires[1].key == ASSAULT)
        check(TAG .. "F1b: the strike is placed on the INFANTRY unit's own position vector",
          #W.ground_fires == 1 and W.ground_fires[1].pos ~= nil
          and tostring(W.ground_fires[1].pos.marker) == "pos:11619")
        check(TAG .. "F1c: the target line names the infantry unit and the distance [live log]",
          lg106((TAG ~= "[live] ")
            or (count_log(W, "assault_of_stone target: '" .. INF .. "'") == 1
              and count_log(W, "closest in-melee INFANTRY enemy within bound") == 1)))
        tally(W)
      end
    end

    -- F2: the only in-melee enemy is a commander -> SILENT.
    do
      local uid = 11608
      local W = soul_world(uid, { owns = { ASSAULT }, melee = false, dist_by_target = { [11620] = 4.0 } },
        { { name = CMD, uid = 11620, melee = true } })
      stub_inf(W, 11620, false)
      print("== F2 " .. TAG .. "== ")
      if boot106(W, PATH, TAG, uid, "assault_of_stone", "F2") then
        polln(W, 3)
        check(TAG .. "F2a: a commander in melee is NOT infantry - the strike never fires ("
          .. #W.fires .. "/" .. #W.ground_fires .. ")",
          #W.fires == 0 and #W.ground_fires == 0)
        check(TAG .. "F2b: and nothing is attempted [live log]",
          lg106((TAG ~= "[live] ") or count_log(W, "ATTEMPT assault_of_stone") == 0))
        tally(W)
      end
    end

    -- F3: the only infantry is BEYOND the 70% bound (140 m of the real 200).
    do
      local uid = 11609
      local W = soul_world(uid, { owns = { ASSAULT }, melee = false, dist_by_target = { [11621] = 150.0 } },
        { { name = INF, uid = 11621, melee = true } })
      stub_inf(W, 11621, true)
      print("== F3 " .. TAG .. "== ")
      if boot106(W, PATH, TAG, uid, "assault_of_stone", "F3") then
        polln(W, 3)
        check(TAG .. "F3a: 150 m is outside the 140 m bound - no fire (" .. #W.ground_fires .. ")",
          #W.fires == 0 and #W.ground_fires == 0)
        tally(W)
      end
    end

    -- F4: infantry UNREADABLE on both reads -> FAIL CLOSED (silent).
    do
      local uid = 11630
      local W = soul_world(uid, { owns = { ASSAULT }, melee = false, dist_by_target = { [11622] = 5.0 } },
        { { name = INF, uid = 11622, melee = true } })
      stub_inf(W, 11622, "raise")
      local e = enemy_of106(W, 11622)
      if e ~= nil then e.unit_class = function() error("mock: unit_class refused", 0) end end
      print("== F4 " .. TAG .. "== ")
      if boot106(W, PATH, TAG, uid, "assault_of_stone", "F4") then
        polln(W, 3)
        check(TAG .. "F4a: an unreadable infantry answer is NEVER infantry - no fire ("
          .. #W.fires .. "/" .. #W.ground_fires .. ")", #W.fires == 0 and #W.ground_fires == 0)
        check(TAG .. "F4b: and the one-time fail-closed notice is written [live log]",
          lg106((TAG ~= "[live] ") or count_log(W, "NEITHER is_infantry() NOR unit_class()") == 1))
        tally(W)
      end
    end

    -- F5: a UNIT-targeted key -> perform_special_ability(key, enemy).
    do
      local uid = 11631
      local W = soul_world(uid, { owns = { DOOMBOLT }, melee = false, dist_by_target = { [11623] = 6.0 } },
        { { name = INF, uid = 11623, melee = true } })
      stub_inf(W, 11623, true)
      print("== F5 " .. TAG .. "== ")
      if boot106(W, PATH, TAG, uid, "lesser_doombolt", "F5") then
        polln(W, 1)
        check(TAG .. "F5a: a unit-targeted bombardment casts on the ENEMY unit (" .. #W.fires .. ")",
          #W.fires == 1 and W.fires[1].key == DOOMBOLT
          and W.fires[1].target == enemy_of106(W, 11623))
        check(TAG .. "F5b: and it never uses the ground form", #W.ground_fires == 0)
        tally(W)
      end
    end

    -- F6: a GROUND-targeted key -> the ground form on the enemy's own vector.
    do
      local uid = 11632
      local W = soul_world(uid, { owns = { ASSAULT }, melee = false, dist_by_target = { [11624] = 8.0 } },
        { { name = INF, uid = 11624, melee = true } })
      stub_inf(W, 11624, true)
      print("== F6 " .. TAG .. "== ")
      if boot106(W, PATH, TAG, uid, "assault_of_stone", "F6") then
        polln(W, 1)
        check(TAG .. "F6a: a ground-targeted bombardment uses the GROUND form (" .. #W.ground_fires .. ")",
          #W.ground_fires == 1 and W.ground_fires[1].key == ASSAULT)
        check(TAG .. "F6b: the position passed is the ENEMY's own vector, not the caster's",
          #W.ground_fires == 1 and tostring(W.ground_fires[1].pos.marker) == "pos:11624")
        check(TAG .. "F6c: the log names the enemy-ground form [live log]",
          lg106((TAG ~= "[live] ") or count_log(W, "enemy-ground cast") == 1))
        tally(W)
      end
    end

    -- F7: is_infantry() unreadable but unit_class == "inf_mel" -> fires.
    do
      local uid = 11633
      local W = soul_world(uid, { owns = { ASSAULT }, melee = false, dist_by_target = { [11625] = 9.0 } },
        { { name = INF, uid = 11625, melee = true } })
      stub_inf(W, 11625, "nil")
      local e = enemy_of106(W, 11625)
      if e ~= nil then e.unit_class = function() return "inf_mel" end end
      print("== F7 " .. TAG .. "== ")
      if boot106(W, PATH, TAG, uid, "assault_of_stone", "F7") then
        polln(W, 1)
        check(TAG .. "F7a: the unit_class fallback is a REAL read - an inf_mel unit fires (" .. #W.ground_fires .. ")",
          #W.ground_fires == 1)
        tally(W)
      end
    end
  end

  -- ==========================================================================
  print("== HARNESS 106 - the red-run aggregate ==")
  if RED_MODE then
    check("H106 (RED): the pre-106 snapshot has neither trigger, no infantry reader and no engagement "
      .. "set, so every 0x static check and the S1/S4/S5/S6/F1/F5/F6/F7 fire checks fail - those are "
      .. "the discriminators; the silence worlds pass by design.", true)
  else
    check("H106: the bombardment round ships TWO families - Soulfire (2 keys) + Arachneruption on "
      .. "melee_skip_commanders (in melee, unless every engaged enemy is a Lord or Hero, with the "
      .. "judged set logged) and 30 bombardment abilities on enemy_ground_melee_infantry (closest "
      .. "in-melee INFANTRY enemy inside the 70% bound, cast at its position in the form its row "
      .. "declares).", true)
  end

  -- ==========================================================================
  if RED_MODE then
    check("HARNESS 105 suite boundary (harness 106): N/A in the red run - the pre-106 snapshot "
      .. "carries every harness-105 world unchanged", true)
  else
    check("HARNESS 105 suite boundary (harness 106): every harness-105 check ran first ("
      .. pre106 .. ", want 3701)", pre106 == 3701)
  end
end
run_h106()
