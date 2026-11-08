# WH3_mod — relocation notes (2026-10-16)

Everything the WH3 auto-ability project owned used to live in five places on the Desktop.
It now lives under one root. This file records the old → new mapping, what was repaired,
what was deliberately **left byte-identical**, and the evidence that the toolchain still
works from the new home.

## 1. New layout

```
C:\Users\vlady\Desktop\WH3_mod\
├─ mod_source\     the mod source tree (script/battle/mod, ui/, dist/, releases/)   483 files
├─ tools\          RPFM server + build/verify/smoke scripts, mocks, harness runners  371 files
├─ docs\           the tracker, every report/research doc, the annotated reading copy 36 files
│   ├─ backups\    the tracker's pre-round snapshots (WH3_ability_tracker.md.bak_*)     7 files
│   └─ helpers\    the Desktop _*.py / _*.json analysis helpers                         9 files
├─ audit\          the audit slices (WH3_audit: slice_*.md, _slice*.json, extractors)  35 files
├─ viewer\         WH3_abilities_viewer.html + the three smaller HTML artifacts          4 files
└─ archive\        the 466 MB game-independence snapshot (structure kept intact)      8971 files
```

## 2. Old → new mapping (every path that changed)

| Was | Is now |
|---|---|
| `Desktop\wh3_auto_ability_test\` | `Desktop\WH3_mod\mod_source\` |
| `Desktop\rpfm_tools\` | `Desktop\WH3_mod\tools\` |
| `Desktop\WH3_audit\` | `Desktop\WH3_mod\audit\` |
| `Desktop\WH3_project_archive\` | `Desktop\WH3_mod\archive\` |
| `Desktop\WH3_abilities_viewer.html` (+ the 3 other HTML artifacts) | `Desktop\WH3_mod\viewer\` |
| `Desktop\WH3_*.md` (tracker, reports, research) | `Desktop\WH3_mod\docs\` |
| `Desktop\WH3_auto_ability_annotated.lua` | `Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua` |
| `Desktop\WH3_ability_tracker.md.bak_*` | `Desktop\WH3_mod\docs\backups\` |
| `Desktop\_*.py` / `Desktop\_*.json` | `Desktop\WH3_mod\docs\helpers\` |

Bare/relative forms (`wh3_auto_ability_test\…`, `rpfm_tools/rpfm/…`, `…/wh3_auto_ability_test/…`)
were remapped to `WH3_mod/mod_source\…` / `WH3_mod/tools/…` in the same pass.

## 3. Paths repaired

**198 files were rewritten** (byte-level, so no newline or encoding was ever altered):

| Area | Files | References replaced |
|---|---:|---:|
| `mod_source\` (per-round builders, harness .lua files, make/verify scripts) | 116 | 287 |
| `tools\` (build_and_install.py, probes, mocks, smoke/verify scripts) | 46 | 70 |
| `docs\` (the tracker + research docs) | 12 | 17 |
| `audit\` (the extractors + slice docs) | 11 | 16 |
| the tracker's 7 `.bak_*` snapshots and the 6 `build_and_install.py.bak_*` backups | 13 | — |

The **`H<NN>_LIVE` / `H<NN>_ANN` env-var defaults** inside every relocated harness were
repaired with the rest (the harnesses now default to
`WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua` and
`WH3_mod/docs/WH3_auto_ability_annotated.lua`). The skill
`software-development/wh3-battle-mod-iteration` was updated to the new project root.

### Deliberately NOT rewritten (and why)

* **`archive\` (all 8,971 files)** — it is a checksum-sealed snapshot: `archive\checksums.sha256`
  covers every file, so rewriting a path inside it would falsify the archive's own integrity
  manifest. It is verified intact after the move (see §5).
* **`*.txt` run logs (76 files, e.g. `tools\build_out*.txt`, `mod_source\releases\**\*_out.txt`,
  `h*_green.txt` / `h*_red.txt`)** — these are historical records of what a past run printed.
  Rewriting a path inside a log would misrepresent where that run happened. They are inert
  (no tool reads a path out of them).
* **`__pycache__\*.pyc` (4 files)** — regenerable bytecode caches.

## 4. The game install was not touched

`…\Total War WARHAMMER III\data\` still carries both packs (the main pack was only rebuilt
and re-installed by the verification build, the passive observer probe was left alone):

| Pack | Before the move | After the move |
|---|---|---|
| `zz_test_deadly_onslaught.pack` | `a7313d327f6ee57ebb73b30e048506a0` | `4bd68993f7e12fc4523d6bb83167f2f2` (rebuilt by the verification build; RPFM stamps the save time into the header, so the pack md5 is an IDENTIFIER, not a reproducibility target — content is proven by the per-file sha256 gates) |
| `zz_probe_dist.pack` | `d4e67cfb8bc562c7d6f0ff742909c13d` | `d4e67cfb8bc562c7d6f0ff742909c13d` (untouched, still installed) |

**The mod's bytes did not change in the move:** the shipped script is
`cac6cb443a846994538bec99706047a6` before and after (546,751 bytes, LF only, zero CR), and
`mod_source/dist/zz_test_deadly_onslaught.pack` matched it byte-for-byte at move time.

## 5. Evidence the toolchain works from the new home

1. **RPFM server** started from `WH3_mod\tools\rpfm\rpfm_server.exe` — `Listening on 127.0.0.1:45127`.
2. **One real build + install** from `WH3_mod\mod_source\releases\20261015_classgated_harness99\build_and_install99.py`
   (the current-generation builder): every per-file gate printed `MATCHES SOURCE: True`
   (script 546,751 bytes; tooltip 331,235; badge template 2,864; two PNGs),
   `main mod untouched (byte-identical): True`, `installed md5 4bd68993f7e12fc4523d6bb83167f2f2`,
   `IDENTICAL True`.
3. **The relocated harness suite runs green**: `harness99.lua` → `checks: 3365, failures: 0`,
   `HARNESS OK - all checks passed` — proving the repaired `H99_LIVE` / `H99_ANN` defaults resolve.
4. **Archive integrity**: `sha256sum -c archive\checksums.sha256` → 8,966 of 8,967 entries verify.
   The single failure (`mod_source/tools/build_and_install.py`) is **pre-existing**: that file's
   mtime (2026-10-04 19:18) is later than the manifest's creation (18:21), and it still contains
   the OLD path — i.e. it was never rewritten by this move.

## 6. Known staleness found while verifying (pre-existing, NOT caused by the move)

* **`tools\build_and_install.py` is a generation-92 builder** and no longer validates the
  generation-99 mod: 13 content gates are stale (the tooltip hint sentence, the now-renamed
  range constants, the moved `melee_unwavering` / `ushoran_health` / `melee_health75` trigger
  counts). Its **path-dependent steps all pass** (it reads the sources from the new location,
  builds the pack and prints every `MATCHES SOURCE: True`) — only the content gates fail, and
  they failed before the move too. The current-generation builder for each round lives in that
  round's release folder (`mod_source\releases\<round>\build_and_install<NN>.py`).
* **Tracker/mod inconsistency**: `wh3_main_prisoners_butcher` (Meat Feast) is implemented in the
  mod (`trigger = ushoran_health`) while its tracker row still reads `skipped (army-bar ability)`.
  Recorded — not silently corrected — in the database's §1.6.

## 7. Where the new master reference lives

`docs\WH3_ability_database_master.md` — the definitive database of all 1,797 abilities
(every EFFECT, RESTRICTION flag name, RANGE value and the 70% trigger bound, STATUS and
plain-English trigger/logic). Regenerate it any time with:

```
cd C:\Users\vlady\Desktop\WH3_mod\tools
uv run --quiet python build_ability_database.py
```
