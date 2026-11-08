"""Open a pack and decode selected DB tables into readable rows.

Usage: python decode_tables.py <pack path> [path filter]
"""
import json
import sys
from websockets.sync.client import connect

WS_URL = "ws://127.0.0.1:45127/ws"


class Client:
    def __init__(self, url):
        self.ws = connect(url, max_size=None, open_timeout=20)
        self.next_id = 1
        json.loads(self.ws.recv(timeout=20))

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
    pack_path = sys.argv[1]
    filt = sys.argv[2] if len(sys.argv) > 2 else ""

    c = Client(WS_URL)
    c.send({"SetGameSelected": ["warhammer_3", False]})
    resp = c.send({"OpenPackFiles": [pack_path]})
    key, _ = resp["StringContainerInfo"]

    info = c.send({"GetPackFileDataForTreeView": key})
    _, files = info["ContainerInfoVecRFileInfo"]
    paths = [f["path"] for f in files if filt in f["path"]]

    for path in sorted(paths):
        print(f"\n{'='*80}\n{path}")
        dec = c.send({"DecodePackedFile": [key, path, "PackFile"]})
        top = next(iter(dec)) if isinstance(dec, dict) else dec
        print("  decoded as:", top)
        if top == "DBRFileInfo":
            db, _info = dec["DBRFileInfo"]
            print("  table:", db.get("name"))
            print("  columns:", [(c_["name"], c_.get("field_type")) for c_ in db.get("definitions", [])])
            rows = db.get("rows") or []
            print(f"  ROWS: {len(rows)}")
            for r in rows[:60]:
                print("   ", json.dumps(r)[:400])

    try:
        c.send("ClientDisconnecting")
    except Exception:
        pass


if __name__ == "__main__":
    main()
