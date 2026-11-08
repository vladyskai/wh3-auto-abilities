# Inventory status vs status reason (the column-pair trap)

**The bug:** two rows (Thorsen's Thunderstorm, both keys) read `IN-WHEEL` while their own
status-reason column said `skipped (round 106: army-bar ability (army_spec junction) - out of
wheel scope)`. Two contradicting statements inside one row.

**Why the pipeline produced it** (`tools/build_abilities_master_xlsx.py`):

- `:590` computes `"IN-WHEEL" if in_wheel else "EXCLUDED"` with `in_wheel = src in IN_WHEEL_SRC`
  (`:568`), where `src` is `unit_abilities.source_type`. The documented IN-WHEEL rule names the
  army-bar family **only** as `source_type = army`, so the `army_spec` junction
  (`army_special_abilities_tables`) is never consulted. Both Thorsen keys are `source_type =
  bound` (bound spells), so they land IN-WHEEL. Outside the wheel means real army-bar buttons.
- A later round discovered the junction by hand and wrote the skip through `make_xlsx_v7.py`'s
  `SKIP_KEYS` loop (`:168-185`), which writes columns 19/20/21/22 and never writes or asserts
  column 18 - while `set_impl()` (`:144-156`) asserts `column 18 == "IN-WHEEL"` before writing.
  The asymmetry is the defect: a skip could be recorded against a status nobody re-derived.

**Rules that follow:**

- Every status/reason writer asserts BOTH columns, in both directions (an implement-writer that
  asserts its row is in-wheel needs a skip-writer that asserts its row is out of it).
- Run `tools/audit_wheel_status.py <workbook>` on every new version. G1: fails on any IN-WHEEL
  row whose own reason/implementation/trigger text names army-bar / army_spec / army-ability /
  campaign-side junction. G2: IN-WHEEL reasons must be `carrier family:…` or `skipped …`, and
  EXCLUDED rows must not name a trigger family. G3: fails if the set of `army_spec` rows still
  reading IN-WHEEL drifts from the documented baseline **in either direction** (a fresh mislabel
  fails; a silent fix that forgets the baseline also fails). Red control: v18 gave 3 failures
  (the 2 rows + one malformed reason cell), v19 gives 0.
- Do not "fix" the whole `army_spec` class in one go without a ruling: when some of those rows
  are IMPLEMENTED in the mod, moving them to EXCLUDED puts implemented abilities outside the
  wheel and implies removing them from the mod - a roster decision. State both figures instead.

**The other half of the same class - a key with no row:** `wh3_main_spell_slaanesh_slicing_shards_bound`
shipped in the mod (second key of the `slicing_shards` entry) with no inventory row at all, which
is why "741 implemented rows / 742 implemented keys" never resolved. After every round, join the
mod's key set to the workbook's key column and require **0 unmatched**:

```python
mod_keys = set(k for e in bd.mod_entries()[0] for k in e["keys"])   # 689 entries / 742 keys
sheet = set(k.strip() for r in rows for k in str(r[2]).split(";") if k.strip())
assert not (mod_keys - sheet)          # implemented keys with no row
assert not (impl_keys - mod_keys)      # rows marked IMPLEMENTED whose key is not in the mod
```

**Numbers-block rule:** a per-carrier-family block must be counted in the SAME unit as the
headline it sits under. v18's block was an older key-level count (1,143 keys / 638 implemented)
under a row-level headline (1,141 rows / 742 implemented) and could not tie; a footnote saying so
still left two numbers that look comparable. Re-derive it from the workbook's own rows joined by
exact key to `unit_abilities.source_type` and assert the column sums equal the headline cells.
