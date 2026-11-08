# WH3 Auto-Ability Mod — Analysis of Critique V2

**Method:** every claim checked against the *current* installed source
(`WH3_mod/mod_source\script\battle\mod\zz_test_deadly_onslaught.lua`, md5 `0a431a98…`, the four-ability build),
against the engine's own code dumps, and against what we measured in play. Line numbers are the live file's.

**Verdict key:** `Confirmed` (the code does this) · `Partly` (real, but the description or the severity is off) ·
`Already addressed` (fixed tonight before the critique was written) · `Wrong` (the code does not do this) ·
`Expansion-gated` (deliberate now, mandatory when the ability table grows).
**Priority:** H = correctness/now · M = worth doing · L = low. **Difficulty:** L / M / H.

## Summary

| # | Item | Verdict | P | D |
|---|------|---------|---|---|
| 1 | `all_buttons_found()` gate at scale | Partly — the gate does exist, but 1.1 already governs when it walks | M (expansion) | L |
| 2 | State leak on drop (selected set + caches) | **Confirmed** | **H** | **L** |
| 3 | Poll `break` aborts the whole army's tick | **Confirmed** | **H** | **L** |
| 4 | Silent callback failure (no fallback) | Confirmed, softened by the card reconciliation | M | L |
| 5 | Identity watch ignores a nil-cached read | **Confirmed** | M-H | L |
| 6 | Zombie units linger in the watch list | Partly (the read is pcall'd; the *match* still fails) | M | L |
| 7 | Hardcoded targeting (`FOURTH` table) | Expansion-gated (by design) | H at expansion | M |
| 8 | Monolithic trigger chain | Expansion-gated (by design) | M at expansion | M |
| 9 | Fixed 0-degree ground casts | Expansion-gated; harmless for the current ability | M at expansion | M |
| 10 | `collective_armed` → `unit_owns_marker` string loop | Confirmed (cheap today, wrong shape at scale) | M | L |
| 11 | `selected_unit_owns_unclaimed_key` scans the global table | Confirmed | M | L |
| 12 | Redundant `refresh_active_abilities()` per unit | Partly (cheap, not "stuttering") | L | L |
| 13 | Per-unit caches never purged (leak) | **Confirmed** (same fix as #2) | M | L |
| 14 | `pairs()` order + cap ⇒ sweep flicker | Confirmed — and we measured it ourselves | M | L |
| 15 | Ghost badges on hidden buttons | Confirmed as a risk; our claim happens to land right | M | L |
| 16 | Ghost badges via active-set dropout | **Wrong — already guarded** | — | — |
| 17 | `slot_index` not refreshed on recycling | **Wrong — refreshed on every claim** | — | — |

---

## Critical execution & logic

### 1 — The `all_buttons_found()` gate at scale  (Partly)
`all_buttons_found()` (L3006) still returns "all four of our abilities have claimed buttons", and the walk gate is
still `if not all_buttons_found() then … end` (L4562). So the critique's *mechanism* is right. Its *consequence* is
not: since item 1.1, the walk no longer runs every other tick. It runs on a selection change, on a newly tracked
unit, briskly (~200 ms) only while an *owned* key's claim is missing, and otherwise once per 5 s. With 500 abilities
`all_buttons_found()` would be false nearly always, so the cost becomes the 5 s safety net plus any unclaimed owned
key — not "constantly tanking the frame rate". **Fix worth doing anyway:** redefine `all_buttons_found()` against the
active set / the selected unit's owned markers, which lets the safety net stop entirely. **P: M at expansion. D: L.**

### 2 — State leak on drop  (Confirmed — the most serious item here)
`drop_unit_by_ui_id` (L1744) purges exactly three things: `gone_units`, `tracked_units` and `units_by_ui_id`. It does
**not** touch `selected_ui_ids`, `armed`, `last_attempt_at`, `cooldown_hold`, `identity_by_unit`, `target_key_by_unit`,
`owned_keys_by_unit` or `owned_abilities_by_unit`. Consequences: (a) a dead unit can stay in `selected_ui_ids`
indefinitely, and with its arming entry either present (stale "armed") or purged (false), the **collective letter for
the group is computed from a unit that no longer exists** — the failure modes are "stuck showing A" or "stuck showing
M" depending on which tables were touched; (b) every cache keeps growing. The engine usually deselects a dead unit,
so this is often self-healing — which is exactly why it has not shown up in play, and exactly why it should be fixed
rather than relied on. **P: H. D: L** (one purge loop in the drop path).

### 3 — The poll `break` aborts the army's tick  (Confirmed)
The fire outcome `"gone"` sets `gone_ui_id` and breaks the inner loop (L2024-2026) — correct — but then
**L2059 `if gone_ui_id ~= nil then break end`** breaks out of the *unit* loop as well. Every remaining unit in the
army is skipped for that 250 ms tick, on the tick where a unit died. One lost tick is small, but it is wrong, and
it was my own spec's ambiguity that produced it ("breaks the walk … drops after the loop" — the drop *is* after the
loop; the unit loop should not break). **P: H. D: L** (`break` → continue the outer loop, drop the unit at the end).

### 4 — Silent callback failure  (Confirmed, softened)
There is a `selection_callback_alive` flag (L400), set true on the first delivered event (L740) — but **no error
counter exists anywhere** (the critique's `engine_selection_callback_errors` does not appear in the file). So a
callback that starts throwing stays "alive" forever. Mitigation we already have: the card sweep is not *gated* on the
flag — it reconciles additively — so selection tracking degrades rather than stopping. **Fix:** count swallowed
callback errors and flip the flag past a small threshold, taking the pre-callback code path. **P: M. D: L.**

### 5 — Identity watch ignores a nil-cached read  (Confirmed — exactly as described)
L1867 caches the new identity **unconditionally**, and L1869 requires `old_identity ~= nil and new_identity ~= nil`.
So: first read returns nil (transient) → nil is cached → the next *good* read is compared against nil → never
"moved" → no rescan until the 60 s fallback. For a transformation that is up to a minute of the mod not knowing the
new form's abilities. **Fix is exactly the critique's:** trigger on `new ~= nil and new ~= old`, and never cache a
nil read. **P: M-H. D: L.**

### 6 — Zombie units in the watch list  (Partly)
The drop routine's read *is* guarded — `pcall(function() return unit:unique_ui_id() end)` — so no crash, contra the
critique. But the guard cuts the other way: when the read fails, `same` stays false and **the dead unit is not
removed** from `tracked_units`. The alive check keeps it from firing, so the impact is a permanent dead entry that
consumes a poll slot. **Fix (as proposed):** cache the ui id on the wrapper at registration and use the cache for
matching. **P: M. D: L.**

## Architectural / expansion

### 7 — Hardcoded targeting typology  (Expansion-gated by design)
`FOURTH` holds the ground keys and a dedicated cast function. That was deliberate: Stand Your Ground was the *first*
targeted ability and I did not want to redesign the table for one case. It is precisely item 4.1, and it is the
gate for the expansion. **Fix:** `target_type` on each table entry, one routing function, the ground-key list gone.
**P: H at expansion. D: M.**

### 8 — Monolithic trigger chain  (Expansion-gated by design)
The `if/elseif ability.trigger == …` chain is the readable form at four abilities and the annotated reading copy
depends on it. At dozens it must become `ability.evaluate(unit)`. **P: M at expansion. D: M.**

DONE 2026-10-04 - replaced with per-entry ability.evaluate(unit) at 33 entries; five shipped abilities' behaviour + log text byte-identical (harness82: all 1720 pre-existing checks unchanged); annotated reading copy updated in step.

### 9 — Fixed 0-degree ground casts  (Expansion-gated; harmless today)
`perform_special_ability_ground(key, pos, 0, 0)` — the current ability is a non-directional area buff, so the angle is
meaningless to it. It becomes a real bug only for directional casts (breath, wind), which also need a *target chooser*
(the genuinely hard part of 4.1). **P: M at expansion. D: M.**

## Performance & memory

### 10 — `collective_armed` → `unit_owns_marker`  (Confirmed; cheap now, wrong shape at scale)
The collective letter test walks the selected units and, per unit, searches its owned keys by string comparison. At
four abilities and a handful of selected units this is nothing; the critique's "tens of thousands every 50 ms" is an
expansion-scale projection. The fix is real and now trivial: **item 1.3 already built `owned_abilities_by_unit`** —
the mapped marker list — so this becomes a direct lookup. **P: M. D: L.**

### 11 — `selected_unit_owns_unclaimed_key()`  (Confirmed — I left this one in on purpose)
It iterates the global table every gate evaluation. I noted it as deliberately-left during item 1.4; the critique is
right that it should iterate the selected unit's owned markers instead. **P: M. D: L.**

### 12 — Redundant `refresh_active_abilities()`  (Partly)
The refresh does run from the scan path, which the 60 s fallback can hit per unit in one tick. But the refresh is a
pass over units × owned markers — cheap — and it logs only on change, so there is no "stuttering" or log flood.
Hoisting it to once per tick if a flag tripped is good hygiene. **P: L. D: L.**

### 13 — Per-unit caches never purged  (Confirmed — same fix as #2)
See #2. Growth is bounded by the number of units a battle ever contains (dozens), so the leak is tiny in practice —
but it is one purge loop away from being correct, and it shares the fix with a real correctness bug. **P: M. D: L.**

### 14 — `pairs()` order + cap ⇒ sweep flicker  (Confirmed — with our own evidence)
`read_tracked_card_states` builds its wanted list from `pairs(units_by_ui_id)`, which has no defined order, and caps
it. We *measured* this class of problem while fixing §4.2: the harness had to self-calibrate because the old cap's
drop set varied with per-process hash order. Above the cap the subset can differ call to call. **Fix:** iterate the
ordered `tracked_units` array. **P: M. D: L.**

## UI and badges

### 15 — Ghost badges on engine-hidden buttons  (Confirmed as a risk)
`marker_claimed_now` judges by the button's script key. The engine hides rather than destroys buttons — our own
inventory dumps show duplicate components carrying the same key with different visibility (`button_order1`
`visible=false` alongside `button_ability` `visible=true`). If the claim ever matches the hidden copy, a badge is
drawn against an invisible button. In play our placement has always landed on the visible one, so this is hardening
rather than a reported bug. **Fix:** require the component to be visible before claiming. **P: M. D: L.**

### 16 — Ghost badges via active-set dropout  (Wrong — already guarded)
`active_abilities` is the union of owned markers **and currently claimed markers**, so a badge that is on screen can
never drop out of the set. The one path where a claim dies sets `active_dropped` (L4439) *inside* the show/hide loop
and only calls `refresh_active_abilities()` **after** that loop (L4488) — the hide runs first, in the same tick. No
orphan is possible. **No action.**

### 17 — `slot_index` not refreshed on component recycling  (Wrong)
`slot_index[marker]` is written on **every** claim (L3132, with the comment saying so) and nil'd when a claim is
lost (L3137/3141) — it is not gated on `state.button == nil`. The badge's offset is recomputed from it at placement,
which is why the badge follows an ability that sits in different slots on different units — something we fixed and
you verified earlier. **No action.**

---

## Proposed implementation order (high priority + low difficulty first)

1. **#2 + #13 — purge everything on drop** (H/L). One loop; fixes the stale-collective-letter class and the cache leak.
2. **#3 — stop breaking the unit loop** (H/L). One flag; a death no longer costs the army its tick.
3. **#5 — identity: never cache nil, rescan when it changes** (M-H/L). Removes up to 60 s of post-transformation blindness.
4. **#15 — require a visible button before claiming** (M/L). Closes the ghost-badge class we have already seen hints of.
5. **#10 + #11 — use the owned-marker cache in the letter and gate lookups** (M/L). Hot-path shape, near-zero risk.
6. **#14 — ordered card sweep** (M/L). Kills the flicker class we measured while fixing §4.2.
7. **#4 — callback error counter → flag flip** (M/L). Graceful degradation if the engine API misbehaves.
8. **#6 — cache the ui id at registration** (M/L). Also makes the drop match reliable.
9. **#12 — hoist the active-set refresh** (L/L). Hygiene.
10. **#1 — redefine `all_buttons_found()` against the active/owned set** (M/L now, L at expansion). Lets the 5 s net stop.
11. **The expansion set: #7 targeting typology + #8 trigger functions + #9 dynamic bearing** (H/M/M) — one designed
    round, to be done *with* the ability-table growth rather than after it.

## Two things the critique got wrong, with the evidence
- **#16** — it assumes a badge can leave the active set while displayed. It cannot: claimed markers are members, and
  the drop path hides before the set shrinks (L4439/L4488).
- **#17** — it reads `slot_index` as conditionally updated; L3128-3141 show it refreshed on every claim and cleared on
  loss, which is why per-unit slot differences already work.
