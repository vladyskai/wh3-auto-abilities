# Retired probe sources — 2026-10-04

These two throwaway experiment probes were **REMOVED from the shipped pack** on
2026-10-04 (housekeeping round). They are preserved here, byte-identical to the
sources that shipped inside the packs up to and including the last pre-clean
build (pack md5 `d9f55f808e3661d160ee4bda7246583a`).

| file | bytes | sha256 | role |
|---|---|---|---|
| `zz_probe_ui_text.lua` | 362617 | `774ede58e5e4b58860f8e74417fe1534cd3c53f36c1f5f06cd6356178f185afa` | UI-text probe — rounds 1–15 of the UI-layer experiments (stat read-back through UIC, simulated-hover passes, context objects). Log: `zz_probe_ui_text_log.txt`. |
| `zz_probe_unit_reads.lua` | 26400 | `41c0773b3ae9f9103861d79a77a1e83bbab448fd21f7e0fe38fce9922c480c78` | Older runtime probe (unit read-path experiments). Log: `zz_probe_unit_reads_log.txt`. |

## Why retired

Both experiments are finished; their findings are recorded in the project
README and in the probe logs (archived under
`C:\Users\vlady\Desktop\WH3_mod\archive\logs\`). Neither file is part of
the mod; they only ever existed to answer one-off questions about the engine.

## Do NOT ship again

`WH3_mod/tools/build_and_install.py` no longer lists them in `FILES` and now
**asserts that no `zz_probe_*` file path can appear inside the built pack**.
To re-run an experiment, copy a probe back out, give it a NEW round number, add
it to `FILES` deliberately — and remove it again when that round closes.
