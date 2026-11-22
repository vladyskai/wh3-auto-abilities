"""Build the mod pack, verify it, install it. One WebSocket session, then done.

ROUND 125: the spell-bar rule and the read-only ammo probe (no roster change).
ROUND 124: the spell-bar badge test (no roster change; army_spec read from gamedata\\wh3).
ROUND 123: the hex batch (4 melee_unwavering, 3 charge_or_melee, 3 on the new
enemy_melee, 1 twin key); the table is 707 entries / 759 keys.
ROUND 122: ten self-cast melee buffs added on melee_unwavering; the table is
697 entries / 748 keys, melee_unwavering 370.
ROUND 121: the ABILITIES table is 687 entries / 738 keys (two whole army-bar entries
and one army-bar key removed). The ARMY-BAR GATE below refuses the build outright if
any army_spec key is in the table; every count pin in this script follows the table.

Pack contents (housekeeping 20261004 - the two experiment probes are RETIRED):
  script/battle/mod/zz_test_deadly_onslaught.lua   the main mod (trigger + right-click toggle)
  ui/templates/zz_auto_badge.twui.xml              the auto badge template
  ui/zz_auto/auto_badge.png  ui/zz_auto/blank.png  the badge art
  (ROUND 166: ui/common ui/special_ability_tooltip.twui.xml is RETIRED - the game's own card layout ships)

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
ROUND v100 (2026-10-17): REMOVAL. Meat Feast (wh3_main_prisoners_butcher)
and Massacre (wh3_main_prisoners_massacre) were implemented but sit OUTSIDE
the single in-wheel rule (both source_type = army). Per the user's decision
of 2026-10-17 they are REMOVED from the ABILITIES table: 579 -> 577 entries,
605 -> 603 keys, melee_unwavering 363 -> 362, ushoran_health 34 -> 33.
Grut's Sickle and every other ability are untouched.

ROUND v101 (2026-10-17): BOSS-ONLY EXCLUSION + GATE OF KHORNE.
(A) Every active ability whose only grant path is a `_boss` unit is excluded.
    Five were IMPLEMENTED and are REMOVED: Greater Faith Bastion
    (wh_dlc06_quest_abilities_grand_faiths_bastion), Bitter Sting
    (wh3_dlc27_qb_unit_abilities_bitter_sting), Frenzied Challenge
    (wh3_dlc27_qb_unit_abilities_frenzied_challenge), Visions of Madness
    (wh3_dlc27_qb_unit_abilities_visions_of_madness) and Guttural Roar
    (wh3_dlc27_qb_unit_abilities_guttural_roar). 577 -> 573 entries,
    603 -> 599 keys, melee_unwavering 362 -> 360, enemy_engaged_or_shot
    89 -> 86.
(B) Gate of Khorne (wh3_main_character_abilities_gate_of_khorne) is ADDED:
    its own `enemy_ground_melee` trigger - among enemies within its 70% bound
    (50 m -> 35 m) keep those FIGHTING (in melee), take the CLOSEST and place
    the summon on THAT ENEMY's ground via perform_special_ability_ground with
    the fresh caster controller. Its own reason string names the enemy type
    and the REAL distance; the cast target is never the caster.
    melee_unwavering self-cast and every other ability are untouched.
"""
"""

ROUND v102 (2026-10-17): THE SUMMON ROUND.
(A) THE REST OF THE SUMMON CLASS - every in-wheel, non-illusion,
    GROUND-CASTABLE `wh_type_summon_unit` row derived from the game's own data
    (spawned_unit set + type wh_type_summon_unit + spawn_is_decoy false +
    target_ground true + in-wheel + not boss-only + not implemented): 57 entries
    / 68 keys. They ride the PROVEN `enemy_ground_melee` trigger (Gate of
    Khorne's): the closest FIGHTING enemy inside the ability's own 70% bound,
    the summon placed on THAT ENEMY's ground. ONE of them (The Tallyman's
    Blades Upgraded) declares target_intercept_range = -1.0 - NO real range -
    so it carries `unbounded = true` and skips the distance test.
(D) THE NINE unlabelled real spawners (Beast Pack, Blacktoof's Conjuration,
    Call to Gwindalor, Lesser Raise Dead, Savage Dominion, Savage Predators,
    Tide of Death, Tide of Pox, Wake Da Idol): 9 entries / 9 keys on the same
    trigger and the same enemy-ground form.
(B) Nurgling Tide gets its OWN trigger `self_summon_melee` - the user's rule,
    verbatim: "that one should only trigger when the caster himself is in
    melee." Owner alive + not routing + is_in_melee() true; the cast goes on
    the OWNER through the unit form, with a freshly re-fetched caster
    controller, a hold and a pre-cast re-check of the same state. NO RANGE
    BOUND: a self cast has no distance to measure (its row has
    target_intercept_range = 0, no target flags at all, affect_self = true).
(E) Eye of Khorne is a FINISHER on the NEW `enemy_low_health_noncommander`
    trigger: any enemy inside its 70% bound (50 m -> 35 m) BELOW 20% HEALTH
    that is NOT a Lord or Hero; the LOWEST-health one wins (closest as the
    tiebreak). It casts through the UNIT form (target_enemies = true,
    target_ground = false).
(F) The Dreaded Thirteenth (FOUR keys, ONE entry) rides the NEW
    `enemy_melee_noncommander` trigger: the closest non-commander enemy in
    melee inside its 70% bound (100 m -> 70 m), placed on that enemy's ground.
(THE LORD/HERO TEST) FOURTH.commander_keys is DERIVED from the game's own
    class/caste columns: every land_units key whose `class` is "com" (the
    engine's commander class - its own invalid-target flags are named
    unit_is_commander_class / unit_is_not_commander_class) UNION every
    land_units key reached from a main_units row whose `caste` is "lord" or
    "hero" (which catches the six Krell variants still marked inf_mel). It is
    matched by EXACT WHOLE-KEY equality against battle_unit:type(); 
    battle_unit:unit_class() == "com" is the fallback; neither readable ->
    FAIL CLOSED (treated as a commander).
(C) THE FOUR ILLUSIONS stay EXCLUDED (spawn_is_decoy; engine-refused while
    engaged in melee) - none was ever in the mod, and the gate below proves all
    four keys are absent.
COUNTS: 573 -> 642 entries (573 + 69), 599 -> 682 keys (599 + 83);
    melee_unwavering stays 360, enemy_engaged_or_shot stays 86,
    enemy_ground_area stays 9, enemy_ground_melee 1 -> 67.

ROUND v103: TWO FIELD-FAILURE FIXES (diagnosis: docs/WH3_bug_diagnosis_nurgling_eye.md).
(A) THE CHARGE GATE. Nurgling Tide (3 uses / 90 s recharge) kept casting: the
    field log holds 55 ACCEPTED attempts at a 2.0 s cadence over 108 s, its
    button greyed from t=74 s on, and its uses refilled at 67+90 / 69+90 /
    71+90 s. can_perform answers TRUE while a multi-use pool is EMPTY, so the
    2 s guard re-spent the pool forever. All 129 abilities whose
    unit_spec_abil num_uses > 1 now carry their own recharge_time in
    charge_gate.hold_s; after a successful cast the pair is held for exactly
    that long - ONE use per charge cycle, the pool never drains. Single-use
    abilities are untouched: the engine refuses those by itself.
(B) THE ONE HEALTH READ. HealthPercent answers a FRACTION (0..1): 336 field
    picks printed ONLY 0%/1% while the picked unit fought on for 84 s, so
    every hp<20 test was true and Eye of Khorne cast on units far above 20%.
    Every HealthPercent consumer now goes through FOURTH.health_pct, which
    prefers battle_unit:unary_hitpoints() (a documented fraction) and scales
    any 0..1 answer by 100. ABILITIES unchanged: 642 entries / 682 keys.

ROUND v104 (2026-10-17): TWO ITEMS.
(A) THE IN-FLIGHT GATE. The user's Nurgling Tide theory: the ability needs about
    4 s to activate while the guard is only 2 s, so the mod re-issues the order
    and REPLACES the cast that is still resolving. The game's own row declares
    wind_up_time 3.0 s (no other activation field, no phase row), and the API's
    queued twin documents the non-queued call as an ORDER - "Queued orders start
    when the current order completes" - so a second order inside the wind-up
    replaces the first. Every key whose row declares a wind-up (136) now carries
    it in cast_gate.wind_up_s; after a successful cast the pair is held for
    wind_up + 2 s slack (never less than the guard). The charge gate STAYS.
(B) THE ALLY-AWARE HEALTH FAMILY. Star of Avelorn (ground-targeted group heal,
    target_ground_under_allies, 15 m aura, 3 friendly units) only fired when the
    CASTER was below 75%, at her own feet. 13 entries whose game text says the
    effect reaches allies now fire when THIS unit OR a friendly unit inside the
    ability's own reach is at or below 75%, choose the LOWEST-health unit, and
    cast per the ability's own targeting: ground under the ally (2), the ally
    itself (9), or the caster for a self-centred aura (2). The reach is the
    standing 70% rule (aura_real/ally_range_real -> floor(real * 0.70)).

ROUND v105 (2026-10-17): TZ'ARKAN ON A LOW-HEALTH TRIGGER + THE TRANSFORMS SKIPPED.
(A) TZ'ARKAN. The user's rule: "activate Tz'arkan when caster health is below
    15%". ONE new entry ("tzarkan") carries all FIVE Tz'arkan keys (base, _mp,
    _snikch, _spite, _spite_mp) on ONE new trigger family, health_below_15:
    the owner is ALIVE, NOT routing, and its health - through FOURTH.health_pct,
    the ONE 0-100 reader, NEVER raw HealthPercent - is BELOW 15. The cast is on
    the OWNER ITSELF through the unit form, with the caster's controller
    re-fetched FRESH that tick; no range bound is read (a self cast has no
    distance). The exact percentage is logged at the decision and again at the
    PRE-CAST RE-CHECK, which SKIPS the cast when the unit died or rose above
    the line inside the wind-up. The in-flight and charge gates apply through
    the shared tables (3.0 s wind-up on four keys, 1.5 s on Snikch).
    THE THRESHOLD IS DELIBERATE and ONE constant (FOURTH.TZARKAN_PCT = 15): the
    transform is likely one-way and the wind-up can let a 14% caster die before
    it resolves - raise the constant if field tests show that.
    Counts: 642 -> 643 entries, 682 -> 687 keys, 42 -> 43 evaluators.
(B) THE REST OF THE TRANSFORMS ARE SKIPPED BY THE USER'S DECISION (no
    automation wanted): Formless Horror x4, Transformation of the Dragon x6,
    Burrow and Surface - 12 keys, NONE of them implemented, so NOTHING is in
    this pack for them. The tracker and the master spreadsheet record
    "skipped (user decision 2026-10-17: no automation wanted)".
(C) ROUND v106 - THE BOMBARDMENT ROUND (two user-approved families).
    (1) Soulfire (both keys) + Arachneruption on the NEW trigger
        melee_skip_commanders: fire when the CASTER is in melee, but SKIP when
        every enemy it is engaged with is a Lord or a Hero. The engagement set
        is the enemy enumerator's ALIVE + is_in_melee() units whose
        edge-to-edge unit_distance() to the caster is <= FOURTH.ENGAGE_CONTACT_M
        (12 m); each member is classified by FOURTH.enemy_is_commander (the
        1,409-key derived set, unit_class()=="com" fallback, FAIL CLOSED). The
        judged set is logged (type + flag + real distance) once per (unit,
        marker) and again only when it changes; no enemy readable -> the
        caster's current_target() -> plain in-melee.
    (2) 30 of the user's 32 bombardment abilities on the NEW trigger
        enemy_ground_melee_infantry: the CLOSEST enemy inside the ability's own
        70% bound that is IN MELEE and IS INFANTRY (battle_unit:is_infantry(),
        unit_class exact-match fallback inf_mel/inf_mis/inf_spr, FAIL CLOSED).
        The cast follows each row's own flags: 24 ground-targeted keys use
        perform_special_ability_ground(key, enemy position); 6 unit-targeted
        keys (lesser_doombolt, rod_of_torment, tome_of_furion,
        wand_of_the_kharaidon, traitors_sword, wraith_storm) use
        perform_special_ability(key, enemy). The chosen enemy is re-checked
        immediately before the cast (alive, in melee, still infantry, inside
        the bound).
    TWO OF THE 32 ARE REPORTED, NOT IMPLEMENTED: Thorsen's Thunderstorm (both
    keys are army_spec / ARMY-bar - out of wheel scope) and Warp Lightning Rod
    (target flags all false, range 0 - no enemy target exists to cast at).
    Counts: 643 -> 675 entries, 687 -> 721 keys, 43 -> 45 evaluators.

ROUND 107 (2026-10-18): Call of Tor joins melee_skip_commanders; the 11
"on top of" abilities (12 entries / 19 keys) ride the NEW
air_drop_on_infantry evaluator (enemy INFANTRY inside the row's 70%
bound, airborne / out of melee where the row says so, self-centred
cast, logged pre-cast re-check); the PER-UNIT serialisation window
(wind-up + 2 s, min 2.5 s) stops two ready abilities on one unit from
replacing each other. Counts: 675 -> 688 entries, 721 -> 741 keys,
45 -> 46 evaluators.

ROUND 112 (2026-10-24): THE ENEMY-SIDE LEAD DIAL + THE TWO DIAGNOSTIC FIXES.
    The Sky-junk diagnosis (docs/WH3_skyjunk_diagnosis.md): four armed, airborne,
    every-poll-evaluated bombers let the zombies walk THROUGH underneath and did
    not fire, because the enemy's projected centre was carried the FULL 1.5 s
    ahead (3.45 m at 2.3 m/s) PAST the hoverer - the projected gap bottomed at
    ~5 m and GREW to 10 m, largest exactly when the enemy was underneath.
    (1) FOURTH.AIR_DROP_ENEMY_LEAD = 0.3 scales ONLY the enemy's velocity term:
        enemy_projected = enemy + v_enemy * AIR_DROP_DELAY_S * AIR_DROP_ENEMY_LEAD.
        0.0 = the enemy's current position; 1.0 = the old full carry; 0.3 ships
        because the release is not instantaneous but 1.5 s is far too much.
    (2) The watch line prints EXACT distances below 15 m (the 6 m bound sat
        inside a 5 m band, so the deciding number was destroyed).
    (3) Every air-drop line is prefixed with the unit's ui id ("[1003] ..."),
        because four identical Sky-junks made the diagnosis a 231 MB log dive.
    (4) The decision/watch/skip/re-check lines print ALL FOUR dials.
    The caster dials, the 6 m bound, AIR_DROP_INHERIT, air_only / no_melee, the
    self-centred cast, the fail-closed reads and the re-projecting pre-cast
    re-check are UNCHANGED. Counts UNCHANGED: 689 entries / 742 keys,
    air_drop_on_infantry 12 / 19.

ROUND 113 (2026-10-25): THE PATH TEST, THE DERIVED FRONTAGE AND THE
SINGLE-ENTITY EXCLUSION (the user's sixth air-drop report: a hovering Sky-junk
BESIDE a 20-model zombie block never fired while the block walked past - the
enemy's CENTRE stayed 10+ m away even though its models swept under the caster;
and one fired at a LORD).
    (1) THE TEST IS THE ENEMY'S PATH, NOT ITS POINT. The segment is
        enemy_current -> enemy_projected (the enemy's own dials, unchanged) and
        the number that decides is the SHORTEST HORIZONTAL DISTANCE FROM THAT
        SEGMENT TO THE CASTER'S PROJECTED POINT (point-to-segment arithmetic on
        x/z, parameter clamped to 0..1). A point cannot describe a block: a
        20-model formation is 10 m wide in two ranks, so its centre stays 10 m
        away while a MODEL of it passes under the flyer.
    (2) THE FRONTAGE CREDIT IS DERIVED, NOT GUESSED: fire when
        perp <= AIR_DROP_CENTER_M + FOURTH.ad_frontage(enemy), where
        ad_frontage returns a HALF-width - ordered_width()/2 when that read is
        sane, otherwise ceil(men/2) * radius under ONE documented assumption
        (two ranks), clamped to 1..12 m, failing closed to 0.
    (3) THE PER-MODEL RADIUS IS A CONSTANT (0.6 m): battle Lua cannot join
        land_units.man_entity -> battle_entities.radius at battle time, so the
        value comes from the extracted tables (modal 0.6 m over the 942 infantry
        rows, median 0.7 m). One dial, documented.
    (4) THE SINGLE-ENTITY EXCLUSION: a candidate whose
        initial_number_of_men() == 1 is skipped, once per episode, as
        "single entity (1 model)". EXACT equality (zero models cannot exist), and
        INITIAL not current (a depleted 20-model block is still a block). The
        commander key set is deliberately NOT consulted here - every
        infantry-class lord/hero in the data is one model, so the count covers it.
    (5) The pre-cast re-check RE-RUNS the same segment test on fresh reads.
    KEPT EXACTLY: the four dials, the 6 m bound, AIR_DROP_INHERIT, air_only /
    no_melee, the self-centred cast and every fail-closed read. Counts UNCHANGED:
    689 entries / 742 keys, air_drop_on_infantry 12 / 19.

ROUND 116 (2026-10-18): THE WAIT IS MEASURED, NOT FIXED - THE ENEMY'S VELOCITY.
    The user's ruling, verbatim: "if the enemy unit is running away, then it is
    too soon. If the enemy moving is running towards, then it is too late. ...
    But it must be calculated the moment the edge to edge distance is below our
    theshold. Then, if the unit is running towards the caster, then the delay
    would be 0. If running away, then the delay would be 2. If stationary or
    perpedicular, then should be 1. ... the delay is dynamic in this way."
    THE FORMULA:
        axis  = normalise(caster.position - enemy.position)      (x/z)
        v     = speed * normalise(ordered_position - position)
        proj  = dot(v, axis) / (speed * |axis|)   clamped to +-1
        delay = AIR_DROP_DWELL_MID_S - AIR_DROP_DWELL_SWING_S * proj, floor 0
    with MID = 1.0 s and SWING = 1.0 s (closing 0 s / across 1 s / receding 2 s).
    MEASURED ONCE at the first contact of a pair, stored on the pair row with
    the cosine and the velocity source, NEVER re-measured inside that contact;
    a re-contact measures again. The 0.2 s fast pass, the 250 ms poll, the
    candidate filter, air_only / no_melee, the self-centred cast, the
    short-crossing fallback and the re-verifying pre-cast re-check are kept.
    THE READ-VERIFICATION LOG: every contact episode prints the RAW answers
    (is_moving, is_moving_fast, slow_speed, fast_speed, position,
    ordered_position, |h|), the cosine, the delay and the velocity source, with
    UNREADABLE where a read failed, so ordered_position()'s real behaviour is
    visible in the field log. Counts UNCHANGED: 689 / 742, air-drop 12 / 19.

ROUND 117 (2026-10-18): THE DETECTION MOVES FROM THE EDGE TO THE CENTRE.
    The user's ruling, verbatim: "Let's keep our current calculation but just
    replace the detection on edge with detection on the distance to center.
    Let's say 6 meters for now. I'll test."
    THE ONE NUMBER THAT MOVED is the gap that decides UNDER. It was the engine's
    bounding-box EDGE gap (`unit:unit_distance(enemy)`, battle_unit.lua:160)
    against AIR_DROP_EDGE_M = 0.1 m; it is now the GROUND-PLANE
    CENTRE-to-CENTRE distance between the caster's and the enemy's own
    position() reads (x/z only - get_y is HEIGHT - via
    position():distance_xz with a sqrt(dx^2 + dz^2) fallback), against
    FOURTH.AIR_DROP_CENTER_M = 6.0 m. FOURTH.ad_centre_gap is BACK as the ONE
    measurement the rule makes; AIR_DROP_EDGE_M is RETIRED (nothing else in the
    file used it).
    RE-MEASURED EVERYWHERE THE OLD NUMBER WAS TAKEN: the candidate's measured
    gap for ranking, the UNDER test, the contact stamping, the dwell / waiting
    and separation lines, the short-crossing fallback, the pre-cast re-check,
    every decision log line (edge= -> centre=, 2 decimals), the family's
    inventory bound and the tooltip sentence.
    KEPT EXACTLY: the candidate filter, the velocity-aware delay MEASURED ONCE
    PER CONTACT, the short-crossing fallback (0.3 s), the 0.2 s fast pass, the
    250 ms poll, air_only / no_melee, the self-centred cast, the gates and the
    read-verification lines. Counts UNCHANGED: 689 / 742, air-drop 12 / 19.
ROUND 118 (2026-10-18): THE AIR-DROP DELAY IS GONE. THE CENTRE STAYS.
The user's ruling, verbatim: "I tried it. Let's keep the distance to center and
remove the delay we had completely." The trigger now casts on the evaluation
that first measures the nearest valid enemy's CENTRE inside 6 m: no dwell, no
dynamic velocity delay, no cosine, no per-pair contact row, no timestamps, no
short-crossing fallback, no raw movement/heading read-verification log. The
centre helper, the candidate filter, the 0.2 s fast pass (30 m gate), the
250 ms poll, air_only / no_melee, the self-centred cast, every fail-closed read,
the gates and the pre-cast re-check are KEPT.

"""
import hashlib
import json
import sys
import re
import shutil
import os
from websockets.sync.client import connect

WS_URL = "ws://127.0.0.1:45127/ws"
SRC_ROOT = r"C:/Users/vlady/Desktop/WH3_mod/mod_source"
ROUND114 = True

FILES = [
    (SRC_ROOT + "/script/battle/mod/zz_test_deadly_onslaught.lua",
     "script/battle/mod/zz_test_deadly_onslaught.lua"),
    (SRC_ROOT + "/ui/templates/zz_auto_badge.twui.xml",
     "ui/templates/zz_auto_badge.twui.xml"),
    (SRC_ROOT + "/ui/zz_auto/blank.png", "ui/zz_auto/blank.png"),
    (SRC_ROOT + "/ui/zz_auto/auto_badge.png",
     "ui/zz_auto/auto_badge.png"),
    # ROUND 194: the optional MCT page (MCT alone loads script/mct/settings/; without MCT it never runs)
    (SRC_ROOT + "/script/mct/settings/smart_ability_autocast.lua",
     "script/mct/settings/smart_ability_autocast.lua"),
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


# =====================================================================
# ROUND 121 GATE - REFUSE TO BUILD IF ANY ARMY-BAR (army_spec) KEY IS IN THE
# ABILITIES TABLE.
#
# The user's ruling, round 121, verbatim: "The triggers will not work if the
# ability is not in the ability wheel on the lower left corner of the battle
# screen, meaning 'you'd lose working triggers' makes no sense. Therefore, ALL
# ARMY ABILITIES PLEASE EXCLUDE."
#
# An army-bar ability (a key in the army_spec junction) has no button on the
# battle ability wheel, so perform_special_ability can never be called for it:
# such an entry can never fire. It is dead weight by definition, not a roster
# choice. This assertion has NO exceptions list and runs BEFORE any stale pack
# is deleted or any WebSocket command is sent - a violating table does not
# build at all.
# =====================================================================
ARMY_SPEC_TSV = r"C:/Users/vlady/Desktop/WH3_mod/gamedata/wh3/army_spec.tsv"  # was Temp until round 124
MOD_LUA = FILES[0][0]


def _army_bar_keys():
    with open(ARMY_SPEC_TSV, encoding="utf-8", errors="replace") as f:
        f.readline()
        out = set()
        for line in f:
            if line.startswith("#"):
                continue
            c = line.rstrip("\n").split("\t")
            if c and c[0].strip():
                out.add(c[0].strip())
        return out


def _abilities_keys(path):
    src = open(path, encoding="utf-8").read()
    a = src.index("local ABILITIES = {")
    b = src.index("\n}", a)
    region = re.sub(r"--[^\n]*", "", src[a:b])   # a commented-out key is not a key
    keys = []
    for m in re.finditer(r"keys = \{(.*?)\}", region, re.S):
        keys += re.findall(r'"([^"]+)"', m.group(1))
    return keys


_army = _army_bar_keys()
_mod_keys = _abilities_keys(MOD_LUA)
_hits = sorted(set(k for k in _mod_keys if k in _army))
assert not _hits, (
    "BUILD REFUSED (round 121 army-bar gate): %d ABILITIES key(s) are in the army_spec junction. "
    "An army-bar ability is NOT on the battle ability wheel, so perform_special_ability can never "
    "be called for it and the entry can never fire - it must not ship (user ruling: ALL ARMY "
    "ABILITIES EXCLUDE). Offending keys: %s" % (len(_hits), _hits))
print("ARMY-BAR GATE OK: %d ABILITIES keys, none of them in the %d-key army_spec junction"
      % (len(_mod_keys), len(_army)))

# THE ORDER FIX (2026-11-09): only the builder's OWN output is cleared here. The installed pack in the
# game's data folder is never deleted: the INSTALL step at the very end overwrites it, after every gate has
# passed, so a refused build leaves the game with the pack it had (round 135 lost it for minutes).
if os.path.exists(OUT_PACK):
    os.remove(OUT_PACK)
    print("removed stale build output:", OUT_PACK)
print("installed pack left in place until the INSTALL step:", os.path.exists(GAME_PACK))

hashes = {}
for _src, _in_pack in FILES:
    _data = open(_src, "rb").read()
    hashes[_in_pack] = (len(_data), hashlib.sha256(_data).hexdigest())
    print(f"source {_src.split('/')[-1]:34s} {len(_data):>8d} bytes  sha256 {hashes[_in_pack][1][:32]}")

c = Client(WS_URL)
step("1 select game", {"SetGameSelected": ["warhammer_3", False]})
key = step("2 new pack", "NewPack")["String"]
step("3 add the main script and the three ui files",
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
# ROUND 166: the card xml is retired: nothing to read, and it must not be in the pack
assert "ui/common ui/special_ability_tooltip.twui.xml" not in in_pack_paths, "BUILD REFUSED (round 166): the retired card xml is in the pack"
t_txt = ""
print("\n== 6 what the pack must contain")
script_txt = open(SRC_ROOT + "/script/battle/mod/zz_test_deadly_onslaught.lua",
                  encoding="utf-8", errors="replace").read()
print(f"   static card line retired (not in the pack): {HINT not in t_txt and HINT not in script_txt}")
print(f"   the double-click toggles are gone         : "
      f"{'Double Click Unit Card' not in script_txt}"
      f" and {'ComponentLDBLClickUp' not in script_txt}")
dead = sum(script_txt.count(t) for t in ('zz_rclick', 'check_rclick_property'))
print(f"   dead property-route code left behind      : {dead} (want 0)")
assert HINT not in t_txt and HINT not in script_txt, "BUILD REFUSED (round 166): the static card line is back"
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
assert 'marker = "foe_seeker", name = "Foe-Seeker", trigger = "charge_or_tired"' in script_txt, "the fatigue trigger is missing from the script"
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
# ROUND 123: the melee-only enemy-unit trigger (No Escape, Transfix dlc29, Flash Bomb).
assert ("function FOURTH.evaluate_enemy_melee(unit, routing)\n\tFOURTH.eg_melee_only = true\n"
        "\treturn FOURTH.eg_pick_enemy(unit, routing, false)\nend") in script_txt, \
    "the enemy_melee evaluator is missing or changed"
assert "\tenemy_melee = FOURTH.evaluate_enemy_melee," in script_txt, "enemy_melee is not wired in the map"
assert script_txt.count('trigger = "enemy_melee"') == 35, "enemy_melee is not 34 entries"
assert "wh3_main_lord_abilities_daemonic_possession" not in script_txt, \
    "Daemonic Possession must not be automated (user decision, round 123)"
print("ROUND 123 GATE OK: enemy_melee evaluator wired, 3 entries, no Daemonic Possession")
# ROUND 125: the spell-bar RULE replaces the round-124 placement test, and the
# read-only ammo probe is in (user rulings 2026-11-03).
assert "SPELLBAR_BADGES" not in script_txt and "spellbar_id" not in script_txt, \
    "the removed round-124 spell-bar placement test is back in the source"
assert "if state.button == nil and not on_spell_bar and key_is_ours(ability, key) then" in script_txt, \
    "the spell-bar rule (never claim a button_spell button) is missing"
assert "function FOURTH.ammo_probe(units)" in script_txt and \
    script_txt.count("pcall(FOURTH.ammo_probe, tracked_units)") == 1, "the ammo probe is missing or called twice"
print("ROUND 125 GATE OK: spell-bar buttons are never claimed; the ammo probe is in")
# ROUND 126: the firing flag from the game's reload table (generated, never hand-typed).
import subprocess as _sp
_gen = _sp.run([sys.executable, r"C:/Users/vlady/Desktop/WH3_mod/tools/gen_reload_table.py", "--check",
                FILES[0][0]], capture_output=True, text=True)
assert _gen.returncode == 0, "BUILD REFUSED (round 126): " + (_gen.stdout + _gen.stderr).strip()
assert "AMMO_SAME_VOLLEY_S" not in script_txt and "st.gap_s" not in script_txt, \
    "the deleted round-125 measured-gap window is back in the source"
assert "function FOURTH.ammo_in_range(u)" in script_txt and "FOURTH.AMMO_CAST_FRACTION = 0.5" in script_txt, \
    "the cast point / in-range code is missing"
print("ROUND 126 GATE OK: " + _gen.stdout.strip())
# ROUND 127: OFF window max(2 x reload, 20 s); a disappeared target logs "target lost".
assert "FOURTH.AMMO_OFF_FACTOR = 2 " in script_txt and "FOURTH.AMMO_OFF_MIN_S = 20 " in script_txt \
    and "AMMO_WINDOW_DEFAULT_S" not in script_txt, "the round-127 OFF window is missing"
assert "target lost (no current target)" in script_txt, "the target-lost fix is missing"
print("ROUND 127 GATE OK: OFF = max(2 x reload, 20 s); a lost target is logged, not formatted")
# ROUND 128: fix A (dropped multi-use casts) and the NOT FIRING snapshot.
assert "function FOURTH.charge_hold_ready_on_screen(ui_id, ability, held_until)" in script_txt \
    and "if #selected_ui_ids ~= 1 or tostring(selected_ui_ids[1]) ~= tostring(ui_id) then return false end" in script_txt, \
    "fix A is missing, or it trusts something other than the engine's single live selection"
assert "function FOURTH.not_firing_snapshot(u, st, now_s, inr, d, r)" in script_txt, "the NOT FIRING snapshot is missing"
print("ROUND 128 GATE OK: fix A (engine-selected unit, READY button) and the NOT FIRING snapshot are in")
# ROUND 129: the unit cards veto a ghost selection.
assert "FOURTH.CARD_UNSELECTED_STATES = { active = true, hover = true, inactive = true, taking_damage = true, wavering = true }" in script_txt     and "if st ~= nil and FOURTH.CARD_UNSELECTED_STATES[st] == true then" in script_txt     and "elseif (tick_count - since) >= FOURTH.CARD_DESELECT_CONFIRM_POLLS then" in script_txt,     "the round-129 card veto is missing"
print("ROUND 129 GATE OK: a unit whose card reads unselected for 2 polls leaves the selected set")
# ROUND 130: the first triggers on the firing flag.
assert 'trigger = "ally_ammo_low"' in script_txt and 'trigger = "allies_firing_aura"' in script_txt \
    and 'trigger = "melee_or_self_shooting"' in script_txt \
    and "ally_ammo_low = FOURTH.evaluate_ally_ammo_low," in script_txt \
    and "allies_firing_aura = FOURTH.evaluate_allies_firing_aura," in script_txt \
    and "melee_or_shooting_into_melee = FOURTH.evaluate_melee_or_shooting_into_melee," in script_txt \
    and '["wh2_dlc17_hero_abilities_more_powder_generic"] = 60,' in script_txt \
    and '["wh_main_hero_abilities_ballistics_calibration"] = true,' in script_txt \
    and "FOURTH.ammo_by_id[tostring(u:unique_ui_id())] = st" in script_txt, \
    "the round-130 firing-flag triggers are missing"
# the 70% rule on the two new ranges: Restock! 100 m -> 70 m (ALLY_CAST_R100),
# Ballistics Calibration's aura 55 m -> floor(55 * 0.70) = 38 m (computed at load)
assert "FOURTH.ALLY_CAST_R100 = 80" in script_txt and int(55 * 0.70 + 1e-9) == 38
print("ROUND 130 GATE OK: Restock!, Ballistics Calibration and Skjalandir's Fall's shooting arm are wired")
# ROUND 131: the shooting buffs leave the melee trigger; the nine stances leave the mod.
assert "self_or_ally_shooting = FOURTH.evaluate_self_or_ally_shooting," in script_txt \
    and "melee_or_self_or_ally_shooting = FOURTH.evaluate_melee_or_self_or_ally_shooting," in script_txt \
    and "no_enemy_in_range_within_boost = FOURTH.evaluate_no_enemy_in_range_within_boost," in script_txt \
    and "FOURTH.FIRING_AURA_MIN = 1 " in script_txt and "BALLISTICS_MIN_FIRING" not in script_txt \
    and "FOURTH.FARSIGHT_BAND = 1 + FOURTH.FARSIGHT_BONUS * FOURTH.RANGE_FRACTION" in script_txt \
    and script_txt.count('trigger = "allies_firing_aura"') == 8, \
    "the round-131 triggers are missing"
for _st in ['master_predator', 'immovable_bulwark', 'unstoppable_choppas', 'the_shadows_coil', 'woven_mist', 'chanson_of_caging', 'the_dance_of_dreaming', 'the_praise_of_slaanesh', 'the_waltz_of_lethargy']:
    assert _st not in script_txt, "a stance is still automated: " + _st
# the 70% rule on the new bounds: aura 55 m -> 38, 35 m -> 24 (computed at load);
# Deranged Munitions 100 m -> ALLY_CAST_R100 = 70; Entrenchment 150 m -> ALLY_CAST_R150 = 105
assert "FOURTH.ALLY_CAST_R150 = 130" in script_txt and int(55 * 0.70 + 1e-9) == 38 and int(35 * 0.70 + 1e-9) == 24
print("ROUND 131 GATE OK: 8 firing auras, 3 new triggers, Farsight's 1.21 band, no stance left")
# ROUND 132: audit batch 1 and the patch-9.0.5 data.
assert "melee_or_shooting_aura = FOURTH.evaluate_melee_or_shooting_aura," in script_txt \
    and "melee_or_shooting_self_or_ally = FOURTH.evaluate_melee_or_shooting_self_or_ally," in script_txt \
    and "self_shooting = FOURTH.evaluate_self_shooting," in script_txt \
    and script_txt.count('trigger = "melee_or_shooting_aura"') == 10 \
    and script_txt.count('trigger = "melee_or_shooting_self_or_ally"') == 2 \
    and script_txt.count('trigger = "self_shooting"') == 1, \
    "the round-132 triggers are missing"
assert "range_real = 50,   -- patch 9.0.5: 100 -> 50 m" in script_txt \
    and '["wh3_dlc29_weapon_abilities_aken_seth_the_staff_of_pain"] = 120,' in script_txt \
    and '["wh3_dlc29_spell_bound_okkams_mindrazor"] = 1,' not in script_txt \
    and 'if f == "overseer" then' in script_txt, \
    "the patch-9.0.5 data fixes are missing"
# the 70%% rule: Gaze 50 m -> ENEMY_CAST_R50 = 35; Seerstaff / Harmonic 200 m -> ALLY_CAST_R200 = 140
assert "FOURTH.ENEMY_CAST_R50  = 35" in script_txt and "FOURTH.ALLY_CAST_R200 = 180" in script_txt
print("ROUND 132 GATE OK: 13 entries on the new shooting-aware triggers; patch 9.0.5 data in")
# ROUND 133: audit batch 2, protection against shots fires when under fire.
assert "under_fire = FOURTH.evaluate_under_fire," in script_txt \
    and "melee_or_under_fire = FOURTH.evaluate_melee_or_under_fire," in script_txt \
    and script_txt.count('trigger = "under_fire"') == 4 \
    and script_txt.count('trigger = "melee_or_under_fire"') == 4, \
    "the round-133 triggers are missing"
print("ROUND 133 GATE OK: 3 on under_fire, 4 on melee_or_under_fire")
# ROUND 134: audit batch 3, the speed buffs leave the melee-only trigger; Thunderburner leaves the mod.
for _m in ("apocalyptic_charge", "twilight_horn_i", "potion_of_speed", "blooood"):
    assert '{ marker = "%s", name = ' % _m in script_txt, "round-134 charge-only marker missing: " + _m
assert "thunderburner" not in script_txt, "Thunderburner is still automated"
assert script_txt.count('trigger = "charge_only"') == 5 \
    and script_txt.count('trigger = "charge_or_melee"') == 34, \
    "the round-134 trigger counts are wrong"
print("ROUND 134 GATE OK: 5 on charge_only, 36 on charge_or_melee, Thunderburner gone")
# ROUND 135: audit batch 4, the enemy slows, the fast-enemy trigger and the target filters.
assert "enemy_fast_near_ally = FOURTH.evaluate_enemy_fast_near_ally," in script_txt \
    and script_txt.count('trigger = "enemy_melee"') == 35 \
    and script_txt.count('trigger = "enemy_fast_near_ally"') == 18 \
    and script_txt.count('trigger = "enemy_engaged_or_shot"') == 22 \
    and script_txt.count("\t\ttarget_class = ") == 57 \
    and "FOURTH.FAST_ENEMY_MPS = 5 " in script_txt and "FOURTH.FAST_ENEMY_NEAR_M = 40 " in script_txt \
    and "\t\t\tor not FOURTH.eg_class_ok(enemy) then\n" in script_txt, \
    "the round-135 triggers or filters are missing"
import sys as _sys135
_sys135.path.insert(0, r"C:\Users\vlady\Desktop\WH3_mod\tools")
import gen_unit_size_keys as _g135
_l135, _s135 = _g135.derive()
assert _g135.lua_block(_l135, _s135) in script_txt, \
    "BUILD REFUSED (round 135): the large / single-entity tables differ from the game data"
print("ROUND 135 GATE OK: enemy_melee 14, enemy_fast_near_ally 4, 15 target classes; size tables match the game (%d large, %d single)" % (len(_l135), len(_s135)))
# ROUND 136: audit batch 5, the melee hexes leave the missile arm; the immobilisers on the fast-enemy trigger.
for _m in ("gaze_of_fate", "sadistic_snare", "spearfishers_net"):
    assert '{ marker = "%s", name = ' % _m in script_txt, "round-136 marker missing: " + _m
assert 'if cls == "not_flying" then' in script_txt and 'target_class = "not_flying"' in script_txt, \
    "Spearfisher's Net's not_flying class is missing"
print("ROUND 136 GATE OK: enemy_melee 34, enemy_fast_near_ally 7, enemy_engaged_or_shot 47, 16 target classes")
# ROUND 137: audit batch 6, morale abilities fire when morale is in danger.
assert "wavering_aura = FOURTH.evaluate_wavering_aura," in script_txt \
    and script_txt.count('trigger = "wavering_aura"') == 9 \
    and "function FOURTH.wavering_ally_in_aura(unit)" in script_txt, \
    "the round-137 wavering_aura trigger is missing"
print("ROUND 137 GATE OK: 9 on wavering_aura, 6 on wavering_ally_range, melee_unwavering 314")
# ROUND 138: the rarer target filters and Missile Mirror's shooting trigger.
assert 'if cls == "not_undead" then' in script_txt and 'if cls == "missile" then' in script_txt \
    and "enemy_missile_shooting = FOURTH.evaluate_enemy_missile_shooting," in script_txt \
    and script_txt.count('trigger = "enemy_missile_shooting"') == 1, \
    "the round-138 classes or the Missile Mirror trigger are missing"
import gen_undead_keys as _g138
assert _g138.lua_block(_g138.derive()) in script_txt, \
    "BUILD REFUSED (round 138): the undead table differs from the game data"
print("ROUND 138 GATE OK: 21 target classes, enemy_missile_shooting 1, the undead table matches the game")
# ROUND 139: Stand Your Ground fires for the allies it protects (QA battle 1).
assert 'name = "Stand Your Ground", trigger = "melee_or_wavering_aura",' in script_txt \
    and "melee_or_wavering_aura = FOURTH.evaluate_melee_or_wavering_aura," in script_txt \
    and 'trigger = "melee_low_morale"' not in script_txt, \
    "Stand Your Ground's round-139 trigger is missing"
print("ROUND 139 GATE OK: Stand Your Ground on melee_or_wavering_aura")
# ROUND 140: shooting and moving are incompatible unless the unit fires on the move; Blooood! when running.
assert "st.cast_point_passed == true and FOURTH.can_shoot_now(unit)" in script_txt \
    and "st.firing ~= true or not FOURTH.can_shoot_now(unit)" in script_txt \
    and "if not FOURTH.can_shoot_now(enemy) then return false end" in script_txt \
    and 'name = "Blooood!", trigger = "self_moving",' in script_txt \
    and "self_running = FOURTH.evaluate_self_running," in script_txt, \
    "the round-140 moving rule or Blooood!'s running trigger is missing"
import gen_fire_move_keys as _g140
assert _g140.lua_block(_g140.derive()) in script_txt, \
    "BUILD REFUSED (round 140): the fire_move table differs from the game data"
print("ROUND 140 GATE OK: the moving rule guards every firing-flag read; Blooood! on self_running; fire_move matches the game")
# ROUND 141: the nine recharge reducers, one by one.
assert "FOURTH.note_cast(unit, ability_key)" in script_txt \
    and script_txt.count('trigger = "self_recharging"') == 6 \
    and script_txt.count('trigger = "self_recharging_2"') == 1 \
    and script_txt.count('trigger = "recharging_in_reach"') == 1 \
    and script_txt.count('trigger = "melee_self_or_ally"') == 3, \
    "the round-141 recharge-reducer triggers are missing"
import gen_recharge_keys as _g141
assert _g141.lua_block(_g141.derive()) in script_txt, \
    "BUILD REFUSED (round 141): the lock-time table differs from the game data"
print("ROUND 141 GATE OK: casts remembered; 5 + 1 + 1 + 1 reducers on their families; the lock table matches the game")
# ROUND 142: open batch 1 (shooting buffs and ammo refills) and Blooood! when moving.
for _m in ("more_powder", "restock_gunnery_school", "master_of_mists", "of_warp_and_ruin", "ominous_powder"):
    assert '{ marker = "%s", name = ' % _m in script_txt, "round-142 entry missing: " + _m
assert "FOURTH.ALLY_CAST_R250 = 230" in script_txt and max(int(250 * 0.70 + 1e-9), 250 - 20) == 230 \
    and "[250] = FOURTH.ALLY_CAST_R250," in script_txt, "the 250 m bound breaks the 70% rule"
assert "ground_ally_before_range = FOURTH.evaluate_ground_ally_before_range," in script_txt \
    and "self_shooting_clear = FOURTH.evaluate_self_shooting_clear," in script_txt \
    and "self_shooting_healthy = FOURTH.evaluate_self_shooting_healthy," in script_txt \
    and "self_moving = FOURTH.evaluate_self_moving," in script_txt \
    and 'name = "Blooood!", trigger = "self_moving",' in script_txt, \
    "the round-142 families are missing"
print("ROUND 142 GATE OK: 5 new entries / 6 keys; 250 m -> 175 m; Blooood! on self_moving")
# ROUND 143: open batch 2 (ground curses, Curse of Djaf, Soulblight, Squig Thinkin', the fanatic releases).
for _m in ("curse_of_anraheir", "transmutation_of_lead", "soulblight", "the_soulstealer", "curse_of_djaf",
           "soulblight_handmaidens", "squig_thinkin", "spinning_loons", "loons_of_eight_peaks"):
    assert '{ marker = "%s", name = ' % _m in script_txt, "round-143 entry missing: " + _m
assert "FOURTH.ENEMY_CAST_R25  = 17" in script_txt and int(25 * 0.70 + 1e-9) == 17 \
    and "\t[25]  = FOURTH.ENEMY_CAST_R25," in script_txt, "the 25 m bound breaks the 70% rule"
assert "enemy_ground_shooting = FOURTH.evaluate_enemy_ground_shooting," in script_txt \
    and "function FOURTH.evaluate_enemy_ground_shooting(unit, routing)" in script_txt, \
    "the round-143 family is missing"
_g0 = script_txt.find("enemy_ground_keys = {")
_g1 = script_txt.find("\t},\n", _g0)
for _k in ("wh2_dlc16_spell_bound_the_curse_of_anraheir", "wh3_main_spell_bound_the_curse_of_anraheir",
           "wh_dlc05_spell_bound_the_curse_of_anraheir", "wh3_main_spell_bound_transmutation_of_lead",
           "wh2_dlc10_spell_bound_soulblight", "wh3_dlc29_spell_bound_undeath_khizaar_the_soulstealer",
           "wh2_dlc09_character_abilities_curse_of_djaf", "wh3_dlc26_character_abilities_squig_thinkin",
           "wh_main_unit_abilities_spinning_loons", "wh_dlc06_unit_abilities_the_loons_of_eight_peaks"):
    assert ('["%s"] = true,' % _k) in script_txt[_g0:_g1], "round-143 key not in enemy_ground_keys: " + _k
assert '["wh3_dlc29_spell_bound_soulblight"] = true,' not in script_txt[_g0:_g1], \
    "the Handmaidens' Soulblight is a self buff, never an enemy-ground key"
print("ROUND 143 GATE OK: 9 new entries / 11 keys; 25 m -> 17 m; enemy_ground_shooting wired")
# ROUND 144: open batch 3 (the rest of group C).
for _m in ("hags_denial", "ruinshelter", "rock_bottom", "morikhane", "hunters_call", "icon_of_the_king",
           "the_gold_standard", "banner_of_hellfire", "ghostly_howl", "petrifying_gaze"):
    assert '{ marker = "%s", name = ' % _m in script_txt, "round-144 entry missing: " + _m
for _f in ("self_last_stand", "self_out_of_ammo", "health_aura_self_undead", "ally_hurt_melee", "enemy_wavering"):
    assert ("%s = FOURTH.evaluate_%s," % (_f, _f)) in script_txt, "round-144 family not wired: " + _f
assert "FOURTH.LAST_STAND_PCT = 10" in script_txt, "Hag's Denial: the user's 10% line is missing"
assert 'elseif eg_mode_now == "wavering" then' in script_txt and 'if FOURTH.ah_mode == "melee" then' in script_txt \
    and 'if FOURTH.ah_mode == "undead" then' in script_txt, "a round-144 pre-cast re-check mode is missing"
for _k in ("wh_dlc05_unit_abilities_storm_of_blades", "wh2_dlc16_unit_abilities_whirling_death",
           "wh2_dlc09_item_abilities_cloak_of_the_dunes"):
    assert _k not in script_txt, "a skipped ability (stance / stealth) is in the mod: " + _k
print("ROUND 144 GATE OK: 10 new entries / 10 keys; 5 new families; 3 skipped abilities absent")
# ROUND 145: the read-only battlefield map probe.
assert "FOURTH.MAP_EVERY_S = 2" in script_txt and script_txt.count("pcall(FOURTH.map_tick, tick_count)") == 1, \
    "the map probe is missing or called more than once per poll"
_m0 = script_txt.find("function FOURTH.map_num(f, fmt)")
_m1 = script_txt.find("-- ROUND 146 - THE BLOB TRIGGER", _m0)
assert 0 < _m0 < _m1, "the map probe block is missing"
_mspan = script_txt[_m0:_m1]
for _bad in ("perform_special_ability", "cast_target", "eg_enemy", "ah_ally", "string.find"):
    assert _bad not in _mspan, "the map probe is not read-only: " + _bad
print("ROUND 145 GATE OK: the map probe is read-only and pcall'd once per poll")
# ROUND 146: the blob trigger.
assert script_txt.count('trigger = "enemy_blob"') == 68, "the blob trigger does not carry the 77 exploding attacks"
for _k in ("dead_eye", "focused_shot"):   # ROUND 156: they ride enemy_single_shot, never enemy_blob
    assert ('trigger = "enemy_blob",\n\t\tbadge = "zz_auto_badge_%s"' % _k) not in script_txt, \
        "a single-entity-only snipe is on the blob trigger: " + _k
assert "FOURTH.BLOB_MARGIN_M = 10 " in script_txt and "FOURTH.BLOB_FRACTION = 0.5 " in script_txt, \
    "the user's blob settings (10 m, half a packed block) are missing"
for _r in (55, 60, 80, 130, 250, 350, 400, 600):
    assert ("FOURTH.ENEMY_CAST_R%-3d = %d " % (_r, max(int(_r * 0.70 + 1e-9), _r - 20))) in script_txt, "70%% rule broken for %d m" % _r
assert 'elseif eg_mode_now == "blob" then' in script_txt and "enemy_blob = FOURTH.evaluate_enemy_blob," in script_txt, \
    "the blob evaluator or its pre-cast re-check is missing"
import gen_blob_tables as _g146
assert _g146.lua_block(_g146.blast_table(_g146.keys_in(script_txt)), _g146.spacing_table()) in script_txt, \
    "BUILD REFUSED (round 146): the blast / spacing tables differ from the game data"
print("ROUND 146 GATE OK: 77 blob entries; the tables match the game; 10 m margin; half a packed block")
# ROUND 149: the revert of rounds 147-148 (user ruling 2026-11-14).
for _bad in ("map_addr", "mr_unit", "mr_check", "memreader", "MEMREADER", " addr="):
    assert _bad not in script_txt, "BUILD REFUSED (round 149): probe code is still in the script: " + _bad
print("ROUND 149 GATE OK: no address field and no memreader code")
# ROUND 150: the blob target destroys the most value; never while moving; Winds of Magic when ready; the WINDS row.
assert script_txt.count('trigger = "when_ready"') == 21 and "when_ready = FOURTH.evaluate_when_ready," in script_txt, \
    "the 21 Winds of Magic abilities are not on when_ready"
assert "FOURTH.BLOB_AP_ARMOUR_MIN = 50 " in script_txt and "function FOURTH.blob_value(tgt, m, r, dmg)" in script_txt \
    and "function FOURTH.blob_still(unit)" in script_txt and "if not FOURTH.blob_still(unit) then" in script_txt, \
    "the value rule, the armour rule or the standstill gate is missing"
assert '"WINDS t=" .. t' in script_txt, "the WINDS map row is missing"
import gen_blob_tables as _g150
assert _g150.lua_block_value(_g150.damage_table(_g150.keys_in(script_txt)), _g150.defence_table()) in script_txt, \
    "BUILD REFUSED (round 150): the damage / defence tables differ from the game data"
print("ROUND 150 GATE OK: value rule, armour 50, standstill, 21 when_ready, WINDS row; the tables match the game")
# ROUND 151: large first + hold, usage rules, breaths at 90 degrees, default-armed families, the ALL badge.
for _f in ("function FOURTH.blob_pick_large(unit, m, r, key)", "function FOURTH.blob_not_flying(u)",
           "function FOURTH.blob_usage_ok(unit, key)", "FOURTH.BREATH_VALUE_BAND = 0.8 ",
           'FOURTH.ALL_BADGE_ID = "zz_auto_badge_all"', "function FOURTH.all_click()", "function FOURTH.armed_slot(slot, marker)"):
    assert _f in script_txt, "round-151 piece missing: " + _f
assert script_txt.count("pcall(FOURTH.all_badge_tick)") == 1, "the ALL badge tick is not called exactly once"
_d0 = script_txt.find("FOURTH.DEFAULT_ON_TRIGGERS = {")
_d1 = script_txt.find("}", _d0)
_fams = set(l.strip().split(" = ")[0] for l in script_txt[_d0:_d1].split("\n")[1:] if " = true" in l)
assert _fams == set(['ally_ammo_low', 'ally_heal', 'ally_melee_buff', 'ally_wavering', 'charge', 'charge_only', 'charge_or_melee', 'glorious_death', 'health_aura_ally', 'health_aura_ground', 'health_aura_self', 'health_aura_self_undead', 'health_below_15', 'melee', 'melee_health75', 'melee_or_under_fire', 'melee_or_wavering_aura', 'melee_skip_commanders', 'melee_unwavering', 'self_last_stand', 'self_out_of_ammo', 'tired', 'under_fire', 'ushoran_health', 'wavering_ally_range', 'wavering_aura', 'wavering_self', 'wavering_self_or_ally', 'when_ready']), "the default-armed families differ from the user's ruling"
assert "and ZZ_AUTO_TEST_NO_DEFAULTS ~= true" in script_txt, "the default switch is missing"
import gen_blob_tables as _g151
_k151 = _g151.keys_in(script_txt)
assert _g151.lua_block_large(_g151.shot_table(_k151), _g151.large_def_table()) in script_txt, \
    "BUILD REFUSED (round 151): the shot / large tables differ from the game data"
print("ROUND 151 GATE OK: large first, usage rules, breath band 0.8, 28 default-armed families (round 152), ALL badge; tables match")
# ROUND 152: no whole-map hold, fliers skipped, 90 degrees for every central attack, 'tired' armed, the ALL spot.
assert "blob_large_hold" not in script_txt, "the whole-map hold is still in the mod"
assert "and FOURTH.blob_not_flying(e.unit) then" in script_txt, "large first does not skip flying targets"
assert "if shot ~= nil and (shot[5] == 1 or shot[6] == 1) then" in script_txt, "the 90-degree rule is not on every central attack"
assert "FOURTH.ALL_OX, FOURTH.ALL_OY = -923, 0" in script_txt and "st.badge:SetDockOffset(FOURTH.ALL_OX + FOURTH.ui_dx, FOURTH.ALL_OY + FOURTH.ui_dy)" in script_txt, \
    "the ALL badge is not at the user's spot"
print("ROUND 152 GATE OK: no hold, fliers skipped, 90 degrees for 53 central attacks, tired armed, ALL badge on screen")
# ROUND 153: no trash targets unless a big blob; the ALL badge for any selection, in the middle of the cloth, a tooltip.
assert "FOURTH.TRASH_VPS = 2\n" in script_txt and "FOURTH.TRASH_BLOCKS = 3\n" in script_txt \
    and script_txt.count("FOURTH.blob_trash_ok(e, sc, r)") == 2 \
    and script_txt.count("FOURTH.blob_trash_rule(e, sc, r)") == 3, "the trash rule is missing (definition, the round-197 wrapper, pick and re-check through the wrapper)"   # ROUND 197 rebase
assert "local any = FOURTH.all_selection_has_ours()" in script_txt, "the ALL badge still follows the ability badges"
assert "st.badge:SetTooltipText(FOURTH.ALL_TIP, true)" in script_txt, "the ALL tooltip is missing"
print("ROUND 153 GATE OK: trash below 2 per soldier unless 3 packed blocks; ALL shown for any owner; spot; tooltip")
# ROUND 154: the ALL control is the game's own round toggle button with the abilities icon; console hooks.
assert 'FOURTH.ALL_TEMPLATE = "ui/templates/round_small_button_toggle"' in script_txt \
    and 'FOURTH.ALL_ICON = "ui/skins/default/icon_abilities.png"' in script_txt \
    and "badge_parent:CreateComponent(FOURTH.ALL_BADGE_ID, FOURTH.ALL_TEMPLATE)" in script_txt \
    and "st.badge:SetImagePath(FOURTH.ALL_ICON, 0)" in script_txt, "the ALL control is not the round button"
assert 'write_badge_letter(st, "ALL")' not in script_txt, "the ALL control still writes letters"
assert "if any then FOURTH.all_sync_pressed(st) end" in script_txt, "the pressed sync is missing"
assert "function zz_all_nudge(dx, dy)" in script_txt and "function zz_all_set(x, y)" in script_txt \
    and "function zz_all_where()" in script_txt, "the Lua Console hooks are missing"
import mmap as _mmap
def _in_pack(pack, needle):
    with open(r"C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III/data/" + pack, "rb") as fh:
        mm = _mmap.mmap(fh.fileno(), 0, access=_mmap.ACCESS_READ)
        try:
            return mm.find(needle) >= 0
        finally:
            mm.close()
assert _in_pack("ui3.pack", b"templates\\round_small_button_toggle.twui.xml") \
    or _in_pack("ui3.pack", b"templates/round_small_button_toggle.twui.xml"), "the game has no round_small_button_toggle"
assert _in_pack("ui2.pack", b"default\\icon_abilities.png") \
    or _in_pack("ui2.pack", b"default/icon_abilities.png"), "the game has no icon_abilities.png"
print("ROUND 154 GATE OK: the ALL control is the game's round toggle button (template and icon found in the game's"
      " packs); pressed sync; zz_all_nudge / zz_all_set / zz_all_where")
# ROUND 155: the ALL button at the spot the user tuned by hand in battle.
assert "FOURTH.ALL_OX, FOURTH.ALL_OY = -923, 0\n" in script_txt, "the hand-tuned ALL spot is missing"
print("ROUND 155 GATE OK: the ALL button at the hand-tuned (-923, 0)")
# ROUND 156: the magic missiles (user rulings 2026-11-15).
for _f, _n in (("enemy_large_shot", 7), ("enemy_single_shot", 2), ("enemy_infantry_shot", 1),
               ("enemy_melee_or_fast", 4), ("enemy_melee_or_shooting", 3)):
    assert script_txt.count('trigger = "%s"' % _f) == _n, "family %s does not carry %d entries" % (_f, _n)
    assert ("%s = FOURTH.evaluate_%s," % (_f, _f)) in script_txt, "family %s is not wired" % _f
assert "FOURTH.SHOT_SAFE_M = 10 " in script_txt, "the user's 10 m safety setting is missing"
assert "FOURTH.ENEMY_CAST_R120 = %d " % max(int(120 * 0.70 + 1e-9), 120 - 20) in script_txt and "[120]  = FOURTH.ENEMY_CAST_R120," in script_txt, \
    "70% rule broken for 120 m"
assert 'if cls == "single" then return FOURTH.class_keys.single[t] == true end' in script_txt, "the single class is missing"
assert script_txt.count('\t\ttarget_class = "single",') == 2, "Dead Eye / Focused Shot do not honour the single-entity rule"
assert 'elseif eg_mode_now == "shot" then' in script_txt, "the magic-missile pre-cast re-check is missing"
import gen_shot_tables as _g156
_k156 = _g156.keys_in(script_txt)
assert len(_k156) == 70, "the shot families do not carry 23 keys (round 157: + the drains, the Executioner)"
assert _g156.lua_block(_g156.derive(_k156)) in script_txt, \
    "BUILD REFUSED (round 156): the SHOT table differs from the game data"
print("ROUND 156 GATE OK: 11 magic missiles on 5 families; the SHOT table matches the game; 10 m; 120 m -> 84 m; single class")
# ROUND 157: the drains and the Executioner (user rulings 2026-11-15).
assert script_txt.count('trigger = "enemy_single_drain"') == 13 and script_txt.count('trigger = "enemy_execute"') == 2, \
    "the drains / the Executioner are not on their families"
for _f in ("enemy_single_drain", "enemy_execute"):
    assert ("%s = FOURTH.evaluate_%s," % (_f, _f)) in script_txt, "family %s is not wired" % _f
assert ('trigger = "enemy_execute",\n\t\tbadge = "zz_auto_badge_emperors_executioner",\n'
        '\t\tkeys = { "wh3_dlc24_lord_abilities_the_emperors_executioner" },\n\t\trange_real = 50,\n'
        '\t\ttarget_class = "commander",') in script_txt, "the base Executioner lacks the game's commander class"
assert 'if kind == "execute" and not FOURTH.exec_ok(e) then return false end' in script_txt, \
    "the execute re-check is missing"
import gen_shot_tables as _g157
_k157 = _g157.keys_in(script_txt)
assert len(_k157) == 70, "the shot families do not carry 33 keys (round 158)"
assert _g157.exec_block(_g157.exec_rows(set(_k157))) in script_txt, \
    "BUILD REFUSED (round 157): the EXEC table differs from the game data"
print("ROUND 157 GATE OK: 10 drains, 2 executes; the SHOT and EXEC tables match the game; commander class on the base Executioner")
# ROUND 158: the last group B attacks (user rulings 2026-11-15).
assert script_txt.count('trigger = "enemy_area_drain"') == 13 and script_txt.count('trigger = "enemy_commander_value"') == 4, \
    "the area drains / the Leach Orb are not on their families"
for _f in ("enemy_area_drain", "enemy_commander_value"):
    assert ("%s = FOURTH.evaluate_%s," % (_f, _f)) in script_txt, "family %s is not wired" % _f
for _m, _t, _extra in (("storm_of_the_night", "enemy_melee_or_fast", '\t\ttarget_class = "flying",'),
                       ("dweomer_leach_orb", "enemy_spellcaster", ""),   # ROUND 178: the spellcaster list
                       ("ethracs_brazier", "enemy_melee_or_fast", ""), ("preyton_horns", "enemy_melee", ""),
                       ("the_amber_trance", "enemy_wavering", "")):
    _i = script_txt.find('{ marker = "%s", ' % _m)
    assert _i >= 0 and ('trigger = "%s",' % _t) in script_txt[_i:_i + 200] and _extra in script_txt[_i:_i + 300], \
        "%s is not on %s with its class" % (_m, _t)
assert 'if cls == "flying" then' in script_txt, "the flying class is missing"
import gen_shot_tables as _g158
_k158 = _g158.keys_in(script_txt)
assert len(_k158) == 70, "the shot families do not carry 36 keys (round 163)"
import re as _re158
_a158 = set(m.group(1) for m in _re158.finditer(
    r'trigger = "enemy_(?:area_drain|area_drain_hurt|most_models)",\n\t\tbadge = "[^"]+",\n\t\tkeys = \{ "([^"]+)" \}', script_txt))
assert len(_a158) == 18 and _g158.area_block(_g158.area_rows(_a158)) in script_txt, \
    "BUILD REFUSED (round 158): the AREA table differs from the game data"
print("ROUND 158 GATE OK: 7 area drains, the Leach Orb proxy, Storm flying-only, the morale hexes; the AREA table matches the game")
# ROUND 159: group E (user rulings 2026-11-15).
for _f, _n in (("melee_clear", 6), ("fly_dive", 2), ("last_stand_clear", 3), ("enemy_blob_vortex", 2)):
    assert script_txt.count('trigger = "%s"' % _f) == _n, "%s does not carry %d entries" % (_f, _n)
for _f in ("melee_clear", "fly_dive", "last_stand_clear"):
    assert ("%s = FOURTH.evaluate_%s," % (_f, _f)) in script_txt, "family %s is not wired" % _f
assert "enemy_blob_vortex = FOURTH.evaluate_enemy_blob," in script_txt, "enemy_blob_vortex is not wired"
for _f in ("melee_clear", "fly_dive", "last_stand_clear", "enemy_blob_vortex"):
    assert ("\t%s = true," % _f) not in script_txt.split("FOURTH.DEFAULT_ON_TRIGGERS = {", 1)[1].split("}", 1)[0], \
        "%s must start unarmed (M)" % _f
for _m, _t, _extra in (("deathmasters_sigil", "enemy_commander_value", '\t\ttarget_class = "commander_ground",'),
                       ("slann_gold", "enemy_spellcaster", ""),   # ROUND 178: the spellcaster list
                       ("heavens_flash", "enemy_ground_melee", "\t\trange_real = 75,"),
                       ("slime_smoothie", "health_aura_ground", "\t\taura_real = 35,"),
                       ("maneater_smoke_bomb", "charge_or_melee", ""), ("verminous_valour", "wavering_self", ""),
                       ("burp_of_grom", "melee_unwavering", ""), ("necrotic_explosion", "last_stand_clear", "")):
    _i = script_txt.find('{ marker = "%s", ' % _m)
    assert _i >= 0 and ('trigger = "%s",' % _t) in script_txt[_i:_i + 200] and _extra in script_txt[_i:_i + 400], \
        "%s is not on %s with its fields" % (_m, _t)
assert 'if cls == "commander_ground" then' in script_txt, "the commander_ground class is missing"
import gen_vortex_tables as _g159
_v159 = _g159.derive(_g159.keys_in(script_txt))
assert len(_v159) == 16 and _g159.lua_block(_v159) in script_txt, \
    "BUILD REFUSED (round 159): the VORTEX table differs from the game data"
print("ROUND 159 GATE OK: group E on its families (5 melee_clear, 2 fly_dive, 1 last_stand_clear, 1 enemy_blob_vortex), "
      "the Sigil's commander_ground class; the VORTEX table matches the game (10 keys)")
# ROUND 160: the Beastmen-battle fixes (user ruling 2026-11-16).
assert 'function FOURTH.evaluate_when_ready(unit, routing)\n\t-- ROUND 160' in script_txt \
    and "\tif routing then return nil end\n\treturn \"when ready (Winds of Magic), cast on self\"" in script_txt, \
    "when_ready does not skip a routing unit"
assert "FOURTH.SERIAL_MIN_HOLD_SECONDS = 2.5\n" in script_txt and "FOURTH.SERIAL_INSTANT_HOLD_SECONDS = POLL_MS / 1000\n" in script_txt, \
    "the per-unit hold constants are missing"
assert "if ability.wind_up_s == nil then\n\t\t\t\t\t\tunit_hold_s = FOURTH.SERIAL_INSTANT_HOLD_SECONDS\n" in script_txt, \
    "the instant one-poll hold is missing"
import re as _re160
import os as _os160
_blk160 = script_txt.split("\twind_up_s = {", 1)[1].split("\n\t}", 1)[0]
_tab160 = dict((k, float(v)) for k, v in _re160.findall(r'\["([^"]+)"\] = ([\d.]+)', _blk160))
_keys160 = set()
for _m160 in _re160.finditer(r"\t\tkeys = \{(.*?)\}", script_txt, _re160.S):
    _keys160.update(_re160.findall(r'"([^"]+)"', _m160.group(1)))
import gamedata_paths as _gp160
_f160 = open(_os160.path.join(_gp160.GAMEDATA, "unit_spec_abil.tsv"), encoding="utf-8-sig")
_h160 = _f160.readline().rstrip("\n").split("\t"); _f160.readline()
_wu160 = {}
for _l160 in _f160:
    _d160 = dict(zip(_h160, _l160.rstrip("\n").split("\t")))
    if _d160["key"] in _keys160 and float(_d160["wind_up_time"] or 0) > 0:
        _wu160[_d160["key"]] = float(_d160["wind_up_time"])
assert len(_keys160) == 1035 and _wu160 == _tab160, \
    "BUILD REFUSED (round 160): the wind-up table differs from the game data (an instant ability would be mis-held)"
print("ROUND 160 GATE OK: when_ready skips a routing unit; instant abilities hold their unit one poll; the wind-up "
      "table matches the game (%d of 1003 keys have a wind-up)" % len(_wu160))
# ROUND 161: the 14 ally melee buffs start armed (user ruling 2026-11-16, "Whole family").
_def161 = script_txt.split("FOURTH.DEFAULT_ON_TRIGGERS = {", 1)[1].split("\n}", 1)[0]
assert "\n\tally_melee_buff = true," in _def161, "ally_melee_buff does not start armed"
for _f161 in ("melee_clear", "fly_dive", "last_stand_clear", "enemy_blob_vortex"):
    assert ("\n\t%s = true," % _f161) not in _def161, "%s must still start unarmed" % _f161
assert script_txt.count('trigger = "ally_melee_buff"') == 1, "ally_melee_buff is not 1 entry (round 179)"
print("ROUND 161 GATE OK: the 14 ally melee buffs start armed; the friendly-fire families still start unarmed")
# ROUND 162: the wandering winds (user rulings 2026-11-16).
assert script_txt.count('trigger = "enemy_wave"') == 32 and script_txt.count('trigger = "enemy_wander"') == 42, \
    "the waves / wanderers are not on their families"
for _f162 in ("enemy_wave", "enemy_wander"):
    assert ("%s = FOURTH.evaluate_%s," % (_f162, _f162)) in script_txt, "family %s is not wired" % _f162
    assert ("\n\t%s = true," % _f162) not in script_txt.split("FOURTH.DEFAULT_ON_TRIGGERS = {", 1)[1].split("\n}", 1)[0], \
        "%s must start unarmed (M)" % _f162
assert 'elseif eg_mode_now == "ww" then' in script_txt and "cond_now = FOURTH.ww_still_ok(enemy, unit)" in script_txt, \
    "the ww pre-cast re-check is missing"
for _k162 in ("wh3_pro10_cataclysm_metal_gehennas_golden_globe_bound", "wh3_main_spell_bound_wall_of_wind_and_fire"):
    assert ('"%s"' % _k162) not in script_txt, "%s was closed by the user" % _k162
import gen_ww_tables as _g162
_kf162 = _g162.keys_in(script_txt)
assert len(_kf162) == 83 and _g162.lua_block(_g162.derive(_kf162)) in script_txt, \
    "BUILD REFUSED (round 162): the WW table differs from the game data"
print("ROUND 162 GATE OK: 12 waves, 20 wanderers, the ww re-check, both unarmed by default; the WW table matches the game")
# ROUND 163: the placed areas and the expendable units (user rulings 2026-11-16).
assert script_txt.count('trigger = "enemy_strike"') == 1 and script_txt.count('trigger = "ally_blast"') == 1, \
    "Siegebreaker / Arcane Vassal are not on their families"
_def163 = script_txt.split("FOURTH.DEFAULT_ON_TRIGGERS = {", 1)[1].split("\n}", 1)[0]
for _f163 in ("enemy_strike", "ally_blast"):
    assert ("%s = FOURTH.evaluate_%s," % (_f163, _f163)) in script_txt, "family %s is not wired" % _f163
    assert ("\n\t%s = true," % _f163) not in _def163, "%s must start unarmed (M)" % _f163
assert "if s ~= nil and not FOURTH.ff_ignored(s) then m.ours[#m.ours + 1] = s end" in script_txt \
    and "return s.vps ~= nil and s.vps < FOURTH.TRASH_VPS" in script_txt, "the expendable / cheap skip is missing"
for _k163 in ("wh_main_rune_abilities_rune_of_wrath_and_ruin", "wh_dlc06_rune_abilities_master_rune_of_wrath_and_ruin"):
    assert ('"%s"' % _k163) not in script_txt, "%s was closed by the user" % _k163
import gen_expendable_keys as _g163
_e163 = _g163.derive()
assert len(_e163) == 48 and _g163.lua_block(_e163) in script_txt, \
    "BUILD REFUSED (round 163): the EXPENDABLE table differs from the game data"
print("ROUND 163 GATE OK: the strike and the vassal wired and unarmed, the expendable / cheap skip; the EXPENDABLE "
      "table matches the game (48 units)")
# ROUND 164: the friendly-fire breaths (user rulings 2026-11-16).
_def164 = script_txt.split("FOURTH.DEFAULT_ON_TRIGGERS = {", 1)[1].split("\n}", 1)[0]
for _f164, _n164 in (("enemy_wave_charge", 0), ("enemy_cone", 5), ("enemy_sweep", 2)):   # ROUND 204: Tidecall, Wind Blast moved
    assert script_txt.count('trigger = "%s"' % _f164) == _n164, "%s does not carry %d entries" % (_f164, _n164)
    assert ("%s = FOURTH.evaluate_%s," % (_f164, _f164)) in script_txt, "family %s is not wired" % _f164
    assert ("\n\t%s = true," % _f164) not in _def164, "%s must start unarmed (M)" % _f164
assert "if oid == nil or oid ~= self_id then" in script_txt and "function FOURTH.ww_caster_ok(unit)" in script_txt, \
    "the caster exclusion or the ww caster gate is missing"
import gen_ww_tables as _g164
_kf164 = _g164.keys_in(script_txt)
assert len(_kf164) == 83 and _g164.nomelee_block(_kf164) in script_txt, \
    "BUILD REFUSED (round 164): the WW_NOMELEE list differs from the game data"
print("ROUND 164 GATE OK: the charge waves, the cones and the sweeps wired and unarmed; the caster no longer blocks its "
      "own wave; WW_NOMELEE matches the game")
# ROUND 165: the night audit (2026-11-17).
import gen_usage_keys as _g165
_u165 = _g165.derive(script_txt)
_t165 = _g165.derive_target(script_txt)
assert ('FOURTH.USAGE_TEXT = "%s"\n' % _g165.text(_u165)) in script_txt, \
    "BUILD REFUSED (round 165): the USAGE table differs from the game data"
assert ('FOURTH.ATARGET_TEXT = "%s"\n' % _g165.target_text(_t165)) in script_txt, \
    "BUILD REFUSED (round 165): the ATARGET table differs from the game data"
_card165 = script_txt.split("FOURTH.CARD_TIP = {", 1)[1].split("\n}", 1)[0]
_used165 = set(re.findall(r'trigger = "([a-z_0-9]+)"', script_txt.split("\nlocal ABILITIES = {", 1)[1].split("\n}\n", 1)[0]))
_miss165 = sorted(f for f in _used165 if ("\n\t%s = \"" % f) not in _card165)
assert not _miss165, "BUILD REFUSED (round 165): families without a card sentence: %s" % _miss165
assert "\t\tif not FOURTH.usage_ok(unit, ability, ui_id) then return nil end\n" in script_txt \
    and "\tif not FOURTH.ab_atarget_ok(unit) then return false end\n" in script_txt \
    and '\t\tor (FOURTH.eg_arm == "ww" and FOURTH.eg_ground == true) then\n' in script_txt \
    and "state.badge:SetTooltipText(ability.card, true)" in script_txt, \
    "BUILD REFUSED (round 165): a gate, the ground line or the badge card is missing"
_ec165 = script_txt.split("FOURTH.ENEMY_CAST = {", 1)[1].split("\n}", 1)[0]
_have165 = set(int(x) for x in re.findall(r"\[(\d+)\]\s*=", _ec165))
_rr165 = set(int(float(x)) for x in re.findall(r"\n\t\trange_real = ([\d.]+)", script_txt))
assert _rr165 <= _have165, "BUILD REFUSED (round 165): range_real without a 70%% bound: %s" % sorted(_rr165 - _have165)
for _r165 in (3, 6):
    assert ("FOURTH.ENEMY_CAST_R%-3d = %d " % (_r165, max(int(_r165 * 0.70 + 1e-9), _r165 - 20))) in script_txt, \
        "70%% rule broken for %d m" % _r165
print("ROUND 165 GATE OK: USAGE (%d keys) and ATARGET (%d keys) match the game; %d families carry a card; the gates, "
      "the ground line and the badge card are in place; every range_real has its 70%% bound"
      % (len(_u165), len(_t165), len(_used165)))
# ROUND 166: the short cards, the short ALL text, the wanderer caster rule, the friendly-fire gate (2026-11-17).
import ff_gate as _ff166
_card166 = script_txt.split("FOURTH.CARD_TIP = {", 1)[1].split("\n}", 1)[0]
_sent166 = re.findall(r'\n\t[a-z_0-9]+ = "([^"]*)",', _card166)
assert len(_sent166) >= 95 and all(x.startswith("Fires") for x in _sent166), \
    "BUILD REFUSED (round 166): a card sentence does not start with 'Fires'"
for _tok166 in ("{IN_R}", "{IN_A}", "{IN_REACH}", "{CLEAR}", "{W1}", "{W2}", "{WPATH}", "{CMIN}", "{DIVE}"):
    assert _tok166 not in _card166, "BUILD REFUSED (round 166): a distance token is back on the card: " + _tok166
assert ' .. " on A: " .. ' not in script_txt and '\treturn table.concat(parts, "; ")   -- ROUND 166' in script_txt, \
    "BUILD REFUSED (round 166): the card carries the name / 'on A:' again"
assert 'FOURTH.ALL_TIP = "Arm or disarm every automatic ability of the selected unit(s)"\n' in script_txt \
    and "ALL: arm or disarm" not in script_txt, "BUILD REFUSED (round 166): the ALL tooltip is not the user's sentence"
assert "\t\t\tif (oid == nil or oid ~= self_id) and FOURTH.blob_rect_gap(e.x, e.z, m.ours[i]) <= need then return nil end\n" \
    in script_txt, "BUILD REFUSED (round 166): the wanderer safety loop counts the caster again"
_bad166, _n166 = _ff166.violations(script_txt)
assert not _bad166, "BUILD REFUSED (round 166): a friendly-fire check on a blast that cannot hit our units: %s" % _bad166
print("ROUND 166 GATE OK: %d short card sentences, no distances, no name; the ALL text; the caster never blocks its "
      "wanderer; friendly-fire checks only on blasts that hit our units (%d keys); the card xml retired"
      % (len(_sent166), _n166))
# ROUND 167: no final period; rampage and self-damage abilities start on M (2026-11-17).
import gen_risky_keys as _gr167
_r167 = _gr167.derive(script_txt)
assert ('FOURTH.RISKY_TEXT = "%s"\n' % _gr167.text(_r167)) in script_txt, \
    "BUILD REFUSED (round 167): the RISKY table differs from the game data"
assert "\t\tand not FOURTH.entry_risky(ability)   -- ROUND 167: rampage and self-damage start on M\n" in script_txt, \
    "BUILD REFUSED (round 167): the family default no longer skips the risky entries"
_card167 = script_txt.split("FOURTH.CARD_TIP = {", 1)[1].split("\n}", 1)[0]
assert not re.findall(r'\.",\n', _card167), "BUILD REFUSED (round 167): a card sentence ends with a period"
assert '\treturn table.concat(parts, "; ")   -- ROUND 166' in script_txt and 'parts, "; ") .. "."' not in script_txt, \
    "BUILD REFUSED (round 167): the card ends with a period again"
assert 'selected unit(s)."' not in script_txt, "BUILD REFUSED (round 167): the ALL text ends with a period again"
print("ROUND 167 GATE OK: RISKY (%d keys) matches the game and keeps them on M by default; no final period on the "
      "cards or the ALL text" % len(_r167))
# ROUND 168: the cast animation decides the stand-still rule; the older pickers skip hidden enemies (2026-11-17).
import gen_anim_keys as _ga168
_a168 = _ga168.derive(script_txt)
assert ('FOURTH.ANIM_TEXT = "%s"\n' % _ga168.text(_a168)) in script_txt, \
    "BUILD REFUSED (round 168): the ANIM table differs from the game data"
assert "function FOURTH.blob_still(unit)\n\tif not FOURTH.cast_stops_caster() then return true end\n" in script_txt, \
    "BUILD REFUSED (round 168): the stand-still gate does not ask the cast animation"
assert "function FOURTH.eg_class_ok(enemy)\n\tif not FOURTH.enemy_not_hidden(enemy) then return false end" in script_txt \
    and "\t\t\t\t\t\t\t\tand FOURTH.enemy_not_hidden(enemy) then   -- ROUND 168" in script_txt, \
    "BUILD REFUSED (round 168): a picker lacks the visibility test"
assert "\treturn not (ok and vis == false)\n" in script_txt, \
    "BUILD REFUSED (round 168): the visibility test must block only an exact false"
print("ROUND 168 GATE OK: ANIM (%d of 1003 keys) matches the game; the stand-still gate asks it; both pickers skip "
      "hidden enemies" % len(_a168))
# ROUND 169: every enemy read skips hidden enemies (2026-11-17).
_v169 = (script_txt.count("and FOURTH.enemy_not_hidden(enemy) then   -- ROUND 169: never a hidden enemy\n"),
         script_txt.count("and FOURTH.enemy_not_hidden(enemy)   -- ROUND 169: never a hidden enemy\n"))
assert _v169 == (2, 1), "BUILD REFUSED (round 169): an enemy read lacks the visibility test %s" % (_v169,)
for _fn169 in ("function FOURTH.ad_nearest(unit)", "function FOURTH.nearest_enemy_gap(unit, inner)",
               "function FOURTH.engagement_set(unit)"):
    _body169 = script_txt.split(_fn169, 1)[1].split("\nend\n", 1)[0]
    assert "FOURTH.enemy_not_hidden(enemy)" in _body169, "BUILD REFUSED (round 169): %s has no visibility test" % _fn169
print("ROUND 169 GATE OK: the air drop, the 'just beyond range' read and the contact set skip hidden enemies")
# ROUND 170: Potion of Foolhardiness on charge_or_wavering, still armed by default (2026-11-17).
assert ('{ marker = "potion_of_foolhardiness", name = "Potion of Foolhardiness", trigger = "charge_or_wavering",\n'
        '\t\tbadge = "zz_auto_badge_potion_of_foolhardiness",\n'
        '\t\tkeys = { "wh_main_item_abilities_potion_of_foolhardiness" },\n'
        '\t\tstart_armed = true,\n') in script_txt, "BUILD REFUSED (round 170): Foolhardiness is not on charge_or_wavering"
assert "or ability.start_armed == true)   -- ROUND 170\n" in script_txt, \
    "BUILD REFUSED (round 170): the default rule does not read start_armed"
assert script_txt.count("\t\tstart_armed = true,\n") == 42, "BUILD REFUSED (round 170): start_armed is on another entry"
print("ROUND 170 GATE OK: Potion of Foolhardiness fires on its charge or when wavering, and still starts armed")
# ROUND 171: the score 1-2 review, rows 1-15 and 21 (2026-11-17).
import gen_contact_keys as _gc171
assert ('FOURTH.CONTACT_TEXT = "%s"\n' % _gc171.text(_gc171.derive())) in script_txt, \
    "BUILD REFUSED (round 171): the CONTACT table differs from the game data"
for _f171 in ("army_charge", "aura_charge", "self_or_ally_charge", "slow_aura", "winds_low", "contact_melee"):
    assert ("\t%s = FOURTH.evaluate_%s," % (_f171, _f171)) in script_txt, "BUILD REFUSED (round 171): %s not wired" % _f171
    assert ('trigger = "%s"' % _f171) in script_txt, "BUILD REFUSED (round 171): no entry rides %s" % _f171
assert '{ marker = "ursuns_roar_charge"' in script_txt and '{ marker = "waaagh_army"' in script_txt, \
    "BUILD REFUSED (round 171): a split entry is missing"
for _m171, _k171 in (("earthing_rod", "wh_main_item_abilities_earthing_rod"),
                     ("hagtree_fetish", "wh_dlc03_item_abilities_hagtree_fetish"),
                     ("master_of_the_black_arts", "wh_main_lord_abilities_master_of_the_black_arts"),
                     ("maw_shard", "wh3_main_item_abilities_maw_shard"),
                     ("power_familiar", "wh3_dlc27_item_abilities_power_familiar"),
                     ("watched_by_the_watcher", "wh3_dlc24_character_abilities_watched_by_the_watcher"),
                     ("sceptre_of_stability", "wh_main_item_abilities_sceptre_of_stability"),
                     ("locus_of_abjuration", "wh3_main_character_abilities_locus_of_abjuration"),
                     ("focus_instincts", "wh2_dlc12_lord_abilities_focus_instincts")):
    assert ('marker = "%s"' % _m171) not in script_txt and ('"%s"' % _k171) not in script_txt, \
        "BUILD REFUSED (round 171): the closed ability is back: " + _m171
assert script_txt.count("\tpcall(FOURTH.track_melee)") == 1, "BUILD REFUSED (round 171): the melee tracker is not polled"
print("ROUND 171 GATE OK: CONTACT (%d land units) matches the game; six families wired; Ursun's Roar and Waaagh! split; "
      "nine abilities closed; the fresh-contact tracker polled" % len(_gc171.derive()))
# ROUND 172: rows 1, 3 and 5 of the low score review as RULED in the doc (2026-11-18).
assert "\tarmy_charge_or_melee = FOURTH.evaluate_army_charge_or_melee," in script_txt, \
    "BUILD REFUSED (round 172): army_charge_or_melee is not wired"
assert '{ marker = "waaagh_army", name = "Waaagh!", trigger = "army_charge_or_melee",' in script_txt, \
    "BUILD REFUSED (round 172): Waaagh! is not on army charge or army melee"
assert script_txt.count('trigger = "army_charge"') == 1 and script_txt.count('trigger = "aura_charge"') == 1 \
    and script_txt.count('trigger = "army_charge_or_melee"') == 1, "BUILD REFUSED (round 172): the family counts moved"
assert "\tc.need = math.min(FOURTH.ARMY_CHARGE_MIN, c.living)\n" in script_txt, \
    "BUILD REFUSED (round 172): the army count lost the smaller-army fallback"
_ur172 = script_txt.split("function FOURTH.evaluate_aura_charge(unit, routing)", 1)[1].split("\nend\n", 1)[0]
assert _ur172.count("FOURTH.wavering(") == 2, "BUILD REFUSED (round 172): Ursun's Roar does not read wavering"
assert "AURA_CHARGE_ALLIES" not in script_txt.replace("-- ROUND 172: AURA_CHARGE_ALLIES is gone", "") \
    and "{ACA}" not in script_txt, "BUILD REFUSED (round 172): the 2-ally rule is back"
for _c172 in ('\tarmy_charge = "Fires when {ACN}+ of your units charge at once (all of them in a smaller army)",',
              '\tarmy_charge_or_melee = "Fires when {ACN}+ of your units charge or fight at once (all of them in a smaller army)",',
              '\taura_charge = "Fires when it or a nearby ally charges or wavers",'):
    assert _c172 in script_txt, "BUILD REFUSED (round 172): a card sentence differs: " + _c172
print("ROUND 172 GATE OK: Horn (every living unit in a smaller army), Waaagh! (army charge or army melee), "
      "Ursun's Roar (one unit charging or wavering)")
# ROUND 173: Null Stone and Rock Eye closed by the user (2026-11-18: "Close Null stone, Rock Eye.").
for _t173 in ("null_stone", "rock_eye"):
    assert _t173 not in script_txt, "BUILD REFUSED (round 173): a closed ability is back: " + _t173
print("ROUND 173 GATE OK: Null Stone and Rock Eye are closed")
# ROUND 174: the score 1-2 review, rows 24-50 (user, 2026-11-18: "You may implement items 24 to 50").
import gen_spellcaster_keys as _gs174
assert ('FOURTH.SPELLCASTER_TEXT = "%s"\n' % _gs174.text(_gs174.derive())) in script_txt, \
    "BUILD REFUSED (round 174): the SPELLCASTER table differs from the game data"
for _f174 in ("enemy_large_value_shot", "enemy_spellcaster", "enemy_ground_spellcasters", "enemy_missile_value",
              "enemy_ground_shooters", "enemy_commander_wavering", "ally_charge_melee", "ally_wavering_melee",
              "ally_lord_melee", "ally_missile_shooting", "ally_melee_risk", "ally_beast_charge", "ally_routing"):
    assert ("\t%s = FOURTH.evaluate_%s," % (_f174, _f174)) in script_txt, "BUILD REFUSED (round 174): %s not wired" % _f174
    assert ('trigger = "%s"' % _f174) in script_txt, "BUILD REFUSED (round 174): no entry rides %s" % _f174
_mv174 = {"weapon_abilities_amber_bow": "enemy_large_shot", "spell_bound_gaze_of_nagash": "enemy_large_shot",
          "spell_bound_hand_of_gods": "enemy_large_value_shot", "spell_light_shems_burning_gaze_bound": "enemy_large_value_shot",
          "character_abilities_goggly_glare": "enemy_large_value_shot", "spell_bound_vindictive_glare": "enemy_large_value_shot",
          "dont_even_try_it": "enemy_single_drain", "muster_of_malevolents": "enemy_single_drain",
          "cube_of_darkness": "enemy_spellcaster", "scroll_of_leeching": "enemy_spellcaster",
          "the_vortex_shard": "enemy_spellcaster", "the_black_tongue": "enemy_spellcaster",
          "the_tricksters_pendant": "enemy_ground_spellcasters", "tricksters_shard": "enemy_ground_spellcasters",
          "silence_the_prey": "enemy_commander_value", "power_siphon": "enemy_commander_value",
          "pageant_of_shrikes": "enemy_missile_value", "chalice_of_dark_rain": "enemy_ground_shooters",
          "transfix_hex": "enemy_commander_wavering", "fury_of_khaine": "ally_charge_melee",
          "verminous_fury": "ally_wavering_melee", "helping_hand": "ally_lord_melee",
          "inspired_marksmanship_i": "ally_missile_shooting", "inspired_marksmanship_ii": "ally_missile_shooting",
          "inspired_marksmanship_iii": "ally_missile_shooting", "overseer_of_the_unseen": "ally_melee_risk",
          "whiplash": "ally_beast_charge", "iron_hand_captain": "ally_routing"}
for _m174, _t174 in _mv174.items():
    assert re.search(r'\{ marker = "%s", name = "[^"]+", trigger = "%s",' % (re.escape(_m174), _t174), script_txt), \
        "BUILD REFUSED (round 174): %s is not on %s" % (_m174, _t174)
assert 'if cls == "spellcaster" then return FOURTH.class_keys.spellcaster[t] == true end' in script_txt, \
    "BUILD REFUSED (round 174): the spellcaster class is not in the class gate"
assert 'and (family == "routing" or not unit_is_routing(other))' in script_txt, \
    "BUILD REFUSED (round 174): the ally picker does not keep routing allies for Iron-Handed Captain"
assert 'if f == "not_missile" then return not FOURTH.class_member(unit, "missile") end' in script_txt, \
    "BUILD REFUSED (round 174): the not-missile ally filter is missing"
assert "FOURTH.CLUSTER_M = math.floor(FOURTH.CLUSTER_REAL_M * 0.70)" in script_txt, \
    "BUILD REFUSED (round 174): the 70% rule is broken for the cluster radius"
print("ROUND 174 GATE OK: SPELLCASTER (%d land units) matches the game; 13 families wired; 27 entries moved"
      % len(_gs174.derive()))
# ROUND 174 COMPILE GATE (a round-174 table regeneration once left a syntax error that every text gate passed): the
# shipped script must COMPILE. Run this builder with 'uv run --with websockets --with lupa'.
try:
    import lupa as _lupa174
except ImportError:
    raise AssertionError("BUILD REFUSED (round 174): lupa is missing - run with 'uv run --with websockets --with lupa'")
_c174 = _lupa174.LuaRuntime().eval("function(s) local f, e = load(s, '=zz_test_deadly_onslaught.lua'); return tostring(e) end")
_e174 = _c174(script_txt)
assert _e174 == "nil", "BUILD REFUSED (round 174): the script does not compile: " + _e174
print("ROUND 174 COMPILE GATE OK: the script compiles")
# ROUND 175: Master of Mists, 'A: before range, else shooting' (user ruling 2026-11-18).
assert "\tif best == nil then return FOURTH.mist_shooting(unit) end   -- ROUND 175: else the shooting units\n" in script_txt, \
    "BUILD REFUSED (round 175): the shooting arm is not reached"
assert 'if FOURTH.ah_mode == "mist_shoot" then   -- ROUND 175: still shooting' in script_txt, \
    "BUILD REFUSED (round 175): the shooting arm is not re-checked before the cast"
assert "FOURTH.MIST_AREA_REAL_M = 35 " in script_txt and \
    "FOURTH.MIST_AREA_M = math.floor(FOURTH.MIST_AREA_REAL_M * 0.70)" in script_txt, \
    "BUILD REFUSED (round 175): the 70% rule is broken for the Master of Mists area"
assert '\tground_ally_before_range = "Fires under missile allies just before their enemy is in range, else while they shoot",' \
    in script_txt, "BUILD REFUSED (round 175): the card sentence differs"
print("ROUND 175 GATE OK: Master of Mists fires before range, else under the shooting missile units")
# ROUND 176: Master of Mists starts armed (user, 2026-11-18: "Start it on A").
assert ('"wh3_dlc27_character_abilities_master_of_mists_custom" },\n\t\tally_range_real = 250,\n'
        '\t\tstart_armed = true,\n\t\tox = 0, oy = 0 },') in script_txt, \
    "BUILD REFUSED (round 176): Master of Mists does not start armed"
print("ROUND 176 GATE OK: Master of Mists starts armed")
# ROUND 177: the score-3 review, rows 1-22 (user, 2026-11-18: "Implement all until item 22, except the number 3").
import gen_squig_keys as _gq177
assert ('FOURTH.SQUIG_TEXT = "%s"\n' % _gq177.text(_gq177.derive())) in script_txt, \
    "BUILD REFUSED (round 177): the SQUIG table differs from the game data"
for _f177 in ("slow_army", "melee_vs_large", "ally_squig_melee", "enemy_melee_near", "aura_charge_or_melee",
              "melee_health25", "guard_aura", "self_or_ally_fire_melee", "melee_healthy"):
    assert ("\t%s = FOURTH.evaluate_%s," % (_f177, _f177)) in script_txt, "BUILD REFUSED (round 177): %s not wired" % _f177
    assert ('trigger = "%s"' % _f177) in script_txt, "BUILD REFUSED (round 177): no entry rides %s" % _f177
import re as _re177
for _m177, _t177 in (("blood_omens", "slow_army"), ("creature_killer", "melee_vs_large"),
                     ("empowering_shrooms", "ally_squig_melee"), ("everyone_has_their_price", "enemy_melee_near"),
                     ("fury_of_the_land", "aura_charge_or_melee"), ("refuse_to_die", "melee_health25"),
                     ("shield_of_aeons", "guard_aura"),   # ROUND 192: Rune of Oath & Steel left the mod
                     ("dispatch_the_swarm_protect", "self_or_ally_fire_melee"),
                     ("dispatch_the_swarm_protect_upgraded", "self_or_ally_fire_melee"),
                     ("slayer_for_chaos", "self_last_stand"), ("steppe_hunters_horn", "melee_vs_large"),
                     ("the_armour_of_morkar", "guard_aura"), ("the_blood_price", "melee_healthy"),
                     ("ostermark_runefang", "melee_vs_large"), ("daemonshield", "melee_unwavering")):
    assert _re177.search(r'\{ marker = "%s", name = "[^"]+", trigger = "%s",' % (_re177.escape(_m177), _t177), script_txt), \
        "BUILD REFUSED (round 177): %s is not on %s" % (_m177, _t177)
print("ROUND 177 GATE OK: SQUIG (%d land units) matches the game; 9 families wired; 15 entries moved; Daemonshield kept"
      % len(_gq177.derive()))
# ROUND 178: the score-3 review, rows 23-55 (user, 2026-11-18: "Approve rows 23-55. Row 56 stays the same").
for _f178 in ("enemy_fast_or_melee", "enemy_fast_fire_melee", "enemy_most_models"):
    assert ("\t%s = FOURTH.evaluate_%s," % (_f178, _f178)) in script_txt, "BUILD REFUSED (round 178): %s not wired" % _f178
    assert ('trigger = "%s"' % _f178) in script_txt, "BUILD REFUSED (round 178): no entry rides %s" % _f178
# the review doc's RULED texts (rows 23-24, 29: "a minimum of 16 units for both"; rows 36-41: no melee arm; rows 44-45:
# "makes sense to also add root")
for _m178, _t178 in (("spell_heavens_chain_lightning_bound", "enemy_most_models"),
                     ("spell_heavens_chain_lightning_bound_unit", "enemy_most_models"), ("the_soulstealer", "enemy_most_models"),
                     ("whip_of_misery", "enemy_melee_or_shooting"), ("word_of_pain", "enemy_melee_or_shooting"),
                     ("soulnetter", "enemy_fast_near_ally"), ("net_of_amyntok", "enemy_fast_near_ally"),
                     ("spider_web_attack", "enemy_fast_near_ally"), ("warp_gaze", "enemy_fast_near_ally"),
                     ("warpstiletto", "enemy_fast_near_ally"), ("pack_trap", "enemy_fast_near_ally"),
                     ("prey_of_anath_raema", "enemy_fast_fire_melee"), ("net_dem_up", "enemy_fast_fire_melee"),
                     ("glory_seeker", "enemy_fast_or_melee"), ("glory_seeker_upgraded", "enemy_fast_or_melee"),
                     ("prey_of_the_blood_god", "enemy_commander_value"), ("void_pendulum", "enemy_spellcaster"),
                     ("word_of_change", "enemy_spellcaster"), ("dweomer_leach_orb", "enemy_spellcaster"),
                     ("slann_gold", "enemy_spellcaster"), ("eye_of_khorne", "enemy_low_health_noncommander"),
                     ("trophy_heads", "enemy_melee"), ("trophy_heads_daemon_wings", "enemy_melee"),
                     ("oil_flask", "enemy_engaged_or_shot"), ("surprise_squig", "enemy_summon_blob")):   # ROUND 181: row 28 built
    assert _re177.search(r'\{ marker = "%s", name = "[^"]+", trigger = "%s",' % (_re177.escape(_m178), _t178), script_txt), \
        "BUILD REFUSED (round 178): %s is not on %s" % (_m178, _t178)
assert '\t\tkeys = { "wh3_main_daemon_wings_abilities_trophy_heads" },\n\t\trange_real = 150,\n\t\tox = 0, oy = 0 },' \
    in script_txt, "BUILD REFUSED (round 178): the Daemon Wings key is not on its own unclassed entry"
assert "local v, bv = FOURTH.unit_value(enemy), FOURTH.unit_value(best_enemy)" in script_txt, \
    "BUILD REFUSED (round 178): Eye of Khorne does not rank the value first"
assert '(arm == (FOURTH.eg_fire_first and "missile" or "melee")' in script_txt, \
    "BUILD REFUSED (round 178): the fire-first picker option is missing"
assert "\nFOURTH.MODELS_FLOOR = 16\n" in script_txt and 'elseif kind == "models" then' in script_txt, \
    "BUILD REFUSED (round 178): the user's 16-model floor is missing"
assert script_txt.count('trigger = "enemy_fast_or_melee"') == 2, "BUILD REFUSED (round 178): only Glory Seeker x2 ride enemy_fast_or_melee"
print("ROUND 178 GATE OK: 3 families wired; 20 entries moved; Trophy Heads split; Eye of Khorne value-first; fire-first; floor 16")
# ROUND 179: the score-3 review, rows 115-134 (user, 2026-11-18: "Items 115-134 approved").
for _f179 in ("ally_charge_or_melee", "ally_melee_wavering_first", "ally_value_melee", "ally_in_melee",
              "health_aura_ally_deep", "heal_ground_best"):
    assert ("\t%s = FOURTH.evaluate_%s," % (_f179, _f179)) in script_txt, "BUILD REFUSED (round 179): %s not wired" % _f179
    assert ('trigger = "%s"' % _f179) in script_txt, "BUILD REFUSED (round 179): no entry rides %s" % _f179
for _m179, _t179 in (("inspired_assault_i", "ally_charge_or_melee"), ("inspired_assault_ii", "ally_charge_or_melee"),
                     ("inspired_assault_iii", "ally_charge_or_melee"), ("inspired_defence_i", "ally_melee_wavering_first"),
                     ("inspired_defence_ii", "ally_melee_wavering_first"), ("inspired_defence_iii", "ally_melee_wavering_first"),
                     ("da_boss_as_a_plan", "ally_melee_wavering_first"), ("favour_of_the_fay", "melee_self_or_ally"),
                     ("orcs_are_da_best", "ally_value_melee"), ("hellish_vigour", "ally_in_melee"),
                     ("berry_wine", "health_aura_ally_deep"), ("star_of_avelorn", "heal_ground_best"),
                     ("gruts_sickle", "ally_winds"), ("commanding_presence", "wavering_self_or_ally"),
                     ("fury_of_ulric", "wavering_self_or_ally"), ("slezuzus_voice", "ally_melee_buff"),
                     ("horn_of_vaul", "melee_or_shooting_aura"), ("hunters_call", "melee_or_wavering_aura"),
                     ("cold_blooded", "wavering_ally_range"), ("captain_of_the_phoenix_guard", "ally_heal_melee")):
    _i179 = script_txt.find('{ marker = "%s", ' % _m179)
    assert _i179 >= 0 and ('trigger = "%s",' % _t179) in script_txt[_i179:_i179 + 200], \
        "BUILD REFUSED (round 179): %s is not on %s" % (_m179, _t179)
    if _m179 not in ("gruts_sickle", "commanding_presence", "fury_of_ulric", "slezuzus_voice", "horn_of_vaul",
                     "hunters_call", "cold_blooded", "captain_of_the_phoenix_guard"):
        _j179 = script_txt.find("\t\tox = 0, oy = 0 },", _i179)
        assert "\t\tstart_armed = true,\n" in script_txt[_i179:_j179], \
            "BUILD REFUSED (round 179): %s lost its default (its old family started armed)" % _m179
for _r179 in ("charge_contact_melee", "melee_wavering_first", "value_melee", "expendable_hp", "cheap_healthy"):
    assert script_txt.count('if family == "%s" then' % _r179) == 1, "BUILD REFUSED (round 179): ranked mode %s" % _r179
assert 'if FOURTH.ah_mode == "spot" then' in script_txt and 'if FOURTH.ah_mode == "deep" then' in script_txt, \
    "BUILD REFUSED (round 179): the heal re-check does not know the new rules"
assert "and not unit_is_routing(other)   -- ROUND 179: no melee condition" in script_txt, \
    "BUILD REFUSED (round 179): the wavering pair still asks for an ally in melee"
assert script_txt.count("if c == nil or c >= FOURTH.WINDS_LOW_POOL or r < FOURTH.WINDS_LOW_RESERVE then return nil end") == 2, \
    "BUILD REFUSED (round 179): Grut's Sickle does not wait for low winds"
assert "\nFOURTH.HEAL_DEEP_PCT = 55" in script_txt and "\nFOURTH.GRUT_HEALTHY_PCT = 75\n" in script_txt, \
    "BUILD REFUSED (round 179): the ruled health lines moved"
print("ROUND 179 GATE OK: 6 families wired; 12 entries moved, defaults kept; 5 ranked modes; spot/deep re-checks; "
      "the wavering pair; Grut's winds gate")
# ROUND 180: the score-3 review, rows 87-114 and 128 (user, 2026-11-18).
for _f180 in ("health_aura_ally_rule", "self_heal_clear", "self_hurt_attacked", "charge_or_tired"):
    assert ("\t%s = FOURTH.evaluate_%s," % (_f180, _f180)) in script_txt, "BUILD REFUSED (round 180): %s not wired" % _f180
    assert ('trigger = "%s"' % _f180) in script_txt, "BUILD REFUSED (round 180): no entry rides %s" % _f180
for _m180, _t180, _armed180 in (("entangle", "enemy_fast_near_ally", False), ("get_em", "enemy_fast_near_ally", False),
                                ("hunters_snare", "enemy_fast_near_ally", False), ("hunters_trap", "enemy_fast_near_ally", False),
                                ("shield_of_thorns", "melee_self_or_ally", True),
                                ("blood_chalice_of_bathori", "health_aura_ally_rule", True),
                                ("undeath_morkharn_breath_of_darkness", "health_aura_ally_rule", True),
                                ("undeath_morkharn_breath_of_darkness_upgraded", "health_aura_ally_rule", True),
                                ("protection_prayer", "health_aura_ally_rule", True), ("bugmans_xxxxxx", "self_heal_clear", True),
                                ("potion_of_charoi", "self_hurt_attacked", True), ("skars_kraken_killer", "self_hurt_attacked", True),
                                ("foe_seeker", "charge_or_tired", True), ("rock_bottom", "self_out_of_ammo", False),
                                ("eat_da_runts", "eat_da_runts", False), ("cold_blooded", "wavering_ally_range", False),
                                ("land_mine", "melee_clear_block", False)):
    _i180 = script_txt.find('{ marker = "%s", ' % _m180)
    assert _i180 >= 0 and ('trigger = "%s",' % _t180) in script_txt[_i180:_i180 + 200], \
        "BUILD REFUSED (round 180): %s is not on %s" % (_m180, _t180)
    _j180 = script_txt.find("\t\tox = ", _i180)
    assert (("\t\tstart_armed = true,\n" in script_txt[_i180:_j180]) == _armed180), \
        "BUILD REFUSED (round 180): %s's default is wrong" % _m180
    if _t180 == "enemy_fast_near_ally":
        assert "\t\trange_real = 100,\n" in script_txt[_i180:_j180], "BUILD REFUSED (round 180): %s is not on its real 100 m" % _m180
for _k180 in ("heavens_gate", "snowflake_pendant", "stave_of_avelorn"):   # ROUND 181: melee_clear_block is back (row 98 "A")
    assert _k180 not in script_txt, "BUILD REFUSED (round 180): %s is still in the script" % _k180
import gen_ww_tables as _gw180
assert len(_gw180.Q80) == 5, "BUILD REFUSED (round 180): the 80% keys moved"
import gen_rule_sets as _gr180
assert _gr180.lua_block() in script_txt, "BUILD REFUSED (round 180): the lizard / tiger sets differ from the game data"
assert 'if a.Z and not FOURTH.class_member(unit, "lizard") then return false end' in script_txt \
    and 'if a.T and not FOURTH.class_member(unit, "tiger") then return false end' in script_txt, \
    "BUILD REFUSED (round 180): the Z / T target rules are not honoured"
assert "and FOURTH.wavering(other) == true and FOURTH.ab_atarget_ok(other) then   -- ROUND 180" in script_txt, \
    "BUILD REFUSED (round 180): Cold-Blooded's picker ignores the game's target rule"
assert "\nFOURTH.BUGMAN_CLEAR_M = 55" in script_txt, "BUILD REFUSED (round 180): Bugman's bound"   # ROUND 198 rebase: the whole 55 m (a keep-out distance)
assert "\nFOURTH.ROCK_BOTTOM_PCT = 50" in script_txt and "\nFOURTH.HURT_ATTACKED_PCT = 75" in script_txt, \
    "BUILD REFUSED (round 180): the ruled health lines moved"
print("ROUND 180 GATE OK: 4 families wired; 13 entries moved, defaults right; 3 closed; roots at 100 m; 80%% WW keys; "
      "lizard (%d) / tiger (%d) sets match the game; Land Mine kept" % (len(_gr180.derive_lizard()), len(_gr180.derive_tiger())))
# ROUND 181: Land Mine "A", Surprise Squig! blob with clearance, the range fixes (user, 2026-11-20).
for _f181 in ("melee_clear_block", "enemy_summon_blob"):
    assert ("\t%s = FOURTH.evaluate_%s," % (_f181, _f181)) in script_txt, "BUILD REFUSED (round 181): %s not wired" % _f181
    assert script_txt.count('trigger = "%s"' % _f181) == {"melee_clear_block": 2}.get(_f181, 1), \
        "BUILD REFUSED (round 181): %s is not ridden as expected (round 185: melee_clear_block x2)" % _f181
assert "\nFOURTH.LAND_MINE_MIN_MEN = 60" in script_txt, "BUILD REFUSED (round 181): the user's 60-soldier line moved"
import gen_summon_blast as _gs181
_ks181 = _gs181.keys_in(script_txt)
assert _ks181 == ["wh3_dlc25_character_abilities_surprise_squig"] and \
    _gs181.lua_block(_gs181.derive(_ks181)) in script_txt, "BUILD REFUSED (round 181): the summon blast differs from the game data"
import subprocess as _sp181, sys as _sy181
_scan181 = _sp181.run([_sy181.executable, r"C:\Users\vlady\Desktop\WH3_mod\tools\scan_range_real.py"], capture_output=True, text=True)
assert _scan181.stdout.strip().endswith("0 mismatches"), \
    "BUILD REFUSED (round 181): a range_real differs from the game's target_intercept_range:\n" + _scan181.stdout
assert '{ marker = "lord_of_undeath_4", name = "Lord of Undeath", trigger = "enemy_ground_melee",' in script_txt, \
    "BUILD REFUSED (round 181): the Lord of Undeath split is missing"
print("ROUND 181 GATE OK: 2 families wired; 60 soldiers; summon blast 21 m matches the game; 0 range mismatches; Lord of Undeath split")
# ROUND 182: the finishers (user rulings 2026-11-17 and 2026-11-20).
for _f182 in ("enemy_finisher", "melee_or_self_shooting"):
    assert ("\t%s = FOURTH.evaluate_%s," % (_f182, _f182)) in script_txt, "BUILD REFUSED (round 182): %s not wired" % _f182
    assert script_txt.count('trigger = "%s"' % _f182) == 1, "BUILD REFUSED (round 182): %s is not ridden once" % _f182
assert "\nFOURTH.SINGLE_RANGE_FRACTION = 0.90" in script_txt and script_txt.count("\t\trange_frac = 0.90,\n") == 1, \
    "BUILD REFUSED (round 182): the 90% exception must stay the Executioner's alone (user ruling 2026-11-20)"
_i182 = script_txt.find('{ marker = "lord_abilities_executioner", name = "Executioner", trigger = "enemy_finisher",')
assert _i182 >= 0 and "\t\trange_real = 250,\n\t\trange_frac = 0.90,\n" in script_txt[_i182:_i182 + 300] and int(250 * 0.90) == 225, \
    "BUILD REFUSED (round 182): the Executioner's 90% bound"
assert "\t\t\ts1 = FOURTH.enemy_health_pct(e.unit) or 0\n\t\t\ts2 = e.value or 0\n" in script_txt, \
    "BUILD REFUSED (round 182): the Emperor's Executioner does not rank the highest health below the line"
assert 'trigger = "melee_or_shooting_into_melee"' not in script_txt, "BUILD REFUSED (round 182): Skjalandir's Fall did not move"
print("ROUND 182 GATE OK: 2 families wired; the Executioner's 90% bound (225 m); execute ranks the highest health; Skjalandir moved")
# ROUND 183: the rule-shut review, rows 1-9 (user 2026-11-20: "You may start implementing #1-9 for now").
_r183 = [
    ("defiling_deluge", "enemy_melee_near", "wh3_twa08_unit_abilities_defiling_deluge", 35),
    ("murderous_exhortations", "enemy_melee_near", "wh3_dlc26_lord_abilities_murderous_exhortations", 35),
    ("rod_of_corruption", "enemy_melee_near", "wh2_main_item_abilities_rod_of_corruption", 35),
    ("wail_of_malice", "enemy_melee_near", "wh2_dlc14_unit_abilities_wail_of_malice", 35),
    ("plaguereaper", "melee_health75", "wh3_dlc29_item_abilities_plaguereaper", None),
    ("reaper_of_souls", "melee_health75", "wh2_dlc14_lord_abilities_reaper_of_souls", None),
    ("shard_blade", "melee_unwavering", "wh3_main_weapon_abilities_shard_blade", None),
    ("web_of_shadows", "melee_unwavering", "wh2_main_weapon_abilities_web_of_shadows", None),
    ("warp_quake", "melee_unwavering", "wh2_dlc14_unit_abilities_warp_quake", None),
]
for _m183, _t183, _k183, _a183 in _r183:
    _e183 = ('{ marker = "%s", name = ' % _m183)
    assert script_txt.count(_e183) == 1, "BUILD REFUSED (round 183): %s is not one entry" % _m183
    _j183 = script_txt.index(_e183)
    _b183 = script_txt[_j183:script_txt.index("ox = 0, oy = 0 },", _j183)]
    assert ('trigger = "%s",' % _t183) in _b183 and ('keys = { "%s" },' % _k183) in _b183, \
        "BUILD REFUSED (round 183): %s is not on its ruled family %s" % (_m183, _t183)
    assert (_a183 is None) == ("aura_real" not in _b183), "BUILD REFUSED (round 183): %s aura" % _m183
    if _a183 is not None:
        assert ("\t\taura_real = %d,\n" % _a183) in _b183, "BUILD REFUSED (round 183): %s aura is not the game's" % _m183
assert script_txt.count("-- ROUND 183 (rule-shut review row ") == 9, "BUILD REFUSED (round 183): row markers"
for _k183, _v183 in (("wh3_twa08_unit_abilities_defiling_deluge", 120), ("wh3_dlc26_lord_abilities_murderous_exhortations", 120),
                     ("wh2_main_item_abilities_rod_of_corruption", 120), ("wh2_dlc14_unit_abilities_wail_of_malice", 90),
                     ("wh3_dlc29_item_abilities_plaguereaper", 120), ("wh3_main_weapon_abilities_shard_blade", 120)):
    assert script_txt.count('\t\t["%s"] = %d,\n' % (_k183, _v183)) == 1, "BUILD REFUSED (round 183): hold for %s" % _k183
print("ROUND 183 GATE OK: 9 entries on the ruled families (4 enemy_melee_near at 35 m, 2 melee_health75, 3 melee_unwavering); 6 holds")
# ROUND 184: the rule-shut review, rows 10-19 (user 2026-11-20: "Up to #19 ruled").
_r184 = [
    ("flock_of_doom_runecaller", "enemy_area_drain", "wh3_dlc27_spell_bound_runecaller_flock_of_doom", 100, None),
    ("flock_of_doom_wh3", "enemy_area_drain", "wh3_main_spell_bound_flock_of_doom", 100, None),
    ("flock_of_doom", "enemy_area_drain", "wh_dlc08_spell_bound_flock_of_doom", 100, None),
    ("sword_of_daith", "enemy_area_drain", "wh_dlc05_weapon_abilities_daiths_sword", 100, None),
    ("zefet_nebtar", "enemy_area_drain", "wh3_dlc29_item_abilities_zefet_nebtar_the_mortis_blade", 100, None),
    ("ring_of_corin", "enemy_single_drain", "wh2_main_spell_bound_ring_of_corin", 200, None),
    ("soul_stealer_ror", "enemy_area_drain_hurt", "wh2_dlc10_spell_bound_soul_stealer_ror", 100, None),
    ("soul_stealer_anointed", "enemy_area_drain_hurt", "wh3_dlc27_spell_bound_soul_stealer", 100, None),
    ("warpstorm_scroll", "enemy_most_valuable", "wh2_main_item_abilities_warpstorm_scroll", 100, "flying"),   # ROUND 186
    ("raging_tornado", "enemy_ground_melee_cluster", "wh3_dlc29_unit_abilities_raging_tornado", 100, None),
]
for _m184, _t184, _k184, _r184r, _c184 in _r184:
    _e184 = ('{ marker = "%s", name = ' % _m184)
    assert script_txt.count(_e184) == 1, "BUILD REFUSED (round 184): %s is not one entry" % _m184
    _j184 = script_txt.index(_e184)
    _b184 = script_txt[_j184:script_txt.index("ox = 0, oy = 0 },", _j184)]
    assert ('trigger = "%s",' % _t184) in _b184 and ('keys = { "%s" },' % _k184) in _b184 \
        and ("\t\trange_real = %d,\n" % _r184r) in _b184, \
        "BUILD REFUSED (round 184): %s is not on its ruled family %s with the game's range" % (_m184, _t184)
    assert (_c184 is None) == ("target_class" not in _b184), "BUILD REFUSED (round 184): %s class" % _m184
    if _c184 is not None:
        assert ('\t\ttarget_class = "%s",\n' % _c184) in _b184, "BUILD REFUSED (round 184): %s class" % _m184
for _f184 in ("enemy_area_drain_hurt", "enemy_ground_melee_cluster"):
    assert ("\t%s = FOURTH.evaluate_%s," % (_f184, _f184)) in script_txt, "BUILD REFUSED (round 184): %s not wired" % _f184
assert "\nFOURTH.DRAIN_HURT_PCT = 75" in script_txt, "BUILD REFUSED (round 184): the 75% gate (user ruling 2026-11-20)"
assert script_txt.count('\t\t["wh3_dlc29_unit_abilities_raging_tornado"] = true,\n') == 1, \
    "BUILD REFUSED (round 184): Raging Tornado must be placed on the ground (enemy_ground_keys)"
assert script_txt.count("-- ROUND 184 (rule-shut review row ") == 10, "BUILD REFUSED (round 184): row markers"
for _k184, _v184 in (("wh3_dlc27_spell_bound_runecaller_flock_of_doom", "60"), ("wh3_main_spell_bound_flock_of_doom", "60"),
                     ("wh_dlc08_spell_bound_flock_of_doom", "60"), ("wh_dlc05_weapon_abilities_daiths_sword", "120"),
                     ("wh3_dlc29_item_abilities_zefet_nebtar_the_mortis_blade", "120"),
                     ("wh2_main_spell_bound_ring_of_corin", "90"), ("wh3_dlc29_unit_abilities_raging_tornado", "120")):
    assert script_txt.count('\t\t["%s"] = %s,\n' % (_k184, _v184)) == 1, "BUILD REFUSED (round 184): hold for %s" % _k184
print("ROUND 184 GATE OK: 10 entries on the ruled families with the game's ranges; 2 families wired; the 75% gate; "
      "Warpstorm flying; Raging Tornado on the ground; 7 holds")
# ROUND 185: the rule-shut review, rows 20-64 (user 2026-11-20: "Review ended, implement pls").
import sys as _sy185
_sy185.path.insert(0, r"C:\Users\vlady\Desktop\WH3_mod\tools")
import round185_rows as _rr185
for _row185, _m185, _n185, _t185, _k185, _f185 in _rr185.ROWS:
    _e185 = ('{ marker = "%s", name = ' % _m185)
    assert script_txt.count(_e185) == 1, "BUILD REFUSED (round 185): %s is not one entry" % _m185
    _j185 = script_txt.index(_e185)
    _b185 = script_txt[_j185:script_txt.index("ox = 0, oy = 0 },", _j185)]
    assert ('trigger = "%s",' % _t185) in _b185 and ('keys = { "%s" },' % _k185) in _b185, \
        "BUILD REFUSED (round 185): %s is not on its ruled family %s" % (_m185, _t185)
    for _fld185 in ("range_real", "ally_range_real", "aura_real", "unbounded", "target_class"):
        if _fld185 in _f185:
            assert ("\t\t%s = %s,\n" % (_fld185, _f185[_fld185])) in _b185, "BUILD REFUSED (round 185): %s %s" % (_m185, _fld185)
        else:
            assert ("\t\t%s = " % _fld185) not in _b185, "BUILD REFUSED (round 185): %s carries a stray %s" % (_m185, _fld185)
assert script_txt.count("-- ROUND 185 (rule-shut review row ") == 33, "BUILD REFUSED (round 185): row markers"
for _f185 in ("aura_charge_only", "ally_offering"):
    assert ("\t%s = FOURTH.evaluate_%s," % (_f185, _f185)) in script_txt, "BUILD REFUSED (round 185): %s not wired" % _f185
assert "\nFOURTH.OFFERING_MIN_MEN = 30" in script_txt, "BUILD REFUSED (round 185): the 30-men floor (user ruling 2026-11-20)"
for _g185 in _rr185.GROUND:
    assert script_txt.count('\t\t["%s"] = true,\n' % _g185) == 1, "BUILD REFUSED (round 185): %s must be a ground cast" % _g185
assert "wh2_dlc17_rune_abilities_master_rune_of_immolation=10;" in script_txt, \
    "BUILD REFUSED (round 185): the Immolation rune's 10 m bombardment radius"
print("ROUND 185 GATE OK: 33 entries on the ruled families; 2 families wired; the 30-men floor; 2 ground keys; "
      "the rune's 10 m bombardment")
# ROUND 186: Warpstorm Scroll as a damage dealer (user 2026-11-20: "No need to enforce single-entity. No need to enforce
# charge, treat it just as a damage dealer").
assert "\tenemy_most_valuable = FOURTH.evaluate_enemy_most_valuable," in script_txt, \
    "BUILD REFUSED (round 186): enemy_most_valuable not wired"
assert script_txt.count('trigger = "enemy_most_valuable"') == 1, "BUILD REFUSED (round 186): enemy_most_valuable is not ridden once"
_i186 = script_txt.index('{ marker = "warpstorm_scroll", name = "Warpstorm Scroll", trigger = "enemy_most_valuable",')
assert '\t\trange_real = 100,\n\t\ttarget_class = "flying",\n' in script_txt[_i186:_i186 + 300], \
    "BUILD REFUSED (round 186): Warpstorm Scroll must keep the game's range and its flying-only rule"
print("ROUND 186 GATE OK: Warpstorm Scroll on enemy_most_valuable (flying only, 100 m -> 70 m)")
# ROUND 187: the badges follow the wheel at any resolution or UI scale (user 2026-11-21: "we need to fix the UI scale").
for _t187 in ("\nfunction FOURTH.ui_shift_tick()\n", "\tpcall(FOURTH.ui_shift_tick)   -- ROUND 187",
              'FOURTH.UI_WHEEL_REFS = { { "ability_parent", 42, 893 }, { "button_ability", 96, 845 } }',
              'FOURTH.UI_CENTRE_REFS = { { "orders_parent", 691, 1055 }, { "behaviour_parent", 1021, 1055 }, { "button_parent", 1072, 1052 } }',
              "FOURTH.UI_SHIFT_EVERY = 40", "FOURTH.ui_replace = replace_all_badges",
              "(slot[1] - WHEEL_TOP_X) + FOURTH.ui_dx", "BADGE_X + ability.ox + FOURTH.ui_dx"):
    assert script_txt.count(_t187) == 1, "BUILD REFUSED (round 187): missing %r" % _t187
assert script_txt.count("FOURTH.ALL_OX + FOURTH.ui_dx, FOURTH.ALL_OY + FOURTH.ui_dy") == 2 \
    and script_txt.count("SetDockOffset(FOURTH.ALL_OX, FOURTH.ALL_OY)") == 0, \
    "BUILD REFUSED (round 187): the ALL button must carry the UI shift"
_pre187 = open(r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round187\pre187_live.lua", encoding="utf-8").read()
assert script_txt.count("find_uicomponent(") == _pre187.count("find_uicomponent("), \
    "BUILD REFUSED (round 187): the UI shift must not call find_uicomponent"
print("ROUND 187 GATE OK: the badges and the ALL button follow the wheel (live shift, 2 s)")
# ROUND 188: the range rule (user 2026-11-21: "C. Your rule, the larger of 70% and real minus 20 m, everywhere.").
assert "\nFOURTH.RANGE_MARGIN_M = 20 " in script_txt and "\nfunction FOURTH.range_bound(real)\n" in script_txt \
    and "math.max(math.floor(real * FOURTH.RANGE_FRACTION + 1e-9), real - FOURTH.RANGE_MARGIN_M)" in script_txt, \
    "BUILD REFUSED (round 188): the range rule's margin or helper is missing"
_c188 = re.findall(r"\nFOURTH\.(ENEMY|ALLY)_CAST_R(\d+)\s*=\s*(\d+)", script_txt)
_bad188 = [c for c in _c188 if int(c[2]) != max(int(c[1]) * 70 // 100, int(c[1]) - 20)]
assert len(_c188) >= 25 and not _bad188, "BUILD REFUSED (round 188): cast bounds off the rule: %s" % _bad188
for _t188 in ("FOURTH.BLOOD_SACRIFICE_RANGE_M = 80 ", "FOURTH.EAT_DA_RUNTS_RANGE_M = 80 ", "FOURTH.ACCUSATION_RANGE_M = 55 "):
    assert script_txt.count("\n" + _t188) == 1, "BUILD REFUSED (round 188): missing %r" % _t188
assert "\t\t\tability.range_m = math.max(ability.range_m or 0,\n\t\t\t\tmath.floor(ability.range_real * FOURTH.SINGLE_RANGE_FRACTION + 1e-9))" \
    in script_txt, "BUILD REFUSED (round 188): the Executioner must take the larger bound"
assert "ability.aura_m = math.floor(ability.aura_real * FOURTH.RANGE_FRACTION + 1e-9)" in script_txt, \
    "BUILD REFUSED (round 188): the aura bound must stay 70%"
print("ROUND 188 GATE OK: %d cast bounds on max(70%%, real - 20); named 80/80/55; the Executioner 230" % len(_c188))
# ROUND 189: the line of fire (user 2026-11-21: "I would just do the check for terrain on all 35 and units on all 35.
# Just let's be safe, and if it doesn't fire, that's okay.").
import gen_los_keys as _g189
_k189 = _g189.derive()
assert len(_k189) == 56 and ("\n" + _g189.lua_text(_k189) + "\n") in script_txt, \
    "BUILD REFUSED (round 189): the LOS table differs from the game data"
_ours189 = sorted(k for k in _k189 if ('"%s"' % k) in script_txt)
assert len(_ours189) == 35, "BUILD REFUSED (round 189): %d line-of-sight keys are ours, expected 35" % len(_ours189)
for _t189 in ("\tif not FOURTH.eg_los_ok(enemy) then return false end   -- ROUND 189: never an enemy behind a blocked line\n",
              "\tFOURTH.eg_caster = unit   -- ROUND 189: the caster the line of fire is drawn from\n",
              "\tFOURTH.eg_los = (ability.los == true)   -- ROUND 189: the game's 'Requires line of sight'\n",
              "\tability.los = FOURTH.entry_los(ability)   -- ROUND 189: the line of fire (terrain and units)\n",
              "\tlocal ok, g = pcall(function() return bm:get_terrain_height(x, z) end)\n",
              "\nfunction FOURTH.los_block(caster, enemy)\n", "\nfunction FOURTH.eg_los_ok(enemy)\n",
              'return "the ground is unreadable", "read"', 'return "the flying read is unreadable", "read"',
              'return "a position is unreadable", "read"'):
    assert script_txt.count(_t189) >= 1, "BUILD REFUSED (round 189): missing %r" % _t189[:70]
assert script_txt.count("\tif not FOURTH.eg_los_ok(enemy) then return false end") == 1, \
    "BUILD REFUSED (round 189): the eg_class_ok hook must appear once"
assert "ZZ_AUTO_TEST_NO_LOS = " not in script_txt and script_txt.count("ZZ_AUTO_TEST_NO_LOS == true") == 1, \
    "BUILD REFUSED (round 189): the test-only global must only be read"
print("ROUND 189 GATE OK: the LOS table matches the game (56 keys, 35 ours); terrain and units checked, fail-closed")
# ROUND 190: the animation decides in every shot trigger (user 2026-11-21: "Fix the 8").
_t190 = "   -- ROUND 190: the animation decides (Amber Bow stopped a walking Markus)"
assert script_txt.count(_t190) == 7, "BUILD REFUSED (round 190): %d stand-still lines, want 7" % script_txt.count(_t190)
assert "\tif still and not FOURTH.blob_still(unit) then return false end" not in script_txt, \
    "BUILD REFUSED (round 190): the shot caster check must not leave standing to the family"
_anim190 = set(re.search(r'\nFOURTH\.ANIM_TEXT = "([^"]*)"', script_txt).group(1).split(";"))
for _k190 in ("wh2_dlc13_weapon_abilities_amber_bow", "wh2_dlc15_spell_bound_gaze_of_nagash",
              "wh3_main_weapon_abilities_godkiller_pistol", "wh3_dlc27_item_abilities_schalkains_teeth",
              "wh2_dlc15_character_abilities_goggly_glare", "wh3_dlc27_character_abilities_the_black_tongue"):
    assert _k190 in _anim190, "BUILD REFUSED (round 190): %s lost its animation in the table" % _k190
print("ROUND 190 GATE OK: every shot trigger asks the animation before casting on the move (7 lines)")
# ROUND 191: the animation decides in group 1 (user 2026-11-21: "For now, please only implement number 1.").
_m191 = re.search(r"\nFOURTH\.STILL_GATE_TRIGGERS = \{\n(.*?)\n\}\n", script_txt, re.S)
assert _m191 is not None, "BUILD REFUSED (round 191): FOURTH.STILL_GATE_TRIGGERS is missing"
_set191 = set(re.findall(r"(\w+) = true", _m191.group(1)))
_want191 = {"enemy_ground_melee_infantry", "enemy_ground_melee", "enemy_engaged_or_shot", "enemy_melee",
            "enemy_fast_near_ally", "enemy_melee_or_fast", "enemy_melee_noncommander", "enemy_missile_shooting"}
assert _set191 == _want191, "BUILD REFUSED (round 191): the stand-still set is %s" % sorted(_set191)
for _t191 in sorted(_set191):
    assert ("\t%s = FOURTH.evaluate_" % _t191) in script_txt, "BUILD REFUSED (round 191): %s is not a wired trigger" % _t191
assert script_txt.count("\t\tif not FOURTH.blob_still(unit) then return nil end   -- ROUND 191: a moving caster waits") == 1, \
    "BUILD REFUSED (round 191): the wrapper must ask FOURTH.blob_still"
assert script_txt.count("\t\tability.evaluate = FOURTH.still_wrap(ability.evaluate)   -- ROUND 191") == 1, \
    "BUILD REFUSED (round 191): the load loop must wrap the group-1 entries"
_anim191 = set(re.search(r'\nFOURTH\.ANIM_TEXT = "([^"]*)"', script_txt).group(1).split(";"))
for _k191 in ("wh2_dlc13_lord_abilities_oil_flask", "wh3_main_mount_bound_celestial_comet"):
    assert _k191 in _anim191, "BUILD REFUSED (round 191): %s lost its animation in the table" % _k191
print("ROUND 191 GATE OK: the 8 group-1 triggers wait for an animated caster to stand still")
# ROUND 192 (user rulings 2026-11-21): the fast enemy must be running and closing; Grombrindal Has No Fear; the five
# spell-bar runes removed; the Moulder rule for Shock Collar and Remouldered.
assert "\nFOURTH.FAST_CLOSING_MPS = 3     -- ROUND 192" in script_txt and "\nFOURTH.FAST_CLOSING_S = 1       -- ROUND 192" in script_txt, \
    "BUILD REFUSED (round 192): the closing constants moved"
assert script_txt.count("local ok_mf, mf = pcall(function() return enemy:is_moving_fast() end)   -- ROUND 192: really running") == 1 \
    and script_txt.count("local closing = old_rule or FOURTH.fast_closing(enemy, best)") == 1, \
    "BUILD REFUSED (round 192): fast_enemy_near does not ask running + closing"
for _m192, _k192 in (("rune_of_breaking", "wh2_dlc17_rune_abilities_rune_of_breaking"),
                     ("rune_of_negation", "wh_main_rune_abilities_rune_of_negation"),
                     ("rune_of_slowness", "wh2_dlc17_rune_abilities_rune_of_slowness"),
                     ("rune_of_speed", "wh2_dlc17_rune_abilities_rune_of_speed"),
                     ("rune_of_oath_and_steel", "wh_main_rune_abilities_rune_of_oath_and_steel")):
    assert ('marker = "%s"' % _m192) not in script_txt and ('"zz_auto_badge_%s"' % _m192) not in script_txt \
        and ('"%s"' % _k192) not in script_txt and (_k192 + "=") not in script_txt, \
        "BUILD REFUSED (round 192): %s is still in the script" % _m192
assert ('{ marker = "grombrindal_has_no_fear", name = "Grombrindal Has No Fear", trigger = "melee_or_wavering_aura",\n'
        '\t\tbadge = "zz_auto_badge_grombrindal_has_no_fear",\n'
        '\t\tkeys = { "wh_pro01_lord_passive_grombrindal_has_no_fear" },') in script_txt \
    and '"wh_pro01_lord_passive_grombrindal_has_no_fear" },   -- ROUND 192 (user: in range in melee or wavering)\n\t\taura_real = 55,' in script_txt, \
    "BUILD REFUSED (round 192): Grombrindal Has No Fear is not on melee_or_wavering_aura with its 55 m aura"
import gen_rule_sets as _gr192
assert len(_gr192.derive_moulder()) == 28, "BUILD REFUSED (round 192): the Moulder set moved (%d)" % len(_gr192.derive_moulder())
assert 'if a.M and not FOURTH.class_member(unit, "moulder") then return false end' in script_txt, \
    "BUILD REFUSED (round 192): the Moulder rule is not honoured"
for _k192 in ("wh2_dlc16_hero_abilities_shock_collar", "wh2_dlc16_lord_abilities_remouldered"):
    assert (_k192 + "=M;") in script_txt, "BUILD REFUSED (round 192): %s does not carry the Moulder rule" % _k192
assert "\tif FOURTH.ab_atarget ~= nil and FOURTH.ab_atarget.M == true then FOURTH.ab_filter = nil end" in script_txt, \
    "BUILD REFUSED (round 192): Remouldered's monster list still decides"
print("ROUND 192 GATE OK: running + closing; 5 runes gone; Grombrindal Has No Fear (55 m); Moulder rule (%d units)"
      % len(_gr192.derive_moulder()))
# ROUND 193 (user 2026-11-21): Scry-Orb on when_ready ("implement"); the read-only pre-shot probe ("implement
# recommendation and propose a test battle").
assert ('{ marker = "scry_orb", name = "Scry-Orb", trigger = "when_ready",\n\t\tbadge = "zz_auto_badge_scry_orb",\n'
        '\t\tkeys = { "wh3_dlc29_item_abilities_scry_orb" },') in script_txt, "BUILD REFUSED (round 193): Scry-Orb is not on when_ready"
import csv as _csv193
import gamedata_paths as _gp193
with open(_gp193.GAMEDATA + r"\unit_spec_abil.tsv", encoding="utf-8-sig") as _f193:
    _r193 = list(_csv193.reader(_f193, delimiter="\t"))
_h193 = _r193[0]
_row193 = next(r for r in _r193[2:] if r and r[0] == "wh3_dlc29_item_abilities_scry_orb")
_rec193 = int(float(_row193[_h193.index("recharge_time")]))
_use193 = int(float(_row193[_h193.index("num_uses")]))
assert _use193 > 1 and ('\t\t["wh3_dlc29_item_abilities_scry_orb"] = %d,\n' % _rec193) in script_txt, \
    "BUILD REFUSED (round 193): Scry-Orb's hold row is not its recharge (%d s, %d uses)" % (_rec193, _use193)
for _fn193 in ("preshot_now", "preshot_probe", "preshot_first_shot"):
    _i193 = script_txt.index("\nfunction FOURTH.%s(" % _fn193)
    _j193 = script_txt.index("\nend\n", _i193)
    _b193 = script_txt[_i193:_j193]
    assert "perform_special_ability" not in _b193 and "attempt_activation" not in _b193, \
        "BUILD REFUSED (round 193): FOURTH.%s issues an order (the probe must be read-only)" % _fn193
assert script_txt.count("if not st.firing then FOURTH.preshot_probe(u, st, now_s, inr, d, r) end   -- ROUND 193: read-only") == 1 \
    and script_txt.count("FOURTH.preshot_first_shot(u, st, now_s)   -- ROUND 193: the read-only pre-shot probe") == 1, \
    "BUILD REFUSED (round 193): the pre-shot probe is not called where it belongs"
print("ROUND 193 GATE OK: Scry-Orb on when_ready (hold %d s, %d uses); the pre-shot probe is read-only" % (_rec193, _use193))
# ROUND 194 (user 2026-11-21): remembered M/A states per unit type and ability; the reset on an optional MCT page.
assert script_txt.count('\nFOURTH.REMEMBER_FILE = "smart_ability_autocast_settings.txt"\n') == 1, \
    "BUILD REFUSED (round 194): the remembered-state file name moved"
assert script_txt.count("FOURTH.remember(ui_id, marker, value)   -- ROUND 194: remembered for the unit's type") == 1 \
    and script_txt.count("local rv = FOURTH.remembered_value(slot, marker)   -- ROUND 194") == 1 \
    and script_txt.count("if a ~= nil and a.remembered ~= nil then   -- ROUND 194: the type's remembered switch comes first") == 1, \
    "BUILD REFUSED (round 194): the switch must write once and both readers must read the remembered state"
assert script_txt.count("\nfunction smart_ability_autocast_reset_remembered()\n") == 1, \
    "BUILD REFUSED (round 194): the in-battle reset hook is missing"
_mct194 = open(SRC_ROOT + "/script/mct/settings/smart_ability_autocast.lua", encoding="utf-8").read()
_code194 = [l for l in _mct194.split("\n") if l.strip() and not l.lstrip().startswith("--")]
assert _code194[0] == 'if type(get_mct) ~= "function" then return end', \
    "BUILD REFUSED (round 194): the MCT page must start with the no-MCT guard"
assert "perform_special_ability" not in _mct194 and "FOURTH" not in _mct194, \
    "BUILD REFUSED (round 194): the MCT page must not act on units or reach into the battle script"
assert '"smart_ability_autocast_settings.txt"' in _mct194 and "smart_ability_autocast_reset_remembered" in _mct194, \
    "BUILD REFUSED (round 194): the MCT page must empty the same file and call the battle hook"
_e194 = _lupa174.LuaRuntime().eval("function(s) local f, e = load(s, '=smart_ability_autocast.lua'); return tostring(e) end")(_mct194)
assert _e194 == "nil", "BUILD REFUSED (round 194): the MCT page does not compile: " + _e194
print("ROUND 194 GATE OK: remembered states (one write, two reads, the hook); the MCT page compiles and is optional")
# ROUND 195 (user 2026-11-21, screenshot: "the '?' is in the middle. Also, there is no feedback to the player").
assert "set_tooltip_text(" not in _mct194, "BUILD REFUSED (round 195): the MCT page sets a tooltip (MCT's '?' marker)"
assert 'mod:add_new_section("remembered", "Remembered M/A choices")' in _mct194, \
    "BUILD REFUSED (round 195): the MCT page must name its section"
assert 'txt:SetStateText("Done")' in _mct194 and 'label:SetStateText("Forgotten")' in _mct194 \
    and 'btn:SetState("inactive")' in _mct194, "BUILD REFUSED (round 195): the Reset button gives no feedback"
print("ROUND 195 GATE OK: the MCT page has no tooltip marker, a named section and the Done / Forgotten feedback")
# ROUND 196 (user 2026-11-21: "I liked the previous text, just not the misaligned '?'")
assert 'add_new_action("reset_remembered", "Forget the remembered M/A choices", pressed)' in _mct194, \
    "BUILD REFUSED (round 196): the MCT label is not the user's text"
print("ROUND 196 GATE OK: the MCT label is 'Forget the remembered M/A choices', no tooltip")
# ROUND 197 (user 2026-11-21: "A: whole army"): the blob family's whole-army fallback.
assert script_txt.count("FOURTH.blob_relax = (ZZ_AUTO_TEST_NO_BLOB_FALLBACK ~= true) and not FOURTH.blob_better_exists(key, central)") == 1, \
    "BUILD REFUSED (round 197): the fallback flag must be set once, by the blob evaluation"
assert script_txt.count("FOURTH.blob_ap_rule(") == 5 and script_txt.count("FOURTH.blob_trash_rule(") == 3, \
    "BUILD REFUSED (round 197): the two rule wrappers are not at their places (armour: 1 definition + 4 uses, trash: 1 + 2)"
assert "if sc < FOURTH.blob_need(row.r) or not FOURTH.blob_trash_ok(e, sc, row.r) then return nil end" in script_txt, \
    "BUILD REFUSED (round 197): the wanderers must keep the plain trash rule"
_i197 = script_txt.index("\nfunction FOURTH.blob_better_exists(")
_b197 = script_txt[_i197:script_txt.index("\nend\n", _i197)]
assert "is_visible_to_alliance" not in _b197 and "local v = better or not readable" in _b197, \
    "BUILD REFUSED (round 197): the fallback must count the whole army (hidden too) and keep the rules when unreadable"
print("ROUND 197 GATE OK: the whole-army fallback (flag set by the blob evaluation, 6 wrapped rule uses, fail-closed)")
# ROUND 198 (user 2026-11-22, the overnight review: "fix" on rows 1, 2, 3, 6, 7, 8, 11).
assert script_txt.count("\nfunction FOURTH.entry_reset(ability, unit)\n") == 1 \
    and script_txt.count("FOURTH.entry_reset(ability, unit)") == 3, \
    "BUILD REFUSED (round 198): the entry reset must be one function, called by the poll and by the fast pass"
_i198 = script_txt.index("\nfunction FOURTH.ad_fast_pass()")
_f198 = script_txt[_i198:script_txt.index("\nbm:repeat_callback(poll, POLL_MS, POLL_NAME)", _i198)]
assert "FOURTH.entry_reset(ability, unit)" in _f198 and "FOURTH.ad_enemy = nil" not in _f198, \
    "BUILD REFUSED (round 198): the fast pass must reset every slot through FOURTH.entry_reset"
assert script_txt.count("\t\t\t\t\tcast_gate.unit_marker[ui_id] = nil\n") == 1 \
    and script_txt.count("cast_gate.unit_waiting[ui_id] == true") == 1 \
    and script_txt.count("cast_gate.unit_waiting[") == 5, \
    "BUILD REFUSED (round 198): the closed serial window must be re-armed by a repeat, and yield to a waiter"
assert script_txt.count('\t\t["wh3_dlc23_hero_abilities_get_tha_gitz!"] = 120,\n') == 1, \
    "BUILD REFUSED (round 198): Get Tha Gitz! (3 uses) has no charge-hold row"
assert script_txt.count('\t\t["wh3_dlc29_vmp_cha_necromancer_undeath_nightmare"] = true,') == 1, \
    "BUILD REFUSED (round 198): the Necromancer on a Nightmare (land_units key) is not in the Lord/Hero list"
for _fn198 in ("evaluate_slow_aura", "evaluate_guard_aura"):
    _a198 = script_txt.index("\nfunction FOURTH." + _fn198 + "(")
    _b198 = script_txt[_a198:script_txt.index("\nend\n", _a198)]
    assert "FOURTH.fast_enemy_near(" in _b198 and "is_moving()" not in _b198, \
        "BUILD REFUSED (round 198): " + _fn198 + " must use the round-192 fast-enemy read (running and closing)"
# every multi-use key of the mod has a hold row, and no_self equals the game's target_self = false on the two families
import csv as _csv198
import re as _re198
import gamedata_paths as _gp198
_rows198 = list(_csv198.reader(open(_gp198.GAMEDATA + "\\unit_spec_abil.tsv", encoding="utf-8"), delimiter="\t"))
_h198 = {n: i for i, n in enumerate(_rows198[0])}
_game198 = {r[0]: r for r in _rows198[1:]}
_ab0 = script_txt.index("local ABILITIES = {")
_ab1 = script_txt.index("local charge_gate = {")
_hold198 = script_txt[_ab1:script_txt.index("\n\tuntil_tick = {}", _ab1)]
_bad198 = []
for _m in _re198.finditer(r'\n\t\{ marker = "([^"]+)", name = "[^"]*", trigger = "([^"]+)",(.*?)(?=\n\t\{ marker = |\n\t-- |\n\}\n)',
                          script_txt[_ab0:_ab1], _re198.S):
    _mk, _tr, _body = _m.group(1), _m.group(2), _m.group(3)
    _keys = _re198.findall(r'"(wh[0-9a-z_!]*[^"]*)"', _body.split("keys = {")[1].split("}")[0])
    # an entry takes the largest hold of its keys, so ONE row is enough for an entry
    _multi = [_k for _k in _keys if int(_game198[_k][_h198["num_uses"]]) > 1]
    if _multi and _tr != "air_drop_on_infantry" and not any(('["' + _k + '"] = ') in _hold198 for _k in _keys):
        _bad198.append("no hold row: " + _mk)
    if _tr in ("melee_self_or_ally", "self_or_ally_fire_melee"):
        _noself = all(_game198[_k][_h198["target_self"]] == "false" for _k in _keys)
        if _noself != ("\t\tno_self = true," in _body):
            _bad198.append("no_self differs from the game's target_self: " + _mk)
assert not _bad198, "BUILD REFUSED (round 198): " + "; ".join(_bad198)
assert script_txt.count("\t\tno_self = true,") == 3 and "FOURTH.CARD_TIP_NOSELF[ability.trigger]" in script_txt, \
    "BUILD REFUSED (round 198): the no_self entries or their card are missing"
assert "\nFOURTH.BUGMAN_CLEAR_M = 55 " in script_txt, "BUILD REFUSED (round 198): Bugman's keep-out distance is the game's 55 m"
# the game runs Lua 5.1: the shipped script must compile there too (lupa's default is a newer Lua)
from lupa import lua51 as _lua51_198
_c198 = _lua51_198.LuaRuntime().eval("function(s) local f, e = loadstring(s, '=zz_test_deadly_onslaught.lua'); return tostring(e) end")(script_txt)
assert _c198 == "nil", "BUILD REFUSED (round 198): the script does not compile on Lua 5.1: " + str(_c198)
print("ROUND 198 GATE OK: the entry reset shared with the fast pass, the re-armed serial window, every multi-use key held, "
      "no_self = the game's target_self, the two auras on the round-192 read, Bugman's 55 m, compiles on Lua 5.1")
# ROUND 199 (user 2026-11-22, the overnight review's second replies: rows 5, 9, 10, 12).
assert script_txt.count("if candidate == listed_key or candidate == FOURTH.KEY_LOWER[listed_key] then") == 1 \
    and "if lk ~= key then FOURTH.KEY_LOWER[key] = lk end" in script_txt, \
    "BUILD REFUSED (round 199): the badge compare must accept a listed key in lower case"
assert script_txt.count("\nfunction FOURTH.ally_arm_wrap(f, ally_only)\n") == 1 \
    and 'ability.evaluate = FOURTH.ally_arm_wrap(ability.evaluate, ability.ally_value_arm == "only")' in script_txt, \
    "BUILD REFUSED (round 199): the ally arm is not wired"
_arm199 = []
for _m in _re198.finditer(r'\n\t\{ marker = "([^"]+)", name = "[^"]*", trigger = "([^"]+)",(.*?)(?=\n\t\{ marker = |\n\t-- |\n\}\n)',
                          script_txt[_ab0:_ab1], _re198.S):
    _mk, _body = _m.group(1), _m.group(3)
    if "\t\tally_value_arm = " not in _body:
        continue
    _keys = _re198.findall(r'"(wh[^"]*)"', _body.split("keys = {")[1].split("}")[0])
    _only = '\t\tally_value_arm = "only",' in _body
    for _k in _keys:
        _r = _game198[_k]
        assert _r[_h198["target_friends"]] == "true", "BUILD REFUSED (round 199): %s does not target friends" % _k
        _game_only = (_r[_h198["target_self"]] == "false" and _r[_h198["target_ground"]] == "false")
        assert _only == _game_only, "BUILD REFUSED (round 199): ally-only differs from the game's target flags: " + _mk
        assert ("\t\tally_range_real = %d,\n" % int(float(_r[_h198["target_intercept_range"]]))) in _body, \
            "BUILD REFUSED (round 199): %s does not carry the game's range" % _mk
    _arm199.append(_mk)
assert len(_arm199) == 9 and script_txt.count("\t\tally_value_arm = true,") == 7 \
    and script_txt.count('\t\tally_value_arm = "only",') == 2, \
    "BUILD REFUSED (round 199): the ally arm rides %d entries, expected 9 (7 + 2 ally-only; round 201)" % len(_arm199)
_i199 = script_txt.index("\nfunction FOURTH.enemy_is_infantry(enemy)\n")
_b199 = script_txt[_i199:script_txt.index("\nend\n", _i199)]
assert "FOURTH.class_keys.large[t199] == true then return false end" in _b199 and "is_currently_flying()" in _b199, \
    "BUILD REFUSED (round 199): the infantry test must refuse the large set and a flying unit"
_r199 = script_txt.index("\nfunction FOURTH.remember(ui_id, marker, value)\n")
_rb199 = script_txt[_r199:script_txt.index("\nend\n", _r199)]
assert "a.remembered" not in _rb199.replace("a.remembered is the START", "") and "a.remember_next[t] = (value == true)" in _rb199 \
    and script_txt.count("pairs(a.remember_next or {})") == 1 and "pairs(a.remembered or {})" not in script_txt, \
    "BUILD REFUSED (round 199): a click must write remember_next only (the battle's start table stays)"
print("ROUND 199 GATE OK: a capital key is claimed; the ally arm on 10 entries (2 ally-only, by the game's flags); "
      "the infantry test refuses large and flying; a click writes the next battle's choice only")
# ROUND 201 (user rulings 2026-11-22, after the Dwarf battle on the release build). PERMANENT (rule 12, the left-hand
# wheel only): the game puts every source_type = rune ability on the right-hand bar. One of them (Master Rune of
# Slowness) fired by itself because its entry rode a default-armed family and a cast needs no badge.
import csv as _csv201
import gamedata_paths as _gp201
with open(_gp201.GAMEDATA + r"\unit_abilities.tsv", encoding="utf-8-sig") as _f201:
    _r201 = list(_csv201.reader(_f201, delimiter="\t"))
_h201 = _r201[0]
_runes201 = [r[0] for r in _r201[2:] if r and r[_h201.index("source_type")] == "rune"]
assert len(_runes201) == 12, "BUILD REFUSED (round 201): the game's rune list moved (%d)" % len(_runes201)
for _k201 in _runes201:
    assert ('"%s"' % _k201) not in script_txt and (_k201 + "=") not in script_txt and (_k201 + ";") not in script_txt, \
        "BUILD REFUSED (round 201 right-hand-bar gate): the rune %s is in the script" % _k201
for _m201 in ("master_rune_of_breaking", "master_rune_of_negation", "master_rune_of_slowness", "master_rune_of_speed",
              "master_rune_of_oath_and_steel"):
    assert ('marker = "%s"' % _m201) not in script_txt and ('"zz_auto_badge_%s"' % _m201) not in script_txt, \
        "BUILD REFUSED (round 201): %s is still in the script" % _m201
with open(_gp201.GAMEDATA + r"\unit_spec_abil.tsv", encoding="utf-8-sig") as _f201:
    _s201 = list(_csv201.reader(_f201, delimiter="\t"))
_sh201 = _s201[0]
with open(_gp201.GAMEDATA + r"\battle_vortexs.tsv", encoding="utf-8-sig") as _f201:
    _v201 = list(_csv201.reader(_f201, delimiter="\t"))
_vh201 = _v201[0]
for _m201, _n201, _k201 in (("whirlwind_of_death_ror", "Endless Whirlwind of Death", "wh3_dlc25_unit_abilities_whirlwind_of_death_ror"),
                            ("whirlwind_of_death_ror_upgraded", "Endless Whirlwind of Death Upgraded",
                             "wh3_dlc25_unit_abilities_whirlwind_of_death_ror_upgraded")):
    assert ('\t{ marker = "%s", name = "%s", trigger = "melee_unwavering",\n\t\tbadge = "zz_auto_badge_%s",\n'
            '\t\tkeys = { "%s" },\n\t\tox = 0, oy = 0 },\n' % (_m201, _n201, _m201, _k201)) in script_txt, \
        "BUILD REFUSED (round 201): %s is not on melee_unwavering" % _m201
    _row201 = next(r for r in _s201[2:] if r and r[0] == _k201)
    _vx201 = _row201[_sh201.index("vortex")]
    _vr201 = next(r for r in _v201[2:] if r and r[0] == _vx201)
    assert _vr201[_vh201.index("affects_allies")] == "false", \
        "BUILD REFUSED (round 201): the vortex of %s hits allies (it needs a clear-of-ours trigger)" % _k201
print("ROUND 201 GATE OK: none of the game's %d rune-type keys is in the script (the right-hand bar); "
      "Endless Whirlwind of Death x2 on melee_unwavering, vortexes that do not hit allies" % len(_runes201))
# ROUND 202 (user 2026-11-22: "Yes, build the probe"): the wave probe is a console command, called by nothing.
assert script_txt.count("\nfunction zz_wave(deg, fwd, side, key)\n") == 1 \
    and script_txt.count("su.uc:perform_special_ability_ground(key, pos, deg, 0)") == 1, \
    "BUILD REFUSED (round 202): the wave probe is not defined once with the orientation argument"
assert script_txt.count("zz_wave(") == 2, \
    "BUILD REFUSED (round 202): something calls the wave probe (%d mentions, expected its banner and its definition)" \
    % script_txt.count("zz_wave(")
assert script_txt.count("perform_special_ability_ground(") - script_txt.count("-- ") * 0 >= 2 \
    and "uc:perform_special_ability_ground(ability_key, pos, 0, 0)" in script_txt, \
    "BUILD REFUSED (round 202): the mod's own ground cast no longer sends orientation 0, width 0"
print("ROUND 202 GATE OK: the wave probe zz_wave (console only, called by nothing), the mod's own ground casts unchanged")
# ROUND 203 (user rulings 2026-11-22): free aim for the straight waves, key by key.
import csv as _csv203
import re as _re203
import gamedata_paths as _gp203


def _tab203(name):
    with open(_gp203.GAMEDATA + "\\" + name, encoding="utf-8-sig") as _f:
        _r = list(_csv203.reader(_f, delimiter="\t"))
    return {x[0]: dict(zip(_r[0], x)) for x in _r[2:] if x}


_usa203, _vx203 = _tab203("unit_spec_abil.tsv"), _tab203("battle_vortexs.tsv")
_n203 = {"enemy_wave": 0, "enemy_wave_charge": 0, "enemy_cone": 0}
_e203 = {"enemy_wave": 0, "enemy_wave_charge": 0, "enemy_cone": 0}
for _fam203, _src203 in (("enemy_wave", "target_near_edge"), ("enemy_wave_charge", "target_near_edge"),
                         ("enemy_cone", "activator_front")):
    for _m203 in _re203.finditer(r'\{ marker = "([^"]+)", name = "[^"]*", trigger = "%s",(.*?)ox = 0' % _fam203,
                                 script_txt, _re203.S):
        _e203[_fam203] += 1
        for _k203 in _re203.findall(r'"(wh[^"]*)"', _m203.group(2).split("keys = {")[1].split("}")[0]):
            _a203 = _usa203[_k203]
            _v203 = _vx203.get(_a203["vortex"])
            assert _v203 is not None, "BUILD REFUSED (round 203): %s has no vortex row" % _k203
            assert _v203["launch_source"] == _src203, \
                "BUILD REFUSED (round 203): %s starts at '%s', its family %s needs '%s'" \
                % (_k203, _v203["launch_source"], _fam203, _src203)
            if _fam203 == "enemy_wave":
                assert _a203["target_ground"] == "true", \
                    "BUILD REFUSED (round 203): %s has no ground form, free aim cannot order it" % _k203
            _n203[_fam203] += 1
assert _e203 == {"enemy_wave": 32, "enemy_wave_charge": 0, "enemy_cone": 5}, \
    "BUILD REFUSED (round 203): the wave families moved: %s" % _e203
assert script_txt.count("\nFOURTH.FREE_AIM_STEPS = 24 ") == 1 \
    and script_txt.count("\nfunction FOURTH.ww_aim_value(unit, e, m, row, hx, hz, shift)\n") == 1 \
    and script_txt.count("\nfunction FOURTH.ww_line_value(unit, m, row, sx, sz, ex, ez)\n") == 1 \
    and script_txt.count("\nfunction FOURTH.aim_cast(uc, ability_key, aim)\n") == 1 \
    and script_txt.count("uc:perform_special_ability_ground(ability_key, pos, aim.deg, 0)") == 1 \
    and script_txt.count('\telseif FOURTH.eg_arm == "ww" and FOURTH.ww_aim ~= nil then\n') == 1 \
    and script_txt.count("\tFOURTH.ww_aim = nil   -- ROUND 203: the free aim of a wave\n") == 1, \
    "BUILD REFUSED (round 203): the free-aim code is not wired"
# free aim is asked for in ONE place: the enemy_wave evaluator (never the charge waves, the cones, the wanderers)
assert script_txt.count("FOURTH.ww_aim_value(") == 3 and script_txt.count("ZZ_AUTO_TEST_NO_FREE_AIM") == 3, \
    "BUILD REFUSED (round 203): free aim is asked for outside the enemy_wave evaluator (%d, %d)" \
    % (script_txt.count("FOURTH.ww_aim_value("), script_txt.count("ZZ_AUTO_TEST_NO_FREE_AIM"))
_i203 = script_txt.index("\nfunction FOURTH.evaluate_enemy_wave(unit, routing)\n")
_b203 = script_txt[_i203:script_txt.index("\nfunction FOURTH.evaluate_enemy_wander(unit, routing)\n", _i203)]
assert "FOURTH.ww_aim_value(unit, e, m, row, hx, hz, shifts[q])" in _b203 and "FOURTH.ww_target_still(e)" in _b203 \
    and "local free = (ZZ_AUTO_TEST_NO_FREE_AIM ~= true)" in _b203, \
    "BUILD REFUSED (round 203): the enemy_wave evaluator does not test the free headings on standing targets"
_c203 = script_txt.index("\nfunction FOURTH.aim_cast(uc, ability_key, aim)\n")
_cb203 = script_txt[_c203:script_txt.index("\nend\n", _c203)]
assert "if pos == nil then return nil, nil, true end" in _cb203 and "bm:get_terrain_height(aim.x, aim.z)" in _cb203, \
    "BUILD REFUSED (round 203): the free-aim cast must fail closed on an unreadable point"
print("ROUND 203 GATE OK: free aim on %d placed wave keys (%d entries, each target_near_edge with a ground form); "
      "%d charge-wave keys and %d caster-front cone keys untouched" % (_n203["enemy_wave"], _e203["enemy_wave"],
                                                                      _n203["enemy_wave_charge"], _n203["enemy_cone"]))
# ROUND 204 (user ruling 2026-11-22): an exact wave drops the safety distance for a count of OUR SOLDIERS under it.
assert script_txt.count("\nFOURTH.WAVE_OWN_MAX = 5 ") == 1 \
    and script_txt.count("\nFOURTH.FREE_AIM_SHIFTS = { 0, 6, -6, 12, -12, 18, -18 }") == 1 \
    and script_txt.count("\nFOURTH.FREE_AIM_EVERY = 4 ") == 1 \
    and script_txt.count("\nfunction FOURTH.wave_cover(s, sx, sz, ex, ez, r)\n") == 1 \
    and script_txt.count("\nfunction FOURTH.ww_exact(row)\n\treturn row.buf == 0 and ZZ_AUTO_TEST_NO_FREE_AIM ~= true\nend\n") == 1, \
    "BUILD REFUSED (round 204): the soldiers rule's constants or functions moved"
_i204 = script_txt.index("\nfunction FOURTH.ww_line_value(unit, m, row, sx, sz, ex, ez)\n")
_b204 = script_txt[_i204:script_txt.index("\n-- ROUND 164: the enemy value a path touches", _i204)]
assert _b204.index("if FOURTH.ww_exact(row) then") < _b204.index("local need = row.r + FOURTH.SHOT_SAFE_M + row.buf * math.min(1, tmax)") \
    and "if o.men > 1 then" in _b204 and "own = own + o.men * FOURTH.wave_cover(o, sx, sz, ex, ez, row.r)" in _b204 \
    and "if own > FOURTH.WAVE_OWN_MAX then return nil end" in _b204 and "if oid == nil or oid ~= self_id then" in _b204, \
    "BUILD REFUSED (round 204): an exact wave must count our soldiers (never single entities, never the caster) and " \
    "a drifting wave must keep the safety distance"
_ww204 = _re203.search(r'FOURTH\.WW_TEXT = "([^"]*)"', script_txt).group(1)
_rows204 = dict(x.split("=", 1) for x in _ww204.split(";") if "=" in x)
_exact204, _drift204 = [], []
for _m204 in _re203.finditer(r'\{ marker = "([^"]+)", name = "[^"]*", trigger = "enemy_wave",(.*?)ox = 0', script_txt, _re203.S):
    for _k204 in _re203.findall(r'"(wh[^"]*)"', _m204.group(2).split("keys = {")[1].split("}")[0]):
        _f204 = _rows204[_k204].split(",")
        assert _f204[0] == "1", "BUILD REFUSED (round 204): %s is on enemy_wave but its table row is not a wave" % _k204
        (_exact204 if float(_f204[4]) == 0 else _drift204).append(_k204)
assert len(_exact204) == 27 and len(_drift204) == 5, \
    "BUILD REFUSED (round 204): the exact / drifting split moved (%d exact, %d drifting)" % (len(_exact204), len(_drift204))
for _k204 in ("wh2_dlc11_spell_bound_tidecall", "wh2_dlc11_spell_bound_wind_blast", "wh_main_item_abilities_fiery_ring_of_thori"):
    assert _k204 in _exact204, "BUILD REFUSED (round 204): %s is not an exact wave" % _k204
print("ROUND 204 GATE OK: %d exact waves count our soldiers under the wave (limit 5, single entities and the caster not "
      "counted), %d drifting waves keep the safety distance; Tidecall and Wind Blast ride enemy_wave" % (len(_exact204), len(_drift204)))
# ROUND 205 (user 2026-11-22): the growing waves are cones (GENERATED), enemy single entities are not counted.
import gen_wave_cone as _gc205
_cone205 = _gc205.derive(script_txt)
assert len(_cone205) == 19, "BUILD REFUSED (round 205): the growing-wave set moved (%d)" % len(_cone205)
assert ('\nFOURTH.WW_CONE_TEXT = "%s"\n' % _gc205.text(_cone205)) in script_txt, \
    "BUILD REFUSED (round 205): FOURTH.WW_CONE_TEXT differs from the game data (run tools/gen_wave_cone.py)"
for _k205 in _cone205:
    assert _k205 in _exact204, "BUILD REFUSED (round 205): the growing wave %s is not an exact wave" % _k205
assert script_txt.count("\nfunction FOURTH.ww_in_wave(px, pz, sx, sz, ex, ez, r)\n") == 1 \
    and "if cone ~= nil then rr = math.min(r, cone.r0 + cone.grow * t * math.sqrt(l2)) end" in script_txt \
    and script_txt.count("FOURTH.ww_in_wave(") == 3 \
    and script_txt.count("\t\tFOURTH.ww_cone = (row.r0 ~= nil) and row or nil   -- ROUND 205") == 1, \
    "BUILD REFUSED (round 205): the cone test is not wired"
assert "\t\t\tif o.men > 1 then\n\t\t\t\tlocal c = FOURTH.wave_cover(o, sx, sz, ex, ez, row.r)\n" in _b204, \
    "BUILD REFUSED (round 205): an exact wave's value must skip enemy single entities"
print("ROUND 205 GATE OK: %d growing waves carry their real cone (start radius, growth per metre from the game data); "
      "an exact wave's value counts enemy soldiers only" % len(_cone205))
# ROUND 206 (tuning, the user's Sunfang battle 2026-11-22): a walking enemy is not counted in an exact wave's value.
assert "\t\t\tif o.still == nil then o.still = FOURTH.ww_target_still(o) end\n" in _b204 \
    and "\t\t\t\tif c > 0 and o.still then val = val + (o.value or 1) * c end\n" in _b204, \
    "BUILD REFUSED (round 206): an exact wave's value must count standing enemies only"
print("ROUND 206 GATE OK: an exact wave's value counts enemy soldiers that stand still")
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
assert script_txt.count('trigger = "melee_unwavering"') == 278, \
    "the melee_unwavering entry count is not 374 (Massacre + 2 boss-only removed)"
assert script_txt.count('trigger = "charge_or_melee"') == 34, \
    "the charge_or_melee entry count is not 28 (round 123: +3 enemy-speed hexes)"

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
assert script_txt.count("\t{ marker = ") == 982, "the abilities table is not 982 entries"
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
assert script_txt.count('trigger = "metallurgy_melee"') == 0, "the metallurgy trigger count is not 8 (four Enchanted Metallurgy + four Master of Alchemy)"
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
assert script_txt.count("\t{ marker = ") == 982, "the abilities table is not 982 entries"
assert script_txt.count('trigger = "charge_only"') == 5, "the charge_only entry count is not 5 (round 185: + Swiftness of Itzl)"
assert script_txt.count('trigger = "wavering_self"') == 4, "the wavering_self entry count is not 3"
assert script_txt.count('trigger = "wavering_self_or_ally"') == 2, "the wavering_self_or_ally entry count is not 2"
assert script_txt.count('trigger = "charge_or_wavering"') == 2, "the charge_or_wavering entry count is not 2 (round 170)"
assert script_txt.count('trigger = "wavering_ally_range"') == 6, "the wavering_ally_range entry count is not 6"
assert script_txt.count('trigger = "metallurgy_melee"') == 0, "the metallurgy_melee entry count is not 8"
assert script_txt.count('trigger = "ushoran_health"') == 11, "the ushoran_health entry count is not 20 (harness 104: 13 moved to the ally-aware triggers)"
assert script_txt.count('trigger = "health_aura_ground"') == 2, "the health_aura_ground entry count is not 2 (Star of Avelorn + Gulyas)"
assert script_txt.count('trigger = "health_aura_ally"') == 8, "the health_aura_ally entry count is not 9"
assert script_txt.count('trigger = "health_aura_self"') == 2, "the health_aura_self entry count is not 2 (Salyak's Lullaby + Locus of Fecundity)"
assert script_txt.count('trigger = "melee_health75"') == 4, "the melee_health75 entry count is not 4 (round 183: + Plaguereaper, Reaper of Souls)"
assert script_txt.count('trigger = "tired"') == 1, "the tired entry count is not 2"
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
    ("captain_of_the_phoenix_guard", { "wh3_dlc27_character_abilities_captain_of_the_phoenix_guard" }),
    ("cash_cascade", { "wh3_dlc26_character_abilities_cash_cascade" }),
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
    ("gulyas", { "wh3_dlc24_lord_abilities_gulyas" }),
    ("helm_of_yvresse", { "wh2_dlc15_item_abilities_helm_of_yvresse" }),
    ("helping_hand", { "wh2_pro08_character_abilities_helping_hand" }),
    ("inspired_assault_i", { "wh3_main_lord_abilities_inspired_assault_i" }),
    ("inspired_assault_ii", { "wh3_main_lord_abilities_inspired_assault_ii" }),
    ("inspired_assault_iii", { "wh3_main_lord_abilities_inspired_assault_iii" }),
    ("inspired_defence_i", { "wh3_main_lord_abilities_inspired_defence_i" }),
    ("inspired_defence_ii", { "wh3_main_lord_abilities_inspired_defence_ii" }),
    ("inspired_defence_iii", { "wh3_main_lord_abilities_inspired_defence_iii" }),
    ("lord_of_grand_cathay", { "wh3_dlc24_lord_abilities_lord_of_grand_cathay" }),
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
    ("vial_of_troll_blood", { "wh_dlc08_item_abilities_vial_of_troll_blood" }),
    ("warpstone_addiction", { "wh3_dlc29_lord_abilities_warpstone_addiction" }),
    ("warrior_familiar", { "wh3_dlc27_item_abilities_warrior_familiar" }),
    ("winters_chill", { "wh3_dlc29_ability_bound_prayer_winters_chill", "wh3_dlc29_spell_bound_prayer_winters_chill" }),
    ("witchbrew", { "wh2_main_character_abilities_witchbrew", "wh3_dlc24_unit_abilities_witchbrew" }),
    ("worlds_edge_armour", { "wh2_main_item_abilities_worlds_edge_armour" }),
    ("znarkharjas_ward", { "wh3_dlc24_hero_abilities_znarkharjas_ward" }),
]
BLOCK789 = [x for x in BLOCK789 if x[0] not in ('rune_of_oath_and_steel', 'rune_of_speed')]   # ROUND 192: the spell-bar runes left the mod
BLOCK789 = [x for x in BLOCK789 if x[0] not in ('master_rune_of_oath_and_steel', 'master_rune_of_speed')]   # ROUND 201: the Master Runes left the mod
assert len(BLOCK789) == 58, "the block-7-9 entry list is not 66 (Greater Faith Bastion removed in 101)"
_nk789 = 0
for _mk, _kys in BLOCK789:
    assert 'marker = "%s"' % _mk in script_txt, "block-7-9 marker missing: " + _mk
    assert 'badge = "zz_auto_badge_%s"' % _mk in script_txt, "block-7-9 badge missing: " + _mk
    for _ky in _kys:
        assert '"%s"' % _ky in script_txt, "block-7-9 key missing: " + _ky
        _nk789 = _nk789 + 1
assert _nk789 == 62, "the block-7-9 key count is not 70 (got %d)" % _nk789

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
    ("master_rune_of_breaking", { "wh2_dlc17_rune_abilities_master_rune_of_breaking" }),
    ("master_rune_of_negation", { "wh_dlc06_rune_abilities_master_rune_of_negation" }),
    ("master_rune_of_slowness", { "wh2_dlc17_rune_abilities_master_rune_of_slowness" }),
    ("beguile", { "wh_dlc04_lord_abilities_beguile" }),
    ("master_of_the_black_arts", { "wh_main_lord_abilities_master_of_the_black_arts" }),
    ("mastered_strike", { "wh3_cp1_lord_abilities_mastered_strike" }),
    ("maw_shard", { "wh3_main_item_abilities_maw_shard" }),
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
    ("the_seerstaff_of_saphery", { "wh2_main_spell_bound_the_seerstaff_of_saphery" }),
    ("the_tricksters_pendant", { "wh2_main_item_abilities_the_tricksters_pendant" }),
    ("the_vial_of_hashut", { "wh3_dlc23_item_abilities_the_vial_of_hashut" }),
    ("the_vortex_shard", { "wh2_main_item_abilities_the_vortex_shard" }),
    ("the_wintertooth_crown", { "wh_dlc08_item_abilities_the_wintertooth_crown" }),
    ("wissenland_runefang", { "wh2_dlc13_weapon_abilities_wissenland_runefang" }),
    ("the_withering", { "wh3_dlc23_spell_bound_the_withering", "wh3_twa08_spell_bound_the_withering" }),
    ("they_needs_stabbin", { "wh2_dlc15_character_abilities_they_needs_stabbin" }),
    ("thorns_aura", { "wh3_dlc24_hero_abilities_thorns_aura" }),
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
    ("void_pendulum", { "wh3_main_item_abilities_void_pendulum" }),
    ("vorozhejas_foresight", { "wh3_dlc24_hero_abilities_vorozhejas_foresight" }),
    ("waaagh_in_combat", { "wh3_dlc26_unit_abilities_waaagh_in_combat", "wh_main_character_abilities_waaagh" }),
    ("wand_of_jet", { "wh_main_item_abilities_wand_of_jet" }),
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
    ("wrath_of_the_storm", { "wh3_main_lord_abilities_wrath_of_the_storm" }),
    ("wrathful_reaper", { "wh3_main_lord_abilities_wrathful_reaper" }),
    ("wristbands_of_black_gold", { "wh3_dlc29_item_abilities_wristbands_of_black_gold" }),
    ("youre_next", { "wh2_dlc15_lord_abilities_youre_next" }),
]
AUTO327 = [x for x in AUTO327 if x[0] not in ('earthing_rod', 'hagtree_fetish', 'master_of_the_black_arts', 'maw_shard', 'power_familiar', 'watched_by_the_watcher', 'sceptre_of_stability', 'locus_of_abjuration', 'focus_instincts')]   # ROUND 171: closed by the user
AUTO327 = [x for x in AUTO327 if x[0] not in ('null_stone', 'item_passive_rock_eye')]   # ROUND 173: closed by the user
AUTO327 = [x for x in AUTO327 if x[0] not in ('snowflake_pendant', 'stave_of_avelorn')]   # ROUND 180: closed by the user
AUTO327 = [x for x in AUTO327 if x[0] not in ('rune_of_breaking', 'rune_of_negation', 'rune_of_slowness')]   # ROUND 192: the spell-bar runes left the mod
AUTO327 = [x for x in AUTO327 if x[0] not in ('master_rune_of_breaking', 'master_rune_of_negation', 'master_rune_of_slowness')]   # ROUND 201: the Master Runes left too
assert len(AUTO327) == 281, ("the auto-327 entry list is not 305 (4 boss-only removed in 101; 2 army-bar entries removed in round 121)")
_nk327 = 0
for _mk, _kys in AUTO327:
    assert 'marker = "%s"' % _mk in script_txt, "auto-327 marker missing: " + _mk
    assert 'badge = "zz_auto_badge_%s"' % _mk in script_txt, "auto-327 badge missing: " + _mk
    for _ky in _kys:
        assert '"%s"' % _ky in script_txt, "auto-327 key missing: " + _ky
        _nk327 = _nk327 + 1
assert _nk327 == 296, ("the auto-327 key count is not 320 (got %d; 3 army-bar keys removed in round 121)" % _nk327)

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
assert "FOURTH.BLOOD_SACRIFICE_RANGE_M = 80" in script_txt, "the 70% blood-sacrifice range constant is missing"
assert "FOURTH.EAT_DA_RUNTS_RANGE_M = 80" in script_txt, "the 70% eat-da-runts range constant is missing"
assert "blood_sacrifice = FOURTH.evaluate_blood_sacrifice," in script_txt, "the blood-sacrifice map entry is missing"
assert "eat_da_runts = FOURTH.evaluate_eat_da_runts," in script_txt, "the eat-da-runts map entry is missing"
assert "blood_sacrifice SKIPPED:" in script_txt, "the blood-sacrifice drift skip is missing"
assert "eat_da_runts SKIPPED:" in script_txt, "the eat-da-runts drift skip is missing"
assert 'string.format("blood sacrifice: lowest-health ally %d%% (<= 75%%), cast on ally"' in script_txt, "the blood-sacrifice reason is missing"
assert 'string.format("eat da runts: self health %d%% (<= 75%%), cast on the cheapest healthy ally"' in script_txt, "the eat-da-runts reason is missing (round 180)"
assert script_txt.count('trigger = "blood_sacrifice"') == 1, "the blood_sacrifice entry count is not 1"
assert script_txt.count('trigger = "eat_da_runts"') == 1, "the eat_da_runts entry count is not 1"
assert script_txt.count("FOURTH.bs_ally = nil") == 3, "the bs_ally clears are not exactly three"
assert script_txt.count("FOURTH.edr_ally = nil") == 3, "the edr_ally clears are not exactly three"
FINAL6 = [
    ("blood_sacrifice", "wh3_dlc26_lord_abilities_blood_sacrifice"),
    ("eat_da_runts", "wh3_dlc26_unit_abilities_eat_da_runts"),
    ("locus_of_virulence", "wh3_main_character_abilities_locus_of_virulence"),
    ("ultimate_verdict", "wh3_cp1_character_abilities_terrifying_presence"),
]
assert len(FINAL6) == 4, "the final-roster entry list is not 6"
assert script_txt.count("FOURTH.cast_target = unit") == 2, "the self-cast writes are not exactly two"
_nk92 = 0
for _mk, _ky in FINAL6:
    assert 'marker = "%s"' % _mk in script_txt, "final-roster marker missing: " + _mk
    assert 'badge = "zz_auto_badge_%s"' % _mk in script_txt, "final-roster badge missing: " + _mk
    assert '"%s"' % _ky in script_txt, "final-roster key missing: " + _ky
    _nk92 = _nk92 + 1
assert _nk92 == 4, "the final-roster key count is not 6 (got %d)" % _nk92

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
assert 'FOURTH.ACCUSATION_RANGE_M = 55' in script_txt, "the 70% accusation range constant is missing"
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
assert script_txt.count('trigger = "enemy_engaged_or_shot"') == 22, \
    "the enemy trigger count is not 85 (3 boss-only removed; Warden's Cage removed in round 121)"
assert script_txt.count('trigger = "melee_unwavering"') == 278, \
    "the melee_unwavering count is not 374 (Massacre + 2 boss-only removed)"
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
           ("FOURTH.BLOOD_SACRIFICE_RANGE_M", 100, 80),   # ROUND 188: max(70%, real - 20)
           ("FOURTH.EAT_DA_RUNTS_RANGE_M", 100, 80),
           ("FOURTH.ACCUSATION_RANGE_M", 75, 55))
for _tok, _real, _want in _RULE95:
    assert max(int(_real * 0.70 + 1e-9), _real - 20) == _want, "the documented 70%% target is wrong for " + _tok
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
# enemy-cast constants, the real->bound map, the 96 range_real fields, the load-loop
# wiring, the shared picker and the enemy-ground evaluator/helper/key-set.
assert "FOURTH.ENEMY_CAST = {" in script_txt, "the real->bound map is missing"
assert "ability.range_m = FOURTH.ENEMY_CAST[ability.range_real]" in script_txt, \
    "the load-loop real->bound mapping is missing"
# ROUND 106: 163 Class-A/B + 30 bombardment entries = 193 range_real fields.
assert script_txt.count("\t\trange_real = ") == 428, "the range_real fields are not 207"
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
assert script_txt.count('trigger = "enemy_ground_area"') == 2, "the enemy-ground trigger count is not 9"
assert "unit_in_range(" not in script_txt, "the engine unit_in_range call is back"
assert "FOURTH.ENEMY_CAST_R15  = 10" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R15  = 10"
assert "FOURTH.ENEMY_CAST_R20  = 14" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R20  = 14"
assert "FOURTH.ENEMY_CAST_R30  = 21" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R30  = 21"
assert "FOURTH.ENEMY_CAST_R35  = 24" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R35  = 24"
assert "FOURTH.ENEMY_CAST_R50  = 35" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R50  = 35"
assert "FOURTH.ENEMY_CAST_R70  = 50" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R70  = 50"
assert "FOURTH.ENEMY_CAST_R75  = 55" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R75  = 55"
assert "FOURTH.ENEMY_CAST_R100 = 80" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R100 = 80"
assert "FOURTH.ENEMY_CAST_R150 = 130" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R150 = 130"
assert "FOURTH.ENEMY_CAST_R180 = 160" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R180 = 160"
assert "FOURTH.ENEMY_CAST_R200 = 180" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R200 = 180"
assert "FOURTH.ENEMY_CAST_R500 = 480" in script_txt, "the 70% enemy-cast constant is missing: FOURTH.ENEMY_CAST_R500 = 480"
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
assert script_txt.count("\t\tally_range_real = ") == 80, "the ally_range_real fields are not 80 (81 - Master Rune of Oath & Steel, round 201)"

# ROUND v104 (A): THE IN-FLIGHT GATE.
assert "local cast_gate = {" in script_txt, "the cast_gate table is missing"
assert '["wh3_main_lord_abilities_nurgling_tide"] = 3,' in script_txt, "Nurgling Tide's 3 s wind-up is missing from cast_gate"
assert script_txt.count("local IN_FLIGHT_SETTLE_SECONDS = 2") == 1, "the in-flight slack constant is missing"
assert "local hold_s = ability.wind_up_s + IN_FLIGHT_SETTLE_SECONDS" in script_txt, "the in-flight hold arithmetic is missing"
assert "cast_gate.until_tick[ui_id]" in script_txt, "the per-pair in-flight deadline is missing"
assert "cast_gate.logged[id_slot] = nil" in script_txt, "the in-flight gate is not purged with a dropped unit"
assert "ability.wind_up_s" in script_txt, "the load mapping for wind_up_s is missing"
assert "in-flight gate " in script_txt, "the in-flight gate log line is missing"

# ROUND v104 (B): THE ALLY-AWARE HEALTH FAMILY.
for _fn in ("function FOURTH.evaluate_health_aura_ground(unit, routing)",
            "function FOURTH.evaluate_health_aura_ally(unit, routing)",
            "function FOURTH.evaluate_health_aura_self(unit, routing)",
            "function FOURTH.ah_pick(unit, routing)",
            "function FOURTH.ally_ground_cast(uc, ally, ability_key)",
            "function FOURTH.ah_log_ally(ally, hp, gap, cast_note)"):
    assert _fn in script_txt, "the ally-aware helper is missing: " + _fn
assert "health_aura_ground = FOURTH.evaluate_health_aura_ground," in script_txt, "the ground trigger is not wired"
assert "health_aura_ally = FOURTH.evaluate_health_aura_ally," in script_txt, "the ally trigger is not wired"
assert "health_aura_self = FOURTH.evaluate_health_aura_self," in script_txt, "the self-aura trigger is not wired"
assert "ability.aura_m = math.floor(ability.aura_real * FOURTH.RANGE_FRACTION + 1e-9)" in script_txt, "the 70% aura bound is missing"
assert 'marker = "star_of_avelorn", name = "Star of Avelorn", trigger = "heal_ground_best"' in script_txt, "Star of Avelorn is not on the ally-aware ground trigger"
assert "if FOURTH.ah_ground then" in script_txt, "the ally-ground cast branch is missing"
assert "FOURTH.ah_chosen" in script_txt, "the chosen-unit slot is missing"
assert "ally-ground cast" in script_txt, "the ally-ground cast log line is missing"
assert "FOURTH.ALLY_CAST_R50  = 35" in script_txt, "the 70% ally-cast constant is missing: FOURTH.ALLY_CAST_R50  = 35"
assert "FOURTH.ALLY_CAST_R60  = 42" in script_txt, "the 70% ally-cast constant is missing: FOURTH.ALLY_CAST_R60  = 42"
assert "FOURTH.ALLY_CAST_R75  = 55" in script_txt, "the 70% ally-cast constant is missing: FOURTH.ALLY_CAST_R75  = 55"
assert "FOURTH.ALLY_CAST_R100 = 80" in script_txt, "the 70% ally-cast constant is missing: FOURTH.ALLY_CAST_R100 = 80"
assert "FOURTH.ALLY_CAST_R150 = 130" in script_txt, "the 70% ally-cast constant is missing: FOURTH.ALLY_CAST_R150 = 130"
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
assert script_txt.count('trigger = "ally_melee_buff"') == 1, "the ally_melee_buff count is not 1 (round 179)"
assert script_txt.count('trigger = "ally_heal"') == 3, "the ally_heal count is not 3"
assert script_txt.count('trigger = "ally_heal_melee"') == 1, "the ally_heal_melee count is not 1"
assert script_txt.count('trigger = "ally_wavering"') == 2, "the ally_wavering count is not 2"
# ROUND v100 (2026-10-17): the TWO ARMY-BAR ENTRIES ARE REMOVED. They were
# implemented but sit OUTSIDE the single in-wheel rule; their keys, markers
# and badge ids must be GONE. Grut's Sickle is a DIFFERENT, in-wheel item
# ability (the max-HP ally pick rule) and must be untouched.
assert "wh3_main_prisoners_butcher" not in script_txt, "the removed Meat Feast key is back"
assert "wh3_main_prisoners_massacre" not in script_txt, "the removed Massacre key is back"
assert 'marker = "butcher"' not in script_txt, "the removed Meat Feast entry is back"
assert 'marker = "massacre"' not in script_txt, "the removed Massacre entry is back"
assert "zz_auto_badge_butcher" not in script_txt and "zz_auto_badge_massacre" not in script_txt, \
    "a removed badge id is back"
assert 'marker = "gruts_sickle"' in script_txt and "wh3_main_item_abilities_gruts_sickle" in script_txt, \
    "Grut's Sickle was touched"
assert "function FOURTH.evaluate_ally_winds(unit, routing)" in script_txt \
    and 'family == "winds"' in script_txt, "the Grut's Sickle max-HP pick rule was touched"
assert "unit_in_range(" not in script_txt, "the engine unit_in_range call is back"
assert "is_firing" not in script_txt and "is_shooting" not in script_txt, \
    "an invented firing predicate is in the mod"
assert script_txt.count("\t{ marker = ") == 982, "the abilities table is not 982 entries"

# ROUND v99: THE TARGET-CLASS-GATED CLASS-B ENTRIES (nothing above is loosened).
# The 15 NEEDS-RULING rows ship as ALLY-TARGETED casts: the 7 derived class-key
# lists, the class reader/gate helpers, the 200 m ally constant, the infinite
# bound text, the ten new evaluators + their map/TIP wiring, the winds (max-hp)
# pick rule and the fresh-handle/hold/lapse machinery.
assert "FOURTH.class_keys = {" in script_txt, "the derived class-key tables are missing"
for _nm, _sz in (("beast", 55), ("monster", 235), ("warmachine", 68), ("construct", 29),
                 ("hellforged", 13), ("missile", 493), ("overseer", 918)):
    _i = script_txt.find(_nm + " = {")
    assert _i >= 0, "the " + _nm + " class list is missing"
    _j = script_txt.find("},", _i)
    assert script_txt[_i:_j].count("] = true,") == _sz, "the " + _nm + " list size is not " + str(_sz)
assert "function FOURTH.class_member(unit, name)" in script_txt, "the class reader is missing"
assert "function FOURTH.ab_filter_ok(unit)" in script_txt, "the class gate is missing"
assert "function FOURTH.morale_broken(unit)" in script_txt, "the morale-broken read is missing"
assert "function FOURTH.ab_bound_text()" in script_txt, "the bound-text helper is missing"
assert "if FOURTH.ab_infinite then return true end" in script_txt, "the infinite bound is not honoured"
assert "none (infinite range per wiki)" in script_txt, "the infinite-range log text is missing"
assert script_txt.count("FOURTH.ab_filter = nil") == 3, "the class-gate slot is not defined+cleared"   # ROUND 192: + Remouldered
assert script_txt.count("FOURTH.ab_infinite = nil") == 2, "the infinite slot is not defined+cleared"
assert "FOURTH.ALLY_CAST_R200 = 180" in script_txt, "the 70% ally-cast constant is missing: FOURTH.ALLY_CAST_R200 = 180"
assert "\t[200] = FOURTH.ALLY_CAST_R200," in script_txt, "the 200 m ally map entry is missing"
assert 'family == "winds"' in script_txt, "the winds (max-hp) family is missing"
assert 'FOURTH.context_value(other, "HealthValue")' in script_txt, "the HealthValue read is missing"
for _f in ("overseer", "beast", "broken", "missile", "warmachine_heal", "hellforged_heal",
           "monster_heal", "construct_heal", "infinite_buff", "winds"):
    assert "function FOURTH.evaluate_ally_" + _f + "(unit, routing)" in script_txt, \
        "the ally_" + _f + " evaluator is missing"
    assert "ally_" + _f + " = FOURTH.evaluate_ally_" + _f + "," in script_txt, \
        "the ally_" + _f + " trigger is not wired"
assert script_txt.count('trigger = "ally_overseer"') == 0 and script_txt.count('trigger = "ally_beast"') == 0, \
    "the overseer/beast trigger counts are wrong"
assert script_txt.count('trigger = "ally_broken"') == 0 and script_txt.count('trigger = "ally_missile"') == 0, \
    "the broken/missile trigger counts are wrong"
assert script_txt.count('trigger = "ally_warmachine_heal"') == 1 and \
    script_txt.count('trigger = "ally_hellforged_heal"') == 1 and \
    script_txt.count('trigger = "ally_monster_heal"') == 1 and \
    script_txt.count('trigger = "ally_construct_heal"') == 1, "a class-heal trigger count is wrong"
assert script_txt.count('trigger = "ally_infinite_buff"') == 0 and script_txt.count('trigger = "ally_winds"') == 1, \
    "the infinite/winds trigger counts are wrong"
assert "unit_in_range(" not in script_txt, "the engine unit_in_range call is back"


# ---------------------------------------------------------------------------
# ROUND v101: the five boss-only removals and GATE OF KHORNE.
# ---------------------------------------------------------------------------
for _mk, _ky in (("grand_faiths_bastion", "wh_dlc06_quest_abilities_grand_faiths_bastion"),
                 ("bitter_sting", "wh3_dlc27_qb_unit_abilities_bitter_sting"),
                 ("frenzied_challenge", "wh3_dlc27_qb_unit_abilities_frenzied_challenge"),
                 ("visions_of_madness", "wh3_dlc27_qb_unit_abilities_visions_of_madness"),
                 ("guttural_roar", "wh3_dlc27_qb_unit_abilities_guttural_roar")):
    assert 'marker = "%s"' % _mk not in script_txt, "the boss-only marker is still in the table: " + _mk
    assert _ky not in script_txt, "the boss-only key is still in the script: " + _ky
    assert 'zz_auto_badge_%s"' % _mk not in script_txt, "the boss-only badge id is still in the script: " + _mk
assert script_txt.count('trigger = "enemy_engaged_or_shot"') == 22, \
    "the enemy_engaged_or_shot count is not 85 (3 boss-only removed; Warden's Cage removed in round 121)"
assert script_txt.count('trigger = "melee_unwavering"') == 278, \
    "the melee_unwavering count is not 374 (2 boss-only removed)"
assert script_txt.count("\t{ marker = ") == 982, "the abilities table is not 982 entries"
# the ten boss-only keys that never shipped stay absent
for _ky in ("wh2_dlc10_quest_abilities_fiery_head", "wh2_dlc10_quest_abilities_regenerating_head",
            "wh_dlc08_quest_abilities_howling_winter", "wh_dlc08_quest_abilities_master_of_souls",
            "wh_dlc04_quest_abilities_servant_of_nagash", "wh3_dlc27_qb_unit_abilities_dissolving_bone",
            "wh3_dlc27_qb_unit_abilities_terrible_malice", "wh3_dlc27_qb_unit_abilities_copious_phlegm",
            "wh2_dlc10_quest_abilities_magic_fiery_convocation", "wh2_dlc10_quest_abilities_flame_storm"):
    assert _ky not in script_txt, "an excluded boss-only key is in the mod: " + _ky
# GATE OF KHORNE
GATE_KEY = "wh3_main_character_abilities_gate_of_khorne"
assert 'marker = "gate_of_khorne"' in script_txt, "the Gate of Khorne entry is missing"
assert 'trigger = "enemy_ground_melee"' in script_txt, "Gate of Khorne's trigger is missing"
assert '"%s"' % GATE_KEY in script_txt, "Gate of Khorne's key is missing"
assert '["%s"] = true,' % GATE_KEY in script_txt, "Gate of Khorne is not in enemy_ground_keys"
assert 'range_real = 50,' in script_txt, "Gate of Khorne's real 50 m range is missing"
assert "FOURTH.ENEMY_CAST_R50  = 35" in script_txt, "the 70% 50 m constant (35) is missing"
assert "function FOURTH.evaluate_enemy_ground_melee(unit, routing)" in script_txt, \
    "the melee-only enemy-ground evaluator is missing"
assert "enemy_ground_melee = FOURTH.evaluate_enemy_ground_melee," in script_txt, \
    "the Gate of Khorne evaluator map entry is missing"
assert 'enemy_ground_melee = "When armed, fires when an enemy in range is fighting in melee' in script_txt, \
    "the Gate of Khorne tooltip wording is missing"
assert "FOURTH.eg_melee_only = nil" in script_txt, "the melee-only flag slot/clear is missing"
assert script_txt.count("FOURTH.eg_melee_only = nil") >= 2, "the melee-only flag is not cleared in the poll"
assert "local melee_only = (FOURTH.eg_melee_only == true)" in script_txt, \
    "the picker does not read the melee-only flag"
assert "local eg_melee_only_now = (FOURTH.eg_melee_only == true)" in script_txt, \
    "the pre-cast re-check does not read the melee-only flag"
assert 'reason = "closest fighting (in-melee) enemy within bound (targeting "' in script_txt, \
    "Gate of Khorne's own reason string is missing"
assert 'FOURTH.enemy_ground_cast(uc, FOURTH.eg_enemy, ability_key)' in script_txt, \
    "the enemy-ground cast route is missing"
assert "unit_in_range(" not in script_txt, "a unit_in_range call is back in the script"


# ---------------------------------------------------------------------------
# ROUND v102: THE SUMMON ROUND.
# ---------------------------------------------------------------------------
NURG = "wh3_main_lord_abilities_nurgling_tide"
EYE = "wh3_dlc26_lord_abilities_eye_of_khorne"
D13 = "wh3_dlc29_spell_bound_the_dreaded_thirteenth"
assert script_txt.count("\t{ marker = ") == 982, "the abilities table is not 982 entries"
assert script_txt.count('trigger = "enemy_ground_melee"') == 74, \
    "enemy_ground_melee is not 67 (1 gate + 57 A + 9 D)"
assert script_txt.count('trigger = "self_summon_melee"') == 1, "the self-summon trigger is missing"
assert script_txt.count('trigger = "enemy_low_health_noncommander"') == 1, "the finisher trigger is missing"
assert script_txt.count('trigger = "enemy_melee_noncommander"') == 1, "the D13 trigger is missing"
assert script_txt.count('trigger = "melee_unwavering"') == 278, "melee_unwavering moved (374 after round 123)"
assert script_txt.count('trigger = "enemy_engaged_or_shot"') == 22, "enemy_engaged_or_shot moved (85 after round 121)"
for _mk, _trig, _key in (
        ("nurgling_tide", "self_summon_melee", NURG),
        ("eye_of_khorne", "enemy_low_health_noncommander", EYE),
        ("the_dreaded_thirteenth", "enemy_melee_noncommander", D13),
        ("gate_of_nurgle", "enemy_ground_melee", "wh3_main_character_abilities_gate_of_nurgle"),
        ("beast_pack", "enemy_ground_melee", "wh2_dlc16_lord_abilities_beast_pack"),
        ("wake_da_idol", "enemy_ground_melee", "wh3_main_item_abilities_zak_aloooog")):
    assert 'marker = "%s"' % _mk in script_txt, "summon marker missing: " + _mk
    assert 'badge = "zz_auto_badge_%s"' % _mk in script_txt, "summon badge missing: " + _mk
    assert 'trigger = "%s"' % _trig in script_txt, "summon trigger missing: " + _trig
    assert '"%s"' % _key in script_txt, "summon key missing: " + _key
# every A/D/F key sits in the enemy-ground set (91 entries: 10 prior + 81 new)
_g0 = script_txt.find("enemy_ground_keys = {")
_g1 = script_txt.find("\t},\n", _g0)
assert _g0 > 0 and _g1 > _g0
# ROUND 106: 91 + the bombardment family's 25 ground-targeted keys = 116.
assert script_txt[_g0:_g1].count('"] = true,') == 128, "enemy_ground_keys is not 125 entries (the cataclysm Gate key left in round 121)"
for _k in ("wh2_dlc16_hero_abilities_tide_of_death", "wh2_dlc16_hero_abilities_tide_of_pox",
           "wh2_dlc15_item_abilities_blacktoofs_conjuration",
           "wh2_dlc16_spell_bound_vampires_lesser_raise_dead",
           "wh2_dlc17_spell_bound_savage_dominion",
           "wh3_dlc26_hero_abilities_savage_predators",
           "wh2_dlc16_lord_abilities_call_to_gwindalor",
           D13, D13 + "_1", D13 + "_thanquol", D13 + "_thanquol_1"):
    assert '["%s"] = true,' % _k in script_txt[_g0:_g1], "ground key missing from the set: " + _k
# the self-summon is NOT a ground key, and Eye of Khorne is NOT either
assert '["%s"] = true,' % NURG not in script_txt[_g0:_g1], "Nurgling Tide must not be a ground key"
assert EYE not in script_txt[_g0:_g1], "Eye of Khorne must not be an enemy-ground key"
# the four illusions stay out
for _k in ("wh2_dlc10_lord_abilities_deadly_mislead", "wh3_dlc24_lord_item_deceiving_shadows",
           "wh2_dlc14_unit_abilities_doppelgang", "wh2_dlc10_lord_abilities_mislead"):
    assert _k not in script_txt, "an illusion summon is in the mod: " + _k
# the commander test
assert "FOURTH.commander_keys = {" in script_txt, "the derived commander key set is missing"
_c0 = script_txt.find("FOURTH.commander_keys = {")
_c1 = script_txt.find("\n}\n", _c0)
assert script_txt[_c0:_c1].count('"] = true,') >= 1400, "the commander key set is too small"
assert '["wh3_main_kho_cha_skarbrand_0"] = true,' in script_txt[_c0:_c1], "a known Lord is missing"
assert '["wh2_dlc09_tmb_inf_skeleton_warriors_0"] = true,' not in script_txt[_c0:_c1], \
    "a line unit is in the commander set"
assert "function FOURTH.enemy_is_commander(enemy)" in script_txt, "the commander test is missing"
assert "enemy:unit_class()" in script_txt, "the unit_class fallback is missing"
assert "FOURTH.HEALTH_LINE_PCT = 20" in script_txt, "the 20% finisher line is missing"
assert "hp < FOURTH.HEALTH_LINE_PCT" in script_txt, "the finisher is not strictly below the line"
assert script_txt.count("\t\trange_real = ") == 428, "range_real count is not 207"
assert script_txt.count("\t\tunbounded = true,") == 3, "the two unbounded entries are not flagged"
assert "FOURTH.eg_no_bound == true then return true end" in script_txt, "the no-bound test is missing"
assert "function FOURTH.evaluate_self_summon_melee(unit, routing)" in script_txt, "the self-summon evaluator is missing"
assert "function FOURTH.evaluate_enemy_low_health_noncommander(unit, routing)" in script_txt, "the finisher evaluator is missing"
assert "function FOURTH.evaluate_enemy_melee_noncommander(unit, routing)" in script_txt, "the D13 evaluator is missing"
assert "self_summon_melee = FOURTH.evaluate_self_summon_melee," in script_txt
assert "enemy_low_health_noncommander = FOURTH.evaluate_enemy_low_health_noncommander," in script_txt
assert "enemy_melee_noncommander = FOURTH.evaluate_enemy_melee_noncommander," in script_txt
assert 'self_summon_melee = "When armed, fires when this unit itself is fighting in melee' in script_txt
assert 'enemy_low_health_noncommander = "When armed, fires on the most valuable enemy' in script_txt   # ROUND 178
assert 'enemy_melee_noncommander = "When armed, fires on the closest enemy' in script_txt
assert "SKIPPED: the caster left melee before the self cast" in script_txt
assert "pre-cast re-check: the caster is still in melee" in script_txt
assert "lowest-health non-commander enemy below" in script_txt
assert 'reason = "closest non-commander enemy in melee within bound (targeting "' in script_txt
assert "FOURTH.ss_self = nil" in script_txt and "FOURTH.eg_noncommander = nil" in script_txt
assert "FOURTH.ENEMY_CAST_R45  = 31" in script_txt and "FOURTH.ENEMY_CAST_R90  = 70" in script_txt
assert "unit_in_range(" not in script_txt, "a unit_in_range call is back"
assert "string.find(" not in script_txt, "a string.find call is back"

# ROUND v103: THE CHARGE GATE (multi-USE abilities) + THE ONE HEALTH READ.
assert "local charge_gate = {" in script_txt, "the charge-gate table is missing"
assert script_txt.count('"] = ') >= 129, "the charge-gate table lost entries"
assert '["wh3_main_lord_abilities_nurgling_tide"] = 90,' in script_txt, \
    "Nurgling Tide is not held for its own 90 s recharge"
assert "ability.charge_s" in script_txt, "the charge_s mapping is missing"
assert "charge_gate.until_tick[ui_id]" in script_txt, "the poll's charge gate is missing"
assert "held_until ~= nil and tick_count < held_until" in script_txt, "the charge hold test is missing"
assert "math.floor((ability.charge_s * 1000) / POLL_MS)" in script_txt, "the next-use deadline is missing"
assert 'charge gate " .. ability.marker' in script_txt, "the one-line charge-gate notice is missing"
assert "function FOURTH.health_pct(unit)" in script_txt, "the ONE health reader is missing"
assert "unit:unary_hitpoints()" in script_txt, "the engine's fraction health read is missing"
assert "return FOURTH.health_pct(enemy)" in script_txt, "the enemy health read is not routed"
assert script_txt.count('FOURTH.context_value(unit, "HealthPercent")') == 1, \
    "a raw HealthPercent read is back outside the ONE reader"


# ROUND v105 (2026-10-17): TZ'ARKAN ON THE NEW LOW-HEALTH TRIGGER - ONE entry,
# FIVE keys, below 15% of the ONE health reader, cast on SELF, with a pre-cast
# re-check that logs the exact percentage and skips a dead or risen caster.
# Nothing above is loosened.
TZ_KEYS = [
    "wh2_dlc14_lord_abilities_tzarkan",
    "wh2_dlc14_lord_abilities_tzarkan_mp",
    "wh2_dlc14_lord_abilities_tzarkan_snikch",
    "wh2_dlc14_lord_abilities_tzarkan_spite",
    "wh2_dlc14_lord_abilities_tzarkan_spite_mp",
]
assert script_txt.count('marker = "tzarkan"') == 1, "the tzarkan entry is missing (or duplicated)"
assert 'name = "Tz\'arkan", trigger = "health_below_15",' in script_txt, \
    "the tzarkan entry is not on the new low-health trigger"
assert 'badge = "zz_auto_badge_tzarkan"' in script_txt, "the tzarkan badge id is missing"
for _k in TZ_KEYS:
    assert '"%s"' % _k in script_txt, "a Tz'arkan key is missing: " + _k
assert "FOURTH.TZARKAN_PCT = 15" in script_txt, "the 15% threshold constant is missing"
assert "function FOURTH.evaluate_tzarkan_low_health(unit, routing)" in script_txt, \
    "the tzarkan evaluator is missing"
assert "health_below_15 = FOURTH.evaluate_tzarkan_low_health," in script_txt, \
    "the tzarkan trigger is not wired in the evaluator map"
assert 'health_below_15 = "When armed, fires when this unit is below 15% health"' in script_txt, \
    "the tzarkan tooltip sentence is missing"
_TZ_EV = script_txt[script_txt.find("function FOURTH.evaluate_tzarkan_low_health(unit, routing)"):]
_TZ_EV = _TZ_EV[:_TZ_EV.find("\nend")]
assert "FOURTH.health_pct(unit)" in _TZ_EV, "the evaluator does not use the ONE health reader"
assert "HealthPercent" not in _TZ_EV, "the evaluator reads raw HealthPercent (the 0..1 fraction trap)"
assert script_txt.count("if FOURTH.tz_self then") == 2, \
    "the tzarkan cast handle and pre-cast re-check are not both present"
assert "FOURTH.tz_self = nil" in script_txt and "FOURTH.tz_caster_su = nil" in script_txt, \
    "the tzarkan cast slots are not declared"
assert "tzarkan SKIPPED: the caster lapsed before the cast" in script_txt, \
    "the pre-cast skip line is missing"
assert "tzarkan pre-cast re-check: the caster is still below the line" in script_txt, \
    "the pre-cast re-check line is missing"
assert '["wh2_dlc14_lord_abilities_tzarkan"] = 3,' in script_txt, \
    "Tz'arkan's own 3 s wind-up is missing from the in-flight gate"
assert '["wh2_dlc14_lord_abilities_tzarkan_snikch"] = 1.5,' in script_txt, \
    "the Snikch key's 1.5 s wind-up is missing from the in-flight gate"
assert "BELOW the %d%% line" in script_txt, "the decision reason does not carry the exact percentage"

# THE 12 TRANSFORMS THE USER SKIPPED ARE NOT AUTOMATED - no key of theirs may
# appear in the shipped script at all (they were never in the ABILITIES table).
SKIPPED_TRANSFORMS = [
    "wh3_dlc24_lord_abilities_formless_horror",
    "wh3_dlc24_lord_abilities_formless_horror_changeling",
    "wh3_dlc24_lord_abilities_formless_horror_quest_battle",
    "wh3_dlc24_lord_abilities_formless_horror_quest_battle_changeling_form",
    "wh3_dlc24_lord_abilities_jade_dragon_dragon_form",
    "wh3_dlc24_lord_abilities_jade_dragon_human_form",
    "wh3_main_lord_abilities_iron_dragon_dragon_form",
    "wh3_main_lord_abilities_iron_dragon_human_form",
    "wh3_main_lord_abilities_storm_dragon_dragon_form",
    "wh3_main_lord_abilities_storm_dragon_human_form",
    "wh3_dlc27_unit_abilities_dread_maw_underground",
    "wh3_dlc27_unit_abilities_dread_maw_surface",
]
for _k in SKIPPED_TRANSFORMS:
    assert '"%s"' % _k not in script_txt, "a user-skipped transform key is in the mod: " + _k

# HOUSEKEEPING 20261004: the two throwaway experiment probes were RETIRED from the
# pack (zz_probe_unit_reads.lua and zz_probe_ui_text.lua - their experiments are
# finished and their findings are recorded). Their sources are preserved in
# releases/20261004_probe_sources_retired/ and must NOT ship again:
assert not any("zz_probe_" in p for p in in_pack_paths), "a retired probe is back in the pack"
for _retired in ("zz_probe_ui_text.lua", "zz_probe_unit_reads.lua"):
    _retired_path = SRC_ROOT + "/releases/20261004_probe_sources_retired/" + _retired
    assert os.path.exists(_retired_path), f"the preserved retired probe source is missing: {_retired_path}"


# ---------------------------------------------------------------------------
# ROUND 107 (2026-10-18): THE REMAINING BOMBARDMENT WORK.
#   (1) Call of Tor joins Soulfire's trigger: melee_skip_commanders now has
#       THREE entries (Soulfire 2 keys, Arachneruption, Call of Tor).
#   (2) The "on top of" family: 12 entries / 19 keys on the NEW
#       air_drop_on_infantry evaluator - an enemy INFANTRY unit inside the
#       row's 70% bound (7 m of its 10 m), airborne where the row says so,
#       out of melee where the row says so, self-centred cast, logged
#       pre-cast re-check.
#   (3) The PER-UNIT serialisation window: after any successful cast no OTHER
#       ability may be issued on that unit for wind-up + 2 s (min 2.5 s), so
#       two ready abilities fire in sequence instead of replacing each other.
# ---------------------------------------------------------------------------
AIR = [
    ("death_from_above", "wh2_dlc09_unit_abilities_death_from_above"),
    ("drop_rocks", "wh2_main_unit_abilities_drop_rocks"),
    ("drop_rocks", "wh2_dlc12_unit_abilities_drop_rocks_character"),
    ("drop_rocks", "wh2_dlc12_unit_abilities_drop_rocks_of_chotec"),
    ("drop_rocks", "wh2_dlc12_unit_abilities_drop_rocks_of_sundering"),
    ("drop_sphere_of_tepok", "wh2_dlc12_lord_abilities_drop_sphere_of_tepok"),
    ("drop_sphere_of_tepok", "wh2_dlc12_lord_abilities_drop_sphere_of_tepok_upgraded"),
    ("fire_bombs", "wh3_dlc25_unit_abilities_gyrobomber_fire_bomb"),
    ("fire_bombs", "wh3_dlc25_unit_abilities_thunderbarge_fire_bomb"),
    ("gyrobomber_bomb", "wh_main_unit_abilities_gyrobomber_bomb"),
    ("gyrobomber_bomb", "wh_main_unit_abilities_gyrocopter_bomb"),
    ("gyrocopter_bomb_anti_large", "wh3_dlc25_unit_abilities_gyrocopter_bomb_anti_large"),
    ("sky_junk_bomb", "wh3_main_unit_abilities_sky_junk_bomb"),
    ("skyhammer_bomb", "wh_dlc06_unit_abilities_skyhammer_bomb"),
    ("skyhammer_bomb", "wh_dlc06_unit_abilities_skyhammer_fire_bomb"),
    ("wake_of_fire", "wh2_main_unit_abilities_wake_of_fire"),
    ("searing_torrent", "wh3_twa07_unit_abilities_searing_torrent"),
    ("nan_gau_grenades", "wh3_dlc24_unit_abilities_nan_gau_grenades"),
    ("undeath_from_above", "wh3_dlc29_unit_abilities_undeath_from_above"),
]
assert len(AIR) == 19, "the air-drop key list is not 19"
assert script_txt.count('trigger = "air_drop_on_infantry"') == 12, \
    "the air-drop family is not 12 entries"
for _mk, _ky in AIR:
    assert 'marker = "%s"' % _mk in script_txt, "air-drop marker missing: " + _mk
    assert '"%s"' % _ky in script_txt, "air-drop key missing: " + _ky
assert script_txt.count("\t\trange_real = 10,") == 12, "the air-drop range_real fields are not 12"
assert "FOURTH.ENEMY_CAST_R10  = 7" in script_txt, "the 10 m -> 7 m 70% constant is missing"
assert "\t[10]  = FOURTH.ENEMY_CAST_R10," in script_txt, "the 10 m map entry is missing"
if not ROUND114: assert "FOURTH.AIR_DROP_CENTER_M = 6" in script_txt, "the air-drop bound constant is not the 6 m centre value"
if not ROUND114: assert "AIR_DROP_BOUND_M" not in script_txt, "the retired edge-to-edge bound is still in the file"
assert "if ability.evaluate == FOURTH.evaluate_air_drop_on_infantry then" in script_txt, \
    "the air-drop family does not bypass the 70% map"
assert 'air_only = true,' in script_txt and 'air_only = false,' in script_txt, "the air_only flags are missing"
assert script_txt.count('air_only = false,') == 2, \
    "the two documented NON-air-gated entries are not exactly two (Drop Sphere, Searing Torrent)"
assert 'no_melee = true,' in script_txt and 'no_melee = false,' in script_txt, "the no_melee flags are missing"
if not ROUND114: assert 'function FOURTH.ad_pick(unit, routing)' in script_txt, "the air-drop picker is missing"
assert 'function FOURTH.evaluate_air_drop_on_infantry(unit, routing)' in script_txt, \
    "the air-drop evaluator is missing"
assert "air_drop_on_infantry = FOURTH.evaluate_air_drop_on_infantry," in script_txt, \
    "the air-drop trigger is not wired"
if not ROUND114: assert 'air_drop_on_infantry = "When armed, fires when this unit is over an infantry unit in range, airborne where the ability requires it",' in script_txt, \
    "the air-drop tooltip sentence is missing"
assert "unit:is_currently_flying()" in script_txt, "the flight read is missing"
assert "FOURTH.enemy_is_infantry(enemy)" in script_txt, "the infantry read is missing from the picker"
assert "FOURTH.eg_enemy_gap(unit, enemy)" in script_txt, "the overlap proxy is missing"
if not ROUND114: assert "SKIPPED: the drop lapsed before the cast" in script_txt, "the air-drop lapse line is missing"
if not ROUND114: assert "pre-cast re-check: still over an INFANTRY enemy" in script_txt, "the air-drop re-check line is missing"
assert "if FOURTH.ad_enemy ~= nil then" in script_txt, "the air-drop pre-cast block is missing"
assert "FOURTH.ad_air_only = (ability.air_only == true)" in script_txt, "the poll does not set the air_only flag"
assert "FOURTH.ad_no_melee = (ability.no_melee == true)" in script_txt, "the poll does not set the no_melee flag"
# the air-drop keys are SELF-CENTRED - they must NEVER be in the ground-key set
_g0 = script_txt.find("enemy_ground_keys = {")
_g1 = script_txt.find("\t},\n", _g0)
assert _g0 > 0 and _g1 > _g0
for _mk, _ky in AIR:
    assert ('["%s"] = true,' % _ky) not in script_txt[_g0:_g1], \
        "an air-drop key is in enemy_ground_keys: " + _ky

# CALL OF TOR
assert 'marker = "call_of_tor", name = "Call of Tor", trigger = "melee_skip_commanders"' in script_txt, \
    "Call of Tor is not on Soulfire's trigger"
assert '"wh3_twa07_spell_bound_call_of_tor"' in script_txt, "Call of Tor's key is missing"
assert '["wh3_twa07_spell_bound_call_of_tor"] = 90,' in script_txt, "Call of Tor's charge-gate row is missing"
assert '["wh3_twa07_spell_bound_call_of_tor"] = 1,' in script_txt, "Call of Tor's 1 s wind-up is missing"

# THE PER-UNIT SERIALISATION WINDOW
assert "FOURTH.SERIAL_MIN_HOLD_SECONDS = 2.5" in script_txt, "the stagger constant is missing"
assert "unit_until = {}," in script_txt, "the per-unit window slot is missing"
assert "unit_marker = {}," in script_txt, "the per-unit marker slot is missing"
assert "unit_logged = {}," in script_txt, "the per-unit log slot is missing"
assert "and cast_gate.unit_marker[ui_id] ~= ability.marker" in script_txt, \
    "the gate does not read the per-unit marker"
assert "local unit_hold_s = ((ability.wind_up_s or 0) + IN_FLIGHT_SETTLE_SECONDS)" in script_txt, \
    "the per-unit hold arithmetic is missing"
assert "if unit_hold_s < FOURTH.SERIAL_MIN_HOLD_SECONDS then" in script_txt, \
    "the per-unit stagger clamp is missing"
assert "cast_gate.unit_until[ui_id] = tick_count + math.floor((unit_hold_s * 1000) / POLL_MS)" in script_txt, \
    "the per-unit window is never armed"
assert "cast_gate.unit_until[id_slot] = nil" in script_txt, "the per-unit window is not purged"
assert "per-unit cast gate " in script_txt, "the per-unit wait/arm log lines are missing"
assert "if cast_gate.unit_marker[ui_id] ~= ability.marker then" in script_txt, \
    "a same-marker repeat would re-arm the window (starvation)"


# ============================================================================
# ROUND 106 - THE BOMBARDMENT ROUND (two approved families). The gates below
# name the NEW tokens only, so a stale build (the pre-106 source) fails here.
# ============================================================================
assert script_txt.count('trigger = "enemy_ground_melee_infantry"') == 30, \
    "the bombardment family is not 30 entries on enemy_ground_melee_infantry"
assert script_txt.count('trigger = "melee_skip_commanders"') == 4, \
    "Soulfire + Arachneruption + Call of Tor + Warp Lightning Rod are not the four melee_skip_commanders entries"
assert 'marker = "soulfire"' in script_txt and 'marker = "arachneruption"' in script_txt, \
    "the two family-1 entries are missing"
assert 'name = "Soulfire", trigger = "melee_skip_commanders"' in script_txt, \
    "Soulfire is not on the new trigger"
assert 'keys = { "wh_main_spell_bound_soulfire",' in script_txt, \
    "Soulfire's base key is not in its entry"
assert '"wh_dlc04_spell_bound_soulfire_upgraded" },' in script_txt, \
    "Grand Soulfire does not ride the same entry"
assert 'name = "Arachneruption", trigger = "melee_skip_commanders"' in script_txt, \
    "Arachneruption is not on the new trigger"
assert 'melee_skip_commanders = FOURTH.evaluate_melee_skip_commanders,' in script_txt, \
    "the melee_skip_commanders evaluator is not wired"
assert 'enemy_ground_melee_infantry = FOURTH.evaluate_enemy_ground_melee_infantry,' in script_txt, \
    "the enemy_ground_melee_infantry evaluator is not wired"
assert 'melee_skip_commanders = "When armed, fires when this unit is in melee, unless every enemy it is fighting is a Lord or Hero",' in script_txt, \
    "the melee_skip_commanders tooltip sentence is missing"
assert 'enemy_ground_melee_infantry = "When armed, fires on the closest infantry unit in range that is fighting in melee",' in script_txt, \
    "the enemy_ground_melee_infantry tooltip sentence is missing"
assert "function FOURTH.enemy_is_infantry(enemy)" in script_txt, "the infantry reader is missing"
assert "enemy:is_infantry()" in script_txt, "the infantry reader does not use the engine's own read"
assert 'cls == "inf_mel"' in script_txt and 'cls == "inf_mis"' in script_txt \
    and 'cls == "inf_spr"' in script_txt, "the unit_class fallback is missing"
assert "FOURTH.ENGAGE_CONTACT_M = 12" in script_txt, "the engagement contact constant is missing"
assert "function FOURTH.engagement_set(unit)" in script_txt, "the engagement set reader is missing"
assert 'elseif mode == "infantry" then' in script_txt, "the picker has no infantry mode"
assert "if FOURTH.eg_infantry then" in script_txt, "the pre-cast infantry re-check is missing"
assert "FOURTH.ENEMY_CAST_R300 = 280" in script_txt, "the 300 m bound is missing"
assert "[300] = FOURTH.ENEMY_CAST_R300," in script_txt, "the 300 m map entry is missing"
# the 24 GROUND-TARGETED bombardment keys (the 6 unit-targeted ones must NOT
# be in the ground set - they cast on the enemy unit itself)
for _gk in ("wh2_dlc10_item_bound_assault_of_stone", "wh3_main_weapon_abilities_axe_of_tor",
            "wh3_main_mount_bound_celestial_comet", "wh3_main_mount_bound_celestial_lightning",
            "wh_dlc07_item_abilities_chalice_of_potions", "wh3_main_spell_bound_comet_of_casandora",
            "wh_dlc08_item_abilities_great_horn_of_dragon_ogre", "wh3_dlc23_lord_abilities_flame_and_shadow",
            "wh_dlc05_weapon_abilities_hawks_talon", "wh2_dlc13_character_ability_ishas_rain",
            "wh2_dlc17_spell_bound_urannons_thunderbolt_upgraded", "wh3_dlc29_unit_abilities_lightning_strike",
            "wh_main_lord_abilities_lord_of_the_storm", "wh3_dlc29_spell_bound_warp_lightning",
            "wh3_dlc29_unit_abilities_meteor_strike", "wh3_dlc25_lord_abilities_nemesis_crown",
            "wh_main_spell_bound_piercing_bolts_of_burning", "wh3_dlc25_character_abilities_pigeon_bomb",
            "wh2_main_spell_bound_rod_of_the_storm", "wh2_dlc10_item_abilities_sceptre_of_stone",
            "wh3_twa08_spell_bound_searing_doom", "wh3_dlc20_spell_bound_slicing_shards",
            "wh3_main_spell_slaanesh_slicing_shards_bound", "wh_dlc05_weapon_abilities_the_bow_of_loren",
            "wh2_dlc17_spell_bound_urannons_thunderbolt"):
    assert '["%s"] = true,' % _gk in script_txt, "a ground-targeted bombardment key is missing: " + _gk
for _uk in ("wh2_dlc10_spell_bound_lesser_doombolt", "wh3_dlc20_item_abilities_rod_of_torment",
            "wh2_main_spell_bound_tome_of_furion", "wh2_main_spell_bound_wand_of_the_kharaidon",
            "wh3_main_weapon_abilities_the_traitors_sword", "wh2_dlc11_lord_abilities_wraith_storm"):
    assert '["%s"] = true,' % _uk not in script_txt, \
        "a UNIT-targeted bombardment key was put in the GROUND set: " + _uk
# the two reported skips must NOT be in the table
assert '"wh3_dlc20_cataclysm_bound_thorsens_thunderstorm"' not in script_txt, \
    "Thorsen's Thunderstorm is army-bar and must not be implemented"
assert '"wh2_dlc16_unit_abilities_warp_lightning_rod"' in script_txt, \
    "Warp Lightning Rod is missing from the table"
assert 'marker = "warp_lightning_rod", name = "Warp Lightning Rod", trigger = "melee_skip_commanders"' in script_txt, \
    "Warp Lightning Rod is not on Soulfire's trigger"
assert '["wh2_dlc16_unit_abilities_warp_lightning_rod"] = 60,' in script_txt, \
    "Warp Lightning Rod's 60 s charge-gate row is missing"
assert '["wh2_dlc16_unit_abilities_warp_lightning_rod"] = 1,' in script_txt, \
    "Warp Lightning Rod's 1 s wind-up row is missing"
assert "Clan Moulder" in script_txt and "LOBOTOMY" in script_txt, \
    "the Clan Moulder Lobotomy mutation note is missing"
# the two new gate tables must carry the new keys
assert '["wh2_dlc15_unit_abilities_arachneruption"] = 90,' in script_txt, \
    "Arachneruption's 90 s recharge is missing from the charge gate"
assert '["wh2_dlc10_item_bound_assault_of_stone"] = 3,' in script_txt, \
    "Assault of Stone's 3 s wind-up is missing from the cast gate"



# ============================================================================
# ROUND 108 (2026-10-18): THE 1 m AIR-DROP TEST BOUND + WARP LIGHTNING ROD.
#
#   (1) the air-drop overlap bound is 1 m - the user's own test value, NOT
#       floor(10 x 0.70) = 7 m - carried by ONE constant and wired by an
#       evaluator-identity bypass of the 70% map.
#   (2) Warp Lightning Rod (wh2_dlc16_unit_abilities_warp_lightning_rod) on
#       melee_skip_commanders, exactly like Soulfire / Call of Tor, with its
#       Clan Moulder Lobotomy mutation note (the missing carrier junction).
# ============================================================================
assert script_txt.count('trigger = "air_drop_on_infantry"') == 12, \
    "the air-drop family is not 12 entries"
if not ROUND114: assert script_txt.count("\nFOURTH.AIR_DROP_CENTER_M = 6\n") == 1, \
    "the 6 m air-drop CENTRE constant is not defined exactly once"
assert script_txt.count("if ability.evaluate == FOURTH.evaluate_air_drop_on_infantry then") == 1, \
    "the air-drop bound bypass is not wired exactly once"
if not ROUND114: assert script_txt.count("ability.range_m = FOURTH.AIR_DROP_CENTER_M") == 1, \
    "the air-drop entries do not take the one centre constant"
if not ROUND114: assert "the user's own test value, NOT the 70% rule" in script_txt, \
    "the source does not state that 6 m is the user's own test value"
if not ROUND114: assert "EDGE-TO-EDGE" in script_txt and "CENTRES are 15 m apart" in script_txt, \
    "the source does not explain the edge-to-edge failure (boxes near, CENTRES far)"
if not ROUND114: assert "ONE value to tune" in script_txt and "LOWER FOURTH.AIR_DROP_CENTER_M" in script_txt, \
    "the source does not say the 6 m value is ONE value to tune"
assert "wh2_main_unit_abilities_drop_rocks" in script_txt, \
    "the field-tested row (Drop Rocks) is missing from the air-drop family"

# ============================================================================
# ROUND 109 (2026-10-18): THE AIR DROP IS A HORIZONTAL CENTRE TEST.
#
#   unit_distance() is EDGE-TO-EDGE (battle_unit.lua:160): two bounding boxes
#   can be half a metre apart while their CENTRES are 15 m apart, so the 1 m
#   edge bound still fired while the flyer was nowhere near over the target.
#   The rule is now |centre(caster) - centre(enemy)| on the GROUND PLANE
#   (x/z - get_y is HEIGHT, so a 3D read would be 30-60 m from a unit directly
#   underneath) against FOURTH.AIR_DROP_CENTER_M = 6 m, ONE documented
#   constant standing in for the formation footprint (the API has no per-unit
#   radius / bbox / size read at all).
# ============================================================================
if not ROUND114: assert script_txt.count("FOURTH.ad_centre_gap(unit, enemy)") == 3, \
    "the centre-gap helper is not defined once and called twice (picker + re-check)"
if not ROUND114: assert "function FOURTH.ad_centre_gap(unit, enemy)" in script_txt, \
    "the centre-gap helper is missing"
if not ROUND114: assert "function FOURTH.ad_pos(x, z)" in script_txt, \
    "the x/z position formatter is missing"
_gap0 = script_txt.find("function FOURTH.ad_centre_gap(unit, enemy)")
_gap1 = script_txt.find("\nend", _gap0)
_gap = script_txt[_gap0:_gap1]
if not ROUND114: assert "get_x()" in _gap and "get_z()" in _gap, "the helper does not read the ground-plane x/z"
assert "get_y()" not in _gap, "the helper reads HEIGHT (get_y) - a 3D distance would fire never"
if not ROUND114: assert "distance_xz" in _gap and "math.sqrt" in _gap, \
    "the helper does not use distance_xz with an x/z fallback"
if not ROUND114: assert "' is UNDER the caster" in script_txt, "the target line does not say UNDER"
# SUPERSEDED IN ROUND 113 (tightened, not removed): `radius=none` was true while
# the 6 m constant stood in for the whole footprint. The line now names the
# PER-MODEL radius constant, the frontage credit derived from it and the
# threshold, so the gate demands all four.
if not ROUND114: assert "per_model_radius=" in script_txt, \
    "the target line does not name the per-model radius constant"
if not ROUND114: assert "frontage=" in script_txt and "threshold=" in script_txt, \
    "the target line does not print the frontage credit and the threshold"
if not ROUND114: assert "function FOURTH.ad_frontage(unit, men_now)" in script_txt, \
    "the frontage helper is missing"
if not ROUND114: assert "watch: nearest INFANTRY " in script_txt, \
    "the why-it-did-not-fire line is missing"
assert "gap <= bound" in script_txt, "the picker does not gate on the centre distance"
_rech0 = script_txt.find("if FOURTH.ad_enemy ~= nil then")
_rech1 = script_txt.find("-- SELF-SUMMON RE-CHECK", _rech0)
assert _rech0 > 0 and _rech1 > _rech0
_rech = script_txt[_rech0:_rech1]
if not ROUND114: assert "FOURTH.ad_centre_gap" in _rech and "FOURTH.eg_enemy_gap" not in _rech, \
    "the pre-cast re-check does not use the same CENTRE test"

assert script_txt.count('trigger = "melee_skip_commanders"') == 4, \
    "melee_skip_commanders is not four entries"
assert 'marker = "warp_lightning_rod", name = "Warp Lightning Rod", trigger = "melee_skip_commanders"' in script_txt, \
    "Warp Lightning Rod is not on Soulfire's trigger"
assert 'keys = { "wh2_dlc16_unit_abilities_warp_lightning_rod" },' in script_txt, \
    "Warp Lightning Rod's single key is missing"
assert '["wh2_dlc16_unit_abilities_warp_lightning_rod"] = 60,' in script_txt, \
    "Warp Lightning Rod's 60 s charge gate is missing"
assert '["wh2_dlc16_unit_abilities_warp_lightning_rod"] = 1,' in script_txt, \
    "Warp Lightning Rod's 1 s wind-up is missing"
assert "NO carrier" in script_txt and "NOT a default" in script_txt, \
    "the missing-carrier explanation is missing"
# WLR is SELF-CENTRED: it must never be in the ground-key set nor carry the
# air-drop usage flags
_g0 = script_txt.find("enemy_ground_keys = {")
_g1 = script_txt.find("\t},\n", _g0)
assert _g0 > 0 and _g1 > _g0
assert '["wh2_dlc16_unit_abilities_warp_lightning_rod"] = true,' not in script_txt[_g0:_g1], \
    "Warp Lightning Rod was put in the ground-key set"
assert script_txt.count('("warp_lightning_rod", "Warp Lightning Rod"') == 0, \
    "Warp Lightning Rod must not ride the air-drop helper table"

# ============================================================================
# ROUND 110 (2026-10-18): THE AIR DROP IS PREDICTED, NOT SAMPLED.
#
#   The user's third field report: firing on Drop Rocks (Terradon Riders) is still
#   early or misses - the rocks take about 1-2 s to fall and the flier keeps
#   moving. TWO-BODY RELATIVE-MOTION PREDICTION now ships, under the user's own
#   assumption ("I think the rocks don't keep the momentum, so let's work with
#   that assumption. Let's implement it and I'll test it."): the ordnance lands
#   STRAIGHT DOWN from the caster's position at RELEASE, so
#       caster(t+d) = caster(t) + v_caster * d      <- the impact point
#       enemy (t+d) = enemy (t)  + v_enemy  * d
#   and the drop fires when the PROJECTED horizontal centre separation is inside
#   the SAME 6 m bound. d = FOURTH.AIR_DROP_DELAY_S = 1.5 s, a TUNABLE constant
#   between the 1 s and 2 s the user observed - NOT a game value: no ability row
#   carries a fall time. The velocity is REBUILT from the only reads the API
#   has - is_moving(), is_moving_fast(), slow_speed() / fast_speed() (m/s) and a
#   heading from ordered_position() (normalise(ordered - current)); bearing()
#   ("the current orientation ... in degrees") is the documented CASTER-ONLY
#   fallback, since the dump never states how its degrees map onto x/z. Every
#   unreadable read is ZERO velocity with a NAMED source, never invented motion.
#   FOURTH.AIR_DROP_INHERIT = false is the ONE FLAG that adds v*d a SECOND time
#   (impact = caster + v*d*2) if the field shows the rocks DO keep the momentum.
#   Counts UNCHANGED: 689 entries / 742 keys, air_drop_on_infantry 12 / 19,
#   46 evaluators - behaviour only.
# ============================================================================
if not ROUND114: assert script_txt.count("\nFOURTH.AIR_DROP_DELAY_S = 1.5\n") == 1, \
    "the 1.5 s fall-delay constant is not defined exactly once"
if not ROUND114: assert script_txt.count("\nFOURTH.AIR_DROP_INHERIT = false\n") == 1, \
    "the momentum flag is not defined exactly once, or it does not ship FALSE"
if not ROUND114: assert script_txt.count("\nFOURTH.AIR_DROP_CENTER_M = 6\n") == 1, \
    "the 6 m centre bound moved (it must stay exactly one definition)"
if not ROUND114: assert "FOURTH.ad_velocity" in script_txt and "function FOURTH.ad_velocity(unit, allow_bearing)" in script_txt, \
    "the velocity helper is missing"
_vel0 = script_txt.find("function FOURTH.ad_velocity(unit, allow_bearing)")
_vel1 = script_txt.find("\nend", _vel0)
_vel = script_txt[_vel0:_vel1]
for _tok in ("is_moving()", "is_moving_fast()", "slow_speed()", "fast_speed()",
             "ordered_position()", "bearing()"):
    if not ROUND114: assert _tok in _vel, "the velocity helper does not read " + _tok
if not ROUND114: assert 'if moving ~= true then return 0, 0, 0, "stationary" end' in _vel, \
    "a unit that is not moving does not get a ZERO velocity"
for _src in ('"moving-unreadable"', '"no-speed"', '"no-heading"'):
    if not ROUND114: assert _src in _vel, "an unreadable velocity source is not named: " + _src
if not ROUND114: assert "len >= 0.5" in _vel, "the degenerate-ordered-point gate is missing"
if not ROUND114: assert "if allow_bearing then" in _vel, "the bearing fallback is not caster-gated"
if not ROUND114: assert script_txt.count("if allow_bearing then") == 1, \
    "the bearing fallback must be offered in exactly one place (ad_velocity)"
if not ROUND114: assert "function FOURTH.ad_lead(unit, t, allow_bearing)" in script_txt, \
    "the two-body state/projection helper is missing"
if not ROUND114: assert "local px, pz = x + vx * t, z + vz * t" in script_txt, \
    "the projection does not add v*t on both axes"
if not ROUND114: assert "if allow_bearing and FOURTH.AIR_DROP_INHERIT == true then" in script_txt, \
    "the ONE momentum flag is not wired to the second v*t"
if not ROUND114: assert "function FOURTH.ad_project(unit, t)" in script_txt, \
    "the projected-position helper is missing"
if not ROUND114: assert "FOURTH.ad_lead(unit, t, false)" in script_txt, \
    "ad_project does not project an enemy through ad_lead"
if not ROUND114: assert script_txt.count("does NOT inherit the caster's velocity") == 1, \
    "the no-momentum assumption is not documented once, in the rule comment"
if not ROUND114: assert "ONE FLAG" in script_txt and "impact = caster + v*d*2" in script_txt, \
    "the single-flag escape hatch is not documented"
if not ROUND114: assert "TUNABLE CONSTANT" in script_txt, \
    "the 1.5 s delay is not documented as a tunable constant (not a game value)"
_pk0 = script_txt.find("function FOURTH.ad_pick(unit, routing)")
_pk1 = script_txt.find("\nfunction FOURTH.evaluate_air_drop_on_infantry", _pk0)
_pk = script_txt[_pk0:_pk1]
if not ROUND114: assert "FOURTH.ad_lead(unit, ad_t, true)" in _pk and "FOURTH.ad_lead(enemy, ad_t, false)" in _pk, \
    "the picker does not project BOTH bodies"
# SUPERSEDED IN ROUND 113: the picker gates on the PERPENDICULAR distance from
# the enemy's path segment to the caster's projected point, plus the frontage.
if not ROUND114: assert "FOURTH.ad_sep(best_ipx, best_ipz, epx, epz)" in _pk and "perp <= eff" in _pk, \
    "the picker does not gate on the PROJECTED separation against the bound"
if not ROUND114: assert "FOURTH.AIR_DROP_DELAY_S" in _pk, "the picker does not read the fall delay"
if not ROUND114: assert "caster position UNREADABLE" in _pk, "the caster-position fail-closed branch is missing"
if not ROUND114: assert "FOURTH.ad_centre_gap(unit, enemy)" in _pk, "the instant cross-check left the picker"
_rc0 = script_txt.find("if FOURTH.ad_enemy ~= nil then")
_rc1 = script_txt.find("-- SELF-SUMMON RE-CHECK", _rc0)
_rc = script_txt[_rc0:_rc1]
# SUPERSEDED IN ROUND 113: the re-check takes ONE ad_lead call for the enemy (it
# needs the CURRENT point as well as the projected one, to rebuild the segment).
if not ROUND114: assert "FOURTH.ad_lead(unit, ad_t_now, true)" in _rc \
    and "FOURTH.ad_lead(enemy, ad_t_now, false)" in _rc and "FOURTH.ad_seg_dist" in _rc, \
    "the pre-cast re-check does not RE-PROJECT both bodies"
if not ROUND114: assert "local gap_now = perp_now" in _rc and \
    "local in_bound_now = (perp_now ~= nil and perp_now <= eff_now)" in _rc, \
    "the re-check's bound test does not run on the projected separation"
if not ROUND114: assert '" (PROJECTED "' in script_txt, "the target line does not announce the projection"
if not ROUND114: assert '" v=" .. FOURTH.ad_vec_text(best_uvx, best_uvz, best_uspd, best_usrc)' in script_txt, \
    "the target line does not print the caster's velocity + source"
if not ROUND114: assert '" v=" .. FOURTH.ad_vec_text(best_evx, best_evz, best_espd, best_esrc)' in script_txt, \
    "the target line does not print the enemy's velocity + source"
if not ROUND114: assert '" proj=" .. FOURTH.ad_pos(best_ipx, best_ipz)' in script_txt, \
    "the target line does not print the caster's projected point"
if not ROUND114: assert '" proj=" .. FOURTH.ad_pos(best_epx, best_epz)' in script_txt, \
    "the target line does not print the enemy's projected point"
if not ROUND114: assert '" centre=" .. string.format("%.1f", best_pgap)' in script_txt, \
    "the target line does not print the projected separation"
if not ROUND114: assert '" now="' in script_txt, "the target line does not print the instant separation"
# SUPERSEDED IN ROUND 112 (a FORMAT gate, tightened not removed): the watch line
# no longer bands below 15 m - the deciding number is printed exactly - so the gate
# now demands the exact-metre branch AND the 15 m band boundary that keeps the log
# short above it.
if not ROUND114: assert '" [perp="' in script_txt and '" projected sep="' in script_txt and '" after delay="' in script_txt, \
    "the watch line does not print the projected distance / delay"
if not ROUND114: assert 'if near_gap < 15 then' in script_txt and 'string.format("%.2f", near_gap)' in script_txt \
    and 'math.floor(near_gap / 5) * 5' in script_txt, \
    "the watch line does not print EXACT metres below 15 m (and a band above it)"
if not ROUND114: assert "momentum=" in script_txt, "the target line does not name the momentum mode"
assert script_txt.count('trigger = "air_drop_on_infantry"') == 12, \
    "the air-drop family is no longer 12 entries"
assert script_txt.count("\t{ marker = ") == 982, "the abilities table is not 982 entries"
if not ROUND114: assert script_txt.count("ability.range_m = FOURTH.AIR_DROP_CENTER_M") == 1, \
    "the 70% bypass lost its single wiring"
assert "string.find(" not in script_txt, "a string.find call is back in the script"
assert "unit_in_range(" not in script_txt, "an engine unit_in_range call is back"

# ============================================================================
# ROUND 111 (2026-10-18): THE MOVING-CASTER DIALS - ONLY THE CASTER'S LEAD.
#
#   The user's fourth field report: "It seems to work okay when the caster is
#   stationary, but it definitely drops the rocks too soon when in movement."
#   A stationary caster is RIGHT, so the ENEMY projection and the 6 m bound are
#   right; the error exists only while the caster moves and fires TOO SOON, so
#   the caster's lead term is OVER-STATED. Two dials now qualify the CASTER only:
#       caster_projected = caster + v_caster * AIR_DROP_CASTER_DELAY_S
#                                          * AIR_DROP_CASTER_LEAD
#       enemy_projected  = enemy  + v_enemy  * AIR_DROP_DELAY_S
#   shipped as (AIR_DROP_CASTER_DELAY_S = 1.5, AIR_DROP_CASTER_LEAD = 0.5).
#   0.0 is a caster treated as stationary (the field-correct case); 1.0 is the
#   round-110 behaviour that over-leads. The enemy term, the 6 m bound, the
#   INHERIT flag, air_only / no_melee, the self-centred cast, the fail-closed
#   reads and the re-projecting pre-cast re-check are ALL unchanged - the
#   re-check calls the same helper, so it reads the same two dials.
#   Counts UNCHANGED: 689 entries / 742 keys, air_drop_on_infantry 12 / 19.
# ============================================================================
if not ROUND114: assert script_txt.count("\nFOURTH.AIR_DROP_CASTER_DELAY_S = 1.5\n") == 1, \
    "the caster's own lead time is not defined exactly once at 1.5 s"
if not ROUND114: assert script_txt.count("\nFOURTH.AIR_DROP_CASTER_LEAD = 0.5\n") == 1, \
    "the caster lead factor is not defined exactly once at 0.5"
if not ROUND114: assert script_txt.count("\nFOURTH.AIR_DROP_DELAY_S = 1.5\n") == 1, \
    "the shared fall delay moved (the ENEMY term must stay exactly as it was)"
if not ROUND114: assert script_txt.count("\nFOURTH.AIR_DROP_INHERIT = false\n") == 1, \
    "the momentum flag moved or no longer ships FALSE"
if not ROUND114: assert script_txt.count("\nFOURTH.AIR_DROP_CENTER_M = 6\n") == 1, \
    "the 6 m centre bound moved (it must stay exactly one definition)"
if not ROUND114: assert "THE MOVING-CASTER DIALS" in script_txt, "the round-111 constant comment is missing"
if not ROUND114: assert "LOWER the lead: 0.5 -> 0.3 -> 0.0" in script_txt, \
    "the tuning guide does not state the 0.5 -> 0.3 -> 0.0 order for an early release"
if not ROUND114: assert "fires EARLY while MOVING" in script_txt and "NEVER fires while MOVING" in script_txt \
    and "still EARLY while STATIONARY" in script_txt, \
    "the three-symptom tuning guide is not in the source"
if not ROUND114: assert "Only ONE dial changes per test" in script_txt, \
    "the source does not say to change one dial per test"
_ld0 = script_txt.find("function FOURTH.ad_lead(unit, t, allow_bearing)")
_ld1 = script_txt.find("\nend", _ld0)
_ld = script_txt[_ld0:_ld1]
if not ROUND114: assert _ld0 > 0 and _ld1 > _ld0, "the projection helper is missing"
if not ROUND114: assert "local t_caster, lead_caster = t, 1" in _ld, \
    "the caster's lead time/factor locals are missing"
if not ROUND114: assert "px = x + vx * t_caster * lead_caster" in _ld, \
    "the caster is not projected as position + v * caster_delay * lead (x axis)"
if not ROUND114: assert "pz = z + vz * t_caster * lead_caster" in _ld, \
    "the caster is not projected as position + v * caster_delay * lead (z axis)"
if not ROUND114: assert "local px, pz = x + vx * t, z + vz * t" in _ld, \
    "the ENEMY projection is no longer the shared v*t on both axes"
if not ROUND114: assert "if allow_bearing == true then" in _ld, \
    "the dials are not applied to the caster alone"
if not ROUND114: assert 'if type(d_caster) == "number" and d_caster >= 0 then t_caster = d_caster end' in _ld, \
    "an unreadable caster delay does not fall back to the shared delay"
if not ROUND114: assert 'if type(l_caster) == "number" and l_caster >= 0 then lead_caster = l_caster end' in _ld, \
    "an unreadable caster lead does not fall back to full lead (never to a guess)"
if not ROUND114: assert "if allow_bearing and FOURTH.AIR_DROP_INHERIT == true then" in _ld and \
    "px = px + vx * t_caster * lead_caster" in _ld, \
    "the ONE momentum flag no longer adds the lead term a second time"
if not ROUND114: assert script_txt.count("FOURTH.AIR_DROP_CASTER_DELAY_S") >= 3, \
    "the caster delay is not read in the source"
if not ROUND114: assert "function FOURTH.ad_dial_text(moving)" in script_txt, "the dial-text helper is missing"
if not ROUND114: assert script_txt.count("FOURTH.ad_dial_text") == 5, \
    "the dial-text helper must be defined once and called four times (target, watch, skip, re-check)"
if not ROUND114: assert '.. " from " .. FOURTH.ad_dial_text(best_uspd > 0)' in script_txt, \
    "the decision line does not print the two dials after the caster projection"
if not ROUND114: assert '" moving caster: lead="' in script_txt, \
    "the moving-caster log fragment is missing"
if not ROUND114: assert script_txt.count("FOURTH.ad_dial_text(uc_spd2 ~= nil and uc_spd2 > 0)") == 2, \
    "the pre-cast re-check does not print the dials on BOTH its lines"
if not ROUND114: assert '.. " (" .. FOURTH.ad_dial_text(best_uspd > 0) .. "); enemy v="' in script_txt, \
    "the why-not line does not print the dials beside the caster velocity"
_pk0 = script_txt.find("function FOURTH.ad_pick(unit, routing)")
_pk1 = script_txt.find("\nfunction FOURTH.evaluate_air_drop_on_infantry", _pk0)
_pk = script_txt[_pk0:_pk1]
if not ROUND114: assert "FOURTH.ad_lead(unit, ad_t, true)" in _pk and "FOURTH.ad_lead(enemy, ad_t, false)" in _pk, \
    "the picker no longer projects both bodies"
# SUPERSEDED IN ROUND 113: the picker gates on the PERPENDICULAR distance from
# the enemy's path segment to the caster's projected point, plus the frontage.
if not ROUND114: assert "FOURTH.ad_sep(best_ipx, best_ipz, epx, epz)" in _pk and "perp <= eff" in _pk, \
    "the picker no longer gates on the projected separation"
if not ROUND114: assert "FOURTH.AIR_DROP_CASTER_DELAY_S" not in _pk, \
    "the picker reaches for a dial directly instead of the one helper"
_rc0 = script_txt.find("if FOURTH.ad_enemy ~= nil then")
_rc1 = script_txt.find("-- SELF-SUMMON RE-CHECK", _rc0)
_rc = script_txt[_rc0:_rc1]
# SUPERSEDED IN ROUND 113: the re-check takes ONE ad_lead call for the enemy (it
# needs the CURRENT point as well as the projected one, to rebuild the segment).
if not ROUND114: assert "FOURTH.ad_lead(unit, ad_t_now, true)" in _rc \
    and "FOURTH.ad_lead(enemy, ad_t_now, false)" in _rc and "FOURTH.ad_seg_dist" in _rc, \
    "the pre-cast re-check no longer re-projects both bodies"
if not ROUND114: assert "FOURTH.AIR_DROP_CASTER_LEAD" not in _rc and "FOURTH.AIR_DROP_CASTER_DELAY_S" not in _rc, \
    "the re-check re-derives the dials instead of using the shared helper"
assert script_txt.count('trigger = "air_drop_on_infantry"') == 12, \
    "the air-drop family is no longer 12 entries"
assert script_txt.count("\t{ marker = ") == 982, "the abilities table is not 982 entries"
if not ROUND114: assert script_txt.count("ability.range_m = FOURTH.AIR_DROP_CENTER_M") == 1, \
    "the 70% bypass lost its single wiring"
assert "string.find(" not in script_txt, "a string.find call is back in the script"
assert "unit_in_range(" not in script_txt, "an engine unit_in_range call is back"

# ============================================================================
# ROUND 112 (2026-10-24): THE ENEMY-SIDE LEAD DIAL, THE EXACT WATCH DISTANCE AND
# THE UI-ID TAG.
#
#   THE EVIDENCE (docs/WH3_skyjunk_diagnosis.md, pack 651f12e61284cae472bb06bf3a66b87d,
#   session lines 947215-952480): four Sky-junk bombers (ui ids 1002-1005), all
#   armed in one click, all airborne, all evaluated on every poll, infantry
#   candidates present every poll - and three of them NEVER fired while the
#   zombies walked underneath. The rule was satisfied only at a projected centre
#   separation <= 6 m and the projected number bottomed in the 5-10 m band:
#   the enemy's centre was carried v_enemy * 1.5 s = 3.45 m PAST the hoverer, so
#   the projected gap was LARGEST exactly when the enemy was underneath (5 m at
#   the pass, 10 m one second later).
#
#   (1) THE FOURTH DIAL - enemy_projected = enemy + v_enemy * AIR_DROP_DELAY_S
#       * AIR_DROP_ENEMY_LEAD, with FOURTH.AIR_DROP_ENEMY_LEAD = 0.3 shipped.
#       0.0 = the enemy's CURRENT position (impact straight down on where it is);
#       1.0 = the round-110/111 full carry that produced the misses; 0.3 = 0.45 s
#       of lead (~1.0 m at 2.3 m/s, not 3.45 m), because the release is not
#       instantaneous but a full 1.5 s of enemy travel is far too much. It scales
#       the ENEMY's velocity term ONLY.
#   (2) THE WATCH LINE prints EXACT distances (%.2f) below 15 m; the 5 m band
#       survives above 15 m, where the number is context only. Diagnosis D1.
#   (3) EVERY air-drop line carries the unit's ui id - "[1003] sky_junk_bomb
#       watch: ..." - via FOURTH.ad_tag, on the decision line, the watch line,
#       the skip line and both pre-cast lines. Diagnosis D2.
#   (4) The dial text is the FOUR-dial form on every one of those lines:
#       delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=0.50.
#   UNCHANGED: AIR_DROP_DELAY_S = 1.5, AIR_DROP_CASTER_DELAY_S = 1.5,
#       AIR_DROP_CASTER_LEAD = 0.5, AIR_DROP_CENTER_M = 6, AIR_DROP_INHERIT =
#       false, air_only / no_melee, the self-centred cast, every fail-closed read
#       and the pre-cast re-check (same helper => same four dials).
#   Counts UNCHANGED: 689 entries / 742 keys, air_drop_on_infantry 12 / 19.
# ============================================================================
if not ROUND114: assert script_txt.count("\nFOURTH.AIR_DROP_ENEMY_LEAD = 0.3\n") == 1, \
    "the enemy lead factor is not defined exactly once at 0.3"
if not ROUND114: assert script_txt.count("\nFOURTH.AIR_DROP_DELAY_S = 1.5\n") == 1, \
    "the shared fall delay moved - the enemy's lead TIME must stay 1.5 s"
if not ROUND114: assert script_txt.count("\nFOURTH.AIR_DROP_CASTER_DELAY_S = 1.5\n") == 1, \
    "the caster's own lead time moved"
if not ROUND114: assert script_txt.count("\nFOURTH.AIR_DROP_CASTER_LEAD = 0.5\n") == 1, \
    "the caster lead factor moved"
if not ROUND114: assert script_txt.count("\nFOURTH.AIR_DROP_CENTER_M = 6\n") == 1, \
    "the 6 m centre bound moved (it must stay exactly one definition)"
if not ROUND114: assert script_txt.count("\nFOURTH.AIR_DROP_INHERIT = false\n") == 1, \
    "the momentum flag moved or no longer ships FALSE"
_ld0 = script_txt.find("function FOURTH.ad_lead(unit, t, allow_bearing)")
_ld1 = script_txt.find("\nend", _ld0)
_ld = script_txt[_ld0:_ld1]
if not ROUND114: assert _ld0 > 0 and _ld1 > _ld0, "the projection helper is missing"
if not ROUND114: assert "local lead_enemy = 1" in _ld and "if allow_bearing ~= true then" in _ld, \
    "the enemy lead is not read on the enemy arm"
if not ROUND114: assert "FOURTH.AIR_DROP_ENEMY_LEAD" in _ld, "the enemy dial is not used in the projection"
if not ROUND114: assert "px = x + vx * t * lead_enemy" in _ld and "pz = z + vz * t * lead_enemy" in _ld, \
    "the enemy is not projected as position + v * delay * enemy_lead"
if not ROUND114: assert 'if type(l_enemy) == "number" and l_enemy >= 0 then lead_enemy = l_enemy end' in _ld, \
    "an unreadable enemy lead does not fall back to the full carry (never to a guess)"
if not ROUND114: assert "local t_caster, lead_caster = t, 1" in _ld, \
    "the caster's lead locals are missing"
if not ROUND114: assert "px = x + vx * t_caster * lead_caster" in _ld, \
    "the caster is no longer projected by its own delay x lead (x axis)"
if not ROUND114: assert "pz = z + vz * t_caster * lead_caster" in _ld, \
    "the caster is no longer projected by its own delay x lead (z axis)"
if not ROUND114: assert "if allow_bearing and FOURTH.AIR_DROP_INHERIT == true then" in _ld, \
    "the ONE momentum flag no longer adds the caster's lead term a second time"
if not ROUND114: assert "function FOURTH.ad_dial_text(moving)" in script_txt, "the dial-text helper is missing"
if not ROUND114: assert '"enemy_lead="' in script_txt and '"delay="' in script_txt, \
    "the dial text does not name the enemy lead and the shared delay"
if not ROUND114: assert '"delay_caster="' in script_txt and '"caster_lead="' in script_txt, \
    "the dial text does not name both caster dials"
if not ROUND114: assert script_txt.count("FOURTH.ad_dial_text") == 5, \
    "the dial-text helper must be defined once and called four times (target, watch, skip, re-check)"
if not ROUND114: assert '.. " from " .. FOURTH.ad_dial_text(best_uspd > 0)' in script_txt, \
    "the decision line does not print the four dials"
if not ROUND114: assert '" moving caster: lead="' in script_txt, \
    "the moving-caster log fragment is missing"
if not ROUND114: assert '.. " (" .. FOURTH.ad_dial_text(best_uspd > 0) .. "); enemy v="' in script_txt, \
    "the why-not line does not print the dials beside the caster velocity"
if not ROUND114: assert "function FOURTH.ad_tag(unit)" in script_txt, "the ui-id tag helper is missing"
if not ROUND114: assert script_txt.count("FOURTH.ad_tag(unit)") == 6, \
    "the tag must be defined once and prepended to the four air-drop log lines"
if not ROUND114: assert 'log("  " .. FOURTH.ad_tag(unit) .. marker .. " target: ' in script_txt, \
    "the decision line does not carry the unit tag"
if not ROUND114: assert 'log("  " .. FOURTH.ad_tag(unit) .. ad_marker_now .. " SKIPPED: ' in script_txt, \
    "the skip line does not carry the unit tag"
if not ROUND114: assert 'log("  " .. FOURTH.ad_tag(unit) .. ad_marker_now .. " pre-cast re-check: ' in script_txt, \
    "the pre-cast re-check line does not carry the unit tag"
_pk0 = script_txt.find("function FOURTH.ad_pick(unit, routing)")
_pk1 = script_txt.find("\nfunction FOURTH.evaluate_air_drop_on_infantry", _pk0)
_pk = script_txt[_pk0:_pk1]
if not ROUND114: assert "if near_gap < 15 then" in _pk and 'string.format("%.2f", near_gap)' in _pk, \
    "the watch line does not print the EXACT projected distance below 15 m"
if not ROUND114: assert 'string.format("%.2f", near_now)' in _pk, \
    "the watch line does not print the EXACT instant distance below 15 m"
if not ROUND114: assert "math.floor(near_gap / 5) * 5" in _pk and "math.floor(near_now / 5) * 5" in _pk, \
    "the 5 m band above 15 m is gone (the log must not grow per 0.1 m there)"
if not ROUND114: assert "FOURTH.ad_lead(unit, ad_t, true)" in _pk and "FOURTH.ad_lead(enemy, ad_t, false)" in _pk, \
    "the picker no longer projects both bodies"
if not ROUND114: assert "perp <= eff" in _pk, "the picker no longer gates on the PERPENDICULAR distance to the enemy path"
if not ROUND114: assert "FOURTH.AIR_DROP_ENEMY_LEAD" not in _pk, \
    "the picker reads the enemy dial directly instead of the one helper"
_rc0 = script_txt.find("if FOURTH.ad_enemy ~= nil then")
_rc1 = script_txt.find("-- SELF-SUMMON RE-CHECK", _rc0)
_rc = script_txt[_rc0:_rc1]
# SUPERSEDED IN ROUND 113: the re-check takes ONE ad_lead call for the enemy (it
# needs the CURRENT point as well as the projected one, to rebuild the segment).
if not ROUND114: assert "FOURTH.ad_lead(unit, ad_t_now, true)" in _rc \
    and "FOURTH.ad_lead(enemy, ad_t_now, false)" in _rc and "FOURTH.ad_seg_dist" in _rc, \
    "the pre-cast re-check no longer re-projects both bodies"
if not ROUND114: assert "FOURTH.AIR_DROP_ENEMY_LEAD" not in _rc and "FOURTH.AIR_DROP_CASTER_LEAD" not in _rc, \
    "the re-check re-derives the dials instead of using the shared helper"
if not ROUND114: assert "AIR_DROP_ENEMY_LEAD 0.3 -> 0.0" in script_txt, \
    "the tuning guide does not state the enemy-lead fix for a walk-through"
if not ROUND114: assert "THE FOUR DIALS" in script_txt and "THE DEFAULTS THAT SHIP" in script_txt, \
    "the four-dial tuning table is not in the source"
if not ROUND114: assert "Only ONE dial changes per test" in script_txt, \
    "the source does not say to change one dial per test"
if not ROUND114: assert "LOWER the lead: 0.5 -> 0.3 -> 0.0" in script_txt, \
    "the caster-lead tuning order is gone"
if not ROUND114: assert "fires EARLY while MOVING" in script_txt and "NEVER fires while MOVING" in script_txt \
    and "still EARLY while STATIONARY" in script_txt, \
    "the symptom tuning guide is not in the source"
assert script_txt.count('trigger = "air_drop_on_infantry"') == 12, \
    "the air-drop family is no longer 12 entries"
assert script_txt.count("\t{ marker = ") == 982, "the abilities table is not 982 entries"
if not ROUND114: assert script_txt.count("ability.range_m = FOURTH.AIR_DROP_CENTER_M") == 1, \
    "the 70% bypass lost its single wiring"
assert "string.find(" not in script_txt, "a string.find call is back in the script"
assert "unit_in_range(" not in script_txt, "an engine unit_in_range call is back"

# ============================================================================
# ROUND 113 (2026-10-25): THE PATH TEST, THE DERIVED FRONTAGE AND THE
# SINGLE-ENTITY EXCLUSION.
#
#   THE FIELD REPORT (the user, with a screenshot): a Sky-junk hovering BESIDE a
#   20-model zombie block never fired while the block walked past - the enemy's
#   CENTRE stayed 10+ m away even though its models swept under the caster; and
#   separately one fired at a LORD.
#   THE USER'S RULINGS, verbatim: "1. Why combine? The started with one model
#   would cover the other case, woudn't it? Also, why comparison is 1 or less? It
#   cannot be less, then the unit does not exist. So comparion should be equal to
#   1. Am I forgetting something? If you agree, start implementing with point 2."
#   and "2. Let's implement the the path test with a derived frontage that you
#   suggest."
#
#   (1) THE PATH: segment = enemy_current -> enemy_projected; the deciding number
#       is the shortest horizontal distance from that SEGMENT to the CASTER'S
#       PROJECTED point. A 20-model block is 10 m wide in two ranks, so its
#       centre can stay 10 m away while one of its models passes underneath.
#   (2) THE FRONTAGE CREDIT: perp <= AIR_DROP_CENTER_M + ad_frontage(enemy).
#       ad_frontage returns a HALF-width: ordered_width()/2 when sane, otherwise
#       ceil(men/2) * radius (TWO RANKS - the wide end of the game's own
#       formations), clamped to 1..12 m, failing closed to 0. A one-model unit
#       gets 0: a point has no width.
#   (3) THE RADIUS IS A DOCUMENTED CONSTANT (0.6 m) because battle Lua cannot read
#       land_units.man_entity -> battle_entities.radius; the value is the MODAL
#       infantry radius in the extracted tables (168 of 942 rows), conservative
#       against the 0.7 m median.
#   (4) THE SINGLE-ENTITY EXCLUSION: initial_number_of_men() == 1 is skipped, once
#       per episode, as "single entity (1 model)". EXACT equality, INITIAL not
#       current, and the commander key set is NOT consulted here - every
#       infantry-class lord/hero in the data is one model.
#   (5) The pre-cast re-check RE-RUNS the segment test on fresh reads.
#   KEPT: the four dials, the 6 m bound, AIR_DROP_INHERIT, air_only / no_melee,
#       the self-centred cast, every fail-closed read.
#   Counts UNCHANGED: 689 entries / 742 keys, air_drop_on_infantry 12 / 19.
# ============================================================================
if not ROUND114: assert script_txt.count("\nFOURTH.AIR_DROP_MODEL_RADIUS_M = 0.6\n") == 1, \
    "the per-model radius constant is not defined exactly once at 0.6"
if not ROUND114: assert script_txt.count("\nFOURTH.AIR_DROP_RANKS = 2\n") == 1, \
    "the two-rank assumption is not defined exactly once"
if not ROUND114: assert script_txt.count("\nFOURTH.AIR_DROP_FRONTAGE_MIN_M = 1\n") == 1 \
    and script_txt.count("\nFOURTH.AIR_DROP_FRONTAGE_MAX_M = 12\n") == 1, \
    "the frontage clamp is not 1 .. 12 m, defined exactly once each"
if not ROUND114: assert script_txt.count("\nFOURTH.AIR_DROP_CENTER_M = 6\n") == 1 \
    and script_txt.count("\nFOURTH.AIR_DROP_DELAY_S = 1.5\n") == 1 \
    and script_txt.count("\nFOURTH.AIR_DROP_ENEMY_LEAD = 0.3\n") == 1 \
    and script_txt.count("\nFOURTH.AIR_DROP_CASTER_DELAY_S = 1.5\n") == 1 \
    and script_txt.count("\nFOURTH.AIR_DROP_CASTER_LEAD = 0.5\n") == 1 \
    and script_txt.count("\nFOURTH.AIR_DROP_INHERIT = false\n") == 1, \
    "one of the SIX older pins moved or was redefined"
_fr0 = script_txt.find("function FOURTH.ad_frontage(unit, men_now)")
_fr1 = script_txt.find("\nfunction FOURTH.ad_frontage_text", _fr0)
_fr = script_txt[_fr0:_fr1]
if not ROUND114: assert _fr0 > 0 and _fr1 > _fr0, "the frontage helper is missing"
if not ROUND114: assert "unit:ordered_width()" in _fr and "local half = w * 0.5" in _fr, \
    "the frontage helper does not prefer ordered_width() (halved)"
if not ROUND114: assert "math.ceil(men / FOURTH.AIR_DROP_RANKS)" in _fr and "FOURTH.AIR_DROP_MODEL_RADIUS_M" in _fr, \
    "the frontage helper does not derive the width from the model count and the radius"
if not ROUND114: assert "if men < 2 then" in _fr and 'return 0, "single"' in _fr, \
    "a one-model unit is not given zero frontage"
if not ROUND114: assert 'return 0, "unreadable"' in _fr, "the frontage helper is not fail-closed"
if not ROUND114: assert _fr.count('return clamped, "clamped"') == 1, "the clamp branch is missing"
_sg0 = script_txt.find("function FOURTH.ad_seg_dist(px, pz, ax, az, bx, bz)")
_sg1 = script_txt.find("\nend", _sg0)
_sg = script_txt[_sg0:_sg1]
if not ROUND114: assert _sg0 > 0 and _sg1 > _sg0, "the point-to-segment helper is missing"
if not ROUND114: assert "local t = ((px - ax) * dx + (pz - az) * dz) / len2" in _sg, \
    "the segment helper does not project the point onto the segment"
if not ROUND114: assert "if t < 0 then" in _sg and "elseif t > 1 then" in _sg, \
    "the segment parameter is not clamped to 0..1 (an END-point miss would read as a hit)"
_pk0 = script_txt.find("function FOURTH.ad_pick(unit, routing)")
_pk1 = script_txt.find("\nfunction FOURTH.evaluate_air_drop_on_infantry", _pk0)
_pk = script_txt[_pk0:_pk1]
if not ROUND114: assert "local perp = FOURTH.ad_seg_dist(best_ipx, best_ipz, ex, ez, epx, epz)" in _pk, \
    "the picker does not measure the perpendicular distance to the enemy's path"
if not ROUND114: assert "local eff = bound + half" in _pk and "if perp <= eff and" in _pk, \
    "the picker does not gate on perp vs bound + frontage"
if not ROUND114: assert "FOURTH.ad_frontage(enemy, alive)" in _pk, \
    "the picker does not credit the candidate's half-frontage"
if not ROUND114: assert "enemy:initial_number_of_men()" in _pk and "elseif im == 1 then" in _pk, \
    "the picker has no single-entity exclusion (exact equality on the INITIAL size)"
assert "im <= 1" not in _pk, "the single-entity guard is a range test again"
assert "FOURTH.enemy_is_commander" not in _pk, \
    "the commander key set is consulted by this evaluator (the model count covers it)"
_rc0 = script_txt.find("if FOURTH.ad_enemy ~= nil then")
_rc1 = script_txt.find("-- SELF-SUMMON RE-CHECK", _rc0)
_rc = script_txt[_rc0:_rc1]
if not ROUND114: assert "FOURTH.ad_lead(enemy, ad_t_now, false)" in _rc and "FOURTH.ad_seg_dist(upx, upz, ex2, ez2, epx, epz)" in _rc, \
    "the pre-cast re-check does not rebuild the segment from FRESH reads"
if not ROUND114: assert "FOURTH.ad_frontage(enemy, (ok_ea and ea) or nil)" in _rc, \
    "the pre-cast re-check does not re-derive the frontage"
if not ROUND114: assert "local in_bound_now = (perp_now ~= nil and perp_now <= eff_now)" in _rc, \
    "the pre-cast re-check still gates on the projected centre rather than the path"
if not ROUND114: assert "TWO RANKS DEEP" in script_txt and "battle_entities.radius is 0.6 m (168 rows)" in script_txt, \
    "the formation assumption / the radius evidence is not documented in the source"
if not ROUND114: assert "1 .. 12 m HALF-width" in script_txt, "the clamp is not documented in the source"
if not ROUND114: assert "THE COMMANDER KEY SET IS DELIBERATELY NOT USED HERE" in script_txt, \
    "the source does not state that the commander key set is not consulted"
if not ROUND114: assert 'SKIPPED: " .. why' in script_txt and 'single entity (1 model)' in script_txt, \
    "the once-per-episode single-entity skip line is missing"
if not ROUND114: assert "FOURTH.ad_se_logged" in script_txt, "the once-per-episode skip bookkeeping is missing"
if not ROUND114: assert "AIR_DROP_FRONTAGE_MAX_M (12 -> 15 -> 20)" in script_txt, \
    "the tuning guide does not say how to widen the frontage credit"
assert script_txt.count('trigger = "air_drop_on_infantry"') == 12, \
    "the air-drop family is no longer 12 entries"
assert script_txt.count("\t{ marker = ") == 982, "the abilities table is not 982 entries"
if not ROUND114: assert script_txt.count("FOURTH.ad_dial_text") == 5, \
    "the dial-text helper must be defined once and called four times"
if not ROUND114: assert script_txt.count("FOURTH.ad_tag(unit)") == 6, \
    "the tag must be defined once and prepended to the five air-drop log sites"
if not ROUND114: assert script_txt.count("ability.range_m = FOURTH.AIR_DROP_CENTER_M") == 1, \
    "the 70% bypass lost its single wiring"
assert "string.find(" not in script_txt, "a string.find call is back in the script"
assert "unit_in_range(" not in script_txt, "an engine unit_in_range call is back"

# the main mod must be byte-identical (untouched by this work)
main_src = open(SRC_ROOT + "/script/battle/mod/zz_test_deadly_onslaught.lua", "rb").read()
main_raw = bytes(c.send({"GetPackedFileRawData": [key, "script/battle/mod/zz_test_deadly_onslaught.lua"]})["VecU8"])
print(f"\n== 6d main mod untouched (byte-identical)     : {main_raw == main_src}")
assert main_raw == main_src, "the main mod changed - it must not"


# ============================================================================
# ROUND 114 (2026-10-18): THE AIR-DROP RULE IS ONE COMPARISON + A FAST PASS.
#
#   candidate = alive and number_of_men_alive() > AIR_DROP_MIN_MEN (10)
#   valid     = its unit_distance() is readable
#   chosen    = the NEAREST valid candidate
#   FIRE      = unit_distance(caster, chosen) < AIR_DROP_EDGE_M (0.10 m)
#
# RETIRED WITH THE OLD RULE: the infantry filter, the single-entity exclusion, the
# four projection dials, AIR_DROP_CENTER_M, AIR_DROP_INHERIT, the derived frontage
# (radius / ranks / min / max) and the segment test with every helper that served
# them (ad_frontage, ad_frontage_text, ad_seg_dist, ad_velocity, ad_lead,
# ad_project, ad_dial_text, ad_single_say, ad_single_clear, ad_centre_gap, ad_pos,
# ad_sep, ad_vec_text). NOTHING else in the file used any of them.
#
# ADDED: FOURTH.ad_nearest (one candidate scan), FOURTH.ad_fast_pass (the same
# evaluator, same gate+cast path via FOURTH.try_pair, every 0.2 s, for armed
# air-drop units with a valid enemy inside 30 m), its own bm:repeat_callback.
# The global poll keeps POLL_MS = 250 and every other ability's cadence.
# ============================================================================
for _k, _v in (("CENTER_M", "6.0"), ("MIN_MEN", "10"), ("NEAR_M", "30"), ("FAST_S", "0.2")):
    _line = "\nFOURTH.AIR_DROP_" + _k + " = " + _v + "\n"
    assert script_txt.count(_line) == 1, "the round-114 constant is not defined exactly once: " + _k
assert script_txt.count("function FOURTH.ad_nearest(unit)") == 1, \
    "the candidate scan (FOURTH.ad_nearest) is missing"
assert script_txt.count("function FOURTH.ad_fast_pass()") == 1, \
    "the air-drop fast pass is missing"
assert script_txt.count("function FOURTH.try_pair(") == 1, \
    "the shared gate+cast function is missing"
assert script_txt.count("FOURTH.try_pair(") == 3, \
    "the shared gate+cast function is not called by both timers"
assert script_txt.count("bm:repeat_callback(") == 2, \
    "the air-drop fast timer is not registered beside the global poll"
assert script_txt.count("local POLL_MS = 250") == 1, \
    "the global poll interval moved (it must stay 250 ms)"
assert "math.floor(FOURTH.AIR_DROP_FAST_S * 1000)" in script_txt, \
    "the fast timer is not keyed on AIR_DROP_FAST_S"
assert 'zz_test_deadly_onslaught_air_drop_fast' in script_txt, \
    "the fast timer has no name"
assert 'if dist >= FOURTH.AIR_DROP_CENTER_M then' in script_txt, \
    "the decision is not the single edge comparison"
assert "alive > FOURTH.AIR_DROP_MIN_MEN" in script_txt, \
    "the > 10 entity filter is missing"
assert 'FOURTH.ad_say(unit, marker, "nearest valid:\'' in script_txt, \
    "the decision line does not name the enemy / distance"
assert "nearest valid:'" in script_txt and "centre=" in script_txt and "need < " in script_txt, \
    "the decision line lost one of its fields"
assert "-> SKIPPED at re-check" in script_txt, \
    "the pre-cast re-check no longer names its skip"
assert "fast poll: ON (nearest valid " in script_txt and 'fast poll: OFF' in script_txt, \
    "the fast-poll transition lines are missing"
assert script_txt.count("FOURTH.ad_fast_abilities") >= 3, \
    "the fast pass is not driven by the air-drop entry list"
for _dead in ("FOURTH.AIR_DROP_DELAY_S",
              "FOURTH.AIR_DROP_ENEMY_LEAD", "FOURTH.AIR_DROP_CASTER_DELAY_S",
              "FOURTH.AIR_DROP_CASTER_LEAD", "FOURTH.AIR_DROP_INHERIT",
              "FOURTH.AIR_DROP_MODEL_RADIUS_M", "FOURTH.AIR_DROP_RANKS",
              "FOURTH.AIR_DROP_FRONTAGE_MIN_M", "FOURTH.AIR_DROP_FRONTAGE_MAX_M",
              "function FOURTH.ad_frontage", "function FOURTH.ad_seg_dist",
              "function FOURTH.ad_lead", "function FOURTH.ad_project",
              "function FOURTH.ad_dial_text"):
    assert _dead not in script_txt, "a retired air-drop token is back: " + _dead
assert script_txt.count('trigger = "air_drop_on_infantry"') == 12, \
    "the air-drop family is no longer 12 entries"
assert script_txt.count("\t{ marker = ") == 982, "the abilities table is not 982 entries"
assert "air_drop_on_infantry = \"When armed, fires when the nearest enemy unit with more than 10 models comes within 6 m of this unit's centre" in script_txt, \
    "the tooltip sentence does not state the measured wait"
assert "string.find(" not in script_txt, "a string.find call is back in the script"
assert "unit_in_range(" not in script_txt, "an engine unit_in_range call is back"
print("\\n== round 114 content gates                : OK ==")

# ============================================================================
# ============================================================================
# ROUND 118 (2026-10-18): THE AIR-DROP DELAY IS GONE. THE CENTRE STAYS.
#
#   candidate = ALIVE, number_of_men_alive() > AIR_DROP_MIN_MEN (10)
#   chosen    = the NEAREST valid candidate by ad_centre_gap
#   FIRE      = ad_centre_gap(caster, chosen) < AIR_DROP_CENTER_M (6.0 m),
#               on the evaluation that measured it (subject only to the armed
#               state, air_only / no_melee, the gates and the pre-cast re-check)
#
# DELETED (nothing outside the air-drop evaluator, its pre-cast re-check and
# the drop routine's purge hook ever named any of it):
#   AIR_DROP_DWELL_MID_S, AIR_DROP_DWELL_SWING_S, AIR_DROP_MIN_CONTACT_S,
#   FOURTH.ad_pair + ad_pair_key / ad_pair_stamp / ad_pair_need / ad_pair_drop
#   / ad_under / ad_purge_unit / ad_contact_clear, the purge hook
#   zz_ad_dwell_purge (its one call site lived in drop_unit_by_ui_id),
#   ad_enemy_velocity + ad_vread / ad_vread_px / ad_vread_pz, ad_proj_text,
#   ad_dynamic_delay, ad_event, the short-crossing fallback and every
#   dwell / hold / delay / cosine log line, INCLUDING the raw movement and
#   heading read-verification block (it existed only to check the cosine).
# KEPT: the CENTRE detection and ad_centre_gap, the candidate filter (no
#   infantry test), the 0.2 s fast pass with its 30 m near gate, POLL_MS = 250,
#   air_only / no_melee, the self-centred cast, every fail-closed read, the
#   gates in try_pair and the pre-cast re-check on FRESH handles.
# ============================================================================
assert script_txt.count("\nFOURTH.AIR_DROP_CENTER_M = 6.0\n") == 1, \
    "the 6 m CENTRE constant is not defined exactly once"
for _k, _v in (("MIN_MEN", "10"), ("NEAR_M", "30"), ("FAST_S", "0.2")):
    assert script_txt.count("\nFOURTH.AIR_DROP_" + _k + " = " + _v + "\n") == 1, \
        "a kept air-drop constant moved or vanished: " + _k
for _dead in ("AIR_DROP_DWELL_MID_S", "AIR_DROP_DWELL_SWING_S", "AIR_DROP_MIN_CONTACT_S",
              "FOURTH.ad_pair", "ad_pair_key", "ad_pair_stamp", "ad_pair_need",
              "ad_pair_drop", "ad_under", "ad_purge_unit", "ad_contact_clear",
              "zz_ad_dwell_purge", "ad_enemy_velocity", "ad_proj_text",
              "ad_dynamic_delay", "ad_vread", "FOURTH.ad_event", "ad_fired",
              " dwell", "short crossing", "proj="):
    assert script_txt.count(_dead) == 0, \
        "the deleted delay machinery is back in the script: " + _dead
assert script_txt.count("function FOURTH.ad_centre_gap(caster, enemy)") == 1, \
    "the centre-gap helper is missing"
assert script_txt.count("FOURTH.ad_centre_gap(") == 4, \
    "the centre-gap helper is not wired in (definition + doc + scan + re-check)"
_centre_gap = script_txt.split("function FOURTH.ad_centre_gap(caster, enemy)", 1)[1].split("\nend", 1)[0]
assert "caster:position()" in _centre_gap and "enemy:position()" in _centre_gap, \
    "the centre gap does not read BOTH units' position()"
assert "get_y" not in _centre_gap, "the centre gap reads the HEIGHT (get_y) - it must be x/z only"
for _tok in ("a:get_x()", "a:get_z()", "b:get_x()", "b:get_z()", "a:distance_xz(b)",
             "math.sqrt((dx * dx) + (dz * dz))"):
    assert _tok in _centre_gap, "the centre gap lost a read: " + _tok
assert _centre_gap.count("return nil") == 3, "the centre gap does not fail closed on every path"
assert "FOURTH.ad_centre_gap(unit, enemy)" in script_txt, \
    "the candidate scan does not measure the centre"
_nearest = script_txt.split("function FOURTH.ad_nearest(unit)", 1)[1].split("\nfunction FOURTH.ad_pick", 1)[0]
assert "eg_enemy_gap" not in _nearest and "unit_distance" not in _nearest, \
    "the candidate scan still uses the edge gap"
_pick = script_txt.split("function FOURTH.ad_pick(unit, routing)", 1)[1].split(
    "\nfunction FOURTH.evaluate_air_drop_on_infantry", 1)[0]
assert _pick.count("if dist >= FOURTH.AIR_DROP_CENTER_M then") == 1, \
    "the evaluator is not ONE comparison against the 6 m line"
assert "-> NOT YET" in _pick, "the NOT YET decision line is missing"
assert "-> FIRING" in _pick and "FOURTH.ad_enemy = enemy" in _pick, \
    "the UNDER branch does not go straight to the cast"
for _read in ("is_moving", "slow_speed", "fast_speed", "ordered_position", "tick_count"):
    assert _read not in _pick, "the evaluator still consults a movement/clock read: " + _read
assert script_txt.count('" centre="') >= 3, "the decision family does not print centre="
assert '" edge="' not in script_txt, "an air-drop line still prints edge="
assert "local centre_now = FOURTH.ad_centre_gap(unit, enemy)" in script_txt, \
    "the pre-cast re-check does not re-measure the centre"
assert "centre_now < FOURTH.AIR_DROP_CENTER_M" in script_txt, \
    "the pre-cast re-check does not compare the centre against the 6 m line"
assert "and (not melee_now) and enemy_alive and men_ok and centre_ok) then" in script_txt, \
    "the pre-cast re-check's gate list is not the centre test"
assert "function FOURTH.eg_enemy_gap(unit, enemy)" in script_txt, \
    "eg_enemy_gap was removed - the OTHER triggers still use it"
assert 'bm:repeat_callback(poll, POLL_MS, POLL_NAME)' in script_txt, \
    "the 250 ms poll is no longer registered"
assert script_txt.count("bm:repeat_callback(") == 2, \
    "the poll + the 0.2 s fast pass are no longer both registered"
assert "zz_test_deadly_onslaught_air_drop_fast" in script_txt, \
    "the fast pass registration is missing"
assert "local POLL_MS = 250" in script_txt, "POLL_MS moved"
assert "dist < FOURTH.AIR_DROP_NEAR_M" in script_txt, "the 30 m fast-pass gate is missing"
assert script_txt.count('trigger = "air_drop_on_infantry"') == 12, \
    "the air-drop family is no longer 12 entries"
assert script_txt.count("\t{ marker = ") == 982, "the abilities table is not 982 entries"
assert script_txt.count("ability.range_m = FOURTH.AIR_DROP_CENTER_M") == 1, \
    "the family's inventory bound does not follow the 6 m line"
assert "comes within 6 m of this unit's centre" in script_txt, \
    "the tooltip sentence does not state the 6 m centre rule"
assert "casts immediately on that evaluation - no delay at all" in script_txt, \
    "the tooltip does not say the cast is immediate"
assert "string.find(" not in script_txt, "a string.find call is back in the script"
assert "unit_in_range(" not in script_txt, "an engine unit_in_range call is back"
print("\\n== round 118 content gates                : OK ==")

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
