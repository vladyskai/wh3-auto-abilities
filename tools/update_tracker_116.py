#!/usr/bin/env python3
"""Round 116 tracker update: the harness-116 entry + the rule text on all 19 rows."""
import io

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"

with open(P, "rb") as f:
    b = f.read()
assert b.count(b"\r\n") == 0, "CRLF in the tracker"
s = b.decode("utf-8")


def must(s, old, new, count=1):
    n = s.count(old)
    assert n == count, "anchor %r matched %d (want %d)" % (old[:70], n, count)
    return s.replace(old, new)


# ---- 1. the rule text on all 19 air-drop rows ------------------------------
OLD = ("**and ONLY once that pair has stayed under the line CONTINUOUSLY for "
       "`FOURTH.AIR_DROP_DWELL_S = 1.0 s`; a separation after `FOURTH.AIR_DROP_MIN_CONTACT_S = 0.3 s` "
       "of contact fires on the separation evaluation (the SHORT-CROSSING FALLBACK), a separation "
       "before it cancels the dwell and logs the time actually under, the FIRST evaluation of a "
       "contact never fires, and a re-contact starts a FRESH dwell (round 115: THE 1-SECOND DWELL).**")

NEW = ("**and ONLY once the delay MEASURED for that pair at the moment of first contact has "
       "elapsed: `delay = FOURTH.AIR_DROP_DWELL_MID_S - FOURTH.AIR_DROP_DWELL_SWING_S * proj`, where "
       "`proj` is the COSINE between the enemy's velocity (`speed * normalise(ordered_position - "
       "position)`, speed from `fast_speed` when `is_moving_fast` else `slow_speed`) and the "
       "enemy-to-caster axis - so 0 s for an enemy running AT the caster, 1 s stationary or "
       "perpendicular, 2 s running AWAY, floored at 0, measured ONCE per contact and NEVER "
       "re-measured inside it; a separation after `FOURTH.AIR_DROP_MIN_CONTACT_S = 0.3 s` of contact "
       "fires on the separation evaluation (the SHORT-CROSSING FALLBACK), a separation before it "
       "cancels and logs the time actually under, the FIRST evaluation of a contact never fires, and "
       "a re-contact MEASURES AGAIN (round 116: THE MEASURED, VELOCITY-AWARE DELAY).**")
s = must(s, OLD, NEW, 19)
_rows = [ln for ln in s.splitlines() if ln.startswith("| ") and "When armed, fires when the **NEAREST enemy" in ln]
assert len(_rows) == 19, len(_rows)
import re as _re
for _ln in _rows:
    assert _re.search(r"AIR_DROP_DWELL_S(?![A-Z_])", _ln) is None, "a retired constant survives in a table row"

# ---- 2. the harness-116 update paragraph ----------------------------------
ANCHOR = "\n## 1. Implemented today (field-verified)"
ENTRY = '''**Update 2026-10-18 (harness 116 - THE AIR-DROP WAIT IS MEASURED, NOT FIXED: THE ENEMY'S OWN VELOCITY, PROJECTED ON THE LINE BETWEEN THE TWO UNITS).** The user's ruling, verbatim: *"if the enemy unit is running away, then it is too soon. If the enemy moving is running towards, then it is too late. So to actually make it work, I think we do need relative velocity. But it must be calculated the moment the edge to edge distance is below our theshold. Then, if the unit is running towards the caster, then the delay would be 0. If running away, then the delay would be 2. If stationary or perpedicular, then should be 1. ... the delay is dynamic in this way."* and *"Also include logs to check the result of the function we use, like ordered_position(), just in case it isn't what we think it is."* **THE FIXED 1-SECOND DWELL IS REPLACED BY A MEASUREMENT.** Round 115's machinery is kept in full - the pair row, the poll clock, the short-crossing fallback, the purge and the re-verifying pre-cast re-check - but the NUMBER it waits for is now taken from the enemy's own velocity at the instant contact begins. **THE FORMULA:** `axis = normalise(caster.position() - enemy.position())` in **x/z only** (`get_y` is height above the water plane, so a 3D axis would be wrong); `v = speed * normalise(ordered_position() - position())` with `speed = fast_speed()` when `is_moving_fast()` is true else `slow_speed()`; `proj = dot(v, axis) / (speed * |axis|)` - the **COSINE**, clamped to `+-1`; `delay = FOURTH.AIR_DROP_DWELL_MID_S - (FOURTH.AIR_DROP_DWELL_SWING_S * proj)`, floored at 0. The axis runs **enemy -> caster**, so a positive cosine means closing. **AT THE SHIPPED PAIR (MID 1.0 s / SWING 1.0 s):** proj +1 (running straight AT the caster) -> **0.0 s**, proj 0 (stationary or perpendicular) -> **1.0 s**, proj -1 (running straight AWAY) -> **2.0 s**, and everything between interpolates linearly (proj +0.71 -> 0.29 s, proj -0.71 -> 1.71 s) - the user's three cases plus the ramp between them come out of that one subtraction, with no table anywhere. **MEASURED ONCE PER CONTACT:** the delay is taken on the FIRST evaluation of a contact - the one that stamps the pair - and stored with the tick, the cosine and the velocity source (`FOURTH.ad_pair[caster][enemy] = { first, delay, proj, src }`); it is **never re-measured inside that contact even if the enemy turns**, and a **re-contact** after a separation starts a **fresh** measurement. **THE DELAY LANDS ON THE POLL GRID:** `tick_count` moves in `POLL_MS = 250 ms` steps, so a measured 0.29 s waits 0.50 s, a measured 1.71 s waits 1.75 s and a measured 0.00 s fires on the NEXT evaluation; the log prints the MEASURED value and quantisation can only delay a cast, never advance it. The 0.2 s fast pass still adds evaluations and never time. **EVERY READ FAILS CLOSED** to a zero velocity with a named source, each falling back to the 1.0 s MID baseline: `ordered` (a real heading), `stationary` (`is_moving()` false), `moving-unreadable`, `speed-unreadable`, `speed-zero`, `pos-unreadable`, `no-heading` (`ordered_position()` unreadable **or** the order point under 0.5 m away - the documented "attacking" case where `ordered_position()` answers the CURRENT position), `axis-degenerate` (the two centres under 0.5 m apart in x/z) and `axis-unreadable`. **THE READ-VERIFICATION LOG the user asked for** - one line per contact episode plus one per waiting tick: `[<ui>] <marker> reads: moving=<b> is_moving_fast=<b> slow_speed=<n.nn> fast_speed=<n.nn> pos=(<x>,<z>) ordered=(<x>,<z>) |h|=<n.n> proj=<+n.nn> src=<src> delay=<n.nn>s (measured once for this contact)` and `... reads(hold): <the same reads RE-TAKEN> proj=<measured> src=<measured> delay=<n.nn>s held=<n.nn>s`, with **UNREADABLE** in any field whose pcall failed. A charging enemy whose `ordered_position()` is its current position therefore shows up as `pos=(x,z)` equal to `ordered=(x,z)`, `|h|=0.0`, `src=no-heading` - directly, without inference - which is the first thing to check in the returned log. **UNCHANGED:** the candidate filter (> 10 alive models), the nearest-by-`unit_distance` pick, `air_only` / `no_melee`, the self-centred cast on the OWNER, every fail-closed read, the 0.2 s fast pass, `POLL_MS = 250`, the short-crossing fallback (0.3 s), the pair purge and the pre-cast re-check - which now verifies the wait against the pair's OWN measured delay (`(dwell <under>s of <measured>s)`) as well as re-validating the models and re-measuring the gap. **NO COUNTS MOVED:** 689 entries / 742 keys, `air_drop_on_infantry` **12 entries / 19 keys**, 46 evaluators - behaviour only. Spreadsheet `docs/WH3_abilities_master_v17_2026-10-18.xlsx` (v17 supersedes v16; **v1-v16 byte-unchanged**); round doc `docs/WH3_round116_airdrop_velocity.md`; harness 116: **4,895 checks / 0 failures** (run twice, byte-identical), red control (the round-115 build) **72 failures, all in the new section and all accounted for**; installed pack md5 `0c489c2438cf9acc98730bff1b0df52b` (five files, all byte-identical); `zz_probe_dist.pack` left installed (md5 `d4e67cfb8bc562c7d6f0ff742909c13d`, untouched).
'''
s = must(s, ANCHOR, "\n" + ENTRY + ANCHOR)

with open(P, "wb") as f:
    f.write(s.encode("utf-8"))
print("tracker updated:", len(s), "bytes")
