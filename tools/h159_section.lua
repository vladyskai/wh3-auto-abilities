-- ============================================================================
-- HARNESS 159 (round 160): the Beastmen-battle fixes (user ruling 2026-11-16).
--   JR1 Jagged Dagger (when_ready) on a ROUTING caster -> no cast.
--   JR2 Jagged Dagger on a steady caster -> ONE cast (control).
--   IN1 Apocalyptic Vision + Burp of Grom (both INSTANT) on one unit in melee -> BOTH cast within 1 s (one poll apart).
--   IN2 Death Frenzy (3 s wind-up, first in the table walk) + Whirl of Weeping Blades (instant) in melee -> ONE cast
--       within 1 s: a wind-up still holds the unit (control).
--   RED (pre-160 = round 159): JR1 casts, IN1 casts only one.
-- ============================================================================
function run_h159()
  local L159 = os.getenv("H159_LIVE") or LIVE
  local A159 = os.getenv("H159_ANN") or ANN
  local RED159 = (os.getenv("H159_LIVE") ~= nil) or (os.getenv("H159_ANN") ~= nil)
  local JD = "wh_dlc03_item_abilities_jagged_dagger"
  local BG = "wh2_dlc15_character_abilities_burp_of_grom_0"
  local AV = "wh_dlc03_character_abilities_apocalyptic_vision"
  local DF = "wh2_dlc16_spell_bound_death_frenzy"
  local WW = "wh2_dlc14_weapon_abilities_whirl_of_weeping_blades"
  local CASTER = "wh_dlc03_bst_cha_beastlord_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local pre159 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 159 - section 0zz7: the round-160 tokens ==")
  if not RED159 then
    for _, f in ipairs({ { name = "live", path = L159 }, { name = "ann", path = A159 } }) do
      local s = read_file(f.path)
      check("0zz7 " .. f.name .. ": the instant hold is one poll, when_ready skips a routing unit",
        raw_find(s, "FOURTH.SERIAL_INSTANT_HOLD_SECONDS = POLL_MS / 1000", 1, true) ~= nil
        and raw_find(s, "if ability.wind_up_s == nil then\n\t\t\t\t\t\tunit_hold_s = FOURTH.SERIAL_INSTANT_HOLD_SECONDS", 1,
          true) ~= nil
        and cp(s, "FOURTH.SERIAL_MIN_HOLD_SECONDS = 2.5") == 1)
    end
  end

  local FILES = { { path = A159, tag = "[annotated] " }, { path = L159, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, unit, enemies, markers, keys, PATH, TAG)
    local cards = { { id = tostring(unit.uid), state = "active", vis = true } }
    local bar = {}
    for i, k in ipairs(keys) do bar[#bar + 1] = { id = "b" .. i, key = k } end
    local W = make_world({ can_perform = true, units = { unit }, enemies = enemies, cards = cards, bar = bar })
    W.defaults_on = false
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, unit.uid, true); ui(W); ui(W)
    for _, m in ipairs(markers) do click(W, "zz_auto_badge_" .. m); ui(W) end
    sel_event(W, unit.uid, false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  local function caster(b, keys, o)
    local c = { name = CASTER, uid = b, owns = keys, melee = false, dist = 60, pos = { 0, 0, 0 }, width = 2,
                men_alive = 1, unit_class = "com" }
    for k, v in pairs(o or {}) do c[k] = v end
    return c
  end
  local function foe(uid)
    return { uid = uid, name = SW, melee = true, pos = { 0, 0, -8 }, width = 29.4, men_alive = 120, initial_men = 120,
             unit_class = "inf_mel", dist = 2 }
  end
  -- name, builder(b) -> unit, enemies; markers; keys; GREEN { key = casts }; RED { key = casts } (nil = not RED)
  local WORLDS = {
    { "JR1. Jagged Dagger on a ROUTING caster -> no cast",
      function(b) return caster(b, { JD }, { routing = true }), {} end, { "jagged_dagger" }, { JD },
      { [JD] = 0 }, { [JD] = 1 } },
    { "JR2. Jagged Dagger on a steady caster -> ONE cast",
      function(b) return caster(b, { JD }), {} end, { "jagged_dagger" }, { JD }, { [JD] = 1 }, nil },
    { "IN1. Apocalyptic Vision + Burp of Grom (both instant) in melee -> BOTH cast within 1 s",
      function(b) return caster(b, { AV, BG }, { melee = true }), { foe(b + 5) } end,
      { "apocalyptic_vision", "burp_of_grom" }, { AV, BG }, { [AV] = 1, [BG] = 1 }, { [AV] = 1, [BG] = 0 } },
    { "IN2. Death Frenzy (3 s wind-up) + Whirl of Weeping Blades (instant) in melee -> ONE cast within 1 s",
      function(b) return caster(b, { DF, WW }, { melee = true }), { foe(b + 5) } end,
      { "death_frenzy", "whirl_of_weeping_blades" }, { DF, WW }, { [DF] = 1, [WW] = 0 }, nil },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[5]
      if RED159 then want = w[6] end
      if want ~= nil then
        local b = 23000 + i * 20
        local unit, enemies = w[2](b)
        local W = world(w[1], unit, enemies, w[3], w[4], f.path, TAG)
        if W ~= nil then
          local got = {}
          for _, x in ipairs(W.fires) do got[x.key] = (got[x.key] or 0) + 1 end
          local a, txt = true, ""
          local ks = {}
          for k in pairs(want) do ks[#ks + 1] = k end
          table.sort(ks)   -- a stable print order, so two runs are byte-identical
          for _, k in ipairs(ks) do
            local n = want[k]
            a = a and ((got[k] or 0) == n)
            txt = txt .. " " .. k:sub(-18) .. "=" .. tostring(got[k] or 0) .. "/" .. n
          end
          check(TAG .. w[1]:sub(1, 3) .. (RED159 and "-RED" or "") .. "a: casts (got/want)" .. txt, a)
          done(a)
          tally(W)
        end
      end
    end
  end
  if RED159 then
    check("RED CONTROL (harness 159): the pre-160 build casts while routing and holds an instant pair - " .. n_ok
      .. "/" .. n_all, n_all == 4 and n_ok == 4)
  else
    check("HARNESS 159: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 8 and n_ok == 8)
  end
  print("== HARNESS 159 done: " .. (checks - pre159) .. " checks in this section ==")
end
