#!/usr/bin/env python3
"""Read side of the RPFM headless workflow: list, extract and search inside a pack.

    python rpfm_probe.py find    <pack> <substring>        # packed paths containing it
    python rpfm_probe.py extract <pack> <dest_dir> <path>… # pull files out
    python rpfm_probe.py search  <pack> <pattern>          # see the warning below

Start rpfm_server first (it exits when the last WebSocket session disconnects), then run
one command per invocation — one session each, no state kept.

WHY `find` + `extract` IS THE WORKHORSE, NOT `search`:
`GlobalSearch` is rejected by the shipped server with a chain of `missing field` errors
(`anim`, then `matches`) even when the payload carries every field of both `SearchOn` and
`Matches` exactly as the sources define them. Do not sink time into it. `GetPackFileDataForTreeView`
lists paths and never fails, and `ExtractPackedFiles` takes ~200 paths per call, so pulling a
whole set out and grepping locally is both reliable and faster — e.g. all 952 UI layouts out of a
103 MB `ui3.pack` in five calls, after which every layout question is a local grep.

Layouts are stored UNCOMPRESSED in the UI packs, so a raw byte scan of the pack often answers a
"does any layout declare X" question with no RPFM involvement at all:

    grep -a -o 'name="rclick"' <game>/data/ui3.pack | wc -l
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
    print(f"opened: {key}  (type {container.get('pfh_file_type')})")
    return key


def main():
    mode, pack = sys.argv[1], sys.argv[2]
    c = Client()
    key = open_pack(c, pack)

    if mode == "find":
        needle = sys.argv[3].lower()
        resp = c.send({"GetPackFileDataForTreeView": key})
        _c, files = resp["ContainerInfoVecRFileInfo"]
        hits = sorted(f["path"] for f in files if needle in f["path"].lower())
        print(f"\n{len(hits)} packed path(s) contain {needle!r} (of {len(files)} files):")
        for p in hits[:200]:
            print("   ", p)

    elif mode == "extract":
        dest, paths = sys.argv[3], sys.argv[4:]
        os.makedirs(dest, exist_ok=True)
        written = 0
        for i in range(0, len(paths), 200):            # ~200 paths per call is comfortable
            batch = paths[i:i + 200]
            resp = c.send({"ExtractPackedFiles": [key, {"PackFile": [{"File": p} for p in batch]},
                                                  dest, False]})
            written += len(resp["StringVecPathBuf"][1])
            print(f"  extracted {written}/{len(paths)}")
        print("into", dest)

    elif mode == "search":
        # Kept for completeness only. Expect: Server failed to deserialize command:
        # missing field `matches`. Use find + extract instead.
        pattern = sys.argv[3]
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
            "use_regex": False, "sources": [{"Pack": key}], "search_on": on,
            "matches": matches, "game_key": "warhammer_3"}]})
        hits = (resp or {}).get("GlobalSearchVecRFileInfo")
        if not hits:
            print("  rejected:", json.dumps(resp)[:400])
            print("  -> GlobalSearch is unusable against this server; extract and grep locally.")
            return
        _cfg, files = hits
        print(f"\n{len(files)} file(s) contain {pattern!r}:")
        for f in files:
            print("   ", f["path"])

    else:
        raise SystemExit(__doc__)

    try:
        c.send("ClientDisconnecting")
    except Exception:
        pass          # the server shuts down as soon as the last session leaves


if __name__ == "__main__":
    main()
