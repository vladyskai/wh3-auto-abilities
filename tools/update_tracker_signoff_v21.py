#!/usr/bin/env python3
"""Tracker edits for the v21 sign-off (rounds 122 and 123). LF file, binary-safe.

1. 21 rows -> implemented, each with the status of the family it rides, and a
   note appended to its last cell naming the round, the trigger and why.
2. Daemonic Possession -> rejected (user decision, round 123).
3. The 4 rows whose EARLIER decision the round-122/123 approval superseded
   (Call for Power, Manus of Ursun, All-Consuming Hatred, Seductive Glory) say
   so explicitly: the user ruled on 2026-10-28 to keep them (they start unarmed).
4. A new section 10.10 recording both rulings, the new enemy_melee trigger and
   the arithmetic. Nothing else is touched; the row count stays the same.
"""
import hashlib
import re

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"

S_MU = "implemented (in-melee self)"
S_CM = "implemented (charge and in-melee)"
S_EM = "implemented (enemy-targeted: in-melee only)"
S_EG = "implemented (enemy-targeted: in-melee / under-fire)"
S_DP = "rejected (only useful just before a friendly spell)"

R122 = "round 122 (2026-10-27)"
R123 = "round 123 (2026-10-27)"
ROWS = {
    # key: (status, note)
    "wh3_main_daemon_head_abilities_call_for_power": (S_MU, R122 + ": IMPLEMENTED on melee_unwavering (self-cast melee damage buff)"),
    "wh3_main_weapon_abilities_ursuns_claws": (S_MU, R122 + ": IMPLEMENTED on melee_unwavering (self-cast melee damage buff)"),
    "wh3_dlc23_weapon_abilities_black_hammer_of_hashut": (S_MU, R122 + ": IMPLEMENTED on melee_unwavering (self-cast melee damage buff)"),
    "wh3_dlc23_weapon_abilities_the_graven_sceptre": (S_MU, R122 + ": IMPLEMENTED on melee_unwavering (self-cast melee damage buff)"),
    "wh3_cp1_weapon_abilities_tyrants_talon": (S_MU, R122 + ": IMPLEMENTED on melee_unwavering (self-cast melee damage buff; the old 'vortex' auto-label was wrong)"),
    "wh3_dlc29_item_abilities_crimson_blade": (S_MU, R122 + ": IMPLEMENTED on melee_unwavering (self-cast Executioner)"),
    "wh2_dlc14_lord_abilities_bloodstorm": (S_MU, R122 + ": IMPLEMENTED on melee_unwavering (self-cast melee survival buff; the old 'vortex' auto-label was wrong)"),
    "wh3_dlc23_hero_abilities_crooked_dice": (S_MU, R122 + ": IMPLEMENTED on melee_unwavering (self-cast melee survival buff)"),
    "wh3_dlc20_lord_abilities_temptator": (S_MU, R122 + ": IMPLEMENTED on melee_unwavering (self-cast melee survival buff)"),
    "wh3_dlc27_unit_abilities_consuming_hatred": (S_MU, R122 + ": IMPLEMENTED on melee_unwavering (self-cast melee reflection)"),
    "wh2_main_item_abilities_rival_hide_talisman": (S_MU, R123 + ": IMPLEMENTED on melee_unwavering (enemy melee attack -40 aura, no speed effect)"),
    "wh3_main_lord_abilities_seductive_glory": (S_MU, R123 + ": IMPLEMENTED on melee_unwavering (enemy melee defence aura, no speed effect)"),
    "wh2_dlc15_item_abilities_vine_dragon_scale": (S_MU, R123 + ": IMPLEMENTED on melee_unwavering (enemy melee defence aura, no speed effect)"),
    "wh3_dlc23_weapon_abilities_dark_mace": (S_MU, R123 + ": IMPLEMENTED on melee_unwavering (enemy armour aura, no speed effect)"),
    "wh2_dlc11_lord_abilities_seduction": (S_CM, R123 + ": IMPLEMENTED on charge_or_melee (reduces enemy speed: fires on the charge or in melee)"),
    "wh2_dlc11_lord_abilities_song_of_enthrallment": (S_CM, R123 + ": IMPLEMENTED on charge_or_melee (reduces enemy speed: fires on the charge or in melee)"),
    "wh_dlc06_unit_abilities_smoke_bomb": (S_CM, R123 + ": IMPLEMENTED on charge_or_melee (reduces enemy speed: fires on the charge or in melee)"),
    "wh3_main_character_abilities_no_escape": (S_EM, R123 + ": IMPLEMENTED on enemy_melee (melee defence -40 only matters in melee; bound 70 m; held 90 s per use)"),
    "wh3_dlc29_lord_abilities_transfix": (S_EM, R123 + ": IMPLEMENTED on enemy_melee (melee defence -40 + Silenced; bound 70 m; held 120 s per use; marker transfix_hex)"),
    "wh_pro01_lord_abilities_flash_bomb": (S_EM, R123 + ": IMPLEMENTED on enemy_melee (bound 52 m; a speed-based trigger may come later)"),
    "wh2_dlc17_character_abilities_hunter_of_champions_upgraded": (S_EG, R123 + ": IMPLEMENTED as the second key of the existing Hunter of Champions entry (enemy_engaged_or_shot, bound 70 m)"),
    "wh3_main_lord_abilities_daemonic_possession": (S_DP, R123 + ": REJECTED by the user: 'Daemonic possesion would make sense only before a cast, so I say we do not automate that one.'"),
}
SUPERSEDED = {
    "wh3_main_daemon_head_abilities_call_for_power": "rejected (rampage), user reason 'Rampage! (loss of control)'",
    "wh3_main_weapon_abilities_ursuns_claws": "rejected (rampage) under standing rule 4/7",
    "wh3_dlc27_unit_abilities_consuming_hatred": "rejected (drawback), user reason 'serious drawback (Melee Defence -12); player should decide'",
    "wh3_main_lord_abilities_seductive_glory": "skipped (revisit), user 'Skip for now.' (drawback + Rampage)",
}
SUP_NOTE = (" The earlier decision (%s) is SUPERSEDED: the round-122/123 proposal missed it, and on "
            "2026-10-28 the user ruled to keep the ability (it starts unarmed, M, so it fires only "
            "once the player clicks A).")

SECTION = """
### 10.10 Rounds 122 and 123 - ten melee buffs, the hex batch and the enemy_melee trigger (v21 sign-off, 2026-10-28)

**Round 122 ruling (2026-10-27), verbatim:** *"Approved as recommended: Group A on melee_unwavering, Group B on melee_unwavering. Implement as a tuning round."* Ten self-cast melee buffs on `melee_unwavering`: Call for Power, Manus of Ursun, Black Hammer of Hashut, The Graven Sceptre, Tyrant's Talon, The Crimson Blade, Bloodstorm, Crooked Dice, Temptator, All-Consuming Hatred.

**Round 123 ruling (2026-10-27), verbatim:** *"Of Group A, the ones that have no speed effects should have the melee_unwavering trigger. The ones that reduce the enemies speed should trigger in melee or when charging. This way we avoid the issue of fire on an enemy that is only passing by. Of Group B, they need more diversity. The one with effect only -40 melee defense makes sense only when the enemy is in melee. It does not make sense to activate it when the enemy is shot (please learn from this example). The Transfix (dlc29 key) should be the same, since a trigger for the Silenced condition would be hard to implement. Flash bomb can be the same, we might think later if a trigger that leverages its speed reduction makes sense. Daemonic possesion would make sense only before a cast, so I say we do not automate that one. Hunter of champions is okay for enemy_engaged_or_shot."*

- `melee_unwavering`: Rival Hide Talisman, Seductive Glory, Vine Dragon Scale, Dark Mace.
- `charge_or_melee`: Seduction, Song of Enthrallment, Smoke Bomb.
- **`enemy_melee` (NEW, the 46th family):** No Escape, Transfix (dlc29 hex key, marker `transfix_hex`), Flash Bomb. The shared enemy picker with the melee-only flag on: the closest enemy within the entry's own 70% bound that is IN MELEE; an enemy only under missile fire never qualifies; the pre-cast re-check skips the cast if the enemy left melee.
- Hunter of Champions: the upgraded key joined the existing entry (`enemy_engaged_or_shot`).
- Daemonic Possession: **rejected** (user decision).

**Earlier decisions superseded (user ruling 2026-10-28: keep all four).** The proposals for rounds 122 and 123 were built from the workbook, which does not carry the questionnaire decisions, so four earlier decisions were missed: Call for Power (rejected, Rampage), Manus of Ursun (rejected, Rampage rule), All-Consuming Hatred (rejected, drawback Melee Defence -12), Seductive Glory (skipped, "Skip for now"). Asked on 2026-10-28, the user chose to keep all four; every ability starts unarmed (M). Standing rule added to CLAUDE.md: read the tracker's decision for every ability before proposing it.

**Arithmetic.** Implemented rows 738 + 10 (round 122) + 11 (round 123: 10 entries + 1 twin key) = **759 rows / 759 keys**. The mod: 687 -> 697 -> **707 entries**, 738 -> 748 -> **759 keys**, 45 -> **46 trigger families**. Harness 122 full suite: **5,359 checks / 0 failures**, run twice byte-identical. Installed pack md5 `88890ada80776c18ba5e142eeb3d9ced`. Round docs: `docs/WH3_round122_melee_buffs.md`, `docs/WH3_round123_hex_batch.md`. Workbook: `docs/WH3_abilities_master_v21_2026-10-28.xlsx` (v21 supersedes v20; v1-v20 byte-unchanged).
"""

raw = open(P, "rb").read()
assert raw.count(b"\r") == 0, "the tracker must stay LF"
before = hashlib.md5(raw).hexdigest()
lines = raw.decode("utf-8").split("\n")
n_before = len(lines)
done = {}
for i, ln in enumerate(lines):
    if not ln.startswith("| "):
        continue
    cells = ln.split(" | ")
    m = re.search(r"`([^`]+)` *$", cells[0])
    if not m or m.group(1) not in ROWS:
        continue
    key = m.group(1)
    assert key not in done, ("duplicate row", key)
    status, note = ROWS[key]
    old = cells[1]
    assert old.startswith("`") and old.endswith("`") and not old.startswith("`implemented"), (key, old)
    cells[1] = "`%s`" % status
    tail = cells[-1]
    assert tail.endswith(" |"), (key, tail[-20:])
    extra = " · **%s**" % note
    if key in SUPERSEDED:
        extra += SUP_NOTE % SUPERSEDED[key]
    cells[-1] = tail[:-2] + extra + " |"
    lines[i] = " | ".join(cells)
    done[key] = old
assert sorted(done) == sorted(ROWS), sorted(set(ROWS) - set(done))

out = "\n".join(lines).rstrip("\n") + "\n" + SECTION
assert "\u2014" not in SECTION
open(P, "wb").write(out.encode("utf-8"))
print("tracker md5 before", before, "rows edited", len(done), "lines", n_before, "->", len(out.split("\n")))
for k, old in sorted(done.items()):
    print("  %-62s %s -> %s" % (k, old[:60], ROWS[k][0]))
