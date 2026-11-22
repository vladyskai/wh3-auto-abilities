-- ============================================================================
-- HARNESS 209 (round 211, tuning: the read-only raw unit probe of the test build, live copy only).
--   0zz57 the round-211 tokens in the live file (the annotated copy has no probe).
--   RP1 the mock battle manager has no alliances() -> no RAW line, no failure line, the hero still casts.
--   RP2 alliances() answers one player army with two units: the hero the mod holds, and ANOTHER object with the same
--       id (a transformed copy) -> RAW lines with held=same and held=OTHER, the hero still casts once per window.
--   RP3 alliances() raises -> ONE "RAW probe failed" line, the hero still casts.
--   RED control: H209_LIVE on docs/backups/round211/pre211_live.lua (no RAW line in any world).
-- ============================================================================
function run_h209()
  local L209 = os.getenv("H209_LIVE") or LIVE
  local RED209 = (os.getenv("H209_LIVE") ~= nil)
  local EW = "wh3_dlc25_unit_abilities_whirlwind_of_death_ror"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local pre209 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 209 - section 0zz57: the round-211 tokens ==")
  do
    local s = read_file(L209)
    local fn = cp(s, "\nfunction FOURTH.raw_probe(tick)\n")
    local call = cp(s, "\tpcall(FOURTH.raw_probe, tick)   -- ROUND 211: read-only\n")
    local orders = 0
    local at = raw_find(s, "\nfunction FOURTH.raw_probe(tick)\n", 1, true)
    if at ~= nil then
      local blk = string.sub(s, at, raw_find(s, "\nfunction FOURTH.map_tick(tick)\n", at, true))
      orders = cp(blk, "perform_special_ability") + cp(blk, "cast_gate") + cp(blk, "owned_keys_by_unit")
    end
    if RED209 then
      check("0zz57 live (RED): the pre-211 file has no raw probe", fn == 0 and call == 0)
    else
      check("0zz57 live: the probe (" .. fn .. "), called once from the map probe (" .. call
        .. "), orders nothing and writes no mod state (" .. orders .. ")", fn == 1 and call == 1 and orders == 0)
    end
  end
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function verdict(id, text, ok)
    check("[live] " .. id .. (RED209 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  local function list(t)
    return { count = function(self) return #t end, item = function(self, i) return t[i] end }
  end
  local function mk(wname, uid, alliances)
    local W = make_world({ can_perform = true, units = { { name = CASTER, uid = uid, owns = { EW }, melee = true, dist = 5,
      width = 2, men_alive = 1, unit_class = "com", hp_frac = 1.0 } }, enemies = {},
      cards = { { id = tostring(uid), state = "active", vis = true } }, bar = { { id = "b1", key = EW } } })
    W.defaults_on = true
    print("== [live] " .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, L209)
    check("[live] " .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    if alliances ~= nil then W.bm.alliances = alliances(W) end
    deploy_phases(W); ui(W)
    W.conflict = true
    polln(W, 20)
    return W
  end
  local function casts(W)
    local n = 0
    for _, x in ipairs(W.fires) do if x.key == EW then n = n + 1 end end
    return n
  end
  do
    local W = mk("RP1. no alliances() on the battle manager", 21100, nil)
    if W ~= nil then
      local raw, fail = count_log(W, "RAW t="), count_log(W, "RAW probe failed")
      verdict("RP1a", raw .. " RAW line(s), " .. fail .. " failure line(s), " .. casts(W) .. " cast(s) (need 0, 0, at least 1)",
        raw == 0 and fail == 0 and casts(W) >= 1)
      tally(W)
    else
      done(false)
    end
  end
  do
    local W = mk("RP2. one player army: the held hero and another object with the same id", 21110, function(W)
      return function(self)
        local twin = {
          unique_ui_id = function() return 21110 end,
          type = function() return "transformed_twin" end,
          position = function() return { get_x = function() return 40 end, get_z = function() return 50 end } end,
          number_of_men_alive = function() return 1 end,
          unary_hitpoints = function() return 0.5 end,
          is_in_melee = function() return true end,
          owned_special_abilities = function() return { EW, "some_other_key" } end,
        }
        local army = { is_player_controlled = function() return true end,
                       units = function() return list({ W.mock_units[1], twin }) end }
        return list({ { armies = function() return list({ army }) end } })
      end
    end)
    if W ~= nil then
      local same, other = count_log(W, " held=same "), count_log(W, " held=OTHER ")
      local army, twin = count_log(W, "RAW_ARMY t="), count_log(W, "type=transformed_twin x=40.0 z=50.0 men=1 hp=0.50 melee=true")
      local good = (same >= 1 and other >= 1 and army >= 1 and twin >= 1 and casts(W) >= 1)
      if RED209 then good = (same == 0 and other == 0 and army == 0 and casts(W) >= 1) end
      verdict("RP2a", same .. " held=same, " .. other .. " held=OTHER, " .. army .. " army line(s), " .. twin
        .. " full twin line(s), " .. casts(W) .. " cast(s)" .. (RED209 and " (RED: no RAW line)" or ""), good)
      tally(W)
    else
      done(false)
    end
  end
  do
    local W = mk("RP3. alliances() raises", 21120, function(W)
      return function(self) error("no such list", 0) end
    end)
    if W ~= nil then
      local fail = count_log(W, "RAW probe failed (said once)")
      local good = (fail == 1 and casts(W) >= 1)
      if RED209 then good = (fail == 0 and casts(W) >= 1) end
      verdict("RP3a", fail .. " failure line(s) (" .. (RED209 and "RED: 0" or "need exactly 1") .. "), " .. casts(W) .. " cast(s)", good)
      tally(W)
    else
      done(false)
    end
  end
  check("HARNESS 209: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 209 done: " .. (checks - pre209) .. " checks in this section ==")
end
