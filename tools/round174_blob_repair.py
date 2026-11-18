#!/usr/bin/env python3
"""Round 174 repair: tools/round174_blob_tables.py cut each GENERATED blob block at the first 'FOURTH.load_X()' text,
which is also the function's own header ('function FOURTH.load_X()'), so the old function body and call stayed behind
the new block (a Lua syntax error: '<eof> expected near end'). This removes the leftover, in both copies, and the regen
script is fixed to match the call at the start of a line."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
ANN = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua"
for path in (SRC, ANN):
    s = open(path, encoding="utf-8", newline="").read()
    for fn in ("load_blob_tables", "load_value_tables", "load_large_tables"):
        call = "\nFOURTH.%s()\n" % fn
        head = "function FOURTH.%s()\n" % fn
        assert s.count(head) == 1, (path[-12:], fn, s.count(head))
        i = s.index(head)
        j = s.index(call, i) + len(call)          # the end of the NEW block
        k = s.find(call, j - 1)                    # the leftover's own call, if any
        if k != -1 and s.find("\n", j, k + 1) != -1 and s.count(call) == 2:
            s = s[:j] + s[k + len(call):]
        assert s.count(call) == 1, (path[-12:], fn, s.count(call))
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path[-30:], "repaired")
