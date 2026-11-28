-- ============================================================================
-- HARNESS 214 (round 216, tuning: the cost of the HUD walk. No cast decision changes).
--   0zz62 the round-216 tokens in both files.
--   SD1 the game's Find answers SA_dial, the selected unit owns an ability on the dial: the letter appears and the
--       walk never enters the rest of the HUD (battle_orders is never asked for its children). RED: it is asked.
--   SD2 the game's Find does NOT answer SA_dial (every older world): the letter appears, the whole HUD is walked
--       (GREEN and RED).
--   SD3 Find answers SA_dial but the unit's button sits OUTSIDE the dial (a UI mod): the dial walk claims nothing,
--       the whole HUD follows in the same tick, the letter appears (GREEN and RED).
--   WU1 the selection events are alive, an owner exists in the army. Selecting a unit that owns nothing of ours and
--       then deselecting it: the HUD walks in those ticks. GREEN: 0. RED: 2 or more.
--   WU2 the same battle, then the owner is selected: a walk on the next tick and the letter (GREEN and RED).
--   RED control: H214_LIVE / H214_ANN on docs/backups/round216/pre216_*.lua.
-- ============================================================================
function run_h214()
  local L214 = os.getenv("H214_LIVE") or LIVE
  local A214 = os.getenv("H214_ANN") or ANN
  local RED214 = (os.getenv("H214_LIVE") ~= nil) or (os.getenv("H214_ANN") ~= nil)
  local EW = "wh3_dlc25_unit_abilities_whirlwind_of_death_ror"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local BADGE = "zz_auto_badge_whirlwind_of_death_ror"
  local ERU = "wh3_main_character_abilities_eruption"   -- owned, never on the mock's dial: the walk gate stays open
  local pre214 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 214 - section 0zz62: the round-216 tokens ==")
  for _, f in ipairs({ { name = "live", path = L214 }, { name = "ann", path = A214 } }) do
    local s = read_file(f.path)
    local fns = cp(s, "\nfunction FOURTH.walk_useful(walk, t)\n") + cp(s, "\nfunction FOURTH.walk_start(hud)\n")
      + cp(s, "\nfunction FOURTH.walk_again()\n")
    local use = cp(s, "scan_component(FOURTH.walk_start(hud), 0)") + cp(s, "\t\tif FOURTH.walk_again() then\n")
      + cp(s, "walk_now = FOURTH.walk_useful(walk_now, ui_ticks)")
    local old = cp(s, "\t\tscan_component(hud, 0)\n")
    if RED214 then
      check("0zz62 " .. f.name .. " (RED): the pre-216 file has none of it", fns == 0 and use == 0 and old == 1)
    else
      check("0zz62 " .. f.name .. ": the three functions (" .. fns .. "), used once each (" .. use .. "), the old walk kept ("
        .. old .. ")", fns == 3 and use == 3 and old == 1)
    end
  end
  local FILES = { { path = A214, tag = "[annotated] " }, { path = L214, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function verdict(TAG, id, text, ok)
    check(TAG .. id .. (RED214 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  -- owners: which of the units own the ability. where: "bar" (under SA_dial) or "wheel" (outside the dial)
  local function mk(wname, base, owners, PATH, TAG, where, dial_found)
    local units, cards = {}, {}
    for i = 1, #owners do
      units[i] = { name = CASTER, uid = base + i, owns = owners[i] or {}, melee = false, dist = 60, width = 2,
                   men_alive = 1, unit_class = "com", hp_frac = 1.0 }
      cards[i] = { id = tostring(base + i), state = "active", vis = true }
    end
    local opts = { can_perform = true, units = units, enemies = {}, cards = cards, bar = {} }
    if where == "wheel" then
      opts.wheel = { { id = "button_ability1", key = EW, vis = true } }
    else
      opts.bar = { { id = "b1", key = EW } }
    end
    local W = make_world(opts)
    W.defaults_on = true
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    W.orders = W.hud_battle._kids[1]          -- battle_orders: the parent of SA_dial, only a whole-HUD walk asks it
    W.dial = W.orders._kids[1]
    -- the test build's inventory sweep walks the mock's whole tree once, on the first UI tick (the reading copy has no sweep)
    W.inv = (TAG == "[live] ") and 1 or 0
    if dial_found then
      local root = core:get_ui_root()
      local old_find = root.Find
      root.Find = function(self, what, a)
        if what == "SA_dial" then return W.dial end
        return old_find(self, what, a)
      end
    end
    deploy_phases(W)
    return W
  end
  local function ticks(W, n) for _ = 1, n do ui(W) end end
  local function letter_ok(W) local l = badge_text(W, BADGE); return (l == "A" or l == "M"), tostring(l) end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    do
      local W = mk("SD1. the dial is found: the walk stays inside it", 21600, { { EW } }, P, TAG, "bar", true)
      if W ~= nil then
        ticks(W, 3)
        while W.ui_calls % 100 > 80 or W.ui_calls % 100 < 2 do ui(W) end   -- keep clear of the 5 s safety net
        sel_event(W, 21601, true)
        ticks(W, 6)
        local asked = W.orders._c.childcount - W.inv   -- since the battle loaded
        local ok_l, l = letter_ok(W)
        local good = ok_l and asked == 0
        if RED214 then good = ok_l and asked >= 1 end
        verdict(TAG, "SD1a", "the letter is " .. l .. ", the rest of the HUD was entered " .. asked .. " time(s) ("
          .. (RED214 and "RED: at least 1" or "need 0") .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("SD2. the dial is not found: the whole HUD as before", 21610, { { EW } }, P, TAG, "bar", false)
      if W ~= nil then
        ticks(W, 3)
        sel_event(W, 21611, true)
        ticks(W, 6)
        local asked = W.orders._c.childcount - W.inv   -- since the battle loaded
        local ok_l, l = letter_ok(W)
        verdict(TAG, "SD2a", "the letter is " .. l .. ", the rest of the HUD was entered " .. asked .. " time(s) (need at least 1)",
          ok_l and asked >= 1)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("SD3. the dial is found but the button sits outside it", 21620, { { EW } }, P, TAG, "wheel", true)
      if W ~= nil then
        ticks(W, 3)
        while W.ui_calls % 100 > 80 or W.ui_calls % 100 < 2 do ui(W) end
        sel_event(W, 21621, true)
        ticks(W, 2)
        local asked = W.orders._c.childcount - W.inv   -- since the battle loaded
        local claimed = false
        for _, l in ipairs(W.log_lines) do
          if raw_find(l, "found: whirlwind_of_death_ror", 1, true) ~= nil then claimed = true end
        end
        if TAG ~= "[live] " then claimed = true end   -- the reading copy does not log
        verdict(TAG, "SD3a", "the whole HUD was walked by 2 ticks after the selection (entered " .. asked
          .. " time(s), need at least 1) and the button was claimed (" .. tostring(claimed) .. ")", asked >= 1 and claimed)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("WU. an owner in the army, a unit that owns nothing is selected and dropped", 21630, { false, { EW, ERU } }, P, TAG, "bar", false)
      if W ~= nil then
        ticks(W, 3)
        sel_event(W, 21632, true)      -- the selection events are alive, the owner's letter exists
        ticks(W, 6)
        sel_event(W, 21632, false)
        ticks(W, 60)                   -- the window of that deselection runs out
        while W.ui_calls % 100 > 80 or W.ui_calls % 100 < 2 do ui(W) end
        W.hud_walks = 0
        sel_event(W, 21631, true)      -- owns nothing of ours
        ticks(W, 3)
        sel_event(W, 21631, false)     -- nothing selected
        ticks(W, 3)
        local walks = W.hud_walks
        local good = (walks == 0)
        if RED214 then good = (walks >= 2) end
        verdict(TAG, "WU1a", walks .. " HUD walk(s) while a unit that owns nothing was selected and dropped ("
          .. (RED214 and "RED: 2 or more" or "need 0") .. ")", good)
        W.hud_walks = 0
        sel_event(W, 21632, true)
        ticks(W, 1)
        local on_owner = W.hud_walks
        ticks(W, 5)
        local ok_l, l = letter_ok(W)
        verdict(TAG, "WU2a", on_owner .. " walk on the tick after the owner is selected (need 1), the letter is " .. l,
          on_owner == 1 and ok_l)
        tally(W)
      else
        done(false); done(false)
      end
    end
  end
  check("HARNESS 214: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 214 done: " .. (checks - pre214) .. " checks in this section ==")
end
