#!/usr/bin/env python3
"""Round 219 (2026-11-28, sign-off): the placed blasts (enemy_wander) hit MOST OF THE TARGET UNIT, standing cavalry
counts as a target, and the timing probe names the trigger families (live copy only).

FIELD (archive/logs/battle_20261128_r218_perf.txt, 280 s, 40 units): Brass Orb fired once per caster (t = 80 to 90 s,
'103 soldiers in the 12m blast (line 96)') and never again. From t = 185 s (13 s effect + 90 s recharge) one target
was free: Free Company Militia, standing, 38 m from our nearest unit, 110 of 120 men: about 94 soldiers under the
circle against a line of 96. Two Outrider units (60 and 46 riders) stood still and clear and were never candidates.

USER RULINGS 2026-11-28: "A, most of the unit" (the blast must cover most of the target unit as it is now), "yes" to
standing cavalry as a target, "yes" to the whole family.

1. THE COVER RULE (FOURTH.cover_need): a wanderer's target needs min(the density line, max(FOURTH.COVER_MIN_MEN 20,
   ceil(FOURTH.COVER_FRACTION 0.50 x the target unit's living soldiers))) enemy soldiers under the blast. The 50% and
   the 20 are Claude's numbers for the user's 'most of the unit' and 'a floor' (60% and 30 were named in chat: a
   12 m circle covers about 55% of the 60 Outriders of the battle and 26 of the 46, so those would never fire).
2. CAVALRY (FOURTH.ww_map): the wanderers also take enemy cavalry (live unit_class cav..., at least BLOB_MIN_MEN
   riders, not flying). Its depth comes from the GENERATED FOURTH.CAV_SPACING (gen_blob_tables.cav_spacing_table,
   183 units). Every other blob family keeps the infantry list.
3. LIVE ONLY: FOURTH.perf_trig times every evaluator call by trigger family, one 'PERF TRIG 10s:' line per 10 PERF
   lines (the 12 most expensive families: ms / calls).
Backups: docs/backups/round219/pre219_{live,ann}.lua."""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_blob_tables as G  # noqa: E402

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round219"

BOTH = [
    ("cav table", "FOURTH.load_blob_tables()\n\n", "FOURTH.load_blob_tables()\n@CAV@\n"),
    ("shape class",
     "\tlocal inf = (cls:sub(1, 3) == \"inf\") and not (t ~= nil and FOURTH.class_keys.large[t] == true)\n",
     "\tlocal inf = (cls:sub(1, 3) == \"inf\") and not (t ~= nil and FOURTH.class_keys.large[t] == true)\n"
     "\tlocal cav = (cls:sub(1, 3) == \"cav\")   -- ROUND 219: cavalry, a target of the placed blasts\n"),
    ("shape depth",
     "\telse\n\t\tdepth = w\n\tend\n\tlocal r = math.rad(b)\n",
     "\telseif cav and t ~= nil and FOURTH.CAV_SPACING[t] ~= nil then\n"
     "\t\t-- ROUND 219: ranks x the game's own mounted spacing (a cavalry line is far shallower than it is wide)\n"
     "\t\tlocal files = math.max(1, math.floor(w / FOURTH.CAV_SPACING[t][1] + 0.5))\n"
     "\t\tdepth = math.ceil(men / files) * FOURTH.CAV_SPACING[t][2]\n"
     "\telse\n\t\tdepth = w\n\tend\n\tlocal r = math.rad(b)\n"),
    ("shape field", "men = men, inf = inf }\n", "men = men, inf = inf, cav = cav }\n"),
    ("map table",
     "\tlocal m = { ours = {}, enemies = {}, large = {}, all = {}, alliance = (alliance ~= nil) }\n",
     "\tlocal m = { ours = {}, enemies = {}, large = {}, all = {}, cav = {}, alliance = (alliance ~= nil) }\n"),
    ("map cav",
     "\t\t\t\t\t\tif s ~= nil then m.all[#m.all + 1] = s end   -- ROUND 156\n",
     "\t\t\t\t\t\tif s ~= nil then m.all[#m.all + 1] = s end   -- ROUND 156\n"
     "\t\t\t\t\t\tif s ~= nil and s.cav and s.men >= FOURTH.BLOB_MIN_MEN and not (ok_f and fly == true) then\n"
     "\t\t\t\t\t\t\tm.cav[#m.cav + 1] = s   -- ROUND 219\n"
     "\t\t\t\t\t\tend\n"),
    ("value fn",
     "function FOURTH.ww_wander_value(unit, e, m, row)\n",
     "-- ============================================================================\n"
     "-- ROUND 219 (user rulings 2026-11-28: \"A, most of the unit\", cavalry \"yes\", the family \"yes\").\n"
     "-- THE COVER RULE: the density line (half a packed block: 96 soldiers for a 12 m blast) let only a full, fresh\n"
     "-- unit qualify (field: Brass Orb held on a 110-man unit, about 94 under the circle). A wanderer's target now\n"
     "-- needs the smaller of that line and COVER_FRACTION of the target unit's LIVING soldiers, never fewer than\n"
     "-- COVER_MIN_MEN (both numbers are Claude's reading of 'most of the unit' and 'a floor').\n"
     "-- CAVALRY: the wanderers read FOURTH.ww_map(m): the infantry blocks plus the enemy cavalry (m.cav).\n"
     "-- ============================================================================\n"
     "FOURTH.COVER_FRACTION = 0.50\n"
     "FOURTH.COVER_MIN_MEN = 20\n"
     "function FOURTH.cover_need(line, men)\n"
     "\tif type(men) ~= \"number\" then return line end\n"
     "\treturn math.min(line, math.max(FOURTH.COVER_MIN_MEN, math.ceil(FOURTH.COVER_FRACTION * men)))\n"
     "end\n"
     "-- the target unit's OWN soldiers under a blast of radius r placed on its centre: a 16 x 8 grid over its\n"
     "-- rectangle, in the unit's own frame, so the answer does not change with the unit's bearing (the 19-point\n"
     "-- blast sample does: 44 to 84 soldiers for the same 120 men on a 10 m deep line)\n"
     "function FOURTH.cover_own(e, r)\n"
     "\tif type(e.men) ~= \"number\" or type(e.w) ~= \"number\" or type(e.d) ~= \"number\" then return 0 end\n"
     "\tlocal hit = 0\n"
     "\tfor i = 1, 16 do\n"
     "\t\tlocal a = ((i - 0.5) / 16 - 0.5) * e.w\n"
     "\t\tfor j = 1, 8 do\n"
     "\t\t\tlocal c = ((j - 0.5) / 8 - 0.5) * e.d\n"
     "\t\t\tif a * a + c * c <= r * r then hit = hit + 1 end\n"
     "\t\tend\n"
     "\tend\n"
     "\treturn e.men * hit / 128\n"
     "end\n"
     "function FOURTH.ww_map(m)\n"
     "\tif m.wv ~= nil then return m.wv end\n"
     "\tlocal list = {}\n"
     "\tfor i = 1, #m.enemies do list[#list + 1] = m.enemies[i] end\n"
     "\tfor i = 1, #(m.cav or {}) do list[#list + 1] = m.cav[i] end\n"
     "\tm.wv = { ours = m.ours, enemies = list, large = m.large, all = m.all, alliance = m.alliance }\n"
     "\tm.wv.wv = m.wv\n"
     "\treturn m.wv\n"
     "end\n"
     "function FOURTH.ww_wander_value(unit, e, m, row)\n"
     "\tm = FOURTH.ww_map(m)   -- ROUND 219: infantry and cavalry\n"),
    ("value need",
     "\tif sc < FOURTH.blob_need(row.r) or not FOURTH.blob_trash_ok(e, sc, row.r) then return nil end\n"
     "\treturn FOURTH.blob_value(e, m, row.r, nil), sc\n",
     "\t-- ROUND 219: the old density line, OR most of the target unit's own soldiers under the blast\n"
     "\tlocal own = FOURTH.cover_own(e, row.r)\n"
     "\tif sc < FOURTH.blob_need(row.r) and own < FOURTH.cover_need(FOURTH.blob_need(row.r), e.men) then return nil end\n"
     "\tif not FOURTH.blob_trash_ok(e, sc, row.r) then return nil end\n"
     "\treturn FOURTH.blob_value(e, m, row.r, nil), math.max(sc, own)\n"),
    ("evaluator list",
     "\tlocal m = FOURTH.blob_map(false)\n\tlocal best, bv, bs = nil, nil, nil\n\tfor i = 1, #m.enemies do\n"
     "\t\tlocal e = m.enemies[i]\n\t\tlocal v, sc = FOURTH.ww_wander_value(unit, e, m, row)\n",
     "\tlocal m = FOURTH.ww_map(FOURTH.blob_map(false))   -- ROUND 219: infantry and cavalry\n"
     "\tlocal best, bv, bs = nil, nil, nil\n\tfor i = 1, #m.enemies do\n"
     "\t\tlocal e = m.enemies[i]\n\t\tlocal v, sc = FOURTH.ww_wander_value(unit, e, m, row)\n"),
    ("recheck list",
     "\tlocal list = (row.kind == 2 or row.kind == 3 or row.kind == 6) and m.enemies or m.all\n",
     "\tlocal list = (row.kind == 2 or row.kind == 3 or row.kind == 6) and FOURTH.ww_map(m).enemies or m.all   -- ROUND 219\n"),
]

LIVE_ONLY = [
    ("reason",
     "\t\tFOURTH.blob_need(row.r), safe, (d ~= nil)",
     "\t\tFOURTH.cover_need(FOURTH.blob_need(row.r), best.men), safe, (d ~= nil)"),
    ("timer fn",
     "function FOURTH.perf_end_ui(t0)\n",
     "-- ROUND 219: the time of every evaluator call, by trigger family. One 'PERF TRIG 10s:' line per 10 PERF lines.\n"
     "FOURTH.perf_t = {}\n"
     "FOURTH.perf_t_lines = 0\n"
     "function FOURTH.perf_trig(name, t0)\n"
     "\tif t0 == nil then return end\n"
     "\tlocal row = FOURTH.perf_t[name]\n"
     "\tif row == nil then row = { 0, 0, tostring(name) }; FOURTH.perf_t[name] = row end\n"
     "\trow[1] = row[1] + (os.clock() - t0) * 1000\n"
     "\trow[2] = row[2] + 1\n"
     "end\n"
     "function FOURTH.perf_trig_line()\n"
     "\tFOURTH.perf_t_lines = FOURTH.perf_t_lines + 1\n"
     "\tif FOURTH.perf_t_lines < 10 then return end\n"
     "\tFOURTH.perf_t_lines = 0\n"
     "\tlocal rows = {}\n"
     "\tfor _, row in pairs(FOURTH.perf_t) do rows[#rows + 1] = row end\n"
     "\ttable.sort(rows, function(a, b) if a[1] ~= b[1] then return a[1] > b[1] end return a[3] < b[3] end)\n"
     "\tlocal bits, total = {}, 0\n"
     "\tfor i = 1, #rows do\n"
     "\t\ttotal = total + rows[i][1]\n"
     "\t\tif i <= 12 then bits[#bits + 1] = string.format(\"%s %.1f/%d\", rows[i][3], rows[i][1], rows[i][2]) end\n"
     "\tend\n"
     "\tFOURTH.perf_t = {}\n"
     "\tlog(string.format(\"PERF TRIG 10s: all evaluators %.1f ms | \", total) .. table.concat(bits, \" | \"))\n"
     "end\n"
     "function FOURTH.perf_end_ui(t0)\n"),
    ("timer line",
     "\tcast_gate.log_ms, cast_gate.log_n = 0, 0\n",
     "\tcast_gate.log_ms, cast_gate.log_n = 0, 0\n"
     "\tFOURTH.perf_trig_line()   -- ROUND 219\n"),
    ("timer use",
     "\t\t\t\t\tFOURTH.entry_reset(ability, unit)   -- ROUND 198: the slot reset, shared with the fast pass\n"
     "\t\t\t\t\tlocal reason = ability.evaluate(unit, routing)\n",
     "\t\t\t\t\tFOURTH.entry_reset(ability, unit)   -- ROUND 198: the slot reset, shared with the fast pass\n"
     "\t\t\t\t\tlocal perf_e0 = FOURTH.perf_now()   -- ROUND 219: the evaluator's time, by trigger family\n"
     "\t\t\t\t\tlocal reason = ability.evaluate(unit, routing)\n"
     "\t\t\t\t\tFOURTH.perf_trig(ability.trigger, perf_e0)\n"),
]


def patch(path, live):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 219" not in s, "already patched: " + path
    cav = G.lua_block_cav(G.cav_spacing_table())
    for what, a, b in BOTH + (LIVE_ONLY if live else []):
        assert s.count(a) == 1, (what, s.count(a), path)
        s = s.replace(a, b.replace("@CAV@", cav))
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre219_live.lua"), (ANN, "pre219_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
        elif "--again" in sys.argv:
            shutil.copy2(dst, src)
    patch(LIVE, True)
    patch(ANN, False)


if __name__ == "__main__":
    main()
