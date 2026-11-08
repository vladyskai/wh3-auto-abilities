"""Independent verification of the INSTALLED step-probe pack (fresh RPFM session).

Opens zz_probe_step.pack FROM THE GAME FOLDER, lists it, byte-compares the packed
probe script against the source, spot-checks its tokens, and asserts the main mod
pack is absent from it.
"""
import hashlib
import json
import os
import sys

from websockets.sync.client import connect

WS_URL = "ws://127.0.0.1:45127/ws"
GAME_DATA = r"C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III/data"
GAME_PACK = GAME_DATA + "/zz_probe_step.pack"
SRC_ROOT = r"C:/Users/vlady/Desktop/WH3_mod/mod_source"
PROBE_SRC = SRC_ROOT + "/script/battle/mod/zz_probe_step.lua"
PROBE_IN_PACK = "script/battle/mod/zz_probe_step.lua"
MAIN_PACK = GAME_DATA + "/zz_test_deadly_onslaught.pack"

EXPECT_MAIN_MD5 = sys.argv[1] if len(sys.argv) > 1 else None


class Client:
    def __init__(self, url=WS_URL):
        self.ws = connect(url, max_size=None, open_timeout=20)
        self.next_id = 1
        self.ws.recv(timeout=20)  # hello

    def send(self, command):
        rid = self.next_id
        self.next_id += 1
        self.ws.send(json.dumps({"id": rid, "data": command}))
        while True:
            msg = json.loads(self.ws.recv(timeout=300))
            if msg.get("id") == rid:
                return msg.get("data")


c = Client()
c.send({"SetGameSelected": ["warhammer_3", False]})
resp = c.send({"OpenPackFiles": [GAME_PACK]})
key, container = resp["StringContainerInfo"]
print("opened INSTALLED pack; type:", container.get("pfh_file_type"),
      "| version:", container.get("pfh_version"))

info = c.send({"GetPackFileDataForTreeView": key})
_, files = info["ContainerInfoVecRFileInfo"]
paths = sorted(f["path"] for f in files)
print(f"\n=== {len(paths)} file(s) in the INSTALLED step-probe pack ===")
for p in paths:
    print("   -", p)
print("only the probe file present :", paths == [PROBE_IN_PACK])
print("no main-mod path present    :", not any("zz_test_deadly_onslaught" in p for p in paths))
assert paths == [PROBE_IN_PACK], f"unexpected contents: {paths}"

raw = bytes(c.send({"GetPackedFileRawData": [key, PROBE_IN_PACK]})["VecU8"])
src = open(PROBE_SRC, "rb").read()
print("\nbyte-for-byte vs source:")
print(f"   pack   {len(raw):>7d}  sha256 {hashlib.sha256(raw).hexdigest()}")
print(f"   source {len(src):>7d}  sha256 {hashlib.sha256(src).hexdigest()}")
print("   MATCHES SOURCE:", raw == src)
assert raw == src, "installed probe file is NOT byte-identical to source"

txt = raw.decode("utf-8", "replace")
for tok in ("zz_probe_step_status",
            "perform_special_ability",
            "register_command_handler_callback",
            "BEFORE cast=", "READ ", " => ", "NOT CALLED (write-shaped)",
            "CMD tick=", "CAST-PLAN cast=", "TRY cast=", "ACCEPTED cast=",
            "POSTPOS cast=", "SAMPLING cast=", "SAMPLE cast=",
            "REFUSED cast=", "STEP RESULT cast=", "VERDICT cast=",
            "moved_total=", "order_after_attack=", "order_after_move=",
            "already_moving_before=", "refused=", "orders_seen=",
            "unit_distance", "is_under_missile_attack", "conflict="):
    print(f"   token {tok:52s} present: {tok in txt}")
    assert tok in txt, f"missing token: {tok}"
for k in ("wh_main_hero_abilities_accusation",
          "wh2_main_character_abilities_assassins_trophy",
          "wh3_dlc29_hero_active_amulet_of_pha_stah"):
    assert f'"{k}"' in txt, f"armed key missing: {k}"
for forbidden in ("select_in_ui(", "SetContextObject(", "reset_ability_cooldown(",
                  "kill_number_of_men(", "heal_hitpoints_unary(", "teleport_to_location(",
                  "attack_unit(", "take_control(", "release_control("):
    assert forbidden not in txt, f"a write snuck into the probe: {forbidden}"

if os.path.exists(MAIN_PACK):
    main_md5 = hashlib.md5(open(MAIN_PACK, "rb").read()).hexdigest()
    print(f"\nmain mod pack md5 (now) : {main_md5}")
    if EXPECT_MAIN_MD5:
        print(f"main mod pack md5 (expected, before) : {EXPECT_MAIN_MD5}")
        print("   UNCHANGED :", main_md5 == EXPECT_MAIN_MD5)
        assert main_md5 == EXPECT_MAIN_MD5, "the main mod pack CHANGED!"

try:
    c.send("ClientDisconnecting")
except Exception:
    pass
print("\nINSTALLED-PACK VERIFY OK")
