# -*- coding: utf-8 -*-
"""Round-86 edit: the GLORIOUS DEATH RANGE GATE (the reported bug fix).

USER REPORT: "it casted before the slayer unit that was fighting was in range
of the ability." Since the fix that always casts on SELF, the engine no longer
refuses (the caster is trivially in range of itself), so the ability fires even
when the in-melee Slayer ally is far away and the 55 m aura would not reach it.

THE FIX:
  * The ally arm only counts while the owner is WITHIN the ability's effect
    range of the ally. The range is the wiki's effects line "Effect range:
    55m", implemented as the ONE named settings constant GLORIOUS_DEATH_RANGE_M.
  * The CLOSEST in-range in-melee Slayer is the one chosen (not merely the
    first / the lowest-health one), so the aura covers the chosen unit.
  * The gap is RE-CHECKED immediately before the cast; if the ally has drifted
    out of range, the cast is SKIPPED rather than wasted.
  * The owner-in-melee self-cast case is NEVER gated (casting on self is always
    in range).

Reuses the mod's EXISTING distance machinery - the charge detector's
battle_unit:unit_distance primitive (section 5); no new API calls.

NO new chunk locals beyond the one wiki constant the task requires; the
per-attempt state (FOURTH.gd_ally) and the two helpers are FOURTH fields.

Applies to the REAL Desktop files (live + annotated) and writes copies to
h86work/next/. Every anchor asserted; line endings stay LF.
"""
import io, os, hashlib

T = "\t"
DESK = "C:/Users/vlady/Desktop"
SRC_LIVE = DESK + "/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"
SRC_ANN  = DESK + "/WH3_auto_ability_annotated.lua"
OUT_DIR  = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "h86work", "next")
os.makedirs(OUT_DIR, exist_ok=True)

RANGE_CONST_LIVE = (
    "\n-- GLORIOUS DEATH'S EFFECT RANGE (this round) - WIKI-SOURCED. The\n"
    "-- ability's wiki effects line reads \"Effect range: 55m\"; the range gate\n"
    "-- below offers, and re-checks just before the cast, an in-melee Slayer\n"
    "-- ally only when the owner is within GLORIOUS_DEATH_RANGE_M metres of it.\n"
    "-- ONE place to tune the gate.\n"
    "local GLORIOUS_DEATH_RANGE_M = 55\n"
)
RANGE_CONST_ANN = (
    "\n-- GLORIOUS DEATH'S EFFECT RANGE (this round) - WIKI-SOURCED. The\n"
    "-- ability's wiki effects line reads \"Effect range: 55m\"; the range gate\n"
    "-- below offers, and re-checks just before the cast, an in-melee Slayer\n"
    "-- ally only when the owner is within GLORIOUS_DEATH_RANGE_M metres of it.\n"
    "local GLORIOUS_DEATH_RANGE_M = 55\n"
)

CAST_FIELD_LIVE = (
    "\n-- GLORIOUS DEATH's chosen ally (this round): the CLOSEST in-melee Slayer\n"
    "-- ally within GLORIOUS_DEATH_RANGE_M, kept only so the cast can RE-CHECK\n"
    "-- the gap immediately before firing. Cleared (with cast_target) before\n"
    "-- every evaluate, so it can never leak into another ability's attempt. The\n"
    "-- owner-in-melee self arm leaves it nil, so that cast is never gated.\n"
    "FOURTH.gd_ally = nil\n"
    "\n"
    "-- GLORIOUS DEATH's distance helper (this round): the gap in metres from\n"
    "-- the OWNER to a candidate Slayer ally, read through the SAME primitive\n"
    "-- the charge detector already uses (battle_unit:unit_distance, section 5).\n"
    "-- nil when the read cannot be taken.\n"
    "function FOURTH.gd_ally_gap(unit, ally)\n"
    + T + "local ok, gap = pcall(function() return ally:unit_distance(unit) end)\n"
    + T + "if ok and type(gap) == \"number\" then return gap end\n"
    + T + "return nil\n"
    "end\n"
    "\n"
    "-- true when the gap is within the ability's 55 m effect range. An\n"
    "-- UNREADABLE gap (nil) is treated as IN range (fail-open) - exactly how the\n"
    "-- charge detector treats an unknown distance - so a flaky read can never\n"
    "-- silently disable the ability.\n"
    "function FOURTH.gd_ally_in_range(unit, ally)\n"
    + T + "local gap = FOURTH.gd_ally_gap(unit, ally)\n"
    + T + "return (gap == nil) or (gap <= GLORIOUS_DEATH_RANGE_M)\n"
    "end\n"
)
CAST_FIELD_ANN = (
    "\n-- GLORIOUS DEATH's chosen ally (this round): the CLOSEST in-melee Slayer\n"
    "-- ally within GLORIOUS_DEATH_RANGE_M, kept only so the cast can RE-CHECK\n"
    "-- the gap immediately before firing. The owner-in-melee self arm leaves it\n"
    "-- nil, so that cast is never gated.\n"
    "FOURTH.gd_ally = nil\n"
    "\n"
    "-- GLORIOUS DEATH's distance helper (this round): the gap in metres from\n"
    "-- the OWNER to a candidate Slayer ally (the charge detector's own\n"
    "-- battle_unit:unit_distance primitive). nil when the read cannot be taken.\n"
    "function FOURTH.gd_ally_gap(unit, ally)\n"
    + T + "local ok, gap = pcall(function() return ally:unit_distance(unit) end)\n"
    + T + "if ok and type(gap) == \"number\" then return gap end\n"
    + T + "return nil\n"
    "end\n"
    "\n"
    "-- true when the gap is within the ability's 55 m effect range; an\n"
    "-- UNREADABLE gap (nil) is treated as IN range (fail-open).\n"
    "function FOURTH.gd_ally_in_range(unit, ally)\n"
    + T + "local gap = FOURTH.gd_ally_gap(unit, ally)\n"
    + T + "return (gap == nil) or (gap <= GLORIOUS_DEATH_RANGE_M)\n"
    "end\n"
)

def live_gd():
    return (
"-- GLORIOUS DEATH: the mod's FIRST ability whose trigger does NOT require the\n"
"-- OWNER to be in melee. THE TRIGGER stays SLAYER-ONLY: a unit is a Slayer\n"
"-- exactly when its land_units type key is in FOURTH.slayer_keys.\n"
"--   (a) an in-melee SLAYER ally (other than self) arms the ability; else\n"
"--   (b) the OWNER itself arms it ONLY when it is a Slayer AND in melee; else\n"
"--   (c) SILENT. A NON-Slayer ally is NEVER offered to the engine.\n"
"-- THE CAST TARGET IS ALWAYS THE OWNER ITSELF (the ability is self-centred, so\n"
"-- the caster must never be ordered to walk to the Slayer ally).\n"
"-- THE RANGE GATE (this round, the reported bug fix): the ally arm only counts\n"
"-- while the owner is WITHIN the ability's 55 m effect range\n"
"-- (GLORIOUS_DEATH_RANGE_M, wiki-sourced) of the ally - otherwise the aura\n"
"-- would not cover it and the cast is wasted. The CLOSEST in-range in-melee\n"
"-- Slayer is the one chosen; the gap is RE-CHECKED immediately before the cast\n"
"-- (a unit can move a little between the poll and the cast) and the cast is\n"
"-- SKIPPED if the ally has drifted out of range. The owner-in-melee self arm\n"
"-- is NEVER gated (casting on self is always in range).\n"
"function FOURTH.evaluate_glorious_death(unit, routing)\n"
+ T + "local reason = nil\n"
+ T + "if not routing then\n"
+ T + T + "local self_id = tostring(unit:unique_ui_id())\n"
+ T + T + "local best_ally = nil\n"
+ T + T + "local best_gap = nil\n"
+ T + T + "for i = 1, #tracked_units do\n"
+ T + T + T + "local other = tracked_units[i] and tracked_units[i].unit\n"
+ T + T + T + "if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then\n"
+ T + T + T + T + "if tostring(other:unique_ui_id()) ~= self_id\n"
+ T + T + T + T + T + "and other:is_in_melee() and not unit_is_routing(other)\n"
+ T + T + T + T + T + "and FOURTH.is_slayer(other) then\n"
+ T + T + T + T + T + "local gap = FOURTH.gd_ally_gap(unit, other)\n"
+ T + T + T + T + T + "if (gap == nil) or (gap <= GLORIOUS_DEATH_RANGE_M) then\n"
+ T + T + T + T + T + T + "if best_ally == nil then\n"
+ T + T + T + T + T + T + T + "best_ally, best_gap = other, gap\n"
+ T + T + T + T + T + T + "elseif gap ~= nil and (best_gap == nil or gap < best_gap) then\n"
+ T + T + T + T + T + T + T + "best_ally, best_gap = other, gap\n"
+ T + T + T + T + T + T + "end\n"
+ T + T + T + T + T + "end\n"
+ T + T + T + T + "end\n"
+ T + T + T + "end\n"
+ T + T + "end\n"
+ T + T + "if best_ally ~= nil then\n"
+ T + T + T + "if best_gap ~= nil then\n"
+ T + T + T + T + "log(\"  glorious_death ally: ui \" .. tostring(best_ally:unique_ui_id())\n"
+ T + T + T + T + T + ".. \" at \" .. string.format(\"%.1f\", best_gap) .. \"m is the CLOSEST\"\n"
+ T + T + T + T + T + ".. \" in-melee Slayer within \" .. tostring(GLORIOUS_DEATH_RANGE_M) .. \"m\")\n"
+ T + T + T + "end\n"
+ T + T + T + "FOURTH.cast_target = unit\n"
+ T + T + T + "FOURTH.gd_ally = best_ally\n"
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
"-- in melee. THE TRIGGER stays SLAYER-ONLY (a unit is a Slayer exactly when\n"
"-- its land_units type key is in FOURTH.slayer_keys):\n"
"-- (a) an in-melee SLAYER ally (other than self) arms it; else (b) the OWNER\n"
"-- itself arms it ONLY when it is a Slayer AND in melee; else silent. A\n"
"-- NON-Slayer ally is NEVER offered. THE CAST TARGET IS ALWAYS THE OWNER\n"
"-- ITSELF. THE RANGE GATE (this round): the ally arm only counts while the\n"
"-- owner is within the ability's 55 m effect range (GLORIOUS_DEATH_RANGE_M) of\n"
"-- the ally; the CLOSEST in-range in-melee Slayer is chosen; the gap is\n"
"-- re-checked immediately before the cast and the cast is SKIPPED if the ally\n"
"-- has drifted out of range. The owner-in-melee self arm is NEVER gated.\n"
"function FOURTH.evaluate_glorious_death(unit, routing)\n"
+ T + "if not routing then\n"
+ T + T + "local self_id = tostring(unit:unique_ui_id())\n"
+ T + T + "local best_ally = nil\n"
+ T + T + "local best_gap = nil\n"
+ T + T + "for i = 1, #tracked_units do\n"
+ T + T + T + "local other = tracked_units[i] and tracked_units[i].unit\n"
+ T + T + T + "if other ~= nil and other ~= unit and other:number_of_men_alive() > 0 then\n"
+ T + T + T + T + "if tostring(other:unique_ui_id()) ~= self_id\n"
+ T + T + T + T + T + "and other:is_in_melee() and not unit_is_routing(other)\n"
+ T + T + T + T + T + "and FOURTH.is_slayer(other) then\n"
+ T + T + T + T + T + "local gap = FOURTH.gd_ally_gap(unit, other)\n"
+ T + T + T + T + T + "if (gap == nil) or (gap <= GLORIOUS_DEATH_RANGE_M) then\n"
+ T + T + T + T + T + T + "if best_ally == nil then\n"
+ T + T + T + T + T + T + T + "best_ally, best_gap = other, gap\n"
+ T + T + T + T + T + T + "elseif gap ~= nil and (best_gap == nil or gap < best_gap) then\n"
+ T + T + T + T + T + T + T + "best_ally, best_gap = other, gap\n"
+ T + T + T + T + T + T + "end\n"
+ T + T + T + T + T + "end\n"
+ T + T + T + T + "end\n"
+ T + T + T + "end\n"
+ T + T + "end\n"
+ T + T + "if best_ally ~= nil then\n"
+ T + T + T + "FOURTH.cast_target = unit\n"
+ T + T + T + "FOURTH.gd_ally = best_ally\n"
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

RECHECK_LIVE = (
    T + "-- GLORIOUS DEATH RANGE RE-CHECK (this round). The Slayer-ally arm chose\n"
    + T + "-- the CLOSEST in-melee Slayer within GLORIOUS_DEATH_RANGE_M at evaluate\n"
    + T + "-- time and left it in FOURTH.gd_ally; RE-READ the gap NOW, immediately\n"
    + T + "-- before the cast - a unit can move a little between the poll and the\n"
    + T + "-- cast. If the ally has drifted beyond the ability's 55 m effect range\n"
    + T + "-- the aura would not cover it, so SKIP the cast rather than waste it.\n"
    + T + "-- The owner-in-melee self arm leaves FOURTH.gd_ally nil - never gated.\n"
    + T + "if FOURTH.gd_ally ~= nil and not FOURTH.gd_ally_in_range(unit, FOURTH.gd_ally) then\n"
    + T + T + "log(\"  glorious_death SKIPPED: the chosen in-melee Slayer ally drifted out of range\"\n"
    + T + T + T + ".. \" before the cast (the aura would not cover it) - cast not spent\")\n"
    + T + T + "FOURTH.gd_ally = nil\n"
    + T + T + "if RELEASE_CONTROL_AFTER and took_control then\n"
    + T + T + T + "local ok_release, err_release = pcall(function() uc:release_control() end)\n"
    + T + T + T + "log(\"  release_control         : ok=\" .. tostring(ok_release)\n"
    + T + T + T + T + ".. (ok_release and \"\" or (\"  ERROR: \" .. tostring(err_release))))\n"
    + T + T + "end\n"
    + T + T + "return \"held\"\n"
    + T + "end\n"
    + "\n"
)
RECHECK_ANN = (
    T + "-- GLORIOUS DEATH RANGE RE-CHECK (this round): re-read the chosen ally's\n"
    + T + "-- gap immediately before the cast; skip when it has drifted beyond the\n"
    + T + "-- ability's 55 m effect range (the aura would not cover it). The\n"
    + T + "-- owner-in-melee self arm leaves FOURTH.gd_ally nil - never gated.\n"
    + T + "if FOURTH.gd_ally ~= nil and not FOURTH.gd_ally_in_range(unit, FOURTH.gd_ally) then\n"
    + T + T + "FOURTH.gd_ally = nil\n"
    + T + T + "return \"held\"\n"
    + T + "end\n"
    + "\n"
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

def count_plain(s, tok):
    n, at = 0, 1
    while True:
        i = s.find(tok, at)
        if i < 0:
            return n
        n += 1
        at = i + 1

# GLORIOUS DEATH'S EFFECT RANGE needs one chunk-level settings local. The LIVE
# chunk sits AT Lua's 200-local ceiling, so four DEAD locals are removed first
# (the vestigial icon-read block - never called or read anywhere, and absent
# from the reading copy): ICON_INDEX, original_icon, read_icon, original_state.
DEAD_NOTE = (
    "-- THE FEEDBACK: a plain image swap on the ability icon. Static - no pulse, no blink.\n"
    "-- The icon slot is the one the vanilla layout marks with icon_index = 8 (round 21's layout read).\n"
    "-- (ROUND 86: the vestigial ICON_INDEX / original_icon / read_icon / original_state\n"
    "--  locals that used to sit here were DEAD - the read_icon helper and the two\n"
    "--  original_* savers were never called or read anywhere, and the icon-swap\n"
    "--  feedback never used them. They were removed to free local-ceiling slots for\n"
    "--  GLORIOUS_DEATH_RANGE_M (section 1). The reading copy never carried them.)\n"
)
import re as _re

# ================================================================== LIVE
live = io.open(SRC_LIVE, encoding="utf-8", newline="").read()
assert "\r" not in live
_dead = _re.compile(r"-- THE FEEDBACK:.*?\nlocal original_state = nil\n", _re.DOTALL)
assert len(_dead.findall(live)) == 1, "the dead icon block is not unique"
live = _dead.sub(DEAD_NOTE, live, count=1)
live = repl(live,
    "local CHARGE_TIME_TO_CONTACT_S = 4      -- fire when impact is this close\n",
    "local CHARGE_TIME_TO_CONTACT_S = 4      -- fire when impact is this close\n" + RANGE_CONST_LIVE,
    "live range constant")
live = repl(live,
    "-- each evaluate and passes it to the cast, so a self-targeted ability can\n"
    "-- never inherit a stale unit.\n"
    "FOURTH.cast_target = nil\n",
    "-- each evaluate and passes it to the cast, so a self-targeted ability can\n"
    "-- never inherit a stale unit.\n"
    "FOURTH.cast_target = nil\n" + CAST_FIELD_LIVE,
    "live cast field + helpers")
live = repl(live,
    "\t\t\t\t\tFOURTH.cast_target = nil\n"
    "\t\t\t\t\tlocal reason = ability.evaluate(unit, routing)\n",
    "\t\t\t\t\tFOURTH.cast_target = nil\n"
    "\t\t\t\t\tFOURTH.gd_ally = nil\n"
    "\t\t\t\t\tlocal reason = ability.evaluate(unit, routing)\n",
    "live dispatch clear")
live = repl(live,
    "\t-- THE CALL. Ordinary keys (self- or unit-targeted) use the proven\n",
    RECHECK_LIVE + "\t-- THE CALL. Ordinary keys (self- or unit-targeted) use the proven\n",
    "live re-check")
live = slice_replace(live,
    "-- GLORIOUS DEATH: the mod's FIRST ability whose trigger does NOT require the",
    "\n-- THE TRIGGER -> EVALUATOR MAP",
    live_gd(), "live GD evaluator")

# ================================================================== ANN
ann = io.open(SRC_ANN, encoding="utf-8", newline="").read()
assert "\r" not in ann
ann = repl(ann,
    "local CHARGE_TIME_TO_CONTACT_S = 4      -- seconds - fire when impact is this close\n",
    "local CHARGE_TIME_TO_CONTACT_S = 4      -- seconds - fire when impact is this close\n" + RANGE_CONST_ANN,
    "ann range constant")
ann = repl(ann,
    "-- per-unit state (cast_target, plus the Slayer key list below) rides the\n"
    "-- same bag too.\n"
    "FOURTH.cast_target = nil\n",
    "-- per-unit state (cast_target, plus the Slayer key list below) rides the\n"
    "-- same bag too.\n"
    "FOURTH.cast_target = nil\n" + CAST_FIELD_ANN,
    "ann cast field + helpers")
ann = repl(ann,
    "\t\t\t\t\tFOURTH.cast_target = nil\n"
    "\t\t\t\t\tlocal want_fire = ability.evaluate(unit, routing)\n",
    "\t\t\t\t\tFOURTH.cast_target = nil\n"
    "\t\t\t\t\tFOURTH.gd_ally = nil\n"
    "\t\t\t\t\tlocal want_fire = ability.evaluate(unit, routing)\n",
    "ann dispatch clear")
ann = repl(ann,
    "\t-- THE CALL. Ordinary keys (self- or unit-targeted) use the proven\n",
    RECHECK_ANN + "\t-- THE CALL. Ordinary keys (self- or unit-targeted) use the proven\n",
    "ann re-check")
ann = slice_replace(ann,
    "-- GLORIOUS DEATH: the ability whose trigger does NOT require the OWNER to be",
    "\n-- The trigger -> evaluator map",
    ann_gd(), "ann GD evaluator")

# =========================================================== postconditions
def post(name, src, is_live):
    print("--", name)
    assert src.count("local GLORIOUS_DEATH_RANGE_M = 55") == 1, name
    assert src.count("function FOURTH.gd_ally_gap(unit, ally)") == 1, name
    assert src.count("function FOURTH.gd_ally_in_range(unit, ally)") == 1, name
    assert src.count("FOURTH.gd_ally = nil") == 3, (name, src.count("FOURTH.gd_ally = nil"))
    assert src.count("FOURTH.gd_ally = best_ally") == 1, name
    assert count_plain(src, "FOURTH.cast_target = unit") == 2, name
    assert src.count("and FOURTH.is_slayer(other) then") == 1, name
    assert src.count("FOURTH.is_slayer(unit) and unit:is_in_melee()") == 1, name
    assert count_plain(src, "unit:is_in_melee() and not routing") == 3, name
    assert src.count("function FOURTH.evaluate_glorious_death(unit, routing)") == 1, name
    assert src.count("FOURTH.cast_target = best_unit") == 0, name
    assert count_plain(src, "unit:unit_distance") == 2, (name, count_plain(src, "unit:unit_distance"))
    if is_live:
        assert src.count('reason = "slayer in melee (self-cast)"') == 1, name
        assert src.count('reason = "self in melee (self-cast)"') == 1, name
        assert src.count('reason = "slayer ally in melee (priority)"') == 0, name
        assert src.count("string.find(") == 0, name
        assert src.count("glorious_death SKIPPED:") == 1, name
        assert src.count("glorious_death ally: ui") == 1, name
        assert "local ICON_INDEX" not in src, name
        assert "local original_icon" not in src and "local original_state" not in src, name
        assert "local function read_icon" not in src, name
        print("   live: range const + gate + recheck + log present; dead icon block removed")
    else:
        assert src.count("log(") == 0, name
        assert src.count("string.find") == 0, name
        assert src.count('reason = "') == 0, name
        print("   ann: range const + gate + recheck present, log-free/find-free")

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
