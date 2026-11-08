# -*- coding: utf-8 -*-
"""ROUND h98 - derive the Class-B list PROGRAMMATICALLY and join it to the mod
table and unit_spec_abil.tsv.

Class B = the 'Ally-targeted effects cast on self' section of WH3_audit_report.md
(34 entries). For each entry we record:
  * num / name / keys (parsed from the report block - never hand-typed);
  * range_real = the ability's REAL target_intercept_range from
    unit_spec_abil.tsv (per key; the FIRST key with a non-zero intercept), and
    the report's own stated intercept as a cross-check;
  * the mod marker(s) that carry the entry's keys;
  * the current mod trigger(s);
  * army-bar membership: the report's own wording OR the key family
    'army_abilities' (the standing rule-10 skip).
Writes _classB_parsed.json and _classB_joined.json.
"""
import io, os, re, json
from collections import Counter, defaultdict

ROOT = "C:/Users/vlady/Desktop"
AUDIT = ROOT + "/WH3_audit"
TSV = ROOT + "/WH3_project_archive/research/wh3/unit_spec_abil.tsv"
MOD = ROOT + "/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"

# ------------------------------------------------------------------ parse report
lines = io.open(ROOT + "/WH3_audit_report.md", encoding="utf-8").read().split("\n")
start = next(i for i, l in enumerate(lines) if l.startswith("## Class B"))
end = next(i for i, l in enumerate(lines) if l.startswith("## Class C"))
sec = lines[start:end]
blocks = []; cur = None
for l in sec:
    m = re.match(r"^####\s+(\d+)\.\s+(.*?)\s{0,3}\(slice\s+\d+\)\s*$", l)
    if m:
        if cur: blocks.append(cur)
        cur = {"num": int(m.group(1)), "name": m.group(2).strip(), "text": []}
    elif cur is not None:
        cur["text"].append(l)
if cur: blocks.append(cur)
print("Class-B entries parsed:", len(blocks))

def getkeys(t):
    ks = []
    for l in t:
        if l.startswith("- **Key(s):**") or l.startswith("- **Keys:**"):
            ks += re.findall(r"`([^`]+)`", l)
    return ks

recs = []
for b in blocks:
    t = b["text"]; txt = "\n".join(t)
    ks = getkeys(t)
    m = re.search(r"intercept\s+([\d.]+)\s*m", txt)
    if m is None:
        m = re.search(r"cast range\s+([\d.]+)\s*m", txt)
    if m is None:
        m = re.search(r"range\s+([\d.]+)\s*m", txt)
    if m is None:
        m = re.search(r"within\s+([\d.]+)\s*m", txt)
    intercept = float(m.group(1)) if m else None
    army = bool(re.search(r"army[- ](?:bar|keyed|abilit)", txt, re.I))
    recs.append({"num": b["num"], "name": b["name"], "keys": ks,
                 "intercept": intercept, "army_text": army, "text": txt})
print("with keys:", sum(1 for r in recs if r["keys"]), "no keys:", [r["num"] for r in recs if not r["keys"]])
print("blocks flagged army by the report's own wording:",
      [(r["num"], r["name"]) for r in recs if r["army_text"]])

# ------------------------------------------------------------------ TSV
rows = io.open(TSV, encoding="utf-8").read().split("\n")
hdr = rows[0].split("\t"); idx = {h: i for i, h in enumerate(hdr)}
tsv = {}
for r in rows[1:]:
    if not r.strip(): continue
    c = r.split("\t")
    if len(c) <= idx["target_intercept_range"]: continue
    def g(f, c=c):
        i = idx[f]; return c[i] if i < len(c) else ""
    tsv[c[0]] = {"intercept": g("target_intercept_range"), "effect": g("effect_range"),
                 "ground": g("target_ground"), "enemies": g("target_enemies"),
                 "friends": g("target_friends"), "self": g("target_self"),
                 "affect_self": g("affect_self"), "always_self": g("always_affect_self"),
                 "num_fr": g("num_effected_friendly_units"), "num_en": g("num_effected_enemy_units"),
                 "only_target": g("only_affect_target")}
print("TSV keys:", len(tsv))

# ------------------------------------------------------------------ mod entries
modtxt = io.open(MOD, encoding="utf-8").read()
ent_re = re.compile(r'\{\s*marker\s*=\s*"([^"]+)"\s*,\s*name\s*=\s*"((?:[^"\\]|\\.)*)"\s*,\s*trigger\s*=\s*"([^"]+)"\s*,\s*\n\s*badge\s*=\s*"([^"]*)"\s*,\s*\n\s*keys\s*=\s*\{([^}]*)\}', re.S)
mod_entries = []
for m in ent_re.finditer(modtxt):
    keys = re.findall(r'"([^"]+)"', m.group(5))
    mod_entries.append({"marker": m.group(1), "name": m.group(2),
                        "trigger": m.group(3), "keys": keys})
print("mod entries parsed:", len(mod_entries), "| trigger counts:", dict(Counter(e["trigger"] for e in mod_entries)))
key2me = defaultdict(list)
for e in mod_entries:
    for k in e["keys"]:
        key2me[k].append(e)

# ------------------------------------------------------------------ join
out = []; unmapped = []
for r in recs:
    keys = r["keys"]
    tkeys = [tsv.get(k) for k in keys]
    missing_tsv = [k for k, t in zip(keys, tkeys) if t is None]
    # real range from the TSV (authority), first key with a non-zero intercept
    range_real = None; src = None
    for t, k in zip(tkeys, keys):
        if t and t["intercept"] not in ("", "0.0000"):
            range_real = float(t["intercept"]); src = "tsv:" + k; break
    if range_real is None:
        for t, k in zip(tkeys, keys):
            if t and t["intercept"] != "":
                range_real = float(t["intercept"]); src = "tsv0:" + k; break
    if range_real is None and r["intercept"] is not None:
        range_real = r["intercept"]; src = "report"
    bound = None if range_real is None else int(range_real * 0.70 + 1e-9)
    # mod markers
    mes = {}
    for k in keys:
        for e in key2me.get(k, []):
            mes[e["marker"]] = e
    if not mes:
        unmapped.append({"num": r["num"], "name": r["name"], "keys": keys})
    # army-bar membership: key family 'army_abilities' OR a key that the project's
    # own grouped classification grades 'army' (army-scope ability) OR the report.
    army_key = any("army_abilities" in k for k in keys)
    army_grouped = False
    try:
        _g = json.load(io.open(ROOT + "/WH3_project_archive/research/wh3/grouped.json", encoding="utf-8"))
        _gi = {e[0]: e for e in _g}
        army_grouped = any((_gi.get(k) is not None and len(_gi[k]) > 3 and _gi[k][3] == "army") for k in keys)
    except Exception:
        pass
    out.append({"num": r["num"], "name": r["name"], "keys": keys,
                "range_real": range_real, "rsrc": src, "bound": bound,
                "report_intercept": r["intercept"], "army_text": r["army_text"],
                "army_key": army_key, "army_grouped": army_grouped,
                "mod_markers": list(mes.keys()),
                "mod_triggers": sorted(set(e["trigger"] for e in mes.values())),
                "missing_tsv": missing_tsv,
                "tsv": {k: tkeys[i] for i, k in enumerate(keys)}})

json.dump(recs, io.open(AUDIT + "/_classB_parsed.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(out, io.open(AUDIT + "/_classB_joined.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("\n== range_real source:", dict(Counter(o["rsrc"].split(":")[0] for o in out)))
print("== range_real still None:", [(o["num"], o["name"], o["keys"]) for o in out if o["range_real"] is None])
print("== bound distribution:", dict(sorted(Counter(o["bound"] for o in out).items(), key=lambda x: (x[0] is None, x[0]))))
print("== entries with NO mod marker (UNMAPPED):", [(o["num"], o["name"], o["keys"]) for o in out if not o["mod_markers"]])
print("== entries missing a TSV key:", [(o["num"], o["name"], o["missing_tsv"]) for o in out if o["missing_tsv"]])
print("== army-bar by KEY FAMILY:", [(o["num"], o["name"], o["keys"]) for o in out if o["army_key"]])
print("== army-bar by REPORT wording:", [(o["num"], o["name"]) for o in out if o["army_text"]])
print("== mod trigger sets:", dict(Counter(tuple(o["mod_triggers"]) for o in out)))
print("\n== per entry ==")
for o in out:
    print("%4d %-34s real=%-7s bound=%-5s trig=%-22s army=%s/%s markers=%s%s"
          % (o["num"], o["name"][:34], o["range_real"], o["bound"],
             ",".join(o["mod_triggers"]) or "-", o["army_key"], o["army_text"],
             ",".join(o["mod_markers"]) or "NONE",
             ("  missTSV=" + str(o["missing_tsv"])) if o["missing_tsv"] else ""))
print("\nwrote _classB_parsed.json / _classB_joined.json")
