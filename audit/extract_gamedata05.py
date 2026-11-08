# -*- coding: utf-8 -*-
import csv, json, os
T = os.path.expandvars(r'%LOCALAPPDATA%\Temp\wh3')
U = os.path.join(T, 'uieff')

def load_tsv(path):
    rows = []
    with open(path, encoding='utf-8-sig', newline='') as f:
        rd = csv.reader(f, delimiter='\t')
        for r in rd:
            rows.append(r)
    # drop the '#table;...' meta line(s)
    return [r for r in rows if r and not r[0].startswith('#')]

# ---- my 58 entries from source of truth ----
import re
src = open(r'C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua', encoding='utf-8').read()
lines = src.split('\n')
start = 157
end = None
for i in range(start+1, len(lines)):
    if lines[i].startswith('}'):
        end = i; break
region = '\n'.join(lines[start:end+1])
parts = re.split(r'\t\{ marker = "', region)[1:]
entries = []
for p in parts:
    marker = p.split('"',1)[0]
    name = re.search(r'name = ("(?:[^"\\]|\\.)*")', p).group(1)
    name = json.loads(name)
    tr = re.search(r'trigger = "([a-z0-9_]+)"', p).group(1)
    ka = re.search(r'keys = \{([^}]*)\}', p)
    keys = re.findall(r'"([^"\\]+)"', ka.group(1))
    entries.append({'marker':marker,'name':name,'trigger':tr,'keys':keys})
print("entries parsed:", len(entries))
mine = entries[232:290]
print("slice:", len(mine), mine[0]['marker'], "..", mine[-1]['marker'])

# sanity cross-check vs slice06 json if present
p6 = r'C:\Users\vlady\Desktop\WH3_mod\audit\_slice06_parsed.json'
if os.path.exists(p6):
    d6 = json.load(open(p6, encoding='utf-8'))
    ok = all(d6[232+i]['marker']==e['marker'] for i,e in enumerate(mine))
    print("cross-check vs slice06 parse:", ok)

# ---- game tables ----
def idx_table(rows, keycol=0):
    d = {}
    for r in rows[1:]:
        if len(r) <= keycol: continue
        d.setdefault(r[keycol], []).append(r)
    return d

spec = load_tsv(os.path.join(T,'unit_spec_abil.tsv'))
spec_hdr = spec[0]; spec_idx = idx_table(spec)
PJ = load_tsv(os.path.join(T,'phase_junc.tsv')); pj_idx = idx_table(PJ, 1)
PH = load_tsv(os.path.join(T,'phases.tsv')); ph_hdr = PH[0]; ph_idx = idx_table(PH)
SPS = load_tsv(os.path.join(U,'special_ability_phase_stat_effects.tsv')); sps_idx = idx_table(SPS,0)
PAE = load_tsv(os.path.join(U,'phase_attribute_effects.tsv')); pae_idx = idx_table(PAE,1)
UAE = load_tsv(os.path.join(U,'unit_abilities_additional_ui_effects_tables.tsv'))
UAE_LOC = load_tsv(os.path.join(U,'unit_abilities_additional_ui_effects__.loc.tsv')); ual = {}
for r in UAE_LOC[1:]:
    ual[r[0]] = r[1]
UB = load_tsv(os.path.join(T,'unit_abilities.tsv'));
UB_LOC = load_tsv(os.path.join(T,'unit_abilities.loc.tsv')); ubl = {}
for r in UB_LOC[1:]:
    ubl[r[0]] = r[1]
JUNC = load_tsv(os.path.join(U,'unit_abilities_to_ui_effects_juncs.tsv')); junc_idx = idx_table(JUNC,0)
P2U = load_tsv(os.path.join(U,'phases_to_ui_effects_juncs.tsv')); p2u_idx = idx_table(P2U,1)
BP = load_tsv(os.path.join(U,'ui_unit_bullet_point_enums__.loc.tsv')); bp = {}
for r in BP[1:]:
    bp[r[0]] = r[1]
INVU = load_tsv(os.path.join(T,'special_ability_to_invalid_usage_flags_tables.tsv')); invu_idx = idx_table(INVU,1)
INVT = load_tsv(os.path.join(T,'special_ability_to_invalid_target_flags_tables.tsv')); invt_idx = idx_table(INVT,1)
ADR = load_tsv(os.path.join(T,'special_ability_to_auto_deactivate_flags_tables.tsv')); adr_idx = idx_table(ADR,1)
SAGJ = load_tsv(os.path.join(T,'sag_to_abilities.tsv')); sagj_idx = idx_table(SAGJ,1)
SAG = load_tsv(os.path.join(T,'sag.tsv'))
USB = load_tsv(os.path.join(T,'uset_ability.tsv')); usb_idx = idx_table(USB,1)
LAND = load_tsv(os.path.join(T,'land_abil.tsv')); land_idx = idx_table(LAND,0)
UNITAB = load_tsv(os.path.join(T,'unit_abilities_to_ui_effects_juncs.tsv')) if os.path.exists(os.path.join(T,'unit_abilities_to_ui_effects_juncs.tsv')) else []
print("loaded tables; spec rows:", len(spec)-1)

out = []
missing = []
for i,e in enumerate(mine, start=233):
    blk = {'n':i, **e, 'keys_data':{}}
    for k in e['keys']:
        kd = {}
        rows = spec_idx.get(k)
        if rows:
            r = rows[0]
            kd['spec'] = {spec_hdr[j]: (r[j] if j < len(r) else '') for j in range(len(spec_hdr))}
        # phase junc
        pjs = pj_idx.get(k, [])
        phs = []
        for r in pjs:
            phase = r[5] if len(r)>5 else ''
            phs.append({'target_self':r[2],'target_friends':r[3],'target_enemies':r[4],'phase':phase})
        kd['phase_junc'] = phs
        # invalid flags
        kd['invalid_usage'] = [r[0] for r in invu_idx.get(k,[])]
        kd['invalid_target'] = [r[0] for r in invt_idx.get(k,[])]
        kd['auto_deactivate'] = [r[0] for r in adr_idx.get(k,[])]
        # ui effects
        eff = [r[1] for r in junc_idx.get(k,[])]
        kd['ui_effects'] = eff
        kd['ui_effects_text'] = [ual.get('unit_abilities_additional_ui_effects_localised_text_'+x, '??'+x) for x in eff]
        # loc name
        kd['loc_name'] = ubl.get('unit_abilities_onscreen_name_'+k)
        kd['loc_tooltip'] = ubl.get('unit_abilities_tooltip_text_'+k)
        # unit abilities type
        urows = [r for r in UB[1:] if r and r[0]==k]
        if urows and len(urows[0])>4:
            kd['ub_type'] = urows[0][4]
        # sag groups
        kd['sag_groups'] = [r[0] for r in sagj_idx.get(k, [])]
        kd['uset'] = [r[2] for r in usb_idx.get(k, [])]
        kd['land_units'] = list({r[1] for r in land_idx.get(k, [])})
        if not rows: missing.append((i,k))
        blk['keys_data'][k] = kd
    # phase details for all phases referenced
    out.append(blk)

print("missing from unit_spec_abil:", missing)

json.dump(out, open(r'C:\Users\vlady\Desktop\WH3_mod\audit\_slice05_gamedata.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print("wrote _slice05_gamedata.json")
