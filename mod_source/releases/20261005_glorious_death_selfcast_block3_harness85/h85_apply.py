# -*- coding: utf-8 -*-
"""Round-85 edits: JOB 1 (Glorious Death self-cast) + JOB 2 (block-3, 38 entries).

JOB 1 - GLORIOUS DEATH: the TRIGGER is UNCHANGED from harness 84 (the Slayer-only
  candidate set: an in-melee Slayer ally arms it, else the owner itself arms it
  only when the owner is a Slayer and in melee, else silent). THE CAST TARGET IS
  NOW ALWAYS THE OWNER ITSELF: the ability is self-centred, so the caster is
  never ordered to walk to the Slayer ally. The old write of the ally into
  FOURTH.cast_target is GONE; every arm writes the OWNER into cast_target. The
  reason strings are reworded: 'slayer in melee (self-cast)' /
  'self in melee (self-cast)'.

JOB 2 - BLOCK 3: 38 new approved entries (35 on the EXISTING in-melee-self
  evaluator = trigger melee_unwavering; 3 on the charge-or-melee trigger =
  trigger charge_or_melee). No new evaluator, no new chunk locals (table rows
  only).

NOTE ON THE COUNT: the task text said "34 abilities (31 in-melee-self + 3
  charge-or-melee)" but its EXPLICIT key list holds 35 in-melee-self keys
  (35 + 3 = 38); every one of the 35 is `approved (in-melee self)` in the
  tracker. All 38 listed keys are implemented.

Applies to the REAL Desktop files (live + annotated) and writes copies to
h85work/next/. Every anchor asserted; line endings stay LF.
"""
import io, os, hashlib

T = "\t"
DESK = "C:/Users/vlady/Desktop"
SRC_LIVE = DESK + "/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"
SRC_ANN  = DESK + "/WH3_auto_ability_annotated.lua"
OUT_DIR  = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "h85work", "next")
os.makedirs(OUT_DIR, exist_ok=True)

# (marker, display name, db key) - trigger melee_unwavering (the EXISTING evaluator)
BLOCK3_SELF = [
    ("legbiter", "Legbiter", "wh3_dlc29_weapon_abilities_legbiter"),
    ("hellfire_sword", "Hellfire Sword", "wh_main_weapon_abilities_hellfire_sword"),
    ("helm_of_discord", "Helm of Discord", "wh_main_weapon_abilities_helm_of_discord"),
    ("helm_of_many_eyes", "Helm of Many Eyes", "wh_dlc01_item_passive_helm_of_many_eyes"),
    ("heroic_killing_blow_2", "Heroic Killing Blow", "wh3_main_pro_character_abilities_heroic_killing_blow_2"),
    ("heroic_killing_blow_dlc07", "Heroic Killing Blow", "wh_dlc07_character_abilities_heroic_killing_blow"),
    ("heroic_killing_blow_main", "Heroic Killing Blow", "wh_main_character_abilities_heroic_killing_blow"),
    ("hydra_blade", "Hydra Blade", "wh2_main_weapon_abilities_hydra_blade"),
    ("inevitable_horror", "Inevitable Horror", "wh3_dlc26_character_abilities_inevitable_horror"),
    ("karaghul", "Karaghul", "wh2_pro08_weapon_abilities_karaghul"),
    ("killing_blow_1", "Killing Blow", "wh3_main_pro_character_abilities_heroic_killing_blow_1"),
    ("killing_blow", "Killing Blow", "wh_main_unit_abilities_killing_blow"),
    ("liarsbane", "Liarsbane", "wh3_dlc25_weapon_abilities_liarsbane"),
    ("lightning_reflexes", "Lightning Reflexes", "wh2_dlc11_lord_abilities_lightning_reflexes"),
    ("locus_of_beguilement", "Locus of Beguilement", "wh3_main_character_abilities_locus_of_beguilement"),
    ("locus_of_grace", "Locus of Grace", "wh3_main_character_abilities_locus_of_grace"),
    ("locus_of_wrath", "Locus of Wrath", "wh3_main_character_abilities_locus_of_wrath"),
    ("lucky_banner", "Lucky Banner", "wh2_dlc15_item_abilities_lucky_banner"),
    ("mace_of_ulumak", "Mace of Ulumak", "wh2_dlc13_weapon_abilities_mace_of_ulumak"),
    ("mananns_luck", "Manann's Luck", "wh2_dlc11_lord_abilities_mananns_luck"),
    ("master_of_the_skies", "Master of the Skies", "wh2_dlc12_lord_abilities_master_of_the_skies"),
    ("mimic_waaagh", "Mirror (Waaagh!)", "wh2_dlc15_unit_abilities_mimic_waaagh"),
    ("mimic_grom_waaagh", "Mirror (Grom's Big Waaagh!)", "wh2_dlc15_unit_abilities_mimic_grom_waaagh"),
    ("monstrous_strength", "Monstrous Strength", "wh2_dlc13_lord_abilities_monstrous_strength"),
    ("mortal_blow", "Mortal Blow", "wh3_main_daemon_arms_abilities_mortal_blow"),
    ("mortal_blow_upgraded", "Mortal Blow (Upgraded)", "wh3_main_daemon_arms_abilities_mortal_blow_upgraded"),
    ("mumbo_jumbo_chant", "Mumbo-Jumbo Chant", "wh3_dlc26_character_abilities_mumbo_jumbo_chant"),
    ("strike_of_nagash", "Necrostrike", "wh2_dlc09_character_abilities_strike_of_nagash"),
    ("nurgles_favoured_son", "Nurgle's Favoured Son", "wh3_dlc25_lord_abilities_nurgles_favoured_son"),
    ("opal_amulet", "Opal Amulet", "wh_main_item_abilities_opal_amulet"),
    ("oracle_of_eternity", "Oracle of Eternity", "wh3_main_lord_abilities_oracle_of_eternity"),
    ("pendant_of_slaanesh", "Pendant of Slaanesh", "wh_main_item_abilities_pendant_of_slaanesh"),
    ("plaguefathers_oration", "Plaguefather's Oration", "wh3_main_lord_abilities_plaguefathers_oration"),
    ("primal_roar", "Primal Roar", "wh2_dlc13_lord_abilities_primal_roar"),
    ("puncture", "Puncture", "wh3_dlc26_character_abilities_puncture"),
]
# (marker, display name, db key) - trigger charge_or_melee (the EXISTING evaluator)
BLOCK3_CHARGE = [
    ("heart_piercing", "Heart Piercing", "wh2_dlc11_lord_abilities_heart_piercing"),
    ("horn_of_the_first_beast", "Horn of the First Beast", "wh_dlc03_item_abilities_horn_of_the_first_beast"),
    ("morglor_the_mangler", "Morglor the Mangler", "wh3_dlc26_weapon_abilities_morglor_the_mangler"),
]

assert len(BLOCK3_SELF) == 35, len(BLOCK3_SELF)
assert len(BLOCK3_CHARGE) == 3, len(BLOCK3_CHARGE)

def entry(marker, name, key, trigger):
    return (T + '{ marker = "' + marker + '", name = "' + name + '", trigger = "' + trigger + '",\n'
            + T + T + 'badge = "zz_auto_badge_' + marker + '",\n'
            + T + T + 'keys = { "' + key + '" },\n'
            + T + T + 'ox = 0, oy = 0 },')

HEADER = (
    T + "-- BLOCK 3 (this round) - THE 38 APPROVED ENTRIES. The 35 in-melee-self\n"
    + T + "-- abilities ride the EXISTING shared melee_unwavering evaluator (no new\n"
    + T + "-- evaluator); the 3 charge-or-melee abilities ride the EXISTING\n"
    + T + "-- charge_or_melee evaluator (the one Fangspike uses). Each carries its\n"
    + T + "-- own marker and badge id, so the field log tells them apart; the\n"
    + T + "-- trigger emits the SAME distinct reason text the evaluator already\n"
    + T + "-- writes. Nothing else in the table changes."
)

def block3_rows():
    rows = [HEADER]
    for m, n, k in BLOCK3_SELF:
        rows.append(entry(m, n, k, "melee_unwavering"))
    for m, n, k in BLOCK3_CHARGE:
        rows.append(entry(m, n, k, "charge_or_melee"))
    return "\n".join(rows)

# ---- the ABILITIES-table anchor (its last entry + the closing brace) ---------
TABLE_TAIL = (
    T + '{ marker = "glorious_death", name = "Glorious Death", trigger = "glorious_death",\n'
    + T + T + 'badge = "zz_auto_badge_glorious_death",\n'
    + T + T + 'keys = { "wh3_dlc25_lord_abilities_glorious_death" },\n'
    + T + T + 'ox = 0, oy = 0 },\n'
    + '}'
)
TABLE_TAIL_NEW = (
    T + '{ marker = "glorious_death", name = "Glorious Death", trigger = "glorious_death",\n'
    + T + T + 'badge = "zz_auto_badge_glorious_death",\n'
    + T + T + 'keys = { "wh3_dlc25_lord_abilities_glorious_death" },\n'
    + T + T + 'ox = 0, oy = 0 },\n'
    + block3_rows() + "\n"
    + '}'
)

# ---- the Glorious Death evaluator + cast_target comment ---------------------
CAST_COMMENT_OLD = (
    "-- where the ALLY-targeting evaluator (Glorious Death) leaves the unit it\n"
    "-- chose. The dispatch clears it before each evaluate and passes it to the\n"
    "-- cast, so a self-targeted ability can never inherit a stale ally.\n"
    "FOURTH.cast_target = nil\n"
)
CAST_COMMENT_NEW = (
    "-- where an evaluator leaves the unit it chose for the cast. Glorious Death\n"
    "-- now ALWAYS leaves the OWNER itself - the ability is self-centred, so the\n"
    "-- caster is never ordered to walk to an ally. The dispatch clears it before\n"
    "-- each evaluate and passes it to the cast, so a self-targeted ability can\n"
    "-- never inherit a stale unit.\n"
    "FOURTH.cast_target = nil\n"
)

def live_gd():
    return (
"-- GLORIOUS DEATH: the mod's FIRST ability whose trigger does NOT require the\n"
"-- OWNER to be in melee. THE TRIGGER IS UNCHANGED from the previous round and\n"
"-- remains SLAYER-ONLY: a unit is a Slayer exactly when its land_units type\n"
"-- key is in FOURTH.slayer_keys.\n"
"--   (a) an in-melee SLAYER ally (other than self) arms the ability; else\n"
"--   (b) the OWNER itself arms it ONLY when it is a Slayer AND in melee; else\n"
"--   (c) SILENT. A NON-Slayer ally is NEVER offered to the engine.\n"
"-- THE FIELD-TEST FIX (this round): THE CAST TARGET IS ALWAYS THE OWNER\n"
"-- ITSELF. The ability is self-centred, so the caster must never be ordered\n"
"-- to walk to the Slayer ally - the previous round passed that ally as the\n"
"-- cast target, which made the Lord reposition to it. Every firing arm writes\n"
"-- the OWNER into FOURTH.cast_target, which the dispatch passes to\n"
"-- perform_special_ability(key, target); the reason strings say so.\n"
"function FOURTH.evaluate_glorious_death(unit, routing)\n"
+ T + "local reason = nil\n"
+ T + "if not routing then\n"
+ T + T + "local self_id = tostring(unit:unique_ui_id())\n"
+ T + T + "local slayer_in_melee = false\n"
+ T + T + "for i = 1, #tracked_units do\n"
+ T + T + T + "local other = tracked_units[i] and tracked_units[i].unit\n"
+ T + T + T + "if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then\n"
+ T + T + T + T + "if tostring(other:unique_ui_id()) ~= self_id\n"
+ T + T + T + T + T + "and other:is_in_melee() and not unit_is_routing(other)\n"
+ T + T + T + T + T + "and FOURTH.is_slayer(other) then\n"
+ T + T + T + T + T + "slayer_in_melee = true\n"
+ T + T + T + T + T + "break\n"
+ T + T + T + T + "end\n"
+ T + T + T + "end\n"
+ T + T + "end\n"
+ T + T + "if slayer_in_melee then\n"
+ T + T + T + "FOURTH.cast_target = unit\n"
+ T + T + T + "reason = \"slayer in melee (self-cast)\"\n"
+ T + T + "elseif FOURTH.is_slayer(unit) and unit:is_in_melee() then\n"
+ T + T + T + "FOURTH.cast_target = unit\n"
+ T + T + T + "reason = \"self in melee (self-cast)\"\n"
+ T + T + "end\n"
+ T + "end\n"
+ T + "return reason\n"
"end\n"
)

def ann_gd():
    return (
"-- GLORIOUS DEATH: the ability whose trigger does NOT require the OWNER to be\n"
"-- in melee. THE TRIGGER IS UNCHANGED and SLAYER-ONLY (a unit is a Slayer\n"
"-- exactly when its land_units type key is in FOURTH.slayer_keys):\n"
"-- (a) an in-melee SLAYER ally (other than self) arms it; else (b) the OWNER\n"
"-- itself arms it ONLY when it is a Slayer AND in melee; else silent. A\n"
"-- NON-Slayer ally is NEVER offered. FIELD-TEST FIX (this round): THE CAST\n"
"-- TARGET IS ALWAYS THE OWNER ITSELF - the ability is self-centred, so the\n"
"-- caster is never ordered to walk to the Slayer ally. Every arm writes the\n"
"-- OWNER into FOURTH.cast_target for the dispatch to pass to\n"
"-- perform_special_ability(key, target).\n"
"function FOURTH.evaluate_glorious_death(unit, routing)\n"
+ T + "if not routing then\n"
+ T + T + "local self_id = tostring(unit:unique_ui_id())\n"
+ T + T + "local slayer_in_melee = false\n"
+ T + T + "for i = 1, #tracked_units do\n"
+ T + T + T + "local other = tracked_units[i] and tracked_units[i].unit\n"
+ T + T + T + "if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then\n"
+ T + T + T + T + "if tostring(other:unique_ui_id()) ~= self_id\n"
+ T + T + T + T + T + "and other:is_in_melee() and not unit_is_routing(other)\n"
+ T + T + T + T + T + "and FOURTH.is_slayer(other) then\n"
+ T + T + T + T + T + "slayer_in_melee = true\n"
+ T + T + T + T + T + "break\n"
+ T + T + T + T + "end\n"
+ T + T + T + "end\n"
+ T + T + "end\n"
+ T + T + "if slayer_in_melee then\n"
+ T + T + T + "FOURTH.cast_target = unit\n"
+ T + T + T + "return true\n"
+ T + T + "end\n"
+ T + T + "if FOURTH.is_slayer(unit) and unit:is_in_melee() then\n"
+ T + T + T + "FOURTH.cast_target = unit\n"
+ T + T + T + "return true\n"
+ T + T + "end\n"
+ T + "end\n"
+ T + "return false\n"
"end\n"
)

def repl(src, old, new, label):
    n = src.count(old)
    assert n == 1, "%s: old anchor x%d" % (label, n)
    return src.replace(old, new, 1)

def slice_replace(src, start_marker, end_marker, new, label):
    a = src.count(start_marker)
    assert a == 1, "%s: start anchor x%d" % (label, a)
    i = src.index(start_marker)
    j = src.index(end_marker, i)
    return src[:i] + new + src[j:]

# ================================================================== LIVE
live = io.open(SRC_LIVE, encoding="utf-8", newline="").read()
assert "\r" not in live
live = repl(live, TABLE_TAIL, TABLE_TAIL_NEW, "live block-3 table rows")
live = repl(live, CAST_COMMENT_OLD, CAST_COMMENT_NEW, "live cast_target comment")
live = slice_replace(live,
    "-- GLORIOUS DEATH: the mod's FIRST ally-targeting ability, and its first",
    "\n-- THE TRIGGER -> EVALUATOR MAP",
    live_gd(), "live GD evaluator")

# ================================================================== ANN
ann = io.open(SRC_ANN, encoding="utf-8", newline="").read()
assert "\r" not in ann
ann = repl(ann, TABLE_TAIL, TABLE_TAIL_NEW, "ann block-3 table rows")
ann = slice_replace(ann,
    "-- GLORIOUS DEATH: the ally-targeting ability whose trigger does NOT require",
    "\n-- The trigger -> evaluator map",
    ann_gd(), "ann GD evaluator")

# =========================================================== postconditions
def post(name, src, is_live):
    n_entries = src.count('marker = "')
    n_keys = src.count("keys = {")
    n_mu = count_plain(src, 'trigger = "melee_unwavering"')
    n_cm = count_plain(src, 'trigger = "charge_or_melee"')
    n_miss = 0
    for m, n, k in BLOCK3_SELF + BLOCK3_CHARGE:
        if (src.count('marker = "%s"' % m) != 1 or src.count('badge = "zz_auto_badge_%s"' % m) != 1
                or src.count('"%s"' % k) != 1):
            n_miss += 1
    n_unit = count_plain(src, "FOURTH.cast_target = unit")
    n_best = count_plain(src, "FOURTH.cast_target = best_unit")
    print("%s: markers %d (want 102), keys-lists %d (want 102), melee_unwavering %d (want 91), "
          "charge_or_melee %d (want 4), block3-missing %d (want 0), cast_target=unit %d, "
          "cast_target=best_unit %d (want 0)"
          % (name, n_entries, n_keys, n_mu, n_cm, n_miss, n_unit, n_best))
    assert n_entries == 102, (name, n_entries)
    assert n_mu == 91, (name, n_mu)
    assert n_cm == 4, (name, n_cm)
    assert n_miss == 0, (name, n_miss)
    assert n_best == 0, (name, n_best)
    assert n_unit == 2, (name, n_unit)
    assert src.count("FOURTH.slayer_keys = {") == 1, name
    assert src.count("function FOURTH.is_slayer(unit)") == 1, name
    assert src.count("return FOURTH.slayer_keys[t] == true") == 1, name
    assert src.count("and FOURTH.is_slayer(other) then") == 1, name
    assert src.count("FOURTH.is_slayer(unit) and unit:is_in_melee()") == 1, name
    assert count_plain(src, "unit:is_in_melee() and not routing") == 3, name
    assert src.count("function FOURTH.evaluate_glorious_death(unit, routing)") == 1, name
    assert src.count("FOURTH.slayer_keys = {") == 1, name
    if is_live:
        assert src.count('reason = "slayer in melee (self-cast)"') == 1, name
        assert src.count('reason = "self in melee (self-cast)"') == 1, name
        assert src.count('reason = "slayer ally in melee (priority)"') == 0, name
        assert src.count('reason = "self slayer fallback (in melee)"') == 0, name
        assert src.count("string.find(") == 0, name
    else:
        assert src.count("log(") == 0, name
        assert src.count("string.find") == 0, name
        assert src.count('reason = "') == 0, name

def count_plain(s, tok):
    n, at = 0, 1
    while True:
        i = s.find(tok, at)
        if i < 0: return n
        n += 1
        at = i + 1

post("LIVE", live, True)
post("ANN", ann, False)

io.open(SRC_LIVE, "w", encoding="utf-8", newline="\n").write(live)
io.open(SRC_ANN, "w", encoding="utf-8", newline="\n").write(ann)
io.open(os.path.join(OUT_DIR, "zz_test_deadly_onslaught.lua"), "w", encoding="utf-8", newline="\n").write(live)
io.open(os.path.join(OUT_DIR, "WH3_auto_ability_annotated.lua"), "w", encoding="utf-8", newline="\n").write(ann)
print("LIVE written %d bytes LF=%d; ANN written %d bytes LF=%d"
      % (len(live), live.count("\n"), len(ann), ann.count("\n")))
print("sha256 LIVE", hashlib.sha256(live.encode("utf-8")).hexdigest()[:32])
print("sha256 ANN ", hashlib.sha256(ann.encode("utf-8")).hexdigest()[:32])
print("ALL EDIT POSTCONDITIONS OK")
