"""Small fix-up: the picker's log line reads '(mode) health=NN%' instead of
'(mode health=NN%)' - the double word was ugly and the harness pins the shape."""
import os
ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
for p in (os.path.join(ROOT, "mod_source", "script", "battle", "mod", "zz_test_deadly_onslaught.lua"),
          os.path.join(ROOT, "docs", "WH3_auto_ability_annotated.lua")):
    s = open(p, "rb").read().decode("utf-8")
    old_hp = '\t\t\t\t\t\thp_text = " health=" .. string.format("%.0f", best_hp) .. "%"'
    new_hp = '\t\t\t\t\t\thp_text = ", health=" .. string.format("%.0f", best_hp) .. "%"'
    assert s.count(old_hp) == 1, p
    s = s.replace(old_hp, new_hp)
    old_log = ('\t\t\t\t\tlog("  " .. marker .. " target: \'" .. etype .. "\' is the chosen enemy (" .. tostring(mode)\n'
               '\t\t\t\t\t\t.. hp_text .. ") distance=" .. ((best_gap ~= nil) and string.format("%.1f", best_gap) or "?")\n'
               '\t\t\t\t\t\t.. "m bound=" .. bound_text)')
    new_log = ('\t\t\t\t\tlog("  " .. marker .. " target: \'" .. etype .. "\' is the chosen enemy (" .. tostring(mode) .. ")"\n'
               '\t\t\t\t\t\t.. hp_text .. " distance=" .. ((best_gap ~= nil) and string.format("%.1f", best_gap) or "?")\n'
               '\t\t\t\t\t\t.. "m bound=" .. bound_text)')
    if old_log in s:
        s = s.replace(old_log, new_log)
    else:
        print("  (no live log line to change in", os.path.basename(p), "- annotated copy)")
    open(p, "wb").write(s.encode("utf-8"))
    print("patched", os.path.basename(p), "CR:", s.count("\r"))
