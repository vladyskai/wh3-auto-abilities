-- ============================================================================
-- HARNESS 116 - THE WAIT IS MEASURED, NOT FIXED: THE ENEMY'S OWN VELOCITY.
--
-- THE USER'S RULING, verbatim: "if the enemy unit is running away, then it is
-- too soon. If the enemy moving is running towards, then it is too late. ...
-- But it must be calculated the moment the edge to edge distance is below our
-- theshold. Then, if the unit is running towards the caster, then the delay
-- would be 0. If running away, then the delay would be 2. If stationary or
-- perpedicular, then should be 1. ... the delay is dynamic in this way." and
-- "Also include logs to check the result of the function we use, like
-- ordered_position(), just in case it isn't what we think it is."
--
-- THE RULE THE WORLDS BELOW PROVE:
--   candidate = alive and number_of_men_alive() > AIR_DROP_MIN_MEN (10)
--   chosen    = the NEAREST valid candidate by unit_distance()
--   UNDER     = unit_distance(caster, chosen) < AIR_DROP_EDGE_M (0.10 m)
--   delay     = MID - SWING * proj, measured ONCE at the first UNDER of the
--               episode, floored at 0, where
--                 axis = normalise(caster.pos - enemy.pos)
--                 v    = speed * normalise(ordered_position - position)
--                 proj = dot(v, axis) / (speed * |axis|)   (clamped to +-1)
--   FIRE      = elapsed >= delay, on the poll's clock, OR a separation after
--               AIR_DROP_MIN_CONTACT_S (0.3 s) - the short-crossing fallback
--
-- THE DELAY LANDS ON THE POLL GRID (250 ms): the log prints the MEASURED delay,
-- the cast lands on the first poll at or after it. Every world asserts the
-- measured value in the log AND the poll it actually fires on.
--
-- PINS (section 0, asserted against BOTH files):
--     MID_S   AIR_DROP_DWELL_MID_S   = 1.0
--     SWING_S AIR_DROP_DWELL_SWING_S = 1.0
--     the formula line, the floor, the single measurement call site, the pair
--     row carrying delay/proj/src, the full raw-read field list, the re-check
--     reading fired.delay, the tooltip sentence, POLL_MS, both timers.
--
-- RED CONTROL (H116_LIVE / H116_ANN -> docs/backups/round116/pre116_*.lua, the
-- round-115 build): there is no AIR_DROP_DWELL_MID_S, no ad_dynamic_delay and
-- no reads line, so every 0 check and every world below fails as designed.
-- ============================================================================
function run_h116()
  if os.getenv("H116_LIVE") ~= nil then LIVE = os.getenv("H116_LIVE") end
  if os.getenv("H116_ANN") ~= nil then ANN = os.getenv("H116_ANN") end
  local red116 = (os.getenv("H116_LIVE") ~= nil) or (os.getenv("H116_ANN") ~= nil)
  local live_src = read_file(LIVE)
  local ann_src = read_file(ANN)
  local pre116 = checks
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

  -- ONE caster (sky_junk, death_from_above, airborne) and ONE enemy whose def
  -- carries the motion reads. dm = { [enemy_uid] = metres } is the caster's
  -- unit_distance answer; dseq is the per-READ sequence (the last repeats).
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
  -- AN ENEMY STATIONARY AT (px, 0, pz): no motion reads at all, so the delay
  -- must fall back to the MID baseline.
  local function still(uid, px, pz)
    return { name = INF, uid = uid, men_alive = 20, pos = { px, 0, pz },
             ordered = { px, 0, pz } }
  end
  -- AN ENEMY AT (px, 0, pz) MOVING ALONG `deg` (x/z plane, degrees from +x),
  -- with a 10 m order point in front of it - so the heading is exactly `deg`.
  -- The caster sits at the origin, so the enemy -> caster axis points 180 deg
  -- from it: deg 180 = closing (proj +1), 0 = receding (proj -1), 90/270 =
  -- perpendicular (proj 0), 135 = +0.71, 225 = -0.71.
  local function mover(uid, px, pz, deg, spd)
    local r = deg * math.pi / 180
    local dx, dz = math.cos(r), math.sin(r)
    return { name = INF, uid = uid, men_alive = 20,
             moving = true, fast = false, slow_speed = spd or 2.5, fast_speed = 4.5,
             pos = { px, 0, pz },
             ordered = { px + dx * 10, 0, pz + dz * 10 } }
  end
  local function fastn(W, n)
    if W.fast_fn == nil then return false end
    for _ = 1, n do W.fast_fn() end
    return true
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

  -- ==========================================================================
  print("== HARNESS 116 - section 0: the dynamic-delay pins, the state, the log fields (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src }, { name = "ann", src = ann_src } }) do
    local nm, s2 = f.name, f.src
    local vel = span(s2, "function FOURTH.ad_enemy_velocity(enemy)", "\nfunction FOURTH.ad_dynamic_delay")
    local dyn = span(s2, "function FOURTH.ad_dynamic_delay(caster, enemy)", "\n-- THE AIR-DROP EVALUATOR")
    local pick = span(s2, "function FOURTH.ad_pick(unit, routing)",
      "\nfunction FOURTH.evaluate_air_drop_on_infantry")
    local stamp = span(s2, "function FOURTH.ad_pair_stamp(cid, eid, delay, proj, src)", "\nend")

    check("0 " .. nm .. ": the TWO dynamic-delay constants are defined EXACTLY ONCE (1.0 s mid / 1.0 s swing)",
      cp(s2, "\nFOURTH.AIR_DROP_DWELL_MID_S = 1.0\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_DWELL_SWING_S = 1.0\n") == 1)
    check("0 " .. nm .. ": the retired FIXED dwell constant is GONE (no AIR_DROP_DWELL_S survives)",
      raw_find(s2, "AIR_DROP_DWELL_S\n", 1, true) == nil
      and raw_find(s2, "AIR_DROP_DWELL_S ", 1, true) == nil
      and raw_find(s2, "AIR_DROP_DWELL_S)", 1, true) == nil
      and raw_find(s2, "AIR_DROP_DWELL_S,", 1, true) == nil)
    check("0 " .. nm .. ": THE FORMULA is the user's, verbatim: delay = MID - SWING * proj, floored at 0",
      dyn ~= nil
      and raw_find(dyn, "local delay = FOURTH.AIR_DROP_DWELL_MID_S - (FOURTH.AIR_DROP_DWELL_SWING_S * proj)", 1, true) ~= nil
      and raw_find(dyn, "if delay < 0 then delay = 0 end", 1, true) ~= nil)
    check("0 " .. nm .. ": the cosine is dot(v, axis) / (speed * |axis|) and is CLAMPED to +-1",
      dyn ~= nil
      and raw_find(dyn, "local proj = ((vx * ax) + (vz * az)) / (speed * alen)", 1, true) ~= nil
      and raw_find(dyn, "if proj > 1 then proj = 1 elseif proj < -1 then proj = -1 end", 1, true) ~= nil)
    check("0 " .. nm .. ": the axis runs ENEMY -> CASTER (cx - enemy x, cz - enemy z)",
      dyn ~= nil
      and raw_find(dyn, "local ax, az = cx - FOURTH.ad_vread_px, cz - FOURTH.ad_vread_pz", 1, true) ~= nil)
    check("0 " .. nm .. ": the heading is ordered_position - position, normalised, with the 0.5 m floor",
      vel ~= nil
      and raw_find(vel, "hlen = math.sqrt(((ox - px) * (ox - px)) + ((oz - pz) * (oz - pz)))", 1, true) ~= nil
      and raw_find(vel, "if hlen == nil or hlen < 0.5 then", 1, true) ~= nil
      and raw_find(vel, "return 0, 0, speed, \"no-heading\"", 1, true) ~= nil)
    check("0 " .. nm .. ": EVERY read is pcall'd and falls back to a ZERO velocity + a named src",
      vel ~= nil
      and cp(vel, "pcall(function()") >= 6
      and raw_find(vel, "\"stationary\"", 1, true) ~= nil
      and raw_find(vel, "\"moving-unreadable\"", 1, true) ~= nil
      and raw_find(vel, "\"speed-unreadable\"", 1, true) ~= nil
      and raw_find(vel, "\"pos-unreadable\"", 1, true) ~= nil)
    check("0 " .. nm .. ": the delay is MEASURED EXACTLY ONCE - one call site, on the stamping branch only",
      cp(s2, "FOURTH.ad_dynamic_delay(") == 2
      and raw_find(pick, "local delay, proj, vsrc = FOURTH.ad_dynamic_delay(unit, enemy)", 1, true) ~= nil
      and raw_find(pick, "FOURTH.ad_pair_stamp(cid, eid, delay, proj, vsrc)", 1, true) ~= nil)
    check("0 " .. nm .. ": the pair row CARRIES the measurement (first, delay, proj, src)",
      stamp ~= nil
      and raw_find(stamp, "per[eid] = { first = tick_count, delay = delay, proj = proj, src = src }", 1, true) ~= nil
      and raw_find(s2, "function FOURTH.ad_pair_need(st)", 1, true) ~= nil)
    check("0 " .. nm .. ": the FIRE test uses THIS pair's own delay, never a global constant",
      pick ~= nil
      and raw_find(pick, "need_s = FOURTH.ad_pair_need(st)", 1, true) ~= nil
      and raw_find(pick, "if (under + 0.000001) >= need_s then", 1, true) ~= nil)
    check("0 " .. nm .. ": the reads line prints EVERY field the user asked for, with UNREADABLE on failure",
      vel ~= nil
      and raw_find(vel, "put_bool(\"moving\", ok_m, moving)", 1, true) ~= nil
      and raw_find(vel, "put_bool(\"is_moving_fast\", ok_f, fast)", 1, true) ~= nil
      and raw_find(vel, "put_num(\"slow_speed\", ok_s, slow)", 1, true) ~= nil
      and raw_find(vel, "put_num(\"fast_speed\", ok_q, fastsp)", 1, true) ~= nil
      and raw_find(vel, "put_xy(\"pos\", ok_p, pos)", 1, true) ~= nil
      and raw_find(vel, "put_xy(\"ordered\", ok_o, ord)", 1, true) ~= nil
      and raw_find(vel, "\"|h|=UNREADABLE\"", 1, true) ~= nil
      and raw_find(vel, "tag .. \"=UNREADABLE\"", 1, true) ~= nil)
    check("0 " .. nm .. ": the measurement line and the hold line both exist, with proj / src / delay",
      pick ~= nil
      and raw_find(pick, "\"reads: \" .. FOURTH.ad_vread", 1, true) ~= nil
      and raw_find(pick, "\" proj=\" .. FOURTH.ad_proj_text(proj)", 1, true) ~= nil
      and raw_find(pick, " src=%s delay=%.2fs (measured once for this contact)", 1, true) ~= nil
      and raw_find(pick, "\"reads(hold): \" .. FOURTH.ad_vread", 1, true) ~= nil
      and raw_find(pick, "\" proj=\" .. FOURTH.ad_proj_text(st.proj or 0)", 1, true) ~= nil
      and raw_find(pick, " src=%s delay=%.2fs held=%.2fs", 1, true) ~= nil
      and raw_find(s2, "function FOURTH.ad_proj_text(proj)", 1, true) ~= nil)
    check("0 " .. nm .. ": the hold RE-READS but never re-measures (the stored proj/src are printed)",
      pick ~= nil
      and raw_find(pick, "FOURTH.ad_proj_text(st.proj or 0)", 1, true) ~= nil
      and raw_find(pick, "tostring(st.src or \"?\")", 1, true) ~= nil)
    check("0 " .. nm .. ": the pre-cast re-check verifies the delay the cast was granted",
      raw_find(s2, "local floor_s = FOURTH.AIR_DROP_DWELL_MID_S", 1, true) ~= nil
      and raw_find(s2, "if type(fired.delay) == \"number\" then floor_s = fired.delay end", 1, true) ~= nil
      and raw_find(s2, "FOURTH.ad_fired = { under = under, delay = need_s, fallback = (on_sep or under < need_s) }", 1, true) ~= nil)
    check("0 " .. nm .. ": the short-crossing fallback and the 0.3 s floor survive untouched",
      cp(s2, "\nFOURTH.AIR_DROP_MIN_CONTACT_S = 0.3\n") == 1
      and raw_find(pick, "if under >= FOURTH.AIR_DROP_MIN_CONTACT_S then", 1, true) ~= nil)
    check("0 " .. nm .. ": the candidate filter, air_only / no_melee, the self cast and the fail-closed reads are unchanged",
      cp(s2, "\nFOURTH.AIR_DROP_MIN_MEN = 10\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_EDGE_M = 0.1\n") == 1
      and raw_find(s2, "is_currently_flying()", 1, true) ~= nil
      and raw_find(s2, "is_in_melee()", 1, true) ~= nil
      and raw_find(s2, "FOURTH.ad_air_only", 1, true) ~= nil
      and raw_find(s2, "FOURTH.ad_no_melee", 1, true) ~= nil)
    check("0 " .. nm .. ": both timers still registered (the 250 ms poll + the 0.2 s fast pass)",
      cp(s2, "bm:repeat_callback(") == 2
      and cp(s2, 'bm:repeat_callback(poll, POLL_MS, POLL_NAME)') == 1
      and cp(s2, "zz_test_deadly_onslaught_air_drop_fast") == 1
      and cp(s2, "local POLL_MS = 250") == 1)
    check("0 " .. nm .. ": the family counts are unchanged (689 entries, 12 air-drop)",
      cp(s2, 'trigger = "air_drop_on_infantry"') == 12 and cp(s2, '\t{ marker = ') == 689)
    check("0 " .. nm .. ": the tooltip sentence states the measured wait",
      raw_find(s2, "after a wait measured from that enemy", 1, true) ~= nil
      and raw_find(s2, "0 s if it is running at this unit, 1 s if it is stationary or crossing, 2 s if it is running away", 1, true) ~= nil)
    if nm == "ann" then
      check("0 ann: the reading copy stays LOG-FREE and carries the new helpers",
        raw_find(s2, "log(", 1, true) == nil
        and raw_find(s2, "function FOURTH.ad_enemy_velocity(enemy)", 1, true) ~= nil
        and raw_find(s2, "function FOURTH.ad_dynamic_delay(caster, enemy)", 1, true) ~= nil
        and raw_find(s2, "function FOURTH.ad_pair_need(st)", 1, true) ~= nil)
    else
      check("0 live: every reads / transition line carries the caster ui id",
        cp(s2, "FOURTH.ad_tag(unit)") >= 7)
    end
  end

  -- ==========================================================================
  print("== HARNESS 116 - A: an enemy CLOSING head-on (proj +1) fires on the NEXT evaluation ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17201, 17301
    local W = mk(uid, mover(euid, 5, 0, 180), { [euid] = 0.05 })
    if boot(W, PATH, TAG, uid, "A") then
      polln(W, 1)
      check(TAG .. "A1: the stamping evaluation does NOT fire (" .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "A2: it measured 0.00 s for a unit running straight in [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "proj=+1.00 src=ordered delay=0.00s (measured once for this contact)") == 1)))
      check(TAG .. "A3: the start line names the measured wait [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "[17201] death_from_above dwell started: under at gap 0.05m, waiting 0.00s") == 1)))
      polln(W, 1)
      check(TAG .. "A4: the very NEXT poll fires, once (" .. #W.fires .. ")", #W.fires == 1)
      check(TAG .. "A5: ... on the delay it measured [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "dwell satisfied after 0.25s -> FIRING") == 1)))
      check(TAG .. "A6: the re-check accepted the 0.00 s delay [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "-> FIRING (re-checked) (dwell 0.25s of 0.00s)") == 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 116 - B: PERPENDICULAR (proj 0) fires at ~1.0 s ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17202, 17302
    local W = mk(uid, mover(euid, 5, 0, 90), { [euid] = 0.05 })
    if boot(W, PATH, TAG, uid, "B") then
      polln(W, 1)
      check(TAG .. "B1: proj is 0 and the measured delay is 1.00 s [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "proj=+0.00 src=ordered delay=1.00s (measured once for this contact)") == 1)))
      polln(W, 3)
      check(TAG .. "B2: 0.75 s in it still holds (" .. #W.fires .. ")", #W.fires == 0)
      polln(W, 1)
      check(TAG .. "B3: 1.00 s in it fires, once (" .. #W.fires .. ")", #W.fires == 1)
      polln(W, 3)
      check(TAG .. "B4: and the contact is consumed - nothing else fires on it (" .. #W.fires .. ")",
        #W.fires == 1)
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 116 - C: RECEDING (proj -1) fires at ~2.0 s ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17203, 17303
    local W = mk(uid, mover(euid, 5, 0, 0), { [euid] = 0.05 })
    if boot(W, PATH, TAG, uid, "C") then
      polln(W, 1)
      check(TAG .. "C1: proj is -1 and the measured delay is 2.00 s [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "proj=-1.00 src=ordered delay=2.00s (measured once for this contact)") == 1)))
      polln(W, 7)
      check(TAG .. "C2: 1.75 s in it STILL holds - a fixed 1 s wait would have fired long ago ("
        .. #W.fires .. ")", #W.fires == 0)
      polln(W, 1)
      check(TAG .. "C3: 2.00 s in it fires, once (" .. #W.fires .. ")", #W.fires == 1)
      check(TAG .. "C4: the held line carried the measured 2.00 s [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "dwell: under 1.75s of 2.00s") == 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 116 - D: a 45-DEGREE approach (proj +0.71) measures 0.29 s ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17204, 17304
    local W = mk(uid, mover(euid, 5, 0, 135), { [euid] = 0.05 })
    if boot(W, PATH, TAG, uid, "D") then
      polln(W, 1)
      check(TAG .. "D1: the interpolation, not a table: proj +0.71 -> delay 0.29 s [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "proj=+0.71 src=ordered delay=0.29s (measured once for this contact)") == 1)))
      polln(W, 1)
      check(TAG .. "D2: 0.25 s is short of the measured 0.29 s - it holds (" .. #W.fires .. ")",
        #W.fires == 0)
      polln(W, 1)
      check(TAG .. "D3: 0.50 s is the first poll at or after it - it fires (" .. #W.fires .. ")",
        #W.fires == 1)
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 116 - E: a 135-DEGREE approach (heading 45 deg off the axis, proj -0.71) measures 1.71 s ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17205, 17305
    local W = mk(uid, mover(euid, 5, 0, 45), { [euid] = 0.05 })
    if boot(W, PATH, TAG, uid, "E") then
      polln(W, 1)
      check(TAG .. "E1: the other side of the interpolation: proj -0.71 -> delay 1.71 s [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "proj=-0.71 src=ordered delay=1.71s (measured once for this contact)") == 1)))
      polln(W, 6)
      check(TAG .. "E2: 1.50 s in it holds (" .. #W.fires .. ")", #W.fires == 0)
      polln(W, 1)
      check(TAG .. "E3: 1.75 s is the first poll at or after 1.71 s - it fires (" .. #W.fires .. ")",
        #W.fires == 1)
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 116 - F: an ATTACKING unit (ordered_position == position) falls back to 1.0 s and says why ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17206, 17306
    -- moving, but the order point IS the unit: the documented "attacking"
    -- shape, |h| = 0.0
    local W = mk(uid, { name = INF, uid = euid, men_alive = 20, moving = true,
                        slow_speed = 2.5, fast_speed = 4.5,
                        pos = { 5, 0, 0 }, ordered = { 5, 0, 0 } }, { [euid] = 0.05 })
    if boot(W, PATH, TAG, uid, "F") then
      polln(W, 1)
      check(TAG .. "F1: no heading -> src=no-heading, delay back to 1.00 s [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "ordered=(5.0,0.0) |h|=0.0 proj=+0.00 src=no-heading delay=1.00s") == 1)))
      polln(W, 4)
      check(TAG .. "F2: the 1.00 s baseline fires on the poll that completes it (" .. #W.fires .. ")",
        #W.fires == 1)
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 116 - G: the delay is measured ONCE - a turn mid-contact changes nothing ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17207, 17307
    local edef = mover(euid, 5, 0, 90)          -- perpendicular: 1.00 s
    local W = mk(uid, edef, { [euid] = 0.05 })
    if boot(W, PATH, TAG, uid, "G") then
      polln(W, 1)
      -- THE TURN: the order point moves to 3 m behind the unit. A re-measure
      -- would see a completely different heading and a different delay.
      edef.ordered = { 5, 0, 3 }
      polln(W, 3)
      check(TAG .. "G1: exactly ONE measurement line in the episode [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "reads: moving=") == 1)))
      check(TAG .. "G2: the hold lines keep printing the MEASURED proj and delay, not the fresh ones [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "reads(hold): moving=true is_moving_fast=false slow_speed=2.50 fast_speed=4.50 pos=(5.0,0.0) ordered=(5.0,3.0) |h|=3.0 proj=+0.00 src=ordered delay=1.00s held=0.75s") == 1)))
      check(TAG .. "G3: 0.75 s in it still holds - an inherited re-measure would have moved the target ("
        .. #W.fires .. ")", #W.fires == 0)
      polln(W, 1)
      check(TAG .. "G4: it fires at the 1.00 s it measured at contact, not at anything the turn implies ("
        .. #W.fires .. ")", #W.fires == 1)
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 116 - H: a RE-CONTACT measures again, fresh ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17208, 17308
    local dm = { [euid] = 0.05 }
    local edef = mover(euid, 5, 0, 90)          -- first contact: 1.00 s
    local W = mk(uid, edef, dm)
    if boot(W, PATH, TAG, uid, "H") then
      polln(W, 1)
      dm[euid] = 0.50
      polln(W, 1)
      check(TAG .. "H1: a 0.25 s contact that separates CANCELS (under the 0.30 s floor) ("
        .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "H2: ... and the cancel line reports the delay it was waiting for [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "the dwell is 1.00s") == 1)))
      -- THE SECOND CONTACT, from a unit now running AWAY: 2.00 s
      edef.ordered = { 15, 0, 0 }
      dm[euid] = 0.05
      polln(W, 1)
      check(TAG .. "H3: the re-contact measured AGAIN - a second measurement line, now 2.00 s [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "reads: moving=") == 2
            and cl(W, "proj=-1.00 src=ordered delay=2.00s (measured once for this contact)") == 1)))
      polln(W, 7)
      check(TAG .. "H4: the fresh 2.00 s is what it waits for (1.75 s in: " .. #W.fires .. ")",
        #W.fires == 0)
      polln(W, 1)
      check(TAG .. "H5: ... and it fires on its own measured tick (" .. #W.fires .. ")", #W.fires == 1)
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 116 - I: UNREADABLE reads print UNREADABLE and fall back to 1.0 s ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    -- I1: the speed read for the unit's state raises
    local uid1, e1 = 17209, 17309
    local d1 = mover(e1, 5, 0, 180)
    d1.slow_speed_raises = true
    local W1 = mk(uid1, d1, { [e1] = 0.05 })
    if boot(W1, PATH, TAG, uid1, "I1") then
      polln(W1, 1)
      check(TAG .. "I1a: slow_speed=UNREADABLE is printed verbatim [live log]",
        lg((TAG ~= "[live] ") or (cl(W1, "slow_speed=UNREADABLE fast_speed=4.50") == 1)))
      check(TAG .. "I1b: ... and the delay falls back to 1.00 s with its reason [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W1, "proj=+0.00 src=speed-unreadable delay=1.00s") == 1)))
      polln(W1, 4)
      check(TAG .. "I1c: the baseline fires at 1.00 s (" .. #W1.fires .. ")", #W1.fires == 1)
      tally(W1)
    end
    -- I2: position() raises
    local uid2, e2 = 17210, 17310
    local d2 = mover(e2, 5, 0, 180)
    d2.position_raises = true
    local W2 = mk(uid2, d2, { [e2] = 0.05 })
    if boot(W2, PATH, TAG, uid2, "I2") then
      polln(W2, 1)
      check(TAG .. "I2a: pos=UNREADABLE is printed verbatim [live log]",
        lg((TAG ~= "[live] ") or (cl(W2, "pos=UNREADABLE ordered=") == 1)))
      check(TAG .. "I2b: ... |h| cannot be computed, so it says UNREADABLE too [live log]",
        lg((TAG ~= "[live] ") or (cl(W2, "|h|=UNREADABLE proj=+0.00 src=pos-unreadable delay=1.00s") == 1)))
      tally(W2)
    end
    -- I3: ordered_position() raises
    local uid3, e3 = 17211, 17311
    local d3 = mover(e3, 5, 0, 180)
    d3.ordered_raises = true
    local W3 = mk(uid3, d3, { [e3] = 0.05 })
    if boot(W3, PATH, TAG, uid3, "I3") then
      polln(W3, 1)
      check(TAG .. "I3a: ordered=UNREADABLE is printed verbatim [live log]",
        lg((TAG ~= "[live] ") or (cl(W3, "ordered=UNREADABLE |h|=UNREADABLE") == 1)))
      check(TAG .. "I3b: ... the heading is unknown, so no-heading and 1.00 s [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W3, "proj=+0.00 src=no-heading delay=1.00s") == 1)))
      tally(W3)
    end
  end

  -- ==========================================================================
  print("== HARNESS 116 - J: the short-crossing fallback, the gates and the re-check still govern ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17212, 17312
    local dm = { [euid] = 0.05 }
    local W = mk(uid, mover(euid, 5, 0, 90), dm)     -- 1.00 s, never reached
    if boot(W, PATH, TAG, uid, "J") then
      polln(W, 1)
      polln(W, 2)
      dm[euid] = 0.40
      polln(W, 1)
      check(TAG .. "J1: a 0.75 s contact that separates FIRES on the way out (" .. #W.fires .. ")",
        #W.fires == 1)
      check(TAG .. "J2: the fallback line states the time and the delay that was measured [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "short crossing: under for 0.75s (>= 0.30s) -> FIRING on separation (gap 0.40m, the delay measured was 1.00s)") == 1)))
      check(TAG .. "J3: the re-check accepts it and says what it held [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "(short crossing: held 0.75s of 0.30s)") == 1)))
      fastn(W, 5)
      polln(W, 2)
      check(TAG .. "J4: five fast ticks and two polls inside the 2 s guard cast NOTHING more ("
        .. #W.fires .. ")", #W.fires == 1)
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 116 - K: the re-check re-measures the gap and the delay before the cast ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17213, 17313
    -- reads 1-4 are the four non-firing polls, read 5 the firing poll's picker,
    -- read 6 the re-check - which sees that the pair has drifted out.
    local W = mk(uid, mover(euid, 5, 0, 90), nil, { 0.05, 0.05, 0.05, 0.05, 0.05, 0.30 })
    if boot(W, PATH, TAG, uid, "K") then
      polln(W, 4)
      polln(W, 1)
      check(TAG .. "K1: the delay completed but the re-check found 0.30 m - no cast (" .. #W.fires .. ")",
        #W.fires == 0)
      check(TAG .. "K2: the skip line prints the FRESH edge and the delay it verified [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "edge=0.30m (need < 0.10m) -> SKIPPED at re-check") == 1
            and cl(W, "dwell=1.00s of 1.00s") == 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  if red116 then
    check("HARNESS 115 suite boundary (harness 116): N/A in the red run - the pre-116 snapshot "
      .. "still carries every harness-115 world", true)
  else
    check("HARNESS 115 suite boundary (harness 116): every earlier check ran first ("
      .. pre116 .. ", want 4739)", pre116 == 4739)
  end
  check("HARNESS 116: the ZERO-search invariant still holds after the new section (counted "
    .. find_calls .. ")", find_calls == 0)
  print("== HARNESS 116 done: checks " .. checks .. ", failures " .. failures .. " ==")
end
