#!/usr/bin/env python3
"""Round 171: the tracker's inventory rows (section 3) follow the round: the 9 closed keys read 'skipped (user decision
2026-11-17: ...)' and the 10 moved keys (plus Potion of Foolhardiness, round 170) name their new family. The
database's section 1.6 compares these statuses with the mod."""
import re

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
CLOSED = {
    "wh_main_item_abilities_earthing_rod": "rule 10, helps only before a friendly spell",
    "wh_dlc03_item_abilities_hagtree_fetish": "rule 10, helps only before a friendly spell",
    "wh_main_lord_abilities_master_of_the_black_arts": "rule 10, helps only before a friendly spell",
    "wh3_main_item_abilities_maw_shard": "rule 10, helps only before a friendly spell",
    "wh3_dlc27_item_abilities_power_familiar": "rule 10, helps only before a friendly spell",
    "wh3_dlc24_character_abilities_watched_by_the_watcher": "close (no actuation)",
    "wh_main_item_abilities_sceptre_of_stability": "no read against enemy magic",
    "wh3_main_character_abilities_locus_of_abjuration": "no read against enemy magic",
    "wh2_dlc12_lord_abilities_focus_instincts": "no read of a rampaging unit",
}
MOVED = {
    "wh_dlc05_item_abilities_horn_of_the_wild_hunt": "army_charge",
    "wh3_main_character_abilities_ursuns_roar": "aura_charge",
    "wh_main_character_abilities_red_fury": "self_or_ally_charge",
    "wh_main_character_abilities_waaagh": "army_charge",
    "wh3_main_item_abilities_the_rock_of_inevitability": "slow_aura",
    "wh2_dlc13_weapon_abilities_wissenland_runefang": "slow_aura",
    "wh2_main_spell_bound_black_staff": "winds_low",
    "wh_main_item_abilities_forbidden_rod": "winds_low",
    "wh_main_item_abilities_wand_of_jet": "when_ready",
    "wh3_dlc25_item_abilities_necrotic_phylactry": "contact_melee",
    "wh_main_item_abilities_potion_of_foolhardiness": "charge_or_wavering",
}
s = open(P, encoding="utf-8", newline="").read()
done = {}
for key, why in list(CLOSED.items()) + [(k, None) for k in MOVED]:
    pat = re.compile(r"(\n\| [^|\n]*`%s` \| )`implemented \([^`]*\)`( \|)" % re.escape(key))
    hits = pat.findall(s)
    assert len(hits) == 1, (key, len(hits))
    if why is not None:
        new = "`skipped (user decision 2026-11-17: closed, %s)`" % why
    else:
        new = "`implemented (%s, round %s)`" % (MOVED[key], "170" if "foolhardiness" in key else "171")
    s = pat.sub(lambda m: m.group(1) + new + m.group(2), s)
    done[key] = new
open(P, "w", encoding="utf-8", newline="").write(s)
print(len(done), "tracker rows updated")
