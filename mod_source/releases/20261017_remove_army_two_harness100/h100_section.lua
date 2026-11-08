-- ============================================================================
-- HARNESS 100 - REMOVAL OF THE TWO OUT-OF-RULE ARMY ABILITIES (2026-10-17)
--   Meat Feast `wh3_main_prisoners_butcher` and Massacre
--   `wh3_main_prisoners_massacre` were IMPLEMENTED but sit OUTSIDE the single
--   in-wheel rule (both are source_type = army). Per the user's decision of
--   2026-10-17 they are REMOVED from the mod. The removal must touch nothing
--   else: Grut's Sickle is a DIFFERENT ability (an in-wheel item ability with
--   the max-HP ally pick rule) and must stay.
--
--   This section proves, in BOTH files (live source and annotated copy):
--     0x: the two keys are ABSENT from the ABILITIES table (and from the whole
--         file); their markers and badge ids are GONE; the table is exactly
--         577 entries / 603 keys (579 - 2 / 605 - 2);
--     the neighbours survive; the `ushoran_health` trigger keeps its OTHER
--         member (Gulyas) and is 33 (34 - 1); `melee_unwavering` is 362
--         (363 - 1); and Grut's Sickle still ships with its key, marker,
--         badge, evaluator and the `winds` (max HealthValue) pick rule.
--
--   RED CONTROL: with H100_LIVE / H100_ANN pointing at the pre-edit snapshot
--         the same predicates flip - both keys and markers ARE present and the
--         counts are 579 / 605 - and the RED summary check asserts exactly
--         that, proving the snapshot is genuinely pre-edit (every green
--         removal check would fail on it).
-- ============================================================================
function run_h100()
  local live_src100 = read_file(LIVE)
  local ann_src100  = read_file(ANN)
  local EXP
  if RED_MODE then
    EXP = { entries = 579, keys = 605, mu = 363, ush = 34, present = true }
  else
    EXP = { entries = 577, keys = 603, mu = 362, ush = 33, present = false }
  end
  local function cp100(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  -- the ABILITIES table span, from its opening brace to the matching close
  local function table_span100(s)
    local i = raw_find(s, "local ABILITIES = {", 1, true)
    if i == nil then return nil end
    local j = raw_find(s, "{", i, true)
    if j == nil then return nil end
    local depth = 0
    for k = j, #s do
      local c = s:sub(k, k)
      if c == "{" then
        depth = depth + 1
      elseif c == "}" then
        depth = depth - 1
        if depth == 0 then return s:sub(j, k) end
      end
    end
    return nil
  end
  -- count the quoted strings across every `keys = { ... }` list in the table
  local function key_count100(t)
    local n, at = 0, 1
    while true do
      local i = raw_find(t, "keys = {", at, true)
      if i == nil then return n end
      local j = raw_find(t, "}", i, true)
      if j == nil then return n end
      local seg = t:sub(i, j)
      for _ in seg:gmatch('"[^"]*"') do n = n + 1 end
      at = j + 1
    end
  end

  print("== HARNESS 100 - section 0x: Meat Feast and Massacre are REMOVED (BOTH files) ==")
  local ok_all = true
  local FILES100 = { { name = "live", src = live_src100 }, { name = "ann", src = ann_src100 } }
  for fi = 1, #FILES100 do
    local nm, s = FILES100[fi].name, FILES100[fi].src
    local span = table_span100(s)
    check("0x " .. nm .. ": the ABILITIES table parses", span ~= nil)
    if span ~= nil then
      local n_e = cp100(span, "\n\t{ marker = ")
      local n_k = key_count100(span)
      local n_lists = cp100(span, "keys = {")
      -- the two keys / markers / badges
      local has_b = (raw_find(span, "wh3_main_prisoners_butcher", 1, true) ~= nil)
      local has_m = (raw_find(span, "wh3_main_prisoners_massacre", 1, true) ~= nil)
      local has_mk_b = (raw_find(span, 'marker = "butcher"', 1, true) ~= nil)
      local has_mk_m = (raw_find(span, 'marker = "massacre"', 1, true) ~= nil)
      local has_bd_b = (raw_find(s, "zz_auto_badge_butcher", 1, true) ~= nil)
      local has_bd_m = (raw_find(s, "zz_auto_badge_massacre", 1, true) ~= nil)
      if EXP.present then
        ok_all = has_b and has_m and has_mk_b and has_mk_m and has_bd_b and has_bd_m and (n_e == EXP.entries)
          and (n_k == EXP.keys) and ok_all
      else
        ok_all = (not has_b) and (not has_m) and (not has_mk_b) and (not has_mk_m)
          and (not has_bd_b) and (not has_bd_m) and (n_e == EXP.entries) and (n_k == EXP.keys) and ok_all
      end
      if EXP.present then
        check("0x " .. nm .. ": the PRE-EDIT snapshot still carries BOTH army keys (" .. n_e .. " entries)",
          has_b and has_m)
      else
        check("0x " .. nm .. ": the two army keys are ABSENT from the ABILITIES table", (not has_b) and (not has_m))
      end
      check("0x " .. nm .. ": the entry count is exactly " .. EXP.entries .. " (got " .. n_e .. ")", n_e == EXP.entries)
      check("0x " .. nm .. ": the key count is exactly " .. EXP.keys .. " (got " .. n_k .. ")", n_k == EXP.keys)
      check("0x " .. nm .. ": every entry carries exactly one keys list (" .. n_lists .. " lists)",
        n_lists == EXP.entries)
      if EXP.present then
        check("0x " .. nm .. ": the PRE-EDIT markers and badge ids are still present",
          has_mk_b and has_mk_m and has_bd_b and has_bd_m)
      else
        check("0x " .. nm .. ": the markers and badge ids are GONE",
          (not has_mk_b) and (not has_mk_m) and (not has_bd_b) and (not has_bd_m))
      end
      check("0x " .. nm .. ": the two removed keys are absent from the WHOLE file",
        (EXP.present and (raw_find(s, "wh3_main_prisoners_butcher", 1, true) ~= nil)
          and (raw_find(s, "wh3_main_prisoners_massacre", 1, true) ~= nil))
        or ((not EXP.present) and raw_find(s, "wh3_main_prisoners_butcher", 1, true) == nil
          and raw_find(s, "wh3_main_prisoners_massacre", 1, true) == nil))
      -- the neighbours and the shared triggers: nothing else moved
      check("0x " .. nm .. ": the neighbours around both removals survive (breath_of_hatred, "
        .. "captain_of_the_phoenix_guard, lord_of_grand_cathay, master_of_alchemy)",
        raw_find(span, 'marker = "breath_of_hatred"', 1, true) ~= nil
        and raw_find(span, 'marker = "captain_of_the_phoenix_guard"', 1, true) ~= nil
        and raw_find(span, 'marker = "lord_of_grand_cathay"', 1, true) ~= nil
        and raw_find(span, 'marker = "master_of_alchemy"', 1, true) ~= nil)
      check("0x " .. nm .. ": ushoran_health keeps its other member - Gulyas - and is exactly "
        .. EXP.ush .. " (got " .. cp100(s, 'trigger = "ushoran_health"') .. ")",
        cp100(s, 'trigger = "ushoran_health"') == EXP.ush
        and raw_find(span, 'marker = "gulyas"', 1, true) ~= nil)
      check("0x " .. nm .. ": melee_unwavering is exactly " .. EXP.mu
        .. " (got " .. cp100(s, 'trigger = "melee_unwavering"') .. ")",
        cp100(s, 'trigger = "melee_unwavering"') == EXP.mu)
      -- Grut's Sickle is a DIFFERENT ability and must be untouched
      check("0x " .. nm .. ": Grut's Sickle is UNTOUCHED (marker, key, badge, evaluator and winds family)",
        raw_find(span, 'marker = "gruts_sickle"', 1, true) ~= nil
        and raw_find(span, 'wh3_main_item_abilities_gruts_sickle', 1, true) ~= nil
        and raw_find(s, 'badge = "zz_auto_badge_gruts_sickle"', 1, true) ~= nil
        and raw_find(s, "function FOURTH.evaluate_ally_winds(unit, routing)", 1, true) ~= nil
        and raw_find(s, "ally_winds = FOURTH.evaluate_ally_winds,", 1, true) ~= nil
        and raw_find(s, 'family == "winds"', 1, true) ~= nil
        and raw_find(s, 'FOURTH.context_value(other, "HealthValue")', 1, true) ~= nil)
    end
  end

  if RED_MODE then
    check("RED CONTROL (harness 100): the pre-edit snapshot carries BOTH keys, their markers and badges, and "
      .. "579 entries / 605 keys - every green removal check above would FAIL on it", ok_all)
  else
    check("HEADLINE (harness 100): Meat Feast (wh3_main_prisoners_butcher) and Massacre "
      .. "(wh3_main_prisoners_massacre) are REMOVED from the ABILITIES table - 577 entries / 603 keys "
      .. "(579 - 2 / 605 - 2); Grut's Sickle and every other ability are untouched. All 0x checks passed.", ok_all)
  end
end
run_h100()
