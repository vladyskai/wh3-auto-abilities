#!/usr/bin/env python3
"""Round 192 (user rulings 2026-11-21), both copies (the live source and the annotated reading copy):

1. THE FAST ENEMY MUST BE COMING AT US (open point 7, option A; user: "try to implement using is_moving_fast()").
   FOURTH.fast_enemy_near now needs the enemy to be RUNNING (is_moving_fast(), exactly true) instead of merely moving,
   and its edge gap to our nearest unit to have SHRUNK by at least FOURTH.FAST_CLOSING_MPS (3 m/s) over at least
   FOURTH.FAST_CLOSING_S (1 s) (FOURTH.fast_closing keeps one gap sample per enemy per poll). The run-speed stat and
   the 40 m closeness are unchanged. TEST-ONLY: ZZ_AUTO_TEST_NO_CLOSING (set by the harness for the older worlds)
   keeps the pre-192 rule.
2. GROMBRINDAL HAS NO FEAR (user: 'implement "at least one ally (caster included) in range in melee or wavering"'):
   a new entry on melee_or_wavering_aura (aura 55 m -> the 70% bound 38 m).
3. THE FIVE SPELL-BAR RUNES LEAVE THE MOD (user: "They should not be in the mod. Just mark them as closed because they
   are on the right ability wheel."): Rune of Breaking, Negation, Slowness, Speed, Oath & Steel (entries and their
   charge_gate rows). The generated key tables are regenerated afterwards by tools/round171_regen_tables.py.
Backups: docs/backups/round192/pre192_{live,ann}.lua."""
import os
import shutil

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round192"

OLD_HEAD = """-- gap, speed when the enemy is MOVING with a run speed of FAST_ENEMY_MPS or
-- more and one of our units (the caster counting) is within FAST_ENEMY_NEAR_M
-- of it (edge to edge, the closest of ours); nil otherwise. Every read
-- fails closed.
function FOURTH.fast_enemy_near(enemy, caster)
	local ok_mv, mv = pcall(function() return enemy:is_moving() end)
	if not (ok_mv and mv == true) then return nil end
"""
NEW_HEAD = """-- ============================================================================
-- ROUND 192 - THE FAST ENEMY MUST BE COMING AT US (user 2026-11-21, option A:
-- "try to implement using is_moving_fast()"). Before, any fast-type enemy that
-- was moving within 40 m counted, even one riding past or walking. Now it must
-- be RUNNING (is_moving_fast() exactly true) AND CLOSING: its edge gap to our
-- nearest unit must have shrunk by at least FAST_CLOSING_MPS metres per second,
-- measured over at least FAST_CLOSING_S seconds. FOURTH.fast_closing keeps one
-- gap sample per enemy per poll; the first answer comes one second after the
-- enemy starts running. Every read fails closed.
-- TEST-ONLY: ZZ_AUTO_TEST_NO_CLOSING (the harness sets it for worlds written
-- before round 192) keeps the old rule (moving, no closing check).
-- ============================================================================
FOURTH.FAST_CLOSING_MPS = 3     -- ROUND 192: the gap must shrink at least this fast (m/s)
FOURTH.FAST_CLOSING_S = 1       -- ROUND 192: ...measured over at least this long (s)
FOURTH.fast_gap_hist = {}

function FOURTH.fast_closing(enemy, gap)
	local ok_id, id = pcall(function() return tostring(enemy:unique_ui_id()) end)
	if not ok_id or id == nil then return false end
	local now = tick_count * POLL_MS / 1000
	local h = FOURTH.fast_gap_hist[id]
	if h == nil then
		h = {}
		FOURTH.fast_gap_hist[id] = h
	end
	if #h > 0 and h[#h].t == now then
		if gap < h[#h].g then h[#h].g = gap end   -- the same poll: keep the closest of ours
	else
		h[#h + 1] = { t = now, g = gap }
	end
	while #h > 0 and now - h[1].t > 2 * FOURTH.FAST_CLOSING_S + 0.5 do table.remove(h, 1) end
	local old = nil
	for i = #h, 1, -1 do
		if now - h[i].t >= FOURTH.FAST_CLOSING_S then
			old = h[i]
			break
		end
	end
	if old == nil then return false end
	return (old.g - h[#h].g) / (now - old.t) >= FOURTH.FAST_CLOSING_MPS
end

-- gap, speed when the enemy is RUNNING with a run speed of FAST_ENEMY_MPS or
-- more, CLOSING on our units (FOURTH.fast_closing, round 192) and one of our
-- units (the caster counting) is within FAST_ENEMY_NEAR_M of it (edge to edge,
-- the closest of ours); nil otherwise. Every read fails closed.
function FOURTH.fast_enemy_near(enemy, caster)
	local old_rule = (ZZ_AUTO_TEST_NO_CLOSING == true)
	if old_rule then
		local ok_mv, mv = pcall(function() return enemy:is_moving() end)
		if not (ok_mv and mv == true) then return nil end
	else
		local ok_mf, mf = pcall(function() return enemy:is_moving_fast() end)   -- ROUND 192: really running
		if not (ok_mf and mf == true) then return nil end
	end
"""
OLD_TAIL = """	try(caster)
	if tracked_units ~= nil then
		for i = 1, #tracked_units do
			try(tracked_units[i] and tracked_units[i].unit)
		end
	end
	if best ~= nil and best <= FOURTH.FAST_ENEMY_NEAR_M then return best, sp end
	return nil
end
"""
NEW_TAIL = """	try(caster)
	if tracked_units ~= nil then
		for i = 1, #tracked_units do
			try(tracked_units[i] and tracked_units[i].unit)
		end
	end
	if best == nil then return nil end
	-- ROUND 192: sampled at every distance, so the history exists when it comes within 40 m
	local closing = old_rule or FOURTH.fast_closing(enemy, best)
	if closing and best <= FOURTH.FAST_ENEMY_NEAR_M then return best, sp end
	return nil
end
"""

RUNES = ["rune_of_breaking", "rune_of_negation", "rune_of_slowness", "rune_of_speed", "rune_of_oath_and_steel"]
RUNE_KEYS = ["wh2_dlc17_rune_abilities_rune_of_breaking", "wh_main_rune_abilities_rune_of_negation",
             "wh2_dlc17_rune_abilities_rune_of_slowness", "wh2_dlc17_rune_abilities_rune_of_speed",
             "wh_main_rune_abilities_rune_of_oath_and_steel"]

ANCHOR_GHNF = '\t{ marker = "hunters_call", name = "Hunter\'s Call", trigger = "melee_or_wavering_aura",\n'
GHNF = ('\t{ marker = "grombrindal_has_no_fear", name = "Grombrindal Has No Fear", trigger = "melee_or_wavering_aura",\n'
        '\t\tbadge = "zz_auto_badge_grombrindal_has_no_fear",\n'
        '\t\tkeys = { "wh_pro01_lord_passive_grombrindal_has_no_fear" },   -- ROUND 192 (user: in range in melee or wavering)\n'
        '\t\taura_real = 55,\n'
        '\t\tox = 0, oy = 0 },\n')


def cut_entry(s, marker):
    head = '\t{ marker = "%s", ' % marker
    assert s.count(head) == 1, (marker, s.count(head))
    i = s.index(head)
    j = s.index("\n\t{ marker = ", i + 1) + 1
    body = s[i:j]
    assert body.rstrip().endswith("},"), body
    return s[:i] + s[j:]


def patch(path):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 192 - THE FAST ENEMY" not in s, "already patched: " + path
    assert s.count(OLD_HEAD) == 1 and s.count(OLD_TAIL) == 1, path
    s = s.replace(OLD_HEAD, NEW_HEAD).replace(OLD_TAIL, NEW_TAIL)
    for m in RUNES:
        s = cut_entry(s, m)
    for k in RUNE_KEYS:
        line = '\t\t["%s"] = 3,\n' % k
        assert s.count(line) == 1, (k, s.count(line))
        s = s.replace(line, "")
    assert s.count(ANCHOR_GHNF) == 1
    s = s.replace(ANCHOR_GHNF, GHNF + ANCHOR_GHNF)
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre192_live.lua"), (ANN, "pre192_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
    patch(LIVE)
    patch(ANN)


if __name__ == "__main__":
    main()
