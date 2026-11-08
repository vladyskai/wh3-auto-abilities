# -*- coding: utf-8 -*-
"""FINALISE the tracker for the FINAL ROSTER round.

1. The 238 triage FAMILY rows (`proposed (FF)` / `proposed` carrying a
   `triage-family:` note) -> `excluded (auto: <family> ...)`.
2. The 12 INDIVIDUAL rows (no `triage-family:` note) -> 6 `implemented (...)`
   and 6 `excluded (...)`.
3. No row may read `proposed` / `proposed (FF)` anywhere afterwards.
4. A closing roster tally is computed programmatically and appended as the
   section-10 closing note.
"""
import io, re, shutil, os
from collections import Counter, OrderedDict

TRACKER = "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_ability_tracker.md"
src = io.open(TRACKER, encoding="utf-8", newline="").read()
# NOTE: the triage step rewrote the tracker with CRLF while every prior backup is
# LF-only; normalise back to LF (the project convention) so this round's edits and
# the appended closing tally are consistent.
src = src.replace("\r\n", "\n").replace("\r", "\n")
assert "\r" not in src, "CRLF in tracker"
lines = src.split("\n")


def idx(p):
    for i, l in enumerate(lines):
        if l.startswith(p):
            return i
    raise SystemExit("section not found: " + p)


i3a, i3b, i3c = idx("### 3a."), idx("### 3b."), idx("### 3c.")

FAMILY_EXCL = {
    "Vortex / wandering wind": "excluded (auto: vortex / wandering wind (friendly fire, family decision 2026-10-09))",
    "Bombardment / ground artillery": "excluded (auto: bombardment / ground artillery (friendly fire, family decision 2026-10-09))",
    "Placed / static area damage": "excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))",
    "Breath / cone damage": "excluded (auto: breath / cone damage (friendly fire, family decision 2026-10-09))",
    "Own-troop-damage AoE": "excluded (auto: own-troop-damage AoE (friendly fire by design, family decision 2026-10-09))",
    "Flanking / ambush (flanking_opportunity)": "excluded (auto: flanking / ambush (stealth/escape, family decision 2026-10-09))",
}

# the 12 individuals -> final status, keyed by game key
INDIV = {
    "wh3_dlc26_lord_abilities_blood_sacrifice": "implemented (blood_sacrifice)",
    "wh3_dlc26_unit_abilities_eat_da_runts": "implemented (eat_da_runts)",
    "wh3_main_character_abilities_locus_of_virulence": "implemented (in-melee self)",
    "wh3_dlc27_lord_abilities_the_dance_of_dreaming": "implemented (in-melee self)",
    "wh3_dlc27_lord_abilities_the_waltz_of_lethargy": "implemented (in-melee self)",
    "wh3_cp1_character_abilities_terrifying_presence": "implemented (in-melee self)",
    "wh2_dlc11_hero_abilities_more_powder": "excluded (auto: no ammo-low read (ammo replenish))",
    "wh3_dlc25_item_abilities_ominous_powder": "excluded (auto: no effect text available (unsourceable))",
    "wh2_dlc17_hero_abilities_more_powder_generic": "excluded (auto: no ammo-low read (ammo replenish))",
    "wh3_dlc25_abilities_restock_gunnery_school": "excluded (auto: no ammo-low read (ammo replenish))",
    "wh3_dlc29_spell_bound_undeath_khizaar_the_soulstealer": "excluded (auto: enemy-ground placement (no placement path))",
    "wh2_dlc17_army_abilities_touched_by_the_moon": "excluded (auto: army-bar ability (standing rule 10))",
}

fam_count = Counter()
indiv_count = Counter()
unknown = []

for i in range(i3a, i3c):
    l = lines[i]
    if not l.startswith("|"):
        continue
    parts = l.split("`")
    if len(parts) < 4:
        continue
    key = parts[1]
    status = parts[3]
    if status not in ("proposed", "proposed (FF)"):
        continue
    m = re.search(r"triage-family:\s*([^|·]+)", l)
    if m:
        fam = m.group(1).strip()
        if fam not in FAMILY_EXCL:
            unknown.append((i + 1, fam))
            continue
        parts[3] = FAMILY_EXCL[fam]
        lines[i] = "`".join(parts)
        fam_count[fam] += 1
    else:
        if key not in INDIV:
            unknown.append((i + 1, "INDIV? " + key))
            continue
        parts[3] = INDIV[key]
        lines[i] = "`".join(parts)
        indiv_count[INDIV[key]] += 1

if unknown:
    for u in unknown:
        print("UNKNOWN ROW:", u)
    raise SystemExit("unknown rows - stopping rather than inventing a mapping")

print("family rows excluded:", sum(fam_count.values()), dict(fam_count))
print("individual rows resolved:", sum(indiv_count.values()), dict(indiv_count))
assert sum(fam_count.values()) == 238, sum(fam_count.values())
assert fam_count["Vortex / wandering wind"] == 70
assert fam_count["Bombardment / ground artillery"] == 63
assert fam_count["Placed / static area damage"] == 42
assert fam_count["Breath / cone damage"] == 30
assert fam_count["Own-troop-damage AoE"] == 26
assert fam_count["Flanking / ambush (flanking_opportunity)"] == 7
assert sum(indiv_count.values()) == 12, sum(indiv_count.values())
assert indiv_count["implemented (blood_sacrifice)"] == 1
assert indiv_count["implemented (eat_da_runts)"] == 1
assert indiv_count["implemented (in-melee self)"] == 4
assert sum(v for k, v in indiv_count.items() if k.startswith("excluded")) == 6

# ---- no ROW may read proposed / proposed (FF) any more (the legend prose and
# the historical decisions log may still NAME the status - that is expected).
src2 = "\n".join(lines)


def count_rows_with(s, status):
    n = 0
    for l in s.split("\n"):
        if l.startswith("|"):
            parts = l.split("`")
            if len(parts) >= 4 and parts[3] == status:
                n += 1
    return n


left_prop = count_rows_with(src2, "proposed")
left_ff = count_rows_with(src2, "proposed (FF)")
print("remaining ROWS reading `proposed`:", left_prop, "| `proposed (FF)`:", left_ff)
assert left_prop == 0, "proposed rows remain"
assert left_ff == 0, "proposed (FF) rows remain"
# prose mentions are expected to remain (the legend + the historical log) - sanity only
print("prose mentions kept: `proposed`", src2.count("`proposed`"), "| `proposed (FF)`", src2.count("`proposed (FF)`"))

# ---- the closing roster tally (programmatic, over the inventory tables)
lines = src2.split("\n")
i3a, i3b, i3c = idx("### 3a."), idx("### 3b."), idx("### 3c.")
i4 = idx("## 4.")


def rows(a, b):
    out = []
    for i in range(a, b):
        l = lines[i]
        if not l.startswith("|"):
            continue
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if not cells:
            continue
        m = re.search(r"`([^`]+)`", cells[0])
        if not m:
            continue
        st = cells[1].strip("`").strip() if len(cells) > 1 else ""
        out.append((m.group(1), st))
    return out


inv = rows(i3a, i3b) + rows(i3b, i3c) + rows(i3c, i4)
total = len(inv)
cat = Counter()
exc_fam = Counter()
for key, st in inv:
    if st.startswith("implemented"):
        cat["implemented"] += 1
    elif st.startswith("approved"):
        cat["approved"] += 1
    elif st.startswith("excluded (impossible"):
        cat["impossible"] += 1
    elif st.startswith("excluded (auto"):
        cat["excluded"] += 1
        reason = st[len("excluded (auto: "):].rstrip(")")
        exc_fam[reason] += 1
    elif st.startswith("excluded"):
        cat["excluded"] += 1
        exc_fam["other"] += 1
    elif st.startswith("skipped"):
        cat["skipped"] += 1
    elif st.startswith("rejected"):
        cat["rejected"] += 1
    else:
        cat["OTHER:" + st] += 1

s = sum(cat.values())
print("inventory rows:", total, "| categorised:", s)
assert s == total, (total, s, dict(cat))
for k in sorted(cat):
    print("   ", k, cat[k])

# fatal: no UNCATEGORISED status may exist
bad = [k for k in cat if k.startswith("OTHER:")]
assert not bad, bad

# impossible reasons
imp = Counter(st[len("excluded (impossible: "):].rstrip(")") for k, st in inv if st.startswith("excluded (impossible"))
# the 6 triage family reasons
fam_reason = Counter()
for k, st in inv:
    for fam, reason in ((v, v) for v in FAMILY_EXCL.values()):
        pass
fam_reason = Counter()
for k, st in inv:
    if st in FAMILY_EXCL.values():
        fam_reason[st] += 1


def node(v):
    return "{:,}".format(v)


tally = []
tally.append("")
tally.append("")
tally.append("---")
tally.append("")
tally.append("**CLOSING ROSTER TALLY (the section-10 closing note) - the FINAL ROSTER BUILD, 2026-10-09.**")
tally.append("")
tally.append("Every one of the **%s** inventory rows (section 3a + 3b) now carries a FINAL status; "
             "**no row anywhere reads `proposed` or `proposed (FF)`**." % node(total))
tally.append("")
tally.append("| Final category | Rows |")
tally.append("|---|---:|")
tally.append("| **implemented** | %s |" % node(cat["implemented"]))
tally.append("| **approved** (awaiting implementation) | %s |" % node(cat["approved"]))
tally.append("| **excluded - impossible** (engine wall / user-rejected class) | %s |" % node(cat["impossible"]))
tally.append("| **excluded - by reason family** (auto/family decisions) | %s |" % node(cat["excluded"]))
tally.append("| **skipped** (revisit / unsuitable / army-bar & magic-scope skips) | %s |" % node(cat["skipped"]))
tally.append("| **rejected** (user) | %s |" % node(cat["rejected"]))
tally.append("| **TOTAL** | **%s** |" % node(total))
tally.append("")
tally.append("Reconcile: %s (implemented) + %s (approved) + %s (excluded) + %s (skipped) + %s (rejected) = **%s** = the inventory row count."
             % (node(cat["implemented"]), node(cat["approved"]),
                node(cat["excluded"] + cat["impossible"]), node(cat["skipped"]),
                node(cat["rejected"]), node(total)))
tally.append("")
tally.append("### The impossible rows (auto-excluded at triage time; reasons):")
tally.append("")
tally.append("| Reason | Rows |")
tally.append("|---|---:|")
for reason, n in imp.most_common():
    tally.append("| %s | %s |" % (reason, node(n)))
tally.append("| **impossible total** | **%s** |" % node(sum(imp.values())))
tally.append("")
tally.append("### The 238 triage-family rows excluded this round (by family):")
tally.append("")
tally.append("| Family | Rows |")
tally.append("|---|---:|")
for fam, n in fam_count.most_common():
    tally.append("| %s | %s |" % (fam, node(n)))
tally.append("| **family total** | **%s** |" % node(sum(fam_count.values())))
tally.append("")
tally.append("### The 12 INDIVIDUAL rows resolved (6 built + 6 excluded):")
tally.append("")
tally.append("| Final status | Rows |")
tally.append("|---|---:|")
for st, n in sorted(indiv_count.items()):
    tally.append("| `%s` | %s |" % (st, node(n)))
tally.append("| **individual total** | **%s** |" % node(sum(indiv_count.values())))
tally.append("")
tally.append("**The flagged 347 = %s excluded (impossible) + %s excluded (family) + 12 individual - all resolved; "
             "totals reconcile.**" % (node(sum(imp.values())), node(sum(fam_count.values()))))
tally.append("")

src2 = src2.rstrip("\n") + "\n".join(tally)
shutil.copyfile(TRACKER, TRACKER + ".bak_pre_impl92")
io.open(TRACKER, "w", encoding="utf-8", newline="\n").write(src2)
print("tracker updated:", os.path.getsize(TRACKER), "bytes")
assert "\r" not in open(TRACKER, "rb").read().decode("utf-8"), "CRLF written"
print("CLOSING TALLY WRITTEN")
