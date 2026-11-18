#!/usr/bin/env python3
"""Round 177: the SQUIG land_units key set from the game's own tables, for Empowering Shrooms (the game's target rule
unit_is_not_squig; user approval 2026-11-18, review row 4 of docs\\WH3_score3_review_2026-11-18.md).

squig: land_units.attribute_group carries the unit attribute "squig" (unit_attributes_to_groups_junctions_tables,
extracted as gamedata/wh3/unit_attr_groups.tsv), the same method as tools/gen_expendable_keys.py. ASSUMPTION: the
engine's unit_is_not_squig flag reads this attribute (the attribute is the only squig grouping in the data).
derive() is imported by the round-177 patch (to embed the text) and by the builder (to refuse a pack whose table
differs from the game data)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_unit_size_keys import rows  # noqa: E402


def derive():
    groups = {r["attribute_group"] for r in rows("unit_attr_groups.tsv") if r.get("attribute") == "squig"}
    return {r["key"] for r in rows("land_units.tsv") if r.get("attribute_group", "") in groups}


def text(keys):
    return ";".join(sorted(keys))


if __name__ == "__main__":
    e = derive()
    print("squig", len(e))
    for k in sorted(e):
        print(" ", k)
