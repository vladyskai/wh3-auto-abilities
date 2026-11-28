-- ============================================================================
-- HARNESS 211 (round 213, tuning: the cost of a selection. No cast decision changes).
--   0zz59 the round-213 tokens in both files.
--   The worlds count the HUD walks (W.hud_walks). A hero owns two abilities of ours, the wheel shows a button for ONE
--   of them, so the other is never claimed.
--   SW1 the hero is selected for the first time: the walks in the 48 UI ticks after the selection. GREEN and RED: 12
--       or more (the first window is unchanged).
--   SW2 the selection is dropped and the hero is selected again: GREEN at most 2 walks in the 48 ticks (the event and
--       one retry). RED: 12 or more.
--   SW3 a third selection: GREEN at most 2. RED: 12 or more.
--   SW4 a hero whose two abilities both have a button: selected, both letters exist within 6 UI ticks and no walk runs
--       in the next 42 (GREEN and RED: nothing is lost on the normal path).
--   RED control: H211_LIVE / H211_ANN on docs/backups/round213/pre213_*.lua.
-- ============================================================================
function run_h211()
  local L211 = os.getenv("H211_LIVE") or LIVE
  local A211 = os.getenv("H211_ANN") or ANN
  local RED211 = (os.getenv("H211_LIVE") ~= nil) or (os.getenv("H211_ANN") ~= nil)
  local EW = "wh3_dlc25_unit_abilities_whirlwind_of_death_ror"
  local ERU = "wh3_main_character_abilities_eruption"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local pre211 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 211 - section 0zz59: the round-213 tokens ==")
  for _, f in ipairs({ { name = "live", path = L211 }, { name = "ann", path = A211 } }) do
    local s = read_file(f.path)
    local fn = cp(s, "\nfunction FOURTH.brisk_due(t, window_end, walk)\n")
    local use = cp(s, "\t\t\t\twalk_now = FOURTH.brisk_due(ui_ticks, brisk_walk_until, walk_now)")
    local old = cp(s, "walk_now = (ui_ticks % 2) == 0") + cp(s, "walk_now = (ui_ticks % 4) == 0")
    local net = cp(s, "walk_now = (ui_ticks % 100) == 0")
    if RED211 then
      check("0zz59 " .. f.name .. " (RED): the pre-213 file has no memory of a unit whose button never came", fn == 0 and use == 0 and old == 2)
    else
      check("0zz59 " .. f.name .. ": the memory (" .. fn .. ", " .. use .. "), the two cadences kept (" .. old
        .. "), the 5 s safety net kept (" .. net .. ")", fn == 1 and use == 1 and old == 2 and net == 3)
    end
  end
  local FILES = { { path = A211, tag = "[annotated] " }, { path = L211, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function verdict(TAG, id, text, ok)
    check(TAG .. id .. (RED211 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  local function mk(wname, uid, bar, PATH, TAG)
    local W = make_world({ can_perform = true, units = { { name = CASTER, uid = uid, owns = { EW, ERU }, melee = false, dist = 60,
      width = 2, men_alive = 1, unit_class = "com", hp_frac = 1.0 } }, enemies = {},
      cards = { { id = tostring(uid), state = "active", vis = true } }, bar = bar })
    W.defaults_on = true
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W)
    for _ = 1, 60 do ui(W) end
    return W
  end
  local function ticks(W, n)
    local before = W.hud_walks or 0
    for _ = 1, n do ui(W) end
    return (W.hud_walks or 0) - before
  end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    do
      local W = mk("SW. a hero with one ability whose button never appears", 21300, { { id = "b1", key = EW } }, P, TAG)
      if W ~= nil then
        sel_event(W, 21300, true)
        local d1 = ticks(W, 48)
        ticks(W, 12)
        sel_event(W, 21300, false)
        ticks(W, 2)
        sel_event(W, 21300, true)
        local d2 = ticks(W, 48)
        ticks(W, 12)
        sel_event(W, 21300, false)
        ticks(W, 2)
        sel_event(W, 21300, true)
        local d3 = ticks(W, 48)
        local g1, g2, g3 = (d1 >= 12), (d2 <= 2), (d3 <= 2)
        if RED211 then g2, g3 = (d2 >= 12), (d3 >= 12) end
        verdict(TAG, "SW1a", d1 .. " HUD walks in the 48 ticks after the first selection (need 12 or more: unchanged)", g1)
        verdict(TAG, "SW2a", d2 .. " HUD walks in the 48 ticks after the second selection (" .. (RED211 and "RED: 12 or more" or "need at most 2") .. ")", g2)
        verdict(TAG, "SW3a", d3 .. " HUD walks in the 48 ticks after the third selection (" .. (RED211 and "RED: 12 or more" or "need at most 2") .. ")", g3)
        tally(W)
      else
        done(false); done(false); done(false)
      end
    end
    do
      local W = mk("SW4. a hero whose two abilities both have a button", 21310,
        { { id = "b1", key = EW }, { id = "b2", key = ERU } }, P, TAG)
      if W ~= nil then
        sel_event(W, 21310, true)
        local d1 = ticks(W, 6)
        local a, b = badge_text(W, "zz_auto_badge_whirlwind_of_death_ror"), badge_text(W, "zz_auto_badge_eruption")
        local d2 = ticks(W, 42)
        verdict(TAG, "SW4a", "both letters exist 6 ticks after the selection (" .. tostring(a) .. ", " .. tostring(b) .. "), "
          .. d1 .. " walk(s) in those ticks and " .. d2 .. " in the next 42 (need letters, at most 2, 0)",
          (a == "A" or a == "M") and (b == "A" or b == "M") and d1 <= 2 and d2 == 0)
        tally(W)
      else
        done(false)
      end
    end
  end
  check("HARNESS 211: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 211 done: " .. (checks - pre211) .. " checks in this section ==")
end
