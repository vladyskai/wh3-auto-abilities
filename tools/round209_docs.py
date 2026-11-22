#!/usr/bin/env python3
"""Round 209: the tracker (the two Loons, Lamprey's Bite, section 10.86), CLAUDE.md, the open points, the review doc and
the round document."""
import re

ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"
TEST_MD5 = "c7835b1a8ef6c3e61dc750f588673aed"
REL_MD5 = "3457ac1b985901ba088c56eade838a8e"
LOONS = ["wh_main_unit_abilities_spinning_loons", "wh_dlc06_unit_abilities_the_loons_of_eight_peaks"]
LAMP = "wh3_dlc24_unit_abilities_lampreys_bite"
LOON_PROPOSAL = (" Since round 209 it also needs none of our other units within 98 m of the caster (the fanatics wander "
                 "84 m and hit our units too).")
LOON_NOTE = (' · **round 209 (2026-11-22):** user, after checking them in battle: "They are really prone for friendly '
             'fire. We need a friendly fire check, yes."')
LAMP_STATUS = "`implemented (standing target, the wave path with the most enemy value: enemy_wave, round 209)`"
LAMP_PROPOSAL = ("When armed and standing still, casts its short wave (24 m long, 0.1 m wide growing to 14.1 m) down the "
                 "path with the most enemy soldiers among the standing enemies within 80 m, with at most 5 of our soldiers "
                 "under it (single entities not counted). An aimed ground order.")
LAMP_NOTE = (' · **round 209 (2026-11-22):** user "fix please" on the code review\'s finding that it was treated as a 25 m '
             'disc it never becomes. Before: enemy_wander.')
LOG = """
### 10.86 Round 209 - the replies to the afternoon code review (2026-11-22)

**Rulings (user, 2026-11-22, row by row on the review's findings):** the Loons: "I checked them in battle now. They are
really prone for friendly fire. We need a friendly fire check, yes." The five caster-front breaths and Lamprey's Bite:
"fix please". The player's own cast replaced by the mod: "Fixable?". The three machinery bugs: "fixable?". The area
blasts counting walkers: "leave for now, we might improve on that later". Chain Lightning: "leave it for now". The button
that arms everything also arms the risky abilities: "that's okay". Round document
`docs\\WH3_round209_review_replies.md`.

**Change:**

- Spinning Loons and The Loons of Eight Peaks keep their trigger and also need none of our other units within 98 m of
  the caster (entry field `ring_clear`, GENERATED `FOURTH.RING_TEXT`: radius 4 m + simulated 95% reach 84 m, + 10 m).
- Lamprey's Bite moved from enemy_wander to enemy_wave: an exact, growing, ground-only wave (0.1 m to 14.1 m over 24 m).
- The player's own cast: the game's "Special Ability" report that the mod did not order arms the per-unit cast window on
  every selected unit (wind-up + 2 s for a key of ours, 5 s for an unknown key, nothing for an instant key of ours).
- The poll guards each unit's reads and each ability step: an error on one unit no longer ends the poll.
- NOT built: the five caster-front breaths. Where such a breath starts is not known, and the three readings of the
  table disagree. A one-minute hand test by the user decides it.

Roster unchanged: 982 entries / 1,035 keys. 33 enemy_wave entries, 41 enemy_wander.

**Proof:** harness 207 full suite **8,412 checks / 0 failures**. RED on the pre-round snapshot: the Loons fire with one
of our units 50 m away, Lamprey's Bite never fires on 160 standing Zombies, the Whirlwind fires at once after the
player's own cast, an error on the first unit ends the poll. The cast trace of the whole suite (2,155 worlds, 1,702
casts) matches between the test build and the release build apart from the 3 probe casts. Workbook v83. Not seen in game.
"""
ROUND_DOC = """# Round 209: the replies to the afternoon code review (2026-11-22)

## 1. The rulings

The user answered the review's findings one by one.

| Finding | The user's reply | What happened |
|---|---|---|
| Spinning Loons, The Loons of Eight Peaks (no friendly test) | "I checked them in battle now. They are really prone for friendly fire. We need a friendly fire check, yes." | BUILT |
| The mod can cancel a cast the player just ordered | "Fixable?" | BUILT |
| Slow units can never be seen charging | "need more details" | Explained in the chat, a ruling is still needed |
| The five caster-front breaths and Lamprey's Bite | "fix please" | Lamprey's Bite BUILT. The five breaths NOT built: a hand test is needed first |
| The area blasts count walking enemies | "leave for now, we might improve on that later" | Left |
| Three machinery bugs | "fixable?" | One BUILT (one bad unit). Two explained, each has a cost |
| The button that arms everything also arms the risky abilities | "that's okay" | Closed |
| "At most 5 of our soldiers" is coarser than it reads | "I don't understand" | Explained in the chat |
| Chain Lightning's explosion | "leave it for now" | Left |

## 2. What changed in battle

1. **The Loons.** Before: they fired at the nearest enemy in melee within 17 m, whatever stood around. Now the same,
   and also none of our other units within 98 m of the Night Goblins. The 98 m is the fanatics' own numbers from the
   game's table: they are 4 m wide, travel 84 m in 12 s and turn at random, plus the usual 10 m. Da Boss' Loons has had
   the same rule since round 164. Our expendable and cheap units do not block it. In a normal battle line this is rarely
   true, so on A the Loons will mostly wait. The letter's hover text says so: "Fires at the nearest enemy in melee when
   none of our other units is near".
2. **Lamprey's Bite.** Before: the mod thought it was a 25 m disc and wanted 415 enemy soldiers inside it, so it almost
   never fired, and when it did the order pointed north. In the game's table it is a short wave: 0.1 m wide at its
   start, growing while it rolls 24 m, 14.1 m wide at the end. Now it is aimed like the Fiery Ring of Thori: the mod
   tries 24 directions and 7 sideways shifts per standing enemy and orders the path with the most enemy soldiers under
   it, with at most 5 of ours.
3. **Your own cast.** The game tells the mod about every ability order, with the ability's key. The mod now remembers
   the orders it gave itself. An order it did not give is yours. Every unit you have selected then stops receiving
   automatic abilities until your cast is out: its wind-up plus 2 s when the mod knows the ability, 5 s when it does not
   (a spell), nothing when it is one of the mod's instant abilities.
4. **One broken unit.** Before: if reading one unit raised an error, every unit after it in the list was skipped for
   that quarter second. Now each unit is read inside its own guard.

## 3. Proof

- RED control (the pre-round snapshot, `docs\\backups\\round209\\`): LN1 and LN3 fire with one of our units 50 m away.
  LB1 never fires on 160 standing Zombies. PC1 and PC5 fire at once after the player's own cast. UE1: no cast after the
  first unit's error.
- GREEN: harness 207, full suite, 8,412 checks, 0 failures (`mod_source\\releases\\20261122_replies_harness207\\h207_run1.txt`).
- The cast trace of the whole suite: 2,155 worlds, 1,702 casts, the test build and the release build differ only in the
  3 casts of the console probe (expected).
- Test pack md5 `%(test)s` (1,649,264 bytes), release pack md5 `%(rel)s`. Workbook v83.

## 4. Rebased pins (old value, new value, why)

| Where | Old | New | Why |
|---|---|---|---|
| harness 114, "the per-ability walk still BREAKS on 'gone'" | the word `break` within 80 characters of the answer | `return "gone"` there, and the caller's `break` after the guard | each ability step runs in a guard, the break moved one line out |
| harness 160 (0zz9) | 32 waves, 42 wanderers | 33, 41 | Lamprey's Bite moved |
| harness 161 (0zz10) | 42 wanderers | 41 | the same |
| harness 162 (0zz11) | 32 waves, 42 wanderers | 33, 41 | the same |
| harness 202 (0zz50) | 32 waves | 33 | the same |
| builder, round 162 gate | 32 / 42 | 33 / 41 | the same |
| builder, round 203 gate | every enemy_wave key target_near_edge, 32 entries | also target_centre for a ground-only key, 33 entries | Lamprey's Bite launches from the target centre and has only the ground form |
| builder, round 204 gate | 27 exact waves | 28 | Lamprey's Bite |
| builder, round 205 gate | 19 growing waves | 20 | Lamprey's Bite |
| builder, round 198 gate | 5 uses of the waiting slot | 6 | the player's-cast window clears it too |

## 5. What is not verified

- Nothing of this round has been seen in a battle.
- Lamprey's Bite: that a ground order starts the wave at the point and sends it along the bearing is seen in game for
  the Fiery Ring of Thori only.
- The player's own cast: the three archived battles show the game's report arriving for the mod's own orders, a moment
  after each. That it also arrives for a hand cast and for a spell is the game's own documentation, not yet a log line
  of ours. The next battle's log shows it: the line "the player's own cast of".
- The 5 s for an unknown key is Claude's number. 37 abilities in the game wind up longer than 5 s.
- When several units are selected and one casts, all of them wait.

## 6. Still waiting

- The five caster-front breaths (Shatter, Pestilent Breath x2, Fishy Breath, Skabscrath): a hand test of where the
  breath starts.
- Slow units and the charge test: a ruling.
- Phantom casts after the last use, and the transformed unit: the user's go-ahead, each has a cost (see the chat).
"""


def one(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


def tracker():
    p = ROOT + "docs\\WH3_ability_tracker.md"
    s = open(p, encoding="utf-8", newline="").read()
    assert "### 10.86 Round 209" not in s
    lines = s.split("\n")
    hits = {k: 0 for k in LOONS + [LAMP]}
    for i, l in enumerate(lines):
        if not l.startswith("| "):
            continue
        m = re.match(r"\| [^|]*`([^`]+)` \|", l)
        if not m or m.group(1) not in hits:
            continue
        c = l.split(" | ")
        if m.group(1) == LAMP:
            assert c[1].startswith("`implemented (blast on a standing blob: enemy_wander)"), l[:160]
            c[1], c[3] = LAMP_STATUS, LAMP_PROPOSAL
            note = LAMP_NOTE
        else:
            assert c[1].startswith("`implemented (fighting enemy, on its ground: enemy_ground_melee)"), l[:160]
            c[3] = c[3] + LOON_PROPOSAL
            note = LOON_NOTE
        row = " | ".join(c)
        assert row.endswith(" |"), row[-40:]
        lines[i] = row[:-2] + note + " |"
        hits[m.group(1)] += 1
    assert all(v == 1 for v in hits.values()), hits
    open(p, "w", encoding="utf-8", newline="").write("\n".join(lines).rstrip("\n") + "\n" + LOG)
    print("tracker updated", hits)


def claude():
    p = ROOT + "CLAUDE.md"
    s = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    s = one(s, "- Installed build: md5 `1d2c5abb71b2267b0ce6ce8ceb95d5ba`, 1,643,517 bytes" + nl
            + "  (round 208, 2026-11-22, tuning: the free-aim search is skipped while not castable and spread by unit id).",
            "- Installed build: md5 `" + TEST_MD5 + "`, 1,649,264 bytes" + nl
            + "  (round 209, 2026-11-22: the Loons' friendly ring, Lamprey's Bite as a wave, the player's own cast protected).")
    s = one(s, "20261122_searchcost_harness206/build_and_install208.py", "20261122_replies_harness207/build_and_install209.py")
    s = one(s, "(harness206: 8,365 checks; it takes about 2 minutes)", "(harness207: 8,412 checks; it takes about 2 minutes)")
    s = one(s, "WH3_abilities_master_v82_2026-11-22.xlsx` | the current master spreadsheet (versioned, newest wins). Built by "
            "`tools\\make_xlsx_v82.py`, verified by `tools\\verify_xlsx_v82.py <v81 md5> <pack md5>` (v82 = v81 + ",
            "WH3_abilities_master_v83_2026-11-22.xlsx` | the current master spreadsheet (versioned, newest wins). Built by "
            "`tools\\make_xlsx_v83.py`, verified by `tools\\verify_xlsx_v83.py <v82 md5> <pack md5>` (v83 = v82 + the RING "
            "sentence on the two Loons rows, Lamprey's Bite on enemy_wave, 3 cards. v82 = v81 + ")
    a = "- ROUND 206 (2026-11-22, TUNING, INSTALLED: test pack md5 b4db5260..., release pack md5 d74e4685...). FIELD"
    note = [
        "- ROUND 209 (2026-11-22, the user's row-by-row replies to the afternoon review; `docs\\WH3_round209_review_replies.md`).",
        "  INSTALLED: test pack md5 c7835b1a..., release pack md5 3457ac1b..., harness 207: 8,412 / 0, the cast trace matches",
        "  apart from the 3 probe casts, workbook v83, tracker 10.86. NOT SEEN IN GAME. BUILT: (1) the Loons (\"They are really",
        "  prone for friendly fire. We need a friendly fire check, yes.\"): entry field ring_clear = true on Spinning Loons and",
        "  The Loons of Eight Peaks, FOURTH.ring_wrap at load (the entry's own trigger AND FOURTH.self_clear(unit, reach)),",
        "  GENERATED FOURTH.RING_TEXT (gen_ww_tables.ring_keys / ring_rows / ring_block: 88 = radius 4 + 95% reach 84, need",
        "  98 m), card FOURTH.CARD_TIP_RING. In a normal line they will mostly wait (told to the user). (2) Lamprey's Bite on",
        "  enemy_wave (33 entries, 41 wanderers; 28 exact, 20 growing): gen_ww_tables takes a GROUND-ONLY wave from",
        "  target_centre and caps a wave's radius at what it reaches (14.1 m), gen_wave_cone accepts that radius. (3) THE",
        "  PLAYER'S OWN CAST (review C1): FOURTH.note_own_order(ready_key) at every 'fired', FOURTH.player_cast(key) from the",
        "  'Special Ability' command callback (the annotated copy now registers it too): a report with no pending own order",
        "  arms cast_gate.unit_until on every SELECTED unit (wind-up + 2 s, FOURTH.PLAYER_CAST_HOLD_S = 5 for an unknown",
        "  key, nothing for an instant key of ours). ENGINE FACT (3 archived battles): the command callback fires for the",
        "  mod's OWN orders too, once per accepted order, a moment AFTER the order, with the key. Grep the next battle for",
        "  \"the player's own cast of\". (4) Review C4: the poll runs each unit's reads and each ability step in a pcall",
        "  (FOURTH.unit_error, 'UNIT ERROR #'). The ability loop's ipairs MUST stay in poll_body: harness 66's POLL_ITERS",
        "  probe counts ipairs calls whose caller is the poll body (a closure around the whole unit read 0). NOT BUILT, WAITING:",
        "  the 5 caster-front breaths (B1): launch_source activator_front with launch_source_offset 24 / 36 has three",
        "  readings (starts at the caster, 24 m ahead, or 24 m behind the front) and no model is safe under all three: the",
        "  user must cast one by hand and say where the fire starts and how far it reaches. E1 (slow units never 'charging'):",
        "  explained, a ruling is needed. C3 (phantom casts): a use counter would stop early when the game adds uses or",
        "  swallows a cast. C2 (transformed unit): the re-scan on an identity change for units that own abilities, not",
        "  testable without knowing whether a transformed unit keeps its id. Closed by the user: A2 Chain Lightning and",
        "  B3/B4 walkers (\"leave for now\"), C6 the arm-everything button (\"that's okay\"). Heredocs broke three Python",
        "  edits AGAIN this round. Next battle from byte 1,067,747,316 (re-measure).",
    ]
    s = one(s, a, nl.join(note) + nl + a)
    open(p, "w", encoding="utf-8", newline="").write(s)
    p = ROOT + "docs\\WH3_open_points.md"
    s = open(p, encoding="utf-8", newline="").read()
    a = "| 25 | **Free aim for waves and cones**"
    row = ("| 26 | **The afternoon code review of 2026-11-22** (`docs\\WH3_code_review_2026-11-22_afternoon.md`). | PARTLY "
           "BUILT (round 209): waiting for a battle and for two answers | Built: the Loons' friendly check, Lamprey's Bite "
           "as a wave, the player's own cast protected, one bad unit. WAITING FOR THE USER: (a) a hand cast of one "
           "caster-front breath (Shatter, Pestilent Breath, Fishy Breath or Skabscrath): where does the fire start and how "
           "far does it reach. (b) a ruling on slow units and the charge test. (c) a go-ahead on the use counter and the "
           "transformed unit. Left by the user: the area blasts counting walkers, Chain Lightning. |\n")
    i = s.index(a)
    j = s.index("\n", i) + 1
    s = s[:j] + row + s[j:]
    open(p, "w", encoding="utf-8", newline="").write(s)
    p = ROOT + "docs\\WH3_code_review_2026-11-22_afternoon.md"
    s = open(p, encoding="utf-8", newline="").read()
    s = one(s, "## 2. Findings that need a ruling, ranked\n",
            "## 1b. The user's replies and round 209 (2026-11-22)\n\n"
            "| Finding | Reply | State |\n|---|---|---|\n"
            "| A1 the Loons | \"We need a friendly fire check, yes.\" | BUILT in round 209 (none of our other units within 98 m of the caster) |\n"
            "| A2 Chain Lightning | \"leave it for now\" | left |\n"
            "| B1 the five caster-front breaths | \"fix please\" | NOT built: where the breath starts needs a hand test |\n"
            "| B2 Lamprey's Bite | \"fix please\" | BUILT in round 209 (an aimed wave) |\n"
            "| B3, B4 the area blasts count walkers | \"leave for now, we might improve on that later\" | left |\n"
            "| C1 the player's own cast | \"Fixable?\" | BUILT in round 209 |\n"
            "| C2, C3 | \"fixable?\" | explained, each has a cost, waiting |\n"
            "| C4 one bad unit | \"fixable?\" | BUILT in round 209 |\n"
            "| C6 the button that arms everything | \"that's okay\" | closed |\n"
            "| D the limit of 5 soldiers | \"I don't understand\" | explained in the chat |\n"
            "| E1 slow units | \"need more details\" | explained in the chat, a ruling is needed |\n\n"
            "## 2. Findings that need a ruling, ranked\n")
    open(p, "w", encoding="utf-8", newline="").write(s)
    open(ROOT + "docs\\WH3_round209_review_replies.md", "w", encoding="utf-8", newline="\n").write(
        ROUND_DOC % {"test": TEST_MD5, "rel": REL_MD5})
    print("CLAUDE.md, open points, the review doc and the round document updated")


if __name__ == "__main__":
    tracker()
    claude()
