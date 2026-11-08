-- ============================================================================
-- HARNESS 87 - GLORIOUS DEATH's TRIGGER RANGE TIGHTENED 55 m -> 25 m.
--   USER INSTRUCTION (verbatim): "I tested Glorious Death again and it casted
--   too soon. Make it 25 m to make sure it is in range."
--   Harness 86 introduced the range gate as the wiki-sourced constant
--   GLORIOUS_DEATH_RANGE_M = 55 (the ability's "Effect range: 55m" line).
--   FIELD TESTING showed 55 m fired too early, so the gate is tightened to a
--   DELIBERATELY CONSERVATIVE 25 m - TIGHTER than the ability's 55 m wiki
--   aura on purpose. The wiki's real effect range stays in the constant's
--   comment for reference. ONLY the constant (and the comments that used to
--   describe the old 55 m gate) changed: the gate, the CLOSEST-ally choice,
--   the pre-cast re-check and the fail-open on an unreadable gap are the
--   harness-86 machinery, untouched.
--   RE-BASELINED WORLDS (the old distances re-based for the 25 m threshold):
--     R1 ally WITHIN range -> fires    (now 20 m; was 30 m)
--     R2 ally BEYOND range -> silent   (now 55 m, the old wiki aura; was 200 m)
--     R3 nearer of two chosen          (now 8 m / 22 m, the farther defined
--                                        first and ALSO in range; was 10 m/50 m)
--     R4 self-cast ungated             (unchanged: casting on self is in range)
--     R5 drift out of range -> SKIP    (now 20 m -> 55 m; was 30 m -> 200 m)
--     R6 BOUNDARY just UNDER -> fires  (NEW: 24 m, one metre inside the gate)
--     R7 BOUNDARY just OVER  -> silent (NEW: 26 m, one metre outside the gate)
--   RED CONTROL: with H87_LIVE / H87_ANN pointing at the pre-edit snapshot
--   (the shipped harness-86 build, constant still 55), only the section-0i
--   tokens that pin the NEW value/comment fail, and only the worlds whose
--   verdict differs at 55 m fail: R2 (55 m fires on the snapshot), R5 (its
--   55 m cast leg is still in range on the snapshot, so no skip), R7 (26 m
--   fires on the snapshot). R1/R3/R4/R6 and every other harness-86-era check
--   pass by design.
-- ============================================================================

if not RED_MODE then
  check("the WHOLE harness-85 suite (2105 checks before the final find check) still re-ran unchanged (checks so far = " .. checks .. ")",
    checks == 2105)
else
  print("   (red mode: the harness-85 suite boundary check is green-only - the red build skips some" ..
    " RED_MODE-gated checks, so its running count is lowered by design)")
end

local function run_h87()
  local SL_DAEMON = "wh3_dlc25_dwf_cha_daemon_slayer"
  local SL_UNIT   = "wh_main_dwf_inf_slayers"
  local SL_DOOMR  = "wh3_dlc25_dwf_inf_doomseekers"
  local NON_SLAYER = "wh_main_emp_inf_swordsmen"
  local GLAD = "wh3_dlc25_lord_abilities_glorious_death"

  local live_src87 = read_file(LIVE)
  local ann_src87  = read_file(ANN)
  local RED87 = { fires = 0, claims = 0, ui = 0 }
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
  local function note87(W, TAG)
    RED87.ui = RED87.ui + (W.ui_failures or 0)
    if TAG == "[live] " then
      RED87.fires = RED87.fires + #W.fires
      RED87.claims = RED87.claims + count_log(W, "claim: ")
    end
  end

  -- --------------------------------------------------------- 0i: the gate tokens (both files)
  print("== HARNESS 87 - section 0i: the GLORIOUS DEATH TRIGGER RANGE (25 m) in BOTH files ==")
  for _, f in ipairs({ { name = "live", src = live_src87 }, { name = "ann", src = ann_src87 } }) do
    local nm, s = f.name, f.src
    check("0i " .. nm .. ": the range constant is the tightened 25 (local GLORIOUS_DEATH_RANGE_M = 25)",
      raw_find(s, "local GLORIOUS_DEATH_RANGE_M = 25", 1, true) ~= nil)
    check("0i " .. nm .. ": the constant is no longer 55 (the field-tested-too-early value is gone)",
      raw_find(s, "local GLORIOUS_DEATH_RANGE_M = 55", 1, true) == nil)
    check("0i " .. nm .. ": the constant is commented as a DELIBERATELY CONSERVATIVE trigger",
      raw_find(s, "DELIBERATELY CONSERVATIVE", 1, true) ~= nil)
    check("0i " .. nm .. ": the comment notes it is TIGHTER than the ability's 55 m wiki aura (the wiki range kept for reference)",
      raw_find(s, "55 m wiki aura", 1, true) ~= nil
      and raw_find(s, "Effect range: 55m", 1, true) ~= nil)
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
    check("0i " .. nm .. ": the gate uses the ONE named range constant (no bare number in the comparison)",
      raw_find(s, "gap <= GLORIOUS_DEATH_RANGE_M", 1, true) ~= nil)
    check("0i " .. nm .. ": the cast TARGET stays the OWNER (unchanged self-cast, FOURTH.cast_target = unit x2)",
      cp(s, "FOURTH.cast_target = unit") == 2)
  end
  check("0i live: the pre-cast drift skip exists ('glorious_death SKIPPED:')",
    raw_find(live_src87, "glorious_death SKIPPED:", 1, true) ~= nil)
  check("0i live: the chosen-ally log line exists ('glorious_death ally: ui')",
    raw_find(live_src87, "glorious_death ally: ui", 1, true) ~= nil)
  check("0i live: the self-cast reasons are unchanged",
    raw_find(live_src87, 'reason = "slayer in melee (self-cast)"', 1, true) ~= nil
    and raw_find(live_src87, 'reason = "self in melee (self-cast)"', 1, true) ~= nil)
  check("0i ann: the reading copy stays log-free and find-free",
    raw_find(ann_src87, "log(", 1, true) == nil and raw_find(ann_src87, "string.find", 1, true) == nil)

  -- ==========================================================================
  -- R1 (i). The in-melee Slayer ally is WITHIN the tightened 25 m -> fires.
  --     The owner is NOT in melee, so ONLY the ally arm can fire it.
  -- ==========================================================================
  local function world_r1(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = SL_DAEMON, uid = 9901, owns = { GLAD }, melee = false, wavering = false },
      { name = SL_UNIT,   uid = 9902, owns = {}, melee = true, dist = 20 },
    }, cards = {
      { id = "9901", state = "active", vis = true }, { id = "9902", state = "active", vis = true },
    }, bar = { { id = "b1", key = GLAD } } })
    print("== " .. TAG .. "R1. GLORIOUS DEATH: an in-melee Slayer ally WITHIN 25m (20m) arms it (owner NOT in melee) == ")
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
    check(TAG .. "R1a: the owner fired glorious_death exactly once - the ally at 20m is WITHIN 25m ("
      .. fire_detail(W) .. ")", a)
    local tgt = fire_target_for(W, 9901)
    local b = (tgt ~= nil and tgt == caster and tgt ~= ally)
    check(TAG .. "R1b: the cast target is STILL the OWNER itself (caster " .. tostring(tgt == caster)
      .. ", ally " .. tostring(tgt == ally) .. ")", b)
    local c = (count_log(W, "reason: slayer in melee (self-cast)") == 1)
    check(TAG .. "R1c: the reason is the Slayer self-cast reason [live log]", lg(TAG, c))
    note87(W, TAG)
    tally(W)
    return a and b and lg(TAG, c)
  end

  -- ==========================================================================
  -- R2 (ii). The in-melee Slayer ally is BEYOND the tightened 25 m -> SILENT.
  --     55 m is used on purpose: it is the ability's OLD wiki aura, so this
  --     world proves the field-test complaint (55 m fired too early) is gone.
  -- ==========================================================================
  local function world_r2(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = SL_DAEMON, uid = 9911, owns = { GLAD }, melee = false, wavering = false },
      { name = SL_UNIT,   uid = 9912, owns = {}, melee = true, dist = 55 },
    }, cards = {
      { id = "9911", state = "active", vis = true }, { id = "9912", state = "active", vis = true },
    }, bar = { { id = "b1", key = GLAD } } })
    print("== " .. TAG .. "R2. GLORIOUS DEATH: an in-melee Slayer ally BEYOND 25m (55m) -> NOTHING fires == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "R2: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9911, true); ui(W); ui(W)
    click(W, badd("glorious_death")); ui(W)
    W.conflict = true
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "R2a: the 55m ally is OUT of the 25m trigger range -> NO cast at all ("
      .. fire_detail(W) .. ") - this is the field-test complaint", a)
    local b = (count_log(W, "reason: slayer in melee (self-cast)") == 0)
    check(TAG .. "R2b: no Slayer self-cast attempt is even made [live log]", lg(TAG, b))
    local c = (count_log(W, "glorious_death ally: ui") == 0)
    check(TAG .. "R2c: no ally is chosen (no chosen-ally line) [live log]", lg(TAG, c))
    note87(W, TAG)
    tally(W)
    return a and lg(TAG, b) and lg(TAG, c)
  end

  -- ==========================================================================
  -- R3 (iii). TWO in-melee Slayers, one NEARER (and one farther) -> the
  --     NEARER is chosen. BOTH are within 25 m so the closest-of-two choice is
  --     still exercised. The FARTHER is defined FIRST, so a naive first-match
  --     scan would pick it; the chosen-ally line must name the nearer one.
  -- ==========================================================================
  local function world_r3(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = SL_DAEMON, uid = 9921, owns = { GLAD }, melee = false, wavering = false },
      { name = SL_UNIT,   uid = 9922, owns = {}, melee = true, dist = 22 },   -- farther, defined FIRST
      { name = SL_DOOMR,  uid = 9923, owns = {}, melee = true, dist = 8 },    -- nearer
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
    check(TAG .. "R3b: the NEARER in-melee Slayer (ui 9923 at 8.0m) is the one CHOSEN [live log]", lg(TAG, b))
    local c = (count_log(W, "glorious_death ally: ui 9922") == 0)
    check(TAG .. "R3c: the FARTHER ally (ui 9922 at 22.0m) is NEVER the chosen one [live log]", lg(TAG, c))
    note87(W, TAG)
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
    note87(W, TAG)
    tally(W)
    return a and lg(TAG, b) and lg(TAG, c)
  end

  -- ==========================================================================
  -- R5 (v). DRIFT: the ally is in range at DECIDE (20m) but out of range at
  --     CAST (55m) -> the cast is SKIPPED rather than wasted.
  -- ==========================================================================
  local function world_r5(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = SL_DAEMON, uid = 9941, owns = { GLAD }, melee = false, wavering = false },
      { name = SL_UNIT,   uid = 9942, owns = {}, melee = true, dist_seq = { 20, 55 } },
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
    local c = (count_log(W, "glorious_death ally: ui 9942 at 20.0m") == 1)
    check(TAG .. "R5c: the decision DID see the ally at 20.0m before the re-check [live log]", lg(TAG, c))
    note87(W, TAG)
    tally(W)
    return a and lg(TAG, b) and lg(TAG, c)
  end

  -- ==========================================================================
  -- R6 (vi). BOUNDARY, just UNDER the gate: 24 m (one metre inside 25) -> the
  --     ally IS in range and the ability FIRES. Pairs with R7 to pin the
  --     threshold exactly at GLORIOUS_DEATH_RANGE_M.
  -- ==========================================================================
  local function world_r6(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = SL_DAEMON, uid = 9951, owns = { GLAD }, melee = false, wavering = false },
      { name = SL_UNIT,   uid = 9952, owns = {}, melee = true, dist = 24 },
    }, cards = {
      { id = "9951", state = "active", vis = true }, { id = "9952", state = "active", vis = true },
    }, bar = { { id = "b1", key = GLAD } } })
    print("== " .. TAG .. "R6. GLORIOUS DEATH BOUNDARY: 24m (just UNDER 25) is IN range -> FIRES == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "R6: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9951, true); ui(W); ui(W)
    click(W, badd("glorious_death")); ui(W)
    W.conflict = true
    polln(W, 1)
    local a = (#W.fires == 1 and W.fires[1].uid == 9951 and W.fires[1].key == GLAD)
    check(TAG .. "R6a: the ally at 24m is 1m INSIDE the 25m gate, so the owner FIRES ("
      .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "glorious_death ally: ui 9952 at 24.0m") == 1)
    check(TAG .. "R6b: the chosen-ally line names 24.0m as CLOSEST/within [live log]", lg(TAG, b))
    local c = (count_log(W, "reason: slayer in melee (self-cast)") == 1)
    check(TAG .. "R6c: the Slayer self-cast reason fires [live log]", lg(TAG, c))
    note87(W, TAG)
    tally(W)
    return a and lg(TAG, b) and lg(TAG, c)
  end

  -- ==========================================================================
  -- R7 (vii). BOUNDARY, just OVER the gate: 26 m (one metre outside 25) -> the
  --     ally is OUT of range and the ability stays SILENT. Pairs with R6.
  -- ==========================================================================
  local function world_r7(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = SL_DAEMON, uid = 9961, owns = { GLAD }, melee = false, wavering = false },
      { name = SL_UNIT,   uid = 9962, owns = {}, melee = true, dist = 26 },
    }, cards = {
      { id = "9961", state = "active", vis = true }, { id = "9962", state = "active", vis = true },
    }, bar = { { id = "b1", key = GLAD } } })
    print("== " .. TAG .. "R7. GLORIOUS DEATH BOUNDARY: 26m (just OVER 25) is OUT of range -> SILENT == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "R7: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 9961, true); ui(W); ui(W)
    click(W, badd("glorious_death")); ui(W)
    W.conflict = true
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "R7a: the ally at 26m is 1m OUTSIDE the 25m gate, so the owner stays SILENT ("
      .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "glorious_death ally: ui") == 0)
    check(TAG .. "R7b: no ally is chosen (no chosen-ally line) [live log]", lg(TAG, b))
    local c = (count_log(W, "reason: slayer in melee (self-cast)") == 0)
    check(TAG .. "R7c: no Slayer self-cast attempt is made [live log]", lg(TAG, c))
    note87(W, TAG)
    tally(W)
    return a and lg(TAG, b) and lg(TAG, c)
  end

  print()
  print("== HARNESS 87 - GLORIOUS DEATH's TRIGGER RANGE = 25 m (conservative) ==")
  local r1a = world_r1(ANN, "[annotated] "); local r1b = world_r1(LIVE, "[live] ")
  local r2a = world_r2(ANN, "[annotated] "); local r2b = world_r2(LIVE, "[live] ")
  local r3a = world_r3(ANN, "[annotated] "); local r3b = world_r3(LIVE, "[live] ")
  local r4a = world_r4(ANN, "[annotated] "); local r4b = world_r4(LIVE, "[live] ")
  local r5a = world_r5(ANN, "[annotated] "); local r5b = world_r5(LIVE, "[live] ")
  local r6a = world_r6(ANN, "[annotated] "); local r6b = world_r6(LIVE, "[live] ")
  local r7a = world_r7(ANN, "[annotated] "); local r7b = world_r7(LIVE, "[live] ")

  local results = { r1a, r1b, r2a, r2b, r3a, r3b, r4a, r4b, r5a, r5b, r6a, r6b, r7a, r7b }
  local n_ok = 0
  for _, r in ipairs(results) do if posv(r) then n_ok = n_ok + 1 end end

  check("every ui tick ran clean across the HARNESS-87 worlds (" .. RED87.ui .. " failures)", RED87.ui == 0)

  if not RED_MODE then
    check("the HARNESS-87 worlds all behaved (live+annotated: R1/R2/R3/R4/R5/R6/R7) - " .. n_ok .. "/14", n_ok == 14)
    check("HEADLINE (harness 87): GLORIOUS DEATH's trigger range is tightened from the ability's 55 m wiki aura to a "
      .. "DELIBERATELY CONSERVATIVE 25 m (GLORIOUS_DEATH_RANGE_M), after field testing showed 55 m fired too early. "
      .. "The ally arm fires only when the in-melee Slayer ally is WITHIN 25 m (R1 20 m fires; R2 55 m is silent; the "
      .. "24 m/26 m BOUNDARY pair pins the threshold: 24 m fires, 26 m silent). The CLOSEST in-range Slayer is chosen "
      .. "(R3), the gap is RE-CHECKED immediately before the cast (R5 drift -> skip), and the owner-in-melee self arm "
      .. "is NEVER gated (R4). The gate logic is the harness-86 machinery, untouched.", n_ok == 14)
  else
    check("RED CONTROL (harness 87): on the pre-edit snapshot (the shipped harness-86 build, constant still 55) ONLY "
      .. "the section-0i tokens pinning the NEW value/comment fail (the 25 value, the 'no longer 55' and the "
      .. "conservative-trigger / 55 m wiki-aura comment) and ONLY the worlds whose verdict differs at 55 m fail: R2 "
      .. "(the 55 m ally FIRES on the snapshot - the field-test complaint), R5 (its 55 m cast leg is still in range on "
      .. "the snapshot, so no skip) and R7 (the 26 m ally fires on the snapshot). R1/R3/R4/R6 pass by design - "
      .. n_ok .. "/14 world results pass (want 8), fires " .. RED87.fires
      .. ", claims " .. RED87.claims, n_ok == 8)
  end
end
run_h87()
