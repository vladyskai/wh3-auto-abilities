"""Build the THROWAWAY step-probe pack zz_probe_step.pack, verify it, install it.

One WebSocket session (RPFM headless backend on ws://127.0.0.1:45127/ws).

Pack contents (exactly ONE file - the probe is self-contained):
  script/battle/mod/zz_probe_step.lua

It is a SEPARATE Movie pack from the main mod. The main mod's pack and source
are NOT touched; their md5s are recorded before and after and asserted equal.

Also rotates any prior zz_probe_step_log.txt (next to Warhammer3.exe) out of the
way so the new run writes a clean file.
"""
import hashlib
import json
import os
import shutil

from websockets.sync.client import connect

WS_URL = "ws://127.0.0.1:45127/ws"
SRC_ROOT = r"C:/Users/vlady/Desktop/WH3_mod/mod_source"

PROBE_SRC = SRC_ROOT + "/script/battle/mod/zz_probe_step.lua"
PROBE_IN_PACK = "script/battle/mod/zz_probe_step.lua"

OUT_PACK = SRC_ROOT + "/dist/zz_probe_step.pack"
GAME_ROOT = r"C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III"
GAME_DATA = GAME_ROOT + "/data"
GAME_PACK = GAME_DATA + "/zz_probe_step.pack"
PROBE_LOG = GAME_ROOT + "/zz_probe_step_log.txt"

MAIN_PACK = GAME_DATA + "/zz_test_deadly_onslaught.pack"
MAIN_SRC = SRC_ROOT + "/script/battle/mod/zz_test_deadly_onslaught.lua"

FILES = [(PROBE_SRC, PROBE_IN_PACK)]

# tokens that MUST be in the shipped probe (the record shape the round needs)
TOKENS = (
    "zz_probe_step_status",
    "get_scriptunits_for_local_players_army",
    "get_scriptunits_for_main_enemy_army_to_local_player",
    "get_first_non_player_army",
    "perform_special_ability",
    "register_command_handler_callback",
    # item a
    "BEFORE cast=", "unit_distance=", "caster_in_melee=", "target_in_melee=",
    "target_under_missile=", "READ ", " => ", "NOT CALLED (write-shaped)",
    "ordered_position", "is_moving", "is_moving_fast", "is_idle", "current_target",
    "has_moved", "slow_speed", "fast_speed",
    # item b
    "CMD tick=", "name=", "bool1=", "str1=",
    # item c
    "CAST-PLAN cast=", "TRY cast=", "ACCEPTED cast=", "POSTPOS cast=",
    # item d/e/f
    "SAMPLING cast=", "SAMPLE cast=", "delta_from_pre=", "step_delta=",
    "STEP RESULT cast=", "orders_seen=", "REFUSED cast=",
    "VERDICT cast=", "moved_total=", "order_after_attack=", "order_after_move=",
    "already_moving_before=", "refused=",
    # gate
    "GATE conflict phase ENTERED", "conflict=", "phase=",
)
# armed keys the probe must know (self-arming, no main-mod badge)
ARMED_KEYS = (
    "wh_main_hero_abilities_accusation",
    "wh2_main_character_abilities_assassins_trophy",
    "wh3_dlc29_hero_active_amulet_of_pha_stah",
)
# command event types the probe must register (spot-check the full family)
CMD_TYPES = (
    "Attack Unit", "Move", "Move Orientation Width", "Move Rotation Angle",
    "Change Speed", "Special Ability", "Halt", "Withdraw",
    "Double Click Unit Card", "Unit Left Battlefield", "Battle Results",
)
# anything write-shaped is BANNED from the probe (zero writes beyond the casts)
FORBIDDEN = (
    "select_in_ui(", "SetContextObject(", "reset_ability_cooldown(",
    "reset_ability_number_of_uses(", "kill_number_of_men(", "heal_hitpoints_unary(",
    "reduce_hitpoints_unary(", "teleport_to_location(", "morale_behavior_rout(",
    "set_invincible(", "deploy_reinforcement(", "goto_location(", "kill_proportion(",
    "attack_unit(", "take_control(", "release_control(", "set_special_abilities_flags(",
    "set_current_ammo_unary(", "disable_special_ability(",
)


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

# ---- rotate any prior step-probe log out of the way -------------------------
if os.path.exists(PROBE_LOG):
    rotated = PROBE_LOG.replace(".txt", ".prev.txt")
    n = 0
    while os.path.exists(rotated):
        n += 1
        rotated = PROBE_LOG.replace(".txt", f".prev{n}.txt")
    shutil.move(PROBE_LOG, rotated)
    print(f"\n== rotated prior probe log -> {rotated}")
else:
    print("\n== no prior zz_probe_step_log.txt (clean start)")

hashes = {}
for _src, _in_pack in FILES:
    _data = open(_src, "rb").read()
    assert _data.count(b"\r") == 0, "probe source has CR bytes - must be LF"
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

# what we shipped must be the probe
packed_txt = bytes(c.send({"GetPackedFileRawData": [key, PROBE_IN_PACK]})["VecU8"]).decode("utf-8", "replace")
print("\n== 6 the pack must contain the step probe (token checks)")
for tok in TOKENS:
    print(f"   {tok:52s} present: {tok in packed_txt}")
    assert tok in packed_txt, f"missing probe token: {tok}"
for k in ARMED_KEYS:
    assert f'"{k}"' in packed_txt, f"armed key missing: {k}"
for t in CMD_TYPES:
    assert f'"{t}"' in packed_txt, f"command event type missing: {t}"
for forbidden in FORBIDDEN:
    assert forbidden not in packed_txt, f"a write snuck into the probe: {forbidden}"
# the ONLY engine-state call the probe makes is the ability cast
assert packed_txt.count("perform_special_ability(") >= 1, "the cast call is missing"
assert "perform_special_ability_ground(" not in packed_txt, "an unexpected ground-cast call"

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
