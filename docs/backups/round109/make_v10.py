import openpyxl, shutil, os, sys

SRC = r"C:/Users/vlady/Desktop/WH3_mod/docs/WH3_abilities_master_v9_2026-10-17.xlsx"
DST = r"C:/Users/vlady/Desktop/WH3_mod/docs/WH3_abilities_master_v10_2026-10-18.xlsx"

NEW_MIDDLE = (
    "Fires when an enemy INFANTRY unit is UNDER the caster: the HORIZONTAL CENTRE-TO-CENTRE "
    "distance between the two units - battle_unit:position() is 'the centre position of the main "
    "squad of the unit' (battle_unit.lua:114) - must be inside FOURTH.AIR_DROP_CENTER_M = 6 m. "
    "The ground plane is X/Z: battle_vector:get_y() is HEIGHT (a 3D read would measure 30-60 m "
    "from a unit directly underneath), so the engine's battle_vector:distance_xz() is used with a "
    "sqrt(x/z) fallback. Infantry read: battle_unit:is_infantry() first, unit_class() exact-match "
    "inf_mel/inf_mis/inf_spr second, FAIL CLOSED. "
    "WHY NOT EDGE-TO-EDGE (round 109): unit_distance() measures the gap between the two BOUNDING "
    "BOXES (battle_unit.lua:160), and two boxes can be half a metre apart while their CENTRES are "
    "15 m apart - so the old 1 m EDGE bound still released the ordnance while the flyer was nowhere "
    "near over the target (the user's second report: 'because the distance is calculated edge to "
    "edge, it still drops the rocks too soon'). 6 m is ONE documented constant standing in for the "
    "formation footprint, because the script API has NO per-unit radius / footprint / bounding box "
    "/ size read at all (script_units:radius() is a COLLECTION's spread radius; "
    "battle_entities.radius = 0.6 m is ONE model's collision radius). It is the one value to tune: "
    "lower it if the drop still releases early, raise it if it never fires. The picker logs both "
    "positions, the centre distance, the edge gap (diagnostic only) and the 6 m bound, and writes a "
    "'watch: nearest INFANTRY ... centre=Nm' line whenever it does not fire."
)

NEW_DEF = (
    "an enemy INFANTRY unit UNDER the caster: the HORIZONTAL CENTRE-TO-CENTRE distance "
    "(battle_unit:position(), X/Z only - get_y is height) inside FOURTH.AIR_DROP_CENTER_M = 6 m. "
    "Round 109 replaced the EDGE-TO-EDGE unit_distance() proxy: two bounding boxes can be 0.5 m "
    "apart while their centres are 15 m apart, which is why the 1 m edge bound released the rocks "
    "too soon. 6 m is ONE documented constant standing in for the formation footprint (the API has "
    "no per-unit radius / bbox / size read); lower it if the drop is still early, raise it if it "
    "never fires. The caster must be airborne where the row says so (the `grounded` flag or a "
    "flying-only carrier) and OUT of melee where the row says so (`engaged_in_melee`); both the "
    "caster and the chosen enemy are re-read immediately before the cast (centre distance included) "
    "and the cast is skipped rather than spent."
)

if os.path.exists(DST):
    os.remove(DST)
shutil.copy2(SRC, DST)

wb = openpyxl.load_workbook(DST)
ab = wb['Abilities']
hdr = [c.value for c in ab[1]]
idx = {h: i for i, h in enumerate(hdr)}
col_trig = idx['Trigger (as implemented)'] + 1
col_fam = idx['Trigger family'] + 1

changed = 0
for r in range(2, ab.max_row + 1):
    if ab.cell(row=r, column=col_fam).value != 'air_drop_on_infantry':
        continue
    v = ab.cell(row=r, column=col_trig).value or ''
    i = v.find("Fires when an enemy INFANTRY unit is")
    j = v.find("no per-row edit.")
    assert i > 0 and j > i, ("cannot slice row %d" % r)
    j += len("no per-row edit.")
    new = v[:i] + NEW_MIDDLE + v[j:]
    ab.cell(row=r, column=col_trig).value = new
    changed += 1
assert changed == 19, changed
print("abilities rows updated:", changed)

df = wb['Definitions']
assert df.cell(row=69, column=1).value == 'air_drop_on_infantry'
df.cell(row=69, column=3).value = NEW_DEF

nm = wb['Numbers']
# the date / version header line
for r in range(1, nm.max_row + 1):
    v = nm.cell(row=r, column=1).value
    if isinstance(v, str) and v.startswith("Date: 2026-10-18"):
        nm.cell(row=r, column=1).value = (
            "Date: 2026-10-18     Rule in force since: 2026-10-17     Inventory: 1,799 active "
            "abilities     (v10: round 109 - the air-drop test is a HORIZONTAL CENTRE distance of "
            "6 m, not the 1 m EDGE-TO-EDGE proxy: two bounding boxes can be 0.5 m apart while their "
            "centres are 15 m apart, which is why the rocks still released too soon)")
    if isinstance(v, str) and v.startswith("Trigger families after round 108"):
        nm.cell(row=r, column=1).value = v.replace("round 108", "round 109")
    if isinstance(v, str) and v.startswith("Reconciliation: included"):
        nm.cell(row=r, column=1).value = (
            "Reconciliation: included 1,141 + excluded 658 = 1,799. Implemented among the included "
            "742 + not implemented 399 = 1,141. The mod's ABILITIES table is 689 entries / 742 keys "
            "(the two Soulfire keys are ONE entry, the two Slicing Shards keys are ONE entry). The "
            "tracker carries the implemented ROWS; implemented keys with no row of their own ride a "
            "row that names its sibling. Round 109 is a BEHAVIOUR-ONLY change: the air-drop family "
            "stays 12 entries / 19 keys and every count on this sheet - inventory, in-wheel, "
            "excluded, implemented, the carrier families and the 46 trigger families - is IDENTICAL "
            "to v9. Only the trigger column of those 12 entries and the rule itself changed."
        )

cl = wb['Changelog']
next_row = cl.max_row + 1
while next_row > 1 and all(cl.cell(row=next_row - 1, column=c).value in (None, "") for c in range(1, 5)):
    next_row -= 1
cl.cell(row=next_row, column=1).value = '2026-10-18'
cl.cell(row=next_row, column=2).value = 'v10'
cl.cell(row=next_row, column=3).value = (
    "ROUND 109 - THE AIR DROP IS NOW A CENTRE-BASED OVERLAP TEST. (1) WHAT WAS WRONG: "
    "battle_unit:unit_distance() is EDGE-TO-EDGE (battle_unit.lua:160) - the gap between the two "
    "BOUNDING BOXES - so a wide flying formation beside a wide infantry block reads a fraction of a "
    "metre while the flyer's CENTRE is 15 m from the block's centre. The round-108 1 m edge bound "
    "therefore still fired while the flyer was nowhere near over the target, exactly as the user "
    "reported: 'because the distance is calculated edge to edge, it still drops the rocks too soon'. "
    "(2) THE NEW RULE: the HORIZONTAL CENTRE-TO-CENTRE distance between the caster and the enemy - "
    "battle_unit:position(), X/Z only because battle_vector:get_y() is HEIGHT, via the engine's "
    "battle_vector:distance_xz() with a sqrt(x/z) fallback - must be inside "
    "FOURTH.AIR_DROP_CENTER_M = 6 m. 6 m is ONE documented constant standing in for the formation "
    "footprint: the API has NO per-unit radius / footprint / bbox / size read (script_units:radius() "
    "is a collection spread radius; battle_entities.radius = 0.6 m is one MODEL's collision radius). "
    "One value to tune - lower it if the drop is still early, raise it if it never fires. (3) THE "
    "FAMILY'S EXEMPTIONS ARE KEPT: the 70% map is still bypassed for air_drop_on_infantry, the "
    "flying / out-of-melee requirements are unchanged, the pre-cast re-check now re-reads the CENTRE "
    "distance and logs it, and an unreadable position FAILS CLOSED. (4) THE LOG now prints both "
    "positions, the centre distance, the edge gap (diagnostic only) and the bound, plus a "
    "'watch: nearest INFANTRY ... centre=Nm' line whenever the drop does not fire. (5) COUNTS: "
    "UNCHANGED - 689 entries / 742 keys, air_drop_on_infantry 12 entries / 19 keys, 46 evaluators; "
    "behaviour only. Harness 109: 4098 checks / 0 failures, red control 36 failures all accounted "
    "for; installed pack md5 947049dcf021ae101d1d509208c85e71."
)
cl.cell(row=next_row, column=4).value = (
    "the user's second air-drop field report ('because the distance is calculated edge to edge, it "
    "still drops the rocks too soon'); the API dump (battle_unit.lua, battle_vector.lua) and the "
    "vanilla lib_bsu.lua for the position/size reads; round 109 doc "
    "docs/WH3_round109_airdrop_centre.md"
)

wb.save(DST)
print("saved", DST, os.path.getsize(DST))

# ---------------------------------------------------------------- verify from disk
wb2 = openpyxl.load_workbook(DST)
ab2 = wb2['Abilities']
hdr2 = [c.value for c in ab2[1]]
i2 = {h: i for i, h in enumerate(hdr2)}
rows2 = ab2.max_row
air = [r for r in range(2, ab2.max_row + 1) if ab2.cell(row=r, column=i2['Trigger family'] + 1).value == 'air_drop_on_infantry']
bad = [r for r in air if 'FOURTH.AIR_DROP_CENTER_M = 6' not in (ab2.cell(row=r, column=i2['Trigger (as implemented)'] + 1).value or '')]
stale = [r for r in range(2, ab2.max_row + 1) if 'AIR_DROP_BOUND_M' in str(ab2.cell(row=r, column=i2['Trigger (as implemented)'] + 1).value or '')]
print("VERIFY abilities rows:", rows2, "air rows:", len(air), "missing new rule:", bad, "stale token rows:", stale)
print("VERIFY changelog last:", wb2['Changelog'].cell(row=wb2['Changelog'].max_row, column=2).value)
print("VERIFY definitions:", wb2['Definitions'].cell(row=69, column=3).value[:80])
print("VERIFY numbers header:", wb2['Numbers'].cell(row=5, column=1).value[:120])
