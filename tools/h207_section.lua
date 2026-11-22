-- ============================================================================
-- HARNESS 207 (round 209, the user's replies to the afternoon code review).
--   0zz55 the round-209 tokens in both files.
--   LN1 Spinning Loons armed, an enemy in melee 10 m away, one of OUR other units 50 m from the caster -> NO cast
--       (inside the fanatics' reach). RED: ONE ground cast (no friendly test at all).
--   LN2 the same, our other unit 150 m away -> ONE ground cast (GREEN and RED).
--   LN3 The Loons of Eight Peaks, our other unit 50 m away -> NO cast. RED: ONE.
--   LB1 Lamprey's Bite armed, 160 Zombies standing 60 m away -> ONE aimed ground order (a point from the vector
--       constructor, a numeric bearing), no unit-form order. RED: no cast (the 25 m disc needs 415 soldiers).
--   LB2 Lamprey's Bite, the only enemy is a single entity -> no cast (GREEN and RED).
--   PC1 a selected hero in melee owns Endless Whirlwind of Death (default A). The game reports an order for a spell the
--       mod does not know (the player's own cast) -> NO cast for 16 polls, a cast by poll 26. RED: a cast at once.
--   PC2 the same report while the hero is NOT selected -> a cast within 4 polls (GREEN and RED).
--   PC3 the report names one of the mod's own instant keys -> no window, a cast within 4 polls (GREEN and RED).
--   PC4 two selected heroes. The mod orders Eruption on the first, the game reports it back (the echo). The second then
--       enters melee -> it casts within 3 polls: the echo of the mod's own order holds nobody (GREEN and RED).
--   PC5 a selected hero in melee owns the Whirlwind. The game reports Eruption (wind-up 1 s, not ordered by the mod) ->
--       NO cast for 8 polls (1 + 2 s window), a cast by poll 16. RED: a cast at once.
--   UE1 two units. The first raises an error on its first read, the second is a hero in melee with the Whirlwind ->
--       the second casts within 4 polls. RED: no cast (the error ends the whole poll).
--   RED control: H207_LIVE / H207_ANN on docs/backups/round209/pre209_*.lua.
-- ============================================================================
function run_h207()
  local L207 = os.getenv("H207_LIVE") or LIVE
  local A207 = os.getenv("H207_ANN") or ANN
  local RED207 = (os.getenv("H207_LIVE") ~= nil) or (os.getenv("H207_ANN") ~= nil)
  local LO = "wh_main_unit_abilities_spinning_loons"
  local LE = "wh_dlc06_unit_abilities_the_loons_of_eight_peaks"
  local LAMP = "wh3_dlc24_unit_abilities_lampreys_bite"
  local EW = "wh3_dlc25_unit_abilities_whirlwind_of_death_ror"
  local ERU = "wh3_main_character_abilities_eruption"
  local SPELL = "wh_main_spell_fire_fireball"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local GOBS = "wh_main_grn_inf_night_goblins"
  local LIVING = "wh_main_emp_inf_swordsmen"
  local ZOM = "wh_main_vmp_inf_zombie"
  local pre207 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 207 - section 0zz55: the round-209 tokens ==")
  for _, f in ipairs({ { name = "live", path = L207 }, { name = "ann", path = A207 } }) do
    local s = read_file(f.path)
    local ring = cp(s, "\t\tring_clear = true,")
    local ringtab = cp(s, "\nFOURTH.RING_TEXT = \"wh_dlc06_unit_abilities_the_loons_of_eight_peaks=88;wh_main_unit_abilities_spinning_loons=88\"\n")
    local waves = cp(s, 'trigger = "enemy_wave"')
    local lamp = cp(s, "wh3_dlc24_unit_abilities_lampreys_bite=1,14.1,24,0,0,1,1")
      + cp(s, "wh3_dlc24_unit_abilities_lampreys_bite=0.1,0.5833")
    local fns = cp(s, "\nfunction FOURTH.player_cast(key)\n") + cp(s, "\nfunction FOURTH.note_own_order(key)\n")
      + cp(s, "\nfunction FOURTH.ring_wrap(f, reach)\n")
    local guard = cp(s, "\t\tlocal ok_unit, routing, ui_id, ability_key, unit_abilities = pcall(function()\n")
      + cp(s, "\t\t\t\tlocal ok_ab, res_ab = pcall(function()\n")
    local note = cp(s, "\t\t\t\t\tFOURTH.note_own_order(ready_key)")
    if RED207 then
      check("0zz55 " .. f.name .. " (RED): the pre-209 file has none of it and 32 waves",
        ring == 0 and ringtab == 0 and waves == 32 and lamp == 0 and fns == 0 and guard == 0 and note == 0)
    else
      check("0zz55 " .. f.name .. ": ring_clear on 2 entries (" .. ring .. "), the ring table (" .. ringtab .. "), " .. waves
        .. " waves, Lamprey's two table rows (" .. lamp .. "), the three functions (" .. fns .. "), the per-unit guard ("
        .. guard .. "), the own-order note (" .. note .. ")",
        ring == 2 and ringtab == 1 and waves == 33 and lamp == 2 and fns == 3 and guard == 2 and note == 1)
    end
  end
  local FILES = { { path = A207, tag = "[annotated] " }, { path = L207, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function casts(W, key)
    local u, g = 0, 0
    for _, x in ipairs(W.fires) do if x.key == key then u = u + 1 end end
    for _, x in ipairs(W.ground_fires or {}) do if x.key == key then g = g + 1 end end
    return u, g
  end
  local function verdict(TAG, id, text, ok)
    check(TAG .. id .. (RED207 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  local function enemies_seen(W, value)
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        pr.unit.is_visible_to_alliance = function(self, a) return true end
        pr.unit.is_currently_flying = function(self) return false end
        pr.unit.strategic_value = function(self) return value end
      end
    end
  end
  -- the game's report of an ability order
  local function report(W, key)
    local n = 0
    for _, h in ipairs(W.cmd_handlers or {}) do
      if h.name == "Special Ability" then
        n = n + 1
        pcall(h.fn, { get_string1 = function() return key end })
      end
    end
    return n
  end
  -- a world whose abilities are armed by a click on the first unit
  local function clicked(wname, key, marker, units, enemies, PATH, TAG, free)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = key } } })
    W.defaults_on = false
    W.free_aim_on = (free == true)
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    W.bm.get_terrain_height = function(self, x, z) return 0 end
    v = nil
    if free then v = function(x, y, z) return { vx = x, vy = y, vz = z } end end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then v = nil; tally(W); return nil end
    deploy_phases(W); ui(W)
    enemies_seen(W, 100)
    sel_event(W, units[1].uid, true); ui(W); ui(W)
    pcall(click, W, "zz_auto_badge_" .. marker); ui(W)
    sel_event(W, units[1].uid, false); ui(W)
    W.conflict = true
    return W
  end
  -- a world on the default M/A states; <selected> lists the unit ids whose card reads selected
  local function defaults(wname, key, units, selected, PATH, TAG)
    local cards, sel = {}, {}
    for _, id in ipairs(selected or {}) do sel[id] = true end
    for _, d in ipairs(units) do
      cards[#cards + 1] = { id = tostring(d.uid), state = sel[d.uid] and "selected" or "active", vis = true }
    end
    local W = make_world({ can_perform = true, units = units, enemies = {}, cards = cards, bar = { { id = "b1", key = key } } })
    W.defaults_on = true
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    for _, id in ipairs(selected or {}) do sel_event(W, id, true) end
    ui(W); ui(W)
    W.conflict = true
    return W
  end
  local function hero(uid, keys, melee)
    return { name = CASTER, uid = uid, owns = keys, melee = melee, dist = melee and 5 or 60, width = 2, men_alive = 1,
             unit_class = "com", hp_frac = 1.0 }
  end
  local function loons(TAG, P, id, wname, base, key, marker, friend_x, want, want_red)
    local units = {
      { name = GOBS, uid = base, owns = { key }, melee = false, dist = 10, pos = { 0, 0, 0 }, width = 30, men_alive = 120,
        initial_men = 120, unit_class = "inf_mel" },
      { name = LIVING, uid = base + 1, owns = {}, melee = false, dist = 60, pos = { friend_x, 0, 0 }, width = 30,
        men_alive = 120, initial_men = 120, unit_class = "inf_mel" },
    }
    local enemies = { { uid = base + 5, name = LIVING, melee = true, pos = { 0, 0, 14 }, width = 30, men_alive = 120,
                        initial_men = 120, unit_class = "inf_mel", dist = 10 } }
    local W = clicked(id .. ". " .. wname, key, marker, units, enemies, P, TAG, false)
    if W == nil then done(false); return end
    polln(W, 4)
    local u, g = casts(W, key)
    local w = want
    if RED207 then w = want_red end
    verdict(TAG, id .. "a", w .. " ground cast(s) expected, got " .. g .. " (and " .. u .. " unit-form)", g == w and u == 0)
    tally(W)
  end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    loons(TAG, P, "LN1", "Spinning Loons: an enemy in melee 10 m away, one of our other units 50 m from the caster -> no cast",
      20700, LO, "spinning_loons", 50, 0, 1)
    loons(TAG, P, "LN2", "Spinning Loons: our other unit is 150 m away -> ONE ground cast",
      20710, LO, "spinning_loons", 150, 1, 1)
    loons(TAG, P, "LN3", "The Loons of Eight Peaks: our other unit 50 m from the caster -> no cast",
      20720, LE, "loons_of_eight_peaks", 50, 0, 1)
    do
      local units = { { name = CASTER, uid = 20730, owns = { LAMP }, melee = false, dist = 60, pos = { 0, 0, 0 }, width = 2,
                        men_alive = 1, unit_class = "com", hp_frac = 1.0 } }
      local enemies = { { uid = 20735, name = ZOM, melee = false, pos = { 0, 0, 60 }, width = 30, men_alive = 160,
                          initial_men = 160, unit_class = "inf_mel", dist = 60 } }
      local W = clicked("LB1. Lamprey's Bite: 160 Zombies standing 60 m away -> ONE aimed ground order", LAMP, "lampreys_bite",
        units, enemies, P, TAG, true)
      if W ~= nil then
        polln(W, 8)
        v = nil
        local u, g = casts(W, LAMP)
        local o = nil
        for _, x in ipairs(W.ground_fires or {}) do if x.key == LAMP then o = x end end
        local good = (u == 0 and g == 1 and o ~= nil and type(o.orient) == "number" and type(o.pos) == "table"
          and o.pos.vx ~= nil and o.width == 0)
        if RED207 then good = (u + g == 0) end
        verdict(TAG, "LB1a", (RED207 and "RED: no cast, got " or "ONE aimed ground order, got ") .. g .. " ground and " .. u
          .. " unit-form" .. ((o ~= nil and not RED207) and (", bearing " .. tostring(o.orient)) or ""), good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local units = { { name = CASTER, uid = 20740, owns = { LAMP }, melee = false, dist = 60, pos = { 0, 0, 0 }, width = 2,
                        men_alive = 1, unit_class = "com", hp_frac = 1.0 } }
      local enemies = { { uid = 20745, name = CASTER, melee = false, pos = { 0, 0, 60 }, width = 2, men_alive = 1,
                          initial_men = 1, unit_class = "com", dist = 60 } }
      local W = clicked("LB2. Lamprey's Bite: the only enemy is a single entity -> no cast", LAMP, "lampreys_bite",
        units, enemies, P, TAG, true)
      if W ~= nil then
        polln(W, 8)
        v = nil
        local u, g = casts(W, LAMP)
        verdict(TAG, "LB2a", "no cast expected, got " .. (u + g), u + g == 0)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = defaults("PC1. the player's own cast of an unknown spell: the selected hero's Whirlwind waits 5 s", EW,
        { hero(20750, { EW }, true) }, { 20750 }, P, TAG)
      if W ~= nil then
        local heard = report(W, SPELL)
        polln(W, 16)
        local u1 = casts(W, EW)
        polln(W, 10)
        local u2 = casts(W, EW)
        local good = (heard == 1 and u1 == 0 and u2 >= 1)
        if RED207 then good = (u1 >= 1) end
        verdict(TAG, "PC1a", u1 .. " cast(s) in the first 16 polls (" .. (RED207 and "RED: at least 1" or "need 0") .. "), "
          .. u2 .. " by poll 26, " .. heard .. " listener(s)", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = defaults("PC2. the same report, the hero is not selected -> it casts at once", EW,
        { hero(20760, { EW }, true) }, {}, P, TAG)
      if W ~= nil then
        report(W, SPELL)
        polln(W, 4)
        local u = casts(W, EW)
        verdict(TAG, "PC2a", u .. " cast(s) within 4 polls (need at least 1)", u >= 1)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = defaults("PC3. the report names one of the mod's instant keys -> no window", EW,
        { hero(20770, { EW }, true) }, { 20770 }, P, TAG)
      if W ~= nil then
        report(W, EW)
        polln(W, 4)
        local u = casts(W, EW)
        verdict(TAG, "PC3a", u .. " cast(s) within 4 polls (need at least 1)", u >= 1)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = defaults("PC4. the echo of the mod's own Eruption holds nobody", ERU,
        { hero(20780, { ERU }, true), hero(20781, { EW }, false) }, { 20780, 20781 }, P, TAG)
      if W ~= nil then
        polln(W, 3)
        local e1 = casts(W, ERU)
        report(W, ERU)
        set_state(W, 2, { melee = true, dist = 5 })
        polln(W, 3)
        local u = casts(W, EW)
        verdict(TAG, "PC4a", "the mod ordered Eruption " .. e1 .. " time(s), then the second hero cast " .. u
          .. " time(s) within 3 polls of the echo (need at least 1 each)", e1 >= 1 and u >= 1)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = defaults("PC5. the player's own cast of Eruption (wind-up 1 s): the selected hero's Whirlwind waits 3 s", EW,
        { hero(20790, { EW }, true) }, { 20790 }, P, TAG)
      if W ~= nil then
        report(W, ERU)
        polln(W, 8)
        local u1 = casts(W, EW)
        polln(W, 8)
        local u2 = casts(W, EW)
        local good = (u1 == 0 and u2 >= 1)
        if RED207 then good = (u1 >= 1) end
        verdict(TAG, "PC5a", u1 .. " cast(s) in the first 8 polls (" .. (RED207 and "RED: at least 1" or "need 0") .. "), "
          .. u2 .. " by poll 16", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = defaults("UE1. the first unit raises an error, the second still casts", EW,
        { hero(20800, {}, false), hero(20801, { EW }, true) }, {}, P, TAG)
      if W ~= nil then
        W.mock_units[1].number_of_men_alive = function(self) error("a broken unit handle", 0) end
        polln(W, 4)
        local u = casts(W, EW)
        local good = (u >= 1)
        if RED207 then good = (u == 0) end
        verdict(TAG, "UE1a", u .. " cast(s) by the second unit within 4 polls (" .. (RED207 and "RED: 0" or "need at least 1")
          .. ")", good)
        W.mock_units[1].number_of_men_alive = function(self) return 1 end
        W.expect_poll_errors = true
        tally(W)
      else
        done(false)
      end
    end
  end
  check("HARNESS 207: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 207 done: " .. (checks - pre207) .. " checks in this section ==")
end
