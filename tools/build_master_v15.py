#!/usr/bin/env python3
"""Build WH3_abilities_master_v15_2026-10-18.xlsx from v14 (v1-v14 stay byte-unchanged).

* all 19 air-drop rows: the rule text is REPLACED with the round-114 simple rule
* Definitions: sections 8-11 (the four dials, the frontage credit) are marked
  RETIRED with the reason, and section 12 documents the four new constants
* Numbers: the version line moves to v15 (no count changes)
* Changelog: a v15 row
"""
import openpyxl
from openpyxl.styles import Alignment, Font

DOCS = r"C:\Users\vlady\Desktop\WH3_mod\docs"
SRC = DOCS + r"\WH3_abilities_master_v14_2026-10-18.xlsx"
OUT = DOCS + r"\WH3_abilities_master_v15_2026-10-18.xlsx"

AIR = {
    "death_from_above": (True, True),
    "drop_rocks": (True, True),
    "drop_sphere_of_tepok": (False, True),
    "fire_bombs": (True, False),
    "gyrobomber_bomb": (True, False),
    "gyrocopter_bomb_anti_large": (True, False),
    "sky_junk_bomb": (True, False),
    "skyhammer_bomb": (True, False),
    "wake_of_fire": (True, True),
    "searing_torrent": (False, True),
    "nan_gau_grenades": (True, False),
    "undeath_from_above": (True, True),
}

MARKER = {
    "Death from Above": "death_from_above",
    "Drop Rocks": "drop_rocks",
    "Drop Rocks of Chotec": "drop_rocks",
    "Drop Rocks of Sundering": "drop_rocks",
    "Drop Sphere of Tepok": "drop_sphere_of_tepok",
    "Drop Sphere of Tepok Upgraded": "drop_sphere_of_tepok",
    "Fire Bombs": "fire_bombs",
    "Gyrobomber Bomb": "gyrobomber_bomb",
    "Gyrocopter Bomb": "gyrobomber_bomb",
    "Gyrocopter Bomb (Trollhammer)": "gyrocopter_bomb_anti_large",
    "Sky-Junk Bomb": "sky_junk_bomb",
    "Skyhammer Bomb": "skyhammer_bomb",
    "Skyhammer Fire Bomb": "skyhammer_bomb",
    "Wake of Fire": "wake_of_fire",
    "Searing Torrent": "searing_torrent",
    "Nan-Gau Grenades": "nan_gau_grenades",
    "Undeath from Above": "undeath_from_above",
}

RULE = (
    "air_drop_on_infantry (round 114 - THE SIMPLE EDGE-GAP RULE; the earlier rounds 107-113 "
    "built and tuned a projection / frontage / path design and were REPLACED by this): the row has NO "
    "target flags at all (target_friends / target_enemies / target_ground / target_self all false), "
    "effect_range 0 and target_intercept_range 10, so the engine drops where the CASTER is and the only "
    "decision is WHEN. THE USER'S RULE, verbatim: '1. I want the trigger to be checked much more "
    "frequently when armed and less than 30 meters from a valid enemy unit. 2. Valid units are those who "
    "have more than 10 entities. 3. I trigger the moment distance between edges is below 0.1 meters. "
    "That's it.' and '1. Remove the \"and it is infantry\". No need for it now. 2. Current count 3. Let's "
    "try with 0.2 s for now.' THE DECISION IS ONE COMPARISON: fire when "
    "battle_unit:unit_distance(caster, enemy) - the engine's EDGE-TO-EDGE distance in metres "
    "(battle_unit.lua:160) - is BELOW FOURTH.AIR_DROP_EDGE_M = 0.10 m. THE CANDIDATE SET is, and only is: "
    "an enemy that is ALIVE (number_of_men_alive() > 0) with number_of_men_alive() > "
    "FOURTH.AIR_DROP_MIN_MEN = 10 entities and a READABLE unit_distance; the NEAREST such enemy by that "
    "distance is chosen. THERE IS NO INFANTRY TEST in this evaluator (removed by the user's ruling; every "
    "other evaluator keeps its own class filters), NO single-entity exclusion (a one-model Lord / Hero "
    "fails the > 10 test by itself - the case that guard was protecting), NO centre-vs-edge distance read, "
    "NO projection / delay / lead / momentum dial, NO derived frontage and NO path segment. THE FOUR "
    "CONSTANTS: AIR_DROP_EDGE_M = 0.1 m (fire below this), AIR_DROP_MIN_MEN = 10 (more models than this), "
    "AIR_DROP_NEAR_M = 30 (the fast pass runs while a valid enemy is this close), AIR_DROP_FAST_S = 0.2 s "
    "(the fast pass interval). Caster-side usage restrictions stay exactly as the row declares them: "
    "air_only = {air_only} (is_currently_flying() must be exactly true, an unreadable read holds); "
    "no_melee = {no_melee} (is_in_melee() must not be true, an unreadable read holds). The cast is "
    "SELF-CENTRED: perform_special_ability(key, OWNER). THE PRE-CAST RE-CHECK re-validates the chosen "
    "enemy on FRESH handles immediately before the call (still alive, still more than 10 models) and "
    "RE-MEASURES the edge distance through the same primitive; a lapsed condition SKIPS the cast rather "
    "than spending it and writes '-> SKIPPED at re-check' with the fresh numbers. THE FAST PASS: a SECOND "
    "model timer (AIR_DROP_FAST_S = 0.2 s, its own bm:repeat_callback) runs the SAME evaluator through the "
    "SAME FOURTH.try_pair gate+cast path as the global poll, but only for units that are ALIVE, ARMED for "
    "an air-drop marker, and only while a VALID enemy is inside AIR_DROP_NEAR_M = 30 m; the global poll "
    "(POLL_MS = 250) and every other ability's cadence are UNCHANGED, and the existing guard, charge, "
    "in-flight and per-unit serialisation gates (stamped in poll ticks) make a second fast tick inside the "
    "same poll window unable to cast again. THE LOG, ON EVERY DECISION: '[<ui id>] <marker> nearest "
    "valid:'<enemy land_units key>' entities=<n> edge=<d.dd>m (need < 0.10m) -> NOT YET / FIRING', the "
    "re-check line with '-> SKIPPED at re-check' or '-> FIRING (re-checked)', and ONE 'fast poll: ON "
    "(nearest valid <d>m)' / 'fast poll: OFF' line per change (never per tick). WHY THE EDGE GAP: it is "
    "the number the user asked for, it needs no radius / footprint read (the API has none) and it is "
    "exactly the engine's own bounding-box gap, so nothing in the decision is an approximation. RETIRED "
    "WITH THE OLD RULE: AIR_DROP_CENTER_M (6 m), AIR_DROP_DELAY_S, AIR_DROP_ENEMY_LEAD, "
    "AIR_DROP_CASTER_DELAY_S, AIR_DROP_CASTER_LEAD, AIR_DROP_INHERIT, AIR_DROP_MODEL_RADIUS_M, "
    "AIR_DROP_RANKS, AIR_DROP_FRONTAGE_MIN_M / _MAX_M and the helpers ad_frontage, ad_seg_dist, ad_lead, "
    "ad_project, ad_dial_text, ad_centre_gap, ad_single_say, ad_single_clear, ad_pos, ad_sep, ad_vec_text, "
    "ad_velocity - nothing else in the mod used any of them."
)

FAMILY_NOTE = (
    "carrier family: active - unit-carried active ability | trigger rule: round 114 - THE SIMPLE EDGE-GAP "
    "RULE: the nearest ALIVE enemy with MORE THAN 10 models whose battle_unit:unit_distance (EDGE-TO-EDGE) "
    "is BELOW 0.10 m; no infantry filter, no single-entity test, no projection / lead / frontage / path; "
    "a separate 0.2 s fast pass re-runs the same evaluator while a valid enemy is inside 30 m; the global "
    "poll is untouched. air_only / no_melee as the row declares them; self-centred cast; pre-cast re-check "
    "re-measures the edge gap on fresh handles."
)

DEF_RETIRED = (
    "RETIRED IN ROUND 114 - DO NOT TUNE THIS. The air-drop rule was REPLACED by the user's own simple "
    "rule (section 12): ONE comparison of the engine's edge-to-edge battle_unit:unit_distance against "
    "FOURTH.AIR_DROP_EDGE_M = 0.10 m for the nearest enemy with more than 10 models. Everything in this "
    "section - and in sections 8, 9, 10 and 11 - was part of the earlier centre / projection / lead / "
    "frontage / path designs, was DELETE from the evaluator in round 114, and can no longer affect any "
    "decision. It is kept only so the history is honest and a field log from an older build still reads."
)

DEF12 = [
    ("12. THE AIR-DROP RULE IN FORCE (round 114) - ONE COMPARISON, AND A 0.2 s FAST PASS",),
    ("THE DECISION (exactly what the evaluator runs)",),
    ("candidate = number_of_men_alive() > 0 AND number_of_men_alive() > FOURTH.AIR_DROP_MIN_MEN (10); "
     "valid = that candidate's battle_unit:unit_distance(caster, enemy) is READABLE; chosen = the NEAREST "
     "valid candidate by that distance; FIRE = unit_distance(caster, chosen) < FOURTH.AIR_DROP_EDGE_M "
     "(0.10 m). Then the caster-side usage checks the row declares (air_only -> is_currently_flying() "
     "exactly true; no_melee -> is_in_melee() not true), the self-centred cast on the OWNER, and the "
     "pre-cast re-check (fresh handles, the same two reads, skip if it moved out).",),
    ("NOTHING ELSE DECIDES: no infantry test, no initial_number_of_men() test, no centre distance, no "
     "projection / delay / lead / momentum, no frontage credit, no path segment. unit_distance is "
     "EDGE-TO-EDGE (battle_unit.lua:160), so 0.10 m means the two bounding boxes are ten centimetres "
     "apart.",),
    ("THE FOUR CONSTANTS",),
    ("Constant | Ships as | What it does / how to tune it",),
    ("FOURTH.AIR_DROP_EDGE_M | 0.1 (m) | THE LINE. Fire when the nearest valid enemy's edge-to-edge gap "
     "is strictly below this. Lower it (0.1 -> 0.05) if a drop still leaves too early; raise it "
     "(0.1 -> 0.2 -> 0.3) if a model passes underneath and nothing fires. One value, every row.",
     ),
    ("FOURTH.AIR_DROP_MIN_MEN | 10 | A candidate needs MORE alive models than this. 10 excludes a "
     "10-model unit and includes 11. This is also what removes Lords and Heroes (a one-model unit fails "
     "it), so no class list is consulted. Raise it to 15/20 to ignore small remnants; set it to 0 to "
     "accept any living enemy (a one-model lord would then fire).",
     ),
    ("FOURTH.AIR_DROP_NEAR_M | 30 (m) | The FAST PASS runs only while a valid enemy is this close. It is "
     "a work-saving gate, never a cast condition: the poll still evaluates the family at its own cadence. "
     "Widen it if the fast pass turns on too late for a fast approach; it costs one candidate scan per "
     "armed unit per fast tick.",
     ),
    ("FOURTH.AIR_DROP_FAST_S | 0.2 (s) | The fast pass interval (200 ms; the registration is "
     "math.floor(AIR_DROP_FAST_S * 1000)). It does NOT touch the global poll (POLL_MS = 250 ms) or any "
     "other ability's cadence: a second model timer runs FOURTH.ad_fast_pass, which iterates only the 12 "
     "air-drop entries, only for armed units, and only when a valid enemy is inside AIR_DROP_NEAR_M.",
     ),
    ("TOTAL | 4 constants | One rule, four knobs, no per-row edit anywhere.",),
    ("THE TWO TIMERS, AND WHY TWO",),
    ("global poll | POLL_MS = 250 ms, bm:repeat_callback(poll, ...) | UNCHANGED. Every ability in the mod "
     "is evaluated here, exactly as before round 114.",
     ),
    ("air-drop fast pass | AIR_DROP_FAST_S = 0.2 s, its own bm:repeat_callback, pcall-wrapped like the "
     "poll | runs FOURTH.ad_pick (the SAME evaluator) and casts through FOURTH.try_pair (the SAME "
     "readiness + guard + charge + in-flight + per-unit-serialisation + cast sequence). Isolation: it "
     "iterates FOURTH.ad_fast_abilities (the 12 air-drop entries built at load), never ABILITIES; it does "
     "not touch tick_count, the re-list, the heartbeat, the identity watch or the active set. The gates "
     "are stamped in POLL ticks and written BEFORE the call, so a second fast tick inside the same poll "
     "window finds an elapsed 0 < GUARD_TICKS and cannot cast again (harness 114 world H: two consecutive "
     "fast ticks -> exactly one cast; five more -> still one).",
     ),
    ("THE LOG (per decision)",),
    ("[<ui id>] <marker> nearest valid:'<enemy key>' entities=<n> edge=<d.dd>m (need < 0.10m) -> NOT YET | "
     "the exact distance, the entity count, the enemy type and the caster's ui id, written whenever the "
     "decision or the number changes (an unchanged 5 Hz repeat is de-duplicated).",),
    ("... -> FIRING (the nearest of the valid enemies; ...) | the same four fields at the moment the edge "
     "gap is under the line; the cast then logs its ATTEMPT and the pre-cast line.",),
    ("... edge=<d.dd>m (need < 0.10m) -> SKIPPED at re-check (... over_min_men=... edge_ok=...) | the "
     "chosen enemy left the line between the decision and the call; the cast is NOT spent.",),
    ("[<ui id>] fast poll: ON (nearest valid <d>m) / [<ui id>] fast poll: OFF | ONE line per CHANGE of "
     "the 30 m gate, never per tick.",),
    ("RETIRED HERE, AND WHY",),
    ("sections 8-11 | AIR_DROP_CENTER_M, AIR_DROP_DELAY_S, AIR_DROP_ENEMY_LEAD, "
     "AIR_DROP_CASTER_DELAY_S, AIR_DROP_CASTER_LEAD, AIR_DROP_INHERIT, AIR_DROP_MODEL_RADIUS_M, "
     "AIR_DROP_RANKS, AIR_DROP_FRONTAGE_MIN_M / _MAX_M, and the helpers ad_frontage / ad_frontage_text / "
     "ad_seg_dist / ad_velocity / ad_lead / ad_project / ad_dial_text / ad_single_say / ad_single_clear / "
     "ad_centre_gap / ad_pos / ad_sep / ad_vec_text | RETIRED IN ROUND 114: they implemented a centre "
     "distance, a two-body projection with four lead dials, a derived frontage credit and a path test. "
     "The user replaced all of that with the single edge-gap comparison above, so the constants and the "
     "helpers were DELETED from the evaluator (nothing else in the mod used them). Their numbers can no "
     "longer change any decision - do not tune them.",
     ),
    ("TUNING GUIDE (round 114) - ONE CHANGE PER FIELD TEST",),
    ("Symptom | What to change | Order to try",),
    ("the ordnance still leaves while the enemy is visibly NOT underneath | AIR_DROP_EDGE_M | "
     "0.1 -> 0.05 (the box gap must be below 5 cm). Nothing else needs to move.",
     ),
    ("a block walks THROUGH underneath and nothing fires | AIR_DROP_EDGE_M | 0.1 -> 0.2 -> 0.3. A wide "
     "block's box gap only reaches 0.1 m when the boxes actually overlap; if the field still misses, the "
     "next suspects are the row's own air_only / no_melee gates (the log says which held it) or the "
     "engine's fall time - both are visible in the log.",
     ),
    ("a Lord / Hero (one model) is targeted | AIR_DROP_MIN_MEN | it cannot be: a one-model unit fails "
     "the > 10 test. If it happens, the unit is NOT one model (a chariot crew) - report it with the "
     "entities= number from the log.",
     ),
    ("the fast pass never turns ON | AIR_DROP_NEAR_M | it needs a valid enemy inside 30 m; the ON/OFF "
     "lines name the distance it saw.",
     ),
    ("TOTAL | 1 rule | The log prints the exact edge gap, the entity count, the enemy type and the "
     "caster's ui id on every decision, so a wrong drop is attributable to one number.",),
]


def main():
    wb = openpyxl.load_workbook(SRC)
    ws = wb["Abilities"]
    hdr = [c.value for c in ws[1]]
    col_trig = hdr.index("Trigger (as implemented)") + 1
    col_reason = hdr.index("Status reason / family") + 1
    col_fam = hdr.index("Trigger family") + 1

    n = 0
    for r in range(2, ws.max_row + 1):
        if ws.cell(row=r, column=col_fam).value != "air_drop_on_infantry":
            continue
        name = ws.cell(row=r, column=2).value
        mk = MARKER.get(name)
        assert mk is not None, "unmapped air-drop row: " + str(name)
        air_only, no_melee = AIR[mk]
        ws.cell(row=r, column=col_trig).value = RULE.format(
            air_only=str(air_only).lower(), no_melee=str(no_melee).lower())
        ws.cell(row=r, column=col_reason).value = FAMILY_NOTE
        n += 1
    assert n == 19, "air-drop rows updated: %d (want 19)" % n

    # ---- Definitions: retire sections 8-11, add section 12 ------------------
    dfn = wb["Definitions"]
    retired_heads = 0
    for r in range(1, dfn.max_row + 1):
        v = dfn.cell(row=r, column=1).value
        if not isinstance(v, str):
            continue
        for old in ("8. THE AIR-DROP PREDICTION CONSTANTS (round 110)",
                    "9. THE MOVING-CASTER DIALS (round 111)",
                    "10. THE FOURTH DIAL AND THE COMPLETE FOUR-DIAL MAP (round 112)",
                    "11. THE PATH RULE AND THE DERIVED FRONTAGE (round 113)"):
            if str(v).startswith(old):
                dfn.cell(row=r, column=1).value = "RETIRED IN ROUND 114 - " + str(v)
                retired_heads += 1
        if str(v).startswith("TUNING GUIDE (round 111)") or str(v).startswith("TUNING GUIDE (round 112)") \
                or str(v).startswith("TUNING GUIDE (round 113)"):
            dfn.cell(row=r, column=1).value = "RETIRED IN ROUND 114 - " + str(v)
            retired_heads += 1
    assert retired_heads >= 7, "retired definition heads: %d" % retired_heads

    # the reason, once, right after the section-8 header block
    start = dfn.max_row + 2
    dfn.cell(row=start, column=1).value = "RETIRED IN ROUND 114"
    dfn.cell(row=start + 1, column=1).value = DEF_RETIRED
    dfn.cell(row=start + 1, column=1).alignment = Alignment(wrap_text=True, vertical="top")
    row = start + 3
    for item in DEF12:
        c = dfn.cell(row=row, column=1)
        c.value = item[0]
        c.alignment = Alignment(wrap_text=True, vertical="top")
        if row - (start + 3) in (0, 1, 4, 5, 10, 11, 12, 16, 17, 21, 22, 25):
            c.font = Font(bold=True)
        row += 1

    # ---- Numbers: the version line ----------------------------------------
    num = wb["Numbers"]
    for r in range(1, num.max_row + 1):
        v = num.cell(row=r, column=1).value
        if isinstance(v, str) and v.startswith("Date: 2026-10-18"):
            num.cell(row=r, column=1).value = (
                "Date: 2026-10-18     Rule in force since: 2026-10-17     Inventory: 1,799 active "
                "abilities     (v15: round 114 - THE AIR-DROP RULE IS ONE COMPARISON. The air_drop_on_"
                "infantry family (12 entries / 19 keys) now fires when the NEAREST enemy that is ALIVE "
                "with MORE THAN 10 models has a battle_unit:unit_distance (EDGE-TO-EDGE) below 0.10 m. "
                "The infantry filter, the single-entity exclusion, the four projection dials, the 6 m "
                "centre bound, the derived frontage and the path test were DELETED from the evaluator and "
                "are marked RETIRED in Definitions sections 8-11; a second 0.2 s timer re-runs the same "
                "evaluator while a valid enemy is inside 30 m and the global poll is untouched. COUNTS "
                "UNCHANGED: 1,797 abilities / 1,141 in-wheel / 742 implemented keys / 689 entries / 46 "
                "evaluators - a behaviour change only)")
            break
    else:
        raise AssertionError("the Numbers version line was not found")

    # ---- Changelog ---------------------------------------------------------
    cl = wb["Changelog"]
    row = cl.max_row + 1
    cl.cell(row=row, column=1).value = "2026-10-18"
    cl.cell(row=row, column=2).value = "v15"
    cl.cell(row=row, column=3).value = (
        "ROUND 114 - THE AIR-DROP RULE IS ONE COMPARISON, PLUS A 0.2 s FAST PASS. (1) THE USER'S RULE, "
        "verbatim: '1. I want the trigger to be checked much more frequently when armed and less than 30 "
        "meters from a valid enemy unit. 2. Valid units are those who have more than 10 entities. 3. I "
        "trigger the moment distance between edges is below 0.1 meters. That's it.' and '1. Remove the "
        "\"and it is infantry\". No need for it now. 2. Current count 3. Let's try with 0.2 s for now.' "
        "(2) THE DECISION: the nearest ALIVE enemy with number_of_men_alive() > 10 whose "
        "battle_unit:unit_distance(caster, enemy) - the engine's EDGE-TO-EDGE bounding-box gap, "
        "battle_unit.lua:160 - is BELOW FOURTH.AIR_DROP_EDGE_M = 0.10 m. That is the whole test. (3) "
        "DELETED from the evaluator: the infantry filter (the user's ruling 1; every OTHER evaluator keeps "
        "its class filters), the single-entity exclusion on initial_number_of_men() == 1 (a one-model "
        "Lord / Hero fails the > 10 test by itself - the user's own point), the four projection dials "
        "AIR_DROP_DELAY_S / AIR_DROP_ENEMY_LEAD / AIR_DROP_CASTER_DELAY_S / AIR_DROP_CASTER_LEAD, "
        "AIR_DROP_INHERIT, the 6 m centre bound AIR_DROP_CENTER_M, the derived frontage "
        "(AIR_DROP_MODEL_RADIUS_M / AIR_DROP_RANKS / AIR_DROP_FRONTAGE_MIN_M / _MAX_M) and the path "
        "segment test - with every helper that served them (ad_frontage, ad_frontage_text, ad_seg_dist, "
        "ad_velocity, ad_lead, ad_project, ad_dial_text, ad_single_say, ad_single_clear, ad_centre_gap, "
        "ad_pos, ad_sep, ad_vec_text). NOTHING else in the mod called any of them, so they were removed "
        "rather than left dead. (4) FOUR NEW CONSTANTS: AIR_DROP_EDGE_M = 0.1 m, AIR_DROP_MIN_MEN = 10, "
        "AIR_DROP_NEAR_M = 30 m, AIR_DROP_FAST_S = 0.2 s. (5) THE FAST PASS: a SECOND model timer at 0.2 s "
        "runs the SAME evaluator (FOURTH.ad_pick) through the SAME gate+cast function (FOURTH.try_pair) "
        "the global poll uses, only for alive units ARMED for an air-drop marker and only while a VALID "
        "enemy is inside 30 m; it never iterates the full ability table, and the global poll (POLL_MS = "
        "250 ms) and every other ability's cadence are unchanged. The existing guard / charge / in-flight "
        "/ per-unit serialisation gates (stamped in poll ticks, written before the call) make a second "
        "fast tick inside the same poll window unable to cast again. (6) THE LOG, on every decision: "
        "'[<ui id>] <marker> nearest valid:'<key>' entities=<n> edge=<d.dd>m (need < 0.10m) -> NOT YET / "
        "FIRING', the re-check line with '-> SKIPPED at re-check', and ONE 'fast poll: ON (nearest valid "
        "<d>m)' / 'fast poll: OFF' line per change. (7) KEPT: air_only (is_currently_flying() exactly "
        "true), no_melee (is_in_melee() not true), the self-centred cast on the OWNER, fail-closed reads, "
        "the readiness gate and every hold, and the pre-cast re-check - which now re-validates the > 10 "
        "model test and re-measures the edge gap on fresh handles and skips the cast if it moved out. "
        "(8) COUNTS UNCHANGED: 689 entries / 742 keys, air_drop_on_infantry 12 entries / 19 keys, 46 "
        "evaluators - a behaviour change only. Harness 114: 4614 checks / 0 failures (run twice, "
        "byte-identical); red control (the round-113 build) 56 failures, ALL in the new section. Installed "
        "pack md5 2cec3140e4d0838fa678187621ea55b0.")
    cl.cell(row=row, column=4).value = (
        "the user's two rulings of 2026-10-18 (the simple edge-gap rule with the > 10 entity filter and "
        "the 30 m / 0.2 s fast pass, then 'remove the infantry filter'); docs/WH3_round114_airdrop_"
        "edgesimple.md; harness 114 (worlds A 0.09 fires / 0.11 silent, B 10 excluded / 11 included, C "
        "20-model cavalry is a legal candidate, D the one-model lord excluded, E nearest-of-two, F the "
        "re-check skip, G the fast-poll ON/OFF transitions, H two consecutive fast ticks cast once, I "
        "unreadable distance fails closed, J the fast pass never runs a non-air-drop ability) with its "
        "section-0 pins in BOTH the live and the annotated copy. Supersedes v14; v1-v14 are left "
        "byte-unchanged.")
    for c in range(1, 5):
        cl.cell(row=row, column=c).alignment = Alignment(wrap_text=True, vertical="top")

    wb.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
