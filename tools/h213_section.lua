-- ============================================================================
-- HARNESS 213 (round 215, tuning: the mod's own cost. No cast decision changes).
--   0zz61 the round-215 tokens in both files.
--   BW1 the DEPLOYMENT phase, nothing selected, the units not listed yet: the HUD walks in UI ticks 41 to 140. GREEN: at most 1 (the 5 s safety
--       net). RED: 45 or more (every 2nd tick, the 10 walks a second the timing probe measured).
--   BW2 the same battle, then the first selection: a walk on the very next tick (GREEN and RED), and the letter exists.
--   CD1 three units. The unit-card reads in 40 UI ticks BEFORE the game's selection events have arrived, and in 40
--       ticks AFTER. GREEN: after is at most 30% of before. RED: 90% or more.
--   CD2 the selection events are alive, then a selection only the card reports -> the letter follows it within 5 UI
--       ticks (GREEN and RED).
--   RED control: H213_LIVE / H213_ANN on docs/backups/round215/pre215_*.lua.
-- ============================================================================
function run_h213()
  local L213 = os.getenv("H213_LIVE") or LIVE
  local A213 = os.getenv("H213_ANN") or ANN
  local RED213 = (os.getenv("H213_LIVE") ~= nil) or (os.getenv("H213_ANN") ~= nil)
  local EW = "wh3_dlc25_unit_abilities_whirlwind_of_death_ror"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local ERU = "wh3_main_character_abilities_eruption"
  local pre213 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 213 - section 0zz61: the round-215 tokens ==")
  for _, f in ipairs({ { name = "live", path = L213 }, { name = "ann", path = A213 } }) do
    local s = read_file(f.path)
    local fns = cp(s, "\nfunction FOURTH.boot_due(t, window_end, walk)\n") + cp(s, "\nfunction FOURTH.cards_due(t)\n")
    local use = cp(s, "walk_now = FOURTH.boot_due(ui_ticks, brisk_walk_until, walk_now)") + cp(s, "\tif FOURTH.cards_due(ui_ticks) then")
    local old = cp(s, "walk_now = (ui_ticks % 2) == 0") + cp(s, "\tpcall(fast_card_selection)\n")
    if RED213 then
      check("0zz61 " .. f.name .. " (RED): the pre-215 file has neither", fns == 0 and use == 0 and old == 2)
    else
      check("0zz61 " .. f.name .. ": the two functions (" .. fns .. "), used once each (" .. use .. "), the old lines kept ("
        .. old .. ")", fns == 2 and use == 2 and old == 2)
    end
  end
  local FILES = { { path = A213, tag = "[annotated] " }, { path = L213, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function verdict(TAG, id, text, ok)
    check(TAG .. id .. (RED213 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  local function mk(wname, base, n_units, PATH, TAG, last_owns, stay_in_deployment)
    local units, cards = {}, {}
    for i = 1, n_units do
      units[i] = { name = CASTER, uid = base + i, owns = { EW }, melee = false, dist = 60, width = 2, men_alive = 1,
                   unit_class = "com", hp_frac = 1.0 }
      cards[i] = { id = tostring(base + i), state = "active", vis = true }
    end
    if last_owns ~= nil then units[n_units].owns = last_owns end
    local W = make_world({ can_perform = true, units = units, enemies = {}, cards = cards, bar = { { id = "b1", key = EW } } })
    W.defaults_on = true
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    W.card_reads = 0
    for i = 1, n_units do
      local c = W.card_comps[tostring(base + i)]
      if c ~= nil and c.CurrentState ~= nil then
        local old = c.CurrentState
        c.CurrentState = function(self, ...)
          W.card_reads = W.card_reads + 1
          return old(self, ...)
        end
      end
    end
    if stay_in_deployment then
      -- the DEPLOYMENT phase of a real battle: the HUD is on screen, the units are not listed yet
      W.conflict = false
      run_phase(W, "Deployment")
      W.icons_on_screen = true
    else
      deploy_phases(W)
    end
    return W
  end
  local function ticks(W, n) for _ = 1, n do ui(W) end end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    do
      local W = mk("BW. a battle where nothing is selected (a second unit owns an ability the wheel does not show)", 21500, 2, P, TAG, { ERU }, true)
      if W ~= nil then
        W.hud_walks = 0
        ticks(W, 40)
        local first = W.hud_walks
        ticks(W, 100)
        local later = W.hud_walks - first
        local good = (later <= 1)
        if RED213 then good = (later >= 45) end
        verdict(TAG, "BW1a", first .. " HUD walks in the first 40 ticks, " .. later .. " in ticks 41 to 140 ("
          .. (RED213 and "RED: 45 or more" or "need at most 1") .. ")", good)
        run_phase(W, "Deployed")   -- the battle starts: the units are listed
        ticks(W, 2)
        local before = W.hud_walks
        sel_event(W, 21501, true)
        ticks(W, 2)
        local on_event = W.hud_walks - before
        ticks(W, 4)
        local letter = badge_text(W, "zz_auto_badge_whirlwind_of_death_ror")
        verdict(TAG, "BW2a", on_event .. " walk(s) within 2 ticks of the first selection (need at least 1), the letter is "
          .. tostring(letter), on_event >= 1 and (letter == "A" or letter == "M"))
        tally(W)
      else
        done(false); done(false)
      end
    end
    do
      local W = mk("CD. three units, the card reads before and after the selection events arrive", 21510, 3, P, TAG)
      if W ~= nil then
        ticks(W, 4)
        W.card_reads = 0
        ticks(W, 40)
        local before = W.card_reads
        sel_event(W, 21511, true)
        sel_event(W, 21511, false)
        ticks(W, 4)
        W.card_reads = 0
        ticks(W, 40)
        local after = W.card_reads
        local share = (before > 0) and (after / before) or 9
        local good = (before > 0 and share <= 0.30)
        if RED213 then good = (before > 0 and share >= 0.90) end
        verdict(TAG, "CD1a", before .. " card reads in 40 ticks before the events, " .. after .. " after ("
          .. string.format("%.0f%%", share * 100) .. ", " .. (RED213 and "RED: 90% or more" or "need at most 30%") .. ")", good)
        W.card_comps["21512"].state = "selected"
        ticks(W, 5)
        local letter = badge_text(W, "zz_auto_badge_whirlwind_of_death_ror")
        click(W, "zz_auto_badge_whirlwind_of_death_ror")
        ticks(W, 1)
        local flipped = badge_text(W, "zz_auto_badge_whirlwind_of_death_ror")
        verdict(TAG, "CD2a", "a selection only the card reports is followed within 5 ticks: the letter " .. tostring(letter)
          .. " flips to " .. tostring(flipped) .. " on a click", (letter == "A" or letter == "M") and flipped ~= letter
          and (flipped == "A" or flipped == "M"))
        tally(W)
      else
        done(false); done(false)
      end
    end
  end
  check("HARNESS 213: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 213 done: " .. (checks - pre213) .. " checks in this section ==")
end
