"""Verify the built pack: open it from disk, list it, and compare the stored
bytes byte-for-byte against the source Lua file."""
import hashlib
import json
from websockets.sync.client import connect

WS_URL = "ws://127.0.0.1:45127/ws"
SRC = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"
PACK = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/dist/zz_test_deadly_onslaught.pack"
IN_PACK = "script/battle/mod/zz_test_deadly_onslaught.lua"


class Client:
    def __init__(self, url):
        self.ws = connect(url, max_size=None, open_timeout=15)
        self.next_id = 1
        hello = json.loads(self.ws.recv(timeout=15))
        print("  hello:", json.dumps(hello))

    def send(self, command):
        req_id = self.next_id
        self.next_id += 1
        self.ws.send(json.dumps({"id": req_id, "data": command}))
        while True:
            msg = json.loads(self.ws.recv(timeout=180))
            if msg.get("id") == req_id:
                return msg.get("data")
            print("  (unsolicited)", json.dumps(msg)[:160])


c = Client(WS_URL)

print("\n== open the pack we just wrote")
resp = c.send({"OpenPackFiles": [PACK]})
print("  <=", json.dumps(resp)[:400])
key = resp["StringContainerInfo"][0]
print("  ** pack key =", key)

print("\n== container info + file list")
resp = c.send({"GetPackFileDataForTreeView": key})
info, files = resp["ContainerInfoVecRFileInfo"]
print("  container:", json.dumps(info))
print("  file count:", len(files))
for f in files:
    print("   -", json.dumps(f))

print("\n== byte-for-byte content check")
resp = c.send({"GetPackedFileRawData": [key, IN_PACK]})
data = bytes(resp["VecU8"])
src = open(SRC, "rb").read()
print("  bytes in pack :", len(data), hashlib.sha256(data).hexdigest()[:32])
print("  bytes on disk :", len(src), hashlib.sha256(src).hexdigest()[:32])
print("  IDENTICAL     :", data == src)

c.send("ClientDisconnecting")
c.ws.close()
print("\nDONE")
