"""Independent verification of the INSTALLED pack: reopen it with a fresh RPFM
server session and byte-compare every one of the five shipped files to source."""
import hashlib
import json
import os
from websockets.sync.client import connect

WS = "ws://127.0.0.1:45127/ws"
SRC = r"C:/Users/vlady/Desktop/WH3_mod/mod_source"
INSTALLED = r"C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III/data/zz_test_deadly_onslaught.pack"

FILES = [
    (SRC + "/script/battle/mod/zz_test_deadly_onslaught.lua", "script/battle/mod/zz_test_deadly_onslaught.lua"),
    (SRC + "/ui/templates/zz_auto_badge.twui.xml", "ui/templates/zz_auto_badge.twui.xml"),
    (SRC + "/ui/zz_auto/blank.png", "ui/zz_auto/blank.png"),
    (SRC + "/ui/zz_auto/auto_badge.png", "ui/zz_auto/auto_badge.png"),
    (SRC + "/ui/common ui/special_ability_tooltip.twui.xml", "ui/common ui/special_ability_tooltip.twui.xml"),
]

next_id = [1]
ws = connect(WS, max_size=None, open_timeout=15)


def send(cmd):
    rid = next_id[0]
    next_id[0] += 1
    ws.send(json.dumps({"id": rid, "data": cmd}))
    while True:
        msg = json.loads(ws.recv(timeout=180))
        if msg.get("id") == rid:
            return msg.get("data")


print("hello:", json.dumps(send({"SetGameSelected": ["warhammer_3", False]}))[:80])
key = send({"OpenPackFiles": [INSTALLED]})
print("open:", json.dumps(key)[:120])
key = key["StringContainerInfo"][0]
info = send({"GetPackFileDataForTreeView": key})
container, files = info["ContainerInfoVecRFileInfo"]
print("container:", container["pfh_file_type"], "| files:", len(files))
ok_all = True
for src, in_pack in FILES:
    raw = bytes(send({"GetPackedFileRawData": [key, in_pack]})["VecU8"])
    srcb = open(src, "rb").read()
    same = raw == srcb
    ok_all = ok_all and same
    print("%-52s %8d bytes  sha256 %s  IDENTICAL=%s" % (in_pack.split("/")[-1], len(raw),
                                                       hashlib.sha256(raw).hexdigest()[:16], same))
send({"ClosePack": key})
try:
    send({"ClientDisconnecting": []})
except Exception:
    pass
print("ALL FIVE BYTE-IDENTICAL TO SOURCE:", ok_all)
print("installed md5:", hashlib.md5(open(INSTALLED, "rb").read()).hexdigest())
