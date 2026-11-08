"""Assemble harness111.lua from harness110.lua plus the round-111 section.

1. Copy harness110.lua verbatim (every earlier world, unchanged).
2. Move harness 110's own call inside harness 111 (its call stays where it is,
   before the new section is defined - the suite order is 109, 110, 111).
3. Append the new section and the final summary AFTER run_h111(), so the printed
   total covers all three suites.
"""
import io

SRC = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261022_airdrop_relative_harness110/harness110.lua"
DST = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261023_airdrop_movingcaster_harness111/harness111.lua"
SEC = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261023_airdrop_movingcaster_harness111/h111_section.lua"

s = io.open(SRC, encoding="utf-8", newline="").read()
assert "\r" not in s

TAIL = '''run_h109()
run_h110()

print("checks: " .. checks .. ", failures: " .. failures)
if failures == 0 then
  print("HARNESS OK - all checks passed")
else
  print("HARNESS FAILURES: " .. failures)
end
'''
assert s.endswith(TAIL), s[-300:]

sec = io.open(SEC, encoding="utf-8", newline="").read()
assert "\r" not in sec

body = s[: -len(TAIL)].rstrip("\n")
out = body + "\n\n" + sec.rstrip("\n") + "\n\nrun_h109()\nrun_h110()\nrun_h111()\n\n" + TAIL[len("run_h109()\nrun_h110()\n"):]

io.open(DST, "w", encoding="utf-8", newline="\n").write(out)
print("wrote", DST, len(out), "bytes")
