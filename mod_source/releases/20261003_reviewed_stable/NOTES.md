# Stable: 2026-10-03 — post-review build (all critique items applied)
Player-verified in game. Installed pack md5 as in PACK_MD5.txt.
Fixed since 20261003_responsive_badges_stable, in order:
- 4.7 release_control runs ONLY after a take_control that actually succeeded (was 210 phantom calls/battle; now zero).
- 4.2 CARD_SWEEP_MAX 12 -> 40, reframed as a runaway guard (panels top out at 20); walk cost measured unchanged.
- 3.5 fire the ability key the unit scan already found (readiness queries halved; no phantom variant query).
- 2.3 discard_badge: Destroy() the engine component before clearing the reference on mid-creation failures.
- 4.4 no auto-fire while routing (pcall'd, fail-open); one routing read per unit per poll.
- 4.3 additive 10 s re-list: mid-battle arrivals (summons/splits) tracked; dead units dropped.
- 3.4 rescan only when the unit's engine identity (battle_unit:type()) changes; 60 s fallback.
- 1.1 reasoned HUD-walk gate: walk on selection change / new unit / unclaimed owned key (200 ms) / 5 s safety net.
  Field result: ability-button log lines 3803 -> 198 (-95%), session 10841 -> 6483 lines.
- Multi-select badge toggling via the engine's own selection callback (card states cannot see group selections).
- Dead-unit hardening: pre-fire validity check; a rejection naming a non-existent unit drops it once with a
  sticky gone_units set. NOTE: the engine's cooldown text is "does not support this special ability" - it must
  never be keyed as a death. The 55 "REJECTED" lines in the previous session were normal cooldown holds.
Known, accepted: cooldown holds are logged as REJECTED lines (noise only). Candidate future item: gate on the
ability button's own cooldown state to cut those.
