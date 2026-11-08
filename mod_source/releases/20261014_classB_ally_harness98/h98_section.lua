-- ============================================================================
-- HARNESS 98 - CLASS B (ally-targeted effects cast on self).
--   THE JOB: implement the audit's Class B (34 entries) on the mod's OWN ally
--   picker (the blood_sacrifice / eat_da_runts shape) with the Class-A round's
--   FRESH-HANDLE discipline. 17 entries move to one of FOUR new ally families;
--   1 (Stay Here, I'll Get Help!) had its ally pick already and only gains the
--   CAST TARGET + its own 70% bound; 1 is an ARMY-BAR ability (Meat Feast,
--   standing rule 10) and is SKIPPED; 15 need a user ruling and are unchanged.
--   Every implemented entry carries its own REAL target_intercept_range
--   (ally_range_real) -> ONE named 70% constant per real range (FOURTH.ALLY_CAST).
--   The offer test is the per-ability constant ONLY (unit:unit_distance(ally)) -
--   NEVER the engine's unit_in_range. The cast goes through the FRESH caster
--   controller AND the FRESH ally unit, re-enumerated the SAME tick.
--   This harness proves, against the LIVE source and the ANNOTATED copy:
--     0v: the 5 named constants, the FOURTH.ALLY_CAST map, the 18 ally_range_real
--         fields, the load-loop wiring, the fresh-friend helper, the shared ally
--         picker, the four family evaluators, the fresh-handle cast branch, the
--         poll slots, the moved trigger counts, and that unit_in_range( is GONE;
--     worlds: an ally in range qualifies and the cast TARGETS THAT ALLY (never
--         the owner); no qualifying ally -> SILENT; an ally BEYOND the bound stays
--         SILENT though the engine's own helper says in-range; a heal entry fires
--         on the health trigger AND picks the LOWEST-health ally; a melee+health
--         heal needs the owner in melee; a wavering family world; two LAPSE worlds
--         (pick->cast drift; pick->cast death) both SKIP; the fresh-handle proof.
--   RED CONTROL: with H98_LIVE / H98_ANN pointing at the pre-edit snapshot (the
--   shipped harness-97 build: no ally triggers at all) the 0v tokens fail and
--   every FIRE world fires nothing; the SILENT worlds pass by design.
-- ============================================================================
function run_h98()
  local live_src98 = read_file(LIVE)
  local ann_src98  = read_file(ANN)
  local RED98 = { fires = 0, claims = 0, ui = 0 }
  -- the RED-control expected pass count (the SILENT worlds whose snapshot
  -- trigger does not fire); verified by the red run below.
  local WANT_RED_98 = 13
  local function posv(v) return (v == true) or (type(v) == "number") end
  local function lg(tag, v) return (tag ~= "[live] ") or posv(v) end
  local function cp98(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function note98(W, TAG)
    RED98.ui = RED98.ui + (W.ui_failures or 0)
    if TAG == "[live] " then
      RED98.fires = RED98.fires + #W.fires
      RED98.claims = RED98.claims + count_log(W, "claim: ")
    end
  end
  local function boot98(W, PATH, TAG, uid, marker, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. marker); ui(W)
    W.conflict = true
    return true
  end
  local function ally_of98(W, uid)
    for i = 1, #(W.live_entries or {}) do
      local pr = W.live_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        local ok, id = pcall(function() return pr.unit:unique_ui_id() end)
        if ok and tostring(id) == tostring(uid) then return pr.unit end
      end
    end
    return nil
  end

  -- --------------------------------------------------- 0v: tokens (both files)
  print("== HARNESS 98 - section 0v: the Class-B ally-targeted tokens (BOTH files) ==")
  local CONSTS = { { "FOURTH.ALLY_CAST_R50  = 35", 50, 35 }, { "FOURTH.ALLY_CAST_R60  = 42", 60, 42 },
                   { "FOURTH.ALLY_CAST_R75  = 52", 75, 52 }, { "FOURTH.ALLY_CAST_R100 = 70", 100, 70 },
                   { "FOURTH.ALLY_CAST_R150 = 105", 150, 105 } }
  for _, f in ipairs({ { name = "live", src = live_src98 }, { name = "ann", src = ann_src98 } }) do
    local nm, s = f.name, f.src
    local allc = true
    for i = 1, #CONSTS do
      if math.floor(CONSTS[i][2] * 0.70 + 1e-9) ~= CONSTS[i][3] then allc = false end
      if raw_find(s, CONSTS[i][1], 1, true) == nil then allc = false end
    end
    check("0v " .. nm .. ": all 5 named 70% ally-cast constants are present with their values", allc)
    check("0v " .. nm .. ": the REAL-range -> ally-bound map (FOURTH.ALLY_CAST) exists",
      raw_find(s, "FOURTH.ALLY_CAST = {", 1, true) ~= nil)
    check("0v " .. nm .. ": every Class-B entry carries its REAL ally range (ally_range_real x18)",
      cp98(s, "\t\tally_range_real = ") == 18)
    check("0v " .. nm .. ": the load loop maps the ally real range to the named constant",
      raw_find(s, "ability.range_m = FOURTH.ALLY_CAST[ability.ally_range_real]", 1, true) ~= nil)
    check("0v " .. nm .. ": the fresh-friend helper + the shared ally picker exist",
      raw_find(s, "function FOURTH.ab_fresh_friend_su(unit)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.ab_pick_ally(unit, routing, family)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.ab_ally_valid(unit, ally)", 1, true) ~= nil
      and raw_find(s, "FOURTH.ab_caster_su = FOURTH.ab_fresh_friend_su(unit)", 1, true) ~= nil
      and raw_find(s, "FOURTH.ab_ally_su = FOURTH.ab_fresh_friend_su(best_ally)", 1, true) ~= nil)
    check("0v " .. nm .. ": the four family evaluators exist and are wired",
      raw_find(s, "function FOURTH.evaluate_ally_heal(unit, routing)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.evaluate_ally_heal_melee(unit, routing)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.evaluate_ally_wavering(unit, routing)", 1, true) ~= nil
      and raw_find(s, "function FOURTH.evaluate_ally_melee_buff(unit, routing)", 1, true) ~= nil
      and raw_find(s, "ally_heal = FOURTH.evaluate_ally_heal,", 1, true) ~= nil
      and raw_find(s, "ally_heal_melee = FOURTH.evaluate_ally_heal_melee,", 1, true) ~= nil
      and raw_find(s, "ally_wavering = FOURTH.evaluate_ally_wavering,", 1, true) ~= nil
      and raw_find(s, "ally_melee_buff = FOURTH.evaluate_ally_melee_buff,", 1, true) ~= nil)
    check("0v " .. nm .. ": the FRESH-HANDLE cast branch is present (caster + ally re-fetched the same tick)",
      raw_find(s, "uc = FOURTH.ab_caster_su.uc", 1, true) ~= nil
      and raw_find(s, "target = FOURTH.ab_ally_su.unit", 1, true) ~= nil
      and raw_find(s, "if FOURTH.ab_ally ~= nil then", 1, true) ~= nil)
    check("0v " .. nm .. ": the per-ability ally bound is read from FOURTH.ab_range_m, never unit_in_range",
      raw_find(s, "local bound = FOURTH.ab_range_m", 1, true) ~= nil
      and raw_find(s, "FOURTH.ab_gap_ok", 1, true) ~= nil
      and raw_find(s, "unit_in_range(", 1, true) == nil)
    check("0v " .. nm .. ": the poll clears the ally slots and sets THIS ability's bound + marker",
      raw_find(s, "FOURTH.ab_ally = nil", 1, true) ~= nil
      and raw_find(s, "FOURTH.ab_range_m = ability.range_m", 1, true) ~= nil
      and raw_find(s, "FOURTH.ab_marker = ability.marker", 1, true) ~= nil)
    check("0v " .. nm .. ": the trigger counts moved (melee_unwavering 373, charge_or_melee 26, ushoran_health 38, melee_health75 1)",
      cp98(s, 'trigger = "melee_unwavering"') == 373
      and cp98(s, 'trigger = "charge_or_melee"') == 26
      and cp98(s, 'trigger = "ushoran_health"') == 38
      and cp98(s, 'trigger = "melee_health75"') == 1)
    check("0v " .. nm .. ": the four ally triggers are wired (11 buff / 3 heal / 1 heal_melee / 2 wavering)",
      cp98(s, 'trigger = "ally_melee_buff"') == 11
      and cp98(s, 'trigger = "ally_heal"') == 3
      and cp98(s, 'trigger = "ally_heal_melee"') == 1
      and cp98(s, 'trigger = "ally_wavering"') == 2)
    check("0v " .. nm .. ": the table stays 579 entries / 579 badges",
      cp98(s, "\t{ marker = ") == 579 and cp98(s, 'badge = "') == 579)
    check("0v " .. nm .. ": the 70% rule is untouched and the engine unit_in_range CALL is still GONE",
      raw_find(s, "FOURTH.RANGE_FRACTION = 0.70", 1, true) ~= nil)
  end
  check("0v live: the picker's chosen-ally log prints the REAL distance + bound",
    raw_find(live_src98, " is the chosen ally (", 1, true) ~= nil
    and raw_find(live_src98, '.. "m bound=" .. tostring(FOURTH.ab_range_m) .. "m")', 1, true) ~= nil)
  check("0v live: the pre-cast ally re-check prints the REAL distance + bound",
    raw_find(live_src98, " pre-cast re-check: the chosen ally is still valid (", 1, true) ~= nil
    and raw_find(live_src98, "SKIPPED: the chosen ally lapsed before the cast", 1, true) ~= nil)
  check("0v ann: the reading copy stays log-free and find-free",
    raw_find(ann_src98, "log(", 1, true) == nil and raw_find(ann_src98, "string.find", 1, true) == nil)

  -- ==========================================================================
  -- THE ALLY WORLDS. One generic builder: a caster (+ an optional ally) and an
  -- expectation of fire-on-the-ally / silence.
  -- ==========================================================================
  local function world_ab(PATH, TAG, o)
    local units = { { name = o.cname or "caster", uid = o.cuid, owns = { o.key },
                      melee = o.cmelee, wavering = o.cwavering, health_percent = o.chp } }
    if o.auid ~= nil then
      units[#units + 1] = { name = o.aname or "ally", uid = o.auid, owns = {},
                            melee = o.amelee, wavering = o.awavering,
                            health_percent = o.ahp, dist = o.adist, dist_seq = o.adist_seq,
                            men_alive = o.amen, men_die_tick = o.amen_die_tick,
                            in_range = true }
    end
    local cards = { { id = tostring(o.cuid), state = "active", vis = true } }
    if o.auid ~= nil then cards[#cards + 1] = { id = tostring(o.auid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, cards = cards,
                           bar = { { id = "b1", key = o.key } } })
    print("== " .. TAG .. o.wname .. " ==")
    if not boot98(W, PATH, TAG, o.cuid, o.marker, o.wname) then return nil end
    local f0 = W.friendly_calls or 0
    polln(W, 1)
    local owner = unit_of(W, o.cuid)
    local ally = (o.auid ~= nil) and ally_of98(W, o.auid) or nil
    if o.expect == "fire_ally" then
      local a = (#W.fires == 1 and W.fires[1].key == o.key and ally ~= nil
        and fire_target_for(W, o.cuid) == ally)
      check(TAG .. o.wname .. ": fires ONCE and the cast target IS THE ALLY (" .. fire_detail(W) .. ")", a)
      local b = (#W.fires == 1 and owner ~= nil and fire_target_for(W, o.cuid) ~= owner)
      check(TAG .. o.wname .. ": the cast target is NOT the owner (self-cast guard)", b)
      local c = true
      if o.fresh then
        c = ((W.friendly_calls or 0) > f0)
        check(TAG .. o.wname .. ": the caster AND the ally are re-fetched FRESH on the firing tick"
          .. " (friendly fetches " .. f0 .. "->" .. tostring(W.friendly_calls) .. ")", c)
      end
      note98(W, TAG); tally(W)
      return a and b and c
    else
      local a = (#W.fires == 0 and #W.ground_fires == 0)
      check(TAG .. o.wname .. ": stays SILENT (" .. fire_detail(W) .. ")", a)
      local b = true
      if o.want_skip_log then
        b = lg(TAG, count_log(W, "SKIPPED: the chosen ally lapsed before the cast") >= 1)
        check(TAG .. o.wname .. ": the pre-cast lapse skip is reported [live log]", b)
      end
      note98(W, TAG); tally(W)
      return a and b
    end
  end

  local DAB   = { key = "wh3_dlc26_character_abilities_da_boss_as_a_plan", marker = "da_boss_as_a_plan", bound = 105 }
  local PATCH = { key = "wh2_dlc13_character_abilities_patch_up", marker = "patch_up", bound = 70 }
  local SHOCK = { key = "wh2_dlc16_hero_abilities_shock_collar", marker = "shock_collar", bound = 70 }
  local PHOEN = { key = "wh3_dlc27_character_abilities_captain_of_the_phoenix_guard", marker = "captain_of_the_phoenix_guard", bound = 35 }
  local STAY  = { key = "wh2_dlc09_character_abilities_stay_here_ill_get_help", marker = "stay_here_ill_get_help", bound = 42 }

  local function w1(PATH, TAG) -- ALLY IN RANGE -> cast ON THE ALLY (buff family) + fresh handles
    return world_ab(PATH, TAG, { wname = "AB-U1: an in-melee caster with an ally in range casts ON THE ALLY",
      key = DAB.key, marker = DAB.marker, cuid = 9901, auid = 9902, cmelee = true, adist = 20, expect = "fire_ally", fresh = true })
  end
  local function w2(PATH, TAG) -- NO ALLY -> SILENT
    return world_ab(PATH, TAG, { wname = "AB-U2: no friendly unit other than the caster -> SILENT",
      key = DAB.key, marker = DAB.marker, cuid = 9903, cmelee = true, expect = "silent" })
  end
  local function w3(PATH, TAG) -- BEYOND the bound -> SILENT though the engine helper says in-range
    return world_ab(PATH, TAG, { wname = "AB-U3: an ally BEYOND the 105 m bound stays SILENT though the engine said in-range",
      key = DAB.key, marker = DAB.marker, cuid = 9904, auid = 9905, cmelee = true, adist = 130, expect = "silent" })
  end
  local function w4(PATH, TAG) -- the OWNER not in melee -> SILENT (the default in-melee shape)
    return world_ab(PATH, TAG, { wname = "AB-U4: the OWNER is not in melee -> SILENT",
      key = DAB.key, marker = DAB.marker, cuid = 9906, auid = 9907, cmelee = false, adist = 20, expect = "silent" })
  end
  local function w5(PATH, TAG) -- HEAL on the health trigger -> cast ON THE ALLY
    return world_ab(PATH, TAG, { wname = "AB-H1: a hurt ally (40%) in range fires the heal ON THE ALLY",
      key = PATCH.key, marker = PATCH.marker, cuid = 9908, auid = 9909, cmelee = false, ahp = 40, adist = 30, expect = "fire_ally" })
  end
  local function w6(PATH, TAG) -- HEAL picks the LOWEST-health ally of two
    local KEY, M = PATCH.key, PATCH.marker
    local W = make_world({ can_perform = true, units = {
      { name = "medic", uid = 9910, owns = { KEY }, melee = false },
      { name = "hurt40", uid = 9911, owns = {}, dist = 30, health_percent = 40 },
      { name = "hurt20", uid = 9912, owns = {}, dist = 50, health_percent = 20 },
    }, cards = { { id = "9910", state = "active", vis = true }, { id = "9911", state = "active", vis = true },
                 { id = "9912", state = "active", vis = true } }, bar = { { id = "b1", key = KEY } } })
    print("== " .. TAG .. "AB-H2: the heal picks the LOWEST-health ally of two ==")
    if not boot98(W, PATH, TAG, 9910, M, "AB-H2 ") then return nil end
    polln(W, 1)
    local a = (#W.fires == 1 and fire_target_for(W, 9910) == ally_of98(W, 9912))
    check(TAG .. "AB-H2: the 20% ally is chosen over the 40% one (" .. fire_detail(W) .. ")", a)
    note98(W, TAG); tally(W)
    return a
  end
  local function w7(PATH, TAG) -- HEAL: an ally ABOVE 75% -> SILENT
    return world_ab(PATH, TAG, { wname = "AB-H3: an ally at 90% health is not a heal target -> SILENT",
      key = PATCH.key, marker = PATCH.marker, cuid = 9913, auid = 9914, cmelee = false, ahp = 90, adist = 30, expect = "silent" })
  end
  local function w8(PATH, TAG) -- HEAL beyond the bound -> SILENT though in-range
    return world_ab(PATH, TAG, { wname = "AB-H4: a hurt ally BEYOND the 70 m bound stays SILENT though the engine said in-range",
      key = PATCH.key, marker = PATCH.marker, cuid = 9915, auid = 9916, cmelee = false, ahp = 40, adist = 100, expect = "silent" })
  end
  local function w9(PATH, TAG) -- LAPSE (drift): in range at pick, out at cast -> SKIP
    return world_ab(PATH, TAG, { wname = "AB-L1: the chosen ally drifts out of range between pick and cast -> SKIP",
      key = PATCH.key, marker = PATCH.marker, cuid = 9917, auid = 9918, cmelee = false, ahp = 40,
      adist_seq = { 30, 100 }, expect = "silent", want_skip_log = true })
  end
  local function w10(PATH, TAG) -- LAPSE (death): the ally is gone at the pre-cast re-check -> SKIP
    return world_ab(PATH, TAG, { wname = "AB-L2: the chosen ally is GONE at the pre-cast re-check -> SKIP",
      key = DAB.key, marker = DAB.marker, cuid = 9919, auid = 9920, cmelee = true, amen = 1, amen_die_tick = 1,
      adist = 30, expect = "silent", want_skip_log = true })
  end
  local function w11(PATH, TAG) -- WAVERING family
    return world_ab(PATH, TAG, { wname = "AB-W1: a WAVERING ally in range fires the wavering family ON THE ALLY",
      key = SHOCK.key, marker = SHOCK.marker, cuid = 9921, auid = 9922, cmelee = false, cwavering = false,
      awavering = true, adist = 30, expect = "fire_ally" })
  end
  local function w12(PATH, TAG) -- WAVERING family: no wavering ally -> SILENT
    return world_ab(PATH, TAG, { wname = "AB-W2: a steady (non-wavering) ally is not a wavering target -> SILENT",
      key = SHOCK.key, marker = SHOCK.marker, cuid = 9923, auid = 9924, cmelee = false, awavering = false,
      adist = 30, expect = "silent" })
  end
  local function w13(PATH, TAG) -- MELEE+HEALTH family: fire on the ally
    return world_ab(PATH, TAG, { wname = "AB-M1: an in-melee caster with a hurt ally fires the melee+health heal ON THE ALLY",
      key = PHOEN.key, marker = PHOEN.marker, cuid = 9925, auid = 9926, cmelee = true, ahp = 50, adist = 25, expect = "fire_ally" })
  end
  local function w14(PATH, TAG) -- MELEE+HEALTH family: the owner not in melee -> SILENT
    return world_ab(PATH, TAG, { wname = "AB-M2: the melee+health heal needs the OWNER in melee -> SILENT",
      key = PHOEN.key, marker = PHOEN.marker, cuid = 9927, auid = 9928, cmelee = false, ahp = 50, adist = 25, expect = "silent" })
  end
  local function w15(PATH, TAG) -- STAY HERE now casts ON THE PICKED ALLY (the Class-B cast-target fix)
    return world_ab(PATH, TAG, { wname = "AB-S1: Stay Here, I'll Get Help! now casts ON THE PICKED WAVERING ALLY",
      key = STAY.key, marker = STAY.marker, cuid = 9929, auid = 9930, cmelee = false, cwavering = false,
      awavering = true, adist = 20, expect = "fire_ally" })
  end
  local function w16(PATH, TAG) -- STAY HERE beyond its own new 42 m bound -> SILENT
    return world_ab(PATH, TAG, { wname = "AB-S2: Stay Here's ally BEYOND its own 42 m bound stays SILENT",
      key = STAY.key, marker = STAY.marker, cuid = 9931, auid = 9932, cmelee = false, cwavering = false,
      awavering = true, adist = 50, expect = "silent" })
  end

  local results = {}
  local WORLD_FNS = { w1, w2, w3, w4, w5, w6, w7, w8, w9, w10, w11, w12, w13, w14, w15, w16 }
  for _, path in ipairs({ LIVE, ANN }) do
    local TAG = (path == LIVE) and "[live] " or "[ann]  "
    for i = 1, #WORLD_FNS do results[#results + 1] = WORLD_FNS[i](path, TAG) end
  end

  local n_ok = 0
  for _, r in ipairs(results) do if posv(r) then n_ok = n_ok + 1 end end
  print("== HARNESS 98 - Class-B ally worlds: " .. n_ok .. "/" .. #results .. " passed; fires " .. RED98.fires .. " ==")

  check("every ui tick ran clean across the HARNESS-98 worlds (" .. RED98.ui .. " failures)", RED98.ui == 0)

  if not RED_MODE then
    check("HEADLINE (harness 98): CLASS B ships on the mod's OWN ally picker (blood_sacrifice / "
      .. "eat_da_runts shape) with the Class-A FRESH-HANDLE discipline. 17 entries move to four new ally "
      .. "families (ally_melee_buff 11 / ally_heal 3 / ally_heal_melee 1 / ally_wavering 2); Stay Here, "
      .. "I'll Get Help! gains its cast target + its own 70% bound; Meat Feast is an ARMY-BAR ability and is "
      .. "SKIPPED (standing rule 10); 15 entries need a user ruling. Every entry carries its own REAL "
      .. "target_intercept_range -> ONE named 70% constant per real range (FOURTH.ALLY_CAST); the offer test "
      .. "is unit:unit_distance(ally) <= that constant ONLY (never the engine's unit_in_range) and the REAL "
      .. "distance is logged. All " .. #results .. " worlds passed.", n_ok == #results)
  else
    check("RED CONTROL (harness 98): on the pre-edit snapshot (the shipped harness-97 build: no ally triggers "
      .. "at all, every Class-B entry still melee_unwavering / uhsoran_health self-cast) the section-0v tokens "
      .. "fail, every FIRE world fails (the snapshot's 5 self-casts land on the OWNER, never on an ally) and the "
      .. "SILENT world whose snapshot trigger does fire (or whose lapse log is absent) fails too; only the SILENT "
      .. "worlds whose snapshot trigger stays quiet pass by design. "
      .. n_ok .. "/" .. #results .. " world results pass (want " .. WANT_RED_98 .. "), fires " .. RED98.fires
      .. ", claims " .. RED98.claims, n_ok == WANT_RED_98)
  end
end
run_h98()
