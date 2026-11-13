# Round 145: the battlefield map probe (read-only)

Date: 2026-11-13. Harness: `harness144.lua`. Release folder: `mod_source\releases\20261113_map_probe_harness144\`.

## 1. The request

The user (2026-11-13): "see if we are able to have an internal map of the units in the game by reading every units
coordinates, their entity numbers and size. Value of the units would also be useful. That map could help us decide
better activation patterns ... Especially to detect blobs of infantry." After the feasibility answer: "Yes, build the
probe".

## 2. What the engine offers (the battle API list, `archive\research\wh3\battle_unit.lua`)

| Wanted | Read | Before this round |
|---|---|---|
| Coordinates | `position()` (centre, X/Z), `position_of_officer()` | position proven; officer never logged |
| Facing | `bearing()` | proven (air drop) |
| Frontage | `ordered_width()` (the ORDERED formation's width, metres) | proven on our units (1.1-29.4 m); never on enemies |
| Soldiers | `number_of_men_alive()`, `initial_number_of_men()` | proven |
| Health | `unary_hitpoints()` | proven |
| Value | `strategic_value()` ("arbitrary indicator of current strength") | never read |
| Visible to us | `is_visible_to_alliance(bm:get_player_alliance())` | never read |
| Depth | none | estimated offline from width, soldiers and the spacing table |

## 3. The change (what you will see)

- **Nothing changes in battle.** No trigger moved, no entry added, nothing is cast by the probe.
- **The log gains a map every 2 s of battle:** one `MAP` row per unit (`side=P` ours, `side=E` the main enemy army)
  and one `MAP_END` line. A row looks like:
  `MAP t=2.0 side=E id=15805 type=wh_main_grn_inf_orc_boyz x=40.0 z=32.0 ox=? oz=? bearing=? width=30.2
  men=1/120 hp=? sv=? inf=? class=inf_mel vis=? melee=1 moving=0 fly=? routing=0` (from the harness mock; `?` means
  the read did not answer).
- **Cost of the probe:**
  - about 40 rows of about 260 bytes every 2 s, so roughly 6 MB for a 20-minute battle;
  - for our units it never repeats the type and routing reads the poll loop already does (routing prints `-`; the
    type is read at most once per unit per battle, reusing the identity watch's cache);
  - it runs at the very end of the poll, through `pcall`, so an error in it can never cost a tick.
- **Known limits:** only the MAIN enemy army (reinforcements are not listed); allied AI armies are not listed; the
  reading copy (log-free by rule) keeps the rows in `FOURTH.map_last` instead.

## 4. New tools

- **`tools\extract_spacing_table.py`** extracted the game's `unit_spacings_tables` (165 rows) into
  `gamedata\wh3\unit_spacings.tsv`, in the extractor's own TSV form, so later re-extracts refresh it. Check: Swordsmen at
  the probe's 29.4 m frontage with 1.48 m spacing make 20 files, so 120 men stand 6 ranks deep, which is the
  game's own `rank_depth = 6`.
- **`tools\analyze_map_log.py`** reads the MAP rows from a byte offset (never the whole log) and reports:
  1. readability per side (do the reads work on enemies?);
  2. `strategic_value()` next to the multiplayer cost;
  3. estimated footprints;
  4. the best blob each snapshot for 10, 15 and 20 m circles: enemy infantry soldiers inside, the units involved, and
     our soldiers within R + 5 m (friendly-fire risk). Hidden enemies (`vis=0`) are left out.
  Self-test: two overlapping orc blocks give 182 soldiers in a 15 m circle centred between them, the hidden third block
  is ignored, and our nearby Swordsmen are counted as at risk.
  **Assumption to check in the field:** bearing b faces (sin b, cos b) on the ground plane.

## 5. The proof

| Run | Checks | Failures | File |
|---|---:|---:|---|
| harness143 on the first probe draft | - | 14: the read-discipline worlds (type and routing read counts) | (not kept) |
| harness143 on the revised probe | - | 4: I1b / I3b, exactly +1 type() read | (not kept) |
| FULL, run 1 | 6,292 | 0 | `h144_run1.txt` |
| FULL, run 2 | 6,292 | 0, byte-identical | `h144_run2.txt` |
| LIGHT | 3,111 | 0 | `h144_light.txt` |
| RED, pre-145 snapshot (light) | 3,097 | 0; M1 logs no MAP row | `h144_red.txt` |

Section 144:
- **M1:** two of ours and two enemies for 24 polls. The snapshots are 2 s apart, each with 2 rows per side and a
  `MAP_END own=2 enemy=2`; the rows carry the coordinates, width and melee flag; our rows print `routing=-`;
  nothing is cast; no poll error.
- **M2:** an enemy whose width and position reads raise prints `width=?` and `x=? z=?`, and the poll goes on.
- **M3:** the same world on the pre-145 snapshot is the baseline: the probe adds at most one type() read (4 against 3).
- **0zq:** the block between the map code and the evaluator table contains no cast call and no trigger state.

## 6. Pins rebased

| Pin | Old | New | Why |
|---|---|---|---|
| I1b (harness 77 identity world) | floor(T/16) type() reads | floor(T/16) + 1 | the probe's one type() read of an own unit per battle |
| I3b | 15 attempts | 16 | same |

The first draft also read our units' routing and type every 2 s, which broke the H1/H2 re-list worlds. The draft was
changed instead of the pins: those worlds prove the poll loop reads each unit once per tick.

## 7. Build and install

- **`build_and_install145.py`:** ROUND 123 to 145 gates OK (the new gate: the probe is read-only and pcall'd once per
  poll); `MATCHES SOURCE: True` for all five files.
- **Installed pack:** md5 **`b6b93c07ee9e4d806ff21d7d4ca9ba75`**, 1,419,432 bytes, `IDENTICAL True`.
- Archived: `archive\packs\zz_test_deadly_onslaught_20261113_round145.pack`; `archive\mod_source\round145\` (source md5
  `7afbea406640ab0643c48adecf293a8b`, annotated md5 `10139764f3adc43a38b62714a3f6bd8e`).

## 8. Not done, and why

- **No workbook version, tracker or database change:** the roster did not change (722 entries / 777 keys / 73
  families). The full suite still ran.
- **Not tested in the game.** The next battle starts at log byte **501,336,775**. After it:
  `uv run python tools/analyze_map_log.py "<game folder>\zz_test_deadly_onslaught_log.txt" --from 501336775 --out docs\WH3_map_probe_battle1.md`.
- **No trigger uses the map yet.** That waits for the field result and the user's design, one ability at a time.
