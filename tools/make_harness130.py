#!/usr/bin/env python3
"""Build harness130.lua from harness129.lua for round 131 (the shooting buffs leave the melee
trigger, Potion of Farsight's out-of-range trigger, the firing aura counts the caster, the nine
stances leave the mod). Older harnesses are never edited.

Pin rebases (each a count or text the round deliberately moves; comment lines untouched):
  entries 709 -> 700 (9 stances removed), keys 761 -> 752,
  melee_unwavering 373 -> 354 (10 moved to shooting triggers, 9 stances removed),
  ally_range_real fields 42 -> 44 (Deranged Munitions 100 m, Entrenchment 150 m),
  wind-up keys 170 -> 165 (the 5 stance keys that had a wind-up row),
  full-table iterations 1418 -> 1400 (2 x 700),
  harness-104 0p: the two Slaanesh dance markers must now be ABSENT,
  harness-129 0y: FOURTH.BALLISTICS_MIN_FIRING = 2 -> FOURTH.FIRING_AURA_MIN = 1,
  harness-129 B1b: the aura reason text (the caster counts now),
  harness-129 B2a: one shooter within 38 m now casts (the user's round-131 ruling),
  the harness-93 tooltip mirror: allies_firing_aura reworded, three new wordings.
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261101_firing_flag_triggers_harness129\harness129.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261101_shooting_triggers_harness130\harness130.lua"

BANNER = """-- ============================================================================
-- HARNESS 130 - ROUND 131: THE SHOOTING BUFFS LEAVE THE MELEE TRIGGER.
--   Ten abilities move off melee_unwavering (7 shooting auras, Deranged
--   Munitions, Entrenchment, Potion of Farsight); the firing aura counts the
--   caster and needs 1 shooter; the nine stances leave the mod.
--   Edited vs harness129: this banner, the pin rebases listed in
--   tools/make_harness130.py, the tooltip mirror, run_h130 and its call.
--   RED control: H130_LIVE / H130_ANN on docs/backups/round131/pre131_*.lua.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 130 (round 131): THE SHOOTING BUFFS LEAVE THE MELEE TRIGGER.
--   0zb: tokens (the nine stances are gone, the new triggers are wired).
--   T1 Hail of Fire: the caster itself shooting, no ally -> ONE self cast on its
--      cast point (poll 28).
--   T2 Hail of Fire: the caster does not shoot, one ally shooting 30 m away (bound
--      38 m) -> ONE cast, on the caster.
--   T3 Hail of Fire: the only shooting ally is 45 m away -> no cast.
--   D1 Deranged Munitions: the caster shooting -> ONE cast on itself.
--   D2 Deranged Munitions: the caster not shooting, allies shooting at 50 m and
--      20 m (bound 70 m) -> ONE cast on the 20 m ally.
--   D3 Deranged Munitions: the only shooting ally is 80 m away -> no cast.
--   E1 Entrenchment: in melee -> ONE self cast. E2: not shooting, one ally
--      shooting at 100 m (bound 105 m) -> ONE cast on that ally.
--   F1 Potion of Farsight: missile range 150 m, nearest enemy 170 m (<= 181.5) ->
--      ONE self cast. F2: one enemy at 140 m (in range) -> no cast. F3: nearest
--      enemy 190 m -> no cast. F4: in melee -> no cast.
--   RED (pre-131 build = round 130): T2, D2 and F1 cast nothing; E1 still casts.
-- ============================================================================
function run_h130()
  local L130 = os.getenv("H130_LIVE") or LIVE
  local A130 = os.getenv("H130_ANN") or ANN
  local RED130 = (os.getenv("H130_LIVE") ~= nil) or (os.getenv("H130_ANN") ~= nil)
  local HK = "wh2_dlc13_lord_abilities_hail_of_fire"
  local DK = "wh3_dlc25_lord_abilities_deranged_munitions"
  local EK = "wh_main_unit_abilities_entrenchment"
  local FK = "wh3_main_item_abilities_potion_of_farsight"
  local HG = "wh_main_emp_inf_handgunners"   -- reload 13 s: cast point 6.5 s (26 polls) after the first shot
  local LORD = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local ZOMB = "wh_main_vmp_inf_zombie"
  local pre130 = checks
  local function lg(tag, v) return (tag ~= "[live] ") or v end

  print("== HARNESS 130 - section 0zb: the round-131 tokens ==")
  if not RED130 then
    for _, f in ipairs({ { name = "live", path = L130 }, { name = "ann", path = A130 } }) do
      local s = read_file(f.path)
      local gone = true
      for _, m in ipairs({ "master_predator", "immovable_bulwark", "unstoppable_choppas", "the_shadows_coil",
                           "woven_mist", "chanson_of_caging", "the_dance_of_dreaming", "the_praise_of_slaanesh",
                           "the_waltz_of_lethargy" }) do
        if raw_find(s, m, 1, true) ~= nil then gone = false end
      end
      check("0zb " .. f.name .. ": the nine stances are gone (no marker, key or wind-up row)", gone)
      check("0zb " .. f.name .. ": the three new evaluators are wired",
        raw_find(s, "self_or_ally_shooting = FOURTH.evaluate_self_or_ally_shooting,", 1, true) ~= nil
        and raw_find(s, "melee_or_self_or_ally_shooting = FOURTH.evaluate_melee_or_self_or_ally_shooting,", 1, true) ~= nil
        and raw_find(s, "no_enemy_in_range_within_boost = FOURTH.evaluate_no_enemy_in_range_within_boost,", 1, true) ~= nil)
      check("0zb " .. f.name .. ": the aura counts the caster and needs one shooter; Farsight's band is 1 + 0.30 x 0.70",
        raw_find(s, "FOURTH.FIRING_AURA_MIN = 1 ", 1, true) ~= nil
        and raw_find(s, "local own = FOURTH.shooting_past_cast_point(unit) and 1 or 0", 1, true) ~= nil
        and raw_find(s, "FOURTH.FARSIGHT_BAND = 1 + FOURTH.FARSIGHT_BONUS * FOURTH.RANGE_FRACTION", 1, true) ~= nil)
    end
  end

  local FILES = { { path = A130, tag = "[annotated] " }, { path = L130, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function unit130(W, uid)
    for i = 1, #(W.live_entries or {}) do
      local pr = W.live_entries[i]
      local ok, id = pcall(function() return pr.unit:unique_ui_id() end)
      if ok and tostring(id) == tostring(uid) then return pr.unit end
    end
    return nil
  end
  local function fires_of(W, key)
    local n = 0
    for _, f in ipairs(W.fires) do if f.key == key then n = n + 1 end end
    for _, f in ipairs(W.ground_fires) do if f.key == key then n = n + 1 end end
    return n
  end
  local function world(wname, units, arm, keys, PATH, TAG, polls, enemies)
    local cards, bar = {}, {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    for i, k in ipairs(keys) do bar[#bar + 1] = { id = "b" .. i, key = k } end
    local W = make_world({ can_perform = true, units = units, cards = cards, bar = bar, enemies = enemies })
    print("== " .. TAG .. wname .. " ==")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    for _, a in ipairs(arm) do
      sel_event(W, a[1], true); ui(W); ui(W)
      click(W, "zz_auto_badge_" .. a[2]); ui(W)
      sel_event(W, a[1], false); ui(W)
    end
    W.conflict = true
    polln(W, polls)
    return W
  end
  -- a unit that shoots from poll 2 on (one ammo drop), at `dist` from the caster
  local function shooter(name, uid, dist, extra)
    local d = { name = name, uid = uid, owns = {}, melee = false, ammo_start = 100, ammo_seq = { 100, 99 }, dist = dist }
    for k, v in pairs(extra or {}) do d[k] = v end
    return d
  end
  local function caster(uid, key, extra)
    local d = { name = LORD, uid = uid, owns = { key }, melee = false }
    for k, v in pairs(extra or {}) do d[k] = v end
    return d
  end
  local function one_on(W, key, cuid, want_uid, tick)
    local f = nil
    for _, x in ipairs(W.fires) do if x.key == key then f = x end end
    return fires_of(W, key) == 1 and f ~= nil and f.target == unit130(W, want_uid)
      and (tick == nil or f.tick == tick), f
  end

  for _, f in ipairs(FILES) do
    local TAG = f.tag

    if not RED130 then
      -- T1: the caster itself shooting
      local W = world("T1. Hail of Fire: the caster shooting, no ally -> ONE self cast on its cast point",
        { shooter(HG, 13101, 0, { owns = { HK } }) }, { { 13101, "hail_of_fire" } }, { HK }, f.path, TAG, 32)
      if W ~= nil then
        local a, x = one_on(W, HK, 13101, 13101, 2 + 26)
        check(TAG .. "T1a: ONE cast on the caster, poll 28 (tick " .. tostring(x and x.tick) .. ")", a)
        local b = (count_log(W, "hail_of_fire: 1 unit(s) within 38m are shooting past their cast point (0 allies + the caster shooting; need 1)") >= 1)
        check(TAG .. "T1b: the reason counts the caster [live log]", lg(TAG, b))
        done(a and lg(TAG, b))
        tally(W)
      end
    end

    -- T2: one ally shooting inside the bound (also a RED world)
    local W2 = world("T2. Hail of Fire: the caster does not shoot, one ally shooting at 30 m -> ONE cast on the caster",
      { caster(13111, HK), shooter(HG, 13112, 30) }, { { 13111, "hail_of_fire" } }, { HK }, f.path, TAG, 32)
    if W2 ~= nil then
      if RED130 then
        local rep = (fires_of(W2, HK) == 0)
        check(TAG .. "T2-RED: the pre-131 build waits for melee - no cast (" .. fires_of(W2, HK) .. ")", rep)
        done(rep)
      else
        local a = one_on(W2, HK, 13111, 13111, 2 + 26)
        check(TAG .. "T2a: ONE cast on the caster when the ally reaches its cast point (" .. fires_of(W2, HK) .. ")", a)
        done(a)
      end
      tally(W2)
    end

    if not RED130 then
      local W3 = world("T3. Hail of Fire: the only shooting ally is 45 m away (bound 38 m) -> no cast",
        { caster(13121, HK), shooter(HG, 13122, 45) }, { { 13121, "hail_of_fire" } }, { HK }, f.path, TAG, 32)
      if W3 ~= nil then
        local a = (fires_of(W3, HK) == 0)
        check(TAG .. "T3a: no cast (" .. fires_of(W3, HK) .. ")", a)
        done(a)
        tally(W3)
      end

      local Wd1 = world("D1. Deranged Munitions: the caster shooting -> ONE cast on itself",
        { shooter(HG, 13131, 0, { owns = { DK } }) }, { { 13131, "deranged_munitions" } }, { DK }, f.path, TAG, 32)
      if Wd1 ~= nil then
        local a = one_on(Wd1, DK, 13131, 13131, 2 + 26)
        check(TAG .. "D1a: ONE cast on the caster (" .. fires_of(Wd1, DK) .. ")", a)
        done(a)
        tally(Wd1)
      end
    end

    -- D2: the closest shooting ally (also a RED world)
    local Wd2 = world("D2. Deranged Munitions: the caster not shooting, allies shooting at 50 m and 20 m -> ONE cast on the 20 m ally",
      { caster(13141, DK), shooter(HG, 13142, 50), shooter(HG, 13143, 20) },
      { { 13141, "deranged_munitions" } }, { DK }, f.path, TAG, 32)
    if Wd2 ~= nil then
      if RED130 then
        local rep = (fires_of(Wd2, DK) == 0)
        check(TAG .. "D2-RED: the pre-131 build waits for melee - no cast (" .. fires_of(Wd2, DK) .. ")", rep)
        done(rep)
      else
        local a = one_on(Wd2, DK, 13141, 13143, 2 + 26)
        check(TAG .. "D2a: ONE cast, on the closest shooting ally (" .. fires_of(Wd2, DK) .. ")", a)
        local b = (count_log(Wd2, "deranged_munitions: the caster is not shooting; the closest ally shooting past its cast point, cast on ally") == 1)
        check(TAG .. "D2b: the reason names the ally arm [live log]", lg(TAG, b))
        done(a and lg(TAG, b))
      end
      tally(Wd2)
    end

    if not RED130 then
      local Wd3 = world("D3. Deranged Munitions: the only shooting ally is 80 m away (bound 70 m) -> no cast",
        { caster(13151, DK), shooter(HG, 13152, 80) }, { { 13151, "deranged_munitions" } }, { DK }, f.path, TAG, 32)
      if Wd3 ~= nil then
        local a = (fires_of(Wd3, DK) == 0)
        check(TAG .. "D3a: no cast (" .. fires_of(Wd3, DK) .. ")", a)
        done(a)
        tally(Wd3)
      end
    end

    -- E1: the melee arm stays (the RED positive control)
    local We1 = world("E1. Entrenchment: in melee -> ONE self cast",
      { caster(13161, EK, { melee = true }) }, { { 13161, "entrenchment" } }, { EK }, f.path, TAG, 4)
    if We1 ~= nil then
      local a = (fires_of(We1, EK) == 1 and fire_target_for(We1, 13161) == unit130(We1, 13161))
      check(TAG .. "E1a: ONE cast on the caster in melee (" .. fires_of(We1, EK) .. ")", a)
      done(a)
      tally(We1)
    end

    if not RED130 then
      local We2 = world("E2. Entrenchment: not shooting, one ally shooting at 100 m (bound 105 m) -> ONE cast on the ally",
        { caster(13171, EK), shooter(HG, 13172, 100) }, { { 13171, "entrenchment" } }, { EK }, f.path, TAG, 32)
      if We2 ~= nil then
        local a = one_on(We2, EK, 13171, 13172, 2 + 26)
        check(TAG .. "E2a: ONE cast on the shooting ally (" .. fires_of(We2, EK) .. ")", a)
        done(a)
        tally(We2)
      end
    end

    -- F1..F4: Potion of Farsight
    local function farsight(wname, uid, gaps, extra, polls)
      local enemies, byt = {}, {}
      for i, g in ipairs(gaps) do
        enemies[#enemies + 1] = { name = ZOMB, uid = uid + 10 + i, owns = {}, melee = false }
        byt[uid + 10 + i] = g
      end
      local d = { name = HG, uid = uid, owns = { FK }, melee = false, ammo_start = 100, ammo_seq = { 100 },
                  missile_range = 150, dist_by_target = byt }
      for k, v in pairs(extra or {}) do d[k] = v end
      return world(wname, { d }, { { uid, "potion_of_farsight" } }, { FK }, f.path, TAG, polls or 4, enemies)
    end
    local Wf1 = farsight("F1. Potion of Farsight: range 150 m, nearest enemy 170 m (<= 181.5 m) -> ONE self cast", 13181, { 170, 260 })
    if Wf1 ~= nil then
      if RED130 then
        local rep = (fires_of(Wf1, FK) == 0)
        check(TAG .. "F1-RED: the pre-131 build waits for melee - no cast (" .. fires_of(Wf1, FK) .. ")", rep)
        done(rep)
      else
        local a = (fires_of(Wf1, FK) == 1 and fire_target_for(Wf1, 13181) == unit130(Wf1, 13181))
        check(TAG .. "F1a: ONE self cast (" .. fires_of(Wf1, FK) .. ")", a)
        local b = (count_log(Wf1, "no enemy inside the missile range 150.0m; the nearest enemy is at 170.0m, inside range x 1.21 = 181.5m, cast on self") == 1)
        check(TAG .. "F1b: the reason names the range, the gap and the band [live log]", lg(TAG, b))
        done(a and lg(TAG, b))
      end
      tally(Wf1)
    end
    if not RED130 then
      for _, c in ipairs({
        { "F2. Potion of Farsight: one enemy at 140 m is already in range -> no cast", 13191, { 140, 170 }, nil },
        { "F3. Potion of Farsight: the nearest enemy is 190 m away (> 181.5 m) -> no cast", 13201, { 190 }, nil },
        { "F4. Potion of Farsight: in melee -> no cast", 13211, { 170 }, { melee = true } } }) do
        local Wf = farsight(c[1], c[2], c[3], c[4])
        if Wf ~= nil then
          local a = (fires_of(Wf, FK) == 0)
          check(TAG .. c[1]:sub(1, 2) .. "a: no cast (" .. fires_of(Wf, FK) .. ")", a)
          done(a)
          tally(Wf)
        end
      end
    end
  end

  if RED130 then
    check("RED CONTROL (harness 130): the pre-131 build casts the shooting buffs only in melee - "
      .. n_ok .. "/" .. n_all, n_all == 8 and n_ok == 8)
  else
    check("HARNESS 130: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 24 and n_ok == 24)
  end
  print("== HARNESS 130 done: " .. (checks - pre130) .. " checks in this section ==")
end
'''

PIN_RULES = [
    ("== 709", "== 700"),
    ("== 761", "== 752"),
    ("'trigger = \"melee_unwavering\"') == 373", "'trigger = \"melee_unwavering\"') == 354"),
    ("mu == 373", "mu == 354"),
    ("entries = 709, keys = 761, mu = 373", "entries = 700, keys = 752, mu = 354"),
    ("entries = 709, keys = 761, sum = true", "entries = 700, keys = 752, sum = true"),
    ("FULL 709-entry table", "FULL 700-entry table"),
    ("709 abilities per pass", "700 abilities per pass"),
    ("has 709 entries", "has 700 entries"),
    ("has all 761 keys", "has all 752 keys"),
    ("table of 709 after round 130", "table of 700 after round 131"),
    ("(12 air-drop entries of 709)", "(12 air-drop entries of 700)"),
    ("want 709", "want 700"),
    ("a = (it == 1418)", "a = (it == 1400)"),
    ('"\\t\\tally_range_real = ") == 42', '"\\t\\tally_range_real = ") == 44'),
    ("blk ~= nil and nkeys == 170)", "blk ~= nil and nkeys == 165)"),
    ("and raw_find(s, 'marker = \"the_dance_of_dreaming\"', 1, true) ~= nil",
     "and raw_find(s, 'marker = \"the_dance_of_dreaming\"', 1, true) == nil"),
    ("and raw_find(s, 'marker = \"the_waltz_of_lethargy\"', 1, true) ~= nil",
     "and raw_find(s, 'marker = \"the_waltz_of_lethargy\"', 1, true) == nil"),
    ('": the four melee_unwavering entries are present"',
     '": the four melee_unwavering entries are present (round 131: the two Slaanesh dances are stances, removed - they must be ABSENT)"'),
    ('raw_find(s, "FOURTH.BALLISTICS_MIN_FIRING = 2", 1, true) ~= nil',
     'raw_find(s, "FOURTH.FIRING_AURA_MIN = 1 ", 1, true) ~= nil'),
    ('"ballistics_calibration: 2 allies within 38m are shooting past their cast point (need 2)"',
     '"ballistics_calibration: 2 unit(s) within 38m are shooting past their cast point (2 allies + the caster not shooting; need 1)"'),
    ('local a = (fires_of(Wb2, BK) == 0)', 'local a = (fires_of(Wb2, BK) >= 1)'),
    ('"B2a: no cast ("', '"B2a: ROUND 131 - one shooter within 38 m is enough now, so it casts ("'),
]

src = open(SRC, encoding="utf-8").read()
lines = src.split("\n")
changed = []
hits = {a: 0 for a, _ in PIN_RULES}
for i, ln in enumerate(lines):
    if ln.lstrip().startswith("--"):
        continue
    new = ln
    for a, b in PIN_RULES:
        if a in new:
            hits[a] += 1
            new = new.replace(a, b)
    if new != ln:
        changed.append((i + 1, ln.strip()[:150], new.strip()[:150]))
        lines[i] = new
src = "\n".join(lines)
assert all(v > 0 for v in hits.values()), [a for a, v in hits.items() if v == 0]
print("count-pin lines rebased:", len(changed))
for n, old, new in changed:
    print("  L%-6d OLD %s\n          NEW %s" % (n, old, new))

TIP_OLD = ('    allies_firing_aura = "When armed, fires when at least 2 friendly units near this unit are shooting, '
           'placed on the ground at its feet",\n')
TIP_NEW = ('    allies_firing_aura = "When armed, fires when this unit or a friendly unit near it is shooting",\n'
           '    self_or_ally_shooting = "When armed, fires on this unit when it is shooting, otherwise on the closest friendly unit in range that is shooting",\n'
           '    melee_or_self_or_ally_shooting = "When armed, fires on this unit in melee or when it is shooting, otherwise on the closest friendly unit in range that is shooting",\n'
           '    no_enemy_in_range_within_boost = "When armed, fires when no enemy is in this unit\'s missile range but one is just beyond it",\n')
assert src.count(TIP_OLD) == 1, src.count(TIP_OLD)
src = src.replace(TIP_OLD, TIP_NEW)
print("harness-93 tooltip mirror: allies_firing_aura reworded, three wordings added")

RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h128()\nrun_h129()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, CALL + "run_h130()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
