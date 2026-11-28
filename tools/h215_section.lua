-- ============================================================================
-- HARNESS 215 (round 217, tuning: the two costs the round-216 battle left. No cast decision changes).
--   0zz63 the round-217 tokens in both files.
--   GW1 the dial is found. Two units are selected together, each owns a DIFFERENT ability of ours (a group's wheel
--       shows neither). GREEN: the rest of the HUD is never entered. RED: it is (the 39 wasted walks of the battle).
--   GW2 the dial is found. Two units are selected together, BOTH own the same ability and its button sits outside the
--       dial: the whole HUD follows and the button is claimed (GREEN and RED).
--   CR1 three units, the game accepted the selection callbacks, no event has arrived yet: the unit-card reads in 40
--       UI ticks. GREEN: at most 30% of one read per card and tick. RED: 90% or more.
--   CR2 the game has NO selection API: the cards are read on every tick (GREEN and RED), and a selection only the
--       card reports gets its letter within 2 ticks.
--   RED control: H215_LIVE / H215_ANN on docs/backups/round217/pre217_*.lua.
-- ============================================================================
function run_h215()
  local L215 = os.getenv("H215_LIVE") or LIVE
  local A215 = os.getenv("H215_ANN") or ANN
  local RED215 = (os.getenv("H215_LIVE") ~= nil) or (os.getenv("H215_ANN") ~= nil)
  local EW = "wh3_dlc25_unit_abilities_whirlwind_of_death_ror"
  local ERU = "wh3_main_character_abilities_eruption"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local BADGE = "zz_auto_badge_whirlwind_of_death_ror"
  local pre215 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 215 - section 0zz63: the round-217 tokens ==")
  for _, f in ipairs({ { name = "live", path = L215 }, { name = "ann", path = A215 } }) do
    local s = read_file(f.path)
    local got = cp(s, "\nfunction FOURTH.walk_group_waiting()\n") + cp(s, "\t\twaiting = FOURTH.walk_group_waiting()")
      + cp(s, "cast_gate.sel_registered = true") + cp(s, "and cast_gate.sel_registered ~= true then return true end")
    if RED215 then
      check("0zz63 " .. f.name .. " (RED): the pre-217 file has none of it", got == 0)
    else
      check("0zz63 " .. f.name .. ": the group rule and the registration flag, each defined once and used once (" .. got .. " of 4)", got == 4)
    end
  end
  local FILES = { { path = A215, tag = "[annotated] " }, { path = L215, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function verdict(TAG, id, text, ok)
    check(TAG .. id .. (RED215 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  local function mk(wname, base, owners, PATH, TAG, o)
    local units, cards = {}, {}
    for i = 1, #owners do
      units[i] = { name = CASTER, uid = base + i, owns = owners[i] or {}, melee = false, dist = 60, width = 2,
                   men_alive = 1, unit_class = "com", hp_frac = 1.0 }
      cards[i] = { id = tostring(base + i), state = "active", vis = true }
    end
    local opts = { can_perform = true, units = units, enemies = {}, cards = cards, bar = {}, no_sel_api = o.no_sel_api }
    if o.where == "wheel" then opts.wheel = { { id = "button_ability1", key = EW, vis = true } } end
    if o.where == "bar" then opts.bar = { { id = "b1", key = EW } } end
    local W = make_world(opts)
    W.defaults_on = true
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    W.orders = W.hud_battle._kids[1]
    W.dial = W.orders._kids[1]
    -- the test build's inventory sweep walks the mock's whole tree once, on the first UI tick
    W.inv = (TAG == "[live] ") and 1 or 0
    if o.dial_found then
      local root = core:get_ui_root()
      local old_find = root.Find
      root.Find = function(self, what, a)
        if what == "SA_dial" then return W.dial end
        return old_find(self, what, a)
      end
    end
    W.card_reads = 0
    for i = 1, #owners do
      local c = W.card_comps[tostring(base + i)]
      if c ~= nil and c.CurrentState ~= nil then
        local old = c.CurrentState
        c.CurrentState = function(self, ...)
          W.card_reads = W.card_reads + 1
          return old(self, ...)
        end
      end
    end
    deploy_phases(W)
    return W
  end
  local function ticks(W, n) for _ = 1, n do ui(W) end end
  local function clear_of_net(W) while W.ui_calls % 100 > 80 or W.ui_calls % 100 < 2 do ui(W) end end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    do
      local W = mk("GW1. a group whose units own different abilities", 21700, { { EW }, { ERU } }, P, TAG, { dial_found = true })
      if W ~= nil then
        ticks(W, 3); clear_of_net(W)
        sel_group(W, { 21701, 21702 })
        ticks(W, 6)
        local asked = W.orders._c.childcount - W.inv
        local good = (asked == 0)
        if RED215 then good = (asked >= 1) end
        verdict(TAG, "GW1a", "the rest of the HUD was entered " .. asked .. " time(s) ("
          .. (RED215 and "RED: at least 1" or "need 0") .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("GW2. a group whose units own the same ability, its button outside the dial", 21710, { { EW }, { EW } }, P, TAG,
        { dial_found = true, where = "wheel" })
      if W ~= nil then
        ticks(W, 3); clear_of_net(W)
        sel_group(W, { 21711, 21712 })
        ticks(W, 2)
        local asked = W.orders._c.childcount - W.inv
        local claimed = false
        for _, l in ipairs(W.log_lines) do
          if raw_find(l, "found: whirlwind_of_death_ror", 1, true) ~= nil then claimed = true end
        end
        if TAG ~= "[live] " then claimed = true end   -- the reading copy does not log
        verdict(TAG, "GW2a", "the whole HUD was walked by 2 ticks after the group selection (entered " .. asked
          .. " time(s), need at least 1) and the button was claimed (" .. tostring(claimed) .. ")", asked >= 1 and claimed)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("CR1. the callbacks are registered, no event yet", 21720, { { EW }, { EW }, { EW } }, P, TAG, { where = "bar" })
      if W ~= nil then
        ticks(W, 4)
        W.card_reads = 0
        ticks(W, 40)
        local reads = W.card_reads
        local share = reads / 120
        local good = (reads > 0 and share <= 0.30)
        if RED215 then good = (share >= 0.90) end
        verdict(TAG, "CR1a", reads .. " card reads in 40 ticks on 3 cards (" .. string.format("%.0f%%", share * 100) .. " of every tick, "
          .. (RED215 and "RED: 90% or more" or "need at most 30%") .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("CR2. no selection API in this game", 21730, { { EW }, { EW }, { EW } }, P, TAG, { where = "bar", no_sel_api = true })
      if W ~= nil then
        ticks(W, 4)
        W.card_reads = 0
        ticks(W, 40)
        local reads = W.card_reads
        W.card_comps["21732"].state = "selected"
        ticks(W, 2)
        local letter = badge_text(W, BADGE)
        click(W, BADGE)
        ticks(W, 1)
        local flipped = badge_text(W, BADGE)
        verdict(TAG, "CR2a", reads .. " card reads in 40 ticks on 3 cards (need 120: every tick), the letter " .. tostring(letter)
          .. " flips to " .. tostring(flipped) .. " on a click 2 ticks after the card reports the selection",
          reads >= 120 and (letter == "A" or letter == "M") and flipped ~= letter and (flipped == "A" or flipped == "M"))
        tally(W)
      else
        done(false)
      end
    end
  end
  check("HARNESS 215: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 215 done: " .. (checks - pre215) .. " checks in this section ==")
end
