#!/usr/bin/env python3
"""Compile the live script and the annotated copy on Lua 5.1 (the game's version). Run with: uv run --with lupa python"""
from lupa import lua51

FILES = (r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua",
         r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_auto_ability_annotated.lua")


def main():
    for p in FILES:
        lua = lua51.LuaRuntime()
        f = lua.eval("function(s) local f, e = loadstring(s) return f ~= nil, e end")
        print(p[-30:], f(open(p, encoding="utf-8").read()))


if __name__ == "__main__":
    main()
