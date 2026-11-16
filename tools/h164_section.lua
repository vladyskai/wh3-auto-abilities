-- ============================================================================
-- HARNESS 164 (round 165): THE NIGHT AUDIT (2026-11-17) - the card, the game's
--   caster and ally target rules, the WW ground cast.
--   CD  every entry carries a card (name, sentence, clauses), no token or bracket left, no em dash; exact texts for
--       Deadly Onslaught, Entice, Bloodbeast; the clauses of Helping Hand, Eye of the Storm, Curse of Djaf, Unholy
--       Clamour, Sunfang. Every card is printed (CARD lines) for the round document.
--   CD3 every entry with a game range has its 70% bound (the two round-164 sweeps had none: 6 m and 3 m fell back
--       to the 52 m default).
--   TT  the M/A badge's hover tooltip is the entry's card.
--   US1 Entice (refused below 50% health): in melee at 40% -> no cast.   US2 at 80% -> ONE cast.
--   US3 Daemon Flask of Ashak (refused in flight): in melee, flying -> no cast.   US4 on the ground -> ONE cast.
--   US5 Eye of the Storm (large casters only): a Huntsmen General -> no cast.   US6 the Storm Dragon -> ONE cast.
--   US7 Curse of Khsar (refused above 50% health): an enemy in melee 10 m away, caster at 90% -> no cast.
--   US8 the same at 40% -> ONE ground cast.
--   AT1 Helping Hand (Lords and Heroes only): in melee, the only ally a Swordsmen block -> no cast.
--   AT2 the ally Arkhan (a Lord) -> ONE cast, on Arkhan.
--   GR1 Blue Fire of Chaos (ground-only): the caster free, a standing block 40 m away -> ONE GROUND cast, no unit cast.
--   RED (pre-165 = round 164): no cards and no tooltip; two unmapped ranges; US1, US3, US5, US7, AT1 cast (the rules are not honoured);
--       GR1 casts in the unit form.
-- ============================================================================
function run_h164()
  local L164 = os.getenv("H164_LIVE") or LIVE
  local A164 = os.getenv("H164_ANN") or ANN
  local RED164 = (os.getenv("H164_LIVE") ~= nil) or (os.getenv("H164_ANN") ~= nil)
  local EN = "wh3_dlc29_unit_abilities_entice"
  local DF = "wh3_dlc23_item_abilities_daemon_flask_of_ashak"
  local EY = "wh3_main_lord_abilities_eye_of_the_storm"
  local CK = "wh2_dlc09_character_abilities_curse_of_khsar"
  local HH = "wh2_pro08_character_abilities_helping_hand"
  local BF = "wh3_main_daemon_arms_abilities_blue_fire"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local DRAGON = "wh3_main_cth_cha_storm_dragon_1"
  local ARKHAN = "wh2_dlc09_tmb_cha_arkhan_0"
  local GG = "wh_main_vmp_inf_grave_guard_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local pre164 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 164 - section 0zz12: the round-165 tokens ==")
  if not RED164 then
    for _, f in ipairs({ { name = "live", path = L164 }, { name = "ann", path = A164 } }) do
      local s = read_file(f.path)
      check("0zz12 " .. f.name .. ": the card table, the two generated rule texts, the gates and the ground line",
        cp(s, "FOURTH.CARD_TIP = {") == 1 and cp(s, 'FOURTH.USAGE_TEXT = "') == 1
        and cp(s, 'FOURTH.ATARGET_TEXT = "') == 1
        and cp(s, "\t\tif not FOURTH.usage_ok(unit, ability, ui_id) then return nil end\n") == 1
        and cp(s, "\tif not FOURTH.ab_atarget_ok(unit) then return false end\n") == 1
        and cp(s, "\t\t\t\t\tFOURTH.ab_atarget = ability.atarget") == 1
        and cp(s, '\t\tor (FOURTH.eg_arm == "ww" and FOURTH.eg_ground == true) then\n') == 1
        and cp(s, "state.badge:SetTooltipText(ability.card, true)") == 1
        and cp(s, "\t{ marker = ") == 946)
    end
  end

  local FILES = { { path = A164, tag = "[annotated] " }, { path = L164, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function our_unit(W, uid)
    for _, u in ipairs(W.mock_units or {}) do
      local ok, id = pcall(function() return u:unique_ui_id() end)
      if ok and tostring(id) == tostring(uid) then return u end
    end
    return nil
  end
  local function world(wname, units, enemies, marker, key, PATH, TAG, selffly)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = key } } })
    W.defaults_on = false
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    OH77.cap = nil
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    W.cap = OH77.cap
    deploy_phases(W); ui(W)
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        pr.unit.is_visible_to_alliance = function(self, a) return true end
        pr.unit.is_currently_flying = function(self) return false end
        pr.unit.strategic_value = function(self) return 800 end
      end
    end
    for _, d in ipairs(units) do
      local u = our_unit(W, d.uid)
      if u ~= nil then
        local f = (d.uid == units[1].uid) and selffly or false
        u.is_currently_flying = function(self) return f end
      end
    end
    sel_event(W, units[1].uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. marker); ui(W)
    sel_event(W, units[1].uid, false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  local function caster(b, key, o)
    local c = { name = CASTER, uid = b, owns = { key }, melee = false, dist = 40, pos = { 0, 0, 0 }, width = 2,
                men_alive = 1, unit_class = "com" }
    for k, v in pairs(o or {}) do c[k] = v end
    return c
  end
  local function block(uid, name, x, z, o)
    local e = { uid = uid, name = name, melee = false, pos = { x, 0, z }, width = 29.4, men_alive = 120,
                initial_men = 120, unit_class = "inf_mel", dist = 40 }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  local function ally(uid, name, o)
    local a = { uid = uid, name = name, owns = {}, melee = true, pos = { 0, 0, 20 }, dist = 20, width = 29.4,
                men_alive = 120, initial_men = 120, unit_class = "inf_mel" }
    for k, v in pairs(o or {}) do a[k] = v end
    return a
  end
  local FOE = function(b) return { block(b + 5, GG, 0, 6, { melee = true, dist = 1 }) } end

  -- CD / TT: the cards, from the Entice world's captured ABILITIES table
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    local b = 29000
    local W = world("CD. the cards (Entice in melee at 80%)", { caster(b, EN, { melee = true, dist = 1, hp_frac = 0.8 }) },
      FOE(b), "entice", EN, f.path, TAG, false)
    if W ~= nil then
      local cap = W.cap or {}
      local total, good, bad = 0, 0, {}
      local by = {}
      for _, e in ipairs(cap) do
        total = total + 1
        local c = e.card
        local ok = type(c) == "string" and c:sub(1, #tostring(e.name) + 7) == tostring(e.name) .. " on A: "
          and c:sub(-1) == "." and raw_find(c, "{", 1, true) == nil and raw_find(c, "[", 1, true) == nil
          and raw_find(c, "]", 1, true) == nil and raw_find(c, "\226\128\148", 1, true) == nil
        if ok then good = good + 1 else bad[#bad + 1] = tostring(e.marker) end
        by[e.marker] = c
        if TAG == "[live] " and not RED164 then print("CARD " .. tostring(e.marker) .. ": " .. tostring(c)) end
      end
      local a = (total == 946 and good == 946)
      check(TAG .. "CD1: every entry carries a whole card (" .. good .. "/" .. total .. ")"
        .. (#bad > 0 and (" first bad: " .. tostring(bad[1])) or ""), (RED164 and (good == 0)) or a)
      done((RED164 and good == 0) or a)
      local function has(m, t) return type(by[m]) == "string" and raw_find(by[m], t, 1, true) ~= nil end
      local exact = by.deadly_onslaught == "Deadly Onslaught on A: fires when this unit runs at the enemy it is "
          .. "attacking, 12 to 60 m away and at most 4 s from contact, or when it is in melee."
        and by.entice == "Entice on A: fires when this unit is in melee and not wavering; not below 50% health."
        and by.bloodbeast == "Bloodbeast on A: fires when this unit is in melee and not wavering, with none of your "
          .. "other units within 25 m of it."
        and has("helping_hand", "; the ally must be a Lord or Hero.")
        and has("eye_of_the_storm", "; only when this unit is a large unit.")
        and has("curse_of_djaf", "; only at or below 50% health.")
        and has("unholy_clamour", "or a friendly unit anywhere on the field, is wavering")
        and has("sunfang", ", with none of your other units within 22 m of the path.")
        and has("wrath_of_manann", "within 16 m of the path at its start, widening to 33 m at its end")
        and has("emberstorm", "none of your other units within 20 m.")
        and not has("eye_of_khorne", "the ally must")
        and has("blue_fire", "; not while this unit is in melee.")
      check(TAG .. "CD2: the exact cards and clauses (Deadly Onslaught, Entice, Bloodbeast, Helping Hand, Eye of the "
        .. "Storm, Curse of Djaf, Unholy Clamour, Sunfang, Wrath of Manann, Emberstorm, Eye of Khorne, Blue Fire)", (RED164 and not exact) or (not RED164 and exact))
      done((RED164 and not exact) or (not RED164 and exact))
      local unmapped = {}
      for _, e in ipairs(cap) do
        if e.range_real ~= nil and e.range_m == nil and e.unbounded ~= true then unmapped[#unmapped + 1] = e.marker end
      end
      local u_ok = (#unmapped == 0)
      check(TAG .. "CD3: every entry with a game range has its 70% bound (unmapped " .. #unmapped
        .. (#unmapped > 0 and (": " .. tostring(unmapped[1])) or "") .. ")", (RED164 and #unmapped == 2) or (not RED164 and u_ok))
      done((RED164 and #unmapped == 2) or (not RED164 and u_ok))
      local rec = W.badge_records and W.badge_records["zz_auto_badge_entice"]
      local tip = rec and rec.tooltip
      local t_ok = (tip ~= nil and tip == by.entice)
      check(TAG .. "TT1: the Entice badge's hover tooltip is its card (" .. tostring(tip) .. ")",
        (RED164 and tip == nil) or (not RED164 and t_ok))
      done((RED164 and tip == nil) or (not RED164 and t_ok))
      tally(W)
    end
  end

  -- name, builder(b) -> units, enemies; marker; key; selffly; GREEN casts; RED casts; target offset; ground-only?
  local WORLDS = {
    { "US1. Entice in melee at 40% health -> no cast (refused below 50%)",
      function(b) return { caster(b, EN, { melee = true, dist = 1, hp_frac = 0.4 }) }, FOE(b) end,
      "entice", EN, false, 0, 1, nil },
    { "US2. Entice in melee at 80% health -> ONE cast",
      function(b) return { caster(b, EN, { melee = true, dist = 1, hp_frac = 0.8 }) }, FOE(b) end,
      "entice", EN, false, 1, nil, nil },
    { "US3. Daemon Flask of Ashak in melee, flying -> no cast (refused in flight)",
      function(b) return { caster(b, DF, { melee = true, dist = 1 }) }, FOE(b) end,
      "daemon_flask_of_ashak", DF, true, 0, 1, nil },
    { "US4. Daemon Flask of Ashak in melee, on the ground -> ONE cast",
      function(b) return { caster(b, DF, { melee = true, dist = 1 }) }, FOE(b) end,
      "daemon_flask_of_ashak", DF, false, 1, nil, nil },
    { "US5. Eye of the Storm on a Huntsmen General (not large) in melee -> no cast",
      function(b) return { caster(b, EY, { melee = true, dist = 1 }) }, FOE(b) end,
      "eye_of_the_storm", EY, false, 0, 1, nil },
    { "US6. Eye of the Storm on the Storm Dragon in melee -> ONE cast",
      function(b) return { caster(b, EY, { name = DRAGON, melee = true, dist = 1 }) }, FOE(b) end,
      "eye_of_the_storm", EY, false, 1, nil, nil },
    { "US7. Curse of Khsar at 90% health, an enemy in melee 10 m away -> no cast (refused above 50%)",
      function(b) return { caster(b, CK, { hp_frac = 0.9, dist = 10 }) },
        { block(b + 5, GG, 0, 20, { melee = true, dist = 10 }) } end,
      "curse_of_khsar", CK, false, 0, 1, nil },
    { "US8. Curse of Khsar at 40% health -> ONE cast",
      function(b) return { caster(b, CK, { hp_frac = 0.4, dist = 10 }) },
        { block(b + 5, GG, 0, 20, { melee = true, dist = 10 }) } end,
      "curse_of_khsar", CK, false, 1, nil, nil },
    { "AT1. Helping Hand in melee, the only ally a Swordsmen block -> no cast (Lords and Heroes only)",
      function(b) return { caster(b, HH, { melee = true, dist = 1 }), ally(b + 1, SW) }, FOE(b) end,
      "helping_hand", HH, false, 0, 1, nil },
    { "AT2. Helping Hand in melee, the ally Arkhan -> ONE cast on Arkhan",
      function(b) return { caster(b, HH, { melee = true, dist = 1 }),
        ally(b + 1, ARKHAN, { men_alive = 1, initial_men = 1, unit_class = "com", width = 2 }) }, FOE(b) end,
      "helping_hand", HH, false, 1, nil, 1 },
    { "GR1. Blue Fire of Chaos: the caster free, a standing block 40 m away -> ONE GROUND cast",
      function(b) return { caster(b, BF) }, { block(b + 5, GG, 0, 55) } end,
      "blue_fire", BF, false, 1, 1, nil, true },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[6]
      if RED164 then want = w[7] end
      if want ~= nil then
        local b = 29100 + i * 20
        local units, enemies = w[2](b)
        local W = world(w[1], units, enemies, w[3], w[4], f.path, TAG, w[5])
        if W ~= nil then
          local unit_n, ground_n, tid = 0, 0, nil
          for _, x in ipairs(W.fires) do
            if x.key == w[4] then
              unit_n = unit_n + 1
              if tid == nil then pcall(function() tid = tostring(x.target:unique_ui_id()) end) end
            end
          end
          for _, x in ipairs(W.ground_fires or {}) do if x.key == w[4] then ground_n = ground_n + 1 end end
          local a
          if w[9] then
            -- the ground-only WW key: GREEN one ground cast and no unit cast; RED the reverse
            if RED164 then a = (unit_n == 1 and ground_n == 0) else a = (ground_n == 1 and unit_n == 0) end
          else
            a = (unit_n + ground_n == want)
          end
          if a and want > 0 and not RED164 and w[8] ~= nil then a = (tid == tostring(b + w[8])) end
          check(TAG .. w[1]:sub(1, 3) .. (RED164 and "-RED" or "") .. ": " .. want .. " cast(s) expected, got unit "
            .. unit_n .. " ground " .. ground_n .. (w[8] and (", target " .. tostring(tid)) or ""), a)
          done(a)
          tally(W)
        end
      end
    end
  end
  if RED164 then
    check("RED CONTROL (harness 164): the pre-165 build has no cards, ignores the game's caster and ally rules and "
      .. "casts Blue Fire in the unit form - " .. n_ok .. "/" .. n_all, n_all == 20 and n_ok == 20)
  else
    check("HARNESS 164: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 30 and n_ok == 30)
  end
  print("== HARNESS 164 done: " .. (checks - pre164) .. " checks in this section ==")
end

