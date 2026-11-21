-- ============================================================================
-- HARNESS 194 (round 195, user 2026-11-21 with a screenshot of the MCT page: "the '?' is in the middle. Also, there is
--   no feedback to the player when I press it."):
--   MC4 MCT with the button type: a named section (not "Default Category"), a short one-line label, NO tooltip (so no
--       "?" marker), the button "Reset"; pressing it empties the file, calls the battle hook, the button reads "Done"
--       and greys out, the label reads "Forgotten".
--   MC5 an older MCT without the button type: the checkbox label is one line ("Reset all") and has no tooltip.
--   RED: H194_MCT on docs/backups/round195/pre195_mct.lua (a tooltip, a three-line label, no feedback).
-- ============================================================================
function run_h194()
  local MCT = os.getenv("H194_MCT") or "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/mct/settings/smart_ability_autocast.lua"
  local RED194 = os.getenv("H194_MCT") ~= nil
  local SFILE = "smart_ability_autocast_settings.txt"
  local pre194 = checks
  print("== HARNESS 194 - the MCT page: section, label, no tooltip, feedback ==")
  local function slurp(p)
    local fh = io.open(p, "r")
    if fh == nil then return nil end
    local t = fh:read("*a")
    fh:close()
    return t
  end
  local saved_get_mct, saved_core, saved_hook, saved_find = get_mct, core, smart_ability_autocast_reset_remembered, find_uicomponent
  local function mock_mct(with_action)
    local rec = { options = {}, sections = {} }
    local mod = {}
    function mod:set_title(t) rec.title = t end
    function mod:set_description(t) rec.desc = t end
    function mod:add_new_section(key, text) rec.sections[#rec.sections + 1] = { key = key, text = text } end
    function mod:get_key() return "smart_ability_autocast" end
    local function uic(name)
      local u = { name = name }
      function u:SetState(s) u.state = s end
      function u:SetStateText(t) u.text = t end
      return u
    end
    local function new_opt(key, kind)
      local o = { key = key, kind = kind, uics = { option = uic("button"), text = uic("label") } }
      o.uics.option.child = uic("button_txt")
      function o:set_text(t) o.text = t end
      function o:set_tooltip_text(t) o.tip = t end
      function o:set_button_text(t) o.button = t end
      function o:set_default_value(v) o.default = v end
      function o:set_is_global(v) o.global = v end
      function o:set_finalized_setting(v) o.finalized = v end
      function o:get_key() return key end
      function o:get_uic_with_key(k) return o.uics[k] end
      rec.options[#rec.options + 1] = o
      return o
    end
    if with_action then
      function mod:add_new_action(key, text, cb) local o = new_opt(key, "action"); o.text = text; o.cb = cb; return o end
    end
    function mod:add_new_option(key, kind) return new_opt(key, kind) end
    local m = {}
    function m:register_mod(key) rec.registered = key; return mod end
    return m, rec
  end
  local function run_page()
    local chunk = loadfile(MCT)
    if chunk == nil then return false end
    return pcall(chunk)
  end
  find_uicomponent = function(parent, name) if parent ~= nil and name == "button_txt" then return parent.child end return false end
  -- MC4
  local m4, r4 = mock_mct(true)
  get_mct = function() return m4 end
  local hook = 0
  smart_ability_autocast_reset_remembered = function() hook = hook + 1 end
  local ok4 = run_page()
  local o = r4.options[1]
  local fh = io.open(SFILE, "w"); fh:write("x y A\n"); fh:close()
  if o ~= nil and o.cb ~= nil then o.cb() end
  local t4 = slurp(SFILE)
  local sec = r4.sections[1]
  local a_layout = ok4 and o ~= nil and o.kind == "action" and o.tip == nil and o.text ~= nil and #o.text <= 15
    and sec ~= nil and sec.text == "Remembered M/A choices" and o.button == "Reset"
  local a_press = o ~= nil and t4 == "" and hook == 1 and o.uics.option.state == "inactive"
    and o.uics.option.child.text == "Done" and o.uics.text.text == "Forgotten"
  if RED194 then
    check("MC4 (RED): the round-194 page has a tooltip or a long label and gives no feedback",
      o ~= nil and (o.tip ~= nil or #(o.text or "") > 15) and o.uics.option.child.text == nil)
  else
    check("MC4a: a section 'Remembered M/A choices', a one-line label '" .. tostring(o and o.text) .. "', no tooltip, button 'Reset'", a_layout)
    check("MC4b: pressing Reset empties the file, calls the battle hook, the button reads 'Done' (" .. tostring(o and o.uics.option.child.text)
      .. ", " .. tostring(o and o.uics.option.state) .. ") and the label 'Forgotten'", a_press)
  end
  -- MC5
  local m5, r5 = mock_mct(false)
  get_mct = function() return m5 end
  core = { add_listener = function() end }
  local ok5 = run_page()
  local o5 = r5.options[1]
  if not RED194 then
    check("MC5: an older MCT: the checkbox label is one line ('" .. tostring(o5 and o5.text) .. "'), no tooltip",
      ok5 and o5 ~= nil and o5.kind == "checkbox" and o5.tip == nil and #(o5.text or "") <= 15)
  end
  get_mct, core, smart_ability_autocast_reset_remembered, find_uicomponent = saved_get_mct, saved_core, saved_hook, saved_find
  os.remove(SFILE)
  print("== HARNESS 194 done: " .. (checks - pre194) .. " checks in this section ==")
end
