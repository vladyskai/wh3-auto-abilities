#!/usr/bin/env python3
"""Round 192: the tracker (docs/WH3_ability_tracker.md).
- the five spell-bar runes: status rejected (user 2026-11-21), removed from the mod;
- Shock Collar and Remouldered: the Moulder rule in their notes;
- two new rows at the end of table 3a: Grombrindal Has No Fear (implemented) and Scry-Orb (open: needs a trigger ruling);
- section 10.70, the round log."""
import re

TRK = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
RUNES = ["wh2_dlc17_rune_abilities_rune_of_breaking", "wh_main_rune_abilities_rune_of_negation",
         "wh2_dlc17_rune_abilities_rune_of_slowness", "wh2_dlc17_rune_abilities_rune_of_speed",
         "wh_main_rune_abilities_rune_of_oath_and_steel"]
RUNE_STATUS = ('`rejected (user 2026-11-21: "They should not be in the mod. Just mark them as closed because they are on '
               'the right ability wheel."; a rune on the right-hand spell bar)`')
RUNE_PROPOSAL = "Not automated (user decision 2026-11-21): removed from the mod in round 192."
MOULDER = ["wh2_dlc16_hero_abilities_shock_collar", "wh2_dlc16_lord_abilities_remouldered"]
NEW_ROWS = (
    "| Grombrindal Has No Fear `wh_pro01_lord_passive_grombrindal_has_no_fear` | `implemented (melee_or_wavering_aura, "
    "round 192)` | aura | Fires when the caster or a friendly unit within 38 m (70% of the 55 m aura) is in melee or "
    "wavering: cast centred on the caster. | cd 120s · 24s · self + allies · ×1 use · +24 melee defence, Unbreakable · "
    "source_type passive (added in round 192) · user ruling 2026-11-21: 'at least one ally (caster included) in range in "
    "melee or wavering' |\n"
    "| Scry-Orb `wh3_dlc29_item_abilities_scry_orb` | `open (round 192: needs a trigger ruling)` | self | Proposal "
    "2026-11-21: fire when ready (when_ready), like the 21 pure winds abilities. | cd 120s · 32s · self · ×3 uses · Winds "
    "of Magic regeneration x1.6, ability recharge -30 s · source_type passive (added in round 192) |\n")
LOG = """
### 10.70 Round 192 - the closing check, the Moulder rule, Grombrindal Has No Fear, the spell-bar runes (2026-11-21)

**Rulings (user, 2026-11-21):** "try to implement using is_moving_fast()" (open point 7, option A); Moulder set "do it";
Grombrindal Has No Fear 'implement "at least one ally (caster included) in range in melee or wavering"'; Scry-Orb and
Grombrindal Has No Fear rows "then add"; the five runes "They should not be in the mod. Just mark them as closed because
they are on the right ability wheel."; Transfix / Ghostly Howl "keep it then"; Eye / Wrath of the Storm "close the item
with no change". Round document `docs\\WH3_round192_closing.md`.

**Change:** `FOURTH.fast_enemy_near` needs the enemy RUNNING (is_moving_fast) and CLOSING (its gap to our nearest unit
shrinks at least 3 m/s over at least 1 s; `FOURTH.fast_closing`): enemy_fast_near_ally and the fast arms of
enemy_melee_or_fast, enemy_fast_or_melee, enemy_fast_fire_melee, enemy_wave_charge, slow_army. Shock Collar and
Remouldered take only a Clan Moulder monster (GENERATED `FOURTH.MOULDER_TEXT`, 28 units; code M; Remouldered's monster
list yields to the rule). NEW entry Grombrindal Has No Fear on melee_or_wavering_aura (55 m aura -> 38 m). Removed: Rune of
Breaking, Negation, Slowness, Speed, Oath & Steel. Roster: 984 entries / 1,037 keys / 141 families.

**Proof:** harness 191 full suite **8,010 checks / 0 failures**, twice identical; RED on the pre-192 snapshot (fires on an
enemy riding past, walking or running away; Shock Collar on Skeletons; the rune fires). Pack md5
`1a12ea1543904e6ae0fc01799d3a905d`. Workbook v74 (1,802 rows; Scry-Orb open). Not seen in game yet.
"""


def main():
    s = open(TRK, encoding="utf-8").read()
    assert "### 10.70 Round 192" not in s
    lines = s.split("\n")
    hits = {k: 0 for k in RUNES + MOULDER}
    for i, l in enumerate(lines):
        if not l.startswith("| "):
            continue
        m = re.match(r"\| [^|]*`([^`]+)` \|", l)
        if not m or m.group(1) not in hits:
            continue
        k = m.group(1)
        c = l.split(" | ")
        if k in RUNES:
            if not c[1].startswith("`implemented"):
                continue
            c[1] = RUNE_STATUS
            c[3] = RUNE_PROPOSAL
        else:
            if not c[1].startswith("`implemented"):
                continue
            c[-1] = c[-1].rstrip().rstrip("|").rstrip() + " · **round 192:** Clan Moulder monsters only (the game's rule) |"
        lines[i] = " | ".join(c)
        hits[k] += 1
    assert all(v == 1 for v in hits.values()), hits
    s = "\n".join(lines)
    i = s.index("\n### 3b.")
    j = s.rindex("\n|", 0, i)
    j = s.index("\n", j + 1) + 1
    s = s[:j] + NEW_ROWS + s[j:]
    s = s.rstrip("\n") + "\n" + LOG
    open(TRK, "w", encoding="utf-8", newline="\n").write(s)
    print("tracker: 5 runes closed, 2 Moulder notes, 2 new rows, section 10.70")


if __name__ == "__main__":
    main()
