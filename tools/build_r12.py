"""ROUND 12 probe editor.

Diagnosis -> fix + rebuild:
  * Round 11's step-3 descent stopped at depth 4 (88 of 400 visits) - the DEPTH
    cap, not the budget, cut the panel hunt short (its last node was
    unit_id_holder/1001/modular_parent, exactly at depth 4).
  * Splice the ROUND 12 section: SEED the descent on the NUMERIC unit-id nodes
    under unit_id_holder, descend to DEPTH 8 with an 800-visit budget, log every
    node (R12 DOWN path/id/children/stext), locate the stat-row nodes, pair the
    rows, read GetContextObjectId (CcoUnitDetails/CcoUnitStat/CcoBattleUnit) on
    the located rows, then run EXACTLY TWO common.get_context_value calls (the
    SELECTED unit's context id, then a NON-selected unit's ui id). SIX steps.
  * Update the build gate in build_and_install.py with the R12 tokens.

Every replacement is count-asserted; the probe is only written if EVERY anchor
matched. Run from %LOCALAPPDATA%\\Temp:
    python build_r12.py
"""
import io
import os

PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_ui_text.lua"
BUILD = r"C:/Users/vlady/Desktop/WH3_mod/tools/build_and_install.py"
HERE = os.path.dirname(os.path.abspath(__file__))
SEC = os.path.join(HERE, "r12_section.lua")

s = io.open(PROBE, "r", encoding="utf-8", newline="").read()
assert "\r" not in s, "probe file has CR chars - expected LF only"
n_edits = 0


def must(old, new, label):
    global s, n_edits
    n = s.count(old)
    assert n == 1, f"{label}: anchor count {n} != 1 :: {old[:110]!r}"
    s = s.replace(old, new)
    n_edits += 1
    print(f"  OK {label}")


# =====================================================================
# A. session header -> round 12
# =====================================================================
must('.. "(round 11: full enumeration + hint descent | rounds 10-3 below) ========\\n"',
     '.. "(round 12: unit-id descent to depth 8 + two context queries | rounds 11-3 below) ========\\n"',
     "session header -> round 12")

# =====================================================================
# B. header comment: the round-12 hooks
# =====================================================================
must("--   zz_probe_r11_help()        the round-11 instructions, as a string\n"
     "--\n"
     "-- REMOVAL: delete this one file and rebuild. Nothing else refers to it.",
     "--   zz_probe_r11_help()        the round-11 instructions, as a string\n"
     "--   ROUND 12 hooks (R12 TOTAL STEPS 6 - you are done after step 6; battle ->\n"
     "--   open AND PIN the unit-info panel -> keep the cards panel up with >=2 units):\n"
     "--   zz_probe_r12()             start/restart the run (step 0)\n"
     "--   zz_probe_r12_step()        run EXACTLY ONE step (SIX total; stop after 6)\n"
     "--   zz_probe_r12_auto()        run every step to the cap\n"
     "--   zz_probe_r12_status()      step / budgets / seeds / located / rows / ctx ids\n"
     "--   zz_probe_r12_help()        the round-12 instructions, as a string\n"
     "--\n"
     "-- REMOVAL: delete this one file and rebuild. Nothing else refers to it.",
     "header comment: round-12 hooks")

# =====================================================================
# C. splice the ROUND 12 section before section 8
# =====================================================================
sec = io.open(SEC, "r", encoding="utf-8", newline="").read()
assert "\r" not in sec, "r12_section.lua has CR chars - expected LF only"
assert sec.startswith("-- ="), "unexpected section start"
if not sec.endswith("\n"):
    sec += "\n"
sec += "\n"
must("-- ============================================================================\n"
     "-- 8. WINDOW LIFECYCLE + THE POLL (mouse-armed primary, no auto windows, manual)",
     sec
     + "-- ============================================================================\n"
       "-- 8. WINDOW LIFECYCLE + THE POLL (mouse-armed primary, no auto windows, manual)",
     "round-12 section spliced")

# =====================================================================
# D. load log: the round-12 banner (before the mouse-listener note)
# =====================================================================
must("if mouse_on_registered then\n"
     "\tlog(\"mouse listener registered: ComponentMouseOn / ComponentMouseOff -> a hover on a unit card\"",
     "log(\"R12 TOTAL STEPS 6 - you are done after step 6. ROUND 12: seed the descent on the\"\n"
     "\t.. \" NUMERIC unit-id nodes under unit_id_holder, descend to DEPTH 8 (800 visits), locate\"\n"
     "\t.. \" and pair the stat rows, read GetContextObjectId (CcoUnitDetails / CcoUnitStat /\"\n"
     "\t.. \" CcoBattleUnit) on the located rows, then run EXACTLY TWO common.get_context_value\"\n"
     "\t.. \" calls - ONE with the SELECTED unit's context id, ONE with a NON-selected unit's ui id.\"\n"
     "\t.. \" Call zz_probe_r12() once, then zz_probe_r12_step() SIX times (STOP after step 6).\"\n"
     "\t.. \" Only proven-safe primitives; ZERO SetContextObject; simhover DISARMED; the name-lookup\"\n"
     "\t.. \" helper is BANNED. zz_probe_r12_auto() runs to the cap. log: \" .. LOG_FILE)\n\n"
     "if mouse_on_registered then\n"
     "\tlog(\"mouse listener registered: ComponentMouseOn / ComponentMouseOff -> a hover on a unit card\"",
     "round-12 load log")

io.open(PROBE, "w", encoding="utf-8", newline="").write(s)
print(f"PROBE written: {len(s)} bytes ({n_edits} edits)")

# =====================================================================
# BUILD GATE updates
# =====================================================================
b = io.open(BUILD, "r", encoding="utf-8", newline="").read()
assert "\r\n" not in b, "build file has CRLF - expected LF only"
norm = b

old_tok = ('assert "function zz_probe_r11_step(" in ui_probe_txt, "the R11 step hook is missing"\n'
           'assert "function zz_probe_r11(" in ui_probe_txt, "the R11 start hook is missing"\n')
assert norm.count(old_tok) == 1, "R11 start-anchor"
new_tok = (old_tok +
           '# round 12: the round-11 depth-cap post-mortem build. Round 11 stopped the descent at\n'
           '# depth 4 (the cap, not the budget); round 12 SEEDS the descent on the NUMERIC unit-id\n'
           '# nodes under unit_id_holder, descends to DEPTH 8 with an 800-visit budget, logs every\n'
           '# node (R12 DOWN), locates + pairs the stat rows (R12 LOCATED / R12 PANEL row=), reads\n'
           '# GetContextObjectId (R12 CTXID) and runs EXACTLY TWO common.get_context_value calls\n'
           '# (R12 QUERY sel= / R12 QUERY nonsel=). SIX steps total, one per armed console call.\n'
           'assert "find_uicomponent" not in ui_probe_txt, "the banned name-lookup helper is back in the probe"\n'
           'for tok in ("ROUND 12", "zz_probe_r12", "zz_probe_r12_step", "zz_probe_r12_auto",\n'
           '            "zz_probe_r12_status", "zz_probe_r12_help",\n'
           '            "ROOTCOUNT", "UNITIDCHILD", "DOWN ", "LOCATED ",\n'
           '            "PANEL row=", "CTXID ", "QUERY sel=", "QUERY nonsel=",\n'
           '            "R12 TOTAL STEPS 6", "descend_visits", "descend_depth",\n'
           '            "unit_id_holder", "is_numeric", "locate_names", "total_steps",\n'
           '            "common.get_context_value", "GetContextObjectId", "StatList.Size"):\n'
           '    assert tok in ui_probe_txt, f"the R12 UI probe is missing {tok}"\n'
           'assert "function zz_probe_r12(" in ui_probe_txt, "the R12 start hook is missing"\n'
           'assert "function zz_probe_r12_step(" in ui_probe_txt, "the R12 step hook is missing"\n'
           'assert "descend_visits  = 800" in ui_probe_txt, "the R12 visit budget is not 800"\n'
           'assert "descend_depth   = 8" in ui_probe_txt, "the R12 depth cap is not 8"\n'
           'assert "total_steps     = 6" in ui_probe_txt, "the R12 total-step count is not 6"\n')
norm = norm.replace(old_tok, new_tok)

io.open(BUILD, "w", encoding="utf-8", newline="").write(norm)
print("BUILD gate updated:", os.path.basename(BUILD))
for t in ("ROUND 12", "R12 TOTAL STEPS 6", "descend_visits  = 800",
          "descend_depth   = 8", "total_steps     = 6",
          "the banned name-lookup helper is back in the probe"):
    print("  token check:", repr(t), t in norm)
