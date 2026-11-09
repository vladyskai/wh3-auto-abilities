#!/usr/bin/env python3
"""Build harness138.lua from harness137.lua for round 139 (Stand Your Ground on the NEW melee_or_wavering_aura,
QA battle 1). Older harnesses are never edited.

Rebases (each the user's new rule "The general or any friendly unit within 24m is in melee or wavering"):
  the harness-68 token check names the new trigger;
  S5c: the in-melee reason is "melee or wavering aura: the caster is in melee";
  S7a/S7b: in melee with a healthy morale now FIRES (melee alone is enough);
  S8b: an unreadable morale in melee fires on the melee arm (the reason names melee);
  S9a: the caster wavering while running now FIRES (wavering alone is enough);
  the harness-93 tooltip mirror gains the melee_or_wavering_aura wording.
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_rare_filters_harness137\harness137.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_stand_your_ground_harness138\harness138.lua"

BANNER = """-- ============================================================================
-- HARNESS 138 - ROUND 139: STAND YOUR GROUND FIRES FOR THE ALLIES IT PROTECTS.
--   QA battle 1: it fired once, when the General himself wavered; the
--   Spearmen around him had wavered 55 s earlier. NEW melee_or_wavering_aura.
--   Edited vs harness137: this banner, the rebases listed in
--   tools/make_harness138.py, the tooltip mirror, run_h138 and its call.
--   RED control: H138_LIVE / H138_ANN on docs/backups/round139/pre139_*.lua.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 138 (round 139): STAND YOUR GROUND, melee_or_wavering_aura.
--   W1 an ally 20 m away wavering (the General not in melee, not wavering) ->
--   ONE cast on the General. W2 an ally 20 m away in melee -> ONE cast. W3 the
--   wavering ally is 30 m away (bound 24 m) -> no cast. W4 nobody in melee or
--   wavering -> no cast. W5 the only wavering ally is ROUTING -> no cast.
--   RED (pre-139 = round 138): W1 and W2 cast nothing (the old rule read only
--   the General's own morale in melee).
-- ============================================================================
function run_h138()
  local L138 = os.getenv("H138_LIVE") or LIVE
  local A138 = os.getenv("H138_ANN") or ANN
  local RED138 = (os.getenv("H138_LIVE") ~= nil) or (os.getenv("H138_ANN") ~= nil)
  local SYG = "wh_main_character_abilities_stand_your_ground"
  local GEN = "wh_main_emp_cha_general_0"
  local SPEAR = "wh_main_emp_inf_spearmen_0"
  local pre138 = checks
  local function lg(tag, v) return (tag ~= "[live] ") or v end

  print("== HARNESS 138 - section 0zj: the round-139 tokens ==")
  if not RED138 then
    for _, f in ipairs({ { name = "live", path = L138 }, { name = "ann", path = A138 } }) do
      local s = read_file(f.path)
      check("0zj " .. f.name .. ": Stand Your Ground rides melee_or_wavering_aura with its 35 m aura",
        raw_find(s, 'name = "Stand Your Ground", trigger = "melee_or_wavering_aura",', 1, true) ~= nil
        and raw_find(s, "melee_or_wavering_aura = FOURTH.evaluate_melee_or_wavering_aura,", 1, true) ~= nil
        and raw_find(s, 'trigger = "melee_low_morale"', 1, true) == nil)
    end
  end

  local FILES = { { path = A138, tag = "[annotated] " }, { path = L138, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, units, arm, PATH, TAG)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, cards = cards, bar = { { id = "b1", key = SYG } } })
    print("== " .. TAG .. wname .. " ==")
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, arm, true); ui(W); ui(W)
    click(W, "zz_auto_badge_syg"); ui(W)
    sel_event(W, arm, false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  local function two(b, adef)
    local a = { name = SPEAR, uid = b + 1, owns = {}, melee = false, wavering = false }
    for k, v in pairs(adef) do a[k] = v end
    return { { name = GEN, uid = b, owns = { SYG }, melee = false, wavering = false }, a }
  end
  local WORLDS = {
    { "W1. an ally 20 m away is wavering -> ONE cast on the General", function(b) return two(b, { wavering = true, dist = 20 }) end, 1, 0,
      "melee or wavering aura: a friendly unit 20.0m away (bound 24m) is in melee or wavering" },
    { "W2. an ally 20 m away is in melee -> ONE cast", function(b) return two(b, { melee = true, dist = 20 }) end, 1, 0, nil },
    { "W3. the wavering ally is 30 m away -> no cast", function(b) return two(b, { wavering = true, dist = 30 }) end, 0, nil, nil },
    { "W4. nobody in melee or wavering -> no cast", function(b) return two(b, { dist = 10 }) end, 0, nil, nil },
    { "W5. the only wavering ally is ROUTING -> no cast", function(b) return two(b, { wavering = true, routing = true, dist = 10 }) end, 0, nil, nil },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[3]
      if RED138 then want = w[4] end
      if want ~= nil then
        local base = 14100 + i * 10
        local W = world(w[1], w[2](base), base, f.path, TAG)
        if W ~= nil then
          local got = 0
          for _, x in ipairs(W.fires) do if x.key == SYG then got = got + 1 end end
          for _, x in ipairs(W.ground_fires or {}) do if x.key == SYG then got = got + 1 end end
          local a = (got == want)
          if a and want == 1 then a = (W.fires[1] ~= nil and W.fires[1].uid == base) end
          if a and w[5] ~= nil and not RED138 then a = lg(TAG, count_log(W, w[5]) >= 1) end
          check(TAG .. w[1]:sub(1, 2) .. (RED138 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got, a)
          done(a)
          tally(W)
        end
      end
    end
  end
  if RED138 then
    check("RED CONTROL (harness 138): the pre-139 Stand Your Ground ignores its allies - " .. n_ok .. "/" .. n_all,
      n_all == 4 and n_ok == 4)
  else
    check("HARNESS 138: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 10 and n_ok == 10)
  end
  print("== HARNESS 138 done: " .. (checks - pre138) .. " checks in this section ==")
end
'''

R = [
    ('check(nm .. "the fourth ability is in the table (marker = \\"stand_your_ground\\", trigger = \\"melee_low_morale\\")",\n'
     '        raw_find(s, \'marker = "stand_your_ground", name = "Stand Your Ground", trigger = "melee_low_morale"\', 1, true) ~= nil)',
     'check(nm .. "the fourth ability is in the table (marker = \\"stand_your_ground\\", trigger = \\"melee_or_wavering_aura\\" since round 139)",\n'
     '        raw_find(s, \'marker = "stand_your_ground", name = "Stand Your Ground", trigger = "melee_or_wavering_aura"\', 1, true) ~= nil)'),
    ('c = (count_log(W, "reason: in melee, morale below the wavering threshold") >= 1)',
     'c = (count_log(W, "reason: melee or wavering aura: the caster is in melee") >= 1)'),
    ('      a = (#W.fires == 0 and #W.ground_fires == 0)\n      check(TAG .. "S7a: in melee but NOT wavering -> NO fire", a)\n'
     '      b = (count_log(W, "ATTEMPT stand_your_ground") == 0)\n      check(TAG .. "S7b: no attempt is even logged", b)',
     '      a = (#W.fires == 1 and #W.ground_fires == 0)\n      check(TAG .. "S7a: ROUND 139 - in melee, NOT wavering -> FIRES (melee alone is enough now)", a)\n'
     '      b = (TAG ~= "[live] ") or (count_log(W, "ATTEMPT stand_your_ground") == 1)\n      check(TAG .. "S7b: ROUND 139 - exactly one attempt is logged", b)'),
    ('b = (count_log(W, "morale unreadable - plain in-melee fallback") >= 1)\n      check(TAG .. "S8b: the log says the morale was unreadable [live log]", (TAG ~= "[live] ") or b)',
     'b = (count_log(W, "reason: melee or wavering aura: the caster is in melee") >= 1)\n      check(TAG .. "S8b: ROUND 139 - the melee arm fires whatever the morale read says [live log]", (TAG ~= "[live] ") or b)'),
    ('      a = (#W.fires == 0 and #W.ground_fires == 0)\n      check(TAG .. "S9a: running (not in melee) -> NO fire", a)',
     '      a = (#W.fires == 1)\n      check(TAG .. "S9a: ROUND 139 - running but WAVERING -> FIRES (wavering alone is enough now)", a)'),
]
src = open(SRC, encoding="utf-8").read()
for a, b in R:
    assert src.count(a) == 1, (a[:90], src.count(a))
    src = src.replace(a, b)
print("rebases:", len(R))
TIP_OLD = '    enemy_missile_shooting = "When armed, fires on the closest enemy missile unit in range that is shooting",\n'
TIP_NEW = TIP_OLD + '    melee_or_wavering_aura = "When armed, fires when this unit or a friendly unit near it is in melee or wavering",\n'
assert src.count(TIP_OLD) == 1, src.count(TIP_OLD)
src = src.replace(TIP_OLD, TIP_NEW)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h136()\nrun_h137()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, CALL + "run_h138()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
