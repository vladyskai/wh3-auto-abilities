# Final stable: 2026-10-03 - critique-2 complete
Player-verified in play. Pack md5 is an identifier (see PACK_MD5.txt).

Applied this wave: 2+13 (single drop routine purging all 14 per-unit tables), 3 (gone_ids list, no
outer-loop break), 5 (identity nil never cached + identity_checked flag), 10+11 (owned-marker cache in
the letter test and walk gate), 14+6 (cached ui id, ordered card sweep, drop matches on the cache),
12 (one active-set refresh per tick instead of N), 1 (all_buttons_found tests the ACTIVE set - the HUD
walk now stops entirely when nothing of ours can be on the dial; measured 0 walks in 500 ticks vs 5).

Reverted: 15 (preferring the visible button family changes the bar ordinal 3->1 and collapses badges
onto the top slot - the HIDDEN bar family supplies the ordinals; never change the claim source).
Not implemented (no evidence in 111 sessions / 42 MB of log): 4 (callback error counter).
Open/known-accepted: cooldown holds logged as REJECTED with an 8 s back-off and coalescing; the 5 s
safety walk still exists as a layer but is unreachable when the active set has no unclaimed members.
