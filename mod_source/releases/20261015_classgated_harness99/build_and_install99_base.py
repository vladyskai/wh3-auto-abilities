"""Build the mod pack, verify it, install it. One WebSocket session, then done.

Pack contents (housekeeping 20261004 - the two experiment probes are RETIRED):
  script/battle/mod/zz_test_deadly_onslaught.lua   the main mod (trigger + right-click toggle)
  ui/templates/zz_auto_badge.twui.xml              the auto badge template
  ui/zz_auto/auto_badge.png  ui/zz_auto/blank.png  the badge art
  ui/common ui/special_ability_tooltip.twui.xml    the tooltip's right-click line, filled in

The throwaway probes (zz_probe_unit_reads.lua, zz_probe_ui_text.lua) shipped until
2026-10-04; their sources are preserved in releases/20261004_probe_sources_retired/
and must NOT ship again (the pack-contents check below fails if a zz_probe_ path returns)

No HUD button, no icon files, no localisation file: the control is a right-click on the
ability's own icon, and the hint is a plain line in the tooltip layout.

ROUND v93: the appended tooltip line is now ONE SHORT clause per ability,
composed from the trigger each entry rides (FOURTH.TRIGGER_TIP[trigger] ->
ability.tip); the old generic 'fires by itself while the unit charges'
sentence is REMOVED from the shipped twui.xml.

ROUND v94: ACCUSATION'S automatic activation - a new reusable evaluator
`enemy_engaged_or_shot` fires when an enemy unit in range is in melee OR
under missile fire; the chosen enemy is the CAST TARGET (never the owner),
cast via the round-4-proven bench_fresh fresh-handle route. Accusation moves
from melee_unwavering (481 -> 480) to the new trigger; the table stays
579 entries / 605 keys.

ROUND v95: THE STANDING 70% RANGE RULE (set by the user, ruled ABSOLUTE -
\"...No exceptions.\"). EVERY trigger-range constant is re-derived as
floor(0.70 * the ability's REAL game-data range): GLORIOUS DEATH 55->38,
VERMINKING / METALLURGY / WAVERING 35->24, BLOOD SACRIFICE / EAT DA RUNTS
100->70 (target_intercept_range; no aura) and ACCUSATION 75->52. The old
field-tuned 25 m Glorious Death gate is replaced by 38 m at the user's
direction. The rule ships as FOURTH.RANGE_FRACTION = 0.70.

ROUND v96: THE ACCUSATION MOVE-ORDER ROOT CAUSE. The observer probe
(zz_probe_dist, tick 59) proved the offer test trusted the engine's loose
unit_in_range reach read: 'CAND-FIRST ... dist=81.3m first_passing_test=engine
engine_unit_in_range=t our_52_test=f our_75_test=f' - the mod offered and cast
at 81.3 m, so the engine WALKED the caster in. The offer test is now the 70%
CONSTANT ONLY (unit:unit_distance(enemy) <= FOURTH.ACCUSATION_RANGE_M = 52 m),
the engine helper is REMOVED from the offer path, and the log prints the REAL
edge-to-edge distance (unit:unit_distance, battle_unit.lua:160) at the target
choice and the pre-cast re-check.

ROUND v97: THE REST OF CLASS A. 97 of the 98 enemy-aimed entries from the
audit (Accusation 263 already done) now fire at the ENEMY: 88 ride the
existing enemy_engaged_or_shot trigger and 9 ride the new enemy_ground_area
trigger (perform_special_ability_ground on the chosen ENEMY's ground). Each
entry carries its own REAL target_intercept_range (range_real) mapped at load
to ONE named 70% constant per real range (12 constants, floor(real*0.70)); the
offer test is unit:unit_distance(enemy) <= that constant ONLY - never the
engine's unit_in_range. melee_unwavering 480 -> 383.

ROUND v98: CLASS B (ally-targeted effects cast on self). 17 of the 34
Class-B entries from the audit now cast ON THE CHOSEN ALLY across four new
families (ally_melee_buff 11 / ally_heal 3 / ally_heal_melee 1 / ally_wavering
2); Stay Here, I'll Get Help! (whose ally pick already shipped) gains the cast
target and its own 70% bound; Meat Feast is an ARMY-BAR ability and is SKIPPED
(standing rule 10); 15 entries need a user ruling. Each implemented entry
carries its own REAL target_intercept_range (ally_range_real) mapped at load to
ONE named 70% constant per real range (5 constants, floor(real*0.70)); the offer
test is unit:unit_distance(ally) <= that constant ONLY - never the engine's
unit_in_range - and the cast goes through the FRESH caster controller AND the
FRESH ally unit, re-enumerated the SAME tick. melee_unwavering 383 -> 373,
charge_or_melee 29 -> 26, ushoran_health 41 -> 38, melee_health75 2 -> 1.
"""
import hashlib
import json
import shutil
import os
from websockets.sync.client import connect

WS_URL = "ws://127.0.0.1:45127/ws"
SRC_ROOT = r"C:/Users/vlady/Desktop/WH3_mod/mod_source"

FILES = [
    (SRC_ROOT + "/script/battle/mod/zz_test_deadly_onslaught.lua",
     "script/battle/mod/zz_test_deadly_onslaught.lua"),
    (SRC_ROOT + "/ui/templates/zz_auto_badge.twui.xml",
     "ui/templates/zz_auto_badge.twui.xml"),
    (SRC_ROOT + "/ui/zz_auto/blank.png", "ui/zz_auto/blank.png"),
    (SRC_ROOT + "/ui/zz_auto/auto_badge.png",
     "ui/zz_auto/auto_badge.png"),
    (SRC_ROOT + "/ui/common ui/special_ability_tooltip.twui.xml",
     "ui/common ui/special_ability_tooltip.twui.xml"),
]

OUT_PACK = SRC_ROOT + "/dist/zz_test_deadly_onslaught.pack"
GAME_PACK = r"C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III/data/zz_test_deadly_onslaught.pack"

HINT = "Automatic: click the M/A badge to switch automatic use on or off"


class Client:
    def __init__(self, url):
        self.ws = connect(url, max_size=None, open_timeout=15)
        self.next_id = 1
        print("  hello:", json.dumps(json.loads(self.ws.recv(timeout=15))))

    def send(self, command):
        req_id = self.next_id
        self.next_id += 1
        self.ws.send(json.dumps({"id": req_id, "data": command}))
        while True:
            msg = json.loads(self.ws.recv(timeout=180))
            if msg.get("id") == req_id:
                return msg.get("data")
            print("  (unsolicited)", json.dumps(msg)[:160])


def step(label, command):
    print(f"\n== {label}")
    resp = c.send(command)
    print(f"  <= {json.dumps(resp)[:200]}")
    return resp


for p in (OUT_PACK, GAME_PACK):
    if os.path.exists(p):
        os.remove(p)
        print("removed stale:", p)

hashes = {}
for _src, _in_pack in FILES:
    _data = open(_src, "rb").read()
    hashes[_in_pack] = (len(_data), hashlib.sha256(_data).hexdigest())
    print(f"source {_src.split('/')[-1]:34s} {len(_data):>8d} bytes  sha256 {hashes[_in_pack][1][:32]}")

c = Client(WS_URL)
step("1 select game", {"SetGameSelected": ["warhammer_3", False]})
key = step("2 new pack", "NewPack")["String"]
step("3 add the main script and the four ui files",
     {"AddPackedFiles": [key, [f[0] for f in FILES], [{"File": f[1]} for f in FILES], None]})
step("4 type = Movie", {"SetPackFileType": [key, "Movie"]})

info = step("5 list contents", {"GetPackFileDataForTreeView": key})
container, files = info["ContainerInfoVecRFileInfo"]
in_pack_paths = sorted(f["path"] for f in files)
expected = sorted(_in_pack for _src, _in_pack in FILES)
print("   container:", container["pfh_file_type"], "| files:", in_pack_paths)
assert in_pack_paths == expected, f"pack contents wrong: {in_pack_paths} != {expected}"

ok_all = True
for _src, in_pack in FILES:
    raw = c.send({"GetPackedFileRawData": [key, in_pack]})
    packed = bytes(raw["VecU8"])
    got = hashlib.sha256(packed).hexdigest()
    want_len, want = hashes[in_pack]
    ok = (got == want and len(packed) == want_len)
    ok_all = ok_all and ok
    print(f"   {in_pack:48s} {len(packed):>8d} bytes  MATCHES SOURCE: {ok}")
assert ok_all, "content mismatch - refusing to install"

# what we shipped must contain what we expect
t_raw = bytes(c.send({"GetPackedFileRawData": [key, "ui/common ui/special_ability_tooltip.twui.xml"]})["VecU8"])
t_txt = t_raw.decode("utf-8", "replace")
print("\n== 6 what the pack must contain")
script_txt = open(SRC_ROOT + "/script/battle/mod/zz_test_deadly_onslaught.lua",
                  encoding="utf-8", errors="replace").read()
print(f"   tooltip hint line present                 : {HINT in t_txt}")
print(f"   the double-click toggles are gone         : "
      f"{'Double Click Unit Card' not in script_txt}"
      f" and {'ComponentLDBLClickUp' not in script_txt}")
dead = sum(script_txt.count(t) for t in ('zz_rclick', 'check_rclick_property'))
print(f"   dead property-route code left behind      : {dead} (want 0)")
assert HINT in t_txt, "tooltip hint missing"
# ROUND v93 (the per-ability tooltip line - nothing above is loosened): the appended
# tooltip line is now composed PER ENTRY from the trigger the entry actually rides;
# the old one-size generic sentence is GONE.
assert "this ability fires by itself while the unit charges" not in t_txt, \
    "the old generic tooltip sentence is back in the shipped twui.xml"
assert "FOURTH.TRIGGER_TIP = {" in script_txt, "the per-trigger tooltip wording map is missing"
assert "ability.tip = FOURTH.TRIGGER_TIP[ability.trigger]" in script_txt, \
    "the per-entry tooltip wiring is missing"
assert "this ability fires by itself while the unit charges" not in script_txt, \
    "the old generic tooltip sentence is back in the script"
for _tip in ("When armed, fires when this unit is in melee",
             "When armed, fires when an ally in range is wavering",
             "When armed, fires when this unit is tired or worse",
             "When armed, fires when a Slayer ally in range is in melee",
             "When armed, fires on the lowest-health ally in range when it is at or below 75% health"):
    assert _tip in script_txt, "a required tooltip wording is missing: " + _tip
assert "Double Click Unit Card" not in script_txt, "the double-click command handler should be gone"
assert "ComponentLDBLClickUp" not in script_txt, "the double-click component listener should be gone"
# the claim path copies the engine's key value before ANY string operation
# (as_plain_string) and the scan probe reports keytype/copyok/lenok; the old
# AddScriptEventReporter gate died with the call itself.
assert "badge creation deferred to the tick" in script_txt, "the deferred badge creation line is missing"
assert "as_plain_string" in script_txt, "the engine-key copy helper is missing from the claim path"
assert "scan probe: keytype=" in script_txt, "the scan probe keytype line is missing"
# round 7: the bounded re-scan loop (the brisk window; the dead local-ceiling
# slot stays freed so the chunk compiles under Lua's 200-local limit).
assert "local brisk_walk_until = -1" in script_txt, "the round-7 window local is missing"
assert "brisk_walk_until = ui_ticks + 48" in script_txt, "the fresh-window open is missing"
assert "CHARGE_ORDER_TOLERANCE_M" not in script_txt, "the freed local-ceiling slot came back"
assert "zz_auto_" in script_txt, "the badge component is missing from the script"
assert "onslaught" in script_txt, "the ability marker is missing from the script"
assert "SetText" in script_txt, "the badge letter switch (SetText) is missing"
for tok in ("zz_rclick", "check_rclick_property"):
    assert tok not in script_txt, f"dead right-click code left in the script: {tok}"

# round 35 (extensions - nothing above is loosened): the second ability
# (Foe-Seeker) must ship, driven by the ABILITIES table, and the 60/90 s
# timers must NOT come back.
assert "foe_seeker" in script_txt, "the foe_seeker ability is missing from the script"
assert "wh_main_character_abilities_foe_seeker" in script_txt, "the foe_seeker key is missing"
assert "wh_dlc03_character_abilities_foe_seeker" in script_txt, "the foe_seeker dlc key variant is missing"
assert "zz_auto_badge_fs" in script_txt, "the Foe-Seeker badge id is missing from the script"
# ROUND v81 (the three approved trigger changes - nothing above is loosened):
#   * Deadly Onslaught fires on the charge window OR in melee (both arms on);
#   * Foe-Seeker's trigger is "tired" - read via battle_unit:fatigue_state(),
#     exact matching only, a one-time notice when unreadable;
#   * the "running" trigger is DELETED - it must never come back.
assert "elseif ability.trigger == \"running\" then" not in script_txt, "the deleted running trigger is back in the script"
assert "reason = \"running\"" not in script_txt, "the old running reason text is back in the script"
assert "fast = unit:is_moving_fast()," in script_txt, "the charge detector's fast read is missing"
assert "melee = unit:is_in_melee()," in script_txt, "the charge detector's melee read is missing"
assert "local FIRE_ON_MELEE  = true" in script_txt, "the approved in-melee arm is not switched on"
assert 'marker = "foe_seeker", name = "Foe-Seeker", trigger = "tired"' in script_txt, "the fatigue trigger is missing from the script"
assert "FOURTH.fatigue_states = {" in script_txt, "the exact-match fatigue state map is missing"
assert "FOURTH.fatigue_fire = {" in script_txt, "the tired-or-worse fire set is missing"
assert "function FOURTH.fatigue_state(unit)" in script_txt, "the fatigue reader is missing"
assert "return unit:fatigue_state() end" in script_txt, "the plain fatigue getter read is missing"
assert "foe_seeker fatigue: read UNAVAILABLE" in script_txt, "the one-time unreadable notice is missing"
assert "foe_seeker fatigue: UNRECOGNISED value" in script_txt, "the unrecognised-state notice is missing"
assert "string.find(" not in script_txt, "a string.find call is back in the script"
assert "check_readiness" in script_txt, "the readiness gate is missing from the script"
assert "GUARD_SECONDS = 2" in script_txt, "the short 2 s guard is missing from the script"
for tok in ("ABILITY_RECHARGE_SECONDS", "ACTIVATION_BRAKE_TICKS", "MIN_SECONDS_BETWEEN_FIRES"):
    assert tok not in script_txt, f"a 60/90 s timer token is back in the script: {tok}"

# ROUND v82 (the approved in-melee-self batch + critique-2 item 8 - nothing
# above is loosened): every ability entry carries its own evaluate(unit,
# routing), wired at load from the trigger name; the if/elseif trigger chain
# is GONE; the approved batch (28 entries, 29 keys, all on blood_lust's
# melee_unwavering rule) ships with its ONE shared evaluator and its own
# badges.
assert "ability.trigger ==" not in script_txt, "the old trigger chain is back in the script"
assert "function FOURTH.evaluate_charge(unit, routing)" in script_txt, "the charge evaluator is missing"
assert "function FOURTH.evaluate_tired(unit, routing)" in script_txt, "the tired evaluator is missing"
assert "function FOURTH.evaluate_melee(unit, routing)" in script_txt, "the melee evaluator is missing"
assert "function FOURTH.evaluate_melee_low_morale(unit, routing)" in script_txt, "the melee_low_morale evaluator is missing"
assert "function FOURTH.evaluate_in_melee_self(unit, routing)" in script_txt, "the shared in-melee-self evaluator is missing"
assert "FOURTH.evaluators = {" in script_txt, "the trigger -> evaluator map is missing"
assert "ability.evaluate = FOURTH.evaluators[ability.trigger]" in script_txt, "the entry wiring loop is missing"
assert "local reason = ability.evaluate(unit, routing)" in script_txt, "the single dispatch call is missing"
assert 'marker = "aether_sword"' in script_txt, "the batch's first entry is missing"
assert 'marker = "strike_of_nehekhara"' in script_txt, "the batch's last entry is missing"
assert "wh3_dlc20_weapon_abilities_aether_sword" in script_txt, "the batch's first key is missing"
assert "wh2_dlc09_character_abilities_strike_of_nehekhara" in script_txt, "the batch's last key is missing"
assert "wh3_main_lord_abilities_deathbringer" in script_txt and "wh3_main_lord_abilities_deathbringer_upgraded" in script_txt, "the deathbringer keys are missing"
assert 'badge = "zz_auto_badge_aether_sword"' in script_txt, "a batch badge id is missing from the script"
assert 'badge = "zz_auto_badge_deathbringer"' in script_txt, "the deathbringer badge id is missing from the script"

# ROUND v83 (BLOCK 2 - the second in-melee-self batch + the five new trigger
# types). Nothing above is loosened. The 27 approved simple entries ride the
# SAME shared evaluator; the four new-trigger entries ship with their own
# evaluators; the summoned Foe-Seeker is a THIRD key on the existing foe_seeker
# entry; and the context read, the ally-target slot and the Ushoran hysteresis
# field all ship.
BLOCK2_SIMPLE = [
    ("dolorous_blade", "wh_dlc07_hero_abilities_dolorous_blade"),
    ("dragon_spear", "wh2_dlc16_weapon_abilities_dragon_spear"),
    ("dreaded_duelist", "wh2_dlc11_lord_abilities_dreaded_duelist"),
    ("dwarf_gouger", "wh2_main_weapon_abilities_dwarf_gouger"),
    ("enrage", "wh_pro04_unit_abilities_enrage"),
    ("entice", "wh3_dlc29_unit_abilities_entice"),
    ("everyone_has_their_price", "wh3_main_lord_abilities_everyone_has_their_price"),
    ("evisceration", "wh2_dlc16_hero_abilities_evisceration"),
    ("eye_jabber", "wh3_dlc29_spell_bound_eye_jabber"),
    ("eye_gouger", "wh3_dlc29_spell_bound_eye_gouger"),
    ("eye_of_the_storm", "wh3_main_lord_abilities_eye_of_the_storm"),
    ("faiths_bastion", "wh_main_hero_abilities_faiths_bastion"),
    ("fangsword_of_eltharion", "wh2_dlc15_weapon_abilities_fangsword_of_eltharion"),
    ("feint_and_reposte", "wh2_main_lord_abilities_feint_and_reposte"),
    ("filth_mace", "wh_main_weapon_abilities_filth_mace"),
    ("fluid_injection", "wh2_dlc16_unit_abilities_fluid_injection"),
    ("gaze_of_khorne", "wh3_dlc26_lord_abilities_gaze_of_khorne"),
    ("fury_of_the_land", "wh3_dlc24_character_abilities_fury_of_the_land"),
    ("fury_of_ursun", "wh3_main_lord_abilities_fury_of_ursun"),
    ("ghal_maraz", "wh_main_weapon_abilities_ghal_maraz"),
    ("giant_leap", "wh3_dlc24_character_abilities_giant_leap"),
    ("gitsnik", "wh_main_weapon_abilities_gitsnik"),
    ("gotrek_doom", "wh2_pro08_character_abilities_gotrek_doom"),
    ("shield_of_faith_upgraded", "wh_dlc04_spell_bound_shield_of_faith_upgraded"),
    ("great_gutgouger", "wh3_dlc26_weapon_abilities_great_gutgouger"),
    ("halo_of_maidenly_wrath", "wh2_dlc14_lord_abilities_halo_of_maidenly_wrath"),
    ("hammer_axe_of_skoll", "wh3_dlc29_weapon_active_hammer_axe_of_skoll"),
]
for _marker, _key in BLOCK2_SIMPLE:
    assert 'marker = "%s"' % _marker in script_txt, "block-2 marker missing: " + _marker
    assert 'badge = "zz_auto_badge_%s"' % _marker in script_txt, "block-2 badge missing: " + _marker
    assert '"%s"' % _key in script_txt, "block-2 key missing: " + _key
# the corrected single-l key must be used; the tracker's double-l typo must not
# appear anywhere.
assert "wh2_dlc11_lord_abilities_dreaded_duelist" in script_txt, "the corrected 'dreaded_duelist' key is missing"
assert "wh2_dlc11_lord_abilities_dreaded_duelist".replace("duelist", "duellist") not in script_txt, \
    "the double-l 'dreaded_duellist' typo came back"
# the four own-evaluator trigger entries
BLOCK2_NEWT = [
    ("eagle_feather_torc", "wh3_dlc27_item_abilities_eagle_feather_torc", "barrier_broken"),
    ("fangspike", "wh3_dlc26_weapon_abilities_fangspike", "charge_or_melee"),
    ("ghoul_king_of_ushoran", "wh2_dlc11_lord_abilities_ghoul_king_of_ushoran", "ushoran_health"),
    ("glorious_death", "wh3_dlc25_lord_abilities_glorious_death", "glorious_death"),
]
for _marker, _key, _trig in BLOCK2_NEWT:
    assert 'marker = "%s"' % _marker in script_txt, "new-trigger marker missing: " + _marker
    assert '"%s"' % _key in script_txt, "new-trigger key missing: " + _key
    assert 'trigger = "%s"' % _trig in script_txt, "new-trigger trigger name missing: " + _trig
    assert 'badge = "zz_auto_badge_%s"' % _marker in script_txt, "new-trigger badge missing: " + _marker
assert "wh_main_character_abilities_foe_seeker_summoned" in script_txt, "the summoned Foe-Seeker key is missing"
for _fn in ("function FOURTH.evaluate_barrier_broken(unit, routing)",
            "function FOURTH.evaluate_charge_or_melee(unit, routing)",
            "function FOURTH.evaluate_ushoran_health(unit, routing)",
            "function FOURTH.evaluate_glorious_death(unit, routing)"):
    assert _fn in script_txt, "a block-2 evaluator is missing: " + _fn
for _map in ("barrier_broken = FOURTH.evaluate_barrier_broken,",
             "charge_or_melee = FOURTH.evaluate_charge_or_melee,",
             "ushoran_health = FOURTH.evaluate_ushoran_health,",
             "glorious_death = FOURTH.evaluate_glorious_death,"):
    assert _map in script_txt, "a block-2 evaluator map entry is missing: " + _map
assert "function FOURTH.context_value(unit, field)" in script_txt, "the context-value reader is missing"
assert "FOURTH.cast_target = nil" in script_txt and "uc:perform_special_ability(ability_key, target or unit)" in script_txt, \
    "the ally-target dispatch is missing"
assert "FOURTH.ushoran_high" not in script_txt, "the removed Ushoran hysteresis field came back"
assert 'string.format("barrier broken (BarrierHp %.0f/%.0f)"' in script_txt, "the barrier-broken reason is missing"
assert 'reason = "in melee (charge or melee)"' in script_txt, "the fangspike melee reason is missing"
assert 'string.format("health %d%% (<= 75%%)"' in script_txt, "the ushoran health reason is missing"
# ROUND v85 (job 1): GLORIOUS DEATH CASTS ON SELF. The trigger is unchanged,
# but every firing arm now writes the OWNER into FOURTH.cast_target - the old
# ally-target reasons and the ally cast-target write are GONE.
assert 'reason = "slayer in melee (self-cast)"' in script_txt, "the Slayer self-cast reason is missing"
assert 'reason = "self in melee (self-cast)"' in script_txt, "the self self-cast reason is missing"
assert 'reason = "slayer ally in melee (priority)"' not in script_txt, "the removed ally-target reason came back"
assert 'reason = "self slayer fallback (in melee)"' not in script_txt, "the removed ally self-fallback reason came back"
assert 'reason = "ally in melee (priority)"' not in script_txt, "the removed any-ally fallback reason came back"
assert 'reason = "self fallback (no other melee ally)"' not in script_txt, "the removed any-ally self reason came back"
assert "FOURTH.cast_target = best_unit" not in script_txt, "the removed ally cast-target write came back"
assert script_txt.count("FOURTH.cast_target = unit") == 2, "the self-cast writes are not exactly two"
# ROUND v85 (job 2): BLOCK 3 - 38 approved entries (35 in-melee-self on the
# existing melee_unwavering evaluator + 3 charge-or-melee on the existing
# charge_or_melee evaluator). NO new evaluator, NO new chunk locals.
BLOCK3_SELF = [
    ("legbiter", "wh3_dlc29_weapon_abilities_legbiter"),
    ("hellfire_sword", "wh_main_weapon_abilities_hellfire_sword"),
    ("helm_of_discord", "wh_main_weapon_abilities_helm_of_discord"),
    ("helm_of_many_eyes", "wh_dlc01_item_passive_helm_of_many_eyes"),
    ("heroic_killing_blow_2", "wh3_main_pro_character_abilities_heroic_killing_blow_2"),
    ("heroic_killing_blow_dlc07", "wh_dlc07_character_abilities_heroic_killing_blow"),
    ("heroic_killing_blow_main", "wh_main_character_abilities_heroic_killing_blow"),
    ("hydra_blade", "wh2_main_weapon_abilities_hydra_blade"),
    ("inevitable_horror", "wh3_dlc26_character_abilities_inevitable_horror"),
    ("karaghul", "wh2_pro08_weapon_abilities_karaghul"),
    ("killing_blow_1", "wh3_main_pro_character_abilities_heroic_killing_blow_1"),
    ("killing_blow", "wh_main_unit_abilities_killing_blow"),
    ("liarsbane", "wh3_dlc25_weapon_abilities_liarsbane"),
    ("lightning_reflexes", "wh2_dlc11_lord_abilities_lightning_reflexes"),
    ("locus_of_beguilement", "wh3_main_character_abilities_locus_of_beguilement"),
    ("locus_of_grace", "wh3_main_character_abilities_locus_of_grace"),
    ("locus_of_wrath", "wh3_main_character_abilities_locus_of_wrath"),
    ("lucky_banner", "wh2_dlc15_item_abilities_lucky_banner"),
    ("mace_of_ulumak", "wh2_dlc13_weapon_abilities_mace_of_ulumak"),
    ("mananns_luck", "wh2_dlc11_lord_abilities_mananns_luck"),
    ("master_of_the_skies", "wh2_dlc12_lord_abilities_master_of_the_skies"),
    ("mimic_waaagh", "wh2_dlc15_unit_abilities_mimic_waaagh"),
    ("mimic_grom_waaagh", "wh2_dlc15_unit_abilities_mimic_grom_waaagh"),
    ("monstrous_strength", "wh2_dlc13_lord_abilities_monstrous_strength"),
    ("mortal_blow", "wh3_main_daemon_arms_abilities_mortal_blow"),
    ("mortal_blow_upgraded", "wh3_main_daemon_arms_abilities_mortal_blow_upgraded"),
    ("mumbo_jumbo_chant", "wh3_dlc26_character_abilities_mumbo_jumbo_chant"),
    ("strike_of_nagash", "wh2_dlc09_character_abilities_strike_of_nagash"),
    ("nurgles_favoured_son", "wh3_dlc25_lord_abilities_nurgles_favoured_son"),
    ("opal_amulet", "wh_main_item_abilities_opal_amulet"),
    ("oracle_of_eternity", "wh3_main_lord_abilities_oracle_of_eternity"),
    ("pendant_of_slaanesh", "wh_main_item_abilities_pendant_of_slaanesh"),
    ("plaguefathers_oration", "wh3_main_lord_abilities_plaguefathers_oration"),
    ("primal_roar", "wh2_dlc13_lord_abilities_primal_roar"),
    ("puncture", "wh3_dlc26_character_abilities_puncture"),
]
BLOCK3_CHARGE = [
    ("heart_piercing", "wh2_dlc11_lord_abilities_heart_piercing"),
    ("horn_of_the_first_beast", "wh_dlc03_item_abilities_horn_of_the_first_beast"),
    ("morglor_the_mangler", "wh3_dlc26_weapon_abilities_morglor_the_mangler"),
]
assert len(BLOCK3_SELF) == 35 and len(BLOCK3_CHARGE) == 3
for _marker, _key in BLOCK3_SELF:
    assert 'marker = "%s"' % _marker in script_txt, "block-3 marker missing: " + _marker
    assert 'badge = "zz_auto_badge_%s"' % _marker in script_txt, "block-3 badge missing: " + _marker
    assert '"%s"' % _key in script_txt, "block-3 key missing: " + _key
for _marker, _key in BLOCK3_CHARGE:
    assert 'marker = "%s"' % _marker in script_txt, "block-3 marker missing: " + _marker
    assert 'badge = "zz_auto_badge_%s"' % _marker in script_txt, "block-3 badge missing: " + _marker
    assert '"%s"' % _key in script_txt, "block-3 key missing: " + _key
# ROUND v90: the shared melee_unwavering trigger and the charge_or_melee trigger
# grew again (blocks 7-9 add 45 in-melee-self + 6 charge-and-in-melee).
assert script_txt.count('trigger = "melee_unwavering"') == 373, \
    "the melee_unwavering entry count is not 373 (10 Class-B entries moved to the ally families)"
assert script_txt.count('trigger = "charge_or_melee"') == 26, \
    "the charge_or_melee entry count is not 26 (3 Class-B entries moved to ally_melee_buff)"

# ROUND v84 (the user's two field-test corrections - nothing above is loosened):
#   * GLORIOUS DEATH's candidate set is SLAYER UNITS ONLY. Who is a Slayer is
#     the DERIVED land_units type-key list (FOURTH.slayer_keys), tested by
#     EXACT WHOLE-KEY equality only (no string.find). A NON-Slayer ally is
#     NEVER targeted (the old any-in-melee-ally fallback is gone); the self
#     fallback fires only when the OWNER is a Slayer and in melee.
#   * GHOUL KING OF USHORAN's HYSTERESIS is REMOVED - plain own health <= 75%.
SLAYER_KEYS = [
    "wh_main_dwf_inf_slayers",
    "wh2_dlc10_dwf_inf_giant_slayers",
    "wh3_dlc25_dwf_cha_daemon_slayer",
    "wh3_dlc25_dwf_cha_dragon_slayer",
    "wh3_dlc25_dwf_inf_slayer_pirates",
    "wh3_dlc25_dwf_inf_slayer_pirates_ror",
    "wh3_dlc25_dwf_inf_slayers_grudge_unit",
    "wh_dlc06_dwf_inf_dragonback_slayers_0",
    "wh3_dlc25_dwf_inf_doomseekers",
    "wh3_dlc25_dwf_inf_doomseekers_ror",
]
assert "FOURTH.slayer_keys = {" in script_txt, "the Slayer type-key list is missing"
for _k in SLAYER_KEYS:
    assert ('["%s"] = true' % _k) in script_txt, "a derived Slayer key is missing: " + _k
assert "function FOURTH.is_slayer(unit)" in script_txt, "the Slayer reader is missing"
assert "return FOURTH.slayer_keys[t] == true" in script_txt, \
    "the Slayer membership test is not the exact whole-key lookup"
assert "and FOURTH.is_slayer(other) then" in script_txt, "the Glorious Death ally scan is not Slayer-filtered"
assert "FOURTH.is_slayer(unit) and unit:is_in_melee()" in script_txt, \
    "the Glorious Death self-cast is not gated on the owner being a Slayer"
# the old outer melee guard is gone from Glorious Death (3 remaining guard paths)
assert script_txt.count("unit:is_in_melee() and not routing") == 4, \
    "the old Glorious Death outer melee guard is back"
assert 'type(hp) == "number" and hp <= 75 then' in script_txt, "the plain Ushoran <=75% test is missing"

# ROUND v87 (the field-tested range correction - nothing above is loosened): the
# Glorious Death trigger range is the STANDING 70% RULE value: floor(0.70 x the
# ability's 55 m game-data aura) = 38 m. The user ruled the rule ABSOLUTE, so the
# old field-tuned 25 m gate is gone. The gate
# logic (closest in-range in-melee Slayer chosen; gap re-checked immediately
# before the cast and the cast SKIPPED on drift; owner-in-melee self arm NEVER
# gated) is the round-86 machinery, untouched. The four dead icon-read locals
# stay removed (freed in round 86 to keep the chunk under Lua's 200-local limit).
assert "local GLORIOUS_DEATH_RANGE_M = 38" in script_txt, "the 70% Glorious Death range constant is missing"
assert "local GLORIOUS_DEATH_RANGE_M = 55" not in script_txt, "the old 55 m range constant came back"
assert "THE STANDING 70% RULE" in script_txt, "the standing-70%-rule comment is missing"
assert "55 * 0.70 = 38.5 -> 38" in script_txt, "the Glorious Death 70%% derivation comment is missing"
assert "function FOURTH.gd_ally_gap(unit, ally)" in script_txt, "the gap helper is missing"
assert "ally:unit_distance(unit)" in script_txt, "the gate does not reuse the unit_distance primitive"
assert "function FOURTH.gd_ally_in_range(unit, ally)" in script_txt, "the range test helper is missing"
assert "gap <= GLORIOUS_DEATH_RANGE_M" in script_txt, "the range comparison does not use the named constant"
assert "FOURTH.gd_ally = best_ally" in script_txt, "the closest-ally choice is missing"
assert script_txt.count("FOURTH.gd_ally = nil") == 3, "the chosen-ally clears are not exactly three"
assert "glorious_death SKIPPED:" in script_txt, "the pre-cast drift skip is missing"
assert "glorious_death ally: ui" in script_txt, "the chosen-ally log line is missing"
for _dead in ("local ICON_INDEX", "local original_icon", "local original_state", "local function read_icon"):
    assert _dead not in script_txt, f"a removed dead local came back: {_dead}"


# ROUND v88 (THE BIG IMPLEMENTATION ROUND - blocks 4, 5 and 6 + two new
# triggers - nothing above is loosened): 87 new ability entries. 80 ride the
# SHARED melee_unwavering evaluator (54 block-4/5 approved in-melee-self + 26
# auto-accepted trivial self-buffs, 15 from block 5 and 11 from block 6's
# standing rule 9) and 5 ride the EXISTING charge_or_melee evaluator, so the
# trigger counts are now 171 and 9. The table is 189 entries / 195 keys. TWO
# NEW TRIGGER TYPES ship: WILL OF THE VERMINKING (trigger verminking_wavering)
# and POTION OF TOUGHNESS (trigger melee_health75). ARMY-BAR abilities are a
# STANDING EXCLUSION - no army_abilities key may ever be in the mod.
assert script_txt.count("\t{ marker = ") == 579, "the abilities table is not 579 entries"
assert "FOURTH.VERMINKING_RANGE_M = 24" in script_txt, "the 70% Verminking range constant is missing"
assert "THE STANDING 70% RULE" in script_txt, "the standing-70%-rule comment is missing"
assert "35.0000 m = effect_range" in script_txt, "the game-data range source note is missing"
assert "function FOURTH.evaluate_verminking_wavering(unit, routing)" in script_txt, \
    "the Verminking evaluator is missing"
assert "function FOURTH.vm_ally_gap(unit, ally)" in script_txt, "the Verminking gap helper is missing"
assert "function FOURTH.vm_ally_in_range(unit, ally)" in script_txt, "the Verminking range helper is missing"
assert "will_of_the_verminking SKIPPED:" in script_txt, "the Verminking drift skip is missing"
assert 'reason = "wavering ally in melee (self-cast)"' in script_txt, "the Verminking reason is missing"
assert "function FOURTH.evaluate_potion_health(unit, routing)" in script_txt, \
    "the Potion evaluator is missing"
assert 'string.format("in melee, health %d%% (<= 75%%)"' in script_txt, "the Potion reason is missing"
for _mk, _ky, _tg in (("will_of_the_verminking", "wh3_dlc29_lord_abilities_will_of_the_verminking", "verminking_wavering"),
                      ("potion_of_toughness", "wh_main_item_abilities_potion_of_toughness", "melee_health75")):
    assert 'marker = "%s"' % _mk in script_txt, "new-trigger marker missing: " + _mk
    assert '"%s"' % _ky in script_txt, "new-trigger key missing: " + _ky
    assert 'trigger = "%s"' % _tg in script_txt, "new-trigger trigger name missing: " + _tg
    assert 'badge = "zz_auto_badge_%s"' % _mk in script_txt, "new-trigger badge missing: " + _mk
assert "verminking_wavering = FOURTH.evaluate_verminking_wavering," in script_txt, "the Verminking map entry is missing"
assert "melee_health75 = FOURTH.evaluate_potion_health," in script_txt, "the Potion map entry is missing"
# a sample of every new group (in-melee-self, charge-or-melee, block-6 auto)
for _mk, _ky in (("quickblood", "wh3_dlc29_lord_abilities_lightning_reflexes"),
                 ("the_eternal_blade", "wh3_main_weapon_abilities_the_eternal_blade"),
                 ("star_lance", "wh2_dlc15_weapon_abilities_star_lance"),
                 ("potion_of_strength", "wh_main_item_abilities_potion_of_strength"),
                 ("doom_glaive", "wh3_dlc29_item_abilities_doom_glaive")):
    assert 'marker = "%s"' % _mk in script_txt, "sample marker missing: " + _mk
    assert '"%s"' % _ky in script_txt, "sample key missing: " + _ky
    assert 'badge = "zz_auto_badge_%s"' % _mk in script_txt, "sample badge missing: " + _mk
# THE ARMY-BAR STANDARD: no army-bar ability may ever be automated.
assert "army_abilities" not in script_txt, "an ARMY-BAR key is in the mod (standing exclusion)"
assert script_txt.count("FOURTH.cast_target = unit") == 2, "the self-cast writes are not exactly two"
assert script_txt.count("FOURTH.vm_ally = nil") == 3, "the Verminking chosen-ally clears are not exactly three"

# ROUND v89 (THE ENCHANTED METALLURGY FAMILY - nothing above is loosened): ONE
# new trigger metallurgy_melee across FOUR keys. The user's trigger is "when
# self or ally in range is in melee; when ally in range is shooting". The MELEE
# half ships (owner in melee OR a friendly unit in melee within the
# conservative FOURTH.METALLURGY_RANGE_M = 25 m; cast on self; closest ally,
# pre-cast gap re-check, skip on drift). The SHOOTING half COULD NOT be built:
# the battle API exposes NO per-unit is-firing / is-shooting read, so NO proxy
# is invented. The table grows 189 -> 193 entries (195 -> 199 keys). NO new
# chunk locals - the constant + state ride the FOURTH helper bag.
MTL = [
    ("enchanted_metallurgy", "wh3_main_character_abilities_enchanted_metallurgy"),
    ("enchanted_metallurgy_flaming", "wh3_main_character_abilities_enchanted_metallurgy_flaming"),
    ("enchanted_metallurgy_piercing", "wh3_main_character_abilities_enchanted_metallurgy_piercing"),
    ("enchanted_metallurgy_poison", "wh3_main_character_abilities_enchanted_metallurgy_poison"),
]
for _mk, _ky in MTL:
    assert 'marker = "%s"' % _mk in script_txt, "metallurgy marker missing: " + _mk
    assert '"%s"' % _ky in script_txt, "metallurgy key missing: " + _ky
    assert 'badge = "zz_auto_badge_%s"' % _mk in script_txt, "metallurgy badge missing: " + _mk
assert script_txt.count('trigger = "metallurgy_melee"') == 8, "the metallurgy trigger count is not 8 (four Enchanted Metallurgy + four Master of Alchemy)"
assert "FOURTH.METALLURGY_RANGE_M = 24" in script_txt, "the 70% metallurgy range constant is missing"
assert "function FOURTH.evaluate_metallurgy_melee(unit, routing)" in script_txt, "the metallurgy evaluator is missing"
assert "function FOURTH.mtl_ally_gap(unit, ally)" in script_txt, "the metallurgy gap helper is missing"
assert "function FOURTH.mtl_ally_in_range(unit, ally)" in script_txt, "the metallurgy range helper is missing"
assert "metallurgy_melee = FOURTH.evaluate_metallurgy_melee," in script_txt, "the metallurgy map entry is missing"
assert 'reason = "in-melee ally (metallurgy self-cast)"' not in script_txt, "the old reason-shape came back"
assert 'return "in melee (metallurgy self-cast)"' in script_txt, "the owner-in-melee reason is missing"
assert 'return "in-melee ally (metallurgy self-cast)"' in script_txt, "the ally-in-melee reason is missing"
assert "enchanted_metallurgy SKIPPED:" in script_txt, "the metallurgy drift skip is missing"
assert "enchanted_metallurgy ally: ui" in script_txt, "the metallurgy chosen-ally line is missing"
# the SHOOTING half was NOT built: no invented firing predicate of any kind
assert "is_firing" not in script_txt, "an invented is_firing predicate is in the mod"
assert "is_shooting" not in script_txt, "an invented is_shooting predicate is in the mod"
assert "FOURTH.mtl_ally = nil" in script_txt, "the metallurgy chosen-ally field is missing"
assert script_txt.count("FOURTH.mtl_ally = nil") == 3, "the metallurgy chosen-ally clears are not exactly three"
assert script_txt.count("FOURTH.cast_target = unit") == 2, "the self-cast writes are not exactly two"


# ROUND v90 (BLOCKS 7-9 - THE NEW TRIGGER TYPES - nothing above is loosened): 69
# new entries / 73 keys, derived programmatically from WH3_ability_tracker.md
# section 3a (every `approved (...)` row not already in the mod + the two
# backlog `redesigned` abilities #36/#46 + the one `pending review` #32). The
# four shipped Enchanted Metallurgy rows are SKIPPED as already present. FIVE
# NEW triggers: charge_only (Ferocious Battle Howl - the charge window WITHOUT
# the melee arm), wavering_self (the owner wavering, fail-closed),
# wavering_self_or_ally (owner wavering OR an in-melee wavering ally within the
# conservative 25 m FOURTH.WAVERING_RANGE_M - the game-data 35 m aura),
# charge_or_wavering (the charge window OR wavering), and wavering_ally_range
# ("Stay Here, I'll Get Help!" - a wavering ally in range with NO ally-melee
# requirement: the Verminking shape minus its melee gate). The redesigned #46
# Dazh's Song rides the EXISTING tired trigger; #36 Commanding Presence rides
# wavering_self_or_ally. All new triggers cast ON SELF with the pre-cast gap
# re-check / drift skip. The table grows 193 -> 262 entries (199 -> 272 keys);
# NO new chunk locals (every constant/state rides the FOURTH bag).
assert script_txt.count("\t{ marker = ") == 579, "the abilities table is not 579 entries"
assert script_txt.count('trigger = "charge_only"') == 1, "the charge_only entry count is not 1"
assert script_txt.count('trigger = "wavering_self"') == 3, "the wavering_self entry count is not 3"
assert script_txt.count('trigger = "wavering_self_or_ally"') == 2, "the wavering_self_or_ally entry count is not 2"
assert script_txt.count('trigger = "charge_or_wavering"') == 1, "the charge_or_wavering entry count is not 1"
assert script_txt.count('trigger = "wavering_ally_range"') == 1, "the wavering_ally_range entry count is not 1"
assert script_txt.count('trigger = "metallurgy_melee"') == 8, "the metallurgy_melee entry count is not 8"
assert script_txt.count('trigger = "ushoran_health"') == 38, "the ushoran_health entry count is not 38 (3 Class-B heals moved to ally_heal)"
assert script_txt.count('trigger = "melee_health75"') == 1, "the melee_health75 entry count is not 1 (Captain of the Phoenix Guard moved to ally_heal_melee)"
assert script_txt.count('trigger = "tired"') == 2, "the tired entry count is not 2"
assert "FOURTH.WAVERING_RANGE_M = 24" in script_txt, "the 70% wavering range constant is missing"
assert "THE STANDING 70% RULE" in script_txt, "the standing-70%-rule comment is missing"
assert "effect_range" in script_txt, "the game-data range source note is missing"
for _fn in ("function FOURTH.evaluate_charge_only(unit, routing)",
            "function FOURTH.evaluate_wavering_self(unit, routing)",
            "function FOURTH.evaluate_wavering_self_or_ally(unit, routing)",
            "function FOURTH.evaluate_charge_or_wavering(unit, routing)",
            "function FOURTH.evaluate_wavering_ally_range(unit, routing)",
            "function FOURTH.ws_ally_gap(unit, ally)", "function FOURTH.ws_ally_in_range(unit, ally)",
            "function FOURTH.wa_ally_gap(unit, ally)", "function FOURTH.wa_ally_in_range(unit, ally)"):
    assert _fn in script_txt, "a block-7-9 evaluator/helper is missing: " + _fn
for _map in ("charge_only = FOURTH.evaluate_charge_only,",
             "wavering_self = FOURTH.evaluate_wavering_self,",
             "wavering_self_or_ally = FOURTH.evaluate_wavering_self_or_ally,",
             "charge_or_wavering = FOURTH.evaluate_charge_or_wavering,",
             "wavering_ally_range = FOURTH.evaluate_wavering_ally_range,"):
    assert _map in script_txt, "a block-7-9 evaluator map entry is missing: " + _map
assert "wavering_self_or_ally SKIPPED:" in script_txt, "the self-or-ally drift skip is missing"
assert "wavering_ally_range SKIPPED:" in script_txt, "the wavering-ally-range drift skip is missing"
assert script_txt.count("FOURTH.ws_ally = nil") == 3, "the ws_ally clears are not exactly three"
assert script_txt.count("FOURTH.wa_ally = nil") == 3, "the wa_ally clears are not exactly three"
assert script_txt.count("FOURTH.cast_target = unit") == 2, "the self-cast writes are not exactly two"
assert 'reason = "wavering (self)"' in script_txt, "the wavering-self reason is missing"
assert 'reason = "wavering (self-or-ally)"' in script_txt, "the self-or-ally self reason is missing"
assert 'reason = "wavering in-melee ally (self-cast, self-or-ally)"' in script_txt, "the self-or-ally ally reason is missing"
assert 'reason = "wavering ally in range, cast on ally"' in script_txt, "the wavering-ally-in-range reason is missing"
assert "is_firing" not in script_txt and "is_shooting" not in script_txt, "an invented firing predicate is in the mod"
# every new entry: its marker, its badge id and each of its keys must be present.
BLOCK789 = [
    ("bastions_defenders", { "wh3_dlc24_character_abilities_bastions_defenders" }),
    ("battle_of_wills", { "wh3_dlc29_unit_abilities_battle_of_wills" }),
    ("bironas_timewarp", { "wh_main_spell_bound_bironas_timewarp" }),
    ("breath_of_hatred", { "wh3_dlc23_bound_abilities_breath_of_hatred", "wh3_dlc23_character_abilities_breath_of_hatred" }),
    ("butcher", { "wh3_main_prisoners_butcher" }),
    ("captain_of_the_phoenix_guard", { "wh3_dlc27_character_abilities_captain_of_the_phoenix_guard" }),
    ("cash_cascade", { "wh3_dlc26_character_abilities_cash_cascade" }),
    ("chanson_of_caging", { "wh3_dlc27_lord_abilities_chanson_of_caging" }),
    ("commanding_presence", { "wh3_dlc29_lord_active_commanding_presence" }),
    ("curse_of_years", { "wh3_dlc29_spell_bound_curse_of_years" }),
    ("da_boss_as_a_plan", { "wh3_dlc26_character_abilities_da_boss_as_a_plan" }),
    ("dazs_song_of_winter_sunlight", { "wh3_main_character_abilities_dazs_song_of_winter_sunlight", "wh3_twa06_unit_abilities_dazs_song_of_winter_sunlight" }),
    ("death_frenzy", { "wh2_dlc16_spell_bound_death_frenzy" }),
    ("dragonhorn", { "wh2_dlc15_lord_abilities_dragonhorn" }),
    ("empowering_shrooms", { "wh3_dlc26_character_abilities_empowering_shrooms" }),
    ("favour_of_the_fay", { "wh_dlc07_lord_abilities_favour_of_the_fay" }),
    ("ferocious_battle_howl", { "wh3_dlc29_spell_bound_prayer_ferocious_battle_howl" }),
    ("ferocious_fury_of_ulric", { "wh3_dlc29_spell_bound_prayer_ferocious_fury_of_ulric" }),
    ("ferocious_winters_chill", { "wh3_dlc29_spell_bound_prayer_ferocious_winters_chill" }),
    ("flame_incarnate", { "wh3_main_character_abilities_flame_incarnate" }),
    ("fury_of_khaine", { "wh2_main_unit_abilities_fury_of_khaine" }),
    ("fury_of_ulric", { "wh3_dlc29_spell_bound_prayer_fury_of_ulric" }),
    ("gaze_of_khaine", { "wh2_dlc10_lord_abilities_gaze_of_khaine" }),
    ("grand_faiths_bastion", { "wh_dlc06_quest_abilities_grand_faiths_bastion" }),
    ("gulyas", { "wh3_dlc24_lord_abilities_gulyas" }),
    ("helm_of_yvresse", { "wh2_dlc15_item_abilities_helm_of_yvresse" }),
    ("helping_hand", { "wh2_pro08_character_abilities_helping_hand" }),
    ("immovable_bulwark", { "wh3_dlc26_unit_abilities_immovable_bulwark" }),
    ("inspired_assault_i", { "wh3_main_lord_abilities_inspired_assault_i" }),
    ("inspired_assault_ii", { "wh3_main_lord_abilities_inspired_assault_ii" }),
    ("inspired_assault_iii", { "wh3_main_lord_abilities_inspired_assault_iii" }),
    ("inspired_defence_i", { "wh3_main_lord_abilities_inspired_defence_i" }),
    ("inspired_defence_ii", { "wh3_main_lord_abilities_inspired_defence_ii" }),
    ("inspired_defence_iii", { "wh3_main_lord_abilities_inspired_defence_iii" }),
    ("lord_of_grand_cathay", { "wh3_dlc24_lord_abilities_lord_of_grand_cathay" }),
    ("massacre", { "wh3_main_prisoners_massacre" }),
    ("master_of_alchemy", { "wh3_main_lord_abilities_master_of_alchemy" }),
    ("master_of_alchemy_flaming", { "wh3_main_lord_abilities_master_of_alchemy_flaming" }),
    ("master_of_alchemy_piercing", { "wh3_main_lord_abilities_master_of_alchemy_piercing" }),
    ("master_of_alchemy_poison", { "wh3_main_lord_abilities_master_of_alchemy_poison" }),
    ("master_rune_of_oath_and_steel", { "wh_dlc06_rune_abilities_master_rune_of_oath_and_steel" }),
    ("master_rune_of_speed", { "wh2_dlc17_rune_abilities_master_rune_of_speed" }),
    ("offense_prayer", { "wh3_cp1_character_abilities_offense_prayer" }),
    ("okkams_mindrazor", { "wh3_dlc29_spell_bound_okkams_mindrazor" }),
    ("orcs_are_da_best", { "wh3_dlc26_character_abilities_orcs_are_da_best" }),
    ("overseer_of_the_unseen", { "wh3_dlc29_hero_active_overseer_of_the_unseen" }),
    ("primeval_roar", { "wh2_dlc17_unit_abilities_primeval_roar" }),
    ("protection_prayer", { "wh3_cp1_character_abilities_protection_prayer" }),
    ("rune_of_doom", { "wh2_dlc17_lord_abilities_rune_of_doom" }),
    ("rune_of_oath_and_steel", { "wh_main_rune_abilities_rune_of_oath_and_steel" }),
    ("rune_of_speed", { "wh2_dlc17_rune_abilities_rune_of_speed" }),
    ("sausage_busta", { "wh2_dlc15_character_abilities_sausage_busta" }),
    ("shield_of_the_old_ones", { "wh2_main_character_abilities_shield_of_the_old_ones" }),
    ("slayer_for_chaos", { "wh3_dlc23_item_abilities_slayer_for_chaos" }),
    ("spite_of_da_bad_moon", { "wh_dlc06_lord_abilities_spite_of_da_bad_moon" }),
    ("star_of_avelorn", { "wh2_dlc10_item_abilities_star_of_avelorn" }),
    ("stay_here_ill_get_help", { "wh2_dlc09_character_abilities_stay_here_ill_get_help" }),
    ("supreme_shield_of_the_old_ones", { "wh2_dlc12_character_abilities_supreme_shield_of_the_old_ones" }),
    ("talisman_of_loec", { "wh2_main_item_abilities_talisman_of_loec" }),
    ("the_liber_mortis", { "wh2_dlc09_lord_abilities_the_liber_mortis" }),
    ("the_shadows_coil", { "wh_dlc05_unit_abilities_the_shadows_coil" }),
    ("unstoppable_choppas", { "wh3_dlc26_unit_abilities_unstoppable_choppas" }),
    ("vial_of_troll_blood", { "wh_dlc08_item_abilities_vial_of_troll_blood" }),
    ("warpstone_addiction", { "wh3_dlc29_lord_abilities_warpstone_addiction" }),
    ("warrior_familiar", { "wh3_dlc27_item_abilities_warrior_familiar" }),
    ("winters_chill", { "wh3_dlc29_ability_bound_prayer_winters_chill", "wh3_dlc29_spell_bound_prayer_winters_chill" }),
    ("witchbrew", { "wh2_main_character_abilities_witchbrew", "wh3_dlc24_unit_abilities_witchbrew" }),
    ("worlds_edge_armour", { "wh2_main_item_abilities_worlds_edge_armour" }),
    ("znarkharjas_ward", { "wh3_dlc24_hero_abilities_znarkharjas_ward" }),
]
assert len(BLOCK789) == 69, "the block-7-9 entry list is not 69"
_nk789 = 0
for _mk, _kys in BLOCK789:
    assert 'marker = "%s"' % _mk in script_txt, "block-7-9 marker missing: " + _mk
    assert 'badge = "zz_auto_badge_%s"' % _mk in script_txt, "block-7-9 badge missing: " + _mk
    for _ky in _kys:
        assert '"%s"' % _ky in script_txt, "block-7-9 key missing: " + _ky
        _nk789 = _nk789 + 1
assert _nk789 == 73, "the block-7-9 key count is not 73 (got %d)" % _nk789

# ROUND v91: THE 327 AUTO-ACCEPTED ABILITIES - a BULK DATA APPEND riding the THREE
# EXISTING evaluators (no new trigger types). 311 new entries / 327 new keys;
# the table grows 262 -> 573 entries (272 -> 599 keys). The rows were derived
# programmatically from WH3_ability_tracker.md section 3a (every `approved
# (auto: <trigger>)` row). Base + DLC/summoned twin keys ride ONE entry; two
# NAME-collision entries take a name-derived marker (horn_of_vaul, whip_of_misery).
assert "THE 327 AUTO-ACCEPTED ABILITIES (this round)" in script_txt, "the auto-327 block header is missing"
assert "311 entries /" in script_txt and "327 database keys" in script_txt, "the auto-327 counts note is missing"
AUTO327 = [
    ("accusation", { "wh_main_hero_abilities_accusation" }),
    ("acquiescence", { "wh3_dlc27_spell_bound_acquiescence" }),
    ("aken_seth_the_staff_of_pain", { "wh3_dlc29_weapon_abilities_aken_seth_the_staff_of_pain" }),
    ("alchemists_elixir_of_iron_skin", { "wh3_main_item_abilities_alchemists_elixir_of_iron_skin" }),
    ("alchemists_elixir_of_puissance", { "wh3_main_item_abilities_alchemists_elixir_of_puissance" }),
    ("alchemists_elixir_of_venom", { "wh3_main_item_abilities_alchemists_elixir_of_venom" }),
    ("all_hands_hoay", { "wh2_dlc11_character_abilities_all_hands_hoay" }),
    ("amulet_of_itzl", { "wh2_main_item_abilities_amulet_of_itzl" }),
    ("amulet_of_phastah", { "wh2_dlc09_item_abilities_amulet_of_phastah" }),
    ("apocalyptic_charge", { "wh_pro04_unit_abilities_apocalyptic_charge" }),
    ("magic_prayer", { "wh3_cp1_character_abilities_magic_prayer" }),
    ("armour_of_caledor", { "wh2_dlc15_item_abilities_armour_of_caledor" }),
    ("armour_of_the_burrows", { "wh3_dlc29_item_abilities_armour_of_the_burrows" }),
    ("assassins_trophy", { "wh2_main_character_abilities_assassins_trophy" }),
    ("aura_of_inertia", { "wh2_dlc13_lord_abilities_aura_of_inertia" }),
    ("avast_ye", { "wh2_dlc11_character_abilities_avast_ye" }),
    ("axe_of_men", { "wh_dlc03_weapon_abilities_axe_of_men" }),
    ("barbed_knuckle_boxing", { "wh2_dlc17_lord_abilities_barbed_knuckle_boxing" }),
    ("bastet", { "wh3_dlc29_lord_abilities_bastet" }),
    ("berry_wine", { "wh2_dlc16_item_abilities_berry_wine" }),
    ("bitter_sting", { "wh3_dlc27_qb_unit_abilities_bitter_sting" }),
    ("black_periapt", { "wh_main_item_abilities_black_periapt" }),
    ("black_staff", { "wh2_main_spell_bound_black_staff" }),
    ("blade_of_setep", { "wh2_dlc09_weapon_abilities_blade_of_setep" }),
    ("blessed_helm_of_the_oblast", { "wh3_dlc24_item_abilities_blessed_helm_of_the_oblast" }),
    ("blight_swarm", { "wh3_main_lord_abilities_blight_swarm" }),
    ("blight_of_terrors", { "wh2_dlc16_character_abilities_blight_of_terrors" }),
    ("blood_chalice", { "wh3_dlc29_hero_abilities_blood_chalice" }),
    ("blood_chalice_of_bathori", { "wh_pro02_item_abilities_blood_chalice_of_bathori" }),
    ("blood_omens", { "wh3_dlc29_unit_abilities_blood_omens" }),
    ("bloodthirst", { "wh3_main_lord_abilities_bloodthirst" }),
    ("bloody_onslaught", { "wh3_dlc26_character_abilities_bloody_onslaught" }),
    ("blooood", { "wh_main_unit_abilities_blooood" }),
    ("book_of_arkhan", { "wh_main_spell_bound_book_of_arkhan" }),
    ("book_of_hoeth", { "wh2_main_item_abilities_book_of_hoeth" }),
    ("book_of_secrets", { "wh3_dlc24_item_abilities_book_of_secrets" }),
    ("boom", { "wh_main_unit_abilities_boom" }),
    ("undeath_morkharn_breath_of_darkness", { "wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness" }),
    ("undeath_morkharn_breath_of_darkness_upgraded", { "wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness_upgraded" }),
    ("bugmans_xxxxxx", { "wh3_dlc26_item_abilities_bugmans_xxxxxx" }),
    ("call_of_violence", { "wh_dlc03_character_abilities_call_of_violence" }),
    ("cascading_fire_cloak", { "wh3_main_spell_bound_cascading_fire_cloak" }),
    ("chalice_of_dark_rain", { "wh_dlc03_item_abilities_chalice_of_dark_rain" }),
    ("channelling_staff", { "wh_main_item_abilities_channelling_staff" }),
    ("charmed_shield", { "wh_main_weapon_abilities_charmed_shield" }),
    ("cold_blooded", { "wh2_main_character_abilities_cold_blooded" }),
    ("colossal_strike", { "wh3_dlc24_character_abilities_colossal_strike", "wh3_dlc24_character_abilities_colossal_strike_summoned" }),
    ("crimson_juggernaut", { "wh3_dlc26_character_abilities_crimson_juggernaut" }),
    ("crown_of_command", { "wh_main_item_abilities_crown_of_command" }),
    ("cube_of_darkness", { "wh2_main_item_abilities_cube_of_darkness" }),
    ("curse_of_khsar", { "wh2_dlc09_character_abilities_curse_of_khsar" }),
    ("daemonic_onslaught", { "wh3_main_daemon_legs_abilities_daemonic_onslaught" }),
    ("slezuzus_voice", { "wh3_dlc27_character_abilities_slezuzus_voice" }),
    ("dark_fortune", { "wh_main_item_abilities_dark_fortune" }),
    ("deadly_onslaught", { "wh_dlc03_character_abilities_deadly_onslaught" }),
    ("deranged_munitions", { "wh3_dlc25_lord_abilities_deranged_munitions" }),
    ("deranged_munitions_upgraded", { "wh3_dlc25_lord_abilities_deranged_munitions_upgraded" }),
    ("dont_even_try_it", { "wh2_dlc15_lord_abilities_dont_even_try_it" }),
    ("doom_and_darkness_gunnery_school", { "wh3_dlc25_spell_Bound_doom_and_darkness_gunnery_school", "wh3_dlc27_spell_bound_runecaller_death_doom_and_darkness", "wh_dlc08_spell_bound_death_doom_and_darkness" }),
    ("doom_lord", { "wh3_dlc29_lord_abilities_doom_lord" }),
    ("dreaming_ring_i", { "wh2_dlc16_item_abilities_dreaming_ring_i" }),
    ("dreaming_ring_ii", { "wh2_dlc16_item_abilities_dreaming_ring_ii" }),
    ("dreaming_ring_iii", { "wh2_dlc16_item_abilities_dreaming_ring_iii" }),
    ("earth_blood", { "wh2_dlc16_spell_bound_earth_blood", "wh3_main_spell_bound_earth_blood" }),
    ("earthing_rod", { "wh_main_item_abilities_earthing_rod" }),
    ("el_syf", { "wh_dlc05_weapon_abilities_el_syf" }),
    ("elixir_of_might", { "wh2_dlc09_item_abilities_elixir_of_might" }),
    ("elfish_healing_herbs", { "wh3_dlc27_unit_abilities_elfish_healing_herbs" }),
    ("embers_of_the_phoenix", { "wh2_main_spell_bound_embers_of_the_phoenix" }),
    ("ballistic_enchantment", { "wh2_dlc11_character_abilities_ballistic_enchantment" }),
    ("enhanced_skavenbrew", { "wh3_dlc29_item_abilities_enhanced_skavenbrew" }),
    ("entangle", { "wh2_dlc10_character_abilities_entangle" }),
    ("entrenchment", { "wh_main_unit_abilities_entrenchment" }),
    ("gaze_of_usirian", { "wh3_dlc29_lord_abilities_gaze_of_usirian" }),
    ("eternal_vigour", { "wh3_dlc29_character_abilities_eternal_vigour" }),
    ("extra_ingredients", { "wh3_main_character_abilities_extra_ingredients" }),
    ("favoured_by_the_matriarch", { "wh3_dlc27_hero_abilities_favoured_by_the_matriarch" }),
    ("fear_of_aramar", { "wh2_dlc10_item_abilities_fear_of_aramar" }),
    ("fearsome_roar", { "wh3_dlc24_unit_abilities_fearsome_roar" }),
    ("mark_of_the_monster", { "wh3_dlc29_character_active_mark_of_the_monster" }),
    ("fermented_fungi", { "wh2_dlc15_lord_abilities_fermented_fungi" }),
    ("fight_or_die", { "wh_dlc08_lord_abilities_fight_or_die" }),
    ("fistful_of_laurels", { "wh3_main_item_abilities_fistful_of_laurels" }),
    ("flesh_to_stone", { "wh2_dlc16_spell_bound_flesh_to_stone" }),
    ("fleshy_abundance", { "wh3_dlc20_spell_bound_fleshy_abundance" }),
    ("focus_instincts", { "wh2_dlc12_lord_abilities_focus_instincts" }),
    ("forbidden_rod", { "wh_main_item_abilities_forbidden_rod" }),
    ("frenzied_challenge", { "wh3_dlc27_qb_unit_abilities_frenzied_challenge" }),
    ("frost_shard_glaive", { "wh3_main_weapon_abilities_frost_shard_glaive" }),
    ("full_power", { "wh3_dlc25_unit_abilities_full_power" }),
    ("funnel_of_flame", { "wh2_dlc13_lord_abilities_funnel_of_flame" }),
    ("gaze_of_fate", { "wh3_main_lord_abilities_gaze_of_fate" }),
    ("get_em", { "wh3_dlc25_character_abilities_get_em" }),
    ("get_back_ere", { "wh_main_character_abilities_get_back_ere" }),
    ("soulnetter", { "wh3_main_weapon_abilities_soulnetter" }),
    ("glacial_defence", { "wh3_twa08_unit_abilities_glacial_defence" }),
    ("glory_seeker", { "wh3_dlc29_hero_active_glory_seeker" }),
    ("glory_seeker_upgraded", { "wh3_dlc29_hero_active_glory_seeker_upgraded" }),
    ("gruts_sickle", { "wh3_main_item_abilities_gruts_sickle" }),
    ("guiding_strike", { "wh3_cp1_lord_abilities_guiding_strike" }),
    ("guttural_roar", { "wh3_dlc27_qb_unit_abilities_guttural_roar" }),
    ("hagtree_fetish", { "wh_dlc03_item_abilities_hagtree_fetish" }),
    ("hail_of_fire", { "wh2_dlc13_lord_abilities_hail_of_fire" }),
    ("harmonic_convergence", { "wh3_main_spell_bound_harmonic_convergence" }),
    ("headhunt", { "wh3_dlc26_character_abilities_headhunt" }),
    ("hellish_vigour", { "wh3_dlc29_lord_abilities_hellish_vigour" }),
    ("hellish_vigour_upgraded", { "wh3_dlc29_lord_abilities_hellish_vigour_upgraded" }),
    ("hidden_huntress", { "wh3_cp1_lord_abilities_hidden_huntress" }),
    ("hidden_huntress_upgraded", { "wh3_cp1_lord_abilities_hidden_huntress_upgraded" }),
    ("hieratic_jar", { "wh2_dlc09_item_abilities_hieratic_jar" }),
    ("horn_of_vaul", { "wh2_main_item_abilities_dragonhorn" }),
    ("horn_of_the_wild_hunt", { "wh_dlc05_item_abilities_horn_of_the_wild_hunt" }),
    ("hornswaggle", { "wh2_dlc11_character_abilities_hornswaggle" }),
    ("howl_of_the_great_beast", { "wh3_dlc24_unit_abilities_howl_of_the_great_beast" }),
    ("hunter_of_champions", { "wh_dlc08_character_abilities_hunter_of_champions" }),
    ("hunters_snare", { "wh2_dlc13_lord_abilities_hunters_snare" }),
    ("hunters_trap", { "wh2_dlc13_lord_abilities_hunters_trap" }),
    ("spell_slaanesh_hysterical_frenzy_bound", { "wh3_main_spell_slaanesh_hysterical_frenzy_bound" }),
    ("immortal_will", { "wh_main_hero_abilities_immortal_will" }),
    ("inspired_marksmanship_i", { "wh3_main_lord_abilities_inspired_marksmanship_i" }),
    ("inspired_marksmanship_ii", { "wh3_main_lord_abilities_inspired_marksmanship_ii" }),
    ("inspired_marksmanship_iii", { "wh3_main_lord_abilities_inspired_marksmanship_iii" }),
    ("invocation_of_nehek", { "wh3_dlc29_spell_bound_invocation_of_nehek" }),
    ("iron_hand_captain", { "wh3_dlc27_character_abilities_iron_hand_captain" }),
    ("jagged_dagger", { "wh_dlc03_item_abilities_jagged_dagger" }),
    ("locus_of_abjuration", { "wh3_main_character_abilities_locus_of_abjuration" }),
    ("locus_of_change", { "wh3_main_character_abilities_locus_of_change" }),
    ("locus_of_conjuration", { "wh3_main_character_abilities_locus_of_conjuration" }),
    ("locus_of_fecundity", { "wh3_main_character_abilities_locus_of_fecundity" }),
    ("locus_of_fury", { "wh3_main_character_abilities_locus_of_fury" }),
    ("locus_of_swiftness", { "wh3_main_character_abilities_locus_of_swiftness" }),
    ("looming_dread", { "wh2_dlc14_lord_abilities_looming_dread" }),
    ("lord_of_dragons", { "wh2_dlc15_lord_abilities_lord_of_dragons" }),
    ("magical_animus", { "wh_main_character_abilities_magical_animus" }),
    ("makaissons_persuader", { "wh3_dlc25_weapon_abilities_makaissons_persuader" }),
    ("mark_of_yin", { "wh3_dlc24_unit_abilities_mark_of_yin" }),
    ("mark_of_the_plague_fleet", { "wh3_dlc29_item_active_mark_of_the_plague_fleet" }),
    ("marked_by_ulthar", { "wh_dlc06_unit_abilities_marked_by_ulthar" }),
    ("marked_for_eatin", { "wh3_dlc26_unit_abilities_marked_for_eatin" }),
    ("master_predator", { "wh2_dlc17_lord_abilities_master_predator" }),
    ("master_rune_of_breaking", { "wh2_dlc17_rune_abilities_master_rune_of_breaking" }),
    ("master_rune_of_negation", { "wh_dlc06_rune_abilities_master_rune_of_negation" }),
    ("master_rune_of_slowness", { "wh2_dlc17_rune_abilities_master_rune_of_slowness" }),
    ("beguile", { "wh_dlc04_lord_abilities_beguile" }),
    ("master_of_the_black_arts", { "wh_main_lord_abilities_master_of_the_black_arts" }),
    ("mastered_strike", { "wh3_cp1_lord_abilities_mastered_strike" }),
    ("maw_shard", { "wh3_main_item_abilities_maw_shard" }),
    ("merciws_monstrous_regiment", { "wh3_dlc20_cataclysm_bound_merciws_monstrous_regiment", "wh3_dlc27_cataclysm_bound_merciws_monstrous_regiment" }),
    ("miasma_of_despair", { "wh2_dlc13_lord_abilities_miasma_of_despair" }),
    ("mighty_oath_stone", { "wh_dlc06_lord_abilities_mighty_oath_stone" }),
    ("mighty_roar", { "wh2_dlc15_unit_abilities_mighty_roar" }),
    ("mimic_cold_blooded", { "wh2_dlc15_unit_abilities_mimic_cold_blooded" }),
    ("mimic_feint_and_riposte", { "wh2_dlc15_unit_abilities_mimic_feint_and_riposte" }),
    ("mimic_grand_hammer_of_faith", { "wh2_dlc15_unit_abilities_mimic_grand_hammer_of_faith" }),
    ("unit_bound_missile_mirror", { "wh3_dlc24_unit_bound_missile_mirror" }),
    ("mither", { "wh2_dlc15_hero_abilities_mither" }),
    ("moonshine", { "wh2_dlc11_item_abilities_moonshine" }),
    ("more_power", { "wh3_dlc23_unit_abilities_more_power" }),
    ("morgrims_eye", { "wh3_dlc23_item_abilities_morgrims_eye" }),
    ("muster_of_malevolents", { "wh2_dlc16_character_abilities_muster_of_malevolents" }),
    ("neuroparasites", { "wh2_dlc16_unit_abilities_neuroparasites" }),
    ("necrotic_phylactry", { "wh3_dlc25_item_abilities_necrotic_phylactry" }),
    ("neferras_scrolls_of_mighty_incantations", { "wh2_dlc09_item_abilities_neferras_scrolls_of_mighty_incantations" }),
    ("net_dem_up", { "wh3_dlc26_unit_abilities_net_dem_up" }),
    ("net_of_amyntok", { "wh_dlc04_spell_bound_net_of_amyntok" }),
    ("null_stone", { "wh3_dlc27_item_abilities_null_stone" }),
    ("oath_of_vengeance", { "wh2_dlc10_lord_abilities_oath_of_vengeance" }),
    ("oil_flask", { "wh2_dlc13_lord_abilities_oil_flask" }),
    ("ottos_scythe", { "wh3_dlc29_item_active_ottos_scythe" }),
    ("pack_trap", { "wh3_dlc24_unit_abilities_pack_trap" }),
    ("pageant_of_shrikes", { "wh2_dlc16_character_abilities_pageant_of_shrikes" }),
    ("patch_up", { "wh2_dlc13_character_abilities_patch_up" }),
    ("pearl_of_infinite_bleakness", { "wh2_main_item_abilities_pearl_of_infinite_bleakness" }),
    ("pestilent_potions", { "wh3_dlc20_item_abilities_pestilent_potions" }),
    ("pestilent_regeneration", { "wh3_main_daemon_head_abilities_pestilent_regeneration" }),
    ("phas_protection", { "wh3_main_spell_bound_phas_protection" }),
    ("pilgrimage_of_skulls", { "wh3_dlc26_lord_abilities_pilgrimage_of_skulls" }),
    ("plague_of_rust", { "wh3_main_spell_bound_plague_of_rust" }),
    ("plaque_of_dominion", { "wh2_main_item_abilities_plaque_of_dominion" }),
    ("potion_of_charoi", { "wh2_main_lord_abilities_potion_of_charoi" }),
    ("potion_of_farsight", { "wh3_main_item_abilities_potion_of_farsight" }),
    ("potion_of_foolhardiness", { "wh_main_item_abilities_potion_of_foolhardiness" }),
    ("potion_of_healing", { "wh_main_item_abilities_potion_of_healing" }),
    ("potion_of_speed", { "wh_main_item_abilities_potion_of_speed" }),
    ("power_familiar", { "wh3_dlc27_item_abilities_power_familiar" }),
    ("power_siphon", { "wh2_dlc11_lord_abilities_power_siphon" }),
    ("power_stone", { "wh_main_item_abilities_power_stone" }),
    ("predatory_instincts", { "wh3_cp1_lord_abilities_predatory_instincts" }),
    ("prey_of_anath_raema", { "wh_dlc05_character_abilities_prey_of_anath_raema" }),
    ("prey_of_the_blood_god", { "wh3_pro12_hero_abilities_prey_of_the_blood_god" }),
    ("prismatic_amplifier", { "wh3_main_item_abilities_prismatic_amplifier" }),
    ("purge_the_weak", { "wh3_main_daemon_wings_abilities_purge_the_weak" }),
    ("radiant_gem_of_hoeth", { "wh2_main_spell_bound_radiant_gem_of_hoeth" }),
    ("rally", { "wh_main_character_abilities_rally" }),
    ("dispatch_the_swarm_attack", { "wh3_dlc29_hero_active_dispatch_the_swarm_attack" }),
    ("dispatch_the_swarm_attack_upgraded", { "wh3_dlc29_hero_active_dispatch_the_swarm_attack_upgraded" }),
    ("tomb_king_rally", { "wh2_dlc09_character_abilities_tomb_king_rally" }),
    ("tomb_king_rally_upgraded", { "wh2_dlc09_character_abilities_tomb_king_rally_upgraded" }),
    ("red_fury", { "wh_main_character_abilities_red_fury" }),
    ("reforge", { "wh3_dlc23_character_abilities_reforge" }),
    ("regenerating_flesh", { "wh_main_item_abilities_regenerating_flesh" }),
    ("regrowth", { "wh2_dlc16_spell_bound_regrowth" }),
    ("remouldered", { "wh2_dlc16_lord_abilities_remouldered" }),
    ("restore", { "wh2_dlc09_character_abilities_restore" }),
    ("revivification_crystal", { "wh2_main_unit_abilities_revivification_crystal" }),
    ("item_passive_rock_eye", { "wh3_main_item_passive_rock_eye" }),
    ("rune_of_breaking", { "wh2_dlc17_rune_abilities_rune_of_breaking" }),
    ("rune_of_negation", { "wh_main_rune_abilities_rune_of_negation" }),
    ("rune_of_slowness", { "wh2_dlc17_rune_abilities_rune_of_slowness" }),
    ("rune_of_thungni", { "wh3_dlc23_item_abilities_rune_of_thungni" }),
    ("sadistic_snare", { "wh3_dlc23_lord_abilities_sadistic_snare" }),
    ("saint_annushkas_finger_bone", { "wh3_main_item_abilities_saint_annushkas_finger_bone" }),
    ("salyaks_lullaby", { "wh3_main_character_abilities_salyaks_lullaby" }),
    ("sceptre_of_stability", { "wh_main_item_abilities_sceptre_of_stability" }),
    ("scroll_of_destiny", { "wh3_main_item_abilities_scroll_of_destiny" }),
    ("scroll_of_leeching", { "wh_main_item_abilities_scroll_of_leeching" }),
    ("scroll_of_power", { "wh_main_item_abilities_scroll_of_power" }),
    ("scroll_of_shielding", { "wh_main_item_abilities_scroll_of_shielding" }),
    ("shield_of_chaqua", { "wh2_dlc12_unit_abilities_shield_of_chaqua" }),
    ("shield_of_thorns", { "wh2_dlc17_spell_bound_shield_of_thorns", "wh_dlc05_spell_bound_shield_of_thorns" }),
    ("dispatch_the_swarm_protect", { "wh3_dlc29_hero_active_dispatch_the_swarm_protect" }),
    ("dispatch_the_swarm_protect_upgraded", { "wh3_dlc29_hero_active_dispatch_the_swarm_protect_upgraded" }),
    ("shock_collar", { "wh2_dlc16_hero_abilities_shock_collar" }),
    ("silence_the_prey", { "wh3_main_character_abilities_silence_the_prey" }),
    ("skalm", { "wh2_main_item_abilities_skalm" }),
    ("skars_kraken_killer", { "wh3_main_weapon_abilities_skars_kraken_killer" }),
    ("skavenbrew", { "wh2_main_item_abilities_skavenbrew" }),
    ("skjalandirs_fall", { "wh3_dlc23_character_abilities_skjalandirs_fall" }),
    ("skull_of_rarkos", { "wh_dlc03_item_abilities_skull_of_rarkos" }),
    ("snowflake_pendant", { "wh3_main_item_abilities_snowflake_pendant" }),
    ("spearfishers_net", { "wh2_dlc11_lord_abilities_spearfishers_net" }),
    ("spell_wrought_sceptre", { "wh3_dlc23_weapon_abilities_spell_wrought_sceptre" }),
    ("spider_web_attack", { "wh3_dlc26_character_abilities_spider_web_attack" }),
    ("staff_of_damnation", { "wh_main_spell_bound_staff_of_damnation" }),
    ("staff_of_nagash", { "wh2_dlc09_item_abilities_staff_of_nagash" }),
    ("staff_of_tomorrow", { "wh3_main_weapon_abilities_staff_of_tomorrow" }),
    ("staff_of_volans", { "wh_main_item_abilities_staff_of_volans" }),
    ("staff_of_wu_xing", { "wh3_main_item_abilities_staff_of_wu_xing" }),
    ("starwood_staff", { "wh2_main_item_abilities_starwood_staff" }),
    ("stave_of_avelorn", { "wh2_dlc10_item_abilities_stave_of_avelorn" }),
    ("storm_hammer", { "wh3_dlc29_spell_bound_storm_hammer" }),
    ("sword_of_filth", { "wh3_dlc25_weapon_abilities_sword_of_filth" }),
    ("tacticians_rally", { "wh3_dlc24_character_abilities_tacticians_rally" }),
    ("taunt", { "wh2_dlc11_character_abilities_taunt" }),
    ("tendrils_of_the_sea", { "wh3_dlc29_hero_active_tendrils_of_the_sea" }),
    ("terrorgheist_skull", { "wh_dlc08_item_abilities_terrorgheist_skull" }),
    ("averland_runefang", { "wh2_dlc13_weapon_abilities_averland_runefang" }),
    ("the_bane_shield", { "wh2_main_item_abilities_the_bane_shield" }),
    ("the_black_tongue", { "wh3_dlc27_character_abilities_the_black_tongue" }),
    ("the_chromatic_tome", { "wh3_main_item_abilities_the_chromatic_tome" }),
    ("the_dark_master", { "wh3_main_lord_abilities_the_dark_master" }),
    ("enfeebling_foe", { "wh3_dlc23_spell_bound_enfeebling_foe", "wh3_dlc27_spell_bound_enfeebling_foe", "wh3_main_spell_bound_enfeebling_foe", "wh3_twa08_spell_bound_enfeebling_foe_keeper_of_secrets_ror" }),
    ("the_golden_eye_of_tzeentch", { "wh3_dlc24_item_abilities_the_golden_eye_of_tzeentch" }),
    ("the_guiding_eye", { "wh2_main_item_abilities_the_guiding_eye" }),
    ("the_hammer_of_karak_drazh", { "wh_main_weapon_abilities_the_hammer_of_karak_drazh" }),
    ("undeath_sulekhim_hand_of_dust", { "wh3_dlc29_spell_bound_undeath_sulekhim_hand_of_dust" }),
    ("the_liber_noctus", { "wh_dlc04_item_abilities_the_liber_noctus" }),
    ("lions_shield", { "wh_dlc07_lord_abilities_lions_shield" }),
    ("the_praise_of_slaanesh", { "wh3_dlc27_lord_abilities_the_praise_of_slaanesh" }),
    ("the_seerstaff_of_saphery", { "wh2_main_spell_bound_the_seerstaff_of_saphery" }),
    ("the_tricksters_pendant", { "wh2_main_item_abilities_the_tricksters_pendant" }),
    ("the_vial_of_hashut", { "wh3_dlc23_item_abilities_the_vial_of_hashut" }),
    ("the_vortex_shard", { "wh2_main_item_abilities_the_vortex_shard" }),
    ("the_wintertooth_crown", { "wh_dlc08_item_abilities_the_wintertooth_crown" }),
    ("wissenland_runefang", { "wh2_dlc13_weapon_abilities_wissenland_runefang" }),
    ("the_withering", { "wh3_dlc23_spell_bound_the_withering", "wh3_twa08_spell_bound_the_withering" }),
    ("they_needs_stabbin", { "wh2_dlc15_character_abilities_they_needs_stabbin" }),
    ("thorns_aura", { "wh3_dlc24_hero_abilities_thorns_aura" }),
    ("thunderburner", { "wh3_dlc25_unit_abilities_thunderburner" }),
    ("thunderburner_upgraded", { "wh3_dlc25_unit_abilities_thunderburner_upgraded" }),
    ("titan_headsman", { "wh3_dlc25_hero_abilities_titan_headsman" }),
    ("torment_blade", { "wh3_main_weapon_abilities_torment_blade" }),
    ("tricksters_shard", { "wh_main_item_abilities_tricksters_shard" }),
    ("trollguts", { "wh3_dlc26_spell_bound_trollguts" }),
    ("trophy_heads", { "wh2_main_lord_abilities_trophy_heads", "wh3_main_daemon_wings_abilities_trophy_heads" }),
    ("twilight_horn_i", { "wh2_dlc16_item_abilities_twilight_horn_i" }),
    ("undeath_resurgent", { "wh_main_character_abilities_undeath_resurgent" }),
    ("unholy_clamour", { "wh2_main_mount_abilities_unholy_clamour" }),
    ("unlimited_power", { "wh2_dlc12_lord_abilities_unlimited_power" }),
    ("ursuns_roar_2", { "wh3_main_pro_character_abilities_ursuns_roar_2" }),
    ("ursuns_roar", { "wh3_main_character_abilities_ursuns_roar", "wh3_main_pro_character_abilities_ursuns_roar", "wh3_main_pro_character_abilities_ursuns_roar_1", "wh3_main_pro_character_abilities_ursuns_roar_3" }),
    ("van_horstmanns_speculum", { "wh_main_item_abilities_van_horstmanns_speculum" }),
    ("verminous_fury", { "wh3_dlc29_lord_abilities_verminous_fury" }),
    ("virulent_contagion", { "wh3_main_lord_abilities_virulent_contagion" }),
    ("virulent_contagion_upgraded", { "wh3_main_lord_abilities_virulent_contagion_upgraded" }),
    ("visions_of_madness", { "wh3_dlc27_qb_unit_abilities_visions_of_madness" }),
    ("void_pendulum", { "wh3_main_item_abilities_void_pendulum" }),
    ("vorozhejas_foresight", { "wh3_dlc24_hero_abilities_vorozhejas_foresight" }),
    ("waaagh_in_combat", { "wh3_dlc26_unit_abilities_waaagh_in_combat", "wh_main_character_abilities_waaagh" }),
    ("wand_of_jet", { "wh_main_item_abilities_wand_of_jet" }),
    ("wardens_cage", { "wh2_dlc15_character_abilities_wardens_cage" }),
    ("warp_gaze", { "wh_pro04_unit_abilities_warp_gaze" }),
    ("warpstiletto", { "wh3_dlc29_item_abilities_warpstiletto" }),
    ("warpstone_tokens", { "wh3_dlc29_item_abilities_warpstone_tokens" }),
    ("watched_by_the_watcher", { "wh3_dlc24_character_abilities_watched_by_the_watcher" }),
    ("were_you_goin", { "wh3_dlc26_character_abilities_were_you_goin" }),
    ("whip_of_agony", { "wh2_twa03_weapon_abilities_whip_of_agony" }),
    ("whip_of_misery", { "wh2_main_spell_bound_whip_of_agony" }),
    ("whiplash", { "wh2_dlc14_lord_abilities_whiplash" }),
    ("whispering_mist", { "wh3_dlc29_hero_abilities_whispering_mist" }),
    ("whispering_skull", { "wh3_dlc29_item_abilities_whispering_skull" }),
    ("wild_abandon", { "wh3_dlc26_lord_abilities_wild_abandon" }),
    ("willing_prey", { "wh3_main_lord_abilities_willing_prey" }),
    ("winds_of_change", { "wh3_main_daemon_body_abilities_winds_of_change" }),
    ("word_of_change", { "wh3_main_daemon_head_abilities_word_of_change" }),
    ("word_of_pain", { "wh2_dlc10_spell_bound_word_of_pain", "wh3_dlc27_spell_dark_magic_word_of_pain_bound_1use" }),
    ("woven_mist", { "wh_dlc05_unit_abilities_woven_mist" }),
    ("wrath_of_the_storm", { "wh3_main_lord_abilities_wrath_of_the_storm" }),
    ("wrathful_reaper", { "wh3_main_lord_abilities_wrathful_reaper" }),
    ("wristbands_of_black_gold", { "wh3_dlc29_item_abilities_wristbands_of_black_gold" }),
    ("youre_next", { "wh2_dlc15_lord_abilities_youre_next" }),
]
assert len(AUTO327) == 311, "the auto-327 entry list is not 311"
_nk327 = 0
for _mk, _kys in AUTO327:
    assert 'marker = "%s"' % _mk in script_txt, "auto-327 marker missing: " + _mk
    assert 'badge = "zz_auto_badge_%s"' % _mk in script_txt, "auto-327 badge missing: " + _mk
    for _ky in _kys:
        assert '"%s"' % _ky in script_txt, "auto-327 key missing: " + _ky
        _nk327 = _nk327 + 1
assert _nk327 == 327, "the auto-327 key count is not 327 (got %d)" % _nk327

# ROUND v92: THE FINAL ROSTER BUILD - the SIX built individual abilities from
# the remaining-abilities triage (WH3_remaining_triage.md section 3 INDIVIDUAL
# table). TWO NEW ally-heal triggers, each its OWN evaluator: blood_sacrifice
# (cast on the lowest-health ally in range at or below 75%) and eat_da_runts
# (cast on self at or below 75%, ELSE the lowest-health ally in range). FOUR
# further entries ride the EXISTING shared melee_unwavering evaluator (in-melee
# self): Locus of Virulence, The Dance of Dreaming, The Waltz of Lethargy,
# Ultimate Verdict. Each new trigger casts on the CHOSEN ALLY, uses a
# conservative named 25 m range constant, and RE-CHECKS the gap and the ally's
# health before the cast (skip on drift). The table grows 573 -> 579 entries
# (599 -> 605 keys); melee_unwavering 477 -> 481. NO new chunk locals (the
# constant and state ride the FOURTH helper bag).
assert "THE FINAL ROSTER ROUND (this round)" in script_txt, "the final-roster block header is missing"
assert "function FOURTH.evaluate_blood_sacrifice(unit, routing)" in script_txt, "the blood-sacrifice evaluator is missing"
assert "function FOURTH.evaluate_eat_da_runts(unit, routing)" in script_txt, "the eat-da-runts evaluator is missing"
assert "function FOURTH.bs_ally_valid(unit, ally)" in script_txt, "the blood-sacrifice validity helper is missing"
assert "function FOURTH.edr_ally_valid(unit, ally)" in script_txt, "the eat-da-runts validity helper is missing"
assert "FOURTH.BLOOD_SACRIFICE_RANGE_M = 70" in script_txt, "the 70% blood-sacrifice range constant is missing"
assert "FOURTH.EAT_DA_RUNTS_RANGE_M = 70" in script_txt, "the 70% eat-da-runts range constant is missing"
assert "blood_sacrifice = FOURTH.evaluate_blood_sacrifice," in script_txt, "the blood-sacrifice map entry is missing"
assert "eat_da_runts = FOURTH.evaluate_eat_da_runts," in script_txt, "the eat-da-runts map entry is missing"
assert "blood_sacrifice SKIPPED:" in script_txt, "the blood-sacrifice drift skip is missing"
assert "eat_da_runts SKIPPED:" in script_txt, "the eat-da-runts drift skip is missing"
assert 'string.format("blood sacrifice: lowest-health ally %d%% (<= 75%%), cast on ally"' in script_txt, "the blood-sacrifice reason is missing"
assert 'string.format("eat da runts: self health %d%% (<= 75%%), cast on self"' in script_txt, "the eat-da-runts self reason is missing"
assert script_txt.count('trigger = "blood_sacrifice"') == 1, "the blood_sacrifice entry count is not 1"
assert script_txt.count('trigger = "eat_da_runts"') == 1, "the eat_da_runts entry count is not 1"
assert script_txt.count("FOURTH.bs_ally = nil") == 3, "the bs_ally clears are not exactly three"
assert script_txt.count("FOURTH.edr_ally = nil") == 3, "the edr_ally clears are not exactly three"
FINAL6 = [
    ("blood_sacrifice", "wh3_dlc26_lord_abilities_blood_sacrifice"),
    ("eat_da_runts", "wh3_dlc26_unit_abilities_eat_da_runts"),
    ("locus_of_virulence", "wh3_main_character_abilities_locus_of_virulence"),
    ("the_dance_of_dreaming", "wh3_dlc27_lord_abilities_the_dance_of_dreaming"),
    ("the_waltz_of_lethargy", "wh3_dlc27_lord_abilities_the_waltz_of_lethargy"),
    ("ultimate_verdict", "wh3_cp1_character_abilities_terrifying_presence"),
]
assert len(FINAL6) == 6, "the final-roster entry list is not 6"
assert script_txt.count("FOURTH.cast_target = unit") == 2, "the self-cast writes are not exactly two"
_nk92 = 0
for _mk, _ky in FINAL6:
    assert 'marker = "%s"' % _mk in script_txt, "final-roster marker missing: " + _mk
    assert 'badge = "zz_auto_badge_%s"' % _mk in script_txt, "final-roster badge missing: " + _mk
    assert '"%s"' % _ky in script_txt, "final-roster key missing: " + _ky
    _nk92 = _nk92 + 1
assert _nk92 == 6, "the final-roster key count is not 6 (got %d)" % _nk92

# ---------------------------------------------------------------------------
# ROUND v94: ACCUSATION'S ENEMY-TARGETED TRIGGER (enemy_engaged_or_shot).
# ---------------------------------------------------------------------------
assert 'function FOURTH.evaluate_enemy_engaged_or_shot(unit, routing)' in script_txt, \
    "the enemy-targeted evaluator is missing"
assert 'enemy_engaged_or_shot = FOURTH.evaluate_enemy_engaged_or_shot,' in script_txt, \
    "the enemy trigger map entry is missing"
assert 'marker = "accusation", name = "Accusation", trigger = "enemy_engaged_or_shot"' in script_txt, \
    "Accusation does not ride the new trigger"
assert 'enemy_engaged_or_shot = "When armed, fires when an enemy unit in range is in melee or under missile fire",' in script_txt, \
    "the accusation tooltip wording is missing"
assert 'FOURTH.ACCUSATION_RANGE_M = 52' in script_txt, "the 70% accusation range constant is missing"
assert 'bm:get_scriptunits_for_main_enemy_army_to_local_player()' in script_txt, \
    "the enemy army enumerator read is missing"
assert 'function FOURTH.eg_fresh_caster_su(unit)' in script_txt, \
    "the proven fresh-caster re-fetch helper is missing"
assert 'enemy:is_under_missile_attack()' in script_txt, "the enemy missile-read is missing"
assert 'reason = "enemy in melee (targeting " .. etype .. ")"' in script_txt, \
    "the in-melee arm reason is missing"
assert 'reason = "enemy under missile fire (targeting " .. etype .. ")"' in script_txt, \
    "the under-fire arm reason is missing"
assert ' SKIPPED: the chosen enemy lapsed before the cast' in script_txt, \
    "the accusation pre-cast lapse skip is missing"
assert 'accusation: enemy is_under_missile_attack read UNAVAILABLE' in script_txt, \
    "the one-time unreadable-missile notice is missing"
assert 'target: \'' in script_txt, "the chosen-target line is missing"
assert script_txt.count('trigger = "enemy_engaged_or_shot"') == 89, \
    "the enemy trigger count is not 89"
assert script_txt.count('trigger = "melee_unwavering"') == 373, \
    "the melee_unwavering count is not 373"
assert script_txt.count("FOURTH.eg_enemy = nil") == 3, "the eg_enemy clears are not exactly three"
assert script_txt.count("FOURTH.eg_caster_su = nil") == 2, "the eg_caster_su clears are not exactly two"
assert script_txt.count("FOURTH.cast_target = unit") == 2, "the self-cast writes are not exactly two"
# ---------------------------------------------------------------------------
# ROUND v95: THE STANDING 70% RANGE RULE (the user ruled it ABSOLUTE -
# "...No exceptions."). Every trigger-range constant == floor(real * 0.70),
# where real is the ability's own game-data range (unit_spec_abil.tsv
# effect_range for an aura, else target_intercept_range).
# ---------------------------------------------------------------------------
assert "FOURTH.RANGE_FRACTION = 0.70" in script_txt, "the standing range-rule constant is missing"
_RULE95 = (("local GLORIOUS_DEATH_RANGE_M", 55, 38),
           ("FOURTH.VERMINKING_RANGE_M", 35, 24),
           ("FOURTH.METALLURGY_RANGE_M", 35, 24),
           ("FOURTH.WAVERING_RANGE_M", 35, 24),
           ("FOURTH.BLOOD_SACRIFICE_RANGE_M", 100, 70),
           ("FOURTH.EAT_DA_RUNTS_RANGE_M", 100, 70),
           ("FOURTH.ACCUSATION_RANGE_M", 75, 52))
for _tok, _real, _want in _RULE95:
    assert int(_real * 0.70 + 1e-9) == _want, "the documented 70%% target is wrong for " + _tok
    assert ("%s = %d" % (_tok, _want)) in script_txt, "the 70%% range constant is missing: " + _tok
for _old_zero in ("local GLORIOUS_DEATH_RANGE_M = 25",
                  "FOURTH.VERMINKING_RANGE_M = 25", "FOURTH.METALLURGY_RANGE_M = 25",
                  "FOURTH.WAVERING_RANGE_M = 25", "FOURTH.BLOOD_SACRIFICE_RANGE_M = 25",
                  "FOURTH.EAT_DA_RUNTS_RANGE_M = 25", "FOURTH.ACCUSATION_RANGE_M = 75"):
    assert _old_zero not in script_txt, "an old (non-70%) range constant is still present: " + _old_zero
# the charge-window pair is NOT an ability range and is deliberately untouched
assert "CHARGE_MIN_DISTANCE_M    = 12" in script_txt and "CHARGE_MAX_DISTANCE_M    = 60" in script_txt, \
    "the charge-window constants changed (they are not 70%-rule ranges)"


# ROUND v96: THE ACCUSATION MOVE-ORDER ROOT CAUSE (nothing above is loosened).
# The offer test is the 70% CONSTANT ONLY and never the engine's unit_in_range;
# the chosen-target and pre-cast re-check logs print the REAL distance.
assert "function FOURTH.eg_enemy_within_bound(unit, enemy)" in script_txt, \
    "the constant-only offer test is missing"
assert "and FOURTH.eg_enemy_within_bound(unit, enemy) then" in script_txt, \
    "the offer gate is not wired to the constant-only test"
assert "function FOURTH.eg_enemy_in_range(unit, enemy)" not in script_txt, \
    "the old engine-helper offer test is back"
assert "unit_in_range(" not in script_txt, \
    "the engine unit_in_range call is back in the offer path"
assert "return gap <= FOURTH.ACCUSATION_RANGE_M" in script_txt, \
    "the offer test does not compare the gap to the 70% constant"
assert "battle_unit.lua:160" in script_txt, \
    "the distance-primitive citation is missing"
assert '") distance="' in script_txt, \
    "the target-choice log does not print the real distance"
assert '.. "m bound=" .. tostring(bound) .. "m")' in script_txt, \
    "the target-choice log does not print the bound"
assert '", distance="' in script_txt, \
    "the pre-cast re-check log does not print the real distance"
assert '.. ") within "' not in script_txt, \
    "the misleading static within-Nm log label is back"


# ROUND v97: THE REST OF CLASS A (nothing above is loosened). The 12 named 70%
# enemy-cast constants, the real->bound map, the 98 range_real fields, the load-loop
# wiring, the shared picker and the enemy-ground evaluator/helper/key-set.
assert "FOURTH.ENEMY_CAST = {" in script_txt, "the real->bound map is missing"
assert "ability.range_m = FOURTH.ENEMY_CAST[ability.range_real]" in script_txt, \
    "the load-loop real->bound mapping is missing"
assert script_txt.count("\t\trange_real = ") == 98, "the range_real fields are not 98"
assert "function FOURTH.eg_pick_enemy(unit, routing, ground)" in script_txt, \
    "the shared enemy picker is missing"
assert "local bound = FOURTH.eg_range_m" in script_txt and "return gap <= bound" in script_txt, \
    "the per-ability bound is not read"
assert "function FOURTH.evaluate_enemy_ground_area(unit, routing)" in script_txt, \
    "the enemy-ground evaluator is missing"
assert "enemy_ground_area = FOURTH.evaluate_enemy_ground_area," in script_txt, \
    "the enemy-ground trigger is not wired"
assert "function FOURTH.enemy_ground_cast(uc, enemy, ability_key)" in script_txt, \
    "the enemy-ground cast helper is missing"
assert "enemy_ground_keys = {" in script_txt, "the enemy-ground key set is missing"
assert "FOURTH.eg_range_m = ability.range_m" in script_txt and \
    "FOURTH.eg_marker = ability.marker" in script_txt, \
    "the poll does not set the current ability bound/marker"
assert script_txt.count('trigger = "enemy_ground_area"') == 9, "the enemy-ground trigger count is not 9"
assert "unit_in_range(" not in script_txt, "the engine unit_in_range call is back"
assert "FOURTH.ENEMY_CAST_R15  = 10" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R15  = 10"
assert "FOURTH.ENEMY_CAST_R20  = 14" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R20  = 14"
assert "FOURTH.ENEMY_CAST_R30  = 21" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R30  = 21"
assert "FOURTH.ENEMY_CAST_R35  = 24" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R35  = 24"
assert "FOURTH.ENEMY_CAST_R50  = 35" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R50  = 35"
assert "FOURTH.ENEMY_CAST_R70  = 49" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R70  = 49"
assert "FOURTH.ENEMY_CAST_R75  = 52" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R75  = 52"
assert "FOURTH.ENEMY_CAST_R100 = 70" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R100 = 70"
assert "FOURTH.ENEMY_CAST_R150 = 105" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R150 = 105"
assert "FOURTH.ENEMY_CAST_R180 = 126" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R180 = 126"
assert "FOURTH.ENEMY_CAST_R200 = 140" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R200 = 140"
assert "FOURTH.ENEMY_CAST_R500 = 350" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R500 = 350"
assert '["wh2_dlc09_item_abilities_amulet_of_phastah"] = true,' in script_txt, "enemy-ground key missing: wh2_dlc09_item_abilities_amulet_of_phastah"
assert '["wh_dlc03_item_abilities_chalice_of_dark_rain"] = true,' in script_txt, "enemy-ground key missing: wh_dlc03_item_abilities_chalice_of_dark_rain"
assert '["wh2_dlc09_character_abilities_curse_of_khsar"] = true,' in script_txt, "enemy-ground key missing: wh2_dlc09_character_abilities_curse_of_khsar"
assert '["wh2_dlc10_character_abilities_entangle"] = true,' in script_txt, "enemy-ground key missing: wh2_dlc10_character_abilities_entangle"
assert '["wh3_dlc25_character_abilities_get_em"] = true,' in script_txt, "enemy-ground key missing: wh3_dlc25_character_abilities_get_em"
assert '["wh2_dlc13_lord_abilities_hunters_snare"] = true,' in script_txt, "enemy-ground key missing: wh2_dlc13_lord_abilities_hunters_snare"
assert '["wh2_dlc13_lord_abilities_hunters_trap"] = true,' in script_txt, "enemy-ground key missing: wh2_dlc13_lord_abilities_hunters_trap"
assert '["wh2_main_item_abilities_the_tricksters_pendant"] = true,' in script_txt, "enemy-ground key missing: wh2_main_item_abilities_the_tricksters_pendant"
assert '["wh_main_item_abilities_tricksters_shard"] = true,' in script_txt, "enemy-ground key missing: wh_main_item_abilities_tricksters_shard"


# ROUND v98: CLASS B (ally-targeted effects cast on self). The five named 70%
# ally-cast constants, the ally real->bound map, the 18 ally_range_real fields,
# the load-loop wiring, the fresh-friend helper, the shared ally picker, the four
# family evaluators, the fresh-handle cast branch and the poll slots.
assert "FOURTH.ALLY_CAST = {" in script_txt, "the ally real->bound map is missing"
assert "ability.range_m = FOURTH.ALLY_CAST[ability.ally_range_real]" in script_txt, \
    "the load-loop ally real->bound mapping is missing"
assert script_txt.count("\t\tally_range_real = ") == 18, "the ally_range_real fields are not 18"
assert "FOURTH.ALLY_CAST_R50  = 35" in script_txt, "the 70% ally-cast constant is missing: FOURTH.ALLY_CAST_R50  = 35"
assert "FOURTH.ALLY_CAST_R60  = 42" in script_txt, "the 70% ally-cast constant is missing: FOURTH.ALLY_CAST_R60  = 42"
assert "FOURTH.ALLY_CAST_R75  = 52" in script_txt, "the 70% ally-cast constant is missing: FOURTH.ALLY_CAST_R75  = 52"
assert "FOURTH.ALLY_CAST_R100 = 70" in script_txt, "the 70% ally-cast constant is missing: FOURTH.ALLY_CAST_R100 = 70"
assert "FOURTH.ALLY_CAST_R150 = 105" in script_txt, "the 70% ally-cast constant is missing: FOURTH.ALLY_CAST_R150 = 105"
assert "function FOURTH.ab_fresh_friend_su(unit)" in script_txt, \
    "the fresh-friend helper is missing"
assert "function FOURTH.ab_pick_ally(unit, routing, family)" in script_txt, \
    "the shared ally picker is missing"
assert "function FOURTH.ab_ally_valid(unit, ally)" in script_txt, \
    "the ally validity helper is missing"
assert "FOURTH.ab_caster_su = FOURTH.ab_fresh_friend_su(unit)" in script_txt and \
    "FOURTH.ab_ally_su = FOURTH.ab_fresh_friend_su(best_ally)" in script_txt, \
    "the fresh caster/ally re-fetch is missing"
assert "uc = FOURTH.ab_caster_su.uc" in script_txt and "target = FOURTH.ab_ally_su.unit" in script_txt, \
    "the fresh-handle ally cast branch is missing"
assert "FOURTH.ab_range_m = ability.range_m" in script_txt and \
    "FOURTH.ab_marker = ability.marker" in script_txt, \
    "the poll does not set the current ability ally bound/marker"
assert "function FOURTH.evaluate_ally_heal(unit, routing)" in script_txt, "the ally_heal evaluator is missing"
assert "ally_heal = FOURTH.evaluate_ally_heal," in script_txt, "the ally_heal trigger is not wired"
assert "function FOURTH.evaluate_ally_heal_melee(unit, routing)" in script_txt, "the ally_heal_melee evaluator is missing"
assert "ally_heal_melee = FOURTH.evaluate_ally_heal_melee," in script_txt, "the ally_heal_melee trigger is not wired"
assert "function FOURTH.evaluate_ally_wavering(unit, routing)" in script_txt, "the ally_wavering evaluator is missing"
assert "ally_wavering = FOURTH.evaluate_ally_wavering," in script_txt, "the ally_wavering trigger is not wired"
assert "function FOURTH.evaluate_ally_melee_buff(unit, routing)" in script_txt, "the ally_melee_buff evaluator is missing"
assert "ally_melee_buff = FOURTH.evaluate_ally_melee_buff," in script_txt, "the ally_melee_buff trigger is not wired"
assert script_txt.count('trigger = "ally_melee_buff"') == 11, "the ally_melee_buff count is not 11"
assert script_txt.count('trigger = "ally_heal"') == 3, "the ally_heal count is not 3"
assert script_txt.count('trigger = "ally_heal_melee"') == 1, "the ally_heal_melee count is not 1"
assert script_txt.count('trigger = "ally_wavering"') == 2, "the ally_wavering count is not 2"
# the ARMY-BAR entry (Meat Feast, standing rule 10) is NOT given ally logic
assert 'marker = "butcher", name = "Meat Feast", trigger = "ushoran_health"' in script_txt, \
    "the army-bar Meat Feast entry was changed"
assert "unit_in_range(" not in script_txt, "the engine unit_in_range call is back"
assert "is_firing" not in script_txt and "is_shooting" not in script_txt, \
    "an invented firing predicate is in the mod"
assert script_txt.count("\t{ marker = ") == 579, "the abilities table is not 579 entries"

# HOUSEKEEPING 20261004: the two throwaway experiment probes were RETIRED from the
# pack (zz_probe_unit_reads.lua and zz_probe_ui_text.lua - their experiments are
# finished and their findings are recorded). Their sources are preserved in
# releases/20261004_probe_sources_retired/ and must NOT ship again:
assert not any("zz_probe_" in p for p in in_pack_paths), "a retired probe is back in the pack"
for _retired in ("zz_probe_ui_text.lua", "zz_probe_unit_reads.lua"):
    _retired_path = SRC_ROOT + "/releases/20261004_probe_sources_retired/" + _retired
    assert os.path.exists(_retired_path), f"the preserved retired probe source is missing: {_retired_path}"

# the main mod must be byte-identical (untouched by this work)
main_src = open(SRC_ROOT + "/script/battle/mod/zz_test_deadly_onslaught.lua", "rb").read()
main_raw = bytes(c.send({"GetPackedFileRawData": [key, "script/battle/mod/zz_test_deadly_onslaught.lua"]})["VecU8"])
print(f"\n== 6d main mod untouched (byte-identical)     : {main_raw == main_src}")
assert main_raw == main_src, "the main mod changed - it must not"

step("7 save to disk", {"SavePackAs": [key, OUT_PACK]})
step("8 close", {"ClosePack": key})
try:
    c.send("ClientDisconnecting")
except Exception:
    pass  # the server shuts down as soon as the last session leaves

print("\n================ INSTALL ================")
shutil.copy2(OUT_PACK, GAME_PACK)
a = hashlib.md5(open(OUT_PACK, "rb").read()).hexdigest()
b = hashlib.md5(open(GAME_PACK, "rb").read()).hexdigest()
print(f"built pack   md5 {a}")
print(f"installed    md5 {b}")
print(f"IDENTICAL    {a == b}")
print(f"installed to {GAME_PACK}")
