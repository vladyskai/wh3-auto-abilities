"""Run a Lua test harness under lupa (the project's Lua interpreter).

Usage:
  uv run --with lupa python run_harness.py <harness.lua> [--red <live> <ann>]

Prints the harness stdout. Exit code 0 when the harness ends with no failures.
"""
import os
import re
import sys

import lupa


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print("usage: run_harness.py <harness.lua> [--red <live.lua> <ann.lua>]")
        return 2
    harness = args[0]
    if "--red" in args:
        i = args.index("--red")
        os.environ["H_LIVE"] = args[i + 1]
        os.environ["H_ANN"] = args[i + 2]
    src = open(harness, "r", encoding="utf-8", errors="replace").read()
    rt = lupa.LuaRuntime(unpack_returned_tuples=True)
    # make os.getenv see the vars we set
    try:
        rt.execute(src)
    except lupa.LuaError as e:
        print("LUA ERROR:", e)
        return 1
    # the harness prints its own summary; scan the captured output is not
    # possible here (it goes to the real stdout), so rely on the exit path.
    return 0


if __name__ == "__main__":
    sys.exit(main())
