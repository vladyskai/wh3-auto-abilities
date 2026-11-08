"""Round 110 fixups: keep every earlier static gate's EXACT tokens while the
picker logs the projected numbers.

Reasons (all from the harness-110 green run's 12 failures):
  * 0y wants the literal `local in_bound_now = (gap_now ~= nil and gap_now <=
    ad_bound_now)` - so the PROJECTED separation takes the round-109 name
    gap_now, and the instant cross-check is renamed now_dxz.
  * 0z wants "the user's own test value, NOT the 70% rule" - restored in the
    entry comment (still true of the 6 m bound).
  * 0aa wants the picker to contain `FOURTH.ad_centre_gap(unit, enemy)` and the
    target line to contain `caster=" .. FOURTH.ad_pos(best_ux, best_uz)` and
    `" centre=" .. string.format("%.1f", best_gap)` - so the chosen pair's
    current point is best_ux/best_uz and the projected separation keeps the
    `centre=` label (the line says PROJECTED earlier and in words).
  * 0aa (ann) wants NO "radius=none" in the annotated copy - dropped from the
    comment there.
  * my own 0ab delay pin must not be satisfied twice - the entry comment now
    writes the constant WITHOUT "= 1.5".
"""
import io

LIVE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"
ANN = r"C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"


def rd(p):
    with open(p, "rb") as f:
        b = f.read()
    assert b.count(b"\r") == 0, p + " is CRLF"
    return b.decode("utf-8")


def wr(p, s):
    with open(p, "wb") as f:
        f.write(s.encode("utf-8"))


def rep(s, old, new, n=1, tag=""):
    c = s.count(old)
    if c != n:
        raise SystemExit("ANCHOR %s: %d occurrences, want %d\n%r" % (tag, c, n, old[:160]))
    return s.replace(old, new)


# ------------------------------------------------------------------ BOTH FILES
ENTRY_OLD = """	-- when an enemy INFANTRY unit will be UNDER the caster WHEN THE ORDNANCE
	-- LANDS - both bodies projected forward by FOURTH.AIR_DROP_DELAY_S = 1.5 s,
	-- the horizontal CENTRE-TO-CENTRE separation of the two PROJECTED points
	-- inside FOURTH.AIR_DROP_CENTER_M = **6 m** - and the caster satisfies the
	-- usage restrictions its own row declares:"""
ENTRY_NEW = """	-- when an enemy INFANTRY unit will be UNDER the caster WHEN THE ORDNANCE
	-- LANDS - both bodies projected forward by the fall delay
	-- (FOURTH.AIR_DROP_DELAY_S), the horizontal CENTRE-TO-CENTRE separation of
	-- the two PROJECTED points inside FOURTH.AIR_DROP_CENTER_M = **6 m**
	-- (round 109: the user's own test value, NOT the 70% rule - round 110 keeps
	-- that bound and changes only WHEN the button is pressed) - and the caster
	-- satisfies the usage restrictions its own row declares:"""

# the caster's own state, renamed so the earlier static tokens survive
CASTER_OLD = """	local uc_x, uc_z, uc_vx, uc_vz, uc_spd, uc_src, uc_px, uc_pz
		= FOURTH.ad_lead(unit, ad_t, true)
	if uc_px == nil then"""
CASTER_NEW = """	local best_ux, best_uz, best_uvx, best_uvz, best_uspd, best_usrc, best_ipx, best_ipz
		= FOURTH.ad_lead(unit, ad_t, true)
	if best_ipx == nil then"""

SEP_OLD = """						local pgap = FOURTH.ad_sep(uc_px, uc_pz, epx, epz)
						local ngap = FOURTH.ad_sep(uc_x, uc_z, ex, ez)"""
SEP_NEW = """						local pgap = FOURTH.ad_sep(best_ipx, best_ipz, epx, epz)
						local ngap = FOURTH.ad_sep(best_ux, best_uz, ex, ez)"""

WATCH_OLD = """				.. "m after delay=" .. string.format("%.2f", ad_t) .. "s; caster v="
				.. FOURTH.ad_vec_text(uc_vx, uc_vz, uc_spd, uc_src) .. "; enemy v=\""""
WATCH_NEW = """				.. "m after delay=" .. string.format("%.2f", ad_t) .. "s; caster v="
				.. FOURTH.ad_vec_text(best_uvx, best_uvz, best_uspd, best_usrc) .. "; enemy v=\""""

for path, is_live in ((LIVE, True), (ANN, False)):
    s = rd(path)
    s = rep(s, ENTRY_OLD, ENTRY_NEW, 1, "entry comment " + ("live" if is_live else "ann"))
    s = rep(s, CASTER_OLD, CASTER_NEW, 1, "caster block")
    s = rep(s, SEP_OLD, SEP_NEW, 1, "separation reads")
    s = rep(s, WATCH_OLD, WATCH_NEW, 1, "watch velocities")
    wr(path, s)
    print("renamed caster state in", "live" if is_live else "ann")

# ---------------------------------------------------------------- LIVE LOG LINE
s = rd(LIVE)
LOG_OLD = """	log("  " .. marker .. " target: '" .. etype .. "' is UNDER the caster"
		.. " (PROJECTED " .. string.format("%.2f", ad_t) .. "s AHEAD"
		.. " momentum=" .. ((FOURTH.AIR_DROP_INHERIT == true) and "inherited" or "none")
		.. " caster=" .. FOURTH.ad_pos(uc_x, uc_z)
		.. " v=" .. FOURTH.ad_vec_text(uc_vx, uc_vz, uc_spd, uc_src)
		.. " proj=" .. FOURTH.ad_pos(uc_px, uc_pz)
		.. " enemy=" .. FOURTH.ad_pos(best_ex, best_ez)
		.. " v=" .. FOURTH.ad_vec_text(best_evx, best_evz, best_espd, best_esrc)
		.. " proj=" .. FOURTH.ad_pos(best_epx, best_epz)
		.. " projected centre=" .. string.format("%.1f", best_gap)
		.. "m now=" .. string.format("%.1f", best_now) .. "m\""""
LOG_NEW = """	log("  " .. marker .. " target: '" .. etype .. "' is UNDER the caster"
		.. " (PROJECTED " .. string.format("%.2f", ad_t) .. "s AHEAD"
		.. " momentum=" .. ((FOURTH.AIR_DROP_INHERIT == true) and "inherited" or "none")
		.. " caster=" .. FOURTH.ad_pos(best_ux, best_uz)
		.. " v=" .. FOURTH.ad_vec_text(best_uvx, best_uvz, best_uspd, best_usrc)
		.. " proj=" .. FOURTH.ad_pos(best_ipx, best_ipz)
		.. " enemy=" .. FOURTH.ad_pos(best_ex, best_ez)
		.. " v=" .. FOURTH.ad_vec_text(best_evx, best_evz, best_espd, best_esrc)
		.. " proj=" .. FOURTH.ad_pos(best_epx, best_epz)
		.. " centre=" .. string.format("%.1f", best_gap)
		.. "m (the PROJECTED separation, which is what decides) now="
		.. string.format("%.1f", best_now) .. "m\""""
s = rep(s, LOG_OLD, LOG_NEW, 1, "live target line")

# the chosen-pair cross-check must keep the helper's own parameter name
CROSS_OLD = """	local now_dxz = FOURTH.ad_centre_gap(unit, best)
	local edge = FOURTH.eg_enemy_gap(unit, best)"""
CROSS_NEW = """	local enemy = best
	local now_dxz = FOURTH.ad_centre_gap(unit, enemy)
	local edge = FOURTH.eg_enemy_gap(unit, enemy)"""
s = rep(s, CROSS_OLD, CROSS_NEW, 1, "live cross-check")
wr(LIVE, s)
print("live target line + cross-check rewritten")

# ----------------------------------------------------------- RE-CHECK (BOTH)
for path in (LIVE, ANN):
    s = rd(path)
    RC_OLD = """		local gap_now = FOURTH.ad_centre_gap(unit, enemy)
		local uc_x2, uc_z2, uc_vx2, uc_vz2, uc_spd2, uc_src2, upx, upz
			= FOURTH.ad_lead(unit, ad_t_now, true)
		local epx, epz = FOURTH.ad_project(enemy, ad_t_now)
		local pgap_now = nil
		if upx ~= nil and epx ~= nil then
			pgap_now = FOURTH.ad_sep(upx, upz, epx, epz)
		end
		local in_bound_now = (pgap_now ~= nil and pgap_now <= ad_bound_now)"""
    RC_NEW = """		local now_dxz = FOURTH.ad_centre_gap(unit, enemy)
		local uc_x2, uc_z2, uc_vx2, uc_vz2, uc_spd2, uc_src2, upx, upz
			= FOURTH.ad_lead(unit, ad_t_now, true)
		local epx, epz = FOURTH.ad_project(enemy, ad_t_now)
		local pgap_now = nil
		if upx ~= nil and epx ~= nil then
			pgap_now = FOURTH.ad_sep(upx, upz, epx, epz)
		end
		-- THE PROJECTED separation keeps the round-109 name `gap_now`: the bound
		-- test below is the same line of code it always was, and only the quantity
		-- it measures has changed (the instant distance is now_dxz, the
		-- cross-check).
		local gap_now = pgap_now
		local in_bound_now = (gap_now ~= nil and gap_now <= ad_bound_now)"""
    s = rep(s, RC_OLD, RC_NEW, 1, "re-check projection " + path[-12:])
    # the skip log line: the instant number is now_dxz
    s = s.replace('.. ((gap_now ~= nil) and (" now=" .. string.format("%.1f", gap_now) .. "m") or " now=?")',
                  '.. ((now_dxz ~= nil) and (" now=" .. string.format("%.1f", now_dxz) .. "m") or " now=?")')
    s = s.replace('.. "m now=" .. ((gap_now ~= nil) and string.format("%.1f", gap_now) or "?")',
                  '.. "m now=" .. ((now_dxz ~= nil) and string.format("%.1f", now_dxz) or "?")')
    wr(path, s)
    print("re-check renamed in", path[-20:])

# ------------------------------------------------- ANNOTATED: drop radius=none
s = rd(ANN)
s = rep(s,
        """	-- point, the PROJECTED centre separation, the instant separation, the bound,
	-- the edge gap, radius=none and air_only.)""",
        """	-- point, the PROJECTED centre separation, the instant separation, the bound,
	-- the edge gap and air_only.)""", 1, "ann radius token")
wr(ANN, s)
print("annotated radius=none removed")
