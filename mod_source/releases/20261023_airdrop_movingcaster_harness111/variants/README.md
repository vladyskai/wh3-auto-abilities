# Harness 111 dial variants (generated, not source)

`harness111.lua` writes one file per non-default world in this directory, then loads it. Each is a
copy of the source under test (live script or annotated copy) with **only the constant line
substituted**:

```
FOURTH.AIR_DROP_CASTER_LEAD = 0.5     ->  the world's lead (1.00 / 0.30 / 0.00 ...)
FOURTH.AIR_DROP_CASTER_DELAY_S = 1.5  ->  the world's caster delay (1.00 ...)
```

Nothing else changes, so a variant world differs from the shipped build in exactly one number — the
same one-line edit a field test would make. They are reproducible artifacts (~780 KB each, 37 MB in
total), so they are **not kept in the repository**: re-running the harness recreates them.

The generator is `harness_variant(path, lead, delay, tag)` at the top level of the harness-110
section inside `harness111.lua`. When the source has no dial lines (the round-110 red-control
snapshot), the helper returns the original path unchanged and the world tests that build as it is.
