# Stable: 2026-10-03 — critique-2 wave (applied items + one revert)

Player-verified. The archived pack is byte-identical to the installed build (identifier in
PACK_MD5.txt). Pack content is proven by the build's per-file sha256 gate (packed script
byte-identical to source), not by the pack md5 — see the note at the bottom.

Source:      script/battle/mod/zz_test_deadly_onslaught.lua
             md5 40e575e6c6e51232c449f27caed52b65
Annotated:   C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua
             md5 72a19b78be359cbe3f7ccc48cb4521e8
Pack (identifier): 19d7c4df0caec212914265675d8d1374

## Applied in this wave

- **Items 2 + 13 — single drop routine.** All per-unit removal is now funnelled through ONE
  drop routine that purges every one of the 14 per-unit tables in a single place. Previously
  each table was cleared at its own call site, so a partially-dropped unit could leave stale
  rows behind. Adding a new per-unit table now means adding it to that one routine only.

- **Item 3 — gone_ids set, no outer-loop break.** A dropped unit is recorded in a sticky
  `gone_ids` set consulted by the re-list, and the drop path no longer `break`s the outer
  loop — the loop keeps iterating so later units are still processed and no engine re-list can
  re-adopt a unit we already dropped.

- **Item 5 — identity nil never cached + identity_checked flag.** A nil engine identity read is
  never written into the cache (a transient failure can no longer erase the last good value),
  and a separate per-unit `identity_checked` flag is set on EVERY check (outcome-independent),
  so a unit that was checked while the cache was still empty is re-scanned as soon as a later
  read succeeds. Purged in the one drop routine alongside the cache.

- **Items 10 + 11 — owned-marker cache.** The badge-letter test and the HUD-walk gate both read
  from one owned-marker cache instead of re-deriving "does this unit own the marker?" each pass.

- **Items 14 + 6 — cached ui id, ordered card sweep, drop matches on the cache.** The card sweep
  runs in a deterministic order over a cached ui id, and the drop path matches units against
  that same cache, so a unit cannot be dropped by an id that the sweep never produced.

## REVERTED — item 15 (do not re-apply without a live battle)

Item 15 proposed preferring the **visible** button family (`button_ability*`) as the claim
source instead of the hidden bar family (`button_order*`).

Reverted. Reason: the two families are different subtrees with different child ordinals, and
`WHEEL_SLOT` was measured against the **hidden** family's ordinals. Preferring the visible
family changes the bar ordinal 3 -> 1 and collapses the badges onto the TOP slot (live proof:
both abilities logged `is bar position 1 -> wheel slot (96,845)`, dragging `stand_your_ground`
off its real slot 3 / (194,947)). The hidden bar family supplies the ordinals — keep it as the
claim source.

Lessons from item 15:
- The premise that motivated it never occurs: across 61,176 inventory lines no ability key
  ever appeared on a hidden component without a visible twin.
- Claim-SOURCE changes are live-battle-only: the mock harness's tree is the harness author's
  construction, so its child order agrees with whatever family the round prefers. Only a live
  battle exposes the real subtree's ordinals.
- Never ship a claim-source change without a live battle behind it; revert immediately on any
  bar-position / wheel-slot regression.

## KNOWN / ACCEPTED (not regressions)

- **Cooldown holds logged as REJECTED.** The engine's cooldown text is the SAME string as its
  dead-unit text ("... does not support this special ability"), and it is a HOLD — one ui id
  produced it ~48x and later ACCEPTED a fire. A rejection-informed back-off is in place: the
  longer interval is armed only on the SECOND consecutive refusal (per-(unit,marker) streak),
  and the first refusal of an episode is logged once with repeats suppressed. A hard
  `MAX_HOLD_TICKS` bound forces a re-probe and re-bases `since`. This is accepted noise, not a
  bug.

- **The 5 s safety walk still runs while `all_buttons_found()` is false — critique-2 item 1,
  STILL OPEN.** The HUD walk gate includes a 5 s safety net that fires whenever not all ability
  buttons have been found. This is the one outstanding critique-2 item and was deliberately NOT
  changed in this wave.

## Why the pack md5 is not a reproducibility target

RPFM stamps the build's SAVE TIME into the pack header, so rebuilding identical content yields
a different pack md5 every time. The pack md5 above is only an **identifier** for this specific
built artifact. Build content is proven by the per-file sha256 gate in `build_and_install.py`
(packed script byte-identical to source), never by matching the pack hash.
