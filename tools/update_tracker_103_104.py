"""Fold rounds 103 (charge gate + health_pct) and 104 (in-flight gate + ally-aware
health) into docs/WH3_ability_tracker.md.  Idempotent-ish: asserts each target row
is found exactly once before rewriting.
"""
import re, sys, os

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
P = os.path.join(ROOT, "docs", "WH3_ability_tracker.md")
lines = open(P, encoding="utf-8").read().split("\n")

# ---------------------------------------------------------------- data
GROUND = [
    ("wh2_dlc10_item_abilities_star_of_avelorn", 15, 10),
    ("wh3_dlc24_lord_abilities_gulyas", 35, 24),
]
SELF = [
    ("wh3_main_character_abilities_salyaks_lullaby", 35, 24),
    ("wh3_main_character_abilities_locus_of_fecundity", 55, 38),
]
ALLY = [
    ("wh2_dlc16_item_abilities_berry_wine", 60, 42),
    ("wh2_dlc16_item_abilities_dreaming_ring_i", 200, 140),
    ("wh2_dlc16_item_abilities_dreaming_ring_ii", 200, 140),
    ("wh2_dlc16_item_abilities_dreaming_ring_iii", 200, 140),
    ("wh2_dlc16_spell_bound_earth_blood", 200, 140),
    ("wh3_main_spell_bound_earth_blood", 200, 140),
    ("wh3_dlc20_spell_bound_fleshy_abundance", 200, 140),
    ("wh2_dlc16_spell_bound_regrowth", 200, 140),
    ("wh2_main_spell_bound_radiant_gem_of_hoeth", 200, 140),
    ("wh3_dlc26_spell_bound_trollguts", 200, 140),
]
OWNER_ONLY = {
    "wh2_dlc11_lord_abilities_ghoul_king_of_ushoran": "self",
    "wh3_dlc29_hero_abilities_blood_chalice": "self",
    "wh3_dlc26_item_abilities_bugmans_xxxxxx": "self",
    "wh2_dlc09_item_abilities_hieratic_jar": "self",
    "wh_main_hero_abilities_immortal_will": "self",
    "wh3_dlc29_spell_bound_invocation_of_nehek": "self",
    "wh2_dlc16_unit_abilities_neuroparasites": "self",
    "wh2_main_lord_abilities_potion_of_charoi": "self",
    "wh_main_item_abilities_potion_of_healing": "self",
    "wh_main_item_abilities_regenerating_flesh": "self",
    "wh2_main_item_abilities_skalm": "self",
    "wh3_main_weapon_abilities_skars_kraken_killer": "self",
    "wh3_cp1_character_abilities_protection_prayer": "tiger",
    "wh_pro02_item_abilities_blood_chalice_of_bathori": "commander",
    "wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness": "undead",
    "wh3_dlc29_spell_bound_undeath_morkharn_breath_of_darkness_upgraded": "undead",
    "wh3_dlc25_item_abilities_necrotic_phylactry": "radius",
    "wh3_main_daemon_head_abilities_pestilent_regeneration": "radius",
    "wh3_main_item_abilities_saint_annushkas_finger_bone": "radius",
    "wh_main_item_abilities_scroll_of_power": "recharge",
}
REASONS = {
    "self": "the game's own effect text says (to self) - a self-only heal, nothing to be ally-aware about",
    "tiger": "reaches allies but `invalid_target = unit_is_not_tiger_warrior`; the mod has no Tiger Warrior key list",
    "commander": "reaches allies but `invalid_target = unit_is_not_commander_class`; a commander list is derivable "
                 "(`FOURTH.commander_keys`) but was not wired this round",
    "undead": "reaches allies but `invalid_target = living_unit` - the recipient must be undead and the mod has no "
              "undead key list",
    "radius": "reaches allies but `effect_range = 0` and no target flags - no measurable radius, so no honest "
              "distance test",
    "recharge": "a recharge buff, not a heal - an ally's health is the wrong trigger",
}

def family_blocks(fam):
    if fam == "ground":
        return (GROUND, "health_aura_ground",
                "When the OWNER or a friendly unit inside the ability's own reach (floor(effect_range x 0.70) = {new} m "
                "aura) is at or below 75% health: cast the GROUND form under the LOWEST-health qualifying ally. The "
                "owner's own arm is unchanged - below 75% she still casts at her own feet.",
                "ground cast under the chosen ally")
    if fam == "self":
        return (SELF, "health_aura_self",
                "When the OWNER or a friendly unit inside the aura (floor(effect_range x 0.70) = {new} m) is at or "
                "below 75% health: cast ON THE CASTER - a hurt ally only ARMS the trigger and is never the cast target.",
                "self-centred aura, cast on the caster")
    return (ALLY, "health_aura_ally",
            "When the OWNER or a friendly unit inside the ability's own 70% bound (floor(target_intercept_range x 0.70) "
            "= {new} m) is at or below 75% health: cast the UNIT form ON the LOWEST-health qualifying ally.",
            "unit cast on the chosen ally")


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def rebuild(c0, status, group, proposal, notes):
    return "| %s | `%s` | %s | %s | %s |" % (c0, status, group, proposal, notes)


def find_rows(key):
    hits = []
    for i, l in enumerate(lines):
        if not l.startswith("|"):
            continue
        c = cells(l)
        if c and re.search(r"`%s`" % re.escape(key), c[0]):
            hits.append(i)
    return hits


changed = 0
for fam in ("ground", "self", "ally"):
    blocks, group, tmpl, cast_note = family_blocks(fam)
    for key, old, new in blocks:
        hits = find_rows(key)
        assert len(hits) == 1, "%s -> %d rows" % (key, len(hits))
        i = hits[0]
        c = cells(lines[i])
        assert c[1].strip("`").startswith("implemented"), (key, c[1])
        proposal = tmpl.format(new=new)
        note = c[4]
        add = (" · **round 103:** the health read is `FOURTH.health_pct` (a real 0-100 %) - this row's <=75% line now "
               "compares a real percentage. · **round 104:** ALLY-AWARE - reach {} m -> **{} m** ({}); {} "
               "(new trigger `{}`).".format(old, new,
                                            "floor(effect_range x 0.70)" if fam != "ally" else "floor(target_intercept_range x 0.70)",
                                            cast_note, group))
        lines[i] = rebuild(c[0], "implemented (health<=75, ally-aware)", group, proposal, note + add)
        changed += 1
print("changed rows:", changed)

notes_only = 0
for key, why in OWNER_ONLY.items():
    hits = find_rows(key)
    assert len(hits) == 1, "%s -> %d rows" % (key, len(hits))
    i = hits[0]
    c = cells(lines[i])
    assert c[1].strip("`").startswith("implemented"), (key, c[1])
    add = " · **round 104:** stayed OWNER-ONLY - %s." % REASONS[why]
    lines[i] = rebuild(c[0], c[1].strip("`"), c[2], c[3], c[4] + add)
    notes_only += 1
print("owner-only notes:", notes_only)

# ---------------------------------------------------------------- top update paragraph
anchor = "**Update 2026-10-10 (annotated copy):**"
idx = next(i for i, l in enumerate(lines) if l.startswith(anchor))
para = (
    "**Update 2026-10-17 (harness 103-104 — charge gate, one health reader, in-flight gate, ally-aware health).** "
    "**103 (a) CHARGE GATE.** The engine answers `can_perform = true` and ACCEPTS a cast on a multi-USE ability whose "
    "pool is EMPTY (proved in the field: Nurgling Tide fired 55 times at a dead-even 2.0 s cadence, 42 of them into "
    "an empty pool, while its own button read `selected_inactive`). A firing-layer table `charge_gate.hold_s` now "
    "maps **every one of the 129 multi-use keys** to its own `recharge_time`, and after a successful cast the pair "
    "waits that many seconds - **one use per charge cycle**. Single-use abilities are untouched (the engine's own "
    "refusal brakes them, also proved in the same log). **(b) ONE HEALTH READER.** `HealthPercent` returns a **0..1 "
    "fraction**, not a percentage (`battle_unit:unary_hitpoints()` documents the same quantity as a 'unary fraction'; "
    "`unit_banner.twui.xml` feeds the context value into a fill bar and tests it against 1). `hp < 20` was therefore "
    "true for every unit in the game. **`FOURTH.health_pct`** now returns **0-100** (prefers `unit:unary_hitpoints()`, "
    "falls back to `HealthPercent` x100) and **all 11 call sites** route through it, so the Eye of Khorne 20 % finisher "
    "and every <=75 % heal compare real percentages. **104 (c) IN-FLIGHT GATE.** `perform_special_ability` issues an "
    "ORDER that replaces the unit's current one (the queued twin is documented to exist because the plain call does "
    "not queue), so a 2 s guard can cancel a 3-5 s wind-up mid-cast. `cast_gate.wind_up_s` carries **136 wind-up keys** "
    "from the game's own `wind_up_time`; after a cast the pair waits **wind-up + 2 s** (Nurgling Tide 3+2 = **5 s**). "
    "The 103 charge gate stays and is the longer hold where both apply. **(d) ALLY-AWARE HEALTH.** The health family "
    "read only the OWNER, so Star of Avelorn (a ground-targeted group heal, 15 m, 3 friendly units) fired at the "
    "caster's feet only. The family is now ally-aware: fire when **this unit OR a friendly unit inside the ability's "
    "own reach** is at or below 75 %, choose the **LOWEST-health** qualifying unit, and cast per the ability's own "
    "targeting - ground under that ally, unit form on that ally, or on the caster for a self-centred aura. Reach is "
    "data-derived (`floor(effect_range x 0.70)` for an aura, `floor(target_intercept_range x 0.70)` for a "
    "friend-targeted heal). **13 entries changed** (Star of Avelorn, Gulyas, Salyak's Lullaby, Locus of Fecundity, "
    "Berry Wine, Dreaming Ring I/II/III, Earth Blood, Fleshy Abundance, Regrowth, Radiant Gem of Hoeth, Trollguts); "
    "**20 stayed owner-only with recorded reasons** (12 self-only heals, 3 with no measurable radius, and the Tiger "
    "Warrior / commander-class / undead / recharge-buff rows). `ushoran_health` **33 -> 20**; new `health_aura_ground` "
    "**2**, `health_aura_self` **2**, `health_aura_ally` **9**; entries stay **642** and keys **682**. Full records: "
    "**§10.5** (round 103) and **§10.6** (round 104). Spreadsheet: `docs/WH3_abilities_master_v5_2026-10-17.xlsx` "
    "(v5 supersedes v4; v1-v4 unchanged). Installed pack md5 **`1d7c199208d3892881fb6dea2adfbfac`** (harness 104)."
)
lines.insert(idx, para)
lines.insert(idx + 1, "")

open(P, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("inserted update paragraph before line", idx)
