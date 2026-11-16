#!/usr/bin/env python3
"""Round 162: the tracker rows (32 implemented, 2 closed by the user) and section 10.40, and the database family texts.
The per-row numbers come from the GENERATED WW table (tools/gen_ww_tables.py) and the game's ranges."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_ww_tables as GW  # noqa: E402
import gamedata_paths as GP  # noqa: E402

TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"
SRC = open(r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua", encoding="utf-8").read()
KF = GW.keys_in(SRC)
ROWS_WW = GW.derive(KF)
USA = {r["key"]: r for r in GW.tsv("unit_spec_abil.tsv")}
NOTE = " · **round 162 (2026-11-16):** the wandering winds, user ruling \"%s\"."


def bound(k):
    return int(math.floor(float(USA[k]["target_intercept_range"]) * 0.70 + 1e-9))


def texts(k):
    kind, r, path, off, buf, allies, ground = ROWS_WW[k]
    if KF[k] == "enemy_wave":
        return ("implemented (clear wave path, most value, target standing: enemy_wave)",
                "When armed and standing still, casts at the standing enemy within %d m whose %g m wave path holds the most "
                "enemy value and none of our units within %g m of its start, widening to %g m at its end (radius %g + 95%% "
                "drift %d + 10 m)." % (bound(k), path, r + 10, r + buf + 10, r, buf),
                "Clear path, most value and not currently moving")
    if not allies:
        safe = "it cannot hurt our units, so no friendly test"
    else:
        extra = " + the target's half extent" if kind == 3 else ""
        safe = "none of our units within %g m of the target (radius %g + 95%% reach %d + 10 m%s)" % (
            r + buf + 10, r, buf, extra)
    return ("implemented (wandering blast on a standing blob: enemy_wander)",
            "When armed and standing still, casts at the standing enemy infantry within %d m worth the most whose %g m "
            "blast covers the blob line; %s." % (bound(k), r, safe),
            "Worst-case reach, Simulated 95%" if allies else "Blob rule; close 2")


ROWS = {k: texts(k) for k in KF}
assert len(ROWS) == 32
CLOSE = {
    "wh3_pro10_cataclysm_metal_gehennas_golden_globe_bound": "a straight 140 m line whose heading is not in the game data",
    "wh3_main_spell_bound_wall_of_wind_and_fire": "a straight 69 m line whose heading is not in the game data",
}
SECTION = """

### 10.40 Round 162 - the wandering winds (2026-11-16)

**Earlier status:** "excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))", a RULE, never
a ruling on these 34 abilities one by one. Wrath of Manann was the first one seen uncovered (Bretonnia battle).

**Rulings (user, 2026-11-16).**

- **The 12 straight waves:** "Clear path, most value and not currently moving" -> NEW `enemy_wave`. The target must
  stand still (the 3-5 s cast: a moving target walks out of the computed path). The buffer follows each ability's own
  randomness ("some abilities are more random than others").
- **The 16 wanderers:** "Worst-case reach", then the buffer rule "Simulated 95%" -> NEW `enemy_wander`.
- **The Burning Head x2 and Arnzipal's Black Horror:** "Automate with the big buffer".
- **The other 6:** "Blob rule; close 2": Heaven's Gate, The Abyssal Swarm (no friendly test) and The Dwellers Below x2
  on `enemy_wander`; Gehenna's Golden Globe and Wall of Wind & Fire closed (`rejected`).

**The buffer:** GENERATED `FOURTH.WW_TEXT` (`tools\\gen_ww_tables.py`): 4,000 simulated paths per reading of the game's
turn fields, the 95% line of the wider reading. Straight waves drift 0 m; Wrath of Manann 17 m; Wind of Death 25 m;
The Burning Head 109 m; Banishment 16 m; Sandstorm 46 m. A wave's corridor widens from radius + 10 m at its start to
radius + drift + 10 m at its end (a wave cannot drift where it starts; the caster is usually inside the full width).

**Arithmetic.**

- **Rows:** implemented 917 + 32 = **949 rows / keys**; not implemented among the included 206 - 34 = **172**, of
  which 32 + 2 = 34 are the user's skips.
- **The mod:** 860 + 32 = **892 entries / 949 keys**; **90** families.
- **Tests:** harness 161 full suite **6,833 checks / 0 failures**, run twice byte-identical. RED 8/8.
- **Install:** pack md5 `5792ffbeaa36c6110448037d38314a06`.
"""
s = open(TRACKER, encoding="utf-8", newline="").read()
lines = s.split("\n")
done = set()
for i, l in enumerate(lines):
    if not l.startswith("| "):
        continue
    first = l.split("|")[1].strip()
    for k in list(ROWS) + list(CLOSE):
        if first.endswith("`%s`" % k):
            assert k not in done, k
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            if k in ROWS:
                st, pr, rule = ROWS[k]
                c[1] = "`%s`" % st
                c[3] = pr
                c[4] = c[4] + NOTE % rule
            else:
                c[1] = "`rejected (user 2026-11-16: \"Blob rule; close 2\"; %s)`" % CLOSE[k]
                c[3] = "Not automated (user decision 2026-11-16)."
                c[4] = c[4] + NOTE % "Blob rule; close 2"
            lines[i] = "| " + " | ".join(c) + " |"
            done.add(k)
want = set(ROWS) | set(CLOSE)
assert done == want, sorted(want - done)
s = "\n".join(lines)
assert "### 10.40" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION and all("\u2014" not in t for v in ROWS.values() for t in v)
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.40" % len(done))
d = open(DBB, encoding="utf-8", newline="").read()
OLD = '        "enemy_wavering": '
NEW = ('        "enemy_wave": "The caster STANDING STILL; among the visible enemies in range that are STANDING STILL, the one '
       'whose straight wave path (from offset + its half extent before it, along the caster-to-target heading, speed x '
       'duration long) has none of our units within radius + 10 m at its start widening to radius + the simulated 95% '
       'sideways drift + 10 m at its end (the GENERATED WW table), and the most enemy value on the path. Casts on that '
       'enemy; re-checked before the cast.",\n'
       '        "enemy_wander": "The caster STANDING STILL; the visible enemy infantry in range, STANDING STILL, whose blast '
       'covers the blob density line and the most value, with none of our units within radius + the simulated 95% reach '
       '+ 10 m of it (no friendly test when the game marks the vortex as not hitting allies). Casts on that enemy (on its '
       'ground for a ground-only ability); re-checked before the cast.",\n' + OLD)
assert d.count(OLD) == 1 and '"enemy_wave":' not in d
d = d.replace(OLD, NEW)
open(DBB, "w", encoding="utf-8", newline="").write(d)
print("database builder: 2 family texts")
