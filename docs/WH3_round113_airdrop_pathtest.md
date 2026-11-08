# Round 113 — the air-drop path test, the derived frontage and the single-entity exclusion

2026-10-25 · release `20261025_airdrop_pathtest_harness113`
Installed pack md5 **`004a1293c35f29a2b863fd399d733cf6`** (5 files, all byte-identical to source)

---

## 1. The two field findings

| # | Report | What was actually happening |
| --- | --- | --- |
| A | A Sky-junk hovering **beside** a 20-model zombie block never fired while the block walked past (screenshot) | `battle_unit:position()` is the **centre of the main squad**. A 20-model block ten models wide in two ranks has ~10 m of frontage, so its **centre** can stay 10 m away while a **model** of it passes under the flyer. The old rule compared the caster's projected **point** with the enemy's projected **centre** — 9–10 m, never inside 6 m — so the release test was never satisfied. |
| B | One drop fired at a **LORD** | The candidate filter was `alive + is_infantry()` only; an infantry-class lord is a perfectly legal infantry candidate and its centre passed the 6 m test. |

## 2. The rule now (one line of arithmetic)

```
segment   = (enemy_x, enemy_z) -> (enemy_projected_x, enemy_projected_z)
enemy_projected  = enemy  + v_enemy  * AIR_DROP_DELAY_S        * AIR_DROP_ENEMY_LEAD     (1.5 s * 0.3)
caster_projected = caster + v_caster * AIR_DROP_CASTER_DELAY_S * AIR_DROP_CASTER_LEAD    (1.5 s * 0.5)
perp      = shortest horizontal distance from the SEGMENT to caster_projected
            (point-to-segment on x/z, parameter clamped to 0..1)
threshold = AIR_DROP_CENTER_M + ad_frontage(enemy)                                       (6 m + half-frontage)
FIRE  iff  perp <= threshold
```

Nothing else about the ability changed: `air_only` / `no_melee` per row, the self-centred cast on the
owner, every fail-closed read, and the pre-cast re-check — which now **re-runs the segment test** on
fresh reads (one `ad_lead` call yields the current *and* the projected point, so the read sequence a
drift world depends on is unchanged).

## 3. The frontage derivation (`FOURTH.ad_frontage`)

| Source | Rule | When |
| --- | --- | --- |
| `ordered` | `half = ordered_width() / 2` | the engine answers a sane positive number ("the width of the position to which the unit has been ordered in metres") |
| `models` | `per_rank = ceil(men / 2)` ; `half = per_rank * radius` | otherwise — the documented **two-rank** assumption; `men` is the alive count the picker already read (no extra engine read) |
| `clamped` | `1 m <= half <= 12 m` | a value outside the range is pulled in; the source says so |
| `single` | `half = 0` | `men < 2`: a point has no width, and the 6 m base already covers its footprint |
| `unreadable` | `half = 0` | neither read answers — **fail closed**: the plain 6 m point distance decides |

### 3.1 Why the radius is a constant

`battle_unit.lua` documents **no** radius / footprint / bounding box / size read, and battle Lua has
**no db access**, so `land_units.man_entity -> battle_entities.radius` cannot be joined at battle
time. `FOURTH.AIR_DROP_MODEL_RADIUS_M = 0.6 m` is taken from the extracted tables:

| Measure | Value |
| --- | --- |
| `battle_entities.radius` over the **942** infantry `land_units` rows | min 0.5 · **mode 0.6 (168 rows)** · median **0.7** · p90 3.9 · max 14.0 |
| Zombies (`wh_main_vmp_inf_zombie`) | 0.5 |
| Terradon rider (`wh2_main_lzd_cav_terradon_riders_0`) | 0.6 |

0.6 ships because it is the **modal** value and is **conservative** against the median.

### 3.2 Why two ranks

`land_units.rank_depth` over the same 942 rows: **1** (245 rows), 3 (150), 5 (143), 6 (133), 4 (125),
8 (68). Two ranks is the **wide end** of the game's own formations, and a wider frontage is the safe
direction for a drop whose failure mode is *missing* a block that sweeps underneath.

### 3.3 Worked example (the reported geometry, harness world A1)

20-model block, centre 10.05 m to the side, walking 2.3 m/s:

```
perp      = 9.02 m              (distance from its path to the caster's projected point)
frontage  = 6.00 m              (models: ceil(20/2)=10 per rank x 0.60 m)
threshold = 12.00 m             (6 m base + 6.00 m credit)
=> FIRES.   The old point test read 9.02 m against 6 m and stayed silent.
```

## 4. The single-entity exclusion

```lua
local ok_im, im = pcall(function() return enemy:initial_number_of_men() end)
if not ok_im or type(im) ~= "number" then  -- unreadable -> SKIP (fail-closed)
elseif im == 1 then                        -- EXACT equality
    -- SKIPPED: single entity (1 model)  (once per episode)
end
```

* **Exact equality 1**, never "1 or less" — a unit with zero models does not exist (the user's point).
* **Initial**, not current: a 20-model block ground down to one survivor is still a block (world G).
* **The 1,409-key commander set is deliberately not consulted here.** It remains in service for the
  other evaluators; this one does not need it (see §5).

## 5. Does a mounted lord count 1 or 2 models?

From `main_units` (the `num_men` column is the size the unit spawns with, which is what
`initial_number_of_men()` reports):

| Mounted lords (504 rows) | `num_men` | `land_units` class |
| --- | --- | --- |
| 432 | **1** | `com` (horse, steed, monster, flying mount, casket, …) |
| 50 | **2** | `com` — **all chariots** (`wh2_dlc09_tmb_cha_khalida_2` / general chariot, `wh2_dlc15_hef_cha_alastair_1` / white-lion chariot, …) |
| 22 | 3–8, 17, 25 | `com` — heavy chariots and multi-crew mounts |

So: **a single-mount lord reads 1 model; a chariot-mounted lord reads 2 (or more) crew.** That does
not weaken the guard, because the candidate set is filtered to **infantry** first:

* **0** lord rows and **6** hero rows have an infantry-class `land_unit` (`inf_mel` / `inf_mis` /
  `inf_spr`) — and **all** of them have `num_men = 1`.
* **All 146** character rows with `num_men >= 2` are class **`com`**, i.e. not infantry, so they were
  already outside the candidate set before this guard runs.

The user's reasoning therefore holds exactly: the model count covers the infantry lord/hero case, and
the commander key set is unnecessary here.

## 6. The log format

Decision line (one per decision, all four dials, ui-id prefix):

```
  [1003] sky_junk_bomb target: 'wh2_dlc13_emp_inf_spearmen_ror_0' is UNDER the caster (PROJECTED 1.50s AHEAD
  momentum=none caster=(100.0, 200.0) v=(0.0, 0.0) 0.0 m/s src=stationary proj=(100.0, 200.0)
  from delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=0.50
  enemy=(110.0, 201.0) v=(-2.3, 0.0) 2.3 m/s src=ordered proj=(109.0, 201.0)
  segment=(110.0, 201.0)->(109.0, 201.0) perp=9.02m
  frontage=6.00m (models, men=20 x 2 ranks (10 per rank) x 0.60m radius)
  threshold=12.00m (bound=6m + frontage=6.00m)
  centre=9.0m (the PROJECTED POINT separation - no longer the test) now=10.0m now_dxz=10.0m
  bound=6m edge=-1.0m per_model_radius=0.60m (a CONSTANT - no battle_unit read exposes a radius) air_only=true)
```

Why-not line (nearest candidate by **perp**, exact metres below 15 m):

```
  [1003] sky_junk_bomb watch: nearest INFANTRY 'wh2_dlc13_emp_inf_spearmen_ror_0' is centre=~15m vs bound=6m
  -> NOT under the caster [perp=~15m vs threshold=12.00m (bound=6m + frontage=6.00m (models, ...))
  segment=(115.0, 200.0)->(115.0, 201.0) projected sep=15.04m after delay=1.50s; caster v=... (dials); enemy v=...]
```

Skip line (once per episode):

```
  [1004] sky_junk_bomb SKIPPED: single entity (1 model) - 'wh2_dlc13_emp_inf_spearmen_ror_0' has
  initial_number_of_men() = 1 (a Lord / Hero / character is ONE model: the 1,409-key commander set is
  deliberately NOT consulted in this evaluator - the model count covers it) - a one-model unit cannot
  justify a drop [delay=1.50s bound=6m air_only=true]
```

Pre-cast re-check line (fresh reads, same helpers): adds `perp=…m vs threshold=…m (bound=6m + frontage=…)`
and `segment=…->…`.

## 7. Harness 113

* **4610 checks / 0 failures**, run twice, byte-identical (`run2.txt` = `run3.txt`).
* **Section-0 pins in BOTH files**: the six older constants, the four new ones (`0.6`, `2`, `1`, `12`),
  the helper branches (`ordered` / `models` / `clamped` / `single` / `unreadable`), the clamped
  point-to-segment parameter, the `perp <= eff` gate, the exact-equality guard, the "commander set not
  consulted" comment, the re-check's segment test, the documented derivation, the 12/19 family counts.
* Worlds (each run against **both** the live and the annotated copy):

| World | Geometry | Expected |
| --- | --- | --- |
| A1 | 20-model block, centre **10.05 m** away, perp **9.02 m** | **FIRES** at threshold 12.00 (the reported bug) |
| A2 | same geometry, **1 alive** model | **SILENT** (credit 0, threshold 6.00) — proves A1 was the credit |
| A3 | enemy 1 m from the point, running away 22.2 m/s: perp **0.00 m**, projected point **8.99 m** away | **FIRES** (the path alone) |
| B | one-model lord, 5 m pass | **SILENT**, exactly **one** `single entity (1 model)` line over 3 polls |
| C | 20 models, 15 m to the side, perp **15.00 m** | **SILENT** (12.00 m threshold) |
| D1 | `ordered_width` 24 → half 12.00 (`ordered`) | **FIRES** at perp 12.20 |
| D2 | same geometry, no width → half 6.00 (`models`) | **SILENT** (12.20 > 12.00) |
| D3 | `ordered_width` 60 → clamped to 12.00 | **FIRES**, log says `clamped` |
| E1 | `ordered_width()` raises → `models` | **FIRES** |
| E2 | both reads gone at the re-check → `unreadable` | frontage 0.00, threshold 6.00, cast not spent |
| F | picked at perp 9.02, block drifts to 30 m → perp **28.98 m** | **SKIPPED**, cast not spent |
| G | 1 alive of **20 initial** | **NOT** skipped, **FIRES** at 5.00 m, no skip line |

* **Red control** (`H113_LIVE` / `H113_ANN` → `docs/backups/round113/pre113_*.lua`, the round-112
  build): **55 failures, every one in the new section** (0 failures before it).
* **Supersessions**, all documented in `assemble113.py` (20 fragments, no check deleted, count
  unchanged): the point gate → the perp gate, `radius=none` → the per-model constant + frontage,
  the re-check's `ad_project` → one `ad_lead` + segment test, `best_gap` → `best_pgap` on the printed
  centre, the watch line's bracket, the ui-id count 5 → 6, and **three REBASED worlds** whose outcome
  legitimately changes under the user's rule:
  * harness-112 **A1** (5 m lateral pass, lead 1.0): projected centre 6.07 m — outside the bound — but
    the path passes **5.00 m** from the point, so it now **fires** (that is the fix);
  * harness-110 **C2** (a receding 20-model-equivalent at 5 m): the path *starts* inside the bound, so
    it now fires — the round-109 answer restored for an enemy that is inside 6 m **right now**;
  * harness-110's picker/re-check static gates, re-spelled for the new quantities.

## 8. Build and install

```
source script/...            805,881 bytes  sha256 …
five files                   all MATCHES SOURCE: True
built pack                   md5 004a1293c35f29a2b863fd399d733cf6
installed                    md5 004a1293c35f29a2b863fd399d733cf6   IDENTICAL True
round-trip (re-opened the INSTALLED pack): all five files byte-identical to source
zz_probe_dist.pack left installed (md5 d4e67cfb8bc562c7d6f0ff742909c13d, untouched)
```

## 9. Retest plan

1. Arm one Sky-junk (`AUTO sky_junk_bomb for unit … now ON`), hover it with a **20-model zombie block
   walking past 5–10 m to the side**.
2. Read its `watch:`/`target:` line. The pass should now show `perp` falling **below** the
   `threshold` (`6 m + frontage`) while `centre=` (the old number) stays well outside 6 m — and it
   should **fire**.
3. If the block's models visibly pass under the flyer and it still does not fire, the credit is
   under-stated: `AIR_DROP_MODEL_RADIUS_M` 0.6 → 0.7 → 0.8, or `AIR_DROP_FRONTAGE_MAX_M` 12 → 15.
   **One constant per test.**
4. If it now drops while the enemy is clearly **not** underneath: `AIR_DROP_FRONTAGE_MAX_M`
   12 → 8 → 6 (a 0 ceiling restores the pure 6 m point test), then `AIR_DROP_CENTER_M`.
5. Send a **lord** (with his unit) past the flyer: expect **no** drop and **one**
   `SKIPPED: single entity (1 model)` line for the pass.
6. If any drop is judged in the wrong **place** (ahead of / behind the block), tune the **leads**
   (`AIR_DROP_ENEMY_LEAD` 0.3 → 0.0, `AIR_DROP_DELAY_S`) — they define the segment's end; the path
   test adds no dial of its own.
