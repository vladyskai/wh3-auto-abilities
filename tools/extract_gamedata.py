#!/usr/bin/env python3
"""Re-extract every game-data TSV in gamedata\\wh3\\ (and uieff\\) from the installed
game, through the RPFM server (ws://127.0.0.1:45127).

Each TSV names its own source on its second line ('#<table>;<version>;db/<table>/data__'
or '#Loc;1;text/db/<name>__.loc'), so the set regenerates itself: a db table comes from
data/db.pack, a localisation file from data/local_en.pack. The output is the editor's TSV
export shape (key columns first, floats with 4 decimals, booleans lower-case), calibrated
byte-for-byte against phases.tsv on 2026-10-28 (tools/extract_uieff.py).

A TSV with no source line (the older db_*.tsv dumps and game_auto_deactivate.tsv) is
left untouched and listed as FROZEN.

    python extract_gamedata.py            # extract, then print the drift per file
    python extract_gamedata.py --dry      # only list what would be extracted

Start rpfm_server first; one WebSocket session per invocation.
"""
import glob
import json
import os
import sys

from websockets.sync.client import connect

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gamedata_paths import GAMEDATA, GAME_DATA_DIR  # noqa: E402


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


def cell(c):
    (_, v), = c.items()
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        return "%.4f" % v
    if v is None:
        return ""
    return str(v)


def processed(fields):
    """the decoded row's cell order: colour channels (is_part_of_colour) are folded into ONE
    ColourRGB cell per colour group, appended after the other fields (named '<prefix>_hex',
    as the editor's own export names it: colour_r/g/b -> colour_hex)"""
    out = [dict(f) for f in fields if not f.get("is_part_of_colour")]
    groups = {}
    for f in fields:
        g = f.get("is_part_of_colour")
        if g:
            groups.setdefault(g, f["name"].rsplit("_", 1)[0])
    for g in sorted(groups):
        out.append({"name": groups[g] + "_hex", "is_key": False})
    return out


def key_first(fields, rows):
    fields = processed(fields)
    assert all(len(r) == len(fields) for r in rows), ("row length differs from the processed fields",
                                                       len(fields), set(len(r) for r in rows))
    order = [i for i, f in enumerate(fields) if f.get("is_key")] + \
            [i for i, f in enumerate(fields) if not f.get("is_key")]
    return [fields[i]["name"] for i in order], [[r[i] for i in order] for r in rows]


def decode(c, key, path):
    r = c.send({"DecodePackedFile": [key, path, "PackFile"]})
    (kind, payload), = r.items()
    t = payload[0]["table"]
    cols, rows = key_first(t["definition"]["fields"], [[cell(x) for x in row] for row in t["table_data"]])
    if kind == "DBRFileInfo":
        meta = "#%s;%s;%s" % (t["table_name"], t["definition"]["version"], path)
    elif kind == "LocRFileInfo":
        meta = "#Loc;1;%s" % path
    else:
        raise SystemExit("unexpected decode reply for %s: %s" % (path, kind))
    return cols, meta, rows


def sources():
    out, frozen = [], []
    for f in sorted(glob.glob(os.path.join(GAMEDATA, "*.tsv")) + glob.glob(os.path.join(GAMEDATA, "uieff", "*.tsv"))):
        with open(f, encoding="utf-8-sig") as fh:
            fh.readline()
            meta = fh.readline().split("\t")[0].strip()
        if not meta.startswith("#") or meta.count(";") < 2:
            frozen.append(f)
            continue
        path = meta.split(";", 2)[2]
        if meta.startswith("#Loc;"):
            out.append((f, "local_en.pack", path))
        else:
            out.append((f, "db.pack", path.rsplit("/", 1)[0] + "/"))
    return out, frozen


def main():
    jobs, frozen = sources()
    for f in frozen:
        print("FROZEN (no source line, left untouched):", os.path.relpath(f, GAMEDATA))
    if "--dry" in sys.argv:
        for f, pk, t in jobs:
            print("%-55s <- %s %s" % (os.path.relpath(f, GAMEDATA), pk, t))
        return
    c = Client()
    c.send({"SetGameSelected": ["warhammer_3", False]})
    if c.send("IsSchemaLoaded") != {"Bool": True}:
        print("schema:", c.send("UpdateSchemas"))
    keys, trees = {}, {}

    def pack(name):
        if name not in keys:
            keys[name] = c.send({"OpenPackFiles": [GAME_DATA_DIR + "/" + name]})["StringContainerInfo"][0]
            tree = c.send({"GetPackFileDataForTreeView": keys[name]})
            trees[name] = [i["path"] for i in tree["ContainerInfoVecRFileInfo"][1]]
        return keys[name]

    for f, pk, target in jobs:
        key = pack(pk)
        paths = sorted(p for p in trees[pk] if p.startswith(target)) if target.endswith("/") else [target]
        assert paths and all(p in trees[pk] for p in paths), ("source not in the game pack", pk, target)
        old = open(f, encoding="utf-8").read().split("\n")
        allrows, cols, meta = [], None, None
        for p in paths:
            cc, mm, rr = decode(c, key, p)
            if cols is None:
                cols, meta = cc, mm
            assert cc == cols, (p, "column set differs between fragments")
            allrows += rr
        pad = "\t" * (len(cols) - 1)
        text = "\t".join(cols) + "\n" + meta + pad + "\n" + "".join("\t".join(r) + "\n" for r in allrows)
        with open(f, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        new = text.split("\n")
        same_header = old[:2] == new[:2]
        o, n = set(old[2:]) - {""}, set(new[2:]) - {""}
        print("%-55s %6d rows from %d file(s)  header %s  rows only-old %d  only-new %d"
              % (os.path.relpath(f, GAMEDATA), len(allrows), len(paths),
                 "same" if same_header else "CHANGED", len(o - n), len(n - o)))
    try:
        c.send("ClientDisconnecting")
    except Exception:
        pass   # the server exits when its last session leaves


if __name__ == "__main__":
    main()
