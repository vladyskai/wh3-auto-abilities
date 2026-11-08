#!/usr/bin/env python3
"""Build harness131.lua from harness130.lua for round 132 (audit batch 1 and the patch-9.0.5 data
fixes). Older harnesses are never edited.

Pin rebases (each a count or name the round deliberately moves; comment lines untouched):
  melee_unwavering 354 -> 349 (Embers of the Phoenix, Horn of Vaul, Harmonic Convergence,
  The Seerstaff of Saphery, Boom! leave it),
  metallurgy_melee 8 -> 0 (the 8 Metallurgy / Master of Alchemy entries move to melee_or_shooting_aura;
  the harness-89 entry check now looks for that trigger name),
  ally_range_real fields 44 -> 46 (Seerstaff, Harmonic Convergence),
  charge-gate keys 164 -> 165 (Aken-seth, patch 9.0.5: 3 uses),
  wind-up keys 165 -> 164 (Okkam's Mindrazor, patch 9.0.5: no wind-up),
  the harness-93 tooltip mirror gains the three new wordings.
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261101_shooting_triggers_harness130\harness130.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261108_audit1_patch905_harness131\harness131.lua"

BANNER = """-- ============================================================================
-- HARNESS 131 - ROUND 132: AUDIT BATCH 1 AND THE PATCH-9.0.5 DATA FIXES.
--   melee_or_shooting_aura (10), melee_or_shooting_self_or_ally (2),
--   self_shooting (1); Eternal Gaze 50 m, Aken-seth charge hold, Okkam's
--   Mindrazor wind-up gone, Overseer skips fliers, reload table regenerated.
--   Edited vs harness130: this banner, the pin rebases listed in
--   tools/make_harness131.py, the tooltip mirror, run_h131 and its call.
--   RED control: H131_LIVE / H131_ANN on docs/backups/round132/pre132_*.lua.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 131 (round 132): AUDIT BATCH 1 AND THE PATCH-9.0.5 DATA FIXES.
--   0zc: tokens.
--   M1 Enchanted Metallurgy: the caster neither fights nor shoots, an ally 20 m
--      away shoots (bound 24 m) -> ONE cast on the caster. M2: the ally is 30 m
--      away -> no cast. M3: the caster in melee -> ONE cast (the melee arm).
--   S1 The Seerstaff of Saphery: an ally in melee 100 m away (bound 140 m) -> ONE
--      cast on that ally. S2: 150 m -> no cast. S3: the caster shooting -> self.
--   B1 Boom!: the unit shooting -> ONE self cast. B2: not shooting -> none.
--   G1 Eternal Gaze: an in-melee enemy 40 m away (new bound 35 m) -> no cast.
--      G2: 30 m -> ONE cast on it.
--   A1 Aken-seth: in melee -> ONE cast and the 120 s charge hold is armed.
--   O1 Overseer of the Unseen: the only eligible ally is FLYING -> no cast.
--      O2: it is not flying -> ONE cast on it.
--   RED (pre-132 build = round 131): M1 and S1 cast nothing, G1 casts at 40 m
--   (the old 70 m bound), A1 arms no hold, O1 casts on the flier.
-- ============================================================================
function run_h131()
  local L131 = os.getenv("H131_LIVE") or LIVE
  local A131 = os.getenv("H131_ANN") or ANN
  local RED131 = (os.getenv("H131_LIVE") ~= nil) or (os.getenv("H131_ANN") ~= nil)
  local MK = "wh3_main_character_abilities_enchanted_metallurgy"
  local SK = "wh2_main_spell_bound_the_seerstaff_of_saphery"
  local BK = "wh_main_unit_abilities_boom"
  local GK = "wh3_dlc29_lord_abilities_gaze_of_usirian"
  local AK = "wh3_dlc29_weapon_abilities_aken_seth_the_staff_of_pain"
  local OK_ = "wh3_dlc29_hero_active_overseer_of_the_unseen"
  local HG = "wh_main_emp_inf_handgunners"
  local LORD = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local PLAIN = "wh2_dlc09_tmb_inf_skeleton_warriors_0"
  local pre131 = checks
  local function lg(tag, v) return (tag ~= "[live] ") or v end

  print("== HARNESS 131 - section 0zc: the round-132 tokens ==")
  if not RED131 then
    for _, f in ipairs({ { name = "live", path = L131 }, { name = "ann", path = A131 } }) do
      local s = read_file(f.path)
      check("0zc " .. f.name .. ": the three new evaluators are wired",
        raw_find(s, "melee_or_shooting_aura = FOURTH.evaluate_melee_or_shooting_aura,", 1, true) ~= nil
        and raw_find(s, "melee_or_shooting_self_or_ally = FOURTH.evaluate_melee_or_shooting_self_or_ally,", 1, true) ~= nil
        and raw_find(s, "self_shooting = FOURTH.evaluate_self_shooting,", 1, true) ~= nil)
      check("0zc " .. f.name .. ": the patch-9.0.5 data is in (Gaze 50 m, Aken-seth 120 s, no Okkam wind-up row, Overseer flier filter)",
        raw_find(s, "range_real = 50,   -- patch 9.0.5: 100 -> 50 m", 1, true) ~= nil
        and raw_find(s, '["' .. AK .. '"] = 120,', 1, true) ~= nil
        and raw_find(s, '["wh3_dlc29_spell_bound_okkams_mindrazor"] = 1,', 1, true) == nil
        and raw_find(s, 'if f == "overseer" then', 1, true) ~= nil)
    end
  end

  local FILES = { { path = A131, tag = "[annotated] " }, { path = L131, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function unit131(W, uid)
    for i = 1, #(W.live_entries or {}) do
      local pr = W.live_entries[i]
      local ok, id = pcall(function() return pr.unit:unique_ui_id() end)
      if ok and tostring(id) == tostring(uid) then return pr.unit end
    end
    return nil
  end
  local function enemy131(W, uid)
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
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
  local function target_of(W, key)
    for _, f in ipairs(W.fires) do if f.key == key then return f.target end end
    return nil
  end
  local function world(wname, units, arm, keys, PATH, TAG, polls, enemies, before)
    local cards, bar = {}, {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    for i, k in ipairs(keys) do bar[#bar + 1] = { id = "b" .. i, key = k } end
    local W = make_world({ can_perform = true, units = units, cards = cards, bar = bar, enemies = enemies })
    print("== " .. TAG .. wname .. " ==")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    if before then before(W) end
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

  for _, f in ipairs(FILES) do
    local TAG = f.tag

    -- M1 (also RED): an ally shooting 20 m away
    local W = world("M1. Enchanted Metallurgy: an ally 20 m away is shooting (bound 24 m) -> ONE cast on the caster",
      { caster(13201, MK), shooter(HG, 13202, 20) }, { { 13201, "enchanted_metallurgy" } }, { MK }, f.path, TAG, 32)
    if W ~= nil then
      if RED131 then
        local rep = (fires_of(W, MK) == 0)
        check(TAG .. "M1-RED: the pre-132 build waits for melee - no cast (" .. fires_of(W, MK) .. ")", rep)
        done(rep)
      else
        local a = (fires_of(W, MK) == 1 and target_of(W, MK) == unit131(W, 13201))
        check(TAG .. "M1a: ONE cast on the caster (" .. fires_of(W, MK) .. ")", a)
        local b = (count_log(W, "enchanted_metallurgy: nobody in melee within reach; 1 unit(s) within 24m are shooting past their cast point (1 allies + the caster not shooting)") == 1)
        check(TAG .. "M1b: the reason names the shooting arm [live log]", lg(TAG, b))
        done(a and lg(TAG, b))
      end
      tally(W)
    end

    if not RED131 then
      local W2 = world("M2. Enchanted Metallurgy: the shooting ally is 30 m away -> no cast",
        { caster(13211, MK), shooter(HG, 13212, 30) }, { { 13211, "enchanted_metallurgy" } }, { MK }, f.path, TAG, 32)
      if W2 ~= nil then
        local a = (fires_of(W2, MK) == 0)
        check(TAG .. "M2a: no cast (" .. fires_of(W2, MK) .. ")", a)
        done(a)
        tally(W2)
      end
      local W3 = world("M3. Enchanted Metallurgy: the caster in melee -> ONE cast (the melee arm stays)",
        { caster(13221, MK, { melee = true }) }, { { 13221, "enchanted_metallurgy" } }, { MK }, f.path, TAG, 4)
      if W3 ~= nil then
        local a = (fires_of(W3, MK) == 1)
        check(TAG .. "M3a: ONE cast in melee (" .. fires_of(W3, MK) .. ")", a)
        done(a)
        tally(W3)
      end
    end

    -- S1 (also RED): an ally in melee 100 m away
    local Ws = world("S1. The Seerstaff of Saphery: an ally in melee 100 m away (bound 140 m) -> ONE cast on that ally",
      { caster(13231, SK), { name = PLAIN, uid = 13232, owns = {}, melee = true, dist = 100 } },
      { { 13231, "the_seerstaff_of_saphery" } }, { SK }, f.path, TAG, 4)
    if Ws ~= nil then
      if RED131 then
        local rep = (fires_of(Ws, SK) == 0)
        check(TAG .. "S1-RED: the pre-132 build casts only on a caster in melee - no cast (" .. fires_of(Ws, SK) .. ")", rep)
        done(rep)
      else
        local a = (fires_of(Ws, SK) == 1 and target_of(Ws, SK) == unit131(Ws, 13232))
        check(TAG .. "S1a: ONE cast on the in-melee ally (" .. fires_of(Ws, SK) .. ")", a)
        done(a)
      end
      tally(Ws)
    end

    if not RED131 then
      local Ws2 = world("S2. The Seerstaff of Saphery: the in-melee ally is 150 m away -> no cast",
        { caster(13241, SK), { name = PLAIN, uid = 13242, owns = {}, melee = true, dist = 150 } },
        { { 13241, "the_seerstaff_of_saphery" } }, { SK }, f.path, TAG, 4)
      if Ws2 ~= nil then
        local a = (fires_of(Ws2, SK) == 0)
        check(TAG .. "S2a: no cast (" .. fires_of(Ws2, SK) .. ")", a)
        done(a)
        tally(Ws2)
      end
      local Ws3 = world("S3. The Seerstaff of Saphery: the caster shooting -> ONE cast on itself",
        { shooter(HG, 13251, 0, { owns = { SK } }) }, { { 13251, "the_seerstaff_of_saphery" } }, { SK }, f.path, TAG, 32)
      if Ws3 ~= nil then
        local a = (fires_of(Ws3, SK) == 1 and target_of(Ws3, SK) == unit131(Ws3, 13251))
        check(TAG .. "S3a: ONE cast on the caster (" .. fires_of(Ws3, SK) .. ")", a)
        done(a)
        tally(Ws3)
      end
      local Wb = world("B1. Boom!: the unit shooting -> ONE self cast",
        { shooter(HG, 13261, 0, { owns = { BK } }) }, { { 13261, "boom" } }, { BK }, f.path, TAG, 32)
      if Wb ~= nil then
        local a = (fires_of(Wb, BK) == 1)
        check(TAG .. "B1a: ONE cast (" .. fires_of(Wb, BK) .. ")", a)
        done(a)
        tally(Wb)
      end
      local Wb2 = world("B2. Boom!: in melee, not shooting -> no cast",
        { { name = HG, uid = 13271, owns = { BK }, melee = true } }, { { 13271, "boom" } }, { BK }, f.path, TAG, 32)
      if Wb2 ~= nil then
        local a = (fires_of(Wb2, BK) == 0)
        check(TAG .. "B2a: no cast (" .. fires_of(Wb2, BK) .. ")", a)
        done(a)
        tally(Wb2)
      end
    end

    -- G1 (also RED): an in-melee enemy 40 m away
    local Wg = world("G1. Eternal Gaze: an in-melee enemy 40 m away (new bound 35 m) -> no cast",
      { caster(13281, GK, { dist_by_target = { [13282] = 40 } }) }, { { 13281, "gaze_of_usirian" } }, { GK }, f.path, TAG, 4,
      { { name = "orc_boyz", uid = 13282, melee = true } })
    if Wg ~= nil then
      if RED131 then
        local rep = (fires_of(Wg, GK) == 1)
        check(TAG .. "G1-RED: the pre-132 build still offers the 40 m enemy (old bound 70 m) - the move-order risk (" .. fires_of(Wg, GK) .. ")", rep)
        done(rep)
      else
        local a = (fires_of(Wg, GK) == 0)
        check(TAG .. "G1a: no cast at 40 m (" .. fires_of(Wg, GK) .. ")", a)
        done(a)
      end
      tally(Wg)
    end
    if not RED131 then
      local Wg2 = world("G2. Eternal Gaze: an in-melee enemy 30 m away -> ONE cast on it",
        { caster(13291, GK, { dist_by_target = { [13292] = 30 } }) }, { { 13291, "gaze_of_usirian" } }, { GK }, f.path, TAG, 4,
        { { name = "orc_boyz", uid = 13292, melee = true } })
      if Wg2 ~= nil then
        local a = (fires_of(Wg2, GK) == 1 and target_of(Wg2, GK) == enemy131(Wg2, 13292))
        check(TAG .. "G2a: ONE cast on the enemy (" .. fires_of(Wg2, GK) .. ")", a)
        done(a)
        tally(Wg2)
      end
    end

    -- A1 (also RED): Aken-seth's new charge hold
    local Wa = world("A1. Aken-seth: in melee -> ONE cast and the 120 s charge hold",
      { caster(13301, AK, { melee = true }) }, { { 13301, "aken_seth_the_staff_of_pain" } }, { AK }, f.path, TAG, 4)
    if Wa ~= nil then
      local hold = count_log(Wa, "charge gate aken_seth_the_staff_of_pain: one use spent - the next attempt waits 120s")
      if RED131 then
        local rep = (TAG ~= "[live] ") or hold == 0
        check(TAG .. "A1-RED: the pre-132 build arms no charge hold (" .. hold .. ") [live log]", rep)
        done(rep)
      else
        local a = (fires_of(Wa, AK) == 1)
        check(TAG .. "A1a: ONE cast (" .. fires_of(Wa, AK) .. ")", a)
        local b = (hold == 1)
        check(TAG .. "A1b: the 120 s hold is armed [live log]", lg(TAG, b))
        done(a and lg(TAG, b))
      end
      tally(Wa)
    end

    -- O1 (also RED) / O2: Overseer of the Unseen and a flying ally
    local function fly(uid, v)
      return function(W)
        local u = unit131(W, uid)
        if u ~= nil then u.is_currently_flying = function() return v end end
      end
    end
    local Wo = world("O1. Overseer of the Unseen: the only eligible ally is flying -> no cast",
      { caster(13311, OK_), { name = PLAIN, uid = 13312, owns = {}, melee = false, dist = 30 } },
      { { 13311, "overseer_of_the_unseen" } }, { OK_ }, f.path, TAG, 4, nil, fly(13312, true))
    if Wo ~= nil then
      if RED131 then
        local rep = (fires_of(Wo, OK_) == 1)
        check(TAG .. "O1-RED: the pre-132 build casts on the flying ally (" .. fires_of(Wo, OK_) .. ")", rep)
        done(rep)
      else
        local a = (fires_of(Wo, OK_) == 0)
        check(TAG .. "O1a: no cast (" .. fires_of(Wo, OK_) .. ")", a)
        done(a)
      end
      tally(Wo)
    end
    if not RED131 then
      local Wo2 = world("O2. Overseer of the Unseen: the eligible ally is not flying -> ONE cast on it",
        { caster(13321, OK_), { name = PLAIN, uid = 13322, owns = {}, melee = false, dist = 30 } },
        { { 13321, "overseer_of_the_unseen" } }, { OK_ }, f.path, TAG, 4, nil, fly(13322, false))
      if Wo2 ~= nil then
        local a = (fires_of(Wo2, OK_) == 1 and target_of(Wo2, OK_) == unit131(Wo2, 13322))
        check(TAG .. "O2a: ONE cast on the ally (" .. fires_of(Wo2, OK_) .. ")", a)
        done(a)
        tally(Wo2)
      end
    end
  end

  if RED131 then
    check("RED CONTROL (harness 131): the pre-132 build shows every fixed fault - " .. n_ok .. "/" .. n_all,
      n_all == 10 and n_ok == 10)
  else
    check("HARNESS 131: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 26 and n_ok == 26)
  end
  print("== HARNESS 131 done: " .. (checks - pre131) .. " checks in this section ==")
end
'''

PIN_RULES = [
    ("'trigger = \"melee_unwavering\"') == 354", "'trigger = \"melee_unwavering\"') == 349"),
    ("mu == 354", "mu == 349"),
    ("entries = 700, keys = 752, mu = 354", "entries = 700, keys = 752, mu = 349"),
    ("cp(s, 'trigger = \"metallurgy_melee\"') == 8", "cp(s, 'trigger = \"metallurgy_melee\"') == 0"),
    ("and raw_find(s, 'trigger = \"metallurgy_melee\"', 1, true) ~= nil then",
     "and raw_find(s, 'trigger = \"melee_or_shooting_aura\"', 1, true) ~= nil then"),
    ('"\\t\\tally_range_real = ") == 44', '"\\t\\tally_range_real = ") == 46'),
    ("(RED_MODE and 0 or 164)", "(RED_MODE and 0 or 165)"),
    ("blk ~= nil and nkeys == 165)", "blk ~= nil and nkeys == 164)"),
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
missing = [a for a, v in hits.items() if v == 0]
print("count-pin lines rebased:", len(changed), "| rules with no hit:", missing)
for n, old, new in changed:
    print("  L%-6d OLD %s\n          NEW %s" % (n, old, new))

TIP_OLD = ('    no_enemy_in_range_within_boost = "When armed, fires when no enemy is in this unit\'s missile range but '
           'one is just beyond it",\n')
TIP_NEW = TIP_OLD + (
    '    melee_or_shooting_aura = "When armed, fires when this unit or a friendly unit near it is in melee or shooting",\n'
    '    melee_or_shooting_self_or_ally = "When armed, fires on this unit when it is in melee or shooting, otherwise on the closest friendly unit in range that is",\n'
    '    self_shooting = "When armed, fires when this unit is shooting",\n')
assert src.count(TIP_OLD) == 1, src.count(TIP_OLD)
src = src.replace(TIP_OLD, TIP_NEW)

RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h129()\nrun_h130()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, CALL + "run_h131()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
