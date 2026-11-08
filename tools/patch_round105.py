"""Round 105: add Tz'arkan (five keys, one entry) on the new health_below_15
trigger to the LIVE mod source and the ANNOTATED reading copy.

Binary read/write keeps LF byte-for-byte. Every anchor is asserted exactly once
so a drifted file fails loudly instead of silently mis-patching.
"""
import hashlib
import os

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
LIVE = os.path.join(ROOT, "mod_source", "script", "battle", "mod", "zz_test_deadly_onslaught.lua")
ANN = os.path.join(ROOT, "docs", "WH3_auto_ability_annotated.lua")

T1 = "wh2_dlc14_lord_abilities_tzarkan"
T2 = "wh2_dlc14_lord_abilities_tzarkan_mp"
T3 = "wh2_dlc14_lord_abilities_tzarkan_snikch"
T4 = "wh2_dlc14_lord_abilities_tzarkan_spite"
T5 = "wh2_dlc14_lord_abilities_tzarkan_spite_mp"


def read(p):
    with open(p, "rb") as fh:
        return fh.read().decode("utf-8")


def write(p, s):
    with open(p, "wb") as fh:
        fh.write(s.encode("utf-8"))


def rep(s, old, new, what, path):
    n = s.count(old)
    assert n == 1, "%s: anchor %r found %d times in %s" % (what, old[:60], n, os.path.basename(path))
    return s.replace(old, new)


def patch(path, is_live):
    s = read(path)
    before = hashlib.md5(s.encode("utf-8")).hexdigest()
    edits = 0

    # ---------------------------------------------------------------- 1. gates
    s = rep(s,
            "\t\t-- wind_up_time 1.9 s\n",
            "\t\t-- wind_up_time 1.5 s\n"
            "\t\t[\"" + T3 + "\"] = 1.5,\n"
            "\t\t-- wind_up_time 1.9 s\n",
            "wind-up 1.5 s group", path)
    edits += 1
    s = rep(s,
            "\t\t[\"wh2_dlc11_item_abilities_captain_roths_moondial\"] = 3,\n",
            "\t\t[\"wh2_dlc11_item_abilities_captain_roths_moondial\"] = 3,\n"
            "\t\t[\"" + T1 + "\"] = 3,\n"
            "\t\t[\"" + T2 + "\"] = 3,\n"
            "\t\t[\"" + T4 + "\"] = 3,\n"
            "\t\t[\"" + T5 + "\"] = 3,\n",
            "wind-up 3 s keys", path)
    edits += 1

    # ------------------------------------------------------- 2. the ABILITIES entry
    entry = (
        "\n"
        "\t-- ============================================================================\n"
        "\t-- TZ'ARKAN (this round) - FIVE keys, ONE entry, ONE new low-health trigger.\n"
        "\t-- The user's rule: \"I think it might make sense to activate Tz'arkan when\n"
        "\t-- caster health is below 15%, don't you think? Let's implement and test it.\"\n"
        "\t-- The five keys are the same transform in its five shipped forms (base, MP,\n"
        "\t-- Snikch's, and the spite form + its MP twin). They share ONE marker, badge,\n"
        "\t-- arming switch and back-off, exactly like the multi-key entries above.\n"
        "\t--\n"
        "\t-- KNOWN RISK, stated deliberately: a transform is very likely ONE-WAY, and\n"
        "\t-- these rows declare a 3 s wind-up (1.5 s for the Snikch key), so a caster at\n"
        "\t-- 14% can DIE inside that window before the transform resolves. The 15% line\n"
        "\t-- is the user's own rule and is ONE number (FOURTH.TZARKAN_PCT) - trivial to\n"
        "\t-- raise to 20% or 25% if field tests show deaths before the transform lands.\n"
        "\t-- ============================================================================\n"
        "\t{ marker = \"tzarkan\", name = \"Tz'arkan\", trigger = \"health_below_15\",\n"
        "\t\tbadge = \"zz_auto_badge_tzarkan\",\n"
        "\t\tkeys = {\n"
        "\t\t\t\"" + T1 + "\",\n"
        "\t\t\t\"" + T2 + "\",\n"
        "\t\t\t\"" + T3 + "\",\n"
        "\t\t\t\"" + T4 + "\",\n"
        "\t\t\t\"" + T5 + "\" },\n"
        "\t\tox = 0, oy = 0 },\n"
        "\n"
    )
    old_tail = (
        "\t{ marker = \"nurgling_tide\", name = \"Nurgling Tide\", trigger = \"self_summon_melee\",\n"
        "\t\tbadge = \"zz_auto_badge_nurgling_tide\",\n"
        "\t\tkeys = { \"wh3_main_lord_abilities_nurgling_tide\" },\n"
        "\t\tox = 0, oy = 0 },\n"
        "\n"
        "}\n"
    )
    s = rep(s, old_tail,
            "\t{ marker = \"nurgling_tide\", name = \"Nurgling Tide\", trigger = \"self_summon_melee\",\n"
            "\t\tbadge = \"zz_auto_badge_nurgling_tide\",\n"
            "\t\tkeys = { \"wh3_main_lord_abilities_nurgling_tide\" },\n"
            "\t\tox = 0, oy = 0 },\n"
            + entry + "\n}\n",
            "ABILITIES entry", path)
    edits += 1

    # --------------------------------------------- 3. the constant + the evaluator
    ev = (
        "\n"
        "-- TZ'ARKAN'S LOW-HEALTH TRIGGER (this round) - the user's rule: activate\n"
        "-- Tz'arkan when the caster's health is BELOW 15%. ONE entry carries all five\n"
        "-- Tz'arkan keys (base / MP / Snikch / spite / spite MP) on this one trigger.\n"
        "--\n"
        "-- The OWNER must be ALIVE (the poll already gated that), NOT routing, and its\n"
        "-- health - read through the ONE reader, FOURTH.health_pct, a real 0-100\n"
        "-- percent - must be BELOW the line. NEVER a raw HealthPercent read: that\n"
        "-- field answers a 0..1 FRACTION, so `hp < 15` on it would be true for every\n"
        "-- unit on the field (the round-103 field failure). The cast is on the OWNER\n"
        "-- ITSELF through the unit form, with the caster's controller re-fetched FRESH\n"
        "-- this tick; a self cast has NO range bound, so no distance is read.\n"
        "--\n"
        "-- THE THRESHOLD IS DELIBERATE (the user's own number, 2026-10-17). This\n"
        "-- transform is very likely ONE-WAY and its wind-up is 3 s (1.5 s for the\n"
        "-- Snikch key), so a caster at 14% may die before the transform resolves. It\n"
        "-- is ONE constant - raise FOURTH.TZARKAN_PCT if field tests show deaths\n"
        "-- inside the wind-up.\n"
        "FOURTH.TZARKAN_PCT = 15\n"
        "\n"
        "function FOURTH.evaluate_tzarkan_low_health(unit, routing)\n"
        "\tif routing then return nil end\n"
        "\tlocal hp = FOURTH.health_pct(unit)\n"
        "\tif type(hp) ~= \"number\" or hp >= FOURTH.TZARKAN_PCT then return nil end\n"
        "\t-- the cast is the OWNER: mark it and re-fetch the caster's controller FRESH\n"
        "\t-- this tick (a controller held from an earlier poll silently no-ops).\n"
        "\tFOURTH.tz_self = true\n"
        "\tFOURTH.tz_caster_su = FOURTH.eg_fresh_caster_su(unit)\n"
        "\treturn string.format(\"health %.1f%% (BELOW the %d%% line) - one-way transform, cast on SELF\",\n"
        "\t\thp, FOURTH.TZARKAN_PCT)\n"
        "end\n"
    )
    old_ev = (
        "-- THE ENEMY HEALTH READ (percent, 0-100): the ONE reader above.\n"
        "function FOURTH.enemy_health_pct(enemy)\n"
        "\treturn FOURTH.health_pct(enemy)\n"
        "end\n"
    )
    s = rep(s, old_ev, old_ev + ev, "evaluator block", path)
    edits += 1

    # ------------------------------------------------------- 4. the two registries
    s = rep(s,
            "\tself_summon_melee = FOURTH.evaluate_self_summon_melee,\n",
            "\tself_summon_melee = FOURTH.evaluate_self_summon_melee,\n"
            "\t-- TZ'ARKAN (this round): the low-health self transform.\n"
            "\thealth_below_15 = FOURTH.evaluate_tzarkan_low_health,\n",
            "evaluator map", path)
    edits += 1
    s = rep(s,
            "\tself_summon_melee = \"When armed, fires when this unit itself is fighting in melee and the summon is cast on it\",\n",
            "\tself_summon_melee = \"When armed, fires when this unit itself is fighting in melee and the summon is cast on it\",\n"
            "\thealth_below_15 = \"When armed, fires when this unit is below 15% health\",\n",
            "TRIGGER_TIP", path)
    edits += 1

    # ---------------------------------------------------- 5. the slot declarations
    s = rep(s,
            "\nFOURTH.ss_self = nil\nFOURTH.ss_caster_su = nil\n",
            "\nFOURTH.ss_self = nil\nFOURTH.ss_caster_su = nil\n"
            "-- TZ'ARKAN (this round): the low-health self-transform arm's own flag and\n"
            "-- the freshly re-fetched caster script_unit. Cleared before every evaluate.\n"
            "FOURTH.tz_self = nil\nFOURTH.tz_caster_su = nil\n",
            "global slot init", path)
    edits += 1
    s = rep(s,
            "\t\t\t\t\tFOURTH.ss_self = nil\n\t\t\t\t\tFOURTH.ss_caster_su = nil\n",
            "\t\t\t\t\tFOURTH.ss_self = nil\n\t\t\t\t\tFOURTH.ss_caster_su = nil\n"
            "\t\t\t\t\t-- TZ'ARKAN (this round): the self-transform slot is cleared\n"
            "\t\t\t\t\t-- before EVERY evaluate, like every other cast slot.\n"
            "\t\t\t\t\tFOURTH.tz_self = nil\n"
            "\t\t\t\t\tFOURTH.tz_caster_su = nil\n",
            "poll slot clear", path)
    edits += 1

    # ---------------------------------------------------------- 6. the cast handle
    cast_old = (
        "\tif FOURTH.ss_self then\n"
        "\t\tif FOURTH.ss_caster_su ~= nil and FOURTH.ss_caster_su.uc ~= nil then\n"
        "\t\t\tuc = FOURTH.ss_caster_su.uc\n"
        "\t\tend\n"
        "\t\ttarget = unit\n"
        "\tend\n"
    )
    cast_new = cast_old + (
        "\t-- TZ'ARKAN (this round): the cast is on the OWNER and the controller is the\n"
        "\t-- CASTER's script_unit re-fetched FRESH this tick (the same discipline as\n"
        "\t-- every other cast in this file). A self cast has no target choice to make.\n"
        "\tif FOURTH.tz_self then\n"
        "\t\tif FOURTH.tz_caster_su ~= nil and FOURTH.tz_caster_su.uc ~= nil then\n"
        "\t\t\tuc = FOURTH.tz_caster_su.uc\n"
        "\t\tend\n"
        "\t\ttarget = unit\n"
        "\tend\n"
    )
    s = rep(s, cast_old, cast_new, "cast handle", path)
    edits += 1

    # ------------------------------------------------------ 7. the pre-cast re-check
    if is_live:
        pre = (
            "\t-- TZ'ARKAN'S PRE-CAST RE-CHECK (this round). The user's rule is health\n"
            "\t-- BELOW 15%, so immediately before the call the OWNER must still be ALIVE\n"
            "\t-- and its health - re-read through the ONE reader - must still be BELOW the\n"
            "\t-- line: a unit that died, or was healed above it, inside the wind-up would\n"
            "\t-- otherwise spend a one-way transform for nothing. The EXACT percentage is\n"
            "\t-- written at the decision (the ATTEMPT reason) and again here. An\n"
            "\t-- UNREADABLE health read does not block a cast the trigger already\n"
            "\t-- justified - the file's standing fail-open rule for an auxiliary read.\n"
            "\tif FOURTH.tz_self then\n"
            "\t\tlocal ok_alive, alive = pcall(function() return unit:number_of_men_alive() end)\n"
            "\t\tlocal alive_now = (ok_alive and type(alive) == \"number\" and alive > 0)\n"
            "\t\tlocal hp_now = FOURTH.health_pct(unit)\n"
            "\t\tlocal hp_text = ((type(hp_now) == \"number\") and (string.format(\"%.1f\", hp_now) .. \"%\") or \"?\")\n"
            "\t\tlocal hp_ok = (type(hp_now) ~= \"number\") or (hp_now < FOURTH.TZARKAN_PCT)\n"
            "\t\tif not alive_now or not hp_ok then\n"
            "\t\t\tlog(\"  tzarkan SKIPPED: the caster lapsed before the cast (alive=\"\n"
            "\t\t\t\t.. tostring(alive_now) .. \", health=\" .. hp_text\n"
            "\t\t\t\t.. \", the line is BELOW \" .. tostring(FOURTH.TZARKAN_PCT)\n"
            "\t\t\t\t.. \"%, no range bound - self cast) - cast not spent\")\n"
            "\t\t\tFOURTH.tz_self = nil\n"
            "\t\t\tif RELEASE_CONTROL_AFTER and took_control then\n"
            "\t\t\t\tlocal ok_release, err_release = pcall(function() uc:release_control() end)\n"
            "\t\t\t\tlog(\"  release_control         : ok=\" .. tostring(ok_release)\n"
            "\t\t\t\t\t.. (ok_release and \"\" or (\"  ERROR: \" .. tostring(err_release))))\n"
            "\t\t\tend\n"
            "\t\t\treturn \"held\"\n"
            "\t\tend\n"
            "\t\tlog(\"  tzarkan pre-cast re-check: the caster is still below the line (alive=\"\n"
            "\t\t\t.. tostring(alive_now) .. \", health=\" .. hp_text .. \" of BELOW \"\n"
            "\t\t\t.. tostring(FOURTH.TZARKAN_PCT) .. \"%, no range bound - self cast) - firing\")\n"
            "\tend\n"
            "\n"
        )
        anchor = "\t-- THE ALLY-AWARE HEALTH FAMILY RE-CHECK (this round). The chosen unit is\n"
    else:
        pre = (
            "\t-- TZ'ARKAN'S PRE-CAST RE-CHECK (this round). The user's rule is health\n"
            "\t-- BELOW 15%, so immediately before the call the OWNER must still be ALIVE\n"
            "\t-- and its health - re-read through the ONE reader - must still be BELOW the\n"
            "\t-- line: a unit that died, or was healed above it, inside the wind-up would\n"
            "\t-- otherwise spend a one-way transform for nothing. An UNREADABLE health\n"
            "\t-- read does not block a cast the trigger already justified (fail-open).\n"
            "\tif FOURTH.tz_self then\n"
            "\t\tlocal ok_alive, alive = pcall(function() return unit:number_of_men_alive() end)\n"
            "\t\tlocal alive_now = (ok_alive and type(alive) == \"number\" and alive > 0)\n"
            "\t\tlocal hp_now = FOURTH.health_pct(unit)\n"
            "\t\tlocal hp_ok = (type(hp_now) ~= \"number\") or (hp_now < FOURTH.TZARKAN_PCT)\n"
            "\t\tif not alive_now or not hp_ok then\n"
            "\t\t\tFOURTH.tz_self = nil\n"
            "\t\t\tif RELEASE_CONTROL_AFTER and took_control then\n"
            "\t\t\t\tlocal ok_release, err_release = pcall(function() uc:release_control() end)\n"
            "\t\t\tend\n"
            "\t\t\treturn \"held\"\n"
            "\t\tend\n"
            "\tend\n"
            "\n"
        )
        anchor = "\t-- THE ALLY-AWARE HEALTH FAMILY RE-CHECK (this round): the chosen unit must\n"
    s = rep(s, anchor, pre + anchor, "pre-cast re-check", path)
    edits += 1

    write(path, s)
    after = hashlib.md5(s.encode("utf-8")).hexdigest()
    b = open(path, "rb").read()
    print("%-28s edits=%d  %s -> %s  bytes=%d  CR=%d"
          % (os.path.basename(path), edits, before[:12], after[:12], len(b), b.count(b"\r")))
    return s


live = patch(LIVE, True)
ann = patch(ANN, False)

# the annotated copy must stay log-free and find-free
for tok in ("log(", "string.find("):
    assert ann.count(tok) == 0, "annotated copy now contains %r" % tok
print("annotated copy: log( = 0, string.find( = 0")
print("tzarkan keys in live:", live.count("wh2_dlc14_lord_abilities_tzarkan"))
