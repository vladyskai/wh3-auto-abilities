"""Create WH3_abilities_master_v14_2026-10-18.xlsx from v13 (v1-v13 untouched).

v14 folds in round 113 - THE PATH TEST, THE DERIVED FRONTAGE AND THE
SINGLE-ENTITY EXCLUSION:
  * the drop is judged against the ENEMY'S PATH, not its point: the segment
    enemy_current -> enemy_projected, and the number that decides is the shortest
    horizontal distance from that segment to the caster's projected point;
  * the bound gains a DERIVED FRONTAGE CREDIT (a half-width): ordered_width()/2
    when that read is sane, otherwise ceil(models/2) * per-model radius under a
    documented TWO-RANK assumption, clamped to 1..12 m, fail-closed to 0;
  * the per-model radius is a documented CONSTANT (0.6 m) because battle Lua has
    no db access and no radius read;
  * a ONE-MODEL candidate (initial_number_of_men() == 1) is skipped once per
    episode - the user's ruling that one model covers the lord/hero case, and
    that equality to 1 is the right comparison.
NO counts change: 689 entries / 742 keys, air_drop_on_infantry 12 / 19,
46 evaluators.
"""
import hashlib
import os
import shutil

import openpyxl
from openpyxl.styles import Alignment, Font

DOCS = r"C:/Users/vlady/Desktop/WH3_mod/docs"
V13 = os.path.join(DOCS, "WH3_abilities_master_v13_2026-10-18.xlsx")
V14 = os.path.join(DOCS, "WH3_abilities_master_v14_2026-10-18.xlsx")
TODAY = "2026-10-18"

WRAP = Alignment(wrap_text=True, vertical="top")

OLD_PREFIX = ("air_drop_on_infantry (rounds 107-112; the WHEN rule CHANGED in round 110, the "
              "CASTER's own lead in round 111, the ENEMY's in round 112)")
NEW_PREFIX = ("air_drop_on_infantry (rounds 107-113; the WHEN rule CHANGED in round 110, the "
              "CASTER's own lead in round 111, the ENEMY's in round 112, the PATH AND THE "
              "FRONTAGE CREDIT in round 113)")

PATH_PARA = (
    "THE PATH TEST AND THE DERIVED FRONTAGE (round 113). The user's sixth field report, verbatim: a "
    "Sky-junk hovering BESIDE a 20-model zombie block never fired while the block walked past - the "
    "enemy's CENTRE stayed 10+ m away even though its MODELS swept under the caster; and separately "
    "one fired at a LORD, which must be excluded. The user's rulings, verbatim: '1. Why combine? The "
    "started with one model would cover the other case, woudn't it? Also, why comparison is 1 or "
    "less? It cannot be less, then the unit does not exist. So comparion should be equal to 1. Am I "
    "forgetting something? If you agree, start implementing with point 2.' and '2. Let's implement "
    "the the path test with a derived frontage that you suggest.' WHY A POINT CANNOT DESCRIBE A "
    "BLOCK: battle_unit:position() is the CENTRE of the main squad (battle_unit.lua:118), so a "
    "20-model formation 10 models wide in two ranks (about 10 m of frontage) can keep its centre "
    "10 m away while one of its models walks underneath the flyer - the round-110/112 point test "
    "never saw that pass. THE TEST IS NOW THE ENEMY'S PATH: "
    "segment = enemy_current -> enemy_projected (the enemy's own two dials, unchanged); "
    "perp = the SHORTEST HORIZONTAL DISTANCE from that segment to the CASTER'S projected point "
    "(standard point-to-segment arithmetic on x/z, the parameter CLAMPED to 0..1 so a path that "
    "ENDS short is judged on its end point, never on the infinite line); "
    "FIRE WHEN perp <= AIR_DROP_CENTER_M + ad_frontage(enemy). THE FRONTAGE CREDIT is DERIVED, not "
    "guessed: (a) ordered_width() when it answers a sane positive number - 'the width of the "
    "position to which the unit has been ordered in metres' - halved (source 'ordered'); "
    "(b) otherwise the MODEL COUNT times the PER-MODEL COLLISION RADIUS under ONE documented "
    "formation assumption - FOURTH.AIR_DROP_RANKS = 2, i.e. the unit stands TWO RANKS DEEP, "
    "so half = ceil(models/2) * radius "
    "(source 'models'); (c) clamped to FOURTH.AIR_DROP_FRONTAGE_MIN_M .. _MAX_M = 1 .. 12 m "
    "HALF-width (source 'clamped'); (d) a ONE-MODEL unit gets 0 (source 'single') - a point has no "
    "width and the 6 m base already covers its footprint; (e) unreadable -> 0 (source 'unreadable', "
    "FAIL CLOSED) and the plain 6 m point distance decides. THE RADIUS IS A DOCUMENTED CONSTANT, "
    "FOURTH.AIR_DROP_MODEL_RADIUS_M = 0.6 m: the battle script has NO radius / footprint / bounding "
    "box / size read and NO db access, so land_units.man_entity -> battle_entities.radius cannot be "
    "joined at battle time; 0.6 m is the MODAL radius over the 942 infantry land_units rows (168 "
    "rows; median 0.7 m, zombies 0.5 m, the Terradon rider 0.6 m) and is CONSERVATIVE against the "
    "median. Two ranks is the WIDE end of the game's own infantry formations (rank_depth runs 1..8, "
    "median 3) - a wider credit is the safe direction for a drop whose failure mode is missing a "
    "block that sweeps underneath. THE SINGLE-ENTITY EXCLUSION: a candidate whose "
    "battle_unit:initial_number_of_men() - 'the number of soldiers the unit started the battle "
    "with' - is EXACTLY 1 is skipped and the skip is logged ONCE PER EPISODE as 'single entity (1 "
    "model)'. EXACT EQUALITY, never '1 or less': a unit with zero models does not exist (the user's "
    "own point). INITIAL, not current: a 20-model block ground down to one survivor is still a "
    "20-model unit and is NOT a lord. THE COMMANDER KEY SET IS DELIBERATELY NOT USED HERE - the "
    "1,409-key set stays in service for the other evaluators, but every INFANTRY-CLASS lord and "
    "hero in the game data is a ONE-MODEL unit (main_units: 0 lord rows and 6 hero rows with a "
    "land_units class of inf_mel / inf_mis / inf_spr, ALL num_men = 1), so the model count already "
    "covers that case without a 1,409-key membership test on every poll; the multi-model character "
    "units (chariot crews of 2-8 men) are every one of them class 'com', not infantry, so the "
    "infantry filter has already removed them. An UNREADABLE initial_number_of_men() SKIPS the "
    "candidate (fail-closed) and says so. KEPT EXACTLY: the caster's two dials, the enemy's two "
    "dials, AIR_DROP_INHERIT, air_only / no_melee, the self-centred cast, every fail-closed read, "
    "and the pre-cast re-check - which now RE-RUNS the SEGMENT test on fresh reads. "
)

LOG_START = "THE LOG, PER DECISION (round 112)."
LOG_END = "where the number is context only. "

NEW_LOG = (
    "THE LOG, PER DECISION (round 113). ONE target line per decision with ALL FOUR DIALS - "
    "delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=0.50 - plus a 'moving caster: "
    "lead=0.50 of 1.50s' fragment ONLY when the caster's velocity is non-zero; the momentum mode, "
    "the caster's current point + velocity + velocity SOURCE + projected point, the enemy's same "
    "four, then THE PATH NUMBERS the rule now decides on: 'segment=(110.0, 201.0)->(109.0, 201.0)' "
    "(the enemy's CURRENT -> PROJECTED leg), 'perp=9.02m' (the shortest distance from that segment "
    "to the caster's projected point), 'frontage=6.00m (models, men=20 x 2 ranks (10 per rank) x "
    "0.60m radius)' (the credit AND the source that produced it - 'ordered' / 'models' / 'clamped' "
    "/ 'single' / 'unreadable'), 'threshold=12.00m (bound=6m + frontage=6.00m)' (the number perp "
    "had to beat) and the old point separation as the diagnostic it now is: 'centre=9.0m (the "
    "PROJECTED POINT separation - no longer the test)'; plus the instant separation, the bound, the "
    "edge gap (diagnostic only), the per-model radius constant and air_only. EVERY air-drop line - "
    "decision, 'watch:', skip, the single-entity skip and both pre-cast lines - is PREFIXED WITH "
    "THE UNIT'S UI ID ('[1003] sky_junk_bomb watch: ...') and carries the same four dials; the "
    "prefix exists because four IDENTICAL wh3_main_cth_veh_sky_junk_0 units (ui ids 1002-1005) made "
    "'which of the four said this?' unanswerable from a 231 MB log. The 'watch: nearest INFANTRY "
    "... centre=X vs bound=6m -> NOT under the caster [perp=Y vs threshold=Z m (bound=6m + "
    "frontage=..., source); segment=...->...; projected sep=W after delay=1.50s; caster v=... "
    "(dials); enemy v=... src=...]' line prints the EXACT distances (%.2f) below 15 m - the 6 m "
    "decision margin used to sit inside a 5 m band, so '~5m' covered 5.00-9.99 m and destroyed the "
    "one number a new bound needs - and keeps the 5 m band ABOVE 15 m, where the number is context "
    "only. THE SINGLE-ENTITY SKIP is ONE line per episode ('SKIPPED: single entity (1 model) - "
    "'<type>' has initial_number_of_men() = 1 ...') and says why the commander key set is not "
    "consulted here. "
)

OLD_RECHECK = ("the TWO-BODY PROJECTION is RE-TAKEN from fresh positions and fresh velocities - if "
               "the projected separation has left the bound the cast is SKIPPED rather than spent.")
NEW_RECHECK = ("the enemy's CURRENT and PROJECTED points are RE-READ (one read gives both, and the "
               "same read sequence, so a drift world behaves identically), the SEGMENT IS REBUILT "
               "and the PERPENDICULAR DISTANCE is re-measured against bound + the FRESH frontage - "
               "if the path is no longer inside the threshold (or the target lapsed) the cast is "
               "SKIPPED rather than spent, and the SKIPPED line prints the fresh perp, the "
               "threshold, the frontage and the segment.")

OLD_CONST = "6 m is ONE documented constant standing in for the formation footprint"
NEW_CONST = ("6 m is ONE documented constant standing in for the formation footprint (ROUND 113 "
             "SUPERSEDES THAT AS THE WHOLE STORY: the bound is now the BASE of the decision and a "
             "DERIVED half-frontage is added to it, see THE PATH TEST AND THE DERIVED FRONTAGE "
             "above - the constant remains the tuning dial for the base and for a one-model enemy)")

CONST_ROWS = [
    ("FOURTH.AIR_DROP_CENTER_M", "6 (m) - round 109, unchanged",
     "THE BASE BOUND. The perpendicular distance from the enemy's path to the caster's projected "
     "point must be inside THIS plus the candidate's half-frontage. It is the 'the enemy is under "
     "me' margin; the frontage adds the 'the enemy is WIDE' margin. Lower it if the drop still "
     "releases early; raise it if a one-model enemy is never hit (a multi-model one is covered by "
     "the frontage credit)."),
    ("FOURTH.AIR_DROP_MODEL_RADIUS_M", "0.6 (m) - NEW in round 113",
     "THE PER-MODEL COLLISION RADIUS used by the model-count half of the frontage derivation. It is "
     "a CONSTANT because battle Lua can read neither land_units.man_entity nor "
     "battle_entities.radius: 0.6 m is the MODAL radius over the 942 infantry land_units rows (168 "
     "rows), the median is 0.7 m and the Terradon rider is 0.6 m. Raise it ONLY if a wide block is "
     "still missed while its models visibly pass under the caster."),
    ("FOURTH.AIR_DROP_RANKS", "2 - NEW in round 113",
     "THE FORMATION ASSUMPTION: the unit is treated as TWO RANKS DEEP, so per_rank = ceil(models "
     "/ 2) and the full frontage = per_rank * 2 * radius. Two ranks is the WIDE end of the game's "
     "own infantry formations (land_units rank_depth runs 1..8, median 3), and a wider credit is "
     "the SAFE direction for a drop that must not miss a block sweeping underneath. Raise it to 3 "
     "to make the credit NARROWER (a deeper formation is less wide)."),
    ("FOURTH.AIR_DROP_FRONTAGE_MIN_M / _MAX_M", "1 / 12 (m half-width) - NEW in round 113",
     "THE CLAMP on the half-width credit. The floor keeps a 2-model unit from getting a "
     "meaningless credit; the ceiling stops a 100-model block from turning the rule into a 26 m "
     "trigger (12 m half + 6 m base = 18 m is already a generous 'on top of'). A one-model unit is "
     "NOT clamped up: it gets 0 (source 'single')."),
    ("FOURTH.AIR_DROP_DELAY_S / ENEMY_LEAD", "1.5 s / 0.3 - rounds 110-112, unchanged",
     "The enemy's lead time and its share: enemy_projected = enemy + v_enemy * 1.5 s * 0.3. These "
     "define the SEGMENT the path test measures, so a wrong-looking path is tuned with THESE - the "
     "path test does not add a dial of its own."),
    ("FOURTH.AIR_DROP_CASTER_DELAY_S / CASTER_LEAD", "1.5 s / 0.5 - round 111, unchanged",
     "The caster's own lead time and share: caster_projected = caster + v_caster * 1.5 s * 0.5. "
     "This is the POINT the perpendicular distance is measured TO; AIR_DROP_INHERIT = false still "
     "means the ordnance does not carry the caster's velocity."),
]

TUNING_ROWS = [
    ("the enemy's MODELS sweep under the caster but the CENTRE stays outside 6 m",
     "FOURTH.AIR_DROP_MODEL_RADIUS_M / _FRONTAGE_MAX_M",
     "0.6 -> 0.7 -> 0.8, or FRONTAGE_MAX 12 -> 15. The credit is under-stated (the round-113 field "
     "report). The log names the source (`ordered`, `models`, `clamped`, `single`) and the arithmetic."),
    ("the drop leaves while the enemy is visibly NOT underneath",
     "FOURTH.AIR_DROP_FRONTAGE_MAX_M (then CENTER_M)",
     "12 -> 8 -> 6, or set the credit to 0 by the same constant (a 0 ceiling restores the pure 6 m "
     "point test). Only then lower AIR_DROP_CENTER_M."),
    ("a LORD / HERO is targeted",
     "nothing - report it",
     "Every infantry-class character is ONE model and is skipped by initial_number_of_men() == 1. A "
     "character that still fires is NOT infantry-class (a chariot crew of 2-8 men is class `com`) "
     "and should have been removed by the infantry filter: that is a bug to report, not a dial."),
    ("the path is judged in the wrong PLACE (ahead of / behind the enemy)",
     "FOURTH.AIR_DROP_DELAY_S / AIR_DROP_ENEMY_LEAD",
     "1.5 s / 0.3 define the segment's END point. The path test adds no dial of its own - tune the "
     "lead, exactly as before."),
    ("still EARLY while STATIONARY (both bodies parked)",
     "FOURTH.AIR_DROP_DELAY_S",
     "1.5 -> 1.2 -> 1.0. Both lead factors multiply zero velocity when nothing moves, so the fall "
     "time itself is too long; it shrinks BOTH bodies."),
]


def set_wrapped(ws, row, col, value, bold=False):
    c = ws.cell(row=row, column=col, value=value)
    c.alignment = WRAP
    if bold:
        c.font = Font(bold=True)
    return c


# ------------------------------------------------------------------ fingerprints
before = {}
import glob
for p in sorted(glob.glob(os.path.join(DOCS, "WH3_abilities_master_v*_2026-10-1*.xlsx"))):
    base = os.path.basename(p)
    if base == os.path.basename(V14):
        continue
    # every EARLIER numbered version, whatever the date in its name
    stem = base.split("_v")[1].split("_")[0]
    if stem.isdigit() and int(stem) < 14:
        before[p] = hashlib.md5(open(p, "rb").read()).hexdigest()

if os.path.exists(V14):
    os.remove(V14)
shutil.copy2(V13, V14)

wb = openpyxl.load_workbook(V14)

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
    assert "THE ENEMY-SIDE DIAL (round 112)." in v, (r, "no round-112 paragraph")
    assert "THE VELOCITY is REBUILT" in v, (r, "no velocity paragraph")
    assert OLD_RECHECK in v, (r, "no re-check sentence")
    assert OLD_CONST in v, (r, "no 6 m constant sentence")
    i_log = v.find(LOG_START)
    j_log = v.find(LOG_END)
    assert 0 < i_log < j_log, (r, i_log, j_log)
    # the log block ENDS at the old (round-110) text; the marker is the end of
    # the round-112 log paragraph
    new = v.replace(OLD_PREFIX, NEW_PREFIX, 1)
    new = new.replace("THE VELOCITY is REBUILT", PATH_PARA + "THE VELOCITY is REBUILT", 1)
    i2 = new.find(LOG_START)
    j2 = new.find(LOG_END, i2)
    new = new[:i2] + NEW_LOG + new[j2 + len(LOG_END):]
    new = new.replace(OLD_RECHECK, NEW_RECHECK, 1)
    new = new.replace(OLD_CONST, NEW_CONST, 1)
    ab.cell(row=r, column=trig).value = new
    ab.cell(row=r, column=trig).alignment = WRAP
    sr = ab.cell(row=r, column=col["Status reason / family"]).value or ""
    if "round 113" not in sr:
        ab.cell(row=r, column=col["Status reason / family"]).value = (
            sr + " | trigger rule: rounds 107-113 (the enemy's PATH is the test: segment = "
                 "current -> projected, perp = distance from it to the caster's projected point, "
                 "fire when perp <= 6 m + a DERIVED half-frontage [ordered_width/2 or "
                 "ceil(men/2) x 0.6 m, 2 ranks, clamped 1..12 m, fail-closed 0]; one-model "
                 "candidates skipped once per episode on initial_number_of_men() == 1; four dials "
                 "unchanged)")
    changed += 1
assert changed == 19, changed
print("abilities rows updated:", changed)

# ----------------------------------------------------------------- Definitions
df = wb["Definitions"]
df.cell(row=1, column=1, value="DEFINITIONS - WH3 ability master v14 (%s)" % TODAY)
gl = df.cell(row=69, column=3).value or ""
assert gl.startswith("an enemy INFANTRY unit that will be UNDER the caster"), gl[:80]
G_OLD = ("the horizontal CENTRE-TO-CENTRE separation of the two PROJECTED points "
         "(battle_unit:position(), X/Z only - get_y is HEIGHT) must be inside "
         "FOURTH.AIR_DROP_CENTER_M = 6 m")
G_NEW = ("and ROUND 113 REPLACES THAT POINT TEST: the PATH test decides - the shortest horizontal distance from the enemy's segment "
         "(current -> projected) to the caster's projected point must be inside FOURTH.AIR_DROP_"
         "CENTER_M = 6 m PLUS the candidate's DERIVED half-frontage (ordered_width/2, or "
         "ceil(models/2) x the 0.6 m per-model radius over two ranks, clamped to 1..12 m, "
         "fail-closed 0); a candidate whose initial_number_of_men() is EXACTLY 1 is skipped, once "
         "per episode, because every infantry-class lord/hero is one model")
assert G_OLD in gl, "the v13 bound clause is not in the glossary row"
gl = gl.replace(G_OLD, G_NEW, 1)
set_wrapped(df, 69, 3, gl)

last = df.max_row
while last > 1 and all(df.cell(row=last, column=c).value in (None, "") for c in range(1, 7)):
    last -= 1
r0 = last + 2
h = df.cell(row=r0, column=1,
            value="11. THE PATH RULE AND THE DERIVED FRONTAGE (round 113) - the threshold formula, "
                  "the frontage derivation and the single-entity exclusion")
h.font = Font(bold=True, size=12)
set_wrapped(df, r0 + 1, 1,
            "THE DECISION (the exact formula the evaluator runs)", bold=True)
set_wrapped(df, r0 + 1, 2, "", bold=True)
set_wrapped(df, r0 + 1, 3, "", bold=True)
set_wrapped(df, r0 + 2, 1,
            "segment = (enemy_x, enemy_z) -> (enemy_projected_x, enemy_projected_z); "
            "enemy_projected = enemy + v_enemy * AIR_DROP_DELAY_S * AIR_DROP_ENEMY_LEAD; "
            "caster_projected = caster + v_caster * AIR_DROP_CASTER_DELAY_S * AIR_DROP_CASTER_LEAD; "
            "perp = shortest horizontal distance from the SEGMENT to caster_projected "
            "(point-to-segment, parameter clamped to 0..1 over x/z); "
            "threshold = AIR_DROP_CENTER_M + ad_frontage(enemy); "
            "FIRE iff perp <= threshold.")
set_wrapped(df, r0 + 2, 3,
            "The four leads are unchanged (1.5 s x 0.3 enemy, 1.5 s x 0.5 caster). The path test "
            "adds no dial of its own - it changes WHAT is measured (a segment, not a point) and "
            "adds ONE derived credit. The pre-cast re-check re-runs the same formula on fresh reads.")

set_wrapped(df, r0 + 4, 1, "THE FRONTAGE DERIVATION (ad_frontage) - in order", bold=True)
set_wrapped(df, r0 + 5, 1, "Source", bold=True)
set_wrapped(df, r0 + 5, 2, "Rule", bold=True)
set_wrapped(df, r0 + 5, 3, "Why", bold=True)
FRONTAGE_ROWS = [
    ("ordered", "half = ordered_width() / 2",
     "The engine's own formation width ('the width of the position to which the unit has been "
     "ordered in metres'). Preferred whenever it answers a sane positive number."),
    ("models", "per_rank = ceil(models / 2); half = per_rank * 0.6 m",
     "The fallback, under the documented TWO-RANK assumption. models = the unit's CURRENT alive "
     "count (a depleted block really is narrower), measured with the count the picker already "
     "read - no extra engine read."),
    ("clamped", "1 m <= half <= 12 m",
     "A value outside the range is pulled in and the source says so. The ceiling keeps a "
     "100-model block from firing a drop 26 m away."),
    ("single", "half = 0",
     "A one-model unit has no frontage; the 6 m base already covers its footprint."),
    ("unreadable", "half = 0",
     "FAIL CLOSED: if neither read answers, the plain 6 m point distance decides, exactly as "
     "before round 113."),
]
for i, (src, rule, why) in enumerate(FRONTAGE_ROWS):
    rr = r0 + 6 + i
    set_wrapped(df, rr, 1, src)
    set_wrapped(df, rr, 2, rule)
    set_wrapped(df, rr, 3, why)

b0 = r0 + 6 + len(FRONTAGE_ROWS) + 1
set_wrapped(df, b0, 1, "THE EVIDENCE BEHIND THE TWO CONSTANTS (from the extracted tables)", bold=True)
set_wrapped(df, b0 + 1, 1, "battle_entities.radius over the 942 infantry land_units rows", bold=True)
set_wrapped(df, b0 + 1, 3,
            "min 0.5 m | MODE 0.6 m (168 rows) | median 0.7 m | p90 3.9 m | max 14.0 m. 0.6 m ships "
            "(the modal value, conservative against the median); the Terradon rider is 0.6 m.")
set_wrapped(df, b0 + 2, 1, "land_units.rank_depth over the same rows", bold=True)
set_wrapped(df, b0 + 2, 3,
            "1 (245 rows) | 3 (150) | 5 (143) | 6 (133) | 4 (125) | 8 (68): TWO RANKS IS THE WIDE "
            "END, and a wider frontage is the safe direction for a drop that must not miss a block "
            "sweeping underneath.")
set_wrapped(df, b0 + 3, 1, "character units with num_men >= 2 (the lord/hero question)", bold=True)
set_wrapped(df, b0 + 3, 3,
            "146 rows (80 lord + 66 hero), EVERY ONE land_units class `com` - not infantry - and "
            "every INFANTRY-CLASS lord/hero row (0 lord + 6 hero) has num_men = 1. So "
            "initial_number_of_men() == 1 covers the whole infantry character case, and the "
            "1,409-key commander set is not needed here.")
set_wrapped(df, b0 + 4, 1, "SINGLE ENTITY - the exact rule", bold=True)
set_wrapped(df, b0 + 4, 3,
            "skip when battle_unit:initial_number_of_men() == 1 (EXACT equality: zero models cannot "
            "exist). INITIAL, not current - a 20-model block ground down to one survivor is still "
            "judged as a block. Unreadable -> SKIP (fail-closed). Logged once per episode as "
            "'single entity (1 model)'.")

c0 = b0 + 6
h2 = df.cell(row=c0, column=1,
             value="THE FRONTAGE CREDIT - constants, what they do and how to tune them (round 113)")
h2.font = Font(bold=True, size=12)
set_wrapped(df, c0 + 1, 1, "Constant", bold=True)
set_wrapped(df, c0 + 1, 2, "Ships as", bold=True)
set_wrapped(df, c0 + 1, 3, "What it does / how to tune it", bold=True)
for i, (name, val, why) in enumerate(CONST_ROWS):
    rr = c0 + 2 + i
    set_wrapped(df, rr, 1, name)
    set_wrapped(df, rr, 2, val)
    set_wrapped(df, rr, 3, why)
tot = c0 + 2 + len(CONST_ROWS)
set_wrapped(df, tot, 1, "TOTAL", bold=True)
set_wrapped(df, tot, 2, "4 dials + 1 bound + 1 flag + 4 frontage constants", bold=True)
set_wrapped(df, tot, 3,
            "The rule is ONE line of arithmetic (above). Only the FRONTAGE constants are new in "
            "round 113; the four leads, the 6 m bound and the momentum flag are unchanged since "
            "rounds 112 / 109 / 110.")

g0 = tot + 2
g = df.cell(row=g0, column=1, value="TUNING GUIDE (round 113) - one change per field test")
g.font = Font(bold=True, size=12)
set_wrapped(df, g0 + 1, 1, "Symptom", bold=True)
set_wrapped(df, g0 + 1, 2, "What to change", bold=True)
set_wrapped(df, g0 + 1, 3, "Order to try", bold=True)
for i, (sym, dial, order) in enumerate(TUNING_ROWS):
    rr = g0 + 2 + i
    set_wrapped(df, rr, 1, sym)
    set_wrapped(df, rr, 2, dial)
    set_wrapped(df, rr, 3, order)
set_wrapped(df, g0 + 2 + len(TUNING_ROWS), 1, "TOTAL", bold=True)
set_wrapped(df, g0 + 2 + len(TUNING_ROWS), 2, "1 rule", bold=True)
set_wrapped(df, g0 + 2 + len(TUNING_ROWS), 3,
            "The field log prints, per decision, the SEGMENT, the PERP, the FRONTAGE WITH ITS "
            "SOURCE and the THRESHOLD - so a wrong decision can be attributed to the base bound, "
            "the model count, the ordered width or the clamp without a new build.")

# -------------------------------------------------------------------- Numbers
nm = wb["Numbers"]
for r in range(1, nm.max_row + 1):
    v = nm.cell(row=r, column=1).value
    if not isinstance(v, str):
        continue
    if v.startswith("Date: 2026-10-18"):
        nm.cell(row=r, column=1).value = (
            "Date: 2026-10-18     Rule in force since: 2026-10-17     Inventory: 1,799 active "
            "abilities     (v14: round 113 - THE PATH TEST AND THE DERIVED FRONTAGE: the drop is "
            "judged against the enemy's PATH (segment = current -> projected) rather than its "
            "centre point, and the 6 m bound gains a DERIVED half-frontage credit - ordered_width/2 "
            "when readable, otherwise ceil(models/2) x the documented 0.6 m per-model radius over "
            "two ranks, clamped to 1..12 m, fail-closed 0. A one-model candidate "
            "(initial_number_of_men() == 1) is skipped, once per episode)")
    elif v.startswith("Trigger families after round"):
        nm.cell(row=r, column=1).value = v.replace("round 112", "round 113")
    elif v.startswith("Reconciliation: included"):
        nm.cell(row=r, column=1).value = (
            "Reconciliation: included 1,141 + excluded 658 = 1,799. Implemented among the included "
            "742 + not implemented 399 = 1,141. The mod's ABILITIES table is 689 entries / 742 keys "
            "(the two Soulfire keys are ONE entry, the two Slicing Shards keys are ONE entry). The "
            "tracker carries the implemented ROWS; implemented keys with no row of their own ride a "
            "row that names its sibling. Round 113 is a BEHAVIOUR change to ONE evaluator: the "
            "air-drop family stays 12 entries / 19 keys, the 46 trigger families are unchanged, and "
            "every count on this sheet - inventory 1,799, excluded 658, included 1,141, implemented "
            "742, not implemented 399, the eight carrier families, the 46 evaluator rows - is "
            "IDENTICAL to v13. What changed: the TEST (a path segment and a perpendicular distance "
            "instead of a point-to-point separation), ONE derived credit (the half-frontage), FOUR "
            "new constants (0.6 m radius, 2 ranks, 1..12 m clamp), the ONE-MODEL exclusion "
            "(initial_number_of_men() == 1, once per episode), the trigger text of those 19 rows "
            "(they name the path test, the frontage credit and the single-entity exclusion), ONE "
            "new Definitions section (11) with the threshold formula and the derivation, and the "
            "log fields that make a wrong decision attributable (segment / perp / frontage+source / "
            "threshold). The four leads, the 6 m base bound, AIR_DROP_INHERIT, air_only / "
            "no_melee, the self-centred cast and every fail-closed read are unchanged.")

# ------------------------------------------------------------------ Changelog
cl = wb["Changelog"]
row = cl.max_row + 1
while row > 1 and all(cl.cell(row=row - 1, column=c).value in (None, "") for c in range(1, 5)):
    row -= 1
cl.cell(row=row, column=1).value = TODAY
cl.cell(row=row, column=2).value = "v14"
cl.cell(row=row, column=3).value = (
    "ROUND 113 - THE PATH TEST, THE DERIVED FRONTAGE AND THE SINGLE-ENTITY EXCLUSION. (1) WHAT THE "
    "FIELD SAID: a Sky-junk hovering BESIDE a 20-model zombie block never fired while the block "
    "walked past - the enemy's CENTRE stayed 10+ m away even though its models swept under the "
    "caster - and separately one fired at a LORD. (2) THE USER'S RULINGS, verbatim: '1. Why "
    "combine? The started with one model would cover the other case, woudn't it? Also, why "
    "comparison is 1 or less? It cannot be less, then the unit does not exist. So comparion should "
    "be equal to 1. Am I forgetting something? If you agree, start implementing with point 2.' and "
    "'2. Let's implement the the path test with a derived frontage that you suggest.' (3) THE RULE: "
    "segment = enemy_current -> enemy_projected (the enemy's own dials, unchanged); perp = the "
    "shortest HORIZONTAL distance from that segment to the caster's projected point "
    "(point-to-segment on x/z, parameter clamped 0..1); FIRE WHEN perp <= AIR_DROP_CENTER_M + "
    "ad_frontage(enemy). (4) THE FRONTAGE CREDIT IS DERIVED: ordered_width()/2 when sane (source "
    "'ordered'); otherwise ceil(models/2) * the per-model radius under a documented TWO-RANK "
    "assumption (source 'models'); clamped to 1..12 m half-width ('clamped'); a one-model unit gets "
    "0 ('single'); unreadable -> 0, fail-closed ('unreadable'). The radius is a CONSTANT, 0.6 m - "
    "the MODAL battle_entities.radius over the 942 infantry land_units rows (median 0.7) - because "
    "battle Lua can read neither land_units.man_entity nor battle_entities.radius. (5) THE "
    "SINGLE-ENTITY EXCLUSION: initial_number_of_men() == 1 -> skipped, EXACT equality (zero models "
    "cannot exist), INITIAL not current (a depleted 20-model block is still a block), logged once "
    "per episode as 'single entity (1 model)'. THE COMMANDER KEY SET IS NOT CONSULTED HERE: every "
    "infantry-class lord/hero in the data is one model (0 lord and 6 hero rows, all num_men = 1), "
    "so the count covers it; the 146 multi-model character rows are all class `com`, not infantry. "
    "(6) THE PRE-CAST RE-CHECK re-runs the SAME segment test on fresh reads (one ad_lead call gives "
    "the current AND projected point), so a drift skips the cast instead of spending it. (7) KEPT "
    "EXACTLY: the four dials (1.5 s / 0.3 enemy, 1.5 s / 0.5 caster), the 6 m base bound, "
    "AIR_DROP_INHERIT = false, air_only / no_melee, the self-centred cast, every fail-closed read. "
    "(8) COUNTS: UNCHANGED - 689 entries / 742 keys, air_drop_on_infantry 12 entries / 19 keys, 46 "
    "evaluators. Harness 113: 4610 checks / 0 failures (run twice, byte-identical); red control "
    "(the round-112 build) 55 failures, ALL in the new section. Installed pack md5 "
    "004a1293c35f29a2b863fd399d733cf6.")
cl.cell(row=row, column=4).value = (
    "the user's sixth air-drop field report + their two rulings; docs/WH3_round113_airdrop_pathtest.md; "
    "harness 113 (worlds A1 the reported side pass at 10 m with the credit, A2 the same geometry "
    "with one alive model, A3 the path crossing the point, B the one-model lord, C 15 m silent, "
    "D1/D2/D3 the three frontage sources, E the fail-closed fallback, F the drift re-check, G the "
    "depleted block) plus section-0 pins in BOTH the live and the annotated copy.")
for c in range(1, 5):
    cl.cell(row=row, column=c).alignment = WRAP

wb.save(V14)
print("saved", V14, os.path.getsize(V14))

# ---------------------------------------------------------------- verify (disk)
wb2 = openpyxl.load_workbook(V14)
a2 = wb2["Abilities"]
h2 = [c.value for c in a2[1]]
i2 = {h: n + 1 for n, h in enumerate(h2)}
air = [r for r in range(2, a2.max_row + 1)
       if a2.cell(row=r, column=i2["Trigger family"]).value == "air_drop_on_infantry"]
texts = [(r, a2.cell(row=r, column=i2["Trigger (as implemented)"]).value or "") for r in air]
need = ["FOURTH.AIR_DROP_MODEL_RADIUS_M = 0.6 m", "FOURTH.AIR_DROP_RANKS", "1 .. 12 m",
        "FOURTH.AIR_DROP_CENTER_M = 6 m", "FOURTH.AIR_DROP_ENEMY_LEAD = 0.3",
        "FOURTH.AIR_DROP_CASTER_DELAY_S = 1.5 s", "FOURTH.AIR_DROP_CASTER_LEAD = 0.5",
        "THE PATH TEST AND THE DERIVED FRONTAGE (round 113)", "perp", "segment",
        "single entity (1 model)", "EXACT EQUALITY", "THE COMMANDER KEY SET IS DELIBERATELY NOT "
        "USED HERE", "initial_number_of_men()", "THE LOG, PER DECISION (round 113)",
        "threshold=12.00m (bound=6m + frontage=6.00m)", "[1003]", "EXACT distances"]
bad = [(r, [x for x in need if x not in t]) for r, t in texts if any(x not in t for x in need)]
stale = [r for r, t in texts if "rounds 107-112" in t or "THE LOG, PER DECISION (round 112)" in t
         or "the TWO-BODY PROJECTION is RE-TAKEN" in t]
print("VERIFY air rows:", len(air), "| missing new rule:", bad, "| stale:", stale)
assert len(air) == 19 and not bad and not stale

d2 = wb2["Definitions"]
gl2 = d2.cell(row=69, column=3).value or ""
assert "the PATH test" in gl2 and "initial_number_of_men()" in gl2, "glossary row lacks the path rule"
const_names = [d2.cell(row=r, column=1).value for r in range(1, d2.max_row + 1)]
for want in ("FOURTH.AIR_DROP_MODEL_RADIUS_M", "FOURTH.AIR_DROP_RANKS",
             "FOURTH.AIR_DROP_FRONTAGE_MIN_M / _MAX_M", "ordered", "models", "clamped",
             "single", "unreadable"):
    assert want in const_names, want
formula = [n for n in const_names if isinstance(n, str) and "threshold = AIR_DROP_CENTER_M" in n]
assert formula, "the threshold formula row is missing"
tuning = [n for n in const_names if isinstance(n, str) and "MODELS sweep under the caster" in n]
assert tuning, "the round-113 tuning-guide table is missing"
print("VERIFY definitions: section 11 (formula + derivation + evidence) and the tuning guide present")
n2 = wb2["Numbers"]
print("VERIFY numbers:", (n2.cell(row=7, column=1).value or "")[:90])
print("VERIFY changelog last:", wb2["Changelog"].cell(row=wb2["Changelog"].max_row, column=2).value)

# the older versions must be byte-identical
after = {p: hashlib.md5(open(p, "rb").read()).hexdigest() for p in before}
assert before == after, "an earlier version changed!"
print("v1-v13 byte-identical:", len(before), "files checked")
