# -*- coding: utf-8 -*-
"""Independent verification of the installed round-99 pack."""
import hashlib, json, os
from websockets.sync.client import connect

WS = "ws://127.0.0.1:45127/ws"
GAME = r"C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III/data"
PACK = GAME + "/zz_test_deadly_onslaught.pack"
SRC = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"
IN_PACK = "script/battle/mod/zz_test_deadly_onslaught.lua"

class C:
    def __init__(self):
        self.ws = connect(WS, max_size=None, open_timeout=20, legacy=True); self.n = 1; self.ws.recv(timeout=20)
    def send(self, cmd):
        i = self.n; self.n += 1
        self.ws.send(json.dumps({"id": i, "data": cmd}))
        while True:
            m = json.loads(self.ws.recv(timeout=300))
            if m.get("id") == i: return m.get("data")

c = C()
c.send({"SetGameSelected": ["warhammer_3", False]})
key = c.send({"OpenPackFiles": [PACK]})["StringContainerInfo"][0]
raw = bytes(c.send({"GetPackedFileRawData": [key, IN_PACK]})["VecU8"])
src = open(SRC, "rb").read()
print("installed md5        :", hashlib.md5(open(PACK, "rb").read()).hexdigest())
print("installed size       :", os.path.getsize(PACK))
print("pack main == source  :", raw == src, len(raw), "bytes")
print("source sha256        :", hashlib.sha256(src).hexdigest())
txt = raw.decode("utf-8")
TOK = ("FOURTH.ALLY_CAST_R50  = 35", "FOURTH.ALLY_CAST_R60  = 42", "FOURTH.ALLY_CAST_R75  = 52",
       "FOURTH.ALLY_CAST_R100 = 70", "FOURTH.ALLY_CAST_R150 = 105", "FOURTH.ALLY_CAST_R200 = 140",
       "FOURTH.ALLY_CAST = {", "\t[200] = FOURTH.ALLY_CAST_R200,",
       "ability.range_m = FOURTH.ALLY_CAST[ability.ally_range_real]",
       "function FOURTH.ab_fresh_friend_su(unit)", "function FOURTH.ab_pick_ally(unit, routing, family)",
       "function FOURTH.ab_ally_valid(unit, ally)",
       "FOURTH.ab_caster_su = FOURTH.ab_fresh_friend_su(unit)",
       "FOURTH.ab_ally_su = FOURTH.ab_fresh_friend_su(best_ally)",
       "uc = FOURTH.ab_caster_su.uc", "target = FOURTH.ab_ally_su.unit",
       "function FOURTH.evaluate_ally_heal(unit, routing)",
       "function FOURTH.evaluate_ally_heal_melee(unit, routing)",
       "function FOURTH.evaluate_ally_wavering(unit, routing)",
       "function FOURTH.evaluate_ally_melee_buff(unit, routing)",
       "function FOURTH.evaluate_ally_overseer(unit, routing)",
       "function FOURTH.evaluate_ally_beast(unit, routing)",
       "function FOURTH.evaluate_ally_broken(unit, routing)",
       "function FOURTH.evaluate_ally_missile(unit, routing)",
       "function FOURTH.evaluate_ally_warmachine_heal(unit, routing)",
       "function FOURTH.evaluate_ally_hellforged_heal(unit, routing)",
       "function FOURTH.evaluate_ally_monster_heal(unit, routing)",
       "function FOURTH.evaluate_ally_construct_heal(unit, routing)",
       "function FOURTH.evaluate_ally_infinite_buff(unit, routing)",
       "function FOURTH.evaluate_ally_winds(unit, routing)",
       "ally_heal = FOURTH.evaluate_ally_heal,", "ally_heal_melee = FOURTH.evaluate_ally_heal_melee,",
       "ally_wavering = FOURTH.evaluate_ally_wavering,", "ally_melee_buff = FOURTH.evaluate_ally_melee_buff,",
       "ally_overseer = FOURTH.evaluate_ally_overseer,", "ally_beast = FOURTH.evaluate_ally_beast,",
       "ally_broken = FOURTH.evaluate_ally_broken,", "ally_missile = FOURTH.evaluate_ally_missile,",
       "ally_warmachine_heal = FOURTH.evaluate_ally_warmachine_heal,",
       "ally_hellforged_heal = FOURTH.evaluate_ally_hellforged_heal,",
       "ally_monster_heal = FOURTH.evaluate_ally_monster_heal,",
       "ally_construct_heal = FOURTH.evaluate_ally_construct_heal,",
       "ally_infinite_buff = FOURTH.evaluate_ally_infinite_buff,",
       "ally_winds = FOURTH.evaluate_ally_winds,",
       "FOURTH.class_keys = {", "function FOURTH.class_member(unit, name)",
       "function FOURTH.ab_filter_ok(unit)", "function FOURTH.morale_broken(unit)",
       "function FOURTH.ab_bound_text()", "if FOURTH.ab_infinite then return true end",
       "none (infinite range per wiki)", 'family == "winds"',
       'FOURTH.context_value(other, "HealthValue")',
       "FOURTH.ab_range_m = ability.range_m", "FOURTH.ab_marker = ability.marker",
       "FOURTH.ab_filter = nil", "FOURTH.ab_infinite = nil",
       'marker = "butcher", name = "Meat Feast", trigger = "ushoran_health"')
missing = [t for t in TOK if t not in txt]
print("tokens missing       :", missing)
print("contains 'unit_in_range(' :", "unit_in_range(" in txt, "(want False)")
print("contains 'string.find('   :", "string.find(" in txt, "(want False)")
print("trigger counts        : melee_unwavering=%d charge_or_melee=%d ushoran_health=%d melee_health75=%d"
      % (txt.count('trigger = "melee_unwavering"'), txt.count('trigger = "charge_or_melee"'),
         txt.count('trigger = "ushoran_health"'), txt.count('trigger = "melee_health75"')))
print("ally trigger counts   : melee_buff=%d heal=%d heal_melee=%d wavering=%d | overseer=%d beast=%d broken=%d missile=%d warmachine=%d hellforged=%d monster=%d construct=%d infinite=%d winds=%d"
      % (txt.count('trigger = "ally_melee_buff"'), txt.count('trigger = "ally_heal"'),
         txt.count('trigger = "ally_heal_melee"'), txt.count('trigger = "ally_wavering"'),
         txt.count('trigger = "ally_overseer"'), txt.count('trigger = "ally_beast"'),
         txt.count('trigger = "ally_broken"'), txt.count('trigger = "ally_missile"'),
         txt.count('trigger = "ally_warmachine_heal"'), txt.count('trigger = "ally_hellforged_heal"'),
         txt.count('trigger = "ally_monster_heal"'), txt.count('trigger = "ally_construct_heal"'),
         txt.count('trigger = "ally_infinite_buff"'), txt.count('trigger = "ally_winds"')))
print("ally_range_real fields:", txt.count("\t\tally_range_real = "), "(want 32)")
# class list sizes
for nm, sz in (("beast", 55), ("monster", 235), ("warmachine", 68), ("construct", 29),
               ("hellforged", 13), ("missile", 493), ("overseer", 918)):
    i = txt.find(nm + " = {"); j = txt.find("},", i)
    got = txt[i:j].count("] = true,")
    print("  class %-11s %5d (want %d) %s" % (nm, got, sz, "OK" if got == sz else "MISMATCH"))
print("entries               :", txt.count("\t{ marker = "), "| badges:", txt.count('badge = "'))
print("--- game data dir ---")
for f in ("zz_test_deadly_onslaught.pack", "zz_probe_dist.pack", "zz_probe_step.pack", "zz_probe_enemy_target.pack"):
    p = os.path.join(GAME, f)
    if os.path.exists(p):
        print("  present %-32s md5 %s  size %d" % (f, hashlib.md5(open(p, "rb").read()).hexdigest(), os.path.getsize(p)))
    else:
        print("  absent  %-32s" % f)
