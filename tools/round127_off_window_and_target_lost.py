#!/usr/bin/env python3
"""Round 127 (harness 126): the firing flag's OFF window and the target-lost fix.

User approval 2026-11-03 ("Yes, both"), after the round-126 field battle
(docs/WH3_round126_field_firing_analysis.md):
  (1) OFF window = max(2 x reload, 20 s). Land Ships, Steam Tanks and hunter
      characters fire SLOWER than their table reload (Land Ship 10 s -> 13 s real,
      Steam Tank 10 s -> 19.75 s, Witch Hunter 4 s -> 16 s), so 1.25 x reload split
      them into one episode per shot (64 episodes for 38 firing units; this window
      gives 43 on the same shots). A unit missing from the table uses the 20 s
      minimum (was a 10 s default). AMMO_WINDOW_DEFAULT_S is deleted.
  (2) THE BUG: when a unit's target disappears, the OUT OF RANGE line formatted a
      nil distance and range, raised inside the probe's pcall, lost the line and
      skipped the remaining units for that poll. It now logs "target lost".
Applied to the live source and the annotated (log-free) copy.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

COMMON = [
    ("""--   * FIRING OFF  once no drop has been seen for AMMO_OFF_FACTOR (1.25) x the
--                 unit's reload (AMMO_WINDOW_DEFAULT_S for a unit missing from
--                 the table). The round-125 rule (1.25 x the most recent
--                 measured gap) flickered on every unit in the field and is gone;
""",
     """--   * FIRING OFF  once no drop has been seen for max(AMMO_OFF_FACTOR (2) x
--                 the unit's reload, AMMO_OFF_MIN_S (20 s)); a unit missing from
--                 the table uses the 20 s minimum. ROUND 127: the round-126
--                 window (1.25 x reload) split Land Ships, Steam Tanks and hunter
--                 characters into one episode per shot - they fire SLOWER than
--                 their table reload (field battle 2026-11-03). The round-125
--                 rule (1.25 x the most recent measured gap) is long gone;
"""),
    ("""FOURTH.AMMO_WINDOW_DEFAULT_S = 10     -- FIRING OFF window for a ranged unit missing from FOURTH.RELOAD_S
FOURTH.AMMO_OFF_FACTOR = 1.25         -- FIRING OFF after 1.25 x the unit's reload with no drop
""",
     """FOURTH.AMMO_OFF_FACTOR = 2            -- FIRING OFF after 2 x the unit's reload with no drop ...
FOURTH.AMMO_OFF_MIN_S = 20            -- ... but never sooner than 20 s (and 20 s for a unit missing from the table)
"""),
    ("""					local window = (st.reload ~= nil) and (FOURTH.AMMO_OFF_FACTOR * st.reload)
						or FOURTH.AMMO_WINDOW_DEFAULT_S
""",
     """					local window = FOURTH.AMMO_OFF_MIN_S
					if st.reload ~= nil and FOURTH.AMMO_OFF_FACTOR * st.reload > window then
						window = FOURTH.AMMO_OFF_FACTOR * st.reload
					end
"""),
]
LIVE_ONLY = [
    ("""					local who = FOURTH.ammo_describe(u)
					log(string.format("OUT OF RANGE %s at t=%.2fs: target at %.1fm > missile range %.1fm", who, now_s, d, r))
""",
     """					local who = FOURTH.ammo_describe(u)
					-- ROUND 127: a target that DISAPPEARED has no distance or range to
					-- print; formatting them raised, lost this line and skipped the rest
					-- of the army for the poll.
					if d ~= nil and r ~= nil then
						log(string.format("OUT OF RANGE %s at t=%.2fs: target at %.1fm > missile range %.1fm", who, now_s, d, r))
					else
						log(string.format("OUT OF RANGE %s at t=%.2fs: target lost (no current target)", who, now_s))
					end
"""),
    ("""							st.reload and string.format(" = %g x reload %gs", FOURTH.AMMO_OFF_FACTOR, st.reload)
								or ", no reload in the table: default"))
""",
     """							(st.reload == nil and ", no reload in the table: the 20 s minimum")
								or (FOURTH.AMMO_OFF_FACTOR * st.reload > FOURTH.AMMO_OFF_MIN_S
									and string.format(" = %g x reload %gs", FOURTH.AMMO_OFF_FACTOR, st.reload))
								or string.format(", the 20 s minimum (%g x reload %gs is shorter)", FOURTH.AMMO_OFF_FACTOR, st.reload)))
"""),
]

for path, edits in ((SRC, COMMON + LIVE_ONLY), (ANN, COMMON)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "\r\n" not in s and "AMMO_OFF_MIN_S" not in s, path
    for i, (a, b) in enumerate(edits, 1):
        n = s.count(a)
        assert n == 1, (path.split("\\")[-1], "edit", i, "anchor count", n)
        s = s.replace(a, b, 1)
    assert "AMMO_WINDOW_DEFAULT_S" not in s, "the deleted constant survived"
    assert "\u2014" not in "".join(b for _, b in edits)
    if path == ANN:
        assert "log(" not in s.split("-- ROUND 126 - THE FIRING FLAG")[1].split("local function poll_body()")[0]
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("applied %d edits:" % len(edits), path.split("\\")[-1])
