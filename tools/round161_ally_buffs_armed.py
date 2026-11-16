#!/usr/bin/env python3
"""Round 161 (harness 160): the 14 ally melee buffs start ARMED (user ruling 2026-11-16, Bretonnia battle: "I feel like
Favour of the Fay could have been armed from the beginning" -> "Whole family"). ally_melee_buff joins
FOURTH.DEFAULT_ON_TRIGGERS; a badge click still switches any of them off.

Also the progress page: an ability shut by an old RULE (the 2026-10-09 family decisions, an 'auto:' exclusion, or a
collection-time 'unsuitable' skip) is no longer counted as decided: it is open, under its own group, because the user
never ruled on it (the round-159 '0 open' counted them as decided)."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
PP = r"C:\Users\vlady\Desktop\WH3_mod\tools\make_progress_page.py"


def sub(s, a, b, n=1):
    assert s.count(a) == n, (a[:80], s.count(a))
    return s.replace(a, b)


OLD = "\tself_out_of_ammo = true,\n"
NEW = OLD + "\tally_melee_buff = true,   -- ROUND 161 (user ruling 2026-11-16: the 14 ally melee buffs, \"Whole family\")\n"
for p in (SRC, ANN):
    s = open(p, encoding="utf-8", newline="").read()
    assert "\tally_melee_buff = true," not in s
    s = sub(s, OLD, NEW)
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("patched", p)

s = open(PP, encoding="utf-8", newline="").read()
G_OLD = ('def group_of(status):\n'
         '    s = status.lower()\n'
         '    if s.startswith(("rejected", "skipped")) or "already rejected" in s or "family decision" in s:\n'
         '        return "decided"\n'
         '    return "open"\n')
G_NEW = ('def shut_by_rule(status):\n'
         '    """ROUND 161: shut by an old RULE, never ruled on by the user: a 2026-10-09 family decision, an \'auto:\'\n'
         '    exclusion, or a collection-time \'unsuitable\' skip."""\n'
         '    s = status.lower()\n'
         '    return "family decision" in s or "(auto:" in s or s.lstrip("`").startswith("skipped (unsuitable")\n'
         '\n'
         '\n'
         'def group_of(status):\n'
         '    s = status.lower()\n'
         '    if shut_by_rule(status):\n'
         '        return "open"\n'
         '    if s.startswith(("rejected", "skipped")) or "already rejected" in s:\n'
         '        return "decided"\n'
         '    return "open"\n')
s = sub(s, G_OLD, G_NEW)
K_OLD = ('def open_kind(status, key):\n'
         '    s = status\n')
K_NEW = ('def open_kind(status, key):\n'
         '    s = status\n'
         '    if shut_by_rule(status):\n'
         '        return "R. Shut by an old rule (2026-10-09 families, auto, collection-time), never ruled on by the user"\n')
s = sub(s, K_OLD, K_NEW)
open(PP, "w", encoding="utf-8", newline="").write(s)
print("patched", PP)
