"""Lua syntax check via lupa. Prints SYNTAX OK, or the compile error + exit 1.

Usage:  uv run --with lupa python lua_check.py <file.lua> [<file2.lua> ...]
"""
import sys

import lupa


def check(path: str) -> bool:
    src = open(path, "r", encoding="utf-8", errors="replace").read()
    rt = lupa.LuaRuntime(register_eval=False)
    try:
        rt.compile(src)  # compiles only - the chunk is NOT executed
    except lupa.LuaSyntaxError as e:
        print(f"SYNTAX ERROR  {path}\n  {e}")
        return False
    except lupa.LuaError as e:  # any other compile-time failure
        print(f"SYNTAX ERROR  {path}\n  {e}")
        return False
    print(f"SYNTAX OK     {path}  ({len(src)} bytes)")
    return True


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: lua_check.py <file.lua> [...]")
        return 2
    ok = all(check(p) for p in sys.argv[1:])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
