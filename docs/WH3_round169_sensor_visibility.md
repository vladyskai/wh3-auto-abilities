# Round 169: every enemy read skips hidden enemies

Date: 2026-11-17. Harness: `harness168.lua`. Release folder: `mod_source\releases\20261117_sensor_visibility_harness168\`.

## 1. The ruling

User, 2026-11-17, on the air drop and the Farsight / Mist reads still seeing hidden enemies: "Yes, those too; I don't
see the reason you kept them different."

## 2. The change

The visibility test (`FOURTH.enemy_not_hidden`, round 168) now also runs in the three enemy reads that pick no target:

| Read | Used by | Effect |
|---|---|---|
| `FOURTH.ad_nearest` | the air drops (Death From Above, Sky-junk Bomb, ...) | a hidden enemy underfoot no longer triggers the drop |
| `FOURTH.nearest_enemy_gap` | Potion of Farsight, the Mist ground cast | a hidden enemy neither counts as "in range" nor as "just beyond" |
| `FOURTH.engagement_set` | the "unless fighting only Lords or Heroes" rule | a hidden enemy in contact is not counted |

The map probe's log rows still read every unit: they report, they decide nothing. Every decision the mod makes now
ignores an enemy the game reads as not visible to us. An unreadable read still passes.

## 3. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| FULL, run 1 | 7,105 | 0 | `h168_run1.txt` |
| FULL, run 2 | 7,105 | 0, byte-identical | `h168_run2.txt` |
| RED, pre-169 snapshot | 7,103 | 0; RED 10/10 | `h168_red.txt` |

**Section 168 (both files):**
- **FV1:** Farsight with a hidden enemy in range and a visible one just beyond: one cast. RED: none, because the hidden
  enemy blocked it.
- **FV2:** the only enemy just beyond range is hidden: no cast. RED: one cast.
- **FV3:** the same enemy visible: one cast.
- **AH1:** an air drop over a hidden enemy: no cast. RED: one cast.
- **AH2:** the same enemy visible: one cast.

No pin needed a rebase.

## 4. Build and install

- **`build_and_install169.py`:** ROUND 123 to 169 gates OK; `MATCHES SOURCE: True` for all four files.
- **Installed pack:** md5 **`c12c1eb107d4372b7fb343b1d61360a1`**, 1,414,973 bytes.
- **Archived:**
  - `archive\packs\zz_test_deadly_onslaught_20261117_round169.pack`;
  - `archive\mod_source\round169\`.

## 5. Not done

- **No workbook version:** no roster, card or trigger text changed. The workbook stays v52.
- **Not seen in game.**
