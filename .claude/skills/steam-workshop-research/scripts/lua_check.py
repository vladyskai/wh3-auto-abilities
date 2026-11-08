#!/usr/bin/env python3
"""Syntax-check Lua files without a Lua install on PATH.

Lua is rarely installed, and the host that will run the script (a game engine, an
embedded runtime) is not available for a dry run. `lupa` embeds a Lua runtime in
Python, which is enough to compile a file and surface syntax errors -- the cheap half
of verifying a script you cannot execute in its real environment.

    uv run --quiet --with lupa python scripts/lua_check.py mod.lua [more.lua ...]

Exit code 0 = every file compiled, 1 = at least one failed, 2 = usage/setup problem.

Compiling proves SYNTAX ONLY. To test logic, drive the real file against a mock of the
host API it calls and assert on the calls it makes -- harness shape in
references/wh3-mod-authoring.md.
"""

import pathlib
import sys


def main(paths: list[str]) -> int:
    try:
        import lupa
    except ImportError:
        print("lupa is not installed. Run this via:")
        print(f"    uv run --quiet --with lupa python {__file__} <file.lua> ...")
        return 2

    runtime = lupa.LuaRuntime()
    failures = 0

    for raw in paths:
        path = pathlib.Path(raw)
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"READ FAIL    {path}: {exc}")
            failures += 1
            continue

        try:
            runtime.compile(source)
            print(f"SYNTAX OK    {path}  ({len(source)} chars)")
        except Exception as exc:  # lupa raises its own Lua error type
            print(f"SYNTAX FAIL  {path}: {exc}")
            failures += 1

    if failures:
        print(f"\n{failures} file(s) failed to compile.")
        return 1
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1:]))
