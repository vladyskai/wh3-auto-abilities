"""ROUND 13 probe editor.

Diagnosis -> fix + rebuild:
  * Round 12 seeded the descent on the NUMERIC unit-id nodes under unit_id_holder
    and walked 532 visits straight into the ON-FIELD UNIT CARD (character_portrait,
    icon_rank_holder, cat_docker, ...) - ZERO stat-row nodes (LOCATED: 0). The
    round-4 marker says the stat components answer to ids that START WITH
    CcoUnitStat - a STABLE PREFIX the hint-substring hunt never tested.
  * Splice the ROUND 13 section: descend EVERY top-level UI root that has children
    (priority hud_battle, panel_manager, under_advisor_docker, left, right,
    tactical_hud, menu_bar, then the rest) to DEPTH 8 with a 1200-visit budget,
    match the CcoUnitStat* PREFIX (case-insensitive) AND the structural names, log
    R13 DOWN per node + R13 HIT per hit, pair the rows (R13 PANEL row=), read
    GetContextObjectId (R13 CTXID), then run EXACTLY TWO common.get_context_value
    calls (R13 QUERY sel= / nonsel=). SEVEN steps.
  * Update the build gate in build_and_install.py with the R13 tokens.

Every replacement is count-asserted; the probe is only written if EVERY anchor
matched. Run from the WH3_mod/tools dir:
    python build_r13.py
"""
import io
import os

PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_ui_text.lua"
BUILD = r"C:/Users/vlady/Desktop/WH3_mod/tools/build_and_install.py"
HERE = os.path.dirname(os.path.abspath(__file__))
SEC = os.path.join(HERE, "r13_section.lua")

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
# A. session header -> round 13
# =====================================================================
must("(round 12: unit-id descent to depth 8 + two context queries | rounds 11-3 below)",
     "(round 13: all-roots descent + CcoUnitStat prefix hunt | rounds 12-3 below)",
     "session header -> round 13")

# =====================================================================
# B. header comment: the round-13 hooks (after the round-12 hooks block)
# =====================================================================
must("--   zz_probe_r12_help()        the round-12 instructions, as a string\n",
     "--   zz_probe_r12_help()        the round-12 instructions, as a string\n"
     "--   ROUND 13 hooks (R13 TOTAL STEPS 7 - you are done after step 7; battle ->\n"
     "--   open AND PIN the unit-info panel -> keep the cards panel up with >=2 units):\n"
     "--   zz_probe_r13()             start/restart the run (step 0)\n"
     "--   zz_probe_r13_step()        run EXACTLY ONE step (SEVEN total; stop after 7)\n"
     "--   zz_probe_r13_auto()        run every step to the cap\n"
     "--   zz_probe_r13_status()      step / budgets / roots / hits / located / rows / ctx ids\n"
     "--   zz_probe_r13_help()        the round-13 instructions, as a string\n",
     "header comment: round-13 hooks")

# =====================================================================
# C. splice the ROUND 13 section before section 8
# =====================================================================
sec = io.open(SEC, "r", encoding="utf-8", newline="").read()
assert "\r" not in sec, "r13_section.lua has CR chars - expected LF only"
assert sec.startswith("-- ="), "unexpected section start"
if not sec.endswith("\n"):
    sec += "\n"
sec += "\n"
must("-- ============================================================================\n"
     "-- 8. WINDOW LIFECYCLE + THE POLL (mouse-armed primary, no auto windows, manual)",
     sec
     + "-- ============================================================================\n"
       "-- 8. WINDOW LIFECYCLE + THE POLL (mouse-armed primary, no auto windows, manual)",
     "round-13 section spliced")

# =====================================================================
# D. load log: the round-13 banner (before the round-12 banner)
# =====================================================================
must('log("R12 TOTAL STEPS 6 - you are done after step 6. ROUND 12: seed the descent on the"',
     'log("R13 TOTAL STEPS 7 - you are done after step 7. ROUND 13: descend EVERY top-level root"\n'
     '\t.. " that has children (priority hud_battle, panel_manager, under_advisor_docker, left, right,"\n'
     '\t.. " tactical_hud, menu_bar, then the rest) to DEPTH 8 (1200 visits), matching the CcoUnitStat*"\n'
     '\t.. " PREFIX (case-insensitive) AND the structural names; pair the stat rows; read"\n'
     '\t.. " GetContextObjectId (CcoUnitDetails / CcoUnitStat / CcoBattleUnit); then run EXACTLY TWO"\n'
     '\t.. " common.get_context_value calls - query 1 with the LOCATED context id, query 2 with a"\n'
     '\t.. " NON-selected unit\'s ui id as text. Call zz_probe_r13() once, then zz_probe_r13_step()"\n'
     '\t.. " SEVEN times (STOP after step 7). Only proven-safe primitives; ZERO SetContextObject;"\n'
     '\t.. " simhover DISARMED; the name-lookup helper is BANNED. zz_probe_r13_auto() runs to the cap."\n'
     '\t.. " log: " .. LOG_FILE)\n\n'
     'log("R12 TOTAL STEPS 6 - you are done after step 6. ROUND 12: seed the descent on the"',
     "round-13 load log")

io.open(PROBE, "w", encoding="utf-8", newline="").write(s)
print(f"PROBE written: {len(s)} bytes ({n_edits} edits)")

# =====================================================================
# BUILD GATE updates
# =====================================================================
b = io.open(BUILD, "r", encoding="utf-8", newline="").read()
assert "\r\n" not in b, "build file has CRLF - expected LF only"
norm = b

old_anchor = 'assert "total_steps     = 6" in ui_probe_txt, "the R12 total-step count is not 6"\n'
assert norm.count(old_anchor) == 1, "R12 total-steps anchor"
new_anchor = (old_anchor +
              '# round 13: the all-roots descent. Round 12 seeded the descent on the NUMERIC unit-id\n'
              '# nodes under unit_id_holder and walked into the ON-FIELD UNIT CARD (LOCATED: 0); the\n'
              '# stat components answer to a STABLE id PREFIX (CcoUnitStat*) the hint-substring hunt\n'
              '# never tested. Round 13 descends EVERY top-level root that has children (priority\n'
              '# hud_battle, panel_manager, under_advisor_docker, left, right, tactical_hud, menu_bar,\n'
              '# then the rest) to DEPTH 8 with a 1200-visit budget, matching the CcoUnitStat* PREFIX\n'
              '# (case-insensitive) AND the structural names; pairs the rows (R13 PANEL row=), reads\n'
              '# GetContextObjectId (R13 CTXID) and runs EXACTLY TWO common.get_context_value calls\n'
              '# (R13 QUERY sel= / nonsel=). SEVEN steps total, one per armed console call.\n'
              'assert "find_uicomponent" not in ui_probe_txt, "the banned name-lookup helper is back in the probe"\n'
              'for tok in ("ROUND 13", "zz_probe_r13", "zz_probe_r13_step", "zz_probe_r13_auto",\n'
              '            "zz_probe_r13_status", "zz_probe_r13_help",\n'
              '            "ROOTCOUNT", "DESCEND PLAN", "DOWN path=", "R13 HIT", "LOCATED ",\n'
              '            "PANEL row=", "ROWCTX ", "CTXID ", "QUERY sel=", "QUERY nonsel=",\n'
              '            "R13 TOTAL STEPS 7", "descend_visits", "descend_depth",\n'
              '            "stat_prefix", "ccounitstat", "locate_names", "priority",\n'
              '            "hud_battle", "panel_manager", "under_advisor_docker", "tactical_hud", "menu_bar",\n'
              '            "is_prefix_id", "is_hit_id", "total_steps", "GetTooltipText",\n'
              '            "common.get_context_value", "GetContextObjectId", "StatList.Size", "DisplayedValue"):\n'
              '    assert tok in ui_probe_txt, f"the R13 UI probe is missing {tok}"\n'
              'assert "function zz_probe_r13(" in ui_probe_txt, "the R13 start hook is missing"\n'
              'assert "function zz_probe_r13_step(" in ui_probe_txt, "the R13 step hook is missing"\n'
              'assert "descend_visits  = 1200" in ui_probe_txt, "the R13 visit budget is not 1200"\n'
              'assert "descend_depth   = 8" in ui_probe_txt, "the R13 depth cap is not 8"\n'
              'assert "total_steps     = 7" in ui_probe_txt, "the R13 total-step count is not 7"\n'
              'assert \'stat_prefix     = "ccounitstat"\' in ui_probe_txt, "the R13 stable prefix is not ccounitstat"\n')
norm = norm.replace(old_anchor, new_anchor)

io.open(BUILD, "w", encoding="utf-8", newline="").write(norm)
print("BUILD gate updated:", os.path.basename(BUILD))
for t in ("ROUND 13", "R13 TOTAL STEPS 7", "descend_visits  = 1200",
          "descend_depth   = 8", "total_steps     = 7", 'stat_prefix     = "ccounitstat"',
          "the banned name-lookup helper is back in the probe"):
    print("  token check:", repr(t), t in norm)
