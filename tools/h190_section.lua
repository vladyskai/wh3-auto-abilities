-- ============================================================================
-- HARNESS 190 (round 191): THE ANIMATION DECIDES IN GROUP 1 OF THE STAND-STILL AUDIT (user 2026-11-21: "For now,
--   please only implement number 1."). The 8 triggers that fire at an enemy somewhere else now wait for an animated
--   caster to stand still; a cast without an animation still fires on the move.
--   0zz39 the ROUND 191 block in both files: the trigger set (8 names), the wrapper, the load-loop wrap.
--   OF1   Oil Flask (animated, enemy_engaged_or_shot), caster WALKING, an enemy in melee at 20 m -> no cast (RED: a cast).
--   OF2   Oil Flask, caster standing -> ONE cast.
--   AC1   Accusation (same trigger, no animation), caster walking -> ONE cast (unchanged).
--   CC1   Celestial Comet (animated, enemy_ground_melee_infantry), caster WALKING, infantry in melee at 60 m -> no cast
--         (RED: a cast).
--   CC2   Celestial Comet, caster standing -> ONE cast.
--   RED control: H190_LIVE / H190_ANN on docs/backups/round191/pre191_*.lua.
-- ============================================================================
function run_h190()
  local L190 = os.getenv("H190_LIVE") or LIVE
  local A190 = os.getenv("H190_ANN") or ANN
  local RED190 = (os.getenv("H190_LIVE") ~= nil) or (os.getenv("H190_ANN") ~= nil)
  local OF = "wh2_dlc13_lord_abilities_oil_flask"
  local ACC = "wh_main_hero_abilities_accusation"
  local CC = "wh3_main_mount_bound_celestial_comet"
  local SQ = "wh_dlc07_brt_inf_foot_squires_0"
  local pre190 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 190 - section 0zz39: the round-191 tokens ==")
  local NAMES = { "enemy_ground_melee_infantry = true", "enemy_ground_melee = true", "enemy_engaged_or_shot = true",
    "enemy_melee = true", "enemy_fast_near_ally = true", "enemy_melee_or_fast = true",
    "enemy_melee_noncommander = true", "enemy_missile_shooting = true" }
  for _, f in ipairs({ { name = "live", path = L190 }, { name = "ann", path = A190 } }) do
    local s = read_file(f.path)
    local set = cp(s, "FOURTH.STILL_GATE_TRIGGERS = {")
    local wrap = cp(s, "\t\tif not FOURTH.blob_still(unit) then return nil end   -- ROUND 191: a moving caster waits")
    local loop = cp(s, "\t\tability.evaluate = FOURTH.still_wrap(ability.evaluate)   -- ROUND 191: the animation decides (group 1)")
    if RED190 then
      check("0zz39 " .. f.name .. " (RED): the pre-191 file has no ROUND 191 block", set == 0 and wrap == 0 and loop == 0)
    else
      local names = 0
      local i0 = raw_find(s, "FOURTH.STILL_GATE_TRIGGERS = {", 1, true)
      local i1 = i0 and raw_find(s, "}\n", i0, true)
      local body = (i0 and i1) and s:sub(i0, i1) or ""
      for _, t in ipairs(NAMES) do if raw_find(body, t, 1, true) ~= nil then names = names + 1 end end
      local trues = cp(body, " = true")
      check("0zz39 " .. f.name .. ": the set (" .. set .. "), its 8 triggers (" .. names .. "/" .. trues
        .. "), the wrapper (" .. wrap .. "), the load-loop wrap (" .. loop .. ")",
        set == 1 and names == 8 and trues == 8 and wrap == 1 and loop == 1)
    end
  end
  local FILES = { { path = A190, tag = "[annotated] " }, { path = L190, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, key, badge, units, enemies, PATH, TAG)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = key } } })
    W.defaults_on = false
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
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
    click(W, badge); ui(W)
    sel_event(W, units[1].uid, false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  local function caster(b, name, key, moving, dist)
    return { name = name, uid = b, owns = { key }, melee = false, dist = dist, pos = { 0, 0, 0 }, width = 2,
             men_alive = 1, unit_class = "com", moving = moving }
  end
  local function fighting(uid, dist)
    return { uid = uid, name = SQ, melee = true, pos = { 0, 0, dist }, width = 34, men_alive = 120, initial_men = 120,
             unit_class = "inf_mel", dist = dist }
  end
  local function casts(W, key)
    local n = 0
    for _, x in ipairs(W.fires) do if x.key == key then n = n + 1 end end
    for _, x in ipairs(W.ground_fires or {}) do if x.key == key then n = n + 1 end end
    return n
  end
  local function run(TAG, P, id, wname, key, badge, u, e, want, want_red)
    local W = world(id .. ". " .. wname, key, badge, u, e, P, TAG)
    if W == nil then done(false); return end
    local w = RED190 and want_red or want
    local a = (casts(W, key) == w)
    check(TAG .. id .. "a: " .. w .. " cast(s) expected, got " .. casts(W, key)
      .. (RED190 and " (RED: the pre-191 file)" or ""), a)
    done(a)
    tally(W)
  end
  local HUNT = "wh2_dlc13_emp_cha_huntsmarshal_0"
  local HERO = "wh_main_emp_cha_witch_hunter_0"
  local WIZ = "wh3_main_cth_cha_astromancer_0"
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    run(TAG, P, "OF1", "Oil Flask, caster WALKING, an enemy in melee at 20 m -> no cast", OF,
      "zz_auto_badge_oil_flask", { caster(19001, HUNT, OF, true, 20) }, { fighting(19005, 20) }, 0, 1)
    run(TAG, P, "OF2", "Oil Flask, caster standing -> ONE cast", OF,
      "zz_auto_badge_oil_flask", { caster(19011, HUNT, OF, false, 20) }, { fighting(19015, 20) }, 1, 1)
    run(TAG, P, "AC1", "Accusation (no animation), caster walking -> ONE cast", ACC,
      "zz_auto_badge_accusation", { caster(19021, HERO, ACC, true, 20) }, { fighting(19025, 20) }, 1, 1)
    run(TAG, P, "CC1", "Celestial Comet, caster WALKING, infantry in melee at 60 m -> no cast", CC,
      "zz_auto_badge_celestial_comet", { caster(19031, WIZ, CC, true, 60) }, { fighting(19035, 60) }, 0, 1)
    run(TAG, P, "CC2", "Celestial Comet, caster standing -> ONE cast", CC,
      "zz_auto_badge_celestial_comet", { caster(19041, WIZ, CC, false, 60) }, { fighting(19045, 60) }, 1, 1)
  end
  check("HARNESS 190: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 190 done: " .. (checks - pre190) .. " checks in this section ==")
end
