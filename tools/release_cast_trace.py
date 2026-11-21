"""Make two copies of harness198 that record every cast order (unit form and ground form) into a trace file:
A runs the development script, B runs the release-test script (the release transform with the test switches kept).
Equal traces = the release build orders exactly the same casts in every world of the suite."""
import sys
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_reviewfixes2_harness198\harness198.lua"
OUT = sys.argv[1].replace("\\", "/")
REL = sys.argv[2].replace("\\", "/")
DEVP = "C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"
s = open(SRC, encoding="utf-8").read()
a = "      W.fires[#W.fires + 1] = { key = tostring(k), uid = def.uid, name = def.name, tick = W.poll_ticks, target = u }\n"
assert s.count(a) == 1
s = s.replace(a, a + '      TRACE[#TRACE + 1] = "U " .. tostring(k) .. " " .. tostring(def.uid) .. " t" .. tostring(W.poll_ticks)'
              ' .. " -> " .. tostring(type(u) == "table" and u.zz_uid or "?")\n')
b = "      W.ground_fires[#W.ground_fires + 1] = { key = tostring(k), uid = def.uid,"
assert s.count(b) == 1
s = s.replace(b, '      TRACE[#TRACE + 1] = "G " .. tostring(k) .. " " .. tostring(def.uid) .. " t" .. tostring(W.poll_ticks)\n' + b)
world = "local function make_world(opts)\n"
assert s.count(world) == 1
s = s.replace(world, world + '  TRACE[#TRACE + 1] = "WORLD"\n')
# one Lua state loads many script copies: the previous copy's console function must not look like "the development
# build is loaded" to the release guard
lw = "  ZZ_AUTO_TEST_REMEMBER_FILE = W.remember_file\n"
assert s.count(lw) == 1
s = s.replace(lw, lw + "  zz_badge_set = nil\n")
tail = 'print("checks: " .. checks .. ", failures: " .. failures)\n'
assert s.count(tail) == 1
print("dev path occurrences:", s.count(DEVP))
for tag, live in (("A", DEVP), ("B", REL)):
    t = "TRACE = {}\n" + s.replace(DEVP, live)
    t = t.replace(tail, tail + 'TRACE_FH = io.open("%s/trace_%s.txt", "w"); TRACE_FH:write(table.concat(TRACE, "\\n") .. "\\n"); TRACE_FH:close()\n' % (OUT, tag))
    open(OUT + "/harness_trace_%s.lua" % tag, "w", encoding="utf-8", newline="\n").write(t)
    print("wrote", OUT + "/harness_trace_%s.lua" % tag)
