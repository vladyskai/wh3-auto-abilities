-- ============================================================================
-- HARNESS 188 (round 189): THE LINE OF FIRE (user ruling 2026-11-21: "I would just do the check for terrain on all
--   35 and units on all 35. Just let's be safe, and if it doesn't fire, that's okay. ... It's better for the mod if
--   it doesn't fire."). The 35 entries the game marks 'Requires line of sight to the target' cast only along a line
--   clear of every other unit (ours and the enemy's) and of the ground.
--   0zz37 the generated key text equals the game data (56 keys), the eg_class_ok hook, the poll's eg_caster / eg_los,
--         the load loop's ability.los, the test-only global is never assigned by the mod.
--   LS0   at load, exactly the entries with a tagged key carry los = true (35; Focused Shot yes, Gaze of Nagash no).
--   LS1   Focused Shot, flat ground, nothing between -> ONE cast.
--   LS2   our Swordsmen stand across the line (the Wulfhart field case) -> no cast (RED: a cast).
--   LS3   an enemy unit stands across the line -> no cast (RED: a cast).
--   LS4   a 4 m ridge crosses the line -> no cast (RED: a cast).
--   LS5   the caster on a 20 m hill, our Swordsmen below across the line -> ONE cast (the line passes over them).
--   LS6   our Swordsmen 40 m beside the line -> ONE cast.
--   LS7   an enemy unit flying 40 m up across the line -> ONE cast (the line passes under it).
--   LS8   bm:get_terrain_height missing -> no cast and the one-per-battle log line (fail-closed; RED: a cast).
--   LS9   the ground read 10 m off the target's height -> no cast and its log line (RED: a cast).
--   LS10  two Vampires, the first behind our Swordsmen -> ONE cast, at the second (RED: at the first).
--   RED control: H188_LIVE / H188_ANN on docs/backups/round189/pre189_*.lua.
-- ============================================================================
function run_h188()
  local L188 = os.getenv("H188_LIVE") or LIVE
  local A188 = os.getenv("H188_ANN") or ANN
  local RED188 = (os.getenv("H188_LIVE") ~= nil) or (os.getenv("H188_ANN") ~= nil)
  local FS = "wh2_dlc13_lord_abilities_kill_shot"
  local CASTER = "wh2_dlc13_emp_cha_markus_wulfhart_0"
  local VA = "wh_main_vmp_cha_vampire_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local ZO = "wh_main_vmp_inf_zombie"
  local TSV = "C:/Users/vlady/Desktop/WH3_mod/gamedata/wh3/uieff/unit_abilities_to_ui_effects_juncs.tsv"
  local pre188 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  -- the game's own set, read from the extract
  local game = {}
  local n_game = 0
  for line in read_file(TSV):gmatch("[^\n]+") do
    local k, eff = line:match("^([^\t]+)\t([^\t\r]+)")
    if eff == "wh3_main_projectile_requires_line_of_sight" and not game[k] then game[k] = true; n_game = n_game + 1 end
  end
  print("== HARNESS 188 - section 0zz37: the round-189 tokens ==")
  for _, f in ipairs({ { name = "live", path = L188 }, { name = "ann", path = A188 } }) do
    local s = read_file(f.path)
    local text = s:match('\nFOURTH%.LOS_TEXT = "([^"]*)"')
    local n_txt, off = 0, 0
    if text ~= nil then
      for k in text:gmatch("[^;]+") do n_txt = n_txt + 1; if not game[k] then off = off + 1 end end
    end
    local ok = text ~= nil and n_txt == n_game and n_game == 56 and off == 0
      and cp(s, "\tif not FOURTH.eg_los_ok(enemy) then return false end   -- ROUND 189") == 1
      and cp(s, "\t\t\t\t\tFOURTH.eg_caster = unit   -- ROUND 189") == 1
      and cp(s, "\t\t\t\t\tFOURTH.eg_los = (ability.los == true)") == 1
      and cp(s, "\tability.los = FOURTH.entry_los(ability)") == 1
      and cp(s, "\nfunction FOURTH.los_block(caster, enemy)\n") == 1
      and cp(s, "return bm:get_terrain_height(x, z)") == 1
      and cp(s, "ZZ_AUTO_TEST_NO_LOS = ") == 0
    if RED188 then
      check("0zz37 " .. f.name .. " (RED): the pre-189 file has no line-of-fire check", not ok and text == nil)
    else
      check("0zz37 " .. f.name .. ": LOS_TEXT = the game's " .. n_game .. " keys (" .. n_txt .. " in the text, " .. off
        .. " not the game's), the eg_class_ok hook, eg_caster / eg_los, ability.los, the test global never set", ok)
    end
  end
  local FILES = { { path = A188, tag = "[annotated] " }, { path = L188, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  -- ground(x, z): nil -> no bm:get_terrain_height at all
  local function world(wname, units, enemies, ground, PATH, TAG)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = FS } } })
    W.defaults_on = false
    W.los_on = true
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    if ground ~= nil then
      W.bm.get_terrain_height = function(self, x, z) return ground(x, z) end
    else
      W.bm.get_terrain_height = nil
    end
    OH77.cap = nil
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    W.cap = OH77.cap
    deploy_phases(W); ui(W)
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        pr.unit.is_visible_to_alliance = function(self, a) return true end
        pr.unit.is_currently_flying = function(self) return false end
        pr.unit.strategic_value = function(self) return 1500 end
      end
    end
    sel_event(W, units[1].uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_focused_shot"); ui(W)
    sel_event(W, units[1].uid, false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  local function flat(x, z) return 0 end
  local function caster(b, dist, y)
    return { name = CASTER, uid = b, owns = { FS }, melee = false, dist = dist, pos = { 0, y or 0, 0 }, width = 2,
             men_alive = 1, unit_class = "com" }
  end
  local function vampire(uid, dist, x)
    return { uid = uid, name = VA, melee = false, pos = { x or 0, 0, dist }, width = 2, men_alive = 1, initial_men = 1,
             unit_class = "com", dist = dist }
  end
  local function block(uid, name, x, y, z)
    return { uid = uid, name = name, owns = {}, melee = false, pos = { x, y, z }, width = 30, men_alive = 100,
             initial_men = 100, unit_class = "inf_mel", dist = math.sqrt(x * x + z * z) }
  end
  local function casts(W)
    local n = 0
    for _, x in ipairs(W.fires) do if x.key == FS then n = n + 1 end end
    for _, x in ipairs(W.ground_fires or {}) do if x.key == FS then n = n + 1 end end
    return n
  end
  local function first_target(W)
    for _, x in ipairs(W.fires) do
      if x.key == FS and x.target ~= nil then
        local ok, id = pcall(function() return x.target:unique_ui_id() end)
        if ok then return id end
      end
    end
    return nil
  end
  local function logged(W, tok)
    for _, l in ipairs(W.log_lines) do if raw_find(l, tok, 1, true) ~= nil then return true end end
    return false
  end
  -- one world: name, units, enemies, ground, the expected casts (GREEN, RED), an extra test
  -- logx: the extra test reads the log, which only the live copy writes (the reading copy is log-free)
  local function run(TAG, PATH, id, wname, units, enemies, ground, want, want_red, extra, logx)
    local W = world(id .. ". " .. wname, units, enemies, ground, PATH, TAG)
    if W == nil then done(false); return end
    local w = RED188 and want_red or want
    local a = (casts(W) == w)
    if a and extra ~= nil and not RED188 and (logx ~= true or TAG == "[live] ") then a = extra(W) end
    check(TAG .. id .. "a: " .. w .. " cast(s) expected, got " .. casts(W)
      .. (RED188 and " (RED: the pre-189 file)" or ""), a)
    done(a)
    tally(W)
  end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    -- LS0 + LS1 on one load
    local W = world("LS1. Focused Shot, flat ground, nothing between -> ONE cast", { caster(18801, 150) },
      { vampire(18805, 150) }, flat, P, TAG)
    if W ~= nil then
      local n, bad, fs, gz = 0, {}, nil, nil
      local tag = {}
      for _, e in ipairs(W.cap or {}) do
        local want = false
        for _, k in ipairs(e.keys or {}) do if game[k] then want = true end end
        if want then n = n + 1 end
        if (e.los == true) ~= want then bad[#bad + 1] = tostring(e.marker) end
        if e.marker == "focused_shot" then fs = e.los end
        if e.marker == "spell_bound_gaze_of_nagash" then gz = e.los end
      end
      local a
      if RED188 then
        a = (fs == nil)
        check(TAG .. "LS0 (RED): the pre-189 entries carry no los flag", a)
      else
        a = (n == 35 and #bad == 0 and fs == true and gz == false)
        check(TAG .. "LS0: the " .. n .. " entries with a tagged key carry los = true, no other (off " .. #bad
          .. (#bad > 0 and (": " .. bad[1]) or "") .. "); Focused Shot " .. tostring(fs) .. ", Gaze of Nagash "
          .. tostring(gz), a)
      end
      done(a)
      local b = (casts(W) == 1)
      check(TAG .. "LS1a: 1 cast expected on a clear line, got " .. casts(W), b)
      done(b)
      tally(W)
    end
    run(TAG, P, "LS2", "our Swordsmen stand across the line 75 m out (the Wulfhart field case) -> no cast",
      { caster(18811, 150), block(18812, SW, 0, 0, 75) }, { vampire(18815, 150) }, flat, 0, 1,
      function(W) return logged(W, "LINE OF FIRE BLOCKED to " .. VA .. ": a unit of ours (" .. SW .. ")") end, true)
    run(TAG, P, "LS3", "an enemy unit stands across the line -> no cast",
      { caster(18821, 150) }, { vampire(18825, 150), block(18826, ZO, 0, 0, 75) }, flat, 0, 1,
      function(W) return logged(W, "a unit of enemy (" .. ZO .. ")") end, true)
    run(TAG, P, "LS4", "a 4 m ridge crosses the line 70-80 m out -> no cast",
      { caster(18831, 150) }, { vampire(18835, 150) },
      function(x, z) if z >= 70 and z <= 80 then return 4 end return 0 end, 0, 1,
      function(W) return logged(W, ": the ground rises across the line") end, true)
    run(TAG, P, "LS5", "the caster on a 20 m hill, our Swordsmen below across the line -> ONE cast",
      { caster(18841, 150, 20), block(18842, SW, 0, 0, 100) }, { vampire(18845, 150) },
      function(x, z) if z <= 2 then return 20 end if z >= 30 then return 0 end return 20 - (z - 2) * 20 / 28 end, 1, 1)
    run(TAG, P, "LS6", "our Swordsmen 40 m beside the line -> ONE cast",
      { caster(18851, 150), block(18852, SW, 40, 0, 75) }, { vampire(18855, 150) }, flat, 1, 1)
    run(TAG, P, "LS7", "an enemy unit flying 40 m up across the line -> ONE cast",
      { caster(18861, 150) }, { vampire(18865, 150), block(18866, ZO, 0, 40, 75) }, flat, 1, 1)
    run(TAG, P, "LS8", "bm:get_terrain_height missing -> no cast (fail-closed)",
      { caster(18871, 150) }, { vampire(18875, 150) }, nil, 0, 1,
      function(W) return logged(W, "LINE OF FIRE: bm:get_terrain_height() is unreadable") end, true)
    run(TAG, P, "LS9", "the ground read 10 m off the target's height -> no cast",
      { caster(18881, 150) }, { vampire(18885, 150) }, function(x, z) return 10 end, 0, 1,
      function(W) return logged(W, "LINE OF FIRE: the ground read is 10.0 m off") end, true)
    run(TAG, P, "LS10", "two Vampires, the first behind our Swordsmen -> ONE cast, at the second",
      { caster(18891, 150), block(18892, SW, 0, 0, 75) }, { vampire(18895, 150), vampire(18896, 150, 100) }, flat, 1, 1,
      function(W)
        local t = first_target(W)
        if RED188 then return t ~= nil end
        return t == 18896
      end)
  end
  check("HARNESS 188: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 188 done: " .. (checks - pre188) .. " checks in this section ==")
end
