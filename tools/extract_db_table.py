#!/usr/bin/env python3
"""Extract one game db table into gamedata\\wh3\\<out>.tsv, in the TSV form tools/extract_gamedata.py writes (header,
then the '#<table>;<version>;<path>' line), so later re-extracts refresh it automatically.

  uv run --with websockets python tools/extract_db_table.py --list <word>        # tables whose path holds <word>
  uv run --with websockets python tools/extract_db_table.py <table_folder> <out>  # e.g. projectiles_explosions_tables projectiles_explosions
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import extract_gamedata as X  # noqa: E402
import gamedata_paths as GP  # noqa: E402


def main():
    c = X.Client()
    c.send({"SetGameSelected": ["warhammer_3", False]})
    if c.send("IsSchemaLoaded") != {"Bool": True}:
        print("schema:", c.send("UpdateSchemas"))
    key = c.send({"OpenPackFiles": [X.GAME_DATA_DIR + "/db.pack"]})["StringContainerInfo"][0]
    tree = c.send({"GetPackFileDataForTreeView": key})
    paths = [i["path"] for i in tree["ContainerInfoVecRFileInfo"][1]]
    try:
        if sys.argv[1] == "--list":
            print(sorted(set(p.rsplit("/", 1)[0] for p in paths if sys.argv[2] in p.lower())))
            return
        folder, name = sys.argv[1], sys.argv[2]
        sp = sorted(p for p in paths if p.startswith("db/%s/" % folder))
        assert sp, "no such table: " + folder
        cols, meta, rows = None, None, []
        for p in sp:
            cc, mm, rr = X.decode(c, key, p)
            if cols is None:
                cols, meta = cc, mm
            assert cc == cols
            rows += rr
        out = os.path.join(GP.GAMEDATA, name + ".tsv")
        pad = "\t" * (len(cols) - 1)
        with open(out, "w", encoding="utf-8", newline="") as fh:
            fh.write("\t".join(cols) + "\n" + meta + pad + "\n" + "".join("\t".join(r) + "\n" for r in rows))
        print("wrote", out, len(rows), "rows; columns:", cols)
    finally:
        try:
            c.send("ClientDisconnecting")
        except Exception:
            pass


if __name__ == "__main__":
    main()
