-- ============================================================================
-- HARNESS 109 - THE AIR DROP: A CENTRE-BASED OVERLAP TEST (round 109)
--
-- THE USER'S REPORT: "I tested again and because the distance is calculated
-- edge to edge, it still drops the rocks too soon." battle_unit:unit_distance()
-- is the shortest gap between the two BOUNDING BOXES (battle_unit.lua:160), so
-- two boxes can be almost touching while their CENTRES are 15 m apart - a wide
-- flying formation next to a wide infantry block reads "0.5 m away" while the
-- flyer is nowhere near over it. The 1 m edge bound therefore still fired too
-- early.
--
-- WHAT THIS SECTION PROVES, against the LIVE source AND the annotated copy:
--   S1-S8  the source carries the centre-based rule: the 6 m centre constant,
--          the ad_centre_gap helper, X/Z (never Y, which is HEIGHT), the
--          engine's distance_xz with an x/z fallback, the picker's gate on the
--          centre distance, the SAME test in the pre-cast re-check, the 70%
--          bypass still wired to the new constant, and the log carrying both
--          positions + the centre distance + the threshold.
--   B1  centre-under (both units at the same ground point) -> FIRES, on the
--       OWNER, and the log prints both positions and centre=0.0m.
--   B2  a 10 m CENTRE offset (box edges 0.5 m apart) -> SILENT, with the
--       "why it did not fire" line naming centre=10.0m.
--   B3  a 15 m CENTRE offset (box edges still 0.5 m apart) -> SILENT. THIS IS
--       THE EXACT FAILURE THE USER HIT: the old edge test fires here.
--   B4  NO radius/footprint read anywhere on either handle -> the constant
--       path still fires and the log says radius=none.
--   B5  a caster 60 m UP with the enemy directly beneath (the 3D distance is
--       60 m, the horizontal distance 0 m) -> FIRES: height is never read.
--   B6  the CLOSEST of two under-lying infantry units is the one named.
--   B7  a non-infantry unit directly under the caster -> SILENT.
--   B8  the enemy drifts from 2 m to 9 m between the pick and the pre-cast
--       re-check -> SKIPPED, cast not spent, and the line prints centre=9.0m.
--   B9  an unreadable position -> SILENT (fail-closed, no crash).
--   B10 the 6 m boundary itself: 6.0 m FIRES, 6.1 m stays SILENT.
--
-- RED CONTROL (H109_LIVE/H109_ANN -> docs/backups/round109/pre109_*.lua): the
-- pre-109 build has no centre helper and still gates on the edge gap, so every
-- S check fails and B2/B3/B10b FIRE (the reported bug reproduced).
-- ============================================================================
function run_h109()
  if os.getenv("H109_LIVE") ~= nil then LIVE = os.getenv("H109_LIVE") end
  if os.getenv("H109_ANN") ~= nil then ANN = os.getenv("H109_ANN") end
  local live_src109 = read_file(LIVE)
  local ann_src109  = read_file(ANN)
  local pre109 = checks
  local DFA = "wh2_dlc09_unit_abilities_death_from_above"
  local INF = "wh2_dlc13_emp_inf_spearmen_ror_0"
  local INF2 = "wh2_dlc09_tmb_inf_skeleton_warriors_0"
  local CAV = "wh2_dlc09_tmb_cav_necropolis_knights_0"

  local function cp109(s2, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s2, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function span109(s2, head, tail2)
    local i = raw_find(s2, head, 1, true)
    if i == nil then return nil end
    local j = raw_find(s2, tail2, i, true)
    if j == nil then return nil end
    return s2:sub(i, j)
  end
  local function lg109(cond) return cond == true end
  local function enemy_of109(W, uid)
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
  local function inf109(W, uid, v)
    local e = enemy_of109(W, uid)
    if e == nil then return end
    -- the ENGINE's own read, exactly as the real unit answers it
    e.is_infantry = function() return v == true end
  end
  local function fly109(W, uid, v)
    local u = unit_of(W, uid)
    if u == nil then u = enemy_of109(W, uid) end
    if u == nil then return end
    if v == "raise" then
      u.is_currently_flying = function() error("mock: is_currently_flying refused", 0) end
    else
      local b = (v == true)
      u.is_currently_flying = function() return b end
    end
  end
  local function mk109(uid, def, enemies, extra)
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
  local function boot109(W, PATH, TAG, uid, marker, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. marker); ui(W)
    W.conflict = true
    return true
  end

  -- ==========================================================================
  print("== HARNESS 109 - section 0aa: the CENTRE rule in the source (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src109 }, { name = "ann", src = ann_src109 } }) do
    local nm, s2 = f.name, f.src
    local pick = span109(s2, "function FOURTH.ad_pick(unit, routing)",
      "\nfunction FOURTH.evaluate_air_drop_on_infantry")
    local gapf = span109(s2, "function FOURTH.ad_centre_gap(unit, enemy)", "\nend")
    local rech = span109(s2, "if FOURTH.ad_enemy ~= nil then", "\n\t-- SELF-SUMMON RE-CHECK")
    local byp = span109(s2, "if ability.evaluate == FOURTH.evaluate_air_drop_on_infantry then", "\n\tend")
    check("0aa " .. nm .. ": the family takes the 6 m CENTRE constant and the old edge bound is GONE",
      raw_find(s2, "FOURTH.AIR_DROP_CENTER_M = 6", 1, true) ~= nil
      and raw_find(s2, "AIR_DROP_BOUND_M", 1, true) == nil)
    check("0aa " .. nm .. ": the centre-gap helper exists and the picker calls it",
      gapf ~= nil and pick ~= nil
      and raw_find(pick, "FOURTH.ad_centre_gap(unit, enemy)", 1, true) ~= nil)
    check("0aa " .. nm .. ": the helper reads the GROUND PLANE x/z and never the height y",
      gapf ~= nil
      and raw_find(gapf, "get_x()", 1, true) ~= nil
      and raw_find(gapf, "get_z()", 1, true) ~= nil
      and raw_find(gapf, "get_y()", 1, true) == nil)
    check("0aa " .. nm .. ": it uses the engine's horizontal primitive distance_xz with a sqrt(x,z) fallback",
      gapf ~= nil and raw_find(gapf, "distance_xz", 1, true) ~= nil
      and raw_find(gapf, "math.sqrt", 1, true) ~= nil)
    check("0aa " .. nm .. ": the picker's GATE is the centre distance (one edge read, diagnostic only)",
      pick ~= nil and raw_find(pick, "gap <= bound", 1, true) ~= nil
      and cp109(pick, "FOURTH.eg_enemy_gap") <= 1)
    check("0aa " .. nm .. ": the PRE-CAST re-check runs the SAME centre test",
      rech ~= nil and raw_find(rech, "FOURTH.ad_centre_gap", 1, true) ~= nil
      and raw_find(rech, "FOURTH.eg_enemy_gap", 1, true) == nil)
    check("0aa " .. nm .. ": the 70% map is still bypassed and now points at the centre constant",
      byp ~= nil and raw_find(byp, "ability.range_m = FOURTH.AIR_DROP_CENTER_M", 1, true) ~= nil)
    if nm == "live" then
      check("0aa " .. nm .. ": the target line prints BOTH positions, the centre distance and the threshold",
        raw_find(s2, "' is UNDER the caster", 1, true) ~= nil
        and raw_find(s2, "caster=\" .. FOURTH.ad_pos(best_ux, best_uz)", 1, true) ~= nil
        and raw_find(s2, "enemy=\" .. FOURTH.ad_pos(best_ex, best_ez)", 1, true) ~= nil
        and raw_find(s2, "\" centre=\" .. string.format(\"%.1f\", best_gap)", 1, true) ~= nil
        and raw_find(s2, "radius=none", 1, true) ~= nil
        and raw_find(s2, "watch: nearest INFANTRY ", 1, true) ~= nil)
    else
      check("0aa " .. nm .. ": the position formatter exists in the logic copy too",
        raw_find(s2, "function FOURTH.ad_pos(x, z)", 1, true) ~= nil
        and raw_find(s2, "radius=none", 1, true) == nil)
    end
  end

  -- ==========================================================================
  -- B1: centre-under -> FIRES.
  print("== HARNESS 109 - B1: both units at the same ground point -> FIRES ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid = 11901
    local W = mk109(uid, { melee = false, pos = { 100, 30, 200 },
        dist_by_target = { [11911] = 0.4 } },
      { { name = INF, uid = 11911, melee = true, pos = { 100, 0, 200 } } })
    inf109(W, 11911, true); fly109(W, uid, true)
    if boot109(W, PATH, TAG, uid, "death_from_above", "B1") then
      polln(W, 2)
      check(TAG .. "B1a: the enemy is UNDER the caster - fires once (" .. #W.fires .. ")", #W.fires == 1)
      check(TAG .. "B1b: the cast is on the OWNER (the row has no target flags)",
        #W.fires == 1 and W.fires[1].target == unit_of(W, uid))
      check(TAG .. "B1c: the target line prints the CENTRE distance [live log]",
        lg109((TAG ~= "[live] ")
          or (count_log(W, "' is UNDER the caster") >= 1
            and count_log(W, "centre=0.0m") >= 1)))
      check(TAG .. "B1d: and both positions, in metres on the ground plane [live log]",
        lg109((TAG ~= "[live] ")
          or (count_log(W, "caster=(100.0, 200.0)") >= 1
            and count_log(W, "enemy=(100.0, 200.0)") >= 1)))
      tally(W)
    end
  end

  -- B2: a 10 m CENTRE offset with the box edges 0.5 m apart -> SILENT.
  print("== HARNESS 109 - B2: 10 m centre offset (edges 0.5 m) -> SILENT ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid = 11902
    local W = mk109(uid, { melee = false, pos = { 100, 30, 200 },
        dist_by_target = { [11912] = 0.5 } },
      { { name = INF, uid = 11912, melee = true, pos = { 110, 0, 200 } } })
    inf109(W, 11912, true); fly109(W, uid, true)
    if boot109(W, PATH, TAG, uid, "death_from_above", "B2") then
      polln(W, 3)
      check(TAG .. "B2a: a 10 m centre offset is NOT under the caster - no fire (" .. #W.fires .. ")",
        #W.fires == 0)
      check(TAG .. "B2b: the why-not line names centre=10.0m [live log]",
        lg109((TAG ~= "[live] ")
          or (count_log(W, "watch: nearest INFANTRY '" .. INF .. "' is centre=~10m") == 1
            and count_log(W, "NOT under the caster") == 1)))
      check(TAG .. "B2c: nothing is attempted [live log]",
        lg109((TAG ~= "[live] ") or count_log(W, "ATTEMPT death_from_above") == 0))
      tally(W)
    end
  end

  -- B3: THE BUG. 15 m centre offset, box edges 0.5 m apart -> SILENT.
  print("== HARNESS 109 - B3: 15 m centre offset WITH CLOSE BOX EDGES -> SILENT (the reported bug) ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid = 11903
    local W = mk109(uid, { melee = false, pos = { 100, 30, 200 },
        dist_by_target = { [11913] = 0.5 } },
      { { name = INF, uid = 11913, melee = true, pos = { 115, 0, 200 } } })
    inf109(W, 11913, true); fly109(W, uid, true)
    if boot109(W, PATH, TAG, uid, "death_from_above", "B3") then
      polln(W, 3)
      check(TAG .. "B3a: the ENEMY'S BOX EDGE is 0.5 m away but its CENTRE is 15 m away - no fire ("
        .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "B3b: the why-not line proves the centre number decided it [live log]",
        lg109((TAG ~= "[live] ")
          or (count_log(W, "watch: nearest INFANTRY '" .. INF .. "' is centre=~15m") == 1)))
      check(TAG .. "B3c: the edge gap really was 0.5 m (the old rule's trigger) - it was NOT used [live log]",
        lg109((TAG ~= "[live] ") or count_log(W, "ATTEMPT death_from_above") == 0))
      tally(W)
    end
  end

  -- B4: no radius read anywhere -> the constant path, and it says so.
  print("== HARNESS 109 - B4: no radius/footprint read exists -> the constant path ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid = 11904
    local W = mk109(uid, { melee = false, pos = { 20, 30, 20 },
        dist_by_target = { [11914] = 0.3 } },
      { { name = INF, uid = 11914, melee = true, pos = { 22, 0, 20 } } })
    inf109(W, 11914, true); fly109(W, uid, true)
    if boot109(W, PATH, TAG, uid, "death_from_above", "B4") then
      local u = unit_of(W, uid)
      local e = enemy_of109(W, 11914)
      check(TAG .. "B4a: neither handle exposes radius / unit_radius / bounding_box / footprint",
        u ~= nil and e ~= nil
        and u.radius == nil and u.unit_radius == nil and u.bounding_box == nil and u.footprint == nil
        and e.radius == nil and e.unit_radius == nil and e.bounding_box == nil and e.footprint == nil)
      polln(W, 2)
      check(TAG .. "B4b: with no radius read the constant still fires (" .. #W.fires .. ")", #W.fires == 1)
      check(TAG .. "B4c: and the log states radius=none [live log]",
        lg109((TAG ~= "[live] ") or count_log(W, "radius=none") >= 1))
      tally(W)
    end
  end

  -- B5: a caster 60 m UP, enemy directly beneath -> FIRES (height never read).
  print("== HARNESS 109 - B5: a caster 60 m up, enemy directly beneath -> FIRES ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid = 11905
    local W = mk109(uid, { melee = false, pos = { 50, 60, 50 },
        dist_by_target = { [11915] = 0.2 } },
      { { name = INF, uid = 11915, melee = true, pos = { 50, 0, 50 } } })
    inf109(W, 11915, true); fly109(W, uid, true)
    if boot109(W, PATH, TAG, uid, "death_from_above", "B5") then
      local u = unit_of(W, uid)
      local e = enemy_of109(W, 11915)
      check(TAG .. "B5a: the 3D distance really is 60 m (the fixture is honest)",
        e ~= nil and math.abs(u:position():distance(e:position()) - 60) < 0.01)
      polln(W, 2)
      check(TAG .. "B5b: the HORIZONTAL distance decides - fires (" .. #W.fires .. ")", #W.fires == 1)
      check(TAG .. "B5c: and the log's centre is 0.0m, not 60 [live log]",
        lg109((TAG ~= "[live] ") or (count_log(W, "centre=0.0m") >= 1)))
      tally(W)
    end
  end

  -- B6: two infantry under the caster -> the CLOSEST is named.
  print("== HARNESS 109 - B6: two infantry under the caster -> the closest is named ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid = 11906
    local W = mk109(uid, { melee = false, pos = { 0, 30, 0 },
        dist_by_target = { [11916] = 4.0, [11917] = 1.0 } },
      { { name = INF, uid = 11916, melee = true, pos = { 5, 0, 0 } },
        { name = INF2, uid = 11917, melee = true, pos = { 2, 0, 0 } } })
    inf109(W, 11916, true); inf109(W, 11917, true); fly109(W, uid, true)
    if boot109(W, PATH, TAG, uid, "death_from_above", "B6") then
      polln(W, 2)
      check(TAG .. "B6a: fires once, on the owner (" .. #W.fires .. ")", #W.fires == 1)
      check(TAG .. "B6b: the CLOSEST centre (2 m) is the one named [live log]",
        lg109((TAG ~= "[live] ")
          or (count_log(W, "target: '" .. INF2 .. "'") >= 1
            and count_log(W, "centre=2.0m") >= 1)))
      tally(W)
    end
  end

  -- B7: a non-infantry unit directly under -> SILENT.
  print("== HARNESS 109 - B7: cavalry directly under the caster -> SILENT ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid = 11907
    local W = mk109(uid, { melee = false, pos = { 0, 30, 0 },
        dist_by_target = { [11918] = 0.1 } },
      { { name = CAV, uid = 11918, melee = true, pos = { 0, 0, 0 } } })
    inf109(W, 11918, false); fly109(W, uid, true)
    if boot109(W, PATH, TAG, uid, "death_from_above", "B7") then
      polln(W, 3)
      check(TAG .. "B7a: the centre test does not bypass the INFANTRY requirement ("
        .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "B7b: nothing is attempted [live log]",
        lg109((TAG ~= "[live] ") or count_log(W, "ATTEMPT death_from_above") == 0))
      tally(W)
    end
  end

  -- B8: the enemy DRIFTS from 2 m to 9 m between the pick and the re-check.
  print("== HARNESS 109 - B8: the enemy drifts out between pick and pre-cast re-check ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid = 11908
    local W = mk109(uid, { melee = false, pos = { 0, 30, 0 },
        dist_by_target = { [11919] = 0.2 } },
      { { name = INF, uid = 11919, melee = true,
          pos_seq = { { 2, 0, 0 }, { 9, 0, 0 } } } })
    inf109(W, 11919, true); fly109(W, uid, true)
    if boot109(W, PATH, TAG, uid, "death_from_above", "B8") then
      polln(W, 2)
      check(TAG .. "B8a: the re-check sees the 9 m position - the cast is NOT spent (" .. #W.fires .. ")",
        #W.fires == 0)
      check(TAG .. "B8b: the SKIPPED line names the centre distance that failed [live log]",
        lg109((TAG ~= "[live] ")
          or (count_log(W, "SKIPPED: the drop lapsed before the cast") >= 1
            and count_log(W, "centre=9.0m") >= 1)))
      tally(W)
    end
  end

  -- B9: an unreadable position -> SILENT, fail-closed.
  print("== HARNESS 109 - B9: an unreadable position -> SILENT (fail-closed) ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid = 11909
    local W = mk109(uid, { melee = false, pos = { 0, 30, 0 }, position_raises = true,
        dist_by_target = { [11920] = 0.1 } },
      { { name = INF, uid = 11920, melee = true, pos = { 0, 0, 0 } } })
    inf109(W, 11920, true); fly109(W, uid, true)
    if boot109(W, PATH, TAG, uid, "death_from_above", "B9") then
      polln(W, 3)
      check(TAG .. "B9a: no readable position means NOT under the caster - no fire (" .. #W.fires .. ")",
        #W.fires == 0)
      check(TAG .. "B9b: the attempted reads are recorded, so the fail-closed path really ran ("
        .. tostring(W.position_raise_attempts) .. ")", (W.position_raise_attempts or 0) > 0)
      tally(W)
    end
  end

  -- B10: the 6 m boundary itself.
  print("== HARNESS 109 - B10: the 6 m boundary - 6.0 fires, 6.1 does not ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid = 11910
    local W = mk109(uid, { melee = false, pos = { 0, 30, 0 }, dist_by_target = { [11921] = 0.1 } },
      { { name = INF, uid = 11921, melee = true, pos = { 6, 0, 0 } } })
    inf109(W, 11921, true); fly109(W, uid, true)
    if boot109(W, PATH, TAG, uid, "death_from_above", "B10a") then
      polln(W, 2)
      check(TAG .. "B10a: exactly 6.0 m is INSIDE the bound - fires (" .. #W.fires .. ")", #W.fires == 1)
      tally(W)
    end
    local uid2 = 11911
    local W2 = mk109(uid2, { melee = false, pos = { 0, 30, 0 }, dist_by_target = { [11922] = 0.1 } },
      { { name = INF, uid = 11922, melee = true, pos = { 6.1, 0, 0 } } })
    inf109(W2, 11922, true); fly109(W2, uid2, true)
    if boot109(W2, PATH, TAG, uid2, "death_from_above", "B10b") then
      polln(W2, 2)
      check(TAG .. "B10b: 6.1 m is OUTSIDE - no fire (" .. #W2.fires .. ")", #W2.fires == 0)
      tally(W2)
    end
  end

  -- B11: the watch line's two brakes - a distant enemy writes NOTHING.
  print("== HARNESS 109 - B11: a distant nearest enemy writes no watch line ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid = 11912
    local W = mk109(uid, { melee = false, pos = { 0, 30, 0 }, dist_by_target = { [11923] = 25.0 } },
      { { name = INF, uid = 11923, melee = true, pos = { 40, 0, 0 } } })
    inf109(W, 11923, true); fly109(W, uid, true)
    if boot109(W, PATH, TAG, uid, "death_from_above", "B11") then
      polln(W, 3)
      check(TAG .. "B11a: a 40 m nearest enemy never fires the drop (" .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "B11b: and writes NO watch line (the 30 m gate) [live log]",
        lg109((TAG ~= "[live] ") or count_log(W, "watch: nearest INFANTRY") == 0))
      tally(W)
    end
  end

  -- ==========================================================================
  if RED_MODE then
    check("HARNESS 108 suite boundary (harness 109): N/A in the red run - the pre-109 snapshot "
      .. "still carries every harness-108 world", true)
  else
    check("HARNESS 108 suite boundary (harness 109): every harness-108 check ran first ("
      .. pre109 .. ", want 4006)", pre109 == 4006)
  end
  check("HARNESS 109: the ZERO-search invariant still holds after the new section (counted "
    .. find_calls .. ")", find_calls == 0)
  print("== HARNESS 109 done: checks " .. checks .. ", failures " .. failures .. " ==")
end
run_h109()
