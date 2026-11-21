-- ============================================================================
-- HARNESS 196 (round 197, user 2026-11-21: "A: whole army"): THE WHOLE-ARMY FALLBACK for the blob family. When no
--   living unit of the enemy army, visible or HIDDEN, passes the armour and trash rules, the blob ability takes the
--   best visible target without them.
--   0zz43 the round-197 tokens in both files.
--   FB1 Volley of High Arrows (armour-piercing), the enemy army is only Tithe (armour 15, trash) -> ONE cast at it.
--       RED: no cast (the armour rule holds it all battle, the Arrow of Kurnous case).
--   FB2 the same Tithe in sight, and a HIDDEN Grave Guard block (armour 90) in the army -> no cast (save it).
--   FB3 Fireball (not armour-piercing), the army is only Tithe (trash) -> ONE cast at it. RED: no cast.
--   FB4 Fireball, Tithe in sight and a hidden block worth 7 a soldier -> no cast.
--   FB5 (live) the BLOB FALLBACK line once, and the reason names the fallback.
--   RED control: H196_LIVE / H196_ANN on docs/backups/round197/pre197_*.lua.
-- ============================================================================
function run_h196()
  local L196 = os.getenv("H196_LIVE") or LIVE
  local A196 = os.getenv("H196_ANN") or ANN
  local RED196 = (os.getenv("H196_LIVE") ~= nil) or (os.getenv("H196_ANN") ~= nil)
  local FB = "wh_main_spell_bound_fireball"
  local VO = "wh2_main_character_abilities_volley_of_high_arrows"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local GG = "wh_main_vmp_inf_grave_guard_0"
  local TI = "wh_dlc04_vmp_inf_tithe_0"
  local pre196 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 196 - section 0zz43: the round-197 tokens ==")
  for _, f in ipairs({ { name = "live", path = L196 }, { name = "ann", path = A196 } }) do
    local s = read_file(f.path)
    local head = cp(s, "-- ROUND 197 - THE WHOLE-ARMY FALLBACK")
    local set = cp(s, "FOURTH.blob_relax = (ZZ_AUTO_TEST_NO_BLOB_FALLBACK ~= true) and not FOURTH.blob_better_exists(key, central)")
    local rules = cp(s, "FOURTH.blob_ap_rule(") + cp(s, "FOURTH.blob_trash_rule(")
    if RED196 then
      check("0zz43 " .. f.name .. " (RED): the pre-197 file has no fallback", head == 0 and set == 0 and rules == 0)
    else
      -- 2 definitions + blob_pick (2) + blob_pick_large (1) + blob_still_ok (3) = 8
      check("0zz43 " .. f.name .. ": the block (" .. head .. "), the flag (" .. set .. "), the rules at their 8 places (" .. rules .. ")",
        head == 1 and set == 1 and rules == 8)
    end
  end
  local FILES = { { path = A196, tag = "[annotated] " }, { path = L196, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, units, enemies, arm, key, PATH, TAG, sv, hidden)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = key } } })
    W.blob_fallback_on = true
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        local id = nil
        pcall(function() id = tostring(pr.unit:unique_ui_id()) end)
        local vis = not (hidden ~= nil and hidden[id] == true)
        pr.unit.is_visible_to_alliance = function(self, a) return vis end
        if sv ~= nil and sv[id] ~= nil then
          local v = sv[id]
          pr.unit.strategic_value = function(self) return v end
        end
      end
    end
    sel_event(W, arm[1], true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. arm[2]); ui(W)
    sel_event(W, arm[1], false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  local function caster(b, key)
    return { name = CASTER, uid = b, owns = { key }, melee = false, dist = 100, pos = { 0, 0, 0 }, width = 2,
             men_alive = 1, unit_class = "com" }
  end
  local function block(uid, name, men, x, z)
    return { uid = uid, name = name, melee = false, pos = { x, 0, z }, width = 29.4, men_alive = men,
             initial_men = men, unit_class = "inf_mel" }
  end
  -- name, builder(b) -> units, enemies, values, hidden; marker; key; GREEN casts; RED casts; GREEN target offset
  local WORLDS = {
    { "FB1. Volley of High Arrows: the enemy army is only Tithe (armour 15, trash) -> ONE cast at it",
      function(b) return { caster(b, VO) }, { block(b + 5, TI, 120, 0, 150) }, { [tostring(b + 5)] = 120 }, nil end,
      "character_abilities_volley_of_high_arrows", VO, 1, 0, 5 },
    { "FB2. Volley: Tithe in sight, a HIDDEN Grave Guard block (armour 90) in the army -> no cast",
      function(b) return { caster(b, VO) }, { block(b + 5, TI, 120, 0, 150), block(b + 6, GG, 120, 200, 400) },
        { [tostring(b + 5)] = 120, [tostring(b + 6)] = 850 }, { [tostring(b + 6)] = true } end,
      "character_abilities_volley_of_high_arrows", VO, 0, 0, nil },
    { "FB3. Fireball: the enemy army is only Tithe (trash) -> ONE cast at it",
      function(b) return { caster(b, FB) }, { block(b + 5, TI, 120, 0, 150) }, { [tostring(b + 5)] = 120 }, nil end,
      "spell_bound_fireball", FB, 1, 0, 5 },
    { "FB4. Fireball: Tithe in sight, a hidden block worth 7 a soldier -> no cast",
      function(b) return { caster(b, FB) }, { block(b + 5, TI, 120, 0, 150), block(b + 6, GG, 120, 200, 400) },
        { [tostring(b + 5)] = 120, [tostring(b + 6)] = 850 }, { [tostring(b + 6)] = true } end,
      "spell_bound_fireball", FB, 0, 0, nil },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = RED196 and w[6] or w[5]
      local base = 19500 + i * 20
      local units, enemies, sv, hidden = w[2](base)
      local W = world(w[1], units, enemies, { base, w[3] }, w[4], f.path, TAG, sv, hidden)
      if W ~= nil then
        local got, last = 0, nil
        for _, x in ipairs(W.fires) do if x.key == w[4] then got = got + 1; last = x end end
        local a = (got == want)
        local tid = nil
        if last ~= nil and last.target ~= nil then pcall(function() tid = tostring(last.target:unique_ui_id()) end) end
        if a and got >= 1 and w[7] ~= nil then a = (tid == tostring(base + w[7])) end
        check(TAG .. w[1]:sub(1, 3) .. (RED196 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got, a)
        done(a)
        if TAG == "[live] " and not RED196 and got >= 1 then
          local said = count_log(W, "BLOB FALLBACK " .. w[4] .. ":")
          local why = count_log(W, "fallback: nothing better in the enemy army")
          local b5 = (said == 1 and why >= 1)
          check(TAG .. w[1]:sub(1, 3) .. "b (FB5): one BLOB FALLBACK line (" .. said .. "), the reason names it (" .. why .. ")", b5)
          done(b5)
        end
        tally(W)
      else
        done(false)
      end
    end
  end
  check("HARNESS 196: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 196 done: " .. (checks - pre196) .. " checks in this section ==")
end
