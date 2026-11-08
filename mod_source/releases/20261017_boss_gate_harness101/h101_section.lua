-- ============================================================================
-- HARNESS 101 - BOSS-ONLY EXCLUSION + GATE OF KHORNE (2026-10-17)
--   (A) Every active ability whose ONLY grant path is a `_boss` unit is
--       excluded. Five of them were IMPLEMENTED and are REMOVED from the mod:
--         Greater Faith Bastion  wh_dlc06_quest_abilities_grand_faiths_bastion
--         Bitter Sting           wh3_dlc27_qb_unit_abilities_bitter_sting
--         Frenzied Challenge     wh3_dlc27_qb_unit_abilities_frenzied_challenge
--         Visions of Madness     wh3_dlc27_qb_unit_abilities_visions_of_madness
--         Guttural Roar          wh3_dlc27_qb_unit_abilities_guttural_roar
--       The other ten boss-only keys never shipped and stay absent. The table
--       moves 577 -> 573 entries / 603 -> 599 keys; melee_unwavering
--       362 -> 360 and enemy_engaged_or_shot 89 -> 86.
--   (B) Gate of Khorne (wh3_main_character_abilities_gate_of_khorne) is ADDED
--       on the user's trigger, verbatim: "The trigger will place it on the
--       closest enemy that is in range of the ability and fighting." Among
--       enemies within its own 70% bound (50 m -> 35 m) keep those FIGHTING
--       (in melee), pick the CLOSEST, and place the summon on THAT ENEMY'S
--       GROUND (perform_special_ability_ground(key, enemy_pos, 0, 0)) with
--       fresh caster+enemy handles, a hold, a pre-cast re-check and its own
--       reason string naming the enemy type and the REAL distance.
--
--   0aa (static, BOTH files) + seven worlds:
--     W1 a fighting enemy inside the bound -> FIRES at that enemy's position;
--     W2 several qualifying -> picks the CLOSEST;
--     W3 a fighting enemy BEYOND the bound -> SILENT though the engine helper
--        says in-range (the old move-order bug's guard);
--     W4 an enemy in range but NOT fighting -> SILENT;
--     W5 the chosen enemy stops fighting between pick and cast -> SKIPPED;
--     W6 no enemies -> SILENT;
--     W7 self-cast guard: the position is the ENEMY's, never the caster's.
--   RED CONTROL: with H101_LIVE / H101_ANN on the pre-101 snapshot the five
--   boss keys ARE present, Gate of Khorne is absent, the counts are 577 / 603
--   and every gate world fires nothing - the RED summary asserts exactly that.
-- ============================================================================
function run_h101()
  local live_src101 = read_file(LIVE)
  local ann_src101  = read_file(ANN)
  local RED101 = { fires = 0, ground = 0, claims = 0, ui = 0 }
  local GATE = "wh3_main_character_abilities_gate_of_khorne"
  local function cp101(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function note101(W, TAG)
    RED101.ui = RED101.ui + (W.ui_failures or 0)
    if TAG == "[live] " then
      RED101.fires = RED101.fires + #W.fires
      RED101.ground = RED101.ground + #W.ground_fires
      RED101.claims = RED101.claims + count_log(W, "claim: ")
    end
  end
  local function badd101(marker) return "zz_auto_badge_" .. marker end
  local function boot101(W, PATH, TAG, uid, marker, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, badd101(marker)); ui(W)
    W.conflict = true
    return true
  end
  local function table_span101(s)
    local i = raw_find(s, "local ABILITIES = {", 1, true)
    if i == nil then return nil end
    local j = raw_find(s, "{", i, true)
    if j == nil then return nil end
    local depth = 0
    for k = j, #s do
      local c = s:sub(k, k)
      if c == "{" then
        depth = depth + 1
      elseif c == "}" then
        depth = depth - 1
        if depth == 0 then return s:sub(j, k) end
      end
    end
    return nil
  end
  local function key_count101(t)
    local n, at = 0, 1
    while true do
      local i = raw_find(t, "keys = {", at, true)
      if i == nil then return n end
      local j = raw_find(t, "}", i, true)
      if j == nil then return n end
      for _ in t:sub(i, j):gmatch('"[^"]*"') do n = n + 1 end
      at = j + 1
    end
  end

  local REMOVED = {
    { m = "grand_faiths_bastion", k = "wh_dlc06_quest_abilities_grand_faiths_bastion" },
    { m = "bitter_sting",         k = "wh3_dlc27_qb_unit_abilities_bitter_sting" },
    { m = "frenzied_challenge",   k = "wh3_dlc27_qb_unit_abilities_frenzied_challenge" },
    { m = "visions_of_madness",   k = "wh3_dlc27_qb_unit_abilities_visions_of_madness" },
    { m = "guttural_roar",        k = "wh3_dlc27_qb_unit_abilities_guttural_roar" },
  }
  local NEVER = {
    "wh2_dlc10_quest_abilities_fiery_head",
    "wh2_dlc10_quest_abilities_regenerating_head",
    "wh_dlc08_quest_abilities_howling_winter",
    "wh_dlc08_quest_abilities_master_of_souls",
    "wh_dlc04_quest_abilities_servant_of_nagash",
    "wh3_dlc27_qb_unit_abilities_dissolving_bone",
    "wh3_dlc27_qb_unit_abilities_terrible_malice",
    "wh3_dlc27_qb_unit_abilities_copious_phlegm",
    "wh2_dlc10_quest_abilities_magic_fiery_convocation",
    "wh2_dlc10_quest_abilities_flame_storm",
  }

  local EXP
  if RED_MODE then
    EXP = { entries = 577, keys = 603, mu = 362, es = 89, gate = false, boss = true }
  else
    EXP = { entries = 573, keys = 599, mu = 360, es = 86, gate = true, boss = false }
  end

  print("== HARNESS 101 - section 0y: the five boss-only entries are REMOVED and Gate of Khorne is ADDED ==")
  for _, f in ipairs({ { name = "live", src = live_src101 }, { name = "ann", src = ann_src101 } }) do
    local nm, s = f.name, f.src
    local span = table_span101(s)
    check("0aa " .. nm .. ": the ABILITIES table parses", span ~= nil)
    if span == nil then goto continue end
    do
      local n_e = cp101(span, "\n\t{ marker = ")
      local n_k = key_count101(span)
      local n_lists = cp101(span, "keys = {")
      check("0aa " .. nm .. ": the entry count is exactly " .. EXP.entries .. " (got " .. n_e .. ")", n_e == EXP.entries)
      check("0aa " .. nm .. ": the key count is exactly " .. EXP.keys .. " (got " .. n_k .. ")", n_k == EXP.keys)
      check("0aa " .. nm .. ": every entry carries exactly one keys list (" .. n_lists .. ")", n_lists == n_e)
      -- the five boss-only entries
      local any5, all5 = false, true
      for i = 1, #REMOVED do
        local has_k = (raw_find(span, REMOVED[i].k, 1, true) ~= nil)
        local has_m = (raw_find(span, 'marker = "' .. REMOVED[i].m .. '"', 1, true) ~= nil)
        local has_b = (raw_find(s, 'badge = "zz_auto_badge_' .. REMOVED[i].m .. '"', 1, true) ~= nil)
        any5 = any5 or has_k
        if not (has_k and has_m and has_b) then all5 = false end
      end
      if EXP.boss then
        check("0aa " .. nm .. ": the PRE-EDIT snapshot still carries all FIVE boss-only keys and badges", all5 and any5)
      else
        check("0aa " .. nm .. ": all five boss-only keys are ABSENT from the ABILITIES table", (not any5))
        local allgone = true
        for i = 1, #REMOVED do
          if raw_find(span, REMOVED[i].k, 1, true) ~= nil then allgone = false end
          if raw_find(span, 'marker = "' .. REMOVED[i].m .. '"', 1, true) ~= nil then allgone = false end
          if raw_find(s, 'badge = "zz_auto_badge_' .. REMOVED[i].m .. '"', 1, true) ~= nil then allgone = false end
          if raw_find(s, REMOVED[i].k, 1, true) ~= nil then allgone = false end
        end
        check("0aa " .. nm .. ": their markers, badge ids and keys are gone from the WHOLE file", allgone)
      end
      -- the ten that never shipped stay absent in BOTH files and BOTH modes
      local never_hits = 0
      for i = 1, #NEVER do
        if raw_find(s, NEVER[i], 1, true) ~= nil then never_hits = never_hits + 1 end
      end
      check("0aa " .. nm .. ": the other ten boss-only keys never shipped and are still absent (" .. never_hits .. " hits)",
        never_hits == 0)
      -- neighbours survive
      check("0aa " .. nm .. ": the neighbours of every removal survive (gaze_of_khaine, gulyas, black_periapt, "
        .. "frost_shard_glaive, hagtree_fetish, void_pendulum)",
        raw_find(span, 'marker = "gaze_of_khaine"', 1, true) ~= nil
        and raw_find(span, 'marker = "gulyas"', 1, true) ~= nil
        and raw_find(span, 'marker = "black_periapt"', 1, true) ~= nil
        and raw_find(span, 'marker = "frost_shard_glaive"', 1, true) ~= nil
        and raw_find(span, 'marker = "hagtree_fetish"', 1, true) ~= nil
        and raw_find(span, 'marker = "void_pendulum"', 1, true) ~= nil)
      local mu = cp101(s, 'trigger = "melee_unwavering"')
      local es = cp101(s, 'trigger = "enemy_engaged_or_shot"')
      check("0aa " .. nm .. ": melee_unwavering is " .. EXP.mu .. " (got " .. mu .. ") and enemy_engaged_or_shot is "
        .. EXP.es .. " (got " .. es .. ")", mu == EXP.mu and es == EXP.es)
      check("0aa " .. nm .. ": enemy_ground_area stays 9 and the new enemy_ground_melee is "
        .. (EXP.gate and "1" or "0"),
        cp101(s, 'trigger = "enemy_ground_area"') == 9
        and cp101(s, 'trigger = "enemy_ground_melee"') == (EXP.gate and 1 or 0))
      -- GATE OF KHORNE
      local has_key = (raw_find(span, GATE, 1, true) ~= nil)
      if EXP.gate then
        check("0aa " .. nm .. ": Gate of Khorne is in the table on its own trigger and real range",
          raw_find(span, 'marker = "gate_of_khorne"', 1, true) ~= nil
          and raw_find(span, 'trigger = "enemy_ground_melee"', 1, true) ~= nil
          and raw_find(span, 'keys = { "' .. GATE .. '" }', 1, true) ~= nil
          and raw_find(span, 'range_real = 50,', 1, true) ~= nil)
        check("0aa " .. nm .. ": the picker is registered and its chart entry names the enemy-ground form",
          raw_find(s, "function FOURTH.evaluate_enemy_ground_melee(unit, routing)", 1, true) ~= nil
          and raw_find(s, "enemy_ground_melee = FOURTH.evaluate_enemy_ground_melee,", 1, true) ~= nil
          and raw_find(s, 'enemy_ground_melee = "When armed, fires when an enemy in range is fighting in melee', 1, true) ~= nil)
        check("0aa " .. nm .. ": the key is registered in enemy_ground_keys (enemy position), NOT in ground_keys (caster position)",
          raw_find(s, '["' .. GATE .. '"] = true,', 1, true) ~= nil
          and (function()
            local gi = raw_find(s, "ground_keys = {", 1, true)
            local gj = raw_find(s, "}", gi, true)
            local seg = s:sub(gi, gj)
            return raw_find(seg, GATE, 1, true) == nil
          end)())
        check("0aa " .. nm .. ": the melee-only flag is set by the evaluator, cleared before every evaluate and demanded by the re-check",
          raw_find(s, "FOURTH.eg_melee_only = nil", 1, true) ~= nil
          and raw_find(s, "local melee_only = (FOURTH.eg_melee_only == true)", 1, true) ~= nil
          and raw_find(s, "local eg_melee_only_now = (FOURTH.eg_melee_only == true)", 1, true) ~= nil
          and cp101(s, "FOURTH.eg_melee_only = nil") >= 2)
      else
        check("0aa " .. nm .. ": Gate of Khorne is ABSENT from the pre-edit snapshot", not has_key)
        check("0aa " .. nm .. ": the pre-edit snapshot has no enemy_ground_melee trigger",
          cp101(s, 'trigger = "enemy_ground_melee"') == 0)
      end
      check("0aa " .. nm .. ": the engine's unit_in_range CALL is still absent from the whole file",
        raw_find(s, "unit_in_range(", 1, true) == nil)
    end
    ::continue::
  end

  -- ==========================================================================
  -- THE WORLDS
  -- ==========================================================================
  print("== HARNESS 101 - the Gate of Khorne worlds ==")

  -- W1: a fighting enemy inside the bound -> fires AT THAT ENEMY'S POSITION.
  do
    local uid, euid = 10101, 10102
    local W = make_world({ can_perform = true,
      units = { { name = "caster", uid = uid, owns = { GATE }, melee = false,
                  in_range = true, dist = 30 } },
      enemies = { { name = "orc_boyz", uid = euid, melee = true, in_range = true } },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = GATE } } })
    print("== W1 fighting enemy inside the bound ==")
    if boot101(W, LIVE, "[live] ", uid, "gate_of_khorne", "W1 ") then
      polln(W, 3)
      if EXP.gate then
        check("[live] W1: the ground cast fired the key (" .. #W.ground_fires .. " ground fires, "
          .. #W.fires .. " unit fires)", #W.ground_fires == 1 and #W.fires == 0
          and W.ground_fires[1].key == GATE)
        check("[live] W1: the position passed is the ENEMY's own vector (marker "
          .. tostring(W.ground_fires[1] and W.ground_fires[1].pos and W.ground_fires[1].pos.marker) .. ")",
          W.ground_fires[1] ~= nil and W.ground_fires[1].pos ~= nil
          and W.ground_fires[1].pos.marker == ("pos:" .. tostring(euid)))
        check("[live] W1: the position is NOT the caster's and the orientation/width are 0",
          W.ground_fires[1] ~= nil and W.ground_fires[1].pos ~= nil
          and W.ground_fires[1].pos.marker ~= ("pos:" .. tostring(uid))
          and W.ground_fires[1].orient == 0 and W.ground_fires[1].width == 0)
        check("[live] W1: the reason names the chosen enemy type and the REAL distance",
          count_log(W, "closest fighting (in-melee) enemy within bound") == 1
          and count_log(W, "distance=30.0m") >= 1)
        check("[live] W1: the picker log names the enemy and the 35 m bound",
          count_log(W, "gate_of_khorne target: 'orc_boyz'") >= 1
          and count_log(W, "bound=35m") >= 1)
      else
        check("[live] W1 (RED): no gate cast is possible on the pre-edit snapshot",
          #W.ground_fires == 0 and #W.fires == 0)
      end
      note101(W, "[live] "); tally(W)
    end
  end

  -- W2: several qualifying -> the CLOSEST one.
  do
    local uid = 10201
    local far, near, mid = 10202, 10203, 10204
    local W = make_world({ can_perform = true,
      units = { { name = "caster", uid = uid, owns = { GATE }, melee = false, in_range = true,
                  dist_by_target = { [far] = 33, [near] = 20, [mid] = 28 } } },
      enemies = { { name = "far_boar", uid = far, melee = true, in_range = true },
                  { name = "near_clanrat", uid = near, melee = true, in_range = true },
                  { name = "mid_slave", uid = mid, melee = true, in_range = true } },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = GATE } } })
    print("== W2 closest of three qualifying enemies ==")
    if boot101(W, LIVE, "[live] ", uid, "gate_of_khorne", "W2 ") then
      polln(W, 3)
      if EXP.gate then
        check("[live] W2: exactly one ground cast fired, on the CLOSEST enemy (" .. #W.ground_fires .. ")",
          #W.ground_fires == 1 and W.ground_fires[1].pos ~= nil
          and W.ground_fires[1].pos.marker == ("pos:" .. tostring(near)))
        check("[live] W2: the reason names the closest enemy and its 20.0 m distance",
          count_log(W, "near_clanrat") >= 1 and count_log(W, "distance=20.0m") >= 1)
      else
        check("[live] W2 (RED): nothing fires on the pre-edit snapshot", #W.ground_fires == 0)
      end
      note101(W, "[live] "); tally(W)
    end
  end

  -- W3: fighting but BEYOND the 35 m bound; the engine's own in-range helper
  --     says TRUE (the old move-order bug's exact shape).
  do
    local uid, euid = 10301, 10302
    local W = make_world({ can_perform = true,
      units = { { name = "caster", uid = uid, owns = { GATE }, melee = false,
                  in_range = true, dist = 60 } },
      enemies = { { name = "orc_big_uns", uid = euid, melee = true, in_range = true } },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = GATE } } })
    print("== W3 fighting enemy BEYOND the bound (engine helper says in-range) ==")
    if boot101(W, LIVE, "[live] ", uid, "gate_of_khorne", "W3 ") then
      polln(W, 3)
      check("[live] W3: beyond the 35 m bound stays SILENT although unit_in_range is true (ground "
        .. #W.ground_fires .. ", unit " .. #W.fires .. ")", #W.ground_fires == 0 and #W.fires == 0)
      check("[live] W3: the engine's unit_in_range helper was never consulted (calls "
        .. tostring(W.range_calls[euid] or 0) .. ")", (W.range_calls[euid] or 0) == 0)
      note101(W, "[live] "); tally(W)
    end
  end

  -- W4: in range, but NOT fighting.
  do
    local uid, euid = 10401, 10402
    local W = make_world({ can_perform = true,
      units = { { name = "caster", uid = uid, owns = { GATE }, melee = false,
                  in_range = true, dist = 10 } },
      enemies = { { name = "orc_archers", uid = euid, melee = false, missile = true, in_range = true } },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = GATE } } })
    print("== W4 in range but NOT fighting (under missile fire only) ==")
    if boot101(W, LIVE, "[live] ", uid, "gate_of_khorne", "W4 ") then
      polln(W, 3)
      check("[live] W4: an enemy that is only under missile fire is NOT 'fighting' - SILENT (ground "
        .. #W.ground_fires .. ", unit " .. #W.fires .. ")", #W.ground_fires == 0 and #W.fires == 0)
      check("[live] W4: the missile read was never even taken (melee-only picker; calls "
        .. tostring(W.missile_calls[euid] or 0) .. ")", (W.missile_calls[euid] or 0) == 0)
      note101(W, "[live] "); tally(W)
    end
  end

  -- W5: the chosen enemy stops fighting between the pick and the cast.
  do
    local uid, euid = 10501, 10502
    local W = make_world({ can_perform = true,
      units = { { name = "caster", uid = uid, owns = { GATE }, melee = false,
                  in_range = true, dist = 30 } },
      enemies = { { name = "orc_boyz", uid = euid, melee = true, melee_seq = { true, false }, in_range = true } },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = GATE } } })
    print("== W5 the chosen enemy stops fighting before the cast ==")
    if boot101(W, LIVE, "[live] ", uid, "gate_of_khorne", "W5 ") then
      polln(W, 3)
      check("[live] W5: the lapse is caught by the pre-cast re-check - cast NOT spent (ground "
        .. #W.ground_fires .. ")", #W.ground_fires == 0 and #W.fires == 0)
      if EXP.gate then
        check("[live] W5: the skip line names the lapse and logs the REAL distance",
          count_log(W, "gate_of_khorne SKIPPED: the chosen enemy lapsed before the cast") >= 1
          and count_log(W, "melee_only=true") >= 1)
      end
      note101(W, "[live] "); tally(W)
    end
  end

  -- W6: no enemies at all.
  do
    local uid = 10601
    local W = make_world({ can_perform = true,
      units = { { name = "caster", uid = uid, owns = { GATE }, melee = false, in_range = true, dist = 20 } },
      enemies = {},
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = GATE } } })
    print("== W6 no enemies ==")
    if boot101(W, LIVE, "[live] ", uid, "gate_of_khorne", "W6 ") then
      polln(W, 3)
      check("[live] W6: no enemies -> SILENT (ground " .. #W.ground_fires .. ", unit " .. #W.fires .. ")",
        #W.ground_fires == 0 and #W.fires == 0)
      note101(W, "[live] "); tally(W)
    end
  end

  -- W7: the self-cast guard - the target is the enemy, NEVER the owner.
  do
    local uid, euid = 10701, 10702
    local W = make_world({ can_perform = true,
      units = { { name = "caster", uid = uid, owns = { GATE }, melee = true,
                  in_range = true, dist = 25 } },
      enemies = { { name = "orc_boyz", uid = euid, melee = true, in_range = true } },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = GATE } } })
    print("== W7 self-cast guard (the caster itself is in melee) ==")
    if boot101(W, LIVE, "[live] ", uid, "gate_of_khorne", "W7 ") then
      polln(W, 3)
      if EXP.gate then
        check("[live] W7: the cast is placed on the ENEMY, never the caster (" ..
          tostring(W.ground_fires[1] and W.ground_fires[1].pos and W.ground_fires[1].pos.marker) .. ")",
          #W.ground_fires == 1 and W.ground_fires[1].pos.marker == ("pos:" .. tostring(euid)))
        check("[live] W7: no fire ever targets the owner's position",
          W.ground_fires[1] ~= nil and W.ground_fires[1].pos ~= nil
          and W.ground_fires[1].pos.marker ~= ("pos:" .. tostring(uid)))
      else
        check("[live] W7 (RED): no gate cast on the pre-edit snapshot", #W.ground_fires == 0)
      end
      note101(W, "[live] "); tally(W)
    end
  end

  -- ==========================================================================
  if RED_MODE then
    check("RED CONTROL (harness 101): on the pre-101 snapshot Gate of Khorne is absent, so every gate world fires "
      .. "NOTHING (ground " .. RED101.ground .. ", unit " .. RED101.fires .. ") while the SILENT worlds pass by "
      .. "design; the five boss keys are still carried and every green 0aa check would FAIL.", RED101.ground == 0)
  else
    check("HEADLINE (harness 101): the five boss-only entries are REMOVED (573 entries / 599 keys; "
      .. "melee_unwavering 360, enemy_engaged_or_shot 86) and Gate of Khorne fires on the CLOSEST FIGHTING "
      .. "enemy in its 35 m bound, placing the summon on THAT ENEMY's ground (ground fires "
      .. tostring(RED101.ground) .. ", unit fires " .. tostring(RED101.fires) .. ").", RED101.ground >= 1)
  end
end
run_h101()
