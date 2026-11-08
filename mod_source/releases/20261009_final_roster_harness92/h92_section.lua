
-- ============================================================================
-- HARNESS 92 (this round): THE FINAL ROSTER BUILD - the SIX built individual
--   abilities from the remaining-abilities triage (WH3_remaining_triage.md
--   section 3 INDIVIDUAL table). TWO NEW ally-heal triggers, each its OWN
--   evaluator, plus FOUR entries riding the EXISTING shared melee_unwavering
--   evaluator (in-melee self):
--     blood_sacrifice  1 entry / 1 key  - cast on the LOWEST-health ally in
--                                        range at or below 75%;
--     eat_da_runts     1 entry / 1 key  - cast on self at or below 75%, ELSE
--                                        on the lowest-health ally in range;
--     melee_unwavering 4 entries / 4 keys (Locus of Virulence, The Dance of
--                                        Dreaming, The Waltz of Lethargy,
--                                        Ultimate Verdict - in-melee self).
--   The table grows 573 -> 579 entries (599 -> 605 keys); melee_unwavering
--   477 -> 481.
--   RED CONTROL: with H92_LIVE / H92_ANN pointing at the pre-edit snapshot (the
--   shipped harness-91 build, 573 entries), the grown-table pins and this
--   HARNESS-92 section fail; the SILENT worlds pass trivially because the new
--   abilities are simply absent on the snapshot.
-- ============================================================================
function run_h92()
  local BS  = "wh3_dlc26_lord_abilities_blood_sacrifice"
  local EDR = "wh3_dlc26_unit_abilities_eat_da_runts"
  local LOV = "wh3_main_character_abilities_locus_of_virulence"

  local live_src92 = read_file(LIVE)
  local ann_src92  = read_file(ANN)
  local RED92 = { fires = 0, claims = 0, ui = 0 }
  local function posv(v) return (v == true) or (type(v) == "number") end
  local function lg(tag, v) return (tag ~= "[live] ") or posv(v) end
  local function badd92(marker) return "zz_auto_badge_" .. marker end
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function note92(W, TAG)
    RED92.ui = RED92.ui + (W.ui_failures or 0)
    if TAG == "[live] " then
      RED92.fires = RED92.fires + #W.fires
      RED92.claims = RED92.claims + count_log(W, "claim: ")
    end
  end
  local function boot92(W, PATH, TAG, uid, marker, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, badd92(marker)); ui(W)
    W.conflict = true
    return true
  end

  -- --------------------------------------------------- 0p: tokens (both files)
  print("== HARNESS 92 - section 0p: the final roster build + grown table (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src92 }, { name = "ann", src = ann_src92 } }) do
    local nm, s = f.name, f.src
    check("0p " .. nm .. ": the two new ally-heal evaluators exist",
      raw_find(s, "function FOURTH.evaluate_blood_sacrifice(unit, routing)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.evaluate_eat_da_runts(unit, routing)", 1, true) ~= nil)
    check("0p " .. nm .. ": the two new trigger names are wired in the map",
      raw_find(s, "blood_sacrifice = FOURTH.evaluate_blood_sacrifice,", 1, true) ~= nil
      and raw_find(s, "eat_da_runts = FOURTH.evaluate_eat_da_runts,", 1, true) ~= nil)
    check("0p " .. nm .. ": the conservative named 25 m range constants exist",
      raw_find(s, "FOURTH.BLOOD_SACRIFICE_RANGE_M = 25", 1, true) ~= nil
      and raw_find(s, "FOURTH.EAT_DA_RUNTS_RANGE_M = 25", 1, true) ~= nil)
    check("0p " .. nm .. ": the grown table is 579 entries (each with a badge field)",
      cp(s, "\t{ marker = ") == 579 and cp(s, 'badge = "') == 579)
    check("0p " .. nm .. ": the trigger counts grew to (melee_unwavering 481, blood_sacrifice 1, eat_da_runts 1) "
      .. "and every other trigger is UNCHANGED (ushoran_health 41, charge_or_melee 29, charge_only 1, "
      .. "wavering_self 3, wavering_self_or_ally 2, charge_or_wavering 1, wavering_ally_range 1, tired 2, "
      .. "metallurgy_melee 8, melee_health75 2)",
      cp(s, 'trigger = "melee_unwavering"') == 481 and cp(s, 'trigger = "blood_sacrifice"') == 1
      and cp(s, 'trigger = "eat_da_runts"') == 1 and cp(s, 'trigger = "ushoran_health"') == 41
      and cp(s, 'trigger = "charge_or_melee"') == 29 and cp(s, 'trigger = "charge_only"') == 1
      and cp(s, 'trigger = "wavering_self"') == 3 and cp(s, 'trigger = "wavering_self_or_ally"') == 2
      and cp(s, 'trigger = "charge_or_wavering"') == 1 and cp(s, 'trigger = "wavering_ally_range"') == 1
      and cp(s, 'trigger = "tired"') == 2 and cp(s, 'trigger = "metallurgy_melee"') == 8
      and cp(s, 'trigger = "melee_health75"') == 2)
    check("0p " .. nm .. ": every new entry is present (marker + badge + key)",
      raw_find(s, 'marker = "blood_sacrifice"', 1, true) ~= nil
      and raw_find(s, 'badge = "zz_auto_badge_blood_sacrifice"', 1, true) ~= nil
      and raw_find(s, '"' .. BS .. '"', 1, true) ~= nil
      and raw_find(s, 'marker = "eat_da_runts"', 1, true) ~= nil
      and raw_find(s, 'badge = "zz_auto_badge_eat_da_runts"', 1, true) ~= nil
      and raw_find(s, '"' .. EDR .. '"', 1, true) ~= nil)
    check("0p " .. nm .. ": the four melee_unwavering entries are present",
      raw_find(s, 'marker = "locus_of_virulence"', 1, true) ~= nil
      and raw_find(s, 'marker = "the_dance_of_dreaming"', 1, true) ~= nil
      and raw_find(s, 'marker = "the_waltz_of_lethargy"', 1, true) ~= nil
      and raw_find(s, 'marker = "ultimate_verdict"', 1, true) ~= nil
      and raw_find(s, '"' .. LOV .. '"', 1, true) ~= nil
      and raw_find(s, '"wh3_cp1_character_abilities_terrifying_presence"', 1, true) ~= nil)
    check("0p " .. nm .. ": the self-cast writes stay exactly two (eat-da-runts self arm rides the default)",
      cp(s, "FOURTH.cast_target = unit") == 2)
    check("0p " .. nm .. ": each new chosen-ally field is set once and cleared three times",
      cp(s, "FOURTH.bs_ally = best_ally") == 1 and cp(s, "FOURTH.bs_ally = nil") == 3
      and cp(s, "FOURTH.edr_ally = best_ally") == 1 and cp(s, "FOURTH.edr_ally = nil") == 3)
    check("0p " .. nm .. ": NO army-bar key is in the mod (standing exclusion)",
      raw_find(s, "army_abilities", 1, true) == nil)
  end
  check("0p ann: the reading copy stays log-free and find-free",
    raw_find(ann_src92, "log(", 1, true) == nil and raw_find(ann_src92, "string.find(", 1, true) == nil)
  check("0p live: the new ally-heal drift skips are reported",
    raw_find(live_src92, "blood_sacrifice SKIPPED:", 1, true) ~= nil
    and raw_find(live_src92, "eat_da_runts SKIPPED:", 1, true) ~= nil)

  -- ==========================================================================
  -- P1. BLOOD SACRIFICE: a hurt ally in range -> FIRES, cast on the ALLY.
  -- ==========================================================================
  local function world_p1(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "lord", uid = 9301, owns = { BS }, melee = false, health_percent = 100 },
      { name = "ally", uid = 9302, owns = {}, melee = false, health_percent = 40, dist = 15 },
    }, cards = { { id = "9301", state = "active", vis = true }, { id = "9302", state = "active", vis = true } },
       bar = { { id = "b1", key = BS } } })
    print("== " .. TAG .. "P1. BLOOD SACRIFICE: a hurt ally in range -> FIRES (cast on the ally) == ")
    if not boot92(W, PATH, TAG, 9301, "blood_sacrifice", "P1") then return nil end
    polln(W, 1)
    local caster = unit_of(W, 9301)
    local ally = unit_of(W, 9302)
    local a = (#W.fires == 1 and W.fires[1].uid == 9301 and W.fires[1].key == BS)
    check(TAG .. "P1a: the lord fired blood_sacrifice once (" .. fire_detail(W) .. ")", a)
    local b = (fire_target_for(W, 9301) == ally and ally ~= caster)
    check(TAG .. "P1b: the cast target is the HURT ALLY, not the caster", b)
    local c = (count_log(W, "reason: blood sacrifice: lowest-health ally 40% (<= 75%), cast on ally") == 1)
    check(TAG .. "P1c: the blood-sacrifice reason names the live percent [live log]", lg(TAG, c))
    note92(W, TAG); tally(W)
    return a and b and lg(TAG, c)
  end

  -- ==========================================================================
  -- P2. BLOOD SACRIFICE, SILENT: no ally is hurt -> SILENT.
  -- ==========================================================================
  local function world_p2(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "lord", uid = 9311, owns = { BS }, melee = false, health_percent = 100 },
      { name = "ally", uid = 9312, owns = {}, melee = false, health_percent = 90, dist = 15 },
    }, cards = { { id = "9311", state = "active", vis = true }, { id = "9312", state = "active", vis = true } },
       bar = { { id = "b1", key = BS } } })
    print("== " .. TAG .. "P2. BLOOD SACRIFICE: the ally is healthy (90%) -> SILENT == ")
    if not boot92(W, PATH, TAG, 9311, "blood_sacrifice", "P2") then return nil end
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "P2a: the healthy-only board stays SILENT (" .. fire_detail(W) .. ")", a)
    note92(W, TAG); tally(W)
    return a
  end

  -- ==========================================================================
  -- P3. BLOOD SACRIFICE, RANGE BOUNDARY (inside): the ally is exactly at the
  --     25 m trigger radius -> still IN range -> FIRES.
  -- ==========================================================================
  local function world_p3(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "lord", uid = 9321, owns = { BS }, melee = false, health_percent = 100 },
      { name = "ally", uid = 9322, owns = {}, melee = false, health_percent = 40, dist = 25 },
    }, cards = { { id = "9321", state = "active", vis = true }, { id = "9322", state = "active", vis = true } },
       bar = { { id = "b1", key = BS } } })
    print("== " .. TAG .. "P3. BLOOD SACRIFICE: the ally is exactly at 25 m -> FIRES (boundary in) == ")
    if not boot92(W, PATH, TAG, 9321, "blood_sacrifice", "P3") then return nil end
    polln(W, 1)
    local ally = unit_of(W, 9322)
    local a = (#W.fires == 1 and W.fires[1].uid == 9321 and W.fires[1].key == BS)
    check(TAG .. "P3a: the 25.0 m ally is WITHIN the 25 m trigger range -> FIRES (" .. fire_detail(W) .. ")", a)
    local b = (fire_target_for(W, 9321) == ally)
    check(TAG .. "P3b: the boundary-in cast targets the ally", b)
    note92(W, TAG); tally(W)
    return a and b
  end

  -- ==========================================================================
  -- P4. BLOOD SACRIFICE, RANGE BOUNDARY (outside): the ally is at 26 m -> OUT
  --     of the 25 m trigger range -> SILENT.
  -- ==========================================================================
  local function world_p4(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "lord", uid = 9331, owns = { BS }, melee = false, health_percent = 100 },
      { name = "ally", uid = 9332, owns = {}, melee = false, health_percent = 40, dist = 26 },
    }, cards = { { id = "9331", state = "active", vis = true }, { id = "9332", state = "active", vis = true } },
       bar = { { id = "b1", key = BS } } })
    print("== " .. TAG .. "P4. BLOOD SACRIFICE: the ally is at 26 m -> SILENT (boundary out) == ")
    if not boot92(W, PATH, TAG, 9331, "blood_sacrifice", "P4") then return nil end
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "P4a: the 26 m ally is OUT of the 25 m trigger range -> NO cast (" .. fire_detail(W) .. ")", a)
    note92(W, TAG); tally(W)
    return a
  end

  -- ==========================================================================
  -- P5. BLOOD SACRIFICE, DRIFT: the ally is in range at DECIDE (15 m) but out
  --     at CAST (60 m) -> the cast is SKIPPED rather than wasted.
  -- ==========================================================================
  local function world_p5(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "lord", uid = 9341, owns = { BS }, melee = false, health_percent = 100 },
      { name = "ally", uid = 9342, owns = {}, melee = false, health_percent = 40, dist_seq = { 15, 60 } },
    }, cards = { { id = "9341", state = "active", vis = true }, { id = "9342", state = "active", vis = true } },
       bar = { { id = "b1", key = BS } } })
    print("== " .. TAG .. "P5. BLOOD SACRIFICE: the ally DRIFTS out of range between decide and cast -> SKIP == ")
    if not boot92(W, PATH, TAG, 9341, "blood_sacrifice", "P5") then return nil end
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "P5a: the drifted ally -> the cast is SKIPPED, nothing fires (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "blood_sacrifice SKIPPED:") == 1)
    check(TAG .. "P5b: the blood-sacrifice drift skip is reported [live log]", lg(TAG, b))
    local c = (count_log(W, "blood_sacrifice ally: ui") == 1)
    check(TAG .. "P5c: the ally WAS chosen at decide time (chosen-ally line once) [live log]", lg(TAG, c))
    note92(W, TAG); tally(W)
    return a and lg(TAG, b) and lg(TAG, c)
  end

  -- ==========================================================================
  -- P6. EAT DA RUNTS!, SELF ARM: the owner is at 70% health -> FIRES, target
  --     is the OWNER itself (self-cast).
  -- ==========================================================================
  local function world_p6(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "unit", uid = 9351, owns = { EDR }, melee = false, health_percent = 70 },
    }, cards = { { id = "9351", state = "active", vis = true } }, bar = { { id = "b1", key = EDR } } })
    print("== " .. TAG .. "P6. EAT DA RUNTS!: owner at 70% health -> FIRES (self arm) == ")
    if not boot92(W, PATH, TAG, 9351, "eat_da_runts", "P6") then return nil end
    polln(W, 1)
    local caster = unit_of(W, 9351)
    local a = (#W.fires == 1 and W.fires[1].uid == 9351 and W.fires[1].key == EDR)
    check(TAG .. "P6a: the hurt owner fired eat_da_runts once (" .. fire_detail(W) .. ")", a)
    local b = (fire_target_for(W, 9351) == caster)
    check(TAG .. "P6b: the self arm casts on the OWNER itself", b)
    local c = (count_log(W, "reason: eat da runts: self health 70% (<= 75%), cast on self") == 1)
    check(TAG .. "P6c: the eat-da-runts self reason names the live percent [live log]", lg(TAG, c))
    note92(W, TAG); tally(W)
    return a and b and lg(TAG, c)
  end

  -- ==========================================================================
  -- P7. EAT DA RUNTS!, ALLY ARM: the owner is healthy, a hurt ally is in range
  --     -> FIRES, cast on the ALLY.
  -- ==========================================================================
  local function world_p7(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "unit", uid = 9361, owns = { EDR }, melee = false, health_percent = 100 },
      { name = "ally", uid = 9362, owns = {}, melee = false, health_percent = 50, dist = 15 },
    }, cards = { { id = "9361", state = "active", vis = true }, { id = "9362", state = "active", vis = true } },
       bar = { { id = "b1", key = EDR } } })
    print("== " .. TAG .. "P7. EAT DA RUNTS!: healthy owner, hurt ally in range -> FIRES (ally arm) == ")
    if not boot92(W, PATH, TAG, 9361, "eat_da_runts", "P7") then return nil end
    polln(W, 1)
    local caster = unit_of(W, 9361)
    local ally = unit_of(W, 9362)
    local a = (#W.fires == 1 and W.fires[1].uid == 9361 and W.fires[1].key == EDR)
    check(TAG .. "P7a: the healthy owner fired eat_da_runts once for the hurt ally (" .. fire_detail(W) .. ")", a)
    local b = (fire_target_for(W, 9361) == ally and ally ~= caster)
    check(TAG .. "P7b: the ally arm casts on the HURT ALLY", b)
    local c = (count_log(W, "reason: eat da runts: lowest-health ally 50% (<= 75%), cast on ally") == 1)
    check(TAG .. "P7c: the eat-da-runts ally reason names the live percent [live log]", lg(TAG, c))
    note92(W, TAG); tally(W)
    return a and b and lg(TAG, c)
  end

  -- ==========================================================================
  -- P8. EAT DA RUNTS!, SILENT: owner healthy and no hurt ally -> SILENT.
  -- ==========================================================================
  local function world_p8(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "unit", uid = 9371, owns = { EDR }, melee = false, health_percent = 100 },
      { name = "ally", uid = 9372, owns = {}, melee = false, health_percent = 95, dist = 15 },
    }, cards = { { id = "9371", state = "active", vis = true }, { id = "9372", state = "active", vis = true } },
       bar = { { id = "b1", key = EDR } } })
    print("== " .. TAG .. "P8. EAT DA RUNTS!: healthy owner, no hurt ally -> SILENT == ")
    if not boot92(W, PATH, TAG, 9371, "eat_da_runts", "P8") then return nil end
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "P8a: the all-healthy board stays SILENT (" .. fire_detail(W) .. ")", a)
    note92(W, TAG); tally(W)
    return a
  end

  -- ==========================================================================
  -- P9. EAT DA RUNTS!, DRIFT (ally arm): the ally is in range at DECIDE (15 m)
  --     but out at CAST (60 m) -> the cast is SKIPPED.
  -- ==========================================================================
  local function world_p9(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "unit", uid = 9381, owns = { EDR }, melee = false, health_percent = 100 },
      { name = "ally", uid = 9382, owns = {}, melee = false, health_percent = 50, dist_seq = { 15, 60 } },
    }, cards = { { id = "9381", state = "active", vis = true }, { id = "9382", state = "active", vis = true } },
       bar = { { id = "b1", key = EDR } } })
    print("== " .. TAG .. "P9. EAT DA RUNTS!: the ally DRIFTS out of range between decide and cast -> SKIP == ")
    if not boot92(W, PATH, TAG, 9381, "eat_da_runts", "P9") then return nil end
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "P9a: the drifted ally -> the cast is SKIPPED, nothing fires (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "eat_da_runts SKIPPED:") == 1)
    check(TAG .. "P9b: the eat-da-runts drift skip is reported [live log]", lg(TAG, b))
    local c = (count_log(W, "eat_da_runts ally: ui") == 1)
    check(TAG .. "P9c: the ally WAS chosen at decide time (chosen-ally line once) [live log]", lg(TAG, c))
    note92(W, TAG); tally(W)
    return a and lg(TAG, b) and lg(TAG, c)
  end

  -- ==========================================================================
  -- P10. MELEE_UNWAVERING: a NEW in-melee-self member (Locus of Virulence)
  --      FIRES in melee with the shared in-melee-self reason, self-cast.
  -- ==========================================================================
  local function world_p10(PATH, TAG)
    local W = make_world({ can_perform = true, units = {
      { name = "chaos", uid = 9391, owns = { LOV }, melee = true, wavering = false },
    }, cards = { { id = "9391", state = "active", vis = true } }, bar = { { id = "b1", key = LOV } } })
    print("== " .. TAG .. "P10. MELEE_UNWAVERING member: in melee -> FIRES (locus_of_virulence) == ")
    if not boot92(W, PATH, TAG, 9391, "locus_of_virulence", "P10") then return nil end
    polln(W, 1)
    local caster = unit_of(W, 9391)
    local a = (#W.fires == 1 and W.fires[1].uid == 9391 and W.fires[1].key == LOV)
    check(TAG .. "P10a: the in-melee unit fired locus_of_virulence once (" .. fire_detail(W) .. ")", a)
    local b = (fire_target_for(W, 9391) == caster)
    check(TAG .. "P10b: the cast target is the OWNER itself (self-cast)", b)
    local c = (count_log(W, "reason: in melee, morale not wavering") == 1)
    check(TAG .. "P10c: the shared in-melee-self reason is used [live log]", lg(TAG, c))
    note92(W, TAG); tally(W)
    return a and b and lg(TAG, c)
  end

  print()
  print("== HARNESS 92 - the final roster build: two new ally-heal triggers + four melee entries ==")
  local p01a = world_p1(ANN, "[annotated] ");  local p01b = world_p1(LIVE, "[live] ")
  local p02a = world_p2(ANN, "[annotated] ");  local p02b = world_p2(LIVE, "[live] ")
  local p03a = world_p3(ANN, "[annotated] ");  local p03b = world_p3(LIVE, "[live] ")
  local p04a = world_p4(ANN, "[annotated] ");  local p04b = world_p4(LIVE, "[live] ")
  local p05a = world_p5(ANN, "[annotated] ");  local p05b = world_p5(LIVE, "[live] ")
  local p06a = world_p6(ANN, "[annotated] ");  local p06b = world_p6(LIVE, "[live] ")
  local p07a = world_p7(ANN, "[annotated] ");  local p07b = world_p7(LIVE, "[live] ")
  local p08a = world_p8(ANN, "[annotated] ");  local p08b = world_p8(LIVE, "[live] ")
  local p09a = world_p9(ANN, "[annotated] ");  local p09b = world_p9(LIVE, "[live] ")
  local p10a = world_p10(ANN, "[annotated] "); local p10b = world_p10(LIVE, "[live] ")

  local results = { p01a, p01b, p02a, p02b, p03a, p03b, p04a, p04b, p05a, p05b,
                    p06a, p06b, p07a, p07b, p08a, p08b, p09a, p09b, p10a, p10b }
  local n_ok = 0
  for _, r in ipairs(results) do if posv(r) then n_ok = n_ok + 1 end end

  check("every ui tick ran clean across the HARNESS-92 worlds (" .. RED92.ui .. " failures)", RED92.ui == 0)

  if not RED_MODE then
    check("the HARNESS-92 worlds all behaved (live+annotated: P1..P10) - " .. n_ok .. "/20", n_ok == 20)
    check("HEADLINE (harness 92): THE FINAL ROSTER BUILD ships the SIX built individual abilities from the "
      .. "remaining-abilities triage - TWO NEW ally-heal triggers, each its own evaluator (blood_sacrifice: cast "
      .. "on the lowest-health ally in range at or below 75%; eat_da_runts: cast on self at or below 75%, else the "
      .. "lowest-health ally in range) plus FOUR in-melee-self entries riding the EXISTING melee_unwavering "
      .. "evaluator (Locus of Virulence, The Dance of Dreaming, The Waltz of Lethargy, Ultimate Verdict). Each new "
      .. "trigger casts on the CHOSEN ALLY, uses a conservative named 25 m range constant, and RE-CHECKS the gap "
      .. "and the ally's health before the cast (skip on drift). The table grows 573 -> 579 entries (599 -> 605 "
      .. "keys); melee_unwavering 477 -> 481; no new chunk locals.", n_ok == 20)
  else
    check("RED CONTROL (harness 92): on the pre-edit snapshot (the shipped harness-91 build, 573 entries) the "
      .. "grown-table pins and this HARNESS-92 section fail; the SILENT worlds pass trivially because the new "
      .. "abilities are simply absent on the snapshot (P2 / P4 / P8 both files = 6) plus the ANNOTATED legs of the "
      .. "drift worlds P5 / P9 (their live-only skip-log legs are masked in the reading copy) = 8 - " .. n_ok
      .. "/20 world results pass (want 8), fires " .. RED92.fires .. ", claims " .. RED92.claims, n_ok == 8)
  end
end
run_h92()
