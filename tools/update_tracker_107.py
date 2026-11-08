# -*- coding: utf-8 -*-
"""Round 107 tracker update: the remaining bombardment work."""
import re

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
s = open(P, encoding="utf-8").read()
orig_len = len(s)

AIR = [
    "wh2_dlc09_unit_abilities_death_from_above",
    "wh2_main_unit_abilities_drop_rocks",
    "wh2_dlc12_unit_abilities_drop_rocks_character",
    "wh2_dlc12_unit_abilities_drop_rocks_of_chotec",
    "wh2_dlc12_unit_abilities_drop_rocks_of_sundering",
    "wh2_dlc12_lord_abilities_drop_sphere_of_tepok",
    "wh2_dlc12_lord_abilities_drop_sphere_of_tepok_upgraded",
    "wh3_dlc25_unit_abilities_gyrobomber_fire_bomb",
    "wh3_dlc25_unit_abilities_thunderbarge_fire_bomb",
    "wh_main_unit_abilities_gyrobomber_bomb",
    "wh_main_unit_abilities_gyrocopter_bomb",
    "wh3_dlc25_unit_abilities_gyrocopter_bomb_anti_large",
    "wh3_main_unit_abilities_sky_junk_bomb",
    "wh_dlc06_unit_abilities_skyhammer_bomb",
    "wh_dlc06_unit_abilities_skyhammer_fire_bomb",
    "wh2_main_unit_abilities_wake_of_fire",
    "wh3_twa07_unit_abilities_searing_torrent",
    "wh3_dlc24_unit_abilities_nan_gau_grenades",
    "wh3_dlc29_unit_abilities_undeath_from_above",
]

CALL = "wh3_twa07_spell_bound_call_of_tor"

UPDATE = """
**Update 2026-10-18 (harness 107 — THE REMAINING BOMBARDMENT WORK).** Four user rulings are **implemented and shipping**. **(1) THE COUNT IS CORRECTED: the wheel bombardment set is 55, not 57.** 131 `wh_type_bombardment` rows sit in `unit_abilities.tsv`; 58 are unit-side with a real ability row, visible and drawable; **3 of those 58 are army-bar junctions** (Thorsen's Thunderstorm x2, Bubonic Broadside) — out of wheel scope — leaving **55**. The old 57 subtracted Bubonic Broadside only, so it still counted the two Thorsen army-bar keys. Of the 55: **54 implemented** (Soulfire, Arachneruption, the 30, Call of Tor, the 19 air-drop keys) and **1 awaiting a ruling** (Warp Lightning Rod — no target flags at all, range 0; two candidate rules are stated on its row). **(2) Call of Tor** (`wh3_twa07_spell_bound_call_of_tor`, Oath-Brothers of Tor War Bear Riders) rides the EXISTING **`melee_skip_commanders`** trigger exactly like Soulfire — the user's words: "Call of Tor looks very similar to Soulfire, so let's do the same trigger as a Soulfire." `melee_skip_commanders` now carries **3 entries / 4 keys**. **(3) THE 11 "ON TOP OF" ABILITIES — 12 entries / 19 keys — on the NEW trigger `air_drop_on_infantry`:** Death from Above, Drop Rocks (4 keys), Drop Sphere of Tepok (2 keys), Fire Bombs (2), Gyrobomber Bomb (2), Gyrocopter Bomb anti-large, Sky-Junk Bomb, Skyhammer Bomb (2), Wake of Fire, Searing Torrent, Nan-Gau Grenades, Undeath from Above (the Deck Droppers set `wh2_dlc11_cst_deck_droppers`, all four variants fly). Every one of those rows has **no target flags at all**, `effect_range 0`, `target_intercept_range 10` and `ai_usage always_use_only_land`: the engine drops where the **caster** is, so the only decision is WHEN. The rule: fire when an enemy **INFANTRY** unit is inside the ability's own **70% bound (7 m of its 10 m)** — `battle_unit:is_infantry()` first, `unit_class()` exact-match `inf_mel`/`inf_mis`/`inf_spr` second, **FAIL CLOSED** — with `unit_distance(caster)` as the "under the caster" **overlap proxy** (the blast radius is NOT in the extracted tables; **7 m is a constant, not a game radius**). The caster must be **airborne** where the row says so (the engine's `grounded` invalid-usage flag, or every carrier flying) and **out of melee** where the row says so (`engaged_in_melee`); both the caster and the chosen enemy are **re-read immediately before the cast** and the cast is skipped rather than spent. **Two documented exceptions:** Drop Sphere of Tepok (one lord key is a GROUND variant and the row declares no `grounded` flag) and Searing Torrent (a ground carrier — the user's field note is that it recharges in melee, so melee is never required, only excluded). **(4) THE WRAITH STORM / CAPTAIN ROTH'S MOONDIAL FIX — the PER-UNIT SERIALISATION WINDOW.** The field log shows the Moondial issued first at ~84 s (3 s wind-up), **Wraith Storm issued 0.25 s later on the same caster**, both accepted by the controller, and the Moondial's **120 s recharge consumed with no effect** — the engine allows **ONE special ability in flight per unit** and the second order replaces the first during its wind-up (the same order-replacement behaviour found for Nurgling Tide). There is **no shared cooldown in the data** (`shared_recharge_time -1` on both, different recharge times and use counts, no cooldown-group column, no exclusivity field). The fix: after any successful cast **no OTHER ability may be issued on that unit** for its own wind-up + 2 s, **never less than 2.5 s**; a repeat of the **same** ability does **not** extend the window, so a fast-repeating ability cannot starve the others. **Counts:** ABILITIES **675 -> 688 entries**, **721 -> 741 keys**, **45 -> 46 evaluators**; `air_drop_on_infantry` **12 entries / 19 keys**, `melee_skip_commanders` **3**. Spreadsheet: `docs/WH3_abilities_master_v8_2026-10-17.xlsx` (+ `.ods`; v8 supersedes v7; v1-v7 unchanged); research in `docs/WH3_bombardment_round2.md`; harness 107: **3939 checks / 0 failures**, red control 160 failures all accounted for; installed pack md5 `c44f38d415e3e1e2e7b0bfb886c41e8c`.
"""

anchor = "\n**Legend — Status column:**"
assert s.count(anchor) == 1
s = s.replace(anchor, UPDATE + anchor, 1)

# ---------------------------------------------------------------- the 19 rows
AIR_DESC = ("When armed, fires when an enemy INFANTRY unit is UNDER the caster (inside the ability's own 70% "
            "bound - 7 m of its 10 m) and the caster is airborne / out of melee where its row requires it; the "
            "cast is self-centred (on the owner).")
done = 0
for k in AIR:
    pat = re.compile(r"^\| ([^|]*?)`" + re.escape(k) + r"` \| `[^`]*` \| [^|]* \| [^|]* \| ([^|]*)\|$", re.M)
    m = pat.search(s)
    assert m, "row not found: " + k
    details = m.group(2).strip()
    if "round 107" not in details:
        details = details + " · **round 107 (2026-10-18):** implemented (harness 107)"
    row = "| %s`%s` | `implemented (air drop on infantry)` | air_drop_on_infantry | %s | %s |" % (
        m.group(1), k, AIR_DESC, details)
    s = s[:m.start()] + row + s[m.end():]
    done += 1
assert done == 19, done

# ---------------------------------------------------------------- Call of Tor
_DEC_OLD = ("- Decision: **skipped (unsuitable: bombardment/ranged)** — collection-time: unsuitable "
            "(bombardment/ranged); no automatic logic.")
_DEC_NEW = ("- Decision: **implemented (melee, skipping Lord/Hero-only fights)** — round 107 (2026-10-18): "
            "the user's ruling, verbatim: \"Call of Tor looks very similar to Soulfire, so let's do the same "
            "trigger as a Soulfire.\" It rides `melee_skip_commanders`; its row is self-centred (all four "
            "target flags false, range 0), so the cast is on the owner and the judged engagement set is logged.")
_ci = s.index("**272. Call of Tor**")
_cj = s.index("\n\n", _ci)
_block = s[_ci:_cj]
assert _DEC_OLD in _block, _block[:300]
s = s[:_ci] + _block.replace(_DEC_OLD, _DEC_NEW, 1) + s[_cj:]

# the §3a row, right after Soulfire's
soul_pat = re.compile(r"^\| Soulfire `wh_main_spell_bound_soulfire` \|.*\n", re.M)
m = soul_pat.search(s)
assert m, "the Soulfire §3a row is missing"
call_row = ("| Call of Tor `wh3_twa07_spell_bound_call_of_tor` | `implemented (melee, skipping Lord/Hero-only "
            "fights)` | melee_skip_commanders | When armed, fires when THIS unit is in melee, unless every "
            "enemy it is engaged with is a Lord or Hero (the engagement set is read from the enemy enumerator: "
            "alive + is_in_melee + edge-to-edge unit_distance <= 12 m, each member classified with the 1,409-key "
            "commander set, fail-closed; the judged set is logged); the cast is on the OWNER (the row is "
            "self-centred). | cd 90s · 7s · self · unlimited uses · wind-up 1s · bound · triage-family: "
            "Bombardment / ground artillery · **round 107 (2026-10-18):** implemented (harness 107) |\n")
s = s[:m.end()] + call_row + s[m.end():]

# ---------------------------------------------------------------- glossary
gl = ("| `melee_skip_commanders` | **round 106** - the caster is IN MELEE, unless EVERY enemy it is engaged "
      "with is a Lord or Hero (the engagement set = alive + is_in_melee + edge-to-edge `unit_distance` <= 12 m, "
      "each classified with the 1,409-key commander set; logged, deduped by note) | self cast "
      "(`perform_special_ability(key, self)`) |")
assert s.count(gl) == 1
s = s.replace(gl, gl.replace("**round 106**", "**rounds 106-107** - Soulfire, Arachneruption, Call of Tor:"))

gl_anchor = "| `melee_skip_commanders` |"
i = s.index(gl_anchor)
j = s.index("\n", i)
new_gl = ("\n| `air_drop_on_infantry` | **round 107** - an enemy INFANTRY unit is UNDER the caster: inside "
          "the ability's own 70% bound (7 m of the row's 10 m) measured by `unit_distance(caster)` as the "
          "overlap proxy, with `is_currently_flying()` enforced where the row declares `grounded` (or every "
          "carrier flies) and `is_in_melee()` == false where the row declares `engaged_in_melee`; both the "
          "caster and the chosen enemy are re-read immediately before the cast | self cast "
          "(`perform_special_ability(key, self)` - the rows have no target flags at all) |")
s = s[:j] + new_gl + s[j:]

open(P, "wb").write(s.encode("utf-8"))
print("tracker:", orig_len, "->", len(s), "| air rows", done)
