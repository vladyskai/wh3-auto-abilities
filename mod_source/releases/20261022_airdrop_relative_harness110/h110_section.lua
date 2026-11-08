-- ============================================================================
-- HARNESS 110 - THE AIR DROP: TWO-BODY RELATIVE-MOTION PREDICTION (round 110)
--
-- THE USER'S THIRD FIELD REPORT: firing on Drop Rocks (Terradon Riders) is
-- still early or misses - the rocks take about 1-2 s to fall and the flier
-- keeps moving, so the enemy that was UNDER the caster when the button was
-- pressed is not under the rocks when they land.
--
-- THE ASSUMPTION UNDER TEST (the user's ruling): the ordnance does NOT inherit
-- the caster's velocity, so it lands STRAIGHT DOWN from the caster's position at
-- RELEASE. The button therefore has to predict BOTH bodies:
--     caster(t+d) = caster(t) + v_caster * d      <- the impact point
--     enemy (t+d) = enemy (t)  + v_enemy  * d
-- and fire when their PROJECTED horizontal centre separation <= 6 m.
--
-- WHAT THIS SECTION PROVES, against the LIVE source AND the annotated copy:
--   S1-S12 the source carries the mechanics: the 1.5 s tunable delay, the
--          momentum flag (default FALSE = no inheritance), the velocity helper's
--          SIX reads (is_moving / is_moving_fast / slow_speed / fast_speed /
--          ordered_position / bearing), its fail-closed ZERO returns with a
--          named source, the 0.5 m degenerate-ordered-point gate, the projection
--          helper, the picker's gate on the PROJECTED separation, the same
--          projection re-taken in the pre-cast re-check, the 70% bypass still
--          wired to the 6 m centre constant, and the documented assumption +
--          ONE-FLAG escape hatch.
--   A  both stationary: projected = current; 5.5 m FIRES, 6.5 m stays SILENT
--      (exactly round 109's behaviour, so nothing regressed for a parked pair).
--   B1 a caster CLOSING fast (8 m/s) on a stationary enemy 12 m away: the
--      projected point reaches it -> FIRES, which the round-109 instant test at
--      12 m could not (it needed <= 6 m). The log prints projected=0.0m now=12.0m.
--   B2 a caster RECEDING at 8 m/s with the enemy 5 m away (round 109 fired here):
--      the projected separation is 17 m -> SILENT. This is the "fires later than
--      the old test" case: motion AWAY from the target delays or drops the cast.
--   C1 an enemy CLOSING at 4 m/s from 10 m: judged at its projected point
--      (4 m) -> FIRES, though its CURRENT point is outside the bound.
--   C2 an enemy RECEDING from 5 m to 11 m: SILENT, though its current point is
--      inside the bound - the exact mirror of C1.
--   D1 both CLOSING (8 m/s and 4 m/s) 20 m apart: the gap closes 18 m in the
--      delay -> projected 2 m -> FIRES (round 109 needed <= 6 m).
--   D2 the same closing pair 25 m apart: projected 7 m -> SILENT (the pin).
--   E  both moving the SAME direction at the SAME speed: the projected
--      separation equals the current one (4 m -> FIRES; 7 m -> SILENT), i.e. a
--      shared velocity cancels exactly as the relative-motion rule says.
--   F1 a target CROSSING the flight path 7 m to the side, whose projected point
--      is still 7 m away -> SILENT; F2 the same crossing at 5 m -> FIRES. The
--      path is never the test - the projected POINT is.
--   G1 is_moving() UNREADABLE: velocity ZERO, source "moving-unreadable" - the
--      motion is not guessed, so a 12 m pair stays SILENT and the log says so.
--   G2 the same unreadable caster 5 m from the enemy: FIRES (treated as
--      stationary, round-109 behaviour), with the source in the log.
--   G3 a moving caster whose ordered point is degenerate and with no bearing
--      read: source "no-heading", velocity ZERO -> SILENT at 12 m.
--   G4 the CASTER-ONLY bearing fallback: moving, degenerate ordered point,
--      bearing 90 (and slow_speed 4) -> v=(4.0, 0.0), projected +6 m -> the
--      12 m pair FIRES with source "bearing". An ENEMY never gets this treated.
--   H  drift during the delay: the enemy is 5 m at the pick and 30 m at the
--      pre-cast re-check -> SKIPPED (cast not spent), with the projected number
--      in the skip line.
--   I  THE ONE FLAG: the same source with FOURTH.AIR_DROP_INHERIT = true (the
--      documented variant file) adds v*d a SECOND time, so a caster closing at
--      8 m/s fires on an enemy 24 m ahead (projected 124 vs 124) where the
--      shipped flag=false source is SILENT (projected 112 vs 124). Proves the
--      flag is a real, single switch.
--
-- PINS (documented, asserted against the source): BOUND = 6 m,
-- DELAY = 1.5 s. Every world states the distances it uses.
-- ROUND 111 PIN: this section measures the two-body MECHANICS with the caster
-- projected the full delay ahead, i.e. the round-110 rule
-- (AIR_DROP_CASTER_LEAD = 1.0). That is no longer the shipped default, so every
-- world whose CASTER MOVES pins lead 1.0 through boot110's `knobs` argument; a
-- stationary caster needs no pin (the lead multiplies zero velocity). Round 111's
-- own section proves the knob.
--
-- RED CONTROL (H110_LIVE / H110_ANN -> docs/backups/round110/pre110_*.lua): the
-- pre-110 build has no velocity / projection helper at all, so every S check and
-- B1/B2/C1/C2/D1/D2/G4/H/I fail - and the A, F2 and E-fire worlds still pass BY
-- DESIGN (a stationary pair, and a 5 m crossing, are round-109 decisions).
-- ============================================================================
-- THE DIAL VARIANTS (round 111). FOURTH is a FILE-LOCAL table, so a world cannot
-- reach the two caster dials through a global; instead it loads a copy of the
-- same source with ONLY the two constant lines substituted - precisely the edit
-- the user makes in the field. Nothing else in the file changes, so a variant
-- world differs from the shipped build in exactly one number. A build without the
-- dials (the RED CONTROL snapshot, or the round-110 annotated tree) has no such
-- lines: the original path is returned unchanged, and the world tests the old
-- build as it is.
VAR_DIR_111 = "C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261023_airdrop_movingcaster_harness111/variants"

function harness_replace_all_111(s2, needle, repl)
  local out, at = {}, 1
  while true do
    local i, j = raw_find(s2, needle, at, true)
    if i == nil then break end
    out[#out + 1] = s2:sub(at, i - 1)
    out[#out + 1] = repl
    at = j + 1
  end
  out[#out + 1] = s2:sub(at)
  return table.concat(out)
end

function harness_variant(path, lead, delay, tag)
  if lead == nil and delay == nil then return path end
  local txt = read_file(path)
  local t_lead = "\nFOURTH.AIR_DROP_CASTER_LEAD = 0.5\n"
  local t_del = "\nFOURTH.AIR_DROP_CASTER_DELAY_S = 1.5\n"
  if raw_find(txt, t_lead, 1, true) == nil or raw_find(txt, t_del, 1, true) == nil then
    return path
  end
  if lead ~= nil then
    txt = harness_replace_all_111(txt, t_lead, "\nFOURTH.AIR_DROP_CASTER_LEAD = " .. string.format("%.2f", lead) .. "\n")
  end
  if delay ~= nil then
    txt = harness_replace_all_111(txt, t_del, "\nFOURTH.AIR_DROP_CASTER_DELAY_S = " .. string.format("%.2f", delay) .. "\n")
  end
  local dst = VAR_DIR_111 .. "/" .. tag .. ".lua"
  local f = assert(io.open(dst, "w"))
  f:write(txt)
  f:close()
  return dst
end

function run_h110()
  if os.getenv("H110_LIVE") ~= nil then LIVE = os.getenv("H110_LIVE") end
  if os.getenv("H110_ANN") ~= nil then ANN = os.getenv("H110_ANN") end
  local live_src110 = read_file(LIVE)
  local ann_src110  = read_file(ANN)
  local pre110 = checks
  local DFA = "wh2_dlc09_unit_abilities_death_from_above"
  local INF = "wh2_dlc13_emp_inf_spearmen_ror_0"
  local INF2 = "wh2_dlc09_tmb_inf_skeleton_warriors_0"
  local CAV = "wh2_dlc09_tmb_cav_necropolis_knights_0"
  -- THE PINS: the two constants this round turns on. Both are asserted present
  -- in the source below, so a silent retune of either FAILS the suite.
  local PIN_BOUND = 6
  local PIN_DELAY = 1.5

  local function cp110(s2, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s2, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function span110(s2, head, tail2)
    local i = raw_find(s2, head, 1, true)
    if i == nil then return nil end
    local j = raw_find(s2, tail2, i, true)
    if j == nil then return nil end
    return s2:sub(i, j)
  end
  local function lg110(cond) return cond == true end
  local function enemy_of110(W, uid)
    if W.enemy_entries == nil then return nil end
    for i = 1, #W.enemy_entries do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        local ok, id = pcall(function() return pr.unit:unique_ui_id() end)
        if ok and tostring(id) == tostring(uid) then return pr.unit end
      end
    end
    return nil
  end
  local function inf110(W, uid, v)
    local e = enemy_of110(W, uid)
    if e == nil then return end
    e.is_infantry = function() return v == true end
  end
  local function fly110(W, uid, v)
    local u = unit_of(W, uid)
    if u == nil then u = enemy_of110(W, uid) end
    if u == nil then return end
    local b = (v == true)
    u.is_currently_flying = function() return b end
  end
  local function mk110(uid, def, enemies, extra)
    def.name = def.name or "air_caster"
    def.uid = uid
    local owns = def.owns or { DFA }
    def.owns = owns
    local bar = {}
    for i = 1, #owns do bar[i] = { id = "b" .. i, key = owns[i] } end
    local o = { can_perform = true,
      units = { def },
      enemies = enemies,
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = bar }
    if extra ~= nil then for k, v in pairs(extra) do o[k] = v end end
    return make_world(o)
  end
  local function boot110(W, PATH, TAG, uid, marker, wname, knobs)
    local load_path = PATH
    if knobs ~= nil then
      load_path = harness_variant(PATH, knobs.lead, knobs.delay,
        wname .. (TAG == "[live] " and "_live" or "_ann"))
    end
    local ok = pcall(load_world, W, load_path)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. marker); ui(W)
    W.conflict = true
    return true
  end

  -- ==========================================================================
  print("== HARNESS 110 - section 0ab: the RELATIVE-MOTION rule in the source (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src110 }, { name = "ann", src = ann_src110 } }) do
    local nm, s2 = f.name, f.src
    local vel = span110(s2, "function FOURTH.ad_velocity(unit, allow_bearing)", "\nend")
    local lead = span110(s2, "function FOURTH.ad_lead(unit, t, allow_bearing)", "\nend")
    local proj = span110(s2, "function FOURTH.ad_project(unit, t)", "\nend")
    local pick = span110(s2, "function FOURTH.ad_pick(unit, routing)",
      "\nfunction FOURTH.evaluate_air_drop_on_infantry")
    local rech = span110(s2, "if FOURTH.ad_enemy ~= nil then", "\n\t-- SELF-SUMMON RE-CHECK")
    local byp = span110(s2, "if ability.evaluate == FOURTH.evaluate_air_drop_on_infantry then", "\n\tend")

    check("0ab " .. nm .. ": the 6 m bound is unchanged and ONE 1.5 s delay is defined",
      raw_find(s2, "FOURTH.AIR_DROP_CENTER_M = 6", 1, true) ~= nil
      and cp110(s2, "FOURTH.AIR_DROP_DELAY_S = " .. string.format("%.1f", PIN_DELAY)) == 1)
    check("0ab " .. nm .. ": the momentum flag ships FALSE (the ordnance does NOT inherit the caster's velocity)",
      cp110(s2, "FOURTH.AIR_DROP_INHERIT = false") == 1)
    check("0ab " .. nm .. ": the velocity helper reads ALL SIX documented API methods",
      vel ~= nil
      and raw_find(vel, "is_moving()", 1, true) ~= nil
      and raw_find(vel, "is_moving_fast()", 1, true) ~= nil
      and raw_find(vel, "slow_speed()", 1, true) ~= nil
      and raw_find(vel, "fast_speed()", 1, true) ~= nil
      and raw_find(vel, "ordered_position()", 1, true) ~= nil
      and raw_find(vel, "bearing()", 1, true) ~= nil)
    check("0ab " .. nm .. ": a unit that is NOT moving gets ZERO velocity with source 'stationary'",
      vel ~= nil
      and raw_find(vel, 'if moving ~= true then return 0, 0, 0, "stationary" end', 1, true) ~= nil)
    check("0ab " .. nm .. ": every unreadable source is a NAMED ZERO return (never invented motion)",
      vel ~= nil
      and raw_find(vel, '"moving-unreadable"', 1, true) ~= nil
      and raw_find(vel, '"no-speed"', 1, true) ~= nil
      and raw_find(vel, '"no-heading"', 1, true) ~= nil)
    check("0ab " .. nm .. ": a degenerate ordered point (<0.5 m) carries no heading",
      vel ~= nil and raw_find(vel, "len >= 0.5", 1, true) ~= nil)
    check("0ab " .. nm .. ": the bearing fallback is CASTER-ONLY (guarded by allow_bearing)",
      vel ~= nil and raw_find(vel, "if allow_bearing then", 1, true) ~= nil
      and raw_find(vel, 'return math.sin(r) * speed, math.cos(r) * speed, speed, "bearing"', 1, true) ~= nil)
    check("0ab " .. nm .. ": the projection helper adds v*t on BOTH axes",
      lead ~= nil and raw_find(lead, "local px, pz = x + vx * t, z + vz * t", 1, true) ~= nil)
    check("0ab " .. nm .. ": the ONE momentum flag adds the caster's lead term a SECOND time",
      lead ~= nil
      and raw_find(lead, "if allow_bearing and FOURTH.AIR_DROP_INHERIT == true then", 1, true) ~= nil
      and raw_find(lead, "px = px + vx * t_caster * lead_caster", 1, true) ~= nil
      and raw_find(lead, "pz = pz + vz * t_caster * lead_caster", 1, true) ~= nil)
    check("0ab " .. nm .. ": ad_project exists and projects through ad_lead",
      proj ~= nil and raw_find(proj, "FOURTH.ad_lead(unit, t, false)", 1, true) ~= nil)
    check("0ab " .. nm .. ": the picker projects BOTH bodies and gates on the PROJECTED separation",
      pick ~= nil
      and raw_find(pick, "FOURTH.ad_lead(unit, ad_t, true)", 1, true) ~= nil
      and raw_find(pick, "FOURTH.ad_lead(enemy, ad_t, false)", 1, true) ~= nil
      and raw_find(pick, "FOURTH.ad_sep(best_ipx, best_ipz, epx, epz)", 1, true) ~= nil
      and raw_find(pick, "pgap <= bound", 1, true) ~= nil
      and raw_find(pick, "FOURTH.AIR_DROP_DELAY_S", 1, true) ~= nil)
    check("0ab " .. nm .. ": an unreadable caster position FAILS CLOSED in the picker",
      pick ~= nil and raw_find(pick, "caster position UNREADABLE", 1, true) ~= nil)
    check("0ab " .. nm .. ": the PRE-CAST re-check RE-PROJECTS both bodies",
      rech ~= nil
      and raw_find(rech, "FOURTH.ad_lead(unit, ad_t_now, true)", 1, true) ~= nil
      and raw_find(rech, "FOURTH.ad_project(enemy, ad_t_now)", 1, true) ~= nil
      and raw_find(rech, "FOURTH.ad_sep(upx, upz, epx, epz)", 1, true) ~= nil
      and raw_find(rech, "FOURTH.AIR_DROP_DELAY_S", 1, true) ~= nil)
    check("0ab " .. nm .. ": the 70% map is still bypassed and still points at the 6 m centre constant",
      byp ~= nil and raw_find(byp, "ability.range_m = FOURTH.AIR_DROP_CENTER_M", 1, true) ~= nil)
    check("0ab " .. nm .. ": the no-momentum ASSUMPTION and the ONE-FLAG escape hatch are documented",
      raw_find(s2, "does NOT inherit the caster's velocity", 1, true) ~= nil
      and raw_find(s2, "ONE FLAG", 1, true) ~= nil
      and raw_find(s2, "impact = caster + v*d*2", 1, true) ~= nil
      and raw_find(s2, "TUNABLE CONSTANT", 1, true) ~= nil)
    if nm == "live" then
      check("0ab " .. nm .. ": the target line prints the delay, both bodies, both velocities + sources, both projected points",
        raw_find(s2, '" (PROJECTED "', 1, true) ~= nil
        and raw_find(s2, '" v=" .. FOURTH.ad_vec_text(best_uvx, best_uvz, best_uspd, best_usrc)', 1, true) ~= nil
        and raw_find(s2, '" v=" .. FOURTH.ad_vec_text(best_evx, best_evz, best_espd, best_esrc)', 1, true) ~= nil
        and raw_find(s2, '" proj=" .. FOURTH.ad_pos(best_ipx, best_ipz)', 1, true) ~= nil
        and raw_find(s2, '" proj=" .. FOURTH.ad_pos(best_epx, best_epz)', 1, true) ~= nil
        and raw_find(s2, '" centre=" .. string.format("%.1f", best_gap)', 1, true) ~= nil
        and raw_find(s2, '" now="', 1, true) ~= nil)
      check("0ab " .. nm .. ": the watch line prints the projected band AND both velocities",
        raw_find(s2, '" [projected sep=~"', 1, true) ~= nil
        and raw_find(s2, '"m after delay="', 1, true) ~= nil)
    else
      check("0ab " .. nm .. ": the annotated copy keeps the logic and drops only the log lines",
        raw_find(s2, '" (PROJECTED "', 1, true) == nil
        and raw_find(s2, "pgap <= bound", 1, true) ~= nil)
    end
  end

  -- ==========================================================================
  -- A: both stationary - projected = current (round 109's behaviour, unchanged).
  print("== HARNESS 110 - A: BOTH STATIONARY - projected == current ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    do
      local uid = 12001
      local W = mk110(uid, { melee = false, pos = { 0, 30, 0 } },
        { { name = INF, uid = 12011, melee = true, pos = { 5.5, 0, 0 } } })
      inf110(W, 12011, true); fly110(W, uid, true)
      if boot110(W, PATH, TAG, uid, "death_from_above", "A1") then
        polln(W, 2)
        check(TAG .. "A1a: both parked at 5.5 m (inside the 6 m pin) - fires (" .. #W.fires .. ")",
          #W.fires == 1)
        check(TAG .. "A1b: and the cast is on the OWNER (self-centred, unchanged)", 
          #W.fires == 1 and W.fires[1].target == unit_of(W, uid))
        check(TAG .. "A1c: the log says projected 5.5 m = now 5.5 m with BOTH sources stationary [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "centre=5.5m") >= 1
              and count_log(W, " now=5.5m") >= 1
              and count_log(W, "src=stationary") >= 2)))
        tally(W)
      end
    end
    do
      local uid = 12002
      local W = mk110(uid, { melee = false, pos = { 0, 30, 0 } },
        { { name = INF, uid = 12012, melee = true, pos = { 6.5, 0, 0 } } })
      inf110(W, 12012, true); fly110(W, uid, true)
      if boot110(W, PATH, TAG, uid, "death_from_above", "A2") then
        polln(W, 2)
        check(TAG .. "A2a: 6.5 m is outside the 6 m pin - no fire (" .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "A2b: the watch line names the projected band [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "watch: nearest INFANTRY '" .. INF .. "' is centre=~5m") == 1
              and count_log(W, "projected sep=~5m after delay=1.50s") == 1)))
        tally(W)
      end
    end
  end

  -- ==========================================================================
  -- B1: a caster CLOSING fast -> the projected point reaches the enemy -> FIRES
  -- at 12 m (round 109 needed <= 6 m).
  print("== HARNESS 110 - B1: caster closing at 8 m/s, enemy 12 m ahead -> FIRES ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid = 12003
    local W = mk110(uid, { melee = false, pos = { 100, 30, 200 }, moving = true, fast = true,
        fast_speed = 8, ordered = { 200, 30, 200 } },
      { { name = INF, uid = 12013, melee = true, pos = { 112, 0, 200 } } })
    inf110(W, 12013, true); fly110(W, uid, true)
    if boot110(W, PATH, TAG, uid, "death_from_above", "B1", { lead = 1.0 }) then
      polln(W, 2)
      check(TAG .. "B1a: projected caster 112 m meets the enemy at 112 m - FIRES (" .. #W.fires .. ")",
        #W.fires == 1)
      check(TAG .. "B1b: the CURRENT separation was 12 m - the old instant test could not fire here [live log]",
        lg110((TAG ~= "[live] ")
          or (count_log(W, "centre=0.0m") >= 1 and count_log(W, " now=12.0m") >= 1
            and count_log(W, "caster=(100.0, 200.0) v=(8.0, 0.0) 8.0 m/s src=ordered proj=(112.0, 200.0)") >= 1)))
      check(TAG .. "B1c: the enemy is reported stationary with its own (unmoved) projected point [live log]",
        lg110((TAG ~= "[live] ")
          or (count_log(W, "enemy=(112.0, 200.0) v=(0.0, 0.0) 0.0 m/s src=stationary proj=(112.0, 200.0)") >= 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  -- B2: a caster RECEDING -> projected 17 m -> SILENT (round 109 fired at 5 m).
  print("== HARNESS 110 - B2: caster receding at 8 m/s, enemy 5 m away -> SILENT ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid = 12004
    local W = mk110(uid, { melee = false, pos = { 100, 30, 200 }, moving = true, fast = true,
        fast_speed = 8, ordered = { 0, 30, 200 } },
      { { name = INF, uid = 12014, melee = true, pos = { 105, 0, 200 } } })
    inf110(W, 12014, true); fly110(W, uid, true)
    if boot110(W, PATH, TAG, uid, "death_from_above", "B2", { lead = 1.0 }) then
      polln(W, 3)
      check(TAG .. "B2a: 5 m NOW but 17 m at impact - no fire (" .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "B2b: the why-not line shows both numbers and the receding velocity [live log]",
        lg110((TAG ~= "[live] ")
          or (count_log(W, "is centre=~5m vs bound=6m") == 1
            and count_log(W, "projected sep=~15m after delay=1.50s") == 1
            and count_log(W, "caster v=(-8.0, 0.0) 8.0 m/s src=ordered") == 1)))
      check(TAG .. "B2c: nothing is attempted [live log]",
        lg110((TAG ~= "[live] ") or count_log(W, "ATTEMPT death_from_above") == 0))
      tally(W)
    end
  end

  -- ==========================================================================
  -- C1/C2: the ENEMY's own motion decides, in both directions.
  print("== HARNESS 110 - C: a MOVING enemy is judged at its projected point ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    do
      local uid = 12005
      local W = mk110(uid, { melee = false, pos = { 0, 30, 0 } },
        { { name = INF, uid = 12015, melee = true, pos = { 0, 0, 10 }, moving = true,
            slow_speed = 4, ordered = { 0, 0, 0 } } })
      inf110(W, 12015, true); fly110(W, uid, true)
      if boot110(W, PATH, TAG, uid, "death_from_above", "C1") then
        polln(W, 2)
        check(TAG .. "C1a: the enemy closes from 10 m to 4 m - FIRES (" .. #W.fires .. ")", #W.fires == 1)
        check(TAG .. "C1b: the log shows the projected enemy point (0.0, 4.0) and now=10.0m [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "centre=4.0m") >= 1 and count_log(W, " now=10.0m") >= 1
              and count_log(W, "enemy=(0.0, 10.0) v=(0.0, -4.0) 4.0 m/s src=ordered proj=(0.0, 4.0)") >= 1)))
        tally(W)
      end
    end
    do
      local uid = 12006
      local W = mk110(uid, { melee = false, pos = { 0, 30, 0 } },
        { { name = INF, uid = 12016, melee = true, pos = { 0, 0, 5 }, moving = true,
            slow_speed = 4, ordered = { 0, 0, 20 } } })
      inf110(W, 12016, true); fly110(W, uid, true)
      if boot110(W, PATH, TAG, uid, "death_from_above", "C2") then
        polln(W, 3)
        check(TAG .. "C2a: 5 m NOW but 11 m at impact - no fire (" .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "C2b: the why-not line shows the projected 10 m band [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "is centre=~5m vs bound=6m") == 1
              and count_log(W, "projected sep=~10m after delay=1.50s") == 1)))
        tally(W)
      end
    end
  end

  -- ==========================================================================
  -- D1/D2: both CLOSING - 20 m fires, 25 m does not (projected 2 m / 7 m).
  print("== HARNESS 110 - D: both closing - 20 m FIRES, 25 m stays silent ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    do
      local uid = 12007
      local W = mk110(uid, { melee = false, pos = { 100, 30, 200 }, moving = true, fast = true,
          fast_speed = 8, ordered = { 300, 30, 200 } },
        { { name = INF, uid = 12017, melee = true, pos = { 120, 0, 200 }, moving = true,
            slow_speed = 4, ordered = { 0, 0, 200 } } })
      inf110(W, 12017, true); fly110(W, uid, true)
      if boot110(W, PATH, TAG, uid, "death_from_above", "D1", { lead = 1.0 }) then
        polln(W, 2)
        check(TAG .. "D1a: closing at 12 m/s over 1.5 s leaves 2 m - FIRES (" .. #W.fires .. ")",
          #W.fires == 1)
        check(TAG .. "D1b: the log proves BOTH projections (112 vs 114) and now=20.0m [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "centre=2.0m") >= 1 and count_log(W, " now=20.0m") >= 1
              and count_log(W, "proj=(112.0, 200.0)") >= 1
              and count_log(W, "proj=(114.0, 200.0)") >= 1)))
        tally(W)
      end
    end
    do
      local uid = 12008
      local W = mk110(uid, { melee = false, pos = { 100, 30, 200 }, moving = true, fast = true,
          fast_speed = 8, ordered = { 300, 30, 200 } },
        { { name = INF, uid = 12018, melee = true, pos = { 125, 0, 200 }, moving = true,
            slow_speed = 4, ordered = { 0, 0, 200 } } })
      inf110(W, 12018, true); fly110(W, uid, true)
      if boot110(W, PATH, TAG, uid, "death_from_above", "D2", { lead = 1.0 }) then
        polln(W, 3)
        check(TAG .. "D2a: 25 m closing leaves 7 m at impact - no fire at the 6 m pin ("
          .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "D2b: the why-not band is the projected 5 m band [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "is centre=~25m vs bound=6m") == 1
              and count_log(W, "projected sep=~5m after delay=1.50s") == 1)))
        tally(W)
      end
    end
  end

  -- ==========================================================================
  -- E: the SAME velocity on both bodies cancels - projected == current.
  print("== HARNESS 110 - E: same direction, same speed - separation unchanged ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    do
      local uid = 12009
      local W = mk110(uid, { melee = false, pos = { 100, 30, 200 }, moving = true, fast = true,
          fast_speed = 8, ordered = { 300, 30, 200 } },
        { { name = INF, uid = 12019, melee = true, pos = { 104, 0, 200 }, moving = true,
            fast = true, fast_speed = 8, ordered = { 300, 0, 200 } } })
      inf110(W, 12019, true); fly110(W, uid, true)
      if boot110(W, PATH, TAG, uid, "death_from_above", "E1", { lead = 1.0 }) then
        polln(W, 2)
        check(TAG .. "E1a: 4 m apart and both running the same way - projected is still 4 m - FIRES ("
          .. #W.fires .. ")", #W.fires == 1)
        check(TAG .. "E1b: the log's projected separation EQUALS the current one [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "centre=4.0m") >= 1 and count_log(W, " now=4.0m") >= 1)))
        tally(W)
      end
    end
    do
      local uid = 12010
      local W = mk110(uid, { melee = false, pos = { 100, 30, 200 }, moving = true, fast = true,
          fast_speed = 8, ordered = { 300, 30, 200 } },
        { { name = INF, uid = 12020, melee = true, pos = { 107, 0, 200 }, moving = true,
            fast = true, fast_speed = 8, ordered = { 300, 0, 200 } } })
      inf110(W, 12020, true); fly110(W, uid, true)
      if boot110(W, PATH, TAG, uid, "death_from_above", "E2", { lead = 1.0 }) then
        polln(W, 3)
        check(TAG .. "E2a: 7 m apart on the same heading - still 7 m projected - no fire ("
          .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "E2b: the projected band equals the current band [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "is centre=~5m vs bound=6m") == 1
              and count_log(W, "projected sep=~5m after delay=1.50s") == 1)))
        tally(W)
      end
    end
  end

  -- ==========================================================================
  -- F: a target CROSSING the flight path - the projected POINT decides.
  print("== HARNESS 110 - F: a crossing target - 7 m silent, 5 m fires ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    do
      local uid = 12021
      local W = mk110(uid, { melee = false, pos = { 0, 30, 0 } },
        { { name = INF, uid = 12031, melee = true, pos = { 7, 0, -6 }, moving = true,
            slow_speed = 4, ordered = { 7, 0, 20 } } })
      inf110(W, 12031, true); fly110(W, uid, true)
      if boot110(W, PATH, TAG, uid, "death_from_above", "F1") then
        polln(W, 3)
        check(TAG .. "F1a: it crosses the flight line but its projected point stays 7 m off - SILENT ("
          .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "F1b: the why-not line bands the PROJECTED 7 m, not the current 7.8 m [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "projected sep=~5m after delay=1.50s") == 1
              and count_log(W, "is centre=~5m vs bound=6m") == 1)))
        tally(W)
      end
    end
    do
      local uid = 12022
      local W = mk110(uid, { melee = false, pos = { 0, 30, 0 } },
        { { name = INF, uid = 12032, melee = true, pos = { 5, 0, -6 }, moving = true,
            slow_speed = 4, ordered = { 5, 0, 20 } } })
      inf110(W, 12032, true); fly110(W, uid, true)
      if boot110(W, PATH, TAG, uid, "death_from_above", "F2") then
        polln(W, 2)
        check(TAG .. "F2a: the same crossing 5 m off passes right over the caster at t+1.5 s - FIRES ("
          .. #W.fires .. ")", #W.fires == 1)
        check(TAG .. "F2b: projected centre 5.0 m with now=7.8 m [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "centre=5.0m") >= 1 and count_log(W, " now=7.8m") >= 1)))
        tally(W)
      end
    end
  end

  -- ==========================================================================
  -- G: unreadable / missing velocity - treated as STATIONARY, and the log says why.
  print("== HARNESS 110 - G: unreadable and degenerate velocities are never invented ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    do
      local uid = 12023
      local W = mk110(uid, { melee = false, pos = { 100, 30, 200 }, moving = true,
          moving_raises = true, fast = true, fast_speed = 8, ordered = { 200, 30, 200 } },
        { { name = INF, uid = 12033, melee = true, pos = { 112, 0, 200 } } })
      inf110(W, 12033, true); fly110(W, uid, true)
      if boot110(W, PATH, TAG, uid, "death_from_above", "G1") then
        polln(W, 3)
        check(TAG .. "G1a: is_moving() unreadable -> no motion is assumed -> 12 m stays SILENT ("
          .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "G1b: the source is printed as moving-unreadable [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "src=moving-unreadable") >= 1
              and count_log(W, "projected sep=~10m after delay=1.50s") == 1)))
        tally(W)
      end
    end
    do
      local uid = 12024
      local W = mk110(uid, { melee = false, pos = { 100, 30, 200 }, moving = true,
          moving_raises = true, fast = true, fast_speed = 8 },
        { { name = INF, uid = 12034, melee = true, pos = { 105, 0, 200 } } })
      inf110(W, 12034, true); fly110(W, uid, true)
      if boot110(W, PATH, TAG, uid, "death_from_above", "G2") then
        polln(W, 2)
        check(TAG .. "G2a: the same unreadable caster 5 m away still FIRES (treated as stationary) ("
          .. #W.fires .. ")", #W.fires == 1)
        check(TAG .. "G2b: and the line still names the unreadable source [live log]",
          lg110((TAG ~= "[live] ") or (count_log(W, "src=moving-unreadable") >= 1)))
        tally(W)
      end
    end
    do
      local uid = 12025
      local W = mk110(uid, { melee = false, pos = { 0, 30, 0 }, moving = true, slow_speed = 4,
          ordered = { 0, 30, 0 } },
        { { name = INF, uid = 12035, melee = true, pos = { 12, 0, 0 } } })
      inf110(W, 12035, true); fly110(W, uid, true)
      if boot110(W, PATH, TAG, uid, "death_from_above", "G3") then
        polln(W, 3)
        check(TAG .. "G3a: moving with a DEGENERATE ordered point and no bearing -> no motion -> SILENT ("
          .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "G3b: the source says no-heading [live log]",
          lg110((TAG ~= "[live] ") or (count_log(W, "src=no-heading") >= 1)))
        tally(W)
      end
    end
    do
      local uid = 12026
      local W = mk110(uid, { melee = false, pos = { 0, 30, 0 }, moving = true, slow_speed = 4,
          ordered = { 0, 30, 0 }, bearing = 90 },
        { { name = INF, uid = 12036, melee = true, pos = { 12, 0, 0 } } })
      inf110(W, 12036, true); fly110(W, uid, true)
      if boot110(W, PATH, TAG, uid, "death_from_above", "G4", { lead = 1.0 }) then
        polln(W, 2)
        check(TAG .. "G4a: the CASTER-ONLY bearing fallback gives v=(4.0, 0.0) - projected 6 m from 12 m - FIRES ("
          .. #W.fires .. ")", #W.fires == 1)
        check(TAG .. "G4b: the line names src=bearing and the projected point (6.0, 0.0) [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "src=bearing") >= 1
              and count_log(W, "proj=(6.0, 0.0)") >= 1)))
        tally(W)
      end
    end
  end

  -- ==========================================================================
  -- H: the enemy DRIFTS out between the pick and the pre-cast re-check.
  print("== HARNESS 110 - H: drift during the delay is caught by the re-projection ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid = 12027
    local W = mk110(uid, { melee = false, pos = { 0, 30, 0 } },
      { { name = INF, uid = 12037, melee = true,
          pos_seq = { { 5, 0, 0 }, { 30, 0, 0 } } } })
    inf110(W, 12037, true); fly110(W, uid, true)
    if boot110(W, PATH, TAG, uid, "death_from_above", "H") then
      polln(W, 2)
      check(TAG .. "H1a: chosen at 5 m, then 30 m at the re-check - the cast is NOT spent ("
        .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "H1b: the SKIPPED line names the RE-PROJECTED separation [live log]",
        lg110((TAG ~= "[live] ")
          or (count_log(W, "SKIPPED: the drop lapsed before the cast") >= 1
            and count_log(W, "projected centre=30.0m") >= 1
            and count_log(W, "delay=1.50s") >= 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  -- I: THE ONE FLAG - the documented variant with FOURTH.AIR_DROP_INHERIT = true
  --   adds v*d a second time, so the impact point moves 12 m further forward.
  print("== HARNESS 110 - I: the ONE momentum flag really moves the impact point ==")
  local INHERIT_FILE = "C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261022_airdrop_relative_harness110/harness110_inherit_on.lua"
  if os.getenv("H110_INHERIT") ~= nil then INHERIT_FILE = os.getenv("H110_INHERIT") end
  do
    local uid = 12028
    local W = mk110(uid, { melee = false, pos = { 100, 30, 200 }, moving = true, fast = true,
        fast_speed = 8, ordered = { 300, 30, 200 } },
      { { name = INF, uid = 12038, melee = true, pos = { 124, 0, 200 } } })
    inf110(W, 12038, true); fly110(W, uid, true)
    if boot110(W, LIVE, "[live] ", uid, "death_from_above", "I1", { lead = 1.0 }) then
      polln(W, 3)
      check("[live] I1a (flag FALSE, the shipped build): 24 m ahead projects to 112 m - 12 m short - SILENT ("
        .. #W.fires .. ")", #W.fires == 0)
      check("[live] I1b: the why-not line bands it at 12 m projected vs 24 m now [live log]",
        lg110(count_log(W, "is centre=~20m vs bound=6m") == 1
          and count_log(W, "projected sep=~10m after delay=1.50s") == 1))
      tally(W)
    end
  end
  do
    local uid = 12029
    local W = mk110(uid, { melee = false, pos = { 100, 30, 200 }, moving = true, fast = true,
        fast_speed = 8, ordered = { 300, 30, 200 } },
      { { name = INF, uid = 12039, melee = true, pos = { 124, 0, 200 } } })
    inf110(W, 12039, true); fly110(W, uid, true)
    if boot110(W, INHERIT_FILE, "[inherit] ", uid, "death_from_above", "I2", { lead = 1.0 }) then
      polln(W, 2)
      check("[inherit] I2a (flag TRUE): the impact point moves to 124 m and the same 24 m enemy FIRES ("
        .. #W.fires .. ")", #W.fires == 1)
      check("[inherit] I2b: the log prints proj=(124.0, 200.0) and momentum=inherited [live log]",
        lg110((count_log(W, "proj=(124.0, 200.0)") >= 1
          and count_log(W, "momentum=inherited") >= 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  if RED_MODE then
    check("HARNESS 109 suite boundary (harness 110): N/A in the red run - the pre-110 snapshot "
      .. "still carries every harness-109 world", true)
  else
    check("HARNESS 109 suite boundary (harness 110): every harness-109 check ran first ("
      .. pre110 .. ", want 4104)", pre110 == 4104)
  end
  check("HARNESS 110: the ZERO-search invariant still holds after the new section (counted "
    .. find_calls .. ")", find_calls == 0)
  print("== HARNESS 110 done: checks " .. checks .. ", failures " .. failures .. " ==")
end
