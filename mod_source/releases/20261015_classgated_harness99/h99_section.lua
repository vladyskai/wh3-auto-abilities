-- ============================================================================
-- HARNESS 99 - THE TARGET-CLASS-GATED CLASS-B ENTRIES (the 15 audit rows that
-- carried NEEDS A RULING, now ruled). Each of the class-gated entries must cast
-- on an ALLY OF THE REQUIRED CLASS - NEVER the owner - and the Rampage pair, the
-- two mid-flight entries and Merciw's Monstrous Regiment (unbounded) ride the
-- SAME picker. This section proves, against the LIVE source and the ANNOTATED
-- copy:
--   0w: the 200 m ally constant, the SEVEN derived class-key lists (with their
--       derived SIZES), the class reader, the class-gate helpers, the infinite
--       bound text, the ten new evaluators + their map/TIP wiring, the moved
--       trigger counts, the winds (max-hp) family and the moved entry counts;
--   worlds: for EVERY class, a QUALIFYING ally fires and the cast TARGETS THAT
--       ALLY (never the owner); a NON-qualifying ally in range stays SILENT; a
--       qualifying ally BEYOND the 70% bound stays SILENT even though the engine
--       helper reports in-range; the Rampage pair fires on its family trigger;
--       Merciw's fires with NO bound (an ally 5 km away); Grut's Sickle picks the
--       ally with the HIGHEST hit points; the self-cast guard holds throughout.
--   RED CONTROL: with H99_LIVE / H99_ANN pointing at the pre-edit snapshot every
--       FIRE world fails (the snapshot self-casts, never on an ally) while the
--       SILENT worlds pass by design.
-- ============================================================================
function run_h99()
  local live_src99 = read_file(LIVE)
  local ann_src99  = read_file(ANN)
  local RED99 = { fires = 0, claims = 0, ui = 0 }
  -- the RED-control expected pass count (verified by the red run below).
  local WANT_RED_99 = 26
  local function posv(v) return (v == true) or (type(v) == "number") end
  local function lg(tag, v) return (tag ~= "[live] ") or posv(v) end
  local function cp99(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  -- count the "name = { ... }," table size in a source string
  local function list_size(s, name)
    local i = raw_find(s, name .. " = {", 1, true)
    if i == nil then return -1 end
    local j = raw_find(s, "},", i, true)
    if j == nil then return -1 end
    return cp99(s:sub(i, j), "] = true,")
  end
  local function note99(W, TAG)
    RED99.ui = RED99.ui + (W.ui_failures or 0)
    if TAG == "[live] " then
      RED99.fires = RED99.fires + #W.fires
      RED99.claims = RED99.claims + count_log(W, "claim: ")
    end
  end
  local function boot99(W, PATH, TAG, uid, marker, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. marker); ui(W)
    W.conflict = true
    return true
  end
  local function ally_of99(W, uid)
    for i = 1, #(W.live_entries or {}) do
      local pr = W.live_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        local ok, id = pcall(function() return pr.unit:unique_ui_id() end)
        if ok and tostring(id) == tostring(uid) then return pr.unit end
      end
    end
    return nil
  end

  -- ------------------------------------------------------------------ 0w
  print("== HARNESS 99 - section 0w: the target-class-gated tokens (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src99 }, { name = "ann", src = ann_src99 } }) do
    local nm, s = f.name, f.src
    check("0w " .. nm .. ": the 200 m ally constant exists (FOURTH.ALLY_CAST_R200 = 140) + its map entry",
      raw_find(s, "FOURTH.ALLY_CAST_R200 = 140", 1, true) ~= nil
      and raw_find(s, "\t[200] = FOURTH.ALLY_CAST_R200,", 1, true) ~= nil)
    check("0w " .. nm .. ": the SEVEN derived class-key lists exist",
      raw_find(s, "FOURTH.class_keys = {", 1, true) ~= nil)
    local SIZES = { { "beast", 55 }, { "monster", 235 }, { "warmachine", 68 }, { "construct", 29 },
                    { "hellforged", 13 }, { "missile", 493 }, { "overseer", 918 } }
    for i = 1, #SIZES do
      local got = list_size(s, SIZES[i][1])
      check("0w " .. nm .. ": the " .. SIZES[i][1] .. " list is DERIVED with " .. SIZES[i][2]
        .. " land_units keys (" .. got .. ")", got == SIZES[i][2])
    end
    check("0w " .. nm .. ": the class reader + gate helpers exist",
      raw_find(s, "function FOURTH.class_member(unit, name)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.ab_filter_ok(unit)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.morale_broken(unit)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.ab_bound_text()", 1, true) ~= nil)
    check("0w " .. nm .. ": the infinite bound is honoured and its log text is exact",
      raw_find(s, "if FOURTH.ab_infinite then return true end", 1, true) ~= nil
      and raw_find(s, "none (infinite range per wiki)", 1, true) ~= nil)
    check("0w " .. nm .. ": the winds family reads ABSOLUTE hit points (HealthValue)",
      raw_find(s, 'family == "winds"', 1, true) ~= nil
      and raw_find(s, 'FOURTH.context_value(other, "HealthValue")', 1, true) ~= nil)
    local FAM = { "overseer", "beast", "broken", "missile", "warmachine_heal",
                  "hellforged_heal", "monster_heal", "construct_heal", "infinite_buff", "winds" }
    local allw = true
    for i = 1, #FAM do
      if raw_find(s, "ally_" .. FAM[i] .. " = FOURTH.evaluate_ally_" .. FAM[i] .. ",", 1, true) == nil then allw = false end
      if raw_find(s, "function FOURTH.evaluate_ally_" .. FAM[i] .. "(unit, routing)", 1, true) == nil then allw = false end
    end
    check("0w " .. nm .. ": the ten new evaluators exist AND are wired into the map", allw)
    check("0w " .. nm .. ": the trigger counts moved (melee_unwavering 363, charge_or_melee 25, ushoran_health 34, melee_health75 1)",
      cp99(s, 'trigger = "melee_unwavering"') == 363
      and cp99(s, 'trigger = "charge_or_melee"') == 25
      and cp99(s, 'trigger = "ushoran_health"') == 34
      and cp99(s, 'trigger = "melee_health75"') == 1)
    check("0w " .. nm .. ": the ally trigger counts (buff 14 / heal 3 / heal_melee 1 / wavering 2 + the 10 new)",
      cp99(s, 'trigger = "ally_melee_buff"') == 14
      and cp99(s, 'trigger = "ally_heal"') == 3
      and cp99(s, 'trigger = "ally_heal_melee"') == 1
      and cp99(s, 'trigger = "ally_wavering"') == 2
      and cp99(s, 'trigger = "ally_overseer"') == 1
      and cp99(s, 'trigger = "ally_beast"') == 1
      and cp99(s, 'trigger = "ally_broken"') == 1
      and cp99(s, 'trigger = "ally_missile"') == 3
      and cp99(s, 'trigger = "ally_warmachine_heal"') == 1
      and cp99(s, 'trigger = "ally_hellforged_heal"') == 1
      and cp99(s, 'trigger = "ally_monster_heal"') == 1
      and cp99(s, 'trigger = "ally_construct_heal"') == 1
      and cp99(s, 'trigger = "ally_infinite_buff"') == 1
      and cp99(s, 'trigger = "ally_winds"') == 1)
    check("0w " .. nm .. ": the table stays 579 entries / 579 badges and the 4 old ally fields are joined by 14 more",
      cp99(s, "\t{ marker = ") == 579 and cp99(s, 'badge = "') == 579
      and cp99(s, "\t\tally_range_real = ") == 32)
    check("0w " .. nm .. ": the 70% rule is untouched and the engine unit_in_range CALL is still GONE",
      raw_find(s, "FOURTH.RANGE_FRACTION = 0.70", 1, true) ~= nil
      and raw_find(s, "unit_in_range(", 1, true) == nil)
  end
  check("0w live: the picker logs the class gate, the REAL distance and the bound text",
    raw_find(live_src99, " is the chosen ally (", 1, true) ~= nil
    and raw_find(live_src99, '.. "m bound=" .. FOURTH.ab_bound_text())', 1, true) ~= nil
    and raw_find(live_src99, ", gate=", 1, true) ~= nil)
  check("0w live: the pre-cast re-check logs the REAL distance + bound text",
    raw_find(live_src99, " pre-cast re-check: the chosen ally is still valid (", 1, true) ~= nil
    and raw_find(live_src99, "SKIPPED: the chosen ally lapsed before the cast", 1, true) ~= nil)
  check("0w ann: the reading copy stays log-free and find-free",
    raw_find(ann_src99, "log(", 1, true) == nil and raw_find(ann_src99, "string.find", 1, true) == nil)

  -- -------------------------------------------------------------- worlds
  local BEAST  = "wh2_dlc09_tmb_mon_dire_wolves"
  local MONST  = "wh2_dlc09_tmb_mon_heirotitan_0"
  local WARM   = "wh2_dlc11_cst_art_carronade"
  local CONS   = "wh2_dlc09_tmb_cav_necropolis_knights_0"
  local HELL   = "wh3_dlc23_chd_mon_kdaai_destroyer"
  local MISS   = "wh2_dlc09_tmb_cav_skeleton_horsemen_archers_0"
  local PLAIN  = "wh2_dlc09_tmb_inf_skeleton_warriors_0"
  local PLAIN2 = "wh2_dlc09_tmb_inf_skeleton_warriors_1"
  local CMDR   = "wh2_dlc09_tmb_cha_arkhan_0"
  local BIG    = "wh2_dlc09_tmb_mon_ushabti_0"
  local K = {
    whip = "wh2_dlc14_lord_abilities_whiplash", over = "wh3_dlc29_hero_active_overseer_of_the_unseen",
    iron = "wh3_dlc27_character_abilities_iron_hand_captain",
    mark = "wh3_main_lord_abilities_inspired_marksmanship_i",
    maka = "wh3_dlc25_weapon_abilities_makaissons_persuader", refo = "wh3_dlc23_character_abilities_reforge",
    remo = "wh2_dlc16_lord_abilities_remouldered", rest = "wh2_dlc09_character_abilities_restore",
    fury = "wh2_main_unit_abilities_fury_of_khaine", verm = "wh3_dlc29_lord_abilities_verminous_fury",
    merc = "wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment",
    slez = "wh3_dlc27_character_abilities_slezuzus_voice", grut = "wh3_main_item_abilities_gruts_sickle",
  }
  local function world_cg(PATH, TAG, o)
    local units = { { name = o.cname or "caster", uid = o.cuid, owns = { o.key },
                      melee = o.cmelee, wavering = o.cwavering, health_percent = o.chp } }
    local cards = { { id = tostring(o.cuid), state = "active", vis = true } }
    local allies = o.allies or {}
    for i = 1, #allies do
      local a = allies[i]
      units[#units + 1] = { name = a.name or "ally", uid = a.uid, owns = {}, melee = a.melee,
                            wavering = a.wavering, health_percent = a.hp, ctx = a.ctx,
                            dist = a.dist, dist_seq = a.dist_seq,
                            in_range = (a.in_range ~= false) }
      cards[#cards + 1] = { id = tostring(a.uid), state = "active", vis = true }
    end
    local W = make_world({ can_perform = true, units = units, cards = cards, bar = { { id = "b1", key = o.key } } })
    print("== " .. TAG .. o.wname .. " ==")
    if not boot99(W, PATH, TAG, o.cuid, o.marker, o.wname) then return nil end
    polln(W, 1)
    if o.expect == "fire_ally" then
      local owner = unit_of(W, o.cuid)
      local want = ally_of99(W, o.target)
      local a = (#W.fires == 1 and W.fires[1].key == o.key and want ~= nil and fire_target_for(W, o.cuid) == want)
      check(TAG .. o.wname .. ": fires ONCE and the cast target IS THE QUALIFYING ALLY (" .. fire_detail(W) .. ")", a)
      local b = (#W.fires == 1 and owner ~= nil and fire_target_for(W, o.cuid) ~= owner)
      check(TAG .. o.wname .. ": the cast target is NOT the owner (self-cast guard)", b)
      note99(W, TAG); tally(W)
      return a and b
    else
      local a = (#W.fires == 0 and #W.ground_fires == 0)
      check(TAG .. o.wname .. ": stays SILENT (" .. fire_detail(W) .. ")", a)
      note99(W, TAG); tally(W)
      return a
    end
  end

  local WB = {}
  local function add(fn) WB[#WB + 1] = fn end

  add(function(P, T) return world_cg(P, T, { wname = "CG1: Whiplash! CASTS ON A BEAST ally in range",
    key = K.whip, marker = "whiplash", cuid = 9701, allies = { { name = BEAST, uid = 9702, dist = 30 } },
    expect = "fire_ally", target = 9702 }) end)
  add(function(P, T) return world_cg(P, T, { wname = "CG2: Whiplash! stays SILENT on a NON-beast ally in range",
    key = K.whip, marker = "whiplash", cuid = 9703, allies = { { name = PLAIN, uid = 9704, dist = 30 } },
    expect = "silent" }) end)
  add(function(P, T) return world_cg(P, T, { wname = "CG3: Whiplash!'s beast ally BEYOND the 70 m bound stays SILENT though the engine said in-range",
    key = K.whip, marker = "whiplash", cuid = 9705, allies = { { name = BEAST, uid = 9706, dist = 90, in_range = true } },
    expect = "silent" }) end)
  add(function(P, T) return world_cg(P, T, { wname = "CG4: Overseer of the Unseen CASTS ON A NON-COMMANDER NON-LARGE ally",
    key = K.over, marker = "overseer_of_the_unseen", cuid = 9707, allies = { { name = PLAIN, uid = 9708, dist = 30 } },
    expect = "fire_ally", target = 9708 }) end)
  add(function(P, T) return world_cg(P, T, { wname = "CG5: Overseer stays SILENT on a COMMANDER-CLASS ally",
    key = K.over, marker = "overseer_of_the_unseen", cuid = 9709, allies = { { name = CMDR, uid = 9710, dist = 30 } },
    expect = "silent" }) end)
  add(function(P, T) return world_cg(P, T, { wname = "CG6: Overseer stays SILENT on a LARGE ally",
    key = K.over, marker = "overseer_of_the_unseen", cuid = 9711, allies = { { name = BIG, uid = 9712, dist = 30 } },
    expect = "silent" }) end)
  add(function(P, T) return world_cg(P, T, { wname = "CG7: Iron-Handed Captain CASTS ON A BROKEN-MORALE ally",
    key = K.iron, marker = "iron_hand_captain", cuid = 9713,
    allies = { { name = PLAIN, uid = 9714, dist = 30, ctx = { MoraleState = "broken" } } },
    expect = "fire_ally", target = 9714 }) end)
  add(function(P, T) return world_cg(P, T, { wname = "CG8: Iron-Handed Captain stays SILENT on an ally that is only WAVERING",
    key = K.iron, marker = "iron_hand_captain", cuid = 9715,
    allies = { { name = PLAIN, uid = 9716, dist = 30, ctx = { MoraleState = "wavering" } } },
    expect = "silent" }) end)
  add(function(P, T) return world_cg(P, T, { wname = "CG9: Inspired Marksmanship CASTS ON A MISSILE-CAPABLE ally",
    key = K.mark, marker = "inspired_marksmanship_i", cuid = 9717, allies = { { name = MISS, uid = 9718, dist = 30 } },
    expect = "fire_ally", target = 9718 }) end)
  add(function(P, T) return world_cg(P, T, { wname = "CG10: Inspired Marksmanship stays SILENT on a non-missile ally",
    key = K.mark, marker = "inspired_marksmanship_i", cuid = 9719, allies = { { name = PLAIN, uid = 9720, dist = 30 } },
    expect = "silent" }) end)
  add(function(P, T) return world_cg(P, T, { wname = "CG11: Makaisson's Persuader CASTS ON A WAR MACHINE ally",
    key = K.maka, marker = "makaissons_persuader", cuid = 9721, allies = { { name = WARM, uid = 9722, dist = 30, hp = 40 } },
    expect = "fire_ally", target = 9722 }) end)
  add(function(P, T) return world_cg(P, T, { wname = "CG12: Makaisson's Persuader stays SILENT on a non-war-machine ally",
    key = K.maka, marker = "makaissons_persuader", cuid = 9723, allies = { { name = PLAIN, uid = 9724, dist = 30, hp = 40 } },
    expect = "silent" }) end)
  add(function(P, T) return world_cg(P, T, { wname = "CG13: Reforge CASTS ON A HELL-FORGED ally",
    key = K.refo, marker = "reforge", cuid = 9725, allies = { { name = HELL, uid = 9726, dist = 30, hp = 40 } },
    expect = "fire_ally", target = 9726 }) end)
  add(function(P, T) return world_cg(P, T, { wname = "CG14: Reforge stays SILENT on a non-Hell-Forged ally",
    key = K.refo, marker = "reforge", cuid = 9727, allies = { { name = PLAIN, uid = 9728, dist = 30, hp = 40 } },
    expect = "silent" }) end)
  add(function(P, T) return world_cg(P, T, { wname = "CG15: Remouldered CASTS ON A MONSTER ally",
    key = K.remo, marker = "remouldered", cuid = 9729, allies = { { name = MONST, uid = 9730, dist = 30, hp = 40 } },
    expect = "fire_ally", target = 9730 }) end)
  add(function(P, T) return world_cg(P, T, { wname = "CG16: Remouldered stays SILENT on a non-monster ally",
    key = K.remo, marker = "remouldered", cuid = 9731, allies = { { name = PLAIN, uid = 9732, dist = 30, hp = 40 } },
    expect = "silent" }) end)
  add(function(P, T) return world_cg(P, T, { wname = "CG17: Remouldered's monster ally BEYOND the 70 m bound stays SILENT though the engine said in-range",
    key = K.remo, marker = "remouldered", cuid = 9733, allies = { { name = MONST, uid = 9734, dist = 90, hp = 40, in_range = true } },
    expect = "silent" }) end)
  add(function(P, T) return world_cg(P, T, { wname = "CG18: Restore CASTS ON A CONSTRUCT ally",
    key = K.rest, marker = "restore", cuid = 9735, allies = { { name = CONS, uid = 9736, dist = 30, hp = 40 } },
    expect = "fire_ally", target = 9736 }) end)
  add(function(P, T) return world_cg(P, T, { wname = "CG19: Restore stays SILENT on a non-construct ally",
    key = K.rest, marker = "restore", cuid = 9737, allies = { { name = PLAIN, uid = 9738, dist = 30, hp = 40 } },
    expect = "silent" }) end)
  add(function(P, T) return world_cg(P, T, { wname = "RM1: Fury of Khaine (Rampage) CASTS ON AN ALLY in melee",
    key = K.fury, marker = "fury_of_khaine", cuid = 9739, cmelee = true,
    allies = { { name = PLAIN, uid = 9740, dist = 20 } }, expect = "fire_ally", target = 9740 }) end)
  add(function(P, T) return world_cg(P, T, { wname = "RM2: Verminous Fury (Rampage) CASTS ON AN ALLY in melee",
    key = K.verm, marker = "verminous_fury", cuid = 9741, cmelee = true,
    allies = { { name = PLAIN, uid = 9742, dist = 60 } }, expect = "fire_ally", target = 9742 }) end)
  add(function(P, T) return world_cg(P, T, { wname = "RM3: Verminous Fury's ally BEYOND the 140 m bound stays SILENT",
    key = K.verm, marker = "verminous_fury", cuid = 9743, cmelee = true,
    allies = { { name = PLAIN, uid = 9744, dist = 160, in_range = true } }, expect = "silent" }) end)
  add(function(P, T) return world_cg(P, T, { wname = "MC1: Merciw's Monstrous Regiment CASTS ON AN ALLY 5 km away (NO bound)",
    key = K.merc, marker = "merciws_monstrous_regiment", cuid = 9745,
    allies = { { name = PLAIN, uid = 9746, dist = 5000 } }, expect = "fire_ally", target = 9746 }) end)
  add(function(P, T) return world_cg(P, T, { wname = "MC2: Merciw's stays SILENT with NO ally at all",
    key = K.merc, marker = "merciws_monstrous_regiment", cuid = 9747, expect = "silent" }) end)
  add(function(P, T) return world_cg(P, T, { wname = "DW1: Daemonic Whispers CASTS ON AN ALLY in range",
    key = K.slez, marker = "slezuzus_voice", cuid = 9748, cmelee = true,
    allies = { { name = PLAIN, uid = 9749, dist = 100 } }, expect = "fire_ally", target = 9749 }) end)
  add(function(P, T) return world_cg(P, T, { wname = "GS1: Grut's Sickle picks the ally with the HIGHEST hit points",
    key = K.grut, marker = "gruts_sickle", cuid = 9750,
    allies = { { name = PLAIN, uid = 9751, dist = 30, ctx = { HealthValue = 500 } },
               { name = PLAIN2, uid = 9752, dist = 40, ctx = { HealthValue = 2000 } } },
    expect = "fire_ally", target = 9752 }) end)
  add(function(P, T) return world_cg(P, T, { wname = "GS2: Grut's Sickle CASTS ON A LONE ally",
    key = K.grut, marker = "gruts_sickle", cuid = 9753,
    allies = { { name = PLAIN, uid = 9754, dist = 30, ctx = { HealthValue = 100 } } },
    expect = "fire_ally", target = 9754 }) end)
  add(function(P, T) return world_cg(P, T, { wname = "GS3: Grut's Sickle stays SILENT with NO ally at all",
    key = K.grut, marker = "gruts_sickle", cuid = 9755, expect = "silent" }) end)

  local results = {}
  for _, path in ipairs({ LIVE, ANN }) do
    local TAG = (path == LIVE) and "[live] " or "[ann]  "
    for i = 1, #WB do results[#results + 1] = WB[i](path, TAG) end
  end

  local n_ok = 0
  for _, r in ipairs(results) do if posv(r) then n_ok = n_ok + 1 end end
  print("== HARNESS 99 - target-class-gated worlds: " .. n_ok .. "/" .. #results .. " passed; fires " .. RED99.fires .. " ==")

  check("every ui tick ran clean across the HARNESS-99 worlds (" .. RED99.ui .. " failures)", RED99.ui == 0)

  if not RED_MODE then
    check("HEADLINE (harness 99): the 15 NEEDS-RULING entries ship as ALLY-TARGETED casts on the mod's own "
      .. "ally picker. TEN are TARGET-CLASS-gated on lists DERIVED from the game's own data (beast 55 / monster 235 / "
      .. "warmachine 68 / construct 29 / hellforged 13 / missile 493 / overseer 918 keys; main_units.caste, "
      .. "unit_attributes, land_units.primary_missile_weapon and land_units.class+battle_entities.size); the Rampage "
      .. "pair and Daemonic Whispers ride the plain in-melee buff family; Merciw's Monstrous Regiment has NO distance "
      .. "bound (infinite range per the wiki); Grut's Sickle picks the ally with the MOST hit points. The offer test is "
      .. "the per-ability 70% constant ONLY (never unit_in_range), the cast target is ALWAYS the qualifying ally and "
      .. "the self-cast guard holds. All " .. #results .. " worlds passed.", n_ok == #results)
  else
    check("RED CONTROL (harness 99): on the pre-edit snapshot every FIRE world fails (the snapshot self-casts or stays "
      .. "silent - never on an ally) while the SILENT worlds pass by design. "
      .. n_ok .. "/" .. #results .. " world results pass (want " .. WANT_RED_99 .. "), fires " .. RED99.fires
      .. ", claims " .. RED99.claims, n_ok == WANT_RED_99)
  end
end
run_h99()
