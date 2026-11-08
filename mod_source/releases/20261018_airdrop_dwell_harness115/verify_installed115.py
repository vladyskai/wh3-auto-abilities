"""INDEPENDENT post-install verification: open the INSTALLED pack and compare all
five shipped files byte-for-byte with their sources, then report the md5.

This does not trust the build session: it re-opens the file the GAME will load.
"""
import hashlib
import json
import os

from websockets.sync.client import connect

WS = "ws://127.0.0.1:45127/ws"
SRC = r"C:/Users/vlady/Desktop/WH3_mod/mod_source"
GAME_PACK = (r"C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III"
             r"/data/zz_test_deadly_onslaught.pack")
FILES = [
    (SRC + "/script/battle/mod/zz_test_deadly_onslaught.lua",
     "script/battle/mod/zz_test_deadly_onslaught.lua"),
    (SRC + "/ui/templates/zz_auto_badge.twui.xml", "ui/templates/zz_auto_badge.twui.xml"),
    (SRC + "/ui/zz_auto/blank.png", "ui/zz_auto/blank.png"),
    (SRC + "/ui/zz_auto/auto_badge.png", "ui/zz_auto/auto_badge.png"),
    (SRC + "/ui/common ui/special_ability_tooltip.twui.xml",
     "ui/common ui/special_ability_tooltip.twui.xml"),
]

ws = connect(WS, max_size=None, open_timeout=15)
nid = 0


def send(cmd):
    global nid
    nid += 1
    ws.send(json.dumps({"id": nid, "data": cmd}))
    while True:
        msg = json.loads(ws.recv(timeout=180))
        if msg.get("id") == nid:
            return msg.get("data")


send({"SetGameSelected": ["warhammer_3", False]})
key = send({"OpenPackFiles": [GAME_PACK]})["StringContainerInfo"][0]
info = send({"GetPackFileDataForTreeView": key})
paths = sorted(f["path"] for f in info["ContainerInfoVecRFileInfo"][1])
print("installed pack:", os.path.basename(GAME_PACK))
print("container type:", info["ContainerInfoVecRFileInfo"][0]["pfh_file_type"])
print("files in pack  :", paths)
ok = True
for src, inp in FILES:
    raw = bytes(send({"GetPackedFileRawData": [key, inp]})["VecU8"])
    here = open(src, "rb").read()
    same = raw == here
    ok = ok and same
    print(f"  {inp:48s} {len(raw):>8d} B  md5 {hashlib.md5(raw).hexdigest()}  IDENTICAL: {same}")
send({"ClosePack": key})
try:
    send("ClientDisconnecting")
except Exception:
    pass
print("ALL FIVE BYTE-IDENTICAL:", ok)
print("installed pack md5     :", hashlib.md5(open(GAME_PACK, "rb").read()).hexdigest())
assert ok
