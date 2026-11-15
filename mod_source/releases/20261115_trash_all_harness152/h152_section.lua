
-- ============================================================================
-- HARNESS 152 (round 153).
--   Sun Dragon's Breath (5 m blast, line 17, three packed blocks = about 99.5
--   soldiers), the caster flying and standing.
--   TR1 one TRASH block (value 1 per soldier): no cast.
--   TR2 two trash blocks stacked (about 67 soldiers): no cast.
--   TR3 four trash blocks stacked (about 134 soldiers): ONE cast.
--   TR4 one ordinary block (value about 7 per soldier): ONE cast.
--   AL1 two selected units with NO shared ability (Book of Hoeth / Runefang): the
--   ALL badge is shown, and one click arms both; both then fire.
--   AP2 the ALL badge sits at (-855, -28) and carries the tooltip.
--   RED (pre-153): TR1 and TR2 cast; AP2 at the old spot without a tooltip.
-- ============================================================================
function run_h152()
  local L152 = os.getenv("H152_LIVE") or LIVE
  local A152 = os.getenv("H152_ANN") or ANN
  local RED152 = (os.getenv("H152_LIVE") ~= nil) or (os.getenv("H152_ANN") ~= nil)
  local SU = "wh2_main_unit_abilities_sun_dragons_breath"
  local BH = "wh2_main_item_abilities_book_of_hoeth"
  local RF = "wh_main_weapon_abilities_runefang"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local SW = "wh_main_emp_inf_swordsmen"
  local pre152 = checks

  print("== HARNESS 152 - section 0zy: the round-153 tokens ==")
  if not RED152 then
    for _, f in ipairs({ { name = "live", path = L152 }, { name = "ann", path = A152 } }) do
      local s = read_file(f.path)
      check("0zy " .. f.name .. ": the trash rule (2 per soldier, 3 packed blocks), ALL shown for any owner, spot, tooltip",
        raw_find(s, "FOURTH.TRASH_VPS = 2\n", 1, true) ~= nil
        and raw_find(s, "FOURTH.TRASH_BLOCKS = 3\n", 1, true) ~= nil
        and raw_find(s, "function FOURTH.blob_trash_ok(e, sc, r)", 1, true) ~= nil
        and raw_find(s, "local any = FOURTH.all_selection_has_ours()", 1, true) ~= nil
        and raw_find(s, "FOURTH.ALL_OX, FOURTH.ALL_OY = -855, -28", 1, true) ~= nil
        and raw_find(s, "st.badge:SetTooltipText(FOURTH.ALL_TIP, true)", 1, true) ~= nil)
    end
  end

  local FILES = { { path = A152, tag = "[annotated] " }, { path = L152, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function our_unit(W, uid)
    for _, u in ipairs(W.mock_units or {}) do
      local ok, id = pcall(function() return u:unique_ui_id() end)
      if ok and tostring(id) == tostring(uid) then return u end
    end
    return nil
  end
  local function world(wname, units, enemies, arm, key, PATH, TAG, sv)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = key } } })
    W.defaults_on = false
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        local id = nil
        pcall(function() id = tostring(pr.unit:unique_ui_id()) end)
        pr.unit.is_visible_to_alliance = function(self, a) return true end
        pr.unit.is_currently_flying = function(self) return false end
        local v = sv[id]
        if v ~= nil then pr.unit.strategic_value = function(self) return v end end
      end
    end
    local u = our_unit(W, arm[1])
    if u ~= nil then u.is_currently_flying = function(self) return true end end
    sel_event(W, arm[1], true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. arm[2]); ui(W)
    sel_event(W, arm[1], false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  local function caster(b)
    return { name = CASTER, uid = b, owns = { SU }, melee = false, dist = 40, pos = { 0, 0, 0 }, width = 2,
             men_alive = 1, unit_class = "com" }
  end
  local function stack(b, n, value)
    local es, sv = {}, {}
    for i = 1, n do
      es[#es + 1] = { uid = b + 4 + i, name = SW, melee = false, pos = { 0, 0, 60 }, width = 29.4, men_alive = 120,
                      initial_men = 120, unit_class = "inf_mel" }
      sv[tostring(b + 4 + i)] = value
    end
    return es, sv
  end
  -- name, n blocks, value per block, GREEN casts, RED casts
  local WORLDS = {
    { "TR1. one TRASH block (value 1 per soldier) -> no cast", 1, 120, 0, 1 },
    { "TR2. two trash blocks stacked (about 67 soldiers) -> no cast", 2, 120, 0, 1 },
    { "TR3. four trash blocks stacked (about 134 soldiers) -> ONE cast", 4, 120, 1, nil },
    { "TR4. one ordinary block (value about 7 per soldier) -> ONE cast", 1, 850, 1, nil },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[4]
      if RED152 then want = w[5] end
      if want ~= nil then
        local b = 17500 + i * 20
        local es, sv = stack(b, w[2], w[3])
        local W = world(w[1], { caster(b) }, es, { b, "unit_abilities_sun_dragons_breath" }, SU, f.path, TAG, sv)
        if W ~= nil then
          local got = 0
          for _, x in ipairs(W.fires) do if x.key == SU then got = got + 1 end end
          local a = (got == want)
          check(TAG .. w[1]:sub(1, 3) .. (RED152 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got, a)
          done(a)
          tally(W)
        end
      end
    end
    -- AL1 and AP2: the ALL badge
    do
      local b = 17690
      local units = { { name = CASTER, uid = b, owns = { BH }, melee = false, dist = 300 },
                      { name = CASTER, uid = b + 1, owns = { RF }, melee = true, dist = 300 } }
      local cards = { { id = tostring(b), state = "active", vis = true }, { id = tostring(b + 1), state = "active", vis = true } }
      local W = make_world({ can_perform = true, units = units, cards = cards,
        bar = { { id = "b1", key = BH }, { id = "b2", key = RF } } })
      W.defaults_on = false
      print("== " .. TAG .. "AL1/AP2. the ALL badge with two units that share no ability ==")
      local ok = pcall(load_world, W, f.path)
      check(TAG .. "AL1: the file loads", ok)
      if ok then
        deploy_phases(W); ui(W)
        sel_event(W, b, true); ui(W); ui(W); ui(W)
        sel_event(W, b + 1, true); ui(W); ui(W); ui(W)
        local rec = W.badge_records["zz_auto_badge_all"]
        if RED152 then
          local a = (rec ~= nil and (rec.offset[1] ~= -855 or rec.tooltip == nil))
          check(TAG .. "AP2-RED: the pre-153 badge is elsewhere / has no tooltip", a)
          done(a)
        else
          local a = (rec ~= nil and rec.offset[1] == -855 and rec.offset[2] == -28 and rec.tooltip ~= nil
            and raw_find(rec.tooltip, "ALL: arm or disarm", 1, true) ~= nil)
          check(TAG .. "AP2a: the ALL badge sits at (-855, -28) with its tooltip (" .. tostring(rec and rec.offset[1]) .. ", "
            .. tostring(rec and rec.offset[2]) .. ", tooltip " .. tostring(rec and rec.tooltip ~= nil) .. ")", a)
          done(a)
          a = (rec ~= nil and rec.visible == true)
          check(TAG .. "AL1a: with two selected units sharing no ability the ALL badge is SHOWN", a)
          done(a)
          click(W, "zz_auto_badge_all"); ui(W); ui(W)
          sel_event(W, b, false); sel_event(W, b + 1, false); ui(W)
          W.conflict = true
          polln(W, 8)
          local nb, nr = 0, 0
          for _, x in ipairs(W.fires) do
            if x.key == BH then nb = nb + 1 end
            if x.key == RF then nr = nr + 1 end
          end
          a = (nb >= 1 and nr >= 1)
          check(TAG .. "AL1b: one click armed both units' abilities; both fire (Book of Hoeth " .. nb .. ", Runefang " .. nr .. ")", a)
          done(a)
        end
        tally(W)
      end
    end
  end
  if RED152 then
    check("RED CONTROL (harness 152): the pre-153 build hits trash and keeps the old ALL spot - " .. n_ok .. "/" .. n_all,
      n_all == 6 and n_ok == 6)
  else
    check("HARNESS 152: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 14 and n_ok == 14)
  end
  print("== HARNESS 152 done: " .. (checks - pre152) .. " checks in this section ==")
end
