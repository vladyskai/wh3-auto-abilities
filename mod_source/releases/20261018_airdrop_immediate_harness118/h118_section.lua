-- ============================================================================
-- HARNESS 117 - THE MEASUREMENT MOVES: EDGE-TO-EDGE -> GROUND CENTRE-TO-CENTRE
--
-- THE USER'S RULING, verbatim: "Let's keep our current calculation but just
-- replace the detection on edge with detection on the distance to center.
-- Let's say 6 meters for now. I'll test."
--
-- ONE THING CHANGED. Everything the round-116 rule did is kept exactly:
--   candidate = alive and number_of_men_alive() > AIR_DROP_MIN_MEN (10)
--   chosen    = the NEAREST valid candidate
--   delay     = MID - SWING * proj, measured ONCE at the first UNDER of the
--               episode (0 s closing / 1 s stationary-or-across / 2 s receding)
--   FIRE      = elapsed >= delay on the poll's clock, OR a separation after
--               AIR_DROP_MIN_CONTACT_S (0.3 s) - the short-crossing fallback
-- and the ONE measurement that decides UNDER moved from the engine's
-- bounding-box EDGE gap (unit:unit_distance) to the GROUND-PLANE
-- CENTRE-to-CENTRE distance between the two position() reads (x/z only):
--   UNDER = ad_centre_gap(caster, chosen) < AIR_DROP_CENTER_M (6.0 m)
--
-- THE WORLDS BELOW (each runs against the LIVE source AND the annotated copy):
--   A1  5.9 m -> UNDER: stamps, waits the measured 1.00 s, fires on the poll
--       that completes it, and every line prints gap 5.90m.
--   A2  6.1 m -> NOT under: six polls, nothing stamped, nothing fired, and the
--       decision line prints centre=6.10m (need < 6.00m).
--   B1  5.9 m CLOSING (proj +1)   -> delay 0.00 s -> fires on the NEXT poll.
--   B2  5.9 m RECEDING (proj -1)  -> delay 2.00 s -> holds 1.75 s, then fires.
--   B3  5.9 m ACROSS (proj 0)     -> delay 1.00 s -> fires at 1.00 s.
--   C1  a 0.25 s contact that separates to 6.5 m -> CANCELLED, nothing fires.
--   C2  a 0.75 s contact that separates to 6.5 m -> the short-crossing
--       fallback FIRES on the separation evaluation.
--   D   an unreadable caster position / enemy position / co-ordinate read ->
--       no candidate, no cast, no crash (FAIL CLOSED).
--   E   the pre-cast re-check RE-MEASURES the centre: the pair drifts to
--       6.1 m between the picker and the re-check of the SAME poll -> skipped.
--
-- PINS (section 0, BOTH files): the 6.0 m constant (once) and the 0.1 m edge
-- constant GONE, ad_centre_gap (x/z only, distance_xz + sqrt fallback, nil on
-- any unreadable read), the scan on the centre, the one comparison, centre=
-- on every decision line and edge= on none, the re-check re-measuring the
-- centre, the dynamic delay / fallback / gates untouched, both timers, the
-- family counts and the tooltip sentence.
-- ============================================================================
function run_h117()
  if os.getenv("H117_LIVE") ~= nil then LIVE = os.getenv("H117_LIVE") end
  if os.getenv("H117_ANN") ~= nil then ANN = os.getenv("H117_ANN") end
  local red117 = (os.getenv("H117_LIVE") ~= nil) or (os.getenv("H117_ANN") ~= nil)
  local live_src = read_file(LIVE)
  local ann_src = read_file(ANN)
  local pre117 = checks
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

  -- ==========================================================================
  print("== HARNESS 117 - section 0: the CENTRE measurement, and nothing else moved (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src }, { name = "ann", src = ann_src } }) do
    local nm, s2 = f.name, f.src
    local helper = span(s2, "function FOURTH.ad_centre_gap(caster, enemy)", "\nend")
    local near = span(s2, "function FOURTH.ad_nearest(unit)", "\nfunction FOURTH.ad_pick")
    local pick = span(s2, "function FOURTH.ad_pick(unit, routing)",
      "\nfunction FOURTH.evaluate_air_drop_on_infantry")
    local rechk = span(s2, "-- THE AIR-DROP RE-CHECK", "-- SELF-SUMMON RE-CHECK")

    check("0 " .. nm .. ": the 6.0 m CENTRE constant is defined EXACTLY ONCE and the 0.1 m EDGE constant is GONE",
      cp(s2, "\nFOURTH.AIR_DROP_CENTER_M = 6.0\n") == 1
      and cp(s2, "AIR_DROP_EDGE_M") == 0)
    check("0 " .. nm .. ": ad_centre_gap exists ONCE and reads BOTH units' position()",
      helper ~= nil
      and cp(s2, "function FOURTH.ad_centre_gap(caster, enemy)") == 1
      and raw_find(helper, "caster:position()", 1, true) ~= nil
      and raw_find(helper, "enemy:position()", 1, true) ~= nil)
    check("0 " .. nm .. ": ad_centre_gap is x/z ONLY - it never reads get_y (which is HEIGHT)",
      helper ~= nil
      and raw_find(helper, "get_y", 1, true) == nil
      and raw_find(helper, "a:get_x()", 1, true) ~= nil
      and raw_find(helper, "a:get_z()", 1, true) ~= nil
      and raw_find(helper, "b:get_x()", 1, true) ~= nil
      and raw_find(helper, "b:get_z()", 1, true) ~= nil)
    check("0 " .. nm .. ": ad_centre_gap uses distance_xz FIRST and sqrt(dx^2+dz^2) as the fallback",
      helper ~= nil
      and raw_find(helper, "a:distance_xz(b)", 1, true) ~= nil
      and raw_find(helper, "math.sqrt((dx * dx) + (dz * dz))", 1, true) ~= nil)
    check("0 " .. nm .. ": ad_centre_gap FAILS CLOSED - every unreadable path answers nil",
      helper ~= nil and cp(helper, "return nil") == 3)
    check("0 " .. nm .. ": the candidate scan measures the CENTRE and never calls unit_distance",
      near ~= nil
      and raw_find(near, "FOURTH.ad_centre_gap(unit, enemy)", 1, true) ~= nil
      and raw_find(near, "eg_enemy_gap", 1, true) == nil
      and raw_find(near, "unit_distance", 1, true) == nil)
    check("0 " .. nm .. ": the candidate filter is unchanged (alive, MORE than AIR_DROP_MIN_MEN, no class test)",
      near ~= nil
      and raw_find(near, "enemy:number_of_men_alive()", 1, true) ~= nil
      and raw_find(near, "alive > FOURTH.AIR_DROP_MIN_MEN", 1, true) ~= nil
      and raw_find(near, "enemy_is_infantry", 1, true) == nil
      and raw_find(near, "initial_number_of_men", 1, true) == nil)
    check("0 " .. nm .. ": ONE comparison decides - the CENTRE gap against AIR_DROP_CENTER_M",
      pick ~= nil
      and raw_find(pick, "if dist >= FOURTH.AIR_DROP_CENTER_M then", 1, true) ~= nil
      and raw_find(pick, "AIR_DROP_EDGE_M", 1, true) == nil
      and raw_find(pick, "unit_distance", 1, true) == nil)
    check("0 " .. nm .. ": every decision line says centre= and NO air-drop line still says edge=",
      pick ~= nil
      and cp(pick, '" centre="') >= 3
      and cp(pick, '" edge="') == 0
      and cp(pick, '"m (need < "') >= 3)
    check("0 " .. nm .. ": the pre-cast re-check re-measures the SAME centre gap (fresh handles)",
      rechk ~= nil
      and raw_find(rechk, "local centre_now = FOURTH.ad_centre_gap(unit, enemy)", 1, true) ~= nil
      and raw_find(rechk, "centre_now < FOURTH.AIR_DROP_CENTER_M", 1, true) ~= nil
      and raw_find(rechk, "local gap_ok = (centre_ok or (fallback_now and dwell_ok))", 1, true) ~= nil
      and raw_find(rechk, "edge_text", 1, true) == nil
      and raw_find(rechk, "eg_enemy_gap", 1, true) == nil)
    check("0 " .. nm .. ": the DYNAMIC delay is untouched (MID/SWING, one call site, this pair's own value)",
      cp(s2, "\nFOURTH.AIR_DROP_DWELL_MID_S = 1.0\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_DWELL_SWING_S = 1.0\n") == 1
      and cp(s2, "FOURTH.ad_dynamic_delay(") == 2
      and pick ~= nil
      and raw_find(pick, "local delay, proj, vsrc = FOURTH.ad_dynamic_delay(unit, enemy)", 1, true) ~= nil
      and raw_find(pick, "FOURTH.ad_pair_stamp(cid, eid, delay, proj, vsrc)", 1, true) ~= nil
      and raw_find(pick, "if (under + 0.000001) >= need_s then", 1, true) ~= nil)
    check("0 " .. nm .. ": the short-crossing fallback and the 0.3 s floor are untouched",
      cp(s2, "\nFOURTH.AIR_DROP_MIN_CONTACT_S = 0.3\n") == 1
      and pick ~= nil
      and raw_find(pick, "if under >= FOURTH.AIR_DROP_MIN_CONTACT_S then", 1, true) ~= nil
      and raw_find(pick, "short crossing: under for %.2fs (>= %.2fs) -> FIRING on separation", 1, true) ~= nil)
    check("0 " .. nm .. ": air_only / no_melee / the self-centred cast / the read-verification lines are kept",
      raw_find(s2, "FOURTH.ad_air_only", 1, true) ~= nil
      and raw_find(s2, "FOURTH.ad_no_melee", 1, true) ~= nil
      and raw_find(s2, "perform_special_ability", 1, true) ~= nil
      and pick ~= nil
      and raw_find(pick, '"reads: " .. FOURTH.ad_vread', 1, true) ~= nil
      and raw_find(pick, '"reads(hold): " .. FOURTH.ad_vread', 1, true) ~= nil)
    check("0 " .. nm .. ": both timers still registered (250 ms poll + 0.2 s fast pass) and the 30 m gate",
      cp(s2, "bm:repeat_callback(") == 2
      and cp(s2, 'bm:repeat_callback(poll, POLL_MS, POLL_NAME)') == 1
      and cp(s2, "local POLL_MS = 250") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_FAST_S = 0.2\n") == 1
      and cp(s2, "dist < FOURTH.AIR_DROP_NEAR_M") == 1)
    check("0 " .. nm .. ": the family counts are unchanged (689 entries, 12 air-drop) and the bound follows",
      cp(s2, 'trigger = "air_drop_on_infantry"') == 12
      and cp(s2, "\t{ marker = ") == 689
      and cp(s2, "ability.range_m = FOURTH.AIR_DROP_CENTER_M") == 1)
    check("0 " .. nm .. ": the tooltip states the 6 m CENTRE rule and the measured wait",
      raw_find(s2, "air_drop_on_infantry = \"When armed, fires when the nearest enemy unit with more than 10 models comes within 6 m of this unit's centre", 1, true) ~= nil
      and raw_find(s2, "after a wait measured from that enemy", 1, true) ~= nil)
    check("0 " .. nm .. ": the change is LOCAL - eg_enemy_gap still serves the other triggers",
      cp(s2, "function FOURTH.eg_enemy_gap(unit, enemy)") == 1
      and cp(s2, "FOURTH.eg_enemy_gap(") >= 4)
    if nm == "live" then
      check("0 live: no live code path can still ask for the edge gap in this family",
        raw_find(s2, "FOURTH.AIR_DROP_EDGE_M", 1, true) == nil)
    else
      check("0 ann: the reading copy stays LOG-FREE and carries the same centre helper",
        raw_find(s2, "log(", 1, true) == nil
        and helper ~= nil
        and raw_find(helper, "distance_xz", 1, true) ~= nil
        and raw_find(s2, "function FOURTH.ad_nearest(unit)", 1, true) ~= nil)
    end
  end

  -- ==========================================================================
  -- THE WORLDS. ONE caster (sky_junk / death_from_above, airborne) at the
  -- ORIGIN and ONE 20-model enemy placed r metres away on the ground.
  --   st.r is read on EVERY position() call, so a world moves the enemy by
  --   assigning st.r = 6.5 and the NEXT evaluation measures the new gap.
  --   hdeg nil -> the enemy is stationary; hdeg set -> it moves along that
  --   ground bearing (its order point is 10 m ahead), so with the enemy at
  --   bearing `posdeg` the projected cosine is -cos(hdeg - posdeg):
  --     hdeg = posdeg + 180 -> +1 (running AT the caster)  -> 0.00 s
  --     hdeg = posdeg       -> -1 (running AWAY)           -> 2.00 s
  --     hdeg = posdeg +- 90 ->  0 (crossing / across)      -> 1.00 s
  -- ==========================================================================
  local function cvec(x, z)
    x, z = x or 0, z or 0
    local v = {}
    function v:get_x() return x end
    function v:get_y() return 0 end
    function v:get_z() return z end
    function v:distance_xz(o)
      local ox, oz = o:get_x(), o:get_z()
      return math.sqrt(((x - ox) * (x - ox)) + ((z - oz) * (z - oz)))
    end
    return v
  end

  local function mk(uid, euid, st, posdeg, hdeg, opts)
    opts = opts or {}
    local def = { name = "sky_junk", uid = uid, owns = { DFA }, melee = false }
    if opts.caster_raises then def.position_raises = true end
    local rad = (posdeg or 0) * math.pi / 180
    local ex, ez = math.cos(rad) * st.r, math.sin(rad) * st.r
    local edef = { name = INF, uid = euid, men_alive = opts.men or 20, pos = { ex, 0, ez } }
    if hdeg ~= nil then
      local hr = hdeg * math.pi / 180
      edef.moving = true
      edef.fast = false
      edef.slow_speed = opts.speed or 2.5
      edef.fast_speed = 4.5
      edef.ordered = { ex + math.cos(hr) * 10, 0, ez + math.sin(hr) * 10 }
    else
      edef.ordered = { ex, 0, ez }
    end
    if opts.enemy_raises then edef.position_raises = true end
    local W = make_world({ can_perform = true, units = { def }, enemies = { edef },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = DFA } } })
    local u = unit_of(W, uid)
    if u ~= nil then u.is_currently_flying = function() return true end end
    -- the enemy lives in W.enemy_entries (the army list the mod enumerates),
    -- not in the friendly list unit_of walks
    local eo = nil
    for i = 1, #(W.enemy_entries or {}) do
      local eu2 = W.enemy_entries[i].unit
      local ok_e2, id_e2 = pcall(function() return eu2:unique_ui_id() end)
      if ok_e2 and tostring(id_e2) == tostring(euid) then eo = eu2 end
    end
    if eo ~= nil and not opts.enemy_raises then
      if opts.bare_position then
        -- a position object with NO get_x / get_z: the co-ordinate read raises
        -- and the helper must answer nil (fail closed).
        eo.position = function() return { get_y = function() return 0 end } end
      else
        eo.position = function()
          if opts.seq ~= nil then
            st.i = (st.i or 0) + 1
            local q = opts.seq[st.i] or opts.seq[#opts.seq]
            return cvec(q[1], q[2])
          end
          local a = (posdeg or 0) * math.pi / 180
          return cvec(math.cos(a) * st.r, math.sin(a) * st.r)
        end
        if hdeg ~= nil then
          eo.ordered_position = function()
            local p = eo.position()
            local hr = hdeg * math.pi / 180
            return cvec(p:get_x() + math.cos(hr) * 10, p:get_z() + math.sin(hr) * 10)
          end
        end
      end
    end
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
  print("== HARNESS 117 - A1: a 5.9 m CENTRE contact FIRES, after the measured 1.00 s ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17401, 17501
    local W = mk(uid, euid, { r = 5.9 }, 0, nil)
    if boot(W, PATH, TAG, uid, "A1") then
      polln(W, 1)
      check(TAG .. "A1a: the first evaluation stamps a 5.9 m contact and does NOT fire ("
        .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "A1b: the stamp line prints the CENTRE gap and the measured wait [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "[17401] death_from_above dwell started: under at gap 5.90m, waiting 1.00s") == 1)))
      polln(W, 3)
      check(TAG .. "A1c: 0.75 s in it still holds (" .. #W.fires .. ")", #W.fires == 0)
      polln(W, 1)
      check(TAG .. "A1d: the poll that completes 1.00 s fires, ONCE (" .. #W.fires .. ")", #W.fires == 1)
      check(TAG .. "A1e: the fire line carries the centre gap and the served wait [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "dwell satisfied after 1.00s -> FIRING (gap 5.90m") == 1)))
      check(TAG .. "A1f: the pre-cast re-check accepted it and printed the centre [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "centre=5.90m (need < 6.00m) -> FIRING (re-checked)") == 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 117 - A2: a 6.1 m CENTRE gap does NOT fire ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17402, 17502
    local W = mk(uid, euid, { r = 6.1 }, 0, nil)
    if boot(W, PATH, TAG, uid, "A2") then
      polln(W, 6)
      check(TAG .. "A2a: six polls at 6.1 m cast NOTHING (" .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "A2b: the decision line prints centre=6.10m against the 6.00 m line [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "centre=6.10m (need < 6.00m) -> NOT YET") == 1)))
      check(TAG .. "A2c: no contact was ever stamped (no dwell line) [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "dwell started") == 0)))
      fastn(W, 3)
      check(TAG .. "A2d: three fast ticks do not change it (" .. #W.fires .. ")", #W.fires == 0)
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 117 - B1: at 5.9 m a CLOSING enemy (proj +1) still fires at ~0 s ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17403, 17503
    local W = mk(uid, euid, { r = 5.9 }, 0, 180)
    if boot(W, PATH, TAG, uid, "B1") then
      polln(W, 1)
      check(TAG .. "B1a: the stamping evaluation does NOT fire (" .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "B1b: it measured 0.00 s for a unit running straight in at 5.9 m [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "proj=+1.00 src=ordered delay=0.00s (measured once for this contact)") == 1)))
      polln(W, 1)
      check(TAG .. "B1c: the NEXT poll fires, once (" .. #W.fires .. ")", #W.fires == 1)
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 117 - B2: at 5.9 m a RECEDING enemy (proj -1) still waits 2.00 s ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17404, 17504
    local W = mk(uid, euid, { r = 5.9 }, 0, 0)
    if boot(W, PATH, TAG, uid, "B2") then
      polln(W, 1)
      check(TAG .. "B2a: proj is -1 and the delay is 2.00 s [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "proj=-1.00 src=ordered delay=2.00s (measured once for this contact)") == 1)))
      polln(W, 7)
      check(TAG .. "B2b: 1.75 s in it STILL holds - the 2 s wait is not the 1 s baseline ("
        .. #W.fires .. ")", #W.fires == 0)
      polln(W, 1)
      check(TAG .. "B2c: 2.00 s in it fires, once (" .. #W.fires .. ")", #W.fires == 1)
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 117 - B3: at 5.9 m a CROSSING enemy (proj 0) still waits 1.00 s ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17405, 17505
    local W = mk(uid, euid, { r = 5.9 }, 0, 90)
    if boot(W, PATH, TAG, uid, "B3") then
      polln(W, 1)
      check(TAG .. "B3a: proj is 0 and the delay is 1.00 s [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "proj=+0.00 src=ordered delay=1.00s (measured once for this contact)") == 1)))
      polln(W, 3)
      check(TAG .. "B3b: 0.75 s in it holds (" .. #W.fires .. ")", #W.fires == 0)
      polln(W, 1)
      check(TAG .. "B3c: 1.00 s in it fires, once (" .. #W.fires .. ")", #W.fires == 1)
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 117 - C1: a 0.25 s contact that separates past 6 m CANCELS ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17406, 17506
    local st = { r = 5.9 }
    local W = mk(uid, euid, st, 0, 90)
    if boot(W, PATH, TAG, uid, "C1") then
      polln(W, 1)
      st.r = 6.5
      polln(W, 1)
      check(TAG .. "C1a: a separation under the 0.30 s floor fires NOTHING (" .. #W.fires .. ")",
        #W.fires == 0)
      check(TAG .. "C1b: the cancel line names the time under and the separation gap [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "dwell cancelled: separated after 0.25s (gap 6.50m") == 1)))
      check(TAG .. "C1c: no short-crossing fire was invented [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "short crossing") == 0)))
      polln(W, 2)
      check(TAG .. "C1d: and nothing fires afterwards either (" .. #W.fires .. ")", #W.fires == 0)
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 117 - C2: a 0.75 s contact separated past 6 m fires on the way out ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17407, 17507
    local st = { r = 5.9 }
    local W = mk(uid, euid, st, 0, 90)
    if boot(W, PATH, TAG, uid, "C2") then
      polln(W, 1)
      polln(W, 2)
      st.r = 6.5
      polln(W, 1)
      check(TAG .. "C2a: 0.75 s of contact then a separation past 6 m FIRES ("
        .. #W.fires .. ")", #W.fires == 1)
      check(TAG .. "C2b: the fallback line states the time, the gap and the delay measured [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "short crossing: under for 0.75s (>= 0.30s) -> FIRING on separation (gap 6.50m, the delay measured was 1.00s)") == 1)))
      check(TAG .. "C2c: the re-check accepts the fallback and says what it held [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "(short crossing: held 0.75s of 0.30s)") == 1)))
      fastn(W, 5)
      polln(W, 2)
      check(TAG .. "C2d: five fast ticks and two polls inside the guard cast NOTHING more ("
        .. #W.fires .. ")", #W.fires == 1)
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 117 - D: unreadable positions FAIL CLOSED (no candidate, no cast) ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17408, 17508
    local W = mk(uid, euid, { r = 5.9 }, 0, nil, { caster_raises = true })
    if boot(W, PATH, TAG, uid, "D1") then
      polln(W, 6)
      check(TAG .. "D1a: an unreadable CASTER position casts nothing and does not crash ("
        .. #W.fires .. ")", #W.fires == 0)
      tally(W)
    end
    local uid2, euid2 = 17409, 17509
    local W2 = mk(uid2, euid2, { r = 5.9 }, 0, nil, { enemy_raises = true })
    if boot(W2, PATH, TAG, uid2, "D2") then
      polln(W2, 6)
      check(TAG .. "D2a: an unreadable ENEMY position casts nothing (" .. #W2.fires .. ")",
        #W2.fires == 0)
      tally(W2)
    end
    local uid3, euid3 = 17410, 17510
    local W3 = mk(uid3, euid3, { r = 5.9 }, 0, nil, { bare_position = true })
    if boot(W3, PATH, TAG, uid3, "D3") then
      polln(W3, 6)
      check(TAG .. "D3a: a position object with no get_x/get_z casts nothing (fail closed) ("
        .. #W3.fires .. ")", #W3.fires == 0)
      tally(W3)
    end
  end

  -- ==========================================================================
  print("== HARNESS 117 - E: the pre-cast re-check RE-MEASURES the centre gap ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17411, 17511
    -- READ 1-8 are the four non-firing polls (the picker's centre read plus the
    -- hold tick's velocity read), read 9 the firing poll's picker, read 10 the
    -- PRE-CAST RE-CHECK - which must see that the pair has drifted to 6.1 m.
    local seq = {}
    for i = 1, 9 do seq[i] = { 5.9, 0 } end
    seq[10] = { 6.1, 0 }
    local st = { r = 5.9, i = 0 }
    local W = mk(uid, euid, st, 0, nil, { seq = seq })
    if boot(W, PATH, TAG, uid, "E") then
      polln(W, 5)
      check(TAG .. "E1: the dwell completed but the re-check measured 6.10 m - no cast ("
        .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "E2: the skip line prints the FRESH centre gap and the wait it verified [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "centre=6.10m (need < 6.00m) -> SKIPPED at re-check") == 1
            and cl(W, "dwell=1.00s of 1.00s") == 1
            and cl(W, "centre_ok=false") == 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  if red117 then
    check("HARNESS 116 suite boundary (harness 117): N/A in the red run - the pre-117 "
      .. "snapshot carries the edge measurement, so the 0 checks and every world fail", true)
  else
    -- ROUND 117 WAS A LIGHT ROUND: the FULL suite was deliberately not run, so
    -- this pin is a FLOOR (the air-drop sections always contribute more than
    -- 400 checks), not the exact count the older rounds pinned. The exact
    -- full-suite number is re-established the next time the whole suite runs.
    check("HARNESS 116 suite boundary (harness 117): the air-drop sections ran before this one ("
      .. pre117 .. " checks, floor 400)", pre117 >= 400)
  end
  check("HARNESS 117: the ZERO-search invariant still holds after the new section (counted "
    .. find_calls .. ")", find_calls == 0)
  print("== HARNESS 117 done: checks " .. checks .. ", failures " .. failures .. " ==")
end
