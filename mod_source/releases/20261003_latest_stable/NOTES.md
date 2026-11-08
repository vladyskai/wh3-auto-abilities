# Stable: 2026-10-03 (latest) - second wave, all applied critique items
Player-verified. The archived pack is byte-identical to the installed build (md5 in PACK_MD5.txt).

Applied in this wave (on top of 20261003_reviewed_stable):
- Multi-select badge toggling via the engine's own per-unit selection callback
  (card states cannot see group selections - the engine API is the only way).
- 1.1 reasoned HUD-walk gate: walk on selection change / new tracked unit / unclaimed owned key (200 ms)
  / 5 s safety net. Field effect: ability-button log lines -95%, session lines ~-40%.
- 1.3 poll_body iterates only the markers a unit owns (unknown cache -> full table). Evals: 3->1 per unit,
  30->10 for a ten-unit army, 0 for a unit owning nothing. Firing decisions byte-identical.
- 1.4 active_abilities set for the ui-tick badge/letter paths (owned markers + claimed markers,
  full-table fallback at bootstrap). 3->1 iterations per pass.
- 2.1 arming + guard state as nested tables armed[ui_id][marker] (no composite string keys anywhere).
  Reads never allocate. NOTE: engine ids are numbers, click paths carry text - the unit_slot() normaliser
  is what keeps them the same key. Do not remove it.
- 3.1 ability_for / ability_for_badge / the scan's key test are load-time maps (0 table iterations per call,
  was 1). Map==table equivalence is asserted in the harness.
- Dead-unit hardening: pre-fire validity check + a rejection naming a NON-EXISTENT unit drops it once
  (sticky gone_units). CRITICAL: the engine's cooldown text is "does not support this special ability" -
  never key a drop on it. Verified in a battle where a unit died: zero dead-unit firing, zero errors.

KNOWN, ACCEPTED NOISE (candidate next item): cooldown holds are logged as REJECTED lines - 162 in the last
battle. The ability button's own state reports cooldown; gating the ATTEMPT on it would remove most of this.
