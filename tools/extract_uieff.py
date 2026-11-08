#!/usr/bin/env python3
"""Re-extract the game-data TSVs that tools/build_ability_database.py reads from
%LOCALAPPDATA%\\Temp\\wh3\\uieff\\ (that folder was found emptied on 2026-10-28).

Decodes each table straight from the installed game's own packs through the
RPFM server (ws://127.0.0.1:45127) and writes it in the editor's TSV export
shape: a header row of column names (definition field order), a '#<table>;<version>;<path>'
meta row, then one row per record (floats with 4 decimals, booleans lower-case).

    python extract_uieff.py calibrate   # re-derive phases.tsv into scratch, compare
    python extract_uieff.py extract     # write the uieff set (+ a copy under archive/)

Start rpfm_server first; one WebSocket session per invocation.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import gamedata_paths as GP
import json
import os
import shutil
import sys

from websockets.sync.client import connect

GAME = r"C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III/data"
T = GP.GAMEDATA  # SUPERSEDED by tools/extract_gamedata.py (2026-11-01), which regenerates the whole set
U = os.path.join(T, "uieff")
ARCH = os.path.join(GP.ROOT, "archive", "gamedata_extract", "uieff")

# out name -> (pack, table folder or loc path)
WANT = {
    "special_ability_phase_stat_effects.tsv": ("db.pack", "db/special_ability_phase_stat_effects_tables/"),
    "phase_attribute_effects.tsv": ("db.pack", "db/special_ability_phase_attribute_effects_tables/"),
    "phases_to_ui_effects_juncs.tsv": ("db.pack", "db/special_ability_phases_to_additional_ui_effects_junctions_tables/"),
    "unit_abilities_to_ui_effects_juncs.tsv": ("db.pack", "db/unit_abilities_to_additional_ui_effects_juncs_tables/"),
    "unit_abilities_additional_ui_effects_tables.tsv": ("db.pack", "db/unit_abilities_additional_ui_effects_tables/"),
    "unit_abilities_additional_ui_effects__.loc.tsv": ("local_en.pack", "text/db/unit_abilities_additional_ui_effects__.loc"),
    "unit_stat_localisations__.loc.tsv": ("local_en.pack", "text/db/unit_stat_localisations__.loc"),
    "unit_attributes__.loc.tsv": ("local_en.pack", "text/db/unit_attributes__.loc"),
}
CALIB = ("phases.tsv", "db.pack", "db/special_ability_phases_tables/")


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
    (k, v), = c.items()
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        return "%.4f" % v
    if v is None:
        return ""
    return str(v)


def key_first(fields, rows):
    """the editor's TSV export order: key fields first (in definition order), then the rest"""
    order = [i for i, f in enumerate(fields) if f.get("is_key")] +             [i for i, f in enumerate(fields) if not f.get("is_key")]
    return [fields[i]["name"] for i in order], [[r[i] for i in order] for r in rows]


def decode(c, key, path):
    r = c.send({"DecodePackedFile": [key, path, "PackFile"]})
    (kind, payload), = r.items()
    if kind == "DBRFileInfo":
        db = payload[0]["table"]
        name = db["table_name"]
        ver = db["definition"]["version"]
        meta = "#%s;%s;%s" % (name, ver, path)
        cols, rows = key_first(db["definition"]["fields"],
                               [[cell(x) for x in row] for row in db["table_data"]])
    elif kind == "LocRFileInfo":
        loc = payload[0]["table"]
        meta = "#Loc;1;%s" % path
        cols, rows = key_first(loc["definition"]["fields"],
                               [[cell(x) for x in row] for row in loc["table_data"]])
    else:
        raise SystemExit("unexpected decode reply for %s: %s" % (path, json.dumps(r)[:300]))
    return cols, meta, rows


def write_tsv(out, cols, meta, rows):
    pad = "\t" * (len(cols) - 1)
    with open(out, "w", encoding="utf-8", newline="") as f:
        f.write("\t".join(cols) + "\n")
        f.write(meta + pad + "\n")
        for r in rows:
            f.write("\t".join(r) + "\n")


def files_under(c, key, prefix):
    tree = c.send({"GetPackFileDataForTreeView": key})
    infos = tree["ContainerInfoVecRFileInfo"][1]
    return sorted(i["path"] for i in infos if i["path"].startswith(prefix))


def main():
    mode = sys.argv[1]
    c = Client()
    c.send({"SetGameSelected": ["warhammer_3", False]})
    if c.send("IsSchemaLoaded") != {"Bool": True}:
        print("schema:", c.send("UpdateSchemas"))
    keys = {}

    def pack(name):
        if name not in keys:
            r = c.send({"OpenPackFiles": [GAME + "/" + name]})
            keys[name] = r["StringContainerInfo"][0]
        return keys[name]

    jobs = [CALIB] if mode == "calibrate" else [(o, p, t) for o, (p, t) in WANT.items()]
    os.makedirs(U, exist_ok=True)
    for out, pk, target in jobs:
        key = pack(pk)
        paths = files_under(c, key, target) if target.endswith("/") else [target]
        assert paths, ("nothing under", pk, target)
        allrows, cols, meta = [], None, None
        for p in paths:
            cc, mm, rr = decode(c, key, p)
            if cols is None:
                cols, meta = cc, mm
            assert cc == cols, (p, "column set differs")
            allrows += rr
        dest = os.path.join(T, "scratch", "calib_" + out) if mode == "calibrate" else os.path.join(U, out)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        write_tsv(dest, cols, meta, allrows)
        print("%-50s %6d rows from %d file(s) -> %s" % (out, len(allrows), len(paths), dest))
        if mode == "extract":
            os.makedirs(ARCH, exist_ok=True)
            shutil.copy2(dest, os.path.join(ARCH, out))
    try:
        c.send("ClientDisconnecting")
    except Exception:
        pass   # the server exits when its last session leaves


if __name__ == "__main__":
    main()
