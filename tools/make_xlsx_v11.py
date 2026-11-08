"""Create WH3_abilities_master_v11_2026-10-18.xlsx from v10 (v1-v10 untouched).

v11 folds in round 110 - the two-body relative-motion prediction:
  * the air-drop family fires when the CASTER and the ENEMY, both projected
    forward by FOURTH.AIR_DROP_DELAY_S = 1.5 s, are inside the 6 m centre bound;
  * the ordnance does NOT inherit the caster's velocity (the user's assumption),
    so the impact is straight down from the release point; ONE flag
    (FOURTH.AIR_DROP_INHERIT) adds v*t a second time if the field disproves it;
  * the velocity is rebuilt from is_moving / is_moving_fast / slow_speed /
    fast_speed + a heading from ordered_position (bearing = caster-only
    fallback), and every unreadable read is ZERO velocity with a named source.
NO counts change: 689 entries / 742 keys, air_drop_on_infantry 12 / 19,
46 evaluators - behaviour only.
"""
import os
import shutil

import openpyxl
from openpyxl.styles import Alignment, Font

DOCS = r"C:/Users/vlady/Desktop/WH3_mod/docs"
V10 = os.path.join(DOCS, "WH3_abilities_master_v10_2026-10-18.xlsx")
V11 = os.path.join(DOCS, "WH3_abilities_master_v11_2026-10-18.xlsx")
TODAY = "2026-10-18"

WRAP = Alignment(wrap_text=True, vertical="top")

NEW_LEAD = (
    "air_drop_on_infantry (rounds 107-110; the WHEN rule CHANGED in round 110): the row has NO "
    "target flags at all (target_friends / target_enemies / target_ground / target_self all false), "
    "effect_range 0 and target_intercept_range 10, so the engine drops where the CASTER is and the "
    "only decision is WHEN. "
)

NEW_MIDDLE = (
    "TWO-BODY RELATIVE-MOTION PREDICTION (round 110). The ordnance does NOT inherit the caster's "
    "velocity (the user's assumption, verbatim: 'I think the rocks don't keep the momentum, so "
    "let's work with that assumption'), so it falls STRAIGHT DOWN from the point the caster "
    "occupies AT RELEASE. The button must therefore predict where BOTH bodies will be when it "
    "lands - caster(t+d) = caster(t) + v_caster*d (that projected point IS the impact point) and "
    "enemy(t+d) = enemy(t) + v_enemy*d - and the drop fires when the PROJECTED horizontal "
    "centre-to-centre separation is inside FOURTH.AIR_DROP_CENTER_M = 6 m. "
    "THE DELAY d = FOURTH.AIR_DROP_DELAY_S = 1.5 s is a TUNABLE CONSTANT, not a game value: it sits "
    "between the 1 s and 2 s the user observed and NO ability row carries a fall time. Raise it if "
    "the drop still lands ahead of the target, lower it if it lands behind. "
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
    "current); a CLOSING pair now fires EARLIER in time than the old instant test (at a larger "
    "current distance, because the gap closes during the fall); a RECEDING pair fires later or not "
    "at all; and a target CROSSING the flight path is judged at its projected point instead of "
    "where it happened to be. "
    "THE BOUND (unchanged since round 109, and unchanged by this round): the horizontal "
    "centre-to-centre distance - battle_unit:position() is 'the centre position of the main squad "
    "of the unit' (battle_unit.lua:114) - on the GROUND PLANE X/Z, because battle_vector:get_y() is "
    "HEIGHT (a 3D read would measure 30-60 m from a unit directly underneath); the engine's "
    "battle_vector:distance_xz() with a sqrt(x/z) fallback. 6 m is ONE documented constant standing "
    "in for the formation footprint - the API has NO per-unit radius / footprint / bounding box / "
    "size read (script_units:radius() is a COLLECTION's spread radius; battle_entities.radius = "
    "0.6 m is ONE model's collision radius). WHY THE EDGE TEST WAS DROPPED IN ROUND 109: "
    "unit_distance() measures the gap between the two BOUNDING BOXES (battle_unit.lua:160) and two "
    "boxes can be half a metre apart while their CENTRES are 15 m apart - which is why the rocks "
    "were still released too soon. "
    "IF THE NO-MOMENTUM ASSUMPTION IS WRONG there is ONE FLAG to flip: FOURTH.AIR_DROP_INHERIT = "
    "true adds the caster's velocity to the impact point a SECOND time (impact = caster + v*d*2 - "
    "once because the caster keeps flying while the ordnance falls, once because the ordnance "
    "carries the velocity itself). The bound, the delay, the candidate set and every guard stay as "
    "they are. "
    "Infantry read: battle_unit:is_infantry() first, unit_class() exact-match inf_mel / inf_mis / "
    "inf_spr second, FAIL CLOSED. "
)

NEW_LOG = (
    "THE LOG, PER DECISION: one target line with the delay, the momentum mode, the caster's "
    "current point + velocity + velocity SOURCE + projected point, the enemy's same four, the "
    "PROJECTED centre separation, the instant separation, the bound, the edge gap (diagnostic "
    "only) and air_only; and, when nothing qualifies, a 'watch: nearest INFANTRY ... centre=~Nm vs "
    "bound=6m -> NOT under the caster [projected sep=~Nm after delay=1.50s; caster v=... src=...; "
    "enemy v=... src=...]' line (5 m bands, only while the nearest projected separation is inside "
    "30 m). "
)

NEW_RECHECK = (
    " The cast is SELF-CENTRED: perform_special_ability(key, OWNER). Immediately before the call "
    "the caster must still be alive, airborne where the row is air-only and out of melee where the "
    "row declares it, the enemy must still be alive and infantry, and the TWO-BODY PROJECTION is "
    "RE-TAKEN from fresh positions and fresh velocities - if the projected separation has left the "
    "bound the cast is SKIPPED rather than spent."
)

NEW_DEF = (
    "an enemy INFANTRY unit that will be UNDER the caster WHEN THE ORDNANCE LANDS: BOTH bodies are "
    "projected forward by FOURTH.AIR_DROP_DELAY_S = 1.5 s (a TUNABLE constant - no row carries a "
    "fall time), and the horizontal CENTRE-TO-CENTRE separation of the two PROJECTED points "
    "(battle_unit:position(), X/Z only - get_y is HEIGHT) must be inside FOURTH.AIR_DROP_CENTER_M "
    "= 6 m. The ordnance does NOT inherit the caster's velocity (the user's assumption), so it "
    "lands straight down from the caster's position at release: impact = caster + v_caster*d. "
    "Velocity is rebuilt from is_moving() / is_moving_fast() / slow_speed() / fast_speed() plus a "
    "heading from ordered_position(); bearing() is the CASTER-ONLY fallback while moving; every "
    "unreadable read is ZERO velocity with a named source (stationary / moving-unreadable / "
    "no-speed / no-heading) - motion is never invented. Consequences: a stationary pair behaves as "
    "in round 109, a closing pair fires EARLIER (larger current distance), a receding pair later or "
    "never, and a crossing target is judged at its projected point. 6 m stands in for the formation "
    "footprint (the API has no per-unit radius / bbox / size read); lower it if the drop is still "
    "early, raise it if it never fires. ONE FLAG if the assumption is wrong: "
    "FOURTH.AIR_DROP_INHERIT = true adds v*d a second time (impact = caster + v*d*2). The caster "
    "must be airborne where the row says so (`grounded` or a flying-only carrier) and OUT of melee "
    "where the row says so (`engaged_in_melee`); the pre-cast re-check RE-PROJECTS both bodies and "
    "skips the cast rather than spending it."
)

CONST_ROWS = [
    ("FOURTH.AIR_DROP_CENTER_M", "6 (m)",
     "THE BOUND - unchanged since round 109. The horizontal centre-to-centre separation that counts "
     "as 'under': two units inside 6 m of each other. It stands in for the formation footprint "
     "because the script API exposes no per-unit radius / footprint / bbox / size read. ONE value "
     "to tune: lower it if the drop still releases early, raise it if it never fires."),
    ("FOURTH.AIR_DROP_DELAY_S", "1.5 (s) - NEW in round 110",
     "THE FALL TIME the prediction projects over: how long after the button press the ordnance "
     "lands. A TUNABLE CONSTANT between the 1 s and 2 s the user observed in the field - NOT a game "
     "value (no ability row carries a fall time, so nothing in the data can be quoted for it). "
     "Raise it if the drop still lands AHEAD of the target, lower it if it lands BEHIND. Both "
     "bodies are projected by exactly this much."),
    ("FOURTH.AIR_DROP_INHERIT", "false - NEW in round 110",
     "THE MOMENTUM FLAG, the single switch the assumption rides on. false = the ordnance does NOT "
     "inherit the caster's velocity, so the impact point is the caster's projected position and the "
     "drop fires when the PROJECTED separation is inside the bound. true = the ordnance DOES carry "
     "the caster's momentum, so v*d is added to the impact point a SECOND time (impact = caster + "
     "v*d*2). Flip this ONE flag if field tests show the rocks landing ahead of the release point; "
     "nothing else changes."),
]


def set_wrapped(ws, row, col, value, bold=False):
    c = ws.cell(row=row, column=col, value=value)
    c.alignment = WRAP
    if bold:
        c.font = Font(bold=True)
    return c


if os.path.exists(V11):
    os.remove(V11)
shutil.copy2(V10, V11)

wb = openpyxl.load_workbook(V11)

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
    i = v.find("air_drop_on_infantry (round 107")
    assert i == 0, (r, v[:80])
    j = v.find("the only decision is WHEN. ")
    assert j > 0, (r, "no lead end")
    lead_end = j + len("the only decision is WHEN. ")
    k = v.find("Infantry read:")
    assert k > lead_end, (r, "no middle end")
    p = v.find("FAIL CLOSED.", k)
    assert p > k, (r, "no infantry close")
    m = p + len("FAIL CLOSED. ")
    n = v.find("The cast is SELF-CENTRED:")
    assert n > m, (r, "no cast start")
    new = NEW_LEAD + NEW_MIDDLE + NEW_LOG + v[m:n].rstrip() + NEW_RECHECK
    ab.cell(row=r, column=trig).value = new
    ab.cell(row=r, column=trig).alignment = WRAP
    changed += 1
assert changed == 19, changed
print("abilities rows updated:", changed)

# the status-reason cell of those rows names the rule round
for r in range(2, ab.max_row + 1):
    if ab.cell(row=r, column=col["Trigger family"]).value != "air_drop_on_infantry":
        continue
    sr = ab.cell(row=r, column=col["Status reason / family"]).value or ""
    if "round 110" not in sr:
        ab.cell(row=r, column=col["Status reason / family"]).value = (
            sr + " | trigger rule: rounds 107-110 (two-body projection, delay 1.5 s, bound 6 m, "
                 "no momentum inheritance)")

# ---------------------------------------------------------------- Definitions
df = wb["Definitions"]
df.cell(row=1, column=1, value="DEFINITIONS - WH3 ability master v11 (%s)" % TODAY)
assert df.cell(row=69, column=1).value == "air_drop_on_infantry", df.cell(row=69, column=1).value
set_wrapped(df, 69, 3, NEW_DEF)

last = df.max_row
while last > 1 and all(df.cell(row=last, column=c).value in (None, "") for c in range(1, 7)):
    last -= 1
print("definitions last used row:", last)
hdr_font_row = 97  # "7. FIRING-LAYER GATES"
r0 = last + 2
h = df.cell(row=r0, column=1, value="8. THE AIR-DROP PREDICTION CONSTANTS (round 110)")
h.font = Font(bold=True, size=12)
set_wrapped(df, r0 + 1, 1, "Constant", bold=True)
set_wrapped(df, r0 + 1, 2, "Value", bold=True)
set_wrapped(df, r0 + 1, 3, "What it does / how to tune it", bold=True)
for i, (name, val, why) in enumerate(CONST_ROWS):
    rr = r0 + 2 + i
    set_wrapped(df, rr, 1, name)
    set_wrapped(df, rr, 2, val)
    set_wrapped(df, rr, 3, why)
set_wrapped(df, r0 + 2 + len(CONST_ROWS), 1, "TOTAL", bold=True)
set_wrapped(df, r0 + 2 + len(CONST_ROWS), 2, "3 constants",
            bold=True)
set_wrapped(df, r0 + 2 + len(CONST_ROWS), 3,
            "Two are NEW in round 110 (the delay and the momentum flag); the bound is the round-109 "
            "6 m value, untouched. None of them changes any count, any carrier family or any "
            "evaluator.")

# -------------------------------------------------------------------- Numbers
nm = wb["Numbers"]
for r in range(1, nm.max_row + 1):
    v = nm.cell(row=r, column=1).value
    if not isinstance(v, str):
        continue
    if v.startswith("Date: 2026-10-18"):
        nm.cell(row=r, column=1).value = (
            "Date: 2026-10-18     Rule in force since: 2026-10-17     Inventory: 1,799 active "
            "abilities     (v11: round 110 - the air drop is PREDICTED, not sampled: both bodies "
            "are projected 1.5 s ahead (FOURTH.AIR_DROP_DELAY_S, tunable) and the drop fires when "
            "their PROJECTED centre separation is inside the same 6 m bound; the ordnance does not "
            "inherit the caster's velocity, and FOURTH.AIR_DROP_INHERIT is the one flag if it does)")
    elif v.startswith("Trigger families after round 109"):
        nm.cell(row=r, column=1).value = v.replace("round 109", "round 110")
    elif v.startswith("Reconciliation: included"):
        nm.cell(row=r, column=1).value = (
            "Reconciliation: included 1,141 + excluded 658 = 1,799. Implemented among the included "
            "742 + not implemented 399 = 1,141. The mod's ABILITIES table is 689 entries / 742 keys "
            "(the two Soulfire keys are ONE entry, the two Slicing Shards keys are ONE entry). The "
            "tracker carries the implemented ROWS; implemented keys with no row of their own ride a "
            "row that names its sibling. Round 110 is a BEHAVIOUR-ONLY change: the air-drop family "
            "stays 12 entries / 19 keys, the 46 trigger families are unchanged, and every count on "
            "this sheet - inventory 1,799, excluded 658, included 1,141, implemented 742, not "
            "implemented 399, the eight carrier families, the 46 evaluator rows - is IDENTICAL to "
            "v10. What changed: the trigger text of those 12 entries, the rule itself, and TWO NEW "
            "CONSTANTS in the Definitions (FOURTH.AIR_DROP_DELAY_S = 1.5 s and "
            "FOURTH.AIR_DROP_INHERIT = false; the 6 m bound is unchanged)."
        )

# ------------------------------------------------------------------ Changelog
cl = wb["Changelog"]
row = cl.max_row + 1
while row > 1 and all(cl.cell(row=row - 1, column=c).value in (None, "") for c in range(1, 5)):
    row -= 1
cl.cell(row=row, column=1).value = TODAY
cl.cell(row=row, column=2).value = "v11"
cl.cell(row=row, column=3).value = (
    "ROUND 110 - THE AIR DROP IS PREDICTED, NOT SAMPLED (TWO-BODY RELATIVE MOTION). (1) WHAT WAS "
    "WRONG: the round-109 centre test compared the two units' CURRENT positions, but the ordnance "
    "takes about 1-2 s to land and both bodies keep moving, so the enemy that was under the caster "
    "at the button press was not under the rocks at impact - the user's third field report, still "
    "early or missing. (2) THE ASSUMPTION (the user's ruling: 'I think the rocks don't keep the "
    "momentum, so let's work with that assumption'): the ordnance does NOT inherit the caster's "
    "velocity and falls STRAIGHT DOWN from the release point, so the impact IS the caster's "
    "projected position. (3) THE RULE: project BOTH bodies forward by FOURTH.AIR_DROP_DELAY_S = "
    "1.5 s - caster(t+d) = caster(t) + v_caster*d (the impact point), enemy(t+d) = enemy(t) + "
    "v_enemy*d - and fire when the PROJECTED horizontal centre separation is inside the same "
    "FOURTH.AIR_DROP_CENTER_M = 6 m. The delay is a TUNABLE CONSTANT (between the observed 1 s and "
    "2 s), NOT a game value: no row carries a fall time. Consequences: a stationary pair behaves "
    "exactly as in round 109; a closing pair fires EARLIER in time (at a larger current distance); "
    "a receding pair later or never; a crossing target is judged at its projected point. (4) THE "
    "VELOCITY, AND ITS LIMITS: no velocity vector exists in the API, so it is rebuilt as speed * "
    "normalise(ordered_position() - position()) from is_moving() / is_moving_fast() / slow_speed() "
    "/ fast_speed() (m/s); bearing() ('the current orientation ... in degrees') is the "
    "CASTER-ONLY fallback while moving because the dump never states its degree-to-axis "
    "convention; an ATTACKING unit's ordered_position() returns its own position (no heading); a "
    "point under 0.5 m carries no direction. Every unreadable read is ZERO velocity with a NAMED "
    "source - stationary / moving-unreadable / no-speed / no-heading - so motion is never "
    "invented and an unclear read simply behaves like round 109. (5) ONE FLAG IF THE ASSUMPTION IS "
    "WRONG: FOURTH.AIR_DROP_INHERIT = true adds v*d to the impact point a SECOND time (impact = "
    "caster + v*d*2); nothing else changes. (6) KEPT EXACTLY: the 70% map exemption, air_only / "
    "no_melee per row, the self-centred cast on the OWNER, fail-closed behaviour, and the pre-cast "
    "re-check - which now RE-PROJECTS both bodies from fresh reads and skips the cast rather than "
    "spending it. (7) THE LOG, per decision: one target line with the delay, the momentum mode, "
    "both bodies' current point + velocity + source + projected point, the PROJECTED and the "
    "instant separation, the bound and the edge gap; plus a 'watch:' band line naming the nearest "
    "infantry and both velocities when nothing qualifies. (8) COUNTS: UNCHANGED - 689 entries / "
    "742 keys, air_drop_on_infantry 12 entries / 19 keys, 46 evaluators; behaviour only. Harness "
    "110: 4253 checks / 0 failures (run twice, byte-identical); red control (the round-109 build) "
    "65 failures, ALL in the new section and all accounted for. Installed pack md5 "
    "588e6c3c6781d02321ce7b31af04884f."
)
cl.cell(row=row, column=4).value = (
    "the user's third air-drop field report and their two rulings (the relative-motion shape "
    "'Both should be accounted for' and the no-momentum assumption 'I think the rocks don't keep "
    "the momentum, so let's work with that assumption. Let's implement it and I'll test it.'); the "
    "API dump battle_unit.lua (is_moving / is_moving_fast / slow_speed / fast_speed / "
    "ordered_position / bearing) and battle_vector.lua; harness 110 plus its documented "
    "INHERIT-ON variant."
)
for c in range(1, 5):
    cl.cell(row=row, column=c).alignment = WRAP

wb.save(V11)
print("saved", V11, os.path.getsize(V11))

# ---------------------------------------------------------------- verify from disk
wb2 = openpyxl.load_workbook(V11)
a2 = wb2["Abilities"]
h2 = [c.value for c in a2[1]]
i2 = {h: n + 1 for n, h in enumerate(h2)}
air = [r for r in range(2, a2.max_row + 1)
       if a2.cell(row=r, column=i2["Trigger family"]).value == "air_drop_on_infantry"]
texts = [(r, a2.cell(row=r, column=i2["Trigger (as implemented)"]).value or "") for r in air]
need = ["FOURTH.AIR_DROP_DELAY_S = 1.5", "FOURTH.AIR_DROP_CENTER_M = 6",
        "FOURTH.AIR_DROP_INHERIT", "TWO-BODY RELATIVE-MOTION PREDICTION",
        "does NOT inherit the caster's velocity", "RE-TAKEN",
        "projected sep=~"]
bad = [(r, t) for r, t in texts if any(x not in t for x in need)]
stale = [(r, t) for r, t in texts if "must be inside FOURTH.AIR_DROP_CENTER_M = 6 m. The ground" in t]
print("VERIFY air rows:", len(air), "| missing new rule:", [r for r, _ in bad],
      "| stale round-109 middle:", [r for r, _ in stale])
assert len(air) == 19 and not bad and not stale

d2 = wb2["Definitions"]
assert "FOURTH.AIR_DROP_DELAY_S" in (d2.cell(row=69, column=3).value or "")
const_names = [d2.cell(row=r, column=1).value for r in range(1, d2.max_row + 1)]
for want in ("FOURTH.AIR_DROP_DELAY_S", "FOURTH.AIR_DROP_INHERIT", "FOURTH.AIR_DROP_CENTER_M"):
    assert want in const_names, want
print("VERIFY definitions: 3 constant rows present; air_drop glossary row updated")
n2 = wb2["Numbers"]
print("VERIFY numbers header:", (n2.cell(row=7, column=1).value or "")[:120])
print("VERIFY numbers family header:", (n2.cell(row=42, column=1).value or "")[:80])
print("VERIFY changelog last:", wb2["Changelog"].cell(row=wb2["Changelog"].max_row, column=2).value)
print("VERIFY definitions title:", d2.cell(row=1, column=1).value)
counts = {}
for r in range(2, a2.max_row + 1):
    st = a2.cell(row=r, column=i2["Status"]).value
    counts[st] = counts.get(st, 0) + 1
print("VERIFY status counts:", counts)
