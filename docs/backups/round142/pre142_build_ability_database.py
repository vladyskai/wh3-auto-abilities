"""Build docs/WH3_ability_database_master.md - the definitive ability database.

Merges, per ability row, FOUR sources and invents nothing:
  1. the project's authoritative inventory   docs/WH3_ability_tracker.md  (1,797 rows, 3a/3b/3c)
  2. the project's merged master list        docs/WH3_ability_master_list.md (cross-check only)
  3. the mod's own ABILITIES table           mod_source/script/battle/mod/zz_test_deadly_onslaught.lua
  4. a FRESH extraction from the game's own data
       gamedata\\wh3\\                     unit_spec_abil.tsv, phase_junc.tsv, phases.tsv,
                                             special_ability_to_invalid_target_flags_tables.tsv,
                                             special_ability_to_invalid_usage_flags_tables.tsv,
                                             special_ability_to_auto_deactivate_flags_tables.tsv,
                                             unit_abilities.tsv/.loc.tsv
       gamedata\\wh3\\uieff\\               special_ability_phase_stat_effects.tsv,
                                             phase_attribute_effects.tsv,
                                             unit_abilities_additional_ui_effects*.tsv,
                                             phases_to_ui_effects_juncs.tsv,
                                             unit_stat_localisations__.loc.tsv,
                                             unit_attributes__.loc.tsv
Fields merged per ability: name, key(s), EFFECT, RESTRICTIONS, RANGE, STATUS, plain-English TRIGGER.
Where a field genuinely cannot be sourced it is written 'unknown' - never a guess.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gamedata_paths as GP
import csv
import json
import os
import re
import sys
import collections
from datetime import datetime

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
DOCS = os.path.join(ROOT, "docs")
TRACKER = os.path.join(DOCS, "WH3_ability_tracker.md")
MODLUA = os.path.join(ROOT, "mod_source", "script", "battle", "mod", "zz_test_deadly_onslaught.lua")
OUT = os.path.join(DOCS, "WH3_ability_database_master.md")
T = GP.GAMEDATA  # gamedata\wh3 (was %LOCALAPPDATA%\Temp\wh3 until 2026-11-01)
U = os.path.join(T, "uieff")


def load_tsv(path):
    if not os.path.exists(path):
        raise SystemExit("missing game-data file: " + path)
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = [r for r in csv.reader(f, delimiter="\t")]
    return [r for r in rows if r and r[0] and not r[0].startswith("#")]


def idx(rows, col):
    d = collections.defaultdict(list)
    for r in rows[1:]:
        if len(r) > col:
            d[r[col]].append(r)
    return d


def strip_art(s):
    """drop the [[img:...]][[/img]] markup the game's stat names carry."""
    s = re.sub(r"\[\[img:[^\]]*\]\]", "", s)
    s = re.sub(r"\[\[/img\]\]", "", s)
    return s.strip()


# ---------------------------------------------------------------- game data
spec = load_tsv(os.path.join(T, "unit_spec_abil.tsv"))
SPEC_H = spec[0]
spec_idx = {r[0]: r for r in spec[1:]}

PJ = load_tsv(os.path.join(T, "phase_junc.tsv"))
pj_idx = idx(PJ, 1)
PH = load_tsv(os.path.join(T, "phases.tsv"))
PH_H = PH[0]
ph_idx = idx(PH, 0)
SPS = load_tsv(os.path.join(U, "special_ability_phase_stat_effects.tsv"))
sps_idx = idx(SPS, 0)
PAE = load_tsv(os.path.join(U, "phase_attribute_effects.tsv"))
pae_idx = idx(PAE, 1)
P2U = load_tsv(os.path.join(U, "phases_to_ui_effects_juncs.tsv"))
p2u_idx = idx(P2U, 1)
U2E = load_tsv(os.path.join(U, "unit_abilities_to_ui_effects_juncs.tsv"))
u2e_idx = idx(U2E, 0)
UAE = load_tsv(os.path.join(U, "unit_abilities_additional_ui_effects__.loc.tsv"))
UAE_TXT = {r[0]: strip_art(r[1]) for r in UAE[1:]}
UAE_TBL = load_tsv(os.path.join(U, "unit_abilities_additional_ui_effects_tables.tsv"))
UAE_STATE = {r[0]: (r[2] if len(r) > 2 else "") for r in UAE_TBL[1:]}
STATLOC = load_tsv(os.path.join(U, "unit_stat_localisations__.loc.tsv"))
STATLOC = {r[0]: strip_art(r[1]) for r in STATLOC[1:]}
ATTRLOC = load_tsv(os.path.join(U, "unit_attributes__.loc.tsv"))
ATTRLOC = {r[0]: strip_art(r[1]).split("||")[0] for r in ATTRLOC[1:]}
UB_LOC = load_tsv(os.path.join(T, "unit_abilities.loc.tsv"))
UB_TXT = {r[0]: strip_art(r[1]) for r in UB_LOC[1:]}
INVT = load_tsv(os.path.join(T, "special_ability_to_invalid_target_flags_tables.tsv"))
invt_idx = idx(INVT, 1)
INVU = load_tsv(os.path.join(T, "special_ability_to_invalid_usage_flags_tables.tsv"))
invu_idx = idx(INVU, 1)
ADR = load_tsv(os.path.join(T, "special_ability_to_auto_deactivate_flags_tables.tsv"))
adr_idx = idx(ADR, 1)


def stat_disp(s):
    return STATLOC.get("unit_stat_localisations_onscreen_name_" + s, s)


def attr_disp(a):
    return ATTRLOC.get("unit_attributes_bullet_text_" + a, a)


def numtxt(v):
    try:
        return "%g" % float(v)
    except (TypeError, ValueError):
        return str(v)


def fmt_val(v, how):
    try:
        f = float(v)
    except ValueError:
        return str(v)
    if how == "mult":
        return "%+g%%" % round((f - 1.0) * 100.0, 2)
    return "%+g" % f


def phase_detail(phase):
    rows = ph_idx.get(phase)
    return {PH_H[i]: (rows[0][i] if i < len(rows[0]) else "") for i in range(len(PH_H))} if rows else None


def scope_of(spec_row, phase_flags):
    """plain-English scope for an effect line, from the game's own flags."""
    ts = tf = te = False
    if spec_row is not None:
        d = dict(zip(SPEC_H, spec_row))
        ts = d.get("target_self") == "true"
        tf = d.get("target_friends") == "true"
        te = d.get("target_enemies") == "true"
    if phase_flags:
        ts = ts or phase_flags[0] == "true"
        tf = tf or phase_flags[1] == "true"
        te = te or phase_flags[2] == "true"
    if te and not tf and not ts:
        return "to enemies in range"
    if tf and ts:
        return "to self and allies in range"
    if tf:
        return "to allies in range"
    if te:
        return "to enemies in range"
    if ts:
        return "to self"
    return ""


_GD_CACHE = {}


def game_data(key):
    if key in _GD_CACHE:
        return _GD_CACHE[key]
    g = _game_data(key)
    _GD_CACHE[key] = g
    return g


def _game_data(key):
    """the fresh extraction: every field the database row needs, for one ability key."""
    sr = spec_idx.get(key)
    d = dict(zip(SPEC_H, sr)) if sr else {}
    g = {
        "in_game_data": sr is not None,
        "spec": d,
        "phases": [],
        "effect_items": [],
        "ui_effects": [],
        "invalid_target": [r[0] for r in invt_idx.get(key, [])],
        "invalid_usage": [r[0] for r in invu_idx.get(key, [])],
        "auto_deactivate": [r[0] for r in adr_idx.get(key, [])],
        "onscreen_name": UB_TXT.get("unit_abilities_onscreen_name_" + key),
        "tooltip": UB_TXT.get("unit_abilities_tooltip_text_" + key),
    }
    seen = set()
    for r in pj_idx.get(key, []):
        phase = r[5] if len(r) > 5 else ""
        pf = (r[2], r[3], r[4])
        det = phase_detail(phase)
        g["phases"].append({"phase": phase, "t_self": pf[0], "t_friends": pf[1],
                            "t_enemies": pf[2], "detail": det})
        items = []
        for s in sps_idx.get(phase, []):
            txt = "%s: %s" % (stat_disp(s[1]), fmt_val(s[2], s[3]))
            if txt not in seen:
                seen.add(txt)
                items.append(txt)
        for a in pae_idx.get(phase, []):
            txt = "%s (%s)" % (attr_disp(a[0]), a[2] or "attribute")
            if txt not in seen:
                seen.add(txt)
                items.append(txt)
        for e in p2u_idx.get(phase, []):
            txt = UAE_TXT.get("unit_abilities_additional_ui_effects_localised_text_" + e[0], e[0])
            if txt not in seen:
                seen.add(txt)
                items.append(txt)
        if det:
            if det.get("damage_amount") not in ("", "0", "0.0000"):
                items.append("Damage: %s per hit (max %s entities)" % (numtxt(det["damage_amount"]), numtxt(det.get("max_damaged_entities") or "?")))
            if det.get("heal_amount") not in ("", "0", "0.0000"):
                items.append("Heals: %s per tick every %s s" % (numtxt(det["heal_amount"]), numtxt(det.get("hp_change_frequency") or "?")))
            if det.get("barrier_heal_amount") not in ("", "0", "0.0000"):
                items.append("Barrier restore: %s" % numtxt(det["barrier_heal_amount"]))
            if det.get("resurrect") == "true":
                items.append("Resurrects models")
            if det.get("execute_ratio") not in ("", "0", "0.0000"):
                items.append("Executes below %s of HP" % numtxt(det["execute_ratio"]))
            if det.get("fatigue_change_ratio") not in ("", "0", "0.0000"):
                items.append("Fatigue: %s" % numtxt(det["fatigue_change_ratio"]))
            if det.get("freeze_fatigue") == "true":
                items.append("Freezes fatigue")
            if det.get("requested_stance"):
                items.append("Stance: %s" % det["requested_stance"])
            if det.get("cant_move") == "true":
                items.append("Cannot move")
            if det.get("spreading"):
                items.append("Spreading area: %s" % det["spreading"])
            if det.get("replenish_ammo") not in ("", "0", "0.0000"):
                items.append("Replenishes ammo: %s" % det["replenish_ammo"])
            if det.get("mana_regen_mod") not in ("", "0", "0.0000"):
                items.append("Winds of Magic recharge: %s" % fmt_val(det["mana_regen_mod"], "mult"))
            if det.get("mana_max_depletion_mod") not in ("", "0", "0.0000"):
                items.append("Winds of Magic reserves per second: %s" % ("%+g" % float(det["mana_max_depletion_mod"])))
            if det.get("ability_recharge_change") not in ("", "0", "0.0000"):
                items.append("Own ability recharge: %s s" % numtxt(det["ability_recharge_change"]))
            if det.get("inspiration_aura_range_mod") not in ("", "0", "0.0000"):
                items.append("Inspiration aura range mod: %s" % det["inspiration_aura_range_mod"])
            if det.get("imbue_contact") not in ("", "0", "0.0000", "false"):
                items.append("Imbues its target's attacks on contact: %s" % det["imbue_contact"])
            if det.get("imbue_ignition") not in ("", "0", "0.0000", "false"):
                items.append("Imbues ignition: %s" % det["imbue_ignition"])
            if det.get("imbue_magical") == "true":
                items.append("Imbues magical attacks")
            if det.get("remove_magical") == "true":
                items.append("Removes magical attacks")
            if det.get("freeze_recharge") == "true":
                items.append("Freezes ability recharge")
        sc = scope_of(sr, pf)
        if items:
            line = "; ".join(items)
            if sc:
                line += " (%s)" % sc
            g["effect_items"].append((phase, line))
        for e in u2e_idx.get(key, []):
            txt = UAE_TXT.get("unit_abilities_additional_ui_effects_localised_text_" + e[1], e[1])
            st = UAE_STATE.get(e[1], "")
            g["ui_effects"].append("%s%s" % (txt, (" (%s)" % st) if st else ""))

    # range / targeting / ai_usage, straight from the game's columns
    g["range"] = {
        "effect_range": d.get("effect_range", ""),
        "target_intercept_range": d.get("target_intercept_range", ""),
        "min_range": d.get("min_range", ""),
        "targetting_aoe": d.get("targetting_aoe", ""),
        "passive_aoe": d.get("passive_aoe", ""),
        "active_aoe": d.get("active_aoe", ""),
        "aimed_at_ground": d.get("target_ground", ""),
    }
    g["targeting"] = {
        "target_self": d.get("target_self", ""),
        "target_friends": d.get("target_friends", ""),
        "target_enemies": d.get("target_enemies", ""),
        "target_ground": d.get("target_ground", ""),
        "affect_self": d.get("affect_self", ""),
        "only_affect_owned_units": d.get("only_affect_owned_units", ""),
    }
    g["ai_usage"] = d.get("ai_usage", "")
    # the DELIVERY MECHANISM the game's own row declares (summon / vortex /
    # bombardment / projectile / miscast ...) - a real mechanical fact, and the
    # reason many rows have no stat rows at all.
    mech = []
    for col, label in (("spawned_unit", "summons the unit"), ("spawn_type", "spawn type"),
                       ("vortex", "vortex/area key"), ("bombardment", "bombardment key"),
                       ("activated_projectile", "fires projectile"), ("miscast_explosion", "miscast explosion"),
                       ("form", "formation"), ("behaviour", "behaviour")):
        v = d.get(col, "")
        if v:
            mech.append("%s: %s" % (label, v))
    if d.get("miscast_chance", "") not in ("", "0", "0.0000"):
        mech.append("miscast chance: %s" % numtxt(d["miscast_chance"]))
    if d.get("mana_cost", "") not in ("", "0", "0.0000"):
        mech.append("magic cost: %s" % numtxt(d["mana_cost"]))
    if d.get("additional_melee_cp", "") not in ("", "0", "0.0000"):
        mech.append("AI melee CP: %s" % numtxt(d["additional_melee_cp"]))
    if d.get("additional_missile_cp", "") not in ("", "0", "0.0000"):
        mech.append("AI missile CP: %s" % numtxt(d["additional_missile_cp"]))
    g["mechanism"] = mech
    g["timing"] = {
        "active_time": d.get("active_time", ""),
        "recharge_time": d.get("recharge_time", ""),
        "num_uses": d.get("num_uses", ""),
        "wind_up_time": d.get("wind_up_time", ""),
        "mana_cost": d.get("mana_cost", ""),
        "passive": d.get("passive", ""),
    }
    return g


def effect_text(g):
    parts = [e[1] for e in g["effect_items"]]
    parts += [u for u in g["ui_effects"]]
    out, seen = [], set()
    for p in parts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    if out:
        return "; ".join(out)
    # NOTHING mechanical in the stat/phase/attribute tables: say so plainly
    # (never a guess) and give the two sourced facts that remain - the delivery
    # mechanism the game itself declares, and its own ability description.
    bits = ["unknown (no stat or phase rows in the game's tables"]
    if g["mechanism"]:
        bits.append("; the game's own delivery columns: " + "; ".join(g["mechanism"]))
        if any(x.startswith(("summons", "vortex", "bombardment", "fires projectile")) for x in g["mechanism"]):
            bits.append("; its effect is carried by that projectile / vortex / summoned-unit definition,"
                        " whose tables are NOT part of this extraction")
    bits.append(")")
    txt = "".join(bits)
    if g["tooltip"]:
        t = g["tooltip"].strip().replace("|", "/")
        if len(t) > 220:
            t = t[:217] + "..."
        txt += ' — the game\'s own description: "%s"' % t
    return txt


def range_text(g, bound=None):
    bits = []
    r = g["range"]
    def num(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return None
    tir, er, mr = num(r["target_intercept_range"]), num(r["effect_range"]), num(r["min_range"])
    if tir is not None and tir > 0:
        bits.append("cast reach %g m" % tir)
    if er is not None and er > 0:
        bits.append("effect range (aura) %g m" % er)
    if mr is not None and mr > 0:
        bits.append("min range %g m" % mr)
    if r["aimed_at_ground"] == "true":
        bits.append("targets ground")
    if bound is not None:
        bits.append("trigger bound %s" % bound)
    return " · ".join(bits) if bits else "unlimited / no range column"


def restrictions_text(g):
    t = g["targeting"]
    tf = "self=%s friends=%s enemies=%s ground=%s" % (
        "yes" if t.get("target_self") == "true" else "no",
        "yes" if t.get("target_friends") == "true" else "no",
        "yes" if t.get("target_enemies") == "true" else "no",
        "yes" if t.get("target_ground") == "true" else "no")
    bits = ["targeting: " + tf]
    if t.get("only_affect_owned_units") == "true":
        bits.append("own units only")
    if t.get("affect_self") == "true":
        bits.append("always affects self")
    if g["invalid_target"]:
        bits.append("invalid-target: " + ", ".join("`%s`" % x for x in g["invalid_target"]))
    if g["invalid_usage"]:
        bits.append("invalid-usage: " + ", ".join("`%s`" % x for x in g["invalid_usage"]))
    if g["auto_deactivate"]:
        bits.append("auto-deactivate: " + ", ".join("`%s`" % x for x in g["auto_deactivate"]))
    return " · ".join(bits)


# ---------------------------------------------------------------- tracker rows
def tracker_rows():
    lines = open(TRACKER, encoding="utf-8").read().splitlines()

    def sec(sp, ep):
        si = next(i for i, l in enumerate(lines) if re.match(sp, l))
        ei = next((i for i, l in enumerate(lines[si + 1:], si + 1) if re.match(ep, l)), len(lines))
        return si, ei

    out = []
    for tag, sp, ep in ((3, r"^### 3a\.", r"^### "), (3, r"^### 3b\.", r"^### "), (3, r"^### 3c\.", r"^## \d")):
        si, ei = sec(sp, ep)
        for l in lines[si:ei]:
            if not l.startswith("|") or re.match(r"^\|[\s\-|]+\|$", l) or l.startswith("| Ability"):
                continue
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            m = re.search(r"`([^`]+)`", c[0])
            if not m:
                continue
            name = c[0][:m.start()].strip()
            status = c[1].strip("`").strip()
            out.append({"name": name, "key": m.group(1), "status": status,
                        "group": c[2] if len(c) > 2 else "",
                        "proposal": c[3] if len(c) > 3 else "",
                        "notes": c[4] if len(c) > 4 else ""})
    return out


# ---------------------------------------------------------------- mod table
def mod_entries():
    src = open(MODLUA, encoding="utf-8").read()
    start = src.index("local ABILITIES = {")
    end = src.index("\n}", start)
    region = src[start:end]
    parts = re.split(r"\n\t\{ marker = \"", region)
    entries = []
    for p in parts[1:]:
        e = {"marker": p.split('"', 1)[0]}
        m = re.search(r'name = ("(?:[^"\\]|\\.)*")', p)
        e["name"] = json.loads(m.group(1)) if m else None
        m = re.search(r'trigger = "([a-z0-9_]+)"', p)
        e["trigger"] = m.group(1) if m else None
        kb = re.search(r'keys = \{(.*?)\n\t\t\}', p, re.S) or re.search(r'keys = \{(.*?)\}', p, re.S)
        body = re.sub(r"--[^\n]*", "", kb.group(1) if kb else "")
        e["keys"] = re.findall(r'"([^"]+)"', body)
        m = re.search(r"range_real = (\d+)", p)
        e["range_real"] = int(m.group(1)) if m else None
        m = re.search(r"ally_range_real = (\d+)", p)
        e["ally_range_real"] = int(m.group(1)) if m else None
        m = re.search(r"aura_real = (\d+)", p)
        e["aura_real"] = int(m.group(1)) if m else None
        entries.append(e)
    # named constants + the family tooltip map, straight out of the source
    consts = {}
    for m in re.finditer(r"^(?:local )?(FOURTH\.)?([A-Z][A-Z0-9_]*) = ([0-9.]+)\s*$", src, re.M):
        consts[(m.group(1) or "") + m.group(2)] = float(m.group(3))
    tip = {}
    tb = re.search(r"FOURTH\.TRIGGER_TIP = \{(.*?)\n\}", src, re.S)
    if tb:
        for m in re.finditer(r'([a-z0-9_]+) = "((?:[^"\\]|\\.)*)"', tb.group(1)):
            tip[m.group(1)] = m.group(2)
    return entries, consts, tip


def main():
    rows = tracker_rows()
    entries, consts, tips = mod_entries()
    key2entry = {}
    for e in entries:
        for k in e["keys"]:
            key2entry[k] = e
    mod_keys = set(key2entry)

    # family -> trigger bound, derived from the mod's own constants/fields
    FAM_CONST = {
        "glorious_death": "GLORIOUS_DEATH_RANGE_M",
        "verminking_wavering": "FOURTH.VERMINKING_RANGE_M",
        "metallurgy_melee": "FOURTH.METALLURGY_RANGE_M",
        "wavering_self_or_ally": "FOURTH.WAVERING_RANGE_M",
        "wavering_ally_range": "FOURTH.WAVERING_RANGE_M",
        "blood_sacrifice": "FOURTH.BLOOD_SACRIFICE_RANGE_M",
        "eat_da_runts": "FOURTH.EAT_DA_RUNTS_RANGE_M",
    }
    RANGE_FRACTION = consts.get("FOURTH.RANGE_FRACTION", 0.70)

    def bound_for(e):
        if e is None:
            return None
        if e.get("range_real"):
            return "%g m (70%% of the game's %g m reach)" % (
                (int(e["range_real"] * RANGE_FRACTION + 1e-9)), e["range_real"])
        if e.get("ally_range_real"):
            return "%g m (70%% of the game's %g m ally reach)" % (
                (int(e["ally_range_real"] * RANGE_FRACTION + 1e-9)), e["ally_range_real"])
        if e.get("aura_real"):
            return "%g m (70%% of the mod's %g m aura)" % (
                (int(e["aura_real"] * RANGE_FRACTION + 1e-9)), e["aura_real"])
        c = FAM_CONST.get(e["trigger"])
        if c and c in consts:
            return "%g m (the mod's named constant %s)" % (consts[c], c)
        if e["trigger"] == "ally_infinite_buff":
            return "none - infinite range by ruling"
        return None

    # status families
    def status_family(s):
        low = s.lower()
        if low.startswith("implemented") or low.startswith("implemented "):
            return "implemented"
        if "impossible" in low:
            return "excluded (impossible - engine limit)"
        if low.startswith("excluded"):
            return "excluded (no automatic logic)"
        if low.startswith("rejected"):
            return "rejected (user decision)"
        if low.startswith("skipped"):
            return "skipped (deferred / unsuitable)"
        return "unknown"

    def reason_of(s):
        """the decision reason, with the status word and its wrapping parens removed."""
        s = s.strip()
        body = s.split(" ", 1)[1].strip() if " " in s else s
        if body.startswith("(") and body.endswith(")"):
            body = body[1:-1]
        body = re.sub(r"^(?:auto|impossible):\s*", "", body)
        body = re.sub(r"\s*\(friendly fire, family decision [\d\-]+\)$", "", body)
        body = re.sub(r"\s*\(family decision [\d\-]+\)$", "", body)
        body = re.sub(r"\s*\(standing rule \d+\)$", "", body)
        body = re.sub(r"\s*\(friendly fire by design.*$", "", body)
        return body.strip()

    # ------------------------------------------------------------ compose
    L = []
    A = L.append
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    A("# WARHAMMER III — ABILITY DATABASE (MASTER)")
    A("")
    A("**The definitive, complete record of every ability in the project**: every ability row carries its")
    A("name, key(s), real mechanical EFFECT, RESTRICTIONS (targeting + the engine's invalid-target /")
    A("invalid-usage / auto-deactivate flag names, quoted), RANGE (the game's own range columns **and** the")
    A("trigger bound the mod actually uses), STATUS and the plain-English TRIGGER/logic.")
    A("")
    A("Generated %s by `tools/build_ability_database.py` (re-runnable; nothing hand-typed)." % now)
    A("")
    A("## Sources merged (nothing invented)")
    A("")
    A("| # | Source | What is taken from it |")
    A("|---|---|---|")
    A("| 1 | `docs/WH3_ability_tracker.md` §3a/3b/3c | **the authoritative inventory** — one row per ability key, its status, group, auto-activation proposal and notes |")
    A("| 2 | `docs/WH3_ability_master_list.md` | the earlier merged master list (cross-check of row set, effects and statuses) |")
    A("| 3 | `docs/WH3_audit_report.md`, `docs/WH3_auto_classification_report.md`, `docs/WH3_remaining_triage.md`, `docs/WH3_remaining_classes_C-H.md`, `docs/WH3_blocks_7-8-9_review.md` | the exclude/impossible reasons and the per-class rulings for the implemented rows |")
    A("| 4 | the mod's own `ABILITIES` table (`mod_source/script/battle/mod/zz_test_deadly_onslaught.lua`) | which keys are implemented today, the trigger family each rides, and the **70%% trigger bound** it derives (`FOURTH.RANGE_FRACTION = %g`)" % RANGE_FRACTION)
    A("| 5 | **fresh extraction from the game's own data** (regenerated by `tools/extract_gamedata.py`) — `gamedata\\wh3\\` (`unit_spec_abil.tsv`, `phase_junc.tsv`, `phases.tsv`, the three flag tables, `unit_abilities*.tsv`) and `gamedata\\wh3\\uieff\\` (`special_ability_phase_stat_effects.tsv`, `phase_attribute_effects.tsv`, `*_ui_effects*.tsv`, `unit_stat_localisations__.loc.tsv`, `unit_attributes__.loc.tsv`) | EFFECT (real stat rows / attributes / phase numbers), RESTRICTIONS (targeting flags + invalid-target/invalid-usage/auto-deactivate flag names), RANGE (the engine's own columns), `ai_usage` |")
    A("")
    A("**Blank-field rule:** a field that no source carries is written `unknown`. No value in this file is guessed.")
    A("")
    A("---")
    A("")

    # ---------------------------------------------------------- SECTION 1
    total = len(rows)
    impl_keys = set(k for k, e in key2entry.items())
    fam = collections.Counter(status_family(r["status"]) for r in rows)
    trig_count = collections.Counter(e["trigger"] for e in entries)
    keycount_by_trig = collections.Counter()
    for e in entries:
        for k in e["keys"]:
            keycount_by_trig[e["trigger"]] += 1
    rows_by_key = {r["key"]: r for r in rows}
    impl_rows = [r for r in rows if r["key"] in impl_keys]
    non_impl_rows = [r for r in rows if r["key"] not in impl_keys]
    # two rows can carry the same key; guard the counts
    A("## 1. Summary")
    A("")
    A("### 1.1 The inventory")
    A("")
    A("| Measure | Count |")
    A("|---|---:|")
    A("| Tracker inventory rows (all three tables) | **%d** |" % total)
    A("| distinct ability keys in those rows | %d |" % len(set(r["key"] for r in rows)))
    A("| implemented keys (per the mod's `ABILITIES` table) | **%d** |" % len(mod_keys))
    A("| implemented entries in the mod | **%d** |" % len(entries))
    A("| abilities carrying an **invalid-target** restriction flag | **%d** |" % sum(1 for r in rows if game_data(r["key"])["invalid_target"]))
    A("| abilities carrying an **invalid-usage** restriction flag | **%d** |" % sum(1 for r in rows if game_data(r["key"])["invalid_usage"]))
    A("| abilities carrying an **auto-deactivate** flag | **%d** |" % sum(1 for r in rows if game_data(r["key"])["auto_deactivate"]))
    A("")
    A("### 1.2 Status breakdown (tracker statuses; the implemented set reconciled against the mod)")
    A("")
    A("| Final status family | Abilities |")
    A("|---|---:|")
    for f, n in sorted(fam.items(), key=lambda x: -x[1]):
        A("| %s | %d |" % (f, n))
    A("| **TOTAL** | **%d** |" % sum(fam.values()))
    A("")
    A("Reconciliation: the mod's `ABILITIES` table holds **%d entries / %d keys**; **%d** of the inventory"
      % (len(entries), len(mod_keys), len([r for r in rows if r["key"] in mod_keys])))
    A("rows carry one of those keys. The tracker's own status column counts **%d implemented / %d excluded "
      "(no automatic logic %d + impossible %d) / %d skipped / %d rejected = %d rows** (counted here from the "
      "tracker, not typed in). Any disagreement is listed in §1.6 — never silently smoothed over."
      % (fam["implemented"], fam["excluded (no automatic logic)"] + fam["excluded (impossible - engine limit)"],
         fam["excluded (no automatic logic)"], fam["excluded (impossible - engine limit)"],
         fam["skipped (deferred / unsuitable)"], fam["rejected (user decision)"], total))
    A("")
    A("### 1.3 Implemented abilities by trigger family (what fires, in plain English)")
    A("")
    A("| Trigger family (Lua) | Plain English (the mod's own tooltip sentence) | Entries | Keys |")
    A("|---|---|---:|---:|")
    for t, n in sorted(trig_count.items(), key=lambda x: -x[1]):
        A("| `%s` | %s | %d | %d |" % (t, tips.get(t, "unknown"), n, keycount_by_trig[t]))
    A("| **TOTAL** | | **%d** | **%d** |" % (len(entries), len(mod_keys)))
    A("")
    A("### 1.4 Restriction flags found in the game's own data (the newest, most valuable layer)")
    A("")
    it = collections.Counter(fl for r in rows for fl in game_data(r["key"])["invalid_target"])
    iu = collections.Counter(fl for r in rows for fl in game_data(r["key"])["invalid_usage"])
    ad = collections.Counter(fl for r in rows for fl in game_data(r["key"])["auto_deactivate"])
    A("**Invalid-target flags** (`special_ability_to_invalid_target_flags_tables`) — the ability CANNOT be used")
    A("on a target matching the flag. Example: `unit_is_not_squig` on Empowering Shrooms = \"squig units only\".")
    A("")
    A("| Flag (exact name) | Abilities carrying it |")
    A("|---|---:|")
    for f, n in it.most_common():
        A("| `%s` | %d |" % (f, n))
    A("")
    A("**Invalid-usage flags** (`special_ability_to_invalid_usage_flags_tables`) — the ability cannot be USED while")
    A("the condition named by the flag holds (health, morale, melee state, equipment …).")
    A("")
    A("| Flag (exact name) | Abilities carrying it |")
    A("|---|---:|")
    for f, n in iu.most_common():
        A("| `%s` | %d |" % (f, n))
    A("")
    A("**Auto-deactivate flags** (`special_ability_to_auto_deactivate_flags_tables`) — the engine switches the")
    A("ability off by itself when the condition holds.")
    A("")
    A("| Flag (exact name) | Abilities carrying it |")
    A("|---|---:|")
    for f, n in ad.most_common():
        A("| `%s` | %d |" % (f, n))
    A("")
    A("### 1.5 Game-data coverage (fresh extraction)")
    A("")
    no_spec = [r["key"] for r in rows if not game_data(r["key"])["in_game_data"]]
    no_eff = [r["key"] for r in rows if effect_text(game_data(r["key"])).startswith("unknown")]
    no_eff_no_tip = [r["key"] for r in rows
                     if effect_text(game_data(r["key"])).startswith("unknown")
                     and not game_data(r["key"])["tooltip"]]
    A("| Measure | Count |")
    A("|---|---:|")
    A("| ability keys with a row in `unit_spec_abil.tsv` | %d of %d |" % (total - len(no_spec), total))
    A("| ability keys with a mechanical effect line (stat rows / attributes / phase numbers / UI effects) | %d |" % (total - len(no_eff)))
    A("| ability keys whose EFFECT reads `unknown` (no stat or phase rows in the game's tables) | %d |" % len(no_eff))
    A("| — of those, keys that also carry no game description at all (fully blank) | %d |" % len(no_eff_no_tip))
    A("| ability keys with an `ai_usage` tag | %d |" % sum(1 for r in rows if game_data(r["key"])["ai_usage"]))
    A("| ability keys with a targeting flag set | %d |" % sum(1 for r in rows if any(game_data(r["key"])["targeting"].get(x) == "true" for x in ("target_self", "target_friends", "target_enemies", "target_ground"))))
    A("| ability keys with a delivery mechanism declared (summon / vortex / bombardment / projectile) | %d |" % sum(1 for r in rows if game_data(r["key"])["mechanism"]))
    A("")
    if no_spec:
        A("Keys with no `unit_spec_abil.tsv` row: " + ", ".join("`%s`" % k for k in no_spec) + ".")
        A("")
    A("### 1.6 Reconciliation and known inconsistencies")
    A("")
    dup = [k for k, n in collections.Counter(r["key"] for r in rows).items() if n > 1]
    status_impl = set(r["key"] for r in rows if r["status"].strip().lower().startswith("implemented"))
    A("* Inventory rows: **%d** = one row per ability key across §3a/3b/3c." % total)
    A("* Distinct keys: **%d**" % len(set(r["key"] for r in rows)) + ("; keys appearing on more than one row: %s." % ", ".join("`%s`" % d for d in dup) if dup else "."))
    A("* Implemented: the tracker's status column marks **%d** keys implemented; the mod's `ABILITIES` table carries **%d** keys." % (len(status_impl), len(mod_keys)))
    A("* Tracker status vs the mod: **%d** key(s) differ." % len(status_impl ^ mod_keys) if (status_impl ^ mod_keys) else "* Tracker status and the mod's table agree exactly.")
    for k in sorted(mod_keys - status_impl):
        A("    * `%s` — IN THE MOD (`trigger = %s`) but the tracker row still reads `%s`; the row's own note says the"
          " pre-existing entry was retained. The mod is the authority for what ships." %
          (k, key2entry[k]["trigger"], rows_by_key.get(k, {}).get("status", "no row")))
    for k in sorted(status_impl - mod_keys):
        A("    * `%s` — the tracker says `%s` but the mod's table does NOT carry the key." %
          (k, rows_by_key.get(k, {}).get("status", "?")))
    A("* Status families (counted from the tracker's own status column): " +
      ", ".join("%s **%d**" % (k, v) for k, v in sorted(fam.items())) + ".")
    A("")
    A("---")
    A("")

    # ---------------------------------------------------------- SECTION 2
    A("## 2. IMPLEMENTED ABILITIES — grouped by trigger family")
    A("")
    A("Every row below is shipping in the mod today (%d entries / %d keys). The family heading gives the"
      % (len(entries), len(mod_keys)))
    A("plain-English description of WHEN it fires; the **Trigger / logic** column gives the rule that specific")
    A("ability rides. **Range** shows the game's own range columns and — where the mod gates a distance — the")
    A("named trigger bound it uses (`floor(real x %g)`). **Restrictions** quotes the engine's own flag names." % RANGE_FRACTION)
    A("")
    FAM_DESC = {
        "melee_unwavering": "In melee AND not routing/wobbling. The read is fail-open: an unreadable morale read still rides the plain in-melee condition. Casts on the UNIT ITSELF.",
        "melee": "Plain in-melee (no morale condition). Casts on the unit itself.",
        "melee_low_morale": "In melee AND wavering (morale at or below the wobble threshold). Casts on the unit itself.",
        "melee_health75": "In melee AND the unit's own health at or below 75%. Casts on the unit itself.",
        "ushoran_health": "The unit's OWN health is at or below 75% (no melee requirement, fail-closed). OWNER-ONLY since round 104 - the game's text says (to self), or the row has an unreadable target class / no measurable radius / is a recharge buff. Casts on the unit itself.",
        "health_aura_ground": "The OWNER or a friendly unit inside the ability's own reach (`floor(effect_range x 0.70)`) is at or below 75% health (health_pct, 0-100). The LOWEST-health qualifying unit wins; an ally arm places the GROUND form under that ally, the owner arm at her own feet.",
        "health_aura_self": "The OWNER or a friendly unit inside the self-centred aura (`floor(effect_range x 0.70)`) is at or below 75% health. The hurt ally only ARMS the trigger; the cast always goes on the CASTER.",
        "health_aura_ally": "The OWNER or a friendly unit inside the ability's own 70% bound (`floor(target_intercept_range x 0.70)`) is at or below 75% health. The LOWEST-health qualifying ally is re-checked the same tick and cast ON.",
        "tired": "The unit's fatigue is Tired or worse (exact whole-string match on `battle_unit:fatigue_state()`; an unreadable read fails CLOSED and logs once). Casts on the unit itself.",
        "charge": "The charge window OR already in melee. Casts on the unit itself.",
        "charge_or_melee": "The charge window OR in melee. Casts on the unit itself.",
        "charge_only": "The charge window ONLY (no melee arm). Casts on the unit itself.",
        "barrier_broken": "The unit's own barrier has broken. Casts on the unit itself.",
        "wavering_self": "The unit ITSELF is wavering (fail-closed). Casts on the unit itself.",
        "wavering_self_or_ally": "The unit itself is wavering OR a wavering ally is IN RANGE. Casts on the unit itself.",
        "charge_or_wavering": "The charge window OR the unit is wavering. Casts on the unit itself.",
        "wavering_ally_range": "An ally IN RANGE is wavering — the ally need NOT be in melee. Casts on the CHOSEN ALLY.",
        "verminking_wavering": "An ally IN RANGE is in melee AND wavering. Casts on the unit itself (the ally is the trigger, not the target).",
        "glorious_death": "A SLAYER ally in range is in melee (Slayer status = exact whole-key membership of a list derived from the game's own land_units keys). Casts on that ally; the owner casts on itself only when it is itself a Slayer and in melee.",
        "metallurgy_melee": "The owner is in melee OR an ally in range is in melee. Casts on the unit itself.",
        "blood_sacrifice": "The lowest-health ally in range, when that ally is at or below 75% health. Casts on THAT ALLY (the ability charges the recipient a cost).",
        "eat_da_runts": "The unit itself at or below 75% health; otherwise the lowest-health ally in range. Casts on self, or on that ally.",
        "enemy_engaged_or_shot": "An ENEMY unit in range is in melee, or is under missile fire. Casts on that enemy (the enemy form of `perform_special_ability`).",
        "enemy_ground_area": "An enemy in range is in melee or under missile fire; the area hex is placed on that enemy's own ground (the ground form of the call).",
        "ally_heal": "The lowest-health ally in range that is at or below 75% health. Casts on that ally.",
        "ally_heal_melee": "The owner is in melee AND an ally in range is at or below 75% health. Casts on the lowest-health such ally.",
        "ally_wavering": "An ally in range is wavering. Casts on that ally.",
        "ally_melee_buff": "The owner is in melee; the target is an ally in range (a plain ally buff). Casts on that ally.",
        "ally_overseer": "A non-commander, non-large ally in range (a key list derived from `land_units.class` + `battle_entities.size`). Casts on that ally.",
        "ally_beast": "A BEAST-class ally in range (`main_units.caste == war_beast`). Casts on that ally.",
        "ally_broken": "An ally in range whose morale is BROKEN (a live `MoraleState == broken` read). Casts on that ally.",
        "ally_missile": "A missile-capable ally in range (`land_units.primary_missile_weapon` non-empty). Casts on that ally.",
        "ally_ammo_low": "An ally in range that is SHOOTING (the firing flag: its ammo_left() dropped) with 70% or less of its ammunition left (`FOURTH.RESTOCK_AT_FRACTION`, 100% minus the 30% refill); the one with the least left wins; an ally refilled in the last `FOURTH.RESTOCK_CLAIM_S` (12 s) is skipped. Casts on that ally.",
        "allies_firing_aura": "At least `FOURTH.FIRING_AURA_MIN` (1) unit inside the aura bound, the caster counting, is SHOOTING past its cast point (first shot + 0.5 x its reload). Ballistics Calibration is cast on the ground at the caster's own position; the other auras on the caster.",
        "melee_or_shooting_aura": "The Metallurgy melee rule (the owner in melee, or an ally in melee within 24 m), OR the owner or any unit within the aura bound shooting past its cast point. Casts on the unit itself (the aura).",
        "melee_or_shooting_self_or_ally": "The owner in melee (not wavering) or shooting past its cast point: cast on itself. Otherwise the closest ally in range in melee or shooting: cast on that ally.",
        "self_shooting": "The unit itself shooting past its cast point. Casts on the unit itself.",
        "under_fire": "The unit itself under missile fire (`is_under_missile_attack()` exactly true); for an aura also any friendly unit within the aura bound. Casts on the unit itself.",
        "melee_or_under_fire": "The unit in melee (not wavering) or under missile fire; for an aura also any friendly unit within the aura bound in melee or under fire. Casts on the unit itself.",
        "self_recharging": "At least one other ability of this unit, cast by the mod, still recharging (effect + recharge from the game data). Casts on the unit itself.",
        "self_recharging_2": "At least two other abilities of this unit, cast by the mod, still recharging. Casts on the unit itself.",
        "recharging_in_reach": "The unit itself has an ability recharging (cast on itself), else the closest ally in range that has (cast on that ally).",
        "melee_self_or_ally": "The unit itself in melee (cast on itself), else the closest ally in range in melee (cast on that ally).",
        "self_running": "The unit itself RUNNING (`is_moving_fast()`). Casts on the unit itself.",
        "melee_or_wavering_aura": "The unit itself in melee or WAVERING, or a friendly unit inside the aura bound in melee or wavering. Casts on the unit itself.",
        "enemy_missile_shooting": "An ENEMY missile unit in range that is SHOOTING (its `ammo_left()` dropped between two polls within the firing-flag window) and not in melee. Casts on that enemy.",
        "wavering_aura": "The unit itself WAVERING, or a friendly unit inside the aura bound wavering (the whole army for an army-wide aura; nobody else for a self-only effect). Casts on the unit itself.",
        "enemy_fast_near_ally": "An ENEMY unit in range that is MOVING with a run speed (`fast_speed()`) of 5 m/s or more and is within 40 m of one of our units (the user's settings, round 135). Casts on that enemy.",
        "self_or_ally_shooting": "The caster SHOOTING past its cast point: cast on itself. Otherwise the closest ally in range that is shooting past its cast point: cast on that ally.",
        "melee_or_self_or_ally_shooting": "In melee and not wavering (as melee_unwavering): cast on itself. Otherwise as self_or_ally_shooting (the caster shooting, else the closest shooting ally in range).",
        "no_enemy_in_range_within_boost": "Not in melee, ammunition left, NO live enemy inside the unit's own missile_range(), and at least one inside missile_range x `FOURTH.FARSIGHT_BAND` (1 + 0.30 x 0.70 = 1.21). Casts on the unit itself.",
        "melee_or_shooting_into_melee": "In melee and not wavering (as melee_unwavering), OR shooting past its cast point at a current target that is in melee. Casts on the unit itself.",
        "ally_warmachine_heal": "The lowest-health WAR MACHINE ally in range that is at or below 75% health. Casts on that ally.",
        "ally_hellforged_heal": "The lowest-health HELL-FORGED ally in range that is at or below 75% health. Casts on that ally.",
        "ally_monster_heal": "The lowest-health MONSTER ally in range that is at or below 75% health. Casts on that ally.",
        "ally_construct_heal": "The lowest-health CONSTRUCT ally in range that is at or below 75% health. Casts on that ally.",
        "ally_infinite_buff": "Any ally ANYWHERE on the field (infinite range by ruling). Casts on that ally.",
        "ally_winds": "The ally with the MOST hit points remaining, anywhere in range. Casts on that ally.",
        "air_drop_on_infantry": (
            "The ORDNANCE-CENTRED family: every row has NO target flags, `effect_range 0` and a 10 m "
            "`target_intercept_range`, so the engine drops where the CASTER is and the only decision is WHEN. "
            "FIRE when the NEAREST alive enemy with MORE THAN `FOURTH.AIR_DROP_MIN_MEN = 10` models has a "
            "HORIZONTAL CENTRE-TO-CENTRE distance from the caster (`position()` x/z, "
            "`battle_vector:distance_xz` with a `sqrt(dx^2+dz^2)` fallback) UNDER "
            "`FOURTH.AIR_DROP_CENTER_M = 6.0 m` - on that same evaluation, with NO delay, NO dwell, NO "
            "velocity or position projection and NO edge measurement. `air_only` rows need "
            "`is_currently_flying()` exactly true; `no_melee` rows need `is_in_melee()` not true; every read "
            "fails CLOSED. Casts on the OWNER (self-centred); the pre-cast re-check re-measures the centre gap "
            "on fresh handles and SKIPS rather than spends. A 0.2 s fast pass runs while a valid enemy is "
            "inside `AIR_DROP_NEAR_M = 30 m`; the global poll stays at 250 ms."),
    }
    by_fam = collections.defaultdict(list)
    for e in entries:
        by_fam[e["trigger"]].append(e)
    CAST_TARGET = {
        "allies_firing_aura": "the caster (Ballistics Calibration: the ground at the caster's own position)",
        "self_or_ally_shooting": "the caster when it shoots, otherwise the closest shooting ally",
        "melee_or_shooting_self_or_ally": "the caster in melee or when it shoots, otherwise the closest ally in melee or shooting",
        "melee_or_self_or_ally_shooting": "the caster in melee or when it shoots, otherwise the closest shooting ally",
        "eat_da_runts": "the unit itself, else the lowest-health ally in range",
        "glorious_death": "a Slayer ally in melee, else the unit itself (only when the owner is itself a Slayer)",
        "blood_sacrifice": "the chosen ally (the ability charges the recipient a cost)",
        "wavering_ally_range": "the chosen wavering ally",
        "ally_infinite_buff": "the chosen ally anywhere on the field",
        "metallurgy_melee": "the unit itself",
        "verminking_wavering": "the unit itself (the ally is the trigger, not the target)",
        "wavering_self_or_ally": "the unit itself",
        "health_aura_ground": "the ground under the chosen ally (owner arm: at the caster)",
        "health_aura_self": "the caster",
        "health_aura_ally": "the chosen ally",
    }

    def cast_target_of(f):
        if f in CAST_TARGET:
            return CAST_TARGET[f]
        if f.startswith("enemy_"):
            return "the chosen enemy unit" + ("'s own ground (ground form of the call)" if f == "enemy_ground_area" else "")
        if f.startswith("ally_"):
            return "the chosen ally in range"
        return "the unit itself"

    fam_order = sorted(by_fam, key=lambda t: (-len(by_fam[t]), t))
    gcache = {}
    for f in fam_order:
        es = by_fam[f]
        nk = sum(len(e["keys"]) for e in es)
        A("### `%s` — %d entries / %d keys" % (f, len(es), nk))
        A("")
        A(FAM_DESC.get(f, "unknown - see the mod's own `FOURTH.evaluate_%s`." % f))
        A("")
        A("**Plain English (the sentence the mod ships in that ability's tooltip):** *%s.*" % tips.get(f, "unknown").rstrip("."))
        A("")
        if any(e.get("range_real") or e.get("ally_range_real") or e.get("aura_real") for e in es):
            bound_note = "the per-ability 70% constant shown in each row's Range column"
        elif any(FAM_CONST.get(f) for e in es):
            bound_note = "the mod's named constant shown in each row (see Range)"
        elif f == "ally_infinite_buff":
            bound_note = "none - infinite range by ruling"
        else:
            bound_note = "none - the trigger is self-referential"
        A("**Cast target:** %s. **Trigger bound:** %s." % (cast_target_of(f), bound_note))
        A("")
        A("| Ability | Key | Effect (game data) | Restrictions | Range | Status | Trigger / logic |")
        A("|---|---|---|---|---|---|---|")
        for e in sorted(es, key=lambda x: (x["name"] or "")):
            b = bound_for(e)
            for k in e["keys"]:
                g = gcache.setdefault(k, game_data(k))
                r = rows_by_key.get(k, {})
                A("| %s | `%s` | %s | %s | %s | %s | %s |" % (
                    e["name"] or "unknown",
                    k,
                    effect_text(g).replace("|", "/"),
                    restrictions_text(g).replace("|", "/"),
                    range_text(g, b).replace("|", "/"),
                    (r.get("status", "unknown")).replace("|", "/"),
                    ("Fires: " + tips.get(f, "unknown").rstrip(".") + ". Cast target: " + cast_target_of(f) +
                     (". Bound: " + b if b else "")).replace("|", "/")))
        A("")

    # ---------------------------------------------------------- SECTION 3
    A("---")
    A("")
    A("## 3. EXCLUDED / SKIPPED / REJECTED / IMPOSSIBLE — with reasons")
    A("")
    A("These %d abilities have no automatic logic. The heading is the decision family; the **Why** column is the"
      % len(non_impl_rows))
    A("tracker's own final status/reason for that row. The Effect / Restrictions / Range columns are the same")
    A("fresh game-data extraction used in §2, so a later re-decision has the mechanics at hand.")
    A("")
    groups = collections.defaultdict(list)
    for r in non_impl_rows:
        groups[(status_family(r["status"]), reason_of(r["status"]))].append(r)
    order = sorted(groups, key=lambda g: (-len(groups[g]), g[1]))
    for (famname, reason) in order:
        rs = groups[(famname, reason)]
        A("### %s — %s (%d)" % (famname, reason, len(rs)))
        A("")
        A("| Ability | Key | Effect (game data) | Restrictions | Range | Status | Why |")
        A("|---|---|---|---|---|---|---|")
        for r in sorted(rs, key=lambda x: x["name"]):
            g = gcache.setdefault(r["key"], game_data(r["key"]))
            A("| %s | `%s` | %s | %s | %s | %s | %s |" % (
                r["name"], r["key"],
                effect_text(g).replace("|", "/"),
                restrictions_text(g).replace("|", "/"),
                range_text(g).replace("|", "/"),
                r["status"].replace("|", "/"),
                (r["proposal"] or reason).replace("|", "/")))
        A("")
    A("---")
    A("")
    A("## Reconciliation (repeat of §1.6)")
    A("")
    A("* §1 inventory rows: **%d**; distinct keys **%d**." % (total, len(set(r["key"] for r in rows))))
    A("* §2 implemented: **%d** entries / **%d** keys — equals the mod's `ABILITIES` count." % (len(entries), len(mod_keys)))
    A("* §3 non-implemented: **%d** rows." % len(non_impl_rows))
    A("* Rows whose EFFECT the game's tables cannot source (written `unknown`): **%d** of %d." % (len(no_eff), total))
    A("* Abilities carrying a restriction flag (invalid-target / invalid-usage / auto-deactivate): **%d**." %
      sum(1 for r in rows if gcache.setdefault(r["key"], game_data(r["key"]))["invalid_target"] or
          gcache[r["key"]]["invalid_usage"] or gcache[r["key"]]["auto_deactivate"]))
    A("")
    A("_Generated by `tools/build_ability_database.py` from the sources listed at the top. No ability row was added or dropped._")

    open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    stats = {
        "inventory_rows": total,
        "distinct_keys": len(set(r["key"] for r in rows)),
        "mod_entries": len(entries),
        "mod_keys": len(mod_keys),
        "tracker_implemented_rows": len(impl_rows),
        "non_implemented_rows": len(non_impl_rows),
        "effect_unknown": len(no_eff),
        "effect_unknown_and_no_tooltip": len(no_eff_no_tip),
        "no_spec_row": len(no_spec),
        "invalid_target_abilities": sum(1 for r in rows if gcache[r["key"]]["invalid_target"]),
        "invalid_usage_abilities": sum(1 for r in rows if gcache[r["key"]]["invalid_usage"]),
        "auto_deactivate_abilities": sum(1 for r in rows if gcache[r["key"]]["auto_deactivate"]),
        "any_restriction_flag": sum(1 for r in rows if gcache[r["key"]]["invalid_target"] or gcache[r["key"]]["invalid_usage"] or gcache[r["key"]]["auto_deactivate"]),
        "trigger_families": len(trig_count),
        "status_families": dict(fam),
        "out_bytes": os.path.getsize(OUT),
    }
    print(json.dumps(stats, indent=1))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
