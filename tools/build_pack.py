"""Drive rpfm_server over its WebSocket API to build a Movie pack.

Protocol: {'id': N, 'data': <command>}  ->  {'id': N, 'data': <response>}
Docs: https://github.com/Frodo45127/rpfm/tree/master/docs/server
"""
import json
import sys
from websockets.sync.client import connect

WS_URL = "ws://127.0.0.1:45127/ws"

SRC_LUA = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"
IN_PACK = "script/battle/mod/zz_test_deadly_onslaught.lua"
OUT_PACK = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/dist/zz_test_deadly_onslaught.pack"


class Client:
    def __init__(self, url):
        self.ws = connect(url, max_size=None, open_timeout=15)
        self.next_id = 1
        # unsolicited SessionConnected arrives first
        hello = json.loads(self.ws.recv(timeout=15))
        print(f"  <= hello: {json.dumps(hello)[:200]}")
        self.session = hello.get("data", {}).get("SessionConnected")

    def send(self, command, tries=4):
        for attempt in range(tries):
            req_id = self.next_id
            self.next_id += 1
            self.ws.send(json.dumps({"id": req_id, "data": command}))
            while True:
                raw = self.ws.recv(timeout=120)
                msg = json.loads(raw)
                if msg.get("id") == req_id:
                    return msg.get("data")
                # anything else is server chatter; show and keep waiting
                print(f"  <= (unsolicited) {json.dumps(msg)[:200]}")
        raise RuntimeError(f"no response for {command!r}")

    def close(self):
        try:
            self.send("ClientDisconnecting")
        except Exception:
            pass
        self.ws.close()


def step(label, command):
    print(f"\n== {label}")
    print(f"  => {json.dumps(command)[:260]}")
    resp = c.send(command)
    print(f"  <= {json.dumps(resp)[:400]}")
    return resp


c = Client(WS_URL)
print(f"connected (session {c.session} connected)")

# 1. tell the server which game we are working on
step("select game", {"SetGameSelected": ["warhammer_3", False]})

# 2. empty pack in memory
resp = step("new pack", "NewPack")
pack_key = resp["String"]
print(f"  ** pack key = {pack_key}")

# 3. add our Lua file from disk at the path the game's loader scans
step("add file", {"AddPackedFiles": [pack_key, [SRC_LUA], [{"File": IN_PACK}], None]})

# 4. "Movie" = always loaded from data/, no mod-manager tick required
step("set type", {"SetPackFileType": [pack_key, "Movie"]})

# 5. what is actually inside the pack now?
step("list contents", {"GetPackedFilesInfo": [pack_key, None]})

# 6. write it to disk
step("save as", {"SavePackAs": [pack_key, OUT_PACK]})

step("close", {"ClosePack": pack_key})

c.close()
print("\nDONE")
