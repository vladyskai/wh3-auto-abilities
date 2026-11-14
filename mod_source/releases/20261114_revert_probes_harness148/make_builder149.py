r"""Clones the round-146 builder (whose gates match the restored round-146 source) into build_and_install149.py
with a ROUND 149 gate: no address field, no memreader code."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_blob_trigger_harness145\build_and_install146.py"
OUT = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_revert_probes_harness148\build_and_install149.py"

s = open(SRC, "rb").read().decode("utf-8")
anchor = 'print("ROUND 146 GATE OK: 77 blob entries; the tables match the game; 10 m margin; half a packed block")\n'
assert s.count(anchor) == 1
gate = anchor + r'''# ROUND 149: the revert of rounds 147-148 (user ruling 2026-11-14).
for _bad in ("map_addr", "mr_unit", "mr_check", "memreader", "MEMREADER", " addr="):
    assert _bad not in script_txt, "BUILD REFUSED (round 149): probe code is still in the script: " + _bad
print("ROUND 149 GATE OK: no address field and no memreader code")
'''
open(OUT, "wb").write(s.replace(anchor, gate).encode("utf-8"))
print("wrote", OUT)
