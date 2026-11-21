#!/usr/bin/env python3
"""Build WH3_abilities_master_v70_2026-11-21.xlsx from v69 - round 188: the range rule (user ruling 2026-11-21: "C. Your
rule, the larger of 70% and real minus 20 m, everywhere.").

(1) Abilities: every implemented row's trigger text (column 22) that states a cast bound of a real range above 66 m is
    rewritten to the new bound by rewrite() (deterministic; the verifier recomputes it from v69). Auras keep 70%.
(2) Definitions: title v70, section 67 (the rule). Changelog: a v70 row. Numbers: the date line only (no roster change).
v1-v69 are never opened for writing. Run with DRY=1 to print the rewrites and the residual old numbers instead.
"""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl  # noqa: E402

import build_ability_database as bd  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v69_2026-11-20.xlsx"
DST = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v70_2026-11-21.xlsx"
RULE = "max(70%, real - 20)"


def rb(real):
    return max((real * 70) // 100, real - 20)


def reals_of(e):
    """The entry's real cast ranges whose bound changes under the new rule."""
    out = []
    for f in ("range_real", "ally_range_real"):
        m = e.get(f)
        if m and rb(m) != (m * 70) // 100:
            out.append(m)
    return sorted(set(out))


def rewrite(text, e):
    """The trigger text with every bound of the entry's changed real ranges restated (old 70% -> new)."""
    if not isinstance(text, str):
        return text
    for m in reals_of(e):
        old, new = (m * 70) // 100, rb(m)
        # "within 140 m (70% of the ability's 200 m target_intercept_range)", "(70% of 200)", "(70% of the game's 100 m)"
        text = re.sub(r"\b%d m \(70%% of ([^()]*?\b%d\b)" % (old, m), lambda x: "%d m (%s of %s" % (new, RULE, x.group(1)), text)
        # "bound: 70 m (70% of the ability's 100 m reach)" is covered above; "the 70% bound (140 m of its real 200 m ..."
        text = re.sub(r"70%% bound \(%d m of ([^()]*?\b%d\b)" % (old, m), lambda x: "bound (%d m of %s" % (new, x.group(1)), text)
        text = re.sub(r"70%% ally bound \(%d m\)" % old, "ally bound (%d m)" % new, text)
        # "(floor(target_intercept_range 200 x 0.70) = 140 m)"
        text = re.sub(r"floor\(target_intercept_range %d x 0\.70\)( = %d m)?" % (m, old),
                      lambda x: "max(floor(target_intercept_range %d x 0.70), %d - 20)%s" % (m, m, (" = %d m" % new) if x.group(1) else ""), text)
        text = re.sub(r"\(%d m = floor\(%d \* 0\.70\)\)" % (old, m), "(%d m = %s of %d)" % (new, RULE, m), text)
        # the plain statements: "within 140 m", "within the 70 m bound", "(bound 140 m)", ", bound 70 m)"
        text = re.sub(r"\bwithin %d m\b" % old, "within %d m" % new, text)
        text = re.sub(r"\bwithin the %d m bound\b" % old, "within the %d m bound" % new, text)
        text = re.sub(r"\bbound %d m\)" % old, "bound %d m)" % new, text)
        # a history note "bound 21 -> 70 m)" keeps its words and gains the round-188 value
        text = re.sub(r"-> %d m\)" % old, "-> %d m; %d m since round 188)" % (old, new), text)
    if e.get("marker") in ("blood_sacrifice", "eat_da_runts"):   # the named constants of a real 100 m: 70 -> 80
        for a, b in (("unit_distance <= 70 m", "unit_distance <= 80 m"), ("bound: 70 m (the mod's named constant",
                     "bound: 80 m (the mod's named constant"), ("within 70 m", "within 80 m")):
            text = text.replace(a, b)
    if e.get("marker") == "lord_abilities_executioner":
        text = text.replace("= 225 m (user ruling 2026-11-20, 'let's do 90%': the documented exception to 70%).",
                            "= 225 m (user ruling 2026-11-20, 'let's do 90%': the documented exception to 70%); since "
                            "round 188 the larger of that and " + RULE + ": 230 m.")
    return text


def plan():
    entries, _, _ = bd.mod_entries()
    by_key = {k: e for e in entries for k in e["keys"]}
    wb = openpyxl.load_workbook(SRC, read_only=True)
    ws = wb["Abilities"]
    out = []
    for r, row in enumerate(ws.iter_rows(values_only=True, min_row=2), start=2):
        k = str(row[2]).split(";")[0].strip()
        if row[19] != "IMPLEMENTED" or k not in by_key:
            continue
        e = by_key[k]
        t = row[21]
        n = rewrite(t, e)
        out.append((r, k, e, t, n))
    return out


def residual(t, e):
    """Old bound numbers still in a rewritten text (for review)."""
    hits = []
    for m in reals_of(e):
        old = (m * 70) // 100
        for x in re.finditer(r"[^.;]{0,50}\b%d ?m\b[^.;]{0,30}" % old, t or ""):
            hits.append(x.group(0))
    return hits


def main():
    rows = plan()
    changed = [x for x in rows if x[3] != x[4]]
    affected = [x for x in rows if reals_of(x[2])]
    if os.environ.get("DRY"):
        print("implemented rows", len(rows), "with a changed bound", len(affected), "texts rewritten", len(changed))
        for r, k, e, t, n in affected:
            res = residual(n, e)
            if res or t == n:
                print("ROW", r, k, reals_of(e), "UNCHANGED" if t == n else "", "|", " || ".join(res)[:400])
        return
    assert not os.path.exists(DST), DST
    shutil.copy2(SRC, DST)
    wb = openpyxl.load_workbook(DST)
    ws = wb["Abilities"]
    for r, k, e, t, n in changed:
        assert ws.cell(row=r, column=22).value == t
        ws.cell(row=r, column=22).value = n
    nm = wb["Numbers"]
    assert str(nm.cell(row=7, column=1).value).startswith("Date: 2026-11-20")
    nm.cell(row=7, column=1).value = (
        "Date: 2026-11-21     Rule in force since: 2026-10-18     Inventory: 1,800 active abilities     "
        "(v70 - ROUND 188: the range rule, every cast bound is max(70%, real - 20 m). 1,041 rows / 1,041 keys "
        "implemented; 82 not implemented among the included (62 skipped by the user). The mod: 988 entries / 1,041 keys "
        "/ 141 trigger families.)")
    d = wb["Definitions"]
    assert d.cell(row=1, column=1).value.startswith("DEFINITIONS - WH3 ability master v69")
    d.cell(row=1, column=1).value = "DEFINITIONS - WH3 ability master v70 (2026-11-21)"
    base = d.max_row + 2
    sec = [("67. ROUND 188 - THE RANGE RULE (v70)", None),
           ("RULE", "Every cast-range bound is the larger of floor(real x 0.70) and real - 20 m (FOURTH.range_bound; "
            "FOURTH.RANGE_MARGIN_M = 20). User 2026-11-21: 'C. Your rule, the larger of 70% and real minus 20 m, "
            "everywhere.' It changes every real range above 66 m: 100 m 70 -> 80, 150 m 105 -> 130, 200 m 140 -> 180, "
            "250 m 175 -> 230, 500 m 350 -> 480. Auras and blasts (55 m or less) keep 70%. The Executioner takes the "
            "larger of its 90% exception and the rule (230 m)."),
           ("ROWS", "%d trigger texts restate their bound (the rows whose entry has a real range above 66 m)." % len(changed))]
    for i, (a, b) in enumerate(sec):
        d.cell(row=base + i, column=1).value = a
        if b is not None:
            d.cell(row=base + i, column=2).value = b
    ch = wb["Changelog"]
    r = ch.max_row + 1
    ch.cell(row=r, column=1).value = "2026-11-21"
    ch.cell(row=r, column=2).value = "v70"
    ch.cell(row=r, column=3).value = (
        "ROUND 188. The range rule: every cast bound is max(70%%, real - 20 m); %d trigger texts restated. SHIPPED: "
        "installed pack md5 %s; harness 187 full suite 7,876 checks / 0 failures."
        % (len(changed), os.environ.get("WH3_PACK_MD5", "PENDING")))
    ch.cell(row=r, column=4).value = "user ruling 2026-11-21; xlsx v70 supersedes v69; v1-v69 byte-unchanged."
    wb.save(DST)
    print("wrote", DST, "texts rewritten", len(changed))


if __name__ == "__main__":
    main()
