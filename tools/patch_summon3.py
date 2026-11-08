"""Stage 3: evaluator map entries, tooltip wording, per-ability poll slots."""
import os

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
LIVE = os.path.join(ROOT, "mod_source", "script", "battle", "mod", "zz_test_deadly_onslaught.lua")
ANN = os.path.join(ROOT, "docs", "WH3_auto_ability_annotated.lua")

def rd(p): return open(p, "rb").read().decode("utf-8")
def wr(p, s):
    assert "\r" not in s
    open(p, "wb").write(s.encode("utf-8"))

def sub(s, old, new, count=1, tag=""):
    n = s.count(old)
    assert n == count, "anchor %r hit %d (want %d) %s" % (old[:70], n, count, tag)
    return s.replace(old, new)

MAP_OLD = "\tenemy_ground_melee = FOURTH.evaluate_enemy_ground_melee,\n"
MAP_NEW = ("\tenemy_ground_melee = FOURTH.evaluate_enemy_ground_melee,\n"
           "\t-- THE SUMMON ROUND (harness 102): the self-summon and the two\n"
           "\t-- non-commander enemy triggers, each its own evaluator.\n"
           "\tself_summon_melee = FOURTH.evaluate_self_summon_melee,\n"
           "\tenemy_low_health_noncommander = FOURTH.evaluate_enemy_low_health_noncommander,\n"
           "\tenemy_melee_noncommander = FOURTH.evaluate_enemy_melee_noncommander,\n")

TIP_OLD = '\tenemy_ground_melee = "When armed, fires when an enemy in range is fighting in melee and the summon is placed on its ground",\n'
TIP_NEW = ('\tenemy_ground_melee = "When armed, fires when an enemy in range is fighting in melee and the summon is placed on its ground",\n'
           '\tself_summon_melee = "When armed, fires when this unit itself is fighting in melee and the summon is cast on it",\n'
           '\tenemy_low_health_noncommander = "When armed, fires on the lowest-health enemy in range that is below 20% health and is not a Lord or Hero",\n'
           '\tenemy_melee_noncommander = "When armed, fires on the closest enemy in range that is fighting in melee and is not a Lord or Hero",\n')

CLR_OLD = "\t\t\t\t\tFOURTH.eg_melee_only = nil\n"
CLR_NEW = ("\t\t\t\t\tFOURTH.eg_melee_only = nil\n"
           "\t\t\t\t\t-- THE SUMMON ROUND (harness 102): the self-summon arm and the two\n"
           "\t\t\t\t\t-- non-commander enemy modes are cleared before EVERY evaluate, so no\n"
           "\t\t\t\t\t-- ability can inherit another's flag, target or cast mode.\n"
           "\t\t\t\t\tFOURTH.ss_self = nil\n"
           "\t\t\t\t\tFOURTH.ss_caster_su = nil\n"
           "\t\t\t\t\tFOURTH.eg_noncommander = nil\n"
           "\t\t\t\t\tFOURTH.eg_mode = nil\n")

RANGE_OLD = "\t\t\t\t\tFOURTH.eg_range_m = ability.range_m\n"
RANGE_NEW = ("\t\t\t\t\tFOURTH.eg_range_m = ability.range_m\n"
             "\t\t\t\t\t-- AN UNBOUNDED ENTRY (harness 102): its game row declares\n"
             "\t\t\t\t\t-- target_intercept_range = -1.0 - no real range to take 70% of.\n"
             "\t\t\t\t\tFOURTH.eg_no_bound = (ability.unbounded == true)\n")

for path, tag in ((LIVE, "live"), (ANN, "ann")):
    s = rd(path)
    s = sub(s, MAP_OLD, MAP_NEW, 1, tag)
    s = sub(s, TIP_OLD, TIP_NEW, 1, tag)
    s = sub(s, CLR_OLD, CLR_NEW, 1, tag)
    s = sub(s, RANGE_OLD, RANGE_NEW, 1, tag)
    wr(path, s)
    print(tag, "stage 3 written", len(s))
