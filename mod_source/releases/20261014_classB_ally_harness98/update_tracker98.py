# -*- coding: utf-8 -*-
"""Update WH3_ability_tracker.md for round 98 (Class B).

  * a round-98 update note at the top;
  * each of the 17 newly-implemented abilities' 3a row: status -> implemented
    (ally-targeted: <family>), group -> ally_unit, the proposal names the new
    trigger + its own 70% bound, and the notes carry the round-98 tag;
  * Stay Here, I'll Get Help!'s row: the cast-target fix + its own 70% bound;
  * Meat Feast's row: `skipped (army-bar ability)` (standing rule 10);
  * the 15 ruling-needed abilities: a round-98 NEEDS A RULING note tag.
"""
import io, json, re, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "C:/Users/vlady/Desktop"
TRK = ROOT + "/WH3_ability_tracker.md"
NL = chr(10)

plan = json.load(io.open(ROOT + "/WH3_audit/_classB_impl_plan.json", encoding="utf-8"))
joined = json.load(io.open(ROOT + "/WH3_audit/_classB_joined.json", encoding="utf-8"))
marker_keys = {}
for x in joined:
    for m in x["mod_markers"]:
        marker_keys[m] = x["keys"]

FAM = {
    "ally_melee_buff": "ally buff - the CLOSEST ally in range; owner in melee (not routing / not wavering)",
    "ally_heal": "ally heal - the LOWEST-health ally in range at or below 75%",
    "ally_heal_melee": "ally heal - owner in melee (the melee+health gate), the LOWEST-health ally at or below 75%",
    "ally_wavering": "ally wavering - the CLOSEST WAVERING ally in range",
    "wavering_ally_range": "ally wavering - the picked WAVERING ally (the cast-target fix)",
}
GROUP = {"wavering_ally_range": "ally_unit"}
for p in plan:
    GROUP[p["trigger"]] = "ally_unit"

RULING = {
    "fury_of_khaine": "rule 14 - the effect applies Rampage!; the note keeps the charge_or_melee trigger, which is not one of the ally families",
    "overseer_of_the_unseen": "needs a non-commander / non-large TARGET-CLASS filter (no existing ally family)",
    "slezuzus_voice": "the audit note itself says 'flag for the user'",
    "gruts_sickle": "rule 14 - carries a health COST (drawback); the note says 'flag for the user'",
    "inspired_marksmanship_i": "needs a missile-capability target gate (no existing ally family)",
    "inspired_marksmanship_ii": "needs a missile-capability target gate (no existing ally family)",
    "inspired_marksmanship_iii": "needs a missile-capability target gate (no existing ally family)",
    "iron_hand_captain": "needs a 'morale at or below broken' target gate (no existing ally family)",
    "merciws_monstrous_regiment": "target_intercept_range = -1.0 (no real range) - no defensible 70% bound",
    "verminous_fury": "rule 14 - the effect applies Rampage! (it also grants Unbreakable; the Rampage flag wins)",
    "whiplash": "needs a non-commander / beast TARGET-CLASS filter (no existing ally family)",
    "makaissons_persuader": "needs a war-machine / artillery TARGET-CLASS filter (no existing ally family)",
    "reforge": "needs a Hell-Forged TARGET-CLASS filter (no existing ally family)",
    "remouldered": "needs a monster TARGET-CLASS filter (no existing ally family)",
    "restore": "needs a construct TARGET-CLASS filter (no existing ally family)",
}
ARMY = {"butcher": ("Meat Feast", "wh3_main_prisoners_butcher")}

lines = io.open(TRK, encoding="utf-8", newline="").read().split(NL)
# locate the 3a table region
start = next(i for i, l in enumerate(lines) if l.startswith("| Ability | Status | Group |"))
end = next(i for i, l in enumerate(lines) if l.startswith("### 3b."))

def patch_row(key, status, group, note_tag, label):
    """find the 3a row whose key cell carries `key` and patch it."""
    hits = 0
    for i in range(start, end):
        l = lines[i]
        if not l.startswith("| ") or ("`" + key + "`") not in l:
            continue
        parts = l.split(" | ")
        if len(parts) < 5:
            continue
        if status is not None:
            parts[1] = status
        if group is not None:
            parts[2] = group
        last = parts[-1]
        trail = "|" if last.rstrip().endswith("|") else ""
        body = last.rstrip()
        if trail:
            body = body[:-1].rstrip()
        if note_tag not in body:
            body = body + " · " + note_tag
        parts[-1] = body + " " + ("|" if trail else "")
        lines[i] = " | ".join(parts)
        hits += 1
    assert hits == 1, "%s: %d rows matched for %s" % (label, hits, key)
    print("  patched %-46s %s" % (key[:46], label))

print("== the implemented entries ==")
for p in sorted(plan, key=lambda q: q["num"]):
    m = p["marker"]
    keys = marker_keys[m]
    fam = FAM[p["trigger"]]
    tag = ("**round 98 (Class B):** casts ON THE CHOSEN ALLY - " + fam
           + "; own 70% bound = floor(" + str(p["real"]) + " * 0.70) = " + str(p["bound"])
           + " m (FOURTH.ALLY_CAST_R" + str(p["real"]) + "), offer test on unit:unit_distance only,"
           + " fresh caster+ally handles. Was " + ("a self-cast" if not p.get("existing")
                                                   else "the #250 cast-target gap"))
    st = "`implemented (ally-targeted: %s)`" % ("waver_ally" if p["trigger"] == "wavering_ally_range" else p["trigger"])
    prop = ("Cast on the chosen ally (" + fam + "); trigger range = " + str(p["bound"])
            + " m = 70% of the real target_intercept_range " + str(p["real"]) + " m.")
    patch_row(keys[0], st, GROUP[p["trigger"]], tag, "implemented " + m)

print("== the army-bar skip ==")
for m, (name, key) in ARMY.items():
    patch_row(key, "`skipped (army-bar ability)`", "army_bar",
              "**round 98 (Class B):** ARMY-BAR ability (standing rule 10) - SKIPPED, no Class-B ally logic added."
              " Evidence: the audit's own wording (\"An army-keyed single-target recover\"), the project's"
              " grouped grade `army` and the key's own audio field `wh3_main_army_ability_ogr_butcher`."
              " (The pre-existing `ushoran_health` self-cast entry is retained UNCHANGED by this round.)",
              "army-bar " + name)

print("== the ruling-needed entries ==")
for m, reason in sorted(RULING.items(), key=lambda kv: kv[0]):
    keys = marker_keys[m]
    patch_row(keys[0], None, None,
              "**round 98 (Class B): NEEDS A RULING** - " + reason + ".",
              "needs-ruling " + m)

# ---------------------------------------------------------------- top note
anchor = None
for i, l in enumerate(lines[:120]):
    if l.startswith("**Update 2026-10-") and i < 120:
        anchor = i
assert anchor is not None, "no update-note anchor found"
note = ("**Update 2026-10-14 (Class B IMPLEMENTATION ROUND - harness98):** the audit's **Class B**"
        " (ally-targeted effects cast on self; **34 entries**) was derived programmatically from"
        " `WH3_audit_report.md` and joined to the mod table and `unit_spec_abil.tsv`. Outcome:"
        " **17 implemented** on the mod's OWN ally picker (the `blood_sacrifice` / `eat_da_runts` shape)"
        " across **four new ally families** - `ally_melee_buff` 11 (Da Boss 'as a Plan!, Favour of the Fay,"
        " Helping Hand, Inspired Assault I/II/III, Inspired Defence I/II/III, Orcs are da Best!, Hellish"
        " Vigour), `ally_heal` 3 (Elvish Healing Herbs, Patch Up, Revivification Crystal), `ally_heal_melee` 1"
        " (Captain of the Phoenix Guard), `ally_wavering` 2 (Shock Collar, Where You Goin!?) - plus **1**"
        " (`Stay Here, I'll Get Help!`) whose ally pick already shipped and which now gains the CAST TARGET and"
        " its own 70% bound; **1 SKIPPED as an ARMY-BAR ability** (Meat Feast, standing rule 10); and **15"
        " left for a ruling** (rule-14 Rampage / drawback flags, unavailable target-class gates, or an"
        " undefined real range). Every implemented entry carries its OWN real `target_intercept_range`"
        " (`ally_range_real`) -> ONE named 70% constant per real range (5 constants: `FOURTH.ALLY_CAST_R50`=35,"
        " `R60`=42, `R75`=52, `R100`=70, `R150`=105, `floor(real*0.70)`); the offer test is"
        " `unit:unit_distance(ally)` <= that constant ONLY - **never** the engine's `unit_in_range` - and the"
        " cast goes through the **fresh-handle** route (the caster controller AND the chosen ally re-enumerated"
        " the SAME tick). `melee_unwavering` 383 -> 373, `charge_or_melee` 29 -> 26, `ushoran_health` 41 -> 38,"
        " `melee_health75` 2 -> 1; entries/keys unchanged (579 / 605). Harness98: **3186 checks, 0 failures**;"
        " red control vs the pre-edit snapshot: 3153 checks, 85 failures, 13/32 Class-B world results passing"
        " by design (all documented re-based pins).")
lines.insert(anchor, note)
lines.insert(anchor + 1, "")

io.open(TRK, "w", encoding="utf-8", newline="").write(NL.join(lines))
print("wrote", TRK, len(NL.join(lines)), "bytes")
