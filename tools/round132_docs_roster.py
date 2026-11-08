#!/usr/bin/env python3
"""Round 132: the tracker rows and section 10.13, and the database family texts."""
TRACKER = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
DBB = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_ability_database.py"

NOTE = " · **round 132 (2026-11-08):** %s"
AURA_ST = "implemented (melee or shooting aura: melee_or_shooting_aura)"
AURA_PR = ("When the caster or a friendly unit within 24 m (70% of the 35 m aura) is in melee, or the caster or a "
           "friendly unit within 24 m is shooting past its cast point: cast on self (the aura).")
AURA_NT = "audit batch 1, user ruling: \"%s\"."
ROWS = {}
for k in ("wh3_main_character_abilities_enchanted_metallurgy", "wh3_main_character_abilities_enchanted_metallurgy_flaming",
          "wh3_main_character_abilities_enchanted_metallurgy_piercing", "wh3_main_character_abilities_enchanted_metallurgy_poison",
          "wh3_main_lord_abilities_master_of_alchemy", "wh3_main_lord_abilities_master_of_alchemy_flaming",
          "wh3_main_lord_abilities_master_of_alchemy_piercing", "wh3_main_lord_abilities_master_of_alchemy_poison"):
    ROWS[k] = (AURA_ST, AURA_PR, AURA_NT % "Add the shooting half" + " The user's own 2026-10 rule completed: \"When self or ally in range in melee. When ally in range is shooting.\"")
for k in ("wh2_main_spell_bound_embers_of_the_phoenix", "wh2_main_item_abilities_dragonhorn"):
    ROWS[k] = (AURA_ST, AURA_PR, AURA_NT % "Same as Metallurgy")
for k in ("wh2_main_spell_bound_the_seerstaff_of_saphery", "wh3_main_spell_bound_harmonic_convergence"):
    ROWS[k] = ("implemented (melee or shooting, self or ally: melee_or_shooting_self_or_ally)",
               "When the caster is in melee (not wavering) or shooting past its cast point: cast on self; otherwise on "
               "the closest ally within 140 m (70% of 200 m) that is in melee or shooting.",
               AURA_NT % "Self, else an ally")
ROWS["wh_main_unit_abilities_boom"] = ("implemented (shooting: self_shooting)",
                                      "When the unit itself is shooting past its cast point: cast on self.",
                                      AURA_NT % "When it is shooting")
ROWS["wh3_dlc29_lord_abilities_gaze_of_usirian"] = (None, None,
    "patch 9.0.5 cut the reach from 100 m to 50 m: the bound is now 35 m (was 70 m, which would have made the caster walk).")
ROWS["wh3_dlc29_weapon_abilities_aken_seth_the_staff_of_pain"] = (None, None,
    "patch 9.0.5 gave it 3 uses (120 s recharge): a 120 s charge hold now applies.")
ROWS["wh3_dlc29_spell_bound_okkams_mindrazor"] = (None, None,
    "patch 9.0.5 removed its 1 s wind-up: the in-flight hold row is gone.")
ROWS["wh3_dlc29_hero_active_overseer_of_the_unseen"] = (None, None,
    "patch 9.0.5 forbids a flying target: a flying ally is skipped.")

SECTION = """

### 10.13 Round 132 - audit batch 1 and the patch-9.0.5 data fixes (2026-11-08)

**The loop (agreed 2026-11-08, `docs/WH3_process_proposal_2026-11-08.md`).** The audit
(`tools/audit_triggers.py`, `docs/WH3_trigger_audit_2026-11-08.md`) lists 101 candidates whose trigger
may not match their effect. Batch 1 is the group the user asked for.

**Rulings (2026-11-08), all as recommended.**

- **Enchanted Metallurgy and Master of Alchemy (8): "Add the shooting half".** This completes the
  user's own 2026-10 rule, *"When self or ally in range in melee. When ally in range is shooting."*
- **Embers of the Phoenix and Horn of Vaul: "Same as Metallurgy".**
- **The Seerstaff of Saphery and Harmonic Convergence: "Self, else an ally".**
- **Boom!: "When it is shooting".**

**New families.**

- `melee_or_shooting_aura` (10)
- `melee_or_shooting_self_or_ally` (2)
- `self_shooting` (1)

`metallurgy_melee` is left with no entries; its evaluator is the melee arm of `melee_or_shooting_aura`.

**Patch 9.0.5** (`docs/DRIFT_2026-11-08_patch905.md`).

- **Eternal Gaze:** reach 100 -> 50 m, so the bound is now 35 m.
- **Aken-seth:** 3 uses, so a 120 s charge hold now applies.
- **Okkam's Mindrazor:** no wind-up any more.
- **Overseer of the Unseen:** skips a flying ally.
- **Reload table:** regenerated (Stormfiend Windlaunchers 13 -> 14 s).

**Arithmetic.**

- **Rows:** implemented rows and keys unchanged at **752**.
- **The mod:** **700 entries / 752 keys** (unchanged). Families 52 -> **54** (+3 new, `metallurgy_melee`
  empty). melee_unwavering 354 -> 349.
- **Tests:** harness 131 full suite **5,699 checks / 0 failures**, run twice byte-identical. RED on the
  round-131 build: 10/10.
- **Install:** pack md5 `47efd2465d26047dde59f0fed6d03e51`.
"""


def rewrite(line, key, status, proposal, note):
    c = [x.strip() for x in line.strip().strip("|").split("|")]
    assert len(c) >= 5 and "`%s`" % key in c[0], (key, c[:2])
    if status:
        c[1] = "`%s`" % status
        c[2] = "ally_unit" if "self or ally" in status else "self"
    if proposal:
        c[3] = proposal
    c[4] = c[4] + NOTE % note
    return "| " + " | ".join(c) + " |"


lines = open(TRACKER, encoding="utf-8", newline="").read().split("\n")
done = set()
for i, l in enumerate(lines):
    if not l.startswith("| "):
        continue
    first = l.split("|")[1].strip()
    for k, (st, pr, nt) in ROWS.items():
        if first.endswith("`%s`" % k):
            assert k not in done, k
            lines[i] = rewrite(l, k, st, pr, nt)
            done.add(k)
assert done == set(ROWS), sorted(set(ROWS) - done)
s = "\n".join(lines)
assert "### 10.13" not in s
s = s.rstrip("\n") + SECTION
assert "\u2014" not in SECTION
open(TRACKER, "w", encoding="utf-8", newline="").write(s)
print("tracker: %d rows + section 10.13" % len(done))

d = open(DBB, encoding="utf-8", newline="").read()
OLD = '        "self_or_ally_shooting": "The caster SHOOTING'
NEW = ('        "melee_or_shooting_aura": "The Metallurgy melee rule (the owner in melee, or an ally in melee within 24 m), OR the owner or any unit within the aura bound shooting past its cast point. Casts on the unit itself (the aura).",\n'
       '        "melee_or_shooting_self_or_ally": "The owner in melee (not wavering) or shooting past its cast point: cast on itself. Otherwise the closest ally in range in melee or shooting: cast on that ally.",\n'
       '        "self_shooting": "The unit itself shooting past its cast point. Casts on the unit itself.",\n') + OLD
CT_OLD = '        "self_or_ally_shooting": "the caster when it shoots, otherwise the closest shooting ally",\n'
CT_NEW = CT_OLD + '        "melee_or_shooting_self_or_ally": "the caster in melee or when it shoots, otherwise the closest ally in melee or shooting",\n'
for a, b in ((OLD, NEW), (CT_OLD, CT_NEW)):
    assert d.count(a) == 1, a[:60]
    d = d.replace(a, b, 1)
open(DBB, "w", encoding="utf-8", newline="").write(d)
print("database builder: 3 family texts + 1 cast target")
