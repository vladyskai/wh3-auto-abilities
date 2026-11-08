# Stable: 2026-10-02 — two abilities, both clickable M/A badges, no crash
Working in game (confirmed by the player):
- Deadly Onslaught: fires on the charge when armed. Foe-Seeker: fires when the unit runs when armed.
- Both badges on their measured wheel slots (top + 45 deg), each independent: click to flip M <-> A.
- Matching by exact key (both Foe-Seeker variants listed). NO string.find anywhere (it crashed the game).
- Readiness gate (can_perform_special_ability) + 2 s guard; no hardcoded 60/90 s timers.
- CLAIM_BISECT = 9 stays in the shipped source as the diagnostic ladder; diagnostics (scan probes,
  inventory sweep, dial dump) are still enabled and can be trimmed later.
- Known crash causes fixed here, do not repeat: 4-arg string.find; Id()-must-be-string gates;
  badge creation inside the walk; malformed hand-written ui/ layouts.
