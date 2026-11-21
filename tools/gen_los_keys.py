#!/usr/bin/env python3
"""Round 189: the abilities the game marks 'Requires line of sight to the target' (user ruling 2026-11-21: "I would
just do the check for terrain on all 35 and units on all 35. Just let's be safe, and if it doesn't fire, that's okay.").

The game data: unit_abilities_to_ui_effects_juncs carries the ui effect wh3_main_projectile_requires_line_of_sight on
56 ability keys (gamedata/wh3/uieff/unit_abilities_to_ui_effects_juncs.tsv); 35 of them are ours. The whole set is
embedded (a key that is not ours is simply never read). One string, read at load with string.gmatch, so no key appears
in quotes a second time.
derive() is imported by the round-189 patch (to embed the text) and by the builder (to refuse a pack whose table
differs from the game data)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gamedata_paths import UIEFF  # noqa: E402

EFFECT = "wh3_main_projectile_requires_line_of_sight"
TSV = os.path.join(UIEFF, "unit_abilities_to_ui_effects_juncs.tsv")


def derive():
    out = set()
    with open(TSV, encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 2 and p[1] == EFFECT:
                out.add(p[0])
    return out


def lua_text(keys):
    return "FOURTH.LOS_TEXT = \"%s\"" % ";".join(sorted(keys))


if __name__ == "__main__":
    k = derive()
    print("line-of-sight keys", len(k))
