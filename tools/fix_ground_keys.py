"""Fix: EVERY ground-castable entry of this round must sit in enemy_ground_keys -
the 68 A keys, the nine D keys and the four Dreaded Thirteenth keys (81), not
just the thirteen added first."""
import os, json

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
GEN = os.path.join(os.path.expandvars(r"%LOCALAPPDATA%\Temp"), "gen")
plan = json.load(open(os.path.join(GEN, "plan.json"), encoding="utf-8"))
A = plan["A_keys"]
D = plan["D_keys"]
F = plan["F_keys"]

def rd(p): return open(p, "rb").read().decode("utf-8")
def wr(p, s): open(p, "wb").write(s.encode("utf-8"))

for p in (os.path.join(ROOT, "mod_source", "script", "battle", "mod", "zz_test_deadly_onslaught.lua"),
          os.path.join(ROOT, "docs", "WH3_auto_ability_annotated.lua")):
    s = rd(p)
    # drop the thirteen lines added by stage 1 (D nine + F four), keep the anchor
    i = s.find('\t\t["wh3_main_character_abilities_gate_of_khorne"] = true,\n')
    j = s.find("\t},\n", i)
    assert i > 0 and j > i
    head = s[:i] + '\t\t["wh3_main_character_abilities_gate_of_khorne"] = true,\n'
    tail = s[j:]
    add = ("\t\t-- THE SUMMON ROUND (harness 102), part 1: the 68 keys of the A batch -\n"
           "\t\t-- every in-wheel, non-illusion, GROUND-CASTABLE wh_type_summon_unit row\n"
           "\t\t-- left. Each one is placed on the CHOSEN ENEMY's ground.\n")
    for k in A:
        add += '\t\t["%s"] = true,\n' % k
    add += ("\t\t-- THE SUMMON ROUND, part 2: the nine unlabelled real spawners (D).\n")
    for k in D:
        add += '\t\t["%s"] = true,\n' % k
    add += ("\t\t-- THE SUMMON ROUND, part 3: The Dreaded Thirteenth's four keys (F) -\n"
            "\t\t-- an explosion plus a summon, placed on the enemy's ground.\n")
    for k in F:
        add += '\t\t["%s"] = true,\n' % k
    s = head + add + tail
    n = s.count('"] = true,')
    # count only inside the enemy_ground_keys block
    i2 = s.find("enemy_ground_keys = {")
    j2 = s.find("\t},\n", i2)
    blk = s[i2:j2]
    print(os.path.basename(p), "enemy_ground_keys entries:", blk.count('"] = true,'))
    wr(p, s)
    assert "\r" not in s
