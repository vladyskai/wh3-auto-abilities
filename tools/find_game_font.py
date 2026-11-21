#!/usr/bin/env python3
"""Find and extract the game's font files (read-only): list paths matching a regex in the base packs, optionally copy
them under gamedata\\wh3_layouts\\ (gitignored, Creative Assembly data). Used to draw the Workshop icon's A in the exact
font the mod's badge uses in game (fontcategories.xml: header_16 = brand_header).

    python find_game_font.py list <regex>
    python find_game_font.py get <pack> <path> ...

Start rpfm_server first. Never writes into the game folder."""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamedata_paths as GP  # noqa: E402
from websockets.sync.client import connect  # noqa: E402

OUT = os.path.join(GP.ROOT, "gamedata", "wh3_layouts")
PACKS = ["boot.pack", "local_en.pack", "ui.pack", "ui2.pack", "ui3.pack", "data.pack", "data_3.pack"]


def main():
    ws = connect("ws://127.0.0.1:45127/ws", max_size=None, open_timeout=20)
    ws.recv(timeout=20)
    n = [0]

    def send(cmd):
        n[0] += 1
        ws.send(json.dumps({"id": n[0], "data": cmd}))
        while True:
            m = json.loads(ws.recv(timeout=900))
            if m.get("id") == n[0]:
                return m.get("data")

    send({"SetGameSelected": ["warhammer_3", False]})
    keys = {}

    def pack(name):
        if name not in keys:
            keys[name] = send({"OpenPackFiles": [GP.GAME_DATA_DIR + "/" + name]})["StringContainerInfo"][0]
        return keys[name]

    try:
        if sys.argv[1] == "list":
            rx = re.compile(sys.argv[2], re.I)
            for name in PACKS:
                tree = send({"GetPackFileDataForTreeView": pack(name)})
                for i in tree["ContainerInfoVecRFileInfo"][1]:
                    if rx.search(i["path"]):
                        print(name, i["path"])
        else:
            name = sys.argv[2]
            for p in sys.argv[3:]:
                data = bytes(send({"GetPackedFileRawData": [pack(name), p]})["VecU8"])
                dest = os.path.join(OUT, *p.split("/"))
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                open(dest, "wb").write(data)
                print("%8d bytes  %s" % (len(data), dest))
    finally:
        try:
            send("ClientDisconnecting")
        except Exception:
            pass


if __name__ == "__main__":
    main()
