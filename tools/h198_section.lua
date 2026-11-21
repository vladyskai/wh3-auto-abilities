-- ============================================================================
-- HARNESS 198 (round 199, user 2026-11-22, the overnight review's second replies).
--   0zz46 the round-199 tokens in both files.
--   KB1 Doom & Darkness (gunnery school): the game's key has a capital B. The button is claimed, the badge click arms
--       it, an enemy in melee in range -> ONE cast. RED: no badge, no cast.
--   AA1 Spite of Da Bad Moon: the caster (900) and an ally (1,500) in melee -> ONE cast ON THE ALLY. RED: on the caster.
--   AA2 Spite: the caster (1,500) and an ally (900) in melee -> ONE cast on the caster (GREEN and RED).
--   AA3 Spite: the caster idle, an ally in melee -> ONE cast on the ally. RED: no cast.
--   AA4 Wild Abandon (ally only): the caster in melee, no ally in melee -> no cast. RED: ONE cast on the caster.
--   AA5 Wild Abandon: the caster (1,500) and an ally (900) in melee -> ONE cast on the ally. RED: on the caster.
--   AA6 the cards: Spite ends ", or on a more valuable ally in melee", Wild Abandon "Fires on the most valuable ally in melee".
--   IN1 Assault of Stone: the only enemy in melee is a Varghulf the engine calls infantry -> no cast. RED: ONE cast.
--   IN2 Assault of Stone: Swordsmen in melee -> ONE cast (GREEN and RED).
--   IN3 Assault of Stone: flying "infantry" in melee -> no cast. RED: ONE cast.
--   RS1 two units of ONE type own Primeval Roar, both in melee, a click arms the first -> only the FIRST casts, and the
--       file holds the type's line. RED: both cast (the click flipped the untouched unit too).
--   RS2 the NEXT battle (a fresh load, the same file), no click -> BOTH cast (GREEN and RED).
--   RED control: H198_LIVE / H198_ANN on docs/backups/round199/pre199_*.lua.
-- ============================================================================
function run_h198()
  local L198 = os.getenv("H198_LIVE") or LIVE
  local A198 = os.getenv("H198_ANN") or ANN
  local RED198 = (os.getenv("H198_LIVE") ~= nil) or (os.getenv("H198_ANN") ~= nil)
  local DD = "wh3_dlc25_spell_Bound_doom_and_darkness_gunnery_school"
  local SP = "wh_dlc06_lord_abilities_spite_of_da_bad_moon"
  local WA = "wh3_dlc26_lord_abilities_wild_abandon"
  local AS = "wh2_dlc10_item_bound_assault_of_stone"
  local PR = "wh2_dlc17_unit_abilities_primeval_roar"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local SWD = "wh_main_emp_inf_swordsmen"
  local VARG = "wh_main_vmp_mon_varghulf"
  local FILE = "h198_remember_test.txt"
  local pre198 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 198 - section 0zz46: the round-199 tokens ==")
  for _, f in ipairs({ { name = "live", path = L198 }, { name = "ann", path = A198 } }) do
    local s = read_file(f.path)
    local cap = cp(s, "if candidate == listed_key or candidate == FOURTH.KEY_LOWER[listed_key] then")
    local wrap = cp(s, "\nfunction FOURTH.ally_arm_wrap(f, ally_only)\n")
    local arms = cp(s, "\t\tally_value_arm = true,")
    local only = cp(s, '\t\tally_value_arm = "only",')
    local inf = cp(s, "\tif t199 ~= nil and FOURTH.class_keys.large[t199] == true then return false end\n")
    local nxt = cp(s, "a.remember_next")
    if RED198 then
      check("0zz46 " .. f.name .. " (RED): the pre-199 file has none of the round's tokens",
        cap == 0 and wrap == 0 and arms == 0 and only == 0 and inf == 0 and nxt == 0)
    else
      check("0zz46 " .. f.name .. ": the capital key (" .. cap .. "), the ally arm (" .. wrap .. ", " .. arms .. " + " .. only
        .. " entries), the infantry test (" .. inf .. "), remember_next (" .. nxt .. ")",
        cap == 1 and wrap == 1 and arms == 8 and only == 2 and inf == 1 and nxt >= 8)
    end
  end
  local FILES = { { path = A198, tag = "[annotated] " }, { path = L198, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function casts(W, key, uid)
    local n, last = 0, nil
    for _, x in ipairs(W.fires) do
      if x.key == key and (uid == nil or x.uid == uid) then n = n + 1; last = x end
    end
    for _, x in ipairs(W.ground_fires or {}) do
      if x.key == key and (uid == nil or x.uid == uid) then n = n + 1 end
    end
    return n, last
  end
  local function tid(x)
    local id = nil
    if x ~= nil and x.target ~= nil then pcall(function() id = tostring(x.target:unique_ui_id()) end) end
    return id
  end
  -- arm = { { uid, marker }, ... }; opt.values = { [uid] = strategic value }; opt.file = the remember file
  local function mk(wname, units, enemies, keys, arm, PATH, TAG, opt)
    opt = opt or {}
    local cards, bar = {}, {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    for i, k in ipairs(keys) do bar[i] = { id = "b" .. i, key = k } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies or {}, cards = cards, bar = bar })
    W.defaults_on = false
    if opt.file ~= nil then
      W.remember_on = true
      W.remember_file = opt.file
    end
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
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
        if pr.unit.is_currently_flying == nil then pr.unit.is_currently_flying = function(self) return false end end
        pr.unit.strategic_value = function(self) return 1500 end
      end
    end
    for uid, v in pairs(opt.values or {}) do
      local u = unit_of(W, uid)
      if u ~= nil then u.strategic_value = function(self) return v end end
    end
    if opt.after_load ~= nil then opt.after_load(W) end
    for _, a in ipairs(arm) do
      sel_event(W, a[1], true); ui(W); ui(W)
      pcall(click, W, "zz_auto_badge_" .. a[2]); ui(W)
      sel_event(W, a[1], false); ui(W)
    end
    W.conflict = true
    return W
  end
  local function hero(uid, owns, o)
    local c = { name = CASTER, uid = uid, owns = owns, melee = false, dist = 30, width = 2, men_alive = 1,
                unit_class = "com", hp_frac = 1.0 }
    for k, v in pairs(o or {}) do c[k] = v end
    return c
  end
  local function block(uid, o)
    local a = { name = SWD, uid = uid, owns = {}, melee = false, men_alive = 120, initial_men = 120, unit_class = "inf_mel" }
    for k, v in pairs(o or {}) do a[k] = v end
    return a
  end
  local function verdict(TAG, id, text, ok)
    check(TAG .. id .. (RED198 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  os.remove(FILE)
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    -- KB1: the key with a capital letter
    do
      local h = hero(19901, { DD }, { dist = 20, dist_by_target = { [19905] = 20 } })
      local W = mk("KB1. Doom & Darkness (gunnery school, a capital B in the game's key), an enemy in melee 20 m away",
        { h }, { block(19905, { melee = true, dist = 20 }) }, { DD }, { { 19901, "doom_and_darkness_gunnery_school" } }, P, TAG)
      if W ~= nil then
        polln(W, 4)
        local n = casts(W, DD)
        local ok = (RED198 and n == 0) or (not RED198 and n == 1)
        verdict(TAG, "KB1a", n .. " cast(s) (" .. (RED198 and "RED: 0, the button is never claimed" or "need 1") .. ")", ok)
        tally(W)
      else
        done(false)
      end
    end
    -- the ally arm: caster + one ally; want = casts, who = "ally" / "self" / nil
    local function arm(id, wname, key, marker, base, cdef, adef, vals, want, who, want_red, who_red)
      local W = mk(id .. ". " .. wname, { hero(base, { key }, cdef), block(base + 1, adef) }, {}, { key },
        { { base, marker } }, P, TAG, { values = { [base] = vals[1], [base + 1] = vals[2] } })
      if W == nil then done(false); return nil end
      polln(W, 4)
      local n, last = casts(W, key)
      local w, wh = want, who
      if RED198 then w, wh = want_red, who_red end
      local t = tid(last)
      local ok = (n == w)
      if ok and n >= 1 then
        if wh == "ally" then ok = (t == tostring(base + 1)) else ok = (t == tostring(base)) end
      end
      verdict(TAG, id .. "a", w .. " cast(s) expected" .. (wh and (" on the " .. wh) or "") .. ", got " .. n
        .. (n >= 1 and (" on unit " .. tostring(t)) or ""), ok)
      return W
    end
    local M, I = { melee = true, dist = 5 }, { dist = 20 }
    local W1 = arm("AA1", "Spite of Da Bad Moon: the caster (900) and an ally (1,500) in melee -> on the ally", SP,
      "spite_of_da_bad_moon", 19911, M, { melee = true, dist = 20 }, { 900, 1500 }, 1, "ally", 1, "self")
    if W1 ~= nil then
      local by = {}
      for _, e in ipairs(W1.cap or {}) do by[e.marker] = e.card end
      local tail = ", or on a more valuable ally in melee"
      local s1, s2 = tostring(by.spite_of_da_bad_moon), tostring(by.cash_cascade)
      local c_ok = s1:sub(-#tail) == tail and s2:sub(-#tail) == tail
        and by.wild_abandon == "Fires on the most valuable ally in melee"
        and by.undeath_sulekhim_hand_of_dust == "Fires on the most valuable ally in melee"
        and by.primeval_roar == "Fires in melee unless wavering"
      verdict(TAG, "AA6", "the cards (Spite: " .. s1 .. " | Wild Abandon: " .. tostring(by.wild_abandon) .. ")",
        (RED198 and not c_ok) or (not RED198 and c_ok))
      tally(W1)
    end
    local W2 = arm("AA2", "Spite: the caster (1,500) and an ally (900) in melee -> on the caster", SP,
      "spite_of_da_bad_moon", 19921, M, { melee = true, dist = 20 }, { 1500, 900 }, 1, "self", 1, "self")
    if W2 ~= nil then tally(W2) end
    local W3 = arm("AA3", "Spite: the caster idle, an ally in melee -> on the ally", SP,
      "spite_of_da_bad_moon", 19931, I, { melee = true, dist = 20 }, { 1500, 900 }, 1, "ally", 0, nil)
    if W3 ~= nil then tally(W3) end
    local W4 = arm("AA4", "Wild Abandon (ally only): the caster in melee, no ally in melee -> no cast", WA,
      "wild_abandon", 19941, M, { dist = 20 }, { 1500, 900 }, 0, nil, 1, "self")
    if W4 ~= nil then tally(W4) end
    local W5 = arm("AA5", "Wild Abandon: the caster (1,500) and an ally (900) in melee -> on the ally", WA,
      "wild_abandon", 19951, M, { melee = true, dist = 20 }, { 1500, 900 }, 1, "ally", 1, "self")
    if W5 ~= nil then tally(W5) end
    -- the infantry test: one bombardment caster, one enemy in melee
    local function inf(id, wname, base, edef, flying, want, want_red)
      local h = hero(base, { AS }, { dist = 20, dist_by_target = { [base + 5] = 20 } })
      local e = block(base + 5, { melee = true, dist = 20 })
      for k, v in pairs(edef or {}) do e[k] = v end
      local W = mk(id .. ". " .. wname, { h }, { e }, { AS }, { { base, "assault_of_stone" } }, P, TAG, { after_load = function(W)
        for i = 1, #(W.enemy_entries or {}) do
          local eo = W.enemy_entries[i].unit
          eo.is_infantry = function() return true end
          eo.is_currently_flying = function() return flying == true end
        end
      end })
      if W == nil then done(false); return end
      polln(W, 4)
      local n = casts(W, AS)
      local w = RED198 and want_red or want
      verdict(TAG, id .. "a", w .. " cast(s) expected, got " .. n, n == w)
      tally(W)
    end
    inf("IN1", "Assault of Stone: a Varghulf the engine calls infantry, in melee -> no cast", 19961,
      { name = VARG, men_alive = 1, initial_men = 1 }, false, 0, 1)
    inf("IN2", "Assault of Stone: Swordsmen in melee -> ONE cast", 19971, nil, false, 1, 1)
    inf("IN3", "Assault of Stone: flying 'infantry' in melee -> no cast", 19981, nil, true, 0, 1)
    -- the remembered choice: two units of one type
    do
      os.remove(FILE)
      local function pair(b)
        return { hero(b, { PR }, { melee = true, dist = 5 }), hero(b + 1, { PR }, { melee = true, dist = 5 }) }
      end
      local W = mk("RS1. two units of one type own Primeval Roar, a click arms the first", pair(19991), {}, { PR },
        { { 19991, "primeval_roar" } }, P, TAG, { file = FILE })
      if W ~= nil then
        polln(W, 4)
        local a, b = casts(W, PR, 19991), casts(W, PR, 19992)
        local line = ""
        local fh = io.open(FILE, "r")
        if fh ~= nil then line = fh:read("*a") or ""; fh:close() end
        local file_ok = (line == CASTER .. " primeval_roar A\n")
        local ok
        if RED198 then ok = (a == 1 and b == 1 and file_ok) else ok = (a == 1 and b == 0 and file_ok) end
        verdict(TAG, "RS1a", "the clicked unit casts (" .. a .. "), the untouched unit of the same type: " .. b
          .. (RED198 and " (RED: 1, the click flipped it)" or " (need 0)") .. ", the file holds the type's line ("
          .. tostring(file_ok) .. ")", ok)
        tally(W)
      else
        done(false)
      end
      local W2 = mk("RS2. the next battle, the same file, no click", pair(19995), {}, { PR }, {}, P, TAG, { file = FILE })
      if W2 ~= nil then
        polln(W2, 4)
        local a, b = casts(W2, PR, 19995), casts(W2, PR, 19996)
        verdict(TAG, "RS2a", "both units start armed and cast (" .. a .. ", " .. b .. ")", a == 1 and b == 1)
        tally(W2)
      else
        done(false)
      end
      os.remove(FILE)
    end
  end
  check("HARNESS 198: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 198 done: " .. (checks - pre198) .. " checks in this section ==")
end
