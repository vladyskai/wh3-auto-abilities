-- ============================================================================
-- HARNESS 218 (round 220, sign-off): a PLACED effect does not wait for its caster, three speed fixes for the polls.
--   0zz67 the round-220 tokens in both files. The ANIM set: Brass Orb and Frost Fang (placed effects) are out, Amber
--         Bow, Soporific Breath and Volley of High Arrows (projectiles) are in.
--   ST1 Brass Orb, the caster WALKING, a standing Militia unit in range -> ONE cast (RED: none, the caster must stand).
--   ST2 Brass Orb, the caster walking, the TARGET walking -> no cast (the target rule is unchanged).
--   LK1 Brass Orb fired (3 uses, a 90 s recharge the mod counts). In the next 12 polls the caster's distance to the
--       enemy is not read by the evaluator. GREEN: at most 2 reads. RED: 10 or more.
--   CC1 three Brass Orb casters, one standing enemy block that our own unit stands next to (no cast possible). In 8
--       polls the block's is_moving() is read once per map. GREEN: at most 12 reads. RED: 20 or more.
--   RED control: H218_LIVE / H218_ANN on docs/backups/round220/pre220_*.lua.
-- ============================================================================
function run_h218()
  local L218 = os.getenv("H218_LIVE") or LIVE
  local A218 = os.getenv("H218_ANN") or ANN
  local RED218 = (os.getenv("H218_LIVE") ~= nil) or (os.getenv("H218_ANN") ~= nil)
  local BO = "wh2_dlc12_character_abilities_brass_orb"
  local CASTER = "wh2_dlc12_skv_cha_warlock_master_0"
  local MIL = "wh_dlc04_emp_inf_free_company_militia_0"
  local SW = "wh2_main_skv_inf_stormvermin_0"
  local pre218 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 218 - section 0zz67: the round-220 tokens ==")
  for _, f in ipairs({ { name = "live", path = L218 }, { name = "ann", path = A218 } }) do
    local s = read_file(f.path)
    local a0 = raw_find(s, "\nFOURTH.ANIM_TEXT = \"", 1, true)
    local a1 = a0 and raw_find(s, "\"\n", a0 + 22, true)
    local anim = (a0 and a1) and (";" .. string.sub(s, a0 + 21, a1 - 1) .. ";") or ""
    local function has(k) return raw_find(anim, ";" .. k .. ";", 1, true) ~= nil end
    local proj = has("wh2_dlc13_weapon_abilities_amber_bow") and has("wh2_main_unit_abilities_soporific_breath")
      and has("wh2_main_character_abilities_volley_of_high_arrows")
    local placed = has(BO) or has("wh3_main_weapon_abilities_frost_fang")
    local got = cp(s, "\nfunction FOURTH.locked_now(ui_id, ability)\n") + cp(s, "if FOURTH.locked_now(ui_id, ability) then return nil end")
      + cp(s, "\nfunction FOURTH.blob_score_c(e, m, r)\n") + cp(s, "\nfunction FOURTH.blob_friend_gap_c(e, m, reach)\n")
      + cp(s, "\t\t\tlocal oid = m.ours[i].id   -- ROUND 220: the id the map read\n")
      + cp(s, "\tif e.c_still == nil then   -- ROUND 220: read once per map\n")
    if RED218 then
      check("0zz67 " .. f.name .. " (RED): the pre-220 file has none of it, the placed effects are in the ANIM set",
        got == 0 and proj and placed)
    else
      check("0zz67 " .. f.name .. ": the lock test, the two caches, the map's id and still reads (" .. got
        .. " of 6), the projectiles in the ANIM set (" .. tostring(proj) .. "), the placed effects out (" .. tostring(not placed) .. ")",
        got == 6 and proj and not placed)
    end
  end
  local FILES = { { path = A218, tag = "[annotated] " }, { path = L218, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function verdict(TAG, id, text, ok)
    check(TAG .. id .. (RED218 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  local function world(wname, units, enemies, PATH, TAG, sv, arm_ids, polls)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = BO } } })
    W.defaults_on = false
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    W.e_moving_reads = 0
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        local id = nil
        pcall(function() id = tostring(pr.unit:unique_ui_id()) end)
        pr.unit.is_visible_to_alliance = function(self, a) return true end
        pr.unit.is_currently_flying = function(self) return false end
        local v = sv[id]
        if v ~= nil then pr.unit.strategic_value = function(self) return v end end
        local old_m = pr.unit.is_moving
        pr.unit.is_moving = function(self, ...)
          W.e_moving_reads = W.e_moving_reads + 1
          return old_m(self, ...)
        end
      end
    end
    W.c_dist_reads = 0
    for _, r in ipairs(W.sel_registrations) do
      local id = nil
      pcall(function() id = tostring(r.unit:unique_ui_id()) end)
      if id == tostring(units[1].uid) and not r.unit.zz_h218 then
        r.unit.zz_h218 = true
        local old_d = r.unit.unit_distance
        r.unit.unit_distance = function(self, ...)
          W.c_dist_reads = W.c_dist_reads + 1
          return old_d(self, ...)
        end
      end
    end
    for _, uid in ipairs(arm_ids) do
      sel_event(W, uid, true); ui(W); ui(W)
      click(W, "zz_auto_badge_brass_orb"); ui(W)
      sel_event(W, uid, false); ui(W)
    end
    W.conflict = true
    polln(W, polls)
    return W
  end
  local function caster(uid, x, o)
    local c = { name = CASTER, uid = uid, owns = { BO }, melee = false, dist = 60, pos = { x, 0, 0 }, width = 2,
                men_alive = 1, unit_class = "com" }
    for k, v in pairs(o or {}) do c[k] = v end
    return c
  end
  local function militia(uid, o)
    local e = { uid = uid, name = MIL, melee = false, pos = { 0, 0, 80 }, width = 31.7, men_alive = 110,
                initial_men = 120, unit_class = "inf_mis", dist = 60 }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  local function casts(W)
    local n = 0
    for _, x in ipairs(W.fires) do if x.key == BO then n = n + 1 end end
    return n
  end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    do
      local b = 22200
      local W = world("ST1. Brass Orb, the caster walking, a standing Militia unit", { caster(b, 0, { moving = true }) },
        { militia(b + 5) }, P, TAG, { [tostring(b + 5)] = 430 }, { b }, 4)
      if W ~= nil then
        local got = casts(W)
        local good = (got == 1)
        if RED218 then good = (got == 0) end
        verdict(TAG, "ST1a", got .. " cast(s) (" .. (RED218 and "RED: 0" or "need 1") .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    if not RED218 then
      local b = 22220
      local W = world("ST2. Brass Orb, the caster walking, the target walking", { caster(b, 0, { moving = true }) },
        { militia(b + 5, { moving = true }) }, P, TAG, { [tostring(b + 5)] = 430 }, { b }, 4)
      if W ~= nil then
        verdict(TAG, "ST2a", casts(W) .. " cast(s) (need 0)", casts(W) == 0)
        tally(W)
      else
        done(false)
      end
    end
    do
      local b = 22240
      local W = world("LK1. Brass Orb fired: the evaluator is not called while the recharge runs", { caster(b, 0) },
        { militia(b + 5) }, P, TAG, { [tostring(b + 5)] = 430 }, { b }, 4)
      if W ~= nil then
        local first = casts(W)
        W.c_dist_reads = 0
        polln(W, 12)
        local reads = W.c_dist_reads
        local good = (first == 1 and reads <= 2)
        if RED218 then good = (first == 1 and reads >= 10) end
        verdict(TAG, "LK1a", first .. " cast (need 1), then " .. reads .. " distance read(s) by the caster in 12 polls ("
          .. (RED218 and "RED: 10 or more" or "need at most 2") .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local b = 22260
      local units = { caster(b, 0), caster(b + 1, 6), caster(b + 2, -6),
        { uid = b + 3, name = SW, owns = {}, melee = false, pos = { 0, 0, 95 }, width = 20, men_alive = 100,
          initial_men = 100, unit_class = "inf_mel" } }
      local W = world("CC1. three casters, one block that our own unit stands next to", units, { militia(b + 5) }, P, TAG,
        { [tostring(b + 5)] = 430 }, { b, b + 1, b + 2 }, 2)
      if W ~= nil then
        W.e_moving_reads = 0
        polln(W, 8)
        local reads = W.e_moving_reads
        local good = (casts(W) == 0 and reads <= 12)
        if RED218 then good = (casts(W) == 0 and reads >= 20) end
        verdict(TAG, "CC1a", casts(W) .. " cast(s) (need 0), the block's is_moving() read " .. reads .. " time(s) in 8 polls ("
          .. (RED218 and "RED: 20 or more" or "need at most 12") .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
  end
  check("HARNESS 218: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 218 done: " .. (checks - pre218) .. " checks in this section ==")
end
