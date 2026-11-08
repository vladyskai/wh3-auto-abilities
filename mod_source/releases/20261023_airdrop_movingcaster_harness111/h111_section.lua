-- ============================================================================
-- HARNESS 111 - THE MOVING-CASTER DIALS: ONLY THE CASTER'S LEAD MOVES
--
-- THE USER'S FOURTH FIELD REPORT, verbatim: "I tested it. It seems to work okay
-- when the caster is stationary, but it definitely drops the rocks too soon when
-- in movement. How do we tune it?"
--
-- THE READING: a STATIONARY caster is RIGHT, so the ENEMY projection and the 6 m
-- bound are RIGHT. The error exists only while the caster moves, and it fires TOO
-- SOON, so the caster's projected point runs AHEAD of the real impact point - the
-- caster's lead term is OVER-STATED. Round 111 therefore gives the caster its OWN
-- lead - a delay and a share of it - and leaves the enemy's term exactly as it
-- was:
--     caster_projected = caster + v_caster * AIR_DROP_CASTER_DELAY_S
--                                        * AIR_DROP_CASTER_LEAD
--     enemy_projected  = enemy  + v_enemy  * AIR_DROP_DELAY_S
-- with the pair (1.5, 0.5) shipped.
--
-- WHAT THIS SECTION PROVES, against the LIVE source AND the annotated copy:
--   S1-S10 the source carries the two constants ONCE each with the shipped
--          defaults, the caster formula above, the shared enemy term UNTOUCHED,
--          the dial-text helper and its decision-line wiring.
--   A   a STATIONARY caster is unchanged: at lead 1.0, 0.5 and 0.0 the same 5.5 m
--       pair FIRES and the same 6.5 m pair stays SILENT, with the same projected
--       numbers - the dial multiplies zero velocity, so it cannot move a parked
--       caster. (5.5 / 6.5 are the round-110 pins, re-stated here.)
--   B   THE REPORTED BUG, AS A RED-STYLE CONTROL: a caster closing at 8 m/s with
--       the enemy 16 m ahead FIRES at lead 1.0 (the round-110 default) because
--       its projected point reaches x=112 at a 4 m gap - the release happens
--       while the flier is still 16 m short. At the shipped lead 0.5 the same
--       world projects x=106, a 10 m gap, and stays SILENT.
--   D   lead 0.5 fires LATER than lead 1.0: on the same 10 m world the projected
--       separation is 4.0 m at lead 0.5 against 2.0 m at lead 1.0 (the release is
--       judged further from the trigger), and at 18 m lead 1.0 still fires (6.0 m
--       projection) while lead 0.5 does not (12.0 m).
--   E   lead 0.0 treats the caster as STATIONARY: the moving caster's projected
--       point is exactly its current point (100.0, 200.0), 4.0 m from a 4 m
--       enemy - the SAME point and the SAME decision as a genuinely parked
--       caster, where lead 1.0 projects 8.0 m and stays silent.
--   F   the caster delay is INDEPENDENT: shortening it 1.5 -> 1.0 moves the
--       caster's projected point 72 -> 68 for an 8 m/s caster and leaves the
--       ENEMY's projected point identically (74.0, 200.0) in both worlds - the
--       enemy term reads the shared delay and nothing else.
--   G   the PRE-CAST RE-CHECK uses the same knobs: the pick is taken at lead 0.5,
--       the re-projection at the cast is taken at lead 0.5 too (a 4.0 m pick that
--       has closed to 1.0 m still fires), and a drift to 34.0 m SKIPS the cast
--       with `delay_caster=1.50s lead=0.50` printed in the skip line.
--
-- PINS (documented here and asserted against the source): BOUND = 6 m,
-- DELAY = 1.5 s, CASTER_DELAY = 1.5 s, CASTER_LEAD = 0.5. Per-world distances are
-- stated in each world's comment.
--
-- RED CONTROL (H111_LIVE / H111_ANN -> docs/backups/round111/pre111_*.lua, the
-- round-110 build): there is no caster dial at all, so every S check, every
-- dial-log check and every B/D/E/G world fails as designed - and the A decision
-- and F's enemy point still pass, because a stationary caster and the enemy term
-- are exactly what round 110 got right.
-- ============================================================================
function run_h111()
  if os.getenv("H111_LIVE") ~= nil then LIVE = os.getenv("H111_LIVE") end
  if os.getenv("H111_ANN") ~= nil then ANN = os.getenv("H111_ANN") end
  local live_src111 = read_file(LIVE)
  local ann_src111  = read_file(ANN)
  local pre111 = checks
  local DFA = "wh2_dlc09_unit_abilities_death_from_above"
  local INF = "wh2_dlc13_emp_inf_spearmen_ror_0"

  -- THE PINS. All four are asserted present in the source below, so a silent
  -- retune of any of them FAILS the suite instead of quietly changing behaviour.
  local PIN_BOUND = 6
  local PIN_DELAY = 1.5
  local PIN_CASTER_DELAY = 1.5
  local PIN_CASTER_LEAD = 0.5

  local function cp111(s2, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s2, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function span111(s2, head, tail2)
    local i = raw_find(s2, head, 1, true)
    if i == nil then return nil end
    local j = raw_find(s2, tail2, i, true)
    if j == nil then return nil end
    return s2:sub(i, j)
  end
  local function lg111(cond) return cond == true end
  local function enemy_of111(W, uid)
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
  local function inf111(W, uid, v)
    local e = enemy_of111(W, uid)
    if e == nil then return end
    e.is_infantry = function() return v == true end
  end
  local function fly111(W, uid, v)
    local u = unit_of(W, uid)
    if u == nil then u = enemy_of111(W, uid) end
    if u == nil then return end
    local b = (v == true)
    u.is_currently_flying = function() return b end
  end
  -- THE DIALS, AS A ONE-LINE VARIANT OF THE SAME SOURCE (harness_variant, defined
  -- above run_h110). FOURTH is a FILE-LOCAL table, so this is the only faithful
  -- way to change a dial: the file the world loads differs from the shipped build
  -- in exactly the constant line under test.
  local function dial_path111(PATH, knobs, wname)
    if knobs == nil then return PATH end
    return harness_variant(PATH, knobs.lead, knobs.delay,
      "h111_" .. wname .. (PATH == LIVE and "_live" or "_ann"))
  end
  local function mk111(uid, def, enemies)
    def.name = def.name or "air_caster"
    def.uid = uid
    local owns = def.owns or { DFA }
    def.owns = owns
    local bar = {}
    for i = 1, #owns do bar[i] = { id = "b" .. i, key = owns[i] } end
    return make_world({ can_perform = true,
      units = { def },
      enemies = enemies,
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = bar })
  end
  local function boot111(W, PATH, TAG, uid, marker, wname, knobs)
    local load_path = dial_path111(PATH, knobs, wname)
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
  print("== HARNESS 111 - section 0ac: the two CASTER dials in the source (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src111 }, { name = "ann", src = ann_src111 } }) do
    local nm, s2 = f.name, f.src
    local vel = span111(s2, "function FOURTH.ad_velocity(unit, allow_bearing)", "\nend")
    local lead = span111(s2, "function FOURTH.ad_lead(unit, t, allow_bearing)", "\nend")
    local proj = span111(s2, "function FOURTH.ad_project(unit, t)", "\nend")
    local pick = span111(s2, "function FOURTH.ad_pick(unit, routing)",
      "\nfunction FOURTH.evaluate_air_drop_on_infantry")
    local rech = span111(s2, "if FOURTH.ad_enemy ~= nil then", "\n\t-- SELF-SUMMON RE-CHECK")

    check("0ac " .. nm .. ": the caster delay is defined EXACTLY ONCE at the pin (" ..
      string.format("%.1f", PIN_CASTER_DELAY) .. " s)",
      cp111(s2, "\nFOURTH.AIR_DROP_CASTER_DELAY_S = " .. string.format("%.1f", PIN_CASTER_DELAY) .. "\n") == 1)
    check("0ac " .. nm .. ": the caster lead is defined EXACTLY ONCE at the pin (" ..
      string.format("%.2f", PIN_CASTER_LEAD) .. ")",
      cp111(s2, "\nFOURTH.AIR_DROP_CASTER_LEAD = 0.5\n") == 1)
    check("0ac " .. nm .. ": the shared fall delay line is UNCHANGED and single, and the 6 m bound stands",
      cp111(s2, "\nFOURTH.AIR_DROP_DELAY_S = " .. string.format("%.1f", PIN_DELAY) .. "\n") == 1
      and raw_find(s2, "FOURTH.AIR_DROP_CENTER_M = " .. tostring(PIN_BOUND), 1, true) ~= nil)
    check("0ac " .. nm .. ": the caster is projected with ITS OWN delay AND lead",
      lead ~= nil
      and raw_find(lead, "local t_caster, lead_caster = t, 1", 1, true) ~= nil
      and raw_find(lead, "px = x + vx * t_caster * lead_caster", 1, true) ~= nil
      and raw_find(lead, "pz = z + vz * t_caster * lead_caster", 1, true) ~= nil)
    check("0ac " .. nm .. ": the ENEMY keeps the shared delay in full (one v*t on both axes)",
      lead ~= nil and raw_find(lead, "local px, pz = x + vx * t, z + vz * t", 1, true) ~= nil)
    check("0ac " .. nm .. ": the dials are read ONLY for the caster (allow_bearing gate)",
      lead ~= nil
      and raw_find(lead, "if allow_bearing == true then", 1, true) ~= nil
      and raw_find(lead, "FOURTH.AIR_DROP_CASTER_DELAY_S", 1, true) ~= nil
      and raw_find(lead, "FOURTH.AIR_DROP_CASTER_LEAD", 1, true) ~= nil)
    check("0ac " .. nm .. ": an UNREADABLE dial falls back to the round-110 behaviour, never to a guess",
      lead ~= nil
      and raw_find(lead, 'if type(d_caster) == "number" and d_caster >= 0 then t_caster = d_caster end', 1, true) ~= nil
      and raw_find(lead, 'if type(l_caster) == "number" and l_caster >= 0 then lead_caster = l_caster end', 1, true) ~= nil)
    check("0ac " .. nm .. ": the ONE momentum flag still adds the lead term a SECOND time",
      lead ~= nil
      and raw_find(lead, "if allow_bearing and FOURTH.AIR_DROP_INHERIT == true then", 1, true) ~= nil
      and raw_find(lead, "px = px + vx * t_caster * lead_caster", 1, true) ~= nil)
    check("0ac " .. nm .. ": enemies still project through ad_lead with allow_bearing FALSE",
      proj ~= nil and raw_find(proj, "FOURTH.ad_lead(unit, t, false)", 1, true) ~= nil)
    check("0ac " .. nm .. ": the dial-text helper exists and names BOTH dials",
      raw_find(s2, "function FOURTH.ad_dial_text(moving)", 1, true) ~= nil
      and raw_find(s2, '"delay_caster="', 1, true) ~= nil
      and raw_find(s2, '" moving caster: lead="', 1, true) ~= nil)
    check("0ac " .. nm .. ": the picker still projects BOTH bodies and gates on the projection",
      pick ~= nil
      and raw_find(pick, "FOURTH.ad_lead(unit, ad_t, true)", 1, true) ~= nil
      and raw_find(pick, "FOURTH.ad_lead(enemy, ad_t, false)", 1, true) ~= nil
      and raw_find(pick, "pgap <= bound", 1, true) ~= nil)
    check("0ac " .. nm .. ": the pre-cast re-check re-projects through the SAME helper (same dials)",
      rech ~= nil
      and raw_find(rech, "FOURTH.ad_lead(unit, ad_t_now, true)", 1, true) ~= nil
      and raw_find(rech, "FOURTH.ad_project(enemy, ad_t_now)", 1, true) ~= nil)
    if nm == "live" then
      check("0ac " .. nm .. ": the decision line prints the dials after the caster's projected point",
        raw_find(s2, '.. " from " .. FOURTH.ad_dial_text(best_uspd > 0)', 1, true) ~= nil)
      check("0ac " .. nm .. ": the moving-caster fragment is emitted only for a NON-ZERO caster speed",
        cp111(s2, "FOURTH.ad_dial_text(best_uspd > 0)") == 2
        and cp111(s2, "FOURTH.ad_dial_text(uc_spd2 ~= nil and uc_spd2 > 0)") == 2)
      check("0ac " .. nm .. ": the why-not (watch) line prints the dials beside the caster velocity",
        raw_find(s2, '.. " (" .. FOURTH.ad_dial_text(best_uspd > 0) .. "); enemy v="', 1, true) ~= nil)
    else
      check("0ac " .. nm .. ": the annotated copy keeps the logic and the counterfactual helper",
        raw_find(s2, '"delay_caster="', 1, true) ~= nil
        and raw_find(s2, '" (PROJECTED "', 1, true) == nil)
    end
  end

  -- ==========================================================================
  -- A: a STATIONARY caster is unchanged by either dial.
  --    caster (100, 30, 200) parked; enemy (105.5) -> 5.5 m FIRES, (106.5) -> 6.5 m SILENT.
  print("== HARNESS 111 - A: a stationary caster fires at exactly the same distance ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local function parked(world, uid, euid, ex, lead, wname)
      local W = mk111(uid, { melee = false, pos = { 100, 30, 200 } },
        { { name = INF, uid = euid, melee = true, pos = { ex, 0, 200 } } })
      inf111(W, euid, true); fly111(W, uid, true)
      if not boot111(W, PATH, TAG, uid, "death_from_above", wname, { lead = lead }) then
        return nil
      end
      polln(W, 2)
      return W
    end
    do
      local W = parked(1, 13001, 13101, 105.5, 0.5, "A1")
      if W ~= nil then
        check(TAG .. "A1a: 5.5 m with the SHIPPED lead 0.5 - fires (" .. #W.fires .. ")", #W.fires == 1)
        check(TAG .. "A1b: the projected separation is the INSTANT one, 5.5 m [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W, "centre=5.5m") >= 1 and count_log(W, " now=5.5m") >= 1)))
        check(TAG .. "A1c: the line prints delay_caster=1.50s lead=0.50 and NO moving-caster fragment [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W, "delay_caster=1.50s lead=0.50") >= 1
              and count_log(W, "moving caster:") == 0)))
        tally(W)
      end
    end
    do
      local W = parked(2, 13002, 13102, 105.5, 1.0, "A2")
      if W ~= nil then
        check(TAG .. "A2a: the round-110 lead 1.0 does NOT move a parked caster - still 5.5 m, still fires ("
          .. #W.fires .. ")", #W.fires == 1)
        check(TAG .. "A2b: and the projected number is identical (5.5 m) [live log]",
          lg111((TAG ~= "[live] ") or count_log(W, "centre=5.5m") >= 1))
        tally(W)
      end
    end
    do
      local W = parked(3, 13003, 13103, 105.5, 0.0, "A3")
      if W ~= nil then
        check(TAG .. "A3a: lead 0.0 does NOT move a parked caster either - still 5.5 m, still fires ("
          .. #W.fires .. ")", #W.fires == 1)
        check(TAG .. "A3b: the projected number is identical (5.5 m) [live log]",
          lg111((TAG ~= "[live] ") or count_log(W, "centre=5.5m") >= 1))
        tally(W)
      end
    end
    do
      local W = parked(4, 13004, 13104, 106.5, 1.0, "A4")
      if W ~= nil then
        check(TAG .. "A4a: 6.5 m stays SILENT at lead 1.0 as it does at 0.5 (" .. #W.fires .. ")",
          #W.fires == 0)
        tally(W)
      end
    end
  end

  -- ==========================================================================
  -- B: THE REPORTED BUG. Caster (100, 30, 200) closing at 8 m/s, enemy parked
  --    16 m ahead: lead 1.0 projects x=112 -> 4.0 m -> FIRES while the flier is
  --    still 16 m short; the shipped lead 0.5 projects x=106 -> 10.0 m -> SILENT.
  print("== HARNESS 111 - B: lead 1.0 reproduces the early release; lead 0.5 does not ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local function closing(uid, euid, lead, wname)
      local W = mk111(uid, { melee = false, pos = { 100, 30, 200 }, moving = true, fast = true,
          fast_speed = 8, ordered = { 300, 30, 200 } },
        { { name = INF, uid = euid, melee = true, pos = { 116, 0, 200 } } })
      inf111(W, euid, true); fly111(W, uid, true)
      if not boot111(W, PATH, TAG, uid, "death_from_above", wname, { lead = lead }) then
        return nil
      end
      polln(W, 3)
      return W
    end
    do
      local W = closing(13005, 13105, 1.0, "B1")
      if W ~= nil then
        check(TAG .. "B1a (RED-STYLE CONTROL, lead 1.0 = round 110): a 16 m pair FIRES (" .. #W.fires .. ")",
          #W.fires == 1)
        check(TAG .. "B1b: the log proves the over-lead - projected 4.0 m from an INSTANT 16.0 m [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W, "centre=4.0m") >= 1 and count_log(W, " now=16.0m") >= 1
              and count_log(W, "proj=(112.0, 200.0)") >= 1)))
        check(TAG .. "B1c: the line names lead=1.00 and the moving-caster fragment [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W, "delay_caster=1.50s lead=1.00") >= 1
              and count_log(W, "moving caster: lead=1.00 of 1.50s") >= 1)))
        tally(W)
      end
    end
    do
      local W = closing(13006, 13106, 0.5, "B2")
      if W ~= nil then
        check(TAG .. "B2a (SHIPPED lead 0.5): the same 16 m pair is SILENT (" .. #W.fires .. ")",
          #W.fires == 0)
        check(TAG .. "B2b: the why-not line bands the projection at 10 m against a 15 m instant band [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W, "projected sep=~10m after delay=1.50s") >= 1
              and count_log(W, "is centre=~15m vs bound=6m") >= 1)))
        check(TAG .. "B2c: the why-not line names lead=0.50 beside the caster velocity [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W, "delay_caster=1.50s lead=0.50") >= 1
              and count_log(W, "moving caster: lead=0.50 of 1.50s") >= 1)))
        tally(W)
      end
    end
  end

  -- ==========================================================================
  -- D: lead 0.5 fires LATER than lead 1.0.
  --    D1/D2 the SAME 10 m world: projection 2.0 m at lead 1.0, 4.0 m at 0.5.
  --    D3/D4 the SAME 18 m world: 6.0 m at lead 1.0 fires, 12.0 m at 0.5 does not.
  print("== HARNESS 111 - D: the shipped lead fires later, at a smaller current distance ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local function w(uid, euid, ex, lead, wname)
      local W = mk111(uid, { melee = false, pos = { 100, 30, 200 }, moving = true, fast = true,
          fast_speed = 8, ordered = { 300, 30, 200 } },
        { { name = INF, uid = euid, melee = true, pos = { ex, 0, 200 } } })
      inf111(W, euid, true); fly111(W, uid, true)
      if not boot111(W, PATH, TAG, uid, "death_from_above", wname, { lead = lead }) then
        return nil
      end
      polln(W, 3)
      return W
    end
    do
      local W1 = w(13007, 13107, 110, 1.0, "D1")
      local W2 = w(13008, 13108, 110, 0.5, "D2")
      if W1 ~= nil and W2 ~= nil then
        check(TAG .. "D1a: at 10 m, lead 1.0 projects 2.0 m and FIRES (" .. #W1.fires .. ")",
          #W1.fires == 1 and lg111((TAG ~= "[live] ") or count_log(W1, "centre=2.0m") >= 1))
        check(TAG .. "D2a: at 10 m, lead 0.5 projects 4.0 m and FIRES too (" .. #W2.fires .. ")",
          #W2.fires == 1 and lg111((TAG ~= "[live] ") or count_log(W2, "centre=4.0m") >= 1))
        check(TAG .. "D2b: the 0.5 projection is the LARGER one (4.0 > 2.0) - the release is later",
          lg111((TAG ~= "[live] ")
            or (count_log(W2, "centre=4.0m") >= 1 and count_log(W1, "centre=4.0m") == 0)))
        tally(W1); tally(W2)
      end
    end
    do
      local W3 = w(13009, 13109, 118, 1.0, "D3")
      local W4 = w(13010, 13110, 118, 0.5, "D4")
      if W3 ~= nil and W4 ~= nil then
        check(TAG .. "D3a: at 18 m lead 1.0 still fires at the 6.0 m bound edge (" .. #W3.fires .. ")",
          #W3.fires == 1 and lg111((TAG ~= "[live] ") or count_log(W3, "centre=6.0m") >= 1))
        check(TAG .. "D4a: the SAME 18 m world is SILENT at lead 0.5 (" .. #W4.fires
          .. ") - the fire moves to a smaller current distance", #W4.fires == 0)
        check(TAG .. "D4b: and the why-not band is the projected 10 m [live log]",
          lg111((TAG ~= "[live] ")
            or count_log(W4, "projected sep=~10m after delay=1.50s") >= 1))
        tally(W3); tally(W4)
      end
    end
  end

  -- ==========================================================================
  -- E: lead 0.0 == a STATIONARY caster (impact at the cast position).
  --    caster closing 8 m/s at x=100, enemy parked at 104:
  --      lead 0.0 -> projected (100.0, 200.0), 4.0 m, FIRES
  --      lead 0.5 -> projected (106.0, 200.0), 2.0 m, FIRES
  --      lead 1.0 -> projected (112.0, 200.0), 8.0 m, SILENT
  --      a PARKED caster at 104 -> projected (100.0, 200.0), 4.0 m, FIRES
  print("== HARNESS 111 - E: lead 0.0 treats the caster as stationary ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local function mov(uid, euid, lead, wname)
      local W = mk111(uid, { melee = false, pos = { 100, 30, 200 }, moving = true, fast = true,
          fast_speed = 8, ordered = { 300, 30, 200 } },
        { { name = INF, uid = euid, melee = true, pos = { 104, 0, 200 } } })
      inf111(W, euid, true); fly111(W, uid, true)
      if not boot111(W, PATH, TAG, uid, "death_from_above", wname, { lead = lead }) then
        return nil
      end
      polln(W, 2)
      return W
    end
    do
      local W0 = mov(13011, 13111, 0.0, "E1")
      local W5 = mov(13012, 13112, 0.5, "E2")
      local WH = mov(13013, 13113, 1.0, "E3")
      local WP = mk111(13014, { melee = false, pos = { 100, 30, 200 } },
        { { name = INF, uid = 13114, melee = true, pos = { 104, 0, 200 } } })
      inf111(WP, 13114, true); fly111(WP, 13014, true)
      if boot111(WP, PATH, TAG, 13014, "death_from_above", "E4", { lead = 0.5 })
        and W0 ~= nil and W5 ~= nil and WH ~= nil then
        polln(WP, 2)
        check(TAG .. "E1a: lead 0.0 fires a MOVING caster at 4 m - its projected point IS its current point ("
          .. #W0.fires .. ")", #W0.fires == 1)
        check(TAG .. "E1b: the log shows proj=(100.0, 200.0) with centre=4.0m [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W0, "proj=(100.0, 200.0)") >= 1 and count_log(W0, "centre=4.0m") >= 1)))
        check(TAG .. "E2a: the SHIPPED 0.5 projects 6 m ahead and also fires (2.0 m) (" .. #W5.fires .. ")",
          #W5.fires == 1 and lg111((TAG ~= "[live] ") or count_log(W5, "centre=2.0m") >= 1))
        check(TAG .. "E3a: lead 1.0 projects 12 m ahead and MISSES the same 4 m pair ("
          .. #WH.fires .. ")", #WH.fires == 0)
        check(TAG .. "E4a: a genuinely PARKED caster at the same 4 m also fires (" .. #WP.fires .. ")",
          #WP.fires == 1)
        check(TAG .. "E4b: and produces the SAME projected point (100.0, 200.0) and separation (4.0 m) [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(WP, "proj=(100.0, 200.0)") >= 1 and count_log(WP, "centre=4.0m") >= 1)))
        tally(W0); tally(W5); tally(WH); tally(WP)
      end
    end
  end

  -- ==========================================================================
  -- F: the caster delay is INDEPENDENT of the enemy delay.
  --    caster (60, 30, 200) closing 8 m/s; enemy (80, 0, 200) closing 4 m/s
  --    -> enemy projects 80 - 4*1.5 = 74.0 in BOTH worlds.
  --    caster delay 1.5 -> 60 + 12 = 72.0 (2.0 m gap) ; delay 1.0 -> 60 + 8 = 68.0 (6.0 m gap).
  print("== HARNESS 111 - F: shortening the caster delay moves ONLY the caster ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local function w(uid, euid, delay, wname)
      local W = mk111(uid, { melee = false, pos = { 60, 30, 200 }, moving = true, fast = true,
          fast_speed = 8, ordered = { 300, 30, 200 } },
        { { name = INF, uid = euid, melee = true, pos = { 80, 0, 200 }, moving = true,
            slow_speed = 4, ordered = { 0, 0, 200 } } })
      inf111(W, euid, true); fly111(W, uid, true)
      if not boot111(W, PATH, TAG, uid, "death_from_above", wname, { lead = 1.0, delay = delay }) then
        return nil
      end
      polln(W, 3)
      return W
    end
    do
      local WA = w(13015, 13115, 1.5, "F1")
      local WB = w(13016, 13116, 1.0, "F2")
      if WA ~= nil and WB ~= nil then
        check(TAG .. "F1a: with the caster delay 1.5 the caster projects x=72.0 and FIRES at 2.0 m ("
          .. #WA.fires .. ")", #WA.fires == 1 and lg111((TAG ~= "[live] ")
            or (count_log(WA, "proj=(72.0, 200.0)") >= 1
              and count_log(WA, "centre=2.0m") >= 1
              and count_log(WA, "delay_caster=1.50s") >= 1)))
        check(TAG .. "F2a: with the caster delay 1.0 the caster projects x=68.0 - 4 m less - and still fires (6.0 m)",
          #WB.fires == 1 and lg111((TAG ~= "[live] ")
            or (count_log(WB, "proj=(68.0, 200.0)") >= 1
              and count_log(WB, "centre=6.0m") >= 1
              and count_log(WB, "delay_caster=1.00s") >= 1)))
        check(TAG .. "F2b: the ENEMY projection is IDENTICAL in both worlds - (74.0, 200.0) [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(WA, "proj=(74.0, 200.0)") >= 1 and count_log(WB, "proj=(74.0, 200.0)") >= 1)))
        check(TAG .. "F2c: only the CASTER moved (2.0 -> 6.0 separation), never the enemy term [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(WA, "centre=2.0m") >= 1 and count_log(WB, "centre=6.0m") >= 1)))
        tally(WA); tally(WB)
      end
    end
  end

  -- ==========================================================================
  -- G: the PRE-CAST RE-CHECK re-projects with the SAME dials.
  --    caster closing 8 m/s at x=100; enemy 110 at the pick, then 105 (G1) or
  --    140 (G2). At lead 0.5 the caster projects 106 -> pick gaps 4.0 / 4.0,
  --    re-check gaps 1.0 / 34.0.
  print("== HARNESS 111 - G: the pre-cast re-check uses the same knobs ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local function w(uid, euid, seq, wname)
      local W = mk111(uid, { melee = false, pos = { 100, 30, 200 }, moving = true, fast = true,
          fast_speed = 8, ordered = { 300, 30, 200 } },
        { { name = INF, uid = euid, melee = true, pos_seq = seq } })
      inf111(W, euid, true); fly111(W, uid, true)
      if not boot111(W, PATH, TAG, uid, "death_from_above", wname, { lead = 0.5 }) then
        return nil
      end
      polln(W, 2)
      return W
    end
    do
      local W1 = w(13017, 13117, { { 110, 0, 200 }, { 105, 0, 200 } }, "G1")
      if W1 ~= nil then
        check(TAG .. "G1a: picked at a 4.0 m projection, still over it at the re-check - FIRES ("
          .. #W1.fires .. ")", #W1.fires == 1)
        check(TAG .. "G1b: the re-check line prints the RE-PROJECTED 1.0 m AND lead=0.50 [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W1, "pre-cast re-check: still over an INFANTRY enemy") >= 1
              and count_log(W1, "projected centre=1.0m") >= 1
              and count_log(W1, "delay_caster=1.50s lead=0.50") >= 1)))
        tally(W1)
      end
    end
    do
      local W2 = w(13018, 13118, { { 110, 0, 200 }, { 140, 0, 200 } }, "G2")
      if W2 ~= nil then
        check(TAG .. "G2a: a drift to 34.0 m at the SAME lead 0.5 SKIPS the cast (" .. #W2.fires .. ")",
          #W2.fires == 0)
        check(TAG .. "G2b: the skip line prints projected centre=34.0m and the same two dials [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W2, "SKIPPED: the drop lapsed before the cast") >= 1
              and count_log(W2, "projected centre=34.0m") >= 1
              and count_log(W2, "delay_caster=1.50s lead=0.50") >= 1)))
        tally(W2)
      end
    end
  end

  -- ==========================================================================
  if RED_MODE then
    check("HARNESS 110 suite boundary (harness 111): N/A in the red run - the pre-111 snapshot "
      .. "still carries every harness-110 world", true)
  else
    check("HARNESS 110 suite boundary (harness 111): every harness-110 check ran first ("
      .. pre111 .. ", want 4253)", pre111 == 4253)
  end
  check("HARNESS 111: the ZERO-search invariant still holds after the new section (counted "
    .. find_calls .. ")", find_calls == 0)
  print("== HARNESS 111 done: checks " .. checks .. ", failures " .. failures .. " ==")
end
