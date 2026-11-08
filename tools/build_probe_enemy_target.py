"""Build the THROWAWAY probe pack zz_probe_enemy_target.pack, verify it, install it.

One WebSocket session (RPFM headless backend on ws://127.0.0.1:45127/ws).

Pack contents (exactly ONE file - the probe is self-contained):
  script/battle/mod/zz_probe_enemy_target.lua

It is a SEPARATE Movie pack from the main mod. The main mod's pack and source
are NOT touched; their md5s are recorded before and after and asserted equal.
"""
import hashlib
import json
import os
import shutil

from websockets.sync.client import connect

WS_URL = "ws://127.0.0.1:45127/ws"
SRC_ROOT = r"C:/Users/vlady/Desktop/WH3_mod/mod_source"

PROBE_SRC = SRC_ROOT + "/script/battle/mod/zz_probe_enemy_target.lua"
PROBE_IN_PACK = "script/battle/mod/zz_probe_enemy_target.lua"

OUT_PACK = SRC_ROOT + "/dist/zz_probe_enemy_target.pack"
GAME_DATA = r"C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III/data"
GAME_PACK = GAME_DATA + "/zz_probe_enemy_target.pack"

MAIN_PACK = GAME_DATA + "/zz_test_deadly_onslaught.pack"
MAIN_SRC = SRC_ROOT + "/script/battle/mod/zz_test_deadly_onslaught.lua"

FILES = [(PROBE_SRC, PROBE_IN_PACK)]


class Client:
    def __init__(self, url):
        self.ws = connect(url, max_size=None, open_timeout=20)
        self.next_id = 1
        print("  hello:", json.dumps(json.loads(self.ws.recv(timeout=20))))

    def send(self, command):
        req_id = self.next_id
        self.next_id += 1
        self.ws.send(json.dumps({"id": req_id, "data": command}))
        while True:
            msg = json.loads(self.ws.recv(timeout=300))
            if msg.get("id") == req_id:
                return msg.get("data")
            print("  (unsolicited)", json.dumps(msg)[:160])


def step(label, command):
    print(f"\n== {label}")
    resp = c.send(command)
    print(f"  <= {json.dumps(resp)[:200]}")
    return resp


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


# ---- record the main mod BEFORE anything -------------------------------------
main_pack_md5_before = md5(MAIN_PACK) if os.path.exists(MAIN_PACK) else "<absent>"
main_src_md5_before = md5(MAIN_SRC)
print("== main mod (must stay byte-identical) ==")
print(f"   data/zz_test_deadly_onslaught.pack md5 BEFORE : {main_pack_md5_before}")
print(f"   script source        md5 BEFORE : {main_src_md5_before}")

hashes = {}
for _src, _in_pack in FILES:
    _data = open(_src, "rb").read()
    hashes[_in_pack] = (len(_data), hashlib.sha256(_data).hexdigest())
    print(f"\nsource {_src.split('/')[-1]:32s} {len(_data):>7d} bytes  "
          f"sha256 {hashes[_in_pack][1][:32]}")

# remove stale build artifacts
for p in (OUT_PACK, GAME_PACK):
    if os.path.exists(p):
        os.remove(p)
        print("removed stale:", p)

c = Client(WS_URL)
step("1 select game", {"SetGameSelected": ["warhammer_3", False]})
key = step("2 new pack", "NewPack")["String"]
step("3 add the one probe script",
     {"AddPackedFiles": [key, [f[0] for f in FILES], [{"File": f[1]} for f in FILES], None]})
step("4 type = Movie", {"SetPackFileType": [key, "Movie"]})

info = step("5 list contents", {"GetPackFileDataForTreeView": key})
container, files = info["ContainerInfoVecRFileInfo"]
in_pack_paths = sorted(f["path"] for f in files)
expected = sorted(_in_pack for _src, _in_pack in FILES)
print("   container:", container["pfh_file_type"], "| files:", in_pack_paths)
assert in_pack_paths == expected, f"pack contents wrong: {in_pack_paths} != {expected}"
assert not any("zz_test_deadly_onslaught" in p for p in in_pack_paths), \
    "the MAIN mod leaked into the probe pack"

ok_all = True
for _src, in_pack in FILES:
    raw = c.send({"GetPackedFileRawData": [key, in_pack]})
    packed = bytes(raw["VecU8"])
    got = hashlib.sha256(packed).hexdigest()
    want_len, want = hashes[in_pack]
    ok = (got == want and len(packed) == want_len)
    ok_all = ok_all and ok
    print(f"   {in_pack:48s} {len(packed):>7d} bytes  MATCHES SOURCE: {ok}")
assert ok_all, "content mismatch - refusing to install"

# what we shipped must be the probe (spot-check tokens unique to it)
probe_txt = open(PROBE_SRC, "rb").read().decode("utf-8", "replace")
packed_txt = bytes(c.send({"GetPackedFileRawData": [key, PROBE_IN_PACK]})["VecU8"]).decode("utf-8", "replace")
print("\n== 6 the pack must contain the probe (token checks)")
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
            "SELF route=", "EFF route=", "RESULT route=", "landed=", "in_range=",
            "COOLDOWN ", "NOT CALLED (write-shaped)",
            "ActiveEffectList(true).Size", "conflict=", "accepted="):
    print(f"   {tok:52s} present: {tok in packed_txt}")
    assert tok in packed_txt, f"missing probe token: {tok}"
# all six ROUTE LABELS must be in the shipped probe
for label in ("bench_fresh", "queued_q", "army_use",
              "take_control", "attack_then_cast", "in_range_cast"):
    assert f'"{label}"' in packed_txt, f"route label {label} missing"
# nothing but the probe's own calls writes state. The ONLY order-family calls the
# probe may make are the three routes' legitimate orders.
for forbidden in ("select_in_ui(", "SetContextObject(",
                  "reset_ability_cooldown(", "reset_ability_number_of_uses(",
                  "kill_number_of_men(", "heal_hitpoints_unary(",
                  "reduce_hitpoints_unary(", "teleport_to_location(",
                  "morale_behavior_rout(", "set_invincible(",
                  "deploy_reinforcement(", "goto_location(", "kill_proportion("):
    assert forbidden not in packed_txt, f"a write snuck into the probe: {forbidden}"
for order in ("attack_unit", "take_control", "release_control"):
    assert f"uc:{order}" in packed_txt or f":{order}(" in packed_txt, f"order call missing: {order}"

step("7 save to disk", {"SavePackAs": [key, OUT_PACK]})
step("8 close", {"ClosePack": key})
try:
    c.send("ClientDisconnecting")
except Exception:
    pass  # the server shuts down as soon as the last session leaves

# ---- install + verify the main mod is untouched ------------------------------
print("\n================ INSTALL ================")
shutil.copy2(OUT_PACK, GAME_PACK)
a = md5(OUT_PACK)
b = md5(GAME_PACK)
print(f"built probe pack    md5 {a}")
print(f"installed           md5 {b}")
print(f"IDENTICAL           {a == b}")
print(f"installed to        {GAME_PACK}")

main_pack_md5_after = md5(MAIN_PACK)
main_src_md5_after = md5(MAIN_SRC)
print("\n== main mod AFTER ==")
print(f"   data/zz_test_deadly_onslaught.pack md5 AFTER  : {main_pack_md5_after}")
print(f"   script source        md5 AFTER  : {main_src_md5_after}")
print(f"   main PACK unchanged : {main_pack_md5_before == main_pack_md5_after}")
print(f"   main SOURCE unchanged : {main_src_md5_before == main_src_md5_after}")
assert main_pack_md5_before == main_pack_md5_after, "the main mod PACK changed!"
assert main_src_md5_before == main_src_md5_after, "the main mod SOURCE changed!"

print("\nPROBE BUILD+INSTALL OK")
