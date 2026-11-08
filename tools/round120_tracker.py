#!/usr/bin/env python3
"""Round 120 - tracker edits (the authoritative inventory).

Three edits, each asserted, no other line touched:

1. Thorsen's Thunderstorm x2: the tracker status said `skipped (...)` while the
   WORKBOOK status column said IN-WHEEL. The tracker status becomes `excluded
   (...)` - the same shape as the other army-bar exclusions - with the original
   reason kept and the round-120 correction appended.
2. ADD THE MISSING ROW: `wh3_main_spell_slaanesh_slicing_shards_bound` is the
   second key of the mod entry `slicing_shards` and had no row anywhere in the
   inventory. Real name/game data read from the extracted tables; status and
   trigger text match its shipped twin `wh3_dlc20_spell_bound_slicing_shards`.
3. The header count 1,797 -> 1,800 rows.
"""
import re
import shutil
import sys

TR = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
BAK = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\WH3_ability_tracker.md.bak_pre_v19"

OLD_TH = "`skipped (round 106: army-bar ability (army_spec junction) - out of wheel scope)`"
NEW_TH = ("`excluded (round 106: army-bar ability (army_spec junction) - out of wheel scope; "
          "wheel status corrected in round 120: army-bar abilities are outside the wheel by the "
          "user's own rule)`")

TWIN_KEY = "wh3_dlc20_spell_bound_slicing_shards"
MISS_KEY = "wh3_main_spell_slaanesh_slicing_shards_bound"
NEW_ROW = (
    "| Slicing Shards `%s` | `implemented (closest in-melee infantry, enemy ground)` | "
    "enemy_ground_melee_infantry | When armed, fires on the CLOSEST enemy inside the ability's own "
    "70%% bound that is IN MELEE and IS INFANTRY (battle_unit:is_infantry(), unit_class fallback, "
    "fail-closed); the strike is placed on that enemy's own ground (ground form). | "
    "no cooldown (recharge_time -1, single use) · 9s · enemy ground · ×1 uses · wind-up 5s · bound "
    "· triage-family: Bombardment / ground artillery · **round 120 (2026-10-20): the missing "
    "twin.** This key is implemented in the mod - it is the SECOND key of the `slicing_shards` "
    "entry (`%s`, `%s`) - and had NO row anywhere in the 1,799-row inventory until v19; it is "
    "the remainder behind the 741 implemented rows / 742 implemented keys. Grant path: "
    "`uset_ability.tsv` unit_set `wh3_main_sla_mon_keeper_of_secrets_0` (the Keeper of Secrets); "
    "`unit_abilities.source_type = bound`, `num_uses = 1`, `recharge_time = -1` (one use, no "
    "cooldown), `target_intercept_range 200`, 5 s wind-up. |"
    % (MISS_KEY, TWIN_KEY, MISS_KEY))

BAK_DIR = None
shutil.copy2(TR, BAK)

src = open(TR, encoding="utf-8").read()
lines = src.split("\n")

# ---------------------------------------------------------------- 1. the two rows
hits = [i for i, l in enumerate(lines) if OLD_TH in l]
assert len(hits) == 2, ("expected the 2 Thorsen rows, found %d" % len(hits))
for i in hits:
    assert "thorsens_thunderstorm" in lines[i], lines[i][:120]
    lines[i] = lines[i].replace(OLD_TH, NEW_TH)

# ---------------------------------------------------------------- 2. the new row
twin = [i for i, l in enumerate(lines) if ("`%s`" % TWIN_KEY) in l]
assert len(twin) == 1, twin
assert not any(("`%s`" % MISS_KEY) in l for l in lines), "the key already has a row"
i = twin[0] + 1
lines.insert(i, NEW_ROW)

src = "\n".join(lines)

# ---------------------------------------------------------------- 3. the header count
assert src.count("(1,797 rows") == 1
src = src.replace("(1,797 rows",
                  "(1,800 rows, one row per key - the row added in round 120 is Slicing Shards' "
                  "second key")

open(TR, "w", encoding="utf-8", newline="\n").write(src)
print("tracker rows now:", sum(1 for l in src.split("\n") if l.startswith("| ")))
print("thorsen rows updated:", len(hits))
print("missing row inserted after line", i + 1)
