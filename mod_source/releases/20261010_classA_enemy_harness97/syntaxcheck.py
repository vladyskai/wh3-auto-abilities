import lupa, sys
for p in ["C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua",
          "C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"]:
    src=open(p,encoding="utf-8").read()
    rt=lupa.LuaRuntime()
    fn,err=rt.eval("function(s) return load(s) end"), None
    try:
        chunk=rt.eval("function(s) local f,e = load(s); return e end")(src)
        print(("OK  " if chunk is None else "ERR "), p.split("/")[-1], chunk or "")
    except lupa.LuaError as e:
        print("LUAERR", p, e)
