-- ============================================================================
-- HARNESS 193 (round 194, user rulings 2026-11-21): REMEMBERED M/A STATES per unit type and ability (option A,
--   "implement"), the reset through an optional MCT settings script ("MCT should not be a requirement").
--   0zz42 the round-194 tokens in both files.
--   RM1 a click arms Hammer of Sigmar on a Warrior Priest: the file gets "<type> hammer_of_sigmar A".
--   RM2 the NEXT battle (a fresh load), another Warrior Priest, no click, in melee -> it casts (the remembered A).
--       RED: no cast (the pre-194 file forgets).
--   RM3 a click back to the default (off) removes the line: the file is empty.
--   RM4 the reset (the file emptied, as the MCT script does) -> the next battle, no click -> no cast.
--   RM5 another unit TYPE in the next battle is not affected by the remembered line -> no cast.
--   RED control: H193_LIVE / H193_ANN on docs/backups/round194/pre194_*.lua.
-- ============================================================================
function run_h193()
  local L193 = os.getenv("H193_LIVE") or LIVE
  local A193 = os.getenv("H193_ANN") or ANN
  local RED193 = (os.getenv("H193_LIVE") ~= nil) or (os.getenv("H193_ANN") ~= nil)
  local HOS = "wh_main_spell_bound_hammer_of_sigmar"
  local PRIEST = "wh_dlc04_emp_cha_warrior_priest_0"
  local OTHER = "wh_dlc04_emp_cha_arch_lector_0"
  local SQ = "wh_dlc07_brt_inf_foot_squires_0"
  local FILE = "h193_remember_test.txt"
  local pre193 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1; at = i + #tok
    end
  end
  local function slurp(p)
    local fh = io.open(p, "r")
    if fh == nil then return nil end
    local t = fh:read("*a")
    fh:close()
    return t
  end
  local function wipe(p)
    local fh = io.open(p, "w")
    if fh ~= nil then fh:close() end
  end
  print("== HARNESS 193 - section 0zz42: the round-194 tokens ==")
  for _, f in ipairs({ { name = "live", path = L193 }, { name = "ann", path = A193 } }) do
    local s = read_file(f.path)
    local head = cp(s, "-- ROUND 194 - REMEMBERED M/A STATES")
    local file = cp(s, 'FOURTH.REMEMBER_FILE = "smart_ability_autocast_settings.txt"')
    local write = cp(s, "FOURTH.remember(ui_id, marker, value)   -- ROUND 194: remembered for the unit's type")
    local read = cp(s, "local rv = FOURTH.remembered_value(slot, marker)   -- ROUND 194")
      + cp(s, "if a ~= nil and a.remembered ~= nil then   -- ROUND 194: the type's remembered switch comes first")
    if RED193 then
      check("0zz42 " .. f.name .. " (RED): the pre-194 file remembers nothing", head == 0 and file == 0 and write == 0 and read == 0)
    else
      check("0zz42 " .. f.name .. ": the block (" .. head .. file .. "), the write (" .. write .. "), the two reads (" .. read .. ")",
        head == 1 and file == 1 and write == 1 and read == 2)
    end
  end
  local FILES = { { path = A193, tag = "[annotated] " }, { path = L193, tag = "[live] " } }
  local n_ok, n_all = 0, 0
  local function done(ok) n_all = n_all + 1; if ok then n_ok = n_ok + 1 end end
  -- one battle: a caster in melee with a squire unit; clicks = how many badge clicks before the polls
  local function battle(TAG, P, wname, uid, utype, clicks)
    local units = { { name = utype, uid = uid, owns = { HOS }, melee = true, dist = 5 } }
    local W = make_world({ can_perform = true, units = units, enemies = { { name = SQ, uid = uid + 5, melee = true, dist = 5 } },
      cards = { { id = tostring(uid), state = "active", vis = true } }, bar = { { id = "b1", key = HOS } } })
    W.defaults_on = false
    W.remember_on = true
    W.remember_file = FILE
    print("== " .. TAG .. wname .. " ==")
    local ok = pcall(load_world, W, P)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return nil end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    for _ = 1, clicks do click(W, "zz_auto_badge_hos"); ui(W) end
    sel_event(W, uid, false); ui(W)
    W.conflict = true
    polln(W, 4)
    local n = 0
    for _, x in ipairs(W.fires) do if x.key == HOS then n = n + 1 end end
    tally(W)
    return n
  end
  for _, f in ipairs(FILES) do
    local TAG, P = f.tag, f.path
    wipe(FILE)
    -- RM1: one click arms it and writes the line
    local n1 = battle(TAG, P, "RM1. a click arms Hammer of Sigmar on a Warrior Priest", 19301, PRIEST, 1)
    local t1 = slurp(FILE) or ""
    local a1 = (n1 == 1) and (RED193 and t1 == "" or t1 == PRIEST .. " hammer_of_sigmar A\n")
    check(TAG .. "RM1a: armed by the click (" .. tostring(n1) .. " cast), the file reads '" .. t1:gsub("\n", "|") .. "'"
      .. (RED193 and " (RED: nothing written)" or ""), a1)
    done(a1)
    -- RM2: the next battle, another Warrior Priest, no click
    local n2 = battle(TAG, P, "RM2. the next battle: another Warrior Priest, no click, in melee", 19311, PRIEST, 0)
    local w2 = RED193 and 0 or 1
    check(TAG .. "RM2a: " .. w2 .. " cast expected (the remembered A), got " .. tostring(n2) .. (RED193 and " (RED: forgotten)" or ""), n2 == w2)
    done(n2 == w2)
    -- RM5: another unit type in the next battle
    local n5 = battle(TAG, P, "RM5. the next battle: an Arch Lector (another type), no click", 19321, OTHER, 0)
    check(TAG .. "RM5a: no cast (the line is for Warrior Priests only), got " .. tostring(n5), n5 == 0)
    done(n5 == 0)
    -- RM3: a Warrior Priest clicked back to the default (off) removes the line. Its first click turns the remembered A
    -- off (the state it shows), so one click = back to the default.
    local n3 = battle(TAG, P, "RM3. a click back to the default removes the line", 19331, PRIEST, 1)
    local t3 = slurp(FILE) or ""
    local a3 = (n3 == 0) and (t3 == "")
    check(TAG .. "RM3a: no cast after the click off (" .. tostring(n3) .. "), the file is empty ('" .. t3:gsub("\n", "|") .. "')"
      .. (RED193 and " (RED: the click arms it instead)" or ""), RED193 and (n3 == 1 and t3 == "") or a3)
    done(RED193 and (n3 == 1 and t3 == "") or a3)
    -- RM4: the reset: arm again, then empty the file (the MCT script's job), then the next battle
    battle(TAG, P, "RM4 (setup). arm it again", 19341, PRIEST, 1)
    wipe(FILE)
    local n4 = battle(TAG, P, "RM4. after the reset: the next battle, no click", 19351, PRIEST, 0)
    check(TAG .. "RM4a: no cast after the reset, got " .. tostring(n4), n4 == 0)
    done(n4 == 0)
  end
  os.remove(FILE)
  if not RED193 then
    -- RM6: the in-battle reset hook (the MCT page calls it): two types remembered, the reset, then a click on one of
    -- them: the file stays empty (the hook forgot the other type in memory, so nothing is written back)
    for _, f in ipairs(FILES) do
      local TAG, P = f.tag, f.path
      wipe(FILE)
      local units = { { name = PRIEST, uid = 19401, owns = { HOS }, melee = false },
                      { name = OTHER, uid = 19402, owns = { HOS }, melee = false } }
      local W = make_world({ can_perform = true, units = units,
        cards = { { id = "19401", state = "active", vis = true }, { id = "19402", state = "active", vis = true } },
        bar = { { id = "b1", key = HOS } } })
      W.defaults_on = false
      W.remember_on = true
      W.remember_file = FILE
      print("== " .. TAG .. "RM6. the in-battle reset hook ==")
      local ok = pcall(load_world, W, P)
      check(TAG .. "RM6: the file loads", ok)
      if ok then
        deploy_phases(W); ui(W)
        sel_event(W, 19401, true); ui(W); ui(W); click(W, "zz_auto_badge_hos"); ui(W); sel_event(W, 19401, false); ui(W)
        sel_event(W, 19402, true); ui(W); ui(W); click(W, "zz_auto_badge_hos"); ui(W)
        local before = slurp(FILE) or ""
        local hook = (type(smart_ability_autocast_reset_remembered) == "function")
        if hook then smart_ability_autocast_reset_remembered() end
        local mid = slurp(FILE) or ""
        click(W, "zz_auto_badge_hos"); ui(W)
        local after = slurp(FILE) or ""
        local a = hook and before == OTHER .. " hammer_of_sigmar A\n" .. PRIEST .. " hammer_of_sigmar A\n" and mid == "" and after == ""
        check(TAG .. "RM6a: two lines, the hook empties the file, a later click writes nothing back ('"
          .. before:gsub("\n", "|") .. "' -> '" .. mid:gsub("\n", "|") .. "' -> '" .. after:gsub("\n", "|") .. "')", a)
        done(a)
        tally(W)
      else
        done(false)
      end
    end
    os.remove(FILE)
    -- MC1-MC3: the optional MCT page (script/mct/settings/smart_ability_autocast.lua) under mock MCTs
    local MCT = "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/mct/settings/smart_ability_autocast.lua"
    local SFILE = "smart_ability_autocast_settings.txt"
    local saved_get_mct, saved_core, saved_hook = get_mct, core, smart_ability_autocast_reset_remembered
    local function run_page()
      local chunk = loadfile(MCT)
      if chunk == nil then return false end
      return pcall(chunk)
    end
    -- MC1: no MCT installed
    get_mct = nil
    local ok1 = run_page()
    check("MC1: without MCT the page returns quietly (no error)", ok1)
    done(ok1)
    -- a mock MCT: register_mod returns a mod that records its options
    local function mock_mct(with_action)
      local rec = { options = {}, listeners = {} }
      local mod = { key = "smart_ability_autocast" }
      function mod:set_title(t) rec.title = t end
      function mod:set_description(t) rec.desc = t end
      local function new_opt(key, kind)
        local o = { key = key, kind = kind }
        function o:set_text(t) o.text = t end
        function o:set_tooltip_text(t) o.tip = t end
        function o:set_button_text(t) o.button = t end
        function o:set_default_value(v) o.default = v end
        function o:set_is_global(v) o.global = v end
        function o:set_finalized_setting(v) o.finalized = v end
        function o:get_key() return key end
        rec.options[#rec.options + 1] = o
        return o
      end
      if with_action then
        function mod:add_new_action(key, text, cb) local o = new_opt(key, "action"); o.text = text; o.cb = cb; return o end
      end
      function mod:add_new_option(key, kind) return new_opt(key, kind) end
      function mod:get_key() return "smart_ability_autocast" end
      local m = {}
      function m:register_mod(key) rec.registered = key; return mod end
      rec.mod = mod
      return m, rec
    end
    local function fill() local fh = io.open(SFILE, "w"); fh:write("x y A\n"); fh:close() end
    -- MC2: MCT with the button type
    local m2, r2 = mock_mct(true)
    get_mct = function() return m2 end
    local hook_calls = 0
    smart_ability_autocast_reset_remembered = function() hook_calls = hook_calls + 1 end
    local ok2 = run_page()
    local o2 = r2.options[1]
    fill()
    if o2 ~= nil and o2.cb ~= nil then o2.cb() end
    local t2 = slurp(SFILE)
    local a2 = ok2 and r2.registered == "smart_ability_autocast" and #r2.options == 1 and o2.kind == "action"
      and o2.button == "Reset" and t2 == "" and hook_calls == 1
    check("MC2: with MCT's button type: one action 'Reset' that empties the file and calls the battle hook ("
      .. tostring(o2 and o2.kind) .. ", file '" .. tostring(t2) .. "', hook " .. hook_calls .. ")", a2)
    done(a2)
    -- MC3: an MCT without the button type: the checkbox and its finalize listener
    local m3, r3 = mock_mct(false)
    get_mct = function() return m3 end
    local lis = nil
    core = { add_listener = function(self, name, ev, cond, cb, persist) lis = { ev = ev, cond = cond, cb = cb } end }
    local ok3 = run_page()
    local o3 = r3.options[1]
    fill()
    local ctx = { mod = function() return r3.mod end, option = function() return o3 end, setting = function() return true end }
    local fired = lis ~= nil and lis.ev == "MctOptionSettingFinalized" and lis.cond(ctx)
    if fired then lis.cb(ctx) end
    local t3 = slurp(SFILE)
    local a3 = ok3 and o3 ~= nil and o3.kind == "checkbox" and o3.default == false and o3.global == true and fired
      and t3 == "" and o3.finalized == false
    check("MC3: without the button type: a checkbox, the finalize listener empties the file and unticks it ("
      .. tostring(o3 and o3.kind) .. ", file '" .. tostring(t3) .. "', unticked " .. tostring(o3 and o3.finalized) .. ")", a3)
    done(a3)
    get_mct, core, smart_ability_autocast_reset_remembered = saved_get_mct, saved_core, saved_hook
    os.remove(SFILE)
  end
  check("HARNESS 193: every world behaved - " .. n_ok .. "/" .. n_all, n_ok == n_all)
  print("== HARNESS 193 done: " .. (checks - pre193) .. " checks in this section ==")
end
