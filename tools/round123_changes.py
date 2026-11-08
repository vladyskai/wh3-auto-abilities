#!/usr/bin/env python3
"""Round 123 (harness 122): the hex batch, per the user's per-ability ruling
(2026-10-27), applied identically to the live source and the annotated copy.

User ruling, verbatim:
  "Of Group A, the ones that have no speed effects should have the
   melee_unwavering trigger. The ones that reduce the enemies speed should
   trigger in melee or when charging. ...
   Of Group B, ... The one with effect only -40 melee defense makes sense only
   when the enemy is in melee. It does not make sense to activate it when the
   enemy is shot ... The Transfix (dlc29 key) should be the same ... Flash bomb
   can be the same ... Daemonic possesion would make sense only before a cast,
   so I say we do not automate that one. Hunter of champions is okay for
   enemy_engaged_or_shot."

Changes:
  * 4 entries on melee_unwavering (no speed effect): Rival Hide Talisman,
    Seductive Glory, Vine Dragon Scale, Dark Mace.
  * 3 entries on charge_or_melee (enemy speed reduction): Seduction,
    Song of Enthrallment, Smoke Bomb.
  * 3 entries on the NEW enemy_melee trigger (enemy in range AND in melee,
    never the under-missile-fire arm): No Escape, Transfix (dlc29 hex key),
    Flash Bomb.
  * Hunter of Champions: the upgraded key joins the existing entry
    (enemy_engaged_or_shot, same 100 m range).
  * Charge-gate holds for the two 3-use keys: No Escape 90 s, Transfix 120 s.
  * The enemy_melee evaluator, its map line and its tooltip line.
Daemonic Possession is NOT automated (user decision).
Table: 697 entries / 748 keys -> 707 / 759; evaluator families 45 -> 46.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
ARMY = r"C:\Users\vlady\AppData\Local\Temp\wh3\army_spec.tsv"

NEW = [
    # (marker, name, trigger, key, range_real)
    ("rival_hide_talisman", "Rival Hide Talisman", "melee_unwavering", "wh2_main_item_abilities_rival_hide_talisman", None),
    ("seductive_glory", "Seductive Glory", "melee_unwavering", "wh3_main_lord_abilities_seductive_glory", None),
    ("vine_dragon_scale", "Vine Dragon Scale", "melee_unwavering", "wh2_dlc15_item_abilities_vine_dragon_scale", None),
    ("dark_mace", "Dark Mace", "melee_unwavering", "wh3_dlc23_weapon_abilities_dark_mace", None),
    ("seduction", "Seduction", "charge_or_melee", "wh2_dlc11_lord_abilities_seduction", None),
    ("song_of_enthrallment", "Song of Enthrallment", "charge_or_melee", "wh2_dlc11_lord_abilities_song_of_enthrallment", None),
    ("smoke_bomb", "Smoke Bomb", "charge_or_melee", "wh_dlc06_unit_abilities_smoke_bomb", None),
    ("no_escape", "No Escape", "enemy_melee", "wh3_main_character_abilities_no_escape", 100),
    ("transfix_hex", "Transfix", "enemy_melee", "wh3_dlc29_lord_abilities_transfix", 100),
    ("flash_bomb", "Flash Bomb", "enemy_melee", "wh_pro01_lord_abilities_flash_bomb", 75),
]
HOC_NEW = "wh2_dlc17_character_abilities_hunter_of_champions_upgraded"

HEADER = """
	-- ============================================================================
	-- ROUND 123 (harness 122): THE HEX BATCH, one trigger PER ABILITY from what
	-- its effect changes (user ruling 2026-10-27):
	--   * no speed effect -> melee_unwavering (in melee, not wavering, cast on
	--     self; the 35 m enemy aura is then centred on the fight): Rival Hide
	--     Talisman, Seductive Glory, Vine Dragon Scale, Dark Mace.
	--   * reduces ENEMY SPEED -> charge_or_melee (this unit charges or is in
	--     melee), so the slow lands as the fight starts, never on an enemy that
	--     is only passing by: Seduction, Song of Enthrallment, Smoke Bomb.
	--   * melee-only debuff on ONE enemy -> enemy_melee (NEW: an enemy in range
	--     that is IN MELEE; being shot does NOT count, because melee defence only
	--     matters in melee): No Escape, Transfix (the dlc29 HEX key, a different
	--     ability from the self-buff Transfix above), Flash Bomb.
	--   The 70% bounds: 100 m -> 70 m, 75 m -> 52 m (FOURTH.ENEMY_CAST).
	--   Daemonic Possession is deliberately NOT here (user: it only makes sense
	--   just before a friendly spell, so it is not automated).
	-- ============================================================================
"""

ENTRY_ANCHOR = """	{ marker = "all_consuming_hatred", name = "All-Consuming Hatred", trigger = "melee_unwavering",
		badge = "zz_auto_badge_all_consuming_hatred",
		keys = { "wh3_dlc27_unit_abilities_consuming_hatred" },
		ox = 0, oy = 0 },
"""

HOC_OLD = """		keys = { "wh_dlc08_character_abilities_hunter_of_champions" },"""
HOC_NEWTXT = """		keys = { "wh_dlc08_character_abilities_hunter_of_champions",
			-- ROUND 123: the UPGRADED twin (same 100 m range, same armour /
			-- melee-defence hex) shares this marker, badge and trigger.
			"wh2_dlc17_character_abilities_hunter_of_champions_upgraded" },"""

HOLD_ANCHOR = """local charge_gate = {
	hold_s = {
"""
HOLD_ADD = """		-- ROUND 123: the two 3-use hexes on the new enemy_melee trigger
		-- (unit_spec_abil.tsv num_uses = 3, recharge_time in seconds).
		["wh3_main_character_abilities_no_escape"] = 90,
		["wh3_dlc29_lord_abilities_transfix"] = 120,
"""

EVAL_ANCHOR = """function FOURTH.evaluate_enemy_ground_area(unit, routing)
	return FOURTH.eg_pick_enemy(unit, routing, true)
end
"""
EVAL_ADD = """
-- THE MELEE-ONLY ENEMY-UNIT EVALUATOR (round 123). THE USER'S RULE: a hex
-- whose effect is a melee-only stat (melee defence -40 on No Escape and
-- Transfix) "makes sense only when the enemy is in melee. It does not make
-- sense to activate it when the enemy is shot." So: the SAME shared picker as
-- enemy_engaged_or_shot (enemy alive, a valid target, within this entry's own
-- 70% bound, the closest wins), with the under-missile-fire arm switched OFF
-- by the existing melee-only flag (the one Gate of Khorne uses). The cast is
-- aimed at the chosen ENEMY UNIT (ground = false), and the shared pre-cast
-- re-check requires that enemy to be STILL in melee and still within the
-- bound, or the cast is skipped and not spent.
function FOURTH.evaluate_enemy_melee(unit, routing)
	FOURTH.eg_melee_only = true
	return FOURTH.eg_pick_enemy(unit, routing, false)
end
"""

MAP_ANCHOR = "\tenemy_engaged_or_shot = FOURTH.evaluate_enemy_engaged_or_shot,\n"
MAP_ADD = ("\t-- ROUND 123: an enemy in range that is IN MELEE (no missile arm).\n"
           "\tenemy_melee = FOURTH.evaluate_enemy_melee,\n")

TIP_ANCHOR = ('\tenemy_engaged_or_shot = "When armed, fires when an enemy unit in range is in melee '
              'or under missile fire",\n')
TIP_ADD = '\tenemy_melee = "When armed, fires on the closest enemy unit in range that is fighting in melee",\n'


def block():
    out = HEADER
    for marker, name, trig, key, rr in NEW:
        out += '\t{ marker = "%s", name = "%s", trigger = "%s",\n' % (marker, name, trig)
        out += '\t\tbadge = "zz_auto_badge_%s",\n' % marker
        out += '\t\tkeys = { "%s" },\n' % key
        if rr is not None:
            out += "\t\trange_real = %d,\n" % rr
        out += "\t\tox = 0, oy = 0 },\n"
    return out


army = set()
with open(ARMY, encoding="utf-8", errors="replace") as f:
    f.readline()
    for ln in f:
        c = ln.rstrip("\n").split("\t")
        if c and c[0].strip() and not ln.startswith("#"):
            army.add(c[0].strip())
hits = [k for *_, k, _ in NEW if k in army] + ([HOC_NEW] if HOC_NEW in army else [])
assert not hits, ("army-bar key in the batch", hits)


def put(s, anchor, add, after=True):
    assert s.count(anchor) == 1, (anchor[:60], s.count(anchor))
    return s.replace(anchor, (anchor + add) if after else (add + anchor), 1)


for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    assert "\r\n" not in s, path
    for marker, _, _, key, _ in NEW:
        assert ('"%s"' % key) not in s, (path, "key already present", key)
        assert ('marker = "%s"' % marker) not in s, (path, "marker already present", marker)
    assert ('"%s"' % HOC_NEW) not in s
    assert "evaluate_enemy_melee(" not in s and "\tenemy_melee = " not in s
    n_e = s.count("\t{ marker = ")
    tc = {t: s.count('trigger = "%s"' % t) for t in ("melee_unwavering", "charge_or_melee", "enemy_melee")}
    s = put(s, ENTRY_ANCHOR, block())
    assert s.count(HOC_OLD) == 1, (path, s.count(HOC_OLD))
    s = s.replace(HOC_OLD, HOC_NEWTXT, 1)
    s = put(s, HOLD_ANCHOR, HOLD_ADD)
    s = put(s, EVAL_ANCHOR, EVAL_ADD)
    s = put(s, MAP_ANCHOR, MAP_ADD)
    s = put(s, TIP_ANCHOR, TIP_ADD)
    assert s.count("\t{ marker = ") == n_e + 10
    assert s.count('trigger = "melee_unwavering"') == tc["melee_unwavering"] + 4
    assert s.count('trigger = "charge_or_melee"') == tc["charge_or_melee"] + 3
    assert s.count('trigger = "enemy_melee"') == 3
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("%s: entries %d -> %d, melee_unwavering %d -> %d, charge_or_melee %d -> %d, enemy_melee 0 -> 3" % (
        path.split("\\")[-1], n_e, n_e + 10, tc["melee_unwavering"], tc["melee_unwavering"] + 4,
        tc["charge_or_melee"], tc["charge_or_melee"] + 3))
