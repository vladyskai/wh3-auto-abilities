#!/usr/bin/env python3
"""Round 214 (2026-11-28, tuning, TEST BUILD ONLY): THE TIMING PROBE. No cast decision changes.

User: "figure out a way we can measure the FPS drop, what causes it and how to fix it (if it is there)".

The mod's Lua runs on the game's main thread: every millisecond it spends inside one UI tick or one poll is a
millisecond added to that frame. The probe measures that time with os.clock() and writes ONE line per second of real
time (20 UI ticks):

  PERF 1s: ui 20 ticks 14.2 ms (worst tick 9.8) | walk 1x 8.9 ms | cards 2.1 ms | select 0.3 ms | badges 1.0 ms |
           diag 1.0 ms | poll 4x 5.5 ms (worst 2.0)

  ui      the whole UI tick (it contains walk, cards, select, badges and diag)
  walk    the HUD walk that looks for the ability buttons (and how many walks ran)
  cards   the read of every unit card (the fast selection path)
  select  folding the engine's selection events
  badges  placing the letters and the arm-everything button
  diag    the test build's own log sweeps (the Workshop build does not have them)
  poll    the ability checks, 4 per second

It runs only in the development build (the console functions exist), and the harness switches it off for its older
worlds with the TEST-ONLY global ZZ_AUTO_TEST_NO_PERF. The Workshop build never measures: its console functions are
gone. The live copy only (the reading copy stays log-free).
Backups: docs/backups/round214/pre214_live.lua."""
import os
import shutil
import sys

LIVE = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
BK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round214"

A_POLL = "local function poll()\n\tlocal ok, err = pcall(poll_body)\n"
N_FN = """-- ============================================================================
-- ROUND 214 - THE TIMING PROBE (test build only, read-only). The mod's Lua runs
-- on the game's main thread, so the time one UI tick or one poll takes is time
-- added to that frame. FOURTH.perf_now / perf_add collect it per job with
-- os.clock(), FOURTH.perf_end_ui writes one PERF line per 20 UI ticks (1 s of
-- real time). Active only in the development build (zz_badge_set exists; the
-- release build has no console functions) and not in the harness's older
-- worlds (TEST-ONLY ZZ_AUTO_TEST_NO_PERF).
-- ============================================================================
FOURTH.perf = { ui = 0, ui_max = 0, ticks = 0, walk = 0, walks = 0, cards = 0, select = 0, badges = 0, diag = 0,
	poll = 0, poll_max = 0, polls = 0 }
function FOURTH.perf_now()
	if ZZ_AUTO_TEST_NO_PERF == true or zz_badge_set == nil then return nil end
	if type(os) ~= "table" or type(os.clock) ~= "function" then return nil end
	return os.clock()
end
function FOURTH.perf_add(name, t0)
	if t0 == nil then return end
	local p = FOURTH.perf
	local ms = (os.clock() - t0) * 1000
	p[name] = p[name] + ms
	if name == "walk" then p.walks = p.walks + 1 end
	if name == "poll" then
		p.polls = p.polls + 1
		if ms > p.poll_max then p.poll_max = ms end
	end
end
function FOURTH.perf_end_ui(t0)
	if t0 == nil then return end
	local p = FOURTH.perf
	local ms = (os.clock() - t0) * 1000
	p.ui = p.ui + ms
	p.ticks = p.ticks + 1
	if ms > p.ui_max then p.ui_max = ms end
	if p.ticks < 20 then return end
	log(string.format("PERF 1s: ui %d ticks %.1f ms (worst tick %.1f) | walk %dx %.1f ms | cards %.1f ms | select %.1f ms "
		.. "| badges %.1f ms | diag %.1f ms | poll %dx %.1f ms (worst %.1f)", p.ticks, p.ui, p.ui_max, p.walks, p.walk,
		p.cards, p.select, p.badges, p.diag, p.polls, p.poll, p.poll_max))
	p.ui, p.ui_max, p.ticks, p.walk, p.walks, p.cards, p.select, p.badges, p.diag = 0, 0, 0, 0, 0, 0, 0, 0, 0
	p.poll, p.poll_max, p.polls = 0, 0, 0
end

local function poll()
	local perf_p0 = FOURTH.perf_now()   -- ROUND 214
	local ok, err = pcall(poll_body)
	FOURTH.perf_add("poll", perf_p0)   -- ROUND 214
"""

EDITS = [
    ("local function ui_tick()\n\tui_ticks = ui_ticks + 1\n",
     "local function ui_tick()\n\tlocal perf_u0, perf_t = FOURTH.perf_now(), nil   -- ROUND 214: the timing probe\n\tui_ticks = ui_ticks + 1\n"),
    ("\tpcall(FOURTH.ui_shift_tick)",
     "\tperf_t = FOURTH.perf_now()\n\tpcall(FOURTH.ui_shift_tick)"),
    ("\tpcall(FOURTH.all_badge_tick)\n",
     "\tpcall(FOURTH.all_badge_tick)\n\tFOURTH.perf_add(\"badges\", perf_t)\n"),
    ("\t\tpcall(log_dial_dump)\n",
     "\t\tperf_t = FOURTH.perf_now()\n\t\tpcall(log_dial_dump)\n\t\tFOURTH.perf_add(\"diag\", perf_t)\n"),
    ("\t\tpcall(log_inventory_sweep)\n",
     "\t\tperf_t = FOURTH.perf_now()\n\t\tpcall(log_inventory_sweep)\n\t\tFOURTH.perf_add(\"diag\", perf_t)\n"),
    ("\tpcall(converge_engine_selection, tick_count)\n",
     "\tperf_t = FOURTH.perf_now()\n\tpcall(converge_engine_selection, tick_count)\n\tFOURTH.perf_add(\"select\", perf_t)\n"),
    ("\tpcall(fast_card_selection)\n",
     "\tperf_t = FOURTH.perf_now()\n\tpcall(fast_card_selection)\n\tFOURTH.perf_add(\"cards\", perf_t)\n"),
    ("\t\tpcall(log_card_sweep)\n",
     "\t\tperf_t = FOURTH.perf_now()\n\t\tpcall(log_card_sweep)\n\t\tFOURTH.perf_add(\"diag\", perf_t)\n"),
    ("\t\tif walk_now then\n\t\t\tfind_ability_buttons()\n\t\tend\n\tend\n\nend\n\nbm:repeat_real_callback(ui_tick, 50,",
     "\t\tif walk_now then\n\t\t\tperf_t = FOURTH.perf_now()\n\t\t\tfind_ability_buttons()\n\t\t\tFOURTH.perf_add(\"walk\", perf_t)\n"
     "\t\tend\n\tend\n\n\tFOURTH.perf_end_ui(perf_u0)   -- ROUND 214\nend\n\nbm:repeat_real_callback(ui_tick, 50,"),
]


def one(s, a, b, what):
    assert s.count(a) == 1, (what, s.count(a))
    return s.replace(a, b)


def main():
    os.makedirs(BK, exist_ok=True)
    dst = os.path.join(BK, "pre214_live.lua")
    if not os.path.exists(dst):
        shutil.copy2(LIVE, dst)
    elif "--again" in sys.argv:
        shutil.copy2(dst, LIVE)
    s = open(LIVE, encoding="utf-8", newline="").read()
    assert "ROUND 214" not in s
    s = one(s, A_POLL, N_FN, "poll")
    for a, b in EDITS:
        s = one(s, a, b, a[:40])
    open(LIVE, "w", encoding="utf-8", newline="").write(s)
    print("patched", LIVE)


if __name__ == "__main__":
    main()
