#!/usr/bin/env python3
"""Build WH3_abilities_master_v16_2026-10-18.xlsx from v15.

Round 115: the air-drop trigger WAITS - a per-pair 1-second dwell plus the
short-crossing fallback.  This edits, on all 19 air-drop rows:
  * column 19 (Status reason / family)  - the trigger-rule summary
  * column 22 (Trigger, as implemented) - the full evaluator text
and adds: Definitions section 13 (the two constants + the dwell semantics + its
log lines + a tuning guide), a Numbers reconciliation note, and the v16
Changelog row.  v1-v15 stay byte-unchanged (a NEW filename is written).
"""
import openpyxl

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v15_2026-10-18.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v16_2026-10-18.xlsx"

wb = openpyxl.load_workbook(SRC)
ws = wb["Abilities"]

OLD_SUMMARY_MARK = "trigger rule: round 114 - THE SIMPLE EDGE-GAP RULE"
NEW_SUMMARY = (
    "trigger rule: round 115 - THE EDGE-GAP RULE PLUS A 1-SECOND DWELL ON THE PAIR: the "
    "nearest ALIVE enemy with MORE THAN 10 models whose battle_unit:unit_distance "
    "(EDGE-TO-EDGE) is BELOW 0.10 m, AND the pair must stay under that line CONTINUOUSLY "
    "for AIR_DROP_DWELL_S = 1.0 s before the drop is cast; a separation before that "
    "cancels the dwell (the time actually under and the separation gap are logged), and a "
    "separation after AIR_DROP_MIN_CONTACT_S = 0.3 s of contact fires on the separation "
    "evaluation (the short-crossing fallback); no infantry filter, no single-entity test, no "
    "projection / lead / frontage / path; a separate 0.2 s fast pass re-runs the same "
    "evaluator while a valid enemy is inside 30 m but adds NO time - the dwell clock is the "
    "poll's own 250 ms tick_count; the global poll is untouched. air_only / no_melee as the "
    "row declares them; self-centred cast; pre-cast re-check re-measures the edge gap, "
    "re-validates the model counts and RE-VERIFIES the dwell on fresh handles.")

OLD_DECISION = ("THE DECISION IS ONE COMPARISON: fire when battle_unit:unit_distance(caster, "
                "enemy) - the engine's EDGE-TO-EDGE distance in metres (battle_unit.lua:160) "
                "- is BELOW FOURTH.AIR_DROP_EDGE_M = 0.10 m.")

NEW_DECISION = (
    "THE DECISION IS ONE COMPARISON - AND IT MUST LAST (round 115): UNDER means "
    "battle_unit:unit_distance(caster, enemy) - the engine's EDGE-TO-EDGE distance in "
    "metres (battle_unit.lua:160) - is BELOW FOURTH.AIR_DROP_EDGE_M = 0.10 m; FIRE means "
    "that PAIR has been UNDER CONTINUOUSLY for FOURTH.AIR_DROP_DWELL_S = 1.0 s. THE DWELL, "
    "IN FULL, on the user's ruling 'I mean the trigger fires too soon. So we need a delay "
    "of 1 second for the trigger.': when the NEAREST valid enemy's edge gap first drops "
    "below AIR_DROP_EDGE_M the PAIR (caster ui id, enemy ui id) is stamped with the poll "
    "tick it happened on and NOTHING is cast - the first evaluation of a contact can NEVER "
    "fire. The pair fires only once it has been continuously under the line for "
    "AIR_DROP_DWELL_S = 1.0 s on the poll's own clock - the poll's own tick count "
    "(tick_count, one poll = POLL_MS = 250 ms, so the stamp plus four further polls) - "
    "with both units still valid at the pre-cast re-check, which RE-VERIFIES the dwell on "
    "fresh handles as well as re-measuring the gap. A separation before that CANCELS the dwell and logs how long the "
    "pair was actually under plus the gap it separated to (that line is the tuning datum). A "
    "separation after FOURTH.AIR_DROP_MIN_CONTACT_S = 0.3 s of contact FIRES on the "
    "SEPARATION EVALUATION instead - the SHORT-CROSSING FALLBACK, so a quick pass through "
    "the formation is not silently lost. A re-contact after a separation starts a FRESH "
    "dwell (the old stamp is dropped, never inherited), and the pair row is PURGED with the "
    "unit, caster or enemy. THE TWO NEW CONSTANTS: AIR_DROP_DWELL_S = 1.0 s (the dwell) and "
    "AIR_DROP_MIN_CONTACT_S = 0.3 s (the short-crossing floor).")

OLD_LOG_ANCHOR = " WHY THE EDGE GAP: it is the number the user asked for"
NEW_LOG = (
    " THE DWELL LINES, one per EPISODE (event-driven, not change-gated): "
    "'[<ui id>] <marker> dwell started: under at gap <d.dd>m, waiting 1.00s (pair "
    "'<enemy key>')'; '... dwell: under <t.t>s of 1.00s (gap <d.dd>m)' on each hold while "
    "the dwell runs; '... dwell satisfied after <t.t>s -> FIRING (gap <d.dd>m, pair "
    "'<enemy key>')'; '... dwell cancelled: separated after <t.t>s (gap <d.dd>m; the dwell "
    "is 1.00s and the short-crossing floor is 0.30s)'; '... short crossing: under for "
    "<t.t>s (>= 0.30s) -> FIRING on separation (gap <d.dd>m, the dwell is 1.00s)'. The "
    "pre-cast re-check now also writes '(dwell <t.t>s of <floor>s)' on the firing line, or "
    "'(short crossing: held <t.t>s of <floor>s)', and its SKIPPED line carries 'gap_ok=', "
    "'dwell=', 'dwell_ok=' and 'short_cross='." + OLD_LOG_ANCHOR)

rows = 0
for r in range(2, ws.max_row + 1):
    if ws.cell(row=r, column=21).value != "air_drop_on_infantry":
        continue
    rows += 1
    summary = ws.cell(row=r, column=19).value
    assert OLD_SUMMARY_MARK in summary, "row %d: the round-114 summary is not there" % r
    head, sep, _tail = summary.partition(" | ")
    ws.cell(row=r, column=19).value = head + " | " + NEW_SUMMARY

    trig = ws.cell(row=r, column=22).value
    assert OLD_DECISION in trig, "row %d: the decision sentence is not there" % r
    assert OLD_LOG_ANCHOR in trig and "AIR_DROP_DWELL_S" not in trig
    trig = trig.replace(OLD_DECISION, NEW_DECISION)
    trig = trig.replace(OLD_LOG_ANCHOR, NEW_LOG, 1)
    ws.cell(row=r, column=22).value = trig

assert rows == 19, "expected 19 air-drop rows, edited %d" % rows

# ---------------------------------------------------------------- Definitions
d = wb["Definitions"]
assert d.cell(row=187, column=1).value.startswith("12. THE AIR-DROP RULE IN FORCE (round 114)")
d.cell(row=187, column=1).value = ("12. THE AIR-DROP RULE IN FORCE (round 115) - ONE COMPARISON, "
                                   "A 1-SECOND DWELL ON THE PAIR, AND A 0.2 s FAST PASS")
d.cell(row=197, column=1).value = "TOTAL"
d.cell(row=197, column=2).value = ("4 knobs + 2 dwell constants (section 13) - one rule, six "
                                   "constants, no per-row edit anywhere.")

base = d.max_row + 2
sec = [
    ("13. THE DWELL (round 115) - THE TRIGGER WAITS INSTEAD OF LEADING", None, None),
    ("THE USER'S RULING, verbatim", "'I mean the trigger fires too soon. So we need a delay of 1 second for the trigger.'", None),
    ("What FIRE means now", "UNDER is not FIRE. UNDER = the nearest valid enemy's edge-to-edge gap is below AIR_DROP_EDGE_M (0.10 m). FIRE = that PAIR has been UNDER continuously for AIR_DROP_DWELL_S (1.0 s), with both units still valid at the pre-cast re-check. The first evaluation of a contact stamps the pair and NEVER fires.", None),
    ("The pair state", "ONE row per (caster ui id, enemy ui id), nested as FOURTH.ad_pair[caster][enemy] (no composite string key anywhere in the file). A row holds ONE timestamp - the poll tick the contact started on. No gap history, no closing rate, no velocity.", None),
    ("The dwell clock", "tick_count, the poll's own counter: one poll = POLL_MS = 250 ms, so 1.0 s of dwell is the stamp plus FOUR further polls. The fast pass adds EVALUATIONS (5/s) but never time - it fires the moment the poll's clock completes the dwell. No engine clock is read (os.clock's meaning in this Lua state is unproven), and a missed poll can make a pair wait LONGER, never fire early: the drop lands between 1.00 s and 1.25 s after contact.", None),
    ("THE TWO CONSTANTS", None, None),
    ("Constant", "Ships as", "What it does / how to tune it"),
    ("FOURTH.AIR_DROP_DWELL_S", "1.0 (s)", "How long the pair must stay under the 0.10 m line before the drop is cast. THIS IS THE KNOB FOR 'fires too soon' vs 'too late': raise it to wait longer, lower it to fire sooner. It must stay ABOVE AIR_DROP_MIN_CONTACT_S or the fallback would fire everything."),
    ("FOURTH.AIR_DROP_MIN_CONTACT_S", "0.3 (s)", "The SHORT-CROSSING FLOOR. If the pair separates BEFORE the dwell is complete but had been under for at least this long, the drop fires ON the separation evaluation instead of being cancelled - a quick pass through the formation is not lost. Lower it to catch even briefer crossings; raise it to require a more deliberate overlap."),
    ("THE SHORT-CROSSING FALLBACK, mechanically", "separation evaluation only", "On the evaluation that first sees the gap back at/over 0.10 m: if (time under) >= AIR_DROP_MIN_CONTACT_S the cast is issued THERE (the pre-cast re-check accepts it although the gap is over the line BY CONSTRUCTION, and logs the measured gap plus '(short crossing: held <t.t>s of <floor>s)'); otherwise the dwell is cancelled and logged. Nothing else can fire a short crossing."),
    ("THE DWELL LINES (one per episode, not change-gated)", None, None),
    ("[<ui>] <marker> dwell started: under at gap <d>m, waiting 1.00s (pair '<key>')", "written when the contact is stamped", "the first evaluation of a contact. It NEVER cast."),
    ("[<ui>] <marker> dwell: under <t.t>s of 1.00s (gap <d>m)", "written on each hold", "the running time under, so a battle log shows the pair approaching the line."),
    ("[<ui>] <marker> dwell satisfied after <t.t>s -> FIRING (gap <d>m, pair '<key>')", "written once, on the cast", "the dwell was earned. The pre-cast re-check follows with '-> FIRING (re-checked) (dwell <t.t>s of 1.00s)'."),
    ("[<ui>] <marker> dwell cancelled: separated after <t.t>s (gap <d>m; the dwell is 1.00s and the short-crossing floor is 0.30s)", "written once, on the separation", "the pair left the line before the dwell AND before the floor: nothing was cast. THE TUNING DATUM - the time under in this line is what tells you whether AIR_DROP_DWELL_S is too long for the crossings you are flying."),
    ("[<ui>] <marker> short crossing: under for <t.t>s (>= 0.30s) -> FIRING on separation (gap <d>m, the dwell is 1.00s)", "written once, on the separation", "the fallback fired. The re-check line adds '(short crossing: held <t.t>s of 0.30s)'."),
    ("PURGE", "drop_unit_by_ui_id", "A dropped unit's pair rows are removed with it, as caster (its whole slot) or as enemy (that one row). One named global hook (zz_ad_dwell_purge) carries the call because the drop routine is declared above the FOURTH bag and the chunk is at Lua's 200-local ceiling."),
    ("TUNING GUIDE (round 115) - ONE CHANGE PER FIELD TEST", None, None),
    ("Symptom", "What to change", "Order to try"),
    ("drops still leave too early - it fires the instant the boxes touch", "AIR_DROP_DWELL_S", "1.0 -> 1.5 -> 2.0. Read the 'dwell satisfied after <t>s' line: it prints exactly how long the pair had held."),
    ("drops feel late - the formation is already past", "AIR_DROP_DWELL_S", "1.0 -> 0.7 -> 0.5, but keep it above AIR_DROP_MIN_CONTACT_S. If most contacts end with 'dwell cancelled: separated after 0.50s' the dwell is simply longer than the crossings you get."),
    ("quick crossings are being missed entirely (nothing fires as blocks sweep past)", "AIR_DROP_MIN_CONTACT_S", "0.3 -> 0.2 -> 0.1. Each contact that ends under the floor logs its own 'dwell cancelled ... separated after <t>s' line, so the log says what floor would have caught it."),
    ("the fallback fires when it should not", "AIR_DROP_MIN_CONTACT_S", "0.3 -> 0.5 -> 0.75. The 'short crossing: under for <t>s' line tells you how much contact each fallback fire actually had."),
    ("TOTAL", "2 constants, 1 clock", "The dwell is measured on the poll's clock and every episode is logged with its time under, so one field battle is enough to pick the next value."),
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
assert n.cell(row=42, column=1).value.startswith("Trigger families after round 113")
n.cell(row=42, column=1).value = ("Trigger families after round 115 - re-counted from the mod "
                                  "(689 entries / 742 keys; round 115 changed NO count)")
n.cell(row=101, column=1).value = ("Round 115 reconciliation: the air-drop row is unchanged at "
                                   "12 entries / 19 keys and the mod at 689 / 742 - the round "
                                   "added a TRIGGER CONDITION (the 1 s dwell), not an ability. "
                                   "Every count above is identical to v15 by design.")

# ----------------------------------------------------------------- Changelog
ch = wb["Changelog"]
r = ch.max_row + 1
ch.cell(row=r, column=1).value = "2026-10-18"
ch.cell(row=r, column=2).value = "v16"
ch.cell(row=r, column=3).value = (
    "ROUND 115 - THE AIR-DROP TRIGGER WAITS: A 1-SECOND DWELL ON THE PAIR, PLUS THE "
    "SHORT-CROSSING FALLBACK. (1) WHAT CHANGED: UNDER (edge gap < 0.10 m) is no longer FIRE. "
    "The pair (caster ui id, enemy ui id) is stamped when it first goes under and NOTHING is "
    "cast; the drop fires only once that pair has held under the line continuously for "
    "FOURTH.AIR_DROP_DWELL_S = 1.0 s, measured on the poll's own clock (tick_count, 250 ms - "
    "the stamp plus four further polls). (2) THE FALLBACK: a separation before the dwell "
    "cancels it (logging the time actually under and the separation gap); a separation after "
    "FOURTH.AIR_DROP_MIN_CONTACT_S = 0.3 s of contact FIRES on the separation evaluation, so "
    "a quick pass is not lost. (3) A RE-CONTACT STARTS A FRESH DWELL, the first evaluation of "
    "a contact can never fire, and the pair rows are PURGED with the unit. (4) THE PRE-CAST "
    "RE-CHECK re-measures the gap AND re-verifies the dwell on fresh handles. (5) UNCHANGED: "
    "the candidate filter (> 10 models), the nearest-by-unit_distance pick, air_only / "
    "no_melee, the self-centred cast, the fail-closed reads, the 0.2 s fast pass (which adds "
    "evaluations, never time), POLL_MS = 250 and every gate in FOURTH.try_pair. (6) SHEET "
    "IMPACT: all 19 air-drop rows carry the dwell clause and the fallback in columns 19 and "
    "22; Definitions section 12 is retitled and section 13 is new (the two constants, the "
    "clock, the five dwell lines, the purge and a tuning guide); Numbers is unchanged and "
    "says so. Counts: 689 entries / 742 keys, air_drop_on_infantry 12 / 19.")
ch.cell(row=r, column=4).value = (
    "the user's ruling of 2026-10-18 ('I mean the trigger fires too soon. So we need a delay "
    "of 1 second for the trigger.'); implemented in mod_source/script/battle/mod/"
    "zz_test_deadly_onslaught.lua round 115; harness 115 (4,739 checks); pack md5 "
    "56ef53853b74e2ee9e07ac5e343ce78a")

wb.save(DST)
print("wrote", DST)
