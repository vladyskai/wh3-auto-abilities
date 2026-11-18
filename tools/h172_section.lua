-- ============================================================================
-- HARNESS 172 (round 173): NULL STONE AND ROCK EYE CLOSED (user, 2026-11-18: "Close Null stone, Rock Eye.").
--   0zz21 937 entries; neither marker, badge nor key left in either file.
--   NS1 a unit owning Null Stone, in melee, its badge clicked -> no cast (RED: one cast, it rode melee_unwavering).
--   RE1 the same for Rock Eye.
-- ============================================================================
function run_h172()
  local L172 = os.getenv("H172_LIVE") or LIVE
  local A172 = os.getenv("H172_ANN") or ANN
  local RED172 = (os.getenv("H172_LIVE") ~= nil) or (os.getenv("H172_ANN") ~= nil)
  local NS = "wh3_dlc27_item_abilities_null_stone"
  local RE = "wh3_main_item_passive_rock_eye"
  local pre172 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 172 - section 0zz21: the round-173 closures ==")
  if not RED172 then
    for _, f in ipairs({ { name = "live", path = L172 }, { name = "ann", path = A172 } }) do
      local s = read_file(f.path)
      check("0zz21 " .. f.name .. ": 937 entries; Null Stone and Rock Eye gone (marker, badge, key)",
        cp(s, "\t{ marker = ") == 937 and cp(s, "null_stone") == 0 and cp(s, "rock_eye") == 0)
    end
  end

  local FILES = { { path = A172, tag = "[annotated] " }, { path = L172, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local WORLDS = {
    { "NS1. Null Stone in melee, badge clicked -> no cast", NS, "null_stone" },
    { "RE1. Rock Eye in melee, badge clicked -> no cast", RE, "item_passive_rock_eye" },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local uid = 37000 + i * 20
      local units = { { name = "wh2_dlc13_emp_cha_huntsmen_general_0", uid = uid, owns = { w[2] }, melee = true,
                        dist = 5, men_alive = 1, unit_class = "com", hp_frac = 1.0 } }
      local W = make_world({ can_perform = true, units = units, enemies = {},
        cards = { { id = tostring(uid), state = "active", vis = true } }, bar = { { id = "b1", key = w[2] } } })
      W.defaults_on = false
      print("== " .. TAG .. w[1] .. " ==")
      local ok = pcall(load_world, W, f.path)
      check(TAG .. w[1] .. ": the file loads", ok)
      if ok then
        deploy_phases(W); ui(W)
        sel_event(W, uid, true); ui(W); ui(W)
        click(W, "zz_auto_badge_" .. w[3]); ui(W)
        sel_event(W, uid, false); ui(W)
        W.conflict = true
        polln(W, 3)
        local got = 0
        for _, x in ipairs(W.fires) do if x.key == w[2] then got = got + 1 end end
        local want = RED172 and 1 or 0
        local a = (got == want)
        check(TAG .. w[1]:sub(1, 3) .. (RED172 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got, a)
        done(a)
      end
      tally(W)
    end
  end
  if RED172 then
    check("RED CONTROL (harness 172): the pre-173 build still fires both - " .. n_ok .. "/" .. n_all,
      n_all == 4 and n_ok == 4)
  else
    check("HARNESS 172: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 4 and n_ok == 4)
  end
  print("== HARNESS 172 done: " .. (checks - pre172) .. " checks in this section ==")
end
