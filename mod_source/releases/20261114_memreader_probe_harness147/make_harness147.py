r"""Builds harness147.lua = harness146.lua + the round-148 section + its runner call."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_addr_probe_harness146\harness146.lua"
SEC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_memreader_probe_harness147\h147_section.lua"
OUT = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_memreader_probe_harness147\harness147.lua"

s = open(SRC, "rb").read().decode("utf-8")
sec = open(SEC, "rb").read().decode("utf-8")
anchor = "\n-- THE RUNNER."
assert s.count(anchor) == 1
s = s.replace(anchor, sec + anchor)
call = "\nrun_h146()\n"
assert s.count(call) == 1
s = s.replace(call, call + "run_h147()\n")
open(OUT, "wb").write(s.encode("utf-8"))
print("wrote", OUT)
