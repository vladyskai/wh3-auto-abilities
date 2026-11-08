import hashlib

LIVE = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua"
ANN  = r"C:/Users/vlady/Desktop/WH3_mod/docs/WH3_auto_ability_annotated.lua"

def rd(p):
    with open(p, "rb") as f: return f.read().decode("utf-8")
def wr(p, s):
    b = s.encode("utf-8"); assert b.count(b"\r") == 0
    with open(p, "wb") as f: f.write(b)
def rep(s, old, new, n=1, tag=""):
    c = s.count(old)
    if c != n: raise SystemExit("ANCHOR %s: %d != %d\n%r" % (tag, c, n, old[:160]))
    return s.replace(old, new)

GAP_OLD = """function FOURTH.ad_centre_gap(unit, enemy)
\tlocal ok_a, a = pcall(function() return unit:position() end)
\tlocal ok_b, b = pcall(function() return enemy:position() end)
\tif not ok_a or not ok_b or a == nil or b == nil then return nil end
\tlocal ok_d, d = pcall(function() return a:distance_xz(b) end)
\tif ok_d and type(d) == "number" then return d end
\tlocal ok_x1, x1 = pcall(function() return a:get_x() end)
\tlocal ok_z1, z1 = pcall(function() return a:get_z() end)
\tlocal ok_x2, x2 = pcall(function() return b:get_x() end)
\tlocal ok_z2, z2 = pcall(function() return b:get_z() end)
\tif ok_x1 and ok_z1 and ok_x2 and ok_z2
\t\tand type(x1) == "number" and type(z1) == "number"
\t\tand type(x2) == "number" and type(z2) == "number" then
\t\tlocal dx, dz = x1 - x2, z1 - z2
\t\treturn math.sqrt(dx * dx + dz * dz)
\tend
\treturn nil
end

-- One position as "x, z" metres for the log - never the height, which is the
-- number that would make a flier look far from a unit it is sitting on.
function FOURTH.ad_where(unit)
\tlocal ok_p, p = pcall(function() return unit:position() end)
\tif not ok_p or p == nil then return "(?)" end
\tlocal ok_x, x = pcall(function() return p:get_x() end)
\tlocal ok_z, z = pcall(function() return p:get_z() end)
\tif not ok_x or not ok_z or type(x) ~= "number" or type(z) ~= "number" then return "(?)" end
\treturn string.format("(%.1f, %.1f)", x, z)
end
"""

GAP_NEW = """function FOURTH.ad_centre_gap(unit, enemy)
\tlocal ok_a, a = pcall(function() return unit:position() end)
\tlocal ok_b, b = pcall(function() return enemy:position() end)
\tif not ok_a or not ok_b or a == nil or b == nil then return nil end
\tlocal ok_x1, x1 = pcall(function() return a:get_x() end)
\tlocal ok_z1, z1 = pcall(function() return a:get_z() end)
\tlocal ok_x2, x2 = pcall(function() return b:get_x() end)
\tlocal ok_z2, z2 = pcall(function() return b:get_z() end)
\tif not (ok_x1 and ok_z1 and ok_x2 and ok_z2) then return nil end
\tif type(x1) ~= "number" or type(z1) ~= "number"
\t\tor type(x2) ~= "number" or type(z2) ~= "number" then return nil end
\tlocal ok_d, d = pcall(function() return a:distance_xz(b) end)
\tif not ok_d or type(d) ~= "number" then
\t\tlocal dx, dz = x1 - x2, z1 - z2
\t\td = math.sqrt(dx * dx + dz * dz)
\tend
\treturn d, x1, z1, x2, z2
end

-- One position as "x, z" metres for the log - never the height, which is the
-- number that would make a flier look far from a unit it is sitting on.
function FOURTH.ad_pos(x, z)
\tif type(x) ~= "number" or type(z) ~= "number" then return "(?)" end
\treturn string.format("(%.1f, %.1f)", x, z)
end
"""

LOOP_OLD = """\t\t\t\t\tlocal gap = FOURTH.ad_centre_gap(unit, enemy)
\t\t\t\t\tif gap ~= nil then
\t\t\t\t\t\tif near == nil or gap < near_gap then
\t\t\t\t\t\t\tnear, near_gap = enemy, gap
\t\t\t\t\t\tend
\t\t\t\t\t\tif gap <= bound and (best == nil or gap < best_gap) then
\t\t\t\t\t\t\tbest, best_gap = enemy, gap
\t\t\t\t\t\tend
\t\t\t\t\tend
"""
LOOP_NEW = """\t\t\t\t\tlocal gap, ux, uz, ex, ez = FOURTH.ad_centre_gap(unit, enemy)
\t\t\t\t\tif gap ~= nil then
\t\t\t\t\t\tif near == nil or gap < near_gap then
\t\t\t\t\t\t\tnear, near_gap = enemy, gap
\t\t\t\t\t\tend
\t\t\t\t\t\tif gap <= bound and (best == nil or gap < best_gap) then
\t\t\t\t\t\t\tbest, best_gap = enemy, gap
\t\t\t\t\t\t\tbest_ux, best_uz, best_ex, best_ez = ux, uz, ex, ez
\t\t\t\t\t\tend
\t\t\t\t\tend
"""

LOCALS_OLD = "\tlocal best, best_gap = nil, nil\n\tlocal near, near_gap = nil, nil\n"
LOCALS_NEW = ("\tlocal best, best_gap = nil, nil\n"
              "\tlocal near, near_gap = nil, nil\n"
              "\tlocal best_ux, best_uz, best_ex, best_ez\n")

for path, islive in ((LIVE, True), (ANN, False)):
    s = rd(path)
    s = rep(s, GAP_OLD, GAP_NEW, 1, path + " gap helper")
    s = rep(s, LOCALS_OLD, LOCALS_NEW, 1, path + " locals")
    s = rep(s, LOOP_OLD, LOOP_NEW, 1, path + " loop")
    if islive:
        s = rep(s, "\tlocal edge = FOURTH.eg_enemy_gap(unit, best)\n", "", 1, "live edge decl")
        s = rep(s, "\t\t.. \" (caster=\" .. FOURTH.ad_where(unit) .. \" enemy=\" .. FOURTH.ad_where(best)\n",
                   "\t\t.. \" (caster=\" .. FOURTH.ad_pos(best_ux, best_uz)\n"
                   "\t\t.. \" enemy=\" .. FOURTH.ad_pos(best_ex, best_ez)\n", 1, "live where->pos")
    wr(path, s)
    print(path, "ok", len(s), hashlib.md5(s.encode('utf-8')).hexdigest())
