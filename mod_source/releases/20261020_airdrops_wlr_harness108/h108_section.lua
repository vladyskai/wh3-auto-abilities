-- ============================================================================
-- HARNESS 108 - THE 1 m AIR-DROP TEST BOUND AND WARP LIGHTNING ROD (round 108)
--
-- WHAT THIS SECTION PROVES, against the LIVE source AND the annotated copy:
--
--   item 1 - THE AIR-DROP BOUND IS 1 m, A USER-CHOSEN TEST VALUE:
--     0z  the constant is 1 (not 7), the family BYPASSES the 70% map
--         (if ability.trigger == "air_drop_on_infantry" then ... end), and the
--         source carries the user-chosen / edge-to-edge wording;
--     B1  an enemy 0.4 m from a flying caster FIRES at the 1 m bound and the
--         log prints distance=0.4m bound=1m;
--     B2  an enemy 3.0 m away does NOT fire (the old 7 m proxy would have);
--     B3  an enemy at EXACTLY 1.0 m fires (the bound is inclusive, <=).
--
--   item 2 - WARP LIGHTNING ROD ON SOULFIRE'S TRIGGER:
--     0z  the entry exists once, on melee_skip_commanders, carrying the ONE
--         real key (wh2_dlc16_unit_abilities_warp_lightning_rod), with its
--         60 s charge-gate row, its 1 s wind-up row, and the Clan Moulder
--         Lobotomy mutation note (the explanation for the missing carrier);
--     W1  fires vs a NON-COMMANDER enemy in contact, cast on the OWNER, and
--         logs the judged engagement set under the warp_lightning_rod marker;
--     W2  holds vs a LONE LORD - the same verdict shape as Soulfire / Call of
--         Tor (-> HOLDING (every engaged enemy is a Lord or Hero)).
--
--   COUNTS: melee_skip_commanders is now FOUR entries / FIVE keys; the table
--   is 689 entries / 742 keys.
--
-- RED CONTROL (H108_LIVE/H108_ANN -> docs/backups/round108/pre108_*.lua):
--   the pre-108 build has the 7 m air-drop bound, no WLR entry and no 1 m
--   bypass, so 0z and every B/W world fail there while the older rounds' own
--   pins (689/742/4) fail by design.
-- ============================================================================
-- RED CONTROL: setting H108_LIVE / H108_ANN points the WHOLE suite at the
-- pre-108 snapshot (docs/backups/round108/pre108_*.lua), so every older
-- section's grown-table pin fails there by design as well. The override must
-- happen BEFORE run_h107() is called, which is why the h107 call lives here.
if os.getenv("H108_LIVE") ~= nil then LIVE = os.getenv("H108_LIVE") end
if os.getenv("H108_ANN") ~= nil then ANN = os.getenv("H108_ANN") end
run_h107()

function run_h108()
  local live108 = read_file(LIVE)
  local ann_src108 = read_file(ANN)
  local pre108 = checks
  local DFA  = "wh2_dlc09_unit_abilities_death_from_above"
  local WLR  = "wh2_dlc16_unit_abilities_warp_lightning_rod"
  local INF  = "wh2_dlc13_emp_inf_spearmen_ror_0"
  local CMD  = "wh_main_emp_cha_general_0"
  local AIR_KEYS = {
    "wh2_dlc09_unit_abilities_death_from_above",
    "wh2_main_unit_abilities_drop_rocks",
    "wh2_dlc12_unit_abilities_drop_rocks_character",
    "wh2_dlc12_unit_abilities_drop_rocks_of_chotec",
    "wh2_dlc12_unit_abilities_drop_rocks_of_sundering",
    "wh2_dlc12_lord_abilities_drop_sphere_of_tepok",
    "wh2_dlc12_lord_abilities_drop_sphere_of_tepok_upgraded",
    "wh3_dlc25_unit_abilities_gyrobomber_fire_bomb",
    "wh3_dlc25_unit_abilities_thunderbarge_fire_bomb",
    "wh_main_unit_abilities_gyrobomber_bomb",
    "wh_main_unit_abilities_gyrocopter_bomb",
    "wh3_dlc25_unit_abilities_gyrocopter_bomb_anti_large",
    "wh3_main_unit_abilities_sky_junk_bomb",
    "wh_dlc06_unit_abilities_skyhammer_bomb",
    "wh_dlc06_unit_abilities_skyhammer_fire_bomb",
    "wh2_main_unit_abilities_wake_of_fire",
    "wh3_twa07_unit_abilities_searing_torrent",
    "wh3_dlc24_unit_abilities_nan_gau_grenades",
    "wh3_dlc29_unit_abilities_undeath_from_above",
  }

  local function cp108(s2, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s2, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function span108(s2, head, tail2)
    local i = raw_find(s2, head, 1, true)
    if i == nil then return nil end
    local j = raw_find(s2, tail2, i, true)
    if j == nil then return nil end
    return s2:sub(i, j)
  end
  local function lg108(cond) return cond == true end
  local function stub_inf108(W, uid, val)
    local u = unit_of(W, uid)
    if u == nil and W.enemy_entries ~= nil then
      for i = 1, #W.enemy_entries do
        local pr = W.enemy_entries[i]
        if pr ~= nil and pr.unit ~= nil then
          local ok, id = pcall(function() return pr.unit:unique_ui_id() end)
          if ok and tostring(id) == tostring(uid) then u = pr.unit end
        end
      end
    end
    if u == nil then return end
    if val == "raise" then
      u.is_infantry = function() error("mock: is_infantry refused", 0) end
    else
      local b = (val == true)
      u.is_infantry = function() return b end
    end
  end
  local function stub_fly108(W, uid, val)
    local u = unit_of(W, uid)
    if u == nil then return end
    local b = (val == true)
    u.is_currently_flying = function() return b end
  end
  local function mk108(uid, def, enemies, extra)
    def.name = def.name or "air_caster"
    def.uid = uid
    local owns = def.owns or { DFA }
    def.owns = owns
    local bar = {}
    for i = 1, #owns do bar[i] = { id = "b" .. i, key = owns[i] } end
    local o = { can_perform = true,
      units = { def },
      enemies = enemies,
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = bar }
    if extra ~= nil then for k, v in pairs(extra) do o[k] = v end end
    return make_world(o)
  end
  local function boot108(W, PATH, TAG, uid, marker, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. marker); ui(W)
    W.conflict = true
    return true
  end

  -- ==========================================================================
  print("== HARNESS 108 - section 0z: the round's tokens in the source (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live108 }, { name = "ann", src = ann_src108 } }) do
    local nm, s2 = f.name, f.src
    if RED_MODE then
      check("0z " .. nm .. " (RED): the pre-108 build still carries the 7 m bound and no WLR entry",
        raw_find(s2, "FOURTH.AIR_DROP_BOUND_M = 7", 1, true) ~= nil
        and cp108(s2, "warp_lightning_rod") == 0)
    else
      -- ---------------------------------------------------------- item 1
      check("0z " .. nm .. ": the air-drop bound constant is 1 m",
        raw_find(s2, "FOURTH.AIR_DROP_BOUND_M = 1", 1, true) ~= nil
        and raw_find(s2, "FOURTH.AIR_DROP_BOUND_M = 7", 1, true) == nil)
      local byp = span108(s2, 'if ability.evaluate == FOURTH.evaluate_air_drop_on_infantry then', "\n\tend")
      check("0z " .. nm .. ": the family BYPASSES the 70% map and takes the one constant",
        byp ~= nil and raw_find(byp, "ability.range_m = FOURTH.AIR_DROP_BOUND_M", 1, true) ~= nil)
      check("0z " .. nm .. ": the source calls 1 m a USER-CHOSEN TEST value, much tighter than 70%",
        (raw_find(s2, "USER-CHOSEN TEST", 1, true) ~= nil
          or raw_find(s2, "USER'S OWN TEST VALUE", 1, true) ~= nil
          or raw_find(s2, "user's own TEST VALUE", 1, true) ~= nil)
        and raw_find(s2, "MUCH TIGHTER", 1, true) ~= nil)
      check("0z " .. nm .. ": and states that unit_distance is EDGE-TO-EDGE (a unit on top reads 0-5 m)",
        raw_find(s2, "EDGE-TO-EDGE", 1, true) ~= nil
        and raw_find(s2, "0-5 m", 1, true) ~= nil)
      check("0z " .. nm .. ": the source says the 1 m value is one constant to bump",
        raw_find(s2, "ONE constant", 1, true) ~= nil
        and raw_find(s2, "never fires in the field", 1, true) ~= nil)
      check("0z " .. nm .. ": all 19 air-drop keys are still present and the family is 12 entries",
        cp108(s2, 'trigger = "air_drop_on_infantry"') == 12
        and (function()
          local miss = 0
          for i = 1, #AIR_KEYS do
            if cp108(s2, '"' .. AIR_KEYS[i] .. '"') == 0 then miss = miss + 1 end
          end
          return miss
        end)() == 0)

      -- ---------------------------------------------------------- item 2
      local wlr = span108(s2, '-- ROUND 108 (item 2): WARP LIGHTNING ROD', "ox = 0, oy = 0 },")
      check("0z " .. nm .. ": Warp Lightning Rod is ONE entry on melee_skip_commanders",
        wlr ~= nil
        and raw_find(wlr, 'trigger = "melee_skip_commanders"', 1, true) ~= nil
        and cp108(wlr, WLR) == 1)
      check("0z " .. nm .. ": its entry is SELF-CENTRED like Soulfire (no air-drop flag at all)",
        wlr ~= nil and raw_find(wlr, "air_only", 1, true) == nil
        and raw_find(wlr, "no_melee", 1, true) == nil)
      check("0z " .. nm .. ": FOUR entries / FIVE keys now ride melee_skip_commanders",
        cp108(s2, 'trigger = "melee_skip_commanders"') == 4)
      check("0z " .. nm .. ": the charge gate holds its 60 s recharge (3 uses)",
        cp108(s2, '["' .. WLR .. '"] = 60,') == 1)
      check("0z " .. nm .. ": the in-flight gate carries its 1 s wind-up",
        cp108(s2, '["' .. WLR .. '"] = 1,') == 1)
      check("0z " .. nm .. ": the entry records the Clan Moulder LOBOTOMY mutation grant",
        wlr ~= nil and raw_find(wlr, "Clan Moulder", 1, true) ~= nil
        and raw_find(wlr, "LOBOTOMY", 1, true) ~= nil
        and raw_find(wlr, "mutation", 1, true) ~= nil)
      check("0z " .. nm .. ": and says it is NOT a default unit ability (no carrier junction)",
        wlr ~= nil and raw_find(wlr, "NOT a default", 1, true) ~= nil
        and raw_find(wlr, "NO carrier", 1, true) ~= nil)
      -- the key must NOT be in the ground-key set nor inside the air-drop family
      local g0 = raw_find(s2, "enemy_ground_keys = {", 1, true)
      local g1 = raw_find(s2, "\t},\n", g0, true)
      check("0z " .. nm .. ": WLR is not a ground-targeted key",
        g0 ~= nil and g1 ~= nil and g1 > g0
        and raw_find(s2:sub(g0, g1), "[" .. '"' .. WLR .. '"' .. "] = true", 1, true) == nil)
      check("0z " .. nm .. ": every air-drop entry still carries its own usage flags",
        cp108(s2, "air_only = true,") == 10 and cp108(s2, "air_only = false,") == 2)
    end
  end

  -- ==========================================================================
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag

    -- B1: 0.4 m under a flying caster -> FIRES at the 1 m bound.
    do
      local uid = 11801
      local W = mk108(uid, { melee = false, dist_by_target = { [11810] = 0.4 } },
        { { name = INF, uid = 11810, melee = true } })
      stub_inf108(W, 11810, true); stub_fly108(W, uid, true)
      print("== B1 " .. TAG .. "== ")
      if boot108(W, PATH, TAG, uid, "death_from_above", "B1") then
        polln(W, 2)
        check(TAG .. "B1a: a unit 0.4 m under the caster fires at the 1 m bound (fires " .. #W.fires .. ")",
          #W.fires == 1 and W.fires[1].key == DFA)
        check(TAG .. "B1b: the cast is on the OWNER",
          #W.fires == 1 and W.fires[1].target == unit_of(W, uid))
        check(TAG .. "B1c: the log line prints the real 0.4 m gap and the 1 m bound [live log]",
          lg108((TAG ~= "[live] ")
            or (count_log(W, "distance=0.4m bound=1m") >= 1
              and count_log(W, "pre-cast re-check: still over an INFANTRY enemy") == 1)))
        tally(W)
      end
    end

    -- B2: 3.0 m away -> SILENT (the old 7 m proxy would have fired).
    do
      local uid = 11802
      local W = mk108(uid, { melee = false, dist_by_target = { [11811] = 3.0 } },
        { { name = INF, uid = 11811, melee = true } })
      stub_inf108(W, 11811, true); stub_fly108(W, uid, true)
      print("== B2 " .. TAG .. "== ")
      if boot108(W, PATH, TAG, uid, "death_from_above", "B2") then
        polln(W, 3)
        check(TAG .. "B2a: 3 m is OUTSIDE the 1 m bound - no fire (" .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "B2b: and nothing is attempted [live log]",
          lg108((TAG ~= "[live] ") or count_log(W, "ATTEMPT death_from_above") == 0))
        tally(W)
      end
    end

    -- B3: EXACTLY 1.0 m -> FIRES (the bound is inclusive).
    do
      local uid = 11803
      local W = mk108(uid, { melee = false, dist_by_target = { [11812] = 1.0 } },
        { { name = INF, uid = 11812, melee = true } })
      stub_inf108(W, 11812, true); stub_fly108(W, uid, true)
      print("== B3 " .. TAG .. "== ")
      if boot108(W, PATH, TAG, uid, "death_from_above", "B3") then
        polln(W, 2)
        check(TAG .. "B3a: exactly 1.0 m is INSIDE the bound - it fires (" .. #W.fires .. ")",
          #W.fires == 1 and W.fires[1].key == DFA)
        check(TAG .. "B3b: the boundary line reads distance=1.0m bound=1m [live log]",
          lg108((TAG ~= "[live] ") or count_log(W, "distance=1.0m bound=1m") >= 1))
        tally(W)
      end
    end

    -- W1: Warp Lightning Rod vs a NON-COMMANDER in contact -> FIRES.
    do
      local uid = 11804
      local W = mk108(uid, { owns = { WLR }, melee = true, dist_by_target = { [11813] = 2.0 } },
        { { name = INF, uid = 11813, melee = true } })
      print("== W1 " .. TAG .. "== ")
      if boot108(W, PATH, TAG, uid, "warp_lightning_rod", "W1") then
        polln(W, 1)
        check(TAG .. "W1a: Warp Lightning Rod fires vs a non-commander in contact (" .. #W.fires .. ")",
          #W.fires == 1 and W.fires[1].key == WLR)
        check(TAG .. "W1b: the cast is on the OWNER (self-centred, like Soulfire)",
          #W.fires == 1 and W.fires[1].target == unit_of(W, uid))
        check(TAG .. "W1c: the judged engagement set is logged under its own marker [live log]",
          lg108((TAG ~= "[live] ")
            or count_log(W, "warp_lightning_rod engagement set: 1 enemy unit(s) in contact") == 1))
        tally(W)
      end
    end

    -- W2: Warp Lightning Rod with ONLY a Lord/Hero in contact -> SILENT.
    do
      local uid = 11805
      local W = mk108(uid, { owns = { WLR }, melee = true, dist_by_target = { [11814] = 1.0 } },
        { { name = CMD, uid = 11814, melee = true } })
      print("== W2 " .. TAG .. "== ")
      if boot108(W, PATH, TAG, uid, "warp_lightning_rod", "W2") then
        polln(W, 3)
        check(TAG .. "W2a: a lone Lord/Hero never fires Warp Lightning Rod (" .. #W.fires .. ")",
          #W.fires == 0)
        check(TAG .. "W2b: the HOLDING verdict is logged under the WLR marker [live log]",
          lg108((TAG ~= "[live] ")
            or (count_log(W, "warp_lightning_rod engagement set") == 1
              and count_log(W, "-> HOLDING (every engaged enemy is a Lord or Hero)") == 1)))
        check(TAG .. "W2c: nothing is attempted [live log]",
          lg108((TAG ~= "[live] ") or count_log(W, "ATTEMPT warp_lightning_rod") == 0))
        tally(W)
      end
    end
  end

  -- ==========================================================================
  if RED_MODE then
    check("HARNESS 107 suite boundary (harness 108): N/A in the red run - the pre-108 snapshot "
      .. "carries every harness-107 world unchanged", true)
  else
    check("HARNESS 107 suite boundary (harness 108): every harness-107 check ran first ("
      .. pre108 .. ", want 3938)", pre108 == 3938)
  end
  print("== HARNESS 108 done: checks " .. checks .. ", failures " .. failures .. " ==")
end
run_h108()
