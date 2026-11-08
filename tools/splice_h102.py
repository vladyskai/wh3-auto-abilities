"""Splice the HARNESS 102 section into harness102.lua (built by make_h102_base)."""
import os

TEMP = os.path.expandvars(r"%LOCALAPPDATA%\Temp")
ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
H = os.path.join(TEMP, "harness102.lua")
SEC = os.path.join(ROOT, "mod_source", "releases", "20261017_summon_harness102", "h102_section.lua")

s = open(H, encoding="utf-8").read()
sec = open(SEC, encoding="utf-8").read()

anchor = ('\ncheck("ZERO search calls by the mod across everything, harness 71, 72, 73, 74, 75, 76, 77, 78, 79, '
          '80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99 AND 100\'s worlds included')
i = s.find(anchor)
assert i > 0, "final find-check anchor missing"
assert s.count(anchor) == 1

boundary = ""lice the HARNESS 102 section into harness102.lua (built by make_h102_base)."""
import os

TEMP = os.path.expandvars(r"%LOCALAPPDATA%\Temp")
ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
H = os.path.join(TEMP, "harness102.lua")
SEC = os.path.join(ROOT, "mod_source", "releases", "20261017_summon_harness102", "h102_section.lua")

s = open(H, encoding="utf-8").read()
sec = open(SEC, encoding="utf-8").read()

anchor = ('\ncheck("ZERO search calls by the mod across everything, harness 71, 72, 73, 74, 75, 76, 77, 78, 79, '
          '80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99 AND 100\'s worlds included')
i = s.find(anchor)
assert i > 0, "final find-check anchor missing"
assert s.count(anchor) == 1

boundary = ("\n\n-- HARNESS 102 boundary: the whole harness-101 suite ran first.\n"
            "if RED_MODE then\n"
            '  check("HARNESS 101 suite boundary (harness 102): N/A in the red run - the pre-102 snapshot moves the table-size pins by design", true)\n'
            "else\n"
            '  check("HARNESS 101 suite boundary (harness 102): every harness-101 check ran (checks == 3442)",\n'
            "    checks == 3442)\n"
            "end\n")

s = s[:i] + "\n" + sec + "\n" + boundary + s[i:]

old_lbl = 'ZERO search calls by the mod across everything, harness 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99 AND 100\'s worlds included'
new_lbl = 'ZERO search calls by the mod across everything, harness 71 to 100 AND 101-102\'s worlds included'
assert s.count(old_lbl) == 1, "find-check label anchor"
s = s.replace(old_lbl, new_lbl)

open(H, "w", encoding="utf-8", newline="\n").write(s)
print("harness102 spliced:", len(s), "bytes")
