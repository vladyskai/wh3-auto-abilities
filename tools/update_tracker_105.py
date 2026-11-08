"""Round 105 tracker update: Tz'arkan implemented on health_below_15; the other
12 transform keys unified to 'skipped (user decision 2026-10-17: no automation
wanted)' in EVERY place they appear. LF is preserved (binary read/write).
"""
import re

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
s = open(P, "rb").read().decode("utf-8")
orig = s

TZ = ["wh2_dlc14_lord_abilities_tzarkan", "wh2_dlc14_lord_abilities_tzarkan_mp",
      "wh2_dlc14_lord_abilities_tzarkan_snikch", "wh2_dlc14_lord_abilities_tzarkan_spite",
      "wh2_dlc14_lord_abilities_tzarkan_spite_mp"]
WU = {"wh2_dlc14_lord_abilities_tzarkan_snikch": "1.5s"}
SKIP = ["wh3_dlc24_lord_abilities_formless_horror", "wh3_dlc24_lord_abilities_formless_horror_changeling",
        "wh3_dlc24_lord_abilities_formless_horror_quest_battle",
        "wh3_dlc24_lord_abilities_formless_horror_quest_battle_changeling_form",
        "wh3_dlc24_lord_abilities_jade_dragon_dragon_form", "wh3_dlc24_lord_abilities_jade_dragon_human_form",
        "wh3_main_lord_abilities_iron_dragon_dragon_form", "wh3_main_lord_abilities_iron_dragon_human_form",
        "wh3_main_lord_abilities_storm_dragon_dragon_form", "wh3_main_lord_abilities_storm_dragon_human_form",
        "wh3_dlc27_unit_abilities_dread_maw_underground", "wh3_dlc27_unit_abilities_dread_maw_surface"]

TZ_STATUS = "implemented (health_below_15: below 15% self)"
TZ_TEXT = ("When the unit is alive, NOT routing and its health (FOURTH.health_pct, a real 0-100 %) is strictly "
           "BELOW 15: cast on SELF through the unit form (fresh caster handle; no range bound - a self cast has "
           "no distance). The exact percentage is logged at the decision and again at the pre-cast re-check, "
           "which SKIPS the cast when the unit died or rose to/above 15 inside the wind-up. In-flight gate: "
           "wind-up + 2 s.")
TZ_NOTE = ("cd 0s · 0s · self · wind-up {wu} · **round 105 (2026-10-17):** implemented on the user's rule "
           "(\"activate Tz'arkan when caster health is below 15%\") - ONE entry carrying all FIVE Tz'arkan keys; "
           "the line is ONE constant (FOURTH.TZARKAN_PCT) and easy to raise; harness 105")
SKIP_STATUS = "skipped (user decision 2026-10-17: no automation wanted)"
SKIP_TEXT = ("No automation - SKIPPED by the user's decision of 2026-10-17 (\"I see no point to automate Formless "
             "Horror, Transformation of the Dragon, Burrow and Surface. So we skip them and mark them as skipped "
             "in the spreadsheet.\"). Nothing rides a trigger.")
SKIP_NOTE_ADD = " · **round 105 (2026-10-17):** SKIPPED by the user's decision (no automation wanted); not in the mod."


def row_rewrite(line, key, status, family, text, note_fn):
    parts = line.split(" | ")
    # parts[0] = '| Name `key`'
    assert parts[0].startswith("| ") and ("`" + key + "`") in parts[0], line[:120]
    parts[1] = "`" + status + "`"
    parts[2] = family
    parts[3] = text
    parts[4] = note_fn(parts[4])
    return " | ".join(parts)


lines = s.split("\n")
n_tz = n_sk = 0
for i, l in enumerate(lines):
    if not l.startswith("| "):
        continue
    fields = l.split(" | ")
    for k in TZ:
        if ("`" + k + "`") in fields[0] and len(fields) >= 5 and "|" in l[1:]:
            lines[i] = row_rewrite(l, k, TZ_STATUS, "health_below_15", TZ_TEXT,
                                   lambda note, k=k: TZ_NOTE.format(wu=WU.get(k, "3s")))
            n_tz += 1
            break
    for k in SKIP:
        if ("`" + k + "`") in fields[0] and len(fields) >= 5:
            lines[i] = row_rewrite(l, k, SKIP_STATUS, "-", SKIP_TEXT, lambda note: note + SKIP_NOTE_ADD)
            n_sk += 1
            break
s = "\n".join(lines)
print("main-table rows rewritten: tzarkan", n_tz, "| skipped", n_sk)
assert n_tz == 5, n_tz
assert n_sk == 12, n_sk

# ---------------------------------------------------------------- the legend
leg_anchor = ("- `skipped (revisit)` — user chose to skip the item for now (not a rejection); revisit in a later "
              "questionnaire block.\n")
assert s.count(leg_anchor) == 1
LEG = leg_anchor + (
    "- `skipped (user decision 2026-10-17: no automation wanted)` — the user ruled the item OUT of automation on "
    "2026-10-17: **\"I see no point to automate Formless Horror, Transformation of the Dragon, Burrow and Surface. "
    "So we skip them and mark them as skipped in the spreadsheet.\"** 12 keys carry it — Formless Horror x4, "
    "Transformation of the Dragon x6, Burrow, Surface. No trigger, no code, nothing removed from the mod; the "
    "status holds until the user reopens the item.\n"
    "- `implemented (health_below_15: below 15% self)` — the round-105 trigger (Tz'arkan): the OWNER is alive, "
    "not routing and its health (`FOURTH.health_pct`, 0-100) is strictly BELOW 15; cast on SELF through the unit "
    "form with a fresh caster handle and no range bound; the exact percentage is logged at the decision and at "
    "the pre-cast re-check, which skips a dead or risen caster; the in-flight gate applies (3 s wind-up, 1.5 s "
    "on the Snikch key). ONE entry, FIVE keys.\n")
s = s.replace(leg_anchor, LEG)

# ---------------------------------------------------------------- the decision paragraphs
d1 = ("- Decision: **skipped (revisit)** — user: “Skip for now.” NOTE: its **Effects** line is `<unknown>` in the "
      "review doc")
assert s.count(d1) == 1
s = s.replace(d1,
              "- Decision: **skipped (revisit)** — user: “Skip for now.” NOTE: its **Effects** line is `<unknown>` in the "
              "review doc")
s = s.replace(
    "before this item can ever be decided.\n\n**281. Fury of Ulric**",
    "before this item can ever be decided. **(2026-10-17, FINAL: `skipped (user decision 2026-10-17: no automation "
    "wanted)` — the user ruled the whole transform family out of automation; the `<unknown>` effect line no longer "
    "blocks anything because no automation is wanted.)**\n\n**281. Fury of Ulric**", 1)

d2 = ("- Decision: **skipped (revisit)** — user: “Skip for now.” (Applies to all three keys: "
      "`wh3_dlc24_lord_abilities_jade_dragon_dragon_form`, `wh3_main_lord_abilities_iron_dragon_dragon_form`, "
      "`wh3_main_lord_abilities_storm_dragon_dragon_form`.)")
assert s.count(d2) == 1
s = s.replace(d2, d2 + " **(2026-10-17, FINAL: `skipped (user decision 2026-10-17: no automation wanted)` for all "
                        "six Dragon keys — dragon form AND human form.)**")

d3 = ("- **Formless Horror** (`wh3_dlc24_lord_abilities_formless_horror` + "
      "`wh3_dlc24_lord_abilities_formless_horror_quest_battle`) — `skipped (revisit)`. User: **“Skip for now”**.")
assert s.count(d3) == 1
s = s.replace(d3, d3 + " **(2026-10-17, FINAL: `skipped (user decision 2026-10-17: no automation wanted)`.)**")
d4 = ("- **Transformation of the Dragon** (`wh3_dlc24_lord_abilities_jade_dragon_dragon_form` + "
      "`wh3_main_lord_abilities_iron_dragon_dragon_form` + `wh3_main_lord_abilities_storm_dragon_dragon_form`) — "
      "`skipped (revisit)`. User: **“Skip for now”**.")
assert s.count(d4) == 1
s = s.replace(d4, d4 + " **(2026-10-17, FINAL: `skipped (user decision 2026-10-17: no automation wanted)` for all "
                        "six Dragon keys.)**")

# ---------------------------------------------------------------- the 10.7 table rows
lines = s.split("\n")
n7 = 0
for i, l in enumerate(lines):
    m = re.match(r"^\| \d+ \| .+ \| `([a-z0-9_]+)` \| .*\|$", l)
    if not m:
        continue
    k = m.group(1)
    if k in TZ:
        lines[i] = re.sub(r"\| `[^`]+` \|$", "| `" + TZ_STATUS + "` |", l)
        n7 += 1
    elif k in SKIP:
        lines[i] = re.sub(r"\| `[^`]+` \|$", "| `" + SKIP_STATUS + "` |", l)
        n7 += 1
s = "\n".join(lines)
print("10.7 table rows rewritten:", n7)
assert n7 == 17, n7

s = s.replace(
    "* **All 17 are IN-WHEEL and NONE is implemented** (verified against the mod's 682 keys). There is therefore **no\n"
    "  transform implemented as a summon**.",
    "* **All 17 are IN-WHEEL. FIVE are implemented (Tz'arkan's five keys, `health_below_15`, round 105) and the other\n"
    "  TWELVE are `skipped (user decision 2026-10-17: no automation wanted)`** — the user's ruling of 2026-10-17.\n"
    "  There is still **no transform implemented as a summon**: Tz'arkan is a REAL cast on the caster's own wheel,\n"
    "  not a summon trigger.", 1)

# ---------------------------------------------------------------- the xlsx reference
s = s.replace("`docs/WH3_abilities_master_v5_2026-10-17.xlsx`.", "`docs/WH3_abilities_master_v6_2026-10-17.xlsx`.")

# ---------------------------------------------------------------- 10.8
SEC = """

### 10.8 Tz'arkan on a low-health trigger; the other transforms skipped (round 105, 2026-10-17)

Two user rulings, one round. **Nothing was removed from the mod** — no transform was ever in the `ABILITIES` table.

**A. TZ'ARKAN — implemented.** The user's rule: *"I think it might make sense to activate Tz'arkan when caster
health is below 15%, don't you think? Let's implement and test it."*

* **ONE entry (`marker: tzarkan`) carries all FIVE keys** — `wh2_dlc14_lord_abilities_tzarkan`, `_mp`, `_snikch`,
  `_spite`, `_spite_mp`. They share one badge, one arming switch and one back-off, exactly like the other
  multi-key entries.
* **New trigger family `health_below_15`** (`FOURTH.evaluate_tzarkan_low_health`): the OWNER must be **alive**
  (the poll's own gate), **not routing**, and its health — read only through **`FOURTH.health_pct`**, the ONE
  0-100 reader — must be **strictly BELOW 15**. Never a raw `HealthPercent` read: that field answers a **0..1
  FRACTION**, so `hp < 15` on it would be true for every unit on the field (the round-103 failure).
* **Cast on SELF through the unit form** (`perform_special_ability(key, owner)`) with the caster's controller
  re-fetched FRESH that tick. No range bound is read or needed — a self cast has no distance.
* **The gates apply unchanged**: the in-flight gate holds the pair for `wind_up + 2 s` after a cast (the row
  declares **3.0 s**; **1.5 s** for the Snikch key), and there is no charge gate (unlimited uses).
* **The exact percentage is logged twice**: at the decision (the ATTEMPT reason: `health 14.0% (BELOW the 15%
  line) - one-way transform, cast on SELF`) and at the pre-cast re-check
  (`tzarkan pre-cast re-check: the caster is still below the line (alive=true, health=14.0% of BELOW 15%, no
  range bound - self cast) - firing`). If the unit DIED or ROSE to/above 15 inside the wind-up the cast is
  skipped: `tzarkan SKIPPED: the caster lapsed before the cast (alive=…, health=25.0%, the line is BELOW 15%, no
  range bound - self cast) - cast not spent`.
* **THE THRESHOLD IS DELIBERATE AND EASY TO RAISE.** A transform is very likely **one-way**, and the 3 s wind-up
  can let a caster at 14% die before the transform resolves. 15% is the user's own number and is **one constant**
  (`FOURTH.TZARKAN_PCT = 15`); raising it to 20/25% is a one-line change if field tests show deaths before the
  transform lands.
* **Counts:** 642 → **643 entries**, 682 → **687 keys**, 42 → **43 evaluators**. The five keys were already
  IN-WHEEL; the spreadsheet moves 5 rows from NOT IMPLEMENTED to IMPLEMENTED (682 → 687) and 459 → 454 not
  implemented.

**B. THE OTHER 12 TRANSFORM KEYS — SKIPPED by the user's decision.** *"I see no point to automate Formless
Horror, Transformation of the Dragon, Burrow and Surface. So we skip them and mark them as skipped in the
spreadsheet."* All **12** carry the ONE status `skipped (user decision 2026-10-17: no automation wanted)` in
every place they appear in this tracker:

| # | Ability | Key(s) |
|---|---|---|
| 1-4 | Formless Horror (+ Changeling, + quest battle, + quest battle Changeling form) | `wh3_dlc24_lord_abilities_formless_horror`, `_changeling`, `_quest_battle`, `_quest_battle_changeling_form` |
| 5-10 | Transformation of the Dragon (Jade / Iron / Storm × dragon form / human form) | `wh3_dlc24_lord_abilities_jade_dragon_dragon_form`, `_human_form`; `wh3_main_lord_abilities_iron_dragon_dragon_form`, `_human_form`; `wh3_main_lord_abilities_storm_dragon_dragon_form`, `_human_form` |
| 11 | Burrow | `wh3_dlc27_unit_abilities_dread_maw_underground` |
| 12 | Surface | `wh3_dlc27_unit_abilities_dread_maw_surface` |

None of the 12 was ever in the mod (verified: none of the 12 key strings appears in the shipped script), so
**nothing was deleted**. The spreadsheet shows Implementation **`SKIPPED (user decision)`** on those 12 rows and
carries the new status value in its Definitions vocabulary.

**Proof — harness 105.** GREEN `checks: 3702, failures: 0`. Tz'arkan worlds (each run against the live source
AND the annotated copy): **T1** 14.0% → fires exactly once, on the OWNER, with `health 14.0%` logged at the
decision and `health=14.0%` at the pre-cast re-check, and the `HealthPercent` fallback field never read; **T2**
16.0% → silent; **T3** 14.0% at the decision then 25.0% at the re-check (the wind-up window) → the cast is
SKIPPED with the real number logged; **T4** a dead owner (0 men) at 10% → silent (the poll's alive gate).
RED (pre-105 snapshot, `docs/backups/round105/*.pre105.lua`): `checks: 3601, failures: 110` = the 48 baseline
failures harness 104 itself shows on that snapshot, raised by **53 designed count pins** (this round's copy
pins 643/687 and the 43-entry wording table, the snapshot has 642/682 and 42) + **9 Tz'arkan discriminators**
(T1a/b/c/d/e and T3b on the live side; T1a/b/c on the annotated side). Nothing regressed: 0 failures present in
harness 104's red run are absent here.

**Build/install 105:** script 708,037 bytes; all five ship files byte-identical to source; built == installed pack
md5 **`a8fea1b2ee6292e5c07ada2c621fa900`** (1,043,113 bytes). Tokens present in the installed pack:
`trigger = "health_below_15"`, `FOURTH.TZARKAN_PCT = 15`, `function FOURTH.evaluate_tzarkan_low_health`,
`tzarkan pre-cast re-check`, `tzarkan SKIPPED: the caster lapsed`. `zz_probe_dist.pack` is still installed.

**Spreadsheet:** `docs/WH3_abilities_master_v6_2026-10-17.xlsx` (+ `.ods`) — **v6 supersedes v5; v1-v5 are
byte-unchanged**. Five Tz'arkan rows IMPLEMENTED on `health_below_15` with the full rule text; 12 rows
`SKIPPED (user decision)` with the reason; the Definitions vocabulary carries the new status and the glossary the
new trigger (43 evaluators, TOTAL 643/687); Numbers re-counted (implemented 687, not implemented 454, in-wheel
1,141 unchanged); the Changelog has a v6 row; the Transforms sheet shows 5 implemented / 12 skipped.

**What to retest (Tz'arkan).** Field Malus Darkblade (or Snikch / any unit carrying the key), arm the TZ badge,
and let him drop below 15% health:
1. ONE cast when the log reads `health 14.x% (BELOW the 15% line)` and the pre-cast line repeats the number; the
   unit should transform.
2. No cast at 16% or above.
3. If he dies inside the wind-up the log shows `tzarkan SKIPPED: the caster lapsed before the cast` and no cast
   is spent — that is the designed behaviour; if it happens often, raise `FOURTH.TZARKAN_PCT`.
4. A second cast cannot arrive before the first resolves (in-flight gate, 5 s / 3.5 s for Snikch).
"""
s = s.rstrip("\n") + SEC

open(P, "wb").write(s.encode("utf-8"))
b = open(P, "rb").read()
print("tracker rewritten:", len(orig.encode("utf-8")), "->", len(b), "bytes, CR =", b.count(b"\r"))
