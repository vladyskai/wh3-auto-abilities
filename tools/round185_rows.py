#!/usr/bin/env python3
"""Round 185 (user, 2026-11-20: "Review ended, implement pls"; rulings read from the Claude Docs review "Rule-shut
abilities review", rev 127, dropdowns and threads).

Rows 20-64 of docs\\WH3_rule_shut_review_2026-11-20.md. BUILT (33 entries):
  20-32 the safe self-centred blasts: "Recommended" = melee_unwavering ("Like Bloodstorm", round 159).
  33-34 Glacial Blast, Thundermace: "Recommended" = melee_clear.
  35 Cellular Instability: "Recommended" = melee_clear_block (60 soldiers in its 25 m blast, as Land Mine).
  36 Splode da Big 'Un!: "Recommended" = last_stand_clear ("Necrotic last").
  37-38 Battle Howl x2: "B" = NEW aura_charge_only (the caster, or an ally within 70% of the 55 m aura, charges).
  39 Twilight Horn II: "B" = self_or_ally_charge (itself or the nearest charging ally, as Red Fury).
  40 Silver Horn of Vengeance: "B" = NEW aura_charge_only (35 m aura: 24 m).
  41 Swiftness of Itzl: "Recommended" = charge_only.
  54 Bonecrusher: "Recommended" = enemy_blob_vortex (not on flying targets: the game's rule).
  55 Master Rune of Immolation: "Last stand" (option B) = last_stand_clear; its blast is a BOMBARDMENT (gen_vortex_tables
     reads it since round 185: 6 m shells + 4 m spread = 10 m, affects allies).
  56 Beastlord's Gaze: "Recommended" = ally_melee_risk.
  57 Fog of the Damned: "A" = enemy_ground_melee_cluster (round 184's Raging Tornado pick), not on flying targets; a
     ground-only key, so it joins enemy_ground_keys.
  58 Locus of Contagion: "Recommended" = enemy_melee_near (55 m aura: 38 m).
  59 Mad Cap Mushrooms: "Recommended" = self_recharging.
  60 Mirror of Knowledge: "Recommended" = enemy_fast_near_ally, ground form (enemy_ground_keys); its range is -1 in the
     game data, so the entry is unbounded (the precedent of The Tallyman's Blades Upgraded and Magma Storm).
  61 Offering to the Gods: "Recommended" = NEW ally_offering (ally_value_melee with the floor: no missile unit, at least
     FOURTH.OFFERING_MIN_MEN = 30 men; the game's own rule excludes Lords, Heroes and large units).
  62-63 Seismic Snare x2: "Recommended" = slow_aura (35 m aura).
  64 The Black Gem of Gnar: "Recommended" = self_last_stand.
CLOSED (no code): rows 42-48 (stealth, "Recommended" = keep shut), rows 49-53 (mutual exclusivity, parked with the
stances). Row 18 (Warpstorm Scroll) keeps its round-184 build: the rule-10 question has no answer in the doc.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamedata_paths as GP  # noqa: E402
import gen_vortex_tables as GV  # noqa: E402
import round171_regen_tables as RT  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

MU, MC = "melee_unwavering", "melee_clear"
# (row, marker, name, family, key, {field: value})
ROWS = [
    (20, "alakanash", "Alakanash, the Staff of Power", MU, "wh3_dlc29_item_abilities_alakanash_the_staff_of_power", {}),
    (21, "ark_of_sotek", "Ark of Sotek", MU, "wh2_dlc12_unit_abilities_ark_of_sotek", {}),
    (22, "celestial_sweep", "Celestial Sweep", MU, "wh3_dlc24_lord_abilities_celestial_sweep", {}),
    (23, "prayer_destruction", "Destruction", MU, "wh3_dlc29_spell_bound_prayer_destruction", {}),
    (24, "eruption", "Eruption", MU, "wh3_main_character_abilities_eruption", {}),
    (25, "ferocious_destruction", "Ferocious Destruction", MU, "wh3_dlc29_spell_bound_prayer_ferocious_destruction", {}),
    (26, "kill_for_khorne", "Kill for Khorne!", MU, "wh3_dlc26_character_abilities_kill_for_khorne", {}),
    (27, "sonic_boom", "Sonic Boom", MU, "wh3_main_daemon_head_abilities_sonic_boom", {}),
    (28, "hammer_of_harry", "The Hammer of Harry", MU, "wh3_pro11_weapon_abilities_the_hammer_of_harry", {}),
    (29, "venom_wave", "Venom Wave", MU, "wh2_dlc09_lord_abilities_venom_wave", {}),
    (30, "wrath_of_ptra", "Wrath of Ptra", MU, "wh2_dlc09_lord_abilities_wrath_of_ptra", {}),
    (31, "whirlwind_of_death", "Whirlwind of Death", MU, "wh3_dlc25_unit_abilities_whirlwind_of_death", {}),
    (32, "whirlwind_of_death_upgraded", "Whirlwind of Death Upgraded", MU,
     "wh3_dlc25_unit_abilities_whirlwind_of_death_upgraded", {}),
    (33, "glacial_blast", "Glacial Blast", MC, "wh3_main_character_abilities_glacial_blast", {}),
    (34, "thundermace", "Thundermace", MC, "wh3_main_weapon_abilities_thundermace", {}),
    (35, "cellular_instability", "Cellular Instability", "melee_clear_block", "wh2_dlc16_unit_abilities_cellular_instability", {}),
    (36, "splode_da_big_one", "Splode da Big 'Un!", "last_stand_clear", "wh3_dlc26_unit_abilities_splode_da_big_one", {}),
    (37, "battle_howl_hounds", "Battle Howl", "aura_charge_only", "wh3_dlc29_ability_bound_prayer_battle_howl", {"aura_real": 55}),
    (38, "battle_howl", "Battle Howl", "aura_charge_only", "wh3_dlc29_spell_bound_prayer_battle_howl", {"aura_real": 55}),
    (39, "twilight_horn_ii", "Twilight Horn II", "self_or_ally_charge", "wh2_dlc16_item_abilities_twilight_horn_ii",
     {"ally_range_real": 200}),
    (40, "silver_horn_of_vengeance", "Silver Horn of Vengeance", "aura_charge_only",
     "wh_main_item_abilities_silver_horn_of_vengeance", {"aura_real": 35}),
    (41, "swiftness_of_itzl", "Swiftness of Itzl", "charge_only", "wh2_main_character_abilities_swiftness_of_itzl", {}),
    (54, "bonecrusher", "Bonecrusher", "enemy_blob_vortex", "wh3_dlc26_spell_bound_bonecrusher",
     {"range_real": 200, "target_class": '"not_flying"'}),
    (55, "master_rune_of_immolation", "Master Rune of Immolation", "last_stand_clear",
     "wh2_dlc17_rune_abilities_master_rune_of_immolation", {}),
    (56, "beastlords_gaze", "Beastlord's Gaze", "ally_melee_risk", "wh2_twa03_lord_abilities_beastlords_gaze",
     {"ally_range_real": 200}),
    (57, "fog_of_the_damned", "Fog of the Damned", "enemy_ground_melee_cluster", "wh3_dlc29_bound_deep_fog_of_the_damned",
     {"range_real": 200, "target_class": '"not_flying"'}),
    (58, "locus_of_contagion", "Locus of Contagion", "enemy_melee_near", "wh3_main_character_abilities_locus_of_contagion",
     {"aura_real": 55}),
    (59, "mad_cap_mushrooms", "Mad Cap Mushrooms", "self_recharging", "wh_main_hero_abilities_mad_cap_mushrooms", {}),
    (60, "mirror_of_knowledge", "Mirror of Knowledge", "enemy_fast_near_ally", "wh3_dlc24_item_abilities_mirror_of_knowledge",
     {"unbounded": "true"}),
    (61, "offering_to_the_gods", "Offering to the Gods", "ally_offering", "wh3_dlc27_lord_abilities_offering_to_the_gods",
     {"ally_range_real": 100}),
    (62, "seismic_snare", "Seismic Snare", "slow_aura", "wh2_dlc14_unit_abilities_seismic_snare", {"aura_real": 35}),
    (63, "seismic_snare_stormfiend", "Seismic Snare", "slow_aura", "wh3_dlc29_unit_abilities_stormfiend_seismic_snare",
     {"aura_real": 35}),
    (64, "black_gem_of_gnar", "The Black Gem of Gnar", "self_last_stand", "wh3_dlc23_item_abilities_black_gem_of_gnar", {}),
]
KEYS = [r[4] for r in ROWS]
FAMILY = {r[4]: r[3] for r in ROWS}
GROUND = ["wh3_dlc29_bound_deep_fog_of_the_damned", "wh3_dlc24_item_abilities_mirror_of_knowledge"]
FIELD_ORDER = ("range_real", "ally_range_real", "aura_real", "unbounded", "target_class")


def sub(s, a, b, n=1):
    assert s.count(a) == n, (a[:80], s.count(a))
    return s.replace(a, b)


def entry(row, marker, name, trig, key, fields):
    lines = ['\t-- ROUND 185 (rule-shut review row %d)' % row,
             '\t{ marker = "%s", name = "%s", trigger = "%s",' % (marker, name, trig),
             '\t\tbadge = "zz_auto_badge_%s",' % marker,
             '\t\tkeys = { "%s" },' % key]
    for f in FIELD_ORDER:
        if f in fields:
            lines.append("\t\t%s = %s," % (f, fields[f]))
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
for _r in ROWS:   # rule 3: the ranges and auras are the game's
    u, fl = USA[_r[4]], _r[5]
    for f in ("range_real", "ally_range_real"):
        if f in fl:
            assert float(u["target_intercept_range"]) == fl[f], (_r[4], f, u["target_intercept_range"])
    if "aura_real" in fl:
        assert float(u["effect_range"]) == fl["aura_real"], (_r[4], u["effect_range"])
    if "unbounded" in fl:
        assert float(u["target_intercept_range"]) < 0, _r[4]
HOLD = [(k, num(USA[k]["recharge_time"])) for k in KEYS if int(float(USA[k]["num_uses"])) > 1]
WIND = [(k, num(USA[k]["wind_up_time"])) for k in KEYS if float(USA[k]["wind_up_time"] or 0) > 0]
print("multi-use keys:", len(HOLD))
print("wind-up keys:", len(WIND))

RESTOCK = '\t{ marker = "restock", name = "Restock!", trigger = "ally_ammo_low",'
NEW_ENTRIES = "".join(entry(*r) for r in ROWS)
HOLD_OLD = "\thold_s = {\n"
HOLD_NEW = HOLD_OLD + ("\t\t-- ROUND 185: the rule-shut review's rows 20-64 with more than one use (recharge_time)\n"
                       + "".join('\t\t["%s"] = %s,\n' % (k, v) for k, v in HOLD))
WIND_OLD = "\twind_up_s = {\n"
WIND_NEW = WIND_OLD + ("\t\t-- ROUND 185: the rule-shut review's rows 20-64 with a wind-up (unit_spec_abil wind_up_time)\n"
                       + "".join('\t\t["%s"] = %s,\n' % (k, v) for k, v in WIND))
GK_OLD = "enemy_ground_keys = {\n"
GK_NEW = GK_OLD + ("\t\t-- ROUND 185: Fog of the Damned, Mirror of Knowledge (target_ground only: placed on the enemy's ground)\n"
                   + "".join('\t\t["%s"] = true,\n' % k for k in GROUND))
FILT_OLD = '\tif f == "not_missile" then return not FOURTH.class_member(unit, "missile") end   -- ROUND 174\n'
FILT_NEW = FILT_OLD + (
    '\t-- ROUND 185: Offering to the Gods kills 3 of the ally\'s soldiers: no missile unit, at least OFFERING_MIN_MEN men\n'
    '\tif f == "offering" then\n'
    '\t\tif FOURTH.class_member(unit, "missile") then return false end\n'
    '\t\tlocal ok_n, men = pcall(function() return unit:number_of_men_alive() end)\n'
    '\t\treturn ok_n and type(men) == "number" and men >= FOURTH.OFFERING_MIN_MEN\n'
    '\tend\n')
CAF_OLD = "\tself_or_ally_charge = true,   -- ROUND 171\n"
CAF_NEW = CAF_OLD + "\tally_offering = true,   -- ROUND 185: the game's rule (no Lords or Heroes, no large units)\n"

EVALS = '''
-- ============================================================================
-- ROUND 185 - THE RULE-SHUT REVIEW, ROWS 20-64 (user 2026-11-20: "Review ended, implement pls").
--   aura_charge_only (Battle Howl x2, Silver Horn of Vengeance, "B"): the caster charging (the charge window), or one of
--     our units within the aura's 70% reach charging; no wavering arm (these give no morale).
--   ally_offering (Offering to the Gods, "Recommended"): the most valuable ally in melee within reach, no missile unit,
--     at least OFFERING_MIN_MEN soldiers (the offering kills 3 of them); the game's own rule keeps Lords, Heroes and
--     large units out (ATARGET c and l).
-- ============================================================================
FOURTH.OFFERING_MIN_MEN = 30   -- user ruling 2026-11-20 (row 61: "30+ men", 3 lost = 10% or less)

function FOURTH.evaluate_aura_charge_only(unit, routing)
	if routing then return nil end
	local own = FOURTH.charge_moment(unit)
	if own ~= nil then return "the caster: " .. own .. " (aura charge)" end
	local u, g = FOURTH.ours_in_reach(unit, function(x) return FOURTH.charge_moment(x) ~= nil end)
	if u == nil then return nil end
	return string.format("a unit of ours %.1fm away (aura %sm) is charging", g, tostring(FOURTH.ah_range_m))
end

function FOURTH.evaluate_ally_offering(unit, routing)
	FOURTH.ab_filter = "offering"
	return FOURTH.ab_pick_ally(unit, routing, "value_melee")
end

'''
MAP_OLD = "\tenemy_ground_melee_cluster = FOURTH.evaluate_enemy_ground_melee_cluster,\n"
MAP_NEW = MAP_OLD + ("\taura_charge_only = FOURTH.evaluate_aura_charge_only,   -- ROUND 185\n"
                     "\tally_offering = FOURTH.evaluate_ally_offering,\n")
LBL_OLD = ('\tenemy_ground_melee_cluster = "When armed and standing still, fires on the ground under the enemy in melee with the '
           'most enemy value fighting near it",\n')
LBL_NEW = LBL_OLD + (
    '\taura_charge_only = "When armed, fires when this unit or a friendly unit within its aura charges",   -- ROUND 185\n'
    '\tally_offering = "When armed, fires on the most valuable friendly unit of 30 or more soldiers in melee (no missile '
    'units), cast on it",\n')
CARD_OLD = '\tenemy_ground_melee_cluster = "Fires[ when standing still{ANIM},] under the thickest melee of enemies",\n'
CARD_NEW = CARD_OLD + (
    '\taura_charge_only = "Fires when it or a nearby ally charges",   -- ROUND 185\n'
    '\tally_offering = "Fires on the most valuable ally of 30+ men in melee; no missile units",\n')
ANCHOR = "FOURTH.evaluators = {\n"
VORTEX_GEN = re.compile(r"-- GENERATED by tools/gen_vortex_tables\.py from unit_spec_abil and battle_vortexs.*?"
                        r"\nFOURTH\.load_vortex_table\(\)\n", re.S)


def main():
    for path in (SRC, ANN):
        s = open(path, encoding="utf-8", newline="").read()
        for r in ROWS:
            assert ('"%s"' % r[4]) not in s, r[4]
            assert ('marker = "%s"' % r[1]) not in s, r[1]
        assert "evaluate_aura_charge_only" not in s
        before = s.count("\t{ marker = ")
        s = sub(s, RESTOCK, NEW_ENTRIES + RESTOCK)
        s = sub(s, HOLD_OLD, HOLD_NEW)
        s = sub(s, WIND_OLD, WIND_NEW)
        s = sub(s, GK_OLD, GK_NEW)
        s = sub(s, FILT_OLD, FILT_NEW)
        s = sub(s, CAF_OLD, CAF_NEW)
        s = sub(s, MAP_OLD, MAP_NEW)
        s = sub(s, LBL_OLD, LBL_NEW)
        s = sub(s, CARD_OLD, CARD_NEW)
        s = sub(s, ANCHOR, EVALS + ANCHOR)
        assert s.count("\t{ marker = ") == before + len(ROWS)
        open(path, "w", encoding="utf-8", newline="").write(s)
        print(os.path.basename(path), "entries", before, "->", before + len(ROWS))
    src_now = open(SRC, encoding="utf-8").read()
    vrows = GV.derive(GV.keys_in(src_now))
    print("VORTEX rows:", len(vrows))
    blk = GV.lua_block(vrows)
    for path in (SRC, ANN):
        s = open(path, encoding="utf-8", newline="").read()
        assert len(VORTEX_GEN.findall(s)) == 1
        s = VORTEX_GEN.sub(lambda m: blk, s)
        open(path, "w", encoding="utf-8", newline="").write(s)
    RT.main()


if __name__ == "__main__":
    main()
