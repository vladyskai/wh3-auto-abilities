#!/usr/bin/env python3
"""Round 121 - tracker edits (the authoritative inventory).

Three edits, each asserted, nothing else touched:

1. THE 17 ARMY-BAR ROWS re-statused. Every row whose key is in the army_spec
   junction (the user's ruling: an army-bar ability has no button on the battle
   ability wheel, so perform_special_ability can never be called for it) now
   reads `excluded (not in wheel: army-bar ability ...)`. The 4 that were
   implemented and whose keys LEFT the mod in this round say so in the status.
2. A new legend line, a new Update bullet and a new §10.9 section recording the
   ruling verbatim, the 17 rows, the 4 removed keys (entry vs key), the
   arithmetic and the three permanent gates.
3. Nothing else: the row count stays 1,800; the other 1,783 rows are untouched.
"""
import re

TR = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
ARMY_SPEC = r"C:\Users\vlady\AppData\Local\Temp\wh3\army_spec.tsv"

ARMY = set()
with open(ARMY_SPEC, encoding="utf-8", errors="replace") as f:
    f.readline()
    for line in f:
        if line.startswith("#"):
            continue
        c = line.rstrip("\n").split("\t")
        if c and c[0].strip():
            ARMY.add(c[0].strip())

EXPECTED17 = {
    "wh2_dlc15_character_abilities_wardens_cage",
    "wh3_dlc20_cataclysm_bound_ashes_and_dust",
    "wh3_dlc20_cataclysm_bound_dance_of_despair",
    "wh3_dlc20_cataclysm_bound_gehennas_golden_globe",
    "wh3_dlc20_cataclysm_bound_magma_storm",
    "wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment",
    "wh3_dlc20_cataclysm_bound_storm_of_renewal",
    "wh3_dlc20_cataclysm_bound_time_amok",
    "wh3_dlc27_cataclysm_bound_ashes_and_dust",
    "wh3_dlc27_cataclysm_bound_dance_of_despair",
    "wh3_dlc27_cataclysm_bound_gehennas_golden_globe",
    "wh3_dlc27_cataclysm_bound_magma_storm",
    "wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment",
    "wh3_dlc27_cataclysm_bound_storm_of_renewal",
    "wh3_dlc27_cataclysm_bound_time_amok",
    "wh3_dlc29_army_abilities_pestilential_bombardment",
    "wh3_main_cataclysm_khorne_greater_gate_of_khorne",
}
assert EXPECTED17 <= ARMY, sorted(EXPECTED17 - ARMY)

REMOVED_KEYS = {
    "wh2_dlc15_character_abilities_wardens_cage",
    "wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment",
    "wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment",
    "wh3_main_cataclysm_khorne_greater_gate_of_khorne",
}

STATUS_OUT = ("excluded (not in wheel: army-bar ability - army_spec junction - no battle-wheel "
              "button, so it can never be cast; user ruling round 121)")
STATUS_REMOVED = ("excluded (not in wheel: army-bar ability - army_spec junction - no battle-wheel "
                  "button, so it can never be cast - removed from mod per user ruling round 121)")

NOTE_GONE = (" · **round 121 (2026-10-20):** REMOVED from the mod's ABILITIES table - it is an "
             "army-bar ability (army_spec junction) with no button on the battle ability wheel, so "
             "perform_special_ability could never be called for it (user ruling round 121).")
NOTE_KEPT = (" · **round 121 (2026-10-20):** EXCLUDED - army-bar ability (army_spec junction) with no "
             "button on the battle ability wheel, so it can never be cast (user ruling round 121).")

lines = open(TR, encoding="utf-8").read().split("\n")
out = []
hit_status, hit_note = [], []
for ln in lines:
    if ln.startswith("|"):
        cells = [x.strip() for x in ln.strip().strip("|").split("|")]
        m = re.search(r"`([^`]+)`", cells[0]) if cells else None
        if m and m.group(1) in EXPECTED17 and len(cells) >= 5:
            key = m.group(1)
            old = cells[1]
            assert old.startswith("`") and old.endswith("`"), old
            new_status = STATUS_REMOVED if key in REMOVED_KEYS else STATUS_OUT
            cells[1] = "`" + new_status + "`"
            note = NOTE_GONE if key in REMOVED_KEYS else NOTE_KEPT
            if key in REMOVED_KEYS and "round 121" not in cells[4]:
                cells[4] = cells[4] + note
                hit_note.append(key)
            elif key not in REMOVED_KEYS:
                cells[4] = cells[4] + note
                hit_note.append(key)
            hit_status.append((key, old.strip("`"), new_status))
            ln = "| " + " | ".join(cells) + " |"
    out.append(ln)

assert len(hit_status) == 17, ("rows re-statused", len(hit_status), [h[0] for h in hit_status])
src = "\n".join(out)

# ---------------------------------------------------------------- 1b. the legend
LEGEND_ANCHOR = ("- `excluded (not in wheel: boss-only unit)` — the ability's **ONLY grant path is a "
                 "`_boss` unit**")
assert LEGEND_ANCHOR in src
LEGEND_NEW = (
    "- `excluded (not in wheel: army-bar ability - army_spec junction - no battle-wheel button, so it "
    "can never be cast; user ruling round 121)` — the ability is an **ARMY-BAR** one (a key in the "
    "`army_spec` junction). It has **no button on the battle ability wheel**, so `perform_special_ability` "
    "can never be called for it: it can never fire, and it cannot be IN-WHEEL. **ALL 17 remaining "
    "army_spec rows** carry this status; the **4 that were implemented** were **REMOVED from the mod's "
    "`ABILITIES` table** in round 121 (see **§10.9**).\n")
src = src.replace(LEGEND_ANCHOR, LEGEND_NEW + LEGEND_ANCHOR, 1)

# ---------------------------------------------------------------- 2a. the update bullet
UPDATE_ANCHOR = "**SIGN-OFF DECISIONS (2026-10-18) - TWO THINGS CLOSED, ONE REVIEW FILED, NOTHING PENDING.**"
assert UPDATE_ANCHOR in src
UPDATE = (
    "**Update 2026-10-20 (harness 120 - ALL ARMY-BAR ABILITIES EXCLUDED; 4 KEYS OUT OF THE MOD).** "
    "The user's ruling, verbatim: *\"The triggers will not work if the ability is not in the ability "
    "wheel on the lower left corner of the battle screen, meaning 'you'd lose working triggers' makes "
    "no sense. Therefore, ALL ARMY ABILITIES PLEASE EXCLUDE.\"* It is right: an army-bar ability (a key "
    "in the `army_spec` junction) has **no button on the battle ability wheel**, so "
    "`perform_special_ability` can never be called for it - an ABILITIES entry carrying one can never "
    "fire. **THE 17 ROWS** that still read IN-WHEEL on an army_spec key are now "
    "`excluded (not in wheel: army-bar ability ...)`: Warden's Cage, Greater Gate of Khorne's cataclysm "
    "key, Merciw's Monstrous Regiment (2 rows), Bubonic Broadside, and the 12 `cataclysm_bound` twins "
    "(Ashes & Dust, Dance of Despair, Gehenna's Golden Globe, Magma Storm, Storm of Renewal, Time Amok - "
    "2 each). **THE MOD:** the intersection of the mod's 742 keys with the 286-key army_spec set found "
    "**3 entries / 4 keys**, not the 4 the round-120 report counted as 'implemented': **2 whole entries "
    "removed** (`merciws_monstrous_regiment`, 2 keys; `wardens_cage`, 1 key) and **1 key removed from a "
    "kept entry** (`greater_gate_of_khorne` keeps `wh3_main_character_abilities_greater_gate_of_khorne`), "
    "plus the 4 dead per-key data rows (charge pool / wind-up / enemy-ground set). ABILITIES **689 "
    "entries / 742 keys -> 687 / 738**; **0 army_spec keys remain anywhere in either file**. "
    "**ARITHMETIC:** 1,140 - 17 = **1,123 IN-WHEEL**; 660 + 17 = **677 EXCLUDED**; 1,123 + 677 = 1,800. "
    "Implemented **742 - 4 = 738** rows = 738 keys; not implemented among the included 398 - 13 = 385; "
    "738 + 385 = 1,123. **GATES (permanent):** `tools/audit_wheel_status.py` G3 FAILS on any IN-WHEEL row "
    "carrying an army_spec key - the old 17-row BASELINE and every exceptions list are deleted; "
    "`tools/build_and_install.py` **refuses to build** if any ABILITIES key is in the army_spec set; "
    "`tools/verify_ability_database.py` asserts the same. **HARNESS 120: 4,767 checks / 0 failures** "
    "(run twice, byte-identical; light 1,586 / 0). Spreadsheet `docs/WH3_abilities_master_v20_2026-10-20.xlsx` "
    "(v20 supersedes v19; v1-v19 byte-unchanged). Full record: **§10.9**.\n")
src = src.replace(UPDATE_ANCHOR, UPDATE + "\n" + UPDATE_ANCHOR, 1)

# ---------------------------------------------------------------- 2b. §10.9 at the end
SECTION = """
### 10.9 The army-bar exclusion - all 17 remaining army_spec rows out of the wheel, 4 keys out of the mod (round 121, 2026-10-20)

**The ruling, verbatim:**

> "The triggers will not work if the ability is not in the ability wheel on the lower left corner of the
> battle screen, meaning 'you'd lose working triggers' makes no sense. Therefore, ALL ARMY ABILITIES
> PLEASE EXCLUDE."

**Why it is right.** An army-bar ability is a row in `army_special_abilities_tables` - a key in the
`army_spec` junction. It has no button on the battle ability wheel, so the mod's only cast call,
`perform_special_ability`, can never be issued for it. An entry carrying such a key is dead weight: it
cannot fire, it cannot be "working", and it cannot be IN-WHEEL. Round 120 listed these rows and moved
none of them on the mistaken ground that moving them would cost working triggers. There was nothing
working to lose.

**The 17 rows / 17 keys, all now `excluded (not in wheel: army-bar ability ...)`:**

| # | Ability | army_spec key | Was |
|---|---|---|---|
| 1 | Warden's Cage | `wh2_dlc15_character_abilities_wardens_cage` | IN-WHEEL, IMPLEMENTED |
| 2 | Greater Gate of Khorne (cataclysm twin) | `wh3_main_cataclysm_khorne_greater_gate_of_khorne` | IN-WHEEL, IMPLEMENTED |
| 3-4 | Merciw's Monstrous Regiment (2 rows) | `wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment`, `wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment` | IN-WHEEL, IMPLEMENTED |
| 5 | Bubonic Broadside | `wh3_dlc29_army_abilities_pestilential_bombardment` | IN-WHEEL, NOT IMPLEMENTED |
| 6-7 | Ashes & Dust x2 | `wh3_dlc20_/wh3_dlc27_cataclysm_bound_ashes_and_dust` | IN-WHEEL |
| 8-9 | Dance of Despair x2 | `wh3_dlc20_/wh3_dlc27_cataclysm_bound_dance_of_despair` | IN-WHEEL |
| 10-11 | Gehenna's Golden Globe x2 | `wh3_dlc20_/wh3_dlc27_cataclysm_bound_gehennas_golden_globe` | IN-WHEEL |
| 12-13 | Magma Storm x2 | `wh3_dlc20_/wh3_dlc27_cataclysm_bound_magma_storm` | IN-WHEEL |
| 14-15 | Storm of Renewal x2 | `wh3_dlc20_/wh3_dlc27_cataclysm_bound_storm_of_renewal` | IN-WHEEL |
| 16-17 | Time Amok x2 | `wh3_dlc20_/wh3_dlc27_cataclysm_bound_time_amok` | IN-WHEEL |

**What left the mod - 3 entries / 4 keys (found by intersecting the mod's key set with the army_spec set,
never from a report):**

| Shape | Entry | Keys removed | Entry survives? |
|---|---|---|---|
| WHOLE ENTRY | `merciws_monstrous_regiment` (Merciw's Monstrous Regiment, `ally_infinite_buff`) | 2 - both army-bar | no |
| WHOLE ENTRY | `wardens_cage` (Warden's Cage, `enemy_engaged_or_shot`) | 1 | no |
| KEY ONLY | `greater_gate_of_khorne` (`enemy_ground_melee`) | 1 - the cataclysm twin | **yes** - keeps `wh3_main_character_abilities_greater_gate_of_khorne` |

The 4 dead per-key data rows went with them (the charge pool `= 120`, the three `wind_up_s` rows) plus the
cataclysm key's `enemy_ground_keys` flag: **0 army_spec keys remain anywhere in the shipped source or the
annotated copy** (grep count 0 for all four). The `ally_infinite_buff` **evaluator and its tip line stay**
- they are generic machinery, now unused - so the evaluator count stays **46**.

**The arithmetic.** 1,140 - 17 = **1,123 IN-WHEEL**; 660 + 17 = **677 EXCLUDED**; 1,123 + 677 = **1,800**.
Implemented **742 - 4 = 738** rows = 738 keys; not implemented among the included 398 - 13 = 385;
738 + 385 = 1,123. Exclusions by family: 418 spell + **223 army-bar** (206 + 17) + 16 cataclysm + 1 quest +
15 boss + 4 illusion = 677. The ABILITIES table: **689 entries / 742 keys -> 687 / 738**.

**The three permanent gates (so it cannot recur).**

1. `tools/audit_wheel_status.py` - **G3 fails on ANY row marked IN-WHEEL that carries an army_spec key.**
   The old 17-row `BASELINE` and every exceptions list were **deleted**: a violation can no longer be
   "documented" into passing. Proven both ways: on v19 it reports 17 rows and exits 1; on v20 it exits 0.
2. `tools/build_and_install.py` - an assertion **before any stale pack is deleted or any RPFM command is
   sent**: `BUILD REFUSED (round 121 army-bar gate): N ABILITIES key(s) are in the army_spec junction ...
   Offending keys: [...]`. Proven both ways: the pre-121 snapshot is refused with the 4 keys, the shipped
   source passes with 738 keys / 0 hits.
3. `tools/verify_ability_database.py` - assertion **A0** applies the same test to the regenerated database,
   so a database build cannot bless a mod table that carries an army-bar key.

**Proof - harness 120.** FULL suite **4,767 checks / 0 failures**, run twice byte-identical; LIGHT
(`H118_LIGHT=1`) 1,586 / 0. What changed in the harness: every live count pin rebased (689 -> 687,
742 -> 738), the `merciws_monstrous_regiment` worlds MC1/MC2 and their `K.merc` constant removed (the entry
they exercised no longer exists), the `ally_infinite_buff` family count taken to 0, `enemy_engaged_or_shot`
86 -> 85, `range_real` 205 -> 204, the charge-gate key count 162 -> 161, the wind-up key count 173 -> 170
(3 rows: both Merciw keys + the cataclysm Gate key), and the eleven suite-boundary running counts -10 (the
two removed worlds' ten checks no longer run). No other world changed.

**Files.** Mod: `mod_source/script/battle/mod/zz_test_deadly_onslaught.lua` (+ the annotated copy
`docs/WH3_auto_ability_annotated.lua`) - both edited identically, both syntax-checked. Workbook:
`docs/WH3_abilities_master_v20_2026-10-20.xlsx` (v20 supersedes v19; v1-v19 byte-unchanged). Gates:
`tools/audit_wheel_status.py`, `tools/build_and_install.py`, `tools/verify_ability_database.py`.
"""
src = src.rstrip("\n") + "\n" + SECTION

open(TR, "w", encoding="utf-8", newline="\n").write(src)
print("re-statused rows:", len(hit_status))
for k, old, new in hit_status:
    print("  %-62s %s -> %s" % (k, old, new))
print("notes appended:", len(hit_note))
print("bytes:", len(src))
