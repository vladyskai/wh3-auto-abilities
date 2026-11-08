# -*- coding: utf-8 -*-
"""Flip the 327 auto-accepted section-3a rows from `approved (auto: <trigger>)`
to `implemented (<trigger>)`, preserving the trigger description (the `auto:`
provenance tag is dropped, the description text is kept verbatim). Appends a
section-10 log entry for the implementation round.
"""
import io, re, shutil, os
from collections import Counter

TRACKER = "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_ability_tracker.md"
src = io.open(TRACKER, encoding="utf-8", newline="").read()
assert "\r" not in src, "CRLF in tracker"
lines = src.split("\n")

i3a = next(i for i, l in enumerate(lines) if l.startswith("### 3a."))
i3b = next(i for i, l in enumerate(lines) if l.startswith("### 3b."))

rowre = re.compile(r"^\|\s*(.*?)\s*`([^`]+)`\s*\|\s*`(approved \(auto: [^`]*?)`\s*\|")
changed = 0
seen_trig = Counter()
for i in range(i3a, i3b):
    l = lines[i]
    m = rowre.match(l)
    if not m:
        continue
    st = m.group(3)                       # e.g. approved (auto: health<=75 (no melee gate))
    trigger = st[len("approved (auto: "):-1]   # strip the wrapper -> the trigger description verbatim
    parts = l.split("`")
    assert parts[3] == st, (i + 1, parts[3])
    parts[3] = "implemented (%s)" % trigger
    lines[i] = "`".join(parts)
    changed += 1
    seen_trig[trigger] += 1

print("rows flipped:", changed)
print("by trigger:", dict(seen_trig))
assert changed == 327, changed
assert seen_trig["in-melee self"] == 274
assert seen_trig["health<=75 (no melee gate)"] == 37
assert seen_trig["charge and in-melee"] == 16

# no auto-approved status cell may remain in the 3a inventory (the legend prose
# template `approved (auto: <trigger>)` is expected to stay)
left = sum(1 for i in range(i3a, i3b) if "approved (auto:" in lines[i])
assert left == 0, "auto-approved rows remain: %d" % left

src2 = "\n".join(lines)
log = (
    "\n\n---\n\n"
    "**Auto-accepted implementation round (recorded 2026-10-09 — harness 91).** "
    "All **327** auto-accepted rows (`approved (auto: <trigger>)`) were implemented in ONE build and "
    "their §3a statuses flipped to `implemented (<trigger>)`, preserving each trigger description. "
    "They ride **three EXISTING evaluators** (no new trigger types): `in-melee self` **274** -> the shared "
    "`melee_unwavering` evaluator; `health<=75 (no melee gate)` **37** -> the `ushoran_health` evaluator; "
    "`charge and in-melee` **16** -> the `charge_or_melee` evaluator. Rows sharing an ability name ride ONE "
    "entry (base + DLC/summoned twin keys), so the 327 rows are **311 entries / 327 database keys**; the mod's "
    "abilities table grew **262 -> 573 entries** (**272 -> 599 keys**). Two name-collision entries took a "
    "name-derived marker (Horn of Vaul, Whip of Misery) so no marker repeats. Built and installed as a Movie "
    ".pack (`zz_test_deadly_onslaught.pack`); harness 91 is green (live+annotated) with a red control against "
    "the pre-edit snapshot. The friendly-fire block, the ambiguous/mixed rows and the army-bar rows remain "
    "flagged/excluded as recorded in the auto-rule sweep above.\n"
)
src2 = src2.rstrip("\n") + log
shutil.copyfile(TRACKER, TRACKER + ".bak_pre_impl91")
io.open(TRACKER, "w", encoding="utf-8", newline="").write(src2)
print("tracker updated:", os.path.getsize(TRACKER), "bytes")
assert "\r" not in open(TRACKER, "rb").read().decode("utf-8")
