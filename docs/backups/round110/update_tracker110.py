"""Round 110 tracker update: the 19 air-drop rule texts, the glossary row and a
new dated update paragraph at the top of docs/WH3_ability_tracker.md.

Binary read/write, LF only, CR-free (the project's byte gate).
"""
P = r"C:/Users/vlady/Desktop/WH3_mod/docs/WH3_ability_tracker.md"

with open(P, "rb") as f:
    raw = f.read()
assert raw.count(b"\r") == 0, "CRLF in the tracker before the edit"
s = raw.decode("utf-8")

OLD_HEAD = "fires when an enemy INFANTRY unit is UNDER the caster ("
NEW_HEAD = ("fires when an enemy INFANTRY unit will be UNDER the caster WHEN THE ORDNANCE LANDS (")
assert s.count(OLD_HEAD) == 19, s.count(OLD_HEAD)

OLD_BODY_START = "(the HORIZONTAL CENTRE-TO-CENTRE distance between the caster and the enemy -"
OLD_BODY_END = "raise it if it never fires)"
NEW_BODY = (
    "(**round 110: TWO-BODY RELATIVE-MOTION PREDICTION** - both bodies are projected forward by "
    "**`FOURTH.AIR_DROP_DELAY_S = 1.5 s`** (a TUNABLE constant between the 1 s and 2 s the user "
    "observed; NO ability row carries a fall time) and the drop fires when the **PROJECTED** "
    "horizontal CENTRE-TO-CENTRE separation is inside **`FOURTH.AIR_DROP_CENTER_M = 6 m`**. The "
    "ordnance does NOT inherit the caster's velocity - the user's assumption: *\"I think the rocks "
    "don't keep the momentum, so let's work with that assumption.\"* - so it falls STRAIGHT DOWN "
    "from the caster's position at release and the impact point IS the projected caster point: "
    "`caster(t+d) = caster(t) + v_caster*d`, `enemy(t+d) = enemy(t) + v_enemy*d`. The velocity is "
    "REBUILT from the only reads the API has - `is_moving()`, `is_moving_fast()`, `slow_speed()` / "
    "`fast_speed()` (m/s) and a heading from `ordered_position()` (= `normalise(ordered - "
    "current)`) - because NO velocity vector exists; `bearing()` (\"the current orientation of the "
    "main squad of the unit in degrees\") is the **CASTER-ONLY** fallback while moving, since the "
    "dump never states how its degrees map onto x/z. Every unreadable read is **ZERO velocity with "
    "a named source** (`stationary` / `moving-unreadable` / `no-speed` / `no-heading`): motion is "
    "never invented, and an unclear read simply behaves like round 109. A stationary pair behaves "
    "exactly as in round 109; a **closing** pair fires EARLIER in time (at a larger current "
    "distance); a **receding** pair later or never; a target **crossing** the flight path is judged "
    "at its projected point. **ONE FLAG if the assumption is wrong:** "
    "`FOURTH.AIR_DROP_INHERIT = true` adds `v*d` to the impact point a SECOND time "
    "(`impact = caster + v*d*2`); nothing else changes. The 6 m bound still stands in for the "
    "formation footprint (the API has no per-unit radius / bbox / size read): lower it if the drop "
    "is still early, raise it if it never fires)"
)

# each row: head + body -> new head + new body (the body is identical in all 19 rows)
out = []
pos = 0
done = 0
while True:
    i = s.find(OLD_HEAD, pos)
    if i < 0:
        out.append(s[pos:])
        break
    j = s.find(OLD_BODY_END, i)
    assert j > i, "no body end after row at %d" % i
    j += len(OLD_BODY_END)
    body = s[i:j]
    assert OLD_BODY_START in body, body[:120]
    out.append(s[pos:i])
    out.append(NEW_HEAD + NEW_BODY)
    pos = j
    done += 1
assert done == 19, done
s = "".join(out)

# ------------------------------------------------------------------ glossary row
GL_START = "| `air_drop_on_infantry` | **round 109** - an enemy INFANTRY unit is UNDER the caster:"
i = s.find(GL_START)
assert i > 0
j = s.find("\n", i)
GL_NEW = (
    "| `air_drop_on_infantry` | **round 110** - an enemy INFANTRY unit that will be UNDER the "
    "caster WHEN THE ORDNANCE LANDS: BOTH bodies are projected **`FOURTH.AIR_DROP_DELAY_S = 1.5 s`** "
    "forward (a TUNABLE constant - no row carries a fall time) and the **PROJECTED** horizontal "
    "CENTRE-TO-CENTRE separation (`battle_unit:position()`, **X/Z only** because `battle_vector:"
    "get_y()` is HEIGHT; `battle_vector:distance_xz()`) must be inside **`FOURTH.AIR_DROP_CENTER_M "
    "= 6`**. The ordnance does **NOT** inherit the caster's velocity (the user's assumption), so it "
    "lands straight down from the release point: `impact = caster + v_caster*d`. Velocity is "
    "REBUILT - no vector exists in the API - from `is_moving()` / `is_moving_fast()` / "
    "`slow_speed()` / `fast_speed()` plus a heading from `ordered_position()`; `bearing()` is the "
    "**caster-only** fallback while moving; an unreadable read is ZERO with a named source "
    "(`stationary` / `moving-unreadable` / `no-speed` / `no-heading`). A stationary pair behaves as "
    "in round 109, a closing pair fires EARLIER, a receding pair later or never, a crossing target "
    "is judged at its projected point. **ONE FLAG** if the assumption is wrong: "
    "`FOURTH.AIR_DROP_INHERIT = true` adds `v*d` a second time (`impact = caster + v*d*2`). "
    "Unchanged: `is_currently_flying()` where the row declares `grounded` (or every carrier flies), "
    "out-of-melee where the row declares `engaged_in_melee`, the cast on the OWNER, fail-closed "
    "behaviour, and the logged pre-cast re-check - which now **RE-PROJECTS both bodies** from fresh "
    "reads and skips the cast rather than spending it. The log prints, per decision, the delay, the "
    "momentum mode, both bodies' current point + velocity + source + projected point, the PROJECTED "
    "and instant separations and the bound, plus a `watch:` band line naming the nearest infantry "
    "and both velocities when nothing qualifies. |"
)
s = s[:i] + GL_NEW + s[j:]

# ------------------------------------------------------- the dated update line
ANCHOR = "installed pack md5 `74d71679cda995b9e4e9f4ce9daa3fb5`.\n"
assert s.count(ANCHOR) == 1
UPDATE = (
    "\n**Update 2026-10-18 (harness 110 — THE AIR DROP IS PREDICTED, NOT SAMPLED: TWO-BODY "
    "RELATIVE MOTION).** One field report is **implemented and shipping**: the user's third air-drop "
    "test — firing on Drop Rocks (Terradon Riders) was *still early or missing*. **WHY THE CENTRE "
    "TEST ALONE COULD NOT WIN:** the round-109 rule compared the two units' **current** positions, "
    "but the rocks take about **1-2 s** to come down and the flier keeps flying, so the enemy that "
    "was under the caster at the button press is not under the rocks at impact. **THE ASSUMPTION "
    "(the user's ruling, verbatim):** *\"I think the rocks don't keep the momentum, so let's work "
    "with that assumption. Let's implement it and I'll test it.\"* — the ordnance does **NOT** "
    "inherit the caster's velocity and falls **STRAIGHT DOWN** from the point the caster occupies at "
    "release, so the impact point **is** the caster's projected position. **THE RULE:** project "
    "**BOTH** bodies forward by **`FOURTH.AIR_DROP_DELAY_S = 1.5 s`** — `caster(t+d) = caster(t) + "
    "v_caster*d` (that is the impact point) and `enemy(t+d) = enemy(t) + v_enemy*d` — and fire when "
    "the **PROJECTED** horizontal centre separation is inside the same **6 m** "
    "(`FOURTH.AIR_DROP_CENTER_M`). **CONSEQUENCES, and they are the point of the round:** a "
    "stationary pair behaves *exactly* as in round 109 (projected = current); a **closing** pair "
    "fires **EARLIER** in time, at a larger current distance, because the gap closes during the "
    "fall; a **receding** pair fires later or not at all; and a target **crossing** the flight path "
    "is judged at its projected **point**, not on its path. **THE VELOCITY, AND ITS LIMITS:** the "
    "script API has **no velocity vector and no position history**, so velocity is **REBUILT** as "
    "`speed * normalise(ordered_position() - position())` from `is_moving()` (*\"whether the unit is "
    "currently moving\"*), `is_moving_fast()` (*\"moving fast (running/charging)\"*), `slow_speed()` "
    "/ `fast_speed()` (*\"the unit's slow/walking ... fast/running movement speed in m/s\"*) and "
    "`ordered_position()` (*\"the position to which the unit has been ordered to move to\"*). Its "
    "limits are stated in the code: the speed is a **scalar** (a turning, braking or pushed unit is "
    "mis-estimated); `ordered_position()` answers the **current** position for an **ATTACKING** unit "
    "(the dump says so), so an attacker has no ordered heading; an ordered point under **0.5 m** "
    "carries no direction; and `bearing()` (*\"the current orientation of the main squad of the unit "
    "in degrees\"*) is the documented **CASTER-ONLY** fallback while moving, because the dump never "
    "states how its degrees map onto x/z. **FAIL-CLOSED ALWAYS:** `is_moving()` not exactly true → "
    "ZERO with source `stationary`; unreadable → ZERO, `moving-unreadable`; no speed → ZERO, "
    "`no-speed`; no usable heading → ZERO, `no-heading` (the speed is still logged). Motion is never "
    "invented, and a unit whose velocity cannot be read is simply treated as stationary — i.e. round "
    "109 behaviour. **IF THE ASSUMPTION IS WRONG, ONE FLAG:** `FOURTH.AIR_DROP_INHERIT = true` adds "
    "the caster's velocity to the impact point a **second** time (`impact = caster + v*d*2` — once "
    "because the caster keeps flying while the ordnance falls, once because the ordnance carries the "
    "velocity itself). **KEPT EXACTLY:** the 70% map exemption, `air_only` / `no_melee` per row, the "
    "self-centred cast on the **OWNER**, fail-closed behaviour, and the pre-cast re-check — which now "
    "**RE-PROJECTS both bodies from fresh positions and fresh velocities** and SKIPS the cast rather "
    "than spending it. **THE LOG, per decision:** one target line carrying the delay, the momentum "
    "mode, the caster's current point + velocity + **velocity source** + projected point, the "
    "enemy's same four, the **PROJECTED** centre separation, the instant separation, the bound, the "
    "edge gap (diagnostic only) and `air_only`; and, when nothing qualifies, a `watch: nearest "
    "INFANTRY '<type>' is centre=~Nm vs bound=6m -> NOT under the caster [projected sep=~Nm after "
    "delay=1.50s; caster v=... src=...; enemy v=... src=...]` line (5 m bands, only while the "
    "nearest projected separation is inside 30 m). **NO COUNTS MOVED:** 689 entries / 742 keys, "
    "`air_drop_on_infantry` **12 entries / 19 keys**, 46 evaluators — behaviour only. Spreadsheet "
    "`docs/WH3_abilities_master_v11_2026-10-18.xlsx` (+ `.ods`; v11 supersedes v10; **v1-v10 "
    "byte-unchanged**); harness 110: **4253 checks / 0 failures** (run twice, byte-identical), red "
    "control (the round-109 build) **65 failures, ALL in the new section and all accounted for**; "
    "installed pack md5 `588e6c3c6781d02321ce7b31af04884f`; `zz_probe_dist.pack` left installed "
    "(md5 `d4e67cfb8bc562c7d6f0ff742909c13d`, untouched).\n"
)
s = s.replace(ANCHOR, ANCHOR + UPDATE, 1)

with open(P, "wb") as f:
    f.write(s.encode("utf-8"))

print("rows updated:", done)
print("new size:", len(s))
print("stale 'round 109 replaced' rows:", s.count("**Round 109 replaced the 1 m EDGE-TO-EDGE"))
print("rows with the new rule:", s.count("TWO-BODY RELATIVE-MOTION PREDICTION"))
print("glossary round 110:", s.count("| `air_drop_on_infantry` | **round 110**"))
