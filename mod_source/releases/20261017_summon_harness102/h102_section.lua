-- ============================================================================
-- HARNESS 102 - THE SUMMON ROUND.
--
--   (A) the rest of the wh_type_summon_unit class (57 entries / 68 keys) and
--   (D) the nine unlabelled real spawners ride the PROVEN enemy_ground_melee
--       trigger: the closest FIGHTING enemy inside the ability's own 70% bound,
--       the summon placed on THAT ENEMY's ground through the ground form.
--   (B) Nurgling Tide rides the NEW self_summon_melee trigger - the caster
--       itself must be in melee - and casts on SELF through the unit form.
--   (E) Eye of Khorne rides the NEW enemy_low_health_noncommander FINISHER:
--       the lowest-health enemy below 20% health inside the 70% bound that is
--       NOT a Lord or Hero, cast through the UNIT form.
--   (F) The Dreaded Thirteenth (4 keys, ONE entry) rides the NEW
--       enemy_melee_noncommander trigger: the closest non-commander enemy in
--       melee inside the 70% bound, placed on its ground.
--   (C) the four illusions are EXCLUDED (they are engine-refused while engaged
--       in melee, so a melee trigger can never fire them) - none was ever in
--       the mod, and the check proves all four keys stay absent.
--
-- The commander (Lord/Hero) test is a REAL READ: FOURTH.commander_keys is
-- derived from the game's own class/caste columns and matched by exact
-- whole-key equality against battle_unit:type(); battle_unit:unit_class() =
-- "com" is the fallback, and both-unreadable FAILS CLOSED.
--
-- RED CONTROL: with H102_LIVE / H102_ANN pointing at the pre-102 snapshot every
-- new-entry world fires NOTHING (no entry, no marker), the silent worlds pass
-- by design, and the 0z static gates fail on the absent entries - while every
-- harness-101 world still behaves except the table-size pins, which move with
-- the table (the pre-102 snapshot is 573 / 599).
-- ============================================================================

function run_h102()
  local live_src102 = read_file(LIVE)
  local ann_src102  = read_file(ANN)
  local RED102 = { fires = 0, ground = 0 }
  local NURG = "wh3_main_lord_abilities_nurgling_tide"
  local EYE  = "wh3_dlc26_lord_abilities_eye_of_khorne"
  local D13K = "wh3_dlc29_spell_bound_the_dreaded_thirteenth"
  local GATE_NURGLE = "wh3_main_character_abilities_gate_of_nurgle"
  local ANC_VENG = "wh3_dlc23_item_abilities_ancestral_vengeance"
  local CMDR = "wh3_main_kho_cha_skarbrand_0"
  local GRUNT = "wh2_dlc09_tmb_inf_skeleton_warriors_0"
  local GRUNT2 = "wh2_dlc09_tmb_mon_heirotitan_0"
  local ILLUSIONS = {
    "wh2_dlc10_lord_abilities_deadly_mislead",
    "wh3_dlc24_lord_item_deceiving_shadows",
    "wh2_dlc14_unit_abilities_doppelgang",
    "wh2_dlc10_lord_abilities_mislead",
  }
  local NINE = {
    "wh2_dlc16_lord_abilities_beast_pack",
    "wh2_dlc15_item_abilities_blacktoofs_conjuration",
    "wh2_dlc16_lord_abilities_call_to_gwindalor",
    "wh2_dlc16_spell_bound_vampires_lesser_raise_dead",
    "wh2_dlc17_spell_bound_savage_dominion",
    "wh3_dlc26_hero_abilities_savage_predators",
    "wh2_dlc16_hero_abilities_tide_of_death",
    "wh2_dlc16_hero_abilities_tide_of_pox",
    "wh3_main_item_abilities_zak_aloooog",
  }

  local EXP
  if RED_MODE then
    EXP = { entries = 573, keys = 599, sum = false }
  else
    EXP = { entries = 642, keys = 682, sum = true }
  end

  local function cp102(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function note102(W, TAG)
    if TAG == "[live] " then
      RED102.fires = RED102.fires + #W.fires
      RED102.ground = RED102.ground + #W.ground_fires
    end
  end
  local function boot102(W, PATH, TAG, uid, marker, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. marker); ui(W)
    W.conflict = true
    return true
  end
  local function span102(s, head, tail2)
    local i = raw_find(s, head, 1, true)
    if i == nil then return nil end
    local j = raw_find(s, tail2, i, true)
    if j == nil then return nil end
    return s:sub(i, j)
  end
  -- the ENEMY unit object behind a uid (the enemy list is a separate pool from
  -- the friendly one, so unit_of cannot find these)
  local function enemy102(W, uid)
    for i = 1, #W.enemy_entries do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        local ok, id = pcall(function() return pr.unit:unique_ui_id() end)
        if ok and tostring(id) == tostring(uid) then return pr.unit end
      end
    end
    return nil
  end
  local pre102 = checks

  print("== HARNESS 102 - section 0z: the summon round's static gates ==")
  for _, f in ipairs({ { name = "live", src = live_src102 }, { name = "ann", src = ann_src102 } }) do
    local nm, s = f.name, f.src
    check("0z " .. nm .. ": the table is " .. EXP.entries .. " entries / " .. EXP.keys .. " keys",
      cp102(s, "\n\t{ marker = ") == EXP.entries and cp102(s, 'badge = "') == EXP.entries)
    check("0z " .. nm .. ": enemy_ground_melee now carries the batch + the nine (" ..
      cp102(s, 'trigger = "enemy_ground_melee"') .. ")",
      cp102(s, 'trigger = "enemy_ground_melee"') == (EXP.sum and 67 or 1))
    check("0z " .. nm .. ": the three NEW triggers exist exactly once each",
      cp102(s, 'trigger = "self_summon_melee"') == (EXP.sum and 1 or 0)
      and cp102(s, 'trigger = "enemy_low_health_noncommander"') == (EXP.sum and 1 or 0)
      and cp102(s, 'trigger = "enemy_melee_noncommander"') == (EXP.sum and 1 or 0))
    check("0z " .. nm .. ": every 70%-bounded entry carries its REAL range (range_real x" ..
      cp102(s, "\t\trange_real = ") .. ")",
      cp102(s, "\t\trange_real = ") == (EXP.sum and 163 or 96))
    local ill = 0
    for i = 1, #ILLUSIONS do
      if raw_find(s, ILLUSIONS[i], 1, true) ~= nil then ill = ill + 1 end
    end
    check("0z " .. nm .. ": NONE of the four illusion summons is in the mod (" .. ill .. " hits)", ill == 0)
    local nine = 0
    for i = 1, #NINE do
      if raw_find(s, NINE[i], 1, true) ~= nil then nine = nine + 1 end
    end
    check("0z " .. nm .. ": all nine unlabelled real spawners are in (" .. nine .. "/9)",
      nine == (EXP.sum and 9 or 0))
    check("0z " .. nm .. ": the finisher's health line is 20% and strictly below",
      raw_find(s, "FOURTH.HEALTH_LINE_PCT = 20", 1, true) ~= nil
      and raw_find(s, "hp < FOURTH.HEALTH_LINE_PCT", 1, true) ~= nil)
    if EXP.sum then
      local cm = span102(s, "FOURTH.commander_keys = {", "\n}\n")
      check("0z " .. nm .. ": the DERIVED commander key set is present and big enough",
        cm ~= nil and cp102(cm, '"] = true,') >= 1400)
      check("0z " .. nm .. ": the commander set carries a known Lord and NOT a known line unit",
        cm ~= nil and raw_find(cm, '["' .. CMDR .. '"] = true,', 1, true) ~= nil
        and raw_find(cm, '["' .. GRUNT .. '"] = true,', 1, true) == nil)
      check("0z " .. nm .. ": the commander test reads type() first and unit_class() as the fallback",
        raw_find(s, "function FOURTH.enemy_is_commander(enemy)", 1, true) ~= nil
        and raw_find(s, "enemy:unit_class()", 1, true) ~= nil
        and raw_find(s, "FOURTH.commander_keys[t] == true", 1, true) ~= nil)
      check("0z " .. nm .. ": the self-summon evaluator exists, is mapped and has its own wording",
        raw_find(s, "function FOURTH.evaluate_self_summon_melee(unit, routing)", 1, true) ~= nil
        and raw_find(s, "self_summon_melee = FOURTH.evaluate_self_summon_melee,", 1, true) ~= nil
        and raw_find(s, 'self_summon_melee = "When armed, fires when this unit itself is fighting in melee', 1, true) ~= nil)
      check("0z " .. nm .. ": both non-commander evaluators exist, are mapped and have wordings",
        raw_find(s, "function FOURTH.evaluate_enemy_low_health_noncommander(unit, routing)", 1, true) ~= nil
        and raw_find(s, "function FOURTH.evaluate_enemy_melee_noncommander(unit, routing)", 1, true) ~= nil
        and raw_find(s, "enemy_low_health_noncommander = FOURTH.evaluate_enemy_low_health_noncommander,", 1, true) ~= nil
        and raw_find(s, "enemy_melee_noncommander = FOURTH.evaluate_enemy_melee_noncommander,", 1, true) ~= nil
        and raw_find(s, 'enemy_low_health_noncommander = "When armed, fires on the lowest-health enemy', 1, true) ~= nil
        and raw_find(s, 'enemy_melee_noncommander = "When armed, fires on the closest enemy', 1, true) ~= nil)
      check("0z " .. nm .. ": the self-summon is NOT in either ground-key set (it casts on the OWNER)",
        raw_find(s, '["' .. NURG .. '"] = true,', 1, true) == nil)
      check("0z " .. nm .. ": Eye of Khorne is NOT an enemy-GROUND key (its row is target_enemies, ground false)",
        (function()
          local g = span102(s, "enemy_ground_keys = {", "\n\t},\n")
          return g ~= nil and raw_find(g, EYE, 1, true) == nil
        end)())
      check("0z " .. nm .. ": the nine and the four Dreaded Thirteenth keys ARE enemy-ground keys",
        (function()
          local g = span102(s, "enemy_ground_keys = {", "\n\t},\n")
          if g == nil then return false end
          local n = 0
          for i = 1, #NINE do if raw_find(g, NINE[i], 1, true) ~= nil then n = n + 1 end end
          local d = 0
          for _, k in ipairs({ D13K, D13K .. "_1", D13K .. "_thanquol", D13K .. "_thanquol_1" }) do
            if raw_find(g, k, 1, true) ~= nil then d = d + 1 end
          end
          return n == 9 and d == 4
        end)())
      check("0z " .. nm .. ": the ONE unbounded entry is flagged (a -1.0 real range has no 70% bound)",
        cp102(s, "\t\tunbounded = true,") == 1
        and raw_find(s, "FOURTH.eg_no_bound = (ability.unbounded == true)", 1, true) ~= nil
        and raw_find(s, "if FOURTH.eg_no_bound == true then return true end", 1, true) ~= nil)
    end
    check("0z " .. nm .. ": the engine's unit_in_range CALL is still absent", raw_find(s, "unit_in_range(", 1, true) == nil)
    check("0z " .. nm .. ": no string.find call is present", raw_find(s, "string.find(", 1, true) == nil)
  end
  check("0z ann: the reading copy stays log-free",
    raw_find(ann_src102, "log(", 1, true) == nil)
  check("0z live: the self-summon re-check names its own state and the absent range bound",
    raw_find(live_src102, "SKIPPED: the caster left melee before the self cast", 1, true) ~= nil
    and raw_find(live_src102, "pre-cast re-check: the caster is still in melee", 1, true) ~= nil)
  check("0z live: the finisher's pick and re-check name the health line and the commander state",
    raw_find(live_src102, "lowest-health non-commander enemy below", 1, true) ~= nil
    and raw_find(live_src102, "commander=", 1, true) ~= nil)

  -- ==========================================================================
  print("== HARNESS 102 - the summon worlds ==")

  -- W1: Nurgling Tide - the caster itself is in melee -> SELF cast, one fire.
  do
    local uid = 10201
    local W = make_world({ can_perform = true,
      units = { { name = "nurgle_cultist", uid = uid, owns = { NURG }, melee = true, in_range = false } },
      enemies = {},
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = NURG } } })
    print("== W1 Nurgling Tide: the caster itself is in melee ==")
    if boot102(W, LIVE, "[live] ", uid, "nurgling_tide", "W1 ") then
      polln(W, 5)
      if EXP.sum then
        check("[live] W1: exactly ONE fire, on the UNIT form (" .. #W.fires .. " unit, " .. #W.ground_fires .. " ground)",
          #W.fires == 1 and #W.ground_fires == 0 and W.fires[1].key == NURG)
        check("[live] W1: the cast target is the OWNER itself",
          W.fires[1] ~= nil and W.fires[1].target == unit_of(W, uid))
        check("[live] W1: the 2 s guard HOLDS - five polls still produce one fire", #W.fires == 1)
        check("[live] W1: the reason names the self summon and states there is no range bound",
          count_log(W, "the caster itself is in melee (self summon - cast on SELF, no range bound)") >= 1)
        check("[live] W1: the pre-cast re-check logs the still-in-melee state with no gap",
          count_log(W, "pre-cast re-check: the caster is still in melee") >= 1
          and count_log(W, "no range bound - self cast") >= 1)
      else
        check("[live] W1 (RED): nothing fires on the pre-102 snapshot",
          #W.fires == 0 and #W.ground_fires == 0)
      end
      note102(W, "[live] "); tally(W)
    end
  end

  -- W2: Nurgling Tide - NOT in melee -> silent.
  do
    local uid = 10211
    local W = make_world({ can_perform = true,
      units = { { name = "nurgle_cultist", uid = uid, owns = { NURG }, melee = false, in_range = true, dist = 5 } },
      enemies = { { name = GRUNT, uid = 10212, melee = true } },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = NURG } } })
    print("== W2 Nurgling Tide: the caster is NOT in melee ==")
    if boot102(W, LIVE, "[live] ", uid, "nurgling_tide", "W2 ") then
      polln(W, 4)
      check("[live] W2: an idle caster casts NOTHING (" .. #W.fires .. " unit, " .. #W.ground_fires .. " ground)",
        #W.fires == 0 and #W.ground_fires == 0)
      note102(W, "[live] "); tally(W)
    end
  end

  -- W3: Eye of Khorne - the LOWEST-health non-commander BELOW 20% wins.
  do
    local uid = 10221
    local W = make_world({ can_perform = true,
      units = { { name = "bloodthirster", uid = uid, owns = { EYE }, melee = true,
                  dist_by_target = { [10222] = 10, [10223] = 20, [10224] = 25 } } },
      enemies = { { name = CMDR, uid = 10222, melee = true, ctx = { HealthPercent = 5 } },
                  { name = GRUNT, uid = 10223, melee = true, health_percent = 18 },
                  { name = GRUNT2, uid = 10224, melee = true, ctx = { HealthPercent = "12" } } },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = EYE } } })
    print("== W3 Eye of Khorne: lowest-health non-commander below 20% ==")
    if boot102(W, LIVE, "[live] ", uid, "eye_of_khorne", "W3 ") then
      polln(W, 4)
      if EXP.sum then
        check("[live] W3: ONE fire through the UNIT form (" .. #W.fires .. " unit, " .. #W.ground_fires .. " ground)",
          #W.fires == 1 and #W.ground_fires == 0 and W.fires[1].key == EYE)
        check("[live] W3: the target is the LOWEST-health NON-commander (not the 5% Lord)",
          W.fires[1] ~= nil and W.fires[1].target == enemy102(W, 10224))
        check("[live] W3: the pick log names that unit, the mode and its 12% (a STRING health read)",
          count_log(W, "eye_of_khorne target: '" .. GRUNT2 .. "' is the chosen enemy (health), health=12%") >= 1)
        check("[live] W3: the reason says lowest-health non-commander below 20%",
          count_log(W, "lowest-health non-commander enemy below 20% in bound") >= 1)
        check("[live] W3: neither the 5% Lord nor the 18% line unit was ever the chosen target",
          count_log(W, "target: '" .. CMDR .. "'") == 0
          and count_log(W, "target: '" .. GRUNT .. "'") == 0)
        check("[live] W3: the pre-cast re-check re-read the health and the distance",
          count_log(W, "pre-cast re-check: target still engaged") >= 1
          and count_log(W, "health=12%") >= 2)
      else
        check("[live] W3 (RED): nothing fires on the pre-102 snapshot",
          #W.fires == 0 and #W.ground_fires == 0)
      end
      note102(W, "[live] "); tally(W)
    end
  end

  -- W4: Eye of Khorne - every enemy ABOVE 20% -> silent.
  do
    local uid = 10231
    local W = make_world({ can_perform = true,
      units = { { name = "bloodthirster", uid = uid, owns = { EYE }, melee = true,
                  dist_by_target = { [10232] = 10, [10233] = 15 } } },
      enemies = { { name = GRUNT, uid = 10232, melee = true, health_percent = 40 },
                  { name = GRUNT2, uid = 10233, melee = true, health_percent = 55 } },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = EYE } } })
    print("== W4 Eye of Khorne: all enemies above 20% ==")
    if boot102(W, LIVE, "[live] ", uid, "eye_of_khorne", "W4 ") then
      polln(W, 4)
      check("[live] W4: above the 20% line nothing fires (" .. #W.fires .. " unit, " .. #W.ground_fires .. " ground)",
        #W.fires == 0 and #W.ground_fires == 0)
      note102(W, "[live] "); tally(W)
    end
  end

  -- W5: Eye of Khorne - a LORD below 20% is EXCLUDED.
  do
    local uid = 10241
    local W = make_world({ can_perform = true,
      units = { { name = "bloodthirster", uid = uid, owns = { EYE }, melee = true, dist = 10 } },
      enemies = { { name = CMDR, uid = 10242, melee = true, health_percent = 5 } },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = EYE } } })
    print("== W5 Eye of Khorne: only a LORD below 20% ==")
    if boot102(W, LIVE, "[live] ", uid, "eye_of_khorne", "W5 ") then
      polln(W, 4)
      check("[live] W5: a 5% LORD is NOT a finisher target (" .. #W.fires .. " unit, " .. #W.ground_fires .. " ground)",
        #W.fires == 0 and #W.ground_fires == 0)
      note102(W, "[live] "); tally(W)
    end
  end

  -- W6: Eye of Khorne - beyond the 35 m bound while the ENGINE says in-range.
  do
    local uid, euid = 10251, 10252
    local W = make_world({ can_perform = true,
      units = { { name = "bloodthirster", uid = uid, owns = { EYE }, melee = true, dist = 60 } },
      enemies = { { name = GRUNT, uid = euid, melee = true, health_percent = 10, in_range = true } },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = EYE } } })
    print("== W6 Eye of Khorne: out of bound, engine helper says in-range ==")
    if boot102(W, LIVE, "[live] ", uid, "eye_of_khorne", "W6 ") then
      polln(W, 4)
      check("[live] W6: beyond 35 m stays SILENT although unit_in_range is true (" .. #W.fires .. ")",
        #W.fires == 0 and #W.ground_fires == 0)
      check("[live] W6: the engine helper was never consulted (" .. tostring(W.range_calls[euid] or 0) .. ")",
        (W.range_calls[euid] or 0) == 0)
      note102(W, "[live] "); tally(W)
    end
  end

  -- W7: The Dreaded Thirteenth - a non-commander in melee -> ground cast.
  do
    local uid, euid = 10261, 10262
    local W = make_world({ can_perform = true,
      units = { { name = "skaven_warlock", uid = uid, owns = { D13K }, melee = false, dist = 50 } },
      enemies = { { name = GRUNT, uid = euid, melee = true } },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = D13K } } })
    print("== W7 Dreaded Thirteenth: a non-commander in melee ==")
    if boot102(W, LIVE, "[live] ", uid, "the_dreaded_thirteenth", "W7 ") then
      polln(W, 4)
      if EXP.sum then
        check("[live] W7: ONE ground cast on the ENEMY's own vector (" .. #W.ground_fires .. " ground)",
          #W.ground_fires == 1 and #W.fires == 0 and W.ground_fires[1].key == D13K
          and W.ground_fires[1].pos ~= nil
          and W.ground_fires[1].pos.marker == ("pos:" .. tostring(euid)))
        check("[live] W7: the reason names the non-commander in-melee pick and the real distance",
          count_log(W, "closest non-commander enemy in melee within bound") >= 1
          and count_log(W, "distance=50.0m") >= 1)
        check("[live] W7: the 70% bound of the 100 m row is logged as 70m",
          count_log(W, "bound=70m") >= 1)
      else
        check("[live] W7 (RED): nothing fires on the pre-102 snapshot",
          #W.fires == 0 and #W.ground_fires == 0)
      end
      note102(W, "[live] "); tally(W)
    end
  end

  -- W8: The Dreaded Thirteenth - a COMMANDER in melee is excluded.
  do
    local uid, euid = 10271, 10272
    local W = make_world({ can_perform = true,
      units = { { name = "skaven_warlock", uid = uid, owns = { D13K }, melee = false, dist = 20 } },
      enemies = { { name = CMDR, uid = euid, melee = true } },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = D13K } } })
    print("== W8 Dreaded Thirteenth: only a COMMANDER in melee ==")
    if boot102(W, LIVE, "[live] ", uid, "the_dreaded_thirteenth", "W8 ") then
      polln(W, 4)
      check("[live] W8: a commander in melee is NOT a target (" .. #W.fires .. " unit, " .. #W.ground_fires .. " ground)",
        #W.fires == 0 and #W.ground_fires == 0)
      note102(W, "[live] "); tally(W)
    end
  end

  -- W9: a BATCH sample (Gate of Nurgle, 50 m row -> 35 m bound) fires at the
  --     enemy's own position, never the caster's.
  do
    local uid, euid = 10281, 10282
    local W = make_world({ can_perform = true,
      units = { { name = "cultist", uid = uid, owns = { GATE_NURGLE }, melee = true, dist = 30 } },
      enemies = { { name = GRUNT, uid = euid, melee = true } },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = GATE_NURGLE } } })
    print("== W9 batch sample (Gate of Nurgle): a fighting enemy inside 35 m ==")
    if boot102(W, LIVE, "[live] ", uid, "gate_of_nurgle", "W9 ") then
      polln(W, 4)
      if EXP.sum then
        check("[live] W9: ONE ground cast fired (" .. #W.ground_fires .. " ground, " .. #W.fires .. " unit)",
          #W.ground_fires == 1 and #W.fires == 0 and W.ground_fires[1].key == GATE_NURGLE)
        check("[live] W9: the position is the ENEMY's own vector",
          W.ground_fires[1] ~= nil and W.ground_fires[1].pos ~= nil
          and W.ground_fires[1].pos.marker == ("pos:" .. tostring(euid)))
        check("[live] W9: the position is NEVER the caster's and orient/width are 0",
          W.ground_fires[1] ~= nil and W.ground_fires[1].pos.marker ~= ("pos:" .. tostring(uid))
          and W.ground_fires[1].orient == 0 and W.ground_fires[1].width == 0)
        check("[live] W9: the reason is Gate of Khorne's own closest-fighting wording",
          count_log(W, "closest fighting (in-melee) enemy within bound") >= 1)
      else
        check("[live] W9 (RED): nothing fires on the pre-102 snapshot", #W.ground_fires == 0)
      end
      note102(W, "[live] "); tally(W)
    end
  end

  -- W10: a batch sample with a 30 m row (21 m bound) beyond its bound.
  do
    local uid, euid = 10291, 10292
    local W = make_world({ can_perform = true,
      units = { { name = "wight_king", uid = uid, owns = { ANC_VENG }, melee = false, dist = 25 } },
      enemies = { { name = GRUNT, uid = euid, melee = true, in_range = true } },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = ANC_VENG } } })
    print("== W10 batch sample (Ancestral Vengeance): 25 m vs the 21 m bound ==")
    if boot102(W, LIVE, "[live] ", uid, "ancestral_vengeance", "W10 ") then
      polln(W, 4)
      check("[live] W10: 25 m is beyond the 21 m bound - SILENT although in_range is true",
        #W.fires == 0 and #W.ground_fires == 0)
      check("[live] W10: the engine helper was never consulted (" .. tostring(W.range_calls[euid] or 0) .. ")",
        (W.range_calls[euid] or 0) == 0)
      note102(W, "[live] "); tally(W)
    end
  end

  -- W11: the tiebreak - equal lowest health, the CLOSEST wins.
  do
    local uid = 10301
    local W = make_world({ can_perform = true,
      units = { { name = "bloodthirster", uid = uid, owns = { EYE }, melee = true,
                  dist_by_target = { [10302] = 30, [10303] = 12 } } },
      enemies = { { name = GRUNT, uid = 10302, melee = true, health_percent = 9 },
                  { name = GRUNT2, uid = 10303, melee = true, health_percent = 9 } },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = EYE } } })
    print("== W11 Eye of Khorne: equal health -> the CLOSEST enemy wins ==")
    if boot102(W, LIVE, "[live] ", uid, "eye_of_khorne", "W11 ") then
      polln(W, 4)
      if EXP.sum then
        check("[live] W11: the 12 m enemy wins the tiebreak over the 30 m one",
          #W.fires == 1 and W.fires[1].target == enemy102(W, 10303))
        check("[live] W11: the pick log prints the REAL 12.0 m distance",
          count_log(W, "distance=12.0m") >= 1)
      else
        check("[live] W11 (RED): nothing fires on the pre-102 snapshot", #W.fires == 0)
      end
      note102(W, "[live] "); tally(W)
    end
  end

  -- W12: an enemy whose type() AND unit_class() are unreadable -> FAIL CLOSED
  --      (treated as a commander) with ONE notice.
  do
    local uid = 10311
    local W = make_world({ can_perform = true,
      units = { { name = "bloodthirster", uid = uid, owns = { EYE }, melee = true, dist = 10 } },
      enemies = { { name = "mystery_unit", uid = 10312, melee = true, health_percent = 5,
                    type_empty = true, no_unit_class = true } },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = EYE } } })
    print("== W12 Eye of Khorne: commander unreadable -> FAIL CLOSED ==")
    if boot102(W, LIVE, "[live] ", uid, "eye_of_khorne", "W12 ") then
      polln(W, 4)
      check("[live] W12: an unclassifiable 5% enemy is NEVER fired at (fail-closed, " .. #W.fires .. ")",
        #W.fires == 0 and #W.ground_fires == 0)
      if EXP.sum then
        check("[live] W12: exactly ONE one-time notice names both failed reads",
          count_log(W, "commander check: NEITHER type() NOR unit_class() could be read") == 1)
      end
      note102(W, "[live] "); tally(W)
    end
  end

  -- ==========================================================================
  if RED_MODE then
    check("HARNESS 101 suite boundary (harness 102): N/A in the red run - the pre-102 snapshot"
      .. " moves the table-size pins by design", true)
  else
    check("HARNESS 101 suite boundary (harness 102): every harness-101 check ran first ("
      .. pre102 .. ", want 3441)", pre102 == 3441)
  end
  if RED_MODE then
    check("RED CONTROL (harness 102): on the pre-102 snapshot every summon world fires NOTHING"
      .. " (unit " .. RED102.fires .. ", ground " .. RED102.ground .. ") - the entries and the"
      .. " three new triggers do not exist there - while every silent world passes by design"
      .. " and the harness-101 suite still passes apart from the table-size pins.",
      RED102.fires == 0 and RED102.ground == 0)
  else
    check("HEADLINE (harness 102): the summon round ships 642 entries / 682 keys (573 + 69 /"
      .. " 599 + 83): (A) 57 entries / 68 keys + (D) 9 + (E) 1 + (F) 1 entry / 4 keys + (B) 1 on"
      .. " four triggers - enemy_ground_melee 67, self_summon_melee 1,"
      .. " enemy_low_health_noncommander 1, enemy_melee_noncommander 1 - and every world fired"
      .. " as designed (unit " .. RED102.fires .. ", ground " .. RED102.ground .. ").",
      RED102.fires >= 1 and RED102.ground >= 1)
  end
end
run_h102()
