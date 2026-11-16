#!/usr/bin/env python3
"""Round 163: the tracker rows (26 implemented, 2 closed by the user) and section 10.41, and the database family texts.
The per-row numbers come from the GENERATED WW table and the game's ranges."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_ww_tables as GW  # noqa: E402

TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"
SRC = open(r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua", encoding="utf-8").read()
KF = GW.keys_in(SRC)
WW = GW.derive(KF)
USA = {r["key"]: r for r in GW.tsv("unit_spec_abil.tsv")}
NOTE = " · **round 163 (2026-11-16):** the placed areas, user ruling \"%s\"."
WANDER_KEYS = """wh2_dlc16_item_abilities_acorns_of_the_oak_of_ages wh3_main_item_abilities_deaths_head
wh3_main_weapon_abilities_frost_fang wh3_dlc23_item_abilities_hammer_of_smednir wh_dlc03_spell_bound_viletide
wh3_main_item_abilities_crackleblaze wh3_dlc24_unit_abilities_lampreys_bite wh3_dlc26_lord_abilities_boiling_cauldron
wh3_dlc26_lord_abilities_simmering_pot wh2_dlc12_character_abilities_brass_orb
wh2_dlc12_character_abilities_brass_orb_tech_lab_doom_flayer wh2_dlc12_character_abilities_brass_orb_upgrade
wh3_dlc20_spell_bound_infernal_gateway wh3_dlc27_spell_bound_pit_of_shades wh3_main_spell_bound_pit_of_shades
wh_dlc05_spell_shadow_pit_of_shades_bound wh2_main_spell_bound_rubric_of_dark_dimensions wh3_dlc29_spell_bound_plague
wh3_dlc29_spell_bound_plaguemaster wh3_dlc29_lord_abilities_warp_junction wh3_pro10_cataclysm_fire_magma_storm_bound
wh_main_spell_bound_chain_lightning_ror""".split()
assert len(WANDER_KEYS) == 22 and all(KF.get(k) == "enemy_wander" for k in WANDER_KEYS)
INSTANT = set(WANDER_KEYS[:7])


def bound(k):
    rng = float(USA[k]["target_intercept_range"])
    return None if rng <= 0 else int(math.floor(rng * 0.70 + 1e-9))


def where(k):
    b = bound(k)
    return "anywhere on the field (no range limit)" if b is None else "within %d m" % b


def wander_text(k):
    kind, r, path, off, buf, allies, ground = WW[k]
    if not allies:
        safe = "it cannot hurt our units, so no friendly test"
    else:
        safe = "none of our units (expendable and cheap ones ignored) within %g m of the target (radius %g + reach %d + 10 m)" % (
            r + buf + 10, r, buf)
    rule = ("Like Dwellers Below" if k in INSTANT else
            ("Wanderer rule" if k == "wh_main_spell_bound_chain_lightning_ror" else "Same as the blasts"))
    return ("implemented (blast on a standing blob: enemy_wander)",
            "When armed and standing still, casts at the standing enemy infantry %s worth the most whose %g m blast "
            "covers the blob line; %s." % (where(k), r, safe), rule)


ROWS = {k: wander_text(k) for k in WANDER_KEYS}
ROWS["wh2_main_character_abilities_arcane_vassal"] = (
    "implemented (our unit with the most enemies around: ally_blast)",
    "When armed, casts on our unit (or the caster) within 140 m whose 15 m blast circle covers the most enemy value "
    "(the blob line); the blast hits enemies only.", "Most enemies around")
ROWS["wh2_dlc16_character_abilities_befuddlement_of_mischiefs"] = (
    "implemented (enemy charging: enemy_fast_near_ally)",
    "When armed, casts on a fast enemy within 70 m closing on our units (freezes enemies within 35 m for 11 s; any "
    "enemy, flying or not).", "charge only; Any fast enemy")
ROWS["wh2_main_weapon_bound_winged_staff"] = (
    "implemented (most valuable infantry, standing still: enemy_area_drain)",
    "When armed and standing still, casts on the enemy infantry within 70 m worth the most per soldier that still has "
    "at least 25 soldiers (every strike lands).", "Area drain rule")
ROWS["wh3_main_weapon_abilities_siegebreaker"] = (
    "implemented (strike a standing single: enemy_strike)",
    "When armed and standing still, strikes the ground under the most valuable standing single-entity enemy within "
    "70 m (Lord, Hero, monster), with none of our units within 11 m.", "Strike a standing large single")
assert len(ROWS) == 26
CLOSE = {
    "wh_main_rune_abilities_rune_of_wrath_and_ruin": "an Anvil rune: casting it locks the Runelord's other runes for 60 s",
    "wh_dlc06_rune_abilities_master_rune_of_wrath_and_ruin": "an Anvil rune: casting it locks the Runelord's other runes "
                                                             "for 90 s",
}
SECTION = """

### 10.41 Round 163 - the placed areas and the expendable units (2026-11-16)

**Earlier status:** "excluded (auto: placed / static area damage (friendly fire, family decision 2026-10-09))", a RULE,
never a ruling on these 28 abilities one by one.

**Rulings (user, 2026-11-16).**

- **7 instant blasts:** "Like Dwellers Below" -> `enemy_wander` (static).
- **14 lingering areas:** "Same as the blasts" -> `enemy_wander`. Magma Storm's bombardment (60 m spread + 5 m blasts)
  sets its safety distance to 75 m.
- **Arcane Vassal:** "Most enemies around" -> NEW `ally_blast`.
- **The other 6, "Check one by one":** Befuddlement of Mischiefs "charge only" + "Any fast enemy"
  (`enemy_fast_near_ally`); Winged Staff "Area drain rule" (`enemy_area_drain`); Chain Lightning (RoR) "Wanderer rule"
  (`enemy_wander`); Siegebreaker "Strike a standing large single" (NEW `enemy_strike`); the Rune and Master Rune of
  Wrath & Ruin closed (`rejected`).
- **Expendable units** ("the friendly fire checks skipped these units" -> "Game's set + cheap undead"): every friendly-fire
  check ignores our units the game marks expendable (48, GENERATED) and our units worth less than 2 per soldier.

**Corrections found this round:** Hell Hammer (round 162) also drops a 14 m bombardment blast; its corridor radius is
now 14.1 m (the old corridor already covered it by 1 m).

**Arithmetic.**

- **Rows:** implemented 949 + 26 = **975 rows / keys**; not implemented among the included 174 - 28 = **146**, of which
  34 + 2 = 36 are the user's skips.
- **The mod:** 892 + 26 = **918 entries / 975 keys**; **92** families.
- **Tests:** harness 162 full suite **6,892 checks / 0 failures**, run twice byte-identical. RED 16/16.
- **Install:** pack md5 `66cb4f7ca1ddde52d5af56937ec740d4`.
"""
s = open(TRACKER, encoding="utf-8", newline="").read()
lines = s.split("\n")
done = set()
for i, l in enumerate(lines):
    if not l.startswith("| "):
        continue
    first = l.split("|")[1].strip()
    for k in list(ROWS) + list(CLOSE):
        if first.endswith("`%s`" % k):
            assert k not in done, k
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            if k in ROWS:
                st, pr, rule = ROWS[k]
                c[1] = "`%s`" % st
                c[3] = pr
                c[4] = c[4] + NOTE % rule
            else:
                c[1] = "`rejected (user 2026-11-16: \"Close the runes\"; %s)`" % CLOSE[k]
                c[3] = "Not automated (user decision 2026-11-16)."
                c[4] = c[4] + NOTE % "Close the runes"
            lines[i] = "| " + " | ".join(c) + " |"
            done.add(k)
want = set(ROWS) | set(CLOSE)
assert done == want, sorted(want - done)
s = "\n".join(lines)
assert "### 10.41" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION and all("\u2014" not in t for v in ROWS.values() for t in v)
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.41" % len(done))
d = open(DBB, encoding="utf-8", newline="").read()
OLD = '        "enemy_wavering": '
NEW = ('        "enemy_strike": "The caster STANDING STILL; the most valuable STANDING single-entity enemy in range (Lord, '
       'Hero, monster) with none of our units within the strike\'s blast + 10 m; cast on the ground under it (the game '
       'refuses a unit target unless it climbs, mans equipment or stands on a platform). Re-checked before the cast.",\n'
       '        "ally_blast": "Our unit (or the caster) within the 70% ally bound whose blast circle covers the most enemy '
       'value (the blob value and density line); cast on that unit (the blast hits enemies only).",\n' + OLD)
assert d.count(OLD) == 1 and '"enemy_strike":' not in d
d = d.replace(OLD, NEW)
open(DBB, "w", encoding="utf-8", newline="").write(d)
print("database builder: 2 family texts")
