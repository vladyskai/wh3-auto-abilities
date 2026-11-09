#!/usr/bin/env python3
"""Build harness133.lua from harness132.lua for round 134 (audit batch 3: the speed buffs leave the
melee-only trigger; Thunderburner leaves the mod). Older harnesses are never edited.

Pin rebases (code lines only; comment lines untouched):
  entries 700 -> 698 and keys 752 -> 750 (Thunderburner and Thunderburner Upgraded removed),
  melee_unwavering 342 -> 328 (4 to charge_only, 8 to charge_or_melee, 2 removed),
  charge_or_melee 28 -> 36, charge_only 1 -> 5,
  wind-up keys 164 -> 162 (the two Thunderburner rows),
  full-table iterations 1400 -> 1396 (2 x 698),
  harness-85 S3c: of the 35 block-3 units in melee, 32 keep the shared in-melee reason and 3
    (Lightning Reflexes, Master of the Skies, Pendant of Slaanesh) now give the charge-or-melee
    in-melee reason.
The tooltip mirror is unchanged: no new family.
"""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261108_under_fire_harness132\harness132.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_speed_triggers_harness133\harness133.lua"

BANNER = """-- ============================================================================
-- HARNESS 133 - ROUND 134: AUDIT BATCH 3, THE SPEED BUFFS.
--   charge_only gains 4 (Apocalyptic Charge, Twilight Horn I, Potion of Speed,
--   Blooood!), charge_or_melee gains 8 (Book of Arkhan, Rune of Speed, Master
--   Rune of Speed, Lightning Reflexes, Master of the Skies, Pendant of Slaanesh,
--   Slippery, Transfix); Thunderburner and Thunderburner Upgraded leave the mod.
--   Edited vs harness132: this banner, the pin rebases listed in
--   tools/make_harness133.py, run_h133 and its call.
--   RED control: H133_LIVE / H133_ANN on docs/backups/round134/pre134_*.lua.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 133 (round 134): AUDIT BATCH 3, THE SPEED BUFFS.
--   0ze: tokens (Thunderburner gone; the trigger counts).
--   C1 Apocalyptic Charge: charging (fast, attack target 20 m) -> ONE cast, the
--      charge-only reason. C2: in melee, not charging -> no cast (no melee arm).
--   C3 Potion of Speed: charging -> ONE cast. C4 Blooood!: in melee -> no cast.
--   C5 Twilight Horn I: charging -> ONE cast.
--   G1 Pendant of Slaanesh: charging -> ONE cast. G2: in melee -> ONE cast, the
--      charge-or-melee in-melee reason.
--   G3 Rune of Speed: charging -> ONE cast. G4 Transfix: in melee -> ONE cast.
--   G5 Book of Arkhan: walking (not fast) with a target 20 m away -> no cast.
--   RED (pre-134 build = round 133): C1, C3 and G1 cast nothing; C2 and G2 cast
--      (the old melee-only trigger).
-- ============================================================================
function run_h133()
  local L133 = os.getenv("H133_LIVE") or LIVE
  local A133 = os.getenv("H133_ANN") or ANN
  local RED133 = (os.getenv("H133_LIVE") ~= nil) or (os.getenv("H133_ANN") ~= nil)
  local APO = "wh_pro04_unit_abilities_apocalyptic_charge"
  local POT = "wh_main_item_abilities_potion_of_speed"
  local BLO = "wh_main_unit_abilities_blooood"
  local TWI = "wh2_dlc16_item_abilities_twilight_horn_i"
  local PEN = "wh_main_item_abilities_pendant_of_slaanesh"
  local RUN = "wh2_dlc17_rune_abilities_rune_of_speed"
  local TRA = "wh2_dlc11_lord_abilities_transfix"
  local ARK = "wh_main_spell_bound_book_of_arkhan"
  local LORD = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  local pre133 = checks
  local function lg(tag, v) return (tag ~= "[live] ") or v end

  print("== HARNESS 133 - section 0ze: the round-134 tokens ==")
  if not RED133 then
    for _, f in ipairs({ { name = "live", path = L133 }, { name = "ann", path = A133 } }) do
      local s = read_file(f.path)
      check("0ze " .. f.name .. ": Thunderburner is gone (no marker, key or wind-up row)",
        raw_find(s, "thunderburner", 1, true) == nil)
      check("0ze " .. f.name .. ": melee_unwavering 328, charge_only 5, charge_or_melee 36, 698 entries",
        cp(s, 'trigger = "melee_unwavering"') == 328 and cp(s, 'trigger = "charge_only"') == 5
        and cp(s, 'trigger = "charge_or_melee"') == 36 and cp(s, "\t{ marker = ") == 698)
      local moved = true
      for _, m in ipairs({ "apocalyptic_charge", "twilight_horn_i", "potion_of_speed", "blooood" }) do
        if raw_find(s, '{ marker = "' .. m .. '", name = ', 1, true) == nil then moved = false end
      end
      check("0ze " .. f.name .. ": the four charge-only markers are present", moved)
    end
  end

  local FILES = { { path = A133, tag = "[annotated] " }, { path = L133, tag = "[live] " } }
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
  local function charging(uid, key)
    return { { name = LORD, uid = uid, owns = { key }, fast = true, melee = false, target = true, dist = 20, wavering = false } }
  end
  local function fighting(uid, key)
    return { { name = LORD, uid = uid, owns = { key }, fast = false, melee = true, wavering = false } }
  end
  local function walking(uid, key)
    return { { name = LORD, uid = uid, owns = { key }, fast = false, melee = false, target = true, dist = 20, wavering = false } }
  end
  -- name, units, marker, key, GREEN casts, RED casts (nil = not a RED world), live-log reason (or nil)
  local WORLDS = {
    { "C1. Apocalyptic Charge: charging -> ONE cast", charging, "apocalyptic_charge", APO, 1, 0, "reason: charging (charge only)" },
    { "C2. Apocalyptic Charge: in melee, not charging -> no cast (no melee arm)", fighting, "apocalyptic_charge", APO, 0, 1, nil },
    { "C3. Potion of Speed: charging -> ONE cast", charging, "potion_of_speed", POT, 1, 0, nil },
    { "C4. Blooood!: in melee, not charging -> no cast", fighting, "blooood", BLO, 0, nil, nil },
    { "C5. Twilight Horn I: charging -> ONE cast", charging, "twilight_horn_i", TWI, 1, nil, nil },
    { "G1. Pendant of Slaanesh: charging -> ONE cast", charging, "pendant_of_slaanesh", PEN, 1, 0, "reason: charging (gap=" },
    { "G2. Pendant of Slaanesh: in melee -> ONE cast (the melee arm stays)", fighting, "pendant_of_slaanesh", PEN, 1, 1, "reason: in melee (charge or melee)" },
    { "G3. Rune of Speed: charging -> ONE cast", charging, "rune_of_speed", RUN, 1, nil, nil },
    { "G4. Transfix: in melee -> ONE cast", fighting, "transfix", TRA, 1, nil, nil },
    { "G5. Book of Arkhan: walking (not fast) with a target 20 m away -> no cast", walking, "book_of_arkhan", ARK, 0, nil, nil },
  }

  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[5]
      if RED133 then want = w[6] end
      if want ~= nil then
        local base = 13500 + i * 10
        local W = world(w[1], w[2](base, w[4]), { base, w[3] }, w[4], f.path, TAG)
        if W ~= nil then
          local got = fires_of(W, w[4])
          local a = (got == want)
          if a and want == 1 then
            a = (W.fires[1].target == nil) or (W.fires[1].uid == base)
          end
          if a and want == 1 and w[7] ~= nil and not RED133 then
            a = lg(TAG, count_log(W, w[7]) >= 1)
          end
          check(TAG .. w[1]:sub(1, 2) .. (RED133 and "-RED" or "") .. "a: " .. want .. " cast(s) expected, got " .. got
            .. ((w[7] ~= nil and not RED133) and (" (reason '" .. w[7] .. "' [live log])") or ""), a)
          done(a)
          tally(W)
        end
      end
    end
  end

  if RED133 then
    check("RED CONTROL (harness 133): the pre-134 build casts the speed buffs only in melee - " .. n_ok .. "/" .. n_all,
      n_all == 10 and n_ok == 10)
  else
    check("HARNESS 133: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 20 and n_ok == 20)
  end
  print("== HARNESS 133 done: " .. (checks - pre133) .. " checks in this section ==")
end
'''

# (regex on code lines, replacement)
PIN_RULES = [
    (r"== 700\b", "== 698"),
    (r"== 752\b", "== 750"),
    (r"== 342\b", "== 328"),
    (r"it == 1400\b", "it == 1396"),
    (r"(trigger = \"charge_or_melee\"'\)) == 28\b", r"\1 == 36"),
    (r"\bcm == 28\b", "cm == 36"),
    (r"(trigger = \"charge_only\"'\)) == 1\b", r"\1 == 5"),
    (r"nkeys == 164\b", "nkeys == 162"),
    (r"entries = 700, keys = 752, mu = 342", "entries = 698, keys = 750, mu = 328"),
    (r"entries = 700, keys = 752, sum", "entries = 698, keys = 750, sum"),
    (r"want 700\b", "want 698"),
    (r"FULL 700-entry table", "FULL 698-entry table"),
    (r"700 abilities per pass", "698 abilities per pass"),
    (r"table of 700 after round 131", "table of 698 after round 134"),
    (r"\(12 air-drop entries of 700\)", "(12 air-drop entries of 698)"),
    (r"lg\(TAG, reasons == 35\)",
     "lg(TAG, reasons == 32 and count_log(W, \"reason: in melee (charge or melee)\") == 3)"),
    (r"\.\. \", want 35\) \[live log\]\"", ".. \", want 32 + 3 charge-or-melee since round 134) [live log]\""),
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
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h131()\nrun_h132()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, CALL + "run_h133()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
