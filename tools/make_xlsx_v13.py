"""Create WH3_abilities_master_v13_2026-10-18.xlsx from v12 (v1-v12 untouched).

v13 folds in round 112 - the enemy-side lead dial and the two log fixes:
  * the ENEMY is projected as position + v_enemy * AIR_DROP_DELAY_S *
    AIR_DROP_ENEMY_LEAD (1.5 s x 0.3 shipped) - the Sky-junk evidence being that
    a full 1.5 s carry (3.45 m at 2.3 m/s) put the projected centre PAST a
    hovering caster, so the projected gap was largest exactly when the enemy was
    underneath;
  * 0.0 = the enemy's current position, 1.0 = the round-110/111 full carry;
  * the tuning guide now covers FOUR dials - one per test - and names which
    symptom each addresses;
  * the log fixes ship in the row text: exact metres below 15 m on the watch
    line, the unit's ui id on every air-drop line, all four dials on every line.
NO counts change: 689 entries / 742 keys, air_drop_on_infantry 12 / 19,
46 evaluators - behaviour and observability only.
"""
import hashlib
import os
import shutil

import openpyxl
from openpyxl.styles import Alignment, Font

DOCS = r"C:/Users/vlady/Desktop/WH3_mod/docs"
V12 = os.path.join(DOCS, "WH3_abilities_master_v12_2026-10-18.xlsx")
V13 = os.path.join(DOCS, "WH3_abilities_master_v13_2026-10-18.xlsx")
TODAY = "2026-10-18"

WRAP = Alignment(wrap_text=True, vertical="top")

OLD_PREFIX = ("air_drop_on_infantry (rounds 107-111; the WHEN rule CHANGED in round 110, the "
              "CASTER's own lead in round 111)")
NEW_PREFIX = ("air_drop_on_infantry (rounds 107-112; the WHEN rule CHANGED in round 110, the "
              "CASTER's own lead in round 111, the ENEMY's in round 112)")

ENEMY_PARA = (
    "THE ENEMY-SIDE DIAL (round 112). The user's fifth field report, verbatim: 'when I selected the "
    "other 3 and just left them standing, the zombies passed below the Sky-junks and they didn't "
    "drop the bomb.' The diagnosis (docs/WH3_skyjunk_diagnosis.md, pack "
    "651f12e61284cae472bb06bf3a66b87d - session lines 947215-952480) proved all four bombers were "
    "ARMED, AIRBORNE and EVALUATED ON EVERY POLL, with infantry candidates present and NO gate, "
    "refusal or airborne hold anywhere in the session: the release test was simply never satisfied. "
    "For a STATIONARY caster the enemy's centre was carried the FULL 1.5 s ahead - v_enemy * 1.5 s "
    "= 3.45 m at the zombie's 2.3 m/s - PAST the hoverer, so the PROJECTED gap bottomed at about "
    "5 m (just outside the 6 m bound) and GREW to 10 m as the block went by: the number was LARGEST "
    "exactly when the enemy was underneath. The ENEMY therefore gets its own share of the fall "
    "time, exactly as the caster got one in round 111: enemy_projected = enemy + v_enemy * "
    "FOURTH.AIR_DROP_DELAY_S * FOURTH.AIR_DROP_ENEMY_LEAD, with FOURTH.AIR_DROP_ENEMY_LEAD = 0.3 "
    "as shipped. 0.0 = the enemy's CURRENT position (the ordnance lands straight down on where it "
    "is); 1.0 = the round-110/111 full carry that produced those misses; 0.3 = 0.45 s - about 1.0 m "
    "at 2.3 m/s, not 3.45 m - because the release is not instantaneous but a full 1.5 s of enemy "
    "travel is far too much. It scales the ENEMY's velocity term ONLY: the caster's two dials, the "
    "shared delay FOURTH.AIR_DROP_DELAY_S, the 6 m bound, FOURTH.AIR_DROP_INHERIT, air_only / "
    "no_melee, the self-centred cast, every fail-closed read and the pre-cast re-check (which "
    "re-projects through the SAME helper and so reads the SAME four dials) are UNCHANGED. "
    "THE FOUR DIALS - DEFAULTS THAT SHIP: AIR_DROP_DELAY_S = 1.5 s and AIR_DROP_ENEMY_LEAD = 0.3 "
    "(the enemy's lead time and its share); AIR_DROP_CASTER_DELAY_S = 1.5 s and "
    "AIR_DROP_CASTER_LEAD = 0.5 (the caster's). TUNING GUIDE - ONE DIAL PER TEST: the ENEMY WALKS "
    "THROUGH underneath while the caster HOVERS -> lower FOURTH.AIR_DROP_ENEMY_LEAD 0.3 -> 0.0 (the "
    "round-112 symptom); the CASTER CHASES a STANDING target and fires EARLY -> lower "
    "FOURTH.AIR_DROP_CASTER_LEAD 0.5 -> 0.3 -> 0.0, and only then FOURTH.AIR_DROP_CASTER_DELAY_S "
    "1.5 -> 1.0; fires LATE when BOTH move -> raise the lead of the body that was moving "
    "(AIR_DROP_CASTER_LEAD 0.5 -> 0.8 -> 1.0 / AIR_DROP_ENEMY_LEAD 0.3 -> 0.6 -> 1.0); still EARLY "
    "while STATIONARY (both parked) -> lower FOURTH.AIR_DROP_DELAY_S, which shrinks BOTH bodies. "
)

NEW_LOG = (
    "THE LOG, PER DECISION (round 112). ONE target line per decision with ALL FOUR DIALS - "
    "delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=0.50 - plus a 'moving caster: "
    "lead=0.50 of 1.50s' fragment ONLY when the caster's velocity is non-zero; the momentum mode, "
    "the caster's current point + velocity + velocity SOURCE + projected point, the enemy's same "
    "four, the PROJECTED centre separation, the instant separation, the bound, the edge gap "
    "(diagnostic only) and air_only. EVERY air-drop line - decision, 'watch:', skip and both "
    "pre-cast lines - is PREFIXED WITH THE UNIT'S UI ID ('[1003] sky_junk_bomb watch: ...') and "
    "carries the same four dials; the prefix exists because four IDENTICAL "
    "wh3_main_cth_veh_sky_junk_0 units (ui ids 1002-1005) made 'which of the four said this?' "
    "unanswerable from a 231 MB log. The 'watch: nearest INFANTRY ... centre=X vs bound=6m -> NOT "
    "under the caster [projected sep=Y after delay=1.50s; caster v=... (dials); enemy v=... src=...]' "
    "line prints the EXACT distances (%.2f) below 15 m - the 6 m decision margin used to sit inside "
    "a 5 m band, so '~5m' covered 5.00-9.99 m and destroyed the one number a new bound needs - and "
    "keeps the 5 m band ABOVE 15 m, where the number is context only. "
)

LOGGER_START = "THE LOG, PER DECISION: one target line with the TWO CASTER DIALS"
LOGGER_END = "(5 m bands, only while the nearest projected separation is inside 30 m). "

CONST_ROWS = [
    ("FOURTH.AIR_DROP_DELAY_S", "1.5 (s) - round 110",
     "THE ENEMY'S LEAD TIME (the fall time) - unchanged. It multiplies the ENEMY's velocity term "
     "(enemy + v_enemy * delay * enemy_lead); lower it ONLY when a STATIONARY pair is still early, "
     "which means the fall time itself is too long, and note that it shrinks BOTH bodies' travel."),
    ("FOURTH.AIR_DROP_ENEMY_LEAD", "0.3 - NEW in round 112",
     "THE ENEMY LEAD FACTOR - the user-tunable knob for a target that WALKS THROUGH underneath a "
     "hovering caster. The enemy is projected enemy + v_enemy * delay * this. 0.0 = the enemy's "
     "CURRENT position (impact straight down on where it is); 1.0 = the round-110/111 full carry "
     "that carried the projected centre 3.45 m PAST the hoverer (the reported bug); 0.3 ships = "
     "0.45 s, about 1.0 m at 2.3 m/s. LOWER it if a walk-through still misses (0.3 -> 0.0); raise "
     "it if a walking target is never hit (0.3 -> 0.6 -> 1.0)."),
    ("FOURTH.AIR_DROP_CASTER_DELAY_S", "1.5 (s) - round 111",
     "THE CASTER'S OWN LEAD TIME. How far ahead the CASTER's impact point is projected, independent "
     "of the enemy's delay. 1.5 = the shared fall time; lower it (1.5 -> 1.0) only when the caster "
     "lead factor alone cannot cure an early release while MOVING. It never moves the enemy term."),
    ("FOURTH.AIR_DROP_CASTER_LEAD", "0.5 - round 111",
     "THE CASTER LEAD FACTOR. The caster is projected caster + v_caster * caster_delay * this. 1.0 "
     "= the round-110 behaviour that over-leads a moving caster; 0.0 = the caster treated as "
     "STATIONARY (impact at the cast position); 0.5 ships. Lower it (0.5 -> 0.3 -> 0.0) if a "
     "chasing caster fires early; raise it (0.5 -> 0.8 -> 1.0) if it never fires while moving."),
    ("FOURTH.AIR_DROP_CENTER_M", "6 (m) - round 109",
     "THE BOUND - not a lead, and unchanged. The horizontal centre-to-centre separation that counts "
     "as 'under'. It stands in for the formation footprint because the script API exposes no "
     "per-unit radius / footprint / bbox / size read. Lower it if the drop still releases early at "
     "ANY caster speed; raise it if it never fires."),
    ("FOURTH.AIR_DROP_INHERIT", "false - round 110",
     "THE MOMENTUM FLAG - not a lead. false = the ordnance does NOT inherit the caster's velocity, "
     "so the impact is straight down from the release point. true = the caster's lead term is added "
     "a SECOND time. Flip this ONE flag only if the field shows the rocks landing ahead of the "
     "release point after the lead dials have been tuned."),
]

TUNING_ROWS = [
    ("the ENEMY WALKS THROUGH underneath while the caster HOVERS",
     "FOURTH.AIR_DROP_ENEMY_LEAD",
     "0.3 -> 0.0. The round-112 symptom: the enemy's projected centre is carried past the hoverer, "
     "so the gap is largest exactly when it is underneath. 0.0 = impact on the enemy's CURRENT "
     "position."),
    ("the CASTER CHASES a STANDING target and fires EARLY",
     "FOURTH.AIR_DROP_CASTER_LEAD",
     "0.5 -> 0.3 -> 0.0; only if 0.0 is still early, then FOURTH.AIR_DROP_CASTER_DELAY_S 1.5 -> 1.0. "
     "The round-111 symptom: the caster's projected point runs ahead of the real impact point."),
    ("fires LATE when BOTH move",
     "the lead of the body that was moving",
     "AIR_DROP_CASTER_LEAD 0.5 -> 0.8 -> 1.0, or AIR_DROP_ENEMY_LEAD 0.3 -> 0.6 -> 1.0. The lead on "
     "that body has been cut too far."),
    ("still EARLY while STATIONARY (both bodies parked)",
     "FOURTH.AIR_DROP_DELAY_S",
     "1.5 -> 1.2 -> 1.0. Both lead factors multiply zero velocity when nothing moves, so the shared "
     "fall time itself is too long; it shrinks BOTH bodies."),
]


def set_wrapped(ws, row, col, value, bold=False):
    c = ws.cell(row=row, column=col, value=value)
    c.alignment = WRAP
    if bold:
        c.font = Font(bold=True)
    return c


# ------------------------------------------------------------------ fingerprints
before = {}
for v in range(1, 13):
    p = os.path.join(DOCS, f"WH3_abilities_master_v{v}_2026-10-1{'7' if v <= 1 else '8'}.xlsx")
    if os.path.exists(p):
        before[p] = hashlib.md5(open(p, "rb").read()).hexdigest()

if os.path.exists(V13):
    os.remove(V13)
shutil.copy2(V12, V13)

wb = openpyxl.load_workbook(V13)

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
    assert v.startswith(OLD_PREFIX), (r, v[:90])
    assert "THE MOVING-CASTER DIALS (round 111)." in v, (r, "no round-111 middle")
    assert "THE VELOCITY is REBUILT" in v, (r, "no velocity paragraph")
    i_log = v.find(LOGGER_START)
    j_log = v.find(LOGGER_END)
    assert 0 < i_log < j_log, (r, i_log, j_log)
    new = v.replace(OLD_PREFIX, NEW_PREFIX, 1)
    new = new.replace("THE VELOCITY is REBUILT", ENEMY_PARA + "THE VELOCITY is REBUILT", 1)
    i2 = new.find(LOGGER_START)
    j2 = new.find(LOGGER_END, i2)
    new = new[:i2] + NEW_LOG + new[j2 + len(LOGGER_END):]
    ab.cell(row=r, column=trig).value = new
    ab.cell(row=r, column=trig).alignment = WRAP
    # the status-reason cell names the rule rounds
    sr = ab.cell(row=r, column=col["Status reason / family"]).value or ""
    if "round 112" not in sr:
        ab.cell(row=r, column=col["Status reason / family"]).value = (
            sr + " | trigger rule: rounds 107-112 (two-body projection; caster lead = "
                 "AIR_DROP_CASTER_DELAY_S 1.5 s x AIR_DROP_CASTER_LEAD 0.5, ENEMY lead = "
                 "AIR_DROP_DELAY_S 1.5 s x AIR_DROP_ENEMY_LEAD 0.3, bound 6 m, no momentum "
                 "inheritance; log: ui-id prefix, exact metres < 15 m, four dials)")
    changed += 1
assert changed == 19, changed
print("abilities rows updated:", changed)

# ----------------------------------------------------------------- Definitions
df = wb["Definitions"]
df.cell(row=1, column=1, value="DEFINITIONS - WH3 ability master v13 (%s)" % TODAY)
gl = df.cell(row=69, column=3).value or ""
assert gl.startswith("an enemy INFANTRY unit that will be UNDER the caster"), gl[:80]
G_OLD = ("and the ENEMY by FOURTH.AIR_DROP_DELAY_S = 1.5 s in full (a TUNABLE constant - no row "
         "carries a fall time)")
G_NEW = ("and the ENEMY by FOURTH.AIR_DROP_DELAY_S = 1.5 s x FOURTH.AIR_DROP_ENEMY_LEAD = 0.3 (a "
         "TUNABLE pair - no row carries a fall time; 0.0 = the enemy's CURRENT position, 1.0 = the "
         "old full carry that carried the projected centre past a hovering caster)")
assert G_OLD in gl, "the v12 enemy clause is not in the glossary row"
gl = gl.replace(G_OLD, G_NEW, 1)
L_OLD = ("The log prints, per decision, the two caster dials (`from delay_caster=1.50s lead=0.50`"
         if "(`from delay_caster=1.50s lead=0.50`" in gl else "delay_caster=1.50s lead=0.50")
if L_OLD in gl:
    k = gl.find("The log prints, per decision,")
    if k >= 0:
        gl = gl[:k] + ("The log prints, per decision, ALL FOUR dials "
                       "(delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=0.50, plus "
                       "'moving caster: lead=0.50 of 1.50s' only when the caster is moving); EVERY "
                       "air-drop line carries the unit's ui id ('[1003] ...') and the watch line "
                       "prints the EXACT distances below 15 m (5 m bands only above 15 m).")
set_wrapped(df, 69, 3, gl)

last = df.max_row
while last > 1 and all(df.cell(row=last, column=c).value in (None, "") for c in range(1, 7)):
    last -= 1
r0 = last + 2
h = df.cell(row=r0, column=1,
            value="10. THE FOURTH DIAL AND THE COMPLETE FOUR-DIAL MAP (round 112) - the enemy's lead, "
                  "plus all four leads in one place (section 9 is the round-111 record of the caster pair)")
h.font = Font(bold=True, size=12)
set_wrapped(df, r0 + 1, 1, "THE FOUR DIALS AND THE BOUND - the complete set, defaults that ship", bold=True)
set_wrapped(df, r0 + 2, 1, "Constant", bold=True)
set_wrapped(df, r0 + 2, 2, "Ships as", bold=True)
set_wrapped(df, r0 + 2, 3, "What it does / how to tune it", bold=True)
for i, (name, val, why) in enumerate(CONST_ROWS):
    rr = r0 + 3 + i
    set_wrapped(df, rr, 1, name)
    set_wrapped(df, rr, 2, val)
    set_wrapped(df, rr, 3, why)
tot = r0 + 3 + len(CONST_ROWS)
set_wrapped(df, tot, 1, "TOTAL", bold=True)
set_wrapped(df, tot, 2, "4 dials + 1 bound + 1 flag", bold=True)
set_wrapped(df, tot, 3,
            "FOUR LEADS, ONE PER BODY-TERM (AIR_DROP_DELAY_S 1.5 s x AIR_DROP_ENEMY_LEAD 0.3 for the "
            "enemy; AIR_DROP_CASTER_DELAY_S 1.5 s x AIR_DROP_CASTER_LEAD 0.5 for the caster), the 6 m "
            "bound (not a lead) and the momentum flag (not a lead). Only the ENEMY factor is new in "
            "round 112; the caster pair, the bound and the flag are unchanged since rounds 111 / "
            "109 / 110.")

g0 = tot + 2
g = df.cell(row=g0, column=1,
            value="TUNING GUIDE (round 112) - FOUR DIALS, change ONE per field test")
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
set_wrapped(df, g0 + 2 + len(TUNING_ROWS), 2, "1 rule", bold=True)
set_wrapped(df, g0 + 2 + len(TUNING_ROWS), 3,
            "One dial changes per test so the field log - which now prints ALL FOUR dials AND the "
            "unit's ui id on every air-drop line - says which term moved the impact point. The four "
            "defaults (DELAY 1.5 s, ENEMY_LEAD 0.3, CASTER_DELAY 1.5 s, CASTER_LEAD 0.5) are the "
            "starting point; the 6 m bound and the momentum flag are NOT leads. None of this changes "
            "any count, carrier family or evaluator.")

# -------------------------------------------------------------------- Numbers
nm = wb["Numbers"]
for r in range(1, nm.max_row + 1):
    v = nm.cell(row=r, column=1).value
    if not isinstance(v, str):
        continue
    if v.startswith("Date: 2026-10-18"):
        nm.cell(row=r, column=1).value = (
            "Date: 2026-10-18     Rule in force since: 2026-10-17     Inventory: 1,799 active "
            "abilities     (v13: round 112 - THE ENEMY-SIDE LEAD DIAL: the enemy is projected by "
            "FOURTH.AIR_DROP_DELAY_S = 1.5 s x FOURTH.AIR_DROP_ENEMY_LEAD = 0.3 as well as the "
            "caster by its own 1.5 s x 0.5, with the same 6 m bound; the Sky-junk evidence is that "
            "the full 1.5 s carry (3.45 m at 2.3 m/s) put the projected centre PAST a hovering "
            "caster, so the gap was largest exactly when the enemy was underneath. The log now "
            "names the unit and prints exact metres below 15 m)")
    elif v.startswith("Trigger families after round"):
        nm.cell(row=r, column=1).value = v.replace("round 111", "round 112")
    elif v.startswith("Reconciliation: included"):
        nm.cell(row=r, column=1).value = (
            "Reconciliation: included 1,141 + excluded 658 = 1,799. Implemented among the included "
            "742 + not implemented 399 = 1,141. The mod's ABILITIES table is 689 entries / 742 keys "
            "(the two Soulfire keys are ONE entry, the two Slicing Shards keys are ONE entry). The "
            "tracker carries the implemented ROWS; implemented keys with no row of their own ride a "
            "row that names its sibling. Round 112 is a BEHAVIOUR-AND-OBSERVABILITY change: the "
            "air-drop family stays 12 entries / 19 keys, the 46 trigger families are unchanged, and "
            "every count on this sheet - inventory 1,799, excluded 658, included 1,141, implemented "
            "742, not implemented 399, the eight carrier families, the 46 evaluator rows - is "
            "IDENTICAL to v12. What changed: the rule (a FOURTH dial, AIR_DROP_ENEMY_LEAD = 0.3, "
            "scaling the ENEMY's velocity term only), the trigger text of those 19 rows (they name "
            "all four dials, the tuning guide and the new log format), ONE new constant row in the "
            "Definitions (FOURTH.AIR_DROP_ENEMY_LEAD = 0.3) and a four-dial tuning-guide table, and "
            "the two log fixes (ui-id prefix on every air-drop line; exact metres below 15 m). "
            "FOURTH.AIR_DROP_DELAY_S, FOURTH.AIR_DROP_CASTER_DELAY_S, "
            "FOURTH.AIR_DROP_CASTER_LEAD, the 6 m bound and AIR_DROP_INHERIT are unchanged.")

# ------------------------------------------------------------------ Changelog
cl = wb["Changelog"]
row = cl.max_row + 1
while row > 1 and all(cl.cell(row=row - 1, column=c).value in (None, "") for c in range(1, 5)):
    row -= 1
cl.cell(row=row, column=1).value = TODAY
cl.cell(row=row, column=2).value = "v13"
cl.cell(row=row, column=3).value = (
    "ROUND 112 - THE ENEMY-SIDE LEAD DIAL, AND THE TWO DIAGNOSTIC FIXES. (1) WHAT THE FIELD SAID, "
    "verbatim: 'when I selected the other 3 and just left them standing, the zombies passed below "
    "the Sky-junks and they didn't drop the bomb.' (2) THE EVIDENCE (docs/WH3_skyjunk_diagnosis.md): "
    "all four Sky-junks (ui ids 1002-1005) were armed in one click, airborne all battle, evaluated "
    "on every poll, with infantry candidates present every poll and NO gate, refusal or airborne "
    "hold in the session. The three that never fired had the enemy's centre carried v_enemy * 1.5 s "
    "= 3.45 m PAST the hoverer, so the projected gap bottomed at about 5 m (outside the 6 m bound) "
    "and GREW to 10 m - largest exactly when the enemy was underneath. (3) THE RULE: "
    "enemy_projected = enemy + v_enemy * FOURTH.AIR_DROP_DELAY_S * FOURTH.AIR_DROP_ENEMY_LEAD "
    "(1.5 s x 0.3 shipped), caster_projected = caster + v_caster * "
    "FOURTH.AIR_DROP_CASTER_DELAY_S * FOURTH.AIR_DROP_CASTER_LEAD (1.5 s x 0.5, unchanged), fire "
    "when the PROJECTED horizontal centre separation is inside FOURTH.AIR_DROP_CENTER_M = 6 m. 0.0 "
    "= the enemy's CURRENT position, 1.0 = the round-110/111 full carry; 0.3 = 0.45 s, about 1.0 m "
    "at 2.3 m/s. (4) TUNING GUIDE, ONE DIAL PER TEST: enemy walks through underneath while the "
    "caster hovers -> AIR_DROP_ENEMY_LEAD 0.3 -> 0.0; caster chases a standing target and fires "
    "early -> AIR_DROP_CASTER_LEAD 0.5 -> 0.3 -> 0.0 then AIR_DROP_CASTER_DELAY_S 1.5 -> 1.0; fires "
    "late when both move -> raise the moving body's lead (0.5 -> 0.8 -> 1.0 / 0.3 -> 0.6 -> 1.0); "
    "still early while both are parked -> AIR_DROP_DELAY_S 1.5 -> 1.2 -> 1.0. (5) THE TWO LOG "
    "FIXES: every air-drop line carries the unit's ui id ('[1003] sky_junk_bomb watch: ...') and "
    "ALL FOUR dials (delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=0.50); the watch "
    "line prints the EXACT projected and instant distances below 15 m (the 5 m band survives above "
    "15 m). (6) KEPT EXACTLY: the caster's two dials, the shared delay, the 6 m bound, "
    "AIR_DROP_INHERIT, air_only / no_melee, the self-centred cast, fail-closed reads and the "
    "pre-cast re-check (same helper => same four dials). (7) COUNTS: UNCHANGED - 689 entries / 742 "
    "keys, air_drop_on_infantry 12 entries / 19 keys, 46 evaluators. Harness 112: 4492 checks / 0 "
    "failures (run twice, byte-identical); red control (the round-111 build) 31 failures, ALL in "
    "the new section. Installed pack md5 237702987893b8837d2dbb5df05d566b.")
cl.cell(row=row, column=4).value = (
    "the user's fifth air-drop field report; docs/WH3_skyjunk_diagnosis.md; harness 112 (worlds A "
    "lead 1.0 reproduces the miss and 0.3 fires, B lead 0.0 = the current position, C a parked "
    "enemy is untouched, D both moving, E exact metres below 15 m, F the ui id on every line) with "
    "its one-line enemy-lead VARIANT files; docs/WH3_round112_airdrop_enemylead.md.")
for c in range(1, 5):
    cl.cell(row=row, column=c).alignment = WRAP

wb.save(V13)
print("saved", V13, os.path.getsize(V13))

# ---------------------------------------------------------------- verify (disk)
wb2 = openpyxl.load_workbook(V13)
a2 = wb2["Abilities"]
h2 = [c.value for c in a2[1]]
i2 = {h: n + 1 for n, h in enumerate(h2)}
air = [r for r in range(2, a2.max_row + 1)
       if a2.cell(row=r, column=i2["Trigger family"]).value == "air_drop_on_infantry"]
texts = [(r, a2.cell(row=r, column=i2["Trigger (as implemented)"]).value or "") for r in air]
need = ["FOURTH.AIR_DROP_ENEMY_LEAD = 0.3", "FOURTH.AIR_DROP_DELAY_S = 1.5 s",
        "FOURTH.AIR_DROP_CASTER_DELAY_S = 1.5 s", "FOURTH.AIR_DROP_CASTER_LEAD = 0.5",
        "FOURTH.AIR_DROP_CENTER_M = 6 m", "FOURTH.AIR_DROP_INHERIT",
        "THE ENEMY-SIDE DIAL (round 112)", "THE FOUR DIALS - DEFAULTS THAT SHIP",
        "ONE DIAL PER TEST", "0.3 -> 0.0", "delay=1.50s enemy_lead=0.30 delay_caster=1.50s "
        "caster_lead=0.50", "[1003]", "EXACT distances"]
bad = [(r, [x for x in need if x not in t]) for r, t in texts if any(x not in t for x in need)]
stale = [r for r, t in texts if "rounds 107-111" in t or "in full (a TUNABLE constant" in t]
print("VERIFY air rows:", len(air), "| missing new rule:", [(r, m) for r, m in bad],
      "| stale:", stale)
assert len(air) == 19 and not bad and not stale

d2 = wb2["Definitions"]
gl2 = d2.cell(row=69, column=3).value or ""
assert "FOURTH.AIR_DROP_ENEMY_LEAD = 0.3" in gl2, "glossary row lacks the enemy dial"
const_names = [d2.cell(row=r, column=1).value for r in range(1, d2.max_row + 1)]
for want in ("FOURTH.AIR_DROP_DELAY_S", "FOURTH.AIR_DROP_ENEMY_LEAD",
             "FOURTH.AIR_DROP_CASTER_DELAY_S", "FOURTH.AIR_DROP_CASTER_LEAD",
             "FOURTH.AIR_DROP_CENTER_M", "FOURTH.AIR_DROP_INHERIT"):
    assert want in const_names, want
tuning = [n for n in const_names if isinstance(n, str) and "WALKS THROUGH underneath" in n]
assert tuning, "the round-112 tuning-guide table is missing"
print("VERIFY definitions: 6 constant rows + 4-row tuning guide present; glossary updated")
n2 = wb2["Numbers"]
print("VERIFY numbers:", (n2.cell(row=7, column=1).value or "")[:100])
print("VERIFY changelog last:", wb2["Changelog"].cell(row=wb2["Changelog"].max_row, column=2).value)
print("VERIFY definitions title:", d2.cell(row=1, column=1).value)

# the older versions must be byte-identical
after = {p: hashlib.md5(open(p, "rb").read()).hexdigest() for p in before}
assert before == after, "an earlier version changed!"
print("VERIFY v1-v12 byte-unchanged:", len(before), "files")
