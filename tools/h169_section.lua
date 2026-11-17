-- ============================================================================
-- HARNESS 169 (round 170): POTION OF FOOLHARDINESS ON charge_or_wavering (user ruling 2026-11-17, after a test with two
--   Empire Captains: the armed potion fired only at contact).
--   0zz18 the entry rides charge_or_wavering with start_armed; the default rule reads start_armed.
--   PF1 the captain charging (running at its target 20 m away, not in melee), armed by a click -> ONE cast.
--   PF2 the captain wavering, not charging, not in melee -> ONE cast.
--   PF3 the captain in melee, steady, not charging -> no cast (the old trigger fired here).
--   PF4 NO click (family defaults on): the captain charging -> ONE cast (it still starts armed).
--   PF5 the card reads 'Fires when charging or wavering'.
--   RED (pre-170 = round 169): PF1, PF2, PF4 no cast; PF3 one cast; the card is the in-melee one.
-- ============================================================================
function run_h169()
  local L169 = os.getenv("H169_LIVE") or LIVE
  local A169 = os.getenv("H169_ANN") or ANN
  local RED169 = (os.getenv("H169_LIVE") ~= nil) or (os.getenv("H169_ANN") ~= nil)
  local PF = "wh_main_item_abilities_potion_of_foolhardiness"
  local CAP = "wh_main_emp_cha_captain_2"
  local pre169 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 169 - section 0zz18: the round-170 tokens ==")
  if not RED169 then
    for _, f in ipairs({ { name = "live", path = L169 }, { name = "ann", path = A169 } }) do
      local s = read_file(f.path)
      check("0zz18 " .. f.name .. ": Foolhardiness on charge_or_wavering, start_armed, the default rule reads it",
        cp(s, '{ marker = "potion_of_foolhardiness", name = "Potion of Foolhardiness", trigger = "charge_or_wavering",') == 1
        and cp(s, "\t\tstart_armed = true,\n") == 1
        and cp(s, "or ability.start_armed == true)   -- ROUND 170") == 1)
    end
  end

  local FILES = { { path = A169, tag = "[annotated] " }, { path = L169, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, d, clicks, defaults, PATH, TAG)
    d.name = CAP
    d.owns = { PF }
    local W = make_world({ can_perform = true, units = { d },
      cards = { { id = tostring(d.uid), state = "active", vis = true } }, bar = { { id = "b1", key = PF } } })
    W.defaults_on = defaults
    print("== " .. TAG .. wname .. " ==")
    OH77.cap = nil
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    W.cap = OH77.cap
    deploy_phases(W); ui(W)
    sel_event(W, d.uid, true); ui(W); ui(W)
    for _ = 1, clicks do click(W, "zz_auto_badge_potion_of_foolhardiness"); ui(W) end
    sel_event(W, d.uid, false); ui(W)
    W.conflict = true
    polln(W, 2)
    return W
  end
  -- name, unit def, clicks, defaults on, GREEN casts, RED casts
  local WORLDS = {
    { "PF1. Foolhardiness, the captain CHARGING (20 m, not in melee), armed by a click -> ONE cast",
      { uid = 34001, fast = true, melee = false, target = true, dist = 20, wavering = false }, 1, false, 1, 0 },
    { "PF2. Foolhardiness, the captain WAVERING, not charging, not in melee -> ONE cast",
      { uid = 34021, fast = false, melee = false, wavering = true }, 1, false, 1, 0 },
    { "PF3. Foolhardiness, the captain in melee, steady, not charging -> no cast",
      { uid = 34041, fast = false, melee = true, wavering = false }, 1, false, 0, 1 },
    { "PF4. Foolhardiness, NO click (defaults on), the captain CHARGING -> ONE cast (it still starts armed)",
      { uid = 34061, fast = true, melee = false, target = true, dist = 20, wavering = false }, 0, true, 1, 0 },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = RED169 and w[6] or w[5]
      local W = world(w[1], w[2], w[3], w[4], f.path, TAG)
      if W ~= nil then
        local got = 0
        for _, x in ipairs(W.fires) do if x.key == PF then got = got + 1 end end
        local a = (got == want)
        check(TAG .. w[1]:sub(1, 3) .. (RED169 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got, a)
        done(a)
        if i == 1 then
          local card = nil
          for _, e in ipairs(W.cap or {}) do if e.marker == "potion_of_foolhardiness" then card = e.card end end
          local c_ok = (card == "Fires when charging or wavering")
          check(TAG .. "PF5: the card (" .. tostring(card) .. ")", (RED169 and not c_ok) or (not RED169 and c_ok))
          done((RED169 and not c_ok) or (not RED169 and c_ok))
        end
        tally(W)
      end
    end
  end
  if RED169 then
    check("RED CONTROL (harness 169): the pre-170 potion waits for melee - " .. n_ok .. "/" .. n_all,
      n_all == 10 and n_ok == 10)
  else
    check("HARNESS 169: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 10 and n_ok == 10)
  end
  print("== HARNESS 169 done: " .. (checks - pre169) .. " checks in this section ==")
end
