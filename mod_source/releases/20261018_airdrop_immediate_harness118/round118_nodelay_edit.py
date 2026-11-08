#!/usr/bin/env python3
"""Round 118 edit: REMOVE the air-drop delay entirely.

The user's ruling, verbatim: "I tried it. Let's keep the distance to center and
remove the delay we had completely."

KEPT: the centre-to-centre detection (FOURTH.ad_centre_gap /
AIR_DROP_CENTER_M = 6.0), the candidate filter, the 0.2 s fast pass with its
30 m near gate, the 250 ms poll, air_only / no_melee, the self-centred cast,
the fail-closed reads, the gates in FOURTH.try_pair and the pre-cast re-check
(re-measuring the centre on fresh handles).

DELETED: AIR_DROP_DWELL_MID_S, AIR_DROP_DWELL_SWING_S, AIR_DROP_MIN_CONTACT_S,
FOURTH.ad_pair and every helper over it (ad_pair_key, ad_pair_stamp,
ad_pair_need, ad_pair_drop, ad_under, ad_purge_unit, ad_contact_clear), the
purge hook zz_ad_dwell_purge and its ONE outside call site in
drop_unit_by_ui_id, ad_enemy_velocity and its raw-read body (ad_vread,
ad_vread_px, ad_vread_pz), ad_proj_text, ad_dynamic_delay, ad_event, the whole
short-crossing fallback and every dwell/delay/cosine log line.

Applied to BOTH copies (live + annotated) with exact occurrence assertions.
Binary read/write so the shipped file stays LF.
"""

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
LIVE = ROOT + r"\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = ROOT + r"\docs\WH3_auto_ability_annotated.lua"

SEP = "-- " + "=" * 76


def rd(p):
    with open(p, "rb") as f:
        b = f.read()
    assert b.count(b"\r") == 0, "CR found in " + p
    return b.decode("utf-8")


def wr(p, s):
    with open(p, "wb") as f:
        f.write(s.encode("utf-8"))
    with open(p, "rb") as f:
        assert f.read().count(b"\r") == 0, "CR after write in " + p


def tabs(x):
    """Leading whitespace only: every 2 spaces of indent -> one tab."""
    out = []
    for line in x.split("\n"):
        i = 0
        while line[i:i + 2] == "  ":
            i += 2
        out.append(("\t" * (i // 2)) + line[i:])
    return "\n".join(out)


def cut(s, start, end_incl, new, tag=""):
    """Replace the CONTIGUOUS span start..end_incl (both included) with new."""
    assert s.count(start) == 1, "%s start anchor matched %d: %r" % (tag, s.count(start), start[:80])
    assert s.count(end_incl) == 1, "%s end anchor matched %d: %r" % (tag, s.count(end_incl), end_incl[:80])
    i = s.index(start)
    j = s.index(end_incl, i)
    assert j >= i, tag
    out = s[:i] + new + s[j + len(end_incl):]
    assert s.count(start) == 1
    return out


def cut_excl(s, start, end_excl, new, tag=""):
    """Replace start..end_excl, KEEPING the end anchor."""
    assert s.count(start) == 1, "%s start anchor matched %d: %r" % (tag, s.count(start), start[:80])
    assert s.count(end_excl) == 1, "%s end anchor matched %d: %r" % (tag, s.count(end_excl), end_excl[:80])
    i = s.index(start)
    j = s.index(end_excl, i)
    assert j > i, tag
    return s[:i] + new + s[j:]


def rep(s, old, new, count=1, tag=""):
    assert s.count(old) == count, "%s anchor matched %d, want %d: %r" % (tag, s.count(old), count, old[:80])
    return s.replace(old, new)


# ============================================================================
# THE HEADER: the round-116/117 "wait" documentation becomes the round-118
# "no wait at all" documentation, and the three delay constants go with it.
# ============================================================================
NEW_HEADER = tabs("""-- ============================================================================
-- ROUND 118 - THE DELAY IS GONE: THE FIRST EVALUATION THAT SEES THE CENTRE
-- INSIDE THE LINE CASTS
--
-- THE USER'S RULING, verbatim: "I tried it. Let's keep the distance to center
-- and remove the delay we had completely."
--
-- WHAT THE RULE IS NOW - one measurement, one comparison, no wait:
--   candidate = ALIVE, and number_of_men_alive() > AIR_DROP_MIN_MEN (10)
--   valid     = that candidate's CENTRE gap (ad_centre_gap) is READABLE
--   chosen    = the NEAREST valid candidate by that CENTRE gap
--   FIRE      = the chosen enemy's centre gap < AIR_DROP_CENTER_M (6.0 m)
-- The evaluation that first measures the chosen enemy's centre inside the line
-- returns the decision AND the cast goes out on it: nothing is stamped,
-- nothing is timed, nothing is re-measured inside a contact, and nothing fires
-- on the way out. Nothing waits for a second poll - the 0.2 s fast pass and the
-- 250 ms poll both fire on the evaluation that sees the line crossed, so the drop
-- leaves within one fast-pass interval (0.2 s) of the centre arriving.
--
-- WHAT ROUND 118 DELETED (every one of them existed to TIME a wait; the symbol
-- inventory and the caller audit are in docs/WH3_round118_airdrop_nodelay.md -
-- they are deliberately NOT named here, so a grep for any of them over this
-- file answers 0 and the harness pins exactly that):
--   * the two delay dials (a 1.0 s baseline and a 1.0 s swing) and the 0.3 s
--     minimum-contact floor;
--   * the per-pair contact row - one row per (caster, enemy) holding the tick
--     the contact started on, the delay measured for it, and the evidence that
--     delay came from - and every helper over it: the pair key, the stamp, the
--     per-pair delay read, the row drop, the elapsed read, the purge and the
--     no-valid-pair clear;
--   * the purge hook: its ONE call site was in drop_unit_by_ui_id, which
--     existed only to clear those rows. Both are gone, and nothing else in the
--     file ever named any of it;
--   * the enemy-velocity read, the raw-read body it built, the printed
--     projection and the formula that turned it into a delay;
--   * the un-deduped event line (contact started / held / satisfied /
--     cancelled / fired on separation): there are no delay events left to
--     write, and the change-gated decision line carries the whole decision;
--   * the fallback that fired on separation. With no wait there is no crossing
--     to rescue: a pair that arrives and leaves between two evaluations is
--     simply not seen, which is the fast pass's business, not a rule.
--
-- THE READ-VERIFICATION LOG WENT WITH IT, deliberately: it printed the engine's
-- movement flags, both speed reads, the position and the order point so the
-- projection could be checked against real answers. No rule consults a heading
-- any more, so the whole raw-read block was removed rather than left printing
-- values nothing reads. If a delay is ever designed back in, that block - in
-- the pre-118 source, kept under docs/backups/round118 - is where to start.
--
-- WHAT STAYED: the candidate filter (alive, more than AIR_DROP_MIN_MEN models,
-- no infantry test), the 6 m CENTRE bound and ad_centre_gap, the 0.2 s fast
-- pass with its 30 m near gate, the 250 ms poll, air_only / no_melee, the
-- self-centred cast on the OWNER, every fail-closed read, the gates in
-- FOURTH.try_pair, and the pre-cast re-check - which now only has to confirm
-- that the centre is STILL inside the line, on FRESH handles.
-- ============================================================================
""")

# ============================================================================
# THE PURGE HOOK CALL SITE (outside this evaluator - the ONLY one that existed)
# ============================================================================
OLD_HOOK_CALL = tabs("""  -- ROUND 115: the pair's dwell row dies WITH the unit (caster OR enemy),
  -- through the ONE named global set beside ad_purge_unit below: this
  -- chunk is at Lua's local ceiling, so the routine cannot name FOURTH.
  if zz_ad_dwell_purge ~= nil then zz_ad_dwell_purge(id_text) end
""")

# ============================================================================
# THE PRE-CAST RE-CHECK: no dwell evidence to verify any more
# ============================================================================
LIVE_RECHECK = tabs("""  -- THE AIR-DROP RE-CHECK (round 114, re-measured on the CENTRE in round 117,
  -- delay evidence removed in round 118). Immediately before the call the
  -- CASTER must still be ALIVE, still AIRBORNE where its row is air-only and
  -- still OUT of melee where the engine forbids it; the CHOSEN ENEMY must
  -- still be alive with MORE THAN AIR_DROP_MIN_MEN models, and its CENTRE gap
  -- must still be under AIR_DROP_CENTER_M. The enemy reads and the distance
  -- are RE-TAKEN here from FRESH handles - the same number_of_men_alive() read
  -- and the SAME ad_centre_gap measurement the picker used, so the two
  -- readings cannot disagree - and a lapsed condition SKIPS the cast rather
  -- than spending it. There is NO WAIT to verify any more: the trigger fires on
  -- the evaluation that measured the centre inside the line, so the one
  -- question left is whether it is STILL inside it.
  -- Every number that decided it is written, with `-> SKIPPED at re-check`, and
  -- the gap it prints is the CENTRE gap re-measured on this line.
  if FOURTH.ad_enemy ~= nil then
    local enemy = FOURTH.ad_enemy
    local ad_marker_now = FOURTH.ad_marker or "air_drop"
    local ok_alive, alive = pcall(function() return unit:number_of_men_alive() end)
    local caster_alive = (ok_alive and type(alive) == "number" and alive > 0)
    local fly_now, fly_readable = true, true
    if FOURTH.ad_air_only then
      local ok_fly, v = pcall(function() return unit:is_currently_flying() end)
      fly_readable = ok_fly
      fly_now = (ok_fly and v == true)
    end
    local melee_now, melee_readable = false, true
    if FOURTH.ad_no_melee then
      local ok_m, m = pcall(function() return unit:is_in_melee() end)
      melee_readable = ok_m
      melee_now = (ok_m and m == true)
    end
    local ok_ea, ea = pcall(function() return enemy:number_of_men_alive() end)
    local enemy_alive = (ok_ea and type(ea) == "number" and ea > 0)
    local men_ok = (ok_ea and type(ea) == "number" and ea > FOURTH.AIR_DROP_MIN_MEN)
    local centre_now = FOURTH.ad_centre_gap(unit, enemy)
    local centre_ok = (centre_now ~= nil and centre_now < FOURTH.AIR_DROP_CENTER_M)
    local centre_text = ((centre_now ~= nil) and (string.format("%.2f", centre_now) .. "m") or "?")
    local men_text = ((ok_ea and type(ea) == "number") and tostring(ea) or "?")
    if not (caster_alive and fly_readable and fly_now and melee_readable
      and (not melee_now) and enemy_alive and men_ok and centre_ok) then
      log("  " .. FOURTH.ad_tag(unit) .. ad_marker_now .. " nearest valid:'"
        .. (FOURTH.type_plain(enemy) or "enemy") .. "' entities=" .. men_text
        .. " centre=" .. centre_text .. " (need < "
        .. string.format("%.2f", FOURTH.AIR_DROP_CENTER_M) .. "m) -> SKIPPED at re-check"
        .. " (caster_alive=" .. tostring(caster_alive) .. " flying=" .. tostring(fly_now)
        .. " melee=" .. tostring(melee_now) .. " enemy_alive=" .. tostring(enemy_alive)
        .. " over_min_men=" .. tostring(men_ok) .. " centre_ok=" .. tostring(centre_ok)
        .. " min_men=" .. tostring(FOURTH.AIR_DROP_MIN_MEN) .. ") - cast not spent")
      FOURTH.ad_enemy = nil
      if RELEASE_CONTROL_AFTER and took_control then
        local ok_release, err_release = pcall(function() uc:release_control() end)
        log("  release_control         : ok=" .. tostring(ok_release)
          .. (ok_release and "" or ("  ERROR: " .. tostring(err_release))))
      end
      return "held"
    end
    log("  " .. FOURTH.ad_tag(unit) .. ad_marker_now .. " nearest valid:'"
      .. (FOURTH.type_plain(enemy) or "enemy") .. "' entities=" .. men_text
      .. " centre=" .. centre_text .. " (need < "
      .. string.format("%.2f", FOURTH.AIR_DROP_CENTER_M) .. "m) -> FIRING (re-checked)")
  end

""")

ANN_RECHECK = tabs("""  -- THE AIR-DROP RE-CHECK (round 114, re-measured on the CENTRE in round 117,
  -- delay evidence removed in round 118). Immediately before the call the
  -- CASTER must still be ALIVE, still AIRBORNE where its row is air-only and
  -- still OUT of melee where the engine forbids it; the CHOSEN ENEMY must
  -- still be alive with MORE THAN AIR_DROP_MIN_MEN models, and its CENTRE gap
  -- must still be under AIR_DROP_CENTER_M. The enemy reads and the distance
  -- are RE-TAKEN here from FRESH handles - the same number_of_men_alive() read
  -- and the SAME ad_centre_gap measurement the picker used, so the two
  -- readings cannot disagree - and a lapsed condition SKIPS the cast rather
  -- than spending it. There is NO WAIT to verify any more: the trigger fires on
  -- the evaluation that measured the centre inside the line, so the one
  -- question left is whether it is STILL inside it.
  if FOURTH.ad_enemy ~= nil then
    local enemy = FOURTH.ad_enemy
    local ad_marker_now = FOURTH.ad_marker or "air_drop"
    local ok_alive, alive = pcall(function() return unit:number_of_men_alive() end)
    local caster_alive = (ok_alive and type(alive) == "number" and alive > 0)
    local fly_now, fly_readable = true, true
    if FOURTH.ad_air_only then
      local ok_fly, v = pcall(function() return unit:is_currently_flying() end)
      fly_readable = ok_fly
      fly_now = (ok_fly and v == true)
    end
    local melee_now, melee_readable = false, true
    if FOURTH.ad_no_melee then
      local ok_m, m = pcall(function() return unit:is_in_melee() end)
      melee_readable = ok_m
      melee_now = (ok_m and m == true)
    end
    local ok_ea, ea = pcall(function() return enemy:number_of_men_alive() end)
    local enemy_alive = (ok_ea and type(ea) == "number" and ea > 0)
    local men_ok = (ok_ea and type(ea) == "number" and ea > FOURTH.AIR_DROP_MIN_MEN)
    local centre_now = FOURTH.ad_centre_gap(unit, enemy)
    local centre_ok = (centre_now ~= nil and centre_now < FOURTH.AIR_DROP_CENTER_M)
    local centre_text = ((centre_now ~= nil) and (string.format("%.2f", centre_now) .. "m") or "?")
    local men_text = ((ok_ea and type(ea) == "number") and tostring(ea) or "?")
    if not (caster_alive and fly_readable and fly_now and melee_readable
      and (not melee_now) and enemy_alive and men_ok and centre_ok) then
      -- (annotated copy: the SKIPPED-at-re-check line is a log-only line - it
      -- prints the enemy type, entities=<n>, the FRESH centre gap, the 6.0 m
      -- line, and which of caster_alive / flying / melee / enemy_alive /
      -- over_min_men / centre_ok lapsed)
      FOURTH.ad_enemy = nil
      if RELEASE_CONTROL_AFTER and took_control then
        local ok_release, err_release = pcall(function() uc:release_control() end)
      end
      return "held"
    end
    -- (annotated copy: the FIRING (re-checked) line is a log-only line with the
    -- same fields, the CENTRE gap re-measured on fresh handles)
  end

""")

# ============================================================================
# THE EVALUATOR ITSELF
# ============================================================================
LIVE_PICK = tabs("""-- THE AIR-DROP EVALUATOR. ONE comparison decides - the NEAREST valid enemy's
-- CENTRE gap against AIR_DROP_CENTER_M - after the caster-side usage checks the
-- ability's own row declares. NO DELAY: the evaluation that measures the centre
-- inside the line FIRES on that evaluation. The enemy type, the entity count,
-- the exact CENTRE distance and this caster's ui id are written on EVERY
-- decision:
--     [1003] sky_junk_bomb nearest valid:'wh_main_inf_zombie_0' entities=20
--            centre=5.90m (need < 6.00m) -> FIRING
-- and the same line says NOT YET when the gap is at or over the line. An
-- unreadable caster side (air_only / no_melee) HOLDS with the reason.
function FOURTH.ad_pick(unit, routing)
  if routing then return nil end
  local marker = FOURTH.ad_marker or "air_drop"
  if FOURTH.ad_air_only then
    local ok_fly, flying = pcall(function() return unit:is_currently_flying() end)
    if not ok_fly or flying ~= true then
      FOURTH.ad_say(unit, marker, "airborne check: is_currently_flying() = "
        .. (ok_fly and tostring(flying) or "UNREADABLE")
        .. " -> HOLDING (this ability's row is air-only)")
      return nil
    end
  end
  if FOURTH.ad_no_melee then
    local ok_m, m = pcall(function() return unit:is_in_melee() end)
    if not ok_m then
      FOURTH.ad_say(unit, marker, "melee check: is_in_melee() UNREADABLE -> HOLDING (fail-closed)")
      return nil
    end
    if m == true then
      FOURTH.ad_say(unit, marker, "melee check: the caster is fighting in melee -> HOLDING"
        .. " (the row declares engaged_in_melee)")
      return nil
    end
  end
  local enemy, dist, men, etype = FOURTH.ad_nearest(unit)
  if enemy == nil then
    -- NOTHING VALID IS UNDER THE DROP: no candidate, so there is no decision to
    -- write and nothing to cast at. Fail closed, silently.
    return nil
  end
  etype = etype or "enemy"
  local centre_text = string.format("%.2f", dist)
  local need = string.format("%.2f", FOURTH.AIR_DROP_CENTER_M)
  if dist >= FOURTH.AIR_DROP_CENTER_M then
    -- NOT YET: the nearest valid enemy's CENTRE is at or outside the 6 m line.
    FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
      .. tostring(men) .. " centre=" .. centre_text .. "m (need < " .. need .. "m) -> NOT YET")
    return nil
  end
  -- THE DECISION IS TAKEN NOW. No stamp, no wait and no second look inside the
  -- contact: the gap THIS evaluation measured is the gap the cast is made on,
  -- and the pre-cast re-check in FOURTH.try_pair confirms it before the call.
  FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
    .. tostring(men) .. " centre=" .. centre_text .. "m (need < " .. need .. "m) -> FIRING"
    .. " (the nearest of the valid enemies; the gap is centre-to-centre, x/z)")
  FOURTH.ad_enemy = enemy
  FOURTH.ad_caster_su = FOURTH.eg_fresh_caster_su(unit)
  return "nearest valid '" .. etype .. "' has " .. tostring(men)
    .. " models, its CENTRE gap is " .. centre_text .. "m - under the " .. need
    .. "m line"
end
""")

ANN_PICK = tabs("""-- THE AIR-DROP EVALUATOR. ONE comparison decides - the NEAREST valid enemy's
-- CENTRE gap against AIR_DROP_CENTER_M - after the caster-side usage checks the
-- ability's own row declares. (The live build writes, on EVERY decision, the
-- enemy type, the entity count, the exact CENTRE distance and the caster's ui
-- id:
--     [1003] sky_junk_bomb nearest valid:'<key>' entities=N centre=5.90m
--            (need < 6.00m) -> FIRING / NOT YET)
-- NO DELAY: the evaluation that measures the centre inside the line FIRES on
-- that evaluation.
function FOURTH.ad_pick(unit, routing)
  if routing then return nil end
  local marker = FOURTH.ad_marker or "air_drop"
  if FOURTH.ad_air_only then
    local ok_fly, flying = pcall(function() return unit:is_currently_flying() end)
    if not ok_fly or flying ~= true then
      FOURTH.ad_say(unit, marker, "airborne check: is_currently_flying() = "
        .. (ok_fly and tostring(flying) or "UNREADABLE")
        .. " -> HOLDING (this ability's row is air-only)")
      return nil
    end
  end
  if FOURTH.ad_no_melee then
    local ok_m, m = pcall(function() return unit:is_in_melee() end)
    if not ok_m then
      FOURTH.ad_say(unit, marker, "melee check: is_in_melee() UNREADABLE -> HOLDING (fail-closed)")
      return nil
    end
    if m == true then
      FOURTH.ad_say(unit, marker, "melee check: the caster is fighting in melee -> HOLDING"
        .. " (the row declares engaged_in_melee)")
      return nil
    end
  end
  local enemy, dist, men, etype = FOURTH.ad_nearest(unit)
  if enemy == nil then
    -- NOTHING VALID IS UNDER THE DROP: no candidate, so there is no decision to
    -- write and nothing to cast at. Fail closed, silently.
    return nil
  end
  etype = etype or "enemy"
  local centre_text = string.format("%.2f", dist)
  local need = string.format("%.2f", FOURTH.AIR_DROP_CENTER_M)
  if dist >= FOURTH.AIR_DROP_CENTER_M then
    -- NOT YET: the nearest valid enemy's CENTRE is at or outside the 6 m line.
    FOURTH.ad_say(unit, marker, "nearest valid:'" .. etype .. "' entities="
      .. tostring(men) .. " centre=" .. centre_text .. "m (need < " .. need .. "m) -> NOT YET")
    return nil
  end
  -- THE DECISION IS TAKEN NOW. No stamp, no wait and no second look inside the
  -- contact: the gap THIS evaluation measured is the gap the cast is made on,
  -- and the pre-cast re-check in FOURTH.try_pair confirms it before the call.
  -- (annotated copy: the FIRING decision line is a log-only line that repeats
  -- the nearest enemy, its entity count and the exact CENTRE gap on every cast)
  FOURTH.ad_enemy = enemy
  FOURTH.ad_caster_su = FOURTH.eg_fresh_caster_su(unit)
  return "nearest valid '" .. etype .. "' has " .. tostring(men)
    .. " models, its CENTRE gap is " .. centre_text .. "m - under the " .. need
    .. "m line"
end
""")

OLD_TOOLTIP = ("after a wait measured from that enemy's velocity at the moment of "
               "contact: 0 s if it is running at this unit, 1 s if it is stationary "
               "or crossing, 2 s if it is running away, airborne where the ability "
               "requires it")
NEW_TOOLTIP = ("and casts immediately on that evaluation - no delay at all - "
               "airborne where the ability requires it")

# THE ANCHORS (identical in both copies)
A_HDR_START = "-- ROUND 116 - THE WAIT IS MEASURED, NOT FIXED: THE ENEMY'S OWN VELOCITY"
A_HDR_END = "FOURTH.AIR_DROP_MIN_CONTACT_S = 0.3\n"
A_STATE_START = "-- THE CONTACT STATE (round 116)."
A_STATE_END = "FOURTH.ad_pair = {}\nFOURTH.ad_fired = nil\n"
A_HELP_START = SEP + "\n-- THE DWELL HELPERS (round 115)"
A_HELP_END = "\treturn delay, proj, src\nend\n"
A_PICK_START = "-- THE AIR-DROP EVALUATOR. ONE comparison decides"
A_PICK_END = '.. string.format("%.2f", need_s) .. "s) is satisfied"\nend\n'
A_RC_START = "\t-- THE AIR-DROP RE-CHECK (round 114"
A_RC_END = "\t-- SELF-SUMMON RE-CHECK (harness 102, Nurgling Tide)"
A_HOOK_START = "\t-- ROUND 115: the pair's dwell row dies WITH the unit"
A_HOOK_END = "\tif zz_ad_dwell_purge ~= nil then zz_ad_dwell_purge(id_text) end\n"


def apply(path, ann):
    s = rd(path)
    tag = "ANN" if ann else "LIVE"
    before = len(s)

    # 1. the header prose + the three delay constants
    s = cut(s, A_HDR_START, A_HDR_END, NEW_HEADER, tag + " header")
    # 2. the contact-state table and its evidence field
    s = cut(s, A_STATE_START, A_STATE_END, "", tag + " state")
    # 3. the dwell helpers + the velocity reads + the cosine + the dynamic delay
    s = cut(s, A_HELP_START, A_HELP_END, "", tag + " helpers")
    # 4. the evaluator
    s = cut(s, A_PICK_START, A_PICK_END, ANN_PICK if ann else LIVE_PICK, tag + " pick")
    # 5. the pre-cast re-check
    s = cut_excl(s, A_RC_START, A_RC_END, ANN_RECHECK if ann else LIVE_RECHECK, tag + " recheck")
    # 6. the purge hook's one call site
    s = cut(s, A_HOOK_START, A_HOOK_END, "", tag + " hook")
    # 7. the tooltip sentence
    s = rep(s, OLD_TOOLTIP, NEW_TOOLTIP, 1, tag + " tooltip")

    wr(path, s)
    print("%-4s  %d -> %d bytes (%+d)" % (tag, before, len(s), len(s) - before))

    # ---- ASSERTIONS: nothing of the delay machinery survives --------------
    dead = ["AIR_DROP_DWELL_MID_S", "AIR_DROP_DWELL_SWING_S", "AIR_DROP_MIN_CONTACT_S",
            "FOURTH.ad_pair", "ad_pair_key", "ad_pair_stamp", "ad_pair_need",
            "ad_pair_drop", "ad_under", "ad_purge_unit", "ad_contact_clear",
            "zz_ad_dwell_purge", "ad_enemy_velocity", "ad_proj_text",
            "ad_dynamic_delay", "ad_vread", "FOURTH.ad_event", "ad_fired",
            "dwell", "short crossing", "proj="]
    for d in dead:
        n = s.count(d)
        assert n == 0, "%s: %r still present %d time(s)" % (tag, d, n)
    # ---- the KEPT pieces are all still there ------------------------------
    for k in ["function FOURTH.ad_centre_gap(caster, enemy)",
              "FOURTH.AIR_DROP_CENTER_M = 6.0",
              "FOURTH.AIR_DROP_MIN_MEN = 10",
              "FOURTH.AIR_DROP_NEAR_M = 30",
              "FOURTH.AIR_DROP_FAST_S = 0.2",
              "function FOURTH.ad_nearest(unit)",
              "function FOURTH.ad_pick(unit, routing)",
              "function FOURTH.ad_say(unit, marker, note)",
              "function FOURTH.ad_tag(unit)",
              "FOURTH.ad_air_only", "FOURTH.ad_no_melee",
              "if dist >= FOURTH.AIR_DROP_CENTER_M then",
              "local centre_now = FOURTH.ad_centre_gap(unit, enemy)",
              "centre_now < FOURTH.AIR_DROP_CENTER_M"]:
        assert s.count(k) >= 1, "%s: MISSING %r" % (tag, k)
    print("%-4s  dead symbols: 0 | kept symbols: present" % tag)


apply(LIVE, False)
apply(ANN, True)

# the two copies must still agree on the tree shape
live = rd(LIVE)
ann = rd(ANN)
for tok in ["FOURTH.ad_note = {}", "FOURTH.ad_fast_on = {}", "FOURTH.ad_fast_abilities = {}"]:
    assert live.count(tok) == 1 and ann.count(tok) == 1, tok
assert ann.count("log(") == 0, "the annotated copy gained a log() line"
print("BOTH COPIES OK - the annotated copy is still log-free")
