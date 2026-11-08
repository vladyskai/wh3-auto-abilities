# -*- coding: utf-8 -*-
"""Round-87 edit: GLORIOUS DEATH's trigger range 55 m -> 25 m (conservative).

USER INSTRUCTION (verbatim): "I tested Glorious Death again and it casted too
soon. Make it 25 m to make sure it is in range."

The harness-86 round introduced GLORIOUS_DEATH_RANGE_M = 55 (the ability's
wiki "Effect range: 55m"). FIELD TESTING showed that fired too early, so the
gate is tightened to a DELIBERATELY CONSERVATIVE 25 m - TIGHTER than the
ability's 55 m wiki aura on purpose. The wiki's real effect range is kept in
the comment for reference.

This is a ONE-CONSTANT change plus the comments that described the old 55 m
gate. No logic changes: the gate, the closest-ally choice, the pre-cast
re-check and the fail-open on an unreadable gap all stay exactly as built.

Applies to the REAL Desktop files (live + annotated) and writes copies to
h87work/next/. Every anchor asserted; line endings stay LF.
"""
import io, os, hashlib

DESK = "C:/Users/vlady/Desktop"
SRC_LIVE = DESK + "/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"
SRC_ANN  = DESK + "/WH3_auto_ability_annotated.lua"
OUT_DIR  = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "h87work", "next")
os.makedirs(OUT_DIR, exist_ok=True)

# ------------------------------------------------------------------ anchors
LIVE_CONST_OLD = (
    "-- GLORIOUS DEATH'S EFFECT RANGE (this round) - WIKI-SOURCED. The\n"
    "-- ability's wiki effects line reads \"Effect range: 55m\"; the range gate\n"
    "-- below offers, and re-checks just before the cast, an in-melee Slayer\n"
    "-- ally only when the owner is within GLORIOUS_DEATH_RANGE_M metres of it.\n"
    "-- ONE place to tune the gate.\n"
    "local GLORIOUS_DEATH_RANGE_M = 55\n"
)
LIVE_CONST_NEW = (
    "-- GLORIOUS DEATH'S TRIGGER RANGE (this round) - DELIBERATELY CONSERVATIVE.\n"
    "-- The ability's wiki effects line reads \"Effect range: 55m\" (kept here for\n"
    "-- reference), but the user's FIELD TESTING showed a 55 m trigger fired too\n"
    "-- early, so the gate is set to a TIGHTER, deliberately conservative trigger\n"
    "-- range: GLORIOUS_DEATH_RANGE_M is BELOW the ability's 55 m wiki aura on\n"
    "-- purpose. The range gate below offers, and re-checks just before the cast,\n"
    "-- an in-melee Slayer ally only when the owner is within GLORIOUS_DEATH_RANGE_M\n"
    "-- metres of it. ONE place to tune the gate.\n"
    "local GLORIOUS_DEATH_RANGE_M = 25\n"
)

ANN_CONST_OLD = (
    "-- GLORIOUS DEATH'S EFFECT RANGE (this round) - WIKI-SOURCED. The\n"
    "-- ability's wiki effects line reads \"Effect range: 55m\"; the range gate\n"
    "-- below offers, and re-checks just before the cast, an in-melee Slayer\n"
    "-- ally only when the owner is within GLORIOUS_DEATH_RANGE_M metres of it.\n"
    "local GLORIOUS_DEATH_RANGE_M = 55\n"
)
ANN_CONST_NEW = (
    "-- GLORIOUS DEATH'S TRIGGER RANGE (this round) - DELIBERATELY CONSERVATIVE.\n"
    "-- The ability's wiki effects line reads \"Effect range: 55m\" (reference only);\n"
    "-- the user's FIELD TESTING showed a 55 m trigger fired too early, so this is\n"
    "-- a TIGHTER, deliberately conservative trigger range - GLORIOUS_DEATH_RANGE_M\n"
    "-- is BELOW the ability's 55 m wiki aura on purpose. The gate below offers,\n"
    "-- and re-checks just before the cast, an in-melee Slayer ally only when the\n"
    "-- owner is within GLORIOUS_DEATH_RANGE_M metres of it.\n"
    "local GLORIOUS_DEATH_RANGE_M = 25\n"
)

# the other comments that described the OLD 55 m gate -> the conservative 25 m
LIVE_RECHECK_OLD = (
    "\t-- cast. If the ally has drifted beyond the ability's 55 m effect range\n"
    "\t-- the aura would not cover it, so SKIP the cast rather than waste it.\n"
)
LIVE_RECHECK_NEW = (
    "\t-- cast. If the ally has drifted beyond the conservative 25 m trigger\n"
    "\t-- range the cast is wasted, so SKIP it rather than spend it.\n"
)
LIVE_HELPER_OLD = (
    "-- true when the gap is within the ability's 55 m effect range. An\n"
)
LIVE_HELPER_NEW = (
    "-- true when the gap is within the conservative 25 m trigger range. An\n"
)
LIVE_EVAL_OLD = (
    "-- THE RANGE GATE (this round, the reported bug fix): the ally arm only counts\n"
    "-- while the owner is WITHIN the ability's 55 m effect range\n"
    "-- (GLORIOUS_DEATH_RANGE_M, wiki-sourced) of the ally - otherwise the aura\n"
    "-- would not cover it and the cast is wasted. The CLOSEST in-range in-melee\n"
)
LIVE_EVAL_NEW = (
    "-- THE RANGE GATE (this round, the reported bug fix): the ally arm only counts\n"
    "-- while the owner is WITHIN the conservative trigger range\n"
    "-- (GLORIOUS_DEATH_RANGE_M = 25 m, deliberately tighter than the ability's\n"
    "-- 55 m wiki aura) of the ally - otherwise the cast is wasted. The CLOSEST\n"
    "-- in-range in-melee\n"
)

ANN_RECHECK_OLD = (
    "\t-- ability's 55 m effect range (the aura would not cover it). The\n"
)
ANN_RECHECK_NEW = (
    "\t-- conservative 25 m trigger range. The\n"
)
ANN_HELPER_OLD = (
    "-- true when the gap is within the ability's 55 m effect range; an\n"
)
ANN_HELPER_NEW = (
    "-- true when the gap is within the conservative 25 m trigger range; an\n"
)
ANN_EVAL_OLD = (
    "-- ITSELF. THE RANGE GATE (this round): the ally arm only counts while the\n"
    "-- owner is within the ability's 55 m effect range (GLORIOUS_DEATH_RANGE_M) of\n"
)
ANN_EVAL_NEW = (
    "-- ITSELF. THE RANGE GATE (this round): the ally arm only counts while the\n"
    "-- owner is within the conservative trigger range GLORIOUS_DEATH_RANGE_M\n"
    "-- (25 m, deliberately tighter than the ability's 55 m wiki aura) of\n"
)


def repl(src, old, new, label):
    n = src.count(old)
    assert n == 1, "%s: anchor x%d" % (label, n)
    return src.replace(old, new, 1)

def count_plain(s, tok):
    n, at = 0, 1
    while True:
        i = s.find(tok, at)
        if i < 0:
            return n
        n += 1
        at = i + 1

# ================================================================== LIVE
live = io.open(SRC_LIVE, encoding="utf-8", newline="").read()
assert "\r" not in live
before_live = len(live)
live = repl(live, LIVE_CONST_OLD, LIVE_CONST_NEW, "live range constant")
live = repl(live, LIVE_RECHECK_OLD, LIVE_RECHECK_NEW, "live recheck comment")
live = repl(live, LIVE_HELPER_OLD, LIVE_HELPER_NEW, "live helper comment")
live = repl(live, LIVE_EVAL_OLD, LIVE_EVAL_NEW, "live evaluator comment")

# ================================================================== ANN
ann = io.open(SRC_ANN, encoding="utf-8", newline="").read()
assert "\r" not in ann
before_ann = len(ann)
ann = repl(ann, ANN_CONST_OLD, ANN_CONST_NEW, "ann range constant")
ann = repl(ann, ANN_RECHECK_OLD, ANN_RECHECK_NEW, "ann recheck comment")
ann = repl(ann, ANN_HELPER_OLD, ANN_HELPER_NEW, "ann helper comment")
ann = repl(ann, ANN_EVAL_OLD, ANN_EVAL_NEW, "ann evaluator comment")

# =========================================================== postconditions
def post(name, src, is_live):
    print("--", name)
    assert src.count("local GLORIOUS_DEATH_RANGE_M = 25") == 1, name
    assert "local GLORIOUS_DEATH_RANGE_M = 55" not in src, name
    assert src.count("Effect range: 55m") == 1, (name, "wiki note kept exactly once")
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
    assert src.count("gap <= GLORIOUS_DEATH_RANGE_M") == 2, (name, "range comparisons")
    if is_live:
        assert src.count('reason = "slayer in melee (self-cast)"') == 1, name
        assert src.count('reason = "self in melee (self-cast)"') == 1, name
        assert src.count("string.find(") == 0, name
        assert src.count("glorious_death SKIPPED:") == 1, name
        assert src.count("glorious_death ally: ui") == 1, name
        assert "local ICON_INDEX" not in src, name
        assert "local original_icon" not in src and "local original_state" not in src, name
        assert "local function read_icon" not in src, name
        print("   live: constant 25 + gate + recheck + log present; dead icon block still gone")
    else:
        assert src.count("log(") == 0, name
        assert src.count("string.find") == 0, name
        assert src.count('reason = "') == 0, name
        print("   ann: constant 25 + gate + recheck present, log-free/find-free")

post("LIVE", live, True)
post("ANN", ann, False)

io.open(SRC_LIVE, "w", encoding="utf-8", newline="\n").write(live)
io.open(SRC_ANN, "w", encoding="utf-8", newline="\n").write(ann)
io.open(os.path.join(OUT_DIR, "zz_test_deadly_onslaught.lua"), "w", encoding="utf-8", newline="\n").write(live)
io.open(os.path.join(OUT_DIR, "WH3_auto_ability_annotated.lua"), "w", encoding="utf-8", newline="\n").write(ann)
print("LIVE %d -> %d bytes LF=%d" % (before_live, len(live), live.count("\n")))
print("ANN  %d -> %d bytes LF=%d" % (before_ann, len(ann), ann.count("\n")))
print("sha256 LIVE", hashlib.sha256(live.encode("utf-8")).hexdigest())
print("sha256 ANN ", hashlib.sha256(ann.encode("utf-8")).hexdigest())
print("ALL EDIT POSTCONDITIONS OK")
