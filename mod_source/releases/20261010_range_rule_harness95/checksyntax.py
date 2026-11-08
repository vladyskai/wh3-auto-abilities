import sys
import lupa

ok = True
for p in sys.argv[1:]:
    src = open(p, encoding="utf-8").read()
    lua = lupa.LuaRuntime()
    try:
        lua.compile(src)
        print("OK  ", p)
    except Exception as e:
        ok = False
        print("FAIL", p, e)
sys.exit(0 if ok else 1)
