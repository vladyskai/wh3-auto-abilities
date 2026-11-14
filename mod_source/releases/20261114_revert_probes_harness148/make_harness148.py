r"""Builds harness148.lua = harness147.lua + the round-149 section; run_h146 and run_h147 are RETIRED in the runner
(they test the address field and the memreader probe that round 149 removes; the functions stay in the file)."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_memreader_probe_harness147\harness147.lua"
SEC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_revert_probes_harness148\h148_section.lua"
OUT = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_revert_probes_harness148\harness148.lua"

s = open(SRC, "rb").read().decode("utf-8")
sec = open(SEC, "rb").read().decode("utf-8")
anchor = "\n-- THE RUNNER."
assert s.count(anchor) == 1
s = s.replace(anchor, sec + anchor)
old = "\nrun_h146()\nrun_h147()\n"
assert s.count(old) == 1
s = s.replace(old, """
-- run_h146() RETIRED in round 149: it tested the round-147 address field, removed
-- by the user's ruling of 2026-11-14 ("we close this project and reverse
-- everything"). The function stays above.
-- run_h147() RETIRED in round 149: it tested the round-148 memreader probe,
-- removed by the same ruling. The function stays above.
run_h148()
""")
open(OUT, "wb").write(s.encode("utf-8"))
print("wrote", OUT)
