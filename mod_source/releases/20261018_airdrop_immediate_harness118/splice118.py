#!/usr/bin/env python3
"""Round 118 harness splice.

harness118.lua starts as harness117.lua (LIGHT switch renamed to H118_LIGHT).
This script replaces the three air-drop sections whose worlds pinned the now
deleted delay machinery with:

  1  the delay machinery is GONE            (was run_h115 - the dwell section)
  2  no velocity, no heading, no clock      (was run_h116 - the velocity section)
  3  the CENTRE measurement is untouched    (was run_h117 - section 0 retouched)
  4  the six worlds (a)-(f)                 (new run_h118)

and wires them into the runner.
"""

P = "harness118.lua"

s = open(P, encoding="utf-8").read()
assert "\r" not in s


# ---------------------------------------------------------------- file scope
SHARED = r'''
-- ============================================================================
-- ROUND 118 - THE DELAY IS GONE. THE SHARED PIECES FOR THE AIR-DROP SECTIONS.
--
-- THE USER'S RULING, verbatim: "I tried it. Let's keep the distance to center
-- and remove the delay we had completely."
--
-- The trigger now casts on the evaluation that first measures the nearest valid
-- enemy's CENTRE inside AIR_DROP_CENTER_M = 6 m. Everything that existed to
-- TIME a wait - the two dwell dials, the 0.3 s minimum-contact floor, the
-- per-pair contact row and its helpers, the purge hook, the enemy-velocity read
-- with its raw-read log body, the printed cosine, the dynamic-delay formula and
-- every dwell / hold / short-crossing line - is DELETED.
--
-- THE HARNESS FILE IS AT LUA'S 200-LOCAL CEILING (exactly like the mod), so
-- these shared pieces are named GLOBALS with an h118_ prefix rather than
-- file-scope locals: adding seven locals to the chunk does not compile.
--
-- H118_DEAD is the symbol list the static pin (section 1, per file, and world
-- (c)) searches for: every one of them must answer 0 occurrences in BOTH
-- shipped files, so a rebuild cannot quietly reintroduce a wait.
-- ============================================================================
H118_DEAD = {
  "AIR_DROP_DWELL_MID_S", "AIR_DROP_DWELL_SWING_S", "AIR_DROP_MIN_CONTACT_S",
  "FOURTH.ad_pair", "ad_pair_key", "ad_pair_stamp", "ad_pair_need", "ad_pair_drop",
  "ad_under", "ad_purge_unit", "ad_contact_clear", "zz_ad_dwell_purge",
  "ad_enemy_velocity", "ad_proj_text", "ad_dynamic_delay", "ad_vread",
  "FOURTH.ad_event", "ad_fired", "dwell", "short crossing", "proj=",
}
H118_DFA = "wh2_dlc09_unit_abilities_death_from_above"
H118_INF = "wh_main_inf_zombie_0"

-- A ground position object carrying battle_vector's documented reads.
function h118_cvec(x, z)
  x, z = x or 0, z or 0
  local v = {}
  function v:get_x() return x end
  function v:get_y() return 0 end
  function v:get_z() return z end
  function v:distance_xz(o)
    local ox, oz = o:get_x(), o:get_z()
    return math.sqrt(((x - ox) * (x - ox)) + ((z - oz) * (z - oz)))
  end
  return v
end

-- ONE caster (sky_junk / death_from_above, airborne) at the ORIGIN and ONE
-- 20-model enemy placed st.r metres away on the ground at bearing posdeg.
--   st.r is read on EVERY position() call, so a world moves the enemy by
--   assigning st.r and the NEXT evaluation measures the new CENTRE gap.
--   posdeg 0 -> the enemy sits on the +x axis (bearing 0).
--   hdeg nil -> the enemy is stationary (its order point IS its position).
--   hdeg set -> the enemy carries a real HEADING (ordered = position + 10 m on
--               that bearing), so a world can prove that a heading changes
--               NOTHING any more: the delay that used to be measured from it
--               does not exist.
--   opts.seq = { {x,z}, ... } feeds the position reads IN ORDER (read i uses
--               entry i, the last repeats) - used to drift the pair between the
--               picker and the pre-cast re-check of the SAME evaluation.
function h118_mk(uid, euid, st, posdeg, hdeg, opts)
  opts = opts or {}
  local def = { name = "sky_junk", uid = uid, owns = { H118_DFA }, melee = false }
  if opts.caster_raises then def.position_raises = true end
  local rad = (posdeg or 0) * math.pi / 180
  local ex, ez = math.cos(rad) * st.r, math.sin(rad) * st.r
  local edef = { name = H118_INF, uid = euid, men_alive = opts.men or 20, pos = { ex, 0, ez } }
  if hdeg ~= nil then
    local hr = hdeg * math.pi / 180
    edef.moving = true
    edef.fast = false
    edef.slow_speed = opts.speed or 2.5
    edef.fast_speed = 4.5
    edef.ordered = { ex + math.cos(hr) * 10, 0, ez + math.sin(hr) * 10 }
  else
    edef.ordered = { ex, 0, ez }
  end
  if opts.enemy_raises then edef.position_raises = true end
  local W = make_world({ can_perform = true, units = { def }, enemies = { edef },
    cards = { { id = tostring(uid), state = "active", vis = true } },
    bar = { { id = "b1", key = H118_DFA } } })
  local u = unit_of(W, uid)
  if u ~= nil then u.is_currently_flying = function() return true end end
  local eo = nil
  for i = 1, #(W.enemy_entries or {}) do
    local eu2 = W.enemy_entries[i].unit
    local ok_e2, id_e2 = pcall(function() return eu2:unique_ui_id() end)
    if ok_e2 and tostring(id_e2) == tostring(euid) then eo = eu2 end
  end
  if eo ~= nil and not opts.enemy_raises then
    if opts.bare_position then
      eo.position = function() return { get_y = function() return 0 end } end
    else
      eo.position = function()
        if opts.seq ~= nil then
          st.i = (st.i or 0) + 1
          local q = opts.seq[st.i] or opts.seq[#opts.seq]
          return h118_cvec(q[1], q[2])
        end
        local a = (posdeg or 0) * math.pi / 180
        return h118_cvec(math.cos(a) * st.r, math.sin(a) * st.r)
      end
      if hdeg ~= nil then
        eo.ordered_position = function()
          local p = eo.position()
          local hr = hdeg * math.pi / 180
          return h118_cvec(p:get_x() + math.cos(hr) * 10, p:get_z() + math.sin(hr) * 10)
        end
      end
    end
  end
  return W
end

function h118_boot(W, PATH, TAG, uid, wname)
  local ok = pcall(load_world, W, PATH)
  check(TAG .. wname .. ": the file loads", ok)
  if not ok then tally(W); return false end
  deploy_phases(W); ui(W)
  sel_event(W, uid, true); ui(W); ui(W)
  click(W, "zz_auto_badge_death_from_above"); ui(W)
  W.conflict = true
  return true
end

function h118_fastn(W, n)
  if W.fast_fn == nil then return false end
  for _ = 1, n do W.fast_fn() end
  return true
end

function h118_cp(s2, tok)
  local n, at = 0, 1
  while true do
    local i = raw_find(s2, tok, at, true)
    if i == nil then return n end
    n = n + 1
    at = i + 1
  end
end

function h118_span(s2, head, tail2)
  local i = raw_find(s2, head, 1, true)
  if i == nil then return nil end
  local j = raw_find(s2, tail2, i, true)
  if j == nil then return nil end
  return s2:sub(i, j)
end

function h118_lg(cond) return cond == true end

-- THE PRE-CAST RE-CHECK SPAN (the air-drop block inside FOURTH.try_pair).
function h118_recheck(s2)
  return h118_span(s2, "if FOURTH.ad_enemy ~= nil then", "\n\t-- SELF-SUMMON RE-CHECK")
    or h118_span(s2, "if FOURTH.ad_enemy ~= nil then", "\n  -- SELF-SUMMON RE-CHECK")
end
'''

# ---------------------------------------------------------------- section 1
NEW_H115 = r'''function run_h115()
  -- ROUND 118: this was harness 115's DWELL section. There is no dwell any
  -- more, so its worlds are gone and the section's job is now the opposite one:
  -- prove that every piece of the delay machinery is ABSENT from BOTH shipped
  -- files, and that WHAT STAYED is still wired exactly as before.
  if os.getenv("H118_LIVE") ~= nil then LIVE = os.getenv("H118_LIVE") end
  if os.getenv("H118_ANN") ~= nil then ANN = os.getenv("H118_ANN") end
  local red115 = (os.getenv("H118_LIVE") ~= nil) or (os.getenv("H118_ANN") ~= nil)
  local live_src = read_file(LIVE)
  local ann_src = read_file(ANN)
  local pre115 = checks
  local cp, span, lg = h118_cp, h118_span, h118_lg
  local function cl(W, frag) return count_log(W, frag) end

  -- ==========================================================================
  print("== HARNESS 118 - 1: the DELAY MACHINERY is GONE from both files ==")
  for _, f in ipairs({ { name = "live", src = live_src }, { name = "ann", src = ann_src } }) do
    local nm, s2 = f.name, f.src
    local pick = span(s2, "function FOURTH.ad_pick(unit, routing)",
      "\nfunction FOURTH.evaluate_air_drop_on_infantry")
    local recheck = h118_recheck(s2)

    -- (c) THE STATIC PIN, one check per deleted symbol per file.
    for _, tok in ipairs(H118_DEAD) do
      check("1 " .. nm .. ": deleted symbol '" .. tok .. "' occurs ZERO times ("
        .. cp(s2, tok) .. ")", cp(s2, tok) == 0)
    end

    check("1 " .. nm .. ": the four constants are defined EXACTLY ONCE (6 m centre / 10 men / 30 m / 0.2 s)",
      cp(s2, "\nFOURTH.AIR_DROP_CENTER_M = 6.0\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_MIN_MEN = 10\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_NEAR_M = 30\n") == 1
      and cp(s2, "\nFOURTH.AIR_DROP_FAST_S = 0.2\n") == 1)
    check("1 " .. nm .. ": the ONE comparison decides, and the NOT YET branch is the only early return",
      pick ~= nil
      and cp(pick, "if dist >= FOURTH.AIR_DROP_CENTER_M then") == 1
      and cp(pick, "-> NOT YET") == 1
      and cp(pick, "FOURTH.ad_say") == (nm == "ann" and 4 or 5)
      and (nm == "ann" or cp(pick, "-> FIRING") == 1))
    local after = nil
    if pick ~= nil then
      after = span(pick, nm == "ann" and "THE DECISION IS TAKEN NOW" or "-> FIRING",
        'return "nearest valid')
    end
    check("1 " .. nm .. ": the UNDER branch goes STRAIGHT to the cast (no second look, no time read)",
      after ~= nil
      and raw_find(after, "FOURTH.ad_enemy = enemy", 1, true) ~= nil
      and raw_find(after, "FOURTH.ad_caster_su = FOURTH.eg_fresh_caster_su(unit)", 1, true) ~= nil
      and raw_find(after, "centre=", 1, true) == nil)
    check("1 " .. nm .. ": the candidate filter is the same one scan (alive, > 10 men, readable centre)",
      cp(s2, "function FOURTH.ad_nearest(unit)") == 1
      and raw_find(s2, "alive > FOURTH.AIR_DROP_MIN_MEN", 1, true) ~= nil
      and raw_find(s2, "function FOURTH.ad_centre_gap(caster, enemy)", 1, true) ~= nil
      and raw_find(s2, "local d = FOURTH.ad_centre_gap(unit, enemy)", 1, true) ~= nil)
    check("1 " .. nm .. ": air_only / no_melee / the self-centred cast / fail-closed are ALL still in place",
      raw_find(s2, "is_currently_flying()", 1, true) ~= nil
      and raw_find(s2, "is_in_melee()", 1, true) ~= nil
      and raw_find(s2, "FOURTH.ad_air_only", 1, true) ~= nil
      and raw_find(s2, "FOURTH.ad_no_melee", 1, true) ~= nil
      and raw_find(s2, "perform_special_ability", 1, true) ~= nil
      and raw_find(s2, "pcall(function() return caster:position() end)", 1, true) ~= nil)
    check("1 " .. nm .. ": the pre-cast re-check re-measures the CENTRE on fresh handles and nothing else",
      recheck ~= nil
      and raw_find(recheck, "local centre_now = FOURTH.ad_centre_gap(unit, enemy)", 1, true) ~= nil
      and raw_find(recheck, "centre_ok = (centre_now ~= nil and centre_now < FOURTH.AIR_DROP_CENTER_M)", 1, true) ~= nil
      and raw_find(recheck, "and (not melee_now) and enemy_alive and men_ok and centre_ok) then", 1, true) ~= nil
      and (nm == "live" and raw_find(recheck, "-> SKIPPED at re-check", 1, true) ~= nil
        or nm == "ann" and raw_find(recheck, "the SKIPPED-at-re-check line is a log-only line", 1, true) ~= nil))
    check("1 " .. nm .. ": the fast pass and the poll are still BOTH registered, POLL_MS untouched",
      cp(s2, "bm:repeat_callback(") == 2
      and cp(s2, 'bm:repeat_callback(poll, POLL_MS, POLL_NAME)') == 1
      and cp(s2, "local POLL_MS = 250") == 1
      and cp(s2, "zz_test_deadly_onslaught_air_drop_fast") == 1
      and cp(s2, "dist < FOURTH.AIR_DROP_NEAR_M") == 1)
    check("1 " .. nm .. ": the family counts are unchanged (12 air-drop entries of 689)",
      cp(s2, 'trigger = "air_drop_on_infantry"') == 12 and cp(s2, "\t{ marker = ") == 689)
    check("1 " .. nm .. ": the tooltip says 6 m, cast immediately, no delay at all",
      raw_find(s2, 'air_drop_on_infantry = "When armed, fires when the nearest enemy unit with more than 10 models comes within 6 m', 1, true) ~= nil
      and raw_find(s2, "casts immediately on that evaluation - no delay at all", 1, true) ~= nil)
    if nm == "live" then
      check("1 live: every surviving air-drop line carries the caster ui id (ad_tag definition + 5 sites)",
        cp(s2, "FOURTH.ad_tag(unit)") == 6)
      check("1 live: the decision line prints the type, the entity count and the exact CENTRE gap",
        cp(s2, '"nearest valid:\'" .. etype .. "\' entities="') == 2
        and cp(s2, 'centre=" .. centre_text .. "m (need < " .. need .. "m)') == 2)
      check("1 live: NO air-drop line mentions a wait, a cosine or a contact",
        cp(s2, "reads: ") == 0 and cp(s2, "reads(hold)") == 0
        and cp(s2, "pair '") == 0 and cp(s2, "measured once") == 0)
    else
      check("1 ann: the reading copy stays LOG-FREE and carries the same helpers",
        raw_find(s2, "log(", 1, true) == nil
        and raw_find(s2, "function FOURTH.ad_nearest(unit)", 1, true) ~= nil
        and raw_find(s2, "function FOURTH.ad_say(unit, marker, note)", 1, true) ~= nil
        and raw_find(s2, "function FOURTH.ad_tag(unit)", 1, true) ~= nil)
    end
  end

  -- ==========================================================================
  print("== HARNESS 118 - 1: the caster's own row constraints still HOLD the drop ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17009, 17110
    local W = h118_mk(uid, euid, { r = 5.9 }, 0, nil)
    local u = unit_of(W, uid)
    if u ~= nil then u.is_currently_flying = function() return false end end
    if h118_boot(W, PATH, TAG, uid, "I") then
      polln(W, 6)
      check(TAG .. "I1: a GROUNDED caster never fires an air-only row, however long it sits under 6 m ("
        .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "I2: and it says why [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "-> HOLDING (this ability's row is air-only)") >= 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  if red115 then
    check("HARNESS 114 suite boundary (harness 118): N/A in the red run", true)
  elseif LIGHT then
    check("HARNESS 114 suite boundary (harness 118): LIGHT RUN - the air-drop sections only ("
      .. pre115 .. " checks so far)", pre115 >= 200)
  else
    check("HARNESS 114 suite boundary (harness 118): every earlier check ran first ("
      .. pre115 .. ")", pre115 >= 200)
  end
  check("HARNESS 118-1: the ZERO-search invariant still holds after the section (counted "
    .. find_calls .. ")", find_calls == 0)
  print("== HARNESS 118-1 done: checks " .. checks .. ", failures " .. failures .. " ==")
end
'''

# ---------------------------------------------------------------- section 2
NEW_H116 = r'''function run_h116()
  -- ROUND 118: this was harness 116's VELOCITY section - the cosine and the
  -- dynamic delay measured from the enemy's own heading. All of it is deleted,
  -- so the section now proves the NEGATIVE: the evaluator consults no movement
  -- flag, no speed, no order point and no clock, and a heading cannot move the
  -- cast by a single evaluation.
  local live_src = read_file(LIVE)
  local ann_src = read_file(ANN)
  local pre116 = checks
  local cp, span, lg = h118_cp, h118_span, h118_lg
  local function cl(W, frag) return count_log(W, frag) end

  -- ==========================================================================
  print("== HARNESS 118 - 2: the evaluator reads NO movement, NO heading and NO clock (both files) ==")
  for _, f in ipairs({ { name = "live", src = live_src }, { name = "ann", src = ann_src } }) do
    local nm, s2 = f.name, f.src
    local pick = span(s2, "function FOURTH.ad_pick(unit, routing)",
      "\nfunction FOURTH.evaluate_air_drop_on_infantry")
    check("2 " .. nm .. ": the evaluator reads NOTHING but the candidate scan and the centre gap",
      pick ~= nil
      and raw_find(pick, "is_moving", 1, true) == nil
      and raw_find(pick, "speed", 1, true) == nil
      and raw_find(pick, "ordered_position", 1, true) == nil
      and raw_find(pick, "position()", 1, true) == nil
      and raw_find(pick, "tick_count", 1, true) == nil
      and raw_find(pick, "POLL_MS", 1, true) == nil
      and raw_find(pick, "os.clock", 1, true) == nil)
    check("2 " .. nm .. ": no per-pair table and no elapsed read over one",
      cp(s2, "FOURTH.ad_pair") == 0
      and raw_find(pick, "tick_count", 1, true) == nil)
    check("2 " .. nm .. ": the only state the family keeps is the dedupe + fast-pass bookkeeping",
      raw_find(s2, "FOURTH.ad_note = {}", 1, true) ~= nil
      and raw_find(s2, "FOURTH.ad_fast_on = {}", 1, true) ~= nil
      and raw_find(s2, "FOURTH.ad_fast_abilities = {}", 1, true) ~= nil)
  end

  -- ==========================================================================
  print("== HARNESS 118 - 2: a real HEADING cannot delay the cast by one evaluation ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    -- The enemy is RUNNING STRAIGHT AWAY from the caster (bearing 0, heading 0).
    -- Under the deleted rule that measured proj = -1 and a 2.00 s wait; there is
    -- no wait at all now, so the FIRST evaluation casts.
    local uid, euid = 17420, 17520
    local W = h118_mk(uid, euid, { r = 5.9 }, 0, 0)
    if h118_boot(W, PATH, TAG, uid, "V1") then
      polln(W, 1)
      check(TAG .. "V1a: an enemy running AWAY at 5.9 m fires on the FIRST evaluation ("
        .. #W.fires .. ")", #W.fires == 1)
      check(TAG .. "V1b: the decision line is the plain FIRING line - no measurement, no wait [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "centre=5.90m (need < 6.00m) -> FIRING (the nearest") == 1
            and cl(W, "measured once") == 0 and cl(W, " src=") == 0)))
      h118_fastn(W, 2)
      check(TAG .. "V1c: two fast ticks inside the guard add nothing (" .. #W.fires .. ")",
        #W.fires == 1)
      tally(W)
    end
  end

  -- ==========================================================================
  check("HARNESS 115 suite boundary (harness 118): the earlier sections ran first ("
    .. pre116 .. ")", pre116 >= 200)
  check("HARNESS 118-2: the ZERO-search invariant still holds after the section (counted "
    .. find_calls .. ")", find_calls == 0)
  print("== HARNESS 118-2 done: checks " .. checks .. ", failures " .. failures .. " ==")
end
'''

# ---------------------------------------------------------------- section 3
NEW_H117 = r'''function run_h117()
  -- ROUND 118: the CENTRE measurement is the ONE thing round 117 added that is
  -- still here, so this section keeps its static pins - retouched where they
  -- described the delay - and its worlds have moved to the section below.
  local live_src = read_file(LIVE)
  local ann_src = read_file(ANN)
  local pre117 = checks
  local cp, span, lg = h118_cp, h118_span, h118_lg

  -- ==========================================================================
  print("== HARNESS 118 - 3: the CENTRE measurement, and what still hangs off it ==")
  for _, f in ipairs({ { name = "live", src = live_src }, { name = "ann", src = ann_src } }) do
    local nm, s2 = f.name, f.src
    local pick = span(s2, "function FOURTH.ad_pick(unit, routing)",
      "\nfunction FOURTH.evaluate_air_drop_on_infantry")
    local helper = span(s2, "function FOURTH.ad_centre_gap(caster, enemy)", "\nend")
    local nearest = span(s2, "function FOURTH.ad_nearest(unit)", "\nend")
    local recheck = h118_recheck(s2)

    check("3 " .. nm .. ": the centre helper is defined ONCE, x/z only, with the distance_xz fallback",
      helper ~= nil
      and cp(s2, "function FOURTH.ad_centre_gap(caster, enemy)") == 1
      and raw_find(helper, "get_x()", 1, true) ~= nil
      and raw_find(helper, "get_z()", 1, true) ~= nil
      and raw_find(helper, "distance_xz", 1, true) ~= nil
      and raw_find(helper, "math.sqrt((dx * dx) + (dz * dz))", 1, true) ~= nil
      and raw_find(helper, "get_y()", 1, true) == nil)
    check("3 " .. nm .. ": the scan picks the NEAREST valid candidate by that centre gap, and nothing else",
      nearest ~= nil
      and raw_find(nearest, "local d = FOURTH.ad_centre_gap(unit, enemy)", 1, true) ~= nil
      and raw_find(nearest, "if d ~= nil and (best_d == nil or d < best_d) then", 1, true) ~= nil
      and raw_find(nearest, "unit_distance", 1, true) == nil
      and raw_find(nearest, "is_infantry", 1, true) == nil)
    check("3 " .. nm .. ": the picker compares the CENTRE once and never an EDGE",
      pick ~= nil
      and cp(pick, "FOURTH.AIR_DROP_CENTER_M") == 2
      and raw_find(pick, "dist >= FOURTH.AIR_DROP_CENTER_M", 1, true) ~= nil
      and raw_find(pick, " -> NOT YET", 1, true) ~= nil
      and raw_find(pick, "FOURTH.AIR_DROP_EDGE_M", 1, true) == nil
      and raw_find(pick, "unit_distance", 1, true) == nil)
    check("3 " .. nm .. ": the pre-cast re-check re-measures the SAME centre on FRESH handles",
      recheck ~= nil
      and raw_find(recheck, "local centre_now = FOURTH.ad_centre_gap(unit, enemy)", 1, true) ~= nil
      and raw_find(recheck, "centre_now < FOURTH.AIR_DROP_CENTER_M", 1, true) ~= nil
      and raw_find(recheck, "centre_ok) then", 1, true) ~= nil
      and raw_find(recheck, "edge_text", 1, true) == nil
      and raw_find(recheck, "eg_enemy_gap", 1, true) == nil)
    check("3 " .. nm .. ": the bound follows the rule (ability.range_m = the 6 m line)",
      cp(s2, "ability.range_m = FOURTH.AIR_DROP_CENTER_M") == 1)
    check("3 " .. nm .. ": the change is LOCAL - eg_enemy_gap still serves the other triggers",
      cp(s2, "function FOURTH.eg_enemy_gap(unit, enemy)") == 1
      and cp(s2, "FOURTH.eg_enemy_gap(") >= 4)
    if nm == "live" then
      check("3 live: no live code path can still ask for the edge gap in this family",
        raw_find(s2, "FOURTH.AIR_DROP_EDGE_M", 1, true) == nil)
    else
      check("3 ann: the reading copy stays LOG-FREE and carries the same centre helper",
        raw_find(s2, "log(", 1, true) == nil
        and helper ~= nil
        and raw_find(helper, "distance_xz", 1, true) ~= nil
        and raw_find(s2, "function FOURTH.ad_nearest(unit)", 1, true) ~= nil)
    end
  end

  -- ==========================================================================
  check("HARNESS 116 suite boundary (harness 118): the earlier sections ran first ("
    .. pre117 .. ")", pre117 >= 250)
  check("HARNESS 118-3: the ZERO-search invariant still holds after the section (counted "
    .. find_calls .. ")", find_calls == 0)
  print("== HARNESS 118-3 done: checks " .. checks .. ", failures " .. failures .. " ==")
end
'''

# ---------------------------------------------------------------- section 4
NEW_H118 = r'''function run_h118()
  -- ROUND 118 - THE SIX WORLDS. The trigger fires on the EVALUATION that first
  -- measures the nearest valid enemy's centre inside 6 m; nothing waits, nothing
  -- is stamped, and the pre-cast re-check re-measures the centre on fresh
  -- handles before the call.
  local pre118 = checks
  local cp, span, lg = h118_cp, h118_span, h118_lg
  local function cl(W, frag) return count_log(W, frag) end

  -- ==========================================================================
  print("== HARNESS 118 - (a) a 5.9 m centre CASTS on the FIRST evaluation ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17431, 17531
    local W = h118_mk(uid, euid, { r = 5.9 }, 0, nil)
    if h118_boot(W, PATH, TAG, uid, "A") then
      polln(W, 1)
      check(TAG .. "A1: the FIRST poll casts, once (" .. #W.fires .. ")", #W.fires == 1)
      check(TAG .. "A2: the decision line names the enemy, its count and the centre [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "nearest valid:'wh_main_inf_zombie_0' entities=20 centre=5.90m"
              .. " (need < 6.00m) -> FIRING (the nearest of the valid enemies") == 1)))
      check(TAG .. "A3: the re-check accepted the SAME centre [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "centre=5.90m (need < 6.00m) -> FIRING (re-checked)") == 1)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 118 - (b) a 6.1 m centre casts NOTHING ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17432, 17532
    local W = h118_mk(uid, euid, { r = 6.1 }, 0, nil)
    if h118_boot(W, PATH, TAG, uid, "B") then
      polln(W, 6)
      h118_fastn(W, 5)
      check(TAG .. "B1: six polls and five fast ticks at 6.1 m cast NOTHING (" .. #W.fires .. ")",
        #W.fires == 0)
      check(TAG .. "B2: the line says centre=6.10m against the 6.00 m line [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "centre=6.10m (need < 6.00m) -> NOT YET") == 1
            and cl(W, "-> FIRING") == 0)))
      check(TAG .. "B3: and no contact/dwell line exists to print [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "waiting") == 0 and cl(W, "under at gap") == 0)))
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 118 - (c) NO delay/timestamp state survives, in EITHER file ==")
  local live_src = read_file(LIVE)
  local ann_src = read_file(ANN)
  local n_bad, n_tok = 0, 0
  for _, pair in ipairs({ { nm = "live", src = live_src }, { nm = "ann", src = ann_src } }) do
    for _, tok in ipairs(H118_DEAD) do
      n_tok = n_tok + 1
      if cp(pair.src, tok) ~= 0 then n_bad = n_bad + 1 end
    end
  end
  check("C1: every deleted symbol occurs ZERO times in BOTH files (" .. n_tok
    .. " symbols searched, " .. n_bad .. " hits)", n_bad == 0)
  check("C2: no per-pair/caster state table is declared in either file",
    cp(live_src, "FOURTH.ad_pair") == 0 and cp(ann_src, "FOURTH.ad_pair") == 0)
  check("C3: neither file reads a clock inside the air-drop evaluator",
    (function()
      local ok = true
      for _, s2 in ipairs({ live_src, ann_src }) do
        local pick = span(s2, "function FOURTH.ad_pick(unit, routing)",
          "\nfunction FOURTH.evaluate_air_drop_on_infantry")
        if pick == nil or raw_find(pick, "tick_count", 1, true) ~= nil
          or raw_find(pick, "os.clock", 1, true) ~= nil then ok = false end
      end
      return ok
    end)())

  -- ==========================================================================
  print("== HARNESS 118 - (d) a second evaluation right after a cast does NOT double-cast ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17434, 17534
    local W = h118_mk(uid, euid, { r = 5.9 }, 0, nil)
    if h118_boot(W, PATH, TAG, uid, "D") then
      polln(W, 1)
      check(TAG .. "D1: the first evaluation cast once (" .. #W.fires .. ")", #W.fires == 1)
      h118_fastn(W, 5)
      check(TAG .. "D2: five fast evaluations in the same window cast NOTHING more ("
        .. #W.fires .. ")", #W.fires == 1)
      polln(W, 2)
      check(TAG .. "D3: nor do the next two polls, inside the 2 s guard (" .. #W.fires .. ")",
        #W.fires == 1)
      check(TAG .. "D4: exactly ONE re-checked firing line in the whole window [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "-> FIRING (re-checked)") == 1)))
      polln(W, 12)
      check(TAG .. "D5: past the guard the still-under pair casts again, once (" .. #W.fires .. ")",
        #W.fires == 2)
      tally(W)
    end
  end

  -- ==========================================================================
  print("== HARNESS 118 - (e) unreadable positions FAIL CLOSED ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17435, 17535
    local W = h118_mk(uid, euid, { r = 5.9 }, 0, nil, { caster_raises = true })
    if h118_boot(W, PATH, TAG, uid, "E1") then
      polln(W, 6)
      check(TAG .. "E1a: an unreadable CASTER position casts nothing, no crash (" .. #W.fires .. ")",
        #W.fires == 0)
      tally(W)
    end
    local uid2, euid2 = 17436, 17536
    local W2 = h118_mk(uid2, euid2, { r = 5.9 }, 0, nil, { enemy_raises = true })
    if h118_boot(W2, PATH, TAG, uid2, "E2") then
      polln(W2, 6)
      check(TAG .. "E2a: an unreadable ENEMY position casts nothing (" .. #W2.fires .. ")",
        #W2.fires == 0)
      tally(W2)
    end
    local uid3, euid3 = 17437, 17537
    local W3 = h118_mk(uid3, euid3, { r = 5.9 }, 0, nil, { bare_position = true })
    if h118_boot(W3, PATH, TAG, uid3, "E3") then
      polln(W3, 6)
      check(TAG .. "E3a: a position object with no get_x/get_z casts nothing (" .. #W3.fires .. ")",
        #W3.fires == 0)
      tally(W3)
    end
  end

  -- ==========================================================================
  print("== HARNESS 118 - (f) the pre-cast re-check RE-MEASURES: 5.9 -> 6.1 SKIPS ==")
  for _, f in ipairs({ { path = LIVE, tag = "[live] " }, { path = ANN, tag = "[ann] " } }) do
    local PATH, TAG = f.path, f.tag
    local uid, euid = 17438, 17538
    -- The FIRST evaluation makes exactly TWO position reads on the chosen enemy:
    -- read 1 is the picker (5.9 m, under the line), read 2 is the pre-cast
    -- re-check of the SAME evaluation, which must see the drift to 6.1 m.
    local seq = { { 5.9, 0 }, { 6.1, 0 } }
    local W = h118_mk(uid, euid, { r = 5.9, i = 0 }, 0, nil, { seq = seq })
    if h118_boot(W, PATH, TAG, uid, "F") then
      polln(W, 1)
      check(TAG .. "F1: the picker measured 5.9 m but the re-check measured 6.1 m - no cast ("
        .. #W.fires .. ")", #W.fires == 0)
      check(TAG .. "F2: the skip line prints the FRESH centre gap and names the lapsed test [live log]",
        lg((TAG ~= "[live] ")
          or (cl(W, "centre=6.10m (need < 6.00m) -> SKIPPED at re-check") == 1
            and cl(W, "centre_ok=false") == 1
            and cl(W, "- cast not spent") == 1)))
      check(TAG .. "F3: the refused cast was NOT spent - the re-check never said FIRING [live log]",
        lg((TAG ~= "[live] ") or (cl(W, "-> FIRING (re-checked)") == 0)))
      -- back inside the line on freshly-read handles: the pair casts once the
      -- guard window the refused attempt consumed has passed.
      seq[3] = { 5.9, 0 }
      seq[4] = { 5.9, 0 }
      polln(W, 10)
      check(TAG .. "F4: still 5.9 m on FRESH handles, it casts once the guard has passed ("
        .. #W.fires .. ")", #W.fires == 1)
      tally(W)
    end
    -- the same world WITHOUT the drift: the picker and the re-check agree, so
    -- the cast goes out on the same evaluation (the control for F1)
    local uid2, euid2 = 17439, 17539
    local W2 = h118_mk(uid2, euid2, { r = 5.9, i = 0 }, 0, nil,
      { seq = { { 5.9, 0 }, { 5.9, 0 } } })
    if h118_boot(W2, PATH, TAG, uid2, "F0") then
      polln(W2, 1)
      check(TAG .. "F0: with no drift the same world casts ON THE FIRST evaluation ("
        .. #W2.fires .. ")", #W2.fires == 1)
      tally(W2)
    end
  end

  -- ==========================================================================
  check("HARNESS 117 suite boundary (harness 118): the earlier air-drop sections ran ("
    .. pre118 .. ")", pre118 >= 250)
  check("HARNESS 118: the ZERO-search invariant still holds after the six worlds (counted "
    .. find_calls .. ")", find_calls == 0)
  print("== HARNESS 118 done: checks " .. checks .. ", failures " .. failures .. " ==")
end
'''


def cut(s, start, end_excl, new, tag):
    assert s.count(start) == 1, "%s start matched %d" % (tag, s.count(start))
    assert s.count(end_excl) == 1, "%s end matched %d" % (tag, s.count(end_excl))
    i = s.index(start)
    j = s.index(end_excl, i)
    assert j > i, tag
    return s[:i] + new + s[j:]


# 1. the shared file-scope pieces, inserted just above run_h115
s = s.replace("function run_h115()\n", SHARED + "\nfunction run_h115()\n", 1)
assert s.count("H118_DEAD = {") == 1

# 2. the three retouched sections
s = cut(s,
        "function run_h115()\n",
        "\n-- ============================================================================\n-- HARNESS 116 - THE WAIT IS MEASURED",
        NEW_H115, "h115")
s = cut(s,
        "function run_h116()\n",
        "\n-- ============================================================================\n-- HARNESS 117",
        NEW_H116, "h116")
s = cut(s,
        "function run_h117()\n",
        "\n-- THE RUNNER.",
        NEW_H117 + "\n" + NEW_H118 + "\n", "h117")

# 3. h114's ad_tag site count (the delay deletion removed five of the old
#    sites: the definition plus five surviving call sites remain).
OLD_ADTAG = """      check("0 live: every decision + transition line carries the caster ui id (ad_tag definition + 6 sites)",
        cp(s2, "FOURTH.ad_tag(unit)") == 7)"""
NEW_ADTAG = """      check("0 live: every air-drop line still carries the caster ui id (ad_tag definition + 5 sites)",
        cp(s2, "FOURTH.ad_tag(unit)") == 6)"""
assert s.count(OLD_ADTAG) == 1, "the h114 ad_tag pin was not found"
s = s.replace(OLD_ADTAG, NEW_ADTAG)

# 4. the runner
old_run = """run_h112()
run_h114()
run_h115()
run_h116()
run_h117()
"""
new_run = """run_h112()
run_h114()
run_h115()
run_h116()
run_h117()
run_h118()
"""
assert s.count(old_run) == 1
s = s.replace(old_run, new_run)

s = s.replace('print("== HARNESS 117 - LIGHT RUN: the AIR-DROP sections only (h109-h117) ==")',
              'print("== HARNESS 118 - LIGHT RUN: the AIR-DROP sections only ==")')

assert "\r" not in s
open(P, "w", encoding="utf-8", newline="").write(s)
print("harness118.lua spliced:", len(s), "bytes")
print("checks() in file:", s.count("check("))
