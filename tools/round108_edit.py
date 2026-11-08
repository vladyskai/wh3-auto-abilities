# -*- coding: utf-8 -*-
"""Round 108 - the 1 m air-drop test bound, and Warp Lightning Rod on Soulfire's trigger.

Applies ONE deterministic set of edits to BOTH the shipped source and the
annotated reference copy (same control flow, no log() in the annotated file).
Binary read/write so the shipped file stays LF (a text-mode write on Windows
would flip every newline to CRLF and break the build's byte-identity gate).

EDITS
  item 1  the air_drop_on_infantry overlap bound: 7 m (floor(10 x 0.70)) -> 1 m,
          a USER-CHOSEN TEST VALUE, wired through the one constant
          FOURTH.AIR_DROP_BOUND_M (the 70% table is bypassed for this family)
  item 2  Warp Lightning Rod (wh2_dlc16_unit_abilities_warp_lightning_rod) on
          melee_skip_commanders, exactly like Soulfire / Call of Tor, with the
          Clan Moulder Lobotomy mutation note; charge-gate 60 s and 1 s wind-up
  plus    the backup of the pre-108 files for the harness red control
"""
import hashlib
import os
import shutil

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
SRC = os.path.join(ROOT, "mod_source", "script", "battle", "mod", "zz_test_deadly_onslaught.lua")
ANN = os.path.join(ROOT, "docs", "WH3_auto_ability_annotated.lua")
BAK = os.path.join(ROOT, "docs", "backups", "round108")


def read(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8")


def write(p, s):
    data = s.encode("utf-8")
    assert b"\r" not in data, "CR found - refusing to write " + p
    with open(p, "wb") as f:
        f.write(data)


def must(s, old, n=1):
    c = s.count(old)
    assert c == n, "anchor count %d (want %d): %r" % (c, n, old[:120])
    return s


def apply(s, old, new, n=1):
    must(s, old, n)
    return s.replace(old, new)


# ---------------------------------------------------------------------------
# THE WARP LIGHTNING ROD ENTRY (after Call of Tor, before the 30-entry block)
# ---------------------------------------------------------------------------
WLR = '''\t-- ROUND 108 (item 2): WARP LIGHTNING ROD - the user's rule, verbatim:
\t-- "Warp Lightning Rod seems to be an effect no unit has by default, but
\t-- during the campaign some units can aquire it via mutation (Clan Moulder
\t-- Lobotomy augmentation). Let's treat it the same as Soulfire."
\t-- Its row is SELF-CENTRED exactly like Soulfire's (affect_self = true, all
\t-- four target flags false, target_intercept_range 0, effect_range 0) and it
\t-- calls a bombardment down around the caster, so it rides
\t-- melee_skip_commanders unchanged: in melee, unless every enemy engaged with
\t-- it is a Lord or a Hero. The judged engagement set is logged with every
\t-- member's type, commander flag and real distance - the same line Soulfire
\t-- writes - and the caster/enemy are re-read immediately before the cast.
\t--
\t-- ITS GRANT, WHICH EXPLAINS THE MISSING CARRIER: this key has NO carrier
\t-- junction row anywhere in the extracted data - no land_units / uset_ability
\t-- entry, only the ability row, its invalid-usage flag (`climbing`), its UI
\t-- effects and its loc line. It is NOT a default unit ability. In campaign it
\t-- is granted by the Clan Moulder LOBOTOMY augmentation (a mutation), which
\t-- is why no battle roster shows a carrier and why the pre-108 data sweep
\t-- found no junction. The entry still fires correctly because the mod arms
\t-- per unit on whatever key that unit actually owns at battle time.
\t{ marker = "warp_lightning_rod", name = "Warp Lightning Rod", trigger = "melee_skip_commanders",
\t\tbadge = "zz_auto_badge_warp_lightning_rod",
\t\tkeys = { "wh2_dlc16_unit_abilities_warp_lightning_rod" },
\t\tox = 0, oy = 0 },
'''


def edit(path):
    s = read(path)

    # ---------------------------------------------------------------- item 1a
    # the family table's header comment
    s = apply(
        s,
        "\t-- CASTER is, so the mod's only decision is WHEN. The rule: fire when an\n"
        "\t-- enemy INFANTRY unit is within the ability's own 70% bound (7 m) of the\n"
        "\t-- caster - the edge-to-edge overlap proxy - and the caster satisfies the\n",
        "\t-- CASTER is, so the mod's only decision is WHEN. The rule: fire when an\n"
        "\t-- enemy INFANTRY unit is within FOURTH.AIR_DROP_BOUND_M = **1 m** of the\n"
        "\t-- caster (round 108: the user's own test value, NOT the 70% rule) - the\n"
        "\t-- edge-to-edge overlap proxy - and the caster satisfies the\n")

    s = apply(
        s,
        "\t-- The blast radius is NOT in the extracted tables (the aoe key lives in\n"
        "\t-- an aoe table outside this extraction), so 7 m is a CONSTANT: the row's\n"
        "\t-- own 10 m cast range at the standing 70% rule. Not a game radius.\n",
        "\t-- The blast radius is NOT in the extracted tables (the aoe key lives in\n"
        "\t-- an aoe table outside this extraction), so the bound is a CONSTANT, not\n"
        "\t-- a game radius. It was the row's own 10 m cast range at the standing 70%\n"
        "\t-- rule (7 m) until round 108; the user field-tested the family and asked\n"
        "\t-- for 1 m, so 1 m is what ships. ONE constant - trivial to raise.\n")

    # ---------------------------------------------------------------- item 1b
    # the evaluator's header comment: the rule and the proxy
    s = apply(
        s,
        "-- THE RULE (user-approved): fire when an enemy INFANTRY unit is UNDER the\n"
        "-- caster - inside the ability's own 70% bound, floor(10 * 0.70) = 7 m, the\n"
        "-- constant FOURTH.AIR_DROP_BOUND_M - and the caster satisfies the usage\n"
        "-- restrictions its own row declares:\n",
        "-- THE RULE (round 108 amendment - THE BOUND IS 1 METRE, A USER-CHOSEN TEST\n"
        "-- VALUE): fire when an enemy INFANTRY unit is UNDER the caster - inside\n"
        "-- FOURTH.AIR_DROP_BOUND_M = 1 m, NOT floor(10 * 0.70) = 7 m - and the\n"
        "-- caster satisfies the usage restrictions its own row declares:\n")

    s = apply(
        s,
        "-- THE OVERLAP PROXY, STATED PLAINLY: the battle script API exposes no per-unit\n"
        "-- footprint and no blast radius, and the aoe key the row names\n"
        "-- (wh_abilities_bomb_drop / wh_abilities_bomb_small_drop) lives in a table\n"
        "-- this extraction does not carry. The ONE real read available is\n"
        "-- unit:unit_distance(caster) - EDGE-TO-EDGE metres (battle_unit.lua:160) - so\n"
        "-- \"under the caster\" is proxied by that gap being inside the 70% bound. 7 m is\n"
        "-- a CONSTANT (the row's own 10 m cast range at 70%), NOT the bomb's radius,\n"
        "-- and every log line that uses it says so.\n",
        "-- WHY 1 m (the user's words): \"I tested Drop Bombs but it released them too\n"
        "-- soon. Please make the range only 1 meter, I will test it again.\" The field\n"
        "-- log names the row tested: Drop Rocks (wh2_main_unit_abilities_drop_rocks,\n"
        "-- Terradon Riders) accepted its cast at 6.9 m and again at 6.0 m edge-to-edge,\n"
        "-- i.e. the old 7 m proxy fired while the flyer was still short of being over\n"
        "-- the target. 1 m is the user's own TEST VALUE and is MUCH TIGHTER than the\n"
        "-- standing 70% rule (which says 7 m). It is ONE constant: if the ability\n"
        "-- never fires in the field, the test is too tight - raise\n"
        "-- FOURTH.AIR_DROP_BOUND_M to 2, 3 or 5 m and nothing else changes.\n"
        "--\n"
        "-- THE OVERLAP PROXY, STATED PLAINLY: the battle script API exposes no per-unit\n"
        "-- footprint and no blast radius, and the aoe key the row names\n"
        "-- (wh_abilities_bomb_drop / wh_abilities_bomb_small_drop) lives in a table\n"
        "-- this extraction does not carry. The ONE real read available is\n"
        "-- unit:unit_distance(caster) - EDGE-TO-EDGE metres (battle_unit.lua:160) - so\n"
        "-- \"under the caster\" is proxied by that gap being inside the bound. Note what\n"
        "-- EDGE-TO-EDGE means for a 1 m test: a unit DIRECTLY under the caster should\n"
        "-- read NEAR 0-5 m, not 0 m - two overlapping bounding boxes still report the\n"
        "-- distance between their nearest edges, so a wide flyer over a wide infantry\n"
        "-- block can legitimately read a few metres while squarely on top of it. Every\n"
        "-- log line prints the real distance and the bound it was tested against.\n")

    # ---------------------------------------------------------------- item 1c
    s = apply(
        s,
        "FOURTH.AIR_DROP_BOUND_M = 7\n",
        "FOURTH.AIR_DROP_BOUND_M = 1\n")

    # ---------------------------------------------------------------- item 1d
    # THE WIRING: the 70% table must NOT bound this family any more. The
    # air-drop entries carry range_real = 10 (the row's real value), and the
    # generic mapping would put them back at 7 m, so the one constant is
    # applied directly - the single knob the release notes tell the user to bump.
    s = apply(
        s,
        "\tif ability.range_real ~= nil then\n"
        "\t\tability.range_m = FOURTH.ENEMY_CAST[ability.range_real]\n"
        "\tend\n",
        "\tif ability.range_real ~= nil then\n"
        "\t\tability.range_m = FOURTH.ENEMY_CAST[ability.range_real]\n"
        "\tend\n"
        "\t-- ROUND 108 (item 1): THE AIR-DROP FAMILY IS NOT BOUNDED BY THE 70%\n"
        "\t-- TABLE. Its entries carry the row's real 10 m range, which the map\n"
        "\t-- above would turn into 7 m; the user tested the family in the field\n"
        "\t-- (\"... it released them too soon. Please make the range only 1\n"
        "\t-- meter ...\"), so every air_drop_on_infantry entry takes the ONE\n"
        "\t-- user-chosen constant instead. Raise that constant to loosen the\n"
        "\t-- test - no per-entry edit is needed.\n"
        "\tif ability.evaluate == FOURTH.evaluate_air_drop_on_infantry then\n"
        "\t\tability.range_m = FOURTH.AIR_DROP_BOUND_M\n"
        "\tend\n")

    # ---------------------------------------------------------------- item 2
    s = apply(
        s,
        "\t{ marker = \"call_of_tor\", name = \"Call of Tor\", trigger = \"melee_skip_commanders\",\n"
        "\t\tbadge = \"zz_auto_badge_call_of_tor\",\n"
        "\t\tkeys = { \"wh3_twa07_spell_bound_call_of_tor\" },\n"
        "\t\tox = 0, oy = 0 },\n",
        "\t{ marker = \"call_of_tor\", name = \"Call of Tor\", trigger = \"melee_skip_commanders\",\n"
        "\t\tbadge = \"zz_auto_badge_call_of_tor\",\n"
        "\t\tkeys = { \"wh3_twa07_spell_bound_call_of_tor\" },\n"
        "\t\tox = 0, oy = 0 },\n" + WLR)

    # the charge gate: 3 uses, 60 s recharge (unit_spec_abil.tsv)
    s = apply(
        s,
        "\t\t[\"wh3_twa07_spell_bound_call_of_tor\"] = 90,\n",
        "\t\t[\"wh3_twa07_spell_bound_call_of_tor\"] = 90,\n"
        "\t\t-- ROUND 108: Warp Lightning Rod - 3 uses, 60 s recharge.\n"
        "\t\t[\"wh2_dlc16_unit_abilities_warp_lightning_rod\"] = 60,\n")

    # the in-flight gate: wind_up_time 1 s
    s = apply(
        s,
        "\t\t[\"wh3_twa07_spell_bound_call_of_tor\"] = 1,\n",
        "\t\t[\"wh3_twa07_spell_bound_call_of_tor\"] = 1,\n"
        "\t\t[\"wh2_dlc16_unit_abilities_warp_lightning_rod\"] = 1,\n")

    return s


for p in (SRC, ANN):
    os.makedirs(BAK, exist_ok=True)
    tag = "live" if p == SRC else "ann"
    dst = os.path.join(BAK, "pre108_%s.lua" % tag)
    if not os.path.exists(dst):
        shutil.copy2(p, dst)
    print("backup %-4s -> %s  md5 %s" % (tag, os.path.basename(dst),
          hashlib.md5(open(dst, "rb").read()).hexdigest()[:12]))

for p in (SRC, ANN):
    s = edit(p)
    write(p, s)
    print("edited", p, os.path.getsize(p), "bytes")
