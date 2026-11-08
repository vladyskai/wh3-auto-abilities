"""Verify the INSTALLED pack on disk contains the UI-text probe, byte-identical
to source. Independent of the build session (opens the file from disk)."""
import hashlib
import json
from websockets.sync.client import connect

WS_URL = "ws://127.0.0.1:45127/ws"
GAME_PACK = r"C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III/data/zz_test_deadly_onslaught.pack"
SRC = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_ui_text.lua"
IN_PACK = "script/battle/mod/zz_probe_ui_text.lua"


class Client:
    def __init__(self, url):
        self.ws = connect(url, max_size=None, open_timeout=20)
        self.next_id = 1
        self.ws.recv(timeout=20)

    def send(self, command):
        rid = self.next_id
        self.next_id += 1
        self.ws.send(json.dumps({"id": rid, "data": command}))
        while True:
            msg = json.loads(self.ws.recv(timeout=180))
            if msg.get("id") == rid:
                return msg.get("data")


c = Client(WS_URL)
c.send({"SetGameSelected": ["warhammer_3", False]})
resp = c.send({"OpenPackFiles": [GAME_PACK]})
key, container = resp["StringContainerInfo"]
print("opened installed pack:", container.get("pfh_file_type"))

info = c.send({"GetPackFileDataForTreeView": key})
_, files = info["ContainerInfoVecRFileInfo"]
paths = sorted(f["path"] for f in files)
print(f"\n=== {len(paths)} file(s) in the INSTALLED pack ===")
for p in paths:
    print("   -", p)

raw = bytes(c.send({"GetPackedFileRawData": [key, IN_PACK]})["VecU8"])
src = open(SRC, "rb").read()
print("\nUI probe present in installed pack :", IN_PACK in paths)
print("UI probe byte-identical to source  :", raw == src)
print("UI probe sha256 (source)           :", hashlib.sha256(src).hexdigest())
print("pack md5 (identifier)              :", hashlib.md5(open(GAME_PACK, "rb").read()).hexdigest())

try:
    c.send("ClientDisconnecting")
except Exception:
    pass
