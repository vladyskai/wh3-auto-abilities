-- ============================================================================
-- HARNESS 210 (round 212: a transformed unit is a NEW unit, the watch list comes from the army's own unit list).
--   0zz58 the round-212 tokens in both files.
--   The worlds model the field case: the script-unit list keeps answering the first hero (the ghost after the
--   transformation), the army's own list answers what really stands on the field.
--   TF1 a hero (id A) in melee owns the Whirlwind and casts it. Then the army's own list holds ONE other unit (id B,
--       in melee, owning Eruption) -> B casts Eruption within 12 s, and A casts nothing more after the re-list.
--       RED (round 211): Eruption is never cast, A keeps casting.
--   TF2 the army's own list holds the same hero the script units have -> the hero casts, through the GAME's script
--       unit (no controller is created) (GREEN and RED).
--   TF3 the army's own list cannot be read -> the hero casts as before (GREEN and RED).
--   TF4 the army's list holds a new unit but no controller can be created for it -> it is left out (no cast by B, no
--       error), and the old hero is dropped (GREEN). RED: A keeps casting.
--   TF5 the army's own list is empty -> nothing changes, the hero casts (GREEN and RED).
--   RED control: H210_LIVE / H210_ANN on docs/backups/round212/pre212_*.lua.
-- ============================================================================
function run_h210()
  local L210 = os.getenv("H210_LIVE") or LIVE
  local A210 = os.getenv("H210_ANN") or ANN
  local RED210 = (os.getenv("H210_LIVE") ~= nil) or (os.getenv("H210_ANN") ~= nil)
  local EW = "wh3_dlc25_unit_abilities_whirlwind_of_death_ror"
  local ERU = "wh3_main_character_abilities_eruption"
  local CASTER = "wh2_dlc13_emp_cha_huntsmen_general_0"
  local pre210 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  print("== HARNESS 210 - section 0zz58: the round-212 tokens ==")
  for _, f in ipairs({ { name = "live", path = L210 }, { name = "ann", path = A210 } }) do
    local s = read_file(f.path)
    local fn = cp(s, "\nfunction cast_gate.raw_items(sunits, total)\n")
    local use = cp(s, "\tlocal items, revive = cast_gate.raw_items(sunits, total)\n") + cp(s, "\tfor i = 1, #items do\n\t\tlocal script_unit = items[i]\n")
    local fetch = cp(s, "\treturn cast_gate.raw_sunits[want]   -- ROUND 212")
    local relist = cp(s, "\tif FOURTH.relist_at ~= nil and tick_count >= FOURTH.relist_at then\n")
      + cp(s, "\tFOURTH.relist_at = tick_count + 8   -- ROUND 212")
    if RED210 then
      check("0zz58 " .. f.name .. " (RED): the pre-212 file reads the script units only",
        fn == 0 and use == 0 and fetch == 0 and relist == 0)
    else
      check("0zz58 " .. f.name .. ": the army's own list feeds the watch list (" .. fn .. ", " .. use .. "), the two fetchers "
        .. "fall back to the made script unit (" .. fetch .. "), the re-list after a cast (" .. relist .. ")",
        fn == 1 and use == 2 and fetch == 2 and relist == 2)
    end
  end
  local FILES = { { path = A210, tag = "[annotated] " }, { path = L210, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  local function verdict(TAG, id, text, ok)
    check(TAG .. id .. (RED210 and "-RED" or "") .. ": " .. text, ok)
    done(ok)
  end
  local function casts(W, key, uid)
    local n = 0
    for _, x in ipairs(W.fires) do if x.key == key and x.uid == uid then n = n + 1 end end
    return n
  end
  local function list(t)
    return { count = function(self) return #t end, item = function(self, i) return t[i] end }
  end
  -- the hero A is a script unit. The twin B is built by the mock's own factory (as an entry of the enemy collection,
  -- which the friendly script-unit list never answers): the unit object and the controller that records its casts.
  local function mk(wname, base, PATH, TAG)
    local hero = { name = CASTER, uid = base, owns = { EW }, melee = true, dist = 5, width = 2, men_alive = 1,
                   unit_class = "com", hp_frac = 1.0 }
    local twin = { name = CASTER, uid = base + 1, owns = { ERU }, melee = true, dist = 5, width = 2, men_alive = 1,
                   unit_class = "com", hp_frac = 1.0 }
    local W = make_world({ can_perform = true, units = { hero }, enemies = { twin },
      cards = { { id = tostring(base), state = "active", vis = true }, { id = tostring(base + 1), state = "active", vis = true } },
      bar = { { id = "b1", key = EW } } })
    W.defaults_on = true
    print("== " .. TAG .. wname .. " ==")
    W.bm.get_player_alliance = function() return "OUR_ALLIANCE" end
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    W.made_controllers = 0
    W.army_units = nil   -- nil = the army's own list raises
    W.controller_ok = true
    W.bm.get_player_army = function(self)
      return {
        units = function() if W.army_units == nil then error("no unit list", 0) end; return list(W.army_units) end,
        create_unit_controller = function()
          if not W.controller_ok then error("no controller", 0) end
          W.made_controllers = W.made_controllers + 1
          local twin_uc = W.enemy_entries[1].uc
          return { add_units = function(self, u) end,
                   perform_special_ability = function(self, k, u) return twin_uc:perform_special_ability(k, u) end,
                   perform_special_ability_ground = function(self, ...) return twin_uc:perform_special_ability_ground(...) end,
                   take_control = function(self) return twin_uc:take_control() end,
                   release_control = function(self) return twin_uc:release_control() end }
        end,
      }
    end
    deploy_phases(W); ui(W)
    W.conflict = true
    return W
  end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    do
      local W = mk("TF1. the hero transforms: the army's own list holds a new unit", 21200, P, TAG)
      if W ~= nil then
        W.army_units = { W.mock_units[1] }
        polln(W, 6)
        local a0 = casts(W, EW, 21200)
        W.army_units = { W.enemy_entries[1].unit }
        polln(W, 48)
        local a1, b1 = casts(W, EW, 21200), casts(W, ERU, 21201)
        polln(W, 24)
        local a2, b2 = casts(W, EW, 21200), casts(W, ERU, 21201)
        local good = (a0 >= 1 and b1 >= 1 and a2 == a1 and W.made_controllers == 1)
        if RED210 then good = (a0 >= 1 and b2 == 0 and a2 > a1) end
        verdict(TAG, "TF1a", "the hero cast " .. a0 .. " time(s) before. After the transformation the new unit cast Eruption "
          .. b1 .. " time(s) within 12 s (" .. b2 .. " by 18 s), the old hero " .. (a2 - a1) .. " more time(s) in the last 6 s, "
          .. W.made_controllers .. " controller(s) made" .. (RED210 and " (RED: no Eruption, the ghost keeps casting)" or ""), good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("TF2. the army's own list holds the same hero the script units have", 21210, P, TAG)
      if W ~= nil then
        W.army_units = { W.mock_units[1] }
        polln(W, 48)
        local a, b = casts(W, EW, 21210), casts(W, ERU, 21211)
        verdict(TAG, "TF2a", "the hero cast " .. a .. " time(s), the other unit " .. b .. ", " .. W.made_controllers
          .. " controller(s) made (need at least 1, 0, 0)", a >= 1 and b == 0 and W.made_controllers == 0)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("TF3. the army's own list cannot be read", 21220, P, TAG)
      if W ~= nil then
        polln(W, 48)
        local a = casts(W, EW, 21220)
        verdict(TAG, "TF3a", "the hero cast " .. a .. " time(s) (need at least 1), " .. W.made_controllers .. " controller(s) made",
          a >= 1 and W.made_controllers == 0)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("TF4. a new unit, but no controller can be created for it", 21230, P, TAG)
      if W ~= nil then
        W.army_units = { W.mock_units[1] }
        polln(W, 6)
        W.controller_ok = false
        W.army_units = { W.enemy_entries[1].unit }
        polln(W, 48)
        local a1, b1 = casts(W, EW, 21230), casts(W, ERU, 21231)
        polln(W, 24)
        local a2, b2 = casts(W, EW, 21230), casts(W, ERU, 21231)
        local good = (b2 == 0 and a2 == a1)
        if RED210 then good = (b2 == 0 and a2 > a1) end
        verdict(TAG, "TF4a", "the new unit cast " .. b2 .. " time(s) (need 0), the old hero " .. (a2 - a1)
          .. " more time(s) in the last 6 s (" .. (RED210 and "RED: it keeps casting" or "need 0: dropped") .. ")", good)
        tally(W)
      else
        done(false)
      end
    end
    do
      local W = mk("TF5. the army's own list is empty", 21240, P, TAG)
      if W ~= nil then
        W.army_units = {}
        polln(W, 48)
        local a = casts(W, EW, 21240)
        verdict(TAG, "TF5a", "the hero cast " .. a .. " time(s) (need at least 1)", a >= 1)
        tally(W)
      else
        done(false)
      end
    end
  end
  check("HARNESS 210: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 210 done: " .. (checks - pre210) .. " checks in this section ==")
end
