"""Round 113 tracker update - THE PATH TEST, THE DERIVED FRONTAGE, THE
SINGLE-ENTITY EXCLUSION.

1. All 19 air-drop rows: the round-112 block is replaced by the round-113 text
   (the path test, the frontage credit and its derivation, the one-model
   exclusion, the new log fields and the re-running re-check).
2. The trigger-family glossary row for air_drop_on_infantry is brought to round
   113.
3. A new dated Update paragraph is inserted after the harness-112 update.

Every anchor is asserted, so a stale tracker cannot silently pass.
"""
import io

P = r"C:/Users/vlady/Desktop/WH3_mod/docs/WH3_ability_tracker.md"
s = io.open(P, encoding="utf-8", newline="").read()
assert "\r" not in s
before = s

START = "((**round 112: THE ENEMY-SIDE DIAL"
END = "the cast is self-centred (on the owner)."
assert s.count(START) == 19, s.count(START)

NEW_ROW = (
    "((**round 113: THE PATH TEST, THE DERIVED FRONTAGE AND THE SINGLE-ENTITY EXCLUSION** - the "
    "user's sixth air-drop report, with a screenshot: *a Sky-junk hovering BESIDE a 20-model zombie "
    "block never fired while the block walked past - the enemy's CENTRE stayed 10+ m away even "
    "though its models swept under the caster*; and separately one fired at a **LORD**, which must "
    "be excluded. **WHY A POINT COULD NOT DESCRIBE A BLOCK:** `battle_unit:position()` is the "
    "**CENTRE** of the main squad (`battle_unit.lua:118`), so a 20-model formation - ten models "
    "wide in two ranks, about **10 m** of frontage - can keep its centre 10 m away while one of its "
    "**models** walks underneath the flyer. The round-110/112 test compared the caster's projected "
    "point with the enemy's projected **CENTRE**, so that pass was invisible. **THE TEST IS NOW THE "
    "ENEMY'S PATH** (the user's ruling, verbatim: *\"Let's implement the the path test with a "
    "derived frontage that you suggest.\"*): `segment = enemy_current -> enemy_projected` (the "
    "enemy's own two dials, unchanged); `perp` = the **SHORTEST HORIZONTAL DISTANCE from that "
    "segment to the CASTER'S projected point** (point-to-segment on x/z, the parameter **clamped to "
    "0..1** so a path that ENDS short is judged on its end point, never on the infinite line); "
    "**FIRE WHEN `perp <= FOURTH.AIR_DROP_CENTER_M + FOURTH.ad_frontage(enemy)`**. **THE FRONTAGE "
    "CREDIT IS DERIVED, NOT GUESSED:** (a) `ordered_width()`/2 - *\"the width of the position to "
    "which the unit has been ordered in metres\"* - when that read answers sanely (source "
    "`ordered`); (b) otherwise `ceil(models / 2) * radius` under ONE documented formation "
    "assumption, **two ranks deep** (source `models`); (c) **clamped to `AIR_DROP_FRONTAGE_MIN_M` "
    ".. `_MAX_M` = 1 .. 12 m HALF-width** (source `clamped`); (d) a **one-model unit gets 0** "
    "(source `single`) - a point has no width and the 6 m base already covers its footprint; (e) "
    "**unreadable -> 0** (source `unreadable`, FAIL CLOSED) and the plain 6 m point distance "
    "decides. **THE RADIUS IS A DOCUMENTED CONSTANT, `AIR_DROP_MODEL_RADIUS_M = 0.6 m`:** the "
    "battle script has no radius / footprint / bounding-box / size read and **no db access**, so "
    "`land_units.man_entity -> battle_entities.radius` cannot be joined at battle time; **0.6 m** "
    "is the **MODAL** radius over the 942 infantry `land_units` rows (168 rows; median **0.7 m**, "
    "zombies 0.5 m, the Terradon rider 0.6 m) and is **conservative** against the median. Two "
    "ranks is the **WIDE** end of the game's own formations (`rank_depth` runs 1..8, median 3), and "
    "a wider credit is the safe direction for a drop whose failure mode is missing a block that "
    "sweeps underneath. **THE SINGLE-ENTITY EXCLUSION** (the user's other ruling, verbatim: *\"why "
    "comparison is 1 or less? It cannot be less, then the unit does not exist. So comparion should "
    "be equal to 1.\"* - and the user is RIGHT): a candidate whose "
    "`battle_unit:initial_number_of_men()` - *\"the number of soldiers the unit started the battle "
    "with\"* - is **EXACTLY 1** is skipped, and the skip is logged **once per episode** as "
    "**`single entity (1 model)`**. **EXACT equality**, never *1 or less* (zero models cannot "
    "exist); **INITIAL**, not current (a 20-model block ground down to one survivor is still a "
    "**block**, not a lord). **THE 1,409-KEY COMMANDER SET IS DELIBERATELY NOT USED HERE** - it "
    "stays in service for the other evaluators, but every **infantry-class** lord and hero in the "
    "game data is a **one-model** unit (`main_units`: 0 lord and 6 hero rows with a `land_units` "
    "class of `inf_mel` / `inf_mis` / `inf_spr`, **all `num_men = 1`**), so the model count already "
    "covers that case without a 1,409-key membership test on every poll; the 146 multi-model "
    "character rows (chariot crews of 2-8 men) are **every one** `land_units` class `com` - not "
    "infantry - so the infantry filter has already removed them. An **unreadable** "
    "`initial_number_of_men()` **skips** the candidate (fail-closed) and says so. **THE LOG, PER "
    "DECISION (round 113):** the decision line now prints the **SEGMENT** "
    "(`segment=(110.0, 201.0)->(109.0, 201.0)`), the **PERP** (`perp=9.02m` - the number that "
    "decides), the **FRONTAGE WITH ITS SOURCE** (`frontage=6.00m (models, men=20 x 2 ranks (10 per "
    "rank) x 0.60m radius)`), the **THRESHOLD** (`threshold=12.00m (bound=6m + frontage=6.00m)`) "
    "and the old point separation as the diagnostic it now is (`centre=9.0m (the PROJECTED POINT "
    "separation - no longer the test)`); every air-drop line keeps the unit's **UI id** and **all "
    "four dials**, the `watch:` line prints `perp` against the threshold **and** the point "
    "separation, the exact-metres-below-15 m rule is unchanged, and the skip line is "
    "`SKIPPED: single entity (1 model)`. **UNCHANGED:** the four dials (`AIR_DROP_DELAY_S` **1.5 s** "
    "x `AIR_DROP_ENEMY_LEAD` **0.3**; `AIR_DROP_CASTER_DELAY_S` **1.5 s** x "
    "`AIR_DROP_CASTER_LEAD` **0.5**), the **6 m** base bound, `FOURTH.AIR_DROP_INHERIT = false`, "
    "`air_only` / `no_melee` per row, the self-centred cast on the OWNER, every fail-closed read and "
    "the pre-cast re-check - which now **RE-RUNS THE SEGMENT TEST** on fresh reads (one `ad_lead` "
    "call gives the current AND the projected point) and SKIPS the cast rather than spending it "
    "when the path has drifted. **TUNING, ONE CHANGE PER TEST:** a block whose models sweep under "
    "the caster while the centre stays out -> raise `AIR_DROP_MODEL_RADIUS_M` **0.6 -> 0.7 -> 0.8** "
    "or the ceiling **12 -> 15**; a drop that leaves while the enemy is visibly not underneath -> "
    "lower the ceiling **12 -> 8 -> 6** (a 0 ceiling restores the pure 6 m point test); a character "
    "that still fires -> **report it** (it is not infantry-class, so the infantry filter failed); a "
    "path judged in the wrong place -> tune the **leads** (`AIR_DROP_ENEMY_LEAD` / "
    "`AIR_DROP_DELAY_S`), which define the segment's end. FINALLY: the caster is airborne / out of "
    "melee where its row requires it; the cast is self-centred (on the owner)."
)

out = []
at = 0
while True:
    i = s.find(START, at)
    if i < 0:
        out.append(s[at:])
        break
    j = s.find(END, i)
    assert j > 0
    out.append(s[at:i])
    out.append(NEW_ROW)
    at = j + len(END)
s = "".join(out)
assert s.count("((**round 113: THE PATH TEST") == 19
assert s.count(START) == 0

# ---------------------------------------------------------------- glossary row
G1_OLD = "| `air_drop_on_infantry` | **rounds 110-112** - an enemy INFANTRY unit"
G1_NEW = "| `air_drop_on_infantry` | **rounds 110-113** - an enemy INFANTRY unit"
assert s.count(G1_OLD) == 1
s = s.replace(G1_OLD, G1_NEW)

G2_OLD = ("the drop fires when the **PROJECTED** horizontal CENTRE-TO-CENTRE separation "
          "(`battle_unit:position()`, **X/Z only** because `battle_vector:get_y()` is HEIGHT; "
          "`battle_vector:distance_xz()`) must be inside **`FOURTH.AIR_DROP_CENTER_M = 6`**.")
G2_NEW = ("**ROUND 113 REPLACES THE POINT TEST WITH A PATH TEST:** `segment = enemy_current -> "
          "enemy_projected` and the drop fires when the **SHORTEST HORIZONTAL DISTANCE FROM THAT "
          "SEGMENT TO THE CASTER'S PROJECTED POINT** (`perp`, point-to-segment on **X/Z only** "
          "because `battle_vector:get_y()` is HEIGHT, parameter clamped 0..1) is inside "
          "**`FOURTH.AIR_DROP_CENTER_M = 6 m` PLUS a DERIVED HALF-FRONTAGE** - `ordered_width()/2` "
          "when readable, otherwise `ceil(models/2) * AIR_DROP_MODEL_RADIUS_M` (**0.6 m**, the "
          "modal `battle_entities.radius` over the 942 infantry rows) under a documented **two-rank** "
          "assumption, clamped to **1..12 m**, **0 for a one-model unit** and **0 (fail-closed)** "
          "when unreadable. A candidate whose **`initial_number_of_men() == 1`** is skipped - the "
          "lord/hero case - **once per episode** as `single entity (1 model)`; the 1,409-key "
          "commander set is deliberately **not** consulted here because every infantry-class "
          "character in the data is one model.")
assert s.count(G2_OLD) == 1, "the glossary's centre-test sentence moved"
s = s.replace(G2_OLD, G2_NEW)

G3_OLD = ("and the logged pre-cast re-check - which now **RE-PROJECTS both bodies** from fresh "
          "reads and skips the cast rather than spending it.")
G3_NEW = ("and the logged pre-cast re-check - which now **RE-RUNS THE SEGMENT TEST** from fresh "
          "reads (the same `ad_lead` read gives the current AND the projected point) and skips the "
          "cast rather than spending it.")
assert s.count(G3_OLD) == 1
s = s.replace(G3_OLD, G3_NEW)

# ------------------------------------------------------- the dated Update entry
ANCHOR = ("installed pack md5 `237702987893b8837d2dbb5df05d566b`; `zz_probe_dist.pack` left "
          "installed (md5 `d4e67cfb8bc562c7d6f0ff742909c13d`, untouched).\n")
assert s.count(ANCHOR) == 1, "the harness-112 update tail moved"

UPDATE = (
    "**Update 2026-10-25 (harness 113 - THE PATH TEST, THE DERIVED FRONTAGE AND THE SINGLE-ENTITY "
    "EXCLUSION).** Two field findings, one rule change each, both shipping. **(A) THE SIDE PASS.** "
    "The user's sixth report, with a screenshot: a Sky-junk hovering **beside** a 20-model zombie "
    "block never fired while the block walked past - the enemy's **CENTRE** stayed **10+ m** away "
    "even though its **models** swept under the caster. The arithmetic: `battle_unit:position()` is "
    "the **centre** of the main squad, and a 20-model block in two ranks is about **10 m** wide, so "
    "its centre can sit at 10 m while its near edge is **4 m** from the drop point. The round-110/112 "
    "test compared the caster's projected **point** with the enemy's projected **centre**, so the "
    "pass never came inside 6 m and nothing fired. **THE FIX - THE PATH TEST:** `segment = "
    "enemy_current -> enemy_projected`, `perp` = the shortest horizontal distance from that segment "
    "to the caster's projected point (point-to-segment, parameter clamped 0..1), fire when `perp <= "
    "AIR_DROP_CENTER_M + ad_frontage(enemy)`. **THE FRONTAGE IS DERIVED:** `ordered_width()/2` when "
    "that read is sane; otherwise `ceil(models / 2) * AIR_DROP_MODEL_RADIUS_M` under a documented "
    "**two-rank** assumption; clamped to **1..12 m** half-width; **0** for a one-model unit; **0, "
    "fail-closed**, when unreadable. The radius is a **constant, 0.6 m** - the battle script has no "
    "radius read and no db access, so `land_units.man_entity -> battle_entities.radius` cannot be "
    "joined at battle time - and 0.6 m is the **modal** value over the 942 infantry `land_units` "
    "rows (median 0.7 m). In the harness the reported geometry (centre **10.05 m** away, perp "
    "**9.02 m**, 20 models -> credit **6.00 m** -> threshold **12.00 m**) now **FIRES**, while the "
    "same geometry with one alive model stays silent - the credit is what decides. **(B) THE LORD.** "
    "One drop fired at a **LORD**. The user's ruling: *\"why comparison is 1 or less? It cannot be "
    "less, then the unit does not exist. So comparion should be equal to 1.\"* - and they are right "
    "on both counts: the guard is **`initial_number_of_men() == 1`** (exact equality; zero models "
    "cannot exist) and it logs **once per episode** as `single entity (1 model)`. **Initial**, not "
    "current, so a **depleted** 20-model block is still judged as a block. **The 1,409-key commander "
    "set is NOT used here**: every **infantry-class** lord and hero in the data is a one-model unit "
    "(0 lord and 6 hero rows with a `land_units` class of `inf_mel` / `inf_mis` / `inf_spr`, all "
    "`num_men = 1`), so the model count covers the case; the 146 multi-model character rows "
    "(chariot crews) are all class `com`, not infantry, so the infantry filter has removed them "
    "already. **(C) WHAT IS UNCHANGED:** the four dials (`AIR_DROP_DELAY_S` **1.5 s** x "
    "`AIR_DROP_ENEMY_LEAD` **0.3**; `AIR_DROP_CASTER_DELAY_S` **1.5 s** x `AIR_DROP_CASTER_LEAD` "
    "**0.5**), the **6 m** base bound, `AIR_DROP_INHERIT = false`, `air_only` / `no_melee`, the "
    "self-centred cast, every fail-closed read, and the pre-cast re-check - which **re-runs the "
    "segment test** from fresh reads. Counts are identical (689 entries / 742 keys, "
    "`air_drop_on_infantry` 12 / 19, 46 evaluators). **THE DECISION LOG** now carries `segment=...`, "
    "`perp=...`, `frontage=... (source, arithmetic)` and `threshold=... (bound=6m + frontage=...)` "
    "on the decision line, the same pair on the `watch:` line, the fresh pair on the re-check line, "
    "and `single entity (1 model)` on the skip. **HARNESS 113: 4610 checks / 0 failures** (run "
    "twice, byte-identical); **red control** against the round-112 build: **55 failures, all in the "
    "new section** (worlds A1/A2/A3 the path and the credit, B the one-model lord, C a 15 m side "
    "pass, D1/D2/D3 `ordered` vs `models` vs `clamped`, E the fail-closed fallback, F the drift "
    "re-check, G the depleted block, plus the section-0 pins in BOTH the live and the annotated "
    "copy). Installed pack md5 `004a1293c35f29a2b863fd399d733cf6` (five files, all byte-identical); "
    "`zz_probe_dist.pack` left installed (md5 `d4e67cfb8bc562c7d6f0ff742909c13d`, untouched).\n"
)
s = s.replace(ANCHOR, ANCHOR + UPDATE)

assert s != before
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("tracker updated:", len(before), "->", len(s))
print("round-113 rows:", s.count("((**round 113: THE PATH TEST"))
print("harness-112 rows left:", s.count("((**round 112"))
