"""Build docs/WH3_abilities_master_v1_2026-10-17.xlsx - the master spreadsheet.

One row per ability (1,797), with the full in-game tooltip content, the new
wheel-only status, the implementation status and - for implemented rows - the
trigger EXACTLY as the mod's evaluator performs it.

Sources (nothing invented):
  * docs/WH3_ability_tracker.md                     the inventory (1,797 rows)
  * docs/WH3_ability_database_master.md             cross-check
  * docs/WH3_recount_wheel_only.md                  the wheel rule + the numbers
  * mod_source/script/battle/mod/zz_test_deadly_onslaught.lua  implemented set,
        evaluator source, per-entry bounds
  * %LOCALAPPDATA%\\Temp\\wh3\\  game data (unit_abilities, unit_special_abilities,
        special_ability_phases, stat/attribute effects, flag tables, loc)

The extraction module tools/build_ability_database.py is REUSED (its loaders and
per-key game_data() are imported), not re-implemented.

Run:  python tools/build_abilities_master_xlsx.py [--sample N]
"""
import os
import re
import sys
import csv
import json
import math
import collections
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import build_ability_database as bd          # noqa: E402  (reused extraction)

DOCS = os.path.join(ROOT, "docs")
OUT_XLSX = os.path.join(DOCS, "WH3_abilities_master_v1_2026-10-17.xlsx")
TODAY = "2026-10-17"

T = bd.T
U = bd.U

# --------------------------------------------------------------------------- game lookups
UB = bd.load_tsv(os.path.join(T, "unit_abilities.tsv"))
UB_H = UB[0]
UB_BY_KEY = {r[0]: r for r in UB[1:]}
I_SRC = UB_H.index("source_type")
I_TYPE = UB_H.index("type")

TYPE_LOC = bd.load_tsv(os.path.join(U, "unit_ability_types__.loc.tsv"))
TYPE_NAME = {}
TYPE_DESC = {}
for r in TYPE_LOC[1:]:
    if r[0].startswith("unit_ability_types_onscreen_name_"):
        TYPE_NAME[r[0][len("unit_ability_types_onscreen_name_"):]] = bd.strip_art(r[1])
    elif r[0].startswith("unit_ability_types_localised_description_"):
        TYPE_DESC[r[0][len("unit_ability_types_localised_description_"):]] = bd.strip_art(r[1])

IN_WHEEL_SRC = {"active", "bound", "lord", "character", "unit", "item", "rune", "weapon"}
OUT_SRC = {"spell", "cataclysm", "army", "quest"}

SRC_REASON = {
    "active": "unit-carried active ability",
    "bound": "bound spell on the unit's bar",
    "lord": "lord battle ability (unit-carried)",
    "character": "character battle ability",
    "unit": "unit battle ability",
    "item": "item-granted ability",
    "rune": "rune ability",
    "weapon": "weapon-granted ability",
    "spell": "spell (lore-group, cast from the spellbook)",
    "cataclysm": "cataclysm spell (army-bar registry)",
    "army": "army-bar ability",
    "quest": "quest-battle army ability",
}

# --------------------------------------------------------------------------- helpers
def fl(x, default=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def g(x):
    """format a float without trailing zeros"""
    if x is None:
        return "?"
    return ("%g" % x)


def num_or_none(s):
    return fl(s)


def clean(text):
    if text is None:
        return ""
    text = text.replace("\u00a0", " ").replace("\r", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", text).strip()


# --------------------------------------------------------------------------- tooltip fields
def tooltip_record(key):
    """all tooltip fields for one ability key, each a string ( '-' = absent )."""
    gd = bd.game_data(key)
    spec = gd["spec"]
    ub = UB_BY_KEY.get(key)
    rec = {}

    # -- Category / Targeting Type ------------------------------------------------
    tkey = ub[I_TYPE] if ub and len(ub) > I_TYPE else ""
    cat = TYPE_NAME.get(tkey) or (tkey or "unknown")
    tgt = []
    if spec.get("target_ground") == "true":
        tgt.append("ground (area placed)")
    if spec.get("target_enemies") == "true":
        tgt.append("enemy units")
    if spec.get("target_friends") == "true":
        tgt.append("allies")
    if spec.get("target_self") == "true":
        tgt.append("self")
    if not tgt:
        if spec.get("affect_self") == "true" or spec.get("always_affect_self") == "true":
            tgt.append("self (always affects self)")
        else:
            tgt.append("no explicit target")
    rec["category"] = "%s · targeting: %s" % (cat, " + ".join(tgt))

    # -- Uses ---------------------------------------------------------------------
    nu = spec.get("num_uses")
    if nu is None:
        rec["uses"] = "unknown"
    elif num_or_none(nu) is not None and num_or_none(nu) < 0:
        rec["uses"] = "unlimited"
    elif num_or_none(nu) == 0:
        rec["uses"] = "0 (no charge count)"
    else:
        n = int(num_or_none(nu))
        rec["uses"] = "%d use%s" % (n, "" if n == 1 else "s")

    # -- phases: stats / attributes / ui effects / damage / durations --------------
    stat_rows, attr_rows, ui_rows = [], [], []
    dps_bits, dur_bits, move_rows = [], [], []
    for idx, p in enumerate(gd["phases"], 1):
        ph = p["phase"]
        det = p["detail"] or {}
        scope = bd.scope_of(spec, (p["t_self"], p["t_friends"], p["t_enemies"]))
        for s in bd.sps_idx.get(ph, []):
            name = bd.stat_disp(s[1])
            val = bd.fmt_val(s[2], s[3])
            txt = "%s: %s" % (name, val)
            stat_rows.append(txt)
            if any(w in s[1].lower() for w in ("speed", "acceleration", "deceleration")):
                move_rows.append(txt)
        for a in bd.pae_idx.get(ph, []):
            attr_rows.append("%s (%s)" % (bd.attr_disp(a[0]), a[2] or "attribute"))
        for e in bd.p2u_idx.get(ph, []):
            ui_rows.append(bd.UAE_TXT.get(
                "unit_abilities_additional_ui_effects_localised_text_" + e[0], e[0]))
        # damage / heal numbers that the game's own phase carries
        dmg = fl(det.get("damage_amount"), 0.0) or 0.0
        freq = fl(det.get("hp_change_frequency"), 0.0) or 0.0
        if dmg > 0:
            if freq > 0:
                mde = fl(det.get("max_damaged_entities"))
                suffix = ""
                if mde:
                    suffix = ", max %s entit%s" % (g(mde), "y" if mde == 1 else "ies")
                dps_bits.append("%s dps (%s per hit every %s s%s)" % (
                    g(round(dmg / freq, 2)), g(dmg), g(freq), suffix))
            else:
                dps_bits.append("%s per hit (no tick interval stated)" % g(dmg))
        heal = fl(det.get("heal_amount"), 0.0) or 0.0
        if heal > 0:
            stat_rows.append("Heals: %s per tick every %s s" % (g(heal), g(freq) if freq else "?"))
        if det.get("cant_move") == "true":
            move_rows.append("cannot move")
        if det.get("requested_stance"):
            move_rows.append("stance: %s" % det["requested_stance"])
        if det.get("spreading"):
            move_rows.append("spreading area: %s" % det["spreading"])
        d = fl(det.get("duration"), 0.0)
        dur_bits.append("phase %d: %s s" % (idx, g(d) if d is not None else "?"))

    def uniq(seq):
        out, seen = [], set()
        for x in seq:
            if x and x not in seen:
                seen.add(x)
                out.append(x)
        return out

    stat_rows, attr_rows, ui_rows = uniq(stat_rows), uniq(attr_rows), uniq(ui_rows)
    move_rows = uniq(move_rows)

    rec["dps"] = "; ".join(uniq(dps_bits)) if dps_bits else "-"
    rec["stats"] = "; ".join(stat_rows + attr_rows) if (stat_rows or attr_rows) else "-"
    rec["ui_effects"] = "; ".join(ui_rows)          # helper, folded into stats when present
    if ui_rows:
        rec["stats"] = (rec["stats"] if rec["stats"] != "-" else "") + \
            ("; " if rec["stats"] not in ("-", "") else "") + "; ".join(ui_rows)

    # -- Duration -----------------------------------------------------------------
    at = fl(spec.get("active_time"), 0.0) or 0.0
    phase_durs = [fl(p["detail"].get("duration"), 0.0) for p in gd["phases"]
                  if p["detail"]] if gd["phases"] else []
    phase_durs = [d for d in phase_durs if d]
    if at > 0:
        rec["duration"] = "%s s" % g(at)
    elif phase_durs:
        rec["duration"] = "%s s (from the phase)" % g(max(phase_durs))
    else:
        rec["duration"] = "-"

    # -- Radius / Effect Area -----------------------------------------------------
    rad = []
    er = fl(spec.get("effect_range"), 0.0) or 0.0
    if er > 0:
        rad.append("effect range (aura) %s m" % g(er))
    for col, label in (("targetting_aoe", "targeting area"),
                       ("active_aoe", "active area"), ("passive_aoe", "passive area")):
        v = spec.get(col, "")
        if v:
            rad.append("%s: %s" % (label, v))
    rec["radius"] = "; ".join(rad) if rad else "-"

    # -- Movement Speed -----------------------------------------------------------
    rec["speed"] = "; ".join(move_rows) if move_rows else "-"

    # -- Range --------------------------------------------------------------------
    rng = []
    tir = fl(spec.get("target_intercept_range"), 0.0) or 0.0
    mr = fl(spec.get("min_range"), 0.0) or 0.0
    if tir > 0:
        rng.append("target_intercept_range %s m" % g(tir))
    if er > 0:
        rng.append("effect_range %s m" % g(er))
    if mr > 0:
        rng.append("min_range %s m" % g(mr))
    if spec.get("target_ground") == "true":
        rng.append("targets ground")
    rec["range"] = "; ".join(rng) if rng else "no range column (unlimited / self)"

    # -- Phase Durations ----------------------------------------------------------
    rec["phase_durations"] = "; ".join(dur_bits) if dur_bits else "-"

    # -- Cooldown -----------------------------------------------------------------
    rt = fl(spec.get("recharge_time"), 0.0)
    if rt is None:
        rec["cooldown"] = "unknown"
    elif rt > 0:
        rec["cooldown"] = "%s s" % g(rt)
    else:
        rec["cooldown"] = "0 s (no cooldown)"

    # -- Affects units if ---------------------------------------------------------
    aff = []
    if spec.get("affect_self") == "true" or spec.get("always_affect_self") == "true":
        aff.append("self")
    if spec.get("target_friends") == "true":
        n = fl(spec.get("num_effected_friendly_units"), 0) or 0
        aff.append("allies in range (%s)" % ("all" if n <= 0 else "max %d" % int(n)))
    if spec.get("target_enemies") == "true":
        n = fl(spec.get("num_effected_enemy_units"), 0) or 0
        aff.append("enemies in range (%s)" % ("all" if n <= 0 else "max %d" % int(n)))
    if spec.get("only_affect_owned_units") == "true":
        aff.append("own units only")
    if spec.get("only_affect_target") == "true":
        aff.append("only the chosen target")
    if spec.get("target_ground") == "true":
        aff.append("units at the placed ground point")
    rec["affects"] = "; ".join(aff) if aff else "-"

    # -- Can use if (invalid-usage flags) -----------------------------------------
    iu = gd["invalid_usage"]
    rec["can_use"] = "; ".join("not `%s`" % f for f in iu) if iu else "-"
    rec["invalid_usage"] = iu
    rec["invalid_target"] = gd["invalid_target"]
    rec["auto_deactivate"] = gd["auto_deactivate"]

    # -- Tactical Overview --------------------------------------------------------
    desc = TYPE_DESC.get(tkey, "")
    rec["tactical"] = clean(desc) if desc else "-"
    rec["type_key"] = tkey

    return rec


TOOLTIP_LABELS = [
    ("category", "Category / Targeting Type"),
    ("uses", "Uses"),
    ("dps", "Damage Per Second"),
    ("stats", "Stat Modifiers"),
    ("duration", "Duration"),
    ("radius", "Radius / Effect Area"),
    ("speed", "Movement Speed"),
    ("range", "Range"),
    ("phase_durations", "Phase Durations"),
    ("cooldown", "Cooldown"),
    ("affects", "Affects units if"),
    ("can_use", "Can use if"),
    ("tactical", "Tactical Overview"),
]


def tooltip_full(rec):
    return "\n".join("%s: %s" % (label, rec[k]) for k, label in TOOLTIP_LABELS)


# --------------------------------------------------------------------------- trigger rules
# Every rule below is read from the evaluator source in
# mod_source/script/battle/mod/zz_test_deadly_onslaught.lua (section 7g and the
# CLASS A / CLASS B blocks).  One entry per evaluator name (35).
PIPELINE = ("shared gate: unit alive (>0 men); one is_routing() read for the poll; only the markers this unit is "
            "known to own are evaluated (full-table fallback while its owned set is unknown); this (unit, ability) "
            "pair must be armed; readiness = can_perform_special_ability on the owned key (a variant walk when no "
            "usable cached key); 2 s per-pair guard; on an engine cooldown refusal: 2 s, then 8 s silent back-off, "
            "hard re-probe at 20 s; pre-fire unit-alive check; cast; the cooldown episode clears only on an "
            "accepted fire")

TRIGGERS = {
    "charge": dict(
        rule=("charge window OR in melee; not routing. Charge window = is_moving_fast() and not "
              "is_in_melee() and current_target() ~= nil and target distance between 12 m and 60 m "
              "and (distance / fast_speed) <= 4 s; the melee arm = is_in_melee(). The charge arm is "
              "tested first and wins"),
        target="self"),
    "tired": dict(
        rule=("not routing; fatigue_state() is exactly tired, very_tired or exhausted (an unreadable "
              "or unrecognised state fails closed: no fire)"),
        target="self"),
    "melee": dict(rule="not routing; is_in_melee()", target="self"),
    "melee_low_morale": dict(
        rule=("not routing; is_in_melee(); is_wavering() must be TRUE - an unreadable morale read is "
              "accepted (fail-open)"),
        target="self"),
    "melee_unwavering": dict(
        rule=("not routing; is_in_melee(); is_wavering() must NOT be true - false and unreadable both "
              "pass (fail-open morale)"),
        target="self"),
    "barrier_broken": dict(
        rule=("not routing; the barrier context values are numbers with BarrierMaxHp > 0 and "
              "BarrierHp <= 0"),
        target="self"),
    "charge_or_melee": dict(
        rule=("charge window (as the charge evaluator) OR is_in_melee(); not routing; the charge arm is "
              "tested first and wins"),
        target="self"),
    "ushoran_health": dict(
        rule=("not routing; HealthPercent is a readable number and <= 75 (no hysteresis, no second "
              "threshold - repeat attempts are held only by readiness, the engine cooldown and the back-off)"),
        target="self"),
    "glorious_death": dict(
        rule=("not routing; walk the tracked units: alive (>0 men), not the owner, is_in_melee(), not "
              "routing, type() in the 10-key Slayer list, unit_distance <= 38 m (an unreadable distance "
              "is accepted), keep the CLOSEST; if none, the arm fires when the owner itself is a Slayer "
              "and in melee"),
        target="self",
        recheck="the chosen Slayer ally must still be within 38 m, else the cast is skipped"),
    "verminking_wavering": dict(
        rule=("not routing; walk the tracked units: alive, not the owner, is_in_melee(), not routing, "
              "is_wavering() == true, unit_distance <= 24 m, keep the CLOSEST"),
        target="self",
        recheck="the chosen ally must still be within 24 m, else the cast is skipped"),
    "melee_health75": dict(
        rule="not routing; is_in_melee(); HealthPercent is a readable number and <= 75",
        target="self"),
    "metallurgy_melee": dict(
        rule=("not routing; if is_in_melee() fire at once on self; otherwise walk the tracked units "
              "(alive, not the owner, is_in_melee(), not routing) within 24 m and keep the CLOSEST"),
        target="self",
        recheck="the chosen ally must still be within 24 m, else the cast is skipped"),
    "charge_only": dict(
        rule=("charge window ONLY - the melee arm is deliberately absent; charge window = is_moving_fast() "
              "and not is_in_melee() and current_target() ~= nil and distance 12-60 m and time-to-contact "
              "<= 4 s; not routing"),
        target="self"),
    "wavering_self": dict(
        rule="not routing; is_wavering() == true (fail-closed: an unreadable morale read never fires)",
        target="self"),
    "wavering_self_or_ally": dict(
        rule=("not routing; if the owner is is_wavering() == true fire at once; otherwise the CLOSEST "
              "tracked ally that is alive, not the owner, is_in_melee(), not routing and is_wavering() "
              "== true within 24 m"),
        target="self",
        recheck="the chosen ally must still be within 24 m, else the cast is skipped"),
    "charge_or_wavering": dict(
        rule=("not routing; charge window first (as the charge evaluator, no melee arm), otherwise "
              "is_wavering() == true"),
        target="self"),
    "wavering_ally_range": dict(
        rule=("not routing; the CLOSEST tracked ally that is alive, not the owner, not routing and "
              "is_wavering() == true within the entry's bound; the ally need NOT be in melee and the "
              "owner need not be wavering"),
        target="that ally (cast on the ally)",
        recheck="the chosen ally must still be alive, still wavering and still within the bound, else "
                "the cast is skipped"),
    "blood_sacrifice": dict(
        rule=("not routing; walk the tracked allies: alive, not the owner, not routing, HealthPercent "
              "readable and <= 75, unit_distance <= 70 m, keep the LOWEST health"),
        target="that ally (cast on the ally)",
        recheck="the chosen ally must still be alive, still <= 75% health and still within 70 m, else "
                "the cast is skipped"),
    "eat_da_runts": dict(
        rule=("not routing; if the owner's own HealthPercent is readable and <= 75 fire on self; "
              "otherwise walk the tracked allies (alive, not the owner, not routing, HealthPercent <= 75, "
              "unit_distance <= 70 m) and keep the LOWEST health"),
        target="self, otherwise that ally",
        recheck="for the ally arm: the ally must still be alive, still <= 75% health and still within "
                "70 m, else the cast is skipped (the self arm is not gated)"),
    "enemy_engaged_or_shot": dict(
        rule=("not routing; enumerate the main enemy army list; per enemy: number_of_men_alive() > 0; "
              "is_valid_target() (fallback is_valid()) must not be false - unreadable passes; arm = "
              "is_in_melee() -> melee, else is_under_missile_attack() -> missile (unreadable = false); "
              "unit_distance <= the entry's bound; prefer a melee arm, then the closest"),
        target="that enemy unit",
        recheck="the enemy must still be alive, still in melee or under missile fire and still within "
                "the bound, else the cast is skipped"),
    "enemy_ground_area": dict(
        rule=("the same pick as enemy_engaged_or_shot (enemy alive, validity not false, in melee or under "
              "missile fire, unit_distance <= the entry's bound, melee arm preferred then closest)"),
        target="the chosen enemy's own ground (ground form of the call)",
        recheck="the enemy must still be alive, still in melee or under missile fire and still within "
                "the bound, else the cast is skipped"),
    "ally_heal": dict(
        rule=("not routing; walk the tracked allies: alive, not the owner, not routing, pass the class "
              "gate (none for this family), HealthPercent <= 75, unit_distance <= the entry's bound "
              "(unreadable distance counts as in range), keep the LOWEST health"),
        target="that ally (cast on the ally)",
        recheck="alive, still within the bound and still <= 75% health, else the cast is skipped"),
    "ally_heal_melee": dict(
        rule=("not routing; is_in_melee() on the owner; then the ally_heal pick - alive, not the owner, "
              "not routing, HealthPercent <= 75, within the entry's bound, LOWEST health"),
        target="that ally (cast on the ally)",
        recheck="alive, still within the bound and still <= 75% health, else the cast is skipped"),
    "ally_wavering": dict(
        rule=("not routing; the CLOSEST tracked ally that is alive, not the owner, not routing and "
              "is_wavering() == true within the entry's bound"),
        target="that ally (cast on the ally)",
        recheck="alive and still within the bound, else the cast is skipped"),
    "ally_melee_buff": dict(
        rule=("not routing; is_in_melee() on the owner; is_wavering() must not be true; then the CLOSEST "
              "tracked ally that is alive, not the owner, not routing and within the entry's bound"),
        target="that ally (cast on the ally)",
        recheck="alive and still within the bound, else the cast is skipped"),
    "ally_overseer": dict(
        rule=("not routing; the CLOSEST tracked ally that is alive, not the owner, not routing, type() in "
              "the 918-key overseer list (land_units.class != com AND entity size not large/very_large) "
              "and within the entry's bound"),
        target="that ally (cast on the ally)",
        recheck="alive and still within the bound, else the cast is skipped"),
    "ally_beast": dict(
        rule=("not routing; the CLOSEST tracked ally that is alive, not the owner, not routing, type() in "
              "the 55-key beast list (main_units.caste == war_beast) and within the entry's bound"),
        target="that ally (cast on the ally)",
        recheck="alive and still within the bound, else the cast is skipped"),
    "ally_broken": dict(
        rule=("not routing; the CLOSEST tracked ally that is alive, not the owner, not routing, whose "
              "MoraleState context value is exactly 'broken' (fail-closed) and within the entry's bound"),
        target="that ally (cast on the ally)",
        recheck="alive and still within the bound, else the cast is skipped"),
    "ally_missile": dict(
        rule=("not routing; the CLOSEST tracked ally that is alive, not the owner, not routing, type() in "
              "the 493-key missile list (land_units.primary_missile_weapon non-empty) and within the "
              "entry's bound"),
        target="that ally (cast on the ally)",
        recheck="alive and still within the bound, else the cast is skipped"),
    "ally_warmachine_heal": dict(
        rule=("not routing; the LOWEST-health tracked ally that is alive, not the owner, not routing, "
              "type() in the 68-key war-machine list, HealthPercent <= 75 and within the entry's bound"),
        target="that ally (cast on the ally)",
        recheck="alive, still within the bound and still <= 75% health, else the cast is skipped"),
    "ally_hellforged_heal": dict(
        rule=("not routing; the LOWEST-health tracked ally that is alive, not the owner, not routing, "
              "carrying the 'hellforged' attribute (13-key list), HealthPercent <= 75 and within the "
              "entry's bound"),
        target="that ally (cast on the ally)",
        recheck="alive, still within the bound and still <= 75% health, else the cast is skipped"),
    "ally_monster_heal": dict(
        rule=("not routing; the LOWEST-health tracked ally that is alive, not the owner, not routing, "
              "type() in the 235-key monster list (main_units.caste == monster), HealthPercent <= 75 and "
              "within the entry's bound"),
        target="that ally (cast on the ally)",
        recheck="alive, still within the bound and still <= 75% health, else the cast is skipped"),
    "ally_construct_heal": dict(
        rule=("not routing; the LOWEST-health tracked ally that is alive, not the owner, not routing, "
              "carrying the 'construct' attribute (29-key list), HealthPercent <= 75 and within the "
              "entry's bound"),
        target="that ally (cast on the ally)",
        recheck="alive, still within the bound and still <= 75% health, else the cast is skipped"),
    "ally_infinite_buff": dict(
        rule=("not routing; the CLOSEST tracked ally that is alive, not the owner, not routing - the "
              "distance test is SKIPPED ENTIRELY (infinite range per the wiki)"),
        target="that ally (cast on the ally)",
        recheck="alive, else the cast is skipped"),
    "ally_winds": dict(
        rule=("not routing; the tracked ally that is alive, not the owner, not routing and has the "
              "HIGHEST absolute HealthValue (no health-percentage gate) within the entry's bound"),
        target="that ally (cast on the ally)",
        recheck="alive and still within the bound, else the cast is skipped"),
}

# family -> named trigger bound when the entry carries no per-ability range
FAM_CONST = {
    "wavering_ally_range": 24, "wavering_self_or_ally": 24, "verminking_wavering": 24,
    "metallurgy_melee": 24, "blood_sacrifice": 70, "eat_da_runts": 70, "glorious_death": 38,
}
ALLY_BUCKET = {50: 35, 60: 42, 75: 52, 100: 70, 150: 105, 200: 140}
ENEMY_BUCKET = {15: 10, 20: 14, 30: 21, 35: 24, 50: 35, 70: 49, 75: 52,
                100: 70, 150: 105, 180: 126, 200: 140, 500: 350}


def trigger_text(entry, family):
    spec = TRIGGERS.get(family)
    if spec is None:
        return "unknown (no evaluator entry in FOURTH.evaluators)"
    bits = ["%s: %s" % (family, spec["rule"])]
    # per-entry distance bound
    bound = None
    if family.startswith("enemy_"):
        rr = entry.get("range_real")
        if rr:
            b = ENEMY_BUCKET.get(int(rr))
            if b is not None:
                bound = "%d m (70%% of the ability's %d m target_intercept_range)" % (b, int(rr))
            else:
                bound = "52 m (fallback constant; the entry's %d m range has no named bucket)" % int(rr)
        else:
            bound = "52 m (shared accusation constant - the entry sets no range_real)"
    elif family.startswith("ally_") or family in ("wavering_ally_range", "blood_sacrifice", "eat_da_runts"):
        ar = entry.get("ally_range_real")
        if ar:
            b = ALLY_BUCKET.get(int(ar))
            bound = ("%d m (70%% of the ability's %d m ally cast reach)" % (b, int(ar))
                     if b is not None else
                     "no bound (the entry's %d m ally reach has no named bucket -> unbounded)" % int(ar))
        elif family in FAM_CONST:
            bound = "%d m (the mod's named constant for this trigger)" % FAM_CONST[family]
        elif family == "ally_infinite_buff":
            bound = "none - infinite range by ruling"
    elif family in ("glorious_death", "verminking_wavering", "metallurgy_melee",
                    "wavering_self_or_ally"):
        bound = "%d m (the mod's named constant for this trigger)" % FAM_CONST[family]
    if bound:
        bits.append("bound: " + bound)
    bits.append("cast target: " + spec["target"])
    if spec.get("recheck"):
        bits.append("pre-cast re-check: " + spec["recheck"])
    bits.append(PIPELINE)
    return "; ".join(bits) + "."


# --------------------------------------------------------------------------- inventory
def build_rows():
    rows = bd.tracker_rows()
    entries, consts, tips = bd.mod_entries()
    key2entry = {}
    for e in entries:
        for k in e["keys"]:
            key2entry[k] = e
    out = []
    for n, r in enumerate(rows, 1):
        key = r["key"]
        ub = UB_BY_KEY.get(key)
        src = ub[I_SRC] if ub and len(ub) > I_SRC else ""
        entry = key2entry.get(key)
        rec = tooltip_record(key)
        in_wheel = src in IN_WHEEL_SRC
        if entry is None:
            impl = "NOT IMPLEMENTED"
        elif in_wheel:
            impl = "IMPLEMENTED"
        else:
            impl = "OUTSIDE-RULE-IMPLEMENTED"
        fam = entry["trigger"] if entry else "-"
        trig = trigger_text(entry, fam) if entry else "-"
        restr = []
        if rec["invalid_target"]:
            restr.append("invalid-target: " + ", ".join("`%s`" % x for x in rec["invalid_target"]))
        if rec["invalid_usage"]:
            restr.append("invalid-usage: " + ", ".join("`%s`" % x for x in rec["invalid_usage"]))
        if rec["auto_deactivate"]:
            restr.append("auto-deactivate: " + ", ".join("`%s`" % x for x in rec["auto_deactivate"]))
        out.append({
            "item": n,
            "name": r["name"],
            "keys": key,
            "rec": rec,
            "src": src,
            "status": "IN-WHEEL" if in_wheel else "EXCLUDED",
            "reason": ("carrier family: %s - %s" % (src, SRC_REASON.get(src, "?")) if in_wheel
                       else "excluded family: %s - %s" % (src, SRC_REASON.get(src, "?"))),
            "impl": impl,
            "family": fam,
            "trigger": trig,
            "restrictions": "; ".join(restr) if restr else "none found",
            "entry": entry,
        })
    # multi-key abilities list all their keys (own key first)
    for row in out:
        e = row["entry"]
        if e and len(e["keys"]) > 1:
            others = [k for k in e["keys"] if k != row["keys"]]
            row["keys"] = row["keys"] + "".join("; " + k for k in others)
    return out


def coverage(rows):
    cov = {}
    for k, label in TOOLTIP_LABELS:
        cov[label] = sum(1 for r in rows if r["rec"][k] not in ("-", "", "unknown"))
    cov["Restrictions (flags)"] = sum(1 for r in rows if r["restrictions"] != "none found")
    return cov


if __name__ == "__main__":
    rows = build_rows()
    print("rows", len(rows))
    print("status", collections.Counter(r["status"] for r in rows))
    print("impl", collections.Counter(r["impl"] for r in rows))
    print("families", len(set(r["family"] for r in rows if r["family"] != "-")))
    for label, n in coverage(rows).items():
        print("%-28s %5d" % (label, n))
    if "--sample" in sys.argv:
        k = int(sys.argv[sys.argv.index("--sample") + 1])
        for r in rows[:k]:
            print("\n===", r["item"], r["name"], "|", r["status"], r["impl"], r["family"])
            print("keys:", r["keys"])
            print(tooltip_full(r["rec"])[:1200])
            print("TRIGGER:", r["trigger"][:1500])
            print("RESTR:", r["restrictions"])




# =========================================================================== workbook
FAM_EVAL = {
    "charge": "evaluate_charge",
    "tired": "evaluate_tired",
    "melee": "evaluate_melee",
    "melee_low_morale": "evaluate_melee_low_morale",
    "melee_unwavering": "evaluate_in_melee_self",
    "barrier_broken": "evaluate_barrier_broken",
    "charge_or_melee": "evaluate_charge_or_melee",
    "ushoran_health": "evaluate_ushoran_health",
    "glorious_death": "evaluate_glorious_death",
    "verminking_wavering": "evaluate_verminking_wavering",
    "melee_health75": "evaluate_potion_health",
    "metallurgy_melee": "evaluate_metallurgy_melee",
    "charge_only": "evaluate_charge_only",
    "wavering_self": "evaluate_wavering_self",
    "wavering_self_or_ally": "evaluate_wavering_self_or_ally",
    "charge_or_wavering": "evaluate_charge_or_wavering",
    "wavering_ally_range": "evaluate_wavering_ally_range",
    "blood_sacrifice": "evaluate_blood_sacrifice",
    "eat_da_runts": "evaluate_eat_da_runts",
    "enemy_engaged_or_shot": "evaluate_enemy_engaged_or_shot",
    "enemy_ground_area": "evaluate_enemy_ground_area",
    "ally_heal": "evaluate_ally_heal",
    "ally_heal_melee": "evaluate_ally_heal_melee",
    "ally_wavering": "evaluate_ally_wavering",
    "ally_melee_buff": "evaluate_ally_melee_buff",
    "ally_overseer": "evaluate_ally_overseer",
    "ally_beast": "evaluate_ally_beast",
    "ally_broken": "evaluate_ally_broken",
    "ally_missile": "evaluate_ally_missile",
    "ally_warmachine_heal": "evaluate_ally_warmachine_heal",
    "ally_hellforged_heal": "evaluate_ally_hellforged_heal",
    "ally_monster_heal": "evaluate_ally_monster_heal",
    "ally_construct_heal": "evaluate_ally_construct_heal",
    "ally_infinite_buff": "evaluate_ally_infinite_buff",
    "ally_winds": "evaluate_ally_winds",
}

IN_WHEEL_RULE = (
    "An ability is IN THE ABILITY WHEEL if all three hold: "
    "(1) CARRIER - the engine classifies it as a unit-carried ability: unit_abilities.source_type "
    "in {active, bound, lord, character, unit, item, rune, weapon}; "
    "(2) DRAWABLE - unit_abilities.icon_name is non-empty, is_hidden_in_ui = false, and the key has a "
    "row in unit_special_abilities (a real battle ability with phases, not a campaign command); "
    "(3) NOT AN OFF-WHEEL FAMILY - it is none of: a spell (source_type = spell), a cataclysm spell "
    "(source_type = cataclysm), an army-bar ability (source_type = army), or the quest-battle army "
    "ability (source_type = quest). "
    "Off-wheel => EXCLUDED. Everything else => IN-WHEEL.")

ABSENCES = [
    ("No firing read",
     "The battle-script API exposes no per-unit 'is firing / is shooting' read. is_under_missile_attack "
     "answers whether the unit is TAKING fire (the wrong direction), current_target proves nothing "
     "about firing, and ammo_left is a 'has fired at some point' count. Consequence: the shooting half "
     "of the Enchanted Metallurgy trigger could not be built; the enemy triggers use 'under missile "
     "fire' as the only available proxy."),
    ("No cooldown read",
     "There is no per-unit read of a special ability's remaining cooldown, readiness or active state. "
     "can_perform_special_ability is the only read, and it answers true while the engine is refusing "
     "the cast. Consequence: a pair can only LEARN a cooldown from the engine's refusal, which is why "
     "the mod carries the 2 s guard and the 8 s / 20 s back-off instead of a timer."),
    ("No area-contents read",
     "There is no read of which units stand inside a cone, blast or vortex patch. The enemy-ground "
     "route lets a trigger place a POINT, not a shape, and nothing can prove the area is clear. "
     "Consequence: friendly-fire-heavy delivery families cannot be gated on 'no allies in the area'."),
    ("No enemy-spell-cast event",
     "There is no event for an enemy casting a spell. Consequence: abilities whose purpose is to react "
     "to an enemy spell cast (e.g. Enkhil's Kanopi) have no readable condition and stay unimplemented."),
]

FIELD_NOTES = [
    ("Category / Targeting Type",
     "unit_abilities.type -> unit_ability_types_onscreen_name_<type> (the game's own category label, "
     "e.g. 'Augment (Area)'), plus the targeting mode read from unit_special_abilities "
     "(target_self / target_friends / target_enemies / target_ground, affect_self)."),
    ("Uses", "unit_special_abilities.num_uses; -1 reads as 'unlimited'."),
    ("Damage Per Second",
     "special_ability_phases.damage_amount / hp_change_frequency, with max_damaged_entities stated. "
     "'-' when the phase carries no damage number (damage carried by a projectile / vortex / "
     "bombardment definition is not part of this extraction)."),
    ("Stat Modifiers",
     "special_ability_phase_stat_effects (stat rows, % or flat per the table's 'how'), "
     "phase_attribute_effects (attributes, with positive/negative state), the phase's heal amount and "
     "the ability's additional UI effects."),
    ("Duration", "unit_special_abilities.active_time in seconds; else the longest phase duration."),
    ("Radius / Effect Area",
     "unit_special_abilities.effect_range (the aura radius) plus the AoE template keys "
     "(targetting_aoe / active_aoe / passive_aoe) exactly as the table names them."),
    ("Movement Speed",
     "the speed-family stat rows of the phases (Speed, Charge Speed, Acceleration, Deceleration, Turn "
     "Speed) plus 'cannot move' / stance when the phase sets them."),
    ("Range",
     "unit_special_abilities.target_intercept_range, effect_range and min_range in metres; "
     "'no range column (unlimited / self)' where all three are zero."),
    ("Phase Durations", "special_ability_phases.duration for every phase of the ability, in order."),
    ("Cooldown", "unit_special_abilities.recharge_time in seconds."),
    ("Affects units if",
     "affect_self / always_affect_self, target_friends and num_effected_friendly_units, target_enemies "
     "and num_effected_enemy_units, only_affect_owned_units, only_affect_target, target_ground."),
    ("Can use if",
     "the invalid-usage flags of special_ability_to_invalid_usage_flags_tables, quoted by flag name as "
     "'not `flag`'. '-' when the ability carries none."),
    ("Tactical Overview",
     "the game's own guidance sentence for the ability's category: "
     "unit_ability_types_localised_description_<type>. Every one of the 1,797 keys has a type row, so "
     "this field is populated for all of them. There is no literal 'Tactical Overview' string in the "
     "extracted tables; the flavour paragraph (unit_abilities_tooltip_text_<key>) is deliberately NOT "
     "used anywhere in this workbook."),
]


def write_workbook(rows, path=OUT_XLSX):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    GREEN = PatternFill("solid", fgColor="E4F2DC")
    AMBER = PatternFill("solid", fgColor="FFF0CC")
    HEAD = PatternFill("solid", fgColor="3B2F1E")
    SUB = PatternFill("solid", fgColor="EFE6D2")
    WHITE = Font(color="FFFFFF", bold=True, size=10)
    BODY = Font(size=9)
    BOLD = Font(size=9, bold=True)
    thin = Side(style="thin", color="D9CFB8")
    BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
    TOP = Alignment(vertical="top", wrap_text=True)
    TOPC = Alignment(vertical="top", wrap_text=True, horizontal="center")

    wb = Workbook()

    # ------------------------------------------------------------------ Abilities
    ws = wb.active
    ws.title = "Abilities"
    cols = [
        ("Item #", 7, "item"),
        ("Ability name", 34, "name"),
        ("Ability key(s)", 48, "keys"),
        ("Category / Targeting Type", 34, "category"),
        ("Uses", 12, "uses"),
        ("Damage Per Second", 24, "dps"),
        ("Stat Modifiers", 44, "stats"),
        ("Duration", 12, "duration"),
        ("Radius / Effect Area", 30, "radius"),
        ("Movement Speed", 20, "speed"),
        ("Range", 34, "range"),
        ("Phase Durations", 22, "phase_durations"),
        ("Cooldown", 13, "cooldown"),
        ("Affects units if", 28, "affects"),
        ("Can use if", 26, "can_use"),
        ("Tactical Overview", 50, "tactical"),
        ("Tooltip (full)", 78, "tooltip_full"),
        ("Status", 12, "status"),
        ("Status reason / family", 38, "reason"),
        ("Implementation", 22, "impl"),
        ("Trigger family", 20, "family"),
        ("Trigger (as implemented)", 100, "trigger"),
        ("Restrictions", 42, "restrictions"),
    ]
    ws.append([c[0] for c in cols])
    for i, (title, width, key) in enumerate(cols, 1):
        cell = ws.cell(row=1, column=i)
        cell.fill = HEAD
        cell.font = WHITE
        cell.alignment = Alignment(vertical="center", wrap_text=True, horizontal="center")
        ws.column_dimensions[get_column_letter(i)].width = width
    ws.row_dimensions[1].height = 34

    for r in rows:
        vals = []
        for title, width, key in cols:
            if key == "tooltip_full":
                vals.append(tooltip_full(r["rec"]))
            elif key in ("item", "name", "keys", "status", "reason", "impl", "family",
                         "trigger", "restrictions"):
                vals.append(r[key])
            else:
                vals.append(r["rec"][key])
        ws.append(vals)
        rn = ws.max_row
        tl = len(r["trigger"]) if r["trigger"] and r["trigger"] != "-" else 0
        ws.row_dimensions[rn].height = max(30, min(100, 14 + 12 * math.ceil(tl / 100.0)))
        impl = r["impl"]
        for ci in range(1, len(cols) + 1):
            cell = ws.cell(row=rn, column=ci)
            cell.font = BODY
            cell.alignment = TOPC if ci in (1, 5, 8, 13, 18) else TOP
            cell.border = BOX
            if impl == "IMPLEMENTED":
                cell.fill = GREEN
            elif impl == "OUTSIDE-RULE-IMPLEMENTED":
                cell.fill = AMBER
        ws.cell(row=rn, column=1).number_format = "0"
        ws.cell(row=rn, column=20).font = BOLD
    ws.freeze_panes = "D2"
    ws.auto_filter.ref = "A1:%s%d" % (get_column_letter(len(cols)), ws.max_row)
    ws.sheet_view.zoomScale = 85

    # ------------------------------------------------------------------ Numbers
    ns = wb.create_sheet("Numbers")
    total = len(rows)
    exc = sum(1 for r in rows if r["status"] == "EXCLUDED")
    inc = total - exc
    impl_in = sum(1 for r in rows if r["impl"] == "IMPLEMENTED")
    impl_out = sum(1 for r in rows if r["impl"] == "OUTSIDE-RULE-IMPLEMENTED")
    notimpl = sum(1 for r in rows if r["impl"] == "NOT IMPLEMENTED" and r["status"] == "IN-WHEEL")
    assert (total, exc, inc, impl_in, notimpl, impl_out) == (1797, 639, 1158, 603, 555, 2), \
        (total, exc, inc, impl_in, notimpl, impl_out)

    ns.column_dimensions["A"].width = 5
    ns.column_dimensions["B"].width = 62
    ns.column_dimensions["C"].width = 12
    ns.column_dimensions["D"].width = 16
    ns.column_dimensions["E"].width = 18

    ns["A1"] = "WH3 - ABILITY COUNTS UNDER THE WHEEL-ONLY POLICY"
    ns["A1"].font = Font(bold=True, size=14)
    ns["A3"] = "Definition of IN-WHEEL (the single rule, replacing every earlier exclusion rule):"
    ns["A3"].font = Font(bold=True, size=10)
    ns["A4"] = IN_WHEEL_RULE
    ns.merge_cells("A4:E4")
    ns["A4"].alignment = Alignment(wrap_text=True, vertical="top")
    ns["A4"].font = Font(size=9)
    ns.row_dimensions[4].height = 76
    ns["A6"] = ("Numbers from docs/WH3_recount_wheel_only.md - recomputed from this workbook's own rows: "
                "the totals below are counted, not copied.")
    ns["A6"].font = Font(italic=True, size=9)
    ns["A7"] = "Date: %s     Rule in force since: 2026-10-17     Inventory: 1,797 active abilities" % TODAY
    ns["A7"].font = Font(bold=True, size=10)

    hdr = ["#", "Measure", "Absolute", "% of total (1,797)", "% of included (1,158)"]
    for i, h in enumerate(hdr, 1):
        c = ns.cell(row=9, column=i, value=h)
        c.fill = HEAD
        c.font = WHITE
        c.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")
        c.border = BOX
    ns.row_dimensions[9].height = 30

    table = [
        (1, "Total active abilities (the inventory)", total, 1.0, None),
        (2, "Excluded - not in the ability wheel", exc, exc / total, None),
        (3, "Included - in the ability wheel", inc, inc / total, 1.0),
        (4, "Implemented among the included", impl_in, impl_in / total, impl_in / inc),
        (5, "Not implemented among the included", notimpl, notimpl / total, notimpl / inc),
        (6, "Implemented but OUTSIDE the rule (reported separately)", impl_out, impl_out / total, impl_out / inc),
        (7, "All implemented in the mod (4 + 6)", impl_in + impl_out, (impl_in + impl_out) / total,
         (impl_in + impl_out) / inc),
    ]
    rn = 10
    for n, label, ab, pt, pi in table:
        ns.cell(row=rn, column=1, value=n).alignment = Alignment(horizontal="center")
        ns.cell(row=rn, column=2, value=label)
        c = ns.cell(row=rn, column=3, value=ab)
        c.number_format = "#,##0"
        c.alignment = Alignment(horizontal="right")
        c = ns.cell(row=rn, column=4, value=pt)
        c.number_format = "0.00%"
        c.alignment = Alignment(horizontal="right")
        c = ns.cell(row=rn, column=5, value=pi if pi is not None else "-")
        if pi is not None:
            c.number_format = "0.00%"
            c.alignment = Alignment(horizontal="right")
        if n in (1, 2, 3, 4, 5):
            for ci in range(1, 6):
                ns.cell(row=rn, column=ci).font = BOLD
        for ci in range(1, 6):
            ns.cell(row=rn, column=ci).border = BOX
        rn += 1

    rn += 1
    ns.cell(row=rn, column=1,
            value="Included, by carrier family (unit_abilities.source_type)").font = Font(bold=True, size=11)
    rn += 1
    for i, h in enumerate(["#", "Carrier family", "Included", "Implemented", "% of that family"], 1):
        c = ns.cell(row=rn, column=i, value=h)
        c.fill = SUB
        c.font = BOLD
        c.border = BOX
    rn += 1
    fam_rows = []
    for src in ("active", "bound", "rune", "item", "lord", "character", "unit", "weapon"):
        sub = [r for r in rows if r["src"] == src]
        fam_rows.append((src, len(sub), sum(1 for r in sub if r["impl"] == "IMPLEMENTED")))
    for i, (label, n, k) in enumerate(fam_rows, 1):
        ns.cell(row=rn, column=1, value=i).alignment = Alignment(horizontal="center")
        ns.cell(row=rn, column=2, value="%s" % label)
        c = ns.cell(row=rn, column=3, value=n)
        c.number_format = "#,##0"
        c = ns.cell(row=rn, column=4, value=k)
        c.number_format = "#,##0"
        c = ns.cell(row=rn, column=5, value=(k / n) if n else 0)
        c.number_format = "0.00%"
        for ci in range(1, 6):
            ns.cell(row=rn, column=ci).border = BOX
        rn += 1
    ns.cell(row=rn, column=2, value="Total included").font = BOLD
    c = ns.cell(row=rn, column=3, value=sum(x[1] for x in fam_rows))
    c.number_format = "#,##0"
    c.font = BOLD
    c = ns.cell(row=rn, column=4, value=sum(x[2] for x in fam_rows))
    c.number_format = "#,##0"
    c.font = BOLD
    for ci in range(1, 6):
        ns.cell(row=rn, column=ci).border = BOX
    rn += 2

    ns.cell(row=rn, column=1, value="The 639 exclusions, by family").font = Font(bold=True, size=11)
    rn += 1
    for i, h in enumerate(["#", "Family", "Keys", "% of total", "% of excluded"], 1):
        c = ns.cell(row=rn, column=i, value=h)
        c.fill = SUB
        c.font = BOLD
        c.border = BOX
    rn += 1
    exc_rows = [("spell", "Spells (source_type = spell)"),
                ("army", "Army-bar abilities (source_type = army)"),
                ("cataclysm", "Cataclysm spells (source_type = cataclysm)"),
                ("quest", "Quest-battle army ability (source_type = quest)")]
    for i, (src, label) in enumerate(exc_rows, 1):
        n = sum(1 for r in rows if r["src"] == src)
        ns.cell(row=rn, column=1, value=i).alignment = Alignment(horizontal="center")
        ns.cell(row=rn, column=2, value=label)
        c = ns.cell(row=rn, column=3, value=n)
        c.number_format = "#,##0"
        c = ns.cell(row=rn, column=4, value=n / total)
        c.number_format = "0.00%"
        c = ns.cell(row=rn, column=5, value=n / exc)
        c.number_format = "0.00%"
        for ci in range(1, 6):
            ns.cell(row=rn, column=ci).border = BOX
        rn += 1
    ns.cell(row=rn, column=2, value="Total excluded").font = BOLD
    c = ns.cell(row=rn, column=3, value=exc)
    c.number_format = "#,##0"
    c.font = BOLD
    for ci in range(1, 6):
        ns.cell(row=rn, column=ci).border = BOX
    rn += 2

    ns.cell(row=rn, column=1,
            value=("Reconciliation: included %d + excluded %d = %d; implemented in %d + implemented out %d = %d "
                   "(the whole mod); not implemented in wheel %d + implemented in wheel %d = %d included."
                   % (inc, exc, total, impl_in, impl_out, impl_in + impl_out, notimpl, impl_in, inc)))
    ns.cell(row=rn, column=1).font = Font(size=9)
    ns.merge_cells(start_row=rn, start_column=1, end_row=rn, end_column=5)
    ns.cell(row=rn, column=1).alignment = Alignment(wrap_text=True, vertical="top")
    ns.sheet_view.zoomScale = 100

    # ------------------------------------------------------------------ Changelog
    cs = wb.create_sheet("Changelog")
    for i, (h, w) in enumerate([("Date", 14), ("Version", 10), ("What changed", 110),
                                ("Who / what changed it", 46)], 1):
        c = cs.cell(row=1, column=i, value=h)
        c.fill = HEAD
        c.font = WHITE
        c.alignment = Alignment(vertical="center")
        cs.column_dimensions[get_column_letter(i)].width = w
    cs.append([TODAY, "v1",
               "initial master created from tracker + master DB + game-data extraction",
               "tools/build_abilities_master_xlsx.py (generated; sources: docs/WH3_ability_tracker.md, "
               "docs/WH3_ability_database_master.md, docs/WH3_recount_wheel_only.md, the mod's "
               "zz_test_deadly_onslaught.lua and the game tables under %LOCALAPPDATA%\\Temp\\wh3\\)"])
    for ci in range(1, 5):
        cs.cell(row=2, column=ci).alignment = Alignment(wrap_text=True, vertical="top")
        cs.cell(row=2, column=ci).border = BOX
    cs.row_dimensions[2].height = 60
    cs.freeze_panes = "A2"

    # ------------------------------------------------------------------ Definitions
    ds = wb.create_sheet("Definitions")
    ds.column_dimensions["A"].width = 30
    ds.column_dimensions["B"].width = 66
    ds.column_dimensions["C"].width = 46
    ds.column_dimensions["D"].width = 18
    ds.column_dimensions["E"].width = 12
    ds.column_dimensions["F"].width = 12

    row = 1
    ds.cell(row=row, column=1,
            value="DEFINITIONS - WH3 ability master v1 (%s)" % TODAY).font = Font(bold=True, size=14)
    row += 2
    ds.cell(row=row, column=1, value="1. THE IN-WHEEL RULE").font = Font(bold=True, size=11)
    row += 1
    ds.cell(row=row, column=1, value=IN_WHEEL_RULE)
    ds.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    ds.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical="top")
    ds.cell(row=row, column=1).font = Font(size=9)
    ds.row_dimensions[row].height = 70
    row += 1
    ds.cell(row=row, column=1,
            value=("Consequence: 639 abilities are out and 1,158 are in. Bound spells (176) are counted IN - a bound "
                   "spell is drawn as a button on the unit's bar with a charge count. Passives are not in the "
                   "inventory at all, so the rule says nothing about them."))
    ds.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    ds.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical="top")
    ds.cell(row=row, column=1).font = Font(size=9)
    ds.row_dimensions[row].height = 40
    row += 2

    ds.cell(row=row, column=1, value="2. STATUS VOCABULARY").font = Font(bold=True, size=11)
    row += 1
    for i, h in enumerate(["Status string", "What it means"], 1):
        c = ds.cell(row=row, column=i, value=h)
        c.fill = SUB
        c.font = BOLD
    row += 1
    status_vocab = [
        ("IN-WHEEL", "The ability is on the unit's ability bar under the rule above (1,158 rows). It is in scope."),
        ("EXCLUDED", "The ability is not on the ability bar (639 rows). The reason column names the off-wheel family: "
                     "spell (418), army (204), cataclysm (16), quest (1)."),
        ("IMPLEMENTED", "The ability is in the mod's ABILITIES table AND in the wheel (603 rows). The trigger column "
                        "states exactly what the evaluator does."),
        ("NOT IMPLEMENTED", "The ability is not in the mod's ABILITIES table (1,192 rows, of which 555 are in the wheel)."),
        ("OUTSIDE-RULE-IMPLEMENTED", "The ability is in the mod but NOT in the wheel - the two Ogre army abilities "
                                     "Meat Feast (wh3_main_prisoners_butcher) and Massacre (wh3_main_prisoners_massacre). "
                                     "They are reported, not hidden, and counted neither as progress under the rule nor "
                                     "as exclusions (2 rows)."),
        ("Trigger family", "The evaluator name the entry rides (a key of FOURTH.evaluators). '-' for rows that are not "
                           "implemented."),
        ("Trigger (as implemented)", "Every check and step the code performs, in order, for that row's evaluator, plus the "
                                     "row's own distance bound and the shared gate/guard/back-off pipeline. '-' for rows "
                                     "that are not implemented."),
    ]
    for a, bb in status_vocab:
        ds.cell(row=row, column=1, value=a).font = BOLD
        ds.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical="top")
        ds.cell(row=row, column=2, value=bb).alignment = Alignment(wrap_text=True, vertical="top")
        ds.cell(row=row, column=2).font = Font(size=9)
        ds.merge_cells(start_row=row, start_column=2, end_row=row, end_column=6)
        ds.row_dimensions[row].height = 34 if len(bb) < 160 else 48
        row += 1
    row += 1

    ds.cell(row=row, column=1,
            value="3. TRIGGER-FAMILY GLOSSARY (35 evaluators)").font = Font(bold=True, size=11)
    row += 1
    ds.cell(row=row, column=1,
            value=("One line per evaluator. The full per-row text in the Abilities sheet adds that row's own distance "
                   "bound and the shared pipeline. Every evaluator is a field of the FOURTH helper bag in "
                   "zz_test_deadly_onslaught.lua (section 7g and the CLASS A / CLASS B blocks)."))
    ds.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    ds.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical="top")
    ds.cell(row=row, column=1).font = Font(size=9)
    ds.row_dimensions[row].height = 32
    row += 1
    for i, h in enumerate(["Trigger family", "Evaluator (Lua)", "Rule (one line)", "Cast target", "Entries", "Keys"], 1):
        c = ds.cell(row=row, column=i, value=h)
        c.fill = SUB
        c.font = BOLD
        c.border = BOX
    row += 1
    fam_counts = collections.Counter(r["family"] for r in rows if r["family"] != "-")
    entries, _consts, _tips = bd.mod_entries()
    fam_entries = collections.Counter(e["trigger"] for e in entries)
    for fam in sorted(TRIGGERS, key=lambda f: (-fam_counts[f], f)):
        spec = TRIGGERS[fam]
        ds.cell(row=row, column=1, value=fam).font = BOLD
        ds.cell(row=row, column=2, value=FAM_EVAL.get(fam, "?"))
        ds.cell(row=row, column=3, value=spec["rule"])
        ds.cell(row=row, column=4, value=spec["target"])
        ds.cell(row=row, column=5, value=fam_entries.get(fam, 0)).alignment = Alignment(horizontal="right")
        ds.cell(row=row, column=6, value=fam_counts[fam]).alignment = Alignment(horizontal="right")
        for ci in range(1, 7):
            c = ds.cell(row=row, column=ci)
            c.border = BOX
            c.alignment = Alignment(wrap_text=True, vertical="top",
                                    horizontal="right" if ci in (5, 6) else "left")
            if ci != 1:
                c.font = Font(size=9)
        ds.row_dimensions[row].height = max(
            30, min(120, 14 + 12 * math.ceil(len(spec["rule"]) / 48.0)))
        row += 1
    ds.cell(row=row, column=1, value="TOTAL (all 35 evaluators)").font = BOLD
    ds.cell(row=row, column=5, value=sum(fam_entries.values())).font = BOLD
    ds.cell(row=row, column=5).alignment = Alignment(horizontal="right")
    ds.cell(row=row, column=6, value=sum(fam_counts.values())).font = BOLD
    ds.cell(row=row, column=6).alignment = Alignment(horizontal="right")
    for ci in range(1, 7):
        ds.cell(row=row, column=ci).border = BOX
    row += 2

    ds.cell(row=row, column=1, value="4. THE FOUR KNOWN ABSENCES").font = Font(bold=True, size=11)
    row += 1
    for a, bb in ABSENCES:
        ds.cell(row=row, column=1, value=a).font = BOLD
        ds.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical="top")
        ds.cell(row=row, column=2, value=bb).alignment = Alignment(wrap_text=True, vertical="top")
        ds.cell(row=row, column=2).font = Font(size=9)
        ds.merge_cells(start_row=row, start_column=2, end_row=row, end_column=6)
        ds.row_dimensions[row].height = 46
        row += 1
    row += 1

    ds.cell(row=row, column=1, value="5. TOOLTIP FIELD SOURCES").font = Font(bold=True, size=11)
    row += 1
    for i, h in enumerate(["Field", "Where the value comes from"], 1):
        c = ds.cell(row=row, column=i, value=h)
        c.fill = SUB
        c.font = BOLD
    row += 1
    for a, bb in FIELD_NOTES:
        ds.cell(row=row, column=1, value=a).font = BOLD
        ds.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical="top")
        ds.cell(row=row, column=2, value=bb).alignment = Alignment(wrap_text=True, vertical="top")
        ds.cell(row=row, column=2).font = Font(size=9)
        ds.merge_cells(start_row=row, start_column=2, end_row=row, end_column=6)
        ds.row_dimensions[row].height = 44
        row += 1
    row += 1

    ds.cell(row=row, column=1, value="6. BLANK-FIELD RULE").font = Font(bold=True, size=11)
    row += 1
    ds.cell(row=row, column=1,
            value=("'-' means the field is genuinely absent for that ability (e.g. no damage number, no invalid-usage "
                   "flag). 'unknown' means it could not be sourced at all. No value in this workbook is guessed: every "
                   "number is taken from the game's own tables or the mod's own source."))
    ds.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    ds.cell(row=row, column=1).alignment = Alignment(wrap_text=True, vertical="top")
    ds.cell(row=row, column=1).font = Font(size=9)
    ds.row_dimensions[row].height = 34

    wb.properties.title = "WH3 abilities master v1 (2026-10-17)"
    wb.properties.creator = "tools/build_abilities_master_xlsx.py"
    wb.save(path)
    return path


def main():
    rows = build_rows()
    p = write_workbook(rows)
    print("wrote", p, os.path.getsize(p), "bytes")
    return rows
