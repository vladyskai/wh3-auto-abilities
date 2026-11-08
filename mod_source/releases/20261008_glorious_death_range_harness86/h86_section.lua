-- ============================================================================
-- HARNESS 86 - THE GLORIOUS DEATH RANGE GATE (the reported bug fix).
--   USER REPORT: "it casted before the slayer unit that was fighting was in
--   range of the ability." Since the fix that always casts on SELF, the engine
--   no longer refuses (the caster is trivially in range of itself), so the
--   ability fired even when the in-melee Slayer ally was FAR away and the
--   55 m aura would not reach it - a wasted cast.
--   THE FIX: the ally arm only counts while the owner is WITHIN the ability's
--   effect range of the ally. The range is the wiki's effects line
--   "Effect range: 55m", implemented as the ONE named settings constant
--   GLORIOUS_DEATH_RANGE_M (section 1, wiki-sourced). The CLOSEST in-range
--   in-melee Slayer is the one chosen; the gap is RE-CHECKED immediately
--   before the cast (a unit can move a little between the poll and the cast)
--   and the cast is SKIPPED if the ally has drifted out of range. The
--   owner-in-melee self-cast case is NEVER gated.
--   The distance primitive is the mod's EXISTING one (battle_unit:unit_distance,
--   the charge detector's read); no new API call.
--   RED CONTROL: with H86_LIVE / H86_ANN pointing at the pre-edit snapshot
--   (the shipped harness-85 build), the range gate is ABSENT - the beyond-55m
--   world fires (the bug), the drift world fires, and the chosen-ally log line
--   does not exist. Every other harness-85-era check re-runs unchanged.
-- ============================================================================

if not RED_MODE then
  check("the WHOLE harness-85 suite (2105 checks before the final find check) still re-ran unchanged (checks so far = " .. checks .. ")",
    checks == 2105)
else
  print("   (red mode: the harness-85 suite boundary check is green-only - the red build skips some" ..
    " RED_MODE-gated checks, so its running count is lowered by design)")
end

local function run_h86()
  local SL_DAEMON = "wh3_dlc25_dwf_cha_daemon_slayer"
  local SL_UNIT   = "wh_main_dwf_inf_slayers"
  local SL_DOOMR  = "wh3_dlc25_dwf_inf_doomseekers"
  local NON_SLAYER = "wh_main_emp_inf_swordsmen"
  local GLAD = "wh3_dlc25_lord_abilities_glorious_death"

  local live_src86 = read_file(LIVE)
  local ann_src86  = read_file(ANN)
  local RED86 = { fires = 0, claims = 0, ui = 0 }
  local function posv(v) return (v == true) or (type(v) == "number") end
  local function lg(tag, v) return (tag ~= "[live] ") or posv(v) end
  local function badd(marker) return "zz_auto_badge_" .. marker end
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function note86(W, TAG)
    RED86.ui = RED86.ui + (W.ui_failures or 0)
    if TAG == "[live] " then
      RED86.fires = RED86.fires + #W.fires
      RED86.claims = RED86.claims + count_log(W, "claim: ")
    end
  end

  -- --------------------------------------------------------- 0i: the gate tokens (both files)
  print("== HARNESS 86 - section 0i: the GLORIOUS DEATH RANGE GATE in BOTH files ==")
  for _, f in ipairs({ { name = "live", src = live_src86 }, { name = "ann", src = ann_src86 } }) do
    local nm, s = f.name, f.src
    check("0i " .. nm .. ": the WIKI-SOURCED range constant exists (local GLORIOUS_DEATH_RANGE_M = 55)",
      raw_find(s, "local GLORIOUS_DEATH_RANGE_M = 55", 1, true) ~= nil)
    check("0i " .. nm .. ": the constant is commented as wiki-sourced (the 'Effect range: 55m' note)",
      raw_find(s, "Effect range: 55m", 1, true) ~= nil)
    check("0i " .. nm .. ": the EXISTING distance primitive is reused (FOURTH.gd_ally_gap -> battle_unit:unit_distance)",
      raw_find(s, "function FOURTH.gd_ally_gap(unit, ally)", 1, true) ~= nil
      and raw_find(s, "ally:unit_distance(unit)", 1, true) ~= nil)
    check("0i " .. nm .. ": the range test helper exists (FOURTH.gd_ally_in_range)",
      raw_find(s, "function FOURTH.gd_ally_in_range(unit, ally)", 1, true) ~= nil)
    check("0i " .. nm .. ": the CLOSEST in-range ally is kept for the pre-cast re-check",
      raw_find(s, "FOURTH.gd_ally = best_ally", 1, true) ~= nil
      and cp(s, "FOURTH.gd_ally = best_ally") == 1)
    check("0i " .. nm .. ": the chosen-ally field is only ever set by the ALLY arm, so the self arm stays UNGATED",
      cp(s, "FOURTH.gd_ally = nil") == 3 and cp(s, "FOURTH.gd_ally = best_ally") == 1)
    check("0i " .. nm .. ": the gate uses the ONE named range constant (no bare 55 in the comparison)",
      raw_find(s, "gap <= GLORIOUS_DEATH_RANGE_M", 1, true) ~= nil)
    check("0i " .. nm .. ": the cast TARGET stays the OWNER (unchanged self-cast, FOURTH.cast_target = unit x2)",
      cp(s, "FOURTH.cast_target = unit") == 2)
  end
  check("0i live: the pre-cast drift skip exists ('glorious_death SKIPPED:')",
    raw_find(live_src86, "glorious_death SKIPPED:", 1, true) ~= nil)
  check("0i live: the chosen-ally log line exists ('glorious_death ally: ui')",
    raw_find(live_src86, "glorious_death ally: ui", 1, true) ~= nil)
  check("0i live: the self-cast reasons are unchanged",
    raw_find(live_src86, 'reason = "slayer in melee (self-cast)"', 1, true) ~= nil
    and raw_find(live_src86, 'reason = "self in melee (self-cast)"', 1, true) ~= nil)
  check("0i ann: the reading copy stays log-free and find-free",
    raw_find(ann_src86, "log(", 1, true) == nil and raw_find(ann_src86, "string.find", 1, true) == nil)

  -- ==========================================================================
  -- R1 (i). The in-melee Slayer ally is WITHIN 55m -> the ability fires.
  --     The owner is NOT in melee, so ONLY the ally arm can fire it.
  -- ==========================================================================
  local function world_r1(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = SL_DAEMON, uid = 9901, owns = { GLAD }, melee = false, wavering = false },
      { name = SL_UNIT,   uid = 9902, owns = {}, melee = true, dist = 30 },
    }, cards = {
      { id = "9901", state = "active", vis = true }, { id = "9902", state = "active", vis = true },
    }, bar = { { id = "b1", key = GLAD } } })
    print("== " .. TAG .. "R1. GLORIOUS DEATH: an in-melee Slayer ally WITHIN 55m arms it (owner NOT in melee) == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "R1: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9901, true); ui(W); ui(W)
    click(W, badd("glorious_death")); ui(W)
    W.conflict = true
    polln(W, 1)
    local caster = unit_of(W, 9901)
    local ally = unit_of(W, 9902)
    local a = (#W.fires == 1 and W.fires[1].uid == 9901 and W.fires[1].key == GLAD)
    check(TAG .. "R1a: the owner fired glorious_death exactly once - the ally at 30m is WITHIN 55m ("
      .. fire_detail(W) .. ")", a)
    local tgt = fire_target_for(W, 9901)
    local b = (tgt ~= nil and tgt == caster and tgt ~= ally)
    check(TAG .. "R1b: the cast target is STILL the OWNER itself (caster " .. tostring(tgt == caster)
      .. ", ally " .. tostring(tgt == ally) .. ")", b)
    local c = (count_log(W, "reason: slayer in melee (self-cast)") == 1)
    check(TAG .. "R1c: the reason is the Slayer self-cast reason [live log]", lg(TAG, c))
    note86(W, TAG)
    tally(W)
    return a and b and lg(TAG, c)
  end

  -- ==========================================================================
  -- R2 (ii). The in-melee Slayer ally is BEYOND 55m -> SILENT (the reported
  --     bug: the ability used to fire anyway and waste the cast).
  -- ==========================================================================
  local function world_r2(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = SL_DAEMON, uid = 9911, owns = { GLAD }, melee = false, wavering = false },
      { name = SL_UNIT,   uid = 9912, owns = {}, melee = true, dist = 200 },
    }, cards = {
      { id = "9911", state = "active", vis = true }, { id = "9912", state = "active", vis = true },
    }, bar = { { id = "b1", key = GLAD } } })
    print("== " .. TAG .. "R2. GLORIOUS DEATH: an in-melee Slayer ally BEYOND 55m -> NOTHING fires == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "R2: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9911, true); ui(W); ui(W)
    click(W, badd("glorious_death")); ui(W)
    W.conflict = true
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "R2a: the 200m ally is OUT of the 55m aura -> NO cast at all ("
      .. fire_detail(W) .. ") - this is the reported bug", a)
    local b = (count_log(W, "reason: slayer in melee (self-cast)") == 0)
    check(TAG .. "R2b: no Slayer self-cast attempt is even made [live log]", lg(TAG, b))
    local c = (count_log(W, "glorious_death ally: ui") == 0)
    check(TAG .. "R2c: no ally is chosen (no chosen-ally line) [live log]", lg(TAG, c))
    note86(W, TAG)
    tally(W)
    return a and lg(TAG, b) and lg(TAG, c)
  end

  -- ==========================================================================
  -- R3 (iii). TWO in-melee Slayers, one NEARER (and one farther) -> the
  --     NEARER is chosen. The FARTHER is defined FIRST, so a naive first-match
  --     scan would pick it; the chosen-ally line must name the nearer one.
  -- ==========================================================================
  local function world_r3(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = SL_DAEMON, uid = 9921, owns = { GLAD }, melee = false, wavering = false },
      { name = SL_UNIT,   uid = 9922, owns = {}, melee = true, dist = 50 },   -- farther, defined FIRST
      { name = SL_DOOMR,  uid = 9923, owns = {}, melee = true, dist = 10 },   -- nearer
    }, cards = {
      { id = "9921", state = "active", vis = true }, { id = "9922", state = "active", vis = true },
      { id = "9923", state = "active", vis = true },
    }, bar = { { id = "b1", key = GLAD } } })
    print("== " .. TAG .. "R3. GLORIOUS DEATH: two in-melee Slayers, the NEARER one is chosen == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "R3: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9921, true); ui(W); ui(W)
    click(W, badd("glorious_death")); ui(W)
    W.conflict = true
    polln(W, 1)
    local a = (#W.fires == 1 and W.fires[1].uid == 9921 and W.fires[1].key == GLAD)
    check(TAG .. "R3a: an in-range in-melee Slayer arms it (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "glorious_death ally: ui 9923") == 1)
    check(TAG .. "R3b: the NEARER in-melee Slayer (ui 9923 at 10.0m) is the one CHOSEN [live log]", lg(TAG, b))
    local c = (count_log(W, "glorious_death ally: ui 9922") == 0)
    check(TAG .. "R3c: the FARTHER ally (ui 9922 at 50.0m) is NEVER the chosen one [live log]", lg(TAG, c))
    note86(W, TAG)
    tally(W)
    return a and lg(TAG, b) and lg(TAG, c)
  end

  -- ==========================================================================
  -- R4 (iv). The OWNER itself is in melee, no Slayer ally -> it self-casts,
  --     and the self arm is NEVER gated (casting on self is always in range).
  --     A NON-Slayer ally in melee is never considered.
  -- ==========================================================================
  local function world_r4(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = SL_DAEMON,  uid = 9931, owns = { GLAD }, melee = true, wavering = false },
      { name = NON_SLAYER, uid = 9932, owns = {}, melee = true, dist = 500 },
    }, cards = {
      { id = "9931", state = "active", vis = true }, { id = "9932", state = "active", vis = true },
    }, bar = { { id = "b1", key = GLAD } } })
    print("== " .. TAG .. "R4. GLORIOUS DEATH: owner in melee, no Slayer ally -> self-cast, UNGATED == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "R4: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9931, true); ui(W); ui(W)
    click(W, badd("glorious_death")); ui(W)
    W.conflict = true
    polln(W, 1)
    local caster = unit_of(W, 9931)
    local tgt = fire_target_for(W, 9931)
    local a = (#W.fires == 1 and W.fires[1].uid == 9931 and tgt == caster)
    check(TAG .. "R4a: the Slayer owner in melee SELF-casts - the self arm is never gated ("
      .. fire_detail(W) .. "; target is caster " .. tostring(tgt == caster) .. ")", a)
    local b = (count_log(W, "reason: self in melee (self-cast)") == 1)
    check(TAG .. "R4b: the reason is the self self-cast reason [live log]", lg(TAG, b))
    local c = (count_log(W, "glorious_death ally: ui") == 0)
    check(TAG .. "R4c: the in-melee NON-Slayer ally is never offered (no chosen-ally line) [live log]", lg(TAG, c))
    note86(W, TAG)
    tally(W)
    return a and lg(TAG, b) and lg(TAG, c)
  end

  -- ==========================================================================
  -- R5 (v). DRIFT: the ally is in range at DECIDE (30m) but out of range at
  --     CAST (200m) -> the cast is SKIPPED rather than wasted.
  -- ==========================================================================
  local function world_r5(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = SL_DAEMON, uid = 9941, owns = { GLAD }, melee = false, wavering = false },
      { name = SL_UNIT,   uid = 9942, owns = {}, melee = true, dist_seq = { 30, 200 } },
    }, cards = {
      { id = "9941", state = "active", vis = true }, { id = "9942", state = "active", vis = true },
    }, bar = { { id = "b1", key = GLAD } } })
    print("== " .. TAG .. "R5. GLORIOUS DEATH: the ally DRIFTS out of range between decide and cast -> SKIP == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "R5: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9941, true); ui(W); ui(W)
    click(W, badd("glorious_death")); ui(W)
    W.conflict = true
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "R5a: the ally was in range at decide but out at cast -> the cast is SKIPPED ("
      .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "glorious_death SKIPPED") == 1)
    check(TAG .. "R5b: the drift skip is reported [live log]", lg(TAG, b))
    local c = (count_log(W, "glorious_death ally: ui 9942 at 30.0m") == 1)
    check(TAG .. "R5c: the decision DID see the ally at 30.0m before the re-check [live log]", lg(TAG, c))
    note86(W, TAG)
    tally(W)
    return a and lg(TAG, b) and lg(TAG, c)
  end

  print()
  print("== HARNESS 86 - the GLORIOUS DEATH RANGE GATE ==")
  local r1a = world_r1(ANN, "[annotated] "); local r1b = world_r1(LIVE, "[live] ")
  local r2a = world_r2(ANN, "[annotated] "); local r2b = world_r2(LIVE, "[live] ")
  local r3a = world_r3(ANN, "[annotated] "); local r3b = world_r3(LIVE, "[live] ")
  local r4a = world_r4(ANN, "[annotated] "); local r4b = world_r4(LIVE, "[live] ")
  local r5a = world_r5(ANN, "[annotated] "); local r5b = world_r5(LIVE, "[live] ")

  local results = { r1a, r1b, r2a, r2b, r3a, r3b, r4a, r4b, r5a, r5b }
  local n_ok = 0
  for _, r in ipairs(results) do if posv(r) then n_ok = n_ok + 1 end end

  check("every ui tick ran clean across the HARNESS-86 worlds (" .. RED86.ui .. " failures)", RED86.ui == 0)

  if not RED_MODE then
    check("the HARNESS-86 worlds all behaved (live+annotated: R1/R2/R3/R4/R5) - " .. n_ok .. "/10", n_ok == 10)
    check("HEADLINE (harness 86): GLORIOUS DEATH now has a DISTANCE GATE - in the ally case it fires only when the " 
      .. "in-melee Slayer ally is WITHIN the ability's effect range (GLORIOUS_DEATH_RANGE_M = 55, wiki-sourced: the " 
      .. "ability's 'Effect range: 55m' line) of the owner; the CLOSEST in-range in-melee Slayer is chosen, and the gap " 
      .. "is RE-CHECKED immediately before the cast, skipping the cast if the ally has drifted out of range. The owner-" 
      .. "in-melee self-cast case is NEVER gated, and the cast target stays the OWNER itself. The distance primitive is " 
      .. "the mod's EXISTING battle_unit:unit_distance read. Every earlier check re-ran unchanged.", n_ok == 10)
  else
    check("RED CONTROL (harness 86): on the pre-edit snapshot the range gate is ABSENT - the beyond-55m world FIRES " 
      .. "(the reported bug, R2 fails), the drift world FIRES (R5 fails) and the chosen-ally / drift-skip log lines do " 
      .. "not exist (R3's live half fails); R1/R4 and R3's ANNOTATED half pass by design (the snapshot already self-" 
      .. "casts and does not log) - " .. n_ok .. "/10 world results pass (want 5), fires " .. RED86.fires
      .. ", claims " .. RED86.claims, n_ok == 5)
  end
end
run_h86()
