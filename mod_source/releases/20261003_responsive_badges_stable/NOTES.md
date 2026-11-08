# Stable: 2026-10-03 — responsive M/A badges, per-unit, two abilities
Confirmed working in game (player-verified):
- Deadly Onslaught fires on the charge; Foe-Seeker when running; per unit, per ability, armed by clicking that ability's M/A badge.
- The badge sits on the ability's own wheel slot (static measured table, bar ordinal -> wheel slot).
- Selection follows the engine's own card state ('selected'), sampled every ui tick (50 ms registration; engine resolves at 100-200 ms).
- Card clicks refresh the letters synchronously inside the click handler.
- LATENCY FIX: UIComponent:Layout() (pcall'd) on the badge AND its parent immediately after every real SetText makes the
  engine repaint the letter promptly - without it, flips lag ~0.5 s. This was the ONLY redraw-adjacent method in the
  game's 141-method UI API (no Update/Refresh/Redraw exists).
- Hiding: badges hide whenever their ability is not claimed on the selected unit's dial; clicks on unclaimed badges are ignored.
- Matching by exact key equality; string.find is BANNED in this project (the 4-arg plain form crashes the engine).
- CLAIM_BISECT=9 ladder and diagnostics (probes, census, inventory, dial dump) still enabled - trim later for smaller logs.
