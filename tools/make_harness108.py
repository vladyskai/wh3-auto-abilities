# -*- coding: utf-8 -*-
"""Build harness108.lua from harness107.lua.

1. copies the 107 harness into the round-108 release dir;
2. moves every PIN the round-108 table growth touches (689 entries, 742 keys,
   171 cast-gate keys, 162 charge-gate rows, the +2-entry bootstrap walk) and
   the labels that print them;
3. rewrites the air-drop worlds whose distances the 1 m bound changes (A1, A5,
   A8, A9, A10, S2, S3) so they still test the same rule at 1 m;
4. updates the h107 section's own constant / entry-count assertions;
5. appends h108_section.lua in place of the final run_h107() call.
"""
import os

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
REL107 = os.path.join(ROOT, "mod_source", "releases", "20261019_bombardment_harness107")
REL108 = os.path.join(ROOT, "mod_source", "releases", "20261020_airdrops_wlr_harness108")
SRC = os.path.join(REL107, "harness107.lua")
DST = os.path.join(REL108, "harness108.lua")
SECTION = os.path.join(REL108, "h108_section.lua")


def read(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8")


def write(p, s):
    data = s.encode("utf-8")
    assert b"\r" not in data
    with open(p, "wb") as f:
        f.write(data)


def rep(s, old, new, n):
    c = s.count(old)
    assert c == n, "count %d (want %d): %r" % (c, n, old[:120])
    return s.replace(old, new)


os.makedirs(REL108, exist_ok=True)
s = read(SRC)

# ---------------------------------------------------------------- numeric pins
s = rep(s, "== 688", "== 689", s.count("== 688"))
s = rep(s, "== 741", "== 742", s.count("== 741"))
s = rep(s, "a = (it == 1376)", "a = (it == 1378)", 1)
s = rep(s, "RED_MODE and 0 or 161", "RED_MODE and 0 or 162", 1)
s = rep(s, "nkeys == 172", "nkeys == 173", 1)
s = rep(s, "lists all 172 wind-up keys", "lists all 173 wind-up keys", 1)

# the label strings that print the pin (so a failure reads the truth)
s = rep(s, "the FULL 688-entry table", "the FULL 689-entry table", 2)
s = rep(s, "688 abilities per pass", "689 abilities per pass", 1)
s = rep(s, "the abilities table has 688 entries", "the abilities table has 689 entries", 3)
s = rep(s, "table of 688 after round h105", "table of 689 after round h105", 1)
s = rep(s, "has all 741 keys", "has all 742 keys", 1)
s = rep(s, "the static key->marker map has 741 keys", "the static key->marker map has 742 keys", 3)

# ------------------------------------------------- h107 section: entry counts
s = rep(s,
        '"0x " .. nm .. ": THREE entries carry melee_skip_commanders (Soulfire, Arachneruption, Call of Tor)",\n'
        '        cp106(s2, "trigger = \\"melee_skip_commanders\\"") == 3)',
        '"0x " .. nm .. ": FOUR entries carry melee_skip_commanders (Soulfire, Arachneruption, Call of Tor, Warp Lightning Rod)",\n'
        '        cp106(s2, "trigger = \\"melee_skip_commanders\\"") == 4)', 1)
s = rep(s,
        '"0y " .. nm .. ": THREE entries carry melee_skip_commanders (Soulfire, Arachneruption, Call of Tor)",\n'
        '        cp107(s2, "trigger = \\"melee_skip_commanders\\"") == 3)',
        '"0y " .. nm .. ": FOUR entries carry melee_skip_commanders (Soulfire, Arachneruption, Call of Tor, Warp Lightning Rod)",\n'
        '        cp107(s2, "trigger = \\"melee_skip_commanders\\"") == 4)', 1)

# the 0y bound check: 7 m is gone; the family bypasses the 70% map at 1 m
s = rep(s,
        '      check("0y " .. nm .. ": the 10 m rows map through the NEW 70% constant (10 -> 7)",\n'
        '        raw_find(s2, "FOURTH.ENEMY_CAST_R10  = 7", 1, true) ~= nil\n'
        '        and raw_find(s2, "[10]  = FOURTH.ENEMY_CAST_R10,", 1, true) ~= nil\n'
        '        and raw_find(s2, "FOURTH.AIR_DROP_BOUND_M = 7", 1, true) ~= nil)',
        '      check("0y " .. nm .. ": ROUND 108 - the air-drop bound is the 1 m user constant, NOT the 70% map (10 -> 7)",\n'
        '        raw_find(s2, "FOURTH.ENEMY_CAST_R10  = 7", 1, true) ~= nil\n'
        '        and raw_find(s2, "[10]  = FOURTH.ENEMY_CAST_R10,", 1, true) ~= nil\n'
        '        and raw_find(s2, "FOURTH.AIR_DROP_BOUND_M = 1", 1, true) ~= nil\n'
        '        and raw_find(s2, "FOURTH.AIR_DROP_BOUND_M = 7", 1, true) == nil\n'
        '        and raw_find(s2, "if ability.evaluate == FOURTH.evaluate_air_drop_on_infantry then", 1, true) ~= nil)', 1)

# the h107 header comment: A5 is now a 1 m silence case
s = rep(s, "--     A5 silent when the infantry unit is OUTSIDE the 70% bound (8 m > 7 m);",
        "--     A5 silent when the infantry unit is OUTSIDE the 1 m bound (3 m > 1 m);", 1)
s = rep(s, "--     A1 fires on an INFANTRY enemy under a FLYING caster, and the cast is on",
        "--     A1 fires on an INFANTRY enemy 0.4 m from a FLYING caster (inside the 1 m\n"
        "--        user bound), and the cast is on", 1)

# ------------------------------------------------- the air-drop world distances
WORLDS = [
    ("{ melee = false, dist_by_target = { [11710] = 2.0 } }", "{ melee = false, dist_by_target = { [11710] = 0.4 } }", "A1"),
    ("{ melee = false, dist_by_target = { [11711] = 2.0 } }", "{ melee = false, dist_by_target = { [11711] = 0.5 } }", "A2"),
    ("{ melee = false, dist_by_target = { [11715] = 2.0 } }", "{ melee = false, dist_by_target = { [11715] = 0.5 } }", "A6"),
    ("{ melee = false, dist_by_target = { [11714] = 8.0 } }", "{ melee = false, dist_by_target = { [11714] = 3.0 } }", "A5"),
    ("{ owns = { SPH }, melee = false, dist_by_target = { [11717] = 3.0 } }", "{ owns = { SPH }, melee = false, dist_by_target = { [11717] = 0.5 } }", "A8"),
    ("{ owns = { SEAR }, melee = false, dist_by_target = { [11718] = 3.0 } }", "{ owns = { SEAR }, melee = false, dist_by_target = { [11718] = 0.5 } }", "A9"),
    ("{ owns = { SKYJ }, melee = false, dist_by_target = { [11720] = 2.0 } }", "{ owns = { SKYJ }, melee = false, dist_by_target = { [11720] = 0.5 } }", "A10"),
    ("{ owns = { DFA }, melee = false, dist_by_target = { [11734] = 2.0 } }", "{ owns = { DFA }, melee = false, dist_by_target = { [11734] = 0.5 } }", "S2"),
    ("{ name = \"air_one\", uid = uid1, owns = { DFA }, melee = false, dist_by_target = { [11737] = 2.0 } }",
     "{ name = \"air_one\", uid = uid1, owns = { DFA }, melee = false, dist_by_target = { [11737] = 0.5 } }", "S3a"),
    ("{ name = \"air_two\", uid = uid2, owns = { DFA }, melee = false, dist_by_target = { [11737] = 2.0 } }",
     "{ name = \"air_two\", uid = uid2, owns = { DFA }, melee = false, dist_by_target = { [11737] = 0.5 } }", "S3b"),
]
for old, new, tag in WORLDS:
    s = rep(s, old, new, 1)

s = rep(s, "-- A5: infantry OUTSIDE the 70% bound (8 m > 7 m) -> SILENT.",
        "-- A5: infantry OUTSIDE the 1 m user bound (3 m > 1 m) -> SILENT.", 1)
s = rep(s, 'check(TAG .. "A5a: 8 m is outside the 7 m bound - no fire (" .. #W.fires .. ")", #W.fires == 0)',
        'check(TAG .. "A5a: 3 m is outside the 1 m bound - no fire (" .. #W.fires .. ")", #W.fires == 0)', 1)

# ---------------------------------------------------------------- the append
s = rep(s, "entries = 688, keys = 741", "entries = 689, keys = 742", 3)

assert s.rstrip().endswith("end") or True
tail_marker = "\nrun_h107()\n"
assert s.count(tail_marker) == 1, s.count(tail_marker)
section = read(SECTION)
s = s.replace(tail_marker, "\n" + section)

write(DST, s)
print("wrote", DST, os.path.getsize(DST), "bytes")
