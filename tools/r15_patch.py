"""Round-15 splice: insert the R15 section + the R15 poll registration + the R15
load-log line into script/battle/mod/zz_probe_ui_text.lua.

BINARY read/write (the probe must stay LF-only; a Python text-mode write on
Windows would flip every \n to CRLF and fail the build's byte-identity gate).
Anchors are asserted to be unique; the length delta must match exactly.
"""
import hashlib

PROBE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_ui_text.lua"
SEC_PATH = r"C:/Users/vlady/Desktop/WH3_mod/tools/r15_section.lua"

SEC = open(SEC_PATH, "rb").read()
assert SEC.endswith(b"end\n"), "section must end with end+LF"
assert b"R15 TOTAL STEPS 7" in SEC

REG = (
    b"-- ROUND 15: the experiment's OWN 25 ms poll (it samples one pass per poll and\n"
    b"-- is idle and SILENT between passes). Registered BEFORE the main poll so the\n"
    b"-- main poll stays the primary callback.\n"
    b"local ok_reg15, err_reg15 = pcall(function()\n"
    b"\tbm:repeat_callback(zz_probe_r15_poll, R15.poll_ms, R15.poll_name)\n"
    b"end)\n"
    b"if ok_reg15 then\n"
    b"\tlog(\"R15 poll registered: \" .. R15.poll_name .. \" every \" .. tostring(R15.poll_ms)\n"
    b"\t\t.. \" ms (round 15: the invisible/control hover passes)\")\n"
    b"else\n"
    b"\tlog(\"R15 poll registration FAILED: \" .. truncate(err_reg15, 160)\n"
    b"\t\t.. \" - the hover passes cannot run without it\")\n"
    b"end\n\n"
)

LOADLOG = (
    b"log(\"R15 TOTAL STEPS 7 - you are done after step 7. ROUND 15: the FINAL experiment\"\n"
    b"\t.. \" (user-designed) - with the unit-info panel OPEN and PINNED and ONE unit selected:\"\n"
    b"\t.. \" step A dumps EVERY stat row's comparison components + context ids (read-only baseline);\"\n"
    b"\t.. \" then THREE INVISIBLE simulated hover passes over ONE NON-selected card (holds 100/150/250 ms,\"\n"
    b"\t.. \" all below the \" .. tostring(R15.visible_ms) .. \" ms tooltip draw delay) poll every 25 ms for any\"\n"
    b"\t.. \" change in label_compare text, comparison-named component text, or the row's CcoUnitStat context\"\n"
    b"\t.. \" id (logged with before/after values); then the 1500 ms CONTROL pass (the tooltip WILL draw -\"\n"
    b"\t.. \" expected) and the verdict. Every SimulateMouseOn is paired with its SimulateMouseOff. Call\"\n"
    b"\t.. \" zz_probe_r15() once, then zz_probe_r15_step() SEVEN times (STOP after step 7). ZERO writes; the\"\n"
    b"\t.. \" name-lookup helper is BANNED. log: \" .. LOG_FILE)\n\n"
)

data = open(PROBE, "rb").read()
print("before: bytes=%d CR=%d sha256=%s" % (len(data), data.count(b"\r"), hashlib.sha256(data).hexdigest()[:16]))
assert data.count(b"\r") == 0, "probe is not LF-only before the patch"

# ---- 1) the R15 section, right after the R14 help block, before section 8.
pos = data.index(b"-- 8. WINDOW LIFECYCLE")
assert data.count(b"-- 8. WINDOW LIFECYCLE") == 1
sep_start = data.rfind(b"\n", 0, pos - 1) + 1
assert data[sep_start:sep_start + 7] == b"-- ====", data[sep_start:sep_start + 20]
assert data[sep_start - 5:sep_start] == b"end\n\n", repr(data[sep_start - 8:sep_start])
data2 = data[:sep_start] + SEC + b"\n" + data[sep_start:]

# ---- 2) the R15 poll registration, right before the main poll registration.
anchor2 = b"local ok_reg, err_reg = pcall(function()"
assert data2.count(anchor2) == 1
pos2 = data2.index(anchor2)
data3 = data2[:pos2] + REG + data2[pos2:]

# ---- 3) the R15 load-log line, right before the mouse-listener block.
anchor3 = b"if mouse_on_registered then"
assert data3.count(anchor3) == 1
pos3 = data3.index(anchor3)
data4 = data3[:pos3] + LOADLOG + data3[pos3:]

expected_delta = len(SEC) + 1 + len(REG) + len(LOADLOG)
assert len(data4) - len(data) == expected_delta, (len(data4) - len(data), expected_delta)
assert data4.count(b"\r") == 0, "CRLF leaked into the patched probe"

open(PROBE, "wb").write(data4)
print("after : bytes=%d CR=%d sha256=%s" % (len(data4), data4.count(b"\r"), hashlib.sha256(data4).hexdigest()[:16]))
print("inserted: section=%d reg=%d loadlog=%d" % (len(SEC) + 1, len(REG), len(LOADLOG)))
print("section starts at byte:", sep_start)
print("OK" if b"-- 17c. ROUND 15" in data4 and b"ok_reg15" in data4 else "FAIL")
