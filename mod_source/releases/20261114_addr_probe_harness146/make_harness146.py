r"""Builds harness146.lua = harness145.lua + the round-147 section + its runner call."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_blob_trigger_harness145\harness145.lua"
SEC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_addr_probe_harness146\h146_section.lua"
OUT = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_addr_probe_harness146\harness146.lua"

s = open(SRC, "rb").read().decode("utf-8")
sec = open(SEC, "rb").read().decode("utf-8")
anchor = "\n-- THE RUNNER."
assert s.count(anchor) == 1
s = s.replace(anchor, sec + anchor)
call = "\nrun_h145()\n"
assert s.count(call) == 1
s = s.replace(call, call + "run_h146()\n")
open(OUT, "wb").write(s.encode("utf-8"))
print("wrote", OUT)
