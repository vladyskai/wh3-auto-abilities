#!/usr/bin/env python3
"""Extract vanilla UI files (layouts and icons) from the installed game's UI packs into gamedata\\wh3_layouts\\
(gitignored: Creative Assembly data, read-only reference for the mod's own UI).

    python extract_ui_layouts.py list <regex>            # paths in ui.pack/ui2.pack/ui3.pack matching regex
    python extract_ui_layouts.py get <pack> <path> ...   # write the raw bytes under gamedata\\wh3_layouts\\<path>

Start rpfm_server first; one WebSocket session per invocation. Never writes into the game folder.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamedata_paths as GP  # noqa: E402
from websockets.sync.client import connect  # noqa: E402

OUT = os.path.join(GP.ROOT, "gamedata", "wh3_layouts")
PACKS = ["ui.pack", "ui2.pack", "ui3.pack"]


class Client:
    def __init__(self):
        self.ws = connect("ws://127.0.0.1:45127/ws", max_size=None, open_timeout=20)
        self.n = 1
        self.ws.recv(timeout=20)

    def send(self, cmd):
        i = self.n
        self.n += 1
        self.ws.send(json.dumps({"id": i, "data": cmd}))
        while True:
            m = json.loads(self.ws.recv(timeout=600))
            if m.get("id") == i:
                return m.get("data")


def main():
    mode = sys.argv[1]
    c = Client()
    c.send({"SetGameSelected": ["warhammer_3", False]})
    keys = {}

    def pack(name):
        if name not in keys:
            r = c.send({"OpenPackFiles": [GP.GAME_DATA_DIR + "/" + name]})
            keys[name] = r["StringContainerInfo"][0]
        return keys[name]

    try:
        if mode == "list":
            rx = re.compile(sys.argv[2], re.I)
            for name in PACKS:
                tree = c.send({"GetPackFileDataForTreeView": pack(name)})
                for i in tree["ContainerInfoVecRFileInfo"][1]:
                    if rx.search(i["path"]):
                        print(name, i["path"])
        elif mode == "get":
            name = sys.argv[2]
            for p in sys.argv[3:]:
                r = c.send({"GetPackedFileRawData": [pack(name), p]})
                data = bytes(r["VecU8"])
                dest = os.path.join(OUT, *p.split("/"))
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                open(dest, "wb").write(data)
                print("%7d bytes  %s" % (len(data), dest))
    finally:
        try:
            c.send("ClientDisconnecting")
        except Exception:
            pass


if __name__ == "__main__":
    main()
