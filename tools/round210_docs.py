#!/usr/bin/env python3
"""Round 210: the tracker (the two Loons, the five breaths, section 10.87), CLAUDE.md, the open points, the review doc
and the round document."""
import re

ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"
TEST_MD5 = "8760b82d91ec7feaff51eaf39a0f5ea1"
REL_MD5 = "9a1e8f9a812e06c2168157d256e1a9e4"
LOONS = ["wh_main_unit_abilities_spinning_loons", "wh_dlc06_unit_abilities_the_loons_of_eight_peaks"]
CONES = ["wh2_dlc13_character_ability_shatter", "wh2_dlc15_character_abilities_fishy_breathe",
         "wh2_main_mount_bound_pestilent_breath", "wh3_main_spell_bound_pestilent_breath",
         "wh_main_weapon_abilities_skabscrath"]
LOON_STATUS = "`implemented (approaching infantry, a clear path: enemy_wave_charge, round 210)`"
LOON_PROPOSAL = ("When armed and standing, releases the fanatics towards an enemy infantry unit that is coming closer and "
                 "is 15 to 25 m away, when none of our units of more than one man stands in their path (84 m, widening "
                 "from 4 m to 60 m each side). Single entities of ours do not count.")
LOON_NOTE = (' · **round 210 (2026-11-22):** user, after testing round 209: "They are not working as intended ... I would '
             'like to change them completely", then his own rule (standing caster, approaching infantry between 25 and '
             '15 m, cast in that direction, no friendly unit that is not a single entity in the path).')
CONE_NOTE = (' · **round 210 (2026-11-22):** user test "I tested Skarbscrath and it always starts at the caster". The '
             'breath is now tested as a cone from the caster (0.1 m wide at the caster, growing per metre, the path alone '
             'long), with the exact-wave rule: enemy soldiers under it, at most 5 of ours.')
LOG = """
### 10.87 Round 210 - the second replies to the afternoon code review (2026-11-22)

**Rulings (user, 2026-11-22):** the Loons: "They are not working as intended. They are too fire friendly ... I would
like to change them completely ... they could only fire while the caster is standing. And there is a unit that is enemy
unit, infantry enemy unit that is approaching. And it's, let's say, between 25 and 15 meters from the caster unit. And
then you just cast in that direction ... single entities is okay, but any friendly units that are not single entity
should [not] be in the path." The breaths: "I tested Skarbscrath and it always starts at the caster". Empty orders after
the last use: "no". The transformed unit: "just tested (see image), it's true that they never fire". Slow units and the
charge, option B: "okay, do it". The grid of the soldier count: "then leave it". Round document
`docs\\WH3_round210_review_replies2.md`.

**Change:**

- Spinning Loons and The Loons of Eight Peaks moved from enemy_ground_melee to enemy_wave_charge (table kind 8) with
  the user's rule. Round 209's ring left both entries.
- Shatter, Pestilent Breath x2, Fishy Breath and Skabscrath are cones from the caster with the exact-wave rule.
- A charge's run-up is the smaller of 12 m and 2 seconds of the unit's run speed.
- A unit's owned abilities are read again 2 s and 10 s after a cast on it, and every 4 s once they have changed.
- Test build only: the per-second dial dump writes only the badges that exist.

Roster unchanged: 982 entries / 1,035 keys. 72 enemy_ground_melee entries, 2 enemy_wave_charge.

**Field (archive\\logs\\battle_20261122_r209_transform.txt, bytes 1,067,747,316-1,092,330,525, four battles):** "the
player's own cast of" appeared for Tz'arkan (round 209's protection works for a hand cast). Malus Darkblade keeps his
unit id and his unit type after the transformation. The lag before it: with a Deadly Onslaught owner selected the test
build wrote 31,392 dump lines in 34 s of battle.

**Proof:** harness 208 full suite **8,479 checks / 0 failures**. RED on the pre-round snapshot: no Loons order at
approaching infantry, Skabscrath held for a unit 12 m beside the breath and for one 90 m ahead, no charge at 2.8 m/s
with 8 m to go, the transformed hero's new ability never cast. The cast trace of the whole suite (2,187 worlds, 1,718
casts) matches between the test build and the release build apart from the 3 probe casts. Workbook v84. Not seen in game.
"""
ROUND_DOC = """# Round 210: the second replies to the afternoon code review (2026-11-22)

## 1. The rulings

| Topic | The user's reply | What happened |
|---|---|---|
| The Loons | "I would like to change them completely." Caster standing, enemy infantry approaching between 25 and 15 m, cast in that direction, no friendly unit of more than one man in the path | BUILT |
| The caster-front breaths | "I tested Skarbscrath and it always starts at the caster" | BUILT for all five |
| Empty orders after the last use | "no" | Closed, nothing built |
| A transformed unit's new abilities | "it's true that they never fire. you can see the log" | BUILT |
| The lag before the transformation | "Please check if the mod might be the cause" | Found in the test build's logging, trimmed |
| Slow units and charging, option B | "okay, do it" | BUILT |
| The grid behind "at most 5 soldiers" | "then leave it" | Left |

## 2. What changed in battle

1. **Spinning Loons, The Loons of Eight Peaks.** They fire when all of this is true: the Night Goblins stand, an
   enemy infantry unit of more than one man is moving and coming closer, its edge is 15 to 25 m away, and none of your
   units of more than one man stands in the fanatics' path. The path runs from the Goblins towards that enemy, 84 m
   long. It is 4 m wide each side at the start and 60 m each side at the end, because the fanatics turn at random (the
   width is simulated from the game's own numbers). Your Lords and Heroes on foot do not block it. The order goes on
   the ground in the enemy's direction. They no longer fire at an enemy that is already in melee.
2. **Shatter, Pestilent Breath x2, Fishy Breath, Skabscrath.** The mod now treats the breath as what you saw: it
   starts at the caster, thin, and widens. Before, it was a band of the full width starting at the caster and reaching
   36 m too far. So it stops holding for your units that stand beside the breath or beyond its end, and it fires only
   when enemy soldiers really stand under the cone, with at most 5 of yours.
3. **Charging.** A unit counts as charging when it runs at a target, will hit within 4 seconds, and still has a
   run-up left. The run-up was 12 m for everybody. It is now the smaller of 12 m and what the unit runs in 2 seconds.
   Skeleton Warriors (2.8 m/s) need 5.6 m. A unit of 6 m/s or faster is exactly as before.
4. **Transformation.** Malus Darkblade keeps his unit number and his unit type when he transforms, so the mod never
   noticed. Now, 2 and 10 seconds after any ability is cast on a unit (by you or by the mod), the mod reads that unit's
   ability list again. If it changed, the unit's new abilities fire, and from then on the unit is read again every 4
   seconds, so the change back is seen too.
5. **The lag.** In the test build only: while a unit that owns Deadly Onslaught was selected, the mod wrote one log
   line per ability, 982 lines, every second (31,392 lines in the 34 seconds before your transformation). It now
   writes only the lines of badges that exist. The Workshop build never had this code.

## 3. Proof

- RED control (the pre-round snapshot, `docs\\backups\\round210\\`): every new world behaves the old way.
- GREEN: harness 208, full suite, 8,479 checks, 0 failures (`mod_source\\releases\\20261122_replies2_harness208\\h208_run1.txt`).
- The cast trace of the whole suite: 2,187 worlds, 1,718 casts, the two builds differ only in the 3 probe casts.
- Test pack md5 `%(test)s` (1,659,510 bytes), release pack md5 `%(rel)s`. Workbook v84.

## 4. Rebased pins (old value, new value, why)

| Where | Old | New | Why |
|---|---|---|---|
| harness 97, 98, 101, 102 count pins | 74 enemy_ground_melee entries | 72 | the Loons left the family |
| harness 142 (0zn) | the two Loons entries on enemy_ground_melee | on enemy_wave_charge | the same |
| harness 142, worlds LO1 and LE1 | an enemy in melee 10 m away: one cast | no cast | the Loons no longer fire at an enemy in melee |
| harness 162 (0zz11), harness 202 (0zz50) | 0 enemy_wave_charge entries | 2 | the Loons |
| harness 207 (0zz55) | ring_clear on 2 entries, a ring table | on none, an empty table | round 209's ring is superseded |
| harness 207, world LN2 | a clear 98 m ring: one cast | no cast | the same |
| harness 66 (H1i), harness 73 (I2d) | 1 and 2 reads of a unit's ability list | 2 and 4 | the list is read again 2 s after a cast |
| builder, rounds 162 and 164 | 83 keys in the WW table, 0 enemy_wave_charge entries | 85, 2 | the Loons |
| builder, round 203 | enemy_wave_charge keys launch from the target's near edge, 0 entries | from the caster's front, 2 | the Loons |
| builder, round 205 | 20 growing rows, each an exact wave | 25, each an exact wave or a caster-front breath | the five breaths |
| builder, round 209 | the ring on the two Loons | on no entry | superseded |
| builder | 74 enemy_ground_melee entries | 72 | the Loons |

## 5. What is not verified

- Nothing of this round has been seen in a battle.
- The Loons: whether the game aims the fanatics along the ordered direction. They are released "at the caster's
  front" in the game's table. If they always leave along the unit's facing, the Goblins must face the enemy.
- The Loons' path has no extra 10 m margin: the rule says "in the path". The path's width is the simulated drift.
- "Approaching" is Claude's number: the gap shrinks at least 1 m per second, measured over one second.
- The four other breaths start at the caster by the same table entry as Skabscrath. Only Skabscrath was seen.
- The transformation fix rests on the game returning the new abilities in the unit's ability list. The log line
  "owned abilities changed: unit" in the next battle confirms it.
- The lag: the dump is the only heavy thing the log shows. Whether it was the whole cause is not measured.

## 6. Still open from the review

Chain Lightning, the area blasts counting walkers (left by the user). Hell Hammer, the fliers under an exact wave,
Flesh-eating Scarabs, the delayed self blasts, the Frost Dragon Scale, the pause and selection case, the three
neighbour measurements, the late start of the "running at us" test (never ruled).
"""


def one(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


def tracker():
    p = ROOT + "docs\\WH3_ability_tracker.md"
    s = open(p, encoding="utf-8", newline="").read()
    assert "### 10.87 Round 210" not in s
    lines = s.split("\n")
    hits = {k: 0 for k in LOONS + CONES}
    for i, l in enumerate(lines):
        if not l.startswith("| "):
            continue
        m = re.match(r"\| [^|]*`([^`]+)` \|", l)
        if not m or m.group(1) not in hits:
            continue
        c = l.split(" | ")
        if m.group(1) in LOONS:
            assert c[1].startswith("`implemented (fighting enemy, on its ground: enemy_ground_melee)"), l[:160]
            c[1], c[3] = LOON_STATUS, LOON_PROPOSAL
            note = LOON_NOTE
        else:
            assert c[1].startswith("`implemented (clear cone, most value: enemy_cone)"), l[:160]
            note = CONE_NOTE
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
    s = one(s, "- Installed build: md5 `c7835b1a8ef6c3e61dc750f588673aed`, 1,649,264 bytes" + nl
            + "  (round 209, 2026-11-22: the Loons' friendly ring, Lamprey's Bite as a wave, the player's own cast protected).",
            "- Installed build: md5 `" + TEST_MD5 + "`, 1,659,510 bytes" + nl
            + "  (round 210, 2026-11-22: the Loons' own rule, the breaths as cones from the caster, slow charges, transformations).")
    s = one(s, "20261122_replies_harness207/build_and_install209.py", "20261122_replies2_harness208/build_and_install210.py")
    s = one(s, "(harness207: 8,412 checks; it takes about 2 minutes)", "(harness208: 8,479 checks; it takes about 2 minutes)")
    s = one(s, "WH3_abilities_master_v83_2026-11-22.xlsx` | the current master spreadsheet (versioned, newest wins). Built by "
            "`tools\\make_xlsx_v83.py`, verified by `tools\\verify_xlsx_v83.py <v82 md5> <pack md5>` (v83 = v82 + ",
            "WH3_abilities_master_v84_2026-11-22.xlsx` | the current master spreadsheet (versioned, newest wins). Built by "
            "`tools\\make_xlsx_v84.py`, verified by `tools\\verify_xlsx_v84.py <v83 md5> <pack md5>` (v84 = v83 + the Loons "
            "on enemy_wave_charge with the user's rule, the FROM THE CASTER sentence on the five breaths, 2 cards. v83 = v82 + ")
    a = "- ROUND 209 (2026-11-22, the user's row-by-row replies to the afternoon review; `docs\\WH3_round209_review_replies.md`)."
    note = [
        "- ROUND 210 (2026-11-22, the user's second replies; `docs\\WH3_round210_review_replies2.md`). INSTALLED: test pack md5",
        "  8760b82d..., release pack md5 9a1e8f9a..., harness 208: 8,479 / 0, the cast trace matches apart from the 3 probe",
        "  casts, workbook v84, tracker 10.87. NOT SEEN IN GAME. (1) THE LOONS, the user's own rule (\"I would like to change",
        "  them completely\"): both entries on enemy_wave_charge (2 entries, all 141 families in use), WW kind 8",
        "  (gen_ww_tables: activator_front on that family, sideways drift 56 m), FOURTH.evaluate_loons / ww_loons_ok /",
        "  loons_closing: the caster's is_moving() exactly false, an enemy INFANTRY unit of more than one man moving and",
        "  closing (FOURTH.LOONS_CLOSING_MPS 1 m/s over 1 s: Claude's number), its edge FOURTH.LOONS_MIN_M 15 to",
        "  FOURTH.LOONS_MAX_M 25 m away (the USER'S metre values, outside the range rule: the evaluator sets eg_range_m to",
        "  25 for the pre-cast re-check), none of our units of more than one man within row.r + row.buf x t of the 84 m line",
        "  from the caster (NO extra 10 m: \"in the path\"). An aimed ground order (FOURTH.ww_aim, point at most",
        "  FOURTH.LOONS_AIM_M 20 m from the caster, the bearing). Round 209's ring_clear is on NO entry now (code and the",
        "  empty FOURTH.RING_TEXT stay). UNKNOWN: whether the game releases the fanatics along the ordered direction or along",
        "  the unit's facing. (2) THE FIVE CASTER-FRONT BREATHS (user test: \"I tested Skarbscrath and it always starts at",
        "  the caster\"): FOURTH.ww_cone_value uses FOURTH.ww_line_value (the exact rule) from the caster along row.path",
        "  (not off + path), cone rows GENERATED for enemy_cone too (gen_wave_cone, 25 rows), FOURTH.ww_fine = a 1.5 m grid",
        "  in wave_cover for these thin cones. Old worlds keep the band (ZZ_AUTO_TEST_NO_FREE_AIM). (3) E1 (\"okay, do",
        "  it\"): measure_charge's run-up = min(CHARGE_MIN_DISTANCE_M, 2 x fast_speed) (the literal 2: measure_charge sits",
        "  ABOVE the FOURTH table). (4) TRANSFORMATION (field: Malus Darkblade keeps unit id AND type(); the HUD claim put",
        "  letters on the new buttons, nothing fired): FOURTH.rescan_soon(id) after every 'fired' and for the selected units",
        "  after the player's cast, FOURTH.reread_unit(unit, ui_id, do_redetect) in the poll (2 s and 10 s later, then every",
        "  re-detect period once the list changed). Grep the next battle for 'owned abilities changed: unit'. The poll block",
        "  may hold exactly ONE 'active_refresh_pending = true' (harness 77) and ONE 'log(\"re-scan: unit \"' site. The",
        "  annotated copy's poll has NO local ability_key (it passes target_key_by_unit[ui_id]). (5) LAG (user: \"the game was",
        "  very laggy\"): TEST BUILD ONLY, log_dial_dump wrote one 'OUR BADGE' line per ability (982 a second) while a Deadly",
        "  Onslaught owner was selected. Now only existing badges (and the three original markers). FIELD: \"the player's own",
        "  cast of\" appeared for Tz'arkan, so round 209's protection sees a hand cast. CLOSED by the user: the use counter",
        "  (\"no\"), the soldier grid (\"then leave it\"). MOCK: unit_distance answers the CALLER's def.dist (the caster's),",
        "  not the target's. Heredocs broke Python edits three more times: Write / Edit only. Next battle from byte",
        "  1,092,330,525 (re-measure).",
    ]
    s = one(s, a, nl.join(note) + nl + a)
    s = one(s, "Current roster (round 201): 982 ABILITIES entries / 1,035 ability keys / 141 trigger evaluator families.",
            "Current roster (round 210): 982 ABILITIES entries / 1,035 ability keys / 141 trigger evaluator families.")
    open(p, "w", encoding="utf-8", newline="").write(s)
    p = ROOT + "docs\\WH3_open_points.md"
    s = open(p, encoding="utf-8", newline="").read()
    a = "| PARTLY BUILT (round 209): waiting for a battle and for two answers | Built:"
    s = one(s, a, "| BUILT (rounds 209 and 210): waiting for a battle | ROUND 210 (`docs\\WH3_round210_review_replies2.md`): the "
            "Loons on the user's own rule (standing caster, approaching infantry 15 to 25 m away, a clear path), the five "
            "caster-front breaths as cones from the caster, the 2-second run-up for slow units, the re-read of a unit's "
            "abilities after a cast (transformations). Closed by the user: the use counter, the soldier grid. Open: whether "
            "the fanatics follow the ordered direction. ROUND 209 built:")
    open(p, "w", encoding="utf-8", newline="").write(s)
    p = ROOT + "docs\\WH3_code_review_2026-11-22_afternoon.md"
    s = open(p, encoding="utf-8", newline="").read()
    s = one(s, "## 2. Findings that need a ruling, ranked\n",
            "## 1c. The user's second replies and round 210 (2026-11-22)\n\n"
            "| Finding | Reply | State |\n|---|---|---|\n"
            "| A1 the Loons | \"I would like to change them completely\" and his own rule | BUILT in round 210 (approaching infantry 15 to 25 m away, a clear path) |\n"
            "| B1 the five caster-front breaths | \"I tested Skarbscrath and it always starts at the caster\" | BUILT in round 210 (cones from the caster) |\n"
            "| C2 the transformed unit | \"it's true that they never fire\" | BUILT in round 210 (the ability list is read again after a cast) |\n"
            "| C3 empty orders after the last use | \"no\" | closed |\n"
            "| D the grid of the soldier count | \"then leave it\" | closed |\n"
            "| E1 slow units | \"okay, do it\" (option B) | BUILT in round 210 |\n\n"
            "## 2. Findings that need a ruling, ranked\n")
    open(p, "w", encoding="utf-8", newline="").write(s)
    open(ROOT + "docs\\WH3_round210_review_replies2.md", "w", encoding="utf-8", newline="\n").write(
        ROUND_DOC % {"test": TEST_MD5, "rel": REL_MD5})
    print("CLAUDE.md, open points, the review doc and the round document updated")


if __name__ == "__main__":
    tracker()
    claude()
