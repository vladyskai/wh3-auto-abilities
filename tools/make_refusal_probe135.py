SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_enemy_slows_harness134\build_and_install135.py"
DST = r"C:\Users\vlady\AppData\Local\Temp\claude\7ac174569b7349c6\f7d153bf-9ec2-4c19-b570-ac42979369ed\scratchpad\refusal_probe.py"
s = open(SRC, encoding="utf-8").read()
# break the FIRST content gate after the websocket steps: the round-135 gate
a = "    and script_txt.count('trigger = \"enemy_melee\"') == 14 \\\n"
b = "    and script_txt.count('trigger = \"enemy_melee\"') == 999 \\\n"
assert s.count(a) == 1, s.count(a)
s = s.replace(a, b)
# make sure the probe cannot install even if every gate passed
c = "shutil.copy2(OUT_PACK, GAME_PACK)\n"
assert s.count(c) == 1
s = s.replace(c, "raise SystemExit('PROBE: install step reached - must not happen')\n")
open(DST, "w", encoding="utf-8", newline="\n").write(s)
print("probe written: one gate broken, install disabled")
