# Round 112 — the enemy-side lead dial, exact watch distances, and the ui-id tag

2026-10-24 · release `20261024_airdrop_enemylead_harness112`
Installed pack md5 **`237702987893b8837d2dbb5df05d566b`** (5 files, all byte-identical to source)

---

## 1. What changed

### 1.1 `FOURTH.AIR_DROP_ENEMY_LEAD = 0.3` (the fourth dial)

```
caster_projected = caster + v_caster * AIR_DROP_CASTER_DELAY_S * AIR_DROP_CASTER_LEAD
enemy_projected  = enemy  + v_enemy  * AIR_DROP_DELAY_S       * AIR_DROP_ENEMY_LEAD
fire when |caster_projected - enemy_projected|_xz <= AIR_DROP_CENTER_M
```

It scales the **enemy's velocity term only**. `0.0` = the enemy's current position (impact straight
down on where it is now); `1.0` = the round-110/111 full 1.5 s carry; **`0.3` ships**.

Why 0.3, from the field evidence: at the zombie's 2.3 m/s the full carry was **3.45 m** — carried
*past* a hovering caster — so the projected gap bottomed at ~5 m and **grew to 10 m**, largest
exactly when the enemy was underneath. 0.3 is 0.45 s ≈ **1.0 m**: not zero (the release is not
instantaneous), not 3.45 m (a full fall time of enemy travel).

### 1.2 The two diagnostic fixes

* **`watch:` prints exact metres below 15 m.** The old 5 m band was coarser than the 6 m decision
  margin, so `~5m` covered 5.00–9.99 m. Both the projected and the instant number are `%.2f` below
  15 m; the 5 m band stays above 15 m (context only).
* **Every air-drop line carries the unit's ui id**: decision, `watch:`, skip, pre-cast re-check,
  airborne/melee hold. `FOURTH.ad_tag` prints `[?]` if the id read fails rather than dropping the
  line.
* **All four dials on every line**, exactly:
  `delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=0.50`
  (plus `moving caster: lead=0.50 of 1.50s` only when the caster's velocity is non-zero).

### 1.3 Kept exactly as they were

`AIR_DROP_DELAY_S = 1.5`, `AIR_DROP_CASTER_DELAY_S = 1.5`, `AIR_DROP_CASTER_LEAD = 0.5`,
`AIR_DROP_CENTER_M = 6`, `AIR_DROP_INHERIT = false`, `air_only` / `no_melee`, the self-centred cast,
every fail-closed read, and the pre-cast re-check — which re-projects through the **same** helper and
so reads the **same four dials**. Counts: **689 entries / 742 keys**, `air_drop_on_infantry` **12 /
19**, 46 evaluators — unchanged.

## 2. Tuning guide (one dial per test)

| Dial | Ships as | Change it when |
| --- | --- | --- |
| `AIR_DROP_DELAY_S` | **1.5 s** | still early while **both** are parked → the fall time itself is too long (shrinks both bodies) |
| `AIR_DROP_ENEMY_LEAD` | **0.3** | the **enemy walks through underneath** while the caster hovers → **0.3 → 0.0** |
| `AIR_DROP_CASTER_DELAY_S` | **1.5 s** | the caster lead factor alone cannot cure an early release while moving → **1.5 → 1.0** |
| `AIR_DROP_CASTER_LEAD` | **0.5** | the **caster chases a standing target** and fires early → **0.5 → 0.3 → 0.0** |

Fires **late when both move** → raise the lead of the body that was moving
(`AIR_DROP_CASTER_LEAD` 0.5 → 0.8 → 1.0, `AIR_DROP_ENEMY_LEAD` 0.3 → 0.6 → 1.0).

## 3. Files

| File | Note |
| --- | --- |
| `h112_section.lua` | the new harness section (worlds 0 / A–F) |
| `assemble112.py` | assembles `harness112.lua` from `harness111.lua` + the section; carries the 22 documented format/rebase supersessions |
| `harness112.lua` | the assembled suite (4492 checks) |
| `make_builder112.py` → `build_and_install112.py` | the pack builder (one format gate superseded, round-112 assertions added) |
| `reconstruct_pre112.py` | rebuilds the round-111 source byte-exactly (782,275 B / 15,799 lines) for the red control |
| `verify_installed112.py` | independent post-install check: opens the **installed** pack and compares all five files |
| `h112_run7.txt` / `h112_run8.txt` | two green runs (4492 checks), byte-identical |
| `h112_red.txt` | the red control run |
| `variants/` | one-line enemy-lead variant sources used by the worlds |

## 4. Harness 112

* **4492 checks / 0 failures**, run twice, byte-identical (`h112_run7.txt` = `h112_run8.txt`).
* Pins asserted in **both** trees, each defined exactly once: bound **6 m**, `AIR_DROP_DELAY_S`
  **1.5 s**, `AIR_DROP_ENEMY_LEAD` **0.3**, `AIR_DROP_CASTER_DELAY_S` **1.5 s**,
  `AIR_DROP_CASTER_LEAD` **0.5**, `AIR_DROP_INHERIT` **false**.
* Worlds and their arithmetic:
  * **A1** control, enemy lead 1.0, 5 m lateral crossing at 2.3 m/s → `sqrt(25 + 3.45²)` = **6.07 m**
    → **SILENT** (the reported bug reproduced); **A2** the same world at 0.3 → `sqrt(25 + 1.035²)` =
    **5.11 m** → **FIRES**.
  * **B** lead 0.0 → **5.00 m fires**, **6.50 m silent** (current position only).
  * **C** receding caster + parked enemy → 4.00 m projected / 2.00 m now, **identical at 0.3 and
    1.0**.
  * **D** both moving → **12.20 m silent** (enemy 120 → 118.2 vs caster 106), **4.20 m fires**
    (enemy 112 → 110.2).
  * **E** exact metres: **8.58 m** printed exactly (no `~`); **21.03 m** still bands to `~20m`.
  * **F** two same-type units (1003, 1004): every air-drop line carries its own `[id]`, none carries
    the other's.
* **Red control** (`H112_LIVE` / `H112_ANN` → `docs/backups/round112/pre112_*.lua`, the round-111
  build): **31 failures, all in the new section** — no enemy dial, two-dial text, 5 m bands, no ui
  id.
* **Supersession, stated plainly:** 22 assertions in the older sections were re-spelled for the new
  formats or REBASED for the new enemy arithmetic; each carries `(v112 …)` / `(REBASED v112)` in its
  label with the new number and the arithmetic in its text. No check was deleted and the check count
  is unchanged. The single decision that flips is the harness-110 E2 same-heading world (7 m → 1.40 m,
  now fires) because the caster's lead (12 m) exceeds the enemy's (3.6 m); it is pinned deliberately.

## 5. Build and install

```
source script/... 787094 bytes  sha256 ...   (5 files, all MATCHES SOURCE: True)
built pack   md5 237702987893b8837d2dbb5df05d566b
installed    md5 237702987893b8837d2dbb5df05d566b   IDENTICAL True
round-trip (re-opened the INSTALLED pack): all five files byte-identical to source
zz_probe_dist.pack left installed (md5 d4e67cfb8bc562c7d6f0ff742909c13d, untouched)
```

## 6. Retest plan

1. Arm all four Sky-junks in one click → four `AUTO sky_junk_bomb for unit 10NN: now ON` lines.
2. Park three beside a zombie lane; read **per unit id** the `watch:` line with the lowest exact
   `projected sep`. It should now bottom inside 6 m and fire.
3. Still missing just outside 6 m → change **only** `AIR_DROP_ENEMY_LEAD` (0.3 → 0.0) and retest.
4. Caster chasing and firing early → `AIR_DROP_CASTER_LEAD`. Late when both move → raise the moving
   body's lead. Early while both parked → `AIR_DROP_DELAY_S`. **One dial per test.**
