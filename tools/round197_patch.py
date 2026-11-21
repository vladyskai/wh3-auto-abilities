#!/usr/bin/env python3
"""Round 197 (user 2026-11-21: "A: whole army"), both copies: THE WHOLE-ARMY FALLBACK for the blob family
(enemy_blob, enemy_blob_vortex). When no living unit of the enemy army, visible or hidden, could pass the two save-it
rules (the armour rule for armour-piercing attacks, the trash rule), this evaluation drops them and takes the best
visible target. The wanderers' own use of blob_trash_ok is untouched.
TEST-ONLY: ZZ_AUTO_TEST_NO_BLOB_FALLBACK (older worlds model only the visible enemies).
Backups: docs/backups/round197/pre197_{live,ann}.lua."""
import os
import shutil

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round197"

ANCHOR = "function FOURTH.blob_pick(unit, m, r, key)\n"
BLOCK = """-- ============================================================================
-- ROUND 197 - THE WHOLE-ARMY FALLBACK (user 2026-11-21: "when no better target
-- exists on the enemy side (visible or invisible), it should fire as it
-- wouldn't be wasteful", option "A: whole army"). Two rules save a blob
-- ability for a better target: the armour rule (an armour-piercing attack
-- never aims at armour below BLOB_AP_ARMOUR_MIN) and the trash rule. When NO
-- living unit of the enemy army, visible or HIDDEN, could pass them, saving it
-- is pointless: this evaluation drops both (FOURTH.blob_relax) and takes the
-- best visible target. Everything else stays: the infantry-or-large class,
-- none of ours in the blast + 10 m, the caster standing, the target visible and
-- in range, the coverage line. Hidden enemies are only COUNTED here, never
-- targeted (a deliberate exception to round 169, the user's ruling).
-- A unit counts as better when its class could be a target (an infantry block
-- of BLOB_MIN_MEN or more, or a large unit for the prefer-central attacks;
-- flying or not, since a flier can land), the armour rule lets this attack aim
-- at it, and it is not trash. Read once per poll per key. An unreadable enemy
-- army keeps the rules (fail-closed).
-- TEST-ONLY: ZZ_AUTO_TEST_NO_BLOB_FALLBACK (the harness sets it for older worlds).
-- ============================================================================
FOURTH.blob_relax = false
FOURTH.blob_better_cache = {}
FOURTH.blob_fallback_said = {}

function FOURTH.blob_better_exists(key, central)
	local c = FOURTH.blob_better_cache[key]
	if c ~= nil and c.tick == tick_count then return c.v end
	local dmg = FOURTH.BLOB_DMG[key]
	local better, readable = false, false
	local ok_c, coll = pcall(function() return bm:get_scriptunits_for_main_enemy_army_to_local_player() end)
	local ok_n, n = false, nil
	if ok_c and coll ~= nil then ok_n, n = pcall(function() return coll:count() end) end
	if ok_n and type(n) == "number" then
		readable = true
		for i = 1, n do
			local e = nil
			pcall(function() e = coll:item(i).unit end)
			local s = nil
			if e ~= nil then s = FOURTH.blob_shape(e) end
			if s ~= nil and s.men ~= nil and s.men > 0 then
				local large = (s.t ~= nil and FOURTH.class_keys.large[s.t] == true)
				local cls = (s.inf and s.men >= FOURTH.BLOB_MIN_MEN) or (central and large)
				if cls and FOURTH.blob_ap_ok(s, dmg) and (large or s.vps == nil or s.vps >= FOURTH.TRASH_VPS) then
					better = true
					break
				end
			end
		end
	end
	local v = better or not readable
	FOURTH.blob_better_cache[key] = { tick = tick_count, v = v }
	return v
end

-- the two save-it rules, dropped while this blob evaluation falls back
function FOURTH.blob_ap_rule(e, dmg) return FOURTH.blob_relax == true or FOURTH.blob_ap_ok(e, dmg) end
function FOURTH.blob_trash_rule(e, sc, r) return FOURTH.blob_relax == true or FOURTH.blob_trash_ok(e, sc, r) end

function FOURTH.blob_pick(unit, m, r, key)
"""

EDITS = [
    # blob_pick: both rules
    ("FOURTH.eg_enemy_within_bound(unit, e.unit) and FOURTH.blob_ap_ok(e, dmg) then\n",
     "FOURTH.eg_enemy_within_bound(unit, e.unit) and FOURTH.blob_ap_rule(e, dmg) then   -- ROUND 197\n"),
    ("\t\t\t\tif sc >= need and FOURTH.blob_trash_ok(e, sc, r) then   -- ROUND 153: no trash unless a big blob\n",
     "\t\t\t\tif sc >= need and FOURTH.blob_trash_rule(e, sc, r) then   -- ROUND 153: no trash unless a big blob (ROUND 197: the fallback)\n"),
    # blob_pick_large: the armour rule
    ("FOURTH.eg_enemy_within_bound(unit, e.unit) and FOURTH.blob_ap_ok(e, dmg)\n\t\t\tand FOURTH.blob_not_flying(e.unit) then",
     "FOURTH.eg_enemy_within_bound(unit, e.unit) and FOURTH.blob_ap_rule(e, dmg)   -- ROUND 197\n\t\t\tand FOURTH.blob_not_flying(e.unit) then"),
    # blob_still_ok: the re-check agrees with the pick
    ("\t\t\t\treturn FOURTH.blob_ap_ok(e, key and FOURTH.BLOB_DMG[key])\n",
     "\t\t\t\treturn FOURTH.blob_ap_rule(e, key and FOURTH.BLOB_DMG[key])   -- ROUND 197\n"),
    ("\t\t\tif not FOURTH.blob_ap_ok(e, key and FOURTH.BLOB_DMG[key]) then return false end\n",
     "\t\t\tif not FOURTH.blob_ap_rule(e, key and FOURTH.BLOB_DMG[key]) then return false end   -- ROUND 197\n"),
    ("\t\t\treturn sc >= FOURTH.blob_need(r) and FOURTH.blob_trash_ok(e, sc, r)   -- ROUND 153\n",
     "\t\t\treturn sc >= FOURTH.blob_need(r) and FOURTH.blob_trash_rule(e, sc, r)   -- ROUND 153 (ROUND 197: the fallback)\n"),
    # the evaluation sets the flag
    ("function FOURTH.evaluate_enemy_blob(unit, routing)\n\tFOURTH.eg_mode = \"blob\"\n\tFOURTH.blob_kind = nil\n",
     "function FOURTH.evaluate_enemy_blob(unit, routing)\n\tFOURTH.eg_mode = \"blob\"\n\tFOURTH.blob_kind = nil\n"
     "\tFOURTH.blob_relax = false   -- ROUND 197: set below, after the caster checks\n"),
    ("\tlocal central = (shot ~= nil and shot[5] == 1)\n\tlocal tgt, sc, un, gap, val, kind = nil, nil, nil, nil, nil, nil\n",
     "\tlocal central = (shot ~= nil and shot[5] == 1)\n"
     "\t-- ROUND 197: the whole-army fallback (nothing in the enemy army, visible or hidden, passes the save-it rules)\n"
     "\tFOURTH.blob_relax = (ZZ_AUTO_TEST_NO_BLOB_FALLBACK ~= true) and not FOURTH.blob_better_exists(key, central)\n"
     "\tif FOURTH.blob_relax and not FOURTH.blob_fallback_said[key] then\n"
     "\t\tFOURTH.blob_fallback_said[key] = true\n"
     "\t\tlog(\"BLOB FALLBACK \" .. tostring(key) .. \": no unit of the enemy army (visible or hidden) passes the armour and trash rules, so it takes the best visible target without them\")\n"
     "\tend\n"
     "\tlocal tgt, sc, un, gap, val, kind = nil, nil, nil, nil, nil, nil\n"),
    # the reason names the fallback
    ("\tlocal etype = \"enemy\"\n\tpcall(function() etype = tostring(tgt.unit:type()) end)\n\tFOURTH.blob_r = r\n",
     "\tlocal etype = \"enemy\"\n\tpcall(function() etype = tostring(tgt.unit:type()) end)\n"
     "\tif FOURTH.blob_relax then etype = etype .. \", fallback: nothing better in the enemy army\" end   -- ROUND 197\n"
     "\tFOURTH.blob_r = r\n"),
]


def ann_edits():
    """The reading copy's slim blob evaluator: its own variable line, no reason string, the log line as a comment."""
    out = []
    for a, b in EDITS:
        if a.startswith("\tlocal central = (shot ~= nil and shot[5] == 1)\n"):
            a = "\tlocal central = (shot ~= nil and shot[5] == 1)\n\tlocal tgt, kind = nil, nil\n"
            b = b.replace("\tlocal tgt, sc, un, gap, val, kind = nil, nil, nil, nil, nil, nil\n", "\tlocal tgt, kind = nil, nil\n")
            b = b.replace("\t\tlog(\"BLOB FALLBACK \" .. ", "\t\t-- (live file only) logs \"BLOB FALLBACK \" .. ")
        elif a.startswith("\tlocal etype = \"enemy\"\n"):
            continue   # the reading copy returns true, not a reason string
        out.append((a, b))
    return out


def patch(path, ann):
    s = open(path, encoding="utf-8", newline="").read()
    assert "ROUND 197 - THE WHOLE-ARMY FALLBACK" not in s, "already patched: " + path
    assert s.count(ANCHOR) == 1, path
    s = s.replace(ANCHOR, BLOCK)
    for a, b in (ann_edits() if ann else EDITS):
        assert s.count(a) == 1, (path, a[:70], s.count(a))
        s = s.replace(a, b)
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("patched", path)


def main():
    os.makedirs(BK, exist_ok=True)
    for src, name in ((LIVE, "pre197_live.lua"), (ANN, "pre197_ann.lua")):
        dst = os.path.join(BK, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
    patch(LIVE, False)
    patch(ANN, True)


if __name__ == "__main__":
    main()
