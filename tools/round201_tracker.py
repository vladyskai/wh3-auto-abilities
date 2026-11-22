#!/usr/bin/env python3
"""Round 201: the tracker (docs/WH3_ability_tracker.md).
- the five Master Runes (source_type rune): status rejected (user 2026-11-22), removed from the mod;
- Endless Whirlwind of Death and its Upgraded twin: implemented (melee_unwavering, round 201), the old rejection quoted;
- section 10.78, the round log."""
import re

TRK = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
RUNES = ["wh2_dlc17_rune_abilities_master_rune_of_breaking", "wh_dlc06_rune_abilities_master_rune_of_negation",
         "wh2_dlc17_rune_abilities_master_rune_of_slowness", "wh2_dlc17_rune_abilities_master_rune_of_speed",
         "wh_dlc06_rune_abilities_master_rune_of_oath_and_steel"]
RUNE_STATUS = ('`rejected (user 2026-11-22: "do it" on "remove the five Master Runes the game marks as runes"; a rune on '
               'the right-hand spell bar, Master Rune of Slowness fired by itself in his Dwarf battle)`')
RUNE_PROPOSAL = "Not automated (user decision 2026-11-22): removed from the mod in round 201."
EW = ["wh3_dlc25_unit_abilities_whirlwind_of_death_ror", "wh3_dlc25_unit_abilities_whirlwind_of_death_ror_upgraded"]
EW_STATUS = "`implemented (melee_unwavering, round 201)`"
EW_PROPOSAL = "Fires in melee unless wavering: cast on self (the same trigger as Whirlwind of Death)."
EW_NOTE = (' · **round 201 (2026-11-22):** user "do it" on "the same trigger as Whirlwind of Death". Earlier decision: '
           "rejected (friendly fire), questionnaire §2 #56. The data shows the vortex does not hit allies "
           "(battle_vortexs.affects_allies false, the vortexes of Whirlwind of Death).")
LOG = """
### 10.78 Round 201 - the Master Runes leave, Endless Whirlwind of Death joins (2026-11-22)

**Field (user, 2026-11-22, a Dwarf battle on the RELEASE build, no log):** "Master Rune of Slowness, ability on the right
side, fired by itself" and "Endless Whirlwind has no automatization".

**Rulings (user, 2026-11-22):** "do it" on "remove the five Master Runes the game marks as runes"; "do it" on "the same
trigger as Whirlwind of Death". Round document `docs\\WH3_round201_master_runes.md`.

**Cause:** the five Master Runes (source_type rune) had stayed in ABILITIES after round 192 removed the five plain runes
(a question to the user that was never answered). The game shows them on the right-hand bar, where the mod gives no M/A
letter (rule 12), but their trigger families start armed and a cast needs no letter.

**Change:** removed Master Rune of Breaking, Negation, Slowness, Speed, Oath & Steel (entries and hold rows). NEW entries
Endless Whirlwind of Death and Endless Whirlwind of Death Upgraded on melee_unwavering. The build refuses any key the game
marks source_type = rune (a permanent gate) and checks the two vortexes do not hit allies. Master Rune of Flight and of
Immolation (source_type active) stay. Roster: 982 entries / 1,035 keys / 141 families.

**Proof:** harness 199 full suite **8,245 checks / 0 failures**, twice. RED on the pre-201 snapshot: each of four Master
Runes fires once by itself with the default states, Endless Whirlwind never fires. Workbook v79 (1,802 rows: 687 excluded,
1,115 included, 1,035 implemented, 80 decided by the user, 0 open). Not seen in game yet.
"""


def main():
    s = open(TRK, encoding="utf-8").read()
    assert "### 10.78 Round 201" not in s
    lines = s.split("\n")
    hits = {k: 0 for k in RUNES + EW}
    for i, l in enumerate(lines):
        if not l.startswith("| "):
            continue
        m = re.match(r"\| [^|]*`([^`]+)` \|", l)
        if not m or m.group(1) not in hits:
            continue
        k = m.group(1)
        c = l.split(" | ")
        assert len(c) >= 5, l[:120]
        if k in RUNES:
            assert c[1].startswith("`implemented"), l[:200]
            c[1], c[3] = RUNE_STATUS, RUNE_PROPOSAL
            lines[i] = " | ".join(c)
        else:
            assert c[1] == "rejected (friendly fire)", l[:200]
            c[1], c[3] = EW_STATUS, EW_PROPOSAL
            row = " | ".join(c)
            assert row.endswith(" |"), row[-40:]
            lines[i] = row[:-2] + EW_NOTE + " |"
        hits[k] += 1
    assert all(v == 1 for v in hits.values()), hits
    s = "\n".join(lines).rstrip("\n") + "\n" + LOG
    open(TRK, "w", encoding="utf-8", newline="").write(s)
    print("tracker updated:", hits)


if __name__ == "__main__":
    main()
