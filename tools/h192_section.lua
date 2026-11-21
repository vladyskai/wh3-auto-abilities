-- ============================================================================
-- HARNESS 192 (round 193, user rulings 2026-11-21):
--   (1) Scry-Orb on when_ready ("implement"); 3 uses, a 120 s hold row.
--   (2) The READ-ONLY pre-shot probe ("implement recommendation and propose a test battle"): WOULD CAST / WOULD CAST
--       ENDED / PRESHOT lines in the live log, nothing cast.
--   0zz41 the round-193 tokens in both files.
--   SO1 Scry-Orb on its own, armed -> ONE cast (RED: no entry, none).
--   PS1 crossbowmen standing, the target in range, then the first shot -> WOULD CAST once, PRESHOT 'held' once, 0 casts.
--   PS2 the same unit WALKING -> no WOULD CAST; PRESHOT 'no would-cast before it' at the shot.
--   PS3 the target beyond the missile range -> no WOULD CAST.
--   PS4 the target hidden (is_visible_to_alliance false) -> no WOULD CAST.
--   PS5 the condition holds, then the unit starts walking -> WOULD CAST ENDED (moving).
--   RED control: H192_LIVE / H192_ANN on docs/backups/round193/pre193_*.lua (no probe lines, no Scry-Orb cast).
-- ============================================================================
function run_h192()
  local L192 = os.getenv("H192_LIVE") or LIVE
  local A192 = os.getenv("H192_ANN") or ANN
  local RED192 = (os.getenv("H192_LIVE") ~= nil) or (os.getenv("H192_ANN") ~= nil)
  local SCRY = "wh3_dlc29_item_abilities_scry_orb"
  local XBOW = "wh_main_emp_inf_crossbowmen"
  local pre192 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  local function lg(tag, v) return (tag ~= "[live] ") or v end
  print("== HARNESS 192 - section 0zz41: the round-193 tokens ==")
  for _, f in ipairs({ { name = "live", path = L192 }, { name = "ann", path = A192 } }) do
    local s = read_file(f.path)
    local scry = cp(s, '{ marker = "scry_orb", name = "Scry-Orb", trigger = "when_ready",')
    local hold = cp(s, '["wh3_dlc29_item_abilities_scry_orb"] = 120,')
    local head = cp(s, "-- ROUND 193 - THE PRE-SHOT PROBE (READ-ONLY")
    local call = cp(s, "if not st.firing then FOURTH.preshot_probe(u, st, now_s, inr, d, r) end   -- ROUND 193: read-only")
    local first = cp(s, "FOURTH.preshot_first_shot(u, st, now_s)   -- ROUND 193: the read-only pre-shot probe")
    if RED192 then
      check("0zz41 " .. f.name .. " (RED): the pre-193 file has no Scry-Orb entry and no probe",
        scry == 0 and hold == 0 and head == 0 and call == 0 and first == 0)
    else
      check("0zz41 " .. f.name .. ": Scry-Orb (" .. scry .. hold .. "), the probe (" .. head .. call .. first .. ")",
        scry == 1 and hold == 1 and head == 1 and call == 1 and first == 1)
    end
  end
  local FILES = { { path = A192, tag = "[annotated] " }, { path = L192, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    -- SO1: Scry-Orb, armed by a click
    do
      local u = { { name = "wh3_dlc29_skv_cha_grey_seer_0", uid = 19201, owns = { SCRY }, melee = false } }
      local W = make_world({ can_perform = true, units = u, cards = { { id = "19201", state = "active", vis = true } },
        bar = { { id = "b1", key = SCRY } } })
      W.defaults_on = false
      print("== " .. TAG .. "SO1. Scry-Orb on when_ready, armed -> ONE cast ==")
      local ok = pcall(load_world, W, P)
      check(TAG .. "SO1: the file loads", ok)
      if ok then
        deploy_phases(W); ui(W)
        sel_event(W, 19201, true); ui(W); ui(W)
        click(W, "zz_auto_badge_scry_orb"); ui(W)
        sel_event(W, 19201, false); ui(W)
        W.conflict = true
        polln(W, 4)
        local n = 0
        for _, x in ipairs(W.fires) do if x.key == SCRY then n = n + 1 end end
        local want = RED192 and 0 or 1
        local a = (n == want)
        check(TAG .. "SO1a: " .. want .. " cast(s) expected, got " .. n .. (RED192 and " (RED: the pre-193 file)" or ""), a)
        done(a)
        tally(W)
      else
        done(false)
      end
    end
    -- the probe worlds: one crossbow unit; ammo 20 for 8 polls, then 19 (the first shot)
    local function probe(id, wname, extra, polls, step, check_fn)
      local seq = {}
      for _ = 1, 8 do seq[#seq + 1] = 20 end
      seq[#seq + 1] = 19
      local def = { name = XBOW, uid = 19211, owns = {}, melee = false, moving = false, dist = 100, missile_range = 150,
                    ammo_start = 20, ammo_seq = seq, ammo_target = { type = "wh_main_grn_inf_orc_boyz", melee = false } }
      for k, v in pairs(extra or {}) do def[k] = v end
      local W = make_world({ can_perform = true, units = { def },
        cards = { { id = "19211", state = "active", vis = true } }, bar = {} })
      W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
      print("== " .. TAG .. id .. ". " .. wname .. " ==")
      local ok = pcall(load_world, W, P)
      check(TAG .. id .. ": the file loads", ok)
      if not ok then done(false); return end
      deploy_phases(W); ui(W)
      W.conflict = true
      if def.hidden then
        local mu = W.mock_units[1]
        local tobj = {}
        function tobj:type() return "wh_main_grn_inf_orc_boyz" end
        function tobj:is_in_melee() return false end
        function tobj:is_visible_to_alliance(a) return false end
        mu.current_target = function(self) return tobj end
      end
      for i = 1, polls do
        if step ~= nil then step(i, def) end
        polln(W, 1)
      end
      local a = check_fn(W)
      local nf = #W.fires
      check(TAG .. id .. "a: " .. wname .. (RED192 and " (RED: no probe lines)" or "") .. " [live log]", lg(TAG, a))
      check(TAG .. id .. "b: the probe casts NOTHING (" .. nf .. " fires)", nf == 0)
      done(lg(TAG, a) and nf == 0)
      tally(W)
    end
    local W_ = "WOULD CAST unit 19211"
    probe("PS1", "standing, target in range, then the first shot -> WOULD CAST once, PRESHOT 'held' once", nil, 12, nil,
      function(W)
        if RED192 then return count_log(W, "WOULD CAST") == 0 and count_log(W, "PRESHOT") == 0 end
        return count_log(W, W_ .. " ") == 1 and count_log(W, "PRESHOT unit 19211") == 1
          and count_log(W, "the condition held") == 1 and count_log(W, "WOULD CAST ENDED") == 0
      end)
    probe("PS2", "WALKING -> no WOULD CAST, PRESHOT 'no would-cast before it'", { moving = true }, 12, nil,
      function(W)
        if RED192 then return count_log(W, "WOULD CAST") == 0 and count_log(W, "PRESHOT") == 0 end
        return count_log(W, "WOULD CAST") == 0 and count_log(W, "came with no would-cast before it") == 1
      end)
    probe("PS3", "the target beyond the missile range -> no WOULD CAST", { dist = 200 }, 6, nil,
      function(W) return count_log(W, "WOULD CAST") == 0 end)
    probe("PS4", "the target hidden -> no WOULD CAST", { hidden = true }, 6, nil,
      function(W) return count_log(W, "WOULD CAST") == 0 end)
    probe("PS5", "the condition holds, then the unit walks -> WOULD CAST ENDED (moving)", nil, 7,
      function(i, def) if i >= 4 then def.moving = true end end,
      function(W)
        if RED192 then return count_log(W, "WOULD CAST") == 0 end
        return count_log(W, W_ .. " ") == 1 and count_log(W, "WOULD CAST ENDED unit 19211") == 1
          and count_log(W, "with no shot (moving)") == 1
      end)
  end
  check("HARNESS 192: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 192 done: " .. (checks - pre192) .. " checks in this section ==")
end
