#!/usr/bin/env python3
"""Build harness134.lua from harness133.lua for round 135 (audit batch 4: the enemy slows, the fast-enemy
trigger and the target filters). Older harnesses are never edited.

Pin rebases (code lines only; comment lines untouched):
  enemy_engaged_or_shot 85 -> 70 (11 to enemy_melee, 4 to enemy_fast_near_ally), enemy_melee 3 -> 14;
  the harness-93 tooltip mirror gains the enemy_fast_near_ally wording;
  four worlds whose stand-in enemy is not a Lord now aim a Lord/Hero-only ability at a real commander
  key (wh2_dlc09_tmb_cha_arkhan_0), because the round-135 target filter correctly refuses a non-Lord:
    harness 97 FAM INSIDE r150 (Headhunt) and FRESH (Headhunt);
    harness 122 E2 (the Transfix hex, every case; its reason check names the enemy it was given);
    harness 122 H (Hunter of Champions, upgraded key).
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_speed_triggers_harness133\harness133.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_enemy_slows_harness134\harness134.lua"
LORD = "wh2_dlc09_tmb_cha_arkhan_0"

BANNER = """-- ============================================================================
-- HARNESS 134 - ROUND 135: AUDIT BATCH 4, THE ENEMY SLOWS AND TARGET FILTERS.
--   enemy_melee gains 11; enemy_fast_near_ally (NEW) takes 4; 15 entries get a
--   target_class (Lord/Hero, large, large single entity).
--   Edited vs harness133: this banner, the pin and world rebases listed in
--   tools/make_harness134.py, the tooltip mirror, run_h134 and its call.
--   RED control: H134_LIVE / H134_ANN on docs/backups/round135/pre135_*.lua.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 134 (round 135): AUDIT BATCH 4, THE ENEMY SLOWS AND TARGET FILTERS.
--   0zf: tokens. F1-F7 Mither / Whispering Mist on enemy_fast_near_ally (moving,
--   run speed >= 5 m/s, within 40 m of one of our units, inside the 70% bound).
--   L1-L6 the target filters (Looming Dread Lord/Hero only, Tendrils of the Sea
--   large only, Fecund Rebirth large single entity). M1-M2 Acquiescence on
--   enemy_melee. RED (pre-135 = round 134): F1, F4 cast nothing; L1, L5, M1 cast.
-- ============================================================================
function run_h134()
  local L134 = os.getenv("H134_LIVE") or LIVE
  local A134 = os.getenv("H134_ANN") or ANN
  local RED134 = (os.getenv("H134_LIVE") ~= nil) or (os.getenv("H134_ANN") ~= nil)
  local MITH = "wh2_dlc15_hero_abilities_mither"                  -- 75 m -> bound 52
  local WMIST = "wh3_dlc29_hero_abilities_whispering_mist"        -- 200 m -> bound 140
  local LOOM = "wh2_dlc14_lord_abilities_looming_dread"           -- 150 m -> bound 105, Lord/Hero only
  local TEND = "wh3_dlc29_hero_active_tendrils_of_the_sea"        -- 200 m -> bound 140, large only
  local FEC = "wh3_dlc29_character_active_mark_of_the_monster"    -- 200 m -> bound 140, large single
  local ACQ = "wh3_dlc27_spell_bound_acquiescence"                -- 200 m -> bound 140
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local PLAIN = "wh2_dlc09_tmb_inf_skeleton_warriors_0"
  local CMDR = "wh2_dlc09_tmb_cha_arkhan_0"
  local USHABTI = "wh2_dlc09_tmb_mon_ushabti_0"   -- large, not a single entity
  local GIANT = "wh_main_grn_mon_giant"           -- large, single entity
  local pre134 = checks
  local function lg(tag, v) return (tag ~= "[live] ") or v end
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end

  print("== HARNESS 134 - section 0zf: the round-135 tokens ==")
  if not RED134 then
    for _, f in ipairs({ { name = "live", path = L134 }, { name = "ann", path = A134 } }) do
      local s = read_file(f.path)
      check("0zf " .. f.name .. ": the fast-enemy evaluator is wired, 5 m/s and 40 m are the user's settings",
        raw_find(s, "enemy_fast_near_ally = FOURTH.evaluate_enemy_fast_near_ally,", 1, true) ~= nil
        and raw_find(s, "FOURTH.FAST_ENEMY_MPS = 5 ", 1, true) ~= nil
        and raw_find(s, "FOURTH.FAST_ENEMY_NEAR_M = 40 ", 1, true) ~= nil)
      check("0zf " .. f.name .. ": counts enemy_melee 14, enemy_fast_near_ally 4, enemy_engaged_or_shot 70, 15 target classes",
        cp(s, 'trigger = "enemy_melee"') == 14 and cp(s, 'trigger = "enemy_fast_near_ally"') == 4
        and cp(s, 'trigger = "enemy_engaged_or_shot"') == 70 and cp(s, "\t\ttarget_class = ") == 15)
      check("0zf " .. f.name .. ": the picker and the pre-cast re-check both test the class; the generated size sets exist",
        raw_find(s, "\t\t\t\t\t\t\t\tand FOURTH.eg_class_ok(enemy)\n", 1, true) ~= nil
        and raw_find(s, "\t\t\tor not FOURTH.eg_class_ok(enemy) then\n", 1, true) ~= nil
        and raw_find(s, "FOURTH.class_keys.large = {", 1, true) ~= nil
        and raw_find(s, "FOURTH.class_keys.single = {", 1, true) ~= nil)
    end
  end

  local FILES = { { path = A134, tag = "[annotated] " }, { path = L134, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function fires_of(W, key)
    local n = 0
    for _, f in ipairs(W.fires) do if f.key == key then n = n + 1 end end
    return n
  end
  local function world(wname, units, enemies, arm, key, PATH, TAG)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = key } } })
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
  -- caster dist = its gap to the enemy; ally_dist = an ally's gap to the enemy (nil = no ally)
  local function fast(b, key, cdist, ally_dist, edef)
    local units = { { name = CASTER, uid = b, owns = { key }, melee = false, dist = cdist } }
    if ally_dist ~= nil then units[2] = { name = PLAIN, uid = b + 1, owns = {}, melee = false, dist = ally_dist } end
    local e = { name = "enemy_cavalry", uid = b + 5, melee = false, moving = true, fast_speed = 7 }
    for k, v in pairs(edef or {}) do e[k] = v end
    return units, { e }
  end
  local function hex(b, key, ename, edef)
    local e = { name = ename, uid = b + 5, melee = true }
    for k, v in pairs(edef or {}) do e[k] = v end
    return { { name = CASTER, uid = b, owns = { key }, melee = false, dist = 20 } }, { e }
  end
  -- name, builder(b) -> units, enemies; marker; key; GREEN casts; RED casts (nil = not RED); live reason
  local WORLDS = {
    { "F1. Mither: an enemy moving at 7 m/s, 30 m from the caster -> ONE cast at it",
      function(b) return fast(b, MITH, 30, nil) end, "mither", MITH, 1, 0, "reason: fast enemy near our units (targeting enemy_cavalry, run speed 7.0 m/s >= 5" },
    { "F2. Mither: the enemy runs at 4.5 m/s (infantry) -> no cast",
      function(b) return fast(b, MITH, 30, nil, { fast_speed = 4.5 }) end, "mither", MITH, 0, nil, nil },
    { "F3. Mither: a fast enemy that is not moving -> no cast",
      function(b) return fast(b, MITH, 30, nil, { moving = false, fast_speed = 9 }) end, "mither", MITH, 0, nil, nil },
    { "F4. Mither: the enemy is 50 m from the caster (bound 52) and 30 m from an ally -> ONE cast",
      function(b) return fast(b, MITH, 50, 30) end, "mither", MITH, 1, 0, "30.0m from our closest unit <= 40m" },
    { "F5. Mither: 50 m from the caster, the ally 60 m away -> no cast (no unit of ours within 40 m)",
      function(b) return fast(b, MITH, 50, 60) end, "mither", MITH, 0, nil, nil },
    { "F6. Mither: 10 m from an ally but 60 m from the caster (bound 52) -> no cast",
      function(b) return fast(b, MITH, 60, 10) end, "mither", MITH, 0, nil, nil },
    { "F7. Whispering Mist: an enemy at exactly 5.0 m/s, 30 m away -> ONE cast (5 m/s counts)",
      function(b) return fast(b, WMIST, 30, nil, { fast_speed = 5.0 }) end, "whispering_mist", WMIST, 1, nil, nil },
    { "L1. Looming Dread: the enemy in melee is not a Lord or Hero -> no cast",
      function(b) return hex(b, LOOM, PLAIN) end, "looming_dread", LOOM, 0, 1, nil },
    { "L2. Looming Dread: the enemy in melee is a Lord -> ONE cast",
      function(b) return hex(b, LOOM, CMDR) end, "looming_dread", LOOM, 1, nil, nil },
    { "L3. Tendrils of the Sea: a large enemy (Ushabti) in melee -> ONE cast",
      function(b) return hex(b, TEND, USHABTI) end, "tendrils_of_the_sea", TEND, 1, nil, nil },
    { "L4. Tendrils of the Sea: a small enemy in melee -> no cast",
      function(b) return hex(b, TEND, PLAIN) end, "tendrils_of_the_sea", TEND, 0, nil, nil },
    { "L5. Fecund Rebirth: a large enemy of several models (Ushabti) -> no cast",
      function(b) return hex(b, FEC, USHABTI) end, "mark_of_the_monster", FEC, 0, 1, nil },
    { "L6. Fecund Rebirth: a large single entity (Giant) in melee -> ONE cast",
      function(b) return hex(b, FEC, GIANT) end, "mark_of_the_monster", FEC, 1, nil, nil },
    { "M1. Acquiescence: the enemy is only under missile fire -> no cast (enemy_melee)",
      function(b) return hex(b, ACQ, PLAIN, { melee = false, missile = true }) end, "acquiescence", ACQ, 0, 1, nil },
    { "M2. Acquiescence: the enemy is in melee -> ONE cast",
      function(b) return hex(b, ACQ, PLAIN) end, "acquiescence", ACQ, 1, nil, nil },
  }

  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[5]
      if RED134 then want = w[6] end
      if want ~= nil then
        local base = 13600 + i * 10
        local units, enemies = w[2](base)
        local W = world(w[1], units, enemies, { base, w[3] }, w[4], f.path, TAG)
        if W ~= nil then
          local got = fires_of(W, w[4])
          local a = (got == want)
          if a and want == 1 then
            local t = W.fires[1].target
            a = (W.fires[1].uid == base) and t ~= nil and t.zz_uid == base + 5
          end
          if a and want == 1 and w[7] ~= nil and not RED134 then
            a = lg(TAG, count_log(W, w[7]) >= 1)
          end
          check(TAG .. w[1]:sub(1, 2) .. (RED134 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got
            .. ((want == 1) and " (aimed at the enemy)" or "")
            .. ((w[7] ~= nil and not RED134) and (" (log '" .. w[7] .. "' [live])") or ""), a)
          done(a)
          tally(W)
        end
      end
    end
  end

  if RED134 then
    check("RED CONTROL (harness 134): the pre-135 build has no fast-enemy trigger and no target filter - " .. n_ok .. "/" .. n_all,
      n_all == 10 and n_ok == 10)
  else
    check("HARNESS 134: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 30 and n_ok == 30)
  end
  print("== HARNESS 134 done: " .. (checks - pre134) .. " checks in this section ==")
end
'''

PIN_RULES = [
    (r"(trigger = \"enemy_engaged_or_shot\"'\)) == 85\b", r"\1 == 70"),
    (r"\bes = 85\b", "es = 70"),
    (r"(trigger = \"enemy_melee\"'\)) == 3\b", r"\1 == 14"),
]
WORLD_RULES = [
    ('enemies = { { name = "orc_boyz", uid = euid, melee = true } },',
     'enemies = { { name = (FAM_.marker == "headhunt") and "%s" or "orc_boyz", uid = euid, melee = true } },' % LORD),
    ('enemies = { { name = "orc_boyz", uid = 9822, melee = true } },',
     'enemies = { { name = "%s", uid = 9822, melee = true } },' % LORD),
    ('enemies = { { name = "enemy_block", uid = uid + 1, melee = false, missile = true } },',
     'enemies = { { name = "%s", uid = uid + 1, melee = false, missile = true } },' % LORD),
    ('local edef = { name = "enemy_block", uid = euid }',
     'local edef = { name = (b[1] == "transfix_hex") and "%s" or "enemy_block", uid = euid }' % LORD),
    ('"reason: closest fighting (in-melee) enemy within bound (targeting enemy_block") == 1)',
     '"reason: closest fighting (in-melee) enemy within bound (targeting " .. edef.name) == 1)'),
]
src = open(SRC, encoding="utf-8").read()
lines = src.split("\n")
changed, hits = [], {a: 0 for a, _ in PIN_RULES}
for i, ln in enumerate(lines):
    if ln.lstrip().startswith("--"):
        continue
    new = ln
    for a, b in PIN_RULES:
        new2, n = re.subn(a, b, new)
        if n:
            hits[a] += n
            new = new2
    if new != ln:
        changed.append((i + 1, ln.strip()[:110], new.strip()[:110]))
        lines[i] = new
src = "\n".join(lines)
print("count-pin lines rebased:", len(changed), "| rules with no hit:", [a for a, v in hits.items() if v == 0])
for n, old, new in changed:
    print("  L%-6d OLD %s\n          NEW %s" % (n, old, new))
for a, b in WORLD_RULES:
    assert src.count(a) == 1, (a[:70], src.count(a))
    src = src.replace(a, b)
print("world rebases:", len(WORLD_RULES))
TIP_OLD = ('    melee_or_under_fire = "When armed, fires when this unit (or, for an aura, a friendly unit near it) is in melee '
           'or under missile fire",\n')
TIP_NEW = TIP_OLD + '    enemy_fast_near_ally = "When armed, fires on a fast enemy unit moving close to your units",\n'
assert src.count(TIP_OLD) == 1, src.count(TIP_OLD)
src = src.replace(TIP_OLD, TIP_NEW)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h132()\nrun_h133()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, CALL + "run_h134()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
