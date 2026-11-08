"""Probe a game pack with RPFM's headless backend.

Usage:
  python rpfm_probe.py search <pack_path> <pattern>            # which files contain it
  python rpfm_probe.py extract <pack_path> <dest> <path...>    # pull files out
  python rpfm_probe.py find <pack_path> <substring>            # list packed paths containing it

One WebSocket session per run; rpfm_server exits when the last session leaves.
"""
import json
import os
import sys

from websockets.sync.client import connect

WS_URL = "ws://127.0.0.1:45127/ws"


class Client:
    def __init__(self, url=WS_URL):
        self.ws = connect(url, max_size=None, open_timeout=20)
        self.next_id = 1
        self.ws.recv(timeout=20)          # hello

    def send(self, command):
        req_id = self.next_id
        self.next_id += 1
        self.ws.send(json.dumps({"id": req_id, "data": command}))
        while True:
            msg = json.loads(self.ws.recv(timeout=300))
            if msg.get("id") == req_id:
                return msg.get("data")
            print("  (unsolicited)", json.dumps(msg)[:150])


def open_pack(c, path):
    resp = c.send({"OpenPackFiles": [path]})
    key, container = resp["StringContainerInfo"]
    print(f"opened: {key}  (type {container.get('pfh_file_type')}, "
          f"{container.get('pfh_files_contained')} files)")
    return key


def main():
    mode = sys.argv[1]
    pack = sys.argv[2]
    c = Client()
    key = open_pack(c, pack)

    if mode == "search":
        pattern = sys.argv[3]
        # SearchOn requires EVERY file-type flag (it is not a partial struct).
        on = {k: False for k in (
            "anim", "anim_fragment_battle", "anim_pack", "anims_table", "atlas", "audio",
            "bmd", "esf", "group_formations", "image", "matched_combat", "pack",
            "portrait_settings", "rigid_model", "sound_bank", "uic", "unit_variant",
            "unknown", "video", "schema")}
        on.update({"db": True, "loc": True, "text": True})
        matches = {k: [] for k in (
            "anim", "anim_fragment_battle", "anim_pack", "anims_table", "atlas", "audio",
            "bmd", "db", "esf", "group_formations", "image", "loc", "matched_combat",
            "pack", "portrait_settings", "rigid_model", "sound_bank", "text", "uic",
            "unit_variant", "unknown", "video")}
        matches["schema"] = {}
        resp = c.send({"GlobalSearch": [key, {
            "pattern": pattern, "replace_text": "", "case_sensitive": False,
            "use_regex": False, "sources": [{"Pack": key}],
            "search_on": on,
            "matches": matches, "game_key": "warhammer_3"}]})
        _cfg, hits = resp.get("GlobalSearchVecRFileInfo", (None, None)) if isinstance(resp, dict) else (None, None)
        if hits is None:
            print("  raw response:", json.dumps(resp)[:600])
            return
        print(f"\n{len(hits)} file(s) contain {pattern!r}:")
        for h in hits:
            print("   ", h["path"])

    elif mode == "find":
        sub = sys.argv[3].lower()
        resp = c.send({"GetPackFileDataForTreeView": key})
        _c, files = resp["ContainerInfoVecRFileInfo"]
        hits = [f["path"] for f in files if sub in f["path"].lower()]
        print(f"\n{len(hits)} packed path(s) contain {sub!r} (of {len(files)} files):")
        for p in sorted(hits)[:120]:
            print("   ", p)

    elif mode == "extract":
        dest = sys.argv[3]
        paths = sys.argv[4:]
        os.makedirs(dest, exist_ok=True)
        resp = c.send({"ExtractPackedFiles": [key, {"PackFile": [{"File": p} for p in paths]},
                                              dest, False]})
        _d, written = resp["StringVecPathBuf"]
        print(f"\nextracted {len(written)} file(s) to {dest}:")
        for w in written:
            print("   ", w)

    try:
        c.send("ClientDisconnecting")
    except Exception:
        pass


if __name__ == "__main__":
    main()
