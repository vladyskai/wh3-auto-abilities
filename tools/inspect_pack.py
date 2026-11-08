"""Open a pack with rpfm_server and extract everything, DB tables as TSV.

Usage: python inspect_pack.py <pack path> <destination dir>
"""
import json
import os
import sys
from websockets.sync.client import connect

WS_URL = "ws://127.0.0.1:45127/ws"


class Client:
    def __init__(self, url):
        self.ws = connect(url, max_size=None, open_timeout=20)
        self.next_id = 1
        json.loads(self.ws.recv(timeout=20))          # hello

    def send(self, command):
        req_id = self.next_id
        self.next_id += 1
        self.ws.send(json.dumps({"id": req_id, "data": command}))
        while True:
            msg = json.loads(self.ws.recv(timeout=300))
            if msg.get("id") == req_id:
                return msg.get("data")
            print("  (unsolicited)", json.dumps(msg)[:200])


def main():
    pack_path, dest = sys.argv[1], sys.argv[2]
    os.makedirs(dest, exist_ok=True)

    c = Client(WS_URL)
    c.send({"SetGameSelected": ["warhammer_3", False]})

    print(f"opening {pack_path}")
    resp = c.send({"OpenPackFiles": [pack_path]})
    key, container = resp["StringContainerInfo"]
    print(f"  key: {key}  type: {container.get('pfh_file_type')}  version: {container.get('pfh_version')}")

    info = c.send({"GetPackFileDataForTreeView": key})
    _, files = info["ContainerInfoVecRFileInfo"]
    paths = [f["path"] for f in files]
    print(f"\n=== {len(paths)} file(s) inside ===")
    for p in sorted(paths):
        size = next((f.get("file_size") for f in files if f["path"] == p), None)
        print(f"  {str(size):>10}  {p}")

    print(f"\nextracting to {dest} (tables as TSV)")
    resp = c.send({"ExtractPackedFiles": [
        key,
        {"PackFile": [{"File": p} for p in paths]},
        dest,
        True,
    ]})
    print("  ", json.dumps(resp)[:600])

    try:
        c.send("ClientDisconnecting")
    except Exception:
        pass


if __name__ == "__main__":
    main()
