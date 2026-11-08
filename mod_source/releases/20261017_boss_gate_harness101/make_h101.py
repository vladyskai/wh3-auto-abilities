# -*- coding: utf-8 -*-
"""Assemble harness101.lua from the SHIPPED harness100.lua.

Round 101: five boss-only entries removed (577 -> 573 entries, 603 -> 599
keys, melee_unwavering 362 -> 360, enemy_engaged_or_shot 89 -> 86) and Gate of
Khorne added (+1 entry / +1 key, its own enemy_ground_melee trigger).

Every pin that names the CURRENT table size is re-based; the harness-100
narrative lines that describe the 579 -> 577 removal are history and stay.
"""
import io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261017_remove_army_two_harness100\harness100.lua"
NL = chr(10)

def read(p): return io.open(p, encoding="utf-8", newline="").read()
def write(p, s): io.open(p, "w", encoding="utf-8", newline="").write(s)

src = read(SRC)

# ------------------------------------------------------------------ env pair
for a, b in (("H100_LIVE", "H101_LIVE"), ("H100_ANN", "H101_ANN")):
    assert a in src
    src = src.replace(a, b)
src = src.replace("-- HARNESS 100 (this round): the env pair is now H101_LIVE / H101_ANN.",
                  "-- HARNESS 101 (this round): the env pair is now H101_LIVE / H101_ANN.")

# ------------------------------------------------------------------ the removed representative
old = ('{ real = 30,  bound = 21,  marker = "bitter_sting", '
       'key = "wh3_dlc27_qb_unit_abilities_bitter_sting", ground = false }')
new = ('{ real = 30,  bound = 21,  marker = "dispatch_the_swarm_attack", '
       'key = "wh3_dlc29_hero_active_dispatch_the_swarm_attack", ground = false }')
assert src.count(old) == 1, "bitter_sting FAM row"
src = src.replace(old, new, 1)
src = src.replace("-- THE 12 REAL-RANGE FAMILIES: one representative ability apiece (unit form",
                  "-- THE 12 REAL-RANGE FAMILIES: one representative ability apiece (unit form")
# note the swap in the FAM comment
src = src.replace("  local FAM = {", "  -- ROUND 101: the real=30 representative is dispatch_the_swarm_attack\n"
                                     "  -- (Bitter Sting was REMOVED - a boss-only entry).\n  local FAM = {", 1)

# ------------------------------------------------------------------ numeric re-base
lines = src.split(NL)
HIST = set()
for i, ln in enumerate(lines, 1):
    if "(579 - 2 / 605 - 2)" in ln or "are REMOVED from the ABILITIES table - 577 entries" in ln:
        HIST.add(i)
n = {577: 0, 603: 0, 362: 0, 89: 0}
for i, ln in enumerate(lines, 1):
    if i in HIST:
        continue
    if re.search(r"(?<!\d)577(?!\d)", ln):
        n[577] += len(re.findall(r"(?<!\d)577(?!\d)", ln)); ln = re.sub(r"(?<!\d)577(?!\d)", "573", ln)
    if re.search(r"(?<!\d)603(?!\d)", ln):
        n[603] += len(re.findall(r"(?<!\d)603(?!\d)", ln)); ln = re.sub(r"(?<!\d)603(?!\d)", "599", ln)
    if re.search(r"(?<!\d)362(?!\d)", ln):
        n[362] += len(re.findall(r"(?<!\d)362(?!\d)", ln)); ln = re.sub(r"(?<!\d)362(?!\d)", "360", ln)
    # the enemy_engaged_or_shot pin (89) - only the 0u check line carries it
    if 'trigger = "enemy_engaged_or_shot"\' ) == 89' in ln or 'enemy_engaged_or_shot"\'\)) == 89' in ln:
        n[89] += ln.count("== 89"); ln = ln.replace("== 89", "== 86")
    lines[i - 1] = ln
src = NL.join(lines)
print("re-based: 577 x%d, 603 x%d, 362 x%d, 89 x%d" % (n[577], n[603], n[362], n[89]))
assert n[577] > 0 and n[603] > 0 and n[362] > 0, n

def sub(old, new, label, count=1):
    global src
    assert src.count(old) == count, "%s: %d matches (want %d)" % (label, src.count(old), count)
    src = src.replace(old, new, count)
    print("patch", label)

# the two exact-count expressions the re-base cannot see (they carry == 89 / == 98)
old_0u = ("""      cp(s, 'trigger = "melee_unwavering"') == 360 and cp(s, 'trigger = "enemy_engaged_or_shot"') == 89 and cp(s, 'trigger = "enemy_ground_area"') == 9)""")
new_0u = ("""      cp(s, 'trigger = "melee_unwavering"') == 360 and cp(s, 'trigger = "enemy_engaged_or_shot"') == 86
      and cp(s, 'trigger = "enemy_ground_area"') == 9 and cp(s, 'trigger = "enemy_ground_melee"') == 1)""")
assert src.count(old_0u) == 1, "0u trigger line"
src = src.replace(old_0u, new_0u, 1)
print("patch 0u trigger counts")

sub('check("0u " .. nm .. ": the trigger counts moved (melee_unwavering 383, enemy_engaged_or_shot 89, enemy_ground_area 9)",',
    'check("0u " .. nm .. ": the trigger counts moved (melee_unwavering 360, enemy_engaged_or_shot 86, enemy_ground_area 9)",',
    "0u count label")
sub('check("0u " .. nm .. ": every Class-A entry carries its REAL range (range_real x98)",\n      cp97(s, "\\t\\trange_real = ") == 98)',
    'check("0u " .. nm .. ": every Class-A entry carries its REAL range (range_real x96)",\n      cp97(s, "\\t\\trange_real = ") == 96)',
    "0u range_real pin")

# ------------------------------------------------------------------ h100 section re-base
sub("""  local EXP
  if RED_MODE then
    EXP = { entries = 579, keys = 605, mu = 363, ush = 34, present = true }
  else
    EXP = { entries = 573, keys = 599, mu = 360, ush = 33, present = false }
  end""",
    """  local EXP
  if RED_MODE then
    -- ROUND 101: the red snapshot is the PRE-101 build - post-100, so it
    -- already carries the army removal (577 / 603 / 362) and NOT the 101 edits.
    EXP = { entries = 577, keys = 603, mu = 362, ush = 33, present = false }
  else
    EXP = { entries = 573, keys = 599, mu = 360, ush = 33, present = false }
  end""", "h100 EXP")

old_red100 = ('  if RED_MODE then\n'
              '    check("RED CONTROL (harness 100): the pre-edit snapshot carries BOTH keys, their markers and badges, and "\n'
              '      .. "579 entries / 605 keys - every green removal check above would FAIL on it", ok_all)\n'
              '  else\n')
new_red100 = ('  if RED_MODE then\n'
              '    check("RED CONTROL (harness 100): N/A for the harness-101 round - the harness-101 red snapshot is the "\n'
              '      .. "shipped harness-100 build (577 / 603), so the army keys are already gone and every 0x check "\n'
              '      .. "passes by design. The boss-removal red control lives in harness 101.", ok_all)\n'
              '  else\n')
assert src.count(old_red100) == 1, "h100 red control"
src = src.replace(old_red100, new_red100, 1)
print("patch h100 red control")

# the h100 headline label keeps its numbers in the text (already re-based to 573/599)
# ------------------------------------------------------------------ banner + tail token list
sub('  print("   *** REMOVAL (harness 100): the pre-edit snapshot still CARRIES Meat Feast and Massacre")',
    '  print("   *** REMOVAL + GATE (harness 101): the pre-edit snapshot still CARRIES the five boss-only")',
    "banner l1")
sub('  print("   *** (579 entries / 605 keys), so every 0x removal check is GREEN-only and flips RED there.***")',
    '  print("   *** entries and has no Gate of Khorne, so every 0y check is GREEN-only and flips RED there.***")',
    "banner l2")
sub("94, 95, 96, 97, 98 AND 99's worlds included", "94, 95, 96, 97, 98, 99 AND 100's worlds included", "tail list")

# ------------------------------------------------------------------ append section
section = read(HERE + "/h101_section.lua").lstrip(NL)
assert src.count(NL + "run_h100()" + NL) == 1
src = src.replace(NL + "run_h100()" + NL, NL + "run_h100()" + NL + NL + section + NL, 1)

# ------------------------------------------------------------------ post-patches on the assembled file
# (they live here so the shipped harness101.lua is exactly this script's output)
def sub2(old, new, label, count=1):
    global src
    assert src.count(old) == count, "%s: %d matches (want %d)" % (label, src.count(old), count)
    src = src.replace(old, new, count)
    print("post", label)
sub2("    a = (it == 1154)", "    a = (it == 1146)", "A4a iterations 2x577 -> 2x573")
sub2('    enemy_ground_area = "When armed, fires when an enemy in range is in melee or under missile fire and the area hex is placed on its ground",',
     '    enemy_ground_area = "When armed, fires when an enemy in range is in melee or under missile fire and the area hex is placed on its ground",\n'
     '    enemy_ground_melee = "When armed, fires when an enemy in range is fighting in melee and the summon is placed on its ground",',
     "h93 allowed wording")
# the 0u check still carries the one remaining enemy_engaged_or_shot == 89
old89 = "and cp97(s, 'trigger = \"enemy_engaged_or_shot\"') == 89"
assert src.count(old89) == 1, src.count(old89)
src = src.replace(old89, "and cp97(s, 'trigger = \"enemy_engaged_or_shot\"') == 86", 1)
print("post 0u 89 -> 86")
sub2('      and cp97(s, \'trigger = "enemy_ground_area"\') == 9)',
     '      and cp97(s, \'trigger = "enemy_ground_area"\') == 9\n      and cp97(s, \'trigger = "enemy_ground_melee"\') == 1)',
     "0u gate count")

write(HERE + "/harness101.lua", src)
print("wrote harness101.lua", len(src), "bytes")
