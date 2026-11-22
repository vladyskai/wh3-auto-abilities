#!/usr/bin/env python3
"""Round 204: the tracker (Tidecall, Wind Blast, section 10.81), CLAUDE.md and open point 25."""
import re

ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"
MOVED = ["wh2_dlc11_spell_bound_tidecall", "wh2_dlc11_spell_bound_wind_blast"]
STATUS = "`implemented (standing target, the wave path with the most enemy value: enemy_wave, round 204)`"
PROPOSAL = ("When armed and standing still, casts its wave down the path with the most enemy value among the standing "
            "enemies in range, with at most 5 of our soldiers under the wave (single entities not counted).")
NOTE = (' · **round 204 (2026-11-22):** user "please implement for tight call and wind blast. The slow effect is irrelevant '
        'in this case." Earlier ruling (round 164): "Charge, clear path".')
LOG = """
### 10.81 Round 204 - an exact wave needs no safety distance (2026-11-22)

**Field (user, 2026-11-22):** the Engineer with two Miners units against three Skeleton units, "plenty of targets here,
still not firing". Round 203's free aim tested paths through the enemy's centre only. An enemy in melee with ours has its
centre 6 to 10 m from our unit, inside the 16 m distance, so no heading could pass (replay: 0 of 21 snapshots, and 0 of
25 in the Zombie battle).

**Ruling (user, 2026-11-22):** "I think the safety makes no sense for this ability. Look, the safety was meant for
abilities. That have a deviation from their path. But this ability's path is deterministic. You know exactly where it's
going to land. So why do we need a safety check? We only need to know that in the path of the ability, there is very
little of our units. Or should I say very little of our soldiers. And in this case, we should ignore single entities
because the damage to our single entities would be not relevant. Also, please implement for tight call and wind blast.
The slow effect is irrelevant in this case." Round document `docs\\WH3_round204_exact_wave.md`.

**Change:** a wave whose table row has no sideways drift is EXACT (27 keys). Its friendly test: at most
`FOURTH.WAVE_OWN_MAX` (5) of our soldiers under the wave, our single entities and the caster not counted. Its value: the
enemy value under the wave. Every heading is also tested moved 6, 12 and 18 m to either side. The order always goes out
on the ground at the path's start. The search runs once per second per caster and ability. The 5 drifting waves keep the
round-162 distance. Tidecall and Wind Blast moved from enemy_wave_charge (now empty) to enemy_wave. Roster unchanged:
982 entries / 1,035 keys.

**Proof:** harness 202 full suite **8,305 checks / 0 failures**. RED on the round-203 snapshot: no order in the melee
world, no order with one of our Heroes inside the enemy, no Tidecall on a standing enemy. Workbook v81. Not seen in game
yet.
"""


def one(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


def tracker():
    p = ROOT + "docs\\WH3_ability_tracker.md"
    s = open(p, encoding="utf-8", newline="").read()
    assert "### 10.81 Round 204" not in s
    lines = s.split("\n")
    hits = {k: 0 for k in MOVED}
    for i, l in enumerate(lines):
        if not l.startswith("| "):
            continue
        m = re.match(r"\| [^|]*`([^`]+)` \|", l)
        if not m or m.group(1) not in hits:
            continue
        c = l.split(" | ")
        assert c[1].startswith("`implemented (charging enemy"), l[:160]
        c[1], c[3] = STATUS, PROPOSAL
        row = " | ".join(c)
        assert row.endswith(" |"), row[-40:]
        lines[i] = row[:-2] + NOTE + " |"
        hits[m.group(1)] += 1
    assert all(v == 1 for v in hits.values()), hits
    open(p, "w", encoding="utf-8", newline="").write("\n".join(lines).rstrip("\n") + "\n" + LOG)
    print("tracker updated", hits)


def claude():
    p = ROOT + "CLAUDE.md"
    s = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    s = one(s, "- Installed build: md5 `14e1d8cf6e1882279556c0a1bf80e2ee`, 1,635,145 bytes" + nl
            + "  (round 203, 2026-11-22: free aim for the 30 placed straight waves).",
            "- Installed build: md5 `11a01a69e4c513e1c4d444dab5f7606a`, 1,639,185 bytes" + nl
            + "  (round 204, 2026-11-22: exact waves count our soldiers under the wave, Tidecall and Wind Blast moved).")
    s = one(s, "20261122_freeaim_harness201/build_and_install203.py", "20261122_exactwave_harness202/build_and_install204.py")
    s = one(s, "(harness201: 8,301 checks; it takes about 2 minutes)", "(harness202: 8,305 checks; it takes about 2 minutes)")
    s = one(s, "WH3_abilities_master_v80_2026-11-22.xlsx` | the current master spreadsheet (versioned, newest wins). Built by "
            "`tools\\make_xlsx_v80.py`, verified by `tools\\verify_xlsx_v80.py <v79 md5> <pack md5>` (v80 = v79 + ",
            "WH3_abilities_master_v81_2026-11-22.xlsx` | the current master spreadsheet (versioned, newest wins). Built by "
            "`tools\\make_xlsx_v81.py`, verified by `tools\\verify_xlsx_v81.py <v80 md5> <pack md5>` (v81 = v80 + the EXACT "
            "sentence on 27 wave rows, Tidecall and Wind Blast on enemy_wave. v80 = v79 + ")
    a = "- ROUND 203 (2026-11-22, \"A: but be careful ... check individually\" + \"All 30 placed\";"
    note = [
        "- ROUND 204 (2026-11-22; `docs\\WH3_round204_exact_wave.md`). USER RULING: \"the safety was meant for abilities that",
        "  have a deviation from their path. But this ability's path is deterministic ... We only need to know that in the",
        "  path of the ability, there is very little of our ... soldiers. And in this case, we should ignore single entities",
        "  ... Also, please implement for tight call and wind blast. The slow effect is irrelevant in this case.\" BUILT: a",
        "  wave whose WW row has buf = 0 is EXACT (FOURTH.ww_exact, 27 keys): FOURTH.ww_line_value counts OUR SOLDIERS under",
        "  the wave (FOURTH.wave_cover: a grid over the unit's rectangle, a single entity = its centre) against",
        "  FOURTH.WAVE_OWN_MAX = 5 (Claude's reading of 'very little': ASK if it should move), skips our single entities and",
        "  the caster, and values a path by the enemy value UNDER the wave. FOURTH.FREE_AIM_SHIFTS = 0, +-6, +-12, +-18 m",
        "  sideways per heading (24 x 7 paths per enemy). An exact wave is ALWAYS an aimed ground order (the caster's line",
        "  too, aim.legacy). The search runs once per FOURTH.FREE_AIM_EVERY = 4 polls per caster and ability",
        "  (FOURTH.aim_next[unit id][key]: the mod's pins ban joined '|' keys). The 5 DRIFTING waves (Wrath of Manann, Wind of",
        "  Death, Burning Head x2, Black Horror) keep the round-162 distance and round 203's through-the-centre aim.",
        "  Tidecall and Wind Blast moved to enemy_wave (32 entries; enemy_wave_charge is EMPTY, code kept; 140 families in",
        "  use). Harness 202: run_h201 stays in the file UNCALLED (superseded). LESSON: round 203's harness world put the",
        "  friend 30 m in front of the enemy, not in melee, so it passed for a situation the user never had. Build test",
        "  worlds from the MAP rows of the battle that showed the problem. No minimum of enemy soldiers was built (the user",
        "  did not rule on Claude's proposed 60). NOT SEEN IN GAME. Next battle from byte 1,027,314,867.",
    ]
    s = one(s, a, nl.join(note) + nl + a)
    open(p, "w", encoding="utf-8", newline="").write(s)
    p = ROOT + "docs\\WH3_open_points.md"
    s = open(p, encoding="utf-8", newline="").read()
    a = "| BUILT (round 203, 2026-11-22): waiting for a battle | ROUND 203:"
    s = one(s, a, "| BUILT (round 204, 2026-11-22): waiting for a battle | ROUND 204 (`docs\\WH3_round204_exact_wave.md`): an "
            "exact wave has no safety distance, at most 5 of our soldiers under it, our single entities not counted, sideways "
            "shifts, Tidecall and Wind Blast included. Open: the limit of 5 is Claude's reading of 'very little', and no "
            "minimum of enemy soldiers was built. ROUND 203:")
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("CLAUDE.md and open points updated")


if __name__ == "__main__":
    tracker()
    claude()
