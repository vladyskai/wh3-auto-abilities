"""Independent verification of the INSTALLED distance-observer pack (fresh RPFM session).

Opens zz_probe_dist.pack FROM THE GAME FOLDER, lists it, byte-compares the packed
observer script against the source, spot-checks its tokens, asserts the main mod
pack is absent from it, and re-checks the step-probe retirement + main mod md5.
"""
import hashlib
import json
import os
import sys
from websockets.sync.client import connect

WS_URL = "ws://127.0.0.1:45127/ws"
GAME_ROOT = r"C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III"
GAME_DATA = GAME_ROOT + "/data"
GAME_PACK = GAME_DATA + "/zz_probe_dist.pack"
STEP_PACK = GAME_DATA + "/zz_probe_step.pack"
STEP_LOG = GAME_ROOT + "/zz_probe_step_log.txt"
STEP_LOG_RUN1 = GAME_ROOT + "/zz_probe_step_log_run1.txt"
SRC_ROOT = r"C:/Users/vlady/Desktop/WH3_mod/mod_source"
PROBE_SRC = SRC_ROOT + "/script/battle/mod/zz_probe_dist.lua"
PROBE_IN_PACK = "script/battle/mod/zz_probe_dist.lua"
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
print(f"\n=== {len(paths)} file(s) in the INSTALLED distance-observer pack ===")
for p in paths:
    print("   -", p)
print("only the observer file present :", paths == [PROBE_IN_PACK])
print("no main-mod path present       :", not any("zz_test_deadly_onslaught" in p for p in paths))
assert paths == [PROBE_IN_PACK], f"unexpected contents: {paths}"

raw = bytes(c.send({"GetPackedFileRawData": [key, PROBE_IN_PACK]})["VecU8"])
src = open(PROBE_SRC, "rb").read()
print("\nbyte-for-byte vs source:")
print(f"   pack   {len(raw):>7d}  sha256 {hashlib.sha256(raw).hexdigest()}")
print(f"   source {len(src):>7d}  sha256 {hashlib.sha256(src).hexdigest()}")
print("   MATCHES SOURCE (byte-identical):", raw == src)
assert raw == src, "installed observer file is NOT byte-identical to source"

txt = raw.decode("utf-8", "replace")
for tok in ("zz_probe_dist_status",
            "get_scriptunits_for_local_players_army",
            "get_scriptunits_for_main_enemy_army_to_local_player",
            "unit_distance", "unit_in_range",
            "OWNER chosen:", "OBS tick=", "caster_pos=", "caster_moved_since_last=",
            "caster_is_moving=", "caster_is_idle=",
            "CAND tick=", "in_melee=", "under_fire=",
            "engine_unit_in_range=", "our_52_test=", "our_75_test=",
            "CAND-FIRST tick=", "first_passing_test=", "mode=first",
            "CANPERF tick=",
            "GATE conflict phase ENTERED", "conflict=", "phase=",
            "probe finished (poll cap"):
    print(f"   token {tok:52s} present: {tok in txt}")
    assert tok in txt, f"missing token: {tok}"
assert '"wh_main_hero_abilities_accusation"' in txt, "observed ability key literal missing"
for forbidden in (":perform_special_ability(", ":perform_special_ability_ground(",
                  "select_in_ui(", "SetContextObject(", "reset_ability_cooldown(",
                  "kill_number_of_men(", "heal_hitpoints_unary(", "teleport_to_location(",
                  "attack_unit(", "take_control(", "release_control("):
    assert forbidden not in txt, f"a write snuck into the observer: {forbidden}"
assert "can_perform_special_ability(" in txt, "CANPERF read missing"
print("\nno cast call, no write-shaped call, CANPERF present : True")

# retirement re-check (independent of the build script's own report)
print("\n== step-probe retirement re-check ==")
print(f"   data/zz_probe_step.pack present  : {os.path.exists(STEP_PACK)}  (want False)")
print(f"   zz_probe_step_log.txt present    : {os.path.exists(STEP_LOG)}  (want False)")
print(f"   zz_probe_step_log_run1.txt present: {os.path.exists(STEP_LOG_RUN1)}  (want True)")
assert not os.path.exists(STEP_PACK), "step-probe pack came back!"
assert not os.path.exists(STEP_LOG), "step-probe log still at old path!"
assert os.path.exists(STEP_LOG_RUN1), "rotated step-probe log missing!"

if os.path.exists(MAIN_PACK):
    main_md5 = hashlib.md5(open(MAIN_PACK, "rb").read()).hexdigest()
    print(f"\nmain mod pack md5 (now)              : {main_md5}")
    if EXPECT_MAIN_MD5:
        print(f"main mod pack md5 (expected, before) : {EXPECT_MAIN_MD5}")
        print("   UNCHANGED :", main_md5 == EXPECT_MAIN_MD5)
        assert main_md5 == EXPECT_MAIN_MD5, "the main mod pack CHANGED!"

try:
    c.send("ClientDisconnecting")
except Exception:
    pass
print("\nINSTALLED-PACK VERIFY OK")
