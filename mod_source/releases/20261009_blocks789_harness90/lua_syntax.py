import sys, io, lupa
rt = lupa.LuaRuntime()
loader = rt.eval("function(s, name) local f, err = load(s, name); return f, err end")
for p in sys.argv[1:]:
    src = io.open(p, encoding="utf-8", errors="replace").read()
    f, err = loader(src, p)
    print(p, "->", "OK" if f else ("ERROR: " + str(err)))
