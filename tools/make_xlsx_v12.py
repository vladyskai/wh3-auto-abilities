"""Create WH3_abilities_master_v12_2026-10-18.xlsx from v11 (v1-v11 untouched).

v12 folds in round 111 - the moving-caster dials:
  * the CASTER is projected as position + v_caster * AIR_DROP_CASTER_DELAY_S
    * AIR_DROP_CASTER_LEAD (1.5 s x 0.5 shipped), the ENEMY by the shared
    FOURTH.AIR_DROP_DELAY_S in full - the user's field result being that a
    stationary caster is right and a moving one fires too soon;
  * 0.0 = the caster treated as stationary, 1.0 = the round-110 over-lead;
  * the tuning order ships in the row text, the Definitions and the glossary:
    one dial per test, lead first, then the caster delay, and the shared delay
    ONLY for a stationary symptom.
NO counts change: 689 entries / 742 keys, air_drop_on_infantry 12 / 19,
46 evaluators - behaviour only.
"""
import os
import shutil

import openpyxl
from openpyxl.styles import Alignment, Font

DOCS = r"C:/Users/vlady/Desktop/WH3_mod/docs"
V11 = os.path.join(DOCS, "WH3_abilities_master_v11_2026-10-18.xlsx")
V12 = os.path.join(DOCS, "WH3_abilities_master_v12_2026-10-18.xlsx")
TODAY = "2026-10-18"

WRAP = Alignment(wrap_text=True, vertical="top")

NEW_MIDDLE = (
    "THE MOVING-CASTER DIALS (round 111). The user's fourth field report, verbatim: 'I tested it. "
    "It seems to work okay when the caster is stationary, but it definitely drops the rocks too soon "
    "when in movement.' A STATIONARY caster is therefore RIGHT, so the ENEMY projection and the 6 m "
    "bound are right and are NOT touched; the error exists only while the caster MOVES and it fires "
    "TOO SOON, so the caster's projected point runs AHEAD of the real impact point and the caster's "
    "lead term is OVER-STATED. The CASTER is now projected by its OWN two dials - "
    "caster_projected = caster + v_caster * FOURTH.AIR_DROP_CASTER_DELAY_S * "
    "FOURTH.AIR_DROP_CASTER_LEAD (FOURTH.AIR_DROP_CASTER_DELAY_S = 1.5 s and "
    "FOURTH.AIR_DROP_CASTER_LEAD = 0.5 as shipped) - while the ENEMY keeps "
    "enemy_projected = enemy + v_enemy * FOURTH.AIR_DROP_DELAY_S in full (FOURTH.AIR_DROP_DELAY_S "
    "= 1.5 s); the drop fires when the "
    "PROJECTED horizontal centre-to-centre separation is inside FOURTH.AIR_DROP_CENTER_M = 6 m. At "
    "the shipped pair the caster leads by HALF its 1.5 s travel (8 m/s -> 6 m, not 12 m), and a "
    "PARKED caster is identical at every dial value because the term multiplies zero velocity. "
    "AIR_DROP_CASTER_LEAD 0.0 = the caster treated as STATIONARY (impact at the cast position - the "
    "case the field says is right); 1.0 = the round-110 behaviour that over-leads. The enemies' "
    "term, the delay it reads, the 6 m bound, FOURTH.AIR_DROP_INHERIT, air_only / no_melee, the "
    "self-centred cast on the OWNER, every fail-closed read and the pre-cast re-check are unchanged "
    "- the re-check re-projects through the SAME helper and so reads the SAME two dials. "
    "TUNING GUIDE, ONE DIAL PER TEST: fires EARLY while MOVING -> lower FOURTH.AIR_DROP_CASTER_LEAD "
    "0.5 -> 0.3 -> 0.0, and only if 0.0 is still early lower FOURTH.AIR_DROP_CASTER_DELAY_S "
    "1.5 -> 1.0 (the caster's own time - the enemy prediction does not move); still EARLY while "
    "STATIONARY -> the fall time itself is too long, lower FOURTH.AIR_DROP_DELAY_S (it shrinks BOTH "
    "bodies and returns the round-109 shape for a parked pair); NEVER fires while MOVING -> raise "
    "the lead back 0.5 -> 0.8 -> 1.0. "
    "THE VELOCITY is REBUILT, because the script API exposes NO velocity vector: battle_unit:"
    "is_moving() ('whether the unit is currently moving'), is_moving_fast() ('moving fast "
    "(running/charging)'), slow_speed() / fast_speed() ('the unit's slow/walking ... fast/running "
    "movement speed in m/s') and ordered_position() ('the position to which the unit has been "
    "ordered to move to'), so velocity = speed * normalise(ordered_position - position). LIMITS, "
    "stated: the speed is a SCALAR (a turning, braking or pushed unit is mis-estimated); "
    "ordered_position() answers the CURRENT position for a unit that is ATTACKING, so an attacker "
    "has no ordered heading; an ordered point under 0.5 m away carries no direction; and "
    "battle_unit:bearing() ('the current orientation of the main squad of the unit in degrees') is "
    "the DOCUMENTED FALLBACK, for the CASTER ONLY and only while it is moving, because the dump "
    "never states how its degrees map onto x/z. FAIL-CLOSED ALWAYS: is_moving() not exactly true -> "
    "ZERO velocity, source 'stationary'; an unreadable read -> ZERO, 'moving-unreadable'; no speed "
    "-> ZERO, 'no-speed'; no usable heading -> ZERO, 'no-heading' (the speed is still logged). "
    "Motion is never invented. "
    "WHAT THE PROJECTION CHANGES: a stationary pair behaves exactly as in round 109 (projected = "
    "current); a CLOSING pair fires EARLIER in time than the old instant test (at a larger current "
    "distance, because the gap closes during the fall) - and, since round 111, LATER than the "
    "round-110 build, because the caster's lead is halved by default; a RECEDING pair fires later or "
    "not at all; and a target CROSSING the flight path is judged at its projected point instead of "
    "where it happened to be. "
    "THE BOUND (unchanged since round 109, and unchanged by this round): the horizontal "
    "centre-to-centre distance - battle_unit:position() is 'the centre position of the main squad "
    "of the unit' (battle_unit.lua:114) - on the GROUND PLANE X/Z, because battle_vector:get_y() is "
    "HEIGHT (a 3D read would measure 30-60 m from a unit directly underneath); the engine's "
    "battle_vector:distance_xz() with a sqrt(x/z) fallback. 6 m is ONE documented constant standing "
    "in for the formation footprint - the API has NO per-unit radius / footprint / bounding box / "
    "size read (script_units:radius() is a COLLECTION's spread radius; battle_entities.radius = "
    "0.6 m is ONE model's collision radius). "
    "IF THE NO-MOMENTUM ASSUMPTION IS WRONG there is ONE FLAG to flip: FOURTH.AIR_DROP_INHERIT = "
    "true adds the caster's lead term to the impact point a SECOND time (impact = caster + "
    "v*d_caster*lead*2 - once because the caster keeps flying while the ordnance falls, once because "
    "the ordnance carries the velocity itself). The bound, the delays, the candidate set and every "
    "guard stay as they are. "
    "Infantry read: battle_unit:is_infantry() first, unit_class() exact-match inf_mel / inf_mis / "
    "inf_spr second, FAIL CLOSED. "
)

NEW_LOG = (
    "THE LOG, PER DECISION: one target line with the TWO CASTER DIALS (delay_caster=1.50s "
    "lead=0.50, plus a 'moving caster: lead=0.50 of 1.50s' fragment ONLY when the caster's velocity "
    "is non-zero), the momentum mode, the caster's current point + velocity + velocity SOURCE + "
    "projected point, the enemy's same four, the PROJECTED centre separation, the instant "
    "separation, the bound, the edge gap (diagnostic only) and air_only; the same dials are printed "
    "on the 'watch:' why-not line and on both pre-cast re-check lines; and, when nothing qualifies, "
    "a 'watch: nearest INFANTRY ... centre=~Nm vs bound=6m -> NOT under the caster [projected "
    "sep=~Nm after delay=1.50s; caster v=... (delay_caster=1.50s lead=0.50); enemy v=... src=...]' "
    "line (5 m bands, only while the nearest projected separation is inside 30 m). "
)

NEW_DEF = (
    "an enemy INFANTRY unit that will be UNDER the caster WHEN THE ORDNANCE LANDS: the CASTER is "
    "projected by its OWN two dials - FOURTH.AIR_DROP_CASTER_DELAY_S = 1.5 s and "
    "FOURTH.AIR_DROP_CASTER_LEAD = 0.5, i.e. caster_projected = caster + v_caster * caster_delay * "
    "lead - and the ENEMY by FOURTH.AIR_DROP_DELAY_S = 1.5 s in full (a TUNABLE constant - no row "
    "carries a fall time), and the horizontal CENTRE-TO-CENTRE separation of the two PROJECTED "
    "points (battle_unit:position(), X/Z only - get_y is HEIGHT) must be inside "
    "FOURTH.AIR_DROP_CENTER_M = 6 m. The ordnance does NOT inherit the caster's velocity (the "
    "user's assumption), so it lands straight down from the caster's position at release: impact = "
    "caster + v_caster*caster_delay*lead. WHY THE DIALS EXIST (round 111): the field result is that "
    "a STATIONARY caster is right but a MOVING one fires too soon, so only the caster's lead was "
    "over-stated - 0.0 = the caster treated as stationary, 1.0 = the round-110 over-lead, and the "
    "shipped 0.5 halves the lead. Velocity is rebuilt from is_moving() / is_moving_fast() / "
    "slow_speed() / fast_speed() plus a heading from ordered_position(); bearing() is the "
    "CASTER-ONLY fallback while moving; every unreadable read is ZERO velocity with a named source "
    "(stationary / moving-unreadable / no-speed / no-heading) - motion is never invented. 6 m "
    "stands in for the formation footprint (the API has no per-unit radius / bbox / size read); "
    "lower it if the drop is still early, raise it if it never fires. TUNING ORDER, ONE DIAL PER "
    "TEST: early while MOVING -> AIR_DROP_CASTER_LEAD 0.5 -> 0.3 -> 0.0, then "
    "AIR_DROP_CASTER_DELAY_S 1.5 -> 1.0; early while STATIONARY -> AIR_DROP_DELAY_S (both bodies); "
    "never fires while MOVING -> lead 0.5 -> 0.8 -> 1.0. ONE FLAG if the assumption is wrong: "
    "FOURTH.AIR_DROP_INHERIT = true adds the lead term a second time. The caster must be airborne "
    "where the row says so (`grounded` or a flying-only carrier) and OUT of melee where the row "
    "says so (`engaged_in_melee`); the pre-cast re-check RE-PROJECTS both bodies with the SAME "
    "dials and skips the cast rather than spending it."
)

CONST_ROWS = [
    ("FOURTH.AIR_DROP_CASTER_DELAY_S", "1.5 (s) - NEW in round 111",
     "THE CASTER'S OWN LEAD TIME. How far ahead the CASTER's impact point is projected, independent "
     "of the enemy's delay. 1.5 = the shared fall time; lower it (1.5 -> 1.0) only when the lead "
     "factor alone cannot cure an early release. It never moves the enemy prediction."),
    ("FOURTH.AIR_DROP_CASTER_LEAD", "0.5 - NEW in round 111",
     "THE CASTER LEAD FACTOR - the user-tunable knob for MOVING casters. The caster is projected "
     "caster + v_caster * caster_delay * this. 1.0 = the round-110 behaviour that over-leads "
     "(the reported bug); 0.0 = the caster treated as STATIONARY, impact at the cast position (the "
     "case the field says is right); 0.5 ships = half the caster's own travel. Lower it if a moving "
     "drop is still early (0.5 -> 0.3 -> 0.0); raise it if it never fires while moving "
     "(0.5 -> 0.8 -> 1.0)."),
    ("FOURTH.AIR_DROP_DELAY_S", "1.5 (s) - round 110",
     "THE ENEMY'S PROJECTION and the shared fall time - UNCHANGED by round 111 and NOT the dial to "
     "touch for a moving caster. It scales BOTH bodies: lower it only when a STATIONARY caster is "
     "still early (the fall time itself is too long); raising it moves both projections equally."),
    ("FOURTH.AIR_DROP_CENTER_M", "6 (m) - round 109",
     "THE BOUND - unchanged. The horizontal centre-to-centre separation that counts as 'under'. It "
     "stands in for the formation footprint because the script API exposes no per-unit radius / "
     "footprint / bbox / size read. Lower it if the drop still releases early at ANY caster speed; "
     "raise it if it never fires."),
    ("FOURTH.AIR_DROP_INHERIT", "false - round 110",
     "THE MOMENTUM FLAG. false = the ordnance does NOT inherit the caster's velocity, so the impact "
     "is straight down from the release point. true = v_caster * caster_delay * lead is added a "
     "SECOND time. Flip this ONE flag only if the field shows the rocks landing ahead of the release "
     "point after the lead dial has been tuned."),
]

TUNING_ROWS = [
    ("fires EARLY while MOVING", "FOURTH.AIR_DROP_CASTER_LEAD",
     "0.5 -> 0.3 -> 0.0; if 0.0 is still early, then FOURTH.AIR_DROP_CASTER_DELAY_S 1.5 -> 1.0. "
     "This is the reported symptom: the caster's projected point runs ahead of the real impact "
     "point."),
    ("still EARLY while STATIONARY", "FOURTH.AIR_DROP_DELAY_S",
     "The lead term is inert for a parked caster, so the shared fall time itself is too long: "
     "1.5 -> 1.2 -> 1.0. It shrinks BOTH bodies."),
    ("NEVER fires while MOVING", "FOURTH.AIR_DROP_CASTER_LEAD",
     "0.5 -> 0.8 -> 1.0 (1.0 = the round-110 behaviour). The lead has been cut too far."),
]


def set_wrapped(ws, row, col, value, bold=False):
    c = ws.cell(row=row, column=col, value=value)
    c.alignment = WRAP
    if bold:
        c.font = Font(bold=True)
    return c


if os.path.exists(V12):
    os.remove(V12)
shutil.copy2(V11, V12)

wb = openpyxl.load_workbook(V12)

# ------------------------------------------------------------------ Abilities
ab = wb["Abilities"]
hdr = [c.value for c in ab[1]]
col = {h: i + 1 for i, h in enumerate(hdr)}
trig = col["Trigger (as implemented)"]

changed = 0
for r in range(2, ab.max_row + 1):
    if ab.cell(row=r, column=col["Trigger family"]).value != "air_drop_on_infantry":
        continue
    v = ab.cell(row=r, column=trig).value or ""
    old_lead = "air_drop_on_infantry (rounds 107-110; the WHEN rule CHANGED in round 110)"
    assert v.startswith(old_lead), (r, v[:90])
    assert "TWO-BODY RELATIVE-MOTION PREDICTION (round 110)." in v, (r, "no round-110 middle")
    a = v.find("TWO-BODY RELATIVE-MOTION PREDICTION (round 110).")
    k = v.find("Infantry read: battle_unit:is_infantry()")
    b = v.find("THE LOG, PER DECISION: one target line with the delay, the momentum mode,")
    assert 0 < a < k < b, (r, a, k, b)
    new = (v[:a]
           .replace(old_lead, "air_drop_on_infantry (rounds 107-111; the WHEN rule CHANGED in round "
                              "110, the CASTER's own lead in round 111)")
           + NEW_MIDDLE
           + NEW_LOG
           + v[b + len("THE LOG, PER DECISION: one target line with the delay, the momentum mode,"):])
    ab.cell(row=r, column=trig).value = new
    ab.cell(row=r, column=trig).alignment = WRAP
    changed += 1
assert changed == 19, changed
print("abilities rows updated:", changed)

# the status-reason cell of those rows names the rule rounds
for r in range(2, ab.max_row + 1):
    if ab.cell(row=r, column=col["Trigger family"]).value != "air_drop_on_infantry":
        continue
    sr = ab.cell(row=r, column=col["Status reason / family"]).value or ""
    if "round 111" not in sr:
        ab.cell(row=r, column=col["Status reason / family"]).value = (
            sr + " | trigger rule: rounds 107-111 (two-body projection; caster lead = "
                 "AIR_DROP_CASTER_DELAY_S 1.5 s x AIR_DROP_CASTER_LEAD 0.5, enemy full delay, "
                 "bound 6 m, no momentum inheritance)")

# ---------------------------------------------------------------- Definitions
df = wb["Definitions"]
df.cell(row=1, column=1, value="DEFINITIONS - WH3 ability master v12 (%s)" % TODAY)
assert df.cell(row=69, column=1).value == "air_drop_on_infantry", df.cell(row=69, column=1).value
set_wrapped(df, 69, 3, NEW_DEF)

last = df.max_row
while last > 1 and all(df.cell(row=last, column=c).value in (None, "") for c in range(1, 7)):
    last -= 1
print("definitions last used row:", last)
r0 = last + 2
h = df.cell(row=r0, column=1,
            value="9. THE MOVING-CASTER DIALS (round 111) - ONLY THE CASTER'S LEAD MOVES")
h.font = Font(bold=True, size=12)
set_wrapped(df, r0 + 1, 1, "Constant", bold=True)
set_wrapped(df, r0 + 1, 2, "Ships as", bold=True)
set_wrapped(df, r0 + 1, 3, "What it does / how to tune it", bold=True)
for i, (name, val, why) in enumerate(CONST_ROWS):
    rr = r0 + 2 + i
    set_wrapped(df, rr, 1, name)
    set_wrapped(df, rr, 2, val)
    set_wrapped(df, rr, 3, why)

g0 = r0 + 2 + len(CONST_ROWS) + 1
g = df.cell(row=g0, column=1,
            value="TUNING GUIDE (round 111) - change ONE dial per field test, in this order")
g.font = Font(bold=True, size=12)
set_wrapped(df, g0 + 1, 1, "Symptom", bold=True)
set_wrapped(df, g0 + 1, 2, "Dial to change", bold=True)
set_wrapped(df, g0 + 1, 3, "Order to try", bold=True)
for i, (sym, dial, order) in enumerate(TUNING_ROWS):
    rr = g0 + 2 + i
    set_wrapped(df, rr, 1, sym)
    set_wrapped(df, rr, 2, dial)
    set_wrapped(df, rr, 3, order)
set_wrapped(df, g0 + 2 + len(TUNING_ROWS), 1, "TOTAL", bold=True)
set_wrapped(df, g0 + 2 + len(TUNING_ROWS), 2, "1 rule",
            bold=True)
set_wrapped(df, g0 + 2 + len(TUNING_ROWS), 3,
            "One dial changes per test so the field log (which prints delay_caster and lead on every "
            "decision) says which term moved the impact point. The pair (1.5 s, 0.5) is the "
            "starting point; the bound and the shared delay are NOT moving-caster dials. None of "
            "this changes any count, carrier family or evaluator.")

# -------------------------------------------------------------------- Numbers
nm = wb["Numbers"]
for r in range(1, nm.max_row + 1):
    v = nm.cell(row=r, column=1).value
    if not isinstance(v, str):
        continue
    if v.startswith("Date: 2026-10-18"):
        nm.cell(row=r, column=1).value = (
            "Date: 2026-10-18     Rule in force since: 2026-10-17     Inventory: 1,799 active "
            "abilities     (v12: round 111 - ONLY THE CASTER'S LEAD MOVES: the caster is projected "
            "by its own dials, FOURTH.AIR_DROP_CASTER_DELAY_S = 1.5 s x FOURTH.AIR_DROP_CASTER_LEAD "
            "= 0.5, while the enemy keeps FOURTH.AIR_DROP_DELAY_S = 1.5 s in full and the same 6 m "
            "bound; the field result is that a stationary caster is right and a moving one fired "
            "too soon, so 0.0 = caster treated as stationary and 1.0 = the round-110 over-lead)")
    elif v.startswith("Trigger families after round 110"):
        nm.cell(row=r, column=1).value = v.replace("round 110", "round 111")
    elif v.startswith("Reconciliation: included"):
        nm.cell(row=r, column=1).value = (
            "Reconciliation: included 1,141 + excluded 658 = 1,799. Implemented among the included "
            "742 + not implemented 399 = 1,141. The mod's ABILITIES table is 689 entries / 742 keys "
            "(the two Soulfire keys are ONE entry, the two Slicing Shards keys are ONE entry). The "
            "tracker carries the implemented ROWS; implemented keys with no row of their own ride a "
            "row that names its sibling. Round 111 is a BEHAVIOUR-ONLY change: the air-drop family "
            "stays 12 entries / 19 keys, the 46 trigger families are unchanged, and every count on "
            "this sheet - inventory 1,799, excluded 658, included 1,141, implemented 742, not "
            "implemented 399, the eight carrier families, the 46 evaluator rows - is IDENTICAL to "
            "v11. What changed: the trigger text of those 19 rows (they name the two caster dials "
            "and the tuning order), the rule itself, and TWO NEW DIALS in the Definitions "
            "(FOURTH.AIR_DROP_CASTER_DELAY_S = 1.5 s and FOURTH.AIR_DROP_CASTER_LEAD = 0.5, with "
            "the tuning guide). FOURTH.AIR_DROP_DELAY_S, the 6 m bound and AIR_DROP_INHERIT are "
            "unchanged."
        )

# ------------------------------------------------------------------ Changelog
cl = wb["Changelog"]
row = cl.max_row + 1
while row > 1 and all(cl.cell(row=row - 1, column=c).value in (None, "") for c in range(1, 5)):
    row -= 1
cl.cell(row=row, column=1).value = TODAY
cl.cell(row=row, column=2).value = "v12"
cl.cell(row=row, column=3).value = (
    "ROUND 111 - THE MOVING-CASTER DIALS (ONLY THE CASTER'S LEAD MOVES). (1) WHAT THE FIELD SAID, "
    "verbatim: 'I tested it. It seems to work okay when the caster is stationary, but it definitely "
    "drops the rocks too soon when in movement. How do we tune it?' (2) THE READING: a stationary "
    "caster is RIGHT, so the ENEMY projection and the 6 m bound are right and are NOT touched; the "
    "error exists only while the caster MOVES and it fires TOO SOON, so the caster's projected point "
    "runs ahead of the real impact point - the caster's lead term is OVER-STATED. Round 110 gave it "
    "the full 1.5 s (12 m of lead at 8 m/s); in practice the release happens part-way through the "
    "wind-up, or the flier has already turned into the pass. (3) THE RULE: "
    "caster_projected = caster + v_caster * FOURTH.AIR_DROP_CASTER_DELAY_S * "
    "FOURTH.AIR_DROP_CASTER_LEAD (1.5 s, 0.5 shipped) and enemy_projected = enemy + v_enemy * "
    "FOURTH.AIR_DROP_DELAY_S in full; fire when the PROJECTED horizontal centre separation is inside "
    "the same FOURTH.AIR_DROP_CENTER_M = 6 m. 0.0 = the caster treated as STATIONARY (impact at the "
    "cast position - the field-correct case), 1.0 = the round-110 behaviour; the shipped pair halves "
    "the caster's lead (8 m/s -> 6 m, not 12 m) and leaves a PARKED caster identical at every value. "
    "(4) TUNING ORDER, ONE DIAL PER TEST: fires early while MOVING -> AIR_DROP_CASTER_LEAD "
    "0.5 -> 0.3 -> 0.0, then AIR_DROP_CASTER_DELAY_S 1.5 -> 1.0; still early while STATIONARY -> "
    "AIR_DROP_DELAY_S (the fall time itself, both bodies); never fires while MOVING -> lead "
    "0.5 -> 0.8 -> 1.0. (5) THE LOG: the decision line, the watch line and both pre-cast lines print "
    "delay_caster=..s lead=.., plus 'moving caster: lead=0.50 of 1.50s' ONLY when the caster's "
    "velocity is non-zero. (6) KEPT EXACTLY: the enemy term and its delay, the 6 m bound, "
    "AIR_DROP_INHERIT, air_only / no_melee, the self-centred cast, fail-closed reads, the 70% map "
    "exemption, and the pre-cast re-check that re-projects through the SAME helper (same two dials). "
    "(7) COUNTS: UNCHANGED - 689 entries / 742 keys, air_drop_on_infantry 12 entries / 19 keys, 46 "
    "evaluators. Harness 111: 4387 checks / 0 failures (run twice, byte-identical); red control (the "
    "round-110 build) 41 failures, ALL in the new section. Installed pack md5 "
    "651f12e61284cae472bb06bf3a66b87d."
)
cl.cell(row=row, column=4).value = (
    "the user's fourth air-drop field report and their question ('How do we tune it?'); harness 111 "
    "(worlds A stationary-unchanged, B lead 1.0 reproduces the early release, D lead 0.5 fires later, "
    "E lead 0.0 = stationary, F caster delay independent of the enemy term, G the pre-cast re-check "
    "uses the same dials) with its one-line dial VARIANT files; docs/WH3_round111_airdrop_movingcaster.md."
)
for c in range(1, 5):
    cl.cell(row=row, column=c).alignment = WRAP

wb.save(V12)
print("saved", V12, os.path.getsize(V12))

# ---------------------------------------------------------------- verify from disk
wb2 = openpyxl.load_workbook(V12)
a2 = wb2["Abilities"]
h2 = [c.value for c in a2[1]]
i2 = {h: n + 1 for n, h in enumerate(h2)}
air = [r for r in range(2, a2.max_row + 1)
       if a2.cell(row=r, column=i2["Trigger family"]).value == "air_drop_on_infantry"]
texts = [(r, a2.cell(row=r, column=i2["Trigger (as implemented)"]).value or "") for r in air]
need = ["FOURTH.AIR_DROP_CASTER_DELAY_S = 1.5 s", "FOURTH.AIR_DROP_CASTER_LEAD = 0.5",
        "FOURTH.AIR_DROP_DELAY_S = 1.5 s", "FOURTH.AIR_DROP_CENTER_M = 6 m",
        "FOURTH.AIR_DROP_INHERIT", "THE MOVING-CASTER DIALS (round 111)",
        "delay_caster=1.50s", "moving caster: lead=0.50 of 1.50s",
        "0.5 -> 0.3 -> 0.0", "NEVER fires while MOVING", "ONE DIAL PER TEST",
        "RE-TAKEN"]
bad = [(r, [x for x in need if x not in t]) for r, t in texts if any(x not in t for x in need)]
stale = [(r, t) for r, t in texts if "TWO-BODY RELATIVE-MOTION PREDICTION (round 110)." in t]
print("VERIFY air rows:", len(air), "| missing new rule:", [(r, m) for r, m in bad],
      "| stale round-110 middle:", [r for r, _ in stale])
assert len(air) == 19 and not bad and not stale

d2 = wb2["Definitions"]
assert "FOURTH.AIR_DROP_CASTER_LEAD" in (d2.cell(row=69, column=3).value or "")
assert "FOURTH.AIR_DROP_CASTER_DELAY_S" in (d2.cell(row=69, column=3).value or "")
const_names = [d2.cell(row=r, column=1).value for r in range(1, d2.max_row + 1)]
for want in ("FOURTH.AIR_DROP_CASTER_DELAY_S", "FOURTH.AIR_DROP_CASTER_LEAD",
             "FOURTH.AIR_DROP_DELAY_S", "FOURTH.AIR_DROP_CENTER_M", "FOURTH.AIR_DROP_INHERIT"):
    assert want in const_names, want
tuning = [n for n in const_names if isinstance(n, str) and n.startswith("fires EARLY")]
assert tuning, "the tuning-guide table is missing"
print("VERIFY definitions: 5 constant rows + tuning guide present; air_drop glossary row updated")

n2 = wb2["Numbers"]
print("VERIFY numbers header:", (n2.cell(row=7, column=1).value or "")[:110])
print("VERIFY numbers family header:", (n2.cell(row=42, column=1).value or "")[:80])
print("VERIFY changelog last:", wb2["Changelog"].cell(row=wb2["Changelog"].max_row, column=2).value)
print("VERIFY definitions title:", d2.cell(row=1, column=1).value)
counts = {}
for r in range(2, a2.max_row + 1):
    st = a2.cell(row=r, column=i2["Status"]).value
    counts[st] = counts.get(st, 0) + 1
print("VERIFY status counts:", counts)
