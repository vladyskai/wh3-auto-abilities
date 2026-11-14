r"""Clones the round-147 builder into build_and_install148.py with a ROUND 148 gate."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_addr_probe_harness146\build_and_install147.py"
OUT = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_memreader_probe_harness147\build_and_install148.py"

s = open(SRC, "rb").read().decode("utf-8")
anchor = 'print("ROUND 147 GATE OK: the address probe is read-only and appended once to the MAP row")\n'
assert s.count(anchor) == 1
gate = anchor + r'''# ROUND 148: the memreader probe (optional, read-only).
for _tok in ("function FOURTH.mr_check()", "function FOURTH.mr_unit(u)", "FOURTH.MR_LEAD_OFF = 0x3B78\n",
             "FOURTH.MR_MEN_OFF = 0xA4\n", "FOURTH.MR_HP_PTR_OFF = 0x280\n", "FOURTH.MR_HP_OFF = 0x5CC\n",
             "FOURTH.MR_UNIT_OFF = 0x8\n", "FOURTH.MR_FAIL_LIMIT = 3\n"):
    assert script_txt.count(_tok) == 1, "the memreader probe is missing or duplicated: " + _tok.strip()
_r0 = script_txt.find("-- ROUND 148 - THE MEMREADER PROBE")
_r1 = script_txt.find("function FOURTH.map_row(u, side, t, alliance)", _r0)
assert 0 < _r0 < _r1, "the memreader probe block is missing"
for _bad in ("m.write", "m.hook", "m.call", "m.patch", "m.code_cave", "m.alloc", "perform_special_ability", "string.find"):
    assert _bad not in script_txt[_r0:_r1], "BUILD REFUSED (round 148): the memreader probe is not read-only: " + _bad
assert script_txt.count("FOURTH.mr_unit(") == 2 and script_txt.count("FOURTH.mr_check()") == 2, \
    "the memreader probe is called from somewhere other than the map row / map snapshot"
print("ROUND 148 GATE OK: the memreader probe is optional, read-only and only on the map rows")
'''
s = s.replace(anchor, gate)
open(OUT, "wb").write(s.encode("utf-8"))
print("wrote", OUT)
