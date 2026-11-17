-- ============================================================================
-- HARNESS 168 (round 169): EVERY ENEMY READ SKIPS HIDDEN ENEMIES (user, 2026-11-17: "Yes, those too").
--   0zz17 the three new visibility lines (air drop, the 'just beyond range' read, the contact set) in both files.
--   FV1 Potion of Farsight (range 150 m, band 181.5 m): a HIDDEN enemy 140 m away (in range) and a visible one at 170 m
--       -> ONE cast (the hidden one no longer counts as 'an enemy in range').
--   FV2 the only enemy (170 m) is HIDDEN -> no cast.
--   FV3 the same enemy visible -> ONE cast.
--   AH1 Death From Above (air drop, airborne): a 20-man enemy 3 m under the centre, HIDDEN -> no cast.
--   AH2 the same enemy visible -> ONE cast.
--   RED (pre-169 = round 168): FV1 no cast, FV2 and AH1 cast.
-- ============================================================================
function run_h168()
  local L168 = os.getenv("H168_LIVE") or LIVE
  local A168 = os.getenv("H168_ANN") or ANN
  local RED168 = (os.getenv("H168_LIVE") ~= nil) or (os.getenv("H168_ANN") ~= nil)
  local FK = "wh3_main_item_abilities_potion_of_farsight"
  local HG = "wh_main_emp_inf_handgunners"
  local ZOMB = "wh_main_vmp_inf_zombie"
  local pre168 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 168 - section 0zz17: the round-169 lines ==")
  if not RED168 then
    for _, f in ipairs({ { name = "live", path = L168 }, { name = "ann", path = A168 } }) do
      local s = read_file(f.path)
      check("0zz17 " .. f.name .. ": the air drop, the 'just beyond range' read and the contact set skip hidden enemies",
        cp(s, "and FOURTH.enemy_not_hidden(enemy) then   -- ROUND 169: never a hidden enemy\n") == 2
        and cp(s, "and FOURTH.enemy_not_hidden(enemy)   -- ROUND 169: never a hidden enemy\n") == 1)
    end
  end

  local FILES = { { path = A168, tag = "[annotated] " }, { path = L168, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function hide(W, hidden)
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        local id = nil
        pcall(function() id = tostring(pr.unit:unique_ui_id()) end)
        local vis = not (hidden[id] == true)
        pr.unit.is_visible_to_alliance = function(self, a) return vis end
      end
    end
  end
  local function fires_of(W, key)
    local n = 0
    for _, x in ipairs(W.fires) do if x.key == key then n = n + 1 end end
    for _, x in ipairs(W.ground_fires or {}) do if x.key == key then n = n + 1 end end
    return n
  end
  -- Potion of Farsight: gaps = { {gap, hidden}, ... }
  local function farsight(wname, uid, gaps, PATH, TAG)
    local enemies, byt, hidden = {}, {}, {}
    for i, g in ipairs(gaps) do
      enemies[#enemies + 1] = { name = ZOMB, uid = uid + 10 + i, owns = {}, melee = false }
      byt[uid + 10 + i] = g[1]
      if g[2] then hidden[tostring(uid + 10 + i)] = true end
    end
    local d = { name = HG, uid = uid, owns = { FK }, melee = false, ammo_start = 100, ammo_seq = { 100 },
                missile_range = 150, dist_by_target = byt }
    local W = make_world({ can_perform = true, units = { d }, enemies = enemies,
      cards = { { id = tostring(uid), state = "active", vis = true } }, bar = { { id = "b1", key = FK } } })
    print("== " .. TAG .. wname .. " ==")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    hide(W, hidden)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_potion_of_farsight"); ui(W)
    sel_event(W, uid, false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  -- Death From Above: one 20-man enemy 3 m from the airborne caster's centre
  local function airdrop(wname, uid, hidden_enemy, PATH, TAG)
    local st = { r = 3 }
    local W = h118_mk(uid, uid + 1, st, 0, nil)
    print("== " .. TAG .. wname .. " ==")
    hide(W, hidden_enemy and { [tostring(uid + 1)] = true } or {})
    if not h118_boot(W, PATH, TAG, uid, wname) then return nil end
    hide(W, hidden_enemy and { [tostring(uid + 1)] = true } or {})
    polln(W, 4)
    return W
  end

  -- name, kind, args, GREEN casts, RED casts
  local WORLDS = {
    { "FV1. Farsight: a HIDDEN enemy in range (140 m), a visible one at 170 m -> ONE cast", "f", { { 140, true }, { 170, false } }, 1, 0 },
    { "FV2. Farsight: the only enemy (170 m) is HIDDEN -> no cast", "f", { { 170, true } }, 0, 1 },
    { "FV3. Farsight: the same enemy visible -> ONE cast", "f", { { 170, false } }, 1, 1 },
    { "AH1. Death From Above: a HIDDEN 20-man enemy 3 m under the centre -> no cast", "a", true, 0, 1 },
    { "AH2. Death From Above: the same enemy visible -> ONE cast", "a", false, 1, 1 },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = RED168 and w[5] or w[4]
      local uid = 33000 + i * 20
      local W, key
      if w[2] == "f" then
        W, key = farsight(w[1], uid, w[3], f.path, TAG), FK
      else
        W, key = airdrop(w[1], uid, w[3], f.path, TAG), H118_DFA
      end
      if W ~= nil then
        local got = fires_of(W, key)
        local a = (got == want)
        check(TAG .. w[1]:sub(1, 3) .. (RED168 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got, a)
        done(a)
        tally(W)
      end
    end
  end
  if RED168 then
    check("RED CONTROL (harness 168): the pre-169 build senses hidden enemies - " .. n_ok .. "/" .. n_all,
      n_all == 10 and n_ok == 10)
  else
    check("HARNESS 168: every check behaved - " .. n_ok .. "/" .. n_all, n_all == 10 and n_ok == 10)
  end
  print("== HARNESS 168 done: " .. (checks - pre168) .. " checks in this section ==")
end
