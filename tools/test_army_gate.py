#!/usr/bin/env python3
"""Prove the round-121 BUILD gate both ways, without opening a WebSocket.

Executes ONLY the gate block of tools/build_and_install.py (from the round-121
comment banner up to "for p in (OUT_PACK, GAME_PACK):") against two sources:

  1. the shipped source as edited in round 121  -> must PASS
  2. the pre-121 snapshot (docs/backups/round121/pre121_zz_test_deadly_onslaught.lua)
     -> must raise AssertionError naming the 4 army-bar keys
"""
import re

BUILD = r"C:\Users\vlady\Desktop\WH3_mod\tools\build_and_install.py"
NOW = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua"
PRE = r"C:\Users\vlady\Desktop\WH3_mod\docs\backups\round121\pre121_zz_test_deadly_onslaught.lua"

src = open(BUILD, encoding="utf-8").read()
a = src.index("# ROUND 121 GATE")
b = src.index("for p in (OUT_PACK, GAME_PACK):")
gate = src[a:b]


def run(mod_path):
    env = {"__name__": "gate", "re": re, "FILES": [(mod_path, "script/battle/mod/x.lua")]}
    exec(compile(gate, "<gate>", "exec"), env)


print("-- 1. shipped source (round 121):")
run(NOW)
print("\n-- 2. pre-121 snapshot (must be refused):")
try:
    run(PRE)
except AssertionError as e:
    print("  AssertionError:", e)
else:
    raise SystemExit("FAIL: the pre-121 source was NOT refused")
