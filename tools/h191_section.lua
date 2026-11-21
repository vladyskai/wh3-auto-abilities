-- ============================================================================
-- HARNESS 191 (round 192, user rulings 2026-11-21):
--   (1) "A fast enemy nearby" must be RUNNING (is_moving_fast) and CLOSING on our units (option A; "try to implement
--       using is_moving_fast()"): the gap to our nearest unit shrinks at least 3 m/s over at least 1 s.
--   (2) Grombrindal Has No Fear on melee_or_wavering_aura ("at least one ally (caster included) in range in melee or
--       wavering"), aura 55 m -> bound 38 m.
--   (3) The five spell-bar runes leave the mod ("They should not be in the mod").
--   0zz40 the round-192 tokens in both files.
--   FC1 Mither: an enemy RUNNING at us (the gap 48.5 -> 32 m, 6 m/s) -> it fires (RED: fires).
--   FC2 Mither: an enemy RUNNING past us (the gap stays 30 m) -> no cast (RED: a cast).
--   FC3 Mither: an enemy WALKING at us (moving, not running) -> no cast (RED: a cast).
--   FC4 Mither: an enemy RUNNING away (the gap 30 -> 46.5 m) -> no cast (RED: a cast at 30 m).
--   GH1 Grombrindal Has No Fear: an ally 30 m away in melee -> ONE cast (RED: no entry, no cast).
--   GH2 an ally 45 m away in melee (bound 38) -> no cast.
--   GH3 the caster itself in melee -> ONE cast (RED: none).
--   RB1 Rune of Breaking on the wheel, its caster in melee -> no cast (RED: a cast).
--   RED control: H191_LIVE / H191_ANN on docs/backups/round192/pre192_*.lua.
-- ============================================================================
function run_h191()
  local L191 = os.getenv("H191_LIVE") or LIVE
  local A191 = os.getenv("H191_ANN") or ANN
  local RED191 = (os.getenv("H191_LIVE") ~= nil) or (os.getenv("H191_ANN") ~= nil)
  local MITH = "wh2_dlc15_hero_abilities_mither"
  local GHNF = "wh_pro01_lord_passive_grombrindal_has_no_fear"
  local RB = "wh2_dlc17_rune_abilities_rune_of_breaking"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local PLAIN = "wh2_dlc09_tmb_inf_skeleton_warriors_0"
  local SC = "wh2_dlc16_hero_abilities_shock_collar"
  local OGRES = "wh2_main_skv_mon_rat_ogres"
  local pre191 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 191 - section 0zz40: the round-192 tokens ==")
  local RUNES = { '{ marker = "rune_of_breaking",', '{ marker = "rune_of_negation",', '{ marker = "rune_of_slowness",',
    '{ marker = "rune_of_speed",', '{ marker = "rune_of_oath_and_steel",' }
  for _, f in ipairs({ { name = "live", path = L191 }, { name = "ann", path = A191 } }) do
    local s = read_file(f.path)
    local head = cp(s, "-- ROUND 192 - THE FAST ENEMY MUST BE COMING AT US")
    local mps = cp(s, "FOURTH.FAST_CLOSING_MPS = 3     -- ROUND 192")
    local run = cp(s, "local ok_mf, mf = pcall(function() return enemy:is_moving_fast() end)   -- ROUND 192: really running")
    local close = cp(s, "local closing = old_rule or FOURTH.fast_closing(enemy, best)")
    local runes = 0
    for _, r in ipairs(RUNES) do runes = runes + cp(s, r) end
    local gh = cp(s, '{ marker = "grombrindal_has_no_fear", name = "Grombrindal Has No Fear", trigger = "melee_or_wavering_aura",')
    local mo = cp(s, 'if a.M and not FOURTH.class_member(unit, "moulder") then return false end')
      + cp(s, "wh2_dlc16_hero_abilities_shock_collar=M;") + cp(s, "wh2_dlc16_lord_abilities_remouldered=M;")
      + cp(s, "FOURTH.MOULDER_TEXT = \"")
    if RED191 then
      check("0zz40 " .. f.name .. " (RED): the pre-192 file has no closing rule, the 5 runes, no Grombrindal entry, no Moulder rule",
        head == 0 and mps == 0 and runes == 5 and gh == 0 and mo == 0)
    else
      check("0zz40 " .. f.name .. ": the closing rule (" .. head .. mps .. run .. close .. "), runes left " .. runes
        .. ", Grombrindal Has No Fear " .. gh .. ", the Moulder rule " .. mo,
        head == 1 and mps == 1 and run == 1 and close == 1 and runes == 0 and gh == 1 and mo == 4)
    end
  end
  local FILES = { { path = A191, tag = "[annotated] " }, { path = L191, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function casts(W, key)
    local n = 0
    for _, x in ipairs(W.fires) do if x.key == key then n = n + 1 end end
    for _, x in ipairs(W.ground_fires or {}) do if x.key == key then n = n + 1 end end
    return n
  end
  -- arm the badge, then poll; step(i) runs before poll i (it moves the gaps)
  local function world(wname, key, badge, units, enemies, PATH, TAG, polls, step)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = key } } })
    W.defaults_on = false
    W.closing_on = true
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
    for i = 1, polls do
      if step ~= nil then step(i) end
      polln(W, 1)
    end
    return W
  end
  local function run(TAG, P, id, wname, key, badge, u, e, polls, step, want, want_red)
    local W = world(id .. ". " .. wname, key, badge, u, e, P, TAG, polls, step)
    if W == nil then done(false); return end
    local w = RED191 and want_red or want
    local got = casts(W, key)
    local a = (w == "some") and (got >= 1) or (got == w)
    check(TAG .. id .. "a: " .. tostring(w) .. " cast(s) expected, got " .. got
      .. (RED191 and " (RED: the pre-192 file)" or ""), a)
    done(a)
    tally(W)
  end
  -- Mither: the caster and one enemy cavalry unit; gap(i) gives the edge gap before poll i
  local function mither(b, edef, gap)
    local c = { name = CASTER, uid = b, owns = { MITH }, melee = false, dist = gap(1) }
    local e = { name = "enemy_cavalry", uid = b + 5, melee = false, moving = true, fast = true, fast_speed = 7,
                dist = gap(1) }
    for k, v in pairs(edef or {}) do e[k] = v end
    local step = function(i) c.dist = gap(i); e.dist = gap(i) end
    return { c }, { e }, step
  end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    local u, e, st = mither(19101, nil, function(i) return 50 - 1.5 * i end)
    run(TAG, P, "FC1", "Mither: an enemy RUNNING at us (48.5 -> 32 m) -> it fires", MITH, "zz_auto_badge_mither",
      u, e, 12, st, "some", "some")
    u, e, st = mither(19111, nil, function(i) return 30 end)
    run(TAG, P, "FC2", "Mither: an enemy RUNNING past us (the gap stays 30 m) -> no cast", MITH, "zz_auto_badge_mither",
      u, e, 12, st, 0, "some")
    u, e, st = mither(19121, { fast = false }, function(i) return 50 - 1.5 * i end)
    run(TAG, P, "FC3", "Mither: an enemy WALKING at us (moving, not running) -> no cast", MITH, "zz_auto_badge_mither",
      u, e, 12, st, 0, "some")
    u, e, st = mither(19131, nil, function(i) return 30 + 1.5 * i end)
    run(TAG, P, "FC4", "Mither: an enemy RUNNING away (31.5 -> 48 m) -> no cast", MITH, "zz_auto_badge_mither",
      u, e, 12, st, 0, "some")
    -- Grombrindal Has No Fear: the caster and one ally (the mock's ally gap is the ally's dist field)
    local function gh(b, cmelee, amelee, adist)
      return { { name = CASTER, uid = b, owns = { GHNF }, melee = cmelee, dist = 80 },
               { name = PLAIN, uid = b + 1, owns = {}, melee = amelee, dist = adist } },
             { { name = PLAIN, uid = b + 5, melee = amelee, dist = 80 } }
    end
    u, e = gh(19141, false, true, 30)
    run(TAG, P, "GH1", "Grombrindal Has No Fear: an ally 30 m away in melee -> ONE cast", GHNF,
      "zz_auto_badge_grombrindal_has_no_fear", u, e, 4, nil, 1, 0)
    u, e = gh(19151, false, true, 45)
    run(TAG, P, "GH2", "Grombrindal Has No Fear: the ally in melee is 45 m away (bound 38) -> no cast", GHNF,
      "zz_auto_badge_grombrindal_has_no_fear", u, e, 4, nil, 0, 0)
    u, e = gh(19161, true, false, 30)
    run(TAG, P, "GH3", "Grombrindal Has No Fear: the caster itself in melee -> ONE cast", GHNF,
      "zz_auto_badge_grombrindal_has_no_fear", u, e, 4, nil, 1, 0)
    run(TAG, P, "RB1", "Rune of Breaking on the wheel, its caster in melee -> no cast (the rune left the mod)", RB,
      "zz_auto_badge_rune_of_breaking", { { name = CASTER, uid = 19171, owns = { RB }, melee = true, dist = 10 } },
      { { name = PLAIN, uid = 19176, melee = true, dist = 10 } }, 4, nil, 0, 1)
    -- Shock Collar (ally_wavering: the CLOSEST wavering ally): a wavering Skeleton unit at 20 m and wavering Rat Ogres
    -- at 30 m. The game's rule: Clan Moulder monsters only.
    local function sc(b, with_ogres)
      local us = { { name = CASTER, uid = b, owns = { SC }, melee = false, dist = 80 },
                   { name = PLAIN, uid = b + 1, owns = {}, melee = true, wavering = true, dist = 20 } }
      if with_ogres then us[3] = { name = OGRES, uid = b + 2, owns = {}, melee = true, wavering = true, dist = 30 } end
      return us, { { name = PLAIN, uid = b + 5, melee = true, dist = 80 } }
    end
    for _, w in ipairs({ { "SC1", true, 19182, 19181 }, { "SC2", false, nil, 19191 } }) do
      local id, ogres, want_t, red_t = w[1], w[2], w[3], w[4]
      local b = ogres and 19180 or 19190
      u, e = sc(b, ogres)
      local W = world(id .. ". Shock Collar: a wavering Skeleton unit at 20 m"
        .. (ogres and " and wavering Rat Ogres at 30 m -> cast on the Rat Ogres" or " only -> no cast"),
        SC, "zz_auto_badge_shock_collar", u, e, P, TAG, 4, nil)
      if W == nil then done(false) else
        local n, tgt = 0, nil
        for _, x in ipairs(W.fires) do
          if x.key == SC then
            n = n + 1
            if tgt == nil and x.target ~= nil then tgt = x.target.zz_uid end
          end
        end
        local wt = RED191 and red_t or want_t
        local a = (wt == nil and n == 0) or (wt ~= nil and n >= 1 and tgt == wt)
        check(TAG .. id .. "a: target " .. tostring(wt) .. " expected, got " .. n .. " cast(s) on " .. tostring(tgt)
          .. (RED191 and " (RED: the pre-192 file)" or ""), a)
        done(a)
        tally(W)
      end
    end
  end
  check("HARNESS 191: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 191 done: " .. (checks - pre191) .. " checks in this section ==")
end
