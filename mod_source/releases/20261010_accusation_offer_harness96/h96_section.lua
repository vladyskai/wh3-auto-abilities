-- ============================================================================
-- HARNESS 96 - THE ACCUSATION MOVE-ORDER ROOT CAUSE (this round).
--   THE BUG (proven by the passive observer probe zz_probe_dist, tick 59):
--     CAND-FIRST ... dist=81.3m first_passing_test=engine
--         engine_unit_in_range=t our_52_test=f our_75_test=f
--   The Accusation OFFER test consulted the engine's own loose unit_in_range
--   reach read - TRUE at 81.3 m while BOTH of the mod's bounds said FALSE - so
--   the mod offered and cast at a target 81.3 m away and the engine WALKED the
--   caster in (the reported move order). The log label was static ("within
--   52m") and could not show the real distance.
--   THE FIX: the offer test is the 70% CONSTANT ONLY -
--     unit:unit_distance(enemy) <= FOURTH.ACCUSATION_RANGE_M  (52 m)
--   with the engine helper REMOVED from the offer path, and the log prints the
--   REAL edge-to-edge distance (unit:unit_distance, battle_unit.lua:160) at the
--   target choice AND the pre-cast re-check.
--   WORLDS (each live + annotated):
--     R1 (REGRESSION - the exact bug): in_range=TRUE, distance 81.3 m -> the
--        trigger must NOT fire. RED on the pre-edit snapshot (it fires there).
--     R2 inside the bound (48.7 m) -> FIRES.
--     R3 outside the bound (70 m) -> SILENT.
--     R4 the log carries the REAL distance ("distance=48.7m bound=52m") at
--        BOTH the target choice and the pre-cast re-check.
--     R5 the engine flag is FALSE but 40 m (inside) -> the CONSTANT rules, FIRES.
--   RED CONTROL: with H96_LIVE / H96_ANN pointing at the pre-edit snapshot (the
--   shipped harness-95 build, whose offer test trusts unit_in_range) R1 FIRES,
--   R5 stays silent and R4's log lacks the real distance, plus sheet-0t's tokens
--   fail; every earlier world still passes except harness-95's own boundary-count
--   pin (re-based here to the N/A form).
-- ============================================================================
function run_h96()
  local ACK = "wh_main_hero_abilities_accusation"
  local live_src96 = read_file(LIVE)
  local ann_src96  = read_file(ANN)
  local RED96 = { fires = 0, claims = 0, ui = 0 }
  local function posv(v) return (v == true) or (type(v) == "number") end
  local function lg(tag, v) return (tag ~= "[live] ") or posv(v) end
  local function badd96(marker) return "zz_auto_badge_" .. marker end
  local function cp96(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function note96(W, TAG)
    RED96.ui = RED96.ui + (W.ui_failures or 0)
    if TAG == "[live] " then
      RED96.fires = RED96.fires + #W.fires
      RED96.claims = RED96.claims + count_log(W, "claim: ")
    end
  end
  local function boot96(W, PATH, TAG, uid, marker, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, badd96(marker)); ui(W)
    W.conflict = true
    return true
  end
  local function enemy_of96(W, uid)
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        local ok, id = pcall(function() return pr.unit:unique_ui_id() end)
        if ok and tostring(id) == tostring(uid) then return pr.unit end
      end
    end
    return nil
  end

  -- --------------------------------------------------- 0t: tokens (both files)
  print("== HARNESS 96 - section 0t: the move-order fix tokens (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src96 }, { name = "ann", src = ann_src96 } }) do
    local nm, s = f.name, f.src
    check("0t " .. nm .. ": the offer test uses the constant-only helper (eg_enemy_within_bound)",
      raw_find(s, "function FOURTH.eg_enemy_within_bound(unit, enemy)", 1, true) ~= nil)
    check("0t " .. nm .. ": the offer gate is wired to the constant-only helper",
      raw_find(s, "and FOURTH.eg_enemy_within_bound(unit, enemy) then", 1, true) ~= nil)
    check("0t " .. nm .. ": the engine's unit_in_range CALL is GONE from the file",
      raw_find(s, "unit_in_range(", 1, true) == nil)
    check("0t " .. nm .. ": the old engine-helper function is GONE",
      raw_find(s, "function FOURTH.eg_enemy_in_range(unit, enemy)", 1, true) == nil)
    check("0t " .. nm .. ": the test compares the gap to FOURTH.ACCUSATION_RANGE_M (the 52 m 70% value)",
      raw_find(s, "return gap <= FOURTH.ACCUSATION_RANGE_M", 1, true) ~= nil
      and raw_find(s, "FOURTH.ACCUSATION_RANGE_M = 52", 1, true) ~= nil)
    check("0t " .. nm .. ": the distance primitive is documented (unit:unit_distance + battle_unit.lua:160)",
      raw_find(s, "unit:unit_distance(enemy)", 1, true) ~= nil
      and raw_find(s, "battle_unit.lua:160", 1, true) ~= nil)
    check("0t " .. nm .. ": the whole 579-entry table and the 70% rule are untouched",
      cp96(s, "\t{ marker = ") == 579
      and raw_find(s, "FOURTH.RANGE_FRACTION = 0.70", 1, true) ~= nil)
  end
  check("0t live: the target-choice log prints the REAL distance and the bound",
    raw_find(live_src96, '") distance="', 1, true) ~= nil
    and raw_find(live_src96, '.. "m bound=" .. tostring(FOURTH.ACCUSATION_RANGE_M) .. "m")', 1, true) ~= nil)
  check("0t live: the pre-cast re-check log prints the REAL distance too",
    raw_find(live_src96, '", distance="', 1, true) ~= nil
    and raw_find(live_src96, '.. "m) - firing")', 1, true) ~= nil
    and raw_find(live_src96, '.. " bound=" .. tostring(FOURTH.ACCUSATION_RANGE_M) .. "m) - cast not spent")', 1, true) ~= nil)
  check("0t live: the misleading static 'within 52m' label is GONE",
    raw_find(live_src96, '") within "', 1, true) == nil)
  check("0t ann: the reading copy stays log-free and find-free",
    raw_find(ann_src96, "log(", 1, true) == nil and raw_find(ann_src96, "string.find", 1, true) == nil)

  -- ==========================================================================
  -- R1. THE REGRESSION - the exact probe case: the engine says in-range but the
  --     real distance (81.3 m) EXCEEDS the bound -> the trigger must NOT fire.
  -- ==========================================================================
  local function world_r1(PATH, TAG)
    local W = make_world({ can_perform = true,
      units = { { name = "witch_hunter", uid = 9891, owns = { ACK }, melee = false,
                  in_range = true, dist = 81.3 } },
      enemies = { { name = "orc_boyz", uid = 9892, melee = true } },
      cards = { { id = "9891", state = "active", vis = true } },
      bar = { { id = "b1", key = ACK } } })
    print("== " .. TAG .. "R1. REGRESSION: unit_in_range=TRUE but the distance 81.3 m EXCEEDS the 52 m bound -> MUST stay SILENT ==")
    if not boot96(W, PATH, TAG, 9891, "accusation", "R1") then return nil end
    polln(W, 3)
    local a = (#W.fires == 0)
    check(TAG .. "R1a: the 81.3 m target is NOT offered even though the engine said in-range (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "accusation target:") == 0)
    check(TAG .. "R1b: no target is chosen, so no cast and no walk order [live log]", lg(TAG, b))
    note96(W, TAG); tally(W)
    return a and lg(TAG, b)
  end

  -- ==========================================================================
  -- R2. INSIDE the bound: an in-melee enemy at 48.7 m -> FIRES at that enemy.
  -- ==========================================================================
  local function world_r2(PATH, TAG)
    local W = make_world({ can_perform = true,
      units = { { name = "witch_hunter", uid = 9901, owns = { ACK }, melee = false, dist = 48.7 } },
      enemies = { { name = "orc_boyz", uid = 9902, melee = true } },
      cards = { { id = "9901", state = "active", vis = true } },
      bar = { { id = "b1", key = ACK } } })
    print("== " .. TAG .. "R2. INSIDE: an in-melee enemy at 48.7 m (inside the 52 m bound) -> FIRES ==")
    if not boot96(W, PATH, TAG, 9901, "accusation", "R2") then return nil end
    polln(W, 1)
    local enemy = enemy_of96(W, 9902)
    local a = (#W.fires == 1 and W.fires[1].key == ACK and fire_target_for(W, 9901) == enemy)
    check(TAG .. "R2a: the 48.7 m enemy is chosen and fired at (" .. fire_detail(W) .. ")", a)
    note96(W, TAG); tally(W)
    return a
  end

  -- ==========================================================================
  -- R3. OUTSIDE the bound: an in-melee enemy at 70 m -> SILENT.
  -- ==========================================================================
  local function world_r3(PATH, TAG)
    local W = make_world({ can_perform = true,
      units = { { name = "witch_hunter", uid = 9911, owns = { ACK }, melee = false, dist = 70 } },
      enemies = { { name = "orc_boyz", uid = 9912, melee = true } },
      cards = { { id = "9911", state = "active", vis = true } },
      bar = { { id = "b1", key = ACK } } })
    print("== " .. TAG .. "R3. OUTSIDE: an in-melee enemy at 70 m (outside the 52 m bound) -> SILENT ==")
    if not boot96(W, PATH, TAG, 9911, "accusation", "R3") then return nil end
    polln(W, 3)
    local a = (#W.fires == 0)
    check(TAG .. "R3a: the 70 m enemy is NOT offered (" .. fire_detail(W) .. ")", a)
    note96(W, TAG); tally(W)
    return a
  end

  -- ==========================================================================
  -- R4. THE LOG CARRIES THE REAL DISTANCE at the choice AND the re-check.
  -- ==========================================================================
  local function world_r4(PATH, TAG)
    local W = make_world({ can_perform = true,
      units = { { name = "witch_hunter", uid = 9921, owns = { ACK }, melee = false, dist = 48.7 } },
      enemies = { { name = "orc_boyz", uid = 9922, melee = true } },
      cards = { { id = "9921", state = "active", vis = true } },
      bar = { { id = "b1", key = ACK } } })
    print("== " .. TAG .. "R4. LOG: the real distance (48.7 m) and the bound (52 m) are printed ==")
    if not boot96(W, PATH, TAG, 9921, "accusation", "R4") then return nil end
    polln(W, 1)
    local a = (#W.fires == 1)
    check(TAG .. "R4a: the ability fired (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "is the chosen enemy (melee) distance=48.7m bound=52m") == 1)
    check(TAG .. "R4b: the target-choice line names the REAL 48.7 m and the 52 m bound [live log]", lg(TAG, b))
    local c = (count_log(W, "distance=48.7m bound=52m) - firing") == 1)
    check(TAG .. "R4c: the pre-cast re-check line names the REAL 48.7 m too [live log]", lg(TAG, c))
    note96(W, TAG); tally(W)
    return a and lg(TAG, b) and lg(TAG, c)
  end

  -- ==========================================================================
  -- R5. THE ENGINE FLAG IS FALSE but the real distance is INSIDE the bound ->
  --     the CONSTANT rules, so it FIRES (the engine helper is not consulted).
  -- ==========================================================================
  local function world_r5(PATH, TAG)
    local W = make_world({ can_perform = true,
      units = { { name = "witch_hunter", uid = 9931, owns = { ACK }, melee = false,
                  in_range = false, dist = 40 } },
      enemies = { { name = "orc_boyz", uid = 9932, melee = true } },
      cards = { { id = "9931", state = "active", vis = true } },
      bar = { { id = "b1", key = ACK } } })
    print("== " .. TAG .. "R5. ENGINE-FALSE: the flag says out-of-range but 40 m is INSIDE -> the CONSTANT rules, FIRES ==")
    if not boot96(W, PATH, TAG, 9931, "accusation", "R5") then return nil end
    polln(W, 1)
    local a = (#W.fires == 1)
    check(TAG .. "R5a: the 40 m enemy fires on OUR bound, not the engine's flag (" .. fire_detail(W) .. ")", a)
    note96(W, TAG); tally(W)
    return a
  end

  local WORLDS = { world_r1, world_r2, world_r3, world_r4, world_r5 }
  local results = {}
  for _, path in ipairs({ LIVE, ANN }) do
    local TAG = (path == LIVE) and "[live] " or "[ann]  "
    for _, wfn in ipairs(WORLDS) do
      results[#results + 1] = wfn(path, TAG)
    end
  end
  local n_ok = 0
  for _, r in ipairs(results) do if posv(r) then n_ok = n_ok + 1 end end
  print("== HARNESS 96 - move-order worlds: " .. n_ok .. "/" .. #results .. " passed; fires " .. RED96.fires .. " ==")

  check("every ui tick ran clean across the HARNESS-96 worlds (" .. RED96.ui .. " failures)", RED96.ui == 0)

  if not RED_MODE then
    check("HEADLINE (harness 96): the Accusation move-order ROOT CAUSE is fixed - the offer test is the 70% "
      .. "CONSTANT ONLY (unit:unit_distance(enemy) <= FOURTH.ACCUSATION_RANGE_M = 52 m) and NEVER the engine's "
      .. "looser unit_in_range reach read. The probe's tick-59 case (dist=81.3 m, engine in_range=TRUE) is the "
      .. "regression world: it must NOT offer, so the caster can never be walked in. The log now prints the REAL "
      .. "edge-to-edge distance (unit:unit_distance, battle_unit.lua:160) at the target choice AND the pre-cast "
      .. "re-check ('distance=48.7m bound=52m'). All " .. #results .. " worlds passed.", n_ok == #results)
  else
    check("RED CONTROL (harness 96): on the pre-edit snapshot (the shipped harness-95 build, whose offer test "
      .. "trusts the engine's unit_in_range) the regression world R1 FIRES (81.3 m, engine in-range) and R5 stays "
      .. "silent (engine flag false), and R4's live log lacks the real distance - and the section-0t tokens fail. "
      .. "R2/R3 pass by design (the snapshot's distance fallback agrees), plus R4's annotated leg. " .. n_ok .. "/"
      .. #results .. " world results pass (want 5), fires " .. RED96.fires .. ", claims " .. RED96.claims, n_ok == 5)
  end
end
run_h96()
