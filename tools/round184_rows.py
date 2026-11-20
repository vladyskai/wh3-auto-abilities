#!/usr/bin/env python3
"""Round 184 (user, 2026-11-20: "Up to #19 ruled"; rulings read from the Claude Docs review "Rule-shut abilities
review", rev 83, dropdowns and threads).

Rows 10-19 of docs\\WH3_rule_shut_review_2026-11-20.md (the rest of the "own-troop damage" rows):
  10-12 Flock of Doom x3: "Recommended" = A2, the area drain without a standing-still check on the ENEMY. The shipped
        enemy_area_drain never checks the enemy (its standing-still gate is the CASTER's, for animated casts only), so
        A2 is plain enemy_area_drain.
  13 Sword of Daith: "Recommended" = A, enemy_area_drain.
  14 Zefet-nebtar: "Recommended" = A, plain enemy_area_drain, no clearance (thread: "if not damage, then no need for
     clearance check").
  15 Ring of Corin: "Recommended" = A, enemy_single_drain.
  16 Soul Stealer (RoR): "B with the 75% gate"; 17 Soul Stealer (Druchii Anointed): "same as #16" -> NEW
     enemy_area_drain_hurt: enemy_area_drain while the caster is at or below FOURTH.DRAIN_HURT_PCT (75%) health.
  18 Warpstorm Scroll: "Recommended" = A, enemy_single_drain with target_class "flying".
  19 Raging Tornado: "Recommended" = A -> NEW enemy_ground_melee_cluster: on the ground under the enemy in melee with
     the most enemy value in melee within CLUSTER_M (24 m, FOURTH.cluster_pick), the caster standing still for its
     animated cast (blob_still); no clearance (the damage hits enemies only).
Every aimed entry carries the game's range_real. Multi-use keys join cast_gate.hold_s, wind-up keys cast_gate.wind_up_s;
the SHOT table gains the new family, the AREA table its keys; every key-keyed GENERATED table is regenerated.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamedata_paths as GP  # noqa: E402
import gen_shot_tables as GS  # noqa: E402
import round171_regen_tables as RT  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

AD, AH, SD, GC = "enemy_area_drain", "enemy_area_drain_hurt", "enemy_single_drain", "enemy_ground_melee_cluster"
ROWS = [
    (10, "flock_of_doom_runecaller", "Flock of Doom", AD, "wh3_dlc27_spell_bound_runecaller_flock_of_doom", 100, None),
    (11, "flock_of_doom_wh3", "Flock of Doom", AD, "wh3_main_spell_bound_flock_of_doom", 100, None),
    (12, "flock_of_doom", "Flock of Doom", AD, "wh_dlc08_spell_bound_flock_of_doom", 100, None),
    (13, "sword_of_daith", "Sword of Daith", AD, "wh_dlc05_weapon_abilities_daiths_sword", 100, None),
    (14, "zefet_nebtar", "Zefet-nebtar, the Mortis Blade", AD, "wh3_dlc29_item_abilities_zefet_nebtar_the_mortis_blade", 100, None),
    (15, "ring_of_corin", "Ring of Corin", SD, "wh2_main_spell_bound_ring_of_corin", 200, None),
    (16, "soul_stealer_ror", "Soul Stealer", AH, "wh2_dlc10_spell_bound_soul_stealer_ror", 100, None),
    (17, "soul_stealer_anointed", "Soul Stealer", AH, "wh3_dlc27_spell_bound_soul_stealer", 100, None),
    (18, "warpstorm_scroll", "Warpstorm Scroll", SD, "wh2_main_item_abilities_warpstorm_scroll", 100, "flying"),
    (19, "raging_tornado", "Raging Tornado", GC, "wh3_dlc29_unit_abilities_raging_tornado", 100, None),
]
KEYS = [r[4] for r in ROWS]
FAMILY = {r[4]: r[3] for r in ROWS}
NEW_FAMS = (AH, GC)


def sub(s, a, b, n=1):
    assert s.count(a) == n, (a[:80], s.count(a))
    return s.replace(a, b)


def entry(row, marker, name, trig, key, rng, cls):
    lines = ['\t-- ROUND 184 (rule-shut review row %d)' % row,
             '\t{ marker = "%s", name = "%s", trigger = "%s",' % (marker, name, trig),
             '\t\tbadge = "zz_auto_badge_%s",' % marker,
             '\t\tkeys = { "%s" },' % key,
             "\t\trange_real = %d," % rng]
    if cls is not None:
        lines.append('\t\ttarget_class = "%s",' % cls)
    lines.append("\t\tox = 0, oy = 0 },")
    return "\n".join(lines) + "\n"


def tsv(n):
    f = open(os.path.join(GP.GAMEDATA, n), encoding="utf-8-sig")
    h = f.readline().rstrip("\n").split("\t")
    f.readline()
    return [dict(zip(h, ln.rstrip("\n").split("\t"))) for ln in f]


def num(v):
    f = float(v)
    return str(int(f)) if f == int(f) else ("%.3f" % f).rstrip("0").rstrip(".")


USA = {r["key"]: r for r in tsv("unit_spec_abil.tsv")}
for _r in ROWS:   # rule 3: range_real is the game's target_intercept_range
    assert float(USA[_r[4]]["target_intercept_range"]) == _r[5], (_r[4], USA[_r[4]]["target_intercept_range"])
HOLD = [(k, num(USA[k]["recharge_time"])) for k in KEYS if int(float(USA[k]["num_uses"])) > 1]
WIND = [(k, num(USA[k]["wind_up_time"])) for k in KEYS if float(USA[k]["wind_up_time"] or 0) > 0]
print("multi-use keys:", HOLD)
print("wind-up keys:", WIND)

RESTOCK = '\t{ marker = "restock", name = "Restock!", trigger = "ally_ammo_low",'
NEW_ENTRIES = "".join(entry(*r) for r in ROWS)
HOLD_OLD = "\thold_s = {\n"
HOLD_NEW = HOLD_OLD + ("\t\t-- ROUND 184: the rule-shut review's rows 10-19 with more than one use (recharge_time)\n"
                       + "".join('\t\t["%s"] = %s,\n' % (k, v) for k, v in HOLD))
WIND_OLD = "\twind_up_s = {\n"
WIND_NEW = WIND_OLD + ("\t\t-- ROUND 184: the rule-shut review's rows 10-19 with a wind-up (unit_spec_abil wind_up_time)\n"
                       + "".join('\t\t["%s"] = %s,\n' % (k, v) for k, v in WIND))

EVALS = '''
-- ============================================================================
-- ROUND 184 - THE RULE-SHUT REVIEW, ROWS 10-19 (user 2026-11-20: "Up to #19 ruled").
--   enemy_area_drain_hurt (Soul Stealer x2, "B with the 75% gate"): the area drain while the caster is at or below
--     DRAIN_HURT_PCT health, so the caster's own heal (0.8% a second for 12 s) lands in full.
--   enemy_ground_melee_cluster (Raging Tornado, row 19 "A"): on the ground under the enemy in melee with the most enemy
--     value in melee within CLUSTER_M of it (cluster_pick, as the shooters' cluster of round 174); the caster standing
--     still for an animated cast; the pre-cast re-check keeps that enemy in melee (eg_mode "melee"). No clearance: the
--     damage hits enemies only.
-- ============================================================================
FOURTH.DRAIN_HURT_PCT = 75   -- user ruling 2026-11-20 (rows 16-17: "with the 75% gate")

function FOURTH.evaluate_enemy_area_drain_hurt(unit, routing)
	FOURTH.eg_mode = "shot"
	FOURTH.shot_kind = nil
	if routing then return %NO% end
	local hp = FOURTH.health_pct(unit)
	if type(hp) ~= "number" or hp > FOURTH.DRAIN_HURT_PCT then return %NO% end
	local why = FOURTH.evaluate_enemy_area_drain(unit, routing)
	if not why then return why end
	%RET_AH%
end

function FOURTH.evaluate_enemy_ground_melee_cluster(unit, routing)
	FOURTH.eg_mode = "melee"
	if routing or not FOURTH.blob_still(unit) then return nil end
	local best, n, v = FOURTH.cluster_pick(unit, FOURTH.enemy_list(FOURTH.in_melee_now), false)
	if best == nil then return nil end
	FOURTH.eg_enemy = best.unit
	FOURTH.eg_arm = "melee"
	FOURTH.eg_caster_su = FOURTH.eg_fresh_caster_su(unit)
	FOURTH.cast_target = best.unit
	FOURTH.eg_ground = true
	local etype = "enemy"
	pcall(function() etype = tostring(best.unit:type()) end)
	return string.format("the enemy in melee with the most enemy value in melee near it (%s: %d unit(s), value %.0f within %dm)"
		.. " - on the ground under it", etype, n, v, FOURTH.CLUSTER_M)
end

'''
RET = {
    True: {"%NO%": "nil", "%RET_AH%": 'return string.format("caster at %d%% health (<= %d%%); ", math.floor(hp), FOURTH.DRAIN_HURT_PCT) .. why'},
    False: {"%NO%": "false", "%RET_AH%": "return why"},
}
MAP_OLD = "\tenemy_area_drain = FOURTH.evaluate_enemy_area_drain,\n"
MAP_NEW = MAP_OLD + ("\tenemy_area_drain_hurt = FOURTH.evaluate_enemy_area_drain_hurt,   -- ROUND 184\n"
                     "\tenemy_ground_melee_cluster = FOURTH.evaluate_enemy_ground_melee_cluster,\n")
LBL_OLD = ('\tenemy_area_drain = "When armed and standing still, fires on the enemy infantry in range worth the most per '
           'soldier, with enough soldiers for every strike",\n')
LBL_NEW = LBL_OLD + (
    '\tenemy_area_drain_hurt = "When armed, at 75% health or less and standing still, fires on the enemy infantry in range '
    'worth the most per soldier, with enough soldiers for every strike",   -- ROUND 184\n'
    '\tenemy_ground_melee_cluster = "When armed and standing still, fires on the ground under the enemy in melee with the '
    'most enemy value fighting near it",\n')
CARD_OLD = '\tenemy_area_drain = "Fires[ when standing still{ANIM},] on the most valuable enemy infantry of {AREA}+ men",\n'
CARD_NEW = CARD_OLD + (
    '\tenemy_area_drain_hurt = "Fires below 75% health[, when standing still{ANIM},] on the most valuable enemy infantry '
    'of {AREA}+ men",   -- ROUND 184\n'
    '\tenemy_ground_melee_cluster = "Fires[ when standing still{ANIM},] under the thickest melee of enemies",\n')
ANCHOR = "FOURTH.evaluators = {\n"
AREA_GEN = re.compile(r"-- GENERATED by tools/gen_shot_tables\.py from phase_junc and phases \(max_damaged_entities.*?"
                      r"\nFOURTH\.load_area_table\(\)\n", re.S)
SHOT_GEN = re.compile(r"-- GENERATED by tools/gen_shot_tables\.py from unit_spec_abil, projectiles and the invalid-usage.*?"
                      r"\nFOURTH\.load_shot_table\(\)\n", re.S)
AREA_RE = r'trigger = "enemy_(?:area_drain|area_drain_hurt|most_models)",\n\t\tbadge = "[^"]+",\n\t\tkeys = \{ "([^"]+)" \}'


def main():
    assert AH in GS.FAMILIES, "add enemy_area_drain_hurt to gen_shot_tables.FAMILIES first"
    for path, live in ((SRC, True), (ANN, False)):
        s = open(path, encoding="utf-8", newline="").read()
        for r in ROWS:
            assert ('"%s"' % r[4]) not in s, r[4]
            assert ('marker = "%s"' % r[1]) not in s, r[1]
        assert "evaluate_enemy_area_drain_hurt" not in s
        before = s.count("\t{ marker = ")
        s = sub(s, RESTOCK, NEW_ENTRIES + RESTOCK)
        s = sub(s, HOLD_OLD, HOLD_NEW)
        s = sub(s, WIND_OLD, WIND_NEW)
        s = sub(s, MAP_OLD, MAP_NEW)
        s = sub(s, LBL_OLD, LBL_NEW)
        s = sub(s, CARD_OLD, CARD_NEW)
        ev = EVALS
        for a, b in RET[live].items():
            ev = ev.replace(a, b)
        assert "%NO%" not in ev and "%RET_" not in ev
        s = sub(s, ANCHOR, ev + ANCHOR)
        assert s.count("\t{ marker = ") == before + 10
        open(path, "w", encoding="utf-8", newline="").write(s)
        print(os.path.basename(path), "entries", before, "->", before + 10)
    # the SHOT table (the shot families' keys) and the AREA table (the area families' keys)
    src_now = open(SRC, encoding="utf-8").read()
    ks = GS.keys_in(src_now)
    area_keys = set(m.group(1) for m in re.finditer(AREA_RE, src_now))
    print("SHOT keys:", len(ks), "AREA keys:", len(area_keys))
    shot_blk = GS.lua_block(GS.derive(ks))
    area_blk = GS.area_block(GS.area_rows(area_keys))
    for path in (SRC, ANN):
        s = open(path, encoding="utf-8", newline="").read()
        assert len(SHOT_GEN.findall(s)) == 1 and len(AREA_GEN.findall(s)) == 1
        s = SHOT_GEN.sub(lambda m: shot_blk, s)
        s = AREA_GEN.sub(lambda m: area_blk, s)
        open(path, "w", encoding="utf-8", newline="").write(s)
    RT.main()


if __name__ == "__main__":
    main()
