# -*- coding: utf-8 -*-
"""Build harness107.lua from harness106.lua.

1. copies the 106 harness into the new release dir;
2. moves every PIN the round-107 table growth touches (documented per line
   below) - comments describing older rounds are left alone;
3. adds the air_drop_on_infantry tooltip wording to the harness-93 allowed map;
4. rewrites the FIVE worlds that pinned "two abilities on one unit fire in the
   same poll" so they assert the NEW per-unit serialisation (first fires,
   second waits, then fires) - that behaviour change is the round's item 4;
5. appends h107_section.lua in place of the final run_h106() call.
"""
import hashlib
import os

REL106 = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261018_bombardment_harness106"
REL107 = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261019_bombardment_harness107"
SRC106 = os.path.join(REL106, "harness106.lua")
DST107 = os.path.join(REL107, "harness107.lua")
SECTION = os.path.join(REL107, "h107_section.lua")


def read(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8")


def write(p, s):
    data = s.encode("utf-8")
    assert b"\r" not in data
    with open(p, "wb") as f:
        f.write(data)


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, "count %d (want %d): %r" % (c, n, old[:120])
    return s.replace(old, new)


s = read(SRC106)

# ---------------------------------------------------------------- numeric pins
# every comparison against the grown-table sizes (comments untouched)
s = rep(s, "a = (it == 1350)", "a = (it == 1376)")
s = rep(s, "== 675", "== 688", s.count("== 675"))
s = rep(s, "== 721", "== 741", s.count("== 721"))
s = rep(s, "entries = 675, keys = 721", "entries = 688, keys = 741", 3)
s = rep(s, "== (EXP.sum and 193 or 96)", "== (EXP.sum and 205 or 96)")
s = rep(s, 'cp97(s, "\\t\\trange_real = ") == 193', 'cp97(s, "\\t\\trange_real = ") == 205')
s = rep(s, "RED_MODE and 0 or 154", "RED_MODE and 0 or 161")
s = rep(s, "nkeys == 170", "nkeys == 172")

# the label strings that print the pin (so a failure reads the truth)
s = rep(s, '"A4a: with no information the badge paths walked the FULL 675-entry table ("',
        '"A4a: with no information the badge paths walked the FULL 688-entry table ("')
s = rep(s, '"A4b: 675 abilities per pass, no shortcut set (per pass = "'
        if '"A4b: 675 abilities per pass, no shortcut set (per pass = "' in s
        else '"A4b: 675 abilities per pass, no shortened set (per pass = "',
        '"A4b: 688 abilities per pass, no shortened set (per pass = "')
s = rep(s, '", want 675 - the FULL 675-entry table after round h105)"',
        '", want 688 - the FULL 688-entry table after round h105)"')
s = rep(s, '"S1c: the abilities table has 675 entries ("', '"S1c: the abilities table has 688 entries ("', 1)
s = rep(s, '"M6c: the abilities table has 675 entries ("', '"M6c: the abilities table has 688 entries ("')
s = rep(s, '"N13d: the abilities table has 675 entries ("', '"N13d: the abilities table has 688 entries ("')
s = rep(s, '"H68: the abilities table is reachable ("', '"H68: the abilities table is reachable ("')
s = rep(s, '"H68: the static key->marker map has all 721 keys (marker_by_key, "',
        '"H68: the static key->marker map has all 741 keys (marker_by_key, "')
s = rep(s, '"S1d: the static key->marker map has 721 keys ("', '"S1d: the static key->marker map has 741 keys ("')
s = rep(s, '"M6d: the static key->marker map has 721 keys ("', '"M6d: the static key->marker map has 741 keys ("')
s = rep(s, '"N13e: the static key->marker map has 721 keys ("', '"N13e: the static key->marker map has 741 keys ("')
s = rep(s, '": the grown table is 675 entries (each with a badge field)"',
        '": the grown table is 688 entries (each with a badge field)"', 2)
s = rep(s, '": the table stays 675 entries / 675 badges"',
        '": the table stays 688 entries / 688 badges"', 3)
s = rep(s, '": the table stays 675 entries / 675 badges (harness 104: 41 ally_range_real fields)"',
        '": the table stays 688 entries / 688 badges (harness 104: 41 ally_range_real fields)"')
s = rep(s, '": the ability table is UNCHANGED (675 entries)"', '": the ability table is UNCHANGED (688 entries)"')
s = rep(s, '": the whole 675-entry table and the 70% rule are untouched"',
        '": the whole 688-entry table and the 70% rule are untouched"')
s = rep(s, '": the table is still 675 entries (each with a badge field)"',
        '": the table is still 688 entries (each with a badge field)"')
s = rep(s, '": every Class-A entry carries its REAL range (range_real x193)"',
        '": every Class-A entry carries its REAL range (range_real x205)"', 1)
s = rep(s, '": the charge-gate table exists and lists all 154 multi-USE keys ("',
        '": the charge-gate table exists and lists all 161 multi-USE keys ("', 1)
s = rep(s, '": the cast-gate table exists and lists all 170 wind-up keys ("',
        '": the cast-gate table exists and lists all 172 wind-up keys ("', 1)
s = rep(s, '", table of 675 after round h105)"', '", table of 688 after round h105)"', 1)
s = rep(s, 'check("D1a: the WHOLE ABILITIES table was captured (" .. total .. " entries, want 642)"',
        'check("D1a: the WHOLE ABILITIES table was captured (" .. total .. " entries, want 688)"')
s = rep(s, '" entries match (want 642), total " .. total\n      .. " (want 642)"',
        '" entries match (want 688), total " .. total\n      .. " (want 688)"')

# the h106 0x pin: melee_skip_commanders now carries THREE entries
s = rep(s, 'check("0x " .. nm .. ": TWO entries carry melee_skip_commanders (Soulfire + Arachneruption)",\n'
           '        cp106(s2, "trigger = \\"melee_skip_commanders\\"") == 2)',
        'check("0x " .. nm .. ": THREE entries carry melee_skip_commanders (Soulfire, Arachneruption, Call of Tor)",\n'
        '        cp106(s2, "trigger = \\"melee_skip_commanders\\"") == 3)')

# ------------------------------------------------- the harness-93 wording map
tip_anchor = ('    enemy_ground_melee_infantry = "When armed, fires on the closest infantry unit in range that is fighting in melee",\n')
s = rep(s, tip_anchor, tip_anchor +
        '    air_drop_on_infantry = "When armed, fires when this unit is over an infantry unit in range, airborne where the ability requires it",\n')

# ------------------------------------- B3: one unit, two markers (world 66)
old_b3 = '''    local before = #W.fires
    reset_poll_iters()
    polln(W, 1)
    local keys = {}
    for j = before + 1, #W.fires do keys[W.fires[j].key] = true end
    check(TAG .. "B3b: BOTH abilities fired independently on the same poll (" .. fire_keys(W) .. ")",
      (#W.fires - before) == 2 and keys[ONS] == true and keys[FS_MAIN] == true)
    check(TAG .. "B3c: that poll still evaluated exactly TWO abilities (" .. POLL_ITERS .. ", want 2)",
      POLL_ITERS == 2)'''
new_b3 = '''    local before = #W.fires
    reset_poll_iters()
    polln(W, 1)
    -- ROUND 107: one special ability in flight per unit. The FIRST ready
    -- ability fires; the second is held by the per-unit window and fires only
    -- after it closes. This world used to pin "both on the same poll" - that
    -- is exactly the behaviour the Moondial / Wraith Storm fix removes.
    check(TAG .. "B3b: the FIRST ready ability fires, the second is held by the per-unit window ("
      .. fire_keys(W) .. ")", (#W.fires - before) == 1)
    local t1 = (#W.fires > before) and W.fires[before + 1].tick or -1
    check(TAG .. "B3c: that first poll still evaluated exactly TWO abilities (" .. POLL_ITERS .. ", want 2)",
      POLL_ITERS == 2)
    polln(W, 20)
    local seen, first_at = {}, {}
    for j = before + 1, #W.fires do
      local k = W.fires[j].key
      if seen[k] == nil then seen[k] = true; first_at[k] = W.fires[j].tick end
    end
    check(TAG .. "B3b2: after the window BOTH abilities have fired, the second no sooner than one full window (10 polls) after the first ("
      .. fire_keys(W) .. ")", seen[ONS] == true and seen[FS_MAIN] == true
      and first_at[ONS] ~= nil and first_at[FS_MAIN] ~= nil
      and math.abs(first_at[ONS] - first_at[FS_MAIN]) >= 10)'''
s = rep(s, old_b3, new_b3)

# ------------------------------------- N3: nested guard, two markers (world 90)
old_n3 = '''      polln(W, 1)                                     -- both triggers met: two attempts, two independent stamps
      local g = guard_tbl and guard_tbl[2001]
      c = (g ~= nil and g[M_FS] ~= nil and g[M_HOS] ~= nil and guard_tbl ~= nil and count_keys(guard_tbl) == 1)
      check(TAG .. "N3c: BOTH markers stamped independently inside ONE unit slot (guard[2001] has foe_seeker AND hammer_of_sigmar)", c)
      d = (#W.fires == 2)
      check(TAG .. "N3d: both armed abilities FIRE on the trigger tick (" .. fire_detail(W) .. ")", d)'''
new_n3 = '''      polln(W, 1)                                     -- both triggers met: ONE attempt, one stamp (round 107)
      local g = guard_tbl and guard_tbl[2001]
      c = (g ~= nil and g[M_FS] ~= nil and g[M_HOS] == nil and guard_tbl ~= nil and count_keys(guard_tbl) == 1)
      check(TAG .. "N3c: the FIRST marker is stamped inside ONE unit slot; the second waits for the per-unit window", c)
      d = (#W.fires == 1)
      check(TAG .. "N3d: only the FIRST fires on the trigger tick (" .. fire_detail(W) .. ")", d)
      polln(W, 20)
      local g2 = guard_tbl and guard_tbl[2001]
      local seen = {}
      for i = 1, #W.fires do seen[W.fires[i].key] = true end
      local e = (g2 ~= nil and g2[M_HOS] ~= nil and seen[FS_MAIN] == true and seen[HOS_MAIN] == true)
      check(TAG .. "N3e: after the window the SECOND marker is stamped too and both fired (" .. fire_detail(W) .. ")", e)
      d = d and e'''
s = rep(s, old_n3, new_n3)

# ------------------------------------- C6: the batch world (world 82)
old_c6 = '''    local keys = {}
    for i = 1, #W.fires do keys[W.fires[i].key] = (keys[W.fires[i].key] or 0) + 1 end
    local two = (#W.fires == 2 and keys[KEY_OF[BATCH[1][1]]] == 1 and keys[KEY_OF[BATCH[2][1]]] == 1)
    check(TAG .. "C6f: ONLY the two armed abilities fired (fires: " .. fire_detail(W) .. ")", two)
    polln(W, 8)
    local four = (#W.fires == 4)
    check(TAG .. "C6g: both fire again in the next window, the four unarmed stay silent (fires " .. #W.fires
      .. ", want 4)", four)'''
new_c6 = '''    -- ROUND 107: the per-unit serialisation window means the two armed
    -- abilities on ONE unit fire IN SEQUENCE, not together.
    local two = false
    if #W.fires == 1 then
      local k = W.fires[1].key
      two = (k == KEY_OF[BATCH[1][1]] or k == KEY_OF[BATCH[2][1]])
    end
    check(TAG .. "C6f: the FIRST armed ability fires (the second waits for the per-unit window) (fires: "
      .. fire_detail(W) .. ")", two)
    polln(W, 20)
    local seen, distinct = {}, 0
    for i = 1, #W.fires do
      if seen[W.fires[i].key] == nil then seen[W.fires[i].key] = true; distinct = distinct + 1 end
    end
    local four = (seen[KEY_OF[BATCH[1][1]]] == true and seen[KEY_OF[BATCH[2][1]]] == true and distinct == 2)
    check(TAG .. "C6g: by the end BOTH armed abilities have fired and no unarmed key ever did (fires "
      .. #W.fires .. ", distinct " .. distinct .. ")", four)'''
s = rep(s, old_c6, new_c6)


# ---- the cumulative suite-boundary counts (moved by this round's added
# checks in the 66/90/82 sections; the values are the green run's own totals)
for _old, _new in (
    ('local H70_GREEN_TOTAL = 882', 'local H70_GREEN_TOTAL = 886'),
    ('local H71_GREEN_TOTAL = 1064', 'local H71_GREEN_TOTAL = 1068'),
    ('local H72_GREEN_TOTAL = 1120', 'local H72_GREEN_TOTAL = 1124'),
    ('local H73_GREEN_TOTAL = 1194', 'local H73_GREEN_TOTAL = 1198'),
    ('local H74_GREEN_TOTAL = 1247', 'local H74_GREEN_TOTAL = 1251'),
    ('local H75_GREEN_TOTAL = 1295', 'local H75_GREEN_TOTAL = 1299'),
    ('local H76_GREEN_TOTAL = 1346', 'local H76_GREEN_TOTAL = 1350'),
    ('local H77_GREEN_TOTAL = 1401', 'local H77_GREEN_TOTAL = 1405'),
    ('local H78_GREEN_TOTAL = 1448', 'local H78_GREEN_TOTAL = 1452'),
    ('local H79_SUITE_CHECKS = 1483', 'local H79_SUITE_CHECKS = 1487'),
    ('local H80_SUITE_CHECKS = 1591', 'local H80_SUITE_CHECKS = 1595'),
    ('local H81_SUITE_CHECKS = 1719', 'local H81_SUITE_CHECKS = 1723'),
    ('local H82_SUITE_CHECKS = 1860', 'local H82_SUITE_CHECKS = 1864'),
    ('checks == 1961)', 'checks == 1965)'),
    ('checks == 2038)', 'checks == 2042)'),
    ('checks == 2105)', 'checks == 2109)'),
    ('checks == 2189)', 'checks == 2193)'),
    ('", want 3441)", pre102 == 3441', '", want 3445)", pre102 == 3445'),
    ('", want 3524)", pre103 == 3524', '", want 3528)", pre103 == 3528'),
    ('", want 3568)", pre104 == 3568', '", want 3572)", pre104 == 3572'),
    ('", want 3649)", pre105 == 3649', '", want 3653)", pre105 == 3653'),
    ('", want 3701)", pre106 == 3701', '", want 3705)", pre106 == 3705'),
):
    s = rep(s, _old, _new)


# ---- the env pair this round reads (was H106_*)
s = rep(s, '-- HARNESS 101 (this round): the env pair is now H106_LIVE / H106_ANN.\nlocal LIVE = os.getenv("H106_LIVE")',
        '-- HARNESS 107 (this round): the env pair is now H107_LIVE / H107_ANN.\nlocal LIVE = os.getenv("H107_LIVE")')
s = rep(s, 'local ANN  = os.getenv("H106_ANN")', 'local ANN  = os.getenv("H107_ANN")')
s = rep(s, 'local RED_MODE = (os.getenv("H106_LIVE") ~= nil) or (os.getenv("H106_ANN") ~= nil)',
        'local RED_MODE = (os.getenv("H107_LIVE") ~= nil) or (os.getenv("H107_ANN") ~= nil)')

# ------------------------------------- append the round section
tail = "\nrun_h106()\n\ncheck(\"ZERO search calls"
assert s.count(tail) == 1
s = s.replace(tail, "\nrun_h106()\n\n" + read(SECTION) + "\ncheck(\"ZERO search calls")

os.makedirs(REL107, exist_ok=True)
write(DST107, s)
print("harness107.lua", len(s), "bytes", hashlib.md5(s.encode("utf-8")).hexdigest())
