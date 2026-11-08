import io, re

P = r"C:/Users/vlady/Desktop/WH3_mod/docs/WH3_ability_tracker.md"
with open(P, "rb") as f:
    raw = f.read()
assert raw.count(b"\r") == 0, "CRLF in tracker before the edit"
s = raw.decode("utf-8")

OLD = ("(inside the family's overlap bound - 1 m (round 108: a USER-CHOSEN TEST value, much tighter "
       "than the 70% rule's 7 m; unit_distance is edge-to-edge, so a unit directly under the caster "
       "reads near 0-5 m, and this one constant is easy to raise))")
NEW = ("(the HORIZONTAL CENTRE-TO-CENTRE distance between the caster and the enemy - "
       "battle_unit:position(), X/Z only because battle_vector:get_y() is HEIGHT - is inside "
       "FOURTH.AIR_DROP_CENTER_M = 6 m. **Round 109 replaced the 1 m EDGE-TO-EDGE unit_distance "
       "proxy**: two bounding boxes can be 0.5 m apart while their CENTRES are 15 m apart, which is "
       "why the rocks were still released too soon. 6 m is ONE documented constant standing in for "
       "the formation footprint (the API has no per-unit radius / bbox / size read); lower it if the "
       "drop is still early, raise it if it never fires)")

n = s.count(OLD)
assert n == 19, n
s = s.replace(OLD, NEW)

# glossary row
GL_OLD_START = "| `air_drop_on_infantry` | **round 108** - an enemy INFANTRY unit is UNDER the caster:"
i = s.find(GL_OLD_START)
assert i > 0
j = s.find("\n", i)
gl_old = s[i:j]
gl_new = ("| `air_drop_on_infantry` | **round 109** - an enemy INFANTRY unit is UNDER the caster: the "
          "**HORIZONTAL CENTRE-TO-CENTRE** distance (`battle_unit:position()`, **X/Z only** because "
          "`battle_vector:get_y()` is HEIGHT; `battle_vector:distance_xz()`) is inside "
          "**`FOURTH.AIR_DROP_CENTER_M = 6`** - ONE documented constant standing in for the formation "
          "footprint, because the script API has **no per-unit radius / footprint / bbox / size read** "
          "(`script_units:radius()` is a collection spread radius; `battle_entities.radius = 0.6 m` is "
          "one MODEL's collision radius). The round-108 **1 m EDGE-TO-EDGE** `unit_distance()` proxy is "
          "**retired**: the gap between two bounding boxes can be 0.5 m while their centres are 15 m "
          "apart, which is exactly why the rocks were still released too soon. **One value to tune** - "
          "lower it if the drop is still early, raise it if it never fires. Unchanged: `is_currently_"
          "flying()` where the row declares `grounded` (or every carrier flies), out-of-melee where the "
          "row declares `engaged_in_melee`, the cast on the OWNER, and the logged pre-cast re-check, "
          "which now re-reads the CENTRE distance (an unreadable position FAILS CLOSED). The picker logs "
          "both positions, the centre distance, the edge gap (diagnostic only) and the bound, plus a "
          "`watch: nearest INFANTRY ... centre=Nm` line when it does not fire. |")
s = s[:i] + gl_new + s[j:]

# a new dated update line, right after the harness-108 one
ANCHOR = "installed pack md5 `4a1cedca34d0c4936eab4e9d5bd12f1a`.\n"
assert s.count(ANCHOR) == 1
UPDATE = (
"**Update 2026-10-18 (harness 109 — THE AIR DROP IS A HORIZONTAL CENTRE TEST, NOT AN EDGE GAP).** "
"One field report is **implemented and shipping**: the user's second air-drop test — *\"because the "
"distance is calculated edge to edge, it still drops the rocks too soon.\"* **THE CAUSE, FROM THE API "
"DUMP:** `battle_unit:unit_distance()` is *\"the shortest distance in metres between this unit and a "
"supplied unit, taking into account their bounding box rather than just working out the "
"centre-to-centre distance\"* (`battle_unit.lua:160`) — it is the gap between the two **BOXES**, so a "
"wide flying formation beside a wide infantry block reads a fraction of a metre while the flyer's "
"**centre** is 15 m from the block's centre. The round-108 **1 m edge bound** therefore still fired "
"while the flyer was nowhere near over the target. **THE NEW RULE:** the **HORIZONTAL "
"CENTRE-TO-CENTRE** distance — `battle_unit:position()`, *\"the centre position of the main squad of "
"the unit\"* (`battle_unit.lua:114`) — must be inside **`FOURTH.AIR_DROP_CENTER_M = 6`**. The ground "
"plane is **X/Z**: `battle_vector:get_y()` is *\"the height of the vector position from the water "
"plane\"* and `get_z()` is north-south, so the engine's `battle_vector:distance_xz()` (*\"disregarding "
"any height difference\"*) is used, with a `sqrt(x²+z²)` fallback; a 3D read would measure 30-60 m "
"from a unit directly underneath. **WHY A CONSTANT:** the dump has **no per-unit radius, footprint, "
"bounding box or size read anywhere** — `battle_unit.lua`'s 100 methods carry none; "
"`script_units:radius()` (`lib_bsu.lua:2600`) is a **collection's** spread radius around its mean "
"centre and **no vanilla script calls it**; `battle_entities.radius = 0.6 m` is **one model's** "
"collision radius (a Terradon rider), not the unit's. 6 m is the **one value to tune** (the drop "
"families carry 10 models in a rank_depth-2 formation, a frontage of roughly 15-20 m, so 6 m keeps "
"the enemy under the MIDDLE of the formation). The family's **70% exemption, flying / out-of-melee "
"requirements, fail-closed behaviour and logged pre-cast re-check are all kept** — the re-check now "
"re-reads the **centre** distance. **NO COUNTS MOVED:** 689 entries / 742 keys, `air_drop_on_infantry` "
"**12 entries / 19 keys**, 46 evaluators. Spreadsheet `docs/WH3_abilities_master_v10_2026-10-18.xlsx` "
"(+ `.ods`; v10 supersedes v9; **v1-v9 byte-unchanged**); research in "
"`docs/WH3_round109_airdrop_centre.md`; harness 109: **4098 checks / 0 failures** (run twice, "
"byte-identical), red control **36 failures, all accounted for**; installed pack md5 "
"`947049dcf021ae101d1d509208c85e71`.\n")
s = s.replace(ANCHOR, ANCHOR + UPDATE, 1)

with open(P, "wb") as f:
    f.write(s.encode("utf-8"))
print("tracker rows updated:", n, "| new size:", len(s))
print("stale 1 m phrase left:", s.count("inside the family's overlap bound - 1 m"))
print("new phrase rows:", s.count("FOURTH.AIR_DROP_CENTER_M = 6"))
