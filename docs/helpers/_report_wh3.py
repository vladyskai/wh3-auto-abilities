#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the auto-classification report and update the tracker's statuses,
legend and section-10 log from the R1-R4 classification in _classify_wh3.py."""
import re, os, json, collections, shutil

exec(open(r"C:/Users/vlady/Desktop/WH3_mod/docs/helpers/_classify_wh3.py", encoding="utf-8").read().split("if __name__")[0])

DESK = r"C:/Users/vlady/Desktop"
TRACKER = os.path.join(DESK, "WH3_ability_tracker.md")
REPORT = os.path.join(DESK, "WH3_auto_classification_report.md")

FAM_GLOSS = {
    "augment_melee_self": "melee combat buff (attack / weapon strength)",
    "augment_melee": "melee combat buff (attack / weapon strength)",
    "augment_melee_area": "melee combat buff (area, allies in range)",
    "augment_defense_melee": "melee defence buff",
    "augment_defense_melee_area": "melee defence buff (area)",
    "augment_morale": "leadership (morale) buff",
    "augment_morale_area": "leadership (morale) buff (area)",
    "augment_self_area": "self / ally buff (area)",
    "augment_ranged": "missile (ranged) attack buff",
    "augment_ranged_area": "missile (ranged) attack buff (area)",
    "augment_defense_ranged": "missile resistance / defence buff",
    "augment_defense_ranged_area": "missile resistance / defence buff (area)",
    "augment_spellcasting": "spellcasting buff",
    "augment_support_self": "self support buff",
    "augment_charge_self": "charge bonus (self)",
    "augment_charge": "charge bonus",
    "augment_charged_at": "charge bonus (applied when charged at)",
    "augment_charged_at_area": "charge bonus (when charged at, area)",
    "healing": "heal / hit-point replenish",
    "healing_area": "heal / hit-point replenish (area)",
    "healing_single_use": "one-use heal / replenish",
    "augment_melee_healing": "melee buff + heal",
    "aoe_centred_on_self": "self-centred beneficial aura",
    "hex_melee": "enemy melee debuff (hex)",
    "hex_melee_area": "enemy melee debuff (hex, area)",
    "hex_melee_area_self": "self-centred melee hex aura",
    "hex_morale": "enemy leadership debuff (hex)",
    "hex_morale_area": "enemy leadership debuff (hex, area)",
    "hex_armour": "enemy armour debuff (hex)",
    "hex_armour_area": "enemy armour debuff (hex, area)",
    "hex_speed": "enemy speed debuff (hex)",
    "hex_speed_area": "enemy speed debuff (hex, area)",
    "hex_speed_under_fire": "enemy speed debuff (hex, under fire)",
    "hex_speed_charging_at": "enemy speed debuff (hex, charging)",
    "hex_ranged": "enemy ranged debuff (hex)",
    "hex_ranged_area": "enemy ranged debuff (hex, area)",
    "hex_spellcaster": "enemy spellcaster debuff (hex)",
    "hex_spellcasting": "enemy spellcasting debuff (hex)",
    "hex_flying_area": "enemy flying debuff (hex, area)",
}

def eff(r):
    fam = FAM.get(r["key"], "")
    return FAM_GLOSS.get(fam, fam or "self/ally effect")

# ------------------------------------------------------------------ counts
acc, exc, flg = BUCKETS["accept"], BUCKETS["exclude"], BUCKETS["flag"]
total = len(acc) + len(exc) + len(flg)
acc_by_trigger = collections.Counter(x["reason"] for x in acc)
exc_by_reason = collections.Counter(x["reason"] for x in exc)
flg_by_reason = collections.Counter(x["reason"] for x in flg)

# ------------------------------------------------------------------ report
L = []
w = L.append
w("# WARHAMMER III — auto-classification report (widened standing rules R1–R4)")
w("")
w("Scope: **every undecided tracker candidate** — the rows reading `proposed` or `proposed (FF)` in")
w("`WH3_ability_tracker.md` §3a/§3b — swept **in one pass** into auto-accept / auto-exclude / flag.")
w("Classification is derived from the game's own data: `grouped2.json` (effect family),")
w("`unit_spec_abil.tsv` (targeting / engine flags) and the real effect phases")
w("(`phase_junc.tsv` + `phases.tsv`). **Nothing here is built or installed** — this is the triage list.")
w("")
w("## Count table")
w("")
w("| Bucket | Rows | Share |")
w("|---|---:|---:|")
w(f"| Total scanned (`proposed` + `proposed (FF)`) | {total} | 100% |")
w(f"| **AUTO-ACCEPT** (R1 positive buffs / R2 enemy debuffs) | {len(acc)} | {len(acc)*100//total}% |")
w(f"| **AUTO-EXCLUDE** (R3 unsuitable families) | {len(exc)} | {len(exc)*100//total}% |")
w(f"| **FLAG** (R4 — the only items still to ask about) | {len(flg)} | {len(flg)*100//total}% |")
w("")
w("**Auto-accepted by trigger:** " + " · ".join(f"`{k}` {v}" for k, v in acc_by_trigger.most_common()))
w("")
w("**Top auto-exclude reasons:** " + " · ".join(f"{k} {v}" for k, v in exc_by_reason.most_common(5)))
w("")
w("**Flag reasons:** " + " · ".join(f"{k} {v}" for k, v in flg_by_reason.most_common()))
w("")
w("### How the widened rules were applied")
w("")
w("- **R1 positive-only self/ally buffs** → auto-accept, trigger chosen by effect family "
  "(melee/weapon/armour/leadership/resistance/ranged/spellcasting buffs → `in-melee self`; "
  "charge families → `charge and in-melee`; heals → `health<=75 (no melee gate)`; heal+melee → `in melee and health<=75`).")
w("- **R2 enemy debuffs** (hexes: melee / leadership / armour / speed / ranged / spellcaster) → auto-accept `in-melee self`.")
w("- **R3 unsuitable families** → auto-exclude: vortex · bombardment · explosive/placed AoE · breath · "
  "summon (incl. `threatened`) · ground-target-only · no sourceable effect text. **Army-bar abilities** are also "
  "auto-excluded under the existing **standing rule 10** (user: “Skip all army bar abilities”) rather than re-queued.")
w("- **R4** → flag only: the **friendly-fire block** (the 218 FF-parked rows), own-troop-damage AoE, rampage, "
  "mutual exclusivity, stealth/escape, transform/shapechange, and anything ambiguous or mixed positive/negative.")
w("")
w("> **Note on the FF block.** The task's R4 says the friendly-fire rows are *flagged* (“including the FF rows”); "
  "their effect families (vortex / bombardment / explosive) are otherwise the ones R3 sweeps. This report follows the")
w("> explicit R4 instruction and **flags all 218**. If you would rather sweep them away as R3 excludes, the single")
w(f"> change is: flag {len(flg)} → {len(flg)-218} and auto-exclude {len(exc)} → {len(exc)+218}.")
w("")
w("> **Note on army-bar.** R4 lists army-bar as a flag category, but the user already gave the standing decision")
w("> “Skip all army bar abilities” (rule 10), so those rows are auto-excluded (reason `army-bar ability`) and never re-asked.")
w(f"> If you would rather follow R4 literally and flag them, the change is: flag {len(flg)} → {len(flg)+98} and auto-exclude {len(exc)} → {len(exc)-98}.")
w("")

def tbl(header, rows_):
    w("| " + " | ".join(header) + " |")
    w("|" + "|".join("---" for _ in header) + "|")
    for r in rows_:
        w("| " + " | ".join(str(c) for c in r) + " |")

w("## Appendix A — AUTO-ACCEPT (all rows)")
w("")
w(f"All {len(acc)} rows, sorted by trigger then ability name. Trigger code is what the implementation job will build.")
w("")
tbl(["Ability", "Key", "Trigger (rule)", "One-line effect"],
    [[r["name"], "`" + r["key"] + "`", r["reason"], eff(r)] for r in sorted(acc, key=lambda x: (x["reason"], x["name"].lower()))])
w("")
w("## Appendix B — AUTO-EXCLUDE (all rows, with reason)")
w("")
w(f"All {len(exc)} rows, sorted by reason then ability name.")
w("")
tbl(["Ability", "Key", "Reason", "Notes"],
    [[r["name"], "`" + r["key"] + "`", r["reason"], r["notes"].replace("|", "/")] for r in sorted(exc, key=lambda x: (x["reason"], x["name"].lower()))])
w("")
w("## Appendix C — FLAG for the user (all rows, with reason)")
w("")
w(f"All {len(flg)} rows. These stay `proposed` in the tracker — the only items to be asked about later.")
w("")
tbl(["Ability", "Key", "Flag reason", "Notes"],
    [[r["name"], "`" + r["key"] + "`", r["reason"], r["notes"].replace("|", "/")] for r in sorted(flg, key=lambda x: (x["reason"], x["name"].lower()))])
w("")

open(REPORT, "w", encoding="utf-8", newline="").write("\n".join(L) + "\n")
print("report written:", REPORT, os.path.getsize(REPORT), "bytes")

# ------------------------------------------------------------------ tracker edit
NEW = {r["line"]: r for r in (acc + exc + flg)}
lines = open(TRACKER, encoding="utf-8", newline="").read().split("\n")
changed = 0
for r in acc:
    i = r["line"] - 1
    parts = lines[i].split("`")
    parts[3] = "approved (auto: %s)" % r["reason"]
    lines[i] = "`".join(parts); changed += 1
for r in exc:
    i = r["line"] - 1
    parts = lines[i].split("`")
    parts[3] = "excluded (auto: %s)" % r["reason"]
    lines[i] = "`".join(parts); changed += 1
print("row statuses changed:", changed)

# ---- legend: add rules 11-14 (R1-R4) after rule 10
legend_anchor = "This extends the earlier exclusions (`spell` / winds-of-magic / cataclysm keys, §3c)."
add = legend_anchor + """
11. **(R1) Positive-only buffs auto-accept, by effect family (widened 2026-10-09):** a self-only or ally-only buff with **no negative and no friendly-fire component** is **auto-accepted without the questionnaire**. Trigger by family: **melee attack / melee defence / weapon damage (base or AP) / armour / leadership / physical-or-damage resistance / ward / missile resistance / Expert Charge Defence / Immune to Flanking / Immune to Psychology** → `in-melee self`; **heal-over-time / hit-point replenish** with no melee part → `health<=75` (no melee gate); **heal + armour or melee-defence** → `in melee AND health<=75`; **Unbreakable / Cannot Die / Stubborn / Hold the Line** → `wavering self` (or `wavering self-or-ally` when the text reaches allies in range); **charge bonus / charge speed / mass / impact damage** → `charge and in-melee`. Auto-accepted items are marked `approved (auto: <trigger>)`.
12. **(R2) Enemy debuffs auto-accept (widened 2026-10-09):** effects applied **to enemies in range** — a negative melee attack / defence / leadership / armour / resistance / speed, i.e. the **Hex** families — are **auto-accepted as `in-melee self`**; the user has consistently approved these before.
13. **(R3) Unsuitable families auto-exclude (widened 2026-10-09):** **vortex**, **bombardment**, **explosive**, **summon** (unless already handled), **pure movement / speed-only with no combat effect**, **healing of enemies**, **abilities that target the ground only**, and anything whose **effect text is empty/unknown after one genuine sourcing attempt**. Auto-excluded items are marked `excluded (auto: <reason>)` and get **no automatic logic**.
14. **(R4) Flag for the user — do not auto-decide (widened 2026-10-09):** **applies Rampage**, **damages or kills friendly units** (friendly fire, **including the FF rows**), **mutually exclusive** abilities, **army-bar** abilities, **stealth / escape / stalk / unspottable** effects, **transform / shapechange**, abilities that need a **live enemy-unit read we do not have**, and anything whose net effect is **ambiguous or mixed positive-and-negative**. Flagged rows keep the status `proposed` / `proposed (FF)` so they still surface."""
assert legend_anchor in "\n".join(lines), "legend anchor not found"
src = "\n".join(lines)
src = src.replace(legend_anchor, add, 1)

# ---- section 10 log entry (append at end of file)
log = """

---

**Auto-rule widening sweep (recorded 2026-10-09 — blocks 10, "no per-item review").** The user's direction for this round (relayed): **"tired of the five-questions-at-a-time pipeline"** and **"approved widening the auto-rules so most undecided candidates never reach him"**. Four new **standing rules (R1–R4, recorded as rules 11–14 in the header legend)** were added and applied **in one sweep** to every undecided candidate — the **%d** rows still reading `proposed` plus the **%d** rows reading `proposed (FF)` (**%d** in all). Result: **%d auto-accepted** (`approved (auto: <trigger>)`), **%d auto-excluded** (`excluded (auto: <reason>)`), and **%d flagged** (kept `proposed` / `proposed (FF)` — the only rows the user will be asked about later). Auto-accepted by trigger: %s. Top auto-exclude reasons: %s. The full per-row lists are in the companion report `WH3_auto_classification_report.md` (Appendix A auto-accept, B auto-exclude, C flag), written so the user can **veto** any single auto-decision in one line. **No per-item review of the auto-decisions was performed** (faster option the user chose). **Nothing was built or installed in this round** — implementing the auto-accepted set is the next job. The friendly-fire block stays flagged (per the R4 wording "including the FF rows"); army-bar rows are auto-excluded under standing rule 10 ("Skip all army bar abilities").""" % (
    len([r for r in rows if r["status"] == "proposed"]),
    len([r for r in rows if r["status"] == "proposed (FF)"]), total,
    len(acc), len(exc), len(flg),
    " · ".join(f"`{k}` {v}" for k, v in acc_by_trigger.most_common()),
    " · ".join(f"{k} {v}" for k, v in exc_by_reason.most_common()))
src = src.rstrip("\n") + log + "\n"

shutil.copyfile(TRACKER, TRACKER + ".bak_autowiden")
open(TRACKER, "w", encoding="utf-8", newline="").write(src)
print("tracker updated:", TRACKER, os.path.getsize(TRACKER), "bytes")
print("accept:", len(acc), "exclude:", len(exc), "flag:", len(flg), "total:", total)
