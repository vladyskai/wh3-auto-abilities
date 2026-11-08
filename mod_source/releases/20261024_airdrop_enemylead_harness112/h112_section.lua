-- ============================================================================
-- HARNESS 112 - THE ENEMY-SIDE LEAD DIAL (the fourth dial), AND THE TWO
-- DIAGNOSTIC FIXES.
--
-- THE EVIDENCE (docs/WH3_skyjunk_diagnosis.md): four Sky-junk bombers, all armed,
-- all airborne, all evaluated on every poll; the zombies walked THROUGH
-- underneath three of them and nothing fired. The projected enemy centre was
-- carried v_enemy * 1.5 s = 3.45 m PAST the hoverer, so the projected gap bottomed
-- out around 5 m and then GREW to 10 m - largest exactly when the enemy was
-- underneath. The caster's dials and the 6 m bound were not at fault: the ENEMY
-- carried the whole fall time.
--
-- THE RULE NOW (four dials, two per body):
--     caster_projected = caster + v_caster * AIR_DROP_CASTER_DELAY_S * AIR_DROP_CASTER_LEAD
--     enemy_projected  = enemy  + v_enemy  * AIR_DROP_DELAY_S       * AIR_DROP_ENEMY_LEAD
-- fire when the PROJECTED horizontal centre separation is inside AIR_DROP_CENTER_M.
--
-- PINS (asserted against BOTH files below, so a silent retune fails the suite):
--     BOUND        AIR_DROP_CENTER_M        = 6 m   (unchanged)
--     DELAY        AIR_DROP_DELAY_S         = 1.5 s (unchanged)
--     ENEMY_LEAD   AIR_DROP_ENEMY_LEAD      = 0.3   (NEW)
--     C_CASTER_D   AIR_DROP_CASTER_DELAY_S  = 1.5 s (unchanged)
--     C_CASTER_L   AIR_DROP_CASTER_LEAD     = 0.5   (unchanged)
--     INHERIT      AIR_DROP_INHERIT         = false (unchanged)
--
-- PER-WORLD DISTANCES (the arithmetic is in each world's comment; the asserts
-- pin the exact printed strings):
--   A1  enemy lead 1.0, 5 m lateral crossing at 2.3 m/s: sqrt(25+3.45^2)= 6.07 m -> SILENT (the bug)
--   A2  the SAME world at the shipped 0.3:              sqrt(25+1.035^2)= 5.11 m -> FIRES
--   B   enemy lead 0.0: 5.00 m -> FIRES ; 6.50 m -> SILENT (current position only)
--   C   receding caster + parked enemy: 4.0 m projected, 2.0 m now - IDENTICAL at 0.3 and 1.0
--   D   both moving (caster +8, enemy -4): 12.20 m -> SILENT ; 4.20 m -> FIRES
--   E   exact metres: 8.58 m printed EXACTLY ; 21.03 m still BANDS to ~20m
--   F   the ui id: two same-type units (1003, 1004) - every air-drop line carries its own tag
--
-- RED CONTROL (H112_LIVE / H112_ANN -> docs/backups/round112/pre112_*.lua, the
-- round-111 build): there is no enemy dial, the dial text has only two dials and
-- the watch line bands at 5 m, so every 0 check and every A/B/D/E world fails as
-- designed.
-- ============================================================================
VAR_DIR_112 = "C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261024_airdrop_enemylead_harness112/variants"

-- A variant of the same source with ONLY the enemy-lead constant line replaced -
-- the one-line edit the user makes in the field. A build without the line (the
-- round-111 red snapshot) is returned unchanged, so the red world tests the old
-- build as it is rather than crashing.
function harness_variant112(path, elead, tag)
  if elead == nil then return path end
  local txt = read_file(path)
  local t = "\nFOURTH.AIR_DROP_ENEMY_LEAD = 0.3\n"
  if raw_find(txt, t, 1, true) == nil then return path end
  local out2, at = {}, 1
  while true do
    local i, j = raw_find(txt, t, at, true)
    if i == nil then break end
    out2[#out2 + 1] = txt:sub(at, i - 1)
    out2[#out2 + 1] = "\nFOURTH.AIR_DROP_ENEMY_LEAD = " .. string.format("%.2f", elead) .. "\n"
    at = j + 1
  end
  out2[#out2 + 1] = txt:sub(at)
  local dst = VAR_DIR_112 .. "/" .. tag .. ".lua"
  local f = assert(io.open(dst, "w"))
  f:write(table.concat(out2))
  f:close()
  return dst
end

function run_h112()
  if os.getenv("H112_LIVE") ~= nil then LIVE = os.getenv("H112_LIVE") end
  if os.getenv("H112_ANN") ~= nil then ANN = os.getenv("H112_ANN") end
  local live_src112 = read_file(LIVE)
  local ann_src112  = read_file(ANN)
  local pre112 = checks
  local DFA = "wh2_dlc09_unit_abilities_death_from_above"
  local INF = "wh2_dlc13_emp_inf_spearmen_ror_0"

  -- THE PINS
  local PIN_BOUND  = 6.0
  local PIN_DELAY  = 1.5
  local PIN_ELEAD  = 0.3
  local PIN_CDELAY = 1.5
  local PIN_CLEAD  = 0.5

  local function cp112(s2, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s2, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function span112(s2, head, tail2)
    local i = raw_find(s2, head, 1, true)
    if i == nil then return nil end
    local j = raw_find(s2, tail2, i, true)
    if j == nil then return nil end
    return s2:sub(i, j)
  end
  local function lg112(cond) return cond == true end
  local function enemy_of112(W, uid)
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
  local function inf112(W, uid, v)
    local e = enemy_of112(W, uid)
    if e == nil then return end
    e.is_infantry = function() return v == true end
  end
  local function fly112(W, uid, v)
    local u = unit_of(W, uid)
    if u == nil then return nil end
    local b = (v == true)
    u.is_currently_flying = function() return b end
    return u
  end
  local function mk112(uid, def, enemies)
    def.name = def.name or "sky_junk"
    def.uid = uid
    local owns = def.owns or { DFA }
    def.owns = owns
    local bar = {}
    for i = 1, #owns do bar[i] = { id = "b" .. i, key = owns[i] } end
    return make_world({ can_perform = true,
      units = { def },
      enemies = enemies,
      cards = { { id = tostring(uid), state = "active", vis = true } },
      bar = bar })
  end
  local function boot112(W, PATH, TAG, uid, marker, wname, elead)
    local load_path = harness_variant112(PATH, elead, "h112_" .. wname
      .. (PATH == LIVE and "_live" or "_ann"))
    local ok = pcall(load_world, W, load_path)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. marker); ui(W)
    W.conflict = true
    return true
  end

  -- ==========================================================================
  print("== HARNESS 112 - section 0: the FOUR dials and the two log fixes, in the source (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src112 }, { name = "ann", src = ann_src112 } }) do
    local nm, s2 = f.name, f.src
    local lead = span112(s2, "function FOURTH.ad_lead(unit, t, allow_bearing)", "\nend")
    local dlg  = span112(s2, "function FOURTH.ad_dial_text(moving)", "\nend")
    local say  = span112(s2, "function FOURTH.ad_say(unit, marker, note)", "\nend")
    local pick = span112(s2, "function FOURTH.ad_pick(unit, routing)",
      "\nfunction FOURTH.evaluate_air_drop_on_infantry")
    local rech = span112(s2, "if FOURTH.ad_enemy ~= nil then", "\n\t-- SELF-SUMMON RE-CHECK")

    check("0 " .. nm .. ": the enemy lead is defined EXACTLY ONCE at the pin (0.30)",
      cp112(s2, "\nFOURTH.AIR_DROP_ENEMY_LEAD = " .. string.format("%.1f", PIN_ELEAD) .. "\n") == 1)
    check("0 " .. nm .. ": the FIVE older constants are untouched and single (bound 6, delay 1.5, caster 1.5 / 0.5, inherit false)",
      cp112(s2, "\nFOURTH.AIR_DROP_CENTER_M = " .. string.format("%.0f", PIN_BOUND) .. "\n") == 1
      and cp112(s2, "\nFOURTH.AIR_DROP_DELAY_S = " .. string.format("%.1f", PIN_DELAY) .. "\n") == 1
      and cp112(s2, "\nFOURTH.AIR_DROP_CASTER_DELAY_S = " .. string.format("%.1f", PIN_CDELAY) .. "\n") == 1
      and cp112(s2, "\nFOURTH.AIR_DROP_CASTER_LEAD = " .. string.format("%.1f", PIN_CLEAD) .. "\n") == 1
      and cp112(s2, "\nFOURTH.AIR_DROP_INHERIT = false\n") == 1)
    check("0 " .. nm .. ": the enemy is scaled by its OWN share of the shared delay (lead_enemy, read on the enemy arm only)",
      lead ~= nil
      and raw_find(lead, "local lead_enemy = 1", 1, true) ~= nil
      and raw_find(lead, "if allow_bearing ~= true then", 1, true) ~= nil
      and raw_find(lead, "FOURTH.AIR_DROP_ENEMY_LEAD", 1, true) ~= nil
      and raw_find(lead, "px = x + vx * t * lead_enemy", 1, true) ~= nil
      and raw_find(lead, "pz = z + vz * t * lead_enemy", 1, true) ~= nil)
    check("0 " .. nm .. ": the CASTER's two dials are untouched (own delay x own lead, on the caster arm only)",
      lead ~= nil
      and raw_find(lead, "local t_caster, lead_caster = t, 1", 1, true) ~= nil
      and raw_find(lead, "px = x + vx * t_caster * lead_caster", 1, true) ~= nil
      and raw_find(lead, "pz = z + vz * t_caster * lead_caster", 1, true) ~= nil
      and raw_find(lead, "if allow_bearing == true then", 1, true) ~= nil)
    check("0 " .. nm .. ": an UNREADABLE enemy lead falls back to the full carry (1.0), never to a guess",
      lead ~= nil
      and raw_find(lead, 'if type(l_enemy) == "number" and l_enemy >= 0 then lead_enemy = l_enemy end', 1, true) ~= nil)
    check("0 " .. nm .. ": the ONE momentum flag still adds the caster's lead term a second time",
      lead ~= nil
      and raw_find(lead, "if allow_bearing and FOURTH.AIR_DROP_INHERIT == true then", 1, true) ~= nil
      and raw_find(lead, "px = px + vx * t_caster * lead_caster", 1, true) ~= nil)
    check("0 " .. nm .. ": the dial text prints ALL FOUR dials (delay / enemy_lead / delay_caster / caster_lead)",
      dlg ~= nil
      and raw_find(dlg, '"delay="', 1, true) ~= nil
      and raw_find(dlg, '"enemy_lead="', 1, true) ~= nil
      and raw_find(dlg, '"delay_caster="', 1, true) ~= nil
      and raw_find(dlg, '"caster_lead="', 1, true) ~= nil
      and raw_find(dlg, '" moving caster: lead="', 1, true) ~= nil)
    if nm == "live" then
      check("0 " .. nm .. ": the dial text is defined once and printed on all four air-drop lines (count 5)",
        cp112(s2, "FOURTH.ad_dial_text") == 5)
      check("0 " .. nm .. ": EVERY air-drop log line is prefixed with the unit's ui id (ad_say + target + skip + re-check)",
        cp112(s2, "FOURTH.ad_tag(unit)") == 5
        and raw_find(s2, "function FOURTH.ad_tag(unit)", 1, true) ~= nil
        and say ~= nil and raw_find(say, "FOURTH.ad_tag(unit)", 1, true) ~= nil)
    else
      check("0 " .. nm .. ": the reading copy needs no tag helper (it carries no log lines) and keeps the dial helper",
        raw_find(s2, "function FOURTH.ad_tag(unit)", 1, true) == nil
        and cp112(s2, "FOURTH.ad_dial_text") >= 1)
    end
    check("0 " .. nm .. ": the watch line prints EXACT metres below 15 m and BANDS above it (diagnosis D1)",
      pick ~= nil
      and raw_find(pick, "if near_gap < 15 then", 1, true) ~= nil
      and raw_find(pick, 'string.format("%.2f", near_gap)', 1, true) ~= nil
      and raw_find(pick, 'string.format("%.2f", near_now)', 1, true) ~= nil
      and raw_find(pick, "math.floor(near_gap / 5) * 5", 1, true) ~= nil)
    check("0 " .. nm .. ": the picker still projects both bodies through ONE helper and gates on the projection",
      pick ~= nil
      and raw_find(pick, "FOURTH.ad_lead(unit, ad_t, true)", 1, true) ~= nil
      and raw_find(pick, "FOURTH.ad_lead(enemy, ad_t, false)", 1, true) ~= nil
      and raw_find(pick, "pgap <= bound", 1, true) ~= nil)
    check("0 " .. nm .. ": the pre-cast re-check re-projects through the SAME helper (same four dials)",
      rech ~= nil
      and raw_find(rech, "FOURTH.ad_lead(unit, ad_t_now, true)", 1, true) ~= nil
      and raw_find(rech, "FOURTH.ad_project(enemy, ad_t_now)", 1, true) ~= nil)
    check("0 " .. nm .. ": air_only / no_melee / the self-centred cast / fail-closed are ALL still in place",
      raw_find(s2, "is_currently_flying()", 1, true) ~= nil
      and raw_find(s2, "is_in_melee()", 1, true) ~= nil
      and raw_find(s2, "FOURTH.ad_air_only", 1, true) ~= nil
      and raw_find(s2, "FOURTH.ad_no_melee", 1, true) ~= nil
      and raw_find(s2, "perform_special_ability", 1, true) ~= nil)
    check("0 " .. nm .. ": the FOUR-DIAL tuning guide is in the source (one dial per test, defaults table)",
      raw_find(s2, "AIR_DROP_ENEMY_LEAD 0.3 -> 0.0", 1, true) ~= nil
      and raw_find(s2, "THE FOUR DIALS", 1, true) ~= nil
      and raw_find(s2, "THE DEFAULTS THAT SHIP", 1, true) ~= nil
      and raw_find(s2, "Only ONE dial changes per test", 1, true) ~= nil)
    if nm == "live" then
      check("0 " .. nm .. ": the DECISION line prints all four dials",
        raw_find(s2, '.. " from " .. FOURTH.ad_dial_text(best_uspd > 0)', 1, true) ~= nil)
      check("0 " .. nm .. ": the why-not (watch) line prints all four dials too",
        raw_find(s2, '.. " (" .. FOURTH.ad_dial_text(best_uspd > 0) .. "); enemy v="', 1, true) ~= nil)
      check("0 " .. nm .. ": the target / skip / re-check lines each carry FOURTH.ad_tag(unit)",
        cp112(s2, 'log("  " .. FOURTH.ad_tag(unit) .. marker .. " target: ') == 1
        and cp112(s2, 'log("  " .. FOURTH.ad_tag(unit) .. ad_marker_now .. " SKIPPED: ') == 1
        and cp112(s2, 'log("  " .. FOURTH.ad_tag(unit) .. ad_marker_now .. " pre-cast re-check: ') == 1)
    else
      check("0 " .. nm .. ": the reading copy stays log-free and carries the enemy dial",
        raw_find(s2, "log(", 1, true) == nil
        and raw_find(s2, "FOURTH.AIR_DROP_ENEMY_LEAD = 0.3", 1, true) ~= nil)
    end
  end

  -- ==========================================================================
  -- A: THE REPORTED BUG, AS A CONTROL. Caster (100, 30, 200) hovering; a zombie
  --    crossing at x = 105 (5 m lateral), abreast at z = 200, 2.3 m/s along +z.
  --      enemy lead 1.0 -> proj z = 200 + 3.45 -> sqrt(25 + 11.90) = 6.07 m -> SILENT
  --      enemy lead 0.3 -> proj z = 200 + 1.035 -> sqrt(25 + 1.07) = 5.11 m -> FIRES
  print("== HARNESS 112 - A: the crossing enemy - lead 1.0 misses, the shipped 0.3 fires ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local function cross(uid, euid, elead, wname)
      local W = mk112(uid, { melee = false, pos = { 100, 30, 200 } },
        { { name = INF, uid = euid, melee = true, pos = { 105, 0, 200 }, moving = true,
            slow_speed = 2.3, ordered = { 105, 0, 220 } } })
      inf112(W, euid, true); fly112(W, uid, true)
      if not boot112(W, PATH, TAG, uid, "death_from_above", wname, elead) then return nil end
      polln(W, 2)
      return W
    end
    do
      local W = cross(14001, 14101, 1.0, "A1")
      if W ~= nil then
        check(TAG .. "A1a (CONTROL, enemy lead 1.0 = the reported bug): a 5 m lateral pass projects 6.07 m - SILENT ("
          .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "A1b: the log proves the over-carry - projected 6.07 m from 5.00 m now, at enemy_lead=1.00 [live log]",
          lg112((TAG ~= "[live] ")
            or (count_log(W, "projected sep=6.07m after delay=1.50s") >= 1
              and count_log(W, "is centre=5.00m vs bound=6m") >= 1
              and count_log(W, "delay=1.50s enemy_lead=1.00 delay_caster=1.50s caster_lead=0.50") >= 1)))
        tally(W)
      end
    end
    do
      local W = cross(14002, 14102, 0.3, "A2")
      if W ~= nil then
        check(TAG .. "A2a (SHIPPED 0.3): the SAME pass projects 5.11 m - FIRES (" .. #W.fires .. ")",
          #W.fires == 1)
        check(TAG .. "A2b: the line names enemy_lead=0.30 and the projected 5.1 m [live log]",
          lg112((TAG ~= "[live] ")
            or (count_log(W, "delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=0.50") >= 1
              and count_log(W, "centre=5.1m") >= 1)))
        check(TAG .. "A2c: the DECISION line carries the unit tag too [live log]",
          lg112((TAG ~= "[live] ")
            or count_log(W, "  [14002] death_from_above target: '") >= 1))
        tally(W)
      end
    end
  end

  -- ==========================================================================
  -- B: enemy lead 0.0 - the enemy is judged WHERE IT IS.
  --    5.00 m -> FIRES ; 6.50 m -> SILENT (both exact, because 0.0 carries nothing).
  print("== HARNESS 112 - B: lead 0.0 puts the impact on the enemy's CURRENT position ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local function zero(uid, euid, ex, wname)
      local W = mk112(uid, { melee = false, pos = { 100, 30, 200 } },
        { { name = INF, uid = euid, melee = true, pos = { ex, 0, 200 }, moving = true,
            slow_speed = 6.0, ordered = { ex, 0, 220 } } })
      inf112(W, euid, true); fly112(W, uid, true)
      if not boot112(W, PATH, TAG, uid, "death_from_above", wname, 0.0) then return nil end
      polln(W, 2)
      return W
    end
    do
      local W = zero(14003, 14103, 105.0, "B1")
      if W ~= nil then
        check(TAG .. "B1a (lead 0.0): a 5.00 m enemy FIRES even at 6 m/s of travel (the velocity is not projected at all) ("
          .. #W.fires .. ")", #W.fires == 1)
        check(TAG .. "B1b: projected = current - 5.0 m in both places [live log]",
          lg112((TAG ~= "[live] ")
            or (count_log(W, "centre=5.0m") >= 1 and count_log(W, " now=5.0m") >= 1
              and count_log(W, "enemy_lead=0.00") >= 1)))
        tally(W)
      end
    end
    do
      local W = zero(14004, 14104, 106.5, "B2")
      if W ~= nil then
        check(TAG .. "B2a (lead 0.0): 6.50 m is outside the 6 m pin - SILENT (" .. #W.fires .. ")",
          #W.fires == 0)
        check(TAG .. "B2b: and the why-not line says 6.50 m exactly on both numbers [live log]",
          lg112((TAG ~= "[live] ")
            or (count_log(W, "is centre=6.50m vs bound=6m") >= 1
              and count_log(W, "projected sep=6.50m after delay=1.50s") >= 1)))
        tally(W)
      end
    end
  end

  -- ==========================================================================
  -- C: a RECEDING caster with a PARKED enemy - the enemy dial cannot touch it.
  --    caster (100) ordered to 0, 8 m/s -> proj 100 - 8*1.5*0.5 = 94.0 ;
  --    enemy parked at 98 -> 4.0 m projected, 2.0 m now, in BOTH worlds.
  print("== HARNESS 112 - C: a parked enemy is untouched by the enemy dial ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local function recede(uid, euid, elead, wname)
      local W = mk112(uid, { melee = false, pos = { 100, 30, 200 }, moving = true, fast = true,
          fast_speed = 8, ordered = { 0, 30, 200 } },
        { { name = INF, uid = euid, melee = true, pos = { 98, 0, 200 } } })
      inf112(W, euid, true); fly112(W, uid, true)
      if not boot112(W, PATH, TAG, uid, "death_from_above", wname, elead) then return nil end
      polln(W, 2)
      return W
    end
    do
      local W3 = recede(14005, 14105, 0.3, "C1")
      local W1 = recede(14006, 14106, 1.0, "C2")
      if W3 ~= nil and W1 ~= nil then
        check(TAG .. "C1a: at the shipped 0.3 the receding caster still fires at 4.0 m projected ("
          .. #W3.fires .. ")", #W3.fires == 1)
        check(TAG .. "C2a: and the enemy dial does NOT change it - lead 1.0 fires too ("
          .. #W1.fires .. ")", #W1.fires == 1)
        check(TAG .. "C2b: identical numbers in both worlds - centre=4.0m, now=2.0m, caster proj=(94.0, 200.0) [live log]",
          lg112((TAG ~= "[live] ")
            or (count_log(W3, "centre=4.0m") >= 1 and count_log(W1, "centre=4.0m") >= 1
              and count_log(W3, " now=2.0m") >= 1 and count_log(W1, " now=2.0m") >= 1
              and count_log(W3, "proj=(94.0, 200.0)") >= 1
              and count_log(W1, "proj=(94.0, 200.0)") >= 1)))
        check(TAG .. "C2c: only the printed dial differs (enemy_lead=0.30 vs 1.00) [live log]",
          lg112((TAG ~= "[live] ")
            or (count_log(W3, "enemy_lead=0.30") >= 1 and count_log(W1, "enemy_lead=1.00") >= 1)))
        tally(W3); tally(W1)
      end
    end
  end

  -- ==========================================================================
  -- D: BOTH moving. caster (100) +8 m/s -> 106.0 (lead 0.5) ;
  --    enemy 120 closing 4 m/s -> 120 - 1.8 = 118.2 -> 12.20 m (SILENT) ;
  --    enemy 112 -> 110.2 -> 4.20 m (FIRES).
  print("== HARNESS 112 - D: both bodies moving - 12.20 m silent, 4.20 m fires ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local function both(uid, euid, ex, wname)
      local W = mk112(uid, { melee = false, pos = { 100, 30, 200 }, moving = true, fast = true,
          fast_speed = 8, ordered = { 300, 30, 200 } },
        { { name = INF, uid = euid, melee = true, pos = { ex, 0, 200 }, moving = true,
            slow_speed = 4, ordered = { 0, 0, 200 } } })
      inf112(W, euid, true); fly112(W, uid, true)
      if not boot112(W, PATH, TAG, uid, "death_from_above", wname, 0.3) then return nil end
      polln(W, 2)
      return W
    end
    do
      local W1 = both(14007, 14107, 120, "D1")
      local W2 = both(14008, 14108, 112, "D2")
      if W1 ~= nil and W2 ~= nil then
        check(TAG .. "D1a: 20 m closing projects 12.20 m - SILENT (" .. #W1.fires .. ")",
          #W1.fires == 0)
        check(TAG .. "D1b: the why-not line shows 12.20 m projected from 20.00 m now [live log]",
          lg112((TAG ~= "[live] ")
            or (count_log(W1, "projected sep=12.20m after delay=1.50s") >= 1
              and count_log(W1, "is centre=~20m vs bound=6m") >= 1)))
        check(TAG .. "D2a: 12 m closing projects 4.20 m - FIRES (" .. #W2.fires .. ")",
          #W2.fires == 1)
        check(TAG .. "D2b: and the decision line shows both projections - caster 106.0, enemy 110.2 [live log]",
          lg112((TAG ~= "[live] ")
            or (count_log(W2, "centre=4.2m") >= 1
              and count_log(W2, "proj=(106.0, 200.0)") >= 1
              and count_log(W2, "proj=(110.2, 200.0)") >= 1)))
        tally(W1); tally(W2)
      end
    end
  end

  -- ==========================================================================
  -- E: EXACT METRES BELOW 15 m, bands above (diagnosis D1).
  --    enemy (103, 207) at 2.3 m/s -> proj z 208.035 -> sqrt(9 + 64.56) = 8.58 m EXACT
  --    enemy (100, 220) at 2.3 m/s -> proj z 221.035 -> 21.03 m -> bands to ~20m
  print("== HARNESS 112 - E: the deciding distance is never banded below 15 m ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local function near(uid, euid, ex, ez, wname)
      local W = mk112(uid, { melee = false, pos = { 100, 30, 200 } },
        { { name = INF, uid = euid, melee = true, pos = { ex, 0, ez }, moving = true,
            slow_speed = 2.3, ordered = { ex, 0, ez + 20 } } })
      inf112(W, euid, true); fly112(W, uid, true)
      if not boot112(W, PATH, TAG, uid, "death_from_above", wname, 0.3) then return nil end
      polln(W, 2)
      return W
    end
    do
      local WN = near(14009, 14109, 103, 207, "E1")
      local WF = near(14010, 14110, 100, 220, "E2")
      if WN ~= nil and WF ~= nil then
        check(TAG .. "E1a: an 8.58 m projection is printed EXACTLY, not as a 5 m band [live log]",
          lg112((TAG ~= "[live] ")
            or (count_log(WN, "projected sep=8.58m after delay=1.50s") >= 1
              and count_log(WN, "projected sep=~") == 0)))
        -- the instant gap from (103, 207) to (100, 200) is sqrt(9 + 49) = 7.62 m
        check(TAG .. "E1b: and the instant number is exact too (7.62 m) [live log]",
          lg112((TAG ~= "[live] ") or count_log(WN, "is centre=7.62m vs bound=6m") >= 1))
        check(TAG .. "E2a: above 15 m the 5 m BAND stays (21.03 m -> ~20m) [live log]",
          lg112((TAG ~= "[live] ")
            or (count_log(WF, "projected sep=~20m after delay=1.50s") >= 1
              and count_log(WF, "projected sep=21") == 0
              and count_log(WF, "is centre=~20m vs bound=6m") >= 1)))
        tally(WN); tally(WF)
      end
    end
  end

  -- ==========================================================================
  -- F: EVERY air-drop line carries the unit's own ui id (diagnosis D2). Two
  --    same-type units in two worlds - 1003 and 1004 - so the tag is proved to
  --    follow the UNIT, and no air-drop line is left unattributed.
  print("== HARNESS 112 - F: the air-drop lines name their unit ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local function tagged(uid, euid, wname)
      local W = mk112(uid, { melee = false, pos = { 100, 30, 200 } },
        { { name = INF, uid = euid, melee = true, pos = { 108, 0, 200 }, moving = true,
            slow_speed = 2.3, ordered = { 108, 0, 220 } } })
      inf112(W, euid, true); fly112(W, uid, true)
      if not boot112(W, PATH, TAG, uid, "death_from_above", wname, 0.3) then return nil end
      polln(W, 3)
      return W
    end
    -- ONLY the picker's own lines: the arming line ("AUTO death_from_above for
    -- unit ...") and the click line also name the marker but are not air-drop
    -- decisions.
    local function tag_stats(W, uid)
      local n, bad = 0, 0
      local tag = "[" .. tostring(uid) .. "] death_from_above"
      local keys = { "death_from_above watch:", "death_from_above target:",
        "death_from_above SKIPPED: the drop", "death_from_above pre-cast re-check:",
        "death_from_above airborne check:", "death_from_above melee check:" }
      for _, line in ipairs(W.log_lines) do
        local hit = false
        for _, k in ipairs(keys) do
          if raw_find(line, k, 1, true) ~= nil then hit = true end
        end
        if hit then
          n = n + 1
          if raw_find(line, tag, 1, true) == nil then bad = bad + 1 end
        end
      end
      return n, bad
    end
    do
      local W3 = tagged(1003, 14203, "F1")
      local W4 = tagged(1004, 14204, "F2")
      if W3 ~= nil and W4 ~= nil then
        local n3, bad3 = tag_stats(W3, 1003)
        local n4, bad4 = tag_stats(W4, 1004)
        check(TAG .. "F1a: unit 1003's air-drop lines all carry [1003] (" .. n3 .. " lines, " .. bad3 .. " untagged)",
          lg112((TAG ~= "[live] ") or (n3 >= 1 and bad3 == 0)))
        check(TAG .. "F2a: unit 1004's air-drop lines all carry [1004] - the tag follows the UNIT, not the type ("
          .. n4 .. " lines, " .. bad4 .. " untagged)",
          lg112((TAG ~= "[live] ") or (n4 >= 1 and bad4 == 0)))
        check(TAG .. "F2b: and neither world prints the other unit's tag [live log]",
          lg112((TAG ~= "[live] ")
            or (count_log(W3, "[1004]") == 0 and count_log(W4, "[1003]") == 0)))
        check(TAG .. "F2c: the tag is in front of the marker - '  [1003] death_from_above watch:' [live log]",
          lg112((TAG ~= "[live] ")
            or count_log(W3, "  [1003] death_from_above watch:") >= 1))
        tally(W3); tally(W4)
      end
    end
  end

  -- ==========================================================================
  if RED_MODE then
    check("HARNESS 111 suite boundary (harness 112): N/A in the red run - the pre-112 snapshot "
      .. "still carries every harness-111 world", true)
  else
    check("HARNESS 111 suite boundary (harness 112): every harness-111 check ran first ("
      .. pre112 .. ", want 4387)", pre112 == 4387)
  end
  check("HARNESS 112: the ZERO-search invariant still holds after the new section (counted "
    .. find_calls .. ")", find_calls == 0)
  print("== HARNESS 112 done: checks " .. checks .. ", failures " .. failures .. " ==")
end
