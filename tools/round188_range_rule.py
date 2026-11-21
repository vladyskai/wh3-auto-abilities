#!/usr/bin/env python3
"""Round 188 (user ruling 2026-11-21: "C. Your rule, the larger of 70% and real minus 20 m, everywhere. This one").

Rule 3 changes: every cast-range bound becomes max(floor(real x 0.70), real - FOURTH.RANGE_MARGIN_M), with
RANGE_MARGIN_M = 20. The named constants FOURTH.ENEMY_CAST_R<real> and FOURTH.ALLY_CAST_R<real> are rewritten to that
value (they change for every real range above 66 m: 100 m 70 -> 80, 200 m 140 -> 180, 250 m 175 -> 230). Auras (15, 35,
55 m) and the dive / blast reaches (25 m or less) keep their numbers: there 70% is the larger value. The Executioner's 90%
exception takes the larger of its two bounds (250 m: 225 vs 230 -> 230). The air drop keeps its own test constant.
"""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
MARGIN = 20


def bound(real):
    return max((real * 70) // 100, real - MARGIN)


CONST = re.compile(r"^(FOURTH\.(ENEMY|ALLY)_CAST_R(\d+)\s*=\s*)(\d+)(.*)$", re.M)
FRAC_OLD = "FOURTH.RANGE_FRACTION = 0.70\n"
FRAC_NEW = ("FOURTH.RANGE_FRACTION = 0.70\n"
            "FOURTH.RANGE_MARGIN_M = 20   -- ROUND 188 (user 2026-11-21): a bound is max(floor(real x 0.70), real - 20 m)\n"
            "-- ROUND 188: the cast-range bound of a real range (metres): the larger of 70% and real - RANGE_MARGIN_M\n"
            "function FOURTH.range_bound(real)\n"
            "\treturn math.max(math.floor(real * FOURTH.RANGE_FRACTION + 1e-9), real - FOURTH.RANGE_MARGIN_M)\n"
            "end\n")
EXEC_OLD = ("\t\tif ability.range_frac == FOURTH.SINGLE_RANGE_FRACTION then\n"
            "\t\t\tability.range_m = math.floor(ability.range_real * FOURTH.SINGLE_RANGE_FRACTION + 1e-9)\n"
            "\t\tend\n")
EXEC_NEW = ("\t\tif ability.range_frac == FOURTH.SINGLE_RANGE_FRACTION then\n"
            "\t\t\t-- ROUND 188: the larger of the 90% exception and the standing bound (250 m: 225 vs 230)\n"
            "\t\t\tability.range_m = math.max(ability.range_m or 0,\n"
            "\t\t\t\tmath.floor(ability.range_real * FOURTH.SINGLE_RANGE_FRACTION + 1e-9))\n"
            "\t\tend\n")


def main():
    for path in (SRC, ANN):
        s = open(path, encoding="utf-8", newline="").read()
        assert "FOURTH.RANGE_MARGIN_M" not in s
        changed = []

        def rep(m):
            real, old = int(m.group(3)), int(m.group(4))
            assert old == (real * 70) // 100, (m.group(0), old)
            new = bound(real)
            if new == old:
                return m.group(0)
            changed.append((m.group(2), real, old, new))
            return "%s%d%s   -- ROUND 188: max(70%%, %d - 20) (was %d)" % (m.group(1), new, m.group(5), real, old)

        s = CONST.sub(rep, s)
        assert s.count(FRAC_OLD) == 1 and s.count(EXEC_OLD) == 1
        s = s.replace(FRAC_OLD, FRAC_NEW).replace(EXEC_OLD, EXEC_NEW)
        open(path, "w", encoding="utf-8", newline="").write(s)
        print(path.split("\\")[-1], len(changed), "constants changed")
        for c in changed:
            print("   %s %d m: %d -> %d" % c)


if __name__ == "__main__":
    main()
