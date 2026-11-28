#!/usr/bin/env python3
"""Round 220 (sign-off): the tracker (10.97) and CLAUDE.md."""
ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"
LOG = """
### 10.97 Round 220 - a placed effect does not stop its caster, the polls' speed fixes (2026-11-28)

**Field (the round-219 build; archive\\logs\\battle_20261128_r219_perf.txt, bytes 1,188,201,797-1,202,349,084; 291 s,
40 units, 37 active abilities).**

- Round 219's rule works: 8 automatic Brass Orb casts (4 in the battle before), every caster used a second charge,
  mostly on Hochland Long Rifles (35 to 43 men). One cast went onto Demigryph Knights in contact with the caster
  (0 m). User ruling on protecting the caster of a placed blast: "No".
- The user cast Brass Orb by hand with a Warlock Master (unit 1003, t = 62 s): the unit kept moving 10 m every 2 s
  through the cast and for 18 s after. Brass Orb's wind_up_stance is cast_forward_medium, the same as Amber Bow, which
  stopped Markus Wulfhart (round 190). **The animation does not decide it.**
- The evaluators cost 61.3 ms of every second (the polls' real work 64.0, single seconds up to 449 ms):
  enemy_wander 23.7 (2.44 ms per call), enemy_blob 11.5 (1.19), melee_vs_large 6.3 (1.04), enemy_single_drain 4.6
  (0.74), every other family under 3.

| Seen in battle | Stopped its caster | Delivery |
|---|---|---|
| Volley of High Arrows, Soporific Breath, Amber Bow | yes | a projectile shot by the caster |
| Brass Orb, Gaze of Malice | no | a vortex placed at the target |
| Book of Hoeth | no | no cast animation |

**Rulings (2026-11-28):** all placed ones "Yes". Protect the caster "No". The speed fixes "build them".

**Change:**

- `tools\\gen_anim_keys.py`: a key leaves the GENERATED ANIM set when its effect is a vortex with neither a projectile
  nor a bombardment (`placed`). 51 keys left (18 enemy_wander entries, 17 enemy_wave, 7 melee_unwavering, 2
  enemy_cone, 2 enemy_sweep, fly_dive, health_aura_ground, enemy_area_drain, melee_clear, enemy_blob_vortex), 183
  stay. The 22 bombardments and the other animated kinds wait as before: not seen.
- `FOURTH.locked_now(ui_id, ability)`: the poll returns before the evaluator while the mod knows the cast cannot go
  out (a counted recharge unless the selected unit's button reads ready, the ability's own wind-up, a logged
  back-off after the game refused it).
- `FOURTH.blob_score_c` / `FOURTH.blob_friend_gap_c`: a target's soldiers under a blast and its friendly gap once per
  map and blast size. `FOURTH.blob_shape` stores the unit id, `FOURTH.ww_target_still` reads is_moving() once per map.

**Proof:** harness 218 full suite **8,646 checks / 0 failures**. RED on the pre-round snapshot: no cast from a
walking Brass Orb caster (GREEN one), 12 to 24 distance reads by a caster whose Brass Orb is recharging (GREEN 0), the
target's is_moving() read 25 times in 8 polls by three casters (GREEN 9). The cast trace (2,252 worlds, 1,792
casts) matches between the test build and the release build apart from the 3 probe casts, and its first 2,244 worlds
are byte-equal to round 219's trace: the speed fixes changed no cast. One rebased pin: harness 167 CA1 (Frost Fang's
card no longer asks the caster to stand). Workbook v86 (51 trigger texts, 39 cards).

**Not seen in game. Not measured yet:** what the polls cost now. **Still open:** the 5 s safety walk.
"""


def one(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


def main():
    p = ROOT + "docs\\WH3_ability_tracker.md"
    s = open(p, encoding="utf-8", newline="").read()
    assert "### 10.97 Round 220" not in s
    open(p, "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n" + LOG)
    p = ROOT + "CLAUDE.md"
    s = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    s = one(s, "- Installed build: md5 `d3e437f21661e7c6b2d8064a0c779e22`" + nl
            + "  (round 219, 2026-11-28: the placed blasts take most of a unit and standing cavalry, the evaluators timed by family).",
            "- Installed build: md5 `a0283f3e353a894075e1a72d1317c186`" + nl
            + "  (round 220, 2026-11-28: placed effects fire on the move, no evaluator call while a cast cannot go out).")
    s = one(s, "20261128_cover_harness217/build_and_install219.py", "20261128_placed_harness218/build_and_install220.py")
    s = one(s, "(harness217: 8,627 checks; it takes about 2 minutes)", "(harness218: 8,646 checks; it takes about 2 minutes)")
    s = one(s, "| `docs\\WH3_abilities_master_v85_2026-11-28.xlsx` | the current master spreadsheet (versioned, newest wins). "
            "Built by `tools\\make_xlsx_v85.py`, verified by `tools\\verify_xlsx_v85.py <v84 md5> <pack md5>` (v85 = v84 + ",
            "| `docs\\WH3_abilities_master_v86_2026-11-28.xlsx` | the current master spreadsheet (versioned, newest wins). "
            "Built by `tools\\make_xlsx_v86.py`, verified by `tools\\verify_xlsx_v86.py <v85 md5> <pack md5>` (v86 = v85 + "
            "the PLACED sentence on 51 rows, 39 cards. v85 = v84 + ")
    s = one(s, "- A cast stops its moving caster ONLY when the ability plays a cast animation (unit_special_abilities.wind_up_stance",
            "- ROUND 220 CORRECTION (field 2026-11-28): the animation does NOT decide. A cast stops its moving caster when the "
            "caster SHOOTS A PROJECTILE (Volley of High Arrows, Soporific Breath, Amber Bow stopped). A PLACED effect (a vortex, "
            "no projectile, no bombardment) does not, animation or not (Brass Orb, Gaze of Malice). ANIM = animated AND not "
            "placed (gen_anim_keys.placed). Bombardments and other animated kinds: NOT SEEN, they still wait. The old line: "
            "a cast stops its moving caster ONLY when the ability plays a cast animation (unit_special_abilities.wind_up_stance")
    a = "- ROUND 219 (2026-11-28, SIGN-OFF, TEST PACK INSTALLED: md5 d3e437f2...; workbook v85; tracker 10.96)."
    note = [
        "- ROUND 220 (2026-11-28, SIGN-OFF, TEST PACK INSTALLED: md5 a0283f3e...; workbook v86; tracker 10.97). FIELD on",
        "  round 219 (archive\\logs\\battle_20261128_r219_perf.txt, bytes 1,188,201,797-1,202,349,084, 291 s, 40 units): the",
        "  cover rule WORKS (8 Brass Orb casts, second charges used). THE EVALUATORS COST 61 ms/s: enemy_wander 23.7 (2.4",
        "  ms per call), enemy_blob 11.5, melee_vs_large 6.3, enemy_single_drain 4.6, the rest under 3 each. The user's",
        "  hand cast of Brass Orb did NOT stop a walking Warlock Master (same stance as Amber Bow, which stopped): see",
        "  ENGINE FACTS. RULINGS: all placed ones 'Yes', protect the caster of a placed blast 'No' (a cast at 0 m onto",
        "  enemies in contact with the caster happened), the speed fixes 'build them'. BUILT: gen_anim_keys.placed (51",
        "  keys out of ANIM, 183 stay), FOURTH.locked_now(ui_id, ability) BEFORE the evaluator in the poll's per-ability",
        "  closure ('if ... then return nil end': the pinned lines 'local reason = ability.evaluate(unit, routing)' /",
        "  'local want_fire = ...' in the reading copy must stay literal), FOURTH.blob_score_c / blob_friend_gap_c (one",
        "  slot per shape keyed by the map table and the blast size: the wander view and m are different tables),",
        "  s.id on every shape, e.c_still. Harness 218: 8,646 / 0, RED on all three, the cast trace's first 2,244 worlds",
        "  byte-equal to round 219's (compare a new trace with the previous round's to prove a speed fix changes no",
        "  cast), one rebased pin (harness 167 CA1, Frost Fang's card). NOT SEEN IN GAME, the polls' new cost NOT",
        "  MEASURED. NOT TOUCHED: melee_vs_large and enemy_single_drain (1.0 and 0.7 ms per call), the 5 s safety walk.",
        "  The WORKSHOP ITEM STILL CARRIES ROUND 212. Next battle from byte 1,202,349,084 (re-measure): analyze_perf.py",
        "  and the 'PERF TRIG' lines.",
    ]
    s = one(s, a, nl.join(note) + nl + a)
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("tracker and CLAUDE.md updated")


if __name__ == "__main__":
    main()
