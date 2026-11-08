# -*- coding: utf-8 -*-
"""Round-84 edits (CORRECTED per the user's two out-of-band corrections).

CORRECTION 1 - GLORIOUS DEATH: the candidate set is SLAYER UNITS ONLY.
  * the owner does NOT have to be in melee if a Slayer ally is;
  * (a) an in-melee SLAYER ally (other than self, lowest health) -> target it;
  * (b) else the OWNER itself ONLY IF it is a Slayer AND in melee -> self;
  * (c) else SILENT.  A NON-Slayer ally is NEVER offered (the old "any
    in-melee ally" fallback is REMOVED).
  * who is a Slayer: FOURTH.slayer_keys, the land_units key list DERIVED FROM
    THE GAME'S OWN DATA, tested by EXACT WHOLE-KEY equality (no string search).

CORRECTION 2 - GHOUL KING OF USHORAN: the HYSTERESIS IS REMOVED.
  * plain rule: fire when own health <= 75%;
  * repeat attempts are held back by the EXISTING readiness gate + the
    engine's own cooldown + the rejection-informed back-off only.

Applies to the REAL Desktop files (live + annotated) and writes copies to
h84work/next/. Every anchor asserted; line endings stay LF.
"""
import io, os, hashlib

T = "\t"
DESK = "C:/Users/vlady/Desktop"
SRC_LIVE = DESK + "/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"
SRC_ANN  = DESK + "/WH3_auto_ability_annotated.lua"
OUT_DIR  = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "h84work", "next")
os.makedirs(OUT_DIR, exist_ok=True)

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

def key_block():
    return "\n".join('%s["%s"] = true,' % (T, k) for k in SLAYER_KEYS)

def live_gd():
    return (
"-- THE SLAYER TYPE-KEY LIST (this round). The engine's battle_unit:type()\n"
"-- answers the unit's land_units key (the vanilla API dump: \"the unit type of\n"
"-- the unit, from the land_units table\"), and the mod already reads exactly\n"
"-- that key in the identity watch - so a genuine Slayer CAN be recognised from\n"
"-- script. The list below is DERIVED FROM THE GAME'S OWN DATA, not hand-\n"
"-- written: every land_units key whose own key contains \"slayer\" or\n"
"-- \"doomseeker\" was extracted from the game dump's localisation table\n"
"-- (%LOCALAPPDATA%\\Temp\\wh3\\land_units.loc.tsv - its\n"
"-- land_units_onscreen_name_<key> rows) and copied here VERBATIM:\n"
"--   wh_main_dwf_inf_slayers, wh2_dlc10_dwf_inf_giant_slayers,\n"
"--   wh3_dlc25_dwf_cha_daemon_slayer, wh3_dlc25_dwf_cha_dragon_slayer,\n"
"--   wh3_dlc25_dwf_inf_slayer_pirates, wh3_dlc25_dwf_inf_slayer_pirates_ror,\n"
"--   wh3_dlc25_dwf_inf_slayers_grudge_unit, wh_dlc06_dwf_inf_dragonback_slayers_0,\n"
"--   wh3_dlc25_dwf_inf_doomseekers, wh3_dlc25_dwf_inf_doomseekers_ror.\n"
"-- Membership is EXACT WHOLE-KEY equality (ONE table read) - the banned\n"
"-- string.find never runs, so a near-miss key (the Bretonnian ROR\n"
"-- \"Beastslayers of Bastonne\", whose own key carries no \"slayer\") is\n"
"-- correctly NOT a Slayer. LIMIT: a Slayer whose key does not spell it (e.g.\n"
"-- Gotrek) is a deliberate under-approximation - such a unit is simply not\n"
"-- offered to the engine by this trigger.\n"
"FOURTH.slayer_keys = {\n" + key_block() + "\n}\n"
"\n"
"-- true only for a genuine Slayer unit: the engine's type() key is in the list\n"
"-- above. A missing, raising or non-string read is NOT a Slayer (fail-safe).\n"
"-- ONE pcall'd read, ONE table lookup - no string operation of any kind.\n"
"function FOURTH.is_slayer(unit)\n"
+ T + "local ok, t = pcall(function() return unit:type() end)\n"
+ T + "if not ok or type(t) ~= \"string\" then return false end\n"
+ T + "return FOURTH.slayer_keys[t] == true\n"
"end\n"
"\n"
"-- GLORIOUS DEATH: the mod's FIRST ally-targeting ability, and its first\n"
"-- trigger that does NOT require the OWNER to be in melee. THE CANDIDATE SET\n"
"-- IS SLAYER UNITS ONLY: it fires when a SLAYER unit in the tracked army is\n"
"-- in melee - another SLAYER ally OR the owner itself (a Slayer character\n"
"-- such as Ungrim). A unit is a Slayer exactly when its land_units type key\n"
"-- is in FOURTH.slayer_keys.\n"
"--   (a) an in-melee SLAYER ally (other than self) is preferred - the\n"
"--       lowest-health one; the cast goes to that ally;\n"
"--   (b) else, ONLY when the OWNER itself is a Slayer AND in melee, the cast\n"
"--       falls back to SELF;\n"
"--   (c) otherwise - SILENT.\n"
"-- A NON-Slayer ally is NEVER offered to the engine: the old \"any in-melee\n"
"-- ally\" fallback is REMOVED, so a non-Slayer is never targeted by this\n"
"-- ability. The chosen unit is left in FOURTH.cast_target for the dispatch to\n"
"-- pass to perform_special_ability(key, target).\n"
"function FOURTH.evaluate_glorious_death(unit, routing)\n"
+ T + "local reason = nil\n"
+ T + "if not routing then\n"
+ T + T + "local self_id = tostring(unit:unique_ui_id())\n"
+ T + T + "local best_unit, best_hp = nil, nil\n"
+ T + T + "for i = 1, #tracked_units do\n"
+ T + T + T + "local other = tracked_units[i] and tracked_units[i].unit\n"
+ T + T + T + "if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then\n"
+ T + T + T + T + "if tostring(other:unique_ui_id()) ~= self_id\n"
+ T + T + T + T + T + "and other:is_in_melee() and not unit_is_routing(other)\n"
+ T + T + T + T + T + "and FOURTH.is_slayer(other) then\n"
+ T + T + T + T + T + "local hp = FOURTH.context_value(other, \"HealthPercent\")\n"
+ T + T + T + T + T + "if type(hp) == \"number\" and (best_hp == nil or hp < best_hp) then\n"
+ T + T + T + T + T + T + "best_hp, best_unit = hp, other\n"
+ T + T + T + T + T + "end\n"
+ T + T + T + T + "end\n"
+ T + T + T + "end\n"
+ T + T + "end\n"
+ T + T + "if best_unit ~= nil then\n"
+ T + T + T + "FOURTH.cast_target = best_unit\n"
+ T + T + T + "reason = \"slayer ally in melee (priority)\"\n"
+ T + T + "elseif FOURTH.is_slayer(unit) and unit:is_in_melee() then\n"
+ T + T + T + "FOURTH.cast_target = unit\n"
+ T + T + T + "reason = \"self slayer fallback (in melee)\"\n"
+ T + T + "end\n"
+ T + "end\n"
+ T + "return reason\n"
"end\n"
)

def ann_gd():
    return (
"-- THE SLAYER TYPE-KEY LIST (this round). battle_unit:type() answers the\n"
"-- unit's land_units key; the list below was DERIVED FROM THE GAME'S OWN\n"
"-- DATA - the game dump's land_units localisation table\n"
"-- (%LOCALAPPDATA%\\Temp\\wh3\\land_units.loc.tsv, its\n"
"-- land_units_onscreen_name_<key> rows): every land_units key whose own key\n"
"-- contains \"slayer\" or \"doomseeker\", copied verbatim. Membership is EXACT\n"
"-- WHOLE-KEY equality - one table read, no string search of any kind - so a\n"
"-- near-miss key (the Bretonnian ROR \"Beastslayers of Bastonne\", whose key\n"
"-- carries no \"slayer\") is correctly not a Slayer. A Slayer whose key does\n"
"-- not spell it (Gotrek) is a deliberate under-approximation - such a unit is\n"
"-- simply not offered to the engine by this trigger.\n"
"FOURTH.slayer_keys = {\n" + key_block() + "\n}\n"
"\n"
"-- true only for a genuine Slayer unit (the engine's type() key is in the\n"
"-- list above; a missing/non-string read is not a Slayer).\n"
"function FOURTH.is_slayer(unit)\n"
+ T + "local ok, t = pcall(function() return unit:type() end)\n"
+ T + "if not ok or type(t) ~= \"string\" then return false end\n"
+ T + "return FOURTH.slayer_keys[t] == true\n"
"end\n"
"\n"
"-- GLORIOUS DEATH: the ally-targeting ability whose trigger does NOT require\n"
"-- the OWNER to be in melee. THE CANDIDATE SET IS SLAYER UNITS ONLY - a unit\n"
"-- is a Slayer exactly when its land_units type key is in FOURTH.slayer_keys:\n"
"-- (a) an in-melee SLAYER ally (other than self, lowest health) is preferred;\n"
"-- (b) else the OWNER itself ONLY IF it is a Slayer AND in melee (self-cast);\n"
"-- (c) otherwise SILENT. A NON-Slayer ally is NEVER offered to the engine.\n"
"-- The chosen unit is left in FOURTH.cast_target for the dispatch to pass to\n"
"-- perform_special_ability(key, target).\n"
"function FOURTH.evaluate_glorious_death(unit, routing)\n"
+ T + "if not routing then\n"
+ T + T + "local self_id = tostring(unit:unique_ui_id())\n"
+ T + T + "local best_unit, best_hp = nil, nil\n"
+ T + T + "for i = 1, #tracked_units do\n"
+ T + T + T + "local other = tracked_units[i] and tracked_units[i].unit\n"
+ T + T + T + "if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then\n"
+ T + T + T + T + "if tostring(other:unique_ui_id()) ~= self_id\n"
+ T + T + T + T + T + "and other:is_in_melee() and not unit_is_routing(other)\n"
+ T + T + T + T + T + "and FOURTH.is_slayer(other) then\n"
+ T + T + T + T + T + "local hp = FOURTH.context_value(other, \"HealthPercent\")\n"
+ T + T + T + T + T + "if type(hp) == \"number\" and (best_hp == nil or hp < best_hp) then\n"
+ T + T + T + T + T + T + "best_hp, best_unit = hp, other\n"
+ T + T + T + T + T + "end\n"
+ T + T + T + T + "end\n"
+ T + T + T + "end\n"
+ T + T + "end\n"
+ T + T + "if best_unit ~= nil then\n"
+ T + T + T + "FOURTH.cast_target = best_unit\n"
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

def live_ush():
    return (
"-- GHOUL KING OF USHORAN: fire when the unit's OWN health is at or below 75%,\n"
"-- read live. NO HYSTERESIS - removed this round after a field-test defect: a\n"
"-- unit under sustained damage may never climb back above a second threshold,\n"
"-- so a re-arm gate would disarm this trigger for good. Repeat attempts are\n"
"-- held back by the EXISTING machinery only - the readiness gate\n"
"-- (can_perform_special_ability), the ability's own engine cooldown and the\n"
"-- rejection-informed back-off - never by a second health threshold.\n"
"function FOURTH.evaluate_ushoran_health(unit, routing)\n"
+ T + "local reason = nil\n"
+ T + "if not routing then\n"
+ T + T + "local hp = FOURTH.context_value(unit, \"HealthPercent\")\n"
+ T + T + "if type(hp) == \"number\" and hp <= 75 then\n"
+ T + T + T + "reason = string.format(\"health %d%% (<= 75%%)\", math.floor(hp))\n"
+ T + T + "end\n"
+ T + "end\n"
+ T + "return reason\n"
"end\n"
)

def ann_ush():
    return (
"-- GHOUL KING OF USHORAN: fire when the unit's OWN health is at or below 75%,\n"
"-- read live. NO HYSTERESIS (removed this round - a second health threshold\n"
"-- could disarm the trigger for good under sustained damage). Repeat attempts\n"
"-- are held back by the readiness gate, the engine cooldown and the\n"
"-- rejection-informed back-off only.\n"
"function FOURTH.evaluate_ushoran_health(unit, routing)\n"
+ T + "if not routing then\n"
+ T + T + "local hp = FOURTH.context_value(unit, \"HealthPercent\")\n"
+ T + T + "if type(hp) == \"number\" and hp <= 75 then\n"
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
# 1) remove the ushoran hysteresis field + its comment
live = repl(live,
    "-- the per-unit hysteresis flag for Ghoul King of Ushoran: true once the unit\n"
    "-- has been seen above the re-arm threshold (80%), so a unit that stays low\n"
    "-- does not re-cast on every guard window.\n"
    "FOURTH.ushoran_high = {}\n",
    "", "live ushoran field")
# 2) replace the glorious-death region (slayer list + is_slayer + evaluator)
live = slice_replace(live,
    "-- GLORIOUS DEATH: the mod's FIRST ally-targeting ability. When in melee,",
    "\n-- THE TRIGGER -> EVALUATOR MAP",
    live_gd(), "live gd region")
# 3) replace the ushoran evaluator (now ends right before the new slayer list)
live = slice_replace(live,
    "-- GHOUL KING OF USHORAN: fire when",
    "\n-- THE SLAYER TYPE-KEY LIST (this round).",
    live_ush(), "live ushoran eval")
# 4) update the block-2 header comment (the two-state wording)
live = repl(live,
    "-- chunk compiles at Lua's 200-local limit); their two pieces of per-unit\n"
    "-- state (ushoran_high, cast_target) are fields too - NO new chunk locals.\n",
    "-- chunk compiles at Lua's 200-local limit); their per-unit state\n"
    "-- (cast_target, plus the Slayer key list below) rides the same bag -\n"
    "-- NO new chunk locals.\n",
    "live block-2 header comment")

# ================================================================== ANN
ann = io.open(SRC_ANN, encoding="utf-8", newline="").read()
assert "\r" not in ann
ann = repl(ann,
    "FOURTH.ushoran_high = {}\nFOURTH.cast_target = nil",
    "FOURTH.cast_target = nil", "ann ushoran field")
ann = slice_replace(ann,
    "-- GLORIOUS DEATH: the mod's FIRST ally-targeting ability. When in melee,",
    "\n-- The trigger -> evaluator map",
    ann_gd(), "ann gd region")
ann = slice_replace(ann,
    "-- GHOUL KING OF USHORAN: fire when",
    "\n-- THE SLAYER TYPE-KEY LIST (this round).",
    ann_ush(), "ann ushoran eval")
ann = repl(ann,
    "-- FOURTH helper bag (the chunk compiles at Lua's 200-local limit); their two\n"
    "-- pieces of per-unit state (ushoran_high, cast_target) are fields too.\n",
    "-- FOURTH helper bag (the chunk compiles at Lua's 200-local limit); their\n"
    "-- per-unit state (cast_target, plus the Slayer key list below) rides the\n"
    "-- same bag too.\n",
    "ann block-2 header comment")

# =========================================================== postconditions
def post(name, src, is_live):
    n_and = src.count("and not routing")
    n_old_guard = src.count("unit:is_in_melee() and not routing")
    n_list = sum(src.count('["%s"] = true' % k) for k in SLAYER_KEYS)
    print("%s: 'and not routing' x%d (want 6), old melee guard x%d (want 3), slayer keys x%d/10, "
          "ushoran_high x%d (want 0)"
          % (name, n_and, n_old_guard, n_list, src.count("ushoran_high")))
    assert n_and == 6, (name, n_and)
    assert n_old_guard == 3, (name, n_old_guard)
    assert n_list == 10, (name, n_list)
    assert src.count("ushoran_high") == 0, name
    assert src.count("FOURTH.slayer_keys = {") == 1, name
    assert src.count("function FOURTH.is_slayer(unit)") == 1, name
    assert src.count("return FOURTH.slayer_keys[t] == true") == 1, name
    assert src.count("function FOURTH.evaluate_glorious_death(unit, routing)") == 1, name
    assert src.count("function FOURTH.evaluate_ushoran_health(unit, routing)") == 1, name
    if is_live:
        assert src.count('reason = "slayer ally in melee (priority)"') == 1, name
        assert src.count('reason = "self slayer fallback (in melee)"') == 1, name
        assert src.count('reason = "ally in melee (priority)"') == 0, name
        assert src.count('reason = "self fallback (no other melee ally)"') == 0, name
        assert src.count('string.format("health %d%% (<= 75%%)"') == 1, name
        assert src.count("string.find(") == 0, name
    else:
        assert src.count("log(") == 0, name
        assert src.count("string.find") == 0, name
        assert src.count('reason = "') == 0, name

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
