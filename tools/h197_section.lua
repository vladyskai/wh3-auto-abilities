-- ============================================================================
-- HARNESS 197 (round 198, user 2026-11-22, the overnight review: "fix" on rows 1, 2, 3, 6, 7, 8, 11).
--   0zz44 the round-198 tokens in both files.
--   SW1 THE SERIAL WINDOW: Primeval Roar (4.5 s wind-up) fires, fires AGAIN after its recharge, and only then the
--       hero comes under fire (The Golden Eye of Tzeentch). GREEN: the Eye waits out the Roar's window (20+ polls).
--       RED: the Eye is issued on the very next poll (the repeat armed no window: it replaces the Roar).
--   FP1 THE ENTRY RESET: a hero below 15% (Tz'arkan) is the LAST unit of the poll; then an enemy centre comes under
--       the Sky-junk between two polls and the fast pass tries the bomb. GREEN: the bomb drops. RED: the fast pass
--       inherits Tz'arkan's self slot ("the caster is above 15%"), holds the bomb and locks it.
--   GG1 Get Tha Gitz! (3 uses), an enemy in melee in range for 20 s -> ONE cast. RED: more than one.
--   SL1 The Rock of Inevitability: a fast enemy RUNNING PAST inside the aura (the gap stays 15 m) -> no cast. RED: fires.
--   SL2 The Rock: a fast enemy RUNNING AT us (38 -> 12 m) -> it fires.
--   SL3 The Rock: a fast enemy WALKING at us -> no cast. RED: fires.
--   GA1 Shield of Aeons: a fast enemy WALKING PAST inside the aura -> no cast. RED: fires.
--   GA2 Shield of Aeons: a fast enemy RUNNING AT us -> it fires.
--   NS1 Favour of the Fay: the caster in melee, no ally in melee -> no cast. RED: ONE cast on itself.
--   NS2 Favour of the Fay: the caster and an ally in melee -> ONE cast ON THE ALLY. RED: on itself.
--   NS3 Shielding Swarm: the caster under fire, no ally under fire or in melee -> no cast. RED: ONE cast on itself.
--   NS4 Shielding Swarm: the caster and an ally under fire -> ONE cast ON THE ALLY. RED: on itself.
--   NS5 the three cards say "ally" only.
--   BG3 Bugman's XXXXXX: at 60% with the nearest enemy 45 m away -> no cast. RED: ONE cast (the game refuses it).
--   RED control: H197_LIVE / H197_ANN on docs/backups/round198/pre198_*.lua.
-- ============================================================================
function run_h197()
  local L197 = os.getenv("H197_LIVE") or LIVE
  local A197 = os.getenv("H197_ANN") or ANN
  local RED197 = (os.getenv("H197_LIVE") ~= nil) or (os.getenv("H197_ANN") ~= nil)
  local PR = "wh2_dlc17_unit_abilities_primeval_roar"
  local GE = "wh3_dlc24_item_abilities_the_golden_eye_of_tzeentch"
  local TZ = "wh2_dlc14_lord_abilities_tzarkan"
  local DFA = "wh2_dlc09_unit_abilities_death_from_above"
  local GTG = "wh3_dlc23_hero_abilities_get_tha_gitz!"
  local ROCK = "wh3_main_item_abilities_the_rock_of_inevitability"
  local SA = "wh2_dlc13_item_abilities_shield_of_aeons"
  local FAY = "wh_dlc07_lord_abilities_favour_of_the_fay"
  local SS = "wh3_dlc29_hero_active_dispatch_the_swarm_protect"
  local BG = "wh3_dlc26_item_abilities_bugmans_xxxxxx"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local SWD = "wh_main_emp_inf_swordsmen"
  local pre197 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 197 - section 0zz44: the round-198 tokens ==")
  for _, f in ipairs({ { name = "live", path = L197 }, { name = "ann", path = A197 } }) do
    local s = read_file(f.path)
    local reset = cp(s, "\nfunction FOURTH.entry_reset(ability, unit)\n")
    local calls = cp(s, "FOURTH.entry_reset(ability, unit)")
    local win = cp(s, "\t\t\t\t\tcast_gate.unit_marker[ui_id] = nil\n")
    local hold = cp(s, '\t\t["wh3_dlc23_hero_abilities_get_tha_gitz!"] = 120,\n')
    local necro = cp(s, '\t\t["wh3_dlc29_vmp_cha_necromancer_undeath_nightmare"] = true,')
    local aura = cp(s, "-- ROUND 198: the round-192 read (RUNNING and CLOSING on our units), then inside the aura")
    local noself = cp(s, "\t\tno_self = true,")
    local bug = cp(s, "\nFOURTH.BUGMAN_CLEAR_M = 55 ")
    if RED197 then
      check("0zz44 " .. f.name .. " (RED): the pre-198 file has none of the round's tokens",
        reset == 0 and calls == 0 and win == 0 and hold == 0 and necro == 0 and aura == 0 and noself == 0 and bug == 0)
    else
      check("0zz44 " .. f.name .. ": the entry reset (" .. reset .. ", " .. calls .. " = 1 definition + the poll + the fast pass), "
        .. "the window (" .. win .. "), the hold row (" .. hold .. "), the Necromancer (" .. necro .. "), the two auras ("
        .. aura .. "), no_self (" .. noself .. "), Bugman's 55 m (" .. bug .. ")",
        reset == 1 and calls == 3 and win == 1 and hold == 1 and necro == 1 and aura == 2 and noself == 3 and bug == 1)
    end
  end
  local FILES = { { path = A197, tag = "[annotated] " }, { path = L197, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function casts(W, key)
    local n, last = 0, nil
    for _, x in ipairs(W.fires) do if x.key == key then n = n + 1; last = x end end
    for _, x in ipairs(W.ground_fires or {}) do if x.key == key then n = n + 1 end end
    return n, last
  end
  local function tid(x)
    local id = nil
    if x ~= nil and x.target ~= nil then pcall(function() id = tostring(x.target:unique_ui_id()) end) end
    return id
  end
  -- arm = { { uid, marker }, ... }; keys = the bar's keys; opt.closing = the round-192 closing rule is live
  local function mk(wname, units, enemies, keys, arm, PATH, TAG, opt)
    opt = opt or {}
    local cards, bar = {}, {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    for i, k in ipairs(keys) do bar[i] = { id = "b" .. i, key = k } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies or {}, cards = cards, bar = bar })
    W.defaults_on = false
    W.closing_on = (opt.closing == true)
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
        pr.unit.is_currently_flying = function(self) return false end
        pr.unit.strategic_value = function(self) return 1500 end
      end
    end
    if opt.after_load ~= nil then opt.after_load(W) end
    for _, a in ipairs(arm) do
      sel_event(W, a[1], true); ui(W); ui(W)
      click(W, "zz_auto_badge_" .. a[2]); ui(W)
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
    check(TAG .. id .. (RED197 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    -- SW1: the serial window
    do
      local h = hero(19701, { PR, GE }, { melee = true, dist = 5, missile = false })
      local W = mk("SW1. Primeval Roar twice in a row, then the hero comes under fire", { h }, {}, { PR, GE },
        { { 19701, "primeval_roar" }, { 19701, "the_golden_eye_of_tzeentch" } }, P, TAG)
      if W ~= nil then
        local p2 = nil
        for i = 1, 900 do
          polln(W, 1)
          if casts(W, PR) >= 2 then p2 = i; break end
        end
        local early = casts(W, GE)
        local gap = nil
        if p2 ~= nil then
          h.missile = true
          for i = 1, 80 do
            polln(W, 1)
            if casts(W, GE) >= 1 then gap = i; break end
          end
        end
        local ok
        if RED197 then
          ok = (p2 ~= nil and early == 0 and gap ~= nil and gap <= 2)
        else
          ok = (p2 ~= nil and early == 0 and gap ~= nil and gap >= 20)
        end
        verdict(TAG, "SW1a", "the Roar's second cast at poll " .. tostring(p2) .. ", the Eye " .. tostring(gap)
          .. " poll(s) later (" .. (RED197 and "RED: 2 or fewer, it replaces the Roar" or "need 20 or more: the window") .. ")", ok)
        tally(W)
      else
        done(false)
      end
    end
    -- FP1: the fast pass after a poll whose last entry left its slots set
    do
      local st = { r = 20 }
      local gy = { name = "sky_junk", uid = 19711, owns = { DFA }, melee = false }
      local hz = hero(19712, { TZ }, { hp_frac = 0.10 })
      local en = { name = "wh_main_inf_zombie_0", uid = 19715, men_alive = 20, pos = { 20, 0, 0 }, ordered = { 20, 0, 0 } }
      local W = mk("FP1. the fast pass after a poll that ended on Tz'arkan's hero", { gy, hz }, { en }, { DFA, TZ },
        { { 19711, "death_from_above" }, { 19712, "tzarkan" } }, P, TAG, { after_load = function(W)
          local u = unit_of(W, 19711)
          if u ~= nil then u.is_currently_flying = function() return true end end
          for i = 1, #(W.enemy_entries or {}) do
            local eo = W.enemy_entries[i].unit
            eo.position = function() return h118_cvec(st.r, 0) end
            eo.ordered_position = function() return h118_cvec(st.r, 0) end
          end
        end })
      if W ~= nil then
        polln(W, 2)
        local before = casts(W, DFA)
        local tz = casts(W, TZ)
        st.r = 3
        h118_fastn(W, 1)
        local after, last = casts(W, DFA)
        local ok
        if RED197 then
          ok = (before == 0 and tz >= 1 and after == 0)
        else
          ok = (before == 0 and tz >= 1 and after == 1 and tid(last) == "19711")
        end
        verdict(TAG, "FP1a", "no bomb while the enemy is 20 m off (" .. before .. "), Tz'arkan cast (" .. tz
          .. "), then ONE fast tick with the centre 3 m away: " .. after .. " bomb(s)"
          .. (RED197 and " (RED: held by the inherited slot)" or ", on the Sky-junk itself (" .. tostring(tid(last)) .. ")"), ok)
        tally(W)
      else
        done(false)
      end
    end
    -- GG1: Get Tha Gitz!, 3 uses
    do
      local h = hero(19721, { GTG }, { melee = true, dist = 20, dist_by_target = { [19725] = 20 } })
      local W = mk("GG1. Get Tha Gitz! (3 uses), an enemy in melee 20 m away for 20 s", { h },
        { block(19725, { melee = true, dist = 20 }) }, { GTG }, { { 19721, "get_tha_gitz" } }, P, TAG)
      if W ~= nil then
        polln(W, 80)
        local n = casts(W, GTG)
        local ok = (RED197 and n >= 2) or (not RED197 and n == 1)
        verdict(TAG, "GG1a", n .. " cast(s) in 20 s (" .. (RED197 and "RED: more than one" or "need exactly 1: one use per recharge") .. ")", ok)
        tally(W)
      else
        done(false)
      end
    end
    -- the two auras: caster + one enemy cavalry unit; gap(i) is the edge gap before poll i
    local function aura(id, wname, key, marker, base, edef, gap, want, want_red)
      local c = hero(base, { key }, { dist = gap(1) })
      local e = { name = "enemy_cavalry", uid = base + 5, melee = false, moving = true, fast = true, fast_speed = 7,
                  dist = gap(1), men_alive = 60, initial_men = 60 }
      for k, v in pairs(edef or {}) do e[k] = v end
      local W = mk(id .. ". " .. wname, { c }, { e }, { key }, { { base, marker } }, P, TAG, { closing = true })
      if W == nil then done(false); return end
      for i = 1, 14 do
        c.dist = gap(i); e.dist = gap(i)
        polln(W, 1)
      end
      local n = casts(W, key)
      local w = RED197 and want_red or want
      local ok = (w == "some" and n >= 1) or (w == 0 and n == 0)
      verdict(TAG, id .. "a", tostring(w) .. " cast(s) expected, got " .. n, ok)
      tally(W)
    end
    aura("SL1", "The Rock: a fast enemy RUNNING PAST inside the aura (15 m all along) -> no cast", ROCK,
      "the_rock_of_inevitability", 19731, nil, function(i) return 15 end, 0, "some")
    aura("SL2", "The Rock: a fast enemy RUNNING AT us (38 -> 12 m) -> it fires", ROCK,
      "the_rock_of_inevitability", 19741, nil, function(i) return 40 - 2 * i end, "some", "some")
    aura("SL3", "The Rock: a fast enemy WALKING at us (38 -> 12 m) -> no cast", ROCK,
      "the_rock_of_inevitability", 19751, { fast = false }, function(i) return 40 - 2 * i end, 0, "some")
    aura("GA1", "Shield of Aeons: a fast enemy WALKING PAST inside the aura -> no cast", SA,
      "shield_of_aeons", 19761, { fast = false }, function(i) return 15 end, 0, "some")
    aura("GA2", "Shield of Aeons: a fast enemy RUNNING AT us (38 -> 12 m) -> it fires", SA,
      "shield_of_aeons", 19771, nil, function(i) return 40 - 2 * i end, "some", "some")
    -- no self arm: caster + one ally
    local function noself(id, wname, key, marker, base, cdef, adef, want, want_red, on_ally)
      local W = mk(id .. ". " .. wname, { hero(base, { key }, cdef), block(base + 1, adef) }, {}, { key },
        { { base, marker } }, P, TAG)
      if W == nil then done(false); return nil end
      polln(W, 4)
      local n, last = casts(W, key)
      local w = RED197 and want_red or want
      local ok = (n == w)
      local t = tid(last)
      if ok and n >= 1 and on_ally then
        if RED197 then ok = (t == tostring(base)) else ok = (t == tostring(base + 1)) end
      end
      verdict(TAG, id .. "a", w .. " cast(s) expected, got " .. n .. (n >= 1 and (", on unit " .. tostring(t)) or ""), ok)
      return W
    end
    local W1 = noself("NS1", "Favour of the Fay: the caster in melee, no ally in melee -> no cast", FAY, "favour_of_the_fay",
      19781, { melee = true, dist = 5 }, { dist = 20 }, 0, 1, false)
    if W1 ~= nil then
      local by = {}
      for _, e in ipairs(W1.cap or {}) do by[e.marker] = e.card end
      local c_ok = by.favour_of_the_fay == "Fires on the nearest ally in melee"
        and by.dispatch_the_swarm_protect == "Fires on an ally under fire, else on an ally in melee"
        and by.dispatch_the_swarm_protect_upgraded == "Fires on an ally under fire, else on an ally in melee"
        and by.terrorgheist_skull == "Fires on itself or the nearest ally in melee"
      verdict(TAG, "NS5", "the three cards say ally only, Terrorgheist Skull keeps its card (Favour: "
        .. tostring(by.favour_of_the_fay) .. ")", (RED197 and not c_ok) or (not RED197 and c_ok))
      tally(W1)
    end
    local W2 = noself("NS2", "Favour of the Fay: the caster and an ally 20 m away in melee -> ONE cast on the ally", FAY,
      "favour_of_the_fay", 19791, { melee = true, dist = 5 }, { melee = true, dist = 20 }, 1, 1, true)
    if W2 ~= nil then tally(W2) end
    local W3 = noself("NS3", "Shielding Swarm: the caster under fire, the ally idle -> no cast", SS,
      "dispatch_the_swarm_protect", 19801, { missile = true }, { dist = 20 }, 0, 1, false)
    if W3 ~= nil then tally(W3) end
    local W4 = noself("NS4", "Shielding Swarm: the caster and an ally under fire -> ONE cast on the ally", SS,
      "dispatch_the_swarm_protect", 19811, { missile = true }, { missile = true, dist = 20 }, 1, 1, true)
    if W4 ~= nil then tally(W4) end
    -- BG3: Bugman's keep-out distance
    do
      local h = hero(19821, { BG }, { hp_frac = 0.6, health_percent = 60, dist_by_target = { [19825] = 45 } })
      local W = mk("BG3. Bugman's XXXXXX: at 60% with the nearest enemy 45 m away -> no cast", { h },
        { block(19825) }, { BG }, { { 19821, "bugmans_xxxxxx" } }, P, TAG)
      if W ~= nil then
        polln(W, 4)
        local n = casts(W, BG)
        local ok = (RED197 and n == 1) or (not RED197 and n == 0)
        verdict(TAG, "BG3a", n .. " cast(s) (" .. (RED197 and "RED: 1, inside the game's 55 m" or "need 0") .. ")", ok)
        tally(W)
      else
        done(false)
      end
    end
  end
  check("HARNESS 197: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 197 done: " .. (checks - pre197) .. " checks in this section ==")
end
