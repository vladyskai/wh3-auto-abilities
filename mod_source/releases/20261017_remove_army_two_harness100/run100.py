import os, sys
import lupa

harness = sys.argv[1]
if len(sys.argv) >= 5 and sys.argv[2] == "--red":
    os.environ["H100_LIVE"] = sys.argv[3]
    os.environ["H100_ANN"] = sys.argv[4]
    print("[runner] RED mode:", sys.argv[3], "|", sys.argv[4])
src = open(harness, encoding="utf-8", errors="replace").read()
rt = lupa.LuaRuntime(unpack_returned_tuples=True)
try:
    rt.execute(src)
except lupa.LuaError as e:
    print("LUA ERROR:", e)
    sys.exit(1)
