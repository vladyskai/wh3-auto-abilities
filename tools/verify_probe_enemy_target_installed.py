"""Independent verification of the INSTALLED probe pack (fresh RPFM session).

Opens zz_probe_enemy_target.pack FROM THE GAME FOLDER, lists it, byte-compares
the packed probe script against the source, spot-checks its tokens, and asserts
the main mod pack is absent from it.
"""
import hashlib
import json
import os

from websockets.sync.client import connect

WS_URL = "ws://127.0.0.1:45127/ws"
GAME_DATA = r"C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III/data"
GAME_PACK = GAME_DATA + "/zz_probe_enemy_target.pack"
SRC_ROOT = r"C:/Users/vlady/Desktop/WH3_mod/mod_source"
PROBE_SRC = SRC_ROOT + "/script/battle/mod/zz_probe_enemy_target.lua"
PROBE_IN_PACK = "script/battle/mod/zz_probe_enemy_target.lua"


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
print(f"\n=== {len(paths)} file(s) in the INSTALLED probe pack ===")
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
for tok in ("zz_probe_enemy_target_status",
            "get_scriptunits_for_main_enemy_army_to_local_player",
            "get_scriptunits_for_local_players_army",
            "get_first_non_player_army",
            "script_unit:new",
            "perform_special_ability_q",
            "use_special_ability",
            "attack_unit",
            "take_control",
            "release_control",
            "register_command_handler_callback",
            "CMD event=SpecialAbility",
            "TRY route=", "ORDER route=", "CANPOST route=",
            "SELF route=", "EFF route=", "RESULT route=", "landed=",
            "ActiveEffectList(true).Size", "conflict="):
    print(f"   token {tok:52s} present: {tok in txt}")
    assert tok in txt, f"missing token: {tok}"
for label in ("bench_fresh", "queued_q", "army_use",
              "take_control", "attack_then_cast", "in_range_cast"):
    assert f'"{label}"' in txt, f"route label {label} missing"
for forbidden in ("select_in_ui(", "SetContextObject(",
                  "reset_ability_cooldown(", "kill_number_of_men(",
                  "heal_hitpoints_unary(", "teleport_to_location("):
    assert forbidden not in txt, f"a write snuck into the probe: {forbidden}"

try:
    c.send("ClientDisconnecting")
except Exception:
    pass
print("\nINSTALLED-PACK VERIFY OK")
