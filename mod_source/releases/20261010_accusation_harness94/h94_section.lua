-- ============================================================================
-- HARNESS 94 (this round): ACCUSATION'S AUTOMATIC ACTIVATION - the FIRST
--   ENEMY-TARGETED trigger, and the first ability whose cast target is an
--   ENEMY unit.
--   A new reusable evaluator `enemy_engaged_or_shot` fires when an enemy unit
--   in range is in melee OR under missile fire; the chosen enemy is the CAST
--   TARGET (never the owner), cast through the round-4-proven bench_fresh
--   fresh-handle route (caster + target re-fetched the same tick). Accusation's
--   entry moves from melee_unwavering (481 -> 480) onto the new trigger
--   (0 -> 1); the table stays 579 entries / 605 keys.
--   This harness proves, against the LIVE source and the ANNOTATED copy:
--     0r: the evaluator/helpers/constant/wiring/tooltip tokens, the moved
--         trigger counts, the poll clears, and the distinct live reason strings;
--     N1..N9: enemy in melee in range -> FIRES at that enemy; enemy under
--         missile fire -> FIRES; neither -> SILENT; out of range -> SILENT;
--         condition lapses between pick and cast -> SKIPPED; unreadable
--         is_under_missile_attack -> treated FALSE with the one-time log;
--         self-cast regression (the target is NEVER the owner); prefer in-melee
--         over missile; closest among equals.
--   RED CONTROL: with H94_LIVE / H94_ANN pointing at the pre-edit snapshot (the
--   shipped harness-93 build: no enemy evaluator, Accusation still on
--   melee_unwavering = 481) the 0r section tokens fail and every firing N-world
--   fires nothing - only the SILENT worlds pass (N3/N4 both files = 4, plus the
--   ANNOTATED legs of the lapse/unreadable worlds N5/N6 = 2).
-- ============================================================================
function run_h94()
  local ACC = "wh_main_hero_abilities_accusation"
  local live_src94 = read_file(LIVE)
  local ann_src94  = read_file(ANN)
  local RED94 = { fires = 0, claims = 0, ui = 0 }
  local function posv(v) return (v == true) or (type(v) == "number") end
  local function lg(tag, v) return (tag ~= "[live] ") or posv(v) end
  local function badd94(marker) return "zz_auto_badge_" .. marker end
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function note94(W, TAG)
    RED94.ui = RED94.ui + (W.ui_failures or 0)
    if TAG == "[live] " then
      RED94.fires = RED94.fires + #W.fires
      RED94.claims = RED94.claims + count_log(W, "claim: ")
    end
  end
  local function boot94(W, PATH, TAG, uid, marker, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, badd94(marker)); ui(W)
    W.conflict = true
    return true
  end
  -- the enemy UNIT OBJECT behind a uid (in the enemy list, not the friendly one)
  local function enemy_of(W, uid)
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        local ok, id = pcall(function() return pr.unit:unique_ui_id() end)
        if ok and tostring(id) == tostring(uid) then return pr.unit end
      end
    end
    return nil
  end

  -- --------------------------------------------------- 0r: tokens (both files)
  print("== HARNESS 94 - section 0r: Accusation's enemy trigger tokens (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src94 }, { name = "ann", src = ann_src94 } }) do
    local nm, s = f.name, f.src
    check("0r " .. nm .. ": the enemy_engaged_or_shot evaluator exists",
      raw_find(s, "function FOURTH.evaluate_enemy_engaged_or_shot(unit, routing)", 1, true) ~= nil)
    check("0r " .. nm .. ": the trigger is wired in the map",
      raw_find(s, "enemy_engaged_or_shot = FOURTH.evaluate_enemy_engaged_or_shot,", 1, true) ~= nil)
    check("0r " .. nm .. ": the tooltip wording entry is present verbatim",
      raw_find(s, "enemy_engaged_or_shot = \"When armed, fires when an enemy unit in range is in melee or under missile fire\",", 1, true) ~= nil)
    check("0r " .. nm .. ": Accusation rides the new trigger",
      raw_find(s, "{ marker = \"accusation\", name = \"Accusation\", trigger = \"enemy_engaged_or_shot\",", 1, true) ~= nil)
    check("0r " .. nm .. ": the conservative named range constant exists (75 m)",
      raw_find(s, "FOURTH.ACCUSATION_RANGE_M = 75", 1, true) ~= nil)
    check("0r " .. nm .. ": the enemy enumerator is read",
      raw_find(s, "bm:get_scriptunits_for_main_enemy_army_to_local_player()", 1, true) ~= nil)
    check("0r " .. nm .. ": the proven fresh-caster re-fetch helper exists",
      raw_find(s, "function FOURTH.eg_fresh_caster_su(unit)", 1, true) ~= nil)
    check("0r " .. nm .. ": is_under_missile_attack is read fail-safe",
      raw_find(s, "enemy:is_under_missile_attack()", 1, true) ~= nil)
    check("0r " .. nm .. ": the trigger counts moved (melee_unwavering 480, enemy_engaged_or_shot 1)",
      cp(s, 'trigger = "melee_unwavering"') == 480 and cp(s, 'trigger = "enemy_engaged_or_shot"') == 1)
    check("0r " .. nm .. ": the table stays 579 entries / 579 badges",
      cp(s, "\t{ marker = ") == 579 and cp(s, 'badge = "') == 579)
    check("0r " .. nm .. ": the self-cast writes stay exactly two",
      cp(s, "FOURTH.cast_target = unit") == 2)
    check("0r " .. nm .. ": the enemy slots are set once and cleared (eg_enemy 3, eg_caster_su 2)",
      cp(s, "FOURTH.eg_enemy = nil") == 3 and cp(s, "FOURTH.eg_caster_su = nil") == 2
      and cp(s, "FOURTH.eg_enemy = best_enemy") == 1)
    check("0r " .. nm .. ": NO army-bar key is in the mod (standing exclusion)",
      raw_find(s, "army_abilities", 1, true) == nil)
  end
  check("0r live: the DISTINCT arm reason strings are present",
    raw_find(live_src94, 'reason = "enemy in melee (targeting " .. etype .. ")"', 1, true) ~= nil
    and raw_find(live_src94, 'reason = "enemy under missile fire (targeting " .. etype .. ")"', 1, true) ~= nil)
  check("0r live: the chosen-target, pre-cast re-check and lapse lines are reported",
    raw_find(live_src94, "accusation target: '", 1, true) ~= nil
    and raw_find(live_src94, "accusation pre-cast re-check:", 1, true) ~= nil
    and raw_find(live_src94, "accusation SKIPPED: the chosen enemy lapsed before the cast", 1, true) ~= nil)
  check("0r live: the one-time unreadable-missile notice exists",
    raw_find(live_src94, "accusation: enemy is_under_missile_attack read UNAVAILABLE", 1, true) ~= nil)
  check("0r ann: the reading copy stays log-free and find-free",
    raw_find(ann_src94, "log(", 1, true) == nil and raw_find(ann_src94, "string.find", 1, true) == nil)

  -- ==========================================================================
  -- N1. ENEMY IN MELEE, IN RANGE -> FIRES at that enemy (fresh-handle route).
  -- ==========================================================================
  local function world_n1(PATH, TAG)
    local W = make_world({ can_perform = true,
      units = { { name = "witch_hunter", uid = 9401, owns = { ACC }, melee = false, in_range = true } },
      enemies = { { name = "orc_boyz", uid = 9402, melee = true } },
      cards = { { id = "9401", state = "active", vis = true } },
      bar = { { id = "b1", key = ACC } } })
    print("== " .. TAG .. "N1. ACCUSATION: an enemy in melee in range -> FIRES at it == ")
    if not boot94(W, PATH, TAG, 9401, "accusation", "N1") then return nil end
    local friendly0 = W.friendly_calls or 0
    polln(W, 1)
    local hunter = unit_of(W, 9401)
    local enemy = enemy_of(W, 9402)
    local a = (#W.fires == 1 and W.fires[1].uid == 9401 and W.fires[1].key == ACC)
    check(TAG .. "N1a: the hunter fired accusation once (" .. fire_detail(W) .. ")", a)
    local b = (fire_target_for(W, 9401) == enemy and enemy ~= nil and enemy ~= hunter)
    check(TAG .. "N1b: the cast target is the ENEMY, not the owner", b)
    local c = ((W.friendly_calls or 0) > friendly0)
    check(TAG .. "N1c: the CASTER was re-fetched FRESH on the firing tick (the proven route)", c)
    local d = (count_log(W, "reason: enemy in melee (targeting orc_boyz)") == 1)
    check(TAG .. "N1d: the melee-arm reason names the enemy type [live log]", lg(TAG, d))
    note94(W, TAG); tally(W)
    return a and b and c and lg(TAG, d)
  end

  -- ==========================================================================
  -- N2. ENEMY UNDER MISSILE FIRE, IN RANGE -> FIRES (distance-fallback range).
  -- ==========================================================================
  local function world_n2(PATH, TAG)
    local W = make_world({ can_perform = true,
      units = { { name = "witch_hunter", uid = 9411, owns = { ACC }, melee = false, dist = 20 } },
      enemies = { { name = "goblin_archers", uid = 9412, melee = false, missile = true } },
      cards = { { id = "9411", state = "active", vis = true } },
      bar = { { id = "b1", key = ACC } } })
    print("== " .. TAG .. "N2. ACCUSATION: an enemy under missile fire in range -> FIRES == ")
    if not boot94(W, PATH, TAG, 9411, "accusation", "N2") then return nil end
    polln(W, 1)
    local enemy = enemy_of(W, 9412)
    local a = (#W.fires == 1 and W.fires[1].uid == 9411 and W.fires[1].key == ACC)
    check(TAG .. "N2a: the hunter fired accusation once (" .. fire_detail(W) .. ")", a)
    local b = (fire_target_for(W, 9411) == enemy and enemy ~= nil)
    check(TAG .. "N2b: the cast target is the enemy under fire", b)
    local c = (count_log(W, "reason: enemy under missile fire (targeting goblin_archers)") == 1)
    check(TAG .. "N2c: the missile-arm reason names the enemy type [live log]", lg(TAG, c))
    note94(W, TAG); tally(W)
    return a and b and lg(TAG, c)
  end

  -- ==========================================================================
  -- N3. ENEMY IN RANGE BUT NEITHER in melee nor under fire -> SILENT.
  -- ==========================================================================
  local function world_n3(PATH, TAG)
    local W = make_world({ can_perform = true,
      units = { { name = "witch_hunter", uid = 9421, owns = { ACC }, melee = false, dist = 20 } },
      enemies = { { name = "idle_orcs", uid = 9422, melee = false, missile = false } },
      cards = { { id = "9421", state = "active", vis = true } },
      bar = { { id = "b1", key = ACC } } })
    print("== " .. TAG .. "N3. ACCUSATION: the enemy is neither in melee nor under fire -> SILENT == ")
    if not boot94(W, PATH, TAG, 9421, "accusation", "N3") then return nil end
    polln(W, 3)
    local a = (#W.fires == 0)
    check(TAG .. "N3a: the idle-enemy board stays SILENT (" .. fire_detail(W) .. ")", a)
    note94(W, TAG); tally(W)
    return a
  end

  -- ==========================================================================
  -- N4. ENEMY IN MELEE BUT OUT OF RANGE -> SILENT.
  -- ==========================================================================
  local function world_n4(PATH, TAG)
    local W = make_world({ can_perform = true,
      units = { { name = "witch_hunter", uid = 9431, owns = { ACC }, melee = false, dist = 200 } },
      enemies = { { name = "distant_orcs", uid = 9432, melee = true } },
      cards = { { id = "9431", state = "active", vis = true } },
      bar = { { id = "b1", key = ACC } } })
    print("== " .. TAG .. "N4. ACCUSATION: the enemy is in melee but OUT of range -> SILENT == ")
    if not boot94(W, PATH, TAG, 9431, "accusation", "N4") then return nil end
    polln(W, 3)
    local a = (#W.fires == 0)
    check(TAG .. "N4a: the out-of-range board stays SILENT (" .. fire_detail(W) .. ")", a)
    note94(W, TAG); tally(W)
    return a
  end

  -- ==========================================================================
  -- N5. THE CONDITION LAPSES between the pick and the cast -> SKIPPED.
  --     The enemy is in melee on the evaluator's read; on the pre-cast re-read
  --     it is NOT (a melee_seq of true then false).
  -- ==========================================================================
  local function world_n5(PATH, TAG)
    local W = make_world({ can_perform = true,
      units = { { name = "witch_hunter", uid = 9441, owns = { ACC }, melee = false, dist = 20 } },
      enemies = { { name = "orc_boyz", uid = 9442, melee_seq = { true, false } } },
      cards = { { id = "9441", state = "active", vis = true } },
      bar = { { id = "b1", key = ACC } } })
    print("== " .. TAG .. "N5. ACCUSATION: the condition lapses before the cast -> SKIPPED == ")
    if not boot94(W, PATH, TAG, 9441, "accusation", "N5") then return nil end
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "N5a: the lapsed target is NOT fired for (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "accusation SKIPPED: the chosen enemy lapsed before the cast") == 1)
    check(TAG .. "N5b: the pre-cast lapse skip is reported once [live log]", lg(TAG, b))
    note94(W, TAG); tally(W)
    return a and lg(TAG, b)
  end

  -- ==========================================================================
  -- N6. UNREADABLE is_under_missile_attack -> treated FALSE + ONE-TIME log.
  -- ==========================================================================
  local function world_n6(PATH, TAG)
    local W = make_world({ can_perform = true,
      units = { { name = "witch_hunter", uid = 9451, owns = { ACC }, melee = false, dist = 20 } },
      enemies = { { name = "orc_boyz", uid = 9452, melee = false, missile_raises = true } },
      cards = { { id = "9451", state = "active", vis = true } },
      bar = { { id = "b1", key = ACC } } })
    print("== " .. TAG .. "N6. ACCUSATION: unreadable is_under_missile_attack -> FALSE + one-time log == ")
    if not boot94(W, PATH, TAG, 9451, "accusation", "N6") then return nil end
    polln(W, 3)
    local a = (#W.fires == 0)
    check(TAG .. "N6a: an unreadable missile read never fires (" .. fire_detail(W) .. ")", a)
    local b = ((W.missile_raise_attempts or 0) >= 1)
    check(TAG .. "N6b: the mock WAS asked is_under_missile_attack (raised " .. (W.missile_raise_attempts or 0) .. ")", b)
    local c = (count_log(W, "is_under_missile_attack read UNAVAILABLE") == 1)
    check(TAG .. "N6c: the unreadable read is reported exactly ONCE [live log]", lg(TAG, c))
    note94(W, TAG); tally(W)
    return a and b and lg(TAG, c)
  end

  -- ==========================================================================
  -- N7. SELF-CAST REGRESSION GUARD: the target is the ENEMY, NEVER the owner.
  -- ==========================================================================
  local function world_n7(PATH, TAG)
    local W = make_world({ can_perform = true,
      units = { { name = "witch_hunter", uid = 9461, owns = { ACC }, melee = false, in_range = true } },
      enemies = { { name = "chaos_warriors", uid = 9462, melee = true } },
      cards = { { id = "9461", state = "active", vis = true } },
      bar = { { id = "b1", key = ACC } } })
    print("== " .. TAG .. "N7. ACCUSATION: the cast target is NEVER the owner == ")
    if not boot94(W, PATH, TAG, 9461, "accusation", "N7") then return nil end
    polln(W, 1)
    local hunter = unit_of(W, 9461)
    local enemy = enemy_of(W, 9462)
    local a = (#W.fires == 1)
    check(TAG .. "N7a: the hunter fired once (" .. fire_detail(W) .. ")", a)
    local b = (fire_target_for(W, 9461) == enemy)
    check(TAG .. "N7b: the cast target IS the enemy unit", b)
    local c = (fire_target_for(W, 9461) ~= hunter)
    check(TAG .. "N7c: the cast target is NOT the owner (self-cast regression guard)", c)
    note94(W, TAG); tally(W)
    return a and b and c
  end

  -- ==========================================================================
  -- N8. PREFER IN-MELEE over under-fire: a missile enemy and a melee enemy,
  --     both in range -> the MELEE one is chosen.
  -- ==========================================================================
  local function world_n8(PATH, TAG)
    local W = make_world({ can_perform = true,
      units = { { name = "witch_hunter", uid = 9471, owns = { ACC }, melee = false, in_range = true } },
      enemies = { { name = "goblin_archers", uid = 9472, melee = false, missile = true },
                  { name = "orc_boyz", uid = 9473, melee = true } },
      cards = { { id = "9471", state = "active", vis = true } },
      bar = { { id = "b1", key = ACC } } })
    print("== " .. TAG .. "N8. ACCUSATION: an in-melee enemy is preferred over one under fire == ")
    if not boot94(W, PATH, TAG, 9471, "accusation", "N8") then return nil end
    polln(W, 1)
    local melee_enemy = enemy_of(W, 9473)
    local missile_enemy = enemy_of(W, 9472)
    local a = (#W.fires == 1 and fire_target_for(W, 9471) == melee_enemy)
    check(TAG .. "N8a: the MELEE enemy is chosen, not the closer missile one", a)
    local b = (melee_enemy ~= missile_enemy)
    check(TAG .. "N8b: the two enemies are distinct units", b)
    local c = (count_log(W, "reason: enemy in melee (targeting orc_boyz)") == 1)
    check(TAG .. "N8c: the melee arm's reason is the one logged [live log]", lg(TAG, c))
    note94(W, TAG); tally(W)
    return a and b and lg(TAG, c)
  end

  -- ==========================================================================
  -- N9. AMONG EQUALS PREFER THE CLOSEST: two in-melee enemies; the nearer one
  --     (distance 10 vs 40) is chosen.
  -- ==========================================================================
  local function world_n9(PATH, TAG)
    local W = make_world({ can_perform = true,
      units = { { name = "witch_hunter", uid = 9481, owns = { ACC }, melee = false, in_range = true,
                  dist_by_target = { [9482] = 40, [9483] = 10 } } },
      enemies = { { name = "far_orcs", uid = 9482, melee = true },
                  { name = "near_orcs", uid = 9483, melee = true } },
      cards = { { id = "9481", state = "active", vis = true } },
      bar = { { id = "b1", key = ACC } } })
    print("== " .. TAG .. "N9. ACCUSATION: among equals the CLOSEST enemy is chosen == ")
    if not boot94(W, PATH, TAG, 9481, "accusation", "N9") then return nil end
    polln(W, 1)
    local near_enemy = enemy_of(W, 9483)
    local far_enemy = enemy_of(W, 9482)
    local a = (#W.fires == 1 and fire_target_for(W, 9481) == near_enemy)
    check(TAG .. "N9a: the CLOSER in-melee enemy is chosen (not the far one)", a)
    local b = (near_enemy ~= far_enemy)
    check(TAG .. "N9b: the two enemies are distinct units", b)
    note94(W, TAG); tally(W)
    return a and b
  end

  -- run each world twice: live and annotated
  local WORLDS = { world_n1, world_n2, world_n3, world_n4, world_n5, world_n6, world_n7, world_n8, world_n9 }
  local results = {}
  for _, path in ipairs({ LIVE, ANN }) do
    local TAG = (path == LIVE) and "[live] " or "[ann]  "
    for _, wfn in ipairs(WORLDS) do
      results[#results + 1] = wfn(path, TAG)
    end
  end
  local n_ok = 0
  for _, r in ipairs(results) do if posv(r) then n_ok = n_ok + 1 end end
  print("== HARNESS 94 - N-worlds: " .. n_ok .. "/" .. #results .. " passed; fires " .. RED94.fires .. " ==")

  check("every ui tick ran clean across the HARNESS-94 worlds (" .. RED94.ui .. " failures)", RED94.ui == 0)

  if not RED_MODE then
    check("HEADLINE (harness 94): ACCUSATION now fires automatically through the FIRST ENEMY-TARGETED trigger "
      .. "`enemy_engaged_or_shot` - an enemy unit within the ability's conservative 75 m reach is a valid target "
      .. "when it is in melee OR under missile fire (prefer in-melee, then closest); the chosen enemy is the CAST "
      .. "TARGET (never the owner) and the cast uses the round-4-proven bench_fresh fresh-handle route (caster and "
      .. "target re-enumerated the same tick). Accusation's entry moves from melee_unwavering (481 -> 480) to the "
      .. "new trigger (0 -> 1); the table stays 579 entries / 605 keys. All " .. #results .. " worlds passed.",
      n_ok == #results)
  else
    check("RED CONTROL (harness 94): on the pre-edit snapshot (the shipped harness-93 build: no enemy evaluator, "
      .. "Accusation still on melee_unwavering = 481) the 0r section tokens fail and every FIRING N-world fires "
      .. "nothing - only the SILENT worlds pass (N3/N4 both files = 4) plus the ANNOTATED leg of the lapse world N5 "
      .. "(the unreadable-read world N6 fails on the snapshot too, its mock is never asked): " .. n_ok .. "/"
      .. #results .. " world results pass (want 5), fires "
      .. RED94.fires .. ", claims " .. RED94.claims, n_ok == 5)
  end
end
run_h94()
