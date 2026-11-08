#!/usr/bin/env python3
"""Build harness122.lua from harness121.lua for round 123 (the hex batch).

  1. prepends the round-123 banner;
  2. rebases the LIVE count pins the round deliberately moves (comment lines
     are history and stay; the RED-snapshot expectation rows are not touched):
       entries 697 -> 707, keys 748 -> 759, melee_unwavering 370 -> 374,
       charge_or_melee 25 -> 28, range_real fields 204 -> 207, charge-gate
       keys 161 -> 163, the A4 bootstrap iteration pin 1394 -> 1414;
  3. adds the new trigger's wording to harness 93's allowed-tooltip mirror
     (otherwise D2/D3 correctly report enemy_melee as a trigger with no
     allowed wording);
  4. appends run_h122 and calls it after run_h121.
Older harnesses are never edited.
"""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261027_melee_buffs_harness121\harness121.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261027_hex_batch_harness122\harness122.lua"

BANNER = """-- ============================================================================
-- HARNESS 122 - ROUND 123, THE HEX BATCH (user ruling 2026-10-27): one trigger
-- per ability, chosen from what its effect changes.
--   melee_unwavering (no speed effect): Rival Hide Talisman, Seductive Glory,
--     Vine Dragon Scale, Dark Mace
--   charge_or_melee (reduces enemy speed): Seduction, Song of Enthrallment,
--     Smoke Bomb
--   enemy_melee (NEW: an enemy in range that is IN MELEE; being shot does not
--     count): No Escape, Transfix (dlc29 hex key), Flash Bomb
--   Hunter of Champions: the upgraded key joins the existing entry
--   (enemy_engaged_or_shot). Daemonic Possession: NOT automated.
--   Table: 697 entries / 748 keys -> 707 / 759; 45 -> 46 trigger families.
--
--   Edited vs harness121: this banner, the count pins the round moves, the
--   enemy_melee line in harness 93's allowed-tooltip mirror, the new run_h122
--   section and its call. RED control: H122_LIVE / H122_ANN.
-- ============================================================================
"""

SECTION = r'''
-- ============================================================================
-- HARNESS 122 (round 123): THE HEX BATCH.
--   0s: tokens in BOTH files (entries, triggers, keys, range_real, charge
--       holds, the evaluator, its map line and tooltip, no Daemonic Possession,
--       no batch key in army_spec).
--   A (melee_unwavering x4): in melee FIRES on self; out of melee SILENT;
--       wavering SILENT.
--   C (charge_or_melee x3): in melee FIRES; CHARGING (running, targeted, 20 m)
--       FIRES with the charge reason; running with NO target (a move order,
--       "only passing by") SILENT.
--   E (enemy_melee x3): enemy in melee in range FIRES at the ENEMY; enemy only
--       UNDER MISSILE FIRE stays SILENT (the user's rule); enemy in melee just
--       beyond the 70% bound SILENT; exactly on the bound FIRES; enemy leaves
--       melee between decide and cast -> SKIPPED, not spent.
--   G: No Escape is held for its own 90 s recharge after a cast (3 uses).
--   H: the upgraded Hunter of Champions key fires on an enemy under missile
--       fire (enemy_engaged_or_shot), through the existing entry's badge.
-- ============================================================================
function run_h122()
  local L122 = os.getenv("H122_LIVE") or LIVE
  local A122 = os.getenv("H122_ANN") or ANN
  local RED122 = (os.getenv("H122_LIVE") ~= nil) or (os.getenv("H122_ANN") ~= nil)
  local MU = {
    { "rival_hide_talisman", "wh2_main_item_abilities_rival_hide_talisman" },
    { "seductive_glory", "wh3_main_lord_abilities_seductive_glory" },
    { "vine_dragon_scale", "wh2_dlc15_item_abilities_vine_dragon_scale" },
    { "dark_mace", "wh3_dlc23_weapon_abilities_dark_mace" },
  }
  local CM = {
    { "seduction", "wh2_dlc11_lord_abilities_seduction" },
    { "song_of_enthrallment", "wh2_dlc11_lord_abilities_song_of_enthrallment" },
    { "smoke_bomb", "wh_dlc06_unit_abilities_smoke_bomb" },
  }
  local EM = {
    { "no_escape", "wh3_main_character_abilities_no_escape", 70 },
    { "transfix_hex", "wh3_dlc29_lord_abilities_transfix", 70 },
    { "flash_bomb", "wh_pro01_lord_abilities_flash_bomb", 52 },
  }
  local HOC_UP = "wh2_dlc17_character_abilities_hunter_of_champions_upgraded"
  local pre122 = checks
  local function cp(s, tok)
    local n, at = 0, 1
    while true do
      local i = raw_find(s, tok, at, true)
      if i == nil then return n end
      n = n + 1
      at = i + 1
    end
  end
  local function lg(tag, v) return (tag ~= "[live] ") or v end
  local function enemy_by(W, uid)
    for i = 1, #(W.enemy_entries or {}) do
      local pr = W.enemy_entries[i]
      if pr ~= nil and pr.unit ~= nil then
        local ok, id = pcall(function() return pr.unit:unique_ui_id() end)
        if ok and tostring(id) == tostring(uid) then return pr.unit end
      end
    end
    return nil
  end

  -- ------------------------------------------------------------------ 0s
  print("== HARNESS 122 - section 0s: the hex batch tokens (BOTH files) ==")
  local army = {}
  local fh = io.open("C:/Users/vlady/AppData/Local/Temp/wh3/army_spec.tsv", "r")
  check("0s: the army_spec extract is readable", fh ~= nil)
  if fh then
    fh:read("*l")
    for ln in fh:lines() do
      local k = ln:match("^([^\t#][^\t]*)")
      if k then army[k] = true end
    end
    fh:close()
  end
  local all_keys = { HOC_UP }
  for _, t in ipairs({ MU, CM, EM }) do for _, b in ipairs(t) do all_keys[#all_keys + 1] = b[2] end end
  local hits = 0
  for _, k in ipairs(all_keys) do if army[k] then hits = hits + 1 end end
  check("0s: NO batch key is in the army_spec junction (" .. hits .. " hit(s) of " .. #all_keys .. ")", hits == 0)
  for _, f in ipairs({ { name = "live", path = L122 }, { name = "ann", path = A122 } }) do
    local nm, s = f.name, read_file(f.path)
    check("0s " .. nm .. ": the table is 707 entries with 707 badges (" .. cp(s, "\t{ marker = ") .. ")",
      cp(s, "\t{ marker = ") == 707 and cp(s, 'badge = "') == 707)
    check("0s " .. nm .. ": trigger counts melee_unwavering 374, charge_or_melee 28, enemy_melee 3, "
      .. "enemy_engaged_or_shot 85 (unchanged)",
      cp(s, 'trigger = "melee_unwavering"') == 374 and cp(s, 'trigger = "charge_or_melee"') == 28
      and cp(s, 'trigger = "enemy_melee"') == 3 and cp(s, 'trigger = "enemy_engaged_or_shot"') == 85)
    local function entry_ok(m, k, trig)
      return raw_find(s, 'marker = "' .. m .. '", name = "[^"]*", trigger = "' .. trig .. '"') ~= nil
        and cp(s, 'badge = "zz_auto_badge_' .. m .. '"') == 1 and cp(s, 'keys = { "' .. k .. '" }') == 1
    end
    for _, b in ipairs(MU) do
      check("0s " .. nm .. ": " .. b[1] .. " is on melee_unwavering with its badge and key", entry_ok(b[1], b[2], "melee_unwavering"))
    end
    for _, b in ipairs(CM) do
      check("0s " .. nm .. ": " .. b[1] .. " is on charge_or_melee with its badge and key", entry_ok(b[1], b[2], "charge_or_melee"))
    end
    for _, b in ipairs(EM) do
      check("0s " .. nm .. ": " .. b[1] .. " is on enemy_melee with its badge and key", entry_ok(b[1], b[2], "enemy_melee"))
    end
    check("0s " .. nm .. ": No Escape and Transfix carry range_real 100, Flash Bomb 75 (70% -> 70 m / 52 m)",
      raw_find(s, '"wh3_main_character_abilities_no_escape" },\n\t\trange_real = 100,', 1, true) ~= nil
      and raw_find(s, '"wh3_dlc29_lord_abilities_transfix" },\n\t\trange_real = 100,', 1, true) ~= nil
      and raw_find(s, '"wh_pro01_lord_abilities_flash_bomb" },\n\t\trange_real = 75,', 1, true) ~= nil)
    check("0s " .. nm .. ": the range_real fields are 207 (204 + 3)", cp(s, "\t\trange_real = ") == 207)
    check("0s " .. nm .. ": the two 3-use hexes are held for their own recharge (90 s / 120 s)",
      cp(s, '["wh3_main_character_abilities_no_escape"] = 90,') == 1
      and cp(s, '["wh3_dlc29_lord_abilities_transfix"] = 120,') == 1)
    check("0s " .. nm .. ": the enemy_melee evaluator sets the melee-only flag and uses the UNIT form",
      raw_find(s, "function FOURTH.evaluate_enemy_melee(unit, routing)\n\tFOURTH.eg_melee_only = true\n"
        .. "\treturn FOURTH.eg_pick_enemy(unit, routing, false)\nend", 1, true) ~= nil)
    check("0s " .. nm .. ": enemy_melee is wired in the map and has its tooltip line",
      cp(s, "\tenemy_melee = FOURTH.evaluate_enemy_melee,") == 1
      and cp(s, '\tenemy_melee = "When armed, fires on the closest enemy unit in range that is fighting in melee",') == 1)
    check("0s " .. nm .. ": the upgraded Hunter of Champions key sits in the EXISTING entry",
      raw_find(s, 'marker = "hunter_of_champions", name = "Hunter of Champions", trigger = "enemy_engaged_or_shot",', 1, true) ~= nil
      and cp(s, '"' .. HOC_UP .. '"') == 1 and cp(s, 'marker = "hunter_of_champions"') == 1)
    check("0s " .. nm .. ": Daemonic Possession is NOT in the mod (user decision)",
      raw_find(s, "wh3_main_lord_abilities_daemonic_possession", 1, true) == nil)
  end

  -- ------------------------------------------------------------------ worlds
  local n_ok, n_all, n_silent = 0, 0, 0
  local function boot(W, PATH, TAG, uid, marker, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    deploy_phases(W); ui(W)
    sel_event(W, uid, true); ui(W); ui(W)
    click(W, "zz_auto_badge_" .. marker); ui(W)
    W.conflict = true
    return true
  end
  local function finish(W, TAG, wname, ok, silent)
    check(TAG .. wname .. ": every ui tick ran clean (" .. (W.ui_failures or 0) .. " failures)",
      (W.ui_failures or 0) == 0)
    tally(W)
    n_all = n_all + 1
    if ok then n_ok = n_ok + 1 end
    if silent then n_silent = n_silent + 1 end
  end
  local FILES = { { path = A122, tag = "[annotated] " }, { path = L122, tag = "[live] " } }
  local uid_next = 12200
  local function nid() uid_next = uid_next + 2; return uid_next end

  -- A: melee_unwavering, self-cast
  for i, b in ipairs(MU) do
    print("== HARNESS 122 - A" .. i .. " " .. b[1] .. ": melee / out of melee / wavering ==")
    for _, kind in ipairs({ "M", "S", "V" }) do
      for _, f in ipairs(FILES) do
        local TAG, uid = f.tag, nid()
        local W = make_world({ can_perform = true, units = {
          { name = "owner", uid = uid, owns = { b[2] }, melee = (kind ~= "S"), wavering = (kind == "V") },
        }, cards = { { id = tostring(uid), state = "active", vis = true } }, bar = { { id = "b1", key = b[2] } } })
        local wname = "A" .. i .. kind
        if boot(W, f.path, TAG, uid, b[1], wname) then
          polln(W, 1)
          local ok
          if kind == "M" then
            local a = (#W.fires == 1 and W.fires[1].uid == uid and W.fires[1].key == b[2])
            check(TAG .. wname .. ": " .. b[1] .. " in melee -> FIRES once (" .. fire_detail(W) .. ")", a)
            local c = (fire_target_for(W, uid) == unit_of(W, uid))
            check(TAG .. wname .. ": cast on the OWNER (the aura is centred on the fight)", c)
            local d = (count_log(W, "reason: in melee, morale not wavering") == 1)
            check(TAG .. wname .. ": the shared in-melee reason [live log]", lg(TAG, d))
            ok = a and c and lg(TAG, d)
            finish(W, TAG, wname, ok, false)
          else
            ok = (#W.fires == 0)
            check(TAG .. wname .. ": " .. b[1] .. ((kind == "S") and " NOT in melee" or " in melee but WAVERING")
              .. " -> SILENT (" .. fire_detail(W) .. ")", ok)
            finish(W, TAG, wname, ok, true)
          end
        else
          n_all = n_all + 1
        end
      end
    end
  end

  -- C: charge_or_melee, self-cast
  for i, b in ipairs(CM) do
    print("== HARNESS 122 - C" .. i .. " " .. b[1] .. ": melee / charging / running with no target ==")
    for _, kind in ipairs({ "M", "C", "R" }) do
      for _, f in ipairs(FILES) do
        local TAG, uid = f.tag, nid()
        local def = { name = "owner", uid = uid, owns = { b[2] }, melee = (kind == "M") }
        if kind == "C" then def.fast = true; def.target = "enemy"; def.dist = 20 end
        if kind == "R" then def.fast = true end
        local W = make_world({ can_perform = true, units = { def },
          cards = { { id = tostring(uid), state = "active", vis = true } }, bar = { { id = "b1", key = b[2] } } })
        local wname = "C" .. i .. kind
        if boot(W, f.path, TAG, uid, b[1], wname) then
          polln(W, 1)
          local ok
          if kind == "R" then
            ok = (#W.fires == 0)
            check(TAG .. wname .. ": " .. b[1] .. " RUNNING with no target (a move order, passing by) -> SILENT ("
              .. fire_detail(W) .. ")", ok)
            finish(W, TAG, wname, ok, true)
          else
            local a = (#W.fires == 1 and W.fires[1].uid == uid and W.fires[1].key == b[2])
            check(TAG .. wname .. ": " .. b[1] .. ((kind == "M") and " in melee" or " CHARGING (running, targeted, 20 m)")
              .. " -> FIRES once (" .. fire_detail(W) .. ")", a)
            local c = (fire_target_for(W, uid) == unit_of(W, uid))
            check(TAG .. wname .. ": cast on the OWNER", c)
            local reason = (kind == "M") and "reason: in melee (charge or melee)" or "reason: charging ("
            local d = (count_log(W, reason) == 1)
            check(TAG .. wname .. ": the " .. ((kind == "M") and "melee" or "charge") .. " reason [live log]", lg(TAG, d))
            ok = a and c and lg(TAG, d)
            finish(W, TAG, wname, ok, false)
          end
        else
          n_all = n_all + 1
        end
      end
    end
  end

  -- E: enemy_melee, cast at the enemy
  for i, b in ipairs(EM) do
    local bound = b[3]
    print("== HARNESS 122 - E" .. i .. " " .. b[1] .. " (bound " .. bound .. " m): melee / shot only / beyond / on bound / lapse ==")
    local cases = {
      { k = "M", dist = 20, enemy = { melee = true }, fire = true },
      { k = "SHOT", dist = 20, enemy = { melee = false, missile = true }, fire = false },
      { k = "FAR", dist = bound + 1, enemy = { melee = true }, fire = false },
      { k = "EDGE", dist = bound, enemy = { melee = true }, fire = true },
      { k = "LAPSE", dist = 20, enemy = { melee_seq = { true, false } }, fire = false, lapse = true },
    }
    for _, cs in ipairs(cases) do
      for _, f in ipairs(FILES) do
        local TAG, uid = f.tag, nid()
        local euid = uid + 1
        local edef = { name = "enemy_block", uid = euid }
        for k2, v in pairs(cs.enemy) do edef[k2] = v end
        local W = make_world({ can_perform = true,
          units = { { name = "caster", uid = uid, owns = { b[2] }, melee = false, dist = cs.dist } },
          enemies = { edef },
          cards = { { id = tostring(uid), state = "active", vis = true } },
          bar = { { id = "b1", key = b[2] } } })
        local wname = "E" .. i .. cs.k
        if boot(W, f.path, TAG, uid, b[1], wname) then
          polln(W, 1)
          local ok
          if cs.fire then
            local a = (#W.fires == 1 and W.fires[1].uid == uid and W.fires[1].key == b[2])
            check(TAG .. wname .. ": " .. b[1] .. " enemy IN MELEE at " .. cs.dist .. " m (bound " .. bound
              .. " m) -> FIRES once (" .. fire_detail(W) .. ")", a)
            local enemy = enemy_by(W, euid)
            local c = (enemy ~= nil and fire_target_for(W, uid) == enemy)
            check(TAG .. wname .. ": the cast target is the ENEMY, never the owner", c)
            local d = (count_log(W, "reason: closest fighting (in-melee) enemy within bound (targeting enemy_block") == 1)
            check(TAG .. wname .. ": the melee-only reason names the enemy [live log]", lg(TAG, d))
            ok = a and c and lg(TAG, d)
            finish(W, TAG, wname, ok, false)
          else
            ok = (#W.fires == 0)
            local why = ({ SHOT = "enemy only UNDER MISSILE FIRE (not in melee)",
              FAR = "enemy in melee at " .. cs.dist .. " m, beyond the " .. bound .. " m bound",
              LAPSE = "enemy LEFT melee between decide and cast" })[cs.k]
            check(TAG .. wname .. ": " .. b[1] .. " " .. why .. " -> no cast (" .. fire_detail(W) .. ")", ok)
            if cs.lapse then
              local d = (count_log(W, b[1] .. " SKIPPED: the chosen enemy lapsed before the cast") == 1)
              check(TAG .. wname .. ": the lapse is logged as SKIPPED, cast not spent [live log]", lg(TAG, d))
              ok = ok and lg(TAG, d)
            end
            -- a LIVE lapse world asserts a positive log line (the skip), so it
            -- is a proof of the new path, not a plain silent world (log checks
            -- apply to the live file only)
            finish(W, TAG, wname, ok, not (cs.lapse and TAG == "[live] "))
          end
        else
          n_all = n_all + 1
        end
      end
    end
  end

  -- G: the charge hold on a 3-use hex
  print("== HARNESS 122 - G: No Escape (3 uses) is held for its own 90 s recharge ==")
  for _, f in ipairs(FILES) do
    local TAG, uid = f.tag, nid()
    local K = EM[1][2]
    local W = make_world({ can_perform = true,
      units = { { name = "caster", uid = uid, owns = { K }, melee = false, dist = 20 } },
      enemies = { { name = "enemy_block", uid = uid + 1, melee = true } },
      cards = { { id = tostring(uid), state = "active", vis = true } }, bar = { { id = "b1", key = K } } })
    if boot(W, f.path, TAG, uid, "no_escape", "G") then
      polln(W, 1)
      local a = (#W.fires == 1)
      check(TAG .. "G1: the first poll casts No Escape once (" .. fire_detail(W) .. ")", a)
      polln(W, 40)   -- 10 s at 250 ms: past the 2 s guard, well inside 90 s
      local c = (#W.fires == 1)
      check(TAG .. "G2: 10 s later the pool is still HELD (fires " .. #W.fires .. ", want 1)", c)
      local d = (count_log(W, "charge gate no_escape: one use spent - the next attempt waits 90s") == 1)
      check(TAG .. "G3: the hold names its own 90 s recharge [live log]", lg(TAG, d))
      finish(W, TAG, "G", a and c and lg(TAG, d), false)
    else
      n_all = n_all + 1
    end
  end

  -- H: the upgraded Hunter of Champions key through the existing entry
  print("== HARNESS 122 - H: the upgraded Hunter of Champions key (enemy_engaged_or_shot) ==")
  for _, f in ipairs(FILES) do
    local TAG, uid = f.tag, nid()
    local W = make_world({ can_perform = true,
      units = { { name = "caster", uid = uid, owns = { HOC_UP }, melee = false, dist = 20 } },
      enemies = { { name = "enemy_block", uid = uid + 1, melee = false, missile = true } },
      cards = { { id = tostring(uid), state = "active", vis = true } }, bar = { { id = "b1", key = HOC_UP } } })
    if boot(W, f.path, TAG, uid, "hunter_of_champions", "H") then
      polln(W, 1)
      local a = (#W.fires == 1 and W.fires[1].key == HOC_UP)
      check(TAG .. "H1: the upgraded key fires on an enemy under missile fire in range (" .. fire_detail(W) .. ")", a)
      local enemy = enemy_by(W, uid + 1)
      local c = (enemy ~= nil and fire_target_for(W, uid) == enemy)
      check(TAG .. "H2: the cast target is the ENEMY", c)
      finish(W, TAG, "H", a and c, false)
    else
      n_all = n_all + 1
    end
  end

  if not RED122 then
    check("HARNESS 122: every world behaved - " .. n_ok .. "/" .. n_all, n_all == 76 and n_ok == 76)
  else
    check("RED CONTROL (harness 122): on the pre-123 snapshot only the SILENT worlds pass - "
      .. n_ok .. "/" .. n_all .. " (want " .. n_silent .. " = the silent worlds without a log proof)", n_ok == n_silent)
  end
  print("== HARNESS 122 done: " .. (checks - pre122) .. " checks in this section ==")
end
'''

src = open(SRC, encoding="utf-8").read()

PIN_RULES = [
    ("== 697", "== 707"),
    ("== 748", "== 759"),
    ("entries = 697, keys = 748, mu = 370", "entries = 707, keys = 759, mu = 374"),
    ("entries = 697, keys = 748, sum = true", "entries = 707, keys = 759, sum = true"),
    ("FULL 697-entry table", "FULL 707-entry table"),
    ("697 abilities per pass", "707 abilities per pass"),
    ("has 697 entries", "has 707 entries"),
    ("has all 748 keys", "has all 759 keys"),
    ("table of 697 after round 122", "table of 707 after round 123"),
    ("(12 air-drop entries of 697)", "(12 air-drop entries of 707)"),
    ("want 697", "want 707"),
    ("'trigger = \"melee_unwavering\"') == 370", "'trigger = \"melee_unwavering\"') == 374"),
    ("      mu == 370)", "      mu == 374)"),
    ("'trigger = \"charge_or_melee\"') == 25", "'trigger = \"charge_or_melee\"') == 28"),
    ("      cm == 25)", "      cm == 28)"),
    ("a = (it == 1394)", "a = (it == 1414)"),
    ('"\\t\\trange_real = ") == 204)', '"\\t\\trange_real = ") == 207)'),
    ("(EXP.sum and 204 or 96)", "(EXP.sum and 207 or 96)"),
    ("(RED_MODE and 0 or 161)", "(RED_MODE and 0 or 163)"),
]
lines = src.split("\n")
changed = []
for i, ln in enumerate(lines):
    if ln.lstrip().startswith("--"):
        continue
    new = ln
    for a, b in PIN_RULES:
        if a in new:
            new = new.replace(a, b)
    if new != ln:
        changed.append((i + 1, ln.strip()[:120]))
        lines[i] = new
src = "\n".join(lines)
print("count-pin lines rebased:", len(changed))
for c in changed:
    print("  L%-6d %s" % c)

TIP_OLD = '    enemy_engaged_or_shot = "When armed, fires when an enemy unit in range is in melee or under missile fire",\n'
TIP_NEW = TIP_OLD + '    enemy_melee = "When armed, fires on the closest enemy unit in range that is fighting in melee",\n'
assert src.count(TIP_OLD) == 1, src.count(TIP_OLD)
src = src.replace(TIP_OLD, TIP_NEW)
print("harness-93 tooltip mirror: enemy_melee wording added")

RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
CALL = "run_h118()\nrun_h121()\n"
assert src.count(CALL) == 1, src.count(CALL)
src = src.replace(CALL, "run_h118()\nrun_h121()\nrun_h122()\n")

src = BANNER + src
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
