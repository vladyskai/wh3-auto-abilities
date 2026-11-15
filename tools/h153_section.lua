-- ============================================================================
-- HARNESS 153 (round 154). The ALL control becomes the game's own round
-- toggle button (user ruling 2026-11-15, "Game round button").
--   BT1 one unit owning Book of Hoeth and Runefang is selected: the ALL control
--       is built from ui/templates/round_small_button_toggle with the game's
--       abilities icon in image 0, no letters, no resize, at (-855, -21),
--       bottom-centre docked, with the tooltip that names the pressed look.
--   BT2 the pressed look follows the arming: not pressed while nothing is armed;
--       pressed after the ALL click; the engine's own hover look is never
--       overwritten (selected_hover stays, hover stays); released after the
--       second click; one ability armed by its own badge = not pressed; both
--       armed by their own badges = pressed.
--   BT3 the Lua Console hooks: zz_all_nudge(5, -3), zz_all_set(-900, 10) and
--       zz_all_where() move the control at once and report "ALL POS x,y"
--       (the live copy also logs it).
--   RED (pre-154): BT1 built from the text-badge template; BT2 never pressed;
--       BT3 no hooks.
-- ============================================================================
function run_h153()
  local L153 = os.getenv("H153_LIVE") or LIVE
  local A153 = os.getenv("H153_ANN") or ANN
  local RED153 = (os.getenv("H153_LIVE") ~= nil) or (os.getenv("H153_ANN") ~= nil)
  local BH = "wh2_main_item_abilities_book_of_hoeth"
  local RF = "wh_main_weapon_abilities_runefang"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local TEMPLATE = "ui/templates/round_small_button_toggle"
  local ICON = "ui/skins/default/icon_abilities.png"
  local PRESSED = { selected = true, selected_hover = true, selected_down = true, selected_down_off = true,
    selected_inactive = true }
  local pre153 = checks

  print("== HARNESS 153 - section 0zz: the round-154 tokens ==")
  if not RED153 then
    for _, f in ipairs({ { name = "live", path = L153 }, { name = "ann", path = A153 } }) do
      local s = read_file(f.path)
      check("0zz " .. f.name .. ": the round button, its icon, the pressed sync, the console hooks, no ALL letters",
        raw_find(s, 'FOURTH.ALL_TEMPLATE = "' .. TEMPLATE .. '"', 1, true) ~= nil
        and raw_find(s, 'FOURTH.ALL_ICON = "' .. ICON .. '"', 1, true) ~= nil
        and raw_find(s, "FOURTH.ALL_OX, FOURTH.ALL_OY = -855, -21\n", 1, true) ~= nil
        and raw_find(s, "if any then FOURTH.all_sync_pressed(st) end", 1, true) ~= nil
        and raw_find(s, "function zz_all_nudge(dx, dy)", 1, true) ~= nil
        and raw_find(s, "function zz_all_set(x, y)", 1, true) ~= nil
        and raw_find(s, "function zz_all_where()", 1, true) ~= nil
        and raw_find(s, 'write_badge_letter(st, "ALL")', 1, true) == nil)
    end
  end

  local FILES = { { path = A153, tag = "[annotated] ", live = false }, { path = L153, tag = "[live] ", live = true } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function pressed(rec) return rec ~= nil and PRESSED[tostring(rec.state)] == true end
  local function new_world(TAG, wname, PATH, b)
    local units = { { name = CASTER, uid = b, owns = { BH, RF }, melee = false, dist = 300 } }
    local W = make_world({ can_perform = true, units = units,
      cards = { { id = tostring(b), state = "active", vis = true } },
      bar = { { id = "b1", key = BH }, { id = "b2", key = RF } } })
    W.defaults_on = false
    print("== " .. TAG .. wname .. " ==")
    zz_all_nudge, zz_all_set, zz_all_where = nil, nil, nil   -- a hook must come from THIS file
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then return nil end
    deploy_phases(W); ui(W)
    sel_event(W, b, true); ui(W); ui(W); ui(W)
    return W
  end

  for _, f in ipairs(FILES) do
    local TAG = f.tag
    -- BT1: the look
    local W = new_world(TAG, "BT1. the ALL control is the game's round button", f.path, 17790)
    if W ~= nil then
      local rec = W.badge_records["zz_auto_badge_all"]
      if RED153 then
        local a = (rec ~= nil and rec.layout ~= TEMPLATE)
        check(TAG .. "BT1-RED: the pre-154 control is built from " .. tostring(rec and rec.layout), a)
        done(a)
      else
        local a = (rec ~= nil and rec.layout == TEMPLATE and rec.images[0] == ICON and rec.text == nil
          and rec.resize_calls == 0 and rec.offset[1] == -855 and rec.offset[2] == -21 and rec.dock == 8
          and rec.visible == true and rec.tooltip ~= nil
          and raw_find(rec.tooltip, "The button stays pressed while all of them are on A.", 1, true) ~= nil)
        check(TAG .. "BT1a: round toggle template, the abilities icon in image 0, no letters, no resize, (-855, -21)"
          .. " dock 8, shown, tooltip (" .. tostring(rec and rec.layout) .. ", " .. tostring(rec and rec.images[0])
          .. ", text " .. tostring(rec and rec.text) .. ", resize " .. tostring(rec and rec.resize_calls) .. ", "
          .. tostring(rec and rec.offset[1]) .. ", " .. tostring(rec and rec.offset[2]) .. ")", a)
        done(a)
      end
      tally(W)
    end

    -- BT2: the pressed look
    W = new_world(TAG, "BT2. the pressed look follows the arming", f.path, 17791)
    if W ~= nil then
      local rec = W.badge_records["zz_auto_badge_all"]
      if RED153 then
        click(W, "zz_auto_badge_all"); ui(W); ui(W)
        local a = (rec ~= nil and not pressed(rec))
        check(TAG .. "BT2-RED: the pre-154 control never looks pressed (state " .. tostring(rec and rec.state) .. ")", a)
        done(a)
      else
        local a = (rec ~= nil and not pressed(rec))
        check(TAG .. "BT2a: nothing armed, not pressed (state " .. tostring(rec and rec.state) .. ")", a)
        done(a)
        click(W, "zz_auto_badge_all"); ui(W); ui(W)
        a = (rec ~= nil and rec.state == "selected")
        check(TAG .. "BT2b: after the ALL click (both armed) it is pressed (state " .. tostring(rec and rec.state) .. ")", a)
        done(a)
        rec.state = "selected_hover"; ui(W); ui(W)        -- the engine's hover look on a pressed button
        a = (rec.state == "selected_hover")
        check(TAG .. "BT2c: the engine's pressed-hover look is left alone (state " .. tostring(rec.state) .. ")", a)
        done(a)
        rec.state = "selected"
        click(W, "zz_auto_badge_all"); ui(W); ui(W)
        a = (rec.state == "active")
        check(TAG .. "BT2d: after the second ALL click (both disarmed) it is released (state " .. tostring(rec.state) .. ")", a)
        done(a)
        rec.state = "hover"; ui(W); ui(W)                  -- the engine's hover look on a released button
        a = (rec.state == "hover")
        check(TAG .. "BT2e: the engine's hover look is left alone (state " .. tostring(rec.state) .. ")", a)
        done(a)
        rec.state = "active"
        click(W, "zz_auto_badge_book_of_hoeth"); ui(W); ui(W)
        local lb = W.badge_records["zz_auto_badge_book_of_hoeth"]
        a = (lb ~= nil and lb.text == "A" and not pressed(rec))
        check(TAG .. "BT2f: one ability armed by its own badge, not pressed (Book of Hoeth " .. tostring(lb and lb.text)
          .. ", state " .. tostring(rec.state) .. ")", a)
        done(a)
        click(W, "zz_auto_badge_runefang"); ui(W); ui(W)
        local lr = W.badge_records["zz_auto_badge_runefang"]
        a = (lr ~= nil and lr.text == "A" and rec.state == "selected")
        check(TAG .. "BT2g: both armed by their own badges, pressed (Runefang " .. tostring(lr and lr.text)
          .. ", state " .. tostring(rec.state) .. ")", a)
        done(a)
      end
      tally(W)
    end

    -- BT3: the Lua Console hooks
    W = new_world(TAG, "BT3. the Lua Console hooks", f.path, 17792)
    if W ~= nil then
      local rec = W.badge_records["zz_auto_badge_all"]
      if RED153 then
        local a = (zz_all_nudge == nil and zz_all_set == nil and zz_all_where == nil)
        check(TAG .. "BT3-RED: the pre-154 build has no zz_all_* hooks", a)
        done(a)
      else
        local okn, m1 = pcall(zz_all_nudge, 5, -3)
        local a = (okn and m1 == "ALL POS -850,-24" and rec ~= nil and rec.offset[1] == -850 and rec.offset[2] == -24)
        check(TAG .. "BT3a: zz_all_nudge(5, -3) moves it to -850,-24 (" .. tostring(m1) .. ")", a)
        done(a)
        local oks, m2 = pcall(zz_all_set, -900, 10)
        a = (oks and m2 == "ALL POS -900,10" and rec.offset[1] == -900 and rec.offset[2] == 10)
        check(TAG .. "BT3b: zz_all_set(-900, 10) puts it at -900,10 (" .. tostring(m2) .. ")", a)
        done(a)
        local okw, m3 = pcall(zz_all_where)
        a = (okw and m3 == "ALL POS -900,10" and rec.offset[1] == -900 and rec.offset[2] == 10)
        check(TAG .. "BT3c: zz_all_where() reports -900,10 and moves nothing (" .. tostring(m3) .. ")", a)
        done(a)
        if f.live then
          local n = 0
          for _, l in ipairs(W.log_lines) do
            if raw_find(l, "ALL POS -900,10", 1, true) ~= nil then n = n + 1 end
          end
          a = (n == 2)
          check(TAG .. "BT3d: the live log carries the reported spot (" .. n .. " line(s), want 2)", a)
          done(a)
        end
      end
      tally(W)
    end
  end
  if RED153 then
    check("RED CONTROL (harness 153): the pre-154 build keeps the text badge, never pressed, no hooks - " .. n_ok
      .. "/" .. n_all, n_all == 6 and n_ok == 6)
  else
    check("HARNESS 153: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 23 and n_ok == 23)
  end
  print("== HARNESS 153 done: " .. (checks - pre153) .. " checks in this section ==")
end
