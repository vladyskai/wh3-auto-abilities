"""Round 111: keep the round-110 worlds on the rule they were written against.

The harness-110 section measures the TWO-BODY mechanics with the caster projected
the full delay ahead - i.e. AIR_DROP_CASTER_LEAD = 1.0, which is no longer the
shipped default (0.5). Every world whose CASTER MOVES is now pinned to lead 1.0
explicitly, through a new optional `knobs` argument on boot110, so its documented
distances and log fragments stay exactly what round 110 proved. Stationary-caster
worlds need no pin: the lead term multiplies zero velocity.

Also updates the two source tokens the round-111 formula renames.
"""
import io

P = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261022_airdrop_relative_harness110/h110_section.lua"
s = io.open(P, encoding="utf-8", newline="").read()
assert "\r" not in s

# 1. header note
OLD_H = """-- PINS (documented, asserted against the source): BOUND = 6 m,
-- DELAY = 1.5 s. Every world states the distances it uses.
"""
NEW_H = """-- PINS (documented, asserted against the source): BOUND = 6 m,
-- DELAY = 1.5 s. Every world states the distances it uses.
-- ROUND 111 PIN: this section measures the two-body MECHANICS with the caster
-- projected the full delay ahead, i.e. the round-110 rule
-- (AIR_DROP_CASTER_LEAD = 1.0). That is no longer the shipped default, so every
-- world whose CASTER MOVES pins lead 1.0 through boot110's `knobs` argument; a
-- stationary caster needs no pin (the lead multiplies zero velocity). Round 111's
-- own section proves the knob.
"""
assert s.count(OLD_H) == 1
s = s.replace(OLD_H, NEW_H)

# 2. boot110 gains the knob override
OLD_B = """  local function boot110(W, PATH, TAG, uid, marker, wname)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
"""
NEW_B = """  local function boot110(W, PATH, TAG, uid, marker, wname, knobs)
    local ok = pcall(load_world, W, PATH)
    check(TAG .. wname .. ": the file loads", ok)
    if not ok then tally(W); return false end
    -- ROUND 111: pin the caster's lead for the worlds written against the
    -- round-110 rule (lead 1.0). Read by FOURTH.ad_lead on every call, so this
    -- is the same dial the shipped default sets.
    if knobs ~= nil and FOURTH ~= nil then
      if knobs.lead ~= nil then FOURTH.AIR_DROP_CASTER_LEAD = knobs.lead end
      if knobs.delay ~= nil then FOURTH.AIR_DROP_CASTER_DELAY_S = knobs.delay end
    end
"""
assert s.count(OLD_B) == 1
s = s.replace(OLD_B, NEW_B)

# 3. pin lead 1.0 on every MOVING-CASTER world
PINS = [
    ('if boot110(W, PATH, TAG, uid, "death_from_above", "B1") then',
     'if boot110(W, PATH, TAG, uid, "death_from_above", "B1", { lead = 1.0 }) then'),
    ('if boot110(W, PATH, TAG, uid, "death_from_above", "B2") then',
     'if boot110(W, PATH, TAG, uid, "death_from_above", "B2", { lead = 1.0 }) then'),
    ('if boot110(W, PATH, TAG, uid, "death_from_above", "D1") then',
     'if boot110(W, PATH, TAG, uid, "death_from_above", "D1", { lead = 1.0 }) then'),
    ('if boot110(W, PATH, TAG, uid, "death_from_above", "D2") then',
     'if boot110(W, PATH, TAG, uid, "death_from_above", "D2", { lead = 1.0 }) then'),
    ('if boot110(W, PATH, TAG, uid, "death_from_above", "E1") then',
     'if boot110(W, PATH, TAG, uid, "death_from_above", "E1", { lead = 1.0 }) then'),
    ('if boot110(W, PATH, TAG, uid, "death_from_above", "E2") then',
     'if boot110(W, PATH, TAG, uid, "death_from_above", "E2", { lead = 1.0 }) then'),
    ('if boot110(W, PATH, TAG, uid, "death_from_above", "G4") then',
     'if boot110(W, PATH, TAG, uid, "death_from_above", "G4", { lead = 1.0 }) then'),
    ('if boot110(W, LIVE, "[live] ", uid, "death_from_above", "I1") then',
     'if boot110(W, LIVE, "[live] ", uid, "death_from_above", "I1", { lead = 1.0 }) then'),
    ('if boot110(W, INHERIT_FILE, "[inherit] ", uid, "death_from_above", "I2") then',
     'if boot110(W, INHERIT_FILE, "[inherit] ", uid, "death_from_above", "I2", { lead = 1.0 }) then'),
]
for old, new in PINS:
    assert s.count(old) == 1, old
    s = s.replace(old, new)

# 4. the two source tokens the round-111 formula renames
OLD_T = """    check("0ab " .. nm .. ": the ONE momentum flag adds v*t a SECOND time for the caster",
      lead ~= nil
      and raw_find(lead, "if allow_bearing and FOURTH.AIR_DROP_INHERIT == true then", 1, true) ~= nil
      and raw_find(lead, "px = px + vx * t", 1, true) ~= nil
      and raw_find(lead, "pz = pz + vz * t", 1, true) ~= nil)
"""
NEW_T = """    check("0ab " .. nm .. ": the ONE momentum flag adds the caster's lead term a SECOND time",
      lead ~= nil
      and raw_find(lead, "if allow_bearing and FOURTH.AIR_DROP_INHERIT == true then", 1, true) ~= nil
      and raw_find(lead, "px = px + vx * t_caster * lead_caster", 1, true) ~= nil
      and raw_find(lead, "pz = pz + vz * t_caster * lead_caster", 1, true) ~= nil)
"""
assert s.count(OLD_T) == 1
s = s.replace(OLD_T, NEW_T)

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched", P, len(s), "bytes")
