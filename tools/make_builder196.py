#!/usr/bin/env python3
"""Build the round-196 build script from the round-195 one: the MCT label is the user's long text again (no tooltip).
(Written with the Write tool: a first version made through a bash heredoc lost a line continuation.)"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_mctpage_harness194\build_and_install195.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_mctlabel_harness195\build_and_install196.py"
ANCHOR = 'print("ROUND 195 GATE OK: the MCT page has no tooltip marker, a named section and the Done / Forgotten feedback")\n'
ADD = ANCHOR + r'''# ROUND 196 (user 2026-11-21: "I liked the previous text, just not the misaligned '?'")
assert 'add_new_action("reset_remembered", "Forget the remembered M/A choices", pressed)' in _mct194, \
    "BUILD REFUSED (round 196): the MCT label is not the user's text"
print("ROUND 196 GATE OK: the MCT label is 'Forget the remembered M/A choices', no tooltip")
'''


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(ANCHOR) == 1
    src = src.replace(ANCHOR, ADD).replace("20261121_mctpage_harness194", "20261121_mctlabel_harness195")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
