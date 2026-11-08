-- ============================================================================
-- HARNESS 89 (this round): THE ENCHANTED METALLURGY FAMILY - ONE new trigger.
--   The user's new trigger for all four keys: "when self or ally in range is in
--   melee; when ally in range is shooting". The MELEE half ships; the SHOOTING
--   half COULD NOT be built (the battle API exposes no per-unit is-firing read
--   - see the mod's round note), so no proxy is used.
--   The table grows 189 -> 193 entries (195 -> 199 keys), all four on the new
--   trigger metallurgy_melee. The new section's 0m tokens + the M worlds are
--   appended before the final find check; the adapted count pins are the SAME
--   table-size pins the earlier sections read (now 193/199).
--   RED CONTROL: with H89_LIVE / H89_ANN pointing at the pre-edit snapshot (the
--   shipped harness-88 build, 189 entries), the grown-table pins and this
--   HARNESS-89 section fail; the SILENT worlds pass trivially (the ability is
--   simply absent on the snapshot).
-- ============================================================================
local function run_h89()
  local MT  = "wh3_main_character_abilities_enchanted_metallurgy"
  local MTF = "wh3_main_character_abilities_enchanted_metallurgy_flaming"
  local MTP = "wh3_main_character_abilities_enchanted_metallurgy_piercing"
  local MTX = "wh3_main_character_abilities_enchanted_metallurgy_poison"
  local ALL4 = {
    { "enchanted_metallurgy",          MT  },
    { "enchanted_metallurgy_flaming",  MTF },
    { "enchanted_metallurgy_piercing", MTP },
    { "enchanted_metallurgy_poison",   MTX } }

  local live_src89 = read_file(LIVE)
  local ann_src89  = read_file(ANN)
  local RED89 = { fires = 0, claims = 0, ui = 0 }
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
  local function note89(W, TAG)
    RED89.ui = RED89.ui + (W.ui_failures or 0)
    if TAG == "[live] " then
      RED89.fires = RED89.fires + #W.fires
      RED89.claims = RED89.claims + count_log(W, "claim: ")
    end
  end

  -- --------------------------------------------------- 0m: tokens (both files)
  print("== HARNESS 89 - section 0m: the ENCHANTED METALLURGY family (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src89 }, { name = "ann", src = ann_src89 } }) do
    local nm, s = f.name, f.src
    local n_mk = 0
    for _, e in ipairs(ALL4) do
      if raw_find(s, 'marker = "' .. e[1] .. '"', 1, true) ~= nil
        and raw_find(s, 'badge = "' .. badd(e[1]) .. '"', 1, true) ~= nil
        and raw_find(s, '"' .. e[2] .. '"', 1, true) ~= nil
        and raw_find(s, 'trigger = "metallurgy_melee"', 1, true) ~= nil then
        n_mk = n_mk + 1
      end
    end
    check("0m " .. nm .. ": all four Enchanted Metallurgy entries are present (marker+badge+key+trigger: "
      .. n_mk .. "/4)", n_mk == 4)
    check("0m " .. nm .. ": the metallurgy_melee trigger count is 4 (got "
      .. cp(s, 'trigger = "metallurgy_melee"') .. ")", cp(s, 'trigger = "metallurgy_melee"') == 4)
    check("0m " .. nm .. ": the range is a DELIBERATELY CONSERVATIVE 25 m (FOURTH.METALLURGY_RANGE_M = 25)",
      raw_find(s, "FOURTH.METALLURGY_RANGE_M = 25", 1, true) ~= nil)
    check("0m " .. nm .. ": the range constant's comment names the game-data 35 m aura (the source of the number)",
      raw_find(s, "effect_range =", 1, true) ~= nil and raw_find(s, "35 m", 1, true) ~= nil)
    check("0m " .. nm .. ": the metallurgy evaluator + the two gap helpers exist",
      raw_find(s, "function FOURTH.evaluate_metallurgy_melee(unit, routing)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.mtl_ally_gap(unit, ally)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.mtl_ally_in_range(unit, ally)", 1, true) ~= nil)
    check("0m " .. nm .. ": the chosen-ally field is only ever set by the ally arm (mtl_ally = nil x3)",
      cp(s, "FOURTH.mtl_ally = nil") == 3)
    check("0m " .. nm .. ": the gate uses the ONE named range constant",
      raw_find(s, "gap <= FOURTH.METALLURGY_RANGE_M", 1, true) ~= nil)
    check("0m " .. nm .. ": the cast target rides the DEFAULT (target or unit) - no cast_target write (still x2)",
      cp(s, "FOURTH.cast_target = unit") == 2)
    check("0m " .. nm .. ": the melee_unwavering / charge_or_melee counts are untouched (171 / 9)",
      cp(s, 'trigger = "melee_unwavering"') == 171 and cp(s, 'trigger = "charge_or_melee"') == 9)
    check("0m " .. nm .. ": NO shooting-arm predicate is invented (no is_firing / is_shooting token in the mod)",
      raw_find(s, "is_firing", 1, true) == nil and raw_find(s, "is_shooting", 1, true) == nil)
    check("0m " .. nm .. ": NO army-bar key is in the mod (the standing exclusion rule)",
      raw_find(s, "army_abilities", 1, true) == nil)
  end
  check("0m live: the metallurgy drift skip is reported ('enchanted_metallurgy SKIPPED:')",
    raw_find(live_src89, "enchanted_metallurgy SKIPPED:", 1, true) ~= nil)
  check("0m live: the chosen-ally line exists ('enchanted_metallurgy ally: ui')",
    raw_find(live_src89, "enchanted_metallurgy ally: ui", 1, true) ~= nil)
  check("0m live: the owner-in-melee self-cast reason exists",
    raw_find(live_src89, 'return "in melee (metallurgy self-cast)"', 1, true) ~= nil)
  check("0m live: the ally-in-melee self-cast reason exists",
    raw_find(live_src89, 'return "in-melee ally (metallurgy self-cast)"', 1, true) ~= nil)
  check("0m ann: the reading copy stays log-free and find-free",
    raw_find(ann_src89, "log(", 1, true) == nil and raw_find(ann_src89, "string.find(", 1, true) == nil)

  -- ==========================================================================
  -- M1. THE OWNER is in melee -> FIRES, cast ON SELF.
  -- ==========================================================================
  local function world_m1(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "alchemist", uid = 8901, owns = { MT }, melee = true, wavering = false },
    }, cards = { { id = "8901", state = "active", vis = true } },
       bar = { { id = "b1", key = MT } } })
    print("== " .. TAG .. "M1. METALLURGY: the OWNER is in melee -> FIRES (cast on self) == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "M1: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 8901, true); ui(W); ui(W)
    click(W, badd("enchanted_metallurgy")); ui(W)
    W.conflict = true
    polln(W, 1)
    local caster = unit_of(W, 8901)
    local a = (#W.fires == 1 and W.fires[1].uid == 8901 and W.fires[1].key == MT)
    check(TAG .. "M1a: the owner fired enchanted_metallurgy exactly once (" .. fire_detail(W) .. ")", a)
    local tgt = fire_target_for(W, 8901)
    local b = (tgt ~= nil and tgt == caster)
    check(TAG .. "M1b: the cast target is the OWNER itself (self-cast)", b)
    local c = (count_log(W, "reason: in melee (metallurgy self-cast)") == 1)
    check(TAG .. "M1c: the reason is the owner-in-melee self-cast reason [live log]", lg(TAG, c))
    note89(W, TAG)
    tally(W)
    return a and b and lg(TAG, c)
  end

  -- ==========================================================================
  -- M2. A friendly unit WITHIN range is in melee (owner NOT in melee) -> the
  --     owner FIRES, cast ON SELF; the closest ally is chosen.
  -- ==========================================================================
  local function world_m2(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "alchemist", uid = 8911, owns = { MT }, melee = false, wavering = false },
      { name = "infantry",  uid = 8912, owns = {},     melee = true,  wavering = false, dist = 20 },
    }, cards = { { id = "8911", state = "active", vis = true }, { id = "8912", state = "active", vis = true } },
       bar = { { id = "b1", key = MT } } })
    print("== " .. TAG .. "M2. METALLURGY: an in-melee ally WITHIN 25 m (20 m) arms it (owner NOT in melee) == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "M2: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 8911, true); ui(W); ui(W)
    click(W, badd("enchanted_metallurgy")); ui(W)
    W.conflict = true
    polln(W, 1)
    local caster = unit_of(W, 8911)
    local ally = unit_of(W, 8912)
    local a = (#W.fires == 1 and W.fires[1].uid == 8911 and W.fires[1].key == MT)
    check(TAG .. "M2a: the owner fired enchanted_metallurgy exactly once (" .. fire_detail(W) .. ")", a)
    local tgt = fire_target_for(W, 8911)
    local b = (tgt ~= nil and tgt == caster and tgt ~= ally)
    check(TAG .. "M2b: the cast target is the OWNER itself (caster " .. tostring(tgt == caster)
      .. ", ally " .. tostring(tgt == ally) .. ")", b)
    local c = (count_log(W, "reason: in-melee ally (metallurgy self-cast)") == 1)
    check(TAG .. "M2c: the reason is the ally-in-melee self-cast reason [live log]", lg(TAG, c))
    local d = (count_log(W, "enchanted_metallurgy ally: ui 8912 at 20.0m") == 1)
    check(TAG .. "M2d: the chosen-ally line names ui 8912 at 20.0m [live log]", lg(TAG, d))
    note89(W, TAG)
    tally(W)
    return a and b and lg(TAG, c) and lg(TAG, d)
  end

  -- ==========================================================================
  -- M3. The in-melee ally is BEYOND the conservative 25 m (55 m) -> SILENT.
  -- ==========================================================================
  local function world_m3(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "alchemist", uid = 8921, owns = { MT }, melee = false, wavering = false },
      { name = "infantry",  uid = 8922, owns = {},     melee = true,  wavering = false, dist = 55 },
    }, cards = { { id = "8921", state = "active", vis = true }, { id = "8922", state = "active", vis = true } },
       bar = { { id = "b1", key = MT } } })
    print("== " .. TAG .. "M3. METALLURGY: an in-melee ally BEYOND 25 m (55 m) -> NOTHING fires == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "M3: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 8921, true); ui(W); ui(W)
    click(W, badd("enchanted_metallurgy")); ui(W)
    W.conflict = true
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "M3a: the 55 m ally is OUT of the 25 m trigger range -> NO cast (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "enchanted_metallurgy ally: ui") == 0)
    check(TAG .. "M3b: no ally is chosen (no chosen-ally line) [live log]", lg(TAG, b))
    note89(W, TAG)
    tally(W)
    return a and lg(TAG, b)
  end

  -- ==========================================================================
  -- M4. NOBODY is in melee (owner not in melee, the ally not in melee) -> SILENT.
  -- ==========================================================================
  local function world_m4(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "alchemist", uid = 8931, owns = { MT }, melee = false, wavering = false },
      { name = "infantry",  uid = 8932, owns = {},     melee = false, wavering = false, dist = 20 },
    }, cards = { { id = "8931", state = "active", vis = true }, { id = "8932", state = "active", vis = true } },
       bar = { { id = "b1", key = MT } } })
    print("== " .. TAG .. "M4. METALLURGY: nobody is in melee -> NOTHING fires == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "M4: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 8931, true); ui(W); ui(W)
    click(W, badd("enchanted_metallurgy")); ui(W)
    W.conflict = true
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "M4a: with nobody in melee the ability stays SILENT (" .. fire_detail(W) .. ")", a)
    note89(W, TAG)
    tally(W)
    return a
  end

  -- ==========================================================================
  -- M5. DRIFT: the in-melee ally is in range at DECIDE (20 m) but out at CAST
  --     (55 m) -> the cast is SKIPPED rather than wasted.
  -- ==========================================================================
  local function world_m5(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "alchemist", uid = 8941, owns = { MT }, melee = false, wavering = false },
      { name = "infantry",  uid = 8942, owns = {},     melee = true,  wavering = false, dist_seq = { 20, 55 } },
    }, cards = { { id = "8941", state = "active", vis = true }, { id = "8942", state = "active", vis = true } },
       bar = { { id = "b1", key = MT } } })
    print("== " .. TAG .. "M5. METALLURGY: the in-melee ally DRIFTS out of range between decide and cast -> SKIP == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "M5: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, 8941, true); ui(W); ui(W)
    click(W, badd("enchanted_metallurgy")); ui(W)
    W.conflict = true
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "M5a: the ally was in range at decide but out at cast -> the cast is SKIPPED ("
      .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "enchanted_metallurgy SKIPPED") == 1)
    check(TAG .. "M5b: the drift skip is reported [live log]", lg(TAG, b))
    local c = (count_log(W, "enchanted_metallurgy ally: ui 8942 at 20.0m") == 1)
    check(TAG .. "M5c: the decision DID see the ally at 20.0m before the re-check [live log]", lg(TAG, c))
    note89(W, TAG)
    tally(W)
    return a and lg(TAG, b) and lg(TAG, c)
  end

  -- ==========================================================================
  -- M6. The four newly added entries ALL fire on in-melee alone; also asserts
  --     the grown table (193 entries / 199 keys).
  -- ==========================================================================
  local function world_m6(PATH, TAG)
    local units, cards, bar = {}, {}, {}
    for i, e in ipairs(ALL4) do
      units[i] = { name = "mtl" .. i, uid = 8950 + i, owns = { e[2] }, melee = true, wavering = false }
      cards[i] = { id = tostring(8950 + i), state = "active", vis = true }
      bar[i] = { id = "m" .. i, key = e[2] }
    end
    local W = make_world({ can_perform = true, units = units, cards = cards, bar = bar })
    print("== " .. TAG .. "M6. METALLURGY SAMPLE: all 4 new entries fire on in-melee alone == ")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. "M6: the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    local armed_n = 0
    for i, e in ipairs(ALL4) do
      sel_event(W, 8950 + i, true); ui(W); ui(W)
      click(W, badd(e[1])); ui(W)
      if badge_text(W, badd(e[1])) == "A" then armed_n = armed_n + 1 end
    end
    W.conflict = true
    polln(W, 1)
    local all_fired = (#W.fires == #ALL4)
    check(TAG .. "M6a: all " .. #ALL4 .. " metallurgy badges armed to A (" .. armed_n .. "/" .. #ALL4 .. ")",
      armed_n == #ALL4)
    check(TAG .. "M6b: ALL " .. #ALL4 .. " metallurgy entries FIRED on in-melee alone (" .. #W.fires .. " fires)",
      all_fired)
    local roots = { CUR_UI_FN, POLL_BODY_FN, W.ui_fn, W.poll_fn }
    for _, l in ipairs(W.listeners) do roots[#roots + 1] = l.cb end
    for _, c in ipairs(W.phase_cbs.Deployment or {}) do roots[#roots + 1] = c end
    for _, c in ipairs(W.phase_cbs.Deployed or {}) do roots[#roots + 1] = c end
    for _, r in ipairs(W.sel_registrations) do roots[#roots + 1] = r.cb end
    local ABIL = upvalue_from_roots(roots, "ABILITIES", "table")
    local MK   = upvalue_from_roots(roots, "marker_by_key", "table")
    local n_e = (ABIL ~= nil and #ABIL or -1)
    local n_k = -1
    if MK ~= nil then
      n_k = 0
      for _ in pairs(MK) do n_k = n_k + 1 end
    end
    check(TAG .. "M6c: the abilities table has 193 entries (" .. n_e .. ")", n_e == 193)
    check(TAG .. "M6d: the static key->marker map has 199 keys (" .. n_k .. ")", n_k == 199)
    note89(W, TAG)
    tally(W)
    return armed_n == #ALL4 and all_fired and (n_e == 193) and (n_k == 199)
  end

  print()
  print("== HARNESS 89 - the ENCHANTED METALLURGY family (one new trigger, four keys) ==")
  local m1a = world_m1(ANN, "[annotated] "); local m1b = world_m1(LIVE, "[live] ")
  local m2a = world_m2(ANN, "[annotated] "); local m2b = world_m2(LIVE, "[live] ")
  local m3a = world_m3(ANN, "[annotated] "); local m3b = world_m3(LIVE, "[live] ")
  local m4a = world_m4(ANN, "[annotated] "); local m4b = world_m4(LIVE, "[live] ")
  local m5a = world_m5(ANN, "[annotated] "); local m5b = world_m5(LIVE, "[live] ")
  local m6a = world_m6(ANN, "[annotated] "); local m6b = world_m6(LIVE, "[live] ")

  local results = { m1a, m1b, m2a, m2b, m3a, m3b, m4a, m4b, m5a, m5b, m6a, m6b }
  local n_ok = 0
  for _, r in ipairs(results) do if posv(r) then n_ok = n_ok + 1 end end

  check("every ui tick ran clean across the HARNESS-89 worlds (" .. RED89.ui .. " failures)", RED89.ui == 0)

  if not RED_MODE then
    check("the HARNESS-89 worlds all behaved (live+annotated: M1/M2/M3/M4/M5/M6) - " .. n_ok .. "/12",
      n_ok == 12)
    check("HEADLINE (harness 89): THE ENCHANTED METALLURGY FAMILY ships ONE new trigger "
      .. "(metallurgy_melee = FOURTH.evaluate_metallurgy_melee) across all FOUR keys: fire when the OWNER is "
      .. "in melee, OR any friendly unit other than the caster is in melee within the conservative 25 m "
      .. "FOURTH.METALLURGY_RANGE_M (the game data gives a 35 m ally aura - unit_spec_abil.tsv effect_range "
      .. "35.0000 for all four keys); CAST ON SELF, with the Glorious-Death / Verminking safety pattern "
      .. "(closest ally, pre-cast gap re-check, skip on drift). THE SHOOTING HALF of the user's trigger COULD "
      .. "NOT be built: the battle API exposes NO per-unit is-firing / is-shooting read and NO proxy was "
      .. "invented. The table grows 189 -> 193 entries (195 -> 199 keys); no new chunk locals.", n_ok == 12)
  else
    check("RED CONTROL (harness 89): on the pre-edit snapshot (the shipped harness-88 build, 189 entries) "
      .. "the grown-table pins and this HARNESS-89 section fail; the SILENT/SKIP worlds pass trivially because "
      .. "the ability is simply absent on the snapshot (M3 / M4 both files + the ANNOTATED drift world M5, whose "
      .. "log-based legs pass vacuously in the reading copy) - " .. n_ok
      .. "/12 world results pass (want 5), fires " .. RED89.fires
      .. ", claims " .. RED89.claims, n_ok == 5)
  end
end
run_h89()
