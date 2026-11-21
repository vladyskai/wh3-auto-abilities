-- ============================================================================
-- HARNESS 189 (round 190): THE ANIMATION DECIDES IN EVERY SHOT TRIGGER (user 2026-11-21: "Amber Bow canceled his
--   movement, not good" -> "Fix the 8"). The 2026-11-17 ruling ("Option A, animation decides all") now reaches the shot
--   triggers that skipped the stand-still check: an animated cast waits for its caster to stand still; a cast without
--   an animation still fires on the move.
--   0zz38 the 7 ROUND 190 lines in both files; the old 'if still and not FOURTH.blob_still' line is gone.
--   AB1   Amber Bow (animated), Markus WALKING, armoured infantry at 60 m -> no cast (RED: a cast: the field case).
--   AB2   Amber Bow, Markus standing -> ONE cast.
--   AB3   Hunting Spear (same trigger, no animation), its caster walking -> ONE cast (unchanged).
--   BT1   The Black Tongue (animated, enemy_spellcaster), caster walking, a Vampire at 40 m -> no cast (RED: a cast).
--   BT2   The Black Tongue, caster standing -> ONE cast.
--   RED control: H189_LIVE / H189_ANN on docs/backups/round190/pre190_*.lua.
-- ============================================================================
function run_h189()
  local L189 = os.getenv("H189_LIVE") or LIVE
  local A189 = os.getenv("H189_ANN") or ANN
  local RED189 = (os.getenv("H189_LIVE") ~= nil) or (os.getenv("H189_ANN") ~= nil)
  local AB = "wh2_dlc13_weapon_abilities_amber_bow"
  local HS = "wh_dlc03_weapon_abilities_hunting_spear"
  local BT = "wh3_dlc27_character_abilities_the_black_tongue"
  local CASTER = "wh2_dlc13_emp_cha_markus_wulfhart_0"
  local SQ = "wh_dlc07_brt_inf_foot_squires_0"
  local VA = "wh_main_vmp_cha_vampire_0"
  local TAG190 = "   -- ROUND 190: the animation decides (Amber Bow stopped a walking Markus)"
  local pre189 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 189 - section 0zz38: the round-190 tokens ==")
  for _, f in ipairs({ { name = "live", path = L189 }, { name = "ann", path = A189 } }) do
    local s = read_file(f.path)
    local n = cp(s, TAG190)
    local old = cp(s, "\tif still and not FOURTH.blob_still(unit) then return false end")
    if RED189 then
      check("0zz38 " .. f.name .. " (RED): the pre-190 file has no ROUND 190 line and keeps the old one", n == 0 and old == 1)
    else
      check("0zz38 " .. f.name .. ": " .. n .. " ROUND 190 lines (want 7), the old 'still and' line gone (" .. old .. ")",
        n == 7 and old == 0)
    end
  end
  local FILES = { { path = A189, tag = "[annotated] " }, { path = L189, tag = "[live] " } }
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
  local function caster(b, key, moving, dist)
    return { name = CASTER, uid = b, owns = { key }, melee = false, dist = dist, pos = { 0, 0, 0 }, width = 2,
             men_alive = 1, unit_class = "com", moving = moving }
  end
  local function squires(uid)
    return { uid = uid, name = SQ, melee = false, pos = { 0, 0, 60 }, width = 34, men_alive = 120, initial_men = 120,
             unit_class = "inf_mel", dist = 60 }
  end
  local function vampire(uid)
    return { uid = uid, name = VA, melee = false, pos = { 0, 0, 40 }, width = 2, men_alive = 1, initial_men = 1,
             unit_class = "com", dist = 40 }
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
    local w = RED189 and want_red or want
    local a = (casts(W, key) == w)
    check(TAG .. id .. "a: " .. w .. " cast(s) expected, got " .. casts(W, key)
      .. (RED189 and " (RED: the pre-190 file)" or ""), a)
    done(a)
    tally(W)
  end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    run(TAG, P, "AB1", "Amber Bow, Markus WALKING, armoured infantry at 60 m -> no cast", AB,
      "zz_auto_badge_weapon_abilities_amber_bow", { caster(18901, AB, true, 60) }, { squires(18905) }, 0, 1)
    run(TAG, P, "AB2", "Amber Bow, Markus standing -> ONE cast", AB,
      "zz_auto_badge_weapon_abilities_amber_bow", { caster(18911, AB, false, 60) }, { squires(18915) }, 1, 1)
    run(TAG, P, "AB3", "Hunting Spear (no animation), its caster walking -> ONE cast", HS,
      "zz_auto_badge_hunting_spear", { caster(18921, HS, true, 60) }, { squires(18925) }, 1, 1)
    run(TAG, P, "BT1", "The Black Tongue, caster WALKING, a Vampire at 40 m -> no cast", BT,
      "zz_auto_badge_the_black_tongue", { caster(18931, BT, true, 40) }, { vampire(18935) }, 0, 1)
    run(TAG, P, "BT2", "The Black Tongue, caster standing -> ONE cast", BT,
      "zz_auto_badge_the_black_tongue", { caster(18941, BT, false, 40) }, { vampire(18945) }, 1, 1)
  end
  check("HARNESS 189: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 189 done: " .. (checks - pre189) .. " checks in this section ==")
end
