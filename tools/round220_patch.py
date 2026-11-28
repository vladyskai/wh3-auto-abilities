#!/usr/bin/env python3
"""Round 220 (2026-11-28, sign-off): a PLACED effect does not wait for its caster, and three speed fixes for the polls.

FIELD (archive/logs/battle_20261128_r219_perf.txt, 291 s, 40 units, 37 active abilities):
- The user cast Brass Orb by hand with a Warlock Master at t = 62 s: the unit kept moving 10 m every 2 s through the
  cast. Brass Orb has a cast animation (wind_up_stance cast_forward_medium), the SAME entry as Amber Bow, which stopped
  Markus Wulfhart. So the animation does not decide (round 168's assumption). What separates the cases seen: the
  caster stops when he SHOOTS A PROJECTILE, not when the effect is PLACED at the target.
- The evaluators cost 61 ms of every second: enemy_wander 23.7 (2.4 ms per call), enemy_blob 11.5 (1.2 ms per call),
  melee_vs_large 6.3, enemy_single_drain 4.6, about 15 for all the others.

USER RULINGS 2026-11-28: 'Yes' to all placed ones. 'No' to protecting the caster of a placed blast. 'build them'.

1. FOURTH.ANIM_TEXT regenerated (tools/gen_anim_keys.py): a key with a vortex and neither a projectile nor a
   bombardment leaves the set. Those entries fire on the move.
2. FOURTH.locked_now(ui_id, ability): the poll does not call the evaluator while the mod itself knows the cast cannot
   go out: the ability's own wind-up is resolving, its counted recharge is running (unless the selected unit's
   button reads ready: try_pair's own release), or the game refused it and the logged back-off is running. These are
   the cases where try_pair did nothing with the evaluator's answer.
3. The wanderer's candidate test reads the unit id from the map (FOURTH.blob_shape stores s.id) and the target's
   is_moving() once per map, not once per caster.
4. FOURTH.blob_score_c / blob_friend_gap_c: the soldiers under a blast and the friendly gap of a target are worked
   out once per map and blast size, for every caster that looks at that target.
Backups: docs/backups/round220/pre220_{live,ann}.lua."""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_anim_keys as GA  # noqa: E402

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round220"

LOCK_FN = """-- ============================================================================
-- ROUND 220 - NO EVALUATOR CALL WHILE THE CAST CANNOT GO OUT (field: the evaluators cost 61 ms of every second with
-- 40 units and 37 active abilities). The three cases below are the ones in which FOURTH.try_pair did nothing with the
-- evaluator's answer: (1) a counted recharge is running (a multi-use ability), unless the selected unit's button
-- reads ready, which is try_pair's own early release and still goes through it. (2) this ability's own wind-up is
-- still resolving. (3) the game refused the cast and the logged back-off is running.
-- ============================================================================
function FOURTH.locked_now(ui_id, ability)
	local mk = ability.marker
	if ability.charge_s ~= nil then
		local cu = charge_gate.until_tick[ui_id]
		local held = (cu ~= nil and cu[mk]) or nil
		if held ~= nil and tick_count < held then
			local ready = FOURTH.charge_hold_ready_on_screen(ui_id, ability, held)
			if ready then return false end
			return true
		end
	end
	if ability.wind_up_s ~= nil then
		local cgu = cast_gate.until_tick[ui_id]
		local t = (cgu ~= nil and cgu[mk]) or nil
		if t ~= nil and tick_count < t then return true end
	end
	local bucket = cooldown_hold[ui_id]
	local hold = (bucket ~= nil and bucket[mk]) or nil
	if hold ~= nil and hold.logged == true and (tick_count - hold.since) < MAX_HOLD_TICKS and tick_count < hold.next_at then
		return true
	end
	return false
end

"""
A_TRY = "function FOURTH.try_pair(script_unit, unit, ability, ui_id, ability_key, reason, gone_ids)\n"

CACHE_FN = """-- ROUND 220: the soldiers under a blast and the friendly gap of a target depend on the map, the target and the blast
-- size only, not on the caster: worked out once and kept on the target's shape (a new map has new shapes).
function FOURTH.blob_score_c(e, m, r)
	local c = e.c_sc
	if c == nil or c[1] ~= m or c[2] ~= r then
		local sc, un = FOURTH.blob_score(e, m, r)
		c = { m, r, sc, un }
		e.c_sc = c
	end
	return c[3], c[4]
end
function FOURTH.blob_friend_gap_c(e, m, reach)
	local c = e.c_gap
	if c == nil or c[1] ~= m or c[2] ~= reach then
		c = { m, reach, FOURTH.blob_friend_gap(e, m, reach) }
		e.c_gap = c
	end
	return c[3]
end
"""
A_PICK = "function FOURTH.blob_pick(unit, m, r, key)\n"

BOTH = [
    ("lock fn", A_TRY, LOCK_FN + A_TRY),
    ("cache fn", A_PICK, CACHE_FN + A_PICK),
    ("pick use",
     "\t\t\tlocal g = FOURTH.blob_friend_gap(e, m, reach)\n\t\t\tif g == nil or g > reach then\n"
     "\t\t\t\tlocal sc, un = FOURTH.blob_score(e, m, r)\n",
     "\t\t\tlocal g = FOURTH.blob_friend_gap_c(e, m, reach)   -- ROUND 220: once per map and target\n"
     "\t\t\tif g == nil or g > reach then\n"
     "\t\t\t\tlocal sc, un = FOURTH.blob_score_c(e, m, r)\n"),
    ("wander score", "\tlocal sc = FOURTH.blob_score(e, m, row.r)\n",
     "\tlocal sc = FOURTH.blob_score_c(e, m, row.r)   -- ROUND 220: once per map and target\n"),
    ("shape id",
     "\ts.t = t\n\tlocal ok_v, sv = pcall(function() return u:strategic_value() end)\n",
     "\ts.t = t\n"
     "\tpcall(function() s.id = tostring(u:unique_ui_id()) end)   -- ROUND 220: read once per map\n"
     "\tlocal ok_v, sv = pcall(function() return u:strategic_value() end)\n"),
    ("wander ours",
     "\t\t\tlocal oid = nil\n\t\t\tpcall(function() oid = tostring(m.ours[i].unit:unique_ui_id()) end)\n"
     "\t\t\tif (oid == nil or oid ~= self_id) and FOURTH.blob_rect_gap(e.x, e.z, m.ours[i]) <= need then return nil end\n",
     "\t\t\tlocal oid = m.ours[i].id   -- ROUND 220: the id the map read\n"
     "\t\t\tif (oid == nil or oid ~= self_id) and FOURTH.blob_rect_gap(e.x, e.z, m.ours[i]) <= need then return nil end\n"),
    ("target still",
     "function FOURTH.ww_target_still(e)\n\tlocal ok, mv = pcall(function() return e.unit:is_moving() end)\n"
     "\treturn ok and mv == false\nend\n",
     "function FOURTH.ww_target_still(e)\n"
     "\tif e.c_still == nil then   -- ROUND 220: read once per map\n"
     "\t\tlocal ok, mv = pcall(function() return e.unit:is_moving() end)\n"
     "\t\te.c_still = (ok and mv == false)\n"
     "\tend\n"
     "\treturn e.c_still\nend\n"),
]
LIVE_ONLY = [
    ("poll",
     "\t\t\t\t\tlocal perf_e0 = FOURTH.perf_now()   -- ROUND 219: the evaluator's time, by trigger family\n"
     "\t\t\t\t\tlocal reason = ability.evaluate(unit, routing)\n",
     "\t\t\t\t\tif FOURTH.locked_now(ui_id, ability) then return nil end   -- ROUND 220: no evaluator call while the cast cannot go out\n"
     "\t\t\t\t\tlocal perf_e0 = FOURTH.perf_now()   -- ROUND 219: the evaluator's time, by trigger family\n"
     "\t\t\t\t\tlocal reason = ability.evaluate(unit, routing)\n"),
]
ANN_ONLY = [
    ("poll",
     "\t\t\t\t\tFOURTH.entry_reset(ability, unit)   -- ROUND 198: the slot reset, shared with the fast pass\n"
     "\t\t\t\t\tlocal want_fire = ability.evaluate(unit, routing)\n",
     "\t\t\t\t\tFOURTH.entry_reset(ability, unit)   -- ROUND 198: the slot reset, shared with the fast pass\n"
     "\t\t\t\t\tif FOURTH.locked_now(ui_id, ability) then return nil end   -- ROUND 220: no evaluator call while the cast cannot go out\n"
     "\t\t\t\t\tlocal want_fire = ability.evaluate(unit, routing)\n"),
]
ANIM_RE = re.compile(r'\nFOURTH\.ANIM_TEXT = "[^"\n]*"\n')


def patch(path, live):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 220" not in s, "already patched: " + path
    for what, a, b in BOTH + (LIVE_ONLY if live else ANN_ONLY):
        assert s.count(a) == 1, (what, s.count(a), path)
        s = s.replace(a, b)
    assert len(ANIM_RE.findall(s)) == 1
    return s


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre220_live.lua"), (ANN, "pre220_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
        elif "--again" in sys.argv:
            shutil.copy2(dst, src)
    live = patch(LIVE, True)
    ann = patch(ANN, False)
    keys = GA.derive(live)
    gone = GA.placed_keys(live)
    new = '\nFOURTH.ANIM_TEXT = "%s"\n' % GA.text(keys)
    for path, s in ((LIVE, live), (ANN, ann)):
        s = ANIM_RE.sub(lambda m: new, s)
        open(path, "w", encoding="utf-8", newline="").write(s)
        print("patched", path)
    print("ANIM set:", len(keys), "keys, placed keys taken out:", len(gone))


if __name__ == "__main__":
    main()
