import lupa
for p in ["C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua",
          "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"]:
    src = open(p, encoding="utf-8").read()
    rt = lupa.LuaRuntime()
    f = rt.eval("function(s) local c,e = load(s); return e end")
    err = f(src)
    print(("OK  " if err is None else "ERR "), p.split("/")[-1], err or "")
