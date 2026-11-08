"""Assemble harness112.lua from harness111.lua + the round-112 section.

TWO THINGS HAPPEN HERE, and both are printed by the script so the run is
auditable:

1. FORMAT / REBASE SUPERSESSION. Round 112 deliberately changes two things the
   older suites pinned, and one thing they depended on:

     * the watch line prints EXACT metres below 15 m (round 111 banded at 5 m),
       so every count_log/raw_find token that spelled `~Nm` had to be respelled;
     * the decision/watch/skip/re-check dial text is now the FOUR-dial form
       (`delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=0.50`), so
       `delay_caster=1.50s lead=0.50` no longer appears;
     * the ENEMY's projection is no longer the full 1.5 s carry, so every world
       that measured an enemy projection changes its number - those are REBASED
       with the new arithmetic spelled out in the check's own text and prefixed
       `(REBASED v112)`.

   Each replacement below is exactly one occurrence and the count is asserted,
   so a stale snapshot cannot silently pass. NOTHING is loosened: every rebased
   check still asserts the same quantity, at its new value, with the arithmetic
   in its label; no check is deleted and the check count is unchanged.

2. The new section is appended and run AFTER 109/110/111, so the printed total
   covers all four suites.
"""
import io

SRC = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261023_airdrop_movingcaster_harness111/harness111.lua"
DST = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261024_airdrop_enemylead_harness112/harness112.lua"
SEC = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261024_airdrop_enemylead_harness112/h112_section.lua"

s = io.open(SRC, encoding="utf-8", newline="").read()
assert "\r" not in s

PAIRS = []

# ---------------------------------------------------------------- 109 B2 (format)
PAIRS.append(("""      check(TAG .. "B2b: the why-not line names centre=10.0m [live log]",
        lg109((TAG ~= "[live] ")
          or (count_log(W, "watch: nearest INFANTRY '" .. INF .. "' is centre=~10m") == 1""",
"""      -- (v112 format: exact metres below 15 m)
      check(TAG .. "B2b (v112 EXACT METRES): the why-not line names centre=10.00m [live log]",
        lg109((TAG ~= "[live] ")
          or (count_log(W, "watch: nearest INFANTRY '" .. INF .. "' is centre=10.00m") == 1"""))

# ---------------------------------------------------------------- 110 0ab static
PAIRS.append(("""      check("0ab " .. nm .. ": the watch line prints the projected band AND both velocities",
        raw_find(s2, '" [projected sep=~"', 1, true) ~= nil
        and raw_find(s2, '"m after delay="', 1, true) ~= nil)""",
"""      -- v112: the projected distance is EXACT below 15 m; the gate now demands
      -- the exact-metre form AND the 15 m band boundary.
      check("0ab " .. nm .. ": the watch line prints the EXACT projected distance AND both velocities"
        .. " (v112: exact < 15 m, band above)",
        raw_find(s2, '" [projected sep="', 1, true) ~= nil
        and raw_find(s2, '" after delay="', 1, true) ~= nil
        and raw_find(s2, "near_gap < 15", 1, true) ~= nil)"""))

# ---------------------------------------------------------------- 110 A2b
PAIRS.append(("""        check(TAG .. "A2b: the watch line names the projected band [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "watch: nearest INFANTRY '" .. INF .. "' is centre=~5m") == 1
              and count_log(W, "projected sep=~5m after delay=1.50s") == 1)))""",
"""        check(TAG .. "A2b (v112 EXACT METRES): the watch line names 6.50 m exactly [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "watch: nearest INFANTRY '" .. INF .. "' is centre=6.50m") == 1
              and count_log(W, "projected sep=6.50m after delay=1.50s") == 1)))"""))

# ---------------------------------------------------------------- 110 B2b
PAIRS.append(("""      check(TAG .. "B2b: the why-not line shows both numbers and the receding velocity [live log]",
        lg110((TAG ~= "[live] ")
          or (count_log(W, "is centre=~5m vs bound=6m") == 1
            and count_log(W, "projected sep=~15m after delay=1.50s") == 1""",
"""      -- (v112: exact metres; the enemy here is STATIONARY, so only the print changed)
      check(TAG .. "B2b (v112 EXACT METRES): the why-not line shows 5.00 m now, the 17.0 m projection BANDED to ~15m (above the 15 m exact window), and the receding velocity [live log]",
        lg110((TAG ~= "[live] ")
          or (count_log(W, "is centre=5.00m vs bound=6m") == 1
            and count_log(W, "projected sep=~15m after delay=1.50s") == 1"""))

# ---------------------------------------------------------------- 110 C1 (REBASED)
PAIRS.append(("""        check(TAG .. "C1a: the enemy closes from 10 m to 4 m - FIRES (" .. #W.fires .. ")", #W.fires == 1)
        check(TAG .. "C1b: the log shows the projected enemy point (0.0, 4.0) and now=10.0m [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "centre=4.0m") >= 1 and count_log(W, " now=10.0m") >= 1
              and count_log(W, "enemy=(0.0, 10.0) v=(0.0, -4.0) 4.0 m/s src=ordered proj=(0.0, 4.0)") >= 1)))""",
"""        -- REBASED v112: the enemy is now carried 1.5 s * ENEMY_LEAD 0.3 = 0.45 s,
        -- i.e. 4 m/s * 0.45 s = 1.8 m, not 6 m. 10 m -> 8.2 m, so the 6 m pin is
        -- NOT met. (Under the round-110 full carry this world fired at 4.0 m.)
        check(TAG .. "C1a (REBASED v112): the enemy closes 10 m -> 8.20 m at the shipped enemy lead 0.3 - SILENT ("
          .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "C1b (REBASED v112): the why-not line shows projected 8.20 m from now=10.00 m and the ordered velocity [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "projected sep=8.20m after delay=1.50s") >= 1
              and count_log(W, "is centre=10.00m vs bound=6m") >= 1
              and count_log(W, "enemy v=(0.0, -4.0) 4.0 m/s src=ordered") >= 1
              and count_log(W, "enemy_lead=0.30") >= 1)))"""))

# ---------------------------------------------------------------- 110 C2b
PAIRS.append(("""        check(TAG .. "C2b: the why-not line shows the projected 10 m band [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "is centre=~5m vs bound=6m") == 1
              and count_log(W, "projected sep=~10m after delay=1.50s") == 1)))""",
"""        -- REBASED v112: 5 m + 4 m/s * 0.45 s = 6.80 m projected (was 11 m).
        check(TAG .. "C2b (REBASED v112): the why-not line shows projected 6.80 m from now=5.00 m [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "is centre=5.00m vs bound=6m") == 1
              and count_log(W, "projected sep=6.80m after delay=1.50s") == 1)))"""))

# ---------------------------------------------------------------- 110 D1 (REBASED)
PAIRS.append(("""        check(TAG .. "D1a: closing at 12 m/s over 1.5 s leaves 2 m - FIRES (" .. #W.fires .. ")",
          #W.fires == 1)
        check(TAG .. "D1b: the log proves BOTH projections (112 vs 114) and now=20.0m [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "centre=2.0m") >= 1 and count_log(W, " now=20.0m") >= 1
              and count_log(W, "proj=(112.0, 200.0)") >= 1
              and count_log(W, "proj=(114.0, 200.0)") >= 1)))""",
"""        -- REBASED v112: the caster still leads fully (lead 1.0 -> 112.0) but the
        -- enemy now projects 120 - 4*0.45 = 118.2, so the gap is 6.20 m - 0.20 m
        -- outside the pin. (v110/111: 112 vs 114 -> 2.0 m -> fired.)
        check(TAG .. "D1a (REBASED v112): caster 112.0 vs enemy 118.2 leaves 6.20 m - just outside the 6 m pin ("
          .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "D1b (REBASED v112): the why-not line shows the 20.0 m instant BANDED (~20m) and the deciding 6.20 m EXACT [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "is centre=~20m vs bound=6m") >= 1
              and count_log(W, "projected sep=6.20m after delay=1.50s") >= 1)))"""))

# ---------------------------------------------------------------- 110 D2b
PAIRS.append(("""        check(TAG .. "D2b: the why-not band is the projected 5 m band [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "is centre=~25m vs bound=6m") == 1
              and count_log(W, "projected sep=~5m after delay=1.50s") == 1)))""",
"""        -- REBASED v112: 125 - 4*0.45 = 123.2 against the caster's 112 -> 11.20 m
        -- (was 7 m). The decision is unchanged (silent); the number is not.
        check(TAG .. "D2b (REBASED v112): the why-not line shows the 25.0 m instant BANDED (~25m) and the deciding 11.20 m EXACT [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "is centre=~25m vs bound=6m") == 1
              and count_log(W, "projected sep=11.20m after delay=1.50s") == 1)))"""))

# ---------------------------------------------------------------- 110 E1b
PAIRS.append(("""        check(TAG .. "E1b: the log's projected separation EQUALS the current one [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "centre=4.0m") >= 1 and count_log(W, " now=4.0m") >= 1)))""",
"""        -- REBASED v112: the pair no longer cancels exactly - the caster leads
        -- 8 v 1.5 v 1.0 = 12.0 m while the enemy leads 8 v 0.45 = 3.6 m, so a
        -- 4.0 m start closes to 4.40 m. The DECISION is unchanged (fires).
        check(TAG .. "E1b (REBASED v112): projected 4.40 m against now=4.0m - the caster now leads more than the enemy [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "centre=4.4m") >= 1 and count_log(W, " now=4.0m") >= 1)))"""))

# ---------------------------------------------------------------- 110 E2 (REBASED)
PAIRS.append(("""        check(TAG .. "E2a: 7 m apart on the same heading - still 7 m projected - no fire ("
          .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "E2b: the projected band equals the current band [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "is centre=~5m vs bound=6m") == 1
              and count_log(W, "projected sep=~5m after delay=1.50s") == 1)))""",
"""        -- REBASED v112: same heading, but the caster now leads 12.0 m and the
        -- enemy only 3.6 m, so a 7.0 m start CLOSES to 1.40 m and fires. Under
        -- the round-110 full carry both bodies moved 12 m and it stayed 7 m.
        -- This is the one place where cutting the enemy's lead changes a
        -- decision in the old suites - it is pinned here, deliberately.
        check(TAG .. "E2a (REBASED v112): 7 m on the same heading now closes to 1.40 m - FIRES ("
          .. #W.fires .. ")", #W.fires == 1)
        check(TAG .. "E2b (REBASED v112): the why-not/decision numbers are 7.00 m now, 1.40 m projected [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "centre=1.4m") >= 1
              and count_log(W, " now=7.0m") >= 1)))"""))

# ---------------------------------------------------------------- 110 F1b
PAIRS.append(("""        check(TAG .. "F1b: the why-not line bands the PROJECTED 7 m, not the current 7.8 m [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "projected sep=~5m after delay=1.50s") == 1
              and count_log(W, "is centre=~5m vs bound=6m") == 1)))""",
"""        -- REBASED v112: the crossing enemy is carried 4 * 0.45 = 1.8 m, not 6,
        -- so the projected point is 8.16 m out (was 7.0 m). Still silent.
        check(TAG .. "F1b (REBASED v112): the PROJECTED 8.16 m and now=9.22 m, both exact [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "projected sep=8.16m after delay=1.50s") == 1
              and count_log(W, "is centre=9.22m vs bound=6m") == 1)))"""))

# ---------------------------------------------------------------- 110 F2 (REBASED)
PAIRS.append(("""        check(TAG .. "F2a: the same crossing 5 m off passes right over the caster at t+1.5 s - FIRES ("
          .. #W.fires .. ")", #W.fires == 1)
        check(TAG .. "F2b: projected centre 5.0 m with now=7.8 m [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "centre=5.0m") >= 1 and count_log(W, " now=7.8m") >= 1)))""",
"""        -- REBASED v112: 5 m lateral + 1.8 m of carried travel = 6.53 m, i.e.
        -- just OUTSIDE the 6 m pin (the full carry brought it to 5.0 m and fired).
        check(TAG .. "F2a (REBASED v112): the 5 m crossing projects 6.53 m at the shipped enemy lead 0.3 - SILENT ("
          .. #W.fires .. ")", #W.fires == 0)
        check(TAG .. "F2b (REBASED v112): 6.53 m projected against 7.81 m now, both exact [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "projected sep=6.53m after delay=1.50s") >= 1
              and count_log(W, "is centre=7.81m vs bound=6m") >= 1)))"""))

# ---------------------------------------------------------------- 110 G1b
PAIRS.append(("""        check(TAG .. "G1b: the source is printed as moving-unreadable [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "src=moving-unreadable") >= 1
              and count_log(W, "projected sep=~10m after delay=1.50s") == 1)))""",
"""        check(TAG .. "G1b (v112 EXACT METRES): the source is printed as moving-unreadable, projected 12.00 m [live log]",
          lg110((TAG ~= "[live] ")
            or (count_log(W, "src=moving-unreadable") >= 1
              and count_log(W, "projected sep=12.00m after delay=1.50s") == 1)))"""))

# ---------------------------------------------------------------- 110 I1b
PAIRS.append(("""      check("[live] I1b: the why-not line bands it at 12 m projected vs 24 m now [live log]",
        lg110(count_log(W, "is centre=~20m vs bound=6m") == 1
          and count_log(W, "projected sep=~10m after delay=1.50s") == 1))""",
"""      check("[live] I1b (v112 EXACT METRES): the why-not line shows 12.00 m projected EXACTLY vs the 24.0 m instant BANDED to ~20m [live log]",
        lg110(count_log(W, "is centre=~20m vs bound=6m") == 1
          and count_log(W, "projected sep=12.00m after delay=1.50s") == 1))"""))

# ---------------------------------------------------------------- 111 A1c
PAIRS.append(("""        check(TAG .. "A1c: the line prints delay_caster=1.50s lead=0.50 and NO moving-caster fragment [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W, "delay_caster=1.50s lead=0.50") >= 1
              and count_log(W, "moving caster:") == 0)))""",
"""        check(TAG .. "A1c (v112 FOUR DIALS): the line prints all four dials and NO moving-caster fragment [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W, "delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=0.50") >= 1
              and count_log(W, "moving caster:") == 0)))"""))

# ---------------------------------------------------------------- 111 B1c
PAIRS.append(("""        check(TAG .. "B1c: the line names lead=1.00 and the moving-caster fragment [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W, "delay_caster=1.50s lead=1.00") >= 1
              and count_log(W, "moving caster: lead=1.00 of 1.50s") >= 1)))""",
"""        check(TAG .. "B1c (v112 FOUR DIALS): the line names caster_lead=1.00 and the moving-caster fragment [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W, "delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=1.00") >= 1
              and count_log(W, "moving caster: lead=1.00 of 1.50s") >= 1)))"""))

# ---------------------------------------------------------------- 111 B2b
PAIRS.append(("""        check(TAG .. "B2b: the why-not line bands the projection at 10 m against a 15 m instant band [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W, "projected sep=~10m after delay=1.50s") >= 1
              and count_log(W, "is centre=~15m vs bound=6m") >= 1)))""",
"""        check(TAG .. "B2b (v112 EXACT METRES): the why-not line shows the 10.00 m projection EXACTLY against the 16.0 m instant BANDED to ~15m [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W, "projected sep=10.00m after delay=1.50s") >= 1
              and count_log(W, "is centre=~15m vs bound=6m") >= 1)))"""))

# ---------------------------------------------------------------- 111 B2c
PAIRS.append(("""        check(TAG .. "B2c: the why-not line names lead=0.50 beside the caster velocity [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W, "delay_caster=1.50s lead=0.50") >= 1
              and count_log(W, "moving caster: lead=0.50 of 1.50s") >= 1)))""",
"""        check(TAG .. "B2c (v112 FOUR DIALS): the why-not line names all four dials beside the caster velocity [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W, "delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=0.50") >= 1
              and count_log(W, "moving caster: lead=0.50 of 1.50s") >= 1)))"""))

# ---------------------------------------------------------------- 111 D4b
PAIRS.append(("""        check(TAG .. "D4b: and the why-not band is the projected 10 m [live log]",
          lg111((TAG ~= "[live] ")
            or count_log(W4, "projected sep=~10m after delay=1.50s") >= 1))""",
"""        check(TAG .. "D4b (v112 EXACT METRES): and the why-not number is the projected 12.00 m, exact [live log]",
          lg111((TAG ~= "[live] ")
            or count_log(W4, "projected sep=12.00m after delay=1.50s") >= 1))"""))

# ---------------------------------------------------------------- 111 F1/F2 (REBASED)
PAIRS.append(("""        check(TAG .. "F1a: with the caster delay 1.5 the caster projects x=72.0 and FIRES at 2.0 m ("
          .. #WA.fires .. ")", #WA.fires == 1 and lg111((TAG ~= "[live] ")
            or (count_log(WA, "proj=(72.0, 200.0)") >= 1
              and count_log(WA, "centre=2.0m") >= 1
              and count_log(WA, "delay_caster=1.50s") >= 1)))
        check(TAG .. "F2a: with the caster delay 1.0 the caster projects x=68.0 - 4 m less - and still fires (6.0 m)",
          #WB.fires == 1 and lg111((TAG ~= "[live] ")
            or (count_log(WB, "proj=(68.0, 200.0)") >= 1
              and count_log(WB, "centre=6.0m") >= 1
              and count_log(WB, "delay_caster=1.00s") >= 1)))
        check(TAG .. "F2b: the ENEMY projection is IDENTICAL in both worlds - (74.0, 200.0) [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(WA, "proj=(74.0, 200.0)") >= 1 and count_log(WB, "proj=(74.0, 200.0)") >= 1)))
        check(TAG .. "F2c: only the CASTER moved (2.0 -> 6.0 separation), never the enemy term [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(WA, "centre=2.0m") >= 1 and count_log(WB, "centre=6.0m") >= 1)))""",
"""        -- REBASED v112: the enemy in this world CLOSES at 4 m/s, so its own
        -- lead matters now. Enemy 80 -> 80 - 4*0.45 = 78.20 in BOTH worlds;
        -- caster 72 (delay 1.5) -> 6.20 m, and 68 (delay 1.0) -> 10.20 m.
        -- Both are outside the 6 m pin; v111 fired the 2.0 m case.
        check(TAG .. "F1a (REBASED v112): caster 72.0 vs enemy 78.20 leaves 6.20 m - outside the pin, SILENT ("
          .. #WA.fires .. ")", #WA.fires == 0 and lg111((TAG ~= "[live] ")
            or (count_log(WA, "projected sep=6.20m") >= 1
              and count_log(WA, "delay_caster=1.50s") >= 1
              and count_log(WA, "enemy_lead=0.30") >= 1)))
        check(TAG .. "F2a (REBASED v112): shortening the caster delay 1.5 -> 1.0 moves the gap 6.20 -> 10.20 m, still SILENT",
          #WB.fires == 0 and lg111((TAG ~= "[live] ")
            or (count_log(WB, "projected sep=10.20m") >= 1
              and count_log(WB, "delay_caster=1.00s") >= 1)))
        check(TAG .. "F2b (REBASED v112): the ENEMY term is IDENTICAL in both worlds - it reads enemy_lead=0.30, not the caster delay",
          lg111((TAG ~= "[live] ")
            or (count_log(WA, "enemy v=(-4.0, 0.0) 4.0 m/s src=ordered") >= 1
              and count_log(WB, "enemy v=(-4.0, 0.0) 4.0 m/s src=ordered") >= 1)))
        check(TAG .. "F2c (REBASED v112): only the CASTER moved (6.20 -> 10.20 separation), never the enemy term [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(WA, "projected sep=6.20m") >= 1 and count_log(WB, "projected sep=10.20m") >= 1)))"""))

# ---------------------------------------------------------------- 111 G1b / G2b
PAIRS.append(("""        check(TAG .. "G1b: the re-check line prints the RE-PROJECTED 1.0 m AND lead=0.50 [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W1, "pre-cast re-check: still over an INFANTRY enemy") >= 1
              and count_log(W1, "projected centre=1.0m") >= 1
              and count_log(W1, "delay_caster=1.50s lead=0.50") >= 1)))""",
"""        check(TAG .. "G1b (v112 FOUR DIALS): the re-check line prints the RE-PROJECTED 1.0 m AND all four dials [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W1, "pre-cast re-check: still over an INFANTRY enemy") >= 1
              and count_log(W1, "projected centre=1.0m") >= 1
              and count_log(W1, "delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=0.50") >= 1)))"""))

PAIRS.append(("""        check(TAG .. "G2b: the skip line prints projected centre=34.0m and the same two dials [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W2, "SKIPPED: the drop lapsed before the cast") >= 1
              and count_log(W2, "projected centre=34.0m") >= 1
              and count_log(W2, "delay_caster=1.50s lead=0.50") >= 1)))""",
"""        check(TAG .. "G2b (v112 FOUR DIALS): the skip line prints projected centre=34.0m and the same four dials [live log]",
          lg111((TAG ~= "[live] ")
            or (count_log(W2, "SKIPPED: the drop lapsed before the cast") >= 1
              and count_log(W2, "projected centre=34.0m") >= 1
              and count_log(W2, "delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=0.50") >= 1)))"""))

for old, new in PAIRS:
    assert s.count(old) == 1, (s.count(old), old[:90])
    s = s.replace(old, new)

RUNS = "run_h109()\nrun_h110()\nrun_h111()\n"
i = s.rindex("\n" + RUNS)
SUMMARY = s[i + 1 + len(RUNS):]
assert SUMMARY.lstrip("\n").startswith('print("'), SUMMARY[:80]

sec = io.open(SEC, encoding="utf-8", newline="").read()
assert "\r" not in sec

body = s[:i].rstrip("\n")
out = (body + "\n\n" + sec.rstrip("\n") + "\n\n"
       + "run_h109()\nrun_h110()\nrun_h111()\nrun_h112()\n"
       + SUMMARY.lstrip("\n"))

io.open(DST, "w", encoding="utf-8", newline="\n").write(out)
print("superseded/re-based assertions:", len(PAIRS))
print("wrote", DST, len(out), "bytes")
