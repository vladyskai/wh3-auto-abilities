-- ============================================================================
-- HARNESS 217 (round 219, sign-off): the placed blasts hit MOST OF THE TARGET UNIT, standing cavalry is a target,
--   the timing probe names the trigger families (live copy only).
--   The worlds use the numbers of the battle that showed the problem (archive/logs/battle_20261128_r218_perf.txt).
--   0zz65 the round-219 tokens in both files, the per-family timer in the live copy.
--   CV1 Brass Orb, Free Company Militia standing, 110 of 120 men on a 31.7 m front -> ONE cast (RED: none, the
--       96-soldier line).
--   CV2 Brass Orb, 60 Outriders standing on a 37.4 m front -> ONE cast (RED: none, cavalry was no candidate).
--   CV3 the same Outriders moving -> no cast.
--   CV4 the same Outriders, one of our units 15 m from them -> no cast.
--   CV5 an infantry remnant of 18 men -> no cast (the floor of 20).
--   CV6 12 riders -> no cast.
--   CV7 46 Outriders on a 40.4 m front -> ONE cast (RED: none).
--   TT1 live copy, the probe on: 10 PERF lines bring ONE 'PERF TRIG 10s:' line naming enemy_wander. RED: none.
--   RED control: H217_LIVE / H217_ANN on docs/backups/round219/pre219_*.lua.
-- ============================================================================
function run_h217()
  local L217 = os.getenv("H217_LIVE") or LIVE
  local A217 = os.getenv("H217_ANN") or ANN
  local RED217 = (os.getenv("H217_LIVE") ~= nil) or (os.getenv("H217_ANN") ~= nil)
  local BO = "wh2_dlc12_character_abilities_brass_orb"
  local CASTER = "wh2_dlc12_skv_cha_warlock_master_0"
  local MIL = "wh_dlc04_emp_inf_free_company_militia_0"
  local OUT = "wh_main_emp_cav_outriders_0"
  local SW = "wh2_main_skv_inf_stormvermin_0"
  local pre217 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 217 - section 0zz65: the round-219 tokens ==")
  for _, f in ipairs({ { name = "live", path = L217 }, { name = "ann", path = A217 } }) do
    local s = read_file(f.path)
    local got = cp(s, "\nfunction FOURTH.cover_need(line, men)\n") + cp(s, "\nfunction FOURTH.ww_map(m)\n")
      + cp(s, "FOURTH.COVER_FRACTION = 0.50\n") + cp(s, "FOURTH.COVER_MIN_MEN = 20\n")
      + cp(s, "\tif sc < FOURTH.blob_need(row.r) and own < FOURTH.cover_need(FOURTH.blob_need(row.r), e.men) then return nil end")
      + cp(s, "\nFOURTH.CAV_SPACING_TEXT = \"") + cp(s, "\nfunction FOURTH.cover_own(e, r)\n")
      + cp(s, "\tm = FOURTH.ww_map(m)   -- ROUND 219: infantry and cavalry\n")
    local timer = cp(s, "\nfunction FOURTH.perf_trig(name, t0)\n") + cp(s, "\t\t\t\t\tFOURTH.perf_trig(ability.trigger, perf_e0)\n")
    local want_timer = (f.name == "live") and 2 or 0
    if RED217 then
      check("0zz65 " .. f.name .. " (RED): the pre-219 file has none of it", got == 0 and timer == 0)
    else
      check("0zz65 " .. f.name .. ": the cover rule, the wander map and the cavalry spacing table (" .. got
        .. " of 8), the per-family timer in the live copy only (" .. timer .. " of " .. want_timer .. ")",
        got == 8 and timer == want_timer)
    end
  end
  local FILES = { { path = A217, tag = "[annotated] " }, { path = L217, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function world(wname, units, enemies, PATH, TAG, sv, perf_on)
    local cards = {}
    for _, d in ipairs(units) do cards[#cards + 1] = { id = tostring(d.uid), state = "active", vis = true } end
    local W = make_world({ can_perform = true, units = units, enemies = enemies, cards = cards,
      bar = { { id = "b1", key = BO } } })
    W.defaults_on = false
    W.perf_on = perf_on
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        local id = nil
        pcall(function() id = tostring(pr.unit:unique_ui_id()) end)
        pr.unit.is_visible_to_alliance = function(self, a) return true end
        pr.unit.is_currently_flying = function(self) return false end
        local v = sv[id]
        if v ~= nil then pr.unit.strategic_value = function(self) return v end end
      end
    end
    sel_event(W, units[1].uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_brass_orb"); ui(W)
    sel_event(W, units[1].uid, false); ui(W)
    W.conflict = true
    polln(W, 4)
    return W
  end
  local function caster(b)
    return { name = CASTER, uid = b, owns = { BO }, melee = false, dist = 60, pos = { 0, 0, 0 }, width = 2,
             men_alive = 1, unit_class = "com" }
  end
  local function foe(uid, name, cls, men, men0, width, o)
    local e = { uid = uid, name = name, melee = false, pos = { 0, 0, 80 }, width = width, men_alive = men,
                initial_men = men0, unit_class = cls, dist = 60 }
    for k, v in pairs(o or {}) do e[k] = v end
    return e
  end
  local function ours(uid, x, z)
    return { uid = uid, name = SW, owns = {}, melee = false, pos = { x, 0, z }, width = 20, men_alive = 100,
             initial_men = 100, unit_class = "inf_mel" }
  end
  -- name, builder(b) -> units, enemies, sv; GREEN casts; RED casts (nil = not run in RED)
  local WORLDS = {
    { "CV1. Free Company Militia, 110 of 120 men standing on a 31.7 m front -> ONE cast",
      function(b) return { caster(b) }, { foe(b + 5, MIL, "inf_mis", 110, 120, 31.7) }, { [tostring(b + 5)] = 430 } end, 1, 0 },
    { "CV2. 60 Outriders standing on a 37.4 m front -> ONE cast",
      function(b) return { caster(b) }, { foe(b + 5, OUT, "cav_mis", 60, 60, 37.4) }, { [tostring(b + 5)] = 990 } end, 1, 0 },
    { "CV3. the same Outriders moving -> no cast",
      function(b) return { caster(b) }, { foe(b + 5, OUT, "cav_mis", 60, 60, 37.4, { moving = true }) },
        { [tostring(b + 5)] = 990 } end, 0, nil },
    { "CV4. the same Outriders, one of our units 14 m from their centre -> no cast",
      function(b) return { caster(b), ours(b + 1, 0, 100) }, { foe(b + 5, OUT, "cav_mis", 60, 60, 37.4) },
        { [tostring(b + 5)] = 990 } end, 0, nil },
    { "CV5. an infantry remnant of 18 men -> no cast",
      function(b) return { caster(b) }, { foe(b + 5, MIL, "inf_mis", 18, 120, 9) }, { [tostring(b + 5)] = 70 } end, 0, nil },
    { "CV6. 12 riders -> no cast",
      function(b) return { caster(b) }, { foe(b + 5, OUT, "cav_mis", 12, 60, 12) }, { [tostring(b + 5)] = 200 } end, 0, nil },
    { "CV7. 46 Outriders standing on a 40.4 m front -> ONE cast",
      function(b) return { caster(b) }, { foe(b + 5, OUT, "cav_mis", 46, 48, 40.4) }, { [tostring(b + 5)] = 990 } end, 1, 0 },
  }
  for _, f in ipairs(FILES) do
    local TAG = f.tag
    for i, w in ipairs(WORLDS) do
      local want = w[3]
      if RED217 then want = w[4] end
      if want ~= nil then
        local b = 21900 + i * 20
        local units, enemies, sv = w[2](b)
        local W = world(w[1], units, enemies, f.path, TAG, sv, nil)
        if W ~= nil then
          local got, tid = 0, nil
          for _, x in ipairs(W.fires) do
            if x.key == BO then
              got = got + 1
              if tid == nil then pcall(function() tid = tostring(x.target:unique_ui_id()) end) end
            end
          end
          local ok = (got == want) and (want == 0 or tid == tostring(b + 5))
          check(TAG .. string.sub(w[1], 1, 3) .. (RED217 and "-RED" or "") .. ": " .. got .. " cast(s) (need " .. want
            .. ")" .. (want > 0 and (", at " .. tostring(tid)) or ""), ok)
          done(ok)
          tally(W)
        else
          done(false)
        end
      end
    end
  end
  do
    local b = 22100
    local W = world("TT1. the probe on: the families are timed", { caster(b) },
      { foe(b + 5, MIL, "inf_mis", 110, 120, 31.7) }, L217, "[live] ", { [tostring(b + 5)] = 430 }, true)
    if W ~= nil then
      for i = 1, 230 do
        ui(W)
        if i % 5 == 0 then polln(W, 1) end
      end
      local lines = count_log(W, "PERF TRIG 10s: all evaluators ")
      local named = count_log(W, "| enemy_wander ")
      local good = (lines >= 1 and named >= 1)
      if RED217 then good = (lines == 0) end
      check("[live] TT1" .. (RED217 and "-RED" or "") .. ": " .. lines .. " 'PERF TRIG 10s:' line(s) ("
        .. (RED217 and "RED: 0" or "need at least 1") .. "), " .. named .. " naming enemy_wander", good)
      done(good)
      tally(W)
    else
      done(false)
    end
  end
  check("HARNESS 217: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 217 done: " .. (checks - pre217) .. " checks in this section ==")
end
