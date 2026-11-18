#!/usr/bin/env python3
"""Round 178 (harness 177): rows 23-55 of docs\\WH3_score3_review_2026-11-18.md (user, 2026-11-18: "Approve rows
23-55. Row 56 stays the same."), with the rulings written into the doc since (row 49 Oil Flask: KEEP; row 53 Eye of
Khorne: "the below 20% highest value unit that is not a lord or hero").

Changed:
  23, 24, 29  Chain Lightning (bound), (bound, unit), The Soulstealer -> enemy_area_drain (exists)
  30, 31      Whip of Misery, Word of Pain                            -> enemy_melee_or_shooting (exists)
  36-41       Gilellion's Soulnetter, Net of Amyntok, Spiderweb Attack, Warp Gaze, Warpstiletto, Pack Trap
                                                                      -> NEW enemy_fast_or_melee (a fast enemy closing
                                                                         first, else the closest enemy in melee)
  42, 43      Prey of Anath Raema, Net Dem Up!                        -> NEW enemy_fast_fire_melee (fast, else under our
                                                                         fire, else in melee)
  44, 45      Glory Seeker, Glory Seeker Upgraded                     -> enemy_melee (commander class kept)
  46          Prey of the Blood God                                   -> enemy_commander_value (commander class kept)
  47, 48, 50, 51 Void Pendulum, Word of Change, Dweomer Leach Orb, Slann Gold -> enemy_spellcaster (the commander proxy
                                                                         class is dropped: the spellcaster list replaces it)
  53          Eye of Khorne                                           -> stays on enemy_low_health_noncommander, whose
                                                                         ONLY entry it is; the pick now ranks the highest
                                                                         live value first (the ruling), then the lower
                                                                         health, then the closer
  54          Trophy Heads                                            -> SPLIT: the base key keeps "Lord or Hero in
                                                                         melee"; the Daemon Wings key gets its own entry,
                                                                         "the closest enemy in melee" (no class)
Unchanged: 25-27 (keep), 28 Surprise Squig (the data: it SUMMONS Explosive Squigs; the proposal misread it, a new
proposal follows), 32-35 and 52 (ruled), 49 Oil Flask (ruled KEEP), 55 Siegebreaker (the data: its projectile deals
100 + 100 AP to the unit hit, so it harms units; the row's "if not, close" does not apply), 56 (user).
"""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

# marker -> (old trigger, new trigger, drop target_class)
MOVES = {
    "spell_heavens_chain_lightning_bound": ("enemy_blob", "enemy_area_drain", False),
    "spell_heavens_chain_lightning_bound_unit": ("enemy_blob", "enemy_area_drain", False),
    "the_soulstealer": ("enemy_ground_melee", "enemy_area_drain", False),
    "whip_of_misery": ("enemy_engaged_or_shot", "enemy_melee_or_shooting", False),
    "word_of_pain": ("enemy_engaged_or_shot", "enemy_melee_or_shooting", False),
    "soulnetter": ("enemy_engaged_or_shot", "enemy_fast_or_melee", False),
    "net_of_amyntok": ("enemy_engaged_or_shot", "enemy_fast_or_melee", False),
    "spider_web_attack": ("enemy_engaged_or_shot", "enemy_fast_or_melee", False),
    "warp_gaze": ("enemy_engaged_or_shot", "enemy_fast_or_melee", False),
    "warpstiletto": ("enemy_engaged_or_shot", "enemy_fast_or_melee", False),
    "pack_trap": ("enemy_engaged_or_shot", "enemy_fast_or_melee", False),
    "prey_of_anath_raema": ("enemy_engaged_or_shot", "enemy_fast_fire_melee", False),
    "net_dem_up": ("enemy_engaged_or_shot", "enemy_fast_fire_melee", False),
    "glory_seeker": ("enemy_engaged_or_shot", "enemy_melee", False),
    "glory_seeker_upgraded": ("enemy_engaged_or_shot", "enemy_melee", False),
    "prey_of_the_blood_god": ("enemy_engaged_or_shot", "enemy_commander_value", False),
    "void_pendulum": ("enemy_engaged_or_shot", "enemy_spellcaster", True),
    "word_of_change": ("enemy_engaged_or_shot", "enemy_spellcaster", True),
    "dweomer_leach_orb": ("enemy_commander_value", "enemy_spellcaster", True),
    "slann_gold": ("enemy_commander_value", "enemy_spellcaster", True),
}
NEW = ["enemy_fast_or_melee", "enemy_fast_fire_melee"]
TIP = {
    "enemy_fast_or_melee": "When armed, fires at a fast enemy closing on our units, else at the closest enemy in melee",
    "enemy_fast_fire_melee": "When armed, fires at a fast enemy closing on our units, else at an enemy under our fire, else at one in melee",
}
CARD = {
    "enemy_fast_or_melee": "Fires at a charging enemy, else at one in melee",
    "enemy_fast_fire_melee": "Fires at a charging enemy, else at one we shoot, else at one in melee",
}
TROPHY_OLD = ('\t{ marker = "trophy_heads", name = "Trophy Heads", trigger = "enemy_melee",\n'
              '\t\tbadge = "zz_auto_badge_trophy_heads",\n'
              '\t\tkeys = { "wh2_main_lord_abilities_trophy_heads",\n'
              '\t\t\t"wh3_main_daemon_wings_abilities_trophy_heads" },\n'
              '\t\trange_real = 150,\n'
              '\t\ttarget_class = "commander",\n'
              '\t\tox = 0, oy = 0 },\n')
TROPHY_NEW = ('\t-- ROUND 178 (score-3 review row 54): the entry is split - the base key keeps its game rule (Lords and Heroes\n'
              '\t-- only); the Daemon Wings key has no such rule and gets its own entry\n'
              '\t{ marker = "trophy_heads", name = "Trophy Heads", trigger = "enemy_melee",\n'
              '\t\tbadge = "zz_auto_badge_trophy_heads",\n'
              '\t\tkeys = { "wh2_main_lord_abilities_trophy_heads" },\n'
              '\t\trange_real = 150,\n'
              '\t\ttarget_class = "commander",\n'
              '\t\tox = 0, oy = 0 },\n'
              '\t{ marker = "trophy_heads_daemon_wings", name = "Trophy Heads", trigger = "enemy_melee",\n'
              '\t\tbadge = "zz_auto_badge_trophy_heads_daemon_wings",\n'
              '\t\tkeys = { "wh3_main_daemon_wings_abilities_trophy_heads" },\n'
              '\t\trange_real = 150,\n'
              '\t\tox = 0, oy = 0 },\n')

CODE = r'''
-- ============================================================================
-- ROUND 178 - THE SCORE-3 REVIEW, ROWS 23-55 (user, 2026-11-18: "Approve rows 23-55").
--   enemy_fast_or_melee (the roots): a visible fast enemy closing on our units (the round-135 fast-enemy pick) first -
--     a root stops the charge - else the closest enemy in melee.
--   enemy_fast_fire_melee (roots that also open the target to our missiles): fast first, else the closest enemy under
--     our missile fire, else the closest in melee (the shared picker with fire preferred to melee).
--   enemy_low_health_noncommander (Eye of Khorne; user: "the below 20% highest value unit that is not a lord or
--     hero"): the highest live value first, then the lower health, then the closer.
-- ============================================================================
function FOURTH.evaluate_enemy_fast_or_melee(unit, routing)
	if routing then return nil end
	local r = FOURTH.evaluate_enemy_fast_near_ally(unit, routing)
	if r then return r end
	FOURTH.shot_clear()
	FOURTH.eg_mode = nil   -- the fast arm set its own re-check mode
	FOURTH.eg_melee_only = nil
	return FOURTH.evaluate_enemy_melee(unit, routing)
end

function FOURTH.evaluate_enemy_fast_fire_melee(unit, routing)
	if routing then return nil end
	local r = FOURTH.evaluate_enemy_fast_near_ally(unit, routing)
	if r then return r end
	FOURTH.shot_clear()
	FOURTH.eg_mode = nil   -- the fast arm set its own re-check mode
	FOURTH.eg_melee_only = nil
	FOURTH.eg_fire_first = true
	r = FOURTH.eg_pick_enemy(unit, routing, false)
	FOURTH.eg_fire_first = nil
	return r
end
'''

HEALTH_OLD = ('\t\t\t\t\t\t\t\telseif mode == "health" then\n'
              '\t\t\t\t\t\t\t\t\tif hp < best_hp then\n'
              '\t\t\t\t\t\t\t\t\t\tbetter = true\n'
              '\t\t\t\t\t\t\t\t\telseif hp == best_hp and gap ~= nil and (best_gap == nil or gap < best_gap) then\n'
              '\t\t\t\t\t\t\t\t\t\tbetter = true\n'
              '\t\t\t\t\t\t\t\t\tend\n')
HEALTH_NEW = ('\t\t\t\t\t\t\t\telseif mode == "health" then\n'
              '\t\t\t\t\t\t\t\t\t-- ROUND 178 (Eye of Khorne; user: "the below 20% highest value unit that is not a\n'
              '\t\t\t\t\t\t\t\t\t-- lord or hero"): the highest live value first, then the lower health, then the closer\n'
              '\t\t\t\t\t\t\t\t\tlocal v, bv = FOURTH.unit_value(enemy), FOURTH.unit_value(best_enemy)\n'
              '\t\t\t\t\t\t\t\t\tif v > bv then\n'
              '\t\t\t\t\t\t\t\t\t\tbetter = true\n'
              '\t\t\t\t\t\t\t\t\telseif v == bv and hp < best_hp then\n'
              '\t\t\t\t\t\t\t\t\t\tbetter = true\n'
              '\t\t\t\t\t\t\t\t\telseif v == bv and hp == best_hp and gap ~= nil and (best_gap == nil or gap < best_gap) then\n'
              '\t\t\t\t\t\t\t\t\t\tbetter = true\n'
              '\t\t\t\t\t\t\t\t\tend\n')

R = [
    # the shared enemy picker: fire before melee when asked (Prey of Anath Raema, Net Dem Up!)
    ('(arm == "melee" and best_arm ~= "melee")',
     '(arm == (FOURTH.eg_fire_first and "missile" or "melee") and best_arm ~= (FOURTH.eg_fire_first and "missile" or "melee"))'),
    # Eye of Khorne's pick: the highest value first
    (HEALTH_OLD, HEALTH_NEW),
    # the new code before the round-177 melee_healthy evaluator
    ("function FOURTH.evaluate_melee_healthy(unit, routing)\n",
     "%CODE%\nfunction FOURTH.evaluate_melee_healthy(unit, routing)\n"),
    ("\tmelee_healthy = FOURTH.evaluate_melee_healthy,\n",
     "\tmelee_healthy = FOURTH.evaluate_melee_healthy,\n"
     + "".join("\t%s = FOURTH.evaluate_%s,%s\n" % (f, f, "   -- ROUND 178" if i == 0 else "") for i, f in enumerate(NEW))),
    ('\tmelee_healthy = "When armed, fires in melee while above 50% health",\n',
     '\tmelee_healthy = "When armed, fires in melee while above 50% health",\n'
     + "".join('\t%s = "%s",%s\n' % (f, TIP[f], "   -- ROUND 178" if i == 0 else "") for i, f in enumerate(NEW))),
    ('\tmelee_healthy = "Fires in melee while above 50% health",\n',
     '\tmelee_healthy = "Fires in melee while above 50% health",\n'
     + "".join('\t%s = "%s",%s\n' % (f, CARD[f], "   -- ROUND 178" if i == 0 else "") for i, f in enumerate(NEW))),
    (TROPHY_OLD, TROPHY_NEW),
]


def move_entries(s):
    for m, (old, new, drop) in MOVES.items():
        pat = re.compile(r'(\t\{ marker = "%s", name = "[^"]+", trigger = )"%s",\n((?:\t\t[^\n]*\n)*?)(\t\tox = 0, oy = 0 \},\n)'
                         % (re.escape(m), re.escape(old)))
        assert len(pat.findall(s)) == 1, (m, old, len(pat.findall(s)))

        def sub(x):
            body = x.group(2)
            if drop:
                assert body.count('\t\ttarget_class = "commander",\n') == 1, m
                body = body.replace('\t\ttarget_class = "commander",\n', "")
            return ('\t-- ROUND 178 (score-3 review): %s\n' % new + x.group(1) + '"%s",\n' % new + body + x.group(3))
        s = pat.sub(sub, s)
    return s


def main():
    for path in (SRC, ANN):
        s = open(path, encoding="utf-8", newline="").read()
        if "ROUND 178" in s:
            print(path, "already patched")
            continue
        s = move_entries(s)
        for o, n in R:
            n = n.replace("%CODE%", CODE)
            assert s.count(o) == 1, (path[-12:], o[:80], s.count(o))
            s = s.replace(o, n)
        assert "\u2014" not in s
        open(path, "w", encoding="utf-8", newline="").write(s)
        print(path, "patched")


if __name__ == "__main__":
    main()
