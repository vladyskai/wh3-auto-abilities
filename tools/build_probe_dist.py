"""Build the PASSIVE OBSERVER pack zz_probe_dist.pack, verify it, install it.

One WebSocket session (RPFM headless backend on ws://127.0.0.1:45127/ws).

Pack contents (exactly ONE file - the observer is self-contained):
  script/battle/mod/zz_probe_dist.lua

It is a SEPARATE Movie pack from the main mod. The main mod's pack and source
are NOT touched; their md5s are recorded before and after and asserted equal.

This script ALSO, before building:
  * DELETES the previous step-probe pack from the game's data/ folder
    (data/zz_probe_step.pack) and VERIFIES the deletion, so it cannot interfere.
  * ROTATES the previous step-probe log out of the way
    (zz_probe_step_log.txt -> zz_probe_step_log_run1.txt) and verifies it moved.
  * ROTATES any prior zz_probe_dist_log.txt so the new run writes a clean file.
"""
import hashlib
import json
import os
import shutil

from websockets.sync.client import connect

WS_URL = "ws://127.0.0.1:45127/ws"
SRC_ROOT = r"C:/Users/vlady/Desktop/WH3_mod/mod_source"

PROBE_SRC = SRC_ROOT + "/script/battle/mod/zz_probe_dist.lua"
PROBE_IN_PACK = "script/battle/mod/zz_probe_dist.lua"

OUT_PACK = SRC_ROOT + "/dist/zz_probe_dist.pack"
GAME_ROOT = r"C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III"
GAME_DATA = GAME_ROOT + "/data"
GAME_PACK = GAME_DATA + "/zz_probe_dist.pack"
PROBE_LOG = GAME_ROOT + "/zz_probe_dist_log.txt"

MAIN_PACK = GAME_DATA + "/zz_test_deadly_onslaught.pack"
MAIN_SRC = SRC_ROOT + "/script/battle/mod/zz_test_deadly_onslaught.lua"

# the previous step-probe (to delete + rotate out of the way)
STEP_PACK = GAME_DATA + "/zz_probe_step.pack"
STEP_LOG = GAME_ROOT + "/zz_probe_step_log.txt"
STEP_LOG_RUN1 = GAME_ROOT + "/zz_probe_step_log_run1.txt"

FILES = [(PROBE_SRC, PROBE_IN_PACK)]

# tokens that MUST be in the shipped observer (the record shape the round needs)
TOKENS = (
    "zz_probe_dist_status",
    "get_scriptunits_for_local_players_army",
    "get_scriptunits_for_main_enemy_army_to_local_player",
    "unit_distance",
    "unit_in_range",
    # item (0) owner
    "OWNER chosen:", "key=",
    # item (a) OBS
    "OBS tick=", "caster_pos=", "caster_moved_since_last=",
    "caster_is_moving=", "caster_is_idle=",
    # item (b) CAND
    "CAND tick=", "idx=", "in_melee=", "under_fire=",
    "engine_unit_in_range=", "our_52_test=", "our_75_test=",
    # item (c) CAND-FIRST
    "CAND-FIRST tick=", "first_passing_test=", "mode=first",
    # item (d) CANPERF
    "CANPERF tick=", "can=",
    # gate + cap
    "GATE conflict phase ENTERED", "phase=", "conflict=", "probe finished (poll cap",
)
# the observed ability key must be a quoted literal
KEY_LITERAL = '"wh_main_hero_abilities_accusation"'

# anything write-shaped is BANNED from the observer (zero writes, zero casts).
FORBIDDEN = (
    ":perform_special_ability(", ":perform_special_ability_ground(",
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

# ---- DELETE the previous step-probe from the game's data folder --------------
print("\n================ RETIRE THE PREVIOUS STEP-PROBE ================")
print(f"   step-probe pack present BEFORE delete : {os.path.exists(STEP_PACK)}  ({STEP_PACK})")
if os.path.exists(STEP_PACK):
    os.remove(STEP_PACK)
    print("   deleted zz_probe_step.pack from the game's data/ folder")
step_pack_gone = not os.path.exists(STEP_PACK)
print(f"   step-probe pack present AFTER  delete : {not step_pack_gone}  -> deleted verified: {step_pack_gone}")
assert step_pack_gone, "the step-probe pack is still in the game's data folder!"

print(f"   step-probe log present BEFORE rotate : {os.path.exists(STEP_LOG)}  ({STEP_LOG})")
if os.path.exists(STEP_LOG):
    if os.path.exists(STEP_LOG_RUN1):
        os.remove(STEP_LOG_RUN1)
    shutil.move(STEP_LOG, STEP_LOG_RUN1)
    print(f"   rotated step-probe log -> {STEP_LOG_RUN1}")
step_log_moved = (not os.path.exists(STEP_LOG)) and os.path.exists(STEP_LOG_RUN1)
print(f"   step-probe log at old path AFTER rotate : {os.path.exists(STEP_LOG)}  -> moved verified: {step_log_moved}")
assert not os.path.exists(STEP_LOG), "the step-probe log is still at its old path!"

# ---- rotate any prior dist-probe log out of the way --------------------------
if os.path.exists(PROBE_LOG):
    rotated = PROBE_LOG.replace(".txt", ".prev.txt")
    n = 0
    while os.path.exists(rotated):
        n += 1
        rotated = PROBE_LOG.replace(".txt", f".prev{n}.txt")
    shutil.move(PROBE_LOG, rotated)
    print(f"\n== rotated prior dist-probe log -> {rotated}")
else:
    print("\n== no prior zz_probe_dist_log.txt (clean start)")

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
step("3 add the one observer script",
     {"AddPackedFiles": [key, [f[0] for f in FILES], [{"File": f[1]} for f in FILES], None]})
step("4 type = Movie", {"SetPackFileType": [key, "Movie"]})

info = step("5 list contents", {"GetPackFileDataForTreeView": key})
container, files = info["ContainerInfoVecRFileInfo"]
in_pack_paths = sorted(f["path"] for f in files)
expected = sorted(_in_pack for _src, _in_pack in FILES)
print("   container:", container["pfh_file_type"], "| files:", in_pack_paths)
assert in_pack_paths == expected, f"pack contents wrong: {in_pack_paths} != {expected}"
assert not any("zz_test_deadly_onslaught" in p for p in in_pack_paths), \
    "the MAIN mod leaked into the observer pack"

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

# what we shipped must be the observer
packed_txt = bytes(c.send({"GetPackedFileRawData": [key, PROBE_IN_PACK]})["VecU8"]).decode("utf-8", "replace")
print("\n== 6 the pack must contain the distance observer (token checks)")
for tok in TOKENS:
    print(f"   {tok:52s} present: {tok in packed_txt}")
    assert tok in packed_txt, f"missing probe token: {tok}"
assert KEY_LITERAL in packed_txt, "the observed ability key literal is missing"
for forbidden in FORBIDDEN:
    assert forbidden not in packed_txt, f"a write snuck into the observer: {forbidden}"
# the observer must NEVER cast: no ability-cast call at all
assert ":perform_special_ability(" not in packed_txt, "the observer contains a cast call!"
assert ":perform_special_ability_ground(" not in packed_txt, "the observer contains a ground-cast call!"
assert "can_perform_special_ability(" in packed_txt, "the CANPERF corroboration read is missing"

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
print(f"built observer pack  md5 {a}")
print(f"installed            md5 {b}")
print(f"IDENTICAL            {a == b}")
print(f"installed to         {GAME_PACK}")
assert a == b, "installed pack differs from the built pack!"

main_pack_md5_after = md5(MAIN_PACK)
main_src_md5_after = md5(MAIN_SRC)
print("\n== main mod AFTER ==")
print(f"   data/zz_test_deadly_onslaught.pack md5 AFTER  : {main_pack_md5_after}")
print(f"   script source        md5 AFTER  : {main_src_md5_after}")
print(f"   main PACK unchanged : {main_pack_md5_before == main_pack_md5_after}")
print(f"   main SOURCE unchanged : {main_src_md5_before == main_src_md5_after}")
assert main_pack_md5_before == main_pack_md5_after, "the main mod PACK changed!"
assert main_src_md5_before == main_src_md5_after, "the main mod SOURCE changed!"

print("\n================ RETIREMENT SUMMARY ================")
print(f"   step-probe pack deleted        : {step_pack_gone}  ({STEP_PACK})")
print(f"   step-probe log rotated         : {step_log_moved}  -> {STEP_LOG_RUN1}")

print("\nPROBE BUILD+INSTALL OK")
print(f"PROBE_PACK_MD5={a}")
print(f"MAIN_PACK_MD5_BEFORE={main_pack_md5_before}")
print(f"MAIN_PACK_MD5_AFTER={main_pack_md5_after}")
