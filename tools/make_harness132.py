#!/usr/bin/env python3
"""Build harness132.lua from harness131.lua for round 133 (audit batch 2: protection against shots
fires when under fire). Older harnesses are never edited.

Pin rebases (comment lines untouched):
  melee_unwavering 349 -> 342 (the 7 R5 abilities move to under_fire / melee_or_under_fire),
  the harness-93 tooltip mirror gains the two new wordings.
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261108_audit1_patch905_harness131\harness131.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261108_under_fire_harness132\harness132.lua"

BANNER = """-- ============================================================================
-- HARNESS 132 - ROUND 133: AUDIT BATCH 2, PROTECTION AGAINST SHOTS.
--   under_fire (3) and melee_or_under_fire (4).
--   Edited vs harness131: this banner, the pin rebases listed in
--   tools/make_harness132.py, the tooltip mirror, run_h132 and its call.
--   RED control: H132_LIVE / H132_ANN on docs/backups/round133/pre133_*.lua.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 132 (round 133): AUDIT BATCH 2, PROTECTION AGAINST SHOTS.
--   U1 Shield of Chaqua: an ally 30 m away under fire (bound 38 m) -> ONE cast on
--      the caster. U2: 45 m away -> no cast.
--   U3 The Golden Eye of Tzeentch: the caster under fire -> ONE cast.
--   U4 The Golden Eye: in melee, not under fire -> no cast (no melee arm).
--   U5 The Lion's Shield: the under-fire read is unreadable -> no cast.
--   X1 Charmed Shield: the caster under fire -> ONE cast. X2: in melee -> ONE cast.
--   X3 The Blessed Helm: an ally 20 m away in melee (bound 24 m) -> ONE cast.
--      X4: 30 m away -> no cast.
--   RED (pre-133 build = round 132): U1, U3, X1 cast nothing; X2 still casts.
-- ============================================================================
function run_h132()
  local L132 = os.getenv("H132_LIVE") or LIVE
  local A132 = os.getenv("H132_ANN") or ANN
  local RED132 = (os.getenv("H132_LIVE") ~= nil) or (os.getenv("H132_ANN") ~= nil)
  local CHA = "wh2_dlc12_unit_abilities_shield_of_chaqua"
  local EYE = "wh3_dlc24_item_abilities_the_golden_eye_of_tzeentch"
  local LION = "wh_dlc07_lord_abilities_lions_shield"
  local CHS = "wh_main_weapon_abilities_charmed_shield"
  local HELM = "wh3_dlc24_item_abilities_blessed_helm_of_the_oblast"
  local LORD = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local PLAIN = "wh2_dlc09_tmb_inf_skeleton_warriors_0"
  local pre132 = checks
  local function lg(tag, v) return (tag ~= "[live] ") or v end

  print("== HARNESS 132 - section 0zd: the round-133 tokens ==")
  if not RED132 then
    for _, f in ipairs({ { name = "live", path = L132 }, { name = "ann", path = A132 } }) do
      local s = read_file(f.path)
      check("0zd " .. f.name .. ": the two new evaluators are wired and only an exact true counts as under fire",
        raw_find(s, "under_fire = FOURTH.evaluate_under_fire,", 1, true) ~= nil
        and raw_find(s, "melee_or_under_fire = FOURTH.evaluate_melee_or_under_fire,", 1, true) ~= nil
        and raw_find(s, "local ok, v = pcall(function() return unit:is_under_missile_attack() end)\n\treturn ok and v == true", 1, true) ~= nil)
    end
  end

  local FILES = { { path = A132, tag = "[annotated] " }, { path = L132, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function fires_of(W, key)
    local n = 0
    for _, f in ipairs(W.fires) do if f.key == key then n = n + 1 end end
    return n
  end
  local function world(wname, units, arm, key, PATH, TAG)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, cards = cards, bar = { { id = "b1", key = key } } })
    print("== " .. TAG .. wname .. " ==")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, arm[1], true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. arm[2]); ui(W)
    sel_event(W, arm[1], false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  local function caster(uid, key, extra)
    local d = { name = LORD, uid = uid, owns = { key }, melee = false }
    for k, v in pairs(extra or {}) do d[k] = v end
    return d
  end
  local function ally(uid, dist, extra)
    local d = { name = PLAIN, uid = uid, owns = {}, melee = false, dist = dist }
    for k, v in pairs(extra or {}) do d[k] = v end
    return d
  end
  -- name, units, arm, key, expected casts (GREEN), expected casts (RED or nil = not a RED world)
  local WORLDS = {
    { "U1. Shield of Chaqua: an ally 30 m away under fire (bound 38 m) -> ONE cast", function(b) return
        { caster(b, CHA), ally(b + 1, 30, { missile = true }) } end, "shield_of_chaqua", CHA, 1, 0 },
    { "U2. Shield of Chaqua: the ally under fire is 45 m away -> no cast", function(b) return
        { caster(b, CHA), ally(b + 1, 45, { missile = true }) } end, "shield_of_chaqua", CHA, 0, nil },
    { "U3. The Golden Eye of Tzeentch: the caster under fire -> ONE cast", function(b) return
        { caster(b, EYE, { missile = true }) } end, "the_golden_eye_of_tzeentch", EYE, 1, 0 },
    { "U4. The Golden Eye of Tzeentch: in melee, not under fire -> no cast (no melee arm)", function(b) return
        { caster(b, EYE, { melee = true, missile = false }) } end, "the_golden_eye_of_tzeentch", EYE, 0, nil },
    { "U5. The Lion's Shield: the under-fire read is unreadable -> no cast", function(b) return
        { caster(b, LION, { missile_raises = true }) } end, "lions_shield", LION, 0, nil },
    { "X1. Charmed Shield: the caster under fire -> ONE cast", function(b) return
        { caster(b, CHS, { missile = true }) } end, "charmed_shield", CHS, 1, 0 },
    { "X2. Charmed Shield: in melee -> ONE cast (the melee arm stays)", function(b) return
        { caster(b, CHS, { melee = true }) } end, "charmed_shield", CHS, 1, 1 },
    { "X3. The Blessed Helm of the Oblast: an ally 20 m away in melee (bound 24 m) -> ONE cast", function(b) return
        { caster(b, HELM), ally(b + 1, 20, { melee = true }) } end, "blessed_helm_of_the_oblast", HELM, 1, nil },
    { "X4. The Blessed Helm of the Oblast: the ally in melee is 30 m away -> no cast", function(b) return
        { caster(b, HELM), ally(b + 1, 30, { melee = true }) } end, "blessed_helm_of_the_oblast", HELM, 0, nil },
  }

  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[5]
      if RED132 then want = w[6] end
      if want ~= nil then
        local base = 13400 + i * 10
        local W = world(w[1], w[2](base), { base, w[3] }, w[4], f.path, TAG)
        if W ~= nil then
          local got = fires_of(W, w[4])
          local a = (got == want)
          if a and want == 1 then
            a = (W.fires[1].target == nil) or (W.fires[1].uid == base)
          end
          check(TAG .. w[1]:sub(1, 2) .. (RED132 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got, a)
          done(a)
          tally(W)
        end
      end
    end
  end

  if RED132 then
    check("RED CONTROL (harness 132): the pre-133 build casts the shot protection only in melee - " .. n_ok .. "/" .. n_all,
      n_all == 8 and n_ok == 8)
  else
    check("HARNESS 132: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 18 and n_ok == 18)
  end
  print("== HARNESS 132 done: " .. (checks - pre132) .. " checks in this section ==")
end
'''

PIN_RULES = [
    ("'trigger = \"melee_unwavering\"') == 349", "'trigger = \"melee_unwavering\"') == 342"),
    ("mu == 349", "mu == 342"),
    ("entries = 700, keys = 752, mu = 349", "entries = 700, keys = 752, mu = 342"),
]
src = open(SRC, encoding="utf-8").read()
lines = src.split("\n")
changed, hits = [], {a: 0 for a, _ in PIN_RULES}
for i, ln in enumerate(lines):
    if ln.lstrip().startswith("--"):
        continue
    new = ln
    for a, b in PIN_RULES:
        if a in new:
            hits[a] += 1
            new = new.replace(a, b)
    if new != ln:
        changed.append(i + 1)
        lines[i] = new
src = "\n".join(lines)
print("count-pin lines rebased:", len(changed), "| rules with no hit:", [a for a, v in hits.items() if v == 0])

TIP_OLD = '    self_shooting = "When armed, fires when this unit is shooting",\n'
TIP_NEW = TIP_OLD + (
    '    under_fire = "When armed, fires when this unit (or, for an aura, a friendly unit near it) is under missile fire",\n'
    '    melee_or_under_fire = "When armed, fires when this unit (or, for an aura, a friendly unit near it) is in melee or under missile fire",\n')
assert src.count(TIP_OLD) == 1, src.count(TIP_OLD)
src = src.replace(TIP_OLD, TIP_NEW)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h130()\nrun_h131()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, CALL + "run_h132()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
