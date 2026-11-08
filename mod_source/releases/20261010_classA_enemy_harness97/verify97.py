"""Independent verification of the installed Class-A pack (round 97)."""
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
print("pack main == source  :", raw == src, len(raw), "bytes")
txt = raw.decode("utf-8")
for tok in ("FOURTH.ENEMY_CAST_R100 = 70", "FOURTH.ENEMY_CAST = {",
            "enemy_ground_area = FOURTH.evaluate_enemy_ground_area,",
            "function FOURTH.enemy_ground_cast(uc, enemy, ability_key)",
            "function FOURTH.eg_pick_enemy(unit, routing, ground)",
            "ability.range_m = FOURTH.ENEMY_CAST[ability.range_real]",
            '["wh2_dlc10_character_abilities_entangle"] = true,'):
    print("contains %-58s: %s" % (repr(tok)[:58], tok in txt))
print("contains 'unit_in_range(' :", "unit_in_range(" in txt, "(want False)")
print("trigger counts        : melee_unwavering=%d enemy_engaged_or_shot=%d enemy_ground_area=%d range_real=%d"
      % (txt.count('trigger = "melee_unwavering"'), txt.count('trigger = "enemy_engaged_or_shot"'),
         txt.count('trigger = "enemy_ground_area"'), txt.count("\t\trange_real = ")))
print("entries               :", txt.count("\t{ marker = "))
print("--- game data dir ---")
for f in ("zz_test_deadly_onslaught.pack", "zz_probe_dist.pack", "zz_probe_step.pack", "zz_probe_enemy_target.pack"):
    p = os.path.join(GAME, f)
    if os.path.exists(p):
        print("  present %-32s md5 %s  size %d" % (f, hashlib.md5(open(p, "rb").read()).hexdigest(), os.path.getsize(p)))
    else:
        print("  absent  %-32s" % f)
