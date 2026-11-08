"""Extract the vanilla battle-AI ability-usage tables from data.pack for diffing."""
import json, os, sys
from websockets.sync.client import connect

WS = "ws://127.0.0.1:45127/ws"
PACK = "C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III/data/db.pack"
DEST = "C:/Users/vlady/Desktop/WH3_mod/archive/hecleas_vanilla2"
WANT = ("unit_special_abilities_tables",)

class C:
    def __init__(self, url):
        self.ws = connect(url, max_size=None, open_timeout=30)
        self.n = 1
        json.loads(self.ws.recv(timeout=30))
    def send(self, cmd):
        i = self.n; self.n += 1
        self.ws.send(json.dumps({"id": i, "data": cmd}))
        while True:
            m = json.loads(self.ws.recv(timeout=600))
            if m.get("id") == i:
                return m.get("data")

c = C(WS)
c.send({"SetGameSelected": ["warhammer_3", False]})
key, _ = c.send({"OpenPackFiles": [PACK]})["StringContainerInfo"]
info = c.send({"GetPackFileDataForTreeView": key})
files = info["ContainerInfoVecRFileInfo"][1]
paths = [f["path"] for f in files]
print("total files in data.pack:", len(paths))
sel = [p for p in paths if any(w in p for w in WANT)]
print("selected:", len(sel))
for p in sorted(sel):
    print("   ", p)
os.makedirs(DEST, exist_ok=True)
r = c.send({"ExtractPackedFiles": [key, {"PackFile": [{"File": p} for p in sel]}, DEST, True]})
print("extract:", json.dumps(r)[:300])
try:
    c.send("ClientDisconnecting")
except Exception:
    pass
