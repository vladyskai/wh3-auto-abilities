# WH3 Auto-Ability Mod — Analysis of the Critique Document

**What was checked:** every item in `wh3_auto_ability_script_critique.md` against (a) the *installed* mod source
(`WH3_mod/mod_source\script\battle\mod\zz_test_deadly_onslaught.lua`, the live file — line numbers below are that
file's), (b) our own measured, in-game evidence (runtime logs, harnesses, dial dumps, past field tests), and
(c) the *current* game's own code (the UIC / unit-API dumps we extracted from it).

**Verdict scale:** `Confirmed` = the code really does this / the fix really is needed. `Partly` = something real, but
the description or the numbers are wrong. `Wrong` = the code does not do what the item claims. `Reject` = the fix
would hurt or is proven infeasible here.
**Priority:** H = fix now, it affects the installed mod. M = worth doing before or with the expansion. L = real but
low impact today. **Difficulty:** L / M / H.

---

## Summary table

| # | Item | Verdict | Priority | Difficulty | One-line action |
|---|------|---------|----------|-----------|-----------------|
| 1.1 | Scanner never finishes at scale | Confirmed (future-only) | L now / H at expansion | M | Build an "active abilities" set from the roster, not a global search |
| 1.2 | Fast-loop card walk | Partly (numbers inflated) | L | L-M | No change; the card walk is not the HUD walk |
| 1.3 | Poll matrix units × ability table | Confirmed at scale | M (expansion) | M | Poll only the unit's owned keys |
| 1.4 | UI tick loops over the whole table | Confirmed at scale | M (expansion) | L-M | Same active-set fix as 1.1 |
| 1.5 | Trim the pcall safety net | **Reject** | — | — | Keep; every crash we ever had came from an unguarded engine read |
| 2.1 | String keys for arming state | Confirmed | M (expansion) | M | Nested table `armed[ui_id][marker]` |
| 2.2 | Table thrash in the card sweep | Partly | L | M | Low value; careful if ever done (aliasing risk) |
| 2.3 | Orphaned badge components on failure | **Confirmed** (`Destroy` exists) | M-H | L-M | Destroy before nil on mid-creation failures |
| 3.1 | Array scan of ALL_ABILITY_KEYS | Confirmed, over-ranked | L | L | Add a parallel map for membership; keep the array for order |
| 3.2 | Hardcoded trigger chain | Confirmed at scale, deliberate now | L now / M at expansion | M | Function-per-trigger when the table grows |
| 3.3 | Duplicated charge measurement | **Likely wrong** | L | L | Verify in the round; hoist only if per-ability |
| 3.4 | 4 s rescan of ability-less units | Confirmed, deliberate, cheap | L | L | Optional "scanned, none" flag |
| 3.5 | Cached key not used when firing | **Confirmed** | M | L | Fire the key the scan already found |
| 4.1 | Self-targeting casts | Confirmed, **by design** for these three | L now / H at expansion | M-H | Add targeting typology when adding targeted abilities |
| 4.2 | `CARD_SWEEP_MAX = 12` cap | **Confirmed — real** | M-H | L | Raise/adapt the cap; measure the sweep cost |
| 4.3 | Summoned / mid-battle units invisible | Partly (fact wrong, gap real) | M | L-M | Low-frequency re-list or unit-created events |
| 4.4 | Firing while routing | Plausible; engine has `is_routing` | M | L | Add a routing guard once the accessor is confirmed |
| 4.5 | Charge window constants | Partly (eta already speed-aware) | Your call | M | Optionally derive the window from time-to-contact alone |
| 4.6 | 2 s guard assumes success | Confirmed; keep | L | — | Keep; a post-hoc check would be fragile |
| 4.7 | Control-hijack leftovers | **Confirmed live** (210 calls in the log) | **H** | **L** | Release only what we took |
| 5.1 | Resolution-hardcoded offsets | Confirmed (other setups); dynamic fix infeasible here | L | M | Calibrate per setup; `zz_badge_*` hooks exist in the installed mod |
| 5.2 | 6-slot wheel matrix | Confirmed at expansion | M (expansion) | M | Extend the measured matrix the way the 6 were measured |
| 5.3 | Batch the layout nudges | **Reject** | — | — | Would re-introduce the exact latency we removed |

**Tally:** 15 Confirmed (4 of them only at expansion scale), 4 Partly, 1 likely Wrong, 2 Reject.

---

## Per-item detail

### 1.1 — "The scanner never finishes when the table grows"
**Confirmed, but it does not hurt today.** `all_buttons_found()` (L1834) gates the HUD walk: the ui tick walks only
`if not all_buttons_found() and (ui_ticks % 2) == 0` (L3165), and a single walk is capped at 4000 visited nodes
(L2020) with an early-out (L2053). Today the lookup finishes in the opening seconds of a battle — the log shows
`scan done: 612 component(s) visited` and the claims complete — so the cost after that is **zero**. With hundreds of
abilities the gate can never close and the walk would run ~10×/s forever. The critique's "4000" is the *cap* we
chose, not the observed cost (612 measured). **Pros of fixing:** mandatory before expansion. **Cons:** the
suggested fix ("scan only the selected unit") is wrong shape — the dial belongs to whoever is selected and changes
constantly; the right version is to build the "active abilities" set from the army roster's owned keys (we already
read owned keys per unit during detection) and search only for those. **P: L now, H at expansion. D: M.**

### 1.2 — "Catastrophic UI walk in the 50 ms loop"
**Partly — the mechanism exists, the numbers are inflated.** The fast selection path (L2907) runs every ui tick and
calls `read_tracked_card_states()` (L2776) → `card_collect_from()` (L2734) — but that walks the **unit-card panel's
cards** (capped, L2781), *not* the whole HUD. The 900/4000-node figures in the critique belong to the separate HUD
walk above. Measured: this has run in every battle since the multi-unit build with no observed degradation, in your
own sessions. **Pros of caching card handles:** none today. **Cons:** cached handles go stale when the panel
rebuilds — we lived that exact bug (the era where a click on one card toggled another unit) and re-fetching per
sweep was the fix; caching would re-introduce it without a re-validation path. **P: L. D: L-M. Action: none now.**

### 1.3 — "Polling matrix: units × entire ability table"
**Confirmed at scale, trivial at 3.** `poll_body` iterates tracked units and, inside, `ipairs(ABILITIES)` (L873 and
neighbours). Three abilities ≈ 120 iterations per 250 ms — nothing. Hundreds × a 40-unit army would be real
(same order as the critique's 20 000). The fix — store the unit's *owned keys* on its state when it is scanned and
poll only those — is sound and is also exactly what fixes item 3.5. **P: M (do it in the expansion round). D: M.**

### 1.4 — "UI tick iterates 500+ abilities every 50 ms"
**Confirmed at scale, trivial now.** The ui tick loops the table for badge build/show/hide (the L311/L546 region).
At three entries it is free. The fix is the same "active set" as 1.1 — build it once, iterate it everywhere.
**P: M at expansion. D: L-M (bundle with 1.1).**

### 1.5 — "Excessive pcall usage"
**Reject.** The file has 113 pcall sites, and every hard crash this project ever suffered came from an *unguarded*
engine read: a key-length read that returned a string (`attempt to compare string with number` killing an entire
battle), `Id()` on the ability button returning a function, and stale component handles after menu use. The pcalls
are field-earned, not paranoia. The cost is nothing — the readiness read guarded is ~1 call per unit-ability per
250 ms. The one method the critique names (`can_perform_special_ability`) is exactly the kind of call that sits on a
possibly-stale handle; it stays guarded. **Action: keep as-is; the annotated copy already explains why.**

### 2.1 — "String concatenation keys for armed state"
**Confirmed.** Four sites build `tostring(ui_id) .. "|" .. marker` string keys (L290, L917, L1536, L2240). At three
abilities that is ~120 one-character-class strings per 250 ms — nothing, and no stutter was ever observed. At scale
it is genuine GC pressure, and the fix (a nested `armed[ui_id][marker]` table) is instant and allocation-free.
**Pros:** zero GC, faster. **Cons:** mechanical risk across four sites plus whatever clears/reset the arming state —
must be done with the harness watching. **P: M at expansion. D: M.**

### 2.2 — "Memory thrashing in the card sweep"
**Partly; impact overstated.** `read_tracked_card_states` does create three small tables and a sort per call, 20×/s
— that is 60 small tables/s, not "hundreds", and it has never shown as a stutter. Buffer reuse is a valid
technique but low value here and it introduces aliasing risk if the buffers are reused across the two cadences that
share the reader. **P: L. D: M if ever done.**

### 2.3 — "Orphaned UI components leak on badge-creation failure"
**Confirmed — and better than the critique knew: the engine's UIC has `Destroy`** (verified in the game's own
component dump: `Destroy`, `DestroyChildren`, `RemoveTopMost` exist). Seven sites set `state.badge = nil`
(L1167-L1254, L3050). On a *mid-creation* failure — after the component was made — dropping the Lua reference
leaves the engine-side component in the HUD forever, and the next tick builds another one. In normal battles
creation succeeds (your logs), but a systematic failure is exactly the menu-era failure mode we hit
(`hud_battle children=invalid`), and it would leak at the tick rate. Fix: `pcall(Destroy)` on the component before
clearing the reference, on the sites that can hold a created badge. **P: M-H. D: L-M.**

### 3.1 — "O(N·M) array lookup in scan_unit_abilities"
**Confirmed, but over-ranked.** `ALL_ABILITY_KEYS` is an array (L135-138) walked with `ipairs` inside the per-unit
scan (L382). Crucially the scan runs on detection/redetect paths (every 4 s at most, per unit) — not in the hot
loop. At 500 keys one scan is a few thousand string comparisons every 4 s: fine. If wanted anyway: keep the array
(ordered iteration elsewhere) and add a parallel membership map. **P: L. D: L.**

### 3.2 — "Hardcoded trigger chain becomes a monolith"
**Confirmed at scale; deliberate at three.** The poll evaluates `if trigger == "charge" … "running" … "melee"`.
At three abilities that is the readable form — the annotated file you are reading *depends* on it being a plain
chain. At dozens, evaluating `ability.evaluate_trigger(unit)` from the table is right. **Cons of switching early:**
it makes the reading copy harder to follow and moves trigger logic away from the file's spine; do it in the
expansion round, together with 1.1/1.3/1.4. **P: L now / M at expansion. D: M.**

DONE 2026-10-04 - replaced with per-entry ability.evaluate(unit) at 33 entries; five shipped abilities' behaviour + log text byte-identical (harness82: all 1720 pre-existing checks unchanged); annotated reading copy updated in step.

### 3.3 — "measure_charge runs once per ability"
**Likely wrong.** There are two call sites (L636, L883); L883 sits in the per-unit stretch of the poll loop, before
the per-ability evaluation — i.e. the structure already computes the charge measurement once per unit and reuses
it, which is precisely what the critique proposes as the fix. Verify against SECTION 7 of the annotated copy during
the implementation round; hoist only if it really is per-ability. **P: L. D: L.**

### 3.4 — "Units without abilities are rescanned every 4 s forever"
**Confirmed — and deliberate.** L861-862: a unit whose cached key is nil is rescanned every
`REDETECT_EVERY_N_POLLS` so that a mid-battle transform or mount can still be caught. The cost is a handful of
small scans per 4 s; the "forever" is a feature, not an oversight. If it ever matters: a "scanned, none" flag with
a rare recheck preserves the intent. **P: L. D: L.**

### 3.5 — "target_key_by_unit is a dead end"
**Confirmed — the best structural catch after 4.7.** The cache is written (L540, L864) and read only as a nil-gate
(L857); the firing/readiness path re-queries the engine for *every* key in the ability's key list from scratch.
The log line `readiness …: wh_main_…=true, wh_dlc04_…=false` you have seen is that double query. Fix: fire the key
the scan already found, keeping the list only as the scan's search set. Fewer engine calls, less log noise, and it
is the exact structure the expansion needs (owned keys cached per unit). **P: M. D: L.**

### 4.1 — "Self-targeting casts will fail for other abilities"
**Confirmed — and by design for the current three.** `perform_special_ability(key, unit)` casts on the caster;
correct for Onslaught, Foe-Seeker and Hammer of Sigmar, which are all self-centred (the ability database says
`affect_self` / `augment_melee_area`). It *would* fail for missiles, vortexes and targeted heals — but that is the
expansion's gate, not a bug today. When it comes: a targeting field in the table plus a target chooser; the chooser
(nearest enemy? lowest health? most valuable?) is the genuinely hard part and deserves its own design round.
**P: L now / H at expansion. D: M-H.**

### 4.2 — "The 12-card cap silently ignores units 13+"
**Confirmed — a real cap, cheap to fix.** `CARD_SWEEP_MAX = 12` (L2707), enforced by an early break once 12
wanted cards are found (L2781). A 20-card army means units past the twelfth in walk order never get their
selection state read — their badge letters would not follow a click (or the tracker would lag). Never hit in our
tests (Boris + a few heroes is under 12). Fix: raise to cover the panel maximum (~20) or make it adaptive; measure
the sweep cost at the new bound in the mock first. **P: M-H. D: L.**

### 4.3 — "Summoned / mid-battle units permanently ignored"
**Partly: the gap is real, the description is wrong.** `rebuild_unit_list` runs at startup (L2989) and is retried
in the poll *while the list is empty* (L844 — the crash-fix era), not "once on the first poll". The real gap: after
the first successful build it never runs again, so units that appear later (summons, Tzeentch splits, transformations)
are invisible to the mod. Fix: a low-frequency re-list (≈ every 10 s; the cost is trivial) or the engine's
unit-created event. **P: M. D: L-M.**

### 4.4 — "Firing while routing"
**Plausible — and the engine has the tools.** Verified in the game's own dumps: `battle_unit:is_routing` and
`battle_unit:is_shattered` exist. What still needs one grep during implementation: whether our script_unit handle
reaches the same test (the dump shows it on the battle_unit layer; `script_unit.lua` is on disk to check). If
reachable: add "not routing" to the running and melee triggers. **Pros:** stops burning a cooldown on a fleeing
unit that cannot profit from the buff. **Cons:** none meaningful. **P: M. D: L (if the accessor exists).**

### 4.5 — "Hardcoded charge window (12–60 m)"
**Partly — the window already listens to speed.** The gate is min 12 m / max 60 m **plus** time-to-contact ≤ 4 s,
and time-to-contact is computed from the unit's own speed inside `measure_charge` (L437: speed, facing, distance,
eta). So fast cavalry and slow dwarfs already converge on the eta rule; the residual hard part is the *distance*
bounds, especially the 12 m floor. The full fix — derive the window from eta alone (distance ≤ eta_max × own
speed, plus a sanity cap) — *changes firing behaviour* and deserves a field test of its own. **P: your call.
D: M.**

### 4.6 — "False-positive cooldown lock from the 2 s guard"
**Confirmed; recommend keeping.** `GUARD_SECONDS = 2` (L203/244) is set around the attempt; if the engine swallows
a cast (staggered unit etc.) we lose ≤2 s. The proposed alternative — confirm the cast by re-reading the engine's
readiness — is fragile: the engine's flip lags a frame or more, so the check itself would either miss or allow a
double-fire loop. Two seconds against 60–90 s cooldowns is noise; a doubled cast is not. **P: L. Action: keep,
documented.**

### 4.7 — "Control hijacking: take/release script control"
**Confirmed live — the critique's best catch.** `TAKE_CONTROL_FIRST = false` (L219) so `take_control` never runs
today — but `RELEASE_CONTROL_AFTER = true` (L223) stands alone, so **we call `release_control()` after every
single fire**. The runtime log proves it: **210 release calls** against 10 historical take calls (older builds),
every one answered `ok=true`. The engine accepts releasing control we never took; whether it flushes the unit's
order queue (the critique's concern) we cannot see from a log — but your field evidence says no dropped orders in
all this time. Either way it is pointless, and the fix is one linking condition: release only what we took.
**P: H (live, pointless, possibly cancelling orders). D: L.**

### 5.1 — "Hardcoded resolution offsets break on other setups"
**Confirmed for other setups — but the dynamic fix is proven infeasible in this engine.** We spent multiple rounds
trying to read the button's real screen position: `GetProperty` returns property *names*, `Position()` misreports
for script-created components, right/double-click events never reach script at all, and the dial's geometry itself
misled us (the circle you caught). What survived is the measured static offset table (two battles of dial dumps).
For *this* machine and display it has been stable through every test. If you ever change resolution or UI scale:
recalibrate — the installed mod still carries the `zz_badge_*` console hooks built for exactly that. **P: L now.
D: M for a calibration flow; dynamic anchoring: infeasible (measured).**

### 5.2 — "The 6-slot wheel assumption breaks past 6 abilities"
**Confirmed at expansion.** `WHEEL_SLOT` covers positions 1-6 (L1041); position 7+ hits the `slot = WHEEL_SLOT[k]`
miss (L1080) and falls back to a single backup offset — no crash, wrong spot. Lords and heroes with item abilities
routinely exceed six. The fix is the method that built the current table: a dial-dump measuring session, extended
to 7 and 8. Dynamic anchoring has the same infeasibility as 5.1. **P: M at expansion. D: M.**

### 5.3 — "Batch the layout recalculations"
**Reject — it would undo the responsiveness fix.** `nudge_badge_layout` exists to force the engine's repaint
*immediately after* a write; batching to one call per tick would delay it by up to a full tick — the exact latency
we removed two rounds ago. And the deduplication the critique asks for already exists: the letter cache means only
*changed* letters write and nudge (harness-measured: exactly one `SetText` per real flip; zero on idle ticks).
**P: —. Action: no change. Revisit only if `Layout` ever proves expensive at scale; it has not.**

---

## Proposed implementation order (high priority + low difficulty first)

1. **4.7 — release only what we took** (H / L). One linking condition; field question below.
2. **4.2 — raise/adapt the card cap** (M-H / L). Verify the sweep cost at the new bound in the mock.
3. **3.5 — fire the cached key** (M / L). Removes the double readiness query too.
4. **2.3 — destroy orphaned badges on failure** (M-H / L-M). `Destroy` verified to exist.
5. **4.3 — periodic unit re-list** (M / L-M). Summons and splits become visible.
6. **4.4 — routing guard** (M / L). After one grep of `script_unit.lua` for the accessor.
7. **3.4 — "scanned, none" flag** (L / L). Optional; fold into 5.
8. **Expansion round** — as one set: 1.1 + 1.4 (active set), 1.3 + 3.5 (owned-key polling), 2.1 (arming tables),
   3.2 (trigger functions), 3.1 (membership map). Do these *before* the table grows, not after.
9. **4.1 (targeting typology) and 5.2 (wheel matrix extension)** — when adding the first targeted ability and the
   first 7th-slot ability.
10. **4.5** — only if you decide the charge window should change behaviour; then with its own field test.

## Two questions for the field test

- **4.7:** since installing the mod, have you ever seen a unit ignore a move/attack order right after one of its
  abilities auto-fired? That would confirm the release-control concern; a clean record supports "harmless but
  pointless".
- **4.5:** should the charge window derive purely from time-to-contact (fires at a consistent *seconds-before-impact*
  for all units, instead of fixed 12-60 m bounds)? It changes when charges fire; needs its own test either way.
