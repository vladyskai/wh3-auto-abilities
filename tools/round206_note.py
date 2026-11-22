#!/usr/bin/env python3
"""Round 206 (tuning): the notes in CLAUDE.md (installed build, builder, suite, the round note) and the tracker (10.83)."""
ROOT = "C:\\Users\\vlady\\Desktop\\WH3_mod\\"
LOG = """
### 10.83 Round 206 (tuning) - an exact wave's value counts standing enemies only (2026-11-22)

**Field (user, 2026-11-22):** Sunfang, "It is better than before, but why it casts so far away from the main blob?", then
"Fought until a second cast, and that one was perfect. So still a bit inconsistent".

**The log:** at the first order one Grave Guard unit stood in melee and two were still walking in. The value counted all
visible enemies where they were (108 + 108 soldiers under the cone). The enemy's health dropped only 4 to 6 s after the
order. By then the walking unit had moved 8 m and 48 of its soldiers were under the fire. The losses (15% and 8% of
health) match the model's 88 and 48 soldiers. At the second cast every enemy stood.

**Change:** an exact wave's value counts only enemies whose `is_moving()` reads exactly false. No ruling was needed: it is
option A (standing targets only, user 2026-11-22) applied to the value as well as to the anchor.

**Proof:** harness 204 full suite **8,335 checks / 0 failures** (once). RED on the round-205 snapshot: a walking unit
pulls the cone across both blocks. Tuning round: no workbook version, the 27 wave rows of v82 do not carry this sentence.
"""


def one(s, a, b):
    assert s.count(a) == 1, (a[:70], s.count(a))
    return s.replace(a, b)


def main():
    p = ROOT + "docs\\WH3_ability_tracker.md"
    s = open(p, encoding="utf-8", newline="").read()
    assert "### 10.83 Round 206" not in s
    open(p, "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n" + LOG)
    p = ROOT + "CLAUDE.md"
    s = open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in s else "\n"
    s = one(s, "- Installed build: md5 `c613f8a1338a6fce6fd87158bd2de72a`, 1,642,218 bytes" + nl
            + "  (round 205, 2026-11-22: the growing waves are cones, enemy single entities are not counted).",
            "- Installed build: md5 `b4db526095800c24addb534931f398df`, 1,642,503 bytes" + nl
            + "  (round 206, 2026-11-22, tuning: an exact wave's value counts standing enemies only).")
    s = one(s, "20261122_cone_harness203/build_and_install205.py", "20261122_standing_harness204/build_and_install206.py")
    s = one(s, "(harness203: 8,320 checks; it takes about 2 minutes)", "(harness204: 8,335 checks; it takes about 2 minutes)")
    a = "- ROUND 205 (2026-11-22, `docs\\WH3_round205_cone.md`) INSTALLED"
    note = [
        "- ROUND 206 (2026-11-22, TUNING, INSTALLED: test pack md5 b4db5260..., release pack md5 d74e4685...). FIELD",
        "  (archive\\logs\\battle_20261122_r205_cone.txt, bytes 1,036,362,003-1,045,400,480; user: \"why it casts so far away",
        "  from the main blob?\", then \"a second cast, and that one was perfect. So still a bit inconsistent\"): at the first",
        "  Sunfang order ONE Grave Guard unit stood and two were still WALKING in. The value counted all visible enemies where",
        "  they were (108 + 108 soldiers under the cone by tools\\replay_cone_cast.py). The damage showed in the enemy's hp",
        "  only 4 to 6 s AFTER the order (ENGINE FACT, one cast: order at t~59, hp drop between t=64 and t=66): the walking",
        "  unit had moved 8 m, 48 soldiers left under it. The hp loss (15% and 8%) matches the model's 88 and 48, so the CONE",
        "  MODEL IS RIGHT (tools\\replay_cone.py reproduces the mod's own choice exactly). BUILT: an exact wave's value counts",
        "  only enemies whose is_moving() is exactly false (o.still, read once per unit per map), option A applied to the",
        "  value too. Harness 204: 8,335 checks / 0 failures (once). RED: a walking unit pulls the cone across both blocks.",
        "  No workbook (tuning: v82's wave rows lack this sentence), no cast trace. A wider search (more start distances, 48",
        "  headings) was replayed: +7 to +25% soldiers only, NOT built. NOT SEEN IN GAME. Next battle from byte",
        "  1,045,400,480.",
    ]
    s = one(s, a, nl.join(note) + nl + a)
    open(p, "w", encoding="utf-8", newline="").write(s)
    print("tracker and CLAUDE.md updated")


if __name__ == "__main__":
    main()
