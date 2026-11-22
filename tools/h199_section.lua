-- ============================================================================
-- HARNESS 199 (round 201, user 2026-11-22, after the Dwarf battle on the release build).
--   0zz47 the round-201 tokens in both files: the five Master Rune entries are gone, the two Endless Whirlwind
--         entries exist.
--   MR1-MR4 the default M/A states, NO click: a hero owning Master Rune of Breaking / Negation / Oath & Steel / Speed
--         stands in melee -> NO cast (the mod no longer knows the key). RED: ONE cast each (the rune fired by itself,
--         what the user saw with Master Rune of Slowness on the right-hand bar).
--   EW1 Endless Whirlwind of Death, the default states, the owner in melee -> ONE cast. RED: no cast (no entry).
--   EW2 Endless Whirlwind of Death, the owner NOT in melee -> no cast (GREEN and RED).
--   EW3 Endless Whirlwind of Death Upgraded, the owner in melee -> ONE cast. RED: no cast.
--   EW4 Endless Whirlwind of Death, the owner in melee and WAVERING -> no cast (GREEN and RED).
--   RED control: H199_LIVE / H199_ANN on docs/backups/round201/pre201_*.lua.
-- ============================================================================
function run_h199()
  local L199 = os.getenv("H199_LIVE") or LIVE
  local A199 = os.getenv("H199_ANN") or ANN
  local RED199 = (os.getenv("H199_LIVE") ~= nil) or (os.getenv("H199_ANN") ~= nil)
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local EW = "wh3_dlc25_unit_abilities_whirlwind_of_death_ror"
  local EWU = "wh3_dlc25_unit_abilities_whirlwind_of_death_ror_upgraded"
  local RUNES = {
    { "MR1", "Master Rune of Breaking", "master_rune_of_breaking", "wh2_dlc17_rune_abilities_master_rune_of_breaking" },
    { "MR2", "Master Rune of Negation", "master_rune_of_negation", "wh_dlc06_rune_abilities_master_rune_of_negation" },
    { "MR3", "Master Rune of Oath & Steel", "master_rune_of_oath_and_steel", "wh_dlc06_rune_abilities_master_rune_of_oath_and_steel" },
    { "MR4", "Master Rune of Speed", "master_rune_of_speed", "wh2_dlc17_rune_abilities_master_rune_of_speed" },
    { "MR5", "Master Rune of Slowness", "master_rune_of_slowness", "wh2_dlc17_rune_abilities_master_rune_of_slowness" },
  }
  local pre199 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 199 - section 0zz47: the round-201 tokens ==")
  for _, f in ipairs({ { name = "live", path = L199 }, { name = "ann", path = A199 } }) do
    local s = read_file(f.path)
    local runes, rows = 0, 0
    for _, r in ipairs(RUNES) do
      runes = runes + cp(s, '\t{ marker = "' .. r[3] .. '", ')
      rows = rows + cp(s, '\t\t["' .. r[4] .. '"] = 3,\n')
    end
    local ew = cp(s, '\t\tkeys = { "' .. EW .. '" },\n') + cp(s, '\t\tkeys = { "' .. EWU .. '" },\n')
    local fam = cp(s, '\t{ marker = "whirlwind_of_death_ror", name = "Endless Whirlwind of Death", trigger = "melee_unwavering",\n')
    if RED199 then
      check("0zz47 " .. f.name .. " (RED): the pre-201 file has the five Master Runes (" .. runes .. " entries, " .. rows
        .. " hold rows) and no Endless Whirlwind (" .. ew .. ")", runes == 5 and rows == 5 and ew == 0 and fam == 0)
    else
      check("0zz47 " .. f.name .. ": no Master Rune entry (" .. runes .. "), no hold row (" .. rows
        .. "), the two Endless Whirlwind entries (" .. ew .. ") on melee_unwavering (" .. fam .. ")",
        runes == 0 and rows == 0 and ew == 2 and fam == 1)
    end
  end
  local FILES = { { path = A199, tag = "[annotated] " }, { path = L199, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function casts(W, key)
    local n = 0
    for _, x in ipairs(W.fires) do if x.key == key then n = n + 1 end end
    for _, x in ipairs(W.ground_fires or {}) do if x.key == key then n = n + 1 end end
    return n
  end
  -- the DEFAULT M/A states (no click): what a player gets who never touches a letter
  local function mk(wname, uid, key, o, PATH, TAG)
    local c = { name = CASTER, uid = uid, owns = { key }, melee = false, dist = 30, width = 2, men_alive = 1,
                unit_class = "com", hp_frac = 1.0 }
    for k, v in pairs(o or {}) do c[k] = v end
    local W = make_world({ can_perform = true, units = { c }, enemies = {},
      cards = { { id = tostring(uid), state = "active", vis = true } }, bar = { { id = "b1", key = key } } })
    W.defaults_on = true
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    W.conflict = true
    return W
  end
  local function verdict(TAG, id, text, ok)
    check(TAG .. id .. (RED199 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  local function world(TAG, P, id, wname, uid, key, o, want, want_red)
    local W = mk(id .. ". " .. wname, uid, key, o, P, TAG)
    if W == nil then done(false); return end
    polln(W, 6)
    local n = casts(W, key)
    local w = want
    if RED199 then w = want_red end
    verdict(TAG, id .. "a", w .. " cast(s) expected, got " .. n, n == w)
    tally(W)
  end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    for i = 1, 4 do
      local r = RUNES[i]
      world(TAG, P, r[1], r[2] .. ": the default states, the owner in melee -> no cast (the key left the mod)",
        19920 + i, r[4], { melee = true, dist = 5 }, 0, 1)
    end
    world(TAG, P, "EW1", "Endless Whirlwind of Death: the default states, the owner in melee -> ONE cast",
      19931, EW, { melee = true, dist = 5 }, 1, 0)
    world(TAG, P, "EW2", "Endless Whirlwind of Death: the owner not in melee -> no cast",
      19932, EW, { melee = false, dist = 60 }, 0, 0)
    world(TAG, P, "EW3", "Endless Whirlwind of Death Upgraded: the owner in melee -> ONE cast",
      19933, EWU, { melee = true, dist = 5 }, 1, 0)
    world(TAG, P, "EW4", "Endless Whirlwind of Death: the owner in melee and wavering -> no cast",
      19934, EW, { melee = true, dist = 5, wavering = true }, 0, 0)
  end
  check("HARNESS 199: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 199 done: " .. (checks - pre199) .. " checks in this section ==")
end
