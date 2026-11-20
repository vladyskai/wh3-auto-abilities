#!/usr/bin/env python3
"""Round 183 (user, 2026-11-20: "You may start implementing #1-9 for now"; rulings read from the Claude Docs review
"Rule-shut abilities review", rev 44, and its comment threads).

Rows 1-9 of docs\\WH3_rule_shut_review_2026-11-20.md, the "own-troop damage" rows (the 2026-10-09 rule was wrong: every
damage phase targets enemies only). Nine NEW entries, existing families, no new code:
  1 Defiling Deluge, 2 Murderous Exhortations, 3 Rod of Corruption, 4 Wail of Malice: "Recommended" = B, enemy_melee_near
    (the caster in melee, or an enemy within 70% of the 35 m aura = 24 m in melee); aura_real = 35.
  5 Plaguereaper: "B" = melee_health75 (thread: "the heal is considerable, we shouldn't waste it").
  6 Reaper of Souls: "Recommended" = C, melee_health75 (thread: "just in melee and less that 75% health").
  7 Shard Blade, 8 Web of Shadows: "A" = melee_unwavering.
  9 Warp-Quake: "Other (see comment)": "Melee_unwavering".
The multi-use keys (num_uses > 1) join cast_gate.hold_s (their recharge_time); none has a wind-up. Then every GENERATED
table keyed on the mod's own keys is regenerated (round171_regen_tables).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamedata_paths as GP  # noqa: E402
import round171_regen_tables as RT  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

ROWS = [
    (1, "defiling_deluge", "Defiling Deluge", "enemy_melee_near", "wh3_twa08_unit_abilities_defiling_deluge", 35),
    (2, "murderous_exhortations", "Murderous Exhortations", "enemy_melee_near",
     "wh3_dlc26_lord_abilities_murderous_exhortations", 35),
    (3, "rod_of_corruption", "Rod of Corruption", "enemy_melee_near", "wh2_main_item_abilities_rod_of_corruption", 35),
    (4, "wail_of_malice", "Wail of Malice", "enemy_melee_near", "wh2_dlc14_unit_abilities_wail_of_malice", 35),
    (5, "plaguereaper", "Plaguereaper", "melee_health75", "wh3_dlc29_item_abilities_plaguereaper", None),
    (6, "reaper_of_souls", "Reaper of Souls", "melee_health75", "wh2_dlc14_lord_abilities_reaper_of_souls", None),
    (7, "shard_blade", "Shard Blade", "melee_unwavering", "wh3_main_weapon_abilities_shard_blade", None),
    (8, "web_of_shadows", "Web of Shadows", "melee_unwavering", "wh2_main_weapon_abilities_web_of_shadows", None),
    (9, "warp_quake", "Warp-Quake", "melee_unwavering", "wh2_dlc14_unit_abilities_warp_quake", None),
]
KEYS = [r[4] for r in ROWS]
FAMILY = {r[4]: r[3] for r in ROWS}


def sub(s, a, b, n=1):
    assert s.count(a) == n, (a[:80], s.count(a))
    return s.replace(a, b)


def entry(row, marker, name, trig, key, aura):
    lines = ['\t-- ROUND 183 (rule-shut review row %d)' % row,
             '\t{ marker = "%s", name = "%s", trigger = "%s",' % (marker, name, trig),
             '\t\tbadge = "zz_auto_badge_%s",' % marker,
             '\t\tkeys = { "%s" },' % key]
    if aura is not None:
        lines.append("\t\taura_real = %d," % aura)
    lines.append("\t\tox = 0, oy = 0 },")
    return "\n".join(lines) + "\n"


def tsv(n):
    f = open(os.path.join(GP.GAMEDATA, n), encoding="utf-8-sig")
    h = f.readline().rstrip("\n").split("\t")
    f.readline()
    return [dict(zip(h, ln.rstrip("\n").split("\t"))) for ln in f]


def num(v):
    f = float(v)
    return str(int(f)) if f == int(f) else ("%.3f" % f).rstrip("0").rstrip(".")


USA = {r["key"]: r for r in tsv("unit_spec_abil.tsv")}
for _r in ROWS:
    u = USA[_r[4]]
    if _r[5] is not None:   # the 70% rule reads the aura from the game: effect_range
        assert float(u["effect_range"]) == _r[5], (_r[4], u["effect_range"])
    assert float(u["wind_up_time"] or 0) == 0, _r[4]
HOLD = [(k, num(USA[k]["recharge_time"])) for k in KEYS if int(float(USA[k]["num_uses"])) > 1]
print("multi-use keys:", HOLD)

RESTOCK = '\t{ marker = "restock", name = "Restock!", trigger = "ally_ammo_low",'
NEW_ENTRIES = "".join(entry(*r) for r in ROWS)
HOLD_OLD = "\thold_s = {\n"
HOLD_NEW = HOLD_OLD + ("\t\t-- ROUND 183: the rule-shut review's rows 1-9 with more than one use (recharge_time)\n"
                       + "".join('\t\t["%s"] = %s,\n' % (k, v) for k, v in HOLD))


def main():
    for path in (SRC, ANN):
        s = open(path, encoding="utf-8", newline="").read()
        for r in ROWS:
            assert ('"%s"' % r[4]) not in s, r[4]
            assert ('marker = "%s"' % r[1]) not in s, r[1]
        before = s.count("\t{ marker = ")
        s = sub(s, RESTOCK, NEW_ENTRIES + RESTOCK)
        s = sub(s, HOLD_OLD, HOLD_NEW)
        assert s.count("\t{ marker = ") == before + 9
        open(path, "w", encoding="utf-8", newline="").write(s)
        print(os.path.basename(path), "entries", before, "->", before + 9)
    RT.main()


if __name__ == "__main__":
    main()
