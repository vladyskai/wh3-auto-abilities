#!/usr/bin/env python3
"""Build WH3_abilities_master_v17_2026-10-18.xlsx from v16.

Round 116: the air-drop wait is MEASURED, not fixed - the enemy's own velocity,
projected on the enemy -> caster axis, read once at the first contact of a pair.
Edits, on all 19 air-drop rows:
  * column 19 (Status reason / family)  - the trigger-rule summary
  * column 22 (Trigger, as implemented) - the full evaluator text
and adds: Definitions section 14 (the two constants, the formula, the source
table, the measured-once rule, the poll grid, the read-verification log block and
a tuning guide), a retitled section 13, a Numbers reconciliation note and the v17
Changelog row.  v1-v16 stay byte-unchanged (a NEW filename is written).
"""
import openpyxl

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v16_2026-10-18.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v17_2026-10-18.xlsx"

wb = openpyxl.load_workbook(SRC)
ws = wb["Abilities"]

OLD_SUMMARY_MARK = "trigger rule: round 115 - THE EDGE-GAP RULE PLUS A 1-SECOND DWELL ON THE PAIR"
NEW_SUMMARY = (
    "trigger rule: round 116 - THE EDGE-GAP RULE PLUS a delay MEASURED FROM THE ENEMY'S OWN "
    "VELOCITY at the moment of first contact: the nearest ALIVE enemy with MORE THAN 10 models "
    "whose battle_unit:unit_distance (EDGE-TO-EDGE) is BELOW 0.10 m; when that pair first goes "
    "under the line the enemy's velocity is built from is_moving / is_moving_fast / slow_speed / "
    "fast_speed / position / ordered_position, projected on the enemy-to-caster axis (proj = the "
    "cosine), and the wait becomes AIR_DROP_DWELL_MID_S - AIR_DROP_DWELL_SWING_S * proj = 0 s for "
    "an enemy running AT the caster, 1 s stationary or perpendicular, 2 s running AWAY, floored at "
    "0; that delay is measured ONCE per contact and never re-measured inside it (a re-contact "
    "measures again); a separation before it cancels (the time under and the gap are logged) and a "
    "separation after AIR_DROP_MIN_CONTACT_S = 0.3 s of contact fires on the separation evaluation "
    "(the short-crossing fallback); no infantry filter, no single-entity test, no projection of "
    "POSITIONS, no frontage, no path; a separate 0.2 s fast pass re-runs the same evaluator while a "
    "valid enemy is inside 30 m but adds NO time - the clock is the poll's own 250 ms tick_count, so "
    "a measured delay lands on the first poll at or after it; the global poll is untouched. Every "
    "contact episode PRINTS the raw reads (is_moving, is_moving_fast, slow_speed, fast_speed, "
    "pos=(x,z), ordered=(x,z), |h|), the cosine, the delay and the velocity source, with UNREADABLE "
    "where a read failed. air_only / no_melee as the row declares them; self-centred cast; pre-cast "
    "re-check re-measures the edge gap, re-validates the model counts and RE-VERIFIES the measured "
    "delay on fresh handles.")

OLD_DECISION_START = "THE DECISION IS ONE COMPARISON - AND IT MUST LAST (round 115):"
OLD_DECISION_END = ("THE TWO NEW CONSTANTS: AIR_DROP_DWELL_S = 1.0 s (the dwell) and "
                    "AIR_DROP_MIN_CONTACT_S = 0.3 s (the short-crossing floor).")

NEW_DECISION = (
    "THE DECISION IS ONE COMPARISON, AND THE WAIT AFTER IT IS MEASURED (round 116): UNDER means "
    "battle_unit:unit_distance(caster, enemy) - the engine's EDGE-TO-EDGE distance in metres "
    "(battle_unit.lua:160) - is BELOW FOURTH.AIR_DROP_EDGE_M = 0.10 m. WHEN a pair first goes "
    "UNDER the delay it must serve is MEASURED from the enemy's own velocity, on that very "
    "evaluation, and FIRE means that delay has elapsed. THE USER'S RULING, verbatim: 'if the enemy "
    "unit is running away, then it is too soon. If the enemy moving is running towards, then it is "
    "too late. ... But it must be calculated the moment the edge to edge distance is below our "
    "theshold. Then, if the unit is running towards the caster, then the delay would be 0. If "
    "running away, then the delay would be 2. If stationary or perpedicular, then should be 1. ... "
    "the delay is dynamic in this way.' THE FORMULA, one line, no dials: axis = normalise("
    "caster.position() - enemy.position()) in x/z only; v = speed * normalise(ordered_position() - "
    "position()) with speed = fast_speed() when is_moving_fast() else slow_speed(); proj = dot(v, "
    "axis) / (speed * |axis|) - the COSINE, clamped to +-1; delay = FOURTH.AIR_DROP_DWELL_MID_S - "
    "(FOURTH.AIR_DROP_DWELL_SWING_S * proj), floored at 0. At the shipped pair (MID = 1.0 s, SWING "
    "= 1.0 s): proj +1 (running straight AT the caster) -> 0.0 s, proj 0 (stationary or "
    "perpendicular) -> 1.0 s, proj -1 (running straight AWAY) -> 2.0 s, and everything between "
    "interpolates linearly (proj +0.71 -> 0.29 s, proj -0.71 -> 1.71 s). MEASURED ONCE PER CONTACT: "
    "the first evaluation of a contact stamps the PAIR (caster ui id, enemy ui id) with the poll "
    "tick, the delay, the cosine and the velocity source, and NOTHING is cast on that evaluation; "
    "the value is NEVER re-measured inside the contact even if the enemy turns, and a RE-CONTACT "
    "after a separation starts a FRESH measurement. THE DELAY LANDS ON THE POLL GRID: tick_count "
    "moves in POLL_MS = 250 ms steps, so a measured 0.29 s waits 0.50 s, a measured 1.71 s waits "
    "1.75 s and a measured 0.00 s fires on the NEXT evaluation - quantisation can only delay a cast, "
    "never advance it. A separation before the delay elapses CANCELS and logs the time actually "
    "under plus the separation gap; a separation after FOURTH.AIR_DROP_MIN_CONTACT_S = 0.3 s of "
    "contact FIRES on the SEPARATION EVALUATION instead - the SHORT-CROSSING FALLBACK. THE VELOCITY "
    "IS REBUILT, AND EVERY READ FAILS CLOSED to a ZERO velocity with a named source - 'ordered' (a "
    "real heading), 'stationary' (is_moving() false), 'moving-unreadable', 'speed-unreadable', "
    "'speed-zero', 'pos-unreadable', 'no-heading' (ordered_position() unreadable OR the order point "
    "under 0.5 m away - the documented 'attacking' case, where ordered_position() returns the "
    "CURRENT position), 'axis-degenerate' (the two centres under 0.5 m apart in x/z) and "
    "'axis-unreadable' (the caster's position could not be read) - each falling back to the 1.0 s "
    "MID baseline. THE READ-VERIFICATION LOG, one line per contact episode plus one per waiting "
    "tick: '[<ui>] <marker> reads: moving=<b> is_moving_fast=<b> slow_speed=<n.nn> "
    "fast_speed=<n.nn> pos=(<x>,<z>) ordered=(<x>,<z>) |h|=<n.n> proj=<+n.nn> src=<src> "
    "delay=<n.nn>s (measured once for this contact)' and '[<ui>] <marker> reads(hold): <the same "
    "reads re-taken> proj=<measured> src=<measured> delay=<n.nn>s held=<n.nn>s', with UNREADABLE in "
    "any field whose read failed - so an ordered_position() that answers the current position is "
    "visible as |h|=0.0 src=no-heading instead of being assumed. THE THREE CONSTANTS: "
    "AIR_DROP_DWELL_MID_S = 1.0 s (the across value), AIR_DROP_DWELL_SWING_S = 1.0 s (how far proj "
    "+-1 moves it) and AIR_DROP_MIN_CONTACT_S = 0.3 s (the short-crossing floor).")

OLD_LOG_ANCHOR = " THE DWELL LINES, one per EPISODE (event-driven, not change-gated): "
OLD_LOG_END = " WHY THE EDGE GAP:"
NEW_LOG = (
    " THE DWELL LINES, one per EPISODE (event-driven, not change-gated): '[<ui id>] <marker> dwell "
    "started: under at gap <d.dd>m, waiting <t.tt>s (pair '<enemy key>')' where the wait is the "
    "MEASURED delay; '... dwell: under <t.t>s of <measured>s (gap <d.dd>m)' on each hold, preceded "
    "by one '... reads(hold): ...' line; '... dwell satisfied after <t.t>s -> FIRING (gap <d.dd>m, "
    "pair '<enemy key>')'; '... dwell cancelled: separated after <t.t>s (gap <d.dd>m; the dwell is "
    "<measured>s and the short-crossing floor is 0.30s)'; '... short crossing: under for <t.t>s (>= "
    "0.30s) -> FIRING on separation (gap <d.dd>m, the delay measured was <measured>s)'. The "
    "pre-cast re-check writes '(dwell <t.t>s of <measured>s)' on the firing line - the pair's OWN "
    "delay - or '(short crossing: held <t.t>s of 0.30s)', and its SKIPPED line carries 'gap_ok=', "
    "'dwell=', 'dwell_ok=' and 'short_cross='.")

rows = 0
for r in range(2, ws.max_row + 1):
    if ws.cell(row=r, column=21).value != "air_drop_on_infantry":
        continue
    rows += 1
    summary = ws.cell(row=r, column=19).value
    assert OLD_SUMMARY_MARK in summary, "row %d: the round-115 summary is not there" % r
    head, sep, _tail = summary.partition(" | ")
    ws.cell(row=r, column=19).value = head + " | " + NEW_SUMMARY

    trig = ws.cell(row=r, column=22).value
    assert OLD_DECISION_START in trig, "row %d: the round-115 decision sentence is not there" % r
    assert OLD_DECISION_END in trig
    assert OLD_LOG_ANCHOR in trig and OLD_LOG_END in trig
    assert "AIR_DROP_DWELL_MID_S" not in trig
    i = trig.index(OLD_DECISION_START)
    j = trig.index(OLD_DECISION_END) + len(OLD_DECISION_END)
    trig = trig[:i] + NEW_DECISION + trig[j:]
    # the pre-cast re-check paragraph must state the delay verification too
    OLD_PC = ("THE PRE-CAST RE-CHECK re-validates the chosen enemy on FRESH handles "
              "immediately before the call (still alive, still more than 10 models) and "
              "RE-MEASURES the edge distance through the same primitive; a lapsed condition "
              "SKIPS the cast rather than spending it and writes '-> SKIPPED at re-check' with "
              "the fresh numbers.")
    NEW_PC = ("THE PRE-CAST RE-CHECK re-validates the chosen enemy on FRESH handles "
              "immediately before the call (still alive, still more than 10 models), "
              "RE-MEASURES the edge distance through the same primitive AND VERIFIES THE WAIT "
              "against the pair's OWN measured delay - '(dwell <under>s of <measured>s)' - or "
              "against the short-crossing floor for a fallback fire ('(short crossing: held "
              "<under>s of 0.30s)'); a lapsed condition SKIPS the cast rather than spending it "
              "and writes '-> SKIPPED at re-check' with the fresh numbers.")
    assert OLD_PC in trig, "row %d: the round-114 pre-cast paragraph is not there" % r
    trig = trig.replace(OLD_PC, NEW_PC)
    a = trig.index(OLD_LOG_ANCHOR)
    b = trig.index(OLD_LOG_END)
    trig = trig[:a] + NEW_LOG + trig[b:]
    ws.cell(row=r, column=22).value = trig

assert rows == 19, "expected 19 air-drop rows, edited %d" % rows

# ---------------------------------------------------------------- Definitions
d = wb["Definitions"]
assert d.cell(row=216, column=1).value.startswith("13. THE DWELL (round 115)")
d.cell(row=216, column=1).value = (
    "13. THE DWELL MACHINERY (round 115) - THE PAIR, THE CLOCK AND THE FALLBACK (the VALUE it waits "
    "for is measured since round 116: section 14)")
d.cell(row=223, column=1).value = "FOURTH.AIR_DROP_DWELL_MID_S / _SWING_S (round 116)"
d.cell(row=223, column=2).value = "1.0 / 1.0 (s)"
d.cell(row=223, column=3).value = (
    "The wait is no longer a constant: MID is the delay at proj 0 (stationary / perpendicular) and "
    "SWING is how far proj +-1 moves it, so closing = MID - SWING = 0.0 s and receding = MID + "
    "SWING = 2.0 s, floored at 0. Both ship at 1.0 s. See section 14 for the formula. The RETIRED "
    "FOURTH.AIR_DROP_DWELL_S (a flat 1.0 s) must not be reintroduced.")
d.cell(row=233, column=1).value = ("TUNING GUIDE (round 115 - the machinery; for the VALUES use "
                                   "section 14's guide)")
d.cell(row=235, column=2).value = "AIR_DROP_DWELL_MID_S"
d.cell(row=235, column=3).value = (
    "1.0 -> 1.5. Read the 'reads:' line: it prints the delay that was measured for that contact and "
    "the cosine it came from, so a drop that is still early on a CLOSING enemy (proj near +1) is a "
    "SWING problem, not a MID problem.")
d.cell(row=236, column=2).value = "AIR_DROP_DWELL_MID_S"
d.cell(row=236, column=3).value = (
    "1.0 -> 0.7, keeping it above AIR_DROP_MIN_CONTACT_S. If most contacts end with 'dwell "
    "cancelled: separated after <t>s' the delay is simply longer than the crossings you get.")
d.cell(row=237, column=3).value = (
    "0.3 -> 0.2 -> 0.1. Each contact that ends under the floor logs its own 'dwell cancelled ... "
    "separated after <t>s' line, so the log says what floor would have caught it.")

base = d.max_row + 2
sec = [
    ("14. THE MEASURED DELAY (round 116) - THE WAIT COMES FROM THE ENEMY'S VELOCITY", None, None),
    ("THE USER'S RULING, verbatim",
     "'if the enemy unit is running away, then it is too soon. If the enemy moving is running "
     "towards, then it is too late. ... But it must be calculated the moment the edge to edge "
     "distance is below our theshold. Then, if the unit is running towards the caster, then the "
     "delay would be 0. If running away, then the delay would be 2. If stationary or perpedicular, "
     "then should be 1. ... the delay is dynamic in this way.'", None),
    ("Why a fixed delay could not work",
     "A flat wait is too LATE for an enemy charging in (the boxes are already touching and the "
     "formation is past by the time the drop leaves) and too SOON for one running away (it leaves "
     "the blast area during the wait). The only quantity that separates the two is the enemy's "
     "VELOCITY relative to the line joining it to the caster.", None),
    ("THE FORMULA (one line, no dials)",
     "axis = normalise(caster.position() - enemy.position()) in x/z only (get_x/get_z; get_y is "
     "height above the water plane). v = speed * normalise(ordered_position() - position()), where "
     "speed = fast_speed() when is_moving_fast() is true, else slow_speed(). proj = dot(v, axis) / "
     "(speed * |axis|) - the COSINE, clamped to +-1. delay = FOURTH.AIR_DROP_DWELL_MID_S - "
     "(FOURTH.AIR_DROP_DWELL_SWING_S * proj), floored at 0. The axis runs ENEMY -> CASTER, so a "
     "positive cosine means the enemy is closing on the caster.", None),
    ("At the shipped pair (1.0 / 1.0 s)",
     "proj +1 (running straight AT the caster) -> 0.00 s; proj 0 (stationary, or perpendicular to "
     "the axis) -> 1.00 s; proj -1 (running straight AWAY) -> 2.00 s; proj +0.71 -> 0.29 s; proj "
     "-0.71 -> 1.71 s. Every angle between interpolates linearly - there is no table.", None),
    ("THE TWO CONSTANTS", None, None),
    ("Constant", "Ships as", "What it does / how to tune it"),
    ("FOURTH.AIR_DROP_DWELL_MID_S", "1.0 (s)",
     "The delay at proj 0: a stationary enemy, or one moving across the axis. This is the 'across' "
     "value. Raise it to make every drop wait longer; lower it (but keep it above "
     "AIR_DROP_MIN_CONTACT_S) to make them all fire sooner."),
    ("FOURTH.AIR_DROP_DWELL_SWING_S", "1.0 (s)",
     "How far the cosine moves the delay: closing = MID - SWING (floored at 0), receding = MID + "
     "SWING. Raise it to punish/forgive the head-on and away cases harder (2.0 gives 0 s closing / "
     "3 s receding); set it to 0.0 and the delay is the flat MID again - the round-115 behaviour, "
     "one number away."),
    ("FOURTH.AIR_DROP_MIN_CONTACT_S", "0.3 (s)",
     "Unchanged. The SHORT-CROSSING FLOOR: a separation before the measured delay elapses but after "
     "this much contact fires on the separation evaluation instead of being cancelled."),
    ("MEASURED ONCE PER CONTACT",
     "the pair row",
     "FOURTH.ad_pair[caster ui id][enemy ui id] = { first = <poll tick>, delay = <s>, proj = <cos>, "
     "src = <source> }. Taken on the FIRST evaluation of a contact (the one that stamps the pair, "
     "and which NEVER casts), read back by every later evaluation of that contact, and NEVER "
     "re-measured even if the enemy turns - world G of harness 116 turns an enemy mid-contact and "
     "the fire still lands on the delay measured at contact. A RE-CONTACT after a separation starts "
     "a FRESH measurement (world H). The row is dropped on separation and purged with the unit."),
    ("THE CLOCK, AND THE POLL GRID",
     "tick_count, 250 ms",
     "The elapsed time is the poll's own tick_count (POLL_MS = 250 ms), so the cast lands on the "
     "first poll at or after the measured delay: 0.29 s -> 0.50 s, 1.71 s -> 1.75 s, 0.00 s -> the "
     "NEXT evaluation. The log prints the MEASURED value; the grid is what the clock can deliver, "
     "and it can only delay a cast, never advance it. The 0.2 s fast pass adds evaluations, never "
     "time."),
    ("THE VELOCITY SOURCES - every read fails CLOSED", None, None),
    ("src=ordered", "a real heading",
     "is_moving() true and ordered_position() - position() longer than 0.5 m in x/z: v = speed * "
     "that unit vector, and the delay is MID - SWING*proj."),
    ("src=stationary", "is_moving() false", "No motion at all: proj 0, delay = MID (1.0 s)."),
    ("src=moving-unreadable", "is_moving() raised", "Fail closed: proj 0, delay = MID."),
    ("src=speed-unreadable", "the speed read raised",
     "The speed for the unit's state (fast_speed when is_moving_fast, else slow_speed) could not be "
     "read: proj 0, delay = MID."),
    ("src=speed-zero", "the speed read answered <= 0",
     "A moving unit with no speed: proj 0, delay = MID."),
    ("src=pos-unreadable", "position() (or its x/z) failed", "No heading and no axis: delay = MID."),
    ("src=no-heading", "ordered_position() failed OR the order point is < 0.5 m away",
     "The documented 'attacking' case - ordered_position() returns the CURRENT position, so the "
     "heading collapses. Delay = MID (1.0 s). THE FIRST THING TO CHECK IN THE FIELD LOG: a charging "
     "enemy that reads |h|=0.0 src=no-heading got the 1.0 s baseline, not 0 s."),
    ("src=axis-degenerate", "the two centres are < 0.5 m apart in x/z",
     "There is no axis to project on: delay = MID."),
    ("src=axis-unreadable", "the CASTER's position could not be read", "delay = MID."),
    ("THE READ-VERIFICATION LOG (the user's second request)", None, None),
    ("contact episode - ONE line, on the stamping evaluation",
     "[<ui id>] <marker> reads: moving=true is_moving_fast=false slow_speed=2.50 fast_speed=4.50 "
     "pos=(5.0,0.0) ordered=(-5.0,0.0) |h|=10.0 proj=+1.00 src=ordered delay=0.00s (measured once "
     "for this contact)",
     "Every value the projection depends on, RAW: is_moving(), is_moving_fast(), slow_speed(), "
     "fast_speed(), position() and ordered_position() as (x,z) pairs, the heading length |h|, the "
     "cosine, the delay and the source. UNREADABLE stands in for a read whose pcall failed. "
     "is_moving_fast is named in full so the two 'fast' values cannot be confused."),
    ("each waiting tick - ONE line",
     "[<ui id>] <marker> reads(hold): moving=true is_moving_fast=false slow_speed=2.50 "
     "fast_speed=4.50 pos=(5.0,0.0) ordered=(5.0,3.0) |h|=3.0 proj=+0.00 src=ordered delay=1.00s "
     "held=0.25s",
     "The reads are RE-TAKEN (so ordered_position() is observable during the contact) while the "
     "proj/delay printed are the ones MEASURED AT THE STAMP - which is how 'measured once' is "
     "visible in the log as well as provable in the harness."),
    ("what the line answers", "the question the user asked",
     "If ordered_position() returns the CURRENT position, the line shows pos=(x,z) EQUAL to "
     "ordered=(x,z) and |h|=0.0 with src=no-heading - directly, without inference. If it returns a "
     "real destination, |h| is the distance to it and the cosine is the angle between that heading "
     "and the line to the caster."),
    ("THE PRE-CAST RE-CHECK",
     "models + gap + the measured delay",
     "Immediately before the call the caster is still alive / airborne / out of melee where its row "
     "demands, the chosen enemy still has > 10 models, the edge gap is re-measured on fresh handles "
     "AND the wait is verified against the pair's OWN measured delay ('(dwell <under>s of "
     "<measured>s)'). A lapsed condition SKIPS the cast rather than spending it; a fallback fire is "
     "accepted with '(short crossing: held <under>s of 0.30s)'."),
    ("TUNING GUIDE (round 116) - ONE CHANGE PER FIELD TEST", None, None),
    ("Symptom", "What to change", "Order to try"),
    ("drops still early on an enemy CHARGING IN (the log shows proj near +1)", "AIR_DROP_DWELL_SWING_S",
     "lower it 1.0 -> 0.7 -> 0.5; the closing branch is MID - SWING, so a smaller swing makes the "
     "head-on case wait longer. 0.0 = the flat MID."),
    ("drops LATE on an enemy running away (the log shows proj near -1)", "AIR_DROP_DWELL_SWING_S",
     "raise it 1.0 -> 1.3; the receding branch is MID + SWING."),
    ("every drop is slightly early / late whatever the angle", "AIR_DROP_DWELL_MID_S",
     "1.0 -> 1.2 (later) or 0.8 (earlier) - this moves ALL angles together."),
    ("the log says src=no-heading for an enemy that IS charging", "nothing - report it",
     "ordered_position() is answering the current position for that unit. The delay fell back to "
     "the 1.0 s baseline; the next round would need a different heading source (e.g. the axis to "
     "current_target()). Send that line back."),
    ("quick crossings are being missed entirely", "AIR_DROP_MIN_CONTACT_S",
     "0.3 -> 0.2 -> 0.1; each cancelled contact logs its own time under."),
    ("TOTAL", "2 measured constants + 1 floor",
     "The measured delay, the cosine and every raw read are in the log for every contact, so one "
     "field battle is enough to pick the next value."),
]
for i, (a, b, c) in enumerate(sec):
    row = base + i
    d.cell(row=row, column=1).value = a
    if b is not None:
        d.cell(row=row, column=2).value = b
    if c is not None:
        d.cell(row=row, column=3).value = c

# ------------------------------------------------------------------- Numbers
n = wb["Numbers"]
assert n.cell(row=42, column=1).value.startswith("Trigger families after round 115")
n.cell(row=42, column=1).value = ("Trigger families after round 116 - re-counted from the mod "
                                  "(689 entries / 742 keys; round 116 changed NO count)")
n.cell(row=101, column=1).value = (
    "Round 116 reconciliation: the air-drop row is unchanged at 12 entries / 19 keys and the mod at "
    "689 / 742 - the round replaced the VALUE the trigger waits for (a measured delay instead of a "
    "fixed 1 s), not an ability. Every count above is identical to v16 by design: 1,799 inventory, "
    "1,141 included, 658 excluded, 742 implemented keys, 55/55 bombardment.")

# ----------------------------------------------------------------- Changelog
ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-10-18"
ch.cell(row=r, column=2).value = "v17"
ch.cell(row=r, column=3).value = (
    "ROUND 116 - THE AIR-DROP WAIT IS MEASURED, NOT FIXED: THE ENEMY'S OWN VELOCITY. (1) WHAT "
    "CHANGED: the fixed 1 s dwell is REPLACED by a delay measured at the first contact of each "
    "pair - axis = normalise(caster.position - enemy.position) in x/z, v = speed * "
    "normalise(ordered_position - position), proj = dot(v,axis)/(speed*|axis|) (the cosine, clamped "
    "to +-1), delay = AIR_DROP_DWELL_MID_S - AIR_DROP_DWELL_SWING_S * proj, floored at 0. At 1.0 / "
    "1.0 s that is 0 s for an enemy running AT the caster, 1 s stationary or perpendicular and 2 s "
    "running AWAY, with every angle interpolated. (2) MEASURED ONCE: the delay is taken on the "
    "evaluation that stamps the pair and stored with the tick, the cosine and the source; it is "
    "never re-measured inside that contact (even if the enemy turns) and a re-contact measures "
    "again. (3) THE READ-VERIFICATION LOG the user asked for: every contact episode prints the RAW "
    "is_moving / is_moving_fast / slow_speed / fast_speed / position / ordered_position reads, the "
    "heading length, the cosine, the delay and the source, with UNREADABLE where a read failed, plus "
    "a shorter re-read on each waiting tick - so ordered_position() answering the current position "
    "shows up as |h|=0.0 src=no-heading instead of being assumed. (4) EVERY READ FAILS CLOSED to a "
    "zero velocity with a named source (stationary / moving-unreadable / speed-unreadable / "
    "speed-zero / pos-unreadable / no-heading / axis-degenerate / axis-unreadable) and the 1.0 s "
    "MID baseline. (5) UNCHANGED: the candidate filter (> 10 models), the nearest-by-unit_distance "
    "pick, air_only / no_melee, the self-centred cast, the fail-closed reads, the 0.2 s fast pass, "
    "POLL_MS = 250, the short-crossing fallback (0.3 s), the pair purge and the re-verifying "
    "pre-cast re-check, which now verifies the pair's OWN measured delay. (6) SHEET IMPACT: all 19 "
    "air-drop rows carry the measured-delay rule in columns 19 and 22; Definitions section 13 is "
    "retitled and section 14 is new (the formula, the constants, the source table, measured-once, "
    "the poll grid, the read-verification block, a tuning guide); Numbers is reconciled and says "
    "the counts did not move. Counts: 689 entries / 742 keys, air_drop_on_infantry 12 / 19.")
ch.cell(row=r, column=4).value = (
    "the user's rulings of 2026-10-18 ('... we do need relative velocity. But it must be calculated "
    "the moment the edge to edge distance is below our theshold ... the delay is dynamic in this "
    "way.' and 'Also include logs to check the result of the function we use, like "
    "ordered_position()'); implemented in mod_source/script/battle/mod/zz_test_deadly_onslaught.lua "
    "round 116; harness 116 (4,895 checks, 0 failures, run twice; red control 72); pack md5 "
    "0c489c2438cf9acc98730bff1b0df52b")

wb.save(DST)
print("wrote", DST)
