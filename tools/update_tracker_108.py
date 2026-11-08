# -*- coding: utf-8 -*-
"""Round 108 tracker update: the 1 m air-drop bound + Warp Lightning Rod.

Edits docs/WH3_ability_tracker.md:
  1. a new round-108 update paragraph after the round-107 one;
  2. the Warp Lightning Rod row: AWAITING RULING -> IMPLEMENTED on
     melee_skip_commanders, with the Clan Moulder Lobotomy mutation note;
  3. all 19 air-drop key rows: the 70% bound (7 m) -> the 1 m user value;
  4. the two glossary rows (melee_skip_commanders, air_drop_on_infantry).
"""
import os
import shutil

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
TRACK = os.path.join(ROOT, "docs", "WH3_ability_tracker.md")
BAK = os.path.join(ROOT, "docs", "backups", "round108", "WH3_ability_tracker.pre108.md")


def read(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8")


def write(p, s):
    with open(p, "wb") as f:
        f.write(s.encode("utf-8"))


def rep(s, old, new, n):
    c = s.count(old)
    assert c == n, "count %d (want %d): %r" % (c, n, old[:120])
    return s.replace(old, new)


s = read(TRACK)
if not os.path.exists(BAK):
    shutil.copy2(TRACK, BAK)

PARA = (
    "\n**Update 2026-10-18 (harness 108 — THE 1 m AIR-DROP TEST BOUND + WARP LIGHTNING ROD).** "
    "Two field rulings are **implemented and shipping**. "
    "**(1) THE AIR-DROP OVERLAP BOUND IS 1 m — A USER-CHOSEN TEST VALUE.** The user's words: "
    "\"I tested Drop Bombs but it released them too soon. Please make the range only 1 meter, I will test "
    "it again.\" **'Drop Bombs' is not a shipped ability name** (the loc table carries none), so the row was "
    "resolved from the field log: the only air-drop ability the user actually cast in the 2026-10-18 "
    "session is **Drop Rocks** (`wh2_main_unit_abilities_drop_rocks`, Terradon Riders), accepted at **6.9 m "
    "and 6.0 m** edge-to-edge under the old 7 m proxy — i.e. the ordnance left the flyer while it was still "
    "short of being over the target. The whole `air_drop_on_infantry` family (12 entries / 19 keys) now "
    "takes **ONE constant, `FOURTH.AIR_DROP_BOUND_M = 1`**, and **bypasses the 70% map** (the row's real "
    "10 m no longer maps to 7 m). Why one constant and not 19 edits: `unit:unit_distance()` is "
    "**edge-to-edge**, so a unit **directly under** the caster reads **near 0-5 m, not 0 m** (two "
    "overlapping bounding boxes still report the gap between their edges); if the ability never fires at "
    "1 m the test is simply too tight — raise the constant to 2, 3 or 5 m and nothing else changes. "
    "The 1 m value is **much tighter than the standing 70% rule** and is a test value, not a new rule. "
    "**(2) WARP LIGHTNING ROD IS IMPLEMENTED on `melee_skip_commanders`** exactly like Soulfire and Call of "
    "Tor — in melee, unless every engaged enemy is a Lord or a Hero, with the judged engagement set logged "
    "under its own `warp_lightning_rod` marker and the caster/enemy re-read immediately before the cast. "
    "The user's ruling: \"Warp Lightning Rod seems to be an effect no unit has by default, but during the "
    "campaign some units can aquire it via mutation (Clan Moulder Lobotomy augmentation). Let's treat it "
    "the same as Soulfire.\" The key is `wh2_dlc16_unit_abilities_warp_lightning_rod` (ONE key — no "
    "upgraded twin exists); its row is self-centred (`affect_self` true, all four target flags false, "
    "`target_intercept_range` 0, `effect_range` 0) with a 1 s wind-up and a 3-use / 60 s pool, and its only "
    "invalid-usage flag is `climbing`. **ITS GRANT EXPLAINS THE MISSING CARRIER JUNCTION:** the extraction "
    "carries **no land_units / uset_ability row** for it — only the ability row, the flag row, its UI "
    "effects and its loc line — so it is **not a default unit ability**; in campaign it comes from the "
    "**Clan Moulder Lobotomy mutation**. That is why round 107's data sweep found no carrier and left it "
    "awaiting a ruling. **Counts:** ABILITIES **688 -> 689 entries**, **741 -> 742 keys**, "
    "`melee_skip_commanders` **3 entries / 4 keys -> 4 entries / 5 keys**; the **wheel bombardment set is "
    "COMPLETE at 55 implemented / 0 awaiting**. Spreadsheet `docs/WH3_abilities_master_v9_2026-10-17.xlsx` "
    "(+ `.ods`; v9 supersedes v8; **v1-v8 byte-unchanged**); harness 108: **4006 checks / 0 failures**, red "
    "control **41 failures, all accounted for**; installed pack md5 `82945a05e6f76d241430e7c7bcbafce8`.\n"
)

anchor = "installed pack md5 `c44f38d415e3e1e2e7b0bfb886c41e8c`.\n"
assert s.count(anchor) == 1
s = s.replace(anchor, anchor + PARA)

# ---------------------------------------------------------------- WLR row
old_wlr_start = "| Warp Lightning Rod `wh2_dlc16_unit_abilities_warp_lightning_rod` |"
i = s.index(old_wlr_start)
j = s.index("\n", i)
NEW_WLR = (
    "| Warp Lightning Rod `wh2_dlc16_unit_abilities_warp_lightning_rod` | `implemented (melee, skipping "
    "Lord/Hero-only fights)` | melee_skip_commanders | When armed, fires when THIS unit is in melee, unless "
    "EVERY enemy it is engaged with is a Lord or Hero (the engagement set is read from the enemy "
    "enumerator: alive + is_in_melee + edge-to-edge unit_distance <= 12 m, each member classified with the "
    "1,409-key commander set, fail-closed; the judged set is logged under the warp_lightning_rod marker); "
    "the cast is on the OWNER (the row is self-centred). **Round 108 (2026-10-18): implemented (harness "
    "108)** — the user's ruling: \"Warp Lightning Rod seems to be an effect no unit has by default, but "
    "during the campaign some units can aquire it via mutation (Clan Moulder Lobotomy augmentation). Let's "
    "treat it the same as Soulfire.\" **Its grant is a Clan Moulder LOBOTOMY mutation in campaign, NOT a "
    "default unit ability** — the data carries no carrier junction for it, which is exactly why no battle "
    "roster shows it. | cd 60s · 5s · self · ×3 uses · wind-up 1s · triage-family: Bombardment / ground "
    "artillery · **round 108 (2026-10-18):** implemented (harness 108) |"
)
s = s[:i] + NEW_WLR + s[j:]

# ---------------------------------------------------------------- the 19 rows
s = rep(s,
        "inside the ability's own 70% bound - 7 m of its 10 m",
        "inside the family's overlap bound - 1 m (round 108: a USER-CHOSEN TEST value, much tighter than "
        "the 70% rule's 7 m; unit_distance is edge-to-edge, so a unit directly under the caster reads near "
        "0-5 m, and this one constant is easy to raise)",
        19)

# ---------------------------------------------------------------- glossary
melee_old = ("| `melee_skip_commanders` | **rounds 106-107** - Soulfire, Arachneruption, Call of Tor:")
assert s.count(melee_old) == 1
i = s.index(melee_old)
j = s.index("\n", i)
MELEE_NEW = (
    "| `melee_skip_commanders` | **rounds 106-108** - Soulfire (2 keys), Arachneruption, Call of Tor, Warp "
    "Lightning Rod: the caster is IN MELEE, unless EVERY enemy it is engaged with is a Lord or Hero (the "
    "engagement set = alive + is_in_melee + edge-to-edge `unit_distance` <= 12 m, each classified with the "
    "1,409-key commander set; logged, deduped by note; re-read before the cast) | self cast "
    "(`perform_special_ability(key, self)`) |"
)
s = s[:i] + MELEE_NEW + s[j:]

air_old = ("| `air_drop_on_infantry` | **round 107** - an enemy INFANTRY unit is UNDER the caster: inside the "
           "ability's own 70% bound (7 m of the row's 10 m)")
assert s.count(air_old) == 1
i = s.index(air_old)
j = s.index("\n", i)
AIR_NEW = (
    "| `air_drop_on_infantry` | **round 108** - an enemy INFANTRY unit is UNDER the caster: inside the "
    "family's overlap bound **1 m** (`FOURTH.AIR_DROP_BOUND_M`, a USER-CHOSEN TEST value from round 108 - "
    "it was 7 m at the 70% rule; `unit_distance` is EDGE-TO-EDGE, so a unit directly on top reads near 0-5 m "
    "and this ONE constant is easy to raise if it never fires) measured by `unit_distance(caster)` as the "
    "overlap proxy, with `is_currently_flying()` enforced where the row declares `grounded` (or every "
    "carrier flies)"
)
s = s[:i] + AIR_NEW + s[j:]

write(TRACK, s)
print("tracker updated:", TRACK, os.path.getsize(TRACK), "bytes")
