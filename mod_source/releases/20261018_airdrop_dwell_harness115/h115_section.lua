-- ============================================================================
-- HARNESS 115 - THE TRIGGER WAITS: THE 1-SECOND DWELL ON THE PAIR.
--
-- THE USER'S RULING, verbatim: "I mean the trigger fires too soon. So we need a
-- delay of 1 second for the trigger."
--
-- THE RULE THE WORLDS BELOW PROVE - round 114's edge rule is untouched, it now
-- has to LAST:
--   candidate = alive and number_of_men_alive() > AIR_DROP_MIN_MEN (10)
--   valid     = its unit_distance() is readable
--   chosen    = the NEAREST valid candidate
--   UNDER     = unit_distance(caster, chosen) < AIR_DROP_EDGE_M (0.10 m)
--   FIRE      = the pair has been CONTINUOUSLY UNDER for AIR_DROP_DWELL_S
--               (1.0 s) on the poll's clock, OR it separated after at least
--               AIR_DROP_MIN_CONTACT_S (0.3 s) of contact (the short-crossing
--               fallback)
--
-- THE CLOCK IS THE POLL: tick_count advances once per poll (POLL_MS = 250 ms),
-- so 1.0 s of dwell is the stamp plus FOUR further polls. The fast pass adds
-- EVALUATIONS, never time - world E proves that five fast ticks on a fresh
-- contact move the dwell by nothing at all.
--
-- PINS (section 0, asserted against BOTH files):
--     DWELL_S       AIR_DROP_DWELL_S       = 1.0
--     MIN_CONTACT_S AIR_DROP_MIN_CONTACT_S = 0.3
--   the four round-114 constants unchanged, POLL_MS still 250, the fast timer
--   still registered, the nested pair state, the five event lines, the purge
--   hook, the re-check's dwell verification and the new tooltip sentence.
--
-- RED CONTROL (H115_LIVE / H115_ANN -> docs/backups/round115/pre115_*.lua, the
-- round-114 build): there is no AIR_DROP_DWELL_S, no ad_pair and no dwell line,
-- so every 0 check and every A-J world fails as designed.
-- ============================================================================
function run_h115()
  if os.getenv("H115_LIVE") ~= nil then LIVE = os.getenv("H115_LIVE") end
  if os.getenv("H115_ANN") ~= nil then ANN = os.getenv("H115_ANN") end
  local red115 = (os.getenv("H115_LIVE") ~= nil) or (os.getenv("H115_ANN") ~= nil)
  local live_src = read_file(LIVE)
  local ann_src = read_file(ANN)
  local pre115 = checks
  local DFA = "wh2_dlc09_unit_abilities_death_from_above"
  local INF = "wh_main_inf_zombie_0"

  local function cp(s2, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s2, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function span(s2, head, tail2)
    local i = raw_find(s2, head, 1, true)
    if i == nil then return nil end
    local j = raw_find(s2, tail2, i, true)
    if j == nil then return nil end
    return s2:sub(i, j)
  end
  local function lg(cond) return cond == true end
  local function cl(W, frag) return count_log(W, frag) end

  -- unit_distance is read ON THE CASTER with the enemy as its argument, so the
  -- mock answer hangs on the caster: dm = { [enemy_uid] = metres } and/or a
  -- per-READ dseq = { d1, d2, ... } (the LAST value repeats).
  local function mk(uid, edef, dm, dseq)
    local def = { name = "sky_junk", uid = uid, owns = { DFA }, melee = false }
    if dm ~= nil then def.dist_by_target = dm end
    if dseq ~= nil then def.dist_seq = dseq end
    local W = make_world({ can_perform = true, units = { def }, enemies = { edef },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = DFA } } })
    local u = unit_of(W, uid)
    if u ~= nil then u.is_currently_flying = function() return true end end
    return W
  end
  local function boot(W, PATH, TAG, uid, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_death_from_above"); ui(W)
    W.conflict = true
    return true
  end
  local function fastn(W, n)
    if W.fast_fn == nil then return false end
    for _ = 1, n do W.fast_fn() end
    return true
  end

  -- ==========================================================================
  print("== HARNESS 115 - section 0: the two dwell pins, the state, the hooks (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src }, { name = "ann", src = ann_src } }) do
    local nm, s2 = f.name, f.src
    local pick = span(s2, "function FOURTH.ad_pick(unit, routing)",
      "\nfunction FOURTH.evaluate_air_drop_on_infantry")
    local under = span(s2, "function FOURTH.ad_under(st)", "\nend")
    local purge = span(s2, "function FOURTH.ad_purge_unit(id_text)", "\nend")
    local stamp = span(s2, "function FOURTH.ad_pair_stamp(cid, eid)", "\nend")
    local recheck = span(s2, "local fired = FOURTH.ad_fired", "local gap_ok =")

    check("0 " .. nm .. ": the TWO dwell constants are defined EXACTLY ONCE (1.0 s dwell / 0.3 s floor)",
      cp(s2, "\nFOURTH.AIR_DROP_DWELL_S = 1.0\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_MIN_CONTACT_S = 0.3\n") == 1)
    check("0 " .. nm .. ": the four round-114 constants are untouched (0.1 m / 10 men / 30 m / 0.2 s)",
      cp(s2, "\nFOURTH.AIR_DROP_EDGE_M = 0.1\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_MIN_MEN = 10\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_NEAR_M = 30\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_FAST_S = 0.2\n") == 1)
    check("0 " .. nm .. ": the pair state is NESTED (no composite key) and carries ONE timestamp",
      cp(s2, "FOURTH.ad_pair = {}\n") == 1
      and cp(s2, "function FOURTH.ad_pair_key(unit, enemy)") == 1
      and stamp ~= nil and raw_find(stamp, "per[eid] = { first = tick_count }", 1, true) ~= nil
      and raw_find(s2, '.. "|" ..', 1, true) == nil)
    check("0 " .. nm .. ": THE CLOCK is the poll's tick_count, not a new counter",
      under ~= nil
      and raw_find(under, "local n = tick_count - st.first", 1, true) ~= nil
      and raw_find(under, "(n * POLL_MS) / 1000", 1, true) ~= nil
      and raw_find(under, "AIR_DROP_FAST_S", 1, true) == nil
      and cp(s2, "local POLL_MS = 250") == 1)
    check("0 " .. nm .. ": the FIRST evaluation of a contact cannot fire (stamp, then return nil)",
      pick ~= nil
      and raw_find(pick, "return nil     -- THE FIRST EVALUATION OF A CONTACT NEVER FIRES", 1, true) ~= nil)
    check("0 " .. nm .. ": the short-crossing fallback fires ON the separation evaluation",
      pick ~= nil
      and raw_find(pick, "if under >= FOURTH.AIR_DROP_MIN_CONTACT_S then", 1, true) ~= nil
      and raw_find(pick, "FOURTH.ad_pair_drop(cid, eid)", 1, true) ~= nil)
    check("0 " .. nm .. ": a separation clears the row and a re-contact stamps a FRESH one",
      pick ~= nil
      and raw_find(pick, "FOURTH.ad_pair_stamp(cid, eid)", 1, true) ~= nil
      and raw_find(pick, "FOURTH.ad_contact_clear(unit, marker)", 1, true) ~= nil)
    check("0 " .. nm .. ": the purge hook is attached ONCE and called from the ONE drop routine",
      cp(s2, "zz_ad_dwell_purge = FOURTH.ad_purge_unit") == 1
      and cp(s2, "if zz_ad_dwell_purge ~= nil then zz_ad_dwell_purge(id_text) end") == 1
      and purge ~= nil and raw_find(purge, "FOURTH.ad_pair[idt] = nil", 1, true) ~= nil
      and raw_find(purge, "per[idt] = nil", 1, true) ~= nil)
    check("0 " .. nm .. ": the pre-cast re-check re-verifies the DWELL as well as the gap",
      recheck ~= nil
      and raw_find(recheck, "local dwell_ok, dwell_text = true, \"?\"", 1, true) ~= nil
      and raw_find(recheck, "if fallback_now then floor_s = FOURTH.AIR_DROP_MIN_CONTACT_S end", 1, true) ~= nil
      and raw_find(s2, "local gap_ok = (edge_ok or (fallback_now and dwell_ok))", 1, true) ~= nil
      and raw_find(s2, "and men_ok and gap_ok and dwell_ok) then", 1, true) ~= nil)
    check("0 " .. nm .. ": air_only / no_melee / the self-centred cast / fail-closed are ALL still in place",
      raw_find(s2, "is_currently_flying()", 1, true) ~= nil
      and raw_find(s2, "is_in_melee()", 1, true) ~= nil
      and raw_find(s2, "FOURTH.ad_air_only", 1, true) ~= nil
      and raw_find(s2, "FOURTH.ad_no_melee", 1, true) ~= nil
      and raw_find(s2, "perform_special_ability", 1, true) ~= nil)
    check("0 " .. nm .. ": the fast pass and the poll are still BOTH registered, POLL_MS untouched",
      cp(s2, "bm:repeat_callback(") == 2
      and cp(s2, 'bm:repeat_callback(poll, POLL_MS, POLL_NAME)') == 1
      and cp(s2, "zz_test_deadly_onslaught_air_drop_fast") == 1)
    check("0 " .. nm .. ": the family counts are unchanged (12 air-drop entries of 689)",
      cp(s2, 'trigger = "air_drop_on_infantry"') == 12 and cp(s2, "\t{ marker = ") == 689)
    check("0 " .. nm .. ": the tooltip sentence states the dwell",
      raw_find(s2, "air_drop_on_infantry = \"When armed, fires when the nearest enemy unit with more than 10 models stays within 0.1 m", 1, true) ~= nil
      and raw_find(s2, "stays within 0.1 m of this unit's edge for 1 second", 1, true) ~= nil)
    if nm == "live" then
      check("0 live: every dwell line carries the caster ui id (ad_tag definition + 6 sites)",
        cp(s2, "FOURTH.ad_tag(unit)") == 7)
      check("0 live: the five event lines exist verbatim",
        cp(s2, '"dwell started: under at gap %.2fm, waiting %.2fs (pair \'%s\')"') == 1
        and cp(s2, '"dwell satisfied after %.2fs -> FIRING (gap %.2fm, pair \'%s\')"') == 1
        and cp(s2, '"dwell: under %.2fs of %.2fs (gap %.2fm)"') == 1
        and cp(s2, '"dwell cancelled: separated after %.2fs (gap %.2fm; the dwell is %.2fs"') == 1
        and cp(s2, '"short crossing: under for %.2fs (>= %.2fs) -> FIRING on separation"') == 1)
    else
      check("0 ann: the reading copy stays LOG-FREE and carries the same helpers",
        raw_find(s2, "log(", 1, true) == nil
        and raw_find(s2, "function FOURTH.ad_nearest(unit)", 1, true) ~= nil
        and raw_find(s2, "function FOURTH.ad_pair_stamp(cid, eid)", 1, true) ~= nil
        and raw_find(s2, "function FOURTH.ad_purge_unit(id_text)", 1, true) ~= nil
        and raw_find(s2, "function FOURTH.ad_under(st)", 1, true) ~= nil)
    end
  end

  -- ==========================================================================
  print("== HARNESS 115 - A: a 1.0 s contact FIRES, on the poll that completes it ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17001, 17101
    local W = mk(uid, { name = INF, uid = euid, men_alive = 20 }, { [euid] = 0.05 })
    if boot(W, PATH, TAG, uid, "A") then
      polln(W, 1)
      check(TAG .. "A1: the FIRST evaluation stamps the contact and does NOT fire (" .. #W.fires .. ")",
        #W.fires == 0)
      check(TAG .. "A2: the start line names the gap and the wait [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "[17001] death_from_above dwell started: under at gap 0.05m, waiting 1.00s") == 1)))
      polln(W, 3)
      check(TAG .. "A3: 0.75 s under the line it STILL holds (" .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "A4: the hold line reports the running time [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "dwell: under 0.75s of 1.00s") == 1)))
      polln(W, 1)
      check(TAG .. "A5: the poll that completes 1.00 s fires, ONCE (" .. #W.fires .. ")", #W.fires == 1)
      check(TAG .. "A6: the fire names the dwell it waited for [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "dwell satisfied after 1.00s -> FIRING") == 1)))
      check(TAG .. "A7: the pre-cast re-check re-verified the dwell AND the gap [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "-> FIRING (re-checked) (dwell 1.00s of 1.00s)") == 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 115 - B: a 0.75 s contact that separates FIRES on the way out (fallback) ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17002, 17102
    local dm = { [euid] = 0.05 }
    local W = mk(uid, { name = INF, uid = euid, men_alive = 20 }, dm)
    if boot(W, PATH, TAG, uid, "B") then
      polln(W, 1)
      polln(W, 2)
      check(TAG .. "B1: 0.50 s under is not the dwell - nothing fired yet (" .. #W.fires .. ")",
        #W.fires == 0)
      dm[euid] = 0.40
      polln(W, 1)
      check(TAG .. "B2: it separated at 0.75 s of contact - the fallback FIRES (" .. #W.fires .. ")",
        #W.fires == 1)
      check(TAG .. "B3: the fallback line states the time under and the floor [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "short crossing: under for 0.75s (>= 0.30s) -> FIRING on separation") == 1)))
      check(TAG .. "B4: and it did NOT fire through the dwell [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "dwell satisfied") == 0)))
      check(TAG .. "B5: the re-check accepts the fallback and reports what it held [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "(short crossing: held 0.75s of 0.30s)") == 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 115 - C: a 0.25 s contact that separates CANCELS, with its time logged ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17003, 17103
    local dm = { [euid] = 0.05 }
    local W = mk(uid, { name = INF, uid = euid, men_alive = 20 }, dm)
    if boot(W, PATH, TAG, uid, "C") then
      polln(W, 1)
      dm[euid] = 0.40
      polln(W, 1)
      check(TAG .. "C1: a contact under the 0.30 s floor fires NOTHING (" .. #W.fires .. ")",
        #W.fires == 0)
      check(TAG .. "C2: the cancel line names the time under and the separation gap [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "dwell cancelled: separated after 0.25s (gap 0.40m") == 1)))
      check(TAG .. "C3: no fallback fire was invented [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "short crossing") == 0)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 115 - D: a re-contact starts a FRESH dwell (never inherits the old stamp) ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17004, 17104
    local dm = { [euid] = 0.05 }
    local W = mk(uid, { name = INF, uid = euid, men_alive = 20 }, dm)
    if boot(W, PATH, TAG, uid, "D") then
      polln(W, 1)
      dm[euid] = 0.50
      polln(W, 1)
      dm[euid] = 0.05
      polln(W, 1)
      check(TAG .. "D1: two dwells were started (the re-contact is a NEW one) [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "dwell started:") == 2)))
      polln(W, 3)
      check(TAG .. "D2: 0.75 s after the RE-contact it still holds - an inherited stamp would have"
        .. " fired by now (" .. #W.fires .. ")", #W.fires == 0)
      polln(W, 1)
      check(TAG .. "D3: 1.00 s after the RE-contact it fires (" .. #W.fires .. ")", #W.fires == 1)
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 115 - E: the first evaluation never fires, and fast ticks add NO time ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17005, 17105
    local W = mk(uid, { name = INF, uid = euid, men_alive = 20 }, { [euid] = 0.00 })
    if boot(W, PATH, TAG, uid, "E") then
      fastn(W, 1)
      check(TAG .. "E1: the very first evaluation (a fast tick) does not fire (" .. #W.fires .. ")",
        #W.fires == 0)
      fastn(W, 4)
      check(TAG .. "E2: four more fast ticks still do not fire - the clock is the POLL's, and no"
        .. " poll has run (" .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "E3: exactly ONE dwell was started, and it is still waiting [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "dwell started:") == 1)))
      polln(W, 1)
      polln(W, 4)
      check(TAG .. "E4: the polls then complete the SAME dwell and it fires once (" .. #W.fires .. ")",
        #W.fires == 1)
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 115 - F: the pre-cast re-check re-measures the gap and SKIPS on drift ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17006, 17106
    -- reads 1-4 are the four non-firing polls, read 5 is the firing poll's
    -- picker, read 6 is the re-check - which sees the pair has drifted out.
    local W = mk(uid, { name = INF, uid = euid, men_alive = 20 }, nil,
      { 0.05, 0.05, 0.05, 0.05, 0.05, 0.30 })
    if boot(W, PATH, TAG, uid, "F") then
      polln(W, 4)
      polln(W, 1)
      check(TAG .. "F1: the dwell completed but the re-check found 0.30 m - no cast (" .. #W.fires .. ")",
        #W.fires == 0)
      check(TAG .. "F2: the skip line prints the FRESH edge [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "edge=0.30m (need < 0.10m) -> SKIPPED at re-check") == 1)))
      check(TAG .. "F3: ... and the dwell it re-verified, with both verdicts [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "dwell=1.00s of 1.00s") == 1 and cl(W, "dwell_ok=true") == 1
            and cl(W, "edge_ok=false") == 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 115 - G: the pair rows are PURGED with the unit (caster AND enemy) ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid1, euid2 = 17007, 17107, 17108
    local dm = { [euid1] = 0.05, [euid2] = 9.0 }
    local W = make_world({ can_perform = true,
      units = { { name = "sky_junk", uid = uid, owns = { DFA }, melee = false, dist_by_target = dm } },
      enemies = { { name = INF, uid = euid1, men_alive = 20 },
                  { name = INF, uid = euid2, men_alive = 20 } },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = DFA } } })
    local u = unit_of(W, uid)
    if u ~= nil then u.is_currently_flying = function() return true end end
    if boot(W, PATH, TAG, uid, "G") then
      polln(W, 1)
      local FOURTH = upvalue_from_roots({ POLL_BODY_FN, CUR_UI_FN }, "FOURTH", "table")
      local drop = upvalue_from_roots({ POLL_BODY_FN, CUR_UI_FN }, "drop_unit_by_ui_id", "function")
      check(TAG .. "G0: the dwell table and the drop routine are reachable", FOURTH ~= nil and drop ~= nil)
      local cid, e1, e2 = tostring(uid), tostring(euid1), tostring(euid2)
      -- nil-safe for the RED control: the pre-115 build has no ad_pair at all,
      -- so every read below answers an empty table instead of raising.
      local pair = (FOURTH ~= nil and FOURTH.ad_pair) or {}
      local per = pair[cid]
      check(TAG .. "G1: the contact row exists for (caster, enemy) before any drop",
        per ~= nil and per[e1] ~= nil)
      if drop ~= nil then drop(euid1) end
      per = pair[cid]
      check(TAG .. "G2: the ENEMY's death purges its row", per == nil or per[e1] == nil)
      -- the mock's enemy army still LISTs the dropped enemy, so it must also be
      -- moved out of range or the nearest-valid pick simply re-stamps it
      dm[euid1] = 9.0
      dm[euid2] = 0.05
      polln(W, 1)
      per = pair[cid]
      check(TAG .. "G3: a re-contact with the OTHER enemy stamps a fresh row", per ~= nil and per[e2] ~= nil)
      if drop ~= nil then drop(uid) end
      check(TAG .. "G4: the CASTER's death purges its whole slot", pair[cid] == nil)
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 115 - H: the gates still stop a double cast across fast ticks ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17008, 17109
    local W = mk(uid, { name = INF, uid = euid, men_alive = 20 }, { [euid] = 0.05 })
    if boot(W, PATH, TAG, uid, "H") then
      polln(W, 4)
      check(TAG .. "H0: nothing fires before the dwell is complete (" .. #W.fires .. ")", #W.fires == 0)
      polln(W, 1)
      check(TAG .. "H1: it fires on the poll that completes the dwell (" .. #W.fires .. ")", #W.fires == 1)
      fastn(W, 5)
      check(TAG .. "H2: five fast ticks in the same window cast NOTHING more (" .. #W.fires .. ")",
        #W.fires == 1)
      polln(W, 2)
      check(TAG .. "H3: nor do the next two polls, inside the 2 s guard (" .. #W.fires .. ")",
        #W.fires == 1)
      check(TAG .. "H4: exactly ONE re-checked firing line in the whole window [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "-> FIRING (re-checked)") == 1)))
      polln(W, 12)
      check(TAG .. "H5: past the guard it can fire again, and only once more (" .. #W.fires .. ")",
        #W.fires == 2)
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 115 - I: the row's own caster constraints still HOLD the drop ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17009, 17110
    local W = mk(uid, { name = INF, uid = euid, men_alive = 20 }, { [euid] = 0.02 })
    local u = unit_of(W, uid)
    if u ~= nil then u.is_currently_flying = function() return false end end
    if boot(W, PATH, TAG, uid, "I") then
      polln(W, 6)
      check(TAG .. "I1: a grounded caster never fires an air-only row, however long it sits there ("
        .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "I2: and it says why [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "-> HOLDING (this ability's row is air-only)") >= 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  if red115 then
    check("HARNESS 114 suite boundary (harness 115): N/A in the red run - the pre-115 snapshot "
      .. "still carries every harness-112 world", true)
  else
    check("HARNESS 114 suite boundary (harness 115): every earlier check ran first ("
      .. pre115 .. ", want 4614)", pre115 == 4614)
  end
  check("HARNESS 115: the ZERO-search invariant still holds after the new section (counted "
    .. find_calls .. ")", find_calls == 0)
  print("== HARNESS 115 done: checks " .. checks .. ", failures " .. failures .. " ==")
end
