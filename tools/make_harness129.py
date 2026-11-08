#!/usr/bin/env python3
"""Build harness129.lua from harness128.lua for round 130 (the first triggers on the
firing flag: Restock!, Ballistics Calibration, Skjalandir's Fall's shooting arm).
Older harnesses are never edited.

Pin rebases (every one a count the round deliberately moves; comment lines untouched):
  entries 707 -> 709 (Restock!, Ballistics Calibration), keys 759 -> 761,
  melee_unwavering 374 -> 373 (Skjalandir's Fall moves to melee_or_shooting_into_melee),
  ally_range_real fields 41 -> 42 (Restock!), charge-gate keys 163 -> 164 (Restock!),
  full-table iterations 1414 -> 1418 (2 x 709),
  the harness-93 tooltip mirror gains the three new wordings,
  the harness-125 CAST POINT text: "(nothing is cast in this round)" ->
  "(the firing-flag triggers may cast from here)".
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261103_card_veto_harness128\harness128.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261101_firing_flag_triggers_harness129\harness129.lua"

BANNER = """-- ============================================================================
-- HARNESS 129 - ROUND 130: THE FIRST TRIGGERS ON THE FIRING FLAG.
--   Restock! (ally_ammo_low), Ballistics Calibration (allies_firing_aura) and
--   Skjalandir's Fall's shooting arm (melee_or_shooting_into_melee).
--   Edited vs harness128: this banner, the count-pin rebases listed in
--   tools/make_harness129.py, the tooltip mirror, the CAST POINT text pin,
--   run_h129 and its call.
--   RED control: H129_LIVE / H129_ANN on docs/backups/round130/pre130_*.lua.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 129 (round 130): THE FIRST TRIGGERS ON THE FIRING FLAG.
--   0y: tokens (constants, entries, evaluators, the ground key, the charge key).
--   R1 Restock!: two shooting allies, one at 60% ammo (50 m), one at 80% (30 m)
--      -> ONE cast, on the 60% ally (the lowest at or below 70%, not the closest).
--   R2 Restock!: an ally at 60% that is NOT shooting, and a shooting ally at 60%
--      beyond the 70 m bound -> no cast.
--   R3 Restock!: TWO casters, ONE low shooting ally -> exactly ONE cast (the
--      refilled ally is claimed for 12 s).
--   B1 Ballistics Calibration: two allies within 38 m shooting past their cast
--      point -> ONE ground cast at the caster's own position, not before the
--      cast point.
--   B2 Ballistics Calibration: one ally shooting within 38 m, one at 45 m -> no cast.
--   S1 Skjalandir's Fall: shooting past its cast point at a target IN MELEE -> ONE
--      self cast.
--   S2 Skjalandir's Fall: shooting at a target NOT in melee -> no cast.
--   S3 Skjalandir's Fall: in melee, not shooting -> ONE cast (the melee arm stays).
--   RED (pre-130 build = round 129): R1, B1 and S1 cast nothing; S3 still casts.
-- ============================================================================
function run_h129()
  local L129 = os.getenv("H129_LIVE") or LIVE
  local A129 = os.getenv("H129_ANN") or ANN
  local RED129 = (os.getenv("H129_LIVE") ~= nil) or (os.getenv("H129_ANN") ~= nil)
  local RK = "wh2_dlc17_hero_abilities_more_powder_generic"
  local BK = "wh_main_hero_abilities_ballistics_calibration"
  local SK = "wh3_dlc23_character_abilities_skjalandirs_fall"
  local HG = "wh_main_emp_inf_handgunners"   -- reload 13 s in FOURTH.RELOAD_S: cast point 6.5 s after the first shot
  local UL = "wh3_dlc23_neu_cha_ulrika"      -- reload 7 s: cast point 3.5 s
  local pre129 = checks
  local function lg(tag, v) return (tag ~= "[live] ") or v end

  print("== HARNESS 129 - section 0y: the firing-flag trigger tokens ==")
  if not RED129 then
    for _, f in ipairs({ { name = "live", path = L129 }, { name = "ann", path = A129 } }) do
      local s = read_file(f.path)
      check("0y " .. f.name .. ": the three constants exist",
        raw_find(s, "FOURTH.RESTOCK_AT_FRACTION = 0.70", 1, true) ~= nil
        and raw_find(s, "FOURTH.RESTOCK_CLAIM_S = 12", 1, true) ~= nil
        and raw_find(s, "FOURTH.BALLISTICS_MIN_FIRING = 2", 1, true) ~= nil)
      check("0y " .. f.name .. ": the two entries and Skjalandir's new trigger",
        raw_find(s, '{ marker = "restock", name = "Restock!", trigger = "ally_ammo_low",', 1, true) ~= nil
        and raw_find(s, '{ marker = "ballistics_calibration", name = "Ballistics Calibration", trigger = "allies_firing_aura",', 1, true) ~= nil
        and raw_find(s, 'trigger = "melee_or_shooting_into_melee",', 1, true) ~= nil)
      check("0y " .. f.name .. ": Restock! is charge-gated (60 s) and Ballistics Calibration is a ground key",
        raw_find(s, '["' .. RK .. '"] = 60,', 1, true) ~= nil
        and raw_find(s, '["' .. BK .. '"] = true,', 1, true) ~= nil)
      check("0y " .. f.name .. ": the three evaluators are wired",
        raw_find(s, "ally_ammo_low = FOURTH.evaluate_ally_ammo_low,", 1, true) ~= nil
        and raw_find(s, "allies_firing_aura = FOURTH.evaluate_allies_firing_aura,", 1, true) ~= nil
        and raw_find(s, "melee_or_shooting_into_melee = FOURTH.evaluate_melee_or_shooting_into_melee,", 1, true) ~= nil)
      check("0y " .. f.name .. ": the probe publishes its state by ui id",
        raw_find(s, "FOURTH.ammo_by_id[tostring(u:unique_ui_id())] = st", 1, true) ~= nil)
    end
  end

  local FILES = { { path = A129, tag = "[annotated] " }, { path = L129, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function unit129(W, uid)
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
  -- arm = { {uid, marker}, ... }: each caster is selected and its badge clicked
  local function world(wname, units, arm, keys, PATH, TAG, polls)
    local cards, bar = {}, {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    for i, k in ipairs(keys) do bar[#bar + 1] = { id = "b" .. i, key = k } end
    local W = make_world({ can_perform = true, units = units, cards = cards, bar = bar })
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
  local function shooter(name, uid, start, low, dist, extra)
    local d = { name = name, uid = uid, owns = {}, melee = false, ammo_start = start,
                ammo_seq = { start, low }, dist = dist }
    for k, v in pairs(extra or {}) do d[k] = v end
    return d
  end

  for _, f in ipairs(FILES) do
    local TAG = f.tag

    -- R1: the lowest shooting ally at or below 70% is the target, not the closest
    local W = world("R1. Restock!: allies at 60% (50 m) and 80% (30 m), both shooting -> ONE cast on the 60% ally",
      { { name = "wh2_dlc13_emp_cha_hunter_jorek_grimm_0", uid = 13001, owns = { RK }, melee = false },
        shooter(HG, 13002, 100, 60, 50), shooter(HG, 13003, 100, 80, 30) },
      { { 13001, "restock" } }, { RK }, f.path, TAG, 8)
    if W ~= nil then
      if RED129 then
        local rep = (fires_of(W, RK) == 0)
        check(TAG .. "R1-RED: the pre-130 build never casts Restock! (" .. fires_of(W, RK) .. ")", rep)
        done(rep)
      else
        local a = (fires_of(W, RK) == 1 and fire_target_for(W, 13001) == unit129(W, 13002))
        check(TAG .. "R1a: ONE cast and its target is the 60% ally (" .. fires_of(W, RK) .. ")", a)
        local b = (count_log(W, "restock: shooting ally with the least ammunition left, 60% (<= 70%), cast on ally") == 1)
        check(TAG .. "R1b: the reason names the 60% and the 70% line [live log]", lg(TAG, b))
        done(a and lg(TAG, b))
      end
      tally(W)
    end

    if not RED129 then
      -- R2: not shooting, or out of the bound -> silent
      local quiet = { name = HG, uid = 13012, owns = {}, melee = false, ammo_start = 100, ammo_seq = { 60 }, dist = 30 }
      local W2 = world("R2. Restock!: a 60% ally that is NOT shooting, a shooting 60% ally at 80 m -> no cast",
        { { name = "wh3_dlc25_emp_cha_engineer", uid = 13011, owns = { RK }, melee = false },
          quiet, shooter(HG, 13013, 100, 60, 80) },
        { { 13011, "restock" } }, { RK }, f.path, TAG, 12)
      if W2 ~= nil then
        local a = (fires_of(W2, RK) == 0)
        check(TAG .. "R2a: no cast (" .. fires_of(W2, RK) .. ")", a)
        done(a)
        tally(W2)
      end

      -- R3: two casters, one low ally -> one cast
      local W3 = world("R3. Restock!: TWO casters, ONE shooting ally at 50% -> exactly ONE cast in 10 s",
        { { name = "wh3_dlc25_emp_cha_engineer", uid = 13021, owns = { RK }, melee = false },
          { name = "wh3_dlc25_emp_cha_master_engineer", uid = 13022, owns = { RK }, melee = false },
          shooter(HG, 13023, 100, 50, 20) },
        { { 13021, "restock" }, { 13022, "restock" } }, { RK }, f.path, TAG, 40)
      if W3 ~= nil then
        local a = (fires_of(W3, RK) == 1)
        check(TAG .. "R3a: exactly ONE cast across both casters (" .. fires_of(W3, RK) .. ")", a)
        done(a)
        tally(W3)
      end
    end

    -- B1: two allies within 38 m past their cast point -> ground cast at the caster's feet
    local Wb = world("B1. Ballistics Calibration: two allies within 38 m shooting past their cast point -> ONE ground cast",
      { { name = "wh2_dlc13_emp_cha_hunter_jorek_grimm_0", uid = 13031, owns = { BK }, melee = false },
        shooter(HG, 13032, 100, 99, 30), shooter(HG, 13033, 100, 99, 20) },
      { { 13031, "ballistics_calibration" } }, { BK }, f.path, TAG, 32)
    if Wb ~= nil then
      if RED129 then
        local rep = (fires_of(Wb, BK) == 0)
        check(TAG .. "B1-RED: the pre-130 build never casts Ballistics Calibration (" .. fires_of(Wb, BK) .. ")", rep)
        done(rep)
      else
        local g = Wb.ground_fires[1]
        -- the first shot is read on poll 2 (t=0.50s); the cast point is 6.5 s
        -- (26 polls) later, so the cast lands on poll 28 exactly. The world stops
        -- at poll 32, inside the 2 s guard (the mock engine never refuses a repeat).
        local a = (#Wb.ground_fires == 1 and #Wb.fires == 0 and g.key == BK
          and g.pos ~= nil and g.pos.marker == "pos:13031" and g.tick == 2 + 26)
        check(TAG .. "B1a: ONE ground cast at the caster's own position, on the cast point poll 28 (tick "
          .. tostring(g and g.tick) .. ")", a)
        local b = (count_log(Wb, "ballistics_calibration: 2 allies within 38m are shooting past their cast point (need 2)") >= 1)
        check(TAG .. "B1b: the reason names 2 allies and the 38 m bound [live log]", lg(TAG, b))
        done(a and lg(TAG, b))
      end
      tally(Wb)
    end

    if not RED129 then
      local Wb2 = world("B2. Ballistics Calibration: one shooting ally at 30 m, one at 45 m -> no cast",
        { { name = "wh2_dlc13_emp_cha_hunter_jorek_grimm_0", uid = 13041, owns = { BK }, melee = false },
          shooter(HG, 13042, 100, 99, 30), shooter(HG, 13043, 100, 99, 45) },
        { { 13041, "ballistics_calibration" } }, { BK }, f.path, TAG, 40)
      if Wb2 ~= nil then
        local a = (fires_of(Wb2, BK) == 0)
        check(TAG .. "B2a: no cast (" .. fires_of(Wb2, BK) .. ")", a)
        done(a)
        tally(Wb2)
      end
    end

    -- S1: Ulrika shooting past her cast point at a target in melee -> one self cast
    local Ws = world("S1. Skjalandir's Fall: shooting past the cast point at a target IN MELEE -> ONE self cast",
      { { name = UL, uid = 13051, owns = { SK }, melee = false, ammo_start = 30, ammo_seq = { 30, 29 },
          ammo_target = { type = "wh_main_vmp_inf_zombie", melee = true } } },
      { { 13051, "skjalandirs_fall" } }, { SK }, f.path, TAG, 20)
    if Ws ~= nil then
      if RED129 then
        local rep = (fires_of(Ws, SK) == 0)
        check(TAG .. "S1-RED: the pre-130 build waits for melee - no cast (" .. fires_of(Ws, SK) .. ")", rep)
        done(rep)
      else
        local a = (fires_of(Ws, SK) == 1 and fire_target_for(Ws, 13051) == unit129(Ws, 13051)
          and Ws.fires[1].tick == 2 + 14)
        check(TAG .. "S1a: ONE self cast, on the 3.5 s cast point poll 16 (tick " .. tostring(Ws.fires[1] and Ws.fires[1].tick) .. ")", a)
        local b = (count_log(Ws, "shooting past its cast point at a target that is in melee, cast on self") == 1)
        check(TAG .. "S1b: the reason names the shooting arm [live log]", lg(TAG, b))
        done(a and lg(TAG, b))
      end
      tally(Ws)
    end

    if not RED129 then
      local Ws2 = world("S2. Skjalandir's Fall: shooting at a target NOT in melee -> no cast",
        { { name = UL, uid = 13061, owns = { SK }, melee = false, ammo_start = 30, ammo_seq = { 30, 29 },
            ammo_target = { type = "wh_main_vmp_inf_zombie", melee = false } } },
        { { 13061, "skjalandirs_fall" } }, { SK }, f.path, TAG, 24)
      if Ws2 ~= nil then
        local a = (fires_of(Ws2, SK) == 0)
        check(TAG .. "S2a: no cast (" .. fires_of(Ws2, SK) .. ")", a)
        done(a)
        tally(Ws2)
      end
    end

    -- S3: the melee arm stays (also the RED control's positive)
    local Ws3 = world("S3. Skjalandir's Fall: in melee, not shooting -> ONE cast (the melee arm stays)",
      { { name = UL, uid = 13071, owns = { SK }, melee = true } },
      { { 13071, "skjalandirs_fall" } }, { SK }, f.path, TAG, 4)
    if Ws3 ~= nil then
      local a = (fires_of(Ws3, SK) == 1)
      check(TAG .. "S3a: ONE cast in melee (" .. fires_of(Ws3, SK) .. ")", a)
      done(a)
      tally(Ws3)
    end
  end

  if RED129 then
    check("RED CONTROL (harness 129): the pre-130 build casts none of the firing-flag abilities, melee still works - "
      .. n_ok .. "/" .. n_all, n_all == 8 and n_ok == 8)
  else
    check("HARNESS 129: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 16 and n_ok == 16)
  end
  print("== HARNESS 129 done: " .. (checks - pre129) .. " checks in this section ==")
end
'''

PIN_RULES = [
    ("== 707", "== 709"),
    ("== 759", "== 761"),
    ("'trigger = \"melee_unwavering\"') == 374", "'trigger = \"melee_unwavering\"') == 373"),
    ("mu == 374", "mu == 373"),
    ("entries = 707, keys = 759, mu = 374", "entries = 709, keys = 761, mu = 373"),
    ("entries = 707, keys = 759, sum = true", "entries = 709, keys = 761, sum = true"),
    ("FULL 707-entry table", "FULL 709-entry table"),
    ("707 abilities per pass", "709 abilities per pass"),
    ("has 707 entries", "has 709 entries"),
    ("has all 759 keys", "has all 761 keys"),
    ("table of 707 after round 123", "table of 709 after round 130"),
    ("(12 air-drop entries of 707)", "(12 air-drop entries of 709)"),
    ("want 707", "want 709"),
    ("a = (it == 1414)", "a = (it == 1418)"),
    ("(RED_MODE and 0 or 163)", "(RED_MODE and 0 or 164)"),
    ('"\\t\\tally_range_real = ") == 41', '"\\t\\tally_range_real = ") == 42'),
    ("+ 0.5 x reload 13s (nothing is cast in this round)", "+ 0.5 x reload 13s (the firing-flag triggers may cast from here)"),
]

src = open(SRC, encoding="utf-8").read()
lines = src.split("\n")
changed = []
for i, ln in enumerate(lines):
    if ln.lstrip().startswith("--"):
        continue
    new = ln
    for a, b in PIN_RULES:
        if a in new:
            new = new.replace(a, b)
    if new != ln:
        changed.append((i + 1, ln.strip()[:150], new.strip()[:150]))
        lines[i] = new
src = "\n".join(lines)
print("count-pin lines rebased:", len(changed))
for n, old, new in changed:
    print("  L%-6d OLD %s\n          NEW %s" % (n, old, new))

TIP_OLD = '    ally_missile = "When armed, fires on a missile-capable ally in range",\n'
TIP_NEW = TIP_OLD + (
    '    ally_ammo_low = "When armed, fires on a shooting ally in range with 70% or less of its ammunition left (the lowest first)",\n'
    '    allies_firing_aura = "When armed, fires when at least 2 friendly units near this unit are shooting, placed on the ground at its feet",\n'
    '    melee_or_shooting_into_melee = "When armed, fires when this unit is in melee, or is shooting at an enemy that is in melee",\n')
assert src.count(TIP_OLD) == 1, src.count(TIP_OLD)
src = src.replace(TIP_OLD, TIP_NEW)
print("harness-93 tooltip mirror: three wordings added")

RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h127()\nrun_h128()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, CALL + "run_h129()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
