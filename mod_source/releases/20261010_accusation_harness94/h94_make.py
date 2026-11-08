# -*- coding: utf-8 -*-
"""HARNESS 94 build: assemble harness94.lua from the SHIPPED harness93.lua.

The round-94 job: ACCUSATION'S AUTOMATIC ACTIVATION - a new reusable evaluator
`enemy_engaged_or_shot` (enemy in range in melee OR under missile fire; the
chosen enemy is the cast target, never the owner; cast via the round-4-proven
bench_fresh fresh-handle route). Accusation's entry moves melee_unwavering ->
enemy_engaged_or_shot (481 -> 480; table stays 579 entries / 605 keys).

Steps:
  1. add the ENEMY mock to make_world (a separate enemy collection, the enemy
     reads is_under_missile_attack / is_valid_target / is_valid / unit_in_range,
     melee_seq + missile_seq, dist_by_target/in_range control, and the friendly
     enumerator call counter);
  2. update the moved trigger-count pin (melee_unwavering 481 -> 480);
  3. add the new trigger's wording to the harness-93 section's allowed TIP map
     and RE-BASE that section's red branch to the N/A form (the harness-94 red
     snapshot already carries FOURTH.TRIGGER_TIP and the wiring);
  4. refresh the section labels (harness-93 -> harness-94);
  5. append the new HARNESS-94 section after run_h93().
The pre94_*.lua snapshots (written by impl94.py) are the RED CONTROL target.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "C:/Users/vlady/Desktop/WH3_mod/mod_source"

NL = chr(10)


def L(*lines):
    return NL.join(lines)


def read(p):
    return io.open(p, encoding="utf-8", newline="").read()


def write(p, s):
    io.open(p, "w", encoding="utf-8", newline="").write(s)


src = read(os.path.join(HERE, "harness93.lua"))


def sub(old, new, label, count=1):
    global src
    n = src.count(old)
    assert n == count, "patch %s: %d matches (want %d)" % (label, n, count)
    src = src.replace(old, new, count)
    print("patch %s: applied" % label)


def repl(old, new, label, count=None):
    global src
    n = src.count(old)
    if count is not None:
        assert n == count, "repl %s: %d matches (want %d)" % (label, n, count)
    src = src.replace(old, new)
    print("repl %s: %d occurrences" % (label, n))


# --------------------------------------------------------------------------
# 0. env pair H93 -> H94
# --------------------------------------------------------------------------
sub(L('-- HARNESS 93 (this round): the env pair is now H93_LIVE / H93_ANN (the',
      '-- tooltip path rides H93_TWUI, read inside the section).',
      'local LIVE = os.getenv("H93_LIVE") or "%s/script/battle/mod/zz_test_deadly_onslaught.lua"' % ROOT,
      'local ANN  = os.getenv("H93_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H93_LIVE") ~= nil) or (os.getenv("H93_ANN") ~= nil)'),
    L('-- HARNESS 94 (this round): the env pair is now H94_LIVE / H94_ANN.',
      'local LIVE = os.getenv("H94_LIVE") or "%s/script/battle/mod/zz_test_deadly_onslaught.lua"' % ROOT,
      'local ANN  = os.getenv("H94_ANN")  or "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"',
      'local RED_MODE = (os.getenv("H94_LIVE") ~= nil) or (os.getenv("H94_ANN") ~= nil)'),
    "P1 env")

# --------------------------------------------------------------------------
# 1. the banner
# --------------------------------------------------------------------------
sub(L('  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - THE PER-ABILITY TOOLTIP LINE (harness-93)")',
      '  print("   *** checks EXPECTED to fail: the section-0q map/wiring tokens, the D1 non-empty line, the D2 per-entry")',
      '  print("   *** match over the whole table and the D4b twui old-sentence check. The table size (579) and the")',
      '  print("   *** trigger-wording coverage pass on the snapshot by design (same table, same triggers).")',
      '  print("   *** Every earlier world passes by design.***")'),
    L('  print("   *** RED CONTROL MODE: pre-edit snapshot(s) in use - ACCUSATION ENEMY TRIGGER (harness-94)")',
      '  print("   *** checks EXPECTED to fail: the section-0r tokens (no enemy evaluator, Accusation still on")',
      '  print("   *** melee_unwavering) and the moved trigger-count pin (melee_unwavering is 481 on the snapshot,")',
      '  print("   *** 480 here). Only the SILENT N-worlds pass by design. Every earlier world passes except the")',
      '  print("   *** documented melee_unwavering pin.***")'),
    "P1b banner")

# --------------------------------------------------------------------------
# 2. the ENEMY MOCK (make_world)
# --------------------------------------------------------------------------
# 2a. new W counters
sub(L('    type_first = {},'),
    L('    type_first = {},',
      '    -- HARNESS 94: the enemy-targeted trigger instrumentation.',
      '    missile_calls = {},',
      '    missile_raise_attempts = 0,',
      '    range_calls = {},',
      '    friendly_calls = 0,'),
    "M1 W fields")

# 2b. zz_uid on every unit (so a distance/range map can key by target)
sub(L('  local function create_pair(def)',
      '    local u = {}',
      '    W.ctx_by_id[def.uid] = def   -- BLOCK 2: answer CcoBattleUnit reads for this id'),
    L('  local function create_pair(def)',
      '    local u = {}',
      '    u.zz_uid = def.uid           -- HARNESS 94: a plain field for per-target maps',
      '    W.ctx_by_id[def.uid] = def   -- BLOCK 2: answer CcoBattleUnit reads for this id'),
    "M2 zz_uid")

# 2c. is_in_melee (seq) + the enemy reads
sub(L('    function u:is_moving_fast() touch(); return def.fast == true end',
      '    function u:is_in_melee() touch(); return def.melee == true end'),
    L('    function u:is_moving_fast() touch(); return def.fast == true end',
      '    function u:is_in_melee()',
      '      touch()',
      '      if def.melee_seq ~= nil then',
      '        def.melee_i = (def.melee_i or 0) + 1',
      '        local v = def.melee_seq[def.melee_i]',
      '        if v == nil then v = def.melee_seq[#def.melee_seq] end',
      '        return v == true',
      '      end',
      '      return def.melee == true',
      '    end',
      '    -- HARNESS 94: the enemy-targeted trigger reads.',
      '    function u:is_under_missile_attack()',
      '      touch()',
      '      W.missile_calls[def.uid] = (W.missile_calls[def.uid] or 0) + 1',
      '      if def.missile_raises then',
      '        W.missile_raise_attempts = W.missile_raise_attempts + 1',
      '        error("mock: is_under_missile_attack refused", 0)',
      '      end',
      '      if def.missile_seq ~= nil then',
      '        def.missile_i = (def.missile_i or 0) + 1',
      '        local v = def.missile_seq[def.missile_i]',
      '        if v == nil then v = def.missile_seq[#def.missile_seq] end',
      '        return v == true',
      '      end',
      '      return def.missile == true',
      '    end',
      '    function u:is_valid_target() touch(); return def.invalid ~= true end',
      '    function u:is_valid() touch(); return def.invalid ~= true end',
      '    function u:unit_in_range(o)',
      '      touch()',
      '      W.range_calls[def.uid] = (W.range_calls[def.uid] or 0) + 1',
      '      if def.range_raises then error("mock: unit_in_range refused", 0) end',
      '      if def.in_range_by_target ~= nil then',
      '        local k = (type(o) == "table" and o.zz_uid) or nil',
      '        if k ~= nil and def.in_range_by_target[k] ~= nil then return def.in_range_by_target[k] end',
      '      end',
      '      if def.in_range ~= nil then return def.in_range == true end',
      '      return nil',
      '    end'),
    "M3 enemy reads")

# 2d. unit_distance: per-target distances
sub(L('      if def.dist ~= nil then return def.dist end',
      '      return -1'),
    L('      if def.dist_by_target ~= nil then',
      '        local k = (type(o) == "table" and o.zz_uid) or nil',
      '        if k ~= nil and def.dist_by_target[k] ~= nil then return def.dist_by_target[k] end',
      '      end',
      '      if def.dist ~= nil then return def.dist end',
      '      return -1'),
    "M4 dist_by_target")

# 2e. the friendly enumerator counter + the enemy enumerator method
sub(L('  function bm:get_scriptunits_for_local_players_army()',
      '    -- HARNESS 77: model the engine answering NOTHING on one tick (the',
      '    -- early-battle shape) so the 40-poll re-list\'s own recompute cannot',
      '    -- join the 60 s fallback tick the item-12 world measures.',
      '    if W.army_nil_at ~= nil and W.poll_ticks == W.army_nil_at then return nil end',
      '    return collection',
      '  end'),
    L('  function bm:get_scriptunits_for_local_players_army()',
      '    -- HARNESS 94: count every friend-list fetch so a world can prove the',
      '    -- fresh-caster re-fetch happens on the firing tick.',
      '    W.friendly_calls = (W.friendly_calls or 0) + 1',
      '    -- HARNESS 77: model the engine answering NOTHING on one tick (the',
      '    -- early-battle shape) so the 40-poll re-list\'s own recompute cannot',
      '    -- join the 60 s fallback tick the item-12 world measures.',
      '    if W.army_nil_at ~= nil and W.poll_ticks == W.army_nil_at then return nil end',
      '    return collection',
      '  end',
      '  -- HARNESS 94: the ENEMY army list the enemy-targeted trigger enumerates.',
      '  function bm:get_scriptunits_for_main_enemy_army_to_local_player()',
      '    if W.enemy_nil_at ~= nil and W.poll_ticks == W.enemy_nil_at then return nil end',
      '    if W.enemy_raise then error("mock: enemy army refused", 0) end',
      '    return enemy_collection',
      '  end'),
    "M5 bm enemy method")

# 2f. build the enemy collection (reuses create_pair; NOT in the friendly list)
sub(L('  W.unit_defs = unit_defs',
      '  W.mock_units = units',
      '  W.mock_ucs = ucs'),
    L('  W.unit_defs = unit_defs',
      '  W.mock_units = units',
      '  W.mock_ucs = ucs',
      '',
      '  -- HARNESS 94: the ENEMY army list (a separate collection the mod reads via',
      '  -- get_scriptunits_for_main_enemy_army_to_local_player()). Enemies are built',
      '  -- by the same factory and are NOT in the friendly list.',
      '  local enemy_defs = opts.enemies or {}',
      '  W.enemy_entries = {}',
      '  for i = 1, #enemy_defs do',
      '    local pair = create_pair(enemy_defs[i])',
      '    W.enemy_entries[i] = pair',
      '  end',
      '  W.enemy_defs = enemy_defs',
      '  local enemy_collection = {}',
      '  function enemy_collection:count() return #W.enemy_entries end',
      '  function enemy_collection:item(i) return W.enemy_entries[i] end',
      '  W.enemy_collection = enemy_collection'),
    "M6 enemy collection")

# --------------------------------------------------------------------------
# 3. the moved trigger-count pin (melee_unwavering 481 -> 480)
# --------------------------------------------------------------------------
sub("cp(s, 'trigger = \"melee_unwavering\"') == 481", "cp(s, 'trigger = \"melee_unwavering\"') == 480",
    "pin cp 481->480", count=5)
sub("mu == 481", "mu == 480", "pin mu 481->480")
repl("the melee_unwavering entry count grew to 481", "the melee_unwavering entry count grew to 480", "label grew")
repl("the melee_unwavering entry count is 481", "the melee_unwavering entry count is 480", "label is")
repl("the melee_unwavering / charge_or_melee counts grew to (481 / 29)",
     "the melee_unwavering / charge_or_melee counts grew to (480 / 29)", "label 0m")
repl("the trigger counts are right (melee_unwavering 481,", "the trigger counts are right (melee_unwavering 480,", "label 0n")
repl("the trigger counts grew to (melee_unwavering 481,", "the trigger counts grew to (melee_unwavering 480,", "label 0o/0p")
repl("melee_unwavering 477 -> 481; no new chunk locals.",
     "melee_unwavering 477 -> 480 (Accusation moved to enemy_engaged_or_shot); no new chunk locals.", "label red92")

# --------------------------------------------------------------------------
# 4. the harness-93 section: add the new wording + RE-BASE its red branch
# --------------------------------------------------------------------------
sub(L('    blood_sacrifice = "When armed, fires on the lowest-health ally in range when it is at or below 75% health",',
      '    eat_da_runts = "When armed, fires when this unit is at or below 75% health, otherwise on the lowest-health ally in range",',
      '  }'),
    L('    blood_sacrifice = "When armed, fires on the lowest-health ally in range when it is at or below 75% health",',
      '    eat_da_runts = "When armed, fires when this unit is at or below 75% health, otherwise on the lowest-health ally in range",',
      '    enemy_engaged_or_shot = "When armed, fires when an enemy unit in range is in melee or under missile fire",',
      '  }'),
    "P4 h93 tip")

sub(L('  else',
      '    check("RED CONTROL (harness 93): on the pre-edit snapshot (the shipped harness-92 build, 579 entries, NO "',
      '      .. "TRIGGER_TIP, the old twui.xml sentence) the 0q map/wiring tokens, the D1 non-empty line, the D2 per-entry "',
      '      .. "match and the D4b twui old-sentence check fail; the table-size and trigger-coverage checks still pass: "',
      '      .. matched .. "/" .. total .. " entries match (want 0), total " .. total .. " (want 579)",',
      '      matched == 0 and total == 579)',
      '  end'),
    L('  else',
      '    check("RED CONTROL (harness 93): N/A for the harness-94 round - the harness-94 red snapshot (the shipped "',
      '      .. "harness-93 build) already carries FOURTH.TRIGGER_TIP and the entry wiring, so every entry matches its "',
      '      .. "trigger wording: " .. matched .. "/" .. total .. " entries match (want 579), total " .. total',
      '      .. " (want 579)",',
      '      matched == 579 and total == 579)',
      '  end'),
    "P5 h93 red rebase")

# --------------------------------------------------------------------------
# 5. refresh the section labels (harness-93 -> harness-94)
# --------------------------------------------------------------------------
repl("for the harness-93 round", "for the harness-94 round", "label round")
repl("the harness-93 red snapshot", "the harness-94 red snapshot", "label snapshot")
repl("the shipped harness-92 build", "the shipped harness-93 build", "label build")

# --------------------------------------------------------------------------
# 6. append the new section after run_h93()
# --------------------------------------------------------------------------
section = read(os.path.join(HERE, "h94_section.lua")).lstrip(NL)
sub(L('run_h93()',
      '',
      'check("ZERO search calls by the mod across everything, harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91 AND 92\'s worlds included (counted " .. find_calls .. ")",',
      '  find_calls == 0)'),
    L('run_h93()',
      '',
      section,
      '',
      'check("ZERO search calls by the mod across everything, harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92 AND 93\'s worlds included (counted " .. find_calls .. ")",',
      '  find_calls == 0)'),
    "P6 append section")

write(os.path.join(HERE, "harness94.lua"), src)
print("wrote harness94.lua", len(src), "bytes")
