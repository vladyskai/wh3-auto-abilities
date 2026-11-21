#!/usr/bin/env python3
"""Build the round-199 build script from the round-198 one (the overnight review's second replies, user 2026-11-22:
rows 5, 9, 10, 12). ROUND 199 GATE: the badge compare accepts a listed key in lower case, the ally arm is wired for
exactly ten entries whose game rows target friends (ally-only exactly where the game gives neither the caster nor the
ground), the infantry test refuses the large set and fliers, a click writes remember_next and never the battle's
start table."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_reviewfixes_harness197\build_and_install198.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_reviewfixes2_harness198\build_and_install199.py"
ANCHOR = ('print("ROUND 198 GATE OK: the entry reset shared with the fast pass, the re-armed serial window, every multi-use key held, "\n'
          '      "no_self = the game\'s target_self, the two auras on the round-192 read, Bugman\'s 55 m, compiles on Lua 5.1")\n')
ADD = ANCHOR + r'''# ROUND 199 (user 2026-11-22, the overnight review's second replies: rows 5, 9, 10, 12).
assert script_txt.count("if candidate == listed_key or candidate == FOURTH.KEY_LOWER[listed_key] then") == 1 \
    and "if lk ~= key then FOURTH.KEY_LOWER[key] = lk end" in script_txt, \
    "BUILD REFUSED (round 199): the badge compare must accept a listed key in lower case"
assert script_txt.count("\nfunction FOURTH.ally_arm_wrap(f, ally_only)\n") == 1 \
    and 'ability.evaluate = FOURTH.ally_arm_wrap(ability.evaluate, ability.ally_value_arm == "only")' in script_txt, \
    "BUILD REFUSED (round 199): the ally arm is not wired"
_arm199 = []
for _m in _re198.finditer(r'\n\t\{ marker = "([^"]+)", name = "[^"]*", trigger = "([^"]+)",(.*?)(?=\n\t\{ marker = |\n\t-- |\n\}\n)',
                          script_txt[_ab0:_ab1], _re198.S):
    _mk, _body = _m.group(1), _m.group(3)
    if "\t\tally_value_arm = " not in _body:
        continue
    _keys = _re198.findall(r'"(wh[^"]*)"', _body.split("keys = {")[1].split("}")[0])
    _only = '\t\tally_value_arm = "only",' in _body
    for _k in _keys:
        _r = _game198[_k]
        assert _r[_h198["target_friends"]] == "true", "BUILD REFUSED (round 199): %s does not target friends" % _k
        _game_only = (_r[_h198["target_self"]] == "false" and _r[_h198["target_ground"]] == "false")
        assert _only == _game_only, "BUILD REFUSED (round 199): ally-only differs from the game's target flags: " + _mk
        assert ("\t\tally_range_real = %d,\n" % int(float(_r[_h198["target_intercept_range"]]))) in _body, \
            "BUILD REFUSED (round 199): %s does not carry the game's range" % _mk
    _arm199.append(_mk)
assert len(_arm199) == 10 and script_txt.count("\t\tally_value_arm = true,") == 8 \
    and script_txt.count('\t\tally_value_arm = "only",') == 2, \
    "BUILD REFUSED (round 199): the ally arm rides %d entries, expected 10 (8 + 2 ally-only)" % len(_arm199)
_i199 = script_txt.index("\nfunction FOURTH.enemy_is_infantry(enemy)\n")
_b199 = script_txt[_i199:script_txt.index("\nend\n", _i199)]
assert "FOURTH.class_keys.large[t199] == true then return false end" in _b199 and "is_currently_flying()" in _b199, \
    "BUILD REFUSED (round 199): the infantry test must refuse the large set and a flying unit"
_r199 = script_txt.index("\nfunction FOURTH.remember(ui_id, marker, value)\n")
_rb199 = script_txt[_r199:script_txt.index("\nend\n", _r199)]
assert "a.remembered" not in _rb199.replace("a.remembered is the START", "") and "a.remember_next[t] = (value == true)" in _rb199 \
    and script_txt.count("pairs(a.remember_next or {})") == 1 and "pairs(a.remembered or {})" not in script_txt, \
    "BUILD REFUSED (round 199): a click must write remember_next only (the battle's start table stays)"
print("ROUND 199 GATE OK: a capital key is claimed; the ally arm on 10 entries (2 ally-only, by the game's flags); "
      "the infantry test refuses large and flying; a click writes the next battle's choice only")
'''


# ROUND 199 rebase: the ten ally-arm entries carry ally_range_real (71 fields -> 81)
REBASE = (
    r'assert script_txt.count("\t\tally_range_real = ") == 71, "the ally_range_real fields are not 41 (32 + the 9 ally-aware entries)"',
    r'assert script_txt.count("\t\tally_range_real = ") == 81, "the ally_range_real fields are not 81 (71 + the ten round-199 ally arms)"',
)


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(REBASE[0]) == 1, src.count(REBASE[0])
    src = src.replace(REBASE[0], REBASE[1])
    assert src.count(ANCHOR) == 1, src.count(ANCHOR)
    src = src.replace(ANCHOR, ADD).replace("20261122_reviewfixes_harness197", "20261122_reviewfixes2_harness198")
    open(DST, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", DST)


if __name__ == "__main__":
    main()
