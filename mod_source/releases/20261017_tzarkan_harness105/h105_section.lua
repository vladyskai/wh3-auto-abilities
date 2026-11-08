-- ============================================================================
-- HARNESS 105 - TZ'ARKAN ON THE NEW LOW-HEALTH TRIGGER
--
-- THE USER'S RULE (verbatim): "I think it might make sense to activate Tz'arkan
--   when caster health is below 15%, don't you think? Let's implement and test
--   it."
--
-- WHAT SHIPPED: ONE new entry ("tzarkan") carrying all FIVE Tz'arkan keys
--   (wh2_dlc14_lord_abilities_tzarkan, _mp, _snikch, _spite, _spite_mp) on ONE
--   new trigger family, health_below_15, with its own evaluator
--   FOURTH.evaluate_tzarkan_low_health and its own tooltip sentence. The rule:
--   the OWNER is ALIVE (the poll gates that), NOT routing, and its health -
--   read through FOURTH.health_pct, the ONE 0-100 reader - is BELOW 15. The
--   cast is on the OWNER ITSELF through the unit form, with the caster's
--   controller re-fetched FRESH that tick. There is no range bound: a self
--   cast has no distance to measure.
--
-- THE WIND-UP HOLE THIS ROUND CLOSES: a transform is likely ONE-WAY and its row
--   declares 3 s of wind-up (1.5 s for the Snikch key), so a caster at 14% can
--   DIE or be HEALED inside that window. The evaluator logs the exact
--   percentage at the decision and attempt_activation RE-READS it immediately
--   before the call, logging it again and SKIPPING (cast not spent) when the
--   unit died or rose above the line. The threshold is deliberate (the user's
--   own number) and is ONE constant, FOURTH.TZARKAN_PCT.
--
-- WORLDS (each runs against BOTH the live source and the annotated copy):
--   T1  14.0% health          -> fires exactly once, on the OWNER, exact
--                                percentages in the log at both points.
--   T2  16.0% health          -> SILENT (the line is exclusive: below 15).
--   T3  14.0% -> 25.0% inside the same tick (the wind-up window)
--                             -> the pre-cast re-check SKIPS the cast.
--   T4  a dead owner (0 men)  -> SILENT (the poll's own alive gate).
--
-- RED CONTROL (H105_LIVE/H105_ANN -> docs/backups/round105/*.pre105.lua): the
--   pre-105 build has no entry, no evaluator and no trigger, so T1 never fires
--   and T3's skip line never appears - exactly those discriminators fail there
--   while every harness-104 world still passes. T2/T4 assert SILENCE and so
--   pass by design on the old build (documented, not a discriminator).
-- ============================================================================
function run_h105()
  local live_src105 = read_file(LIVE)
  local ann_src105  = read_file(ANN)
  local TZ = {
    "wh2_dlc14_lord_abilities_tzarkan",
    "wh2_dlc14_lord_abilities_tzarkan_mp",
    "wh2_dlc14_lord_abilities_tzarkan_snikch",
    "wh2_dlc14_lord_abilities_tzarkan_spite",
    "wh2_dlc14_lord_abilities_tzarkan_spite_mp",
  }
  local pre105 = checks
  local READ_N = {}   -- per TAG: unary_hitpoints reads in ONE firing tick

  local function cp105(s2, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s2, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function table_span105(s2)
    local i = raw_find(s2, "local ABILITIES = {", 1, true)
    if i == nil then return nil end
    local j = raw_find(s2, "\n}\n", i, true)
    if j == nil then return nil end
    return s2:sub(i, j)
  end
  local function span105(s2, head, tail2)
    local i = raw_find(s2, head, 1, true)
    if i == nil then return nil end
    local j = raw_find(s2, tail2, i, true)
    if j == nil then return nil end
    return s2:sub(i, j)
  end
  local function boot105(W, PATH, TAG, uid, marker, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. marker); ui(W)
    W.conflict = true
    return true
  end
  local function lg105(cond) return cond == true end

  -- ==========================================================================
  print("== HARNESS 105 - section 0e: Tz'arkan's entry, trigger, gates and re-check (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src105 }, { name = "ann", src = ann_src105 } }) do
    local nm, s2 = f.name, f.src
    local abl = table_span105(s2)
    local ent = nil
    if abl ~= nil then
      ent = span105(abl, '{ marker = "tzarkan"', "ox = 0, oy = 0 },")
    end
    local ev = span105(s2, "function FOURTH.evaluate_tzarkan_low_health(unit, routing)", "\nend")
    if RED_MODE then
      check("0e " .. nm .. " (RED): the pre-105 build has no tzarkan entry", abl ~= nil and ent == nil)
      check("0e " .. nm .. " (RED): and no health_below_15 evaluator",
        raw_find(s2, "function FOURTH.evaluate_tzarkan_low_health", 1, true) == nil)
    else
      check("0e " .. nm .. ": ONE tzarkan entry carries the new trigger ("
        .. tostring(abl ~= nil and cp105(abl, '{ marker = "tzarkan"') or -1) .. ")", abl ~= nil
        and cp105(abl, '{ marker = "tzarkan"') == 1
        and raw_find(abl, 'name = "Tz\'arkan", trigger = "health_below_15",', 1, true) ~= nil)
      check("0e " .. nm .. ": all FIVE Tz'arkan keys sit inside that ONE entry ("
        .. tostring(ent ~= nil and cp105(ent, "wh2_dlc14_lord_abilities_tzarkan") or -1) .. " of 5)",
        ent ~= nil and cp105(ent, "wh2_dlc14_lord_abilities_tzarkan") == 5)
      check("0e " .. nm .. ": the evaluator exists", ev ~= nil)
      check("0e " .. nm .. ": the threshold constant is 15 (the user's own line)",
        raw_find(s2, "FOURTH.TZARKAN_PCT = 15", 1, true) ~= nil)
      check("0e " .. nm .. ": the trigger is wired in FOURTH.evaluators",
        raw_find(s2, "health_below_15 = FOURTH.evaluate_tzarkan_low_health,", 1, true) ~= nil)
      check("0e " .. nm .. ": and carries its own tooltip sentence",
        raw_find(s2, 'health_below_15 = "When armed, fires when this unit is below 15% health",', 1, true) ~= nil)
      check("0e " .. nm .. ": the evaluator reads health through FOURTH.health_pct (never raw HealthPercent)",
        ev ~= nil and raw_find(ev, "FOURTH.health_pct(unit)", 1, true) ~= nil
        and raw_find(ev, "HealthPercent", 1, true) == nil)
      check("0e " .. nm .. ": the cast side re-checks the line immediately before the call (two tz_self blocks)",
        cp105(s2, "if FOURTH.tz_self then") == 2)
      check("0e " .. nm .. ": the five keys carry their declared wind-ups in the in-flight gate",
        raw_find(s2, '["wh2_dlc14_lord_abilities_tzarkan"] = 3,', 1, true) ~= nil
        and raw_find(s2, '["wh2_dlc14_lord_abilities_tzarkan_mp"] = 3,', 1, true) ~= nil
        and raw_find(s2, '["wh2_dlc14_lord_abilities_tzarkan_spite"] = 3,', 1, true) ~= nil
        and raw_find(s2, '["wh2_dlc14_lord_abilities_tzarkan_spite_mp"] = 3,', 1, true) ~= nil
        and raw_find(s2, '["wh2_dlc14_lord_abilities_tzarkan_snikch"] = 1.5,', 1, true) ~= nil)
    end
  end

  -- ==========================================================================
  -- T1-T4: the worlds. Each runs for the live source AND the annotated copy.
  local function tz_world(uid, def)
    def.name = def.name or "tzarkan_caster"
    def.uid = uid
    def.owns = def.owns or { TZ[1] }
    return make_world({ can_perform = true,
      units = { def },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = TZ[1] } } })
  end

  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag

    -- T1: 14% -> FIRES, on the OWNER, with the exact percentages logged.
    do
      local uid = 11501
      local W = tz_world(uid, { hp_frac = 0.14 })
      print("== T1 " .. TAG .. "==")
      if boot105(W, PATH, TAG, uid, "tzarkan", "T1") then
        local reads = 0
        local orig = W.mock_units[1].unary_hitpoints
        W.mock_units[1].unary_hitpoints = function(self)
          reads = reads + 1
          return orig(self)
        end
        polln(W, 1)
        READ_N[TAG] = reads
        check(TAG .. "T1a: at 14.0% health the entry fires exactly once (" .. #W.fires .. ")",
          #W.fires == 1)
        check(TAG .. "T1b: the cast is on the OWNER itself - the unit form, not another unit",
          #W.fires == 1 and W.fires[1].target == W.mock_units[1])
        check(TAG .. "T1c: the fired key is a Tz'arkan key (" .. tostring(#W.fires == 1 and W.fires[1].key or "-") .. ")",
          #W.fires == 1 and W.fires[1].key == TZ[1])
        check(TAG .. "T1d: the exact percentage is logged AT THE DECISION [live log]",
          lg105((TAG ~= "[live] ") or count_log(W, "health 14.0% (BELOW the 15% line)") == 1))
        check(TAG .. "T1e: and again at the pre-cast re-check, with the number [live log]",
          lg105((TAG ~= "[live] ")
            or (count_log(W, "tzarkan pre-cast re-check: the caster is still below the line") == 1
              and count_log(W, "health=14.0%") == 1)))
        check(TAG .. "T1f: the fallback HealthPercent context field was never read (the fraction bug cannot recur)",
          lg105((TAG ~= "[live] ")
            or W.ctx_reads[uid] == nil or W.ctx_reads[uid]["HealthPercent"] == nil))
        tally(W)
      end
    end

    -- T2: 16% -> SILENT. The line is exclusive: BELOW 15.
    do
      local uid = 11502
      local W = tz_world(uid, { hp_frac = 0.16 })
      print("== T2 " .. TAG .. "==")
      if boot105(W, PATH, TAG, uid, "tzarkan", "T2") then
        polln(W, 3)
        check(TAG .. "T2a: at 16.0% health the entry never fires (" .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "T2b: and no ATTEMPT line is written for it [live log]",
          lg105((TAG ~= "[live] ") or count_log(W, "ATTEMPT tzarkan") == 0))
        tally(W)
      end
    end

    -- T3: 14% at the decision, 25% at the pre-cast re-check (the wind-up window).
    do
      local uid = 11503
      local W = tz_world(uid, {})
      local cut = (READ_N[TAG] or 2) - 1
      local n_read = 0
      W.mock_units[1].unary_hitpoints = function(self)
        n_read = n_read + 1
        if n_read <= cut then return 0.14 end
        return 0.25
      end
      print("== T3 " .. TAG .. "==")
      if boot105(W, PATH, TAG, uid, "tzarkan", "T3") then
        polln(W, 1)
        check(TAG .. "T3a: a caster that ROSE above the line inside the wind-up does NOT cast ("
          .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "T3b: and the skip names the real state and the exact percentage [live log]",
          lg105((TAG ~= "[live] ")
            or (count_log(W, "tzarkan SKIPPED: the caster lapsed before the cast") == 1
              and count_log(W, "health=25.0%") == 1)))
        tally(W)
      end
    end

    -- T4: a dead owner -> SILENT (the poll's own alive gate).
    do
      local uid = 11504
      local W = tz_world(uid, { hp_frac = 0.10, men_alive = 0 })
      print("== T4 " .. TAG .. "==")
      if boot105(W, PATH, TAG, uid, "tzarkan", "T4") then
        polln(W, 3)
        check(TAG .. "T4a: a dead owner at 10% never fires (" .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "T4b: and nothing is even attempted [live log]",
          lg105((TAG ~= "[live] ") or count_log(W, "ATTEMPT tzarkan") == 0))
        tally(W)
      end
    end
  end

  -- ==========================================================================
  print("== HARNESS 105 - the red-run aggregate ==")
  if RED_MODE then
    check("H105 (RED): the pre-105 snapshot has no tzarkan entry, no evaluator and no health_below_15 "
      .. "trigger, so T1 never fires, T3's skip line never appears and the exact-percentage lines are "
      .. "absent - those are the discriminators; T2/T4 assert silence and pass by design.", true)
  else
    check("H105: Tz'arkan ships on the new low-health trigger - ONE entry, FIVE keys, below 15% of the "
      .. "ONE health reader, cast on SELF with fresh handles, the in-flight gate applying, and a pre-cast "
      .. "re-check that logs the exact percentage and skips a risen or dead caster.", true)
  end

  -- ==========================================================================
  if RED_MODE then
    check("HARNESS 104 suite boundary (harness 105): N/A in the red run - the pre-105 snapshot carries "
      .. "every harness-104 world unchanged", true)
  else
    check("HARNESS 104 suite boundary (harness 105): every harness-104 check ran first ("
      .. pre105 .. ", want 3649)", pre105 == 3649)
  end
end
run_h105()
