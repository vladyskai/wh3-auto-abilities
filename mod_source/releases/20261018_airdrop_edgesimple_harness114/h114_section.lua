-- ============================================================================
-- HARNESS 114 - THE AIR-DROP RULE IS ONE COMPARISON, AND A 0.2 s FAST PASS.
--
-- THE USER'S RULING, verbatim:
--   "1. I want the trigger to be checked much more frequently when armed and
--    less than 30 meters from a valid enemy unit.
--    2. Valid units are those who have more than 10 entities.
--    3. I trigger the moment distance between edges is below 0.1 meters.
--    That's it."
--   "1. Remove the 'and it is infantry'. No need for it now.
--    2. Current count 3. Let's try with 0.2 s for now."
--
-- THE RULE THE WORLDS BELOW PROVE:
--   candidate = alive and number_of_men_alive() > AIR_DROP_MIN_MEN (10)
--   valid     = its unit_distance() is readable
--   chosen    = the NEAREST valid candidate
--   FIRE      = unit_distance(caster, chosen) < AIR_DROP_EDGE_M (0.10 m)
--
-- PINS (asserted against BOTH files in section 0):
--     EDGE_M  AIR_DROP_EDGE_M  = 0.1
--     MIN_MEN AIR_DROP_MIN_MEN = 10
--     NEAR_M  AIR_DROP_NEAR_M  = 30
--     FAST_S  AIR_DROP_FAST_S  = 0.2
-- and the RETIRED constants/helpers must be GONE (listed in section 0).
--
-- RED CONTROL (H114_LIVE / H114_ANN -> docs/backups/round114/pre114_*.lua, the
-- round-113 build): there is no ad_nearest, no AIR_DROP_EDGE_M and no fast
-- pass, so every 0 check and every A-K world fails as designed.
-- ============================================================================
function run_h114()
  if os.getenv("H114_LIVE") ~= nil then LIVE = os.getenv("H114_LIVE") end
  if os.getenv("H114_ANN") ~= nil then ANN = os.getenv("H114_ANN") end
  local red114 = (os.getenv("H114_LIVE") ~= nil) or (os.getenv("H114_ANN") ~= nil)
  local live_src = read_file(LIVE)
  local ann_src = read_file(ANN)
  local pre114 = checks
  local DFA = "wh2_dlc09_unit_abilities_death_from_above"
  local CAV = "wh_main_cav_emp_knights"
  local LORD = "wh_main_lord_emp_general"
  local OTHER = "wh3_main_character_abilities_deadly_onslaught"

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
  -- unit_distance is called ON THE CASTER with the enemy as its argument, so the
  -- mock answer lives on the caster: dm = { [enemy_uid] = metres }, or dseq =
  -- { d1, d2, ... } for a per-READ sequence, or draise for an unreadable read.
  local function mk(uid, def, enemies, dm, dseq, draise)
    def.name = def.name or "sky_junk"
    def.uid = uid
    def.owns = def.owns or { DFA }
    if dm ~= nil then def.dist_by_target = dm end
    if dseq ~= nil then def.dist_seq = dseq end
    if draise then def.dist_raises = true end
    local bar = {}
    for i = 1, #def.owns do bar[i] = { id = "b" .. i, key = def.owns[i] } end
    local W = make_world({ can_perform = true, units = { def }, enemies = enemies,
      cards = { { id = tostring(uid), state = "active", vis = true } }, bar = bar })
    -- the air-drop rows are air-only: the caster must answer flying = true
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
  print("== HARNESS 114 - section 0: the four pins, and what was RETIRED (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src }, { name = "ann", src = ann_src } }) do
    local nm, s2 = f.name, f.src
    local pick = span(s2, "function FOURTH.ad_pick(unit, routing)",
      "\nfunction FOURTH.evaluate_air_drop_on_infantry")
    local near = span(s2, "function FOURTH.ad_nearest(unit)", "\nfunction FOURTH.ad_pick")
    local fast = span(s2, "function FOURTH.ad_fast_pass()", "\nbm:repeat_callback(poll, POLL_MS, POLL_NAME)")

    check("0 " .. nm .. ": the FOUR new constants are defined EXACTLY ONCE (0.1 m / 10 men / 30 m / 0.2 s)",
      cp(s2, "\nFOURTH.AIR_DROP_EDGE_M = 0.1\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_MIN_MEN = 10\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_NEAR_M = 30\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_FAST_S = 0.2\n") == 1)
    -- (the round-114 header comment still NAMES the retired constants as history,
    -- so this counts the LIVE form - "FOURTH.<name>" - which is what code used)
    check("0 " .. nm .. ": the FOUR DIALS, the 6 m bound, AIR_DROP_INHERIT and the frontage constants are GONE",
      cp(s2, "FOURTH.AIR_DROP_CENTER_M") == 0
      and cp(s2, "FOURTH.AIR_DROP_DELAY_S") == 0
      and cp(s2, "FOURTH.AIR_DROP_ENEMY_LEAD") == 0
      and cp(s2, "FOURTH.AIR_DROP_CASTER_DELAY_S") == 0
      and cp(s2, "FOURTH.AIR_DROP_CASTER_LEAD") == 0
      and cp(s2, "FOURTH.AIR_DROP_INHERIT") == 0
      and cp(s2, "FOURTH.AIR_DROP_MODEL_RADIUS_M") == 0
      and cp(s2, "FOURTH.AIR_DROP_RANKS") == 0
      and cp(s2, "FOURTH.AIR_DROP_FRONTAGE_MIN_M") == 0
      and cp(s2, "FOURTH.AIR_DROP_FRONTAGE_MAX_M") == 0
      and cp(s2, "\nFOURTH.AIR_DROP_EDGE_M = 0.1\n") == 1)
    check("0 " .. nm .. ": the projection / frontage / segment / centre helpers are GONE (12 definitions)",
      cp(s2, "function FOURTH.ad_frontage(") == 0
      and cp(s2, "function FOURTH.ad_frontage_text(") == 0
      and cp(s2, "function FOURTH.ad_seg_dist(") == 0
      and cp(s2, "function FOURTH.ad_velocity(") == 0
      and cp(s2, "function FOURTH.ad_lead(") == 0
      and cp(s2, "function FOURTH.ad_project(") == 0
      and cp(s2, "function FOURTH.ad_dial_text(") == 0
      and cp(s2, "function FOURTH.ad_single_say(") == 0
      and cp(s2, "function FOURTH.ad_single_clear(") == 0
      and cp(s2, "function FOURTH.ad_centre_gap(") == 0
      and cp(s2, "function FOURTH.ad_pos(") == 0
      and cp(s2, "function FOURTH.ad_sep(") == 0)
    check("0 " .. nm .. ": NOTHING else called them either (no ad_lead / ad_seg_dist / ad_frontage call sites)",
      cp(s2, "FOURTH.ad_lead(") == 0 and cp(s2, "FOURTH.ad_seg_dist(") == 0
      and cp(s2, "FOURTH.ad_frontage(") == 0 and cp(s2, "FOURTH.ad_centre_gap(") == 0
      and cp(s2, "FOURTH.ad_dial_text(") == 0 and cp(s2, "FOURTH.ad_project(") == 0)
    check("0 " .. nm .. ": ad_nearest is the WHOLE filter - alive, > AIR_DROP_MIN_MEN, readable distance",
      near ~= nil
      and raw_find(near, "enemy:number_of_men_alive()", 1, true) ~= nil
      and raw_find(near, "alive > FOURTH.AIR_DROP_MIN_MEN", 1, true) ~= nil
      and raw_find(near, "FOURTH.eg_enemy_gap(unit, enemy)", 1, true) ~= nil
      and raw_find(near, "d < best_d", 1, true) ~= nil)
    check("0 " .. nm .. ": ad_nearest applies NO infantry test and NO initial-count test",
      near ~= nil and raw_find(near, "enemy_is_infantry", 1, true) == nil
      and raw_find(near, "initial_number_of_men", 1, true) == nil
      and raw_find(near, "ordered_width", 1, true) == nil)
    check("0 " .. nm .. ": the DECISION is one comparison (dist >= AIR_DROP_EDGE_M -> NOT YET)",
      pick ~= nil
      and raw_find(pick, "if dist >= FOURTH.AIR_DROP_EDGE_M then", 1, true) ~= nil
      and raw_find(pick, "enemy_is_infantry", 1, true) == nil
      and raw_find(pick, "initial_number_of_men", 1, true) == nil
      and raw_find(pick, "AIR_DROP_DELAY_S", 1, true) == nil)
    check("0 " .. nm .. ": the decision carries the ui id, the type, the entity count and the exact edge",
      pick ~= nil
      and raw_find(pick, "nearest valid:'", 1, true) ~= nil
      and raw_find(pick, 'FOURTH.ad_say(unit, marker, "nearest valid:\'', 1, true) ~= nil
      and raw_find(pick, "' entities=", 1, true) ~= nil
      and raw_find(pick, '" edge="', 1, true) ~= nil
      and raw_find(pick, '"m (need < "', 1, true) ~= nil
      and ((nm ~= "live")
        or raw_find(pick, "ad_tag(unit)", 1, true) == nil))
    check("0 " .. nm .. ": ONE copy of the gates + cast for BOTH timers (FOURTH.try_pair: 1 def + 2 calls)",
      cp(s2, "function FOURTH.try_pair(") == 1 and cp(s2, "FOURTH.try_pair(") == 3)
    check("0 " .. nm .. ": the fast pass runs ONLY the air-drop list, gated on AIR_DROP_NEAR_M",
      fast ~= nil
      and raw_find(fast, "local list = FOURTH.ad_fast_abilities", 1, true) ~= nil
      and raw_find(fast, "#list", 1, true) ~= nil
      and raw_find(fast, "dist < FOURTH.AIR_DROP_NEAR_M", 1, true) ~= nil
      and raw_find(fast, "ability.evaluate(unit, routing)", 1, true) ~= nil
      and raw_find(fast, "FOURTH.try_pair(", 1, true) ~= nil
      and raw_find(fast, "ABILITIES", 1, true) == nil)
    check("0 " .. nm .. ": the transition is a CHANGE gate (near ~= was), so it cannot log per tick",
      fast ~= nil
      and raw_find(fast, "if near ~= was then", 1, true) ~= nil
      and raw_find(fast, "FOURTH.ad_fast_on[uid] = near", 1, true) ~= nil
      and ((nm ~= "live")
        or (raw_find(fast, '"fast poll: ON (nearest valid "', 1, true) ~= nil
          and raw_find(fast, '"fast poll: OFF"', 1, true) ~= nil)))
    check("0 " .. nm .. ": the fast timer is registered on AIR_DROP_FAST_S and POLL_MS is UNTOUCHED",
      cp(s2, "local POLL_MS = 250") == 1
      and cp(s2, "math.floor(FOURTH.AIR_DROP_FAST_S * 1000)") == 1
      and cp(s2, 'bm:repeat_callback(poll, POLL_MS, POLL_NAME)') == 1
      and cp(s2, "zz_test_deadly_onslaught_air_drop_fast") == 1)
    check("0 " .. nm .. ": air_only / no_melee / the self-centred cast / fail-closed are ALL still in place",
      raw_find(s2, "is_currently_flying()", 1, true) ~= nil
      and raw_find(s2, "is_in_melee()", 1, true) ~= nil
      and raw_find(s2, "FOURTH.ad_air_only", 1, true) ~= nil
      and raw_find(s2, "FOURTH.ad_no_melee", 1, true) ~= nil
      and raw_find(s2, "perform_special_ability", 1, true) ~= nil)
    check("0 " .. nm .. ": the family counts are unchanged (12 air-drop entries of 689)",
      cp(s2, 'trigger = "air_drop_on_infantry"') == 12 and cp(s2, "\t{ marker = ") == 689)
    check("0 " .. nm .. ": the tooltip sentence states the NEW rule",
      raw_find(s2, "air_drop_on_infantry = \"When armed, fires when the nearest enemy unit with more than 10 models is within 0.1 m", 1, true) ~= nil)
    if nm == "live" then
      check("0 live: every decision + transition line carries the caster ui id (ad_tag definition + 5 sites)",
        cp(s2, "FOURTH.ad_tag(unit)") == 6)
    else
      check("0 ann: the reading copy stays LOG-FREE and carries the same four helpers",
        raw_find(s2, "log(", 1, true) == nil
        and raw_find(s2, "function FOURTH.ad_nearest(unit)", 1, true) ~= nil
        and raw_find(s2, "function FOURTH.try_pair(", 1, true) ~= nil
        and raw_find(s2, "function FOURTH.ad_fast_pass()", 1, true) ~= nil)
    end
  end

  -- ==========================================================================
  print("== HARNESS 114 - A: 0.09 m FIRES, 0.11 m does NOT (the 0.1 m line) ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    do
      local uid, euid = 16001, 16101
      local W = mk(uid, {}, { { name = "wh_main_inf_zombie_0", uid = euid, men_alive = 20 } },
        { [euid] = 0.09 })
      if boot(W, PATH, TAG, uid, "A0") then
        polln(W, 2)
        check(TAG .. "A0a: a 20-model enemy 0.09 m from the edge FIRES (" .. #W.fires .. ")", #W.fires == 1)
        check(TAG .. "A0b: the decision line carries ui id, type, entities and the exact edge [live log]",
          lg((TAG ~= "[live] ")
            or (cl(W, "[16001] death_from_above nearest valid:'wh_main_inf_zombie_0' entities=20 edge=0.09m (need < 0.10m) -> FIRING") >= 1)))
        tally(W)
      end
    end
    do
      local uid, euid = 16002, 16102
      local W = mk(uid, {}, { { name = "wh_main_inf_zombie_0", uid = euid, men_alive = 20 } },
        { [euid] = 0.11 })
      if boot(W, PATH, TAG, uid, "A1") then
        polln(W, 3)
        check(TAG .. "A1a: 0.11 m is NOT under the 0.10 m line - SILENT (" .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "A1b: the NOT YET line prints the exact number it refused on [live log]",
          lg((TAG ~= "[live] ")
            or (cl(W, "entities=20 edge=0.11m (need < 0.10m) -> NOT YET") >= 1)))
        tally(W)
      end
    end
  end

  -- ==========================================================================
  print("== HARNESS 114 - B: 10 entities is NOT a candidate, 11 IS ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    do
      local uid, euid = 16003, 16103
      local W = mk(uid, {}, { { name = "wh_main_inf_zombie_0", uid = euid, men_alive = 10 } },
        { [euid] = 0.0 })
      if boot(W, PATH, TAG, uid, "B10") then
        polln(W, 3)
        check(TAG .. "B10a: 10 entities is NOT > 10 - never a candidate, even at 0.00 m ("
          .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "B10b: and it is not even MEASURED - no decision line at all [live log]",
          lg((TAG ~= "[live] ") or (cl(W, "nearest valid:") == 0)))
        tally(W)
      end
    end
    do
      local uid, euid = 16004, 16104
      local W = mk(uid, {}, { { name = "wh_main_inf_zombie_0", uid = euid, men_alive = 11 } },
        { [euid] = 0.05 })
      if boot(W, PATH, TAG, uid, "B11") then
        polln(W, 2)
        check(TAG .. "B11a: 11 entities IS a candidate and 0.05 m fires (" .. #W.fires .. ")",
          #W.fires == 1)
        check(TAG .. "B11b: the line says entities=11 [live log]",
          lg((TAG ~= "[live] ") or (cl(W, "entities=11 edge=0.05m") >= 1)))
        tally(W)
      end
    end
  end

  -- ==========================================================================
  print("== HARNESS 114 - C: a 20-model CAVALRY unit is now a legal candidate ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 16005, 16105
    local W = mk(uid, {}, { { name = CAV, uid = euid, men_alive = 20 } }, { [euid] = 0.08 })
    if boot(W, PATH, TAG, uid, "C") then
      local e = nil
      if W.enemy_entries ~= nil then
        for i = 1, #W.enemy_entries do
          local pr = W.enemy_entries[i]
          if pr ~= nil and pr.unit ~= nil then
            local ok, id = pcall(function() return pr.unit:unique_ui_id() end)
            if ok and tostring(id) == tostring(euid) then e = pr.unit end
          end
        end
      end
      if e ~= nil then e.is_infantry = function() return false end end
      polln(W, 2)
      check(TAG .. "C1a: the infantry filter is GONE from this evaluator - 20 cavalry at 0.08 m FIRES ("
        .. #W.fires .. ")", #W.fires == 1)
      check(TAG .. "C1b: the line names the cavalry key [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "nearest valid:'" .. CAV .. "'") >= 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 114 - D: a ONE-model lord at 0.00 m is excluded by the > 10 test ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 16006, 16106
    local W = mk(uid, {}, { { name = LORD, uid = euid, men_alive = 1 } }, { [euid] = 0.0 })
    if boot(W, PATH, TAG, uid, "D") then
      polln(W, 3)
      check(TAG .. "D1a: a one-model lord at 0.00 m does NOT fire (" .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "D1b: no decision line was written for it [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "nearest valid:") == 0)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 114 - E: the NEAREST valid enemy wins ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid1, euid2 = 16007, 16107, 16108
    local W = mk(uid, {}, {
      { name = "wh_main_inf_zombie_0", uid = euid1, men_alive = 20 },
      { name = "wh_main_inf_skeleton_warriors", uid = euid2, men_alive = 20 } },
      { [euid1] = 0.9, [euid2] = 0.04 })
    if boot(W, PATH, TAG, uid, "E") then
      polln(W, 2)
      check(TAG .. "E1a: two valid enemies - the 0.04 m one is chosen, so it FIRES (" .. #W.fires .. ")",
        #W.fires == 1)
      check(TAG .. "E1b: the decision names the NEAREST one and its edge [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "nearest valid:'wh_main_inf_skeleton_warriors' entities=20 edge=0.04m") >= 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 114 - F: the pre-cast re-check re-measures and SKIPS on drift ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 16008, 16109
    local W = mk(uid, {}, { { name = "wh_main_inf_zombie_0", uid = euid, men_alive = 20 } },
      nil, { 0.05, 0.2 })
    if boot(W, PATH, TAG, uid, "F") then
      polln(W, 2)
      check(TAG .. "F1a: picked at 0.05 m, 0.20 m at the re-check - the cast is NOT spent ("
        .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "F1b: the SKIPPED-at-re-check line prints the FRESH edge [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "edge=0.20m (need < 0.10m) -> SKIPPED at re-check") >= 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 114 - G: the fast pass turns ON inside 30 m and OFF beyond, ONE line each ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 16009, 16110
    local dm = { [euid] = 20 }
    local edef = { name = "wh_main_inf_zombie_0", uid = euid, men_alive = 20 }
    local W = mk(uid, {}, { edef }, dm)
    if boot(W, PATH, TAG, uid, "G") then
      polln(W, 2)
      check(TAG .. "G0: the fast timer exists in this build", W.fast_fn ~= nil)
      check(TAG .. "G0b: and it is registered at 200 ms (AIR_DROP_FAST_S x 1000)", W.fast_ms == 200)
      fastn(W, 1)
      check(TAG .. "G1a: inside 30 m the fast pass turns ON, once [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "fast poll: ON (nearest valid 20.0m)") == 1)))
      fastn(W, 3)
      check(TAG .. "G1b: three more ticks add NO second ON line [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "fast poll: ON") == 1)))
      dm[euid] = 40
      fastn(W, 1)
      check(TAG .. "G2a: beyond 30 m it turns OFF, once [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "fast poll: OFF") == 1)))
      fastn(W, 3)
      check(TAG .. "G2b: and stays silent afterwards [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "fast poll: OFF") == 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 114 - H: TWO consecutive fast ticks can only cast ONCE ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 16010, 16111
    local dm = { [euid] = 20 }
    local edef = { name = "wh_main_inf_zombie_0", uid = euid, men_alive = 20 }
    local W = mk(uid, {}, { edef }, dm)
    if boot(W, PATH, TAG, uid, "H") then
      polln(W, 2)
      check(TAG .. "H0: nothing fired while the enemy was 20 m away (" .. #W.fires .. ")",
        #W.fires == 0)
      dm[euid] = 0.04
      fastn(W, 1)
      check(TAG .. "H1a: the first fast tick fires the drop (" .. #W.fires .. ")", #W.fires == 1)
      fastn(W, 1)
      check(TAG .. "H1b: the SECOND fast tick in the same poll window does NOT cast again ("
        .. #W.fires .. ")", #W.fires == 1)
      fastn(W, 5)
      check(TAG .. "H1c: nor do five more (" .. #W.fires .. ")", #W.fires == 1)
      polln(W, 1)
      check(TAG .. "H1d: nor does the next poll, inside the guard (" .. #W.fires .. ")",
        #W.fires == 1)
      check(TAG .. "H1e: ONE picker FIRING line and ONE re-checked FIRING line - no second cast"
        .. " (pick " .. cl(W, "-> FIRING (the nearest") .. ", re-check "
        .. cl(W, "-> FIRING (re-checked)") .. ") [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "-> FIRING (the nearest") == 1 and cl(W, "-> FIRING (re-checked)") == 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 114 - I: an UNREADABLE unit_distance fails CLOSED ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 16011, 16112
    local W = mk(uid, {}, { { name = "wh_main_inf_zombie_0", uid = euid, men_alive = 20 } },
      nil, nil, true)
    if boot(W, PATH, TAG, uid, "I") then
      polln(W, 3)
      check(TAG .. "I1a: no readable distance -> no candidate -> no cast (" .. #W.fires .. ")",
        #W.fires == 0)
      check(TAG .. "I1b: and no decision line was invented [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "nearest valid:") == 0)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 114 - J: the fast pass never runs a NON-air-drop ability ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 16012, 16113
    local W = mk(uid, { owns = { OTHER } },
      { { name = "wh_main_inf_zombie_0", uid = euid, men_alive = 20 } }, { [euid] = 0.0 })
    if boot(W, PATH, TAG, uid, "J") then
      polln(W, 2)
      fastn(W, 5)
      check(TAG .. "J1a: an enemy at 0.00 m with a NON-air-drop ability armed fires nothing ("
        .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "J1b: and the fast pass wrote no air-drop line for it [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "fast poll:") == 0 and cl(W, "nearest valid:") == 0)))
      tally(W)
    end
  end

  -- ==========================================================================
  if red114 then
    check("HARNESS 113 suite boundary (harness 114): N/A in the red run - the pre-114 snapshot "
      .. "still carries every harness-112 world", true)
  else
    check("HARNESS 112 suite boundary (harness 114): every earlier check ran first ("
      .. pre114 .. ", want 4492)", pre114 == 4492)
  end
  check("HARNESS 114: the ZERO-search invariant still holds after the new section (counted "
    .. find_calls .. ")", find_calls == 0)
  print("== HARNESS 114 done: checks " .. checks .. ", failures " .. failures .. " ==")
end
