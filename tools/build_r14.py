"""ROUND 14 probe editor.

Diagnosis -> fix + rebuild:
  * Round 13 DISCOVERED the panel's real path
      hud_battle/info_panel_parent/info_panel_background/unit_information/
      info_parent/info_panel/list
    and the context-id format: GetContextObjectId("CcoUnitDetails") on the
    info_panel/list node returned "BattleUnit_1001". But its 1200-visit descent
    exhausted the budget before the stat ROWS (PANEL rows: 0), so both value
    queries returned <ERR> - the FIELD NAME (and/or the type/id pairing) is what
    is wrong, not the mechanism.
  * Splice the ROUND 14 section: SEED the descent on the discovered path (each
    link = the direct child whose Id matches), walk DOWN from `list` (depth 6,
    budget 300), pair the stat rows (stat_name -> value_holder/dy_value), then run
    a FIXED LADDER of common.get_context_value calls - a control (CcoBattleUnit +
    bare id + Name), then CcoUnitDetails/"BattleUnit_1001" with Name / StatList /
    StatList.Size, then CcoUnitStat/"BattleUnit_1001" with DisplayedValue / Name,
    then the SAME ladder shape for the NON-selected unit ("BattleUnit_1002" and
    bare "1002"). Every call is logged before AND after; the ladder STOPS at the
    first success; a NON-selected success logs R14 *** WIN ***. EIGHT steps.
  * Update the build gate in build_and_install.py with the R14 tokens.

Every replacement is count-asserted; the probe is only written if EVERY anchor
matched. Run from the WH3_mod/tools dir:
    python build_r14.py
"""
import io
import os

PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_ui_text.lua"
BUILD = r"C:/Users/vlady/Desktop/WH3_mod/tools/build_and_install.py"
HERE = os.path.dirname(os.path.abspath(__file__))
SEC = os.path.join(HERE, "r14_section.lua")

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
# A. session header -> round 14
# =====================================================================
must("(round 13: all-roots descent + CcoUnitStat prefix hunt | rounds 12-3 below)",
     "(round 14: seeded panel-path descent + fixed GCV ladder | rounds 13-3 below)",
     "session header -> round 14")

# =====================================================================
# B. header comment: the round-14 hooks (after the round-13 hooks block)
# =====================================================================
must("--   zz_probe_r13_help()        the round-13 instructions, as a string\n",
     "--   zz_probe_r13_help()        the round-13 instructions, as a string\n"
     "--   ROUND 14 hooks (R14 TOTAL STEPS 8 - you are done after step 8; battle ->\n"
     "--   open AND PIN the unit-info panel -> keep the cards panel up with >=2 units):\n"
     "--   zz_probe_r14()             start/restart the run (step 0)\n"
     "--   zz_probe_r14_step()        run EXACTLY ONE step (EIGHT total; stop after 8)\n"
     "--   zz_probe_r14_auto()        run every step to the cap\n"
     "--   zz_probe_r14_status()      chain / list / walked / rows / gcv calls / win\n"
     "--   zz_probe_r14_help()        the round-14 instructions, as a string\n",
     "header comment: round-14 hooks")

# =====================================================================
# C. splice the ROUND 14 section before section 8
# =====================================================================
sec = io.open(SEC, "r", encoding="utf-8", newline="").read()
assert "\r" not in sec, "r14_section.lua has CR chars - expected LF only"
assert sec.startswith("-- ="), "unexpected section start"
if not sec.endswith("\n"):
    sec += "\n"
sec += "\n"
must("-- ============================================================================\n"
     "-- 8. WINDOW LIFECYCLE + THE POLL (mouse-armed primary, no auto windows, manual)",
     sec
     + "-- ============================================================================\n"
       "-- 8. WINDOW LIFECYCLE + THE POLL (mouse-armed primary, no auto windows, manual)",
     "round-14 section spliced")

# =====================================================================
# D. load log: the round-14 banner (before the mouse-listener note)
# =====================================================================
must('if mouse_on_registered then\n'
     '\tlog("mouse listener registered: ComponentMouseOn / ComponentMouseOff -> a hover on a unit card"',
     'log("R14 TOTAL STEPS 8 - you are done after step 8. ROUND 14: SEED the descent on the"\n'
     '\t.. " DISCOVERED panel path (hud_battle/info_panel_parent/info_panel_background/"\n'
     '\t.. "unit_information/info_parent/info_panel/list), walk DOWN from `list` (depth 6, budget"\n'
     '\t.. " 300), pair the stat rows, then run a FIXED ladder of common.get_context_value calls:"\n'
     '\t.. " a control (CcoBattleUnit + bare id + Name), CcoUnitDetails/BattleUnit_1001 fields"\n'
     '\t.. " Name/StatList/StatList.Size, CcoUnitStat/BattleUnit_1001 DisplayedValue/Name, then the"\n'
     '\t.. " SAME ladder shape for the NON-selected unit (BattleUnit_1002 and bare 1002). Every call"\n'
     '\t.. " is logged before AND after; the ladder STOPS at the first success; a NON-selected"\n'
     '\t.. " success logs R14 *** WIN ***. Call zz_probe_r14() once, then zz_probe_r14_step() EIGHT"\n'
     '\t.. " times (STOP after step 8). Only proven-safe primitives; ZERO SetContextObject; simhover"\n'
     '\t.. " DISARMED; the name-lookup helper is BANNED. zz_probe_r14_auto() runs to the cap."\n'
     '\t.. " log: " .. LOG_FILE)\n\n'
     'if mouse_on_registered then\n'
     '\tlog("mouse listener registered: ComponentMouseOn / ComponentMouseOff -> a hover on a unit card"',
     "round-14 load log")

io.open(PROBE, "w", encoding="utf-8", newline="").write(s)
print(f"PROBE written: {len(s)} bytes ({n_edits} edits)")

# =====================================================================
# BUILD GATE updates
# =====================================================================
b = io.open(BUILD, "r", encoding="utf-8", newline="").read()
assert "\r\n" not in b, "build file has CRLF - expected LF only"
norm = b

old_anchor = ('assert \'stat_prefix     = "ccounitstat"\' in ui_probe_txt, "the R13 stable prefix is not ccounitstat"\n')
assert norm.count(old_anchor) == 1, "R13 stat_prefix anchor"
new_anchor = (old_anchor +
              '# round 14: the round-13 DISCOVERY build. Round 13 found the panel\'s real path\n'
              '# (unit_information lives UNDER info_panel_parent inside hud_battle) and the context-id\n'
              '# format (GetContextObjectId("CcoUnitDetails") on info_panel/list -> "BattleUnit_1001"),\n'
              '# but its 1200-visit descent ran out of budget before the stat ROWS (PANEL rows: 0), so\n'
              '# both value queries returned <ERR>. Round 14 SEEDS the descent on the discovered path\n'
              '# (each link = the direct child whose Id matches), walks DOWN from `list` (depth 6, budget\n'
              '# 300), pairs the rows (R14 PANEL row=), then runs a FIXED ladder of common.get_context_value\n'
              '# calls - a control, CcoUnitDetails/"BattleUnit_1001" (Name/StatList/StatList.Size),\n'
              '# CcoUnitStat/"BattleUnit_1001" (DisplayedValue/Name), then the SAME shape for the\n'
              '# NON-selected unit ("BattleUnit_1002" and bare "1002") - logged before AND after, stopping\n'
              '# at the first success, with a loud R14 *** WIN *** on any non-selected success. EIGHT steps.\n'
              'assert "find_uicomponent" not in ui_probe_txt, "the banned name-lookup helper is back in the probe"\n'
              'for tok in ("ROUND 14", "zz_probe_r14", "zz_probe_r14_step", "zz_probe_r14_auto",\n'
              '            "zz_probe_r14_status", "zz_probe_r14_help",\n'
              '            "R14 TOTAL STEPS 8", "SEED link ", "SEED resolved the FULL chain",\n'
              '            "DOWN path=", "PANEL row=", "ROWHEADER ", "R14 GCV n=", "R14 CALL ",\n'
              '            "*** WIN: non-selected unit stat field readable ***",\n'
              '            "info_panel_parent", "info_panel_background", "unit_information",\n'
              '            "info_parent", "info_panel", "row_header_stats", "template_stat",\n'
              '            "value_holder", "dy_value", "stat_name", "resolve_chain",\n'
              '            "walk_visits", "walk_depth", "total_steps",\n'
              '            "common.get_context_value", "CcoBattleUnit", "CcoUnitDetails", "CcoUnitStat",\n'
              '            "BattleUnit_1001", "BattleUnit_1002", "StatList", "StatList.Size", "DisplayedValue"):\n'
              '    assert tok in ui_probe_txt, f"the R14 UI probe is missing {tok}"\n'
              'assert "function zz_probe_r14(" in ui_probe_txt, "the R14 start hook is missing"\n'
              'assert "function zz_probe_r14_step(" in ui_probe_txt, "the R14 step hook is missing"\n'
              'assert "walk_visits         = 300" in ui_probe_txt, "the R14 walk budget is not 300"\n'
              'assert "walk_depth          = 6" in ui_probe_txt, "the R14 walk depth is not 6"\n'
              'assert "total_steps         = 8" in ui_probe_txt, "the R14 total-step count is not 8"\n')
norm = norm.replace(old_anchor, new_anchor)

io.open(BUILD, "w", encoding="utf-8", newline="").write(norm)
print("BUILD gate updated:", os.path.basename(BUILD))
for t in ("ROUND 14", "R14 TOTAL STEPS 8", "walk_visits         = 300",
          "walk_depth          = 6", "total_steps         = 8",
          "the banned name-lookup helper is back in the probe"):
    print("  token check:", repr(t), t in norm)
