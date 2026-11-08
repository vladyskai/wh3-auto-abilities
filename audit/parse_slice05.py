import re, json, sys
src = open(r'C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua', encoding='utf-8').read()
lines = src.split('\n')
start = 157  # 'local ABILITIES = {'
end = None
for i in range(start+1, len(lines)):
    if lines[i].startswith('}'):
        end = i
        break
print("table region lines:", start+1, "to", end+1)
region = '\n'.join(lines[start:end+1])
n_marker_lines = sum(1 for l in lines[start:end+1] if 'marker = ' in l)
print("marker lines in region:", n_marker_lines)
# count entries by the canonical entry start pattern
starts = re.findall(r'\t\{ marker = "', region)
print("canonical starts:", len(starts))
# check for marker lines not matching canonical start
for i, l in enumerate(lines[start:end+1], start=start+1):
    if 'marker = ' in l and not l.startswith('\t{ marker = "'):
        print("NONCANON", i, repr(l[:120]))
