
-- ============================================================================
-- HARNESS 93 (this round): THE PER-ABILITY TOOLTIP LINE.
--   The mod appended ONE generic sentence to every implemented ability's
--   tooltip: "Automatic: this ability fires by itself while the unit charges
--   - click the M/A badge ...". That described a CHARGE behaviour most
--   abilities do not have, so it was wrong for the bulk-added entries (which
--   ride a handful of evaluators). THE FIX: the appended line is now ONE
--   SHORT clause describing the TRIGGER the entry actually rides, COMPOSED at
--   load from the entry's own trigger field (FOURTH.TRIGGER_TIP[trigger] ->
--   ability.tip). The old generic sentence is REMOVED from the twui.xml.
--
--   This harness proves, against the LIVE source and the ANNOTATED copy:
--     0q: the FOURTH.TRIGGER_TIP wording map exists; the wiring assigns
--         ability.tip from the entry's trigger; the old generic sentence is
--         gone from the source.
--     D1: the WHOLE ABILITIES table (captured through the ipairs hook) carries
--         a NON-EMPTY tooltip line on EVERY implemented entry.
--     D2: every entry's line EQUALS the allowed wording for its actual trigger
--         (data-driven over all entries - not a sample).
--     D3: no entry is left unmatched, and every trigger used in the table has
--         a wording entry.
--     D4: the shipped twui.xml carries the new short line and NOT the old
--         generic sentence.
--
--   RED CONTROL: with H93_LIVE / H93_ANN / H93_TWUI pointing at the pre-edit
--   snapshot (the shipped harness-92 build: 579 entries, NO TRIGGER_TIP, the
--   old twui.xml sentence) the 0q map+wiring tokens, the D1/D2 per-entry
--   lines and the D4 twui old-sentence check fail; the table-size and
--   trigger-wording-coverage checks still pass (the snapshot has the same
--   table and the same triggers).
-- ============================================================================
function run_h93()
  -- the allowed wording table - MUST match FOURTH.TRIGGER_TIP in the source.
  local TIP = {
    charge = "When armed, fires when this unit charges or is in melee",
    tired = "When armed, fires when this unit is tired or worse",
    melee = "When armed, fires when this unit is in melee",
    melee_low_morale = "When armed, fires when this unit is in melee and wavering",
    melee_unwavering = "When armed, fires when this unit is in melee",
    barrier_broken = "When armed, fires when this unit's barrier breaks",
    charge_or_melee = "When armed, fires when this unit charges or is in melee",
    ushoran_health = "When armed, fires when this unit is at or below 75% health",
    glorious_death = "When armed, fires when a Slayer ally in range is in melee",
    verminking_wavering = "When armed, fires when an ally in range is wavering",
    melee_health75 = "When armed, fires when this unit is in melee and at or below 75% health",
    metallurgy_melee = "When armed, fires when this unit or an ally in range is in melee",
    charge_only = "When armed, fires when this unit charges",
    wavering_self = "When armed, fires when this unit is wavering",
    wavering_self_or_ally = "When armed, fires when this unit or an ally in range is wavering",
    charge_or_wavering = "When armed, fires when this unit charges or is wavering",
    wavering_ally_range = "When armed, fires when an ally in range is wavering",
    blood_sacrifice = "When armed, fires on the lowest-health ally in range when it is at or below 75% health",
    eat_da_runts = "When armed, fires when this unit is at or below 75% health, otherwise on the lowest-health ally in range",
  }
  local OLD_LINE = "this ability fires by itself while the unit charges"
  local NEW_LINE = "Automatic: click the M/A badge to switch automatic use on or off"
  local TWUI_PATH = os.getenv("H93_TWUI")
    or "C:/Users/vlady/Desktop/WH3_mod/mod_source/ui/common ui/special_ability_tooltip.twui.xml"
  local n_words = 0
  for _ in pairs(TIP) do n_words = n_words + 1 end

  local live_src93 = read_file(LIVE)
  local ann_src93  = read_file(ANN)
  local twui_src   = read_file(TWUI_PATH)

  -- --------------------------------------------------- 0q: source tokens (both)
  print("== HARNESS 93 - section 0q: the per-ability tooltip line in the source (BOTH files) ==")
  for _, f in ipairs({ { name = "live", src = live_src93 }, { name = "ann", src = ann_src93 } }) do
    local nm, s = f.name, f.src
    check("0q " .. nm .. ": the FOURTH.TRIGGER_TIP wording map exists",
      raw_find(s, "FOURTH.TRIGGER_TIP = {", 1, true) ~= nil)
    check("0q " .. nm .. ": the wiring sets ability.tip from the entry's trigger",
      raw_find(s, "ability.tip = FOURTH.TRIGGER_TIP[ability.trigger]", 1, true) ~= nil)
    check("0q " .. nm .. ": the old generic tooltip sentence is GONE from the source",
      raw_find(s, OLD_LINE, 1, true) == nil)
    -- every required wording is present verbatim
    local miss = 0
    for _, want in pairs(TIP) do
      if raw_find(s, want, 1, true) == nil then miss = miss + 1 end
    end
    check("0q " .. nm .. ": all " .. tostring(n_words) .. " required wording strings are present verbatim", miss == 0)
  end

  -- --------------------------------------------------- D1-D3: the whole table
  print("== HARNESS 93 - the per-ability tooltip line: EVERY implemented entry ==")
  if OH77.cap == nil then
    local Wfallback = make_world({ can_perform = true, units = {} })
    pcall(load_world, Wfallback, LIVE)
  end
  local total, nonempty, matched = 0, 0, 0
  local unmatched = {}
  local used = {}
  if OH77.cap ~= nil then
    for _, e in ipairs(OH77.cap) do
      total = total + 1
      if e.trigger ~= nil then used[e.trigger] = true end
      local want = TIP[e.trigger]
      if type(e.tip) == "string" and e.tip ~= "" then nonempty = nonempty + 1 end
      if want ~= nil and e.tip == want then
        matched = matched + 1
      else
        unmatched[#unmatched + 1] = tostring(e.marker) .. "(" .. tostring(e.trigger) .. ")"
      end
    end
  end
  check("D1a: the WHOLE ABILITIES table was captured (" .. total .. " entries, want 579)",
    total == 579)
  check("D1b: EVERY implemented entry carries a NON-EMPTY tooltip line (" .. nonempty .. "/" .. total .. ")",
    nonempty == total and total == 579)
  check("D2: EVERY implemented entry's line equals the allowed wording for its actual trigger ("
    .. matched .. "/" .. total .. ")", matched == total and total == 579)
  local unmatched_msg = ""
  if #unmatched > 0 then
    local shown = {}
    for i = 1, math.min(#unmatched, 6) do shown[i] = unmatched[i] end
    unmatched_msg = " (first " .. #shown .. " of " .. #unmatched .. ": " .. table.concat(shown, ", ")
      .. (#unmatched > #shown and ", ..." or "") .. ")"
  end
  check("D3a: no entry left unmatched (" .. #unmatched .. ")" .. unmatched_msg, #unmatched == 0)
  local missing_trig = 0
  for tr in pairs(used) do
    if TIP[tr] == nil then missing_trig = missing_trig + 1 end
  end
  check("D3b: every trigger used in the table has an allowed wording (missing = " .. missing_trig .. ")",
    missing_trig == 0)

  -- --------------------------------------------------- D4: the shipped twui.xml
  check("D4a: the twui.xml carries the NEW short line", raw_find(twui_src, NEW_LINE, 1, true) ~= nil)
  check("D4b: the OLD generic sentence is GONE from the twui.xml", raw_find(twui_src, OLD_LINE, 1, true) == nil)

  if not RED_MODE then
    check("HEADLINE (harness 93): the appended tooltip line is now ONE SHORT clause per ability, COMPOSED from the "
      .. "trigger the entry actually rides (FOURTH.TRIGGER_TIP[trigger] -> ability.tip) - all " .. total
      .. " entries match their evaluator; the old one-size 'fires by itself while the unit charges' sentence is "
      .. "removed from the shipped twui.xml, which now carries only the short badge hint.", matched == total and total == 579)
  else
    check("RED CONTROL (harness 93): on the pre-edit snapshot (the shipped harness-92 build, 579 entries, NO "
      .. "TRIGGER_TIP, the old twui.xml sentence) the 0q map/wiring tokens, the D1 non-empty line, the D2 per-entry "
      .. "match and the D4b twui old-sentence check fail; the table-size and trigger-coverage checks still pass: "
      .. matched .. "/" .. total .. " entries match (want 0), total " .. total .. " (want 579)",
      matched == 0 and total == 579)
  end
end
run_h93()
