import io
BS = chr(92)
s = io.open("harness98_base.lua", encoding="utf-8", newline="").read()
i = s.find("tostring(FOURTH.ab_range_m)")
line = s[:i].split(BS and "\n")[-1] + s[i:i+40].split("\n")[0]
print("LINE:", line)
print("count of backslash in line:", line.count(BS))
print("context chars:", [c for c in s[i-30:i+35]])
