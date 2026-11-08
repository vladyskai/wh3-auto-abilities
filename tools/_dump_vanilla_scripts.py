"""Extract data_script.pack (vanilla battle+frontend lua) for API verification."""
import json, os
from websockets.sync.client import connect

WS = "ws://127.0.0.1:45127/ws"
PACK = "C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III/data/data_script.pack"
DEST = "C:/Users/vlady/Desktop/WH3_mod/archive/vanilla_script"

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
files = c.send({"GetPackFileDataForTreeView": key})["ContainerInfoVecRFileInfo"][1]
paths = [f["path"] for f in files if f["path"].endswith(".lua")]
print("lua files:", len(paths))
os.makedirs(DEST, exist_ok=True)
r = c.send({"ExtractPackedFiles": [key, {"PackFile": [{"File": p} for p in paths]}, DEST, True]})
print("status:", r["StringVecPathBuf"][0], len(r["StringVecPathBuf"][1]))
try:
    c.send("ClientDisconnecting")
except Exception:
    pass
