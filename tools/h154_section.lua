-- ============================================================================
-- HARNESS 154 (round 155). The ALL button sits where the user tuned it by
-- hand in battle: (-923, 0), docked bottom-centre.
--   SP1 one unit owning Book of Hoeth and Runefang is selected: the button is
--       created at (-923, 0), dock 8, and zz_all_where() reports it.
--   RED (pre-155): the button sits at the round-154 estimate (-855, -21).
-- ============================================================================
function run_h154()
  local L154 = os.getenv("H154_LIVE") or LIVE
  local A154 = os.getenv("H154_ANN") or ANN
  local RED154 = (os.getenv("H154_LIVE") ~= nil) or (os.getenv("H154_ANN") ~= nil)
  local BH = "wh2_main_item_abilities_book_of_hoeth"
  local RF = "wh_main_weapon_abilities_runefang"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local pre154 = checks

  print("== HARNESS 154 - section 0zz2: the round-155 token ==")
  if not RED154 then
    for _, f in ipairs({ { name = "live", path = L154 }, { name = "ann", path = A154 } }) do
      local s = read_file(f.path)
      check("0zz2 " .. f.name .. ": the hand-tuned ALL spot (-923, 0)",
        raw_find(s, "FOURTH.ALL_OX, FOURTH.ALL_OY = -923, 0\n", 1, true) ~= nil)
    end
  end

  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  for _, f in ipairs({ { path = A154, tag = "[annotated] " }, { path = L154, tag = "[live] " } }) do
    local TAG = f.tag
    local b = 17890
    local units = { { name = CASTER, uid = b, owns = { BH, RF }, melee = false, dist = 300 } }
    local W = make_world({ can_perform = true, units = units,
      cards = { { id = tostring(b), state = "active", vis = true } },
      bar = { { id = "b1", key = BH }, { id = "b2", key = RF } } })
    W.defaults_on = false
    print("== " .. TAG .. "SP1. the hand-tuned ALL spot ==")
    zz_all_nudge, zz_all_set, zz_all_where = nil, nil, nil
    local ok = pcall(load_world, W, f.path)
    check(TAG .. "SP1: the file loads", ok)
    if ok then
      deploy_phases(W); ui(W)
      sel_event(W, b, true); ui(W); ui(W); ui(W)
      local rec = W.badge_records["zz_auto_badge_all"]
      local ox, oy = rec and rec.offset[1], rec and rec.offset[2]
      if RED154 then
        local a = (rec ~= nil and ox == -855 and oy == -21)
        check(TAG .. "SP1-RED: the pre-155 button sits at the estimate (" .. tostring(ox) .. ", " .. tostring(oy) .. ")", a)
        done(a)
      else
        local okw, m = pcall(zz_all_where)
        local a = (rec ~= nil and ox == -923 and oy == 0 and rec.dock == 8 and okw and m == "ALL POS -923,0")
        check(TAG .. "SP1a: the ALL button sits at the tuned (-923, 0), dock 8 (" .. tostring(ox) .. ", " .. tostring(oy)
          .. ", " .. tostring(m) .. ")", a)
        done(a)
      end
      tally(W)
    end
  end
  if RED154 then
    check("RED CONTROL (harness 154): the pre-155 build keeps the estimate - " .. n_ok .. "/" .. n_all,
      n_all == 2 and n_ok == 2)
  else
    check("HARNESS 154: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 2 and n_ok == 2)
  end
  print("== HARNESS 154 done: " .. (checks - pre154) .. " checks in this section ==")
end
