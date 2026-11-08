-- ============================================================================
-- HARNESS 113 - THE PATH TEST, THE DERIVED FRONTAGE AND THE SINGLE-ENTITY
-- EXCLUSION (round 113).
--
-- THE FIELD REPORT (the user, with a screenshot): a Sky-junk hovering BESIDE a
-- 20-model zombie block never fired while the block walked past - the enemy's
-- CENTRE stayed 10+ m away even though its models swept under the caster; and
-- separately one fired at a LORD, which must be excluded.
--
-- THE USER'S RULINGS, verbatim:
--   "1. Why combine? The started with one model would cover the other case,
--    woudn't it? Also, why comparison is 1 or less? It cannot be less, then the
--    unit does not exist. So comparion should be equal to 1. Am I forgetting
--    something? If you agree, start implementing with point 2."
--   "2. Let's implement the the path test with a derived frontage that you
--    suggest."
--
-- THE RULE NOW:
--     segment = enemy_current -> enemy_projected      (the enemy's own dials)
--     perp    = shortest horizontal distance from that SEGMENT to the CASTER's
--               projected point
--     fire when perp <= AIR_DROP_CENTER_M + ad_frontage(enemy)
-- and a candidate whose initial_number_of_men() is EXACTLY 1 is skipped.
--
-- PINS (asserted against BOTH files in section 0, so a silent retune fails):
--     BOUND            AIR_DROP_CENTER_M         = 6 m    (unchanged)
--     DELAY            AIR_DROP_DELAY_S          = 1.5 s  (unchanged)
--     ENEMY_LEAD       AIR_DROP_ENEMY_LEAD       = 0.3    (unchanged)
--     C_CASTER_DELAY   AIR_DROP_CASTER_DELAY_S   = 1.5 s  (unchanged)
--     C_CASTER_LEAD    AIR_DROP_CASTER_LEAD      = 0.5    (unchanged)
--     INHERIT          AIR_DROP_INHERIT          = false  (unchanged)
--     MODEL_RADIUS     AIR_DROP_MODEL_RADIUS_M   = 0.6 m  (NEW)
--     RANKS            AIR_DROP_RANKS            = 2      (NEW)
--     FRONTAGE_MIN/MAX AIR_DROP_FRONTAGE_MIN/MAX = 1 / 12 (NEW, half-width)
--
-- PER-WORLD ARITHMETIC (the caster is parked at (100, 30, 200) in every world,
-- so its projected point is (100, 200); the enemy lead is the shipped 0.3, i.e.
-- the projected leg is 0.45 s of the enemy's travel):
--   A1  the FIELD CASE: a 20-model block whose centre is 10.05 m to the side
--       (110, 201) walking -x at 2.3 m/s -> projected (108.965, 201); perp
--       9.02 m; frontage 6.00 (models) -> threshold 12.00 -> FIRES. The point
--       test (projected centre 9.02 m > 6 m) was SILENT - the reported bug.
--   A2  the same geometry with ONE alive model (a depleted block): frontage
--       0.00 -> threshold 6.00 -> SILENT. Proof that A1 was the CREDIT.
--   A3  the PATH alone: an enemy 1 m from the drop point running away at
--       22.2 m/s -> its leg crosses the point (perp 0.00 m) while its projected
--       point is 8.99 m away -> FIRES. The point test could never see this.
--   B   a LORD (initial_number_of_men = 1) -> SILENT, ONE
--       `single entity (1 model)` line for the whole episode.
--   C   a 20-model block 15 m to the side -> perp 15.00 m > 12.00 -> SILENT.
--   D1  ordered_width 24 -> half 12.00 (source `ordered`) -> threshold 18.00,
--       perp 12.20 -> FIRES ; D2 the SAME geometry with no width -> half 6.00
--       (source `models`) -> threshold 12.00 -> SILENT (12.20 > 12.00);
--       D3 ordered_width 60 -> half 30 -> CLAMPED to 12.00 -> FIRES.
--   E1  ordered_width() raises -> the MODELS still decide (source `models`);
--       E2 ordered_width() raises AND the alive count is gone at the re-check ->
--       frontage 0.00, source `unreadable`, threshold 6.00 (fail-closed).
--   F   DRIFT: picked at perp 9.02, then the block is 30 m away at the re-check
--       -> perp 30.02 m > 12.00 -> SKIPPED, cast not spent.
--   G   a DEPLETED 20-model block (1 alive, initial 20) is NOT a single entity:
--       no skip line, and it fires at 5.00 m.
--
-- RED CONTROL (H113_LIVE / H113_ANN -> docs/backups/round113/pre113_*.lua, the
-- round-112 build): there is no ad_frontage, no ad_seg_dist and no single-entity
-- guard, so every 0 check and every A-G world fails as designed.
-- ============================================================================
function run_h113()
  if os.getenv("H113_LIVE") ~= nil then LIVE = os.getenv("H113_LIVE") end
  if os.getenv("H113_ANN") ~= nil then ANN = os.getenv("H113_ANN") end
  local red113 = (os.getenv("H113_LIVE") ~= nil) or (os.getenv("H113_ANN") ~= nil)
  local live_src = read_file(LIVE)
  local ann_src = read_file(ANN)
  local pre113 = checks
  local DFA = "wh2_dlc09_unit_abilities_death_from_above"
  local INF = "wh2_dlc13_emp_inf_spearmen_ror_0"

  -- THE PINS
  local PIN_BOUND, PIN_DELAY, PIN_ELEAD = 6.0, 1.5, 0.3
  local PIN_CDELAY, PIN_CLEAD = 1.5, 0.5
  local PIN_RADIUS, PIN_RANKS = 0.6, 2
  local PIN_FMIN, PIN_FMAX = 1.0, 12.0

  local function cp(s2, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s2, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function span(s2, head, tail2)
    local i = raw_find(s2, head, 1, true)
    if i == nil then return nil end
    local j = raw_find(s2, tail2, i, true)
    if j == nil then return nil end
    return s2:sub(i, j)
  end
  local function lg(cond) return cond == true end
  local function cl(W, frag) return count_log(W, frag) end
  local function enemy_of(W, uid)
    if W.enemy_entries == nil then return nil end
    for i = 1, #W.enemy_entries do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        local ok, id = pcall(function() return pr.unit:unique_ui_id() end)
        if ok and tostring(id) == tostring(uid) then return pr.unit end
      end
    end
    return nil
  end
  local function inf(W, uid, v)
    local e = enemy_of(W, uid)
    if e == nil then return end
    e.is_infantry = function() return v == true end
  end
  local function fly(W, uid, v)
    local u = unit_of(W, uid)
    if u == nil then return nil end
    u.is_currently_flying = function() return v == true end
    return u
  end
  local function mk(uid, def, enemies)
    def.name = def.name or "sky_junk"
    def.uid = uid
    def.owns = def.owns or { DFA }
    local bar = {}
    for i = 1, #def.owns do bar[i] = { id = "b" .. i, key = def.owns[i] } end
    return make_world({ can_perform = true, units = { def }, enemies = enemies,
      cards = { { id = tostring(uid), state = "active", vis = true } }, bar = bar })
  end
  local function boot(W, PATH, TAG, uid, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_death_from_above"); ui(W)
    W.conflict = true
    return true
  end

  -- ==========================================================================
  print("== HARNESS 113 - section 0: the pins and the new helpers, in the source (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src }, { name = "ann", src = ann_src } }) do
    local nm, s2 = f.name, f.src
    local fr = span(s2, "function FOURTH.ad_frontage(unit, men_now)", "\nfunction FOURTH.ad_frontage_text")
    local sg = span(s2, "function FOURTH.ad_seg_dist(px, pz, ax, az, bx, bz)", "\nend")
    local pick = span(s2, "function FOURTH.ad_pick(unit, routing)",
      "\nfunction FOURTH.evaluate_air_drop_on_infantry")
    local rech = span(s2, "if FOURTH.ad_enemy ~= nil then", "\n\t-- SELF-SUMMON RE-CHECK")

    check("0 " .. nm .. ": the SIX older pins are untouched and single (bound 6, delay 1.5, enemy lead 0.3, caster 1.5 / 0.5, inherit false)",
      cp(s2, "\nFOURTH.AIR_DROP_CENTER_M = " .. string.format("%.0f", PIN_BOUND) .. "\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_DELAY_S = " .. string.format("%.1f", PIN_DELAY) .. "\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_ENEMY_LEAD = " .. string.format("%.1f", PIN_ELEAD) .. "\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_CASTER_DELAY_S = " .. string.format("%.1f", PIN_CDELAY) .. "\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_CASTER_LEAD = " .. string.format("%.1f", PIN_CLEAD) .. "\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_INHERIT = false\n") == 1)
    check("0 " .. nm .. ": the FOUR new frontage pins are defined EXACTLY ONCE (radius 0.6, ranks 2, min 1, max 12)",
      cp(s2, "\nFOURTH.AIR_DROP_MODEL_RADIUS_M = " .. string.format("%.1f", PIN_RADIUS) .. "\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_RANKS = " .. string.format("%.0f", PIN_RANKS) .. "\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_FRONTAGE_MIN_M = " .. string.format("%.0f", PIN_FMIN) .. "\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_FRONTAGE_MAX_M = " .. string.format("%.0f", PIN_FMAX) .. "\n") == 1)
    check("0 " .. nm .. ": ad_frontage exists and is FAIL-CLOSED (unreadable -> 0)",
      fr ~= nil and raw_find(fr, 'return 0, "unreadable"', 1, true) ~= nil)
    check("0 " .. nm .. ": ad_frontage prefers ordered_width() (halved) and names the source `ordered`",
      fr ~= nil and raw_find(fr, "unit:ordered_width()", 1, true) ~= nil
      and raw_find(fr, "local half = w * 0.5", 1, true) ~= nil
      and raw_find(fr, 'return half, "ordered"', 1, true) ~= nil)
    check("0 " .. nm .. ": and falls back to the MODEL COUNT under the documented two-rank assumption",
      fr ~= nil and raw_find(fr, "math.ceil(men / FOURTH.AIR_DROP_RANKS)", 1, true) ~= nil
      and raw_find(fr, "FOURTH.AIR_DROP_MODEL_RADIUS_M", 1, true) ~= nil
      and raw_find(fr, 'return half, "models"', 1, true) ~= nil)
    check("0 " .. nm .. ": a ONE-MODEL unit gets ZERO frontage (a point has no width)",
      fr ~= nil and raw_find(fr, "if men < 2 then", 1, true) ~= nil
      and raw_find(fr, 'return 0, "single"', 1, true) ~= nil)
    check("0 " .. nm .. ": the derived value is CLAMPED to the pinned 1 .. 12 m range, source `clamped`",
      fr ~= nil and cp(fr, 'return clamped, "clamped"') == 1
      and cp(fr, 'FOURTH.AIR_DROP_FRONTAGE_MAX_M, "clamped"') == 1
      and cp(fr, 'FOURTH.AIR_DROP_FRONTAGE_MIN_M, "clamped"') == 1)
    check("0 " .. nm .. ": ad_seg_dist is the point-to-segment distance with the parameter CLAMPED to 0..1",
      sg ~= nil and raw_find(sg, "local t = ((px - ax) * dx + (pz - az) * dz) / len2", 1, true) ~= nil
      and raw_find(sg, "if t < 0 then", 1, true) ~= nil
      and raw_find(sg, "elseif t > 1 then", 1, true) ~= nil
      and raw_find(sg, "return FOURTH.ad_sep(px, pz, ax, az), 0", 1, true) ~= nil)
    check("0 " .. nm .. ": the PICKER gates on the perpendicular distance vs bound + frontage",
      pick ~= nil
      and raw_find(pick, "local perp = FOURTH.ad_seg_dist(best_ipx, best_ipz, ex, ez, epx, epz)", 1, true) ~= nil
      and raw_find(pick, "local eff = bound + half", 1, true) ~= nil
      and raw_find(pick, "if perp <= eff and", 1, true) ~= nil
      and raw_find(pick, "FOURTH.ad_frontage(enemy, alive)", 1, true) ~= nil)
    check("0 " .. nm .. ": the single-entity guard is EXACT EQUALITY on initial_number_of_men()",
      pick ~= nil and raw_find(pick, "enemy:initial_number_of_men()", 1, true) ~= nil
      and raw_find(pick, "elseif im == 1 then", 1, true) ~= nil
      and raw_find(pick, "im <= 1", 1, true) == nil)
    check("0 " .. nm .. ": and the guard FAILS CLOSED on an unreadable count (no candidate, no guess)",
      pick ~= nil and raw_find(pick, "if not ok_im or type(im) ~= \"number\" then", 1, true) ~= nil
      and raw_find(pick, 'se_state = "unreadable"', 1, true) ~= nil)
    check("0 " .. nm .. ": the COMMANDER key set is NOT consulted by this evaluator (the model count covers it)",
      pick ~= nil and raw_find(pick, "FOURTH.enemy_is_commander", 1, true) == nil
      and raw_find(s2, "THE COMMANDER KEY SET IS DELIBERATELY NOT USED HERE", 1, true) ~= nil)
    check("0 " .. nm .. ": the pre-cast re-check RE-RUNS the same segment test on fresh reads",
      rech ~= nil and raw_find(rech, "FOURTH.ad_lead(enemy, ad_t_now, false)", 1, true) ~= nil
      and raw_find(rech, "FOURTH.ad_seg_dist(upx, upz, ex2, ez2, epx, epz)", 1, true) ~= nil
      and raw_find(rech, "FOURTH.ad_frontage(enemy, (ok_ea and ea) or nil)", 1, true) ~= nil
      and raw_find(rech, "local in_bound_now = (perp_now ~= nil and perp_now <= eff_now)", 1, true) ~= nil)
    check("0 " .. nm .. ": the DERIVATION is documented in the source (two ranks, the modal radius, the clamp)",
      raw_find(s2, "TWO RANKS DEEP", 1, true) ~= nil
      and raw_find(s2, "battle_entities.radius is 0.6 m (168 rows)", 1, true) ~= nil
      and raw_find(s2, "1 .. 12 m HALF-width", 1, true) ~= nil
      and raw_find(s2, "A POINT COULD NOT DESCRIBE A BLOCK", 1, true) ~= nil)
    check("0 " .. nm .. ": air_only / no_melee / the self-centred cast / fail-closed are ALL still in place",
      raw_find(s2, "is_currently_flying()", 1, true) ~= nil
      and raw_find(s2, "is_in_melee()", 1, true) ~= nil
      and raw_find(s2, "FOURTH.ad_air_only", 1, true) ~= nil
      and raw_find(s2, "FOURTH.ad_no_melee", 1, true) ~= nil
      and raw_find(s2, "perform_special_ability", 1, true) ~= nil)
    check("0 " .. nm .. ": the family counts are unchanged (12 air-drop entries out of 689)",
      cp(s2, 'trigger = "air_drop_on_infantry"') == 12 and cp(s2, "\t{ marker = ") == 689)
    if nm == "live" then
      check("0 live: every air-drop line still carries the ui id (one definition + five call sites)",
        cp(s2, "FOURTH.ad_tag(unit)") == 6)
    else
      check("0 ann: the reading copy stays LOG-FREE and carries the same helpers",
        raw_find(s2, "log(", 1, true) == nil
        and raw_find(s2, "function FOURTH.ad_frontage(unit, men_now)", 1, true) ~= nil
        and raw_find(s2, "function FOURTH.ad_seg_dist(px, pz, ax, az, bx, bz)", 1, true) ~= nil)
    end
  end

  -- ==========================================================================
  print("== HARNESS 113 - A1: a 20-model block 10 m to the side FIRES (the reported bug) ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 15001, 15101
    local W = mk(uid, { melee = false, pos = { 100, 30, 200 } },
      { { name = INF, uid = euid, melee = true, pos = { 110, 0, 201 }, moving = true,
          slow_speed = 2.3, ordered = { 0, 0, 201 }, men_alive = 20, initial_men = 20 } })
    inf(W, euid, true); fly(W, uid, true)
    if boot(W, PATH, TAG, uid, "A1") then
      polln(W, 2)
      check(TAG .. "A1a: a 20-model block whose centre is 10.05 m away FIRES - the frontage credit"
        .. " takes the threshold to 12 m (" .. #W.fires .. ")", #W.fires == 1)
      check(TAG .. "A1b: and the cast is self-centred (the row has no target flags)",
        #W.fires == 1 and W.fires[1].target == unit_of(W, uid))
      check(TAG .. "A1c: the decision line names the segment, perp=9.02m, the credit and the 12.00m"
        .. " threshold [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "segment=(110.0, 201.0)->(109.0, 201.0)") >= 1
            and cl(W, "perp=9.02m") >= 1
            and cl(W, "threshold=12.00m (bound=6m + frontage=6.00m)") >= 1)))
      check(TAG .. "A1d: the frontage is derived from the MODEL COUNT with its arithmetic spelled out"
        .. " [live log]",
        lg((TAG ~= "[live] ")
          or cl(W, "frontage=6.00m (models, men=20 x 2 ranks (10 per rank) x 0.60m radius)") >= 1))
      check(TAG .. "A1e: the old POINT separation is still printed as the diagnostic it now is"
        .. " (centre 9.0 m, now 10.0 m) [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "centre=9.0m (the PROJECTED POINT separation - no longer the test)") >= 1
            and cl(W, "now=10.0m") >= 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 113 - A2: the same geometry, one alive model - the credit is what fired A1 ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 15002, 15102
    local W = mk(uid, { melee = false, pos = { 100, 30, 200 } },
      { { name = INF, uid = euid, melee = true, pos = { 110, 0, 201 }, moving = true,
          slow_speed = 2.3, ordered = { 0, 0, 201 }, men_alive = 1, initial_men = 20 } })
    inf(W, euid, true); fly(W, uid, true)
    if boot(W, PATH, TAG, uid, "A2") then
      polln(W, 3)
      check(TAG .. "A2a: with ONE alive model the frontage is 0 and 9.02 m stays outside 6 m - SILENT ("
        .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "A2b: the why-not line shows perp against the UNCREDITED 6.00 m threshold [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "perp=9.02m vs threshold=6.00m") >= 1
            and cl(W, "frontage=0.00m (single, men=1 -> no frontage") >= 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 113 - A3: the enemy's PATH crosses the drop point while its projected point is 9 m away ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 15003, 15103
    local W = mk(uid, { melee = false, pos = { 100, 30, 200 } },
      { { name = INF, uid = euid, melee = true, pos = { 101, 0, 200 }, moving = true,
          slow_speed = 22.2, ordered = { 0, 0, 200 }, men_alive = 20, initial_men = 20 } })
    inf(W, euid, true); fly(W, uid, true)
    if boot(W, PATH, TAG, uid, "A3") then
      polln(W, 2)
      check(TAG .. "A3a: the path passes THROUGH the projected caster point - FIRES (" .. #W.fires .. ")",
        #W.fires == 1)
      check(TAG .. "A3b: perp=0.00m while the projected point is 9.0 m away - the path is the test"
        .. " [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "perp=0.00m") >= 1
            and cl(W, "centre=9.0m (the PROJECTED POINT separation - no longer the test)") >= 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 113 - B: a one-model LORD on the same path is excluded, and the skip is logged once ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 15004, 15104
    local W = mk(uid, { melee = false, pos = { 100, 30, 200 } },
      { { name = INF, uid = euid, melee = true, pos = { 105, 0, 200 }, moving = true,
          slow_speed = 2.3, ordered = { 0, 0, 200 }, men_alive = 1, initial_men = 1 } })
    inf(W, euid, true); fly(W, uid, true)
    if boot(W, PATH, TAG, uid, "B") then
      polln(W, 3)
      check(TAG .. "B1a: a 5 m pass by a ONE-model lord does NOT fire (" .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "B1b: the skip is written ONCE for the whole episode, as `single entity (1 model)`"
        .. " [live log]",
        lg((TAG ~= "[live] ") or cl(W, "SKIPPED: single entity (1 model)") == 1))
      check(TAG .. "B1c: and it says the commander key set is not consulted here [live log]",
        lg((TAG ~= "[live] ")
          or cl(W, "the 1,409-key commander set is deliberately NOT consulted in this evaluator") == 1))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 113 - C: a 20-model block 15 m to the side stays SILENT ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 15005, 15105
    local W = mk(uid, { melee = false, pos = { 100, 30, 200 } },
      { { name = INF, uid = euid, melee = true, pos = { 115, 0, 200 }, moving = true,
          slow_speed = 2.3, ordered = { 115, 0, 220 }, men_alive = 20, initial_men = 20 } })
    inf(W, euid, true); fly(W, uid, true)
    if boot(W, PATH, TAG, uid, "C") then
      polln(W, 3)
      check(TAG .. "C1a: perp 15.00 m against a 12.00 m threshold - no fire (" .. #W.fires .. ")",
        #W.fires == 0)
      check(TAG .. "C1b: the why-not line names perp=~15m, the threshold and the credit [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "perp=~15m vs threshold=12.00m") >= 1
            and cl(W, "-> NOT under the caster") >= 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 113 - D: ordered_width vs models vs clamped, at perp 12.20 m ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local function world(uid, euid, wname, width)
      local W = mk(uid, { melee = false, pos = { 100, 30, 200 } },
        { { name = INF, uid = euid, melee = true, pos = { 112.2, 0, 200 }, moving = true,
            slow_speed = 2.3, ordered = { 112.2, 0, 220 }, men_alive = 20, initial_men = 20,
            width = width } })
      inf(W, euid, true); fly(W, uid, true)
      if not boot(W, PATH, TAG, uid, wname) then return nil end
      polln(W, 2)
      return W
    end
    do
      local W = world(15006, 15106, "D1", 24)
      if W ~= nil then
        check(TAG .. "D1a: ordered_width 24 m -> half 12.00 m (source `ordered`) -> 18 m threshold -"
          .. " the 12.20 m pass FIRES (" .. #W.fires .. ")", #W.fires == 1)
        check(TAG .. "D1b: the log names the `ordered` source and the measured width [live log]",
          lg((TAG ~= "[live] ")
            or (cl(W, "frontage=12.00m (ordered, ordered_width=24.00m)") >= 1
              and cl(W, "threshold=18.00m (bound=6m + frontage=12.00m)") >= 1)))
        tally(W)
      end
    end
    do
      local W = world(15007, 15107, "D2", nil)
      if W ~= nil then
        check(TAG .. "D2a: with no ordered width the MODELS decide - half 6.00 m -> 12 m threshold -"
          .. " the same 12.20 m pass stays SILENT (" .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "D2b: the log names the `models` source [live log]",
          lg((TAG ~= "[live] ")
            or cl(W, "frontage=6.00m (models, men=20 x 2 ranks (10 per rank) x 0.60m radius)") >= 1))
        tally(W)
      end
    end
    do
      local W = world(15008, 15108, "D3", 60)
      if W ~= nil then
        check(TAG .. "D3a: ordered_width 60 m -> half 30 m CLAMPED to 12.00 m - the pass FIRES ("
          .. #W.fires .. ")", #W.fires == 1)
        check(TAG .. "D3b: the log says `clamped` and names the ceiling [live log]",
          lg((TAG ~= "[live] ")
            or cl(W, "frontage=12.00m (clamped, ordered_width=60.00m -> half 30.00m clamped to 12.00m)") >= 1))
        tally(W)
      end
    end
  end

  -- ==========================================================================
  print("== HARNESS 113 - E: an unreadable frontage falls back to 0 and the 6 m bound alone decides ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    do
      local uid, euid = 15009, 15109
      local W = mk(uid, { melee = false, pos = { 100, 30, 200 } },
        { { name = INF, uid = euid, melee = true, pos = { 105, 0, 200 }, moving = true,
            slow_speed = 2.3, ordered = { 0, 0, 200 }, men_alive = 20, initial_men = 20,
            width_raises = true } })
      inf(W, euid, true); fly(W, uid, true)
      if boot(W, PATH, TAG, uid, "E1") then
        polln(W, 2)
        check(TAG .. "E1a: ordered_width() raises, so the MODELS give the credit - FIRES ("
          .. #W.fires .. ")", #W.fires == 1)
        check(TAG .. "E1b: the source is `models`, never a guess [live log]",
          lg((TAG ~= "[live] ")
            or cl(W, "frontage=6.00m (models, men=20 x 2 ranks (10 per rank) x 0.60m radius)") >= 1))
        tally(W)
      end
    end
    do
      local uid, euid = 15010, 15110
      local W = mk(uid, { melee = false, pos = { 100, 30, 200 } },
        { { name = INF, uid = euid, melee = true, pos = { 105, 0, 200 }, moving = true,
            slow_speed = 2.3, ordered = { 0, 0, 200 }, men_alive = 20, initial_men = 20,
            width_raises = true, men_die_tick = 1, men_die_nil = true } })
      inf(W, euid, true); fly(W, uid, true)
      if boot(W, PATH, TAG, uid, "E2") then
        polln(W, 2)
        check(TAG .. "E2a: with BOTH reads gone the cast lapses - not spent (" .. #W.fires .. ")",
          #W.fires == 0)
        check(TAG .. "E2b: the fail-closed frontage is 0.00 m and the bound alone decides [live log]",
          lg((TAG ~= "[live] ")
            or (cl(W, "frontage=0.00m (unreadable, ordered_width() and number_of_men_alive() both unreadable -> point)") >= 1
              and cl(W, "vs threshold=6.00m (bound=6m") >= 1)))
        tally(W)
      end
    end
  end

  -- ==========================================================================
  print("== HARNESS 113 - F: the pre-cast re-check re-derives the segment and skips on drift ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 15011, 15111
    local W = mk(uid, { melee = false, pos = { 100, 30, 200 } },
      { { name = INF, uid = euid, melee = true,
          pos_seq = { { 110, 0, 201 }, { 110, 0, 201 }, { 130, 0, 201 }, { 130, 0, 201 } },
          moving = true, slow_speed = 2.3, ordered = { 0, 0, 201 },
          men_alive = 20, initial_men = 20 } })
    inf(W, euid, true); fly(W, uid, true)
    if boot(W, PATH, TAG, uid, "F") then
      polln(W, 2)
      check(TAG .. "F1a: the block drifted 20 m during the wind-up - the cast is NOT spent ("
        .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "F1b: the SKIPPED line prints the FRESH perp and the threshold [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "SKIPPED: the drop lapsed before the cast") >= 1
            and cl(W, "perp=28.98m") >= 1
            and cl(W, "vs threshold=12.00m") >= 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 113 - G: a depleted 20-model block is judged as a BLOCK (initial, not current) ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 15012, 15112
    local W = mk(uid, { melee = false, pos = { 100, 30, 200 } },
      { { name = INF, uid = euid, melee = true, pos = { 105, 0, 200 }, moving = true,
          slow_speed = 2.3, ordered = { 105, 0, 220 }, men_alive = 1, initial_men = 20 } })
    inf(W, euid, true); fly(W, uid, true)
    if boot(W, PATH, TAG, uid, "G") then
      polln(W, 2)
      check(TAG .. "G1a: the depleted block is NOT skipped and FIRES at 5.00 m (" .. #W.fires .. ")",
        #W.fires == 1)
      check(TAG .. "G1b: no single-entity line was written for it [live log]",
        lg((TAG ~= "[live] ") or cl(W, "single entity (1 model)") == 0))
      check(TAG .. "G1c: the log shows men=1 with the source `single`, while initial 20 kept it a BLOCK"
        .. " [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "frontage=0.00m (single, men=1 -> no frontage, a single model is a point)") >= 1
            and cl(W, "threshold=6.00m (bound=6m + frontage=0.00m)") >= 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  if red113 then
    check("HARNESS 112 suite boundary (harness 113): N/A in the red run - the pre-113 snapshot "
      .. "still carries every harness-112 world", true)
  else
    check("HARNESS 112 suite boundary (harness 113): every harness-112 check ran first ("
      .. pre113 .. ", want 4492)", pre113 == 4492)
  end
  check("HARNESS 113: the ZERO-search invariant still holds after the new section (counted "
    .. find_calls .. ")", find_calls == 0)
  print("== HARNESS 113 done: checks " .. checks .. ", failures " .. failures .. " ==")
end
