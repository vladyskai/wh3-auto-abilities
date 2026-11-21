#!/usr/bin/env python3
"""Build the round-197 build script from the round-196 one (the blob family's whole-army fallback, user 2026-11-21:
"A: whole army"). ROUND 197 GATE: the flag is set by the blob evaluation only, the two rule wrappers stand at their 6
places inside the blob pickers and re-check, the wanderers keep the plain trash rule, the fallback counts the whole
enemy army (no visibility filter) and is fail-closed."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_mctlabel_harness195\build_and_install196.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_blobfallback_harness196\build_and_install197.py"
ANCHOR = 'print("ROUND 196 GATE OK: the MCT label is \'Forget the remembered M/A choices\', no tooltip")\n'
ADD = ANCHOR + r'''# ROUND 197 (user 2026-11-21: "A: whole army"): the blob family's whole-army fallback.
assert script_txt.count("FOURTH.blob_relax = (ZZ_AUTO_TEST_NO_BLOB_FALLBACK ~= true) and not FOURTH.blob_better_exists(key, central)") == 1, \
    "BUILD REFUSED (round 197): the fallback flag must be set once, by the blob evaluation"
assert script_txt.count("FOURTH.blob_ap_rule(") == 5 and script_txt.count("FOURTH.blob_trash_rule(") == 3, \
    "BUILD REFUSED (round 197): the two rule wrappers are not at their places (armour: 1 definition + 4 uses, trash: 1 + 2)"
assert "if sc < FOURTH.blob_need(row.r) or not FOURTH.blob_trash_ok(e, sc, row.r) then return nil end" in script_txt, \
    "BUILD REFUSED (round 197): the wanderers must keep the plain trash rule"
_i197 = script_txt.index("\nfunction FOURTH.blob_better_exists(")
_b197 = script_txt[_i197:script_txt.index("\nend\n", _i197)]
assert "is_visible_to_alliance" not in _b197 and "local v = better or not readable" in _b197, \
    "BUILD REFUSED (round 197): the fallback must count the whole army (hidden too) and keep the rules when unreadable"
print("ROUND 197 GATE OK: the whole-army fallback (flag set by the blob evaluation, 6 wrapped rule uses, fail-closed)")
'''


REBASE = (
    '    and script_txt.count("FOURTH.blob_trash_ok(e, sc, r)") == 3, "the trash rule is missing (definition, pick and re-check)"',
    '    and script_txt.count("FOURTH.blob_trash_ok(e, sc, r)") == 2 \\\n'
    '    and script_txt.count("FOURTH.blob_trash_rule(e, sc, r)") == 3, '
    '"the trash rule is missing (definition, the round-197 wrapper, pick and re-check through the wrapper)"   # ROUND 197 rebase',
)


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(REBASE[0]) == 1
    src = src.replace(REBASE[0], REBASE[1])
    assert src.count(ANCHOR) == 1
    src = src.replace(ANCHOR, ADD).replace("20261121_mctlabel_harness195", "20261121_blobfallback_harness196")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
