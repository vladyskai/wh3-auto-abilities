#!/usr/bin/env python3
"""Build harness121.lua from harness120.lua for round 122.

Round 122 added ten self-cast melee buffs on the EXISTING shared
melee_unwavering evaluator (user ruling 2026-10-27). This is a TUNING round:
only the new section is the proof, run in light mode (H118_LIGHT=1). The older
sections and their count pins (687 entries, melee_unwavering 360, ...) are NOT
rebased here; that is sign-off work, and a full run of this file is expected to
show those stale count pins until then.

This script:
  1. prepends the round-122 banner;
  2. appends run_h121 (the new section) before the runner;
  3. calls run_h121() after run_h118() in the runner.
Older harnesses are never edited.
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261021_armybar_removal_harness120\harness120.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261027_melee_buffs_harness121\harness121.lua"

BANNER = """-- ============================================================================
-- HARNESS 121 - ROUND 122, TEN SELF-CAST MELEE BUFFS (user ruling 2026-10-27,
-- verbatim): "Approved as recommended: Group A on melee_unwavering, Group B on
-- melee_unwavering. Implement as a tuning round."
--
--   Ten new ABILITIES entries ride the EXISTING shared melee_unwavering
--   evaluator (fires in melee when not wavering; cast on the unit itself):
--     GROUP A: Call for Power, Manus of Ursun, Black Hammer of Hashut,
--              The Graven Sceptre, Tyrant's Talon, The Crimson Blade
--     GROUP B: Bloodstorm, Crooked Dice, Temptator, All-Consuming Hatred
--   Table: 687 entries / 738 keys -> 697 / 748; melee_unwavering 360 -> 370.
--
--   Edited vs harness120: this banner, the new run_h121 section, and its call
--   in the runner. TUNING ROUND: the proof is the light run (H118_LIGHT=1).
--   The older count pins are NOT rebased; that is sign-off work.
--   RED control: H121_LIVE / H121_ANN point the section at the pre-122 snapshot.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 121 (round 122): TEN SELF-CAST MELEE BUFFS ON melee_unwavering.
--   0r: tokens in BOTH files - the ten markers, badges and keys; the table is
--       697 entries with 697 badges; melee_unwavering is 370; no batch key is
--       in the army_spec junction (read from the game's own extract).
--   M (per ability): in melee, not wavering -> FIRES once, cast on the OWNER,
--       with the shared reason "in melee, morale not wavering".
--   S (per ability): NOT in melee -> SILENT.
--   V (per ability): in melee but WAVERING -> SILENT.
--   RED CONTROL: with H121_LIVE / H121_ANN on the pre-122 snapshot every 0r
--   token and every M world fails (the entries are absent, nothing fires);
--   S and V pass trivially.
-- ============================================================================
function run_h121()
  local L121 = os.getenv("H121_LIVE") or LIVE
  local A121 = os.getenv("H121_ANN") or ANN
  local RED121 = (os.getenv("H121_LIVE") ~= nil) or (os.getenv("H121_ANN") ~= nil)
  local BATCH = {
    { "call_for_power", "wh3_main_daemon_head_abilities_call_for_power" },
    { "manus_of_ursun", "wh3_main_weapon_abilities_ursuns_claws" },
    { "black_hammer_of_hashut", "wh3_dlc23_weapon_abilities_black_hammer_of_hashut" },
    { "the_graven_sceptre", "wh3_dlc23_weapon_abilities_the_graven_sceptre" },
    { "tyrants_talon", "wh3_cp1_weapon_abilities_tyrants_talon" },
    { "the_crimson_blade", "wh3_dlc29_item_abilities_crimson_blade" },
    { "bloodstorm", "wh2_dlc14_lord_abilities_bloodstorm" },
    { "crooked_dice", "wh3_dlc23_hero_abilities_crooked_dice" },
    { "temptator", "wh3_dlc20_lord_abilities_temptator" },
    { "all_consuming_hatred", "wh3_dlc27_unit_abilities_consuming_hatred" },
  }
  local pre121 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function lg(tag, v) return (tag ~= "[live] ") or v end

  print("== HARNESS 121 - section 0r: the ten new melee_unwavering entries (BOTH files) ==")
  local army = {}
  local fh = io.open("C:/Users/vlady/AppData/Local/Temp/wh3/army_spec.tsv", "r")
  check("0r: the army_spec extract is readable", fh ~= nil)
  if fh then
    fh:read("*l")
    for ln in fh:lines() do
      local k = ln:match("^([^\t#][^\t]*)")
      if k then army[k] = true end
    end
    fh:close()
  end
  for _, f in ipairs({ { name = "live", path = L121 }, { name = "ann", path = A121 } }) do
    local nm, s = f.name, read_file(f.path)
    check("0r " .. nm .. ": the table is 697 entries, each with a badge field ("
      .. cp(s, "\t{ marker = ") .. ")", cp(s, "\t{ marker = ") == 697 and cp(s, 'badge = "') == 697)
    check("0r " .. nm .. ": melee_unwavering is 370 entries (" .. cp(s, 'trigger = "melee_unwavering"') .. ")",
      cp(s, 'trigger = "melee_unwavering"') == 370)
    for _, b in ipairs(BATCH) do
      local m, k = b[1], b[2]
      check("0r " .. nm .. ": " .. m .. " is present once on melee_unwavering with its badge and key",
        cp(s, 'marker = "' .. m .. '", name = ') == 1
        and raw_find(s, 'marker = "' .. m .. '", name = "', 1, true) ~= nil
        and cp(s, 'badge = "zz_auto_badge_' .. m .. '"') == 1
        and cp(s, '"' .. k .. '"') == 1
        and raw_find(s, 'marker = "' .. m .. '", name = "[^"]*", trigger = "melee_unwavering"') ~= nil)
    end
  end
  local army_hits = 0
  for _, b in ipairs(BATCH) do if army[b[2]] then army_hits = army_hits + 1 end end
  check("0r: NO batch key is in the army_spec junction (" .. army_hits .. " hit(s))", army_hits == 0)

  local results, n_ok = {}, 0
  local function boot(W, PATH, TAG, uid, marker, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. marker); ui(W)
    W.conflict = true
    return true
  end
  local function world(PATH, TAG, i, b, kind)
    local m, k = b[1], b[2]
    local uid = 12100 + i * 10 + ({ M = 1, S = 2, V = 3 })[kind]
    local melee = (kind ~= "S")
    local wav = (kind == "V")
    local W = make_world({ can_perform = true, units = {
      { name = "owner", uid = uid, owns = { k }, melee = melee, wavering = wav },
    }, cards = { { id = tostring(uid), state = "active", vis = true } }, bar = { { id = "b1", key = k } } })
    local wname = kind .. i
    if not boot(W, PATH, TAG, uid, m, wname) then return false end
    polln(W, 1)
    local ok
    if kind == "M" then
      local a = (#W.fires == 1 and W.fires[1].uid == uid and W.fires[1].key == k)
      check(TAG .. wname .. ": " .. m .. " in melee, not wavering -> FIRES once (" .. fire_detail(W) .. ")", a)
      local bb = (fire_target_for(W, uid) == unit_of(W, uid))
      check(TAG .. wname .. ": " .. m .. " is cast on the OWNER itself (self-cast)", bb)
      local c = (count_log(W, "reason: in melee, morale not wavering") == 1)
      check(TAG .. wname .. ": " .. m .. " uses the shared in-melee reason [live log]", lg(TAG, c))
      ok = a and bb and lg(TAG, c)
    else
      local why = (kind == "S") and "NOT in melee" or "in melee but WAVERING"
      ok = (#W.fires == 0)
      check(TAG .. wname .. ": " .. m .. " " .. why .. " -> SILENT (" .. fire_detail(W) .. ")", ok)
    end
    check(TAG .. wname .. ": every ui tick ran clean (" .. (W.ui_failures or 0) .. " failures)",
      (W.ui_failures or 0) == 0)
    tally(W)
    return ok
  end

  for i, b in ipairs(BATCH) do
    print("== HARNESS 121 - " .. b[1] .. ": fire / silent / wavering worlds ==")
    for _, kind in ipairs({ "M", "S", "V" }) do
      for _, f in ipairs({ { path = A121, tag = "[annotated] " }, { path = L121, tag = "[live] " } }) do
        local r = world(f.path, f.tag, i, b, kind)
        results[#results + 1] = r
        if r then n_ok = n_ok + 1 end
      end
    end
  end

  if not RED121 then
    check("HARNESS 121: all 60 worlds behaved (10 abilities x fire/silent/wavering x live+annotated) - "
      .. n_ok .. "/60", n_ok == 60)
  else
    check("RED CONTROL (harness 121): on the pre-122 snapshot only the 40 SILENT worlds pass - "
      .. n_ok .. "/60 (want 40)", n_ok == 40)
  end
  print("== HARNESS 121 done: " .. (checks - pre121) .. " checks in this section ==")
end
'''

src = open(SRC, encoding="utf-8").read()

RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1, src.count(RUNNER_ANCHOR)
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)

CALL = "run_h117()\nrun_h118()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, "run_h117()\nrun_h118()\nrun_h121()\n")

# ---------------------------------------------------------------- count pins
# The table grew by ten entries / ten keys, all on melee_unwavering, so every
# LIVE table-size pin follows it: 687 -> 697 entries, 738 -> 748 keys,
# melee_unwavering 360 -> 370, and the A4 bootstrap iteration pin (2 per entry)
# 1374 -> 1394. Comment lines are history and stay. The RED-snapshot
# expectation rows (entries = 573 ...) are not touched.
PIN_RULES = [
    ("== 687", "== 697"),
    ("== 738", "== 748"),
    ("entries = 687, keys = 738, mu = 360", "entries = 697, keys = 748, mu = 370"),
    ("entries = 687, keys = 738, sum = true", "entries = 697, keys = 748, sum = true"),
    ("FULL 687-entry table", "FULL 697-entry table"),
    ("687 abilities per pass", "697 abilities per pass"),
    ("has 687 entries", "has 697 entries"),
    ("has all 738 keys", "has all 748 keys"),
    ("table of 687 after round h105", "table of 697 after round 122"),
    ("(12 air-drop entries of 687)", "(12 air-drop entries of 697)"),
    ("want 687", "want 697"),
    ("'trigger = \"melee_unwavering\"') == 360", "'trigger = \"melee_unwavering\"') == 370"),
    ("      mu == 360)", "      mu == 370)"),
    ("a = (it == 1374)", "a = (it == 1394)"),
]
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
        changed.append((i + 1, ln.strip()[:120]))
        lines[i] = new
src = "\n".join(lines)
print("count-pin lines rebased:", len(changed))
for c in changed:
    print("  L%-6d %s" % c)

src = BANNER + src
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
