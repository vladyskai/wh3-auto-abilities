#!/usr/bin/env python3
"""Round 178, second pass: the review doc's RULED texts for rows 23-24, 29, 36-41 and 44-45 (written before the
round-177 commit; the first pass built the older proposals).

  rows 23, 24, 29 (user: "should not be unused if there are less models in the unit. Maybe preference for numerous
    entities units"; "a minimum of 16 units for both"): NEW enemy_most_models - the visible enemy unit in range with
    the most models alive, counted up to the ability's own cap (the GENERATED AREA table: 75 / 25), the most value per
    soldier among equals; a 16-model floor; the caster standing still. Chain Lightning x2, The Soulstealer.
  rows 36-41 (user: "Yes pls", no melee arm): the roots go to the existing enemy_fast_near_ally.
  rows 44-45 (user: "makes sense to also add root"): Glory Seeker x2 on enemy_fast_or_melee (commander class on both
    arms: eg_class_ok guards the fast pick and the melee pick).
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"


def move(marker, old, new):
    a = '\t-- ROUND 178 (score-3 review): %s\n\t{ marker = "%s", ' % (old, marker)
    b = '\t-- ROUND 178 (score-3 review): %s\n\t{ marker = "%s", ' % (new, marker)
    return (a, b)


R = []
for m in ("the_soulstealer", "spell_heavens_chain_lightning_bound", "spell_heavens_chain_lightning_bound_unit"):
    R.append(move(m, "enemy_area_drain", "enemy_most_models"))
for m in ("soulnetter", "net_of_amyntok", "spider_web_attack", "warp_gaze", "warpstiletto", "pack_trap"):
    R.append(move(m, "enemy_fast_or_melee", "enemy_fast_near_ally"))
for m in ("glory_seeker", "glory_seeker_upgraded"):
    R.append(move(m, "enemy_melee", "enemy_fast_or_melee"))
TRIG = [("the_soulstealer", "The Soulstealer", "enemy_area_drain", "enemy_most_models"),
        ("spell_heavens_chain_lightning_bound", "Chain Lightning", "enemy_area_drain", "enemy_most_models"),
        ("spell_heavens_chain_lightning_bound_unit", "Chain Lightning", "enemy_area_drain", "enemy_most_models"),
        ("soulnetter", "Gilellion's Soulnetter", "enemy_fast_or_melee", "enemy_fast_near_ally"),
        ("net_of_amyntok", "Net of Amyntok", "enemy_fast_or_melee", "enemy_fast_near_ally"),
        ("spider_web_attack", "Spiderweb Attack", "enemy_fast_or_melee", "enemy_fast_near_ally"),
        ("warp_gaze", "Warp Gaze", "enemy_fast_or_melee", "enemy_fast_near_ally"),
        ("warpstiletto", "Warpstiletto", "enemy_fast_or_melee", "enemy_fast_near_ally"),
        ("pack_trap", "Pack Trap", "enemy_fast_or_melee", "enemy_fast_near_ally"),
        ("glory_seeker", "Glory Seeker", "enemy_melee", "enemy_fast_or_melee"),
        ("glory_seeker_upgraded", "Glory Seeker Upgraded", "enemy_melee", "enemy_fast_or_melee")]
for m, n, old, new in TRIG:
    R.append(('{ marker = "%s", name = "%s", trigger = "%s",' % (m, n, old),
              '{ marker = "%s", name = "%s", trigger = "%s",' % (m, n, new)))
R += [
    # the header of the round-178 block
    ("--   enemy_fast_or_melee (the roots): a visible fast enemy closing on our units (the round-135 fast-enemy pick) first -\n",
     "--   enemy_fast_or_melee (Glory Seeker x2, user: \"makes sense to also add root\"): a visible fast enemy closing on\n"
     "--     our units (the round-135 fast-enemy pick; the entry's commander class guards it) first -\n"),
    ("--   enemy_low_health_noncommander (Eye of Khorne; user: \"the below 20% highest value unit that is not a lord or\n",
     "--   enemy_most_models (Chain Lightning x2, The Soulstealer; user: \"should not be unused if there are less models in\n"
     "--     the unit. Maybe preference for numerous entities units\", \"a minimum of 16 units for both\"): the visible enemy\n"
     "--     unit in range with the most models alive, counted up to the ability's own cap (the GENERATED AREA table), the\n"
     "--     most value per soldier among equals; at least FOURTH.MODELS_FLOOR models; the caster standing still.\n"
     "--   The 6 plain roots (rows 36-41, user: \"Yes pls\", no melee arm) ride the existing enemy_fast_near_ally.\n"
     "--   enemy_low_health_noncommander (Eye of Khorne; user: \"the below 20% highest value unit that is not a lord or\n"),
    # the picker kind
    ("\t\telseif kind == \"area\" then   -- ROUND 158: enough soldiers left for every strike\n",
     "\t\telseif kind == \"models\" then   -- ROUND 178: the most models, counted up to the cap; the floor\n"
     "\t\t\tok_kind = (e.men >= FOURTH.MODELS_FLOOR)\n"
     "\t\t\ts1 = math.min(e.men, FOURTH.area_min())\n"
     "\t\t\ts2 = e.vps or 0\n"
     "\t\telseif kind == \"area\" then   -- ROUND 158: enough soldiers left for every strike\n"),
    ("\tif kind == \"drain\" or kind == \"area\" then\n",
     "\tif kind == \"drain\" or kind == \"area\" or kind == \"models\" then   -- ROUND 178: models\n"),
    ("\t\t\tif kind == \"area\" and e.men < FOURTH.area_min() then return false end\n",
     "\t\t\tif kind == \"area\" and e.men < FOURTH.area_min() then return false end\n"
     "\t\t\tif kind == \"models\" and e.men < FOURTH.MODELS_FLOOR then return false end   -- ROUND 178\n"),
    # wiring
    ("\tenemy_fast_fire_melee = FOURTH.evaluate_enemy_fast_fire_melee,\n",
     "\tenemy_fast_fire_melee = FOURTH.evaluate_enemy_fast_fire_melee,\n"
     "\tenemy_most_models = FOURTH.evaluate_enemy_most_models,   -- ROUND 178 (second pass)\n"),
    ("\tenemy_fast_fire_melee = \"When armed, fires at a fast enemy closing on our units, else at an enemy under our fire, else at one in melee\",\n",
     "\tenemy_fast_fire_melee = \"When armed, fires at a fast enemy closing on our units, else at an enemy under our fire, else at one in melee\",\n"
     "\tenemy_most_models = \"When armed and standing still, fires on the enemy unit in range with the most soldiers (16 at least)\",\n"),
    ("\tenemy_fast_fire_melee = \"Fires at a charging enemy, else at one we shoot, else at one in melee\",\n",
     "\tenemy_fast_fire_melee = \"Fires at a charging enemy, else at one we shoot, else at one in melee\",\n"
     "\tenemy_most_models = \"Fires[ when standing still{ANIM},] on the enemy unit with the most soldiers, 16 at least\",\n"),
]
NEW_FN = '''
-- ROUND 178 (second pass): the user's model floor for Chain Lightning and The Soulstealer ("a minimum of 16 units")
FOURTH.MODELS_FLOOR = 16

function FOURTH.evaluate_enemy_most_models(unit, routing)
	FOURTH.eg_mode = "shot"
	FOURTH.shot_kind = nil
	if routing or not FOURTH.blob_still(unit) then return nil end
	local m = FOURTH.blob_map(false)
	local e, s = FOURTH.shot_pick(unit, m, "models", false, true)
	if e == nil then return nil end
	FOURTH.shot_take(unit, e, "models", true, true)
	return FOURTH.shot_reason(unit, e, "the enemy unit with the most models, standing still",
		string.format("%d models alive, counted up to %d (floor %d), value %.1f per soldier", e.men, FOURTH.area_min(),
			FOURTH.MODELS_FLOOR, e.vps or 0))
end
'''
FN_ANCHOR = "\nfunction FOURTH.evaluate_melee_healthy(unit, routing)\n"

for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    for a, b in R:
        assert s.count(a) == 1, (path[-12:], a[:90], s.count(a))
        s = s.replace(a, b)
    assert s.count(FN_ANCHOR) == 1
    s = s.replace(FN_ANCHOR, NEW_FN + FN_ANCHOR)
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path[-36:], "patched")
