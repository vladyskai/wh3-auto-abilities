#!/usr/bin/env python3
"""Round 126 (harness 125): the firing flag from the game's reload table.

User rulings 2026-11-03:
  (1) rule 4 relaxed: a baked stat is allowed when the engine has no live read;
  (2) log the "target within missile range" moment beside the ammo lines, so one
      battle shows how much warning it gives before the first shot;
  (3) the reload-skill question answered: reload = base x (1 - skill / 100), which
      can only move the cast point EARLIER (the safe direction).
The round-125 window (1.25 x the unit's most recent measured gap, drops < 1 s =
one volley) is DELETED: the field log of 2026-11-03 showed it flicker (23 episodes
on the Helstorm). In its place, per ranged unit, from FOURTH.RELOAD_S (generated
by tools/gen_reload_table.py from the game's own tables):
  FIRING ON   on the first ammo drop of an episode (the first shot)
  CAST POINT  first shot + 0.5 x reload (logged once per episode; nothing cast)
  FIRING OFF  no drop for 1.25 x reload (10 s for a unit missing from the table)
  IN RANGE / OUT OF RANGE  target within the unit's own live missile_range()
Applied to the live source (with logging) and the annotated copy (log-free).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_reload_table  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"

HEAD = """-- ============================================================================
-- ROUND 126 - THE FIRING FLAG FROM THE GAME'S RELOAD TABLE (READ-ONLY: nothing
-- is cast from it yet). The battle API has no "this unit is shooting" read and
-- no reload read; ammo_left() drops when the unit fires (field-proven
-- 2026-11-03), and every ranged unit's reload comes from FOURTH.RELOAD_S below,
-- GENERATED from the game's own tables (user ruling 2026-11-03: a baked stat is
-- allowed when no live read exists). Per ranged unit, per poll (250 ms):
--   * FIRING ON   on the first poll whose ammo_left() is LOWER than the poll
--                 before - the first shot of an episode, which cannot be
--                 anticipated;
--   * CAST POINT  first shot + AMMO_CAST_FRACTION (0.5) x the unit's reload:
--                 where a firing-boosting ability would be cast - before the
--                 models that fired first can fire again (the user's design).
--                 Logged once per episode; NOTHING is cast in this round;
--   * FIRING OFF  once no drop has been seen for AMMO_OFF_FACTOR (1.25) x the
--                 unit's reload (AMMO_WINDOW_DEFAULT_S for a unit missing from
--                 the table). The round-125 rule (1.25 x the most recent
--                 measured gap) flickered on every unit in the field and is gone;
--   * IN RANGE / OUT OF RANGE: the unit's current target within its own LIVE
--                 missile_range() (unit_distance, edge to edge), logged on each
--                 change; FIRING ON reports how long the unit had been in range
--                 before its first shot - the measurement that decides whether
--                 the first shot can be predicted;
--   * a rise in ammo_left() is a resupply, never a shot.
-- Units with no ammunition (starting_ammo() 0, or unreadable) are read ONCE.
-- ============================================================================
FOURTH.AMMO_WINDOW_DEFAULT_S = 10     -- FIRING OFF window for a ranged unit missing from FOURTH.RELOAD_S
FOURTH.AMMO_OFF_FACTOR = 1.25         -- FIRING OFF after 1.25 x the unit's reload with no drop
FOURTH.AMMO_CAST_FRACTION = 0.5       -- CAST POINT: first shot + 0.5 x the unit's reload (user, 2026-11-03)
FOURTH.ammo = setmetatable({}, { __mode = "k" })   -- per tracked entry: start, reload, last, firing, ...

"""

DESCRIBE = """-- One unit's description for an AMMO / FIRING line: ui id, type, and its
-- current target with that target's melee state (every read pcall'd).
function FOURTH.ammo_describe(u)
	local id, ty = "?", "?"
	pcall(function() id = tostring(u:unique_ui_id()) end)
	pcall(function() ty = tostring(u:type()) end)
	local tgt, tmelee = "none", "?"
	local ok_t, t = pcall(function() return u:current_target() end)
	if ok_t and t ~= nil then
		tgt = "?"
		pcall(function() tgt = tostring(t:type()) end)
		local ok_m, m = pcall(function() return t:is_in_melee() end)
		if ok_m and type(m) == "boolean" then tmelee = m and "true" or "false" end
	end
	return "unit " .. id .. " '" .. ty .. "'", "target='" .. tgt .. "' target_in_melee=" .. tmelee
end

"""

IN_RANGE = """-- Is the unit's current target within the unit's own live missile range?
-- true / false, or nil when a read is unavailable (the state is then left as
-- it was). Returns the distance and the range too, for the log.
function FOURTH.ammo_in_range(u)
	local ok_t, t = pcall(function() return u:current_target() end)
	if not ok_t or t == nil then return false, nil, nil end
	local ok_r, r = pcall(function() return u:missile_range() end)
	local ok_d, d = pcall(function() return u:unit_distance(t) end)
	if not (ok_r and type(r) == "number" and r > 0 and ok_d and type(d) == "number" and d >= 0) then
		return nil, nil, nil
	end
	return d <= r, d, r
end

"""

PROBE = """function FOURTH.ammo_probe(units)
	if units == nil then return end
	local now_s = tick_count * POLL_MS / 1000
	for i = 1, #units do
		local su = units[i]
		local u = su and su.unit
		if u ~= nil then
			local st = FOURTH.ammo[su]
			if st == nil then
				local ok_s, start = pcall(function() return u:starting_ammo() end)
				st = { start = (ok_s and type(start) == "number") and start or 0, firing = false }
				if st.start > 0 then
					local ok_ty, ty = pcall(function() return u:type() end)
					if ok_ty and type(ty) == "string" then st.reload = FOURTH.RELOAD_S[ty] end
				end
				FOURTH.ammo[su] = st
			end
			if st.start > 0 then
				local inr, d, r = FOURTH.ammo_in_range(u)
				if inr == true and not st.in_range then
					st.in_range = true
					st.in_range_since = now_s
%%IN_LOG%%
				elseif inr == false and st.in_range then
					st.in_range = false
					st.in_range_since = nil
%%OUT_LOG%%
				end
				local ok_a, now = pcall(function() return u:ammo_left() end)
				if ok_a and type(now) == "number" then
					if st.last ~= nil and now < st.last then
						local was_firing = st.firing
						st.firing = true
						st.last_drop_s = now_s
%%DROP_LOG%%
						if not was_firing then
							st.first_shot_s = now_s
							st.cast_point_passed = false
%%ON_LOG%%
						end
%%RISE%%
					end
					st.last = now
				end
				if st.firing then
					if st.reload ~= nil and not st.cast_point_passed
						and (now_s - st.first_shot_s) >= FOURTH.AMMO_CAST_FRACTION * st.reload then
						st.cast_point_passed = true
%%CAST_LOG%%
					end
					local window = (st.reload ~= nil) and (FOURTH.AMMO_OFF_FACTOR * st.reload)
						or FOURTH.AMMO_WINDOW_DEFAULT_S
					if (now_s - st.last_drop_s) > window then
						st.firing = false
%%OFF_LOG%%
					end
				end
			end
		end
	end
end

"""

LOGS = {
    "%%IN_LOG%%": """					local who = FOURTH.ammo_describe(u)
					log(string.format("IN RANGE %s at t=%.2fs: target at %.1fm <= missile range %.1fm", who, now_s, d, r))""",
    "%%OUT_LOG%%": """					local who = FOURTH.ammo_describe(u)
					log(string.format("OUT OF RANGE %s at t=%.2fs: target at %.1fm > missile range %.1fm", who, now_s, d, r))""",
    "%%DROP_LOG%%": """						local who, aim = FOURTH.ammo_describe(u)
						log(string.format("AMMO %s: %s -> %s of %s at t=%.2fs %s", who, tostring(st.last),
							tostring(now), tostring(st.start), now_s, aim))""",
    "%%ON_LOG%%": """							local lead = "never in range before it"
							if st.in_range_since ~= nil then
								lead = string.format("in range %.2fs before it", now_s - st.in_range_since)
							end
							log(string.format("FIRING ON %s at t=%.2fs (first shot; %s; reload %s) %s", who, now_s,
								lead, st.reload and string.format("%gs", st.reload) or "not in the table", aim))""",
    "%%RISE%%": """					elseif st.last ~= nil and now > st.last then
						local who = FOURTH.ammo_describe(u)
						log("AMMO " .. who .. ": " .. tostring(st.last) .. " -> " .. tostring(now)
							.. " of " .. tostring(st.start) .. " - RESUPPLIED (not a shot)")""",
    "%%CAST_LOG%%": """						local who, aim = FOURTH.ammo_describe(u)
						log(string.format("CAST POINT %s at t=%.2fs: first shot %.2fs + %g x reload %gs (nothing is cast in this round) %s",
							who, now_s, st.first_shot_s, FOURTH.AMMO_CAST_FRACTION, st.reload, aim))""",
    "%%OFF_LOG%%": """						local who = FOURTH.ammo_describe(u)
						log(string.format("FIRING OFF %s at t=%.2fs (no drop for %.2fs > window %.2fs%s)", who, now_s,
							now_s - st.last_drop_s, window,
							st.reload and string.format(" = %g x reload %gs", FOURTH.AMMO_OFF_FACTOR, st.reload)
								or ", no reload in the table: default"))""",
}


def probe(with_logs):
    s = PROBE
    for k, v in LOGS.items():
        if with_logs:
            s = s.replace(k, v)
        elif k == "%%RISE%%":
            s = s.replace(k + "\n", "")
        else:
            s = s.replace(k + "\n", "")
    if not with_logs:
        s = s.replace("\t\t\t\t\t\tlocal was_firing = st.firing\n", "")
        s = s.replace("\t\t\t\t\t\tif not was_firing then\n", "\t\t\t\t\t\tif not st.was_on then\n")
    return s


RELOAD = gen_reload_table.block() + "\n"

for path, with_logs in ((SRC, True), (ANN, False)):
    s = open(path, encoding="utf-8", newline="").read()
    assert "\r\n" not in s and "RELOAD_S" not in s, path
    a = s.index("-- ROUND 125 - THE AMMO PROBE (READ-ONLY: nothing is cast from it).")
    a = s.rindex("-- ====", 0, a)
    b = s.index("local function poll_body()\n", a)
    old = s[a:b]
    assert "function FOURTH.ammo_probe(units)" in old and "AMMO_SAME_VOLLEY_S" in old, path
    body = probe(with_logs)
    if not with_logs:
        # the reading copy has no was_firing local: keep the same decision with a field
        body = body.replace("\t\t\t\t\t\tst.firing = true\n",
                            "\t\t\t\t\t\tst.was_on = st.firing\n\t\t\t\t\t\tst.firing = true\n", 1)
    new = HEAD + RELOAD + (DESCRIBE if with_logs else "") + IN_RANGE + body
    if not with_logs:
        assert "log(" not in new, "the reading copy must stay log-free"
    assert "\u2014" not in HEAD + IN_RANGE + body
    s = s[:a] + new + s[b:]
    open(path, "w", encoding="utf-8", newline="").write(s)
    print("replaced the round-125 probe in", path.split("\\")[-1], "(%d -> %d bytes)" % (len(old), len(new)))
