"""Independent verification of the installed Class-B pack (round 98)."""
import hashlib, json, os
from websockets.sync.client import connect

WS = "ws://127.0.0.1:45127/ws"
GAME = r"C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III/data"
PACK = GAME + "/zz_test_deadly_onslaught.pack"
SRC = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"
IN_PACK = "script/battle/mod/zz_test_deadly_onslaught.lua"

class C:
    def __init__(self):
        self.ws = connect(WS, max_size=None, open_timeout=20); self.n = 1; self.ws.recv(timeout=20)
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
       "FOURTH.ALLY_CAST_R100 = 70", "FOURTH.ALLY_CAST_R150 = 105", "FOURTH.ALLY_CAST = {",
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
       "ally_heal = FOURTH.evaluate_ally_heal,", "ally_heal_melee = FOURTH.evaluate_ally_heal_melee,",
       "ally_wavering = FOURTH.evaluate_ally_wavering,", "ally_melee_buff = FOURTH.evaluate_ally_melee_buff,",
       "FOURTH.ab_range_m = ability.range_m", "FOURTH.ab_marker = ability.marker",
       'marker = "butcher", name = "Meat Feast", trigger = "ushoran_health"')
for tok in TOK:
    print("contains %-62s: %s" % (repr(tok)[:62], tok in txt))
print("contains 'unit_in_range(' :", "unit_in_range(" in txt, "(want False)")
print("trigger counts        : melee_unwavering=%d charge_or_melee=%d ushoran_health=%d melee_health75=%d"
      % (txt.count('trigger = "melee_unwavering"'), txt.count('trigger = "charge_or_melee"'),
         txt.count('trigger = "ushoran_health"'), txt.count('trigger = "melee_health75"')))
print("ally trigger counts   : ally_melee_buff=%d ally_heal=%d ally_heal_melee=%d ally_wavering=%d"
      % (txt.count('trigger = "ally_melee_buff"'), txt.count('trigger = "ally_heal"'),
         txt.count('trigger = "ally_heal_melee"'), txt.count('trigger = "ally_wavering"')))
print("ally_range_real fields:", txt.count("\t\tally_range_real = "))
print("enemy counts          : melee_unwavering moved; enemy_engaged_or_shot=%d enemy_ground_area=%d range_real=%d"
      % (txt.count('trigger = "enemy_engaged_or_shot"'), txt.count('trigger = "enemy_ground_area"'),
         txt.count("\t\trange_real = ")))
print("entries               :", txt.count("\t{ marker = "))
print("--- game data dir ---")
for f in ("zz_test_deadly_onslaught.pack", "zz_probe_dist.pack", "zz_probe_step.pack", "zz_probe_enemy_target.pack"):
    p = os.path.join(GAME, f)
    if os.path.exists(p):
        print("  present %-32s md5 %s  size %d" % (f, hashlib.md5(open(p, "rb").read()).hexdigest(), os.path.getsize(p)))
    else:
        print("  absent  %-32s" % f)
