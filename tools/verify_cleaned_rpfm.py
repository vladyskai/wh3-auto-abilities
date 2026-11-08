"""RPFM-side independent verification of the CLEANED installed pack.

Fresh session (server restarted after the build disconnected). Opens the pack
FROM THE GAME FOLDER, lists it, byte-compares each file against source, and
extracts everything to a scratch dir for a filesystem-level double-check.
"""
import hashlib
import json
import os
import shutil
from websockets.sync.client import connect

WS_URL = "ws://127.0.0.1:45127/ws"
GAME_PACK = r"C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III/data/zz_test_deadly_onslaught.pack"
SRC_ROOT = r"C:/Users/vlady/Desktop/WH3_mod/mod_source"
DEST = r"C:/Users/vlady/AppData/Local/Temp/wh3_housekeeping/extracted_cleaned"

EXPECTED = {
    "script/battle/mod/zz_test_deadly_onslaught.lua":
        SRC_ROOT + "/script/battle/mod/zz_test_deadly_onslaught.lua",
    "ui/common ui/special_ability_tooltip.twui.xml":
        SRC_ROOT + "/ui/common ui/special_ability_tooltip.twui.xml",
    "ui/templates/zz_auto_badge.twui.xml":
        SRC_ROOT + "/ui/templates/zz_auto_badge.twui.xml",
    "ui/zz_auto/auto_badge.png": SRC_ROOT + "/ui/zz_auto/auto_badge.png",
    "ui/zz_auto/blank.png": SRC_ROOT + "/ui/zz_auto/blank.png",
}


class Client:
    def __init__(self, url):
        self.ws = connect(url, max_size=None, open_timeout=20)
        self.next_id = 1
        self.ws.recv(timeout=20)  # hello

    def send(self, command):
        rid = self.next_id
        self.next_id += 1
        self.ws.send(json.dumps({"id": rid, "data": command}))
        while True:
            msg = json.loads(self.ws.recv(timeout=300))
            if msg.get("id") == rid:
                return msg.get("data")


c = Client(WS_URL)
c.send({"SetGameSelected": ["warhammer_3", False]})
resp = c.send({"OpenPackFiles": [GAME_PACK]})
key, container = resp["StringContainerInfo"]
print("opened installed pack; type:", container.get("pfh_file_type"),
      "version:", container.get("pfh_version"))

info = c.send({"GetPackFileDataForTreeView": key})
_, files = info["ContainerInfoVecRFileInfo"]
paths = sorted(f["path"] for f in files)
print(f"\n=== {len(paths)} file(s) in the INSTALLED pack (tree view) ===")
for p in paths:
    print("   -", p)
exp = sorted(EXPECTED)
print("\ntree list == expected 5: ", paths == exp)
print("no zz_probe path present:", not any("zz_probe" in p for p in paths))
assert paths == exp, f"{paths} != {exp}"

print("\nbyte-for-byte vs source:")
all_ok = True
for rel, src_path in EXPECTED.items():
    raw = bytes(c.send({"GetPackedFileRawData": [key, rel]})["VecU8"])
    src = open(src_path, "rb").read()
    ok = raw == src
    all_ok = all_ok and ok
    print(f"  {rel}")
    print(f"    pack {len(raw):>7d} sha256 {hashlib.sha256(raw).hexdigest()[:32]}  ==  "
          f"source {len(src):>7d} sha256 {hashlib.sha256(src).hexdigest()[:32]}  ->  {ok}")
assert all_ok, "content mismatch in reopen check"

print("\nextracting all files to", DEST)
if os.path.exists(DEST):
    shutil.rmtree(DEST)
os.makedirs(DEST)
resp = c.send({"ExtractPackedFiles": [
    key,
    {"PackFile": [{"File": p} for p in paths]},
    DEST,
    True,
]})
print("extract response:", json.dumps(resp)[:300])

try:
    c.send("ClientDisconnecting")
except Exception:
    pass
print("\nRPFM reopen+extract: OK")
