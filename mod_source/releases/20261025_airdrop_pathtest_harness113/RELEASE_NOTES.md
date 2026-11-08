# Round 113 — the path test, the derived frontage and the single-entity exclusion

2026-10-25 · release `20261025_airdrop_pathtest_harness113`
Installed pack md5 **`004a1293c35f29a2b863fd399d733cf6`** (5 files, all byte-identical to source)

---

## 1. What changed

### 1.1 The test is the enemy's PATH, not its point

```
segment   = (enemy_x, enemy_z) -> (enemy_projected_x, enemy_projected_z)
perp      = shortest horizontal distance from the SEGMENT to the caster's projected point
            (point-to-segment on x/z; the parameter is clamped to 0..1)
threshold = AIR_DROP_CENTER_M + ad_frontage(enemy)
FIRE  iff  perp <= threshold
```

Why: `battle_unit:position()` is the **centre of the main squad**. A 20-model block ten models wide
in two ranks has ~10 m of frontage, so its centre can stay 10 m away while a model of it passes under
the flyer — exactly the reported side pass. The round-110/112 test compared the caster's projected
point with the enemy's projected **centre**, so that pass never came inside 6 m.

### 1.2 The frontage credit is derived (`FOURTH.ad_frontage`)

| Source | Rule |
| --- | --- |
| `ordered` | `ordered_width() / 2` |
| `models` | `ceil(men / AIR_DROP_RANKS) * AIR_DROP_MODEL_RADIUS_M`, clamped to 1..12 m |
| `clamped` | a value pulled into `AIR_DROP_FRONTAGE_MIN_M .. _MAX_M` |
| `single` | `men < 2` → **0** (a point has no width; the 6 m base covers its footprint) |
| `unreadable` | **0**, fail-closed (the plain 6 m point distance decides) |

New constants, each defined once and pinned in both the live and the annotated copy:

```lua
FOURTH.AIR_DROP_MODEL_RADIUS_M = 0.6   -- modal battle_entities.radius over the 942 infantry rows (median 0.7)
FOURTH.AIR_DROP_RANKS          = 2     -- the documented TWO-RANK formation assumption
FOURTH.AIR_DROP_FRONTAGE_MIN_M = 1     -- half-width floor
FOURTH.AIR_DROP_FRONTAGE_MAX_M = 12    -- half-width ceiling (12 m half + 6 m base = 18 m)
```

The radius is a constant because battle Lua documents **no** radius/footprint/bbox/size read and has
**no db access** — `land_units.man_entity -> battle_entities.radius` cannot be joined at battle time.

### 1.3 The single-entity exclusion

`initial_number_of_men() == 1` (exact equality) → skip, logged **once per episode** as
`single entity (1 model)`. **Initial**, not current, so a depleted 20-model block is still a block.
The 1,409-key commander set is **not** consulted here: every infantry-class lord/hero in the data is a
one-model unit, and every multi-model character row (chariot crews, 2–8 men) is class `com`, i.e. not
infantry, so the infantry filter has already removed them.

### 1.4 Kept exactly as they were

`AIR_DROP_DELAY_S = 1.5`, `AIR_DROP_ENEMY_LEAD = 0.3`, `AIR_DROP_CASTER_DELAY_S = 1.5`,
`AIR_DROP_CASTER_LEAD = 0.5`, `AIR_DROP_CENTER_M = 6`, `AIR_DROP_INHERIT = false`, `air_only` /
`no_melee`, the self-centred cast, every fail-closed read, and the pre-cast re-check — which now
**re-runs the segment test** on fresh reads. Counts: **689 entries / 742 keys**, `air_drop_on_infantry`
**12 / 19**, 46 evaluators — unchanged.

## 2. The log

Decision line: `segment=…->…`, `perp=9.02m`, `frontage=6.00m (models, men=20 x 2 ranks (10 per rank)
x 0.60m radius)`, `threshold=12.00m (bound=6m + frontage=6.00m)`, then the old point separation as a
diagnostic (`centre=9.0m (the PROJECTED POINT separation - no longer the test)`), plus the four dials
and the ui id as before. The `watch:` line prints perp vs threshold **and** the point separation; the
skip line is `SKIPPED: single entity (1 model)`; the re-check line prints the fresh perp and threshold.

## 3. Files

| File | Note |
| --- | --- |
| `round113_edit.py` | the whole source edit, applied to BOTH copies (asserted occurrence counts) |
| `h113_section.lua` | the new harness section (section 0 + worlds A1/A2/A3, B, C, D1-D3, E1/E2, F, G) |
| `assemble113.py` → `harness113.lua` | assembles the suite; the mock gains `ordered_width()` / `initial_number_of_men()`; carries the 20 documented supersessions |
| `make_builder113.py` → `build_and_install113.py` | the pack builder (9 gates superseded, round-113 block added) |
| `verify_installed113.py` | independent post-install check: opens the **installed** pack, compares all five files |
| `run2.txt` / `run3.txt` | two green runs (4610 checks), byte-identical |
| `red.txt` | the red control (round-112 build): 55 failures, all in the new section |

## 4. Harness 113

* **4610 checks / 0 failures**, twice, byte-identical.
* Pins in both trees: bound **6**, delay **1.5**, enemy lead **0.3**, caster **1.5 / 0.5**, inherit
  **false**, radius **0.6**, ranks **2**, frontage **1 / 12**.
* Worlds: A1 fires at 10.05 m centre / 9.02 m perp (the reported bug); A2 the same geometry with one
  alive model is silent (proves the credit); A3 the path crossing the point with the projected point
  8.99 m away fires; B the one-model lord is silent with exactly one skip line; C 15 m stays silent;
  D1/D2/D3 `ordered` vs `models` vs `clamped` at perp 12.20; E1 `models` after `ordered_width` raises,
  E2 both reads gone → frontage 0.00 / threshold 6.00; F a 20 m drift re-checked at perp 28.98 →
  SKIPPED; G 1 alive of 20 initial → not skipped, fires at 5 m.
* **Red control**: 55 failures, every one in the new section, none before it.
* **Supersessions** (documented in `assemble113.py`, nothing deleted, count unchanged): the point gate
  → perp gate, `radius=none` → per-model constant + frontage, `ad_project` → `ad_lead` + segment,
  `best_gap` → `best_pgap` on the printed centre, the watch bracket, the ui-id count 5 → 6, and three
  **REBASED** worlds whose outcome legitimately changes (112-A1, 110-C2 and the 110 static gates).

## 5. Build and install

```
source script/... 805,881 bytes  md5 8666d7dfee60799fd596f002b1903e97
five files        all MATCHES SOURCE: True
built pack        md5 004a1293c35f29a2b863fd399d733cf6
installed         md5 004a1293c35f29a2b863fd399d733cf6   IDENTICAL True
round-trip (re-opened the INSTALLED pack): all five files byte-identical
zz_probe_dist.pack left installed (md5 d4e67cfb8bc562c7d6f0ff742909c13d, untouched)
```

## 6. Retest plan

1. Arm a Sky-junk, hover it beside a **20-model zombie block** walking past 5–10 m to the side.
2. Watch `perp` against `threshold` on the `watch:`/`target:` line: the perp should fall inside
   `6 m + frontage` while the old `centre=` number stays outside 6 m — and it should fire.
3. Still missing while models pass under: `AIR_DROP_MODEL_RADIUS_M` 0.6 → 0.7 → 0.8, or
   `AIR_DROP_FRONTAGE_MAX_M` 12 → 15. **One constant per test.**
4. Firing while clearly not underneath: `AIR_DROP_FRONTAGE_MAX_M` 12 → 8 → 6 (0 restores the pure
   6 m point test), then `AIR_DROP_CENTER_M`.
5. Walk a **lord** past: no drop, one `skipped: single entity (1 model)` line.
6. Wrong PLACE (ahead/behind): tune `AIR_DROP_ENEMY_LEAD` / `AIR_DROP_DELAY_S` — they define the
   segment; the path test adds no dial.
