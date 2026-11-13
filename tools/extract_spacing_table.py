#!/usr/bin/env python3
"""Round 145: extract the game's unit spacing table (land_units.spacing points into it) into gamedata\\wh3\\, in the
same TSV form tools/extract_gamedata.py writes (header, then the '#<table>;<version>;<path>' line), so later re-extracts
refresh it automatically.

  uv run --with websockets python tools/extract_spacing_table.py [--list]
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
    hits = sorted(p for p in paths if "spacing" in p.lower())
    print("tables with 'spacing':", hits)
    if "--list" in sys.argv:
        return
    sp = [p for p in hits if p.startswith("db/unit_spacings_tables/") or p.startswith("db/unit_spacing_tables/")]
    assert sp, "no unit spacing table found"
    cols, meta, rows = None, None, []
    for p in sp:
        cc, mm, rr = X.decode(c, key, p)
        if cols is None:
            cols, meta = cc, mm
        assert cc == cols
        rows += rr
    out = os.path.join(GP.GAMEDATA, "unit_spacings.tsv")
    pad = "\t" * (len(cols) - 1)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        fh.write("\t".join(cols) + "\n" + meta + pad + "\n" + "".join("\t".join(r) + "\n" for r in rows))
    print("wrote", out, len(rows), "rows; columns:", cols)
    try:
        c.send("ClientDisconnecting")
    except Exception:
        pass


if __name__ == "__main__":
    main()
