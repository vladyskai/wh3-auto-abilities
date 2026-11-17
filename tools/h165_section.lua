-- ============================================================================
-- HARNESS 165 (round 166): THE SHORT CARDS (user rulings 2026-11-17, after the Daemons battle).
--   0zz13 the round-166 tokens in both files.
--   SC1 every entry carries a short card: 'Fires ...', ends with '.', no token, bracket, em dash, name or 'on A:',
--       at most 160 characters. Every card is printed (CARD lines) for the round document.
--   SC2 exact cards: Deadly Onslaught, Entice, Bloodbeast, Heaven's Gate (its blast cannot hurt our units: no 'clear of
--       allies'), Banishment (it can), Eye of the Storm, Helping Hand, Unholy Clamour (army-wide aura), Morikhane (no
--       aura), Curse of Djaf, Deathmaster's Sigil.
--   TT2 the Entice badge's hover tooltip is its short card.
--   AL2 the ALL tooltip is exactly 'Arm or disarm every automatic ability of the selected unit(s).'
--   WD1 Banishment (12 m blast, 95% reach 16 m): the caster itself 20 m from a standing 200-man block, no other unit of
--       ours -> ONE cast (the caster never blocks its own wanderer).
--   WD2 the same, plus our Swordsmen 20 m from the block -> no cast (another unit still blocks).
--   RED (pre-166 = round 165): the long cards ('<name> on A: ...'), the long ALL tooltip, WD1 no cast.
-- ============================================================================
function run_h165()
  local L165 = os.getenv("H165_LIVE") or LIVE
  local A165 = os.getenv("H165_ANN") or ANN
  local RED165 = (os.getenv("H165_LIVE") ~= nil) or (os.getenv("H165_ANN") ~= nil)
  local EN = "wh3_dlc29_unit_abilities_entice"
  local BN = "wh3_main_spell_bound_banishment"
  local CASTER = "wh_dlc07_brt_cha_prophetess_life_0"
  local GG = "wh_main_vmp_inf_grave_guard_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local ALL_NEW = "Arm or disarm every automatic ability of the selected unit(s)."
  local pre165 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 165 - section 0zz13: the round-166 tokens ==")
  if not RED165 then
    for _, f in ipairs({ { name = "live", path = L165 }, { name = "ann", path = A165 } }) do
      local s = read_file(f.path)
      check("0zz13 " .. f.name .. ": the short card table, the no-aura choice, the bare return, the ALL text, the wanderer rule",
        cp(s, "FOURTH.CARD_TIP = {") == 1 and cp(s, "FOURTH.CARD_TIP_NOAURA = {") == 1
        and cp(s, '\tcharge_or_melee = "Fires when charging or in melee",\n') == 1
        and cp(s, '\treturn table.concat(parts, "; ") .. "."') == 1
        and cp(s, " on A: ") == 0
        and cp(s, 'FOURTH.ALL_TIP = "' .. ALL_NEW .. '"\n') == 1 and cp(s, "ALL: arm or disarm") == 0
        and cp(s, "-- ROUND 166 (user ruling 2026-11-17, \"do not count the caster\")") == 1
        and cp(s, "\t{ marker = ") == 946)
    end
  end

  local FILES = { { path = A165, tag = "[annotated] " }, { path = L165, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, units, enemies, marker, key, PATH, TAG, sv)
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
        local id = nil
        pcall(function() id = tostring(pr.unit:unique_ui_id()) end)
        pr.unit.is_visible_to_alliance = function(self, a) return true end
        pr.unit.is_currently_flying = function(self) return false end
        local v = sv and sv[id] or 800
        pr.unit.strategic_value = function(self) return v end
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
  local function ours(uid, x, z, o)
    local u = { uid = uid, name = SW, owns = {}, melee = false, pos = { x, 0, z }, width = 29.4, men_alive = 120,
                initial_men = 120, unit_class = "inf_mel" }
    for k, v in pairs(o or {}) do u[k] = v end
    return u
  end
  local BIG = { men_alive = 200, initial_men = 200, width = 20, dist = 60 }

  -- SC / TT: the cards, from the Entice world's captured ABILITIES table
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    local b = 30000
    local W = world("SC. the short cards (Entice in melee at 80%)",
      { caster(b, EN, { melee = true, dist = 1, hp_frac = 0.8 }) },
      { block(b + 5, GG, 0, 6, { melee = true, dist = 1 }) }, "entice", EN, f.path, TAG, nil)
    if W ~= nil then
      local cap = W.cap or {}
      local total, good, bad, longest = 0, 0, {}, 0
      local by = {}
      for _, e in ipairs(cap) do
        total = total + 1
        local c = e.card
        local ok = type(c) == "string" and c:sub(1, 6) == "Fires " and c:sub(-1) == "." and #c <= 160
          and raw_find(c, "{", 1, true) == nil and raw_find(c, "[", 1, true) == nil
          and raw_find(c, "]", 1, true) == nil and raw_find(c, "\226\128\148", 1, true) == nil
          and raw_find(c, " on A:", 1, true) == nil
        if type(c) == "string" and #c > longest then longest = #c end
        if ok then good = good + 1 else bad[#bad + 1] = tostring(e.marker) end
        by[e.marker] = c
        if TAG == "[live] " and not RED165 then print("CARD " .. tostring(e.marker) .. ": " .. tostring(c)) end
      end
      local a = (total == 946 and good == 946)
      check(TAG .. "SC1: every entry carries a whole short card (" .. good .. "/" .. total .. ", longest " .. longest .. ")"
        .. (#bad > 0 and (" first bad: " .. tostring(bad[1])) or ""), (RED165 and (good == 0)) or (not RED165 and a))
      done((RED165 and good == 0) or (not RED165 and a))
      local exact = by.deadly_onslaught == "Fires when charging or in melee."
        and by.entice == "Fires in melee unless wavering; not below 50% health."
        and by.bloodbeast == "Fires in melee unless wavering, clear of allies."
        and by.heavens_gate == "Fires when it and the target stand still, where the blast hurts the enemy most."
        and by.banishment == "Fires when it and the target stand still, where the blast hurts the enemy most, clear of allies."
        and by.eye_of_the_storm == "Fires in melee unless wavering; only in large form."
        and by.helping_hand == "Fires in melee unless wavering, on the nearest ally in range; Lord or Hero allies only."
        and by.unholy_clamour == "Fires when it or any ally wavers."
        and by.morikhane == "Fires under missile fire."
        and by.curse_of_djaf == "Fires under the nearest shooting enemy missile unit; only at 50% health or less."
        and by.deathmasters_sigil == "Fires on the most valuable enemy Lord or Hero; no flying targets, clear of allies."
      check(TAG .. "SC2: the exact short cards (Deadly Onslaught, Entice, Bloodbeast, Heaven's Gate, Banishment, Eye of "
        .. "the Storm, Helping Hand, Unholy Clamour, Morikhane, Curse of Djaf, Deathmaster's Sigil)",
        (RED165 and not exact) or (not RED165 and exact))
      done((RED165 and not exact) or (not RED165 and exact))
      local rec = W.badge_records and W.badge_records["zz_auto_badge_entice"]
      local tip = rec and rec.tooltip
      local t_ok = (tip ~= nil and tip == by.entice and tip == "Fires in melee unless wavering; not below 50% health.")
      check(TAG .. "TT2: the Entice badge's hover tooltip is its short card (" .. tostring(tip) .. ")",
        (RED165 and not t_ok) or (not RED165 and t_ok))
      done((RED165 and not t_ok) or (not RED165 and t_ok))
      tally(W)
    end
  end

  -- AL2: the ALL tooltip text, read from each file
  for _, f in ipairs(FILES) do
    local s = read_file(f.path)
    local a = cp(s, 'FOURTH.ALL_TIP = "' .. ALL_NEW .. '"\n') == 1 and cp(s, "ALL: arm or disarm") == 0
    check(f.tag .. "AL2: the ALL tooltip is exactly '" .. ALL_NEW .. "'", (RED165 and not a) or (not RED165 and a))
    done((RED165 and not a) or (not RED165 and a))
  end

  -- WD: the caster never blocks its own wanderer
  local WORLDS = {
    { "WD1. Banishment: the caster 20 m from a standing 200-man block, no other unit of ours -> ONE cast",
      function(b) return { caster(b, BN, { dist = 60, pos = { 0, 0, 60 } }) }, { block(b + 5, GG, 0, 80, BIG) },
        { [tostring(b + 5)] = 1600 } end, "banishment", BN, 1, 0 },
    { "WD2. Banishment: the same, plus our Swordsmen 20 m from the block -> no cast",
      function(b) return { caster(b, BN, { dist = 60, pos = { 0, 0, 60 } }), ours(b + 1, 0, 100) },
        { block(b + 5, GG, 0, 80, BIG) }, { [tostring(b + 5)] = 1600 } end, "banishment", BN, 0, 0 },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = RED165 and w[6] or w[5]
      local b = 30100 + i * 20
      local units, enemies, sv = w[2](b)
      local W = world(w[1], units, enemies, w[3], w[4], f.path, TAG, sv)
      if W ~= nil then
        local got = 0
        for _, x in ipairs(W.fires) do if x.key == w[4] then got = got + 1 end end
        for _, x in ipairs(W.ground_fires or {}) do if x.key == w[4] then got = got + 1 end end
        local a = (got == want)
        check(TAG .. w[1]:sub(1, 3) .. (RED165 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got, a)
        done(a)
        tally(W)
      end
    end
  end

  if RED165 then
    check("RED CONTROL (harness 165): the pre-166 build has the long cards, the long ALL text and blocks on its caster - "
      .. n_ok .. "/" .. n_all, n_all == 12 and n_ok == 12)
  else
    check("HARNESS 165: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 12 and n_ok == 12)
  end
  print("== HARNESS 165 done: " .. (checks - pre165) .. " checks in this section ==")
end
