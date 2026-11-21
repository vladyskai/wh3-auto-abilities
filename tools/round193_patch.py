#!/usr/bin/env python3
"""Round 193 (user rulings 2026-11-21), both copies (the live source and the annotated reading copy):

1. SCRY-ORB on when_ready (user: "implement" the proposal: fire when ready, like the 21 pure winds abilities).
   3 uses / 120 s recharge: a charge_gate.hold_s row (one use per recharge cycle).
2. THE PRE-SHOT PROBE, READ-ONLY (user: "implement recommendation and propose a test battle"). Every ranged unit of
   ours, every poll, while it is NOT firing: would a buff cast now, before its first shot? The conditions (the user's
   and ours): the unit has a current target (only after an attack order or a fire-at-will pick), the target is within
   the unit's own live missile_range(), the target is visible, the unit is standing (unless it can fire on the move),
   it has ammunition, it is not in melee. The live file logs WOULD CAST when the condition starts, WOULD CAST ENDED
   (with the reason) when it stops without a shot, and PRESHOT at the first shot (how long the condition had held, or
   that it never did). It also logs the unit's fire-at-will behaviour (is_behaviour_active, unproven read). NOTHING is
   cast. The reading copy keeps the same state with its log lines as comments (it stays log-free).
Backups: docs/backups/round193/pre193_{live,ann}.lua."""
import os
import shutil

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round193"

ANCHOR_SCRY = '\t{ marker = "black_periapt", name = "Black Periapt", trigger = "when_ready",\n'
SCRY = ('\t{ marker = "scry_orb", name = "Scry-Orb", trigger = "when_ready",\n'
        '\t\tbadge = "zz_auto_badge_scry_orb",\n'
        '\t\tkeys = { "wh3_dlc29_item_abilities_scry_orb" },   -- ROUND 193 (user: "implement"; winds x1.6, recharges -30 s)\n'
        '\t\tox = 0, oy = 0 },\n')
ANCHOR_HOLD = "\t\t-- ROUND 185: the rule-shut review's rows 20-64 with more than one use (recharge_time)\n"
HOLD = ("\t\t-- ROUND 193: Scry-Orb, 3 uses (recharge_time)\n"
        '\t\t["wh3_dlc29_item_abilities_scry_orb"] = 120,\n')

PROBE = """-- ============================================================================
-- ROUND 193 - THE PRE-SHOT PROBE (READ-ONLY; user 2026-11-21: "implement
-- recommendation and propose a test battle"). Could a shooting buff be cast
-- BEFORE a unit's first shot instead of at the cast point after it? For every
-- ranged unit of ours that is NOT firing, every poll: FOURTH.preshot_now asks
--   * a current target (it exists only after an attack order or a fire-at-will
--     pick) within the unit's own live missile_range() (FOURTH.ammo_in_range),
--   * the target visible (FOURTH.enemy_not_hidden),
--   * the unit standing, unless it can fire on the move (FOURTH.can_shoot_now),
--   * ammunition left (the probe's own last ammo_left() read),
--   * the unit not in melee.
-- WOULD CAST is logged when all of them start to hold, WOULD CAST ENDED (and
-- why) when they stop without a shot, PRESHOT at the first shot: how long the
-- condition had held before it, or that it never did. The unit's fire-at-will
-- behaviour (is_behaviour_active("fire_at_will"), never read before) is logged
-- with WOULD CAST, for information only. NOTHING is cast from this probe.
-- ============================================================================
function FOURTH.preshot_now(u, st, inr)
	if inr ~= true then return false, "no target within its missile range" end
	local ok_t, t = pcall(function() return u:current_target() end)
	if not ok_t or t == nil then return false, "no target" end
	if not FOURTH.enemy_not_hidden(t) then return false, "target hidden" end
	if not FOURTH.can_shoot_now(u) then return false, "moving" end
	if st.last ~= nil and st.last <= 0 then return false, "no ammunition" end
	local ok_m, m = pcall(function() return u:is_in_melee() end)
	if ok_m and m == true then return false, "in melee" end
	return true, nil
end

function FOURTH.preshot_probe(u, st, now_s, inr, d, r)
	local ok, why = FOURTH.preshot_now(u, st, inr)
	if ok and st.pre_since == nil then
		st.pre_since = now_s
		local ok_f, faw = pcall(function() return u:is_behaviour_active("fire_at_will") end)
		local who, aim = FOURTH.ammo_describe(u)
		log(string.format("WOULD CAST %s at t=%.2fs: target %.1fm away within its %.1fm missile range, visible, standing, ammo, not in melee, fire at will=%s %s", who, now_s, d or -1, r or -1, ok_f and tostring(faw) or "?", aim))
	elseif not ok and st.pre_since ~= nil then
		local who = FOURTH.ammo_describe(u)
		log(string.format("WOULD CAST ENDED %s at t=%.2fs after %.2fs with no shot (%s)", who, now_s, now_s - st.pre_since, why))
		st.pre_since = nil
	end
end

-- at the first shot of an episode: how long the would-cast condition had held
function FOURTH.preshot_first_shot(u, st, now_s)
	local who = FOURTH.ammo_describe(u)
	if st.pre_since ~= nil then
		log(string.format("PRESHOT %s: the condition held %.2fs before the first shot at t=%.2fs", who, now_s - st.pre_since, now_s))
	else
		log(string.format("PRESHOT %s: the first shot at t=%.2fs came with no would-cast before it", who, now_s))
	end
	st.pre_since = nil
end

function FOURTH.ammo_probe(units)
"""

LIVE_EDITS = [
    ('lead, st.reload and string.format("%gs", st.reload) or "not in the table", aim))\n',
     'lead, st.reload and string.format("%gs", st.reload) or "not in the table", aim))\n'
     '\t\t\t\t\t\t\tFOURTH.preshot_first_shot(u, st, now_s)   -- ROUND 193: the read-only pre-shot probe\n'),
]
ANN_EDITS = [
    ("\t\t\t\t\t\tif not st.was_on then\n\t\t\t\t\t\t\tst.first_shot_s = now_s\n\t\t\t\t\t\t\tst.cast_point_passed = false\n",
     "\t\t\t\t\t\tif not st.was_on then\n\t\t\t\t\t\t\tst.first_shot_s = now_s\n\t\t\t\t\t\t\tst.cast_point_passed = false\n"
     "\t\t\t\t\t\t\tFOURTH.preshot_first_shot(u, st, now_s)   -- ROUND 193: the read-only pre-shot probe\n"),
]
COMMON = [
    ("\t\t\t\t\tst.last = now\n\t\t\t\tend\n",
     "\t\t\t\t\tst.last = now\n\t\t\t\tend\n"
     "\t\t\t\tif not st.firing then FOURTH.preshot_probe(u, st, now_s, inr, d, r) end   -- ROUND 193: read-only\n"),
    ("\nfunction FOURTH.ammo_probe(units)\n", "\n" + PROBE),
    (ANCHOR_SCRY, SCRY + ANCHOR_SCRY),
    (ANCHOR_HOLD, HOLD + ANCHOR_HOLD),
]


def reading_copy(text):
    """The reading copy stays log-free: each log(...) line of the probe becomes a comment."""
    out = []
    for line in text.split("\n"):
        stripped = line.lstrip("\t")
        if stripped.startswith(("log(string.format(", "local who = FOURTH.ammo_describe(", "local who, aim = FOURTH.ammo_describe(")):
            line = line[:len(line) - len(stripped)] + "-- (live file only) " + stripped.replace("log(string.format(", "logs string.format(", 1)
        out.append(line)
    return "\n".join(out)


def patch(path, extra, ann):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 193 - THE PRE-SHOT PROBE" not in s, "already patched: " + path
    for a, b in extra + COMMON:
        if ann and a == "\nfunction FOURTH.ammo_probe(units)\n":
            b = "\n" + reading_copy(PROBE)
        assert s.count(a) == 1, (path, a[:60], s.count(a))
        s = s.replace(a, b)
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre193_live.lua"), (ANN, "pre193_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
    patch(LIVE, LIVE_EDITS, False)
    patch(ANN, ANN_EDITS, True)


if __name__ == "__main__":
    main()
