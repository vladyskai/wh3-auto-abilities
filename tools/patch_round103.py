"""Round 103: the charge gate (multi-use abilities) + the ONE health read.

Applies the SAME semantic edits to the live script and to the log-free
annotated copy.  Binary read/write keeps LF byte-for-byte.

Run:  uv run --quiet python tools/patch_round103.py
"""
import os, re, sys

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
LIVE = os.path.join(ROOT, "mod_source", "script", "battle", "mod", "zz_test_deadly_onslaught.lua")
ANN = os.path.join(ROOT, "docs", "WH3_auto_ability_annotated.lua")
BLOCK = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "charge_block.lua")


def rd(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8")


def wr(p, s):
    with open(p, "wb") as f:
        f.write(s.encode("utf-8"))


def sub(s, old, new, name, expect=1):
    n = s.count(old)
    if n != expect:
        raise SystemExit("ANCHOR %s: found %d, expected %d\n%r" % (name, n, expect, old[:160]))
    return s.replace(old, new)


CHARGE_BLOCK = rd(BLOCK)

GATE = """\t\t\t\t\t\t\t-- THE CHARGE GATE (this round): a multi-USE ability
\t\t\t\t\t\t\t-- (num_uses > 1) answers can_perform = TRUE while its
\t\t\t\t\t\t\t-- pool is EMPTY and still ACCEPTS the call - 55
\t\t\t\t\t\t\t-- accepted casts of Nurgling Tide's 3 uses in 108 s
\t\t\t\t\t\t\t-- in the field log, with its button greyed the whole
\t\t\t\t\t\t\t-- time. So the 2 s guard would re-spend the same pool
\t\t\t\t\t\t\t-- forever. After a successful cast the pair is held
\t\t\t\t\t\t\t-- for the ability's OWN recharge_time: ONE use per
\t\t\t\t\t\t\t-- charge cycle, the pool never drains, and no cast
\t\t\t\t\t\t\t-- is silently swallowed.
\t\t\t\t\t\t\tif eligible and ability.charge_s ~= nil then
\t\t\t\t\t\t\t\tlocal cu = charge_gate.until_tick[ui_id]
\t\t\t\t\t\t\t\tlocal held_until = (cu ~= nil and cu[ability.marker]) or nil
\t\t\t\t\t\t\t\tif held_until ~= nil and tick_count < held_until then
\t\t\t\t\t\t\t\t\teligible = false
\t\t\t\t\t\t\t\t\tquiet = true
\t\t\t\t\t\t\t\tend
\t\t\t\t\t\t\tend

"""

FIRE_TMPL = """\t\t\t\t\t\t\t\t\t-- THE CHARGE GATE (this round): the cast SPENT
\t\t\t\t\t\t\t\t\t-- one use, so hold the pair for the ability's own
\t\t\t\t\t\t\t\t\t-- recharge_time (one use per charge cycle).
\t\t\t\t\t\t\t\t\tif ability.charge_s ~= nil then
\t\t\t\t\t\t\t\t\t\tlocal cu = charge_gate.until_tick[ui_id]
\t\t\t\t\t\t\t\t\t\tif cu == nil then
\t\t\t\t\t\t\t\t\t\t\tcu = {}
\t\t\t\t\t\t\t\t\t\t\tcharge_gate.until_tick[ui_id] = cu
\t\t\t\t\t\t\t\t\t\tend
\t\t\t\t\t\t\t\t\t\tcu[ability.marker] = tick_count + math.floor((ability.charge_s * 1000) / POLL_MS)
%s\t\t\t\t\t\t\t\t\tend
"""
FIRE_LOG = '\t\t\t\t\t\t\t\t\t\tlog("  charge gate " .. ability.marker .. ": one use spent - the next attempt waits " .. tostring(ability.charge_s) .. "s (the ability\'s own recharge_time)")\n'

HEALTH = """-- THE ONE HEALTH READ (this round): 0-100 PERCENT, whatever scale the engine
-- answers on.
--
-- WHY (field log 2026-10-17, Eye of Khorne): `HealthPercent` comes back as a
-- FRACTION (0..1), NOT a percentage. 336 picks in one battle printed ONLY
-- "health=0%" or "health=1%" while the picked unit was alive and fighting for
-- 84 s; a 0-100 percent read would have moved through 18/12/5%, and a 1%
-- unit does not survive 84 s of melee. The game's own unit_banner layout feeds
-- this same field straight into a ContextFillBar (a 0..1 input), and the
-- sibling unit read `battle_unit:unary_hitpoints()` is documented as a
-- fraction (0.88). Comparing a fraction against a PERCENT threshold made every
-- comparison true (hp < 20 <=> hp < 2000%), so the finisher offered, and cast
-- on, units far above 20% health.
--
-- The engine's own unit read is tried FIRST (unary_hitpoints, a documented
-- fraction); the context field is the fallback, scaled the same way. A value
-- in 0..1 is a fraction and is multiplied by 100; a value above 1 is already a
-- percent (defensive - never observed). nil when neither read answers.
function FOURTH.health_pct(unit)
\tlocal ok, v = pcall(function() return unit:unary_hitpoints() end)
\tif ok and type(v) == "number" then
\t\tif v >= 0 and v <= 1 then return v * 100 end
\t\treturn v
\tend
\tlocal c = FOURTH.context_value(unit, "HealthPercent")
\tif type(c) == "string" then c = tonumber(c) end
\tif type(c) ~= "number" then return nil end
\tif c >= 0 and c <= 1 then return c * 100 end
\treturn c
end

-- THE ENEMY HEALTH READ (percent, 0-100): the ONE reader above.
function FOURTH.enemy_health_pct(enemy)
\treturn FOURTH.health_pct(enemy)
end
"""

OLD_HEALTH = """-- THE ENEMY HEALTH READ (percent, 0-100). Accepts a number or a numeric string
-- (the engine's context layer stringifies some fields); nil when unreadable.
function FOURTH.enemy_health_pct(enemy)
\tlocal v = FOURTH.health_pct(enemy)
\tif type(v) == "number" then return v end
\tif type(v) == "string" then
\t\tlocal n = tonumber(v)
\t\tif n ~= nil then return n end
\tend
\treturn nil
end
"""

DROPPURGE_OLD = "\tlast_attempt_at[id_slot] = nil\n\tcooldown_hold[id_slot] = nil\n"
DROPPURGE_NEW = "\tlast_attempt_at[id_slot] = nil\n\tcooldown_hold[id_slot] = nil\n\tcharge_gate.until_tick[id_slot] = nil\n"

LOAD_OLD = "\t\tability.range_m = FOURTH.ALLY_CAST[ability.ally_range_real]\n\tend\nend\n"
LOAD_NEW = ("\t\tability.range_m = FOURTH.ALLY_CAST[ability.ally_range_real]\n\tend\n"
            "\t-- THE CHARGE GATE (this round): a multi-USE ability carries its own\n"
            "\t-- recharge_time (seconds, from unit_spec_abil.tsv) here; the poll\n"
            "\t-- holds the pair for exactly that long after a successful cast.\n"
            "\t-- Single-use entries leave charge_s nil - the engine refuses those\n"
            "\t-- by itself on the next attempt.\n"
            "\tfor _, key in ipairs(ability.keys) do\n"
            "\t\tlocal hold = charge_gate.hold_s[key]\n"
            "\t\tif hold ~= nil and (ability.charge_s == nil or hold > ability.charge_s) then\n"
            "\t\t\tability.charge_s = hold\n"
            "\t\tend\n"
            "\tend\n"
            "end\n")

GATE_OLD = "\t\t\t\t\t\t\tend\n\n\t\t\t\t\t\t\tif eligible then\n"
GATE_NEW = "\t\t\t\t\t\t\tend\n\n" + GATE + "\t\t\t\t\t\t\tif eligible then\n"

FIRE_OLD = ('\t\t\t\t\t\t\t\telseif outcome == "fired" then\n'
            '\t\t\t\t\t\t\t\t\t-- a real fire ends the cooldown episode\n'
            '\t\t\t\t\t\t\t\t\tlocal b = cooldown_hold[ui_id]\n'
            '\t\t\t\t\t\t\t\t\tif b ~= nil then\n'
            '\t\t\t\t\t\t\t\t\t\tb[ability.marker] = nil\n'
            '\t\t\t\t\t\t\t\t\tend\n')

HEALTH_RE = re.compile(r'FOURTH\.context_value\((\w+), "HealthPercent"\)')


def patch(path, is_live):
    s = rd(path)
    before = s
    # 1) the health read: every HealthPercent consumer goes through ONE reader
    n = len(HEALTH_RE.findall(s))
    s = HEALTH_RE.sub(lambda m: "FOURTH.health_pct(%s)" % m.group(1), s)
    print("  %s: %d HealthPercent reads routed" % (os.path.basename(path), n))
    # 2) the ONE health reader itself
    s = sub(s, OLD_HEALTH, HEALTH, "health-helper")
    # 3) the charge-gate data table, right after the ABILITIES table
    s = sub(s, "local ALL_ABILITY_KEYS = {}", CHARGE_BLOCK + "local ALL_ABILITY_KEYS = {}", "charge-table")
    # 4) drop purge
    s = sub(s, DROPPURGE_OLD, DROPPURGE_NEW, "drop-purge")
    # 5) load-time charge_s mapping
    s = sub(s, LOAD_OLD, LOAD_NEW, "load-map")
    # 6) the poll gate
    s = sub(s, GATE_OLD, GATE_NEW, "poll-gate")
    # 7) the fire record
    s = sub(s, FIRE_OLD, FIRE_OLD + (FIRE_TMPL % (FIRE_LOG if is_live else "")), "fire-record")
    wr(path, s)
    print("  %s: %d -> %d bytes" % (os.path.basename(path), len(before), len(s)))
    return s


print("live:")
live = patch(LIVE, True)
print("annotated:")
ann = patch(ANN, False)

for name, s in (("live", live), ("ann", ann)):
    if "\r" in s:
        raise SystemExit("%s: CR found - LF purity broken" % name)
    print("%s: charge_s refs %d, health_pct refs %d, log( %d"
          % (name, s.count("charge_s"), s.count("health_pct("), s.count("log(")))
print("OK")
