"""Round-15 fix-up #1: apply three refinements to BOTH r15_section.lua and the
patched probe, byte-exact with strict occurrence counts.

1. maybe_delta: quote the computed hovered_expected (log consistency).
2. sample_pass: record the FIRST text-kind deviation in R15.first_text.
3. table + reset_run: first_text field; WIN line prefers first_text.
"""
import hashlib

FILES = [r"C:/Users/vlady/Desktop/WH3_mod/tools/r15_section.lua",
         r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_probe_ui_text.lua"]

EDITS = [
    (b'  local exp = "?"\n  if sn ~= nil then exp = tostring(sn - d) end\n',
     b'  local exp = "?"\n  if sn ~= nil then exp = q(tostring(sn - d)) end\n'),
    (b'          if e.kind == "text" then R15.maybe_delta(p, e, cur) end\n',
     b'          if e.kind == "text" then\n'
     b'            if R15.first_text == nil then\n'
     b'              R15.first_text = { pass = p.n, row = e.row, field = e.field, was = e.base, now = cur }\n'
     b'            end\n'
     b'            R15.maybe_delta(p, e, cur)\n'
     b'          end\n'),
    (b'  first_evidence      = nil,        -- { pass, row, field, was, now }\n',
     b'  first_evidence      = nil,        -- { pass, row, field, was, now } (any value-bearing deviation)\n'
     b'  first_text          = nil,        -- the FIRST text-kind deviation (the WIN line prefers it)\n'),
    (b'  R15.first_evidence = nil\n',
     b'  R15.first_evidence = nil\n  R15.first_text = nil\n'),
    (b'    local e = R15.first_evidence or {}\n',
     b'    local e = R15.first_text or R15.first_evidence or {}\n'),
]

for path in FILES:
    data = open(path, "rb").read()
    before = hashlib.sha256(data).hexdigest()[:16]
    for i, (old, new) in enumerate(EDITS, 1):
        n = data.count(old)
        assert n == 1, f"{path}: edit {i} found {n} occurrences"
        data = data.replace(old, new)
    assert data.count(b"\r") == 0, f"{path}: CRLF leaked"
    open(path, "wb").write(data)
    print(f"{path}\n  {before} -> {hashlib.sha256(data).hexdigest()[:16]}  bytes={len(data)}")
print("OK")
