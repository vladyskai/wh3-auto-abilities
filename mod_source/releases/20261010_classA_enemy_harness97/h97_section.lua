-- ============================================================================
-- HARNESS 97 - THE REST OF CLASS A (this round).
--   THE JOB: apply the PROVEN Accusation enemy-targeting mechanism to the other
--   97 Class-A entries derived from WH3_audit_report.md (98 total; Accusation
--   263 is already done). 88 ride the EXISTING `enemy_engaged_or_shot` trigger
--   (enemy-UNIT casts); 9 ride a NEW `enemy_ground_area` trigger (enemy-GROUND
--   area hexes) that casts through
--   perform_special_ability_ground(key, ENEMY_POSITION, 0, 0).
--   Every entry carries its own REAL target_intercept_range (range_real). ONE
--   named constant per real range (FOURTH.ENEMY_CAST_R<real>) holds the 70%
--   bound = floor(real * FOURTH.RANGE_FRACTION); FOURTH.ENEMY_CAST maps the
--   real range to it and ability.range_m is set at load. The offer test is the
--   per-ability constant ONLY (unit:unit_distance(enemy) <= bound) - NEVER the
--   engine's unit_in_range. The marker-prefixed log prints the REAL distance.
--   This harness proves, against the LIVE source and the ANNOTATED copy:
--     0u: the 12 named constants, the FOURTH.ENEMY_CAST map, the range_real
--         fields (98), the load-loop wiring, the picker, the ground evaluator/
--         helper/key-set, the moved trigger counts, the poll slots, and that
--         unit_in_range( is still GONE;
--     per-family worlds (12 real-range families): an enemy INSIDE the bound and
--         in melee FIRES AT THE ENEMY (unit form) or casts on the ENEMY's GROUND
--         (ground form); an enemy BEYOND the bound stays SILENT even though the
--         engine's own helper says in-range (THE REGRESSION GUARD);
--     plus: an enemy under missile fire FIRES; a lapse between pick and cast
--         SKIPS; the self-cast guard (target is NEVER the owner); the fresh-
--         handle guard (the caster is re-fetched the same tick).
--   RED CONTROL: with H97_LIVE / H97_ANN pointing at the pre-edit snapshot (the
--   shipped harness-96 build: all 97 still melee_unwavering self-cast, no
--   picker, no ground form) the 0u tokens fail and every INSIDE/missile/ground
--   world fires nothing; the BEYOND worlds pass by design (nothing fires).
-- ============================================================================
function run_h97()
  local live_src97 = read_file(LIVE)
  local ann_src97  = read_file(ANN)
  local RED97 = { fires = 0, claims = 0, ui = 0 }
  local function posv(v) return (v == true) or (type(v) == "number") end
  local function lg(tag, v) return (tag ~= "[live] ") or posv(v) end
  local function badd97(marker) return "zz_auto_badge_" .. marker end
  local function cp97(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function note97(W, TAG)
    RED97.ui = RED97.ui + (W.ui_failures or 0)
    if TAG == "[live] " then
      RED97.fires = RED97.fires + #W.fires
      RED97.claims = RED97.claims + count_log(W, "claim: ")
    end
  end
  local function boot97(W, PATH, TAG, uid, marker, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, badd97(marker)); ui(W)
    W.conflict = true
    return true
  end
  local function enemy_of97(W, uid)
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        local ok, id = pcall(function() return pr.unit:unique_ui_id() end)
        if ok and tostring(id) == tostring(uid) then return pr.unit end
      end
    end
    return nil
  end

  -- THE 12 REAL-RANGE FAMILIES: one representative ability apiece (unit form
  -- where the family has one, else the ground form).
  local FAM = {
    { real = 20,  bound = 14,  marker = "sadistic_snare", key = "wh3_dlc23_lord_abilities_sadistic_snare", ground = false },
    { real = 30,  bound = 21,  marker = "bitter_sting", key = "wh3_dlc27_qb_unit_abilities_bitter_sting", ground = false },
    { real = 35,  bound = 24,  marker = "sword_of_filth", key = "wh3_dlc25_weapon_abilities_sword_of_filth", ground = false },
    { real = 50,  bound = 35,  marker = "frost_shard_glaive", key = "wh3_main_weapon_abilities_frost_shard_glaive", ground = false },
    { real = 70,  bound = 49,  marker = "oil_flask", key = "wh2_dlc13_lord_abilities_oil_flask", ground = false },
    { real = 75,  bound = 52,  marker = "accusation", key = "wh_main_hero_abilities_accusation", ground = false },
    { real = 100, bound = 70,  marker = "blade_of_setep", key = "wh2_dlc09_weapon_abilities_blade_of_setep", ground = false },
    { real = 150, bound = 105, marker = "headhunt", key = "wh3_dlc26_character_abilities_headhunt", ground = false },
    { real = 180, bound = 126, marker = "mark_of_yin", key = "wh3_dlc24_unit_abilities_mark_of_yin", ground = false },
    { real = 200, bound = 140, marker = "acquiescence", key = "wh3_dlc27_spell_bound_acquiescence", ground = false },
    { real = 15,  bound = 10,  marker = "entangle", key = "wh2_dlc10_character_abilities_entangle", ground = true },
    { real = 500, bound = 350, marker = "tricksters_shard", key = "wh_main_item_abilities_tricksters_shard", ground = true },
  }

  -- --------------------------------------------------- 0u: tokens (both files)
  print("== HARNESS 97 - section 0u: the Class-A enemy batch tokens (BOTH files) ==")
  local CONSTS = { {"FOURTH.ENEMY_CAST_R15  = 10", "15", "10"}, {"FOURTH.ENEMY_CAST_R20  = 14", "20", "14"},
    {"FOURTH.ENEMY_CAST_R30  = 21", "30", "21"}, {"FOURTH.ENEMY_CAST_R35  = 24", "35", "24"},
    {"FOURTH.ENEMY_CAST_R50  = 35", "50", "35"}, {"FOURTH.ENEMY_CAST_R70  = 49", "70", "49"},
    {"FOURTH.ENEMY_CAST_R75  = 52", "75", "52"}, {"FOURTH.ENEMY_CAST_R100 = 70", "100", "70"},
    {"FOURTH.ENEMY_CAST_R150 = 105", "150", "105"}, {"FOURTH.ENEMY_CAST_R180 = 126", "180", "126"},
    {"FOURTH.ENEMY_CAST_R200 = 140", "200", "140"}, {"FOURTH.ENEMY_CAST_R500 = 350", "500", "350"} }
  for _, f in ipairs({ { name = "live", src = live_src97 }, { name = "ann", src = ann_src97 } }) do
    local nm, s = f.name, f.src
    local allc = true
    for i = 1, #CONSTS do
      if raw_find(s, CONSTS[i][1], 1, true) == nil then allc = false end
    end
    check("0u " .. nm .. ": all 12 named 70% enemy-cast constants are present with their values", allc)
    check("0u " .. nm .. ": the REAL-range -> bound map (FOURTH.ENEMY_CAST) exists",
      raw_find(s, "FOURTH.ENEMY_CAST = {", 1, true) ~= nil)
    check("0u " .. nm .. ": every Class-A entry carries its REAL range (range_real x98)",
      cp97(s, "\t\trange_real = ") == 98)
    check("0u " .. nm .. ": the load loop maps the real range to the named constant",
      raw_find(s, "ability.range_m = FOURTH.ENEMY_CAST[ability.range_real]", 1, true) ~= nil)
    check("0u " .. nm .. ": the shared enemy picker and the fresh-caster route exist",
      raw_find(s, "function FOURTH.eg_pick_enemy(unit, routing, ground)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.eg_fresh_caster_su(unit)", 1, true) ~= nil
      and raw_find(s, "FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)", 1, true) ~= nil
      and raw_find(s, "uc = FOURTH.eg_caster_su.uc", 1, true) ~= nil)
    check("0u " .. nm .. ": the per-ability bound is read from FOURTH.eg_range_m",
      raw_find(s, "local bound = FOURTH.eg_range_m", 1, true) ~= nil
      and raw_find(s, "return gap <= bound", 1, true) ~= nil)
    check("0u " .. nm .. ": the enemy-ground evaluator/helper/key-set exist and are wired",
      raw_find(s, "function FOURTH.evaluate_enemy_ground_area(unit, routing)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.enemy_ground_cast(uc, enemy, ability_key)", 1, true) ~= nil
      and raw_find(s, "enemy_ground_area = FOURTH.evaluate_enemy_ground_area,", 1, true) ~= nil
      and raw_find(s, "enemy_ground_keys = {", 1, true) ~= nil)
    check("0u " .. nm .. ": the 9 enemy-ground keys are registered",
      cp97(s, '["wh2_dlc09_item_abilities_amulet_of_phastah"] = true,') == 1
      and cp97(s, '["wh_dlc03_item_abilities_chalice_of_dark_rain"] = true,') == 1
      and cp97(s, '["wh2_dlc09_character_abilities_curse_of_khsar"] = true,') == 1
      and cp97(s, '["wh2_dlc10_character_abilities_entangle"] = true,') == 1
      and cp97(s, '["wh3_dlc25_character_abilities_get_em"] = true,') == 1
      and cp97(s, '["wh2_dlc13_lord_abilities_hunters_snare"] = true,') == 1
      and cp97(s, '["wh2_dlc13_lord_abilities_hunters_trap"] = true,') == 1
      and cp97(s, '["wh2_main_item_abilities_the_tricksters_pendant"] = true,') == 1
      and cp97(s, '["wh_main_item_abilities_tricksters_shard"] = true,') == 1)
    check("0u " .. nm .. ": the trigger counts moved (melee_unwavering 383, enemy_engaged_or_shot 89, enemy_ground_area 9)",
      cp97(s, 'trigger = "melee_unwavering"') == 383
      and cp97(s, 'trigger = "enemy_engaged_or_shot"') == 89
      and cp97(s, 'trigger = "enemy_ground_area"') == 9)
    check("0u " .. nm .. ": the table stays 579 entries / 579 badges",
      cp97(s, "\t{ marker = ") == 579 and cp97(s, 'badge = "') == 579)
    check("0u " .. nm .. ": the poll sets the current ability's bound + marker",
      raw_find(s, "FOURTH.eg_range_m = ability.range_m", 1, true) ~= nil
      and raw_find(s, "FOURTH.eg_marker = ability.marker", 1, true) ~= nil)
    check("0u " .. nm .. ": the engine's unit_in_range CALL is still GONE",
      raw_find(s, "unit_in_range(", 1, true) == nil)
    check("0u " .. nm .. ": the 70% rule is untouched",
      raw_find(s, "FOURTH.RANGE_FRACTION = 0.70", 1, true) ~= nil)
  end
  check("0u live: the picker's target-choice log is marker-prefixed and prints the REAL distance + bound",
    raw_find(live_src97, 'log("  " .. marker .. " target: \'"', 1, true) ~= nil
    and raw_find(live_src97, '.. "m bound=" .. tostring(bound) .. "m")', 1, true) ~= nil)
  check("0u live: the pre-cast re-check is marker-prefixed and prints the REAL distance + bound",
    raw_find(live_src97, 'log("  " .. eg_marker_now .. " pre-cast re-check:', 1, true) ~= nil
    and raw_find(live_src97, '.. "m bound=" .. tostring(eg_bound_now) .. "m) - firing")', 1, true) ~= nil)
  check("0u live: the enemy-ground cast branch is present and logged",
    raw_find(live_src97, 'enemy-ground cast      : perform_special_ability_ground', 1, true) ~= nil
    and raw_find(live_src97, "FOURTH.enemy_ground_cast(uc, FOURTH.eg_enemy, ability_key)", 1, true) ~= nil)
  check("0u live: the distinct unit/ground reason strings are present",
    raw_find(live_src97, 'reason = "enemy in melee (targeting " .. etype .. ")"', 1, true) ~= nil
    and raw_find(live_src97, 'reason = "enemy-ground area in melee (targeting " .. etype .. ")"', 1, true) ~= nil)
  check("0u ann: the reading copy stays log-free and find-free",
    raw_find(ann_src97, "log(", 1, true) == nil and raw_find(ann_src97, "string.find", 1, true) == nil)

  -- ==========================================================================
  -- THE PER-FAMILY WORLDS: INSIDE (fires at the enemy) / BEYOND (silent, the
  -- regression guard: the engine's own helper says in-range).
  -- ==========================================================================
  local function world_family(FAM_, PATH, TAG, mode)
    local mid = 9700 + (FAM_.real % 90) + (mode == "inside" and 0 or 40)
    local uid, euid = mid, mid + 200
    local inside = (mode == "inside")
    local dist = inside and (FAM_.bound - 5) or (FAM_.bound + 25)
    local W = make_world({ can_perform = true,
      units = { { name = "caster", uid = uid, owns = { FAM_.key }, melee = false,
                  in_range = true, dist = dist } },
      enemies = { { name = "orc_boyz", uid = euid, melee = true } },
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = { { id = "b1", key = FAM_.key } } })
    local wname = string.format("%s r%d/%d b%d", (inside and "INSIDE" or "BEYOND"), FAM_.real, FAM_.real, FAM_.bound)
    print("== " .. TAG .. "FAM " .. wname .. " (" .. FAM_.marker .. ", " .. (FAM_.ground and "ground" or "unit") .. ", dist " .. dist .. " m) ==")
    if not boot97(W, PATH, TAG, uid, FAM_.marker, "FAM " .. wname .. " ") then return nil end
    polln(W, 3)
    local enemy = enemy_of97(W, euid)
    if FAM_.ground then
      if inside then
        local a = (#W.ground_fires == 1 and W.ground_fires[1].key == FAM_.key)
        check(TAG .. "FAM " .. wname .. ": the enemy-ground cast fired the key (" .. #W.ground_fires .. " ground fires)", a)
        local b = (W.ground_fires[1] ~= nil and W.ground_fires[1].pos ~= nil
          and W.ground_fires[1].pos.marker == ("pos:" .. tostring(euid)))
        check(TAG .. "FAM " .. wname .. ": the area was placed on the ENEMY's ground (pos marker " .. tostring(W.ground_fires[1] and W.ground_fires[1].pos and W.ground_fires[1].pos.marker) .. ")", b)
        local c = (W.fires ~= nil and #W.fires == 0)
        check(TAG .. "FAM " .. wname .. ": the unit form was NOT used for the enemy-ground hex", c)
        note97(W, TAG); tally(W)
        return a and b and c
      else
        local a = (#W.ground_fires == 0 and #W.fires == 0)
        check(TAG .. "FAM " .. wname .. ": beyond the bound stays SILENT though the engine said in-range (ground fires " .. #W.ground_fires .. ", unit fires " .. #W.fires .. ")", a)
        note97(W, TAG); tally(W)
        return a
      end
    else
      if inside then
        local a = (#W.fires == 1 and W.fires[1].key == FAM_.key and fire_target_for(W, uid) == enemy)
        check(TAG .. "FAM " .. wname .. ": the in-bound in-melee enemy is fired at (" .. fire_detail(W) .. ")", a)
        local b = (fire_target_for(W, uid) ~= unit_of(W, uid))
        check(TAG .. "FAM " .. wname .. ": the cast target is NOT the owner (self-cast guard)", b)
        note97(W, TAG); tally(W)
        return a and b
      else
        local a = (#W.fires == 0)
        check(TAG .. "FAM " .. wname .. ": beyond the bound stays SILENT though the engine said in-range (" .. fire_detail(W) .. ")", a)
        note97(W, TAG); tally(W)
        return a
      end
    end
  end

  local results = {}
  for _, path in ipairs({ LIVE, ANN }) do
    local TAG = (path == LIVE) and "[live] " or "[ann]  "
    for i = 1, #FAM do
      results[#results + 1] = world_family(FAM[i], path, TAG, "inside")
      results[#results + 1] = world_family(FAM[i], path, TAG, "beyond")
    end
  end

  -- ==========================================================================
  -- MISSILE: an enemy under missile fire (not in melee) inside the bound FIRES.
  -- ==========================================================================
  local function world_missile(PATH, TAG)
    local KEY = "wh2_dlc09_weapon_abilities_blade_of_setep"  -- bound 70
    local W = make_world({ can_perform = true,
      units = { { name = "caster", uid = 9801, owns = { KEY }, melee = false, dist = 60 } },
      enemies = { { name = "goblin_archers", uid = 9802, melee = false, missile = true } },
      cards = { { id = "9801", state = "active", vis = true } },
      bar = { { id = "b1", key = KEY } } })
    print("== " .. TAG .. "MISSILE: an enemy under missile fire inside the bound FIRES ==")
    if not boot97(W, PATH, TAG, 9801, "blade_of_setep", "MISSILE ") then return nil end
    polln(W, 1)
    local enemy = enemy_of97(W, 9802)
    local a = (#W.fires == 1 and fire_target_for(W, 9801) == enemy)
    check(TAG .. "MISSILE: the under-fire enemy at 60 m (bound 70) is fired at (" .. fire_detail(W) .. ")", a)
    note97(W, TAG); tally(W)
    return a
  end

  -- ==========================================================================
  -- LAPSE: the condition lapses between the pick and the cast -> SKIP.
  -- ==========================================================================
  local function world_lapse(PATH, TAG)
    local KEY = "wh2_dlc09_weapon_abilities_blade_of_setep"
    local W = make_world({ can_perform = true,
      units = { { name = "caster", uid = 9811, owns = { KEY }, melee = false, dist = 60 } },
      enemies = { { name = "orc_boyz", uid = 9812, melee_seq = { true, false } } },
      cards = { { id = "9811", state = "active", vis = true } },
      bar = { { id = "b1", key = KEY } } })
    print("== " .. TAG .. "LAPSE: the chosen enemy lapses before the cast -> SKIPPED ==")
    if not boot97(W, PATH, TAG, 9811, "blade_of_setep", "LAPSE ") then return nil end
    polln(W, 1)
    local a = (#W.fires == 0)
    check(TAG .. "LAPSE: the lapsed target is NOT fired for (" .. fire_detail(W) .. ")", a)
    local b = (count_log(W, "SKIPPED: the chosen enemy lapsed before the cast") == 1)
    check(TAG .. "LAPSE: the pre-cast lapse skip is reported once [live log]", lg(TAG, b))
    note97(W, TAG); tally(W)
    return a and lg(TAG, b)
  end

  -- ==========================================================================
  -- FRESH-HANDLE GUARD: the caster is re-fetched the SAME tick (a controller
  -- held from an earlier poll silently no-ops - this is the proof it does not).
  -- ==========================================================================
  local function world_fresh(PATH, TAG)
    local KEY = "wh3_dlc26_character_abilities_headhunt"  -- bound 105
    local W = make_world({ can_perform = true,
      units = { { name = "caster", uid = 9821, owns = { KEY }, melee = false, dist = 90 } },
      enemies = { { name = "orc_boyz", uid = 9822, melee = true } },
      cards = { { id = "9821", state = "active", vis = true } },
      bar = { { id = "b1", key = KEY } } })
    print("== " .. TAG .. "FRESH: the caster is re-fetched FRESH on the firing tick ==")
    if not boot97(W, PATH, TAG, 9821, "headhunt", "FRESH ") then return nil end
    local friendly0 = W.friendly_calls or 0
    polln(W, 1)
    local a = (#W.fires == 1)
    check(TAG .. "FRESH: the in-bound in-melee enemy is fired at (" .. fire_detail(W) .. ")", a)
    local b = ((W.friendly_calls or 0) > friendly0)
    check(TAG .. "FRESH: the CASTER was re-fetched on the firing tick (fresh/not-stale handle)", b)
    note97(W, TAG); tally(W)
    return a and b
  end

  results[#results + 1] = world_missile(LIVE, "[live] "); results[#results + 1] = world_missile(ANN, "[ann]  ")
  results[#results + 1] = world_lapse(LIVE, "[live] ");   results[#results + 1] = world_lapse(ANN, "[ann]  ")
  results[#results + 1] = world_fresh(LIVE, "[live] ");   results[#results + 1] = world_fresh(ANN, "[ann]  ")

  local n_ok = 0
  for _, r in ipairs(results) do if posv(r) then n_ok = n_ok + 1 end end
  print("== HARNESS 97 - Class-A family/guard worlds: " .. n_ok .. "/" .. #results .. " passed; fires " .. RED97.fires .. " ==")

  check("every ui tick ran clean across the HARNESS-97 worlds (" .. RED97.ui .. " failures)", RED97.ui == 0)

  if not RED_MODE then
    check("HEADLINE (harness 97): THE REST OF CLASS A ships on the proven Accusation enemy-targeting mechanism - 97 of the "
      .. "98 enemy-aimed entries (Accusation 263 already done) now fire at the ENEMY: 88 ride enemy_engaged_or_shot "
      .. "and 9 ride the new enemy_ground_area (perform_special_ability_ground on the chosen ENEMY's ground). Each entry "
      .. "carries its own REAL target_intercept_range -> ONE named 70% constant per real range (12 constants, "
      .. "floor(real*0.70)); the offer test is unit:unit_distance(enemy) <= that constant ONLY (never the engine's "
      .. "unit_in_range). The marker-prefixed log prints the REAL distance; the fresh-handle route, the pre-cast "
      .. "re-check and the hold are the Accusation ones. All " .. #results .. " worlds passed.", n_ok == #results)
  else
    check("RED CONTROL (harness 97): on the pre-edit snapshot (the shipped harness-96 build: all 97 still "
      .. "melee_unwavering self-cast, no picker, no ground form) the section-0u tokens fail and every non-accusation "
      .. "INSIDE/missile/ground world fires nothing; the 24 BEYOND worlds pass by design and the ACCUSATION family "
      .. "passes (it is already enemy-targeted on the snapshot). " .. n_ok .. "/" .. #results
      .. " world results pass (want 27), fires " .. RED97.fires .. ", claims " .. RED97.claims, n_ok == 27)
  end
end
run_h97()
