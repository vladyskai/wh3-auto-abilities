# -*- coding: utf-8 -*-
"""Round-101 tracker, part B: the TEN boss-only keys that never shipped."""
import io

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
s = io.open(P, "rb").read().decode("utf-8")

ROWS = [
    ("wh2_dlc10_quest_abilities_fiery_head", "wh2_dlc10_def_mon_war_hydra_boss"),
    ("wh2_dlc10_quest_abilities_regenerating_head", "wh2_dlc10_def_mon_war_hydra_boss"),
    ("wh_dlc08_quest_abilities_howling_winter", "wh_dlc08_nor_mon_frost_wyrm_boss"),
    ("wh_dlc08_quest_abilities_master_of_souls", "wh_dlc08_vmp_mon_terrorgheist_boss"),
    ("wh_dlc04_quest_abilities_servant_of_nagash", "wh_dlc04_vmp_cha_strigoi_ghoul_king_0_boss"),
    ("wh3_dlc27_qb_unit_abilities_dissolving_bone", "wh3_dlc27_tmb_mon_carrion_boss"),
    ("wh3_dlc27_qb_unit_abilities_terrible_malice", "wh3_dlc27_sla_mon_preyton_boss"),
    ("wh3_dlc27_qb_unit_abilities_copious_phlegm", "wh3_dlc27_nur_mon_toad_dragon_boss"),
    ("wh2_dlc10_quest_abilities_magic_fiery_convocation", "wh2_dlc10_nor_mon_phoenix_flamespyre_boss"),
    ("wh2_dlc10_quest_abilities_flame_storm", "wh2_dlc10_nor_mon_phoenix_flamespyre_boss"),
]

lines = s.split("\n")
done = []
for i, ln in enumerate(lines):
    if not ln.startswith("| "):
        continue
    for key, unit in ROWS:
        if ("`%s`" % key) in ln:
            parts = ln.split("|")
            if len(parts) < 6:
                continue
            st = parts[2]
            if "`" not in st:
                continue
            parts[2] = " `excluded (not in wheel: boss-only unit)` "
            note = parts[5].rstrip()
            if "round 101" not in note:
                note = (note + " · **round 101 (2026-10-17):** boss-only - its ONLY grant path is `%s` "
                        "(land_abil.tsv), a quest-battle boss variant; it never shipped in the mod. See §10.3."
                        % unit)
            parts[5] = " " + note + " "
            lines[i] = "|".join(parts)
            done.append(key)
            break

s = "\n".join(lines)
io.open(P, "wb").write(s.encode("utf-8"))
print("rows updated:", len(done))
for k in done:
    print("  ", k)
missing = [k for k, _ in ROWS if k not in done]
print("MISSING:", missing)
