# -*- coding: utf-8 -*-
"""Slice 1 (entries 1-58) game-data extractor - audit support.

Mirrors the sibling slices' extractor but for entries [0:58] and adds
grouped2.json + full phase details (effect_type / heal / damage / targets).
Read-only: writes only _slice01_gamedata.json into WH3_audit/.
"""
import csv, json, os, re

T = os.path.expandvars(r'%LOCALAPPDATA%\Temp\wh3')
U = os.path.join(T, 'uieff')

def load_tsv(path):
    rows = []
    with open(path, encoding='utf-8-sig', newline='') as f:
        rd = csv.reader(f, delimiter='\t')
        for r in rd:
            rows.append(r)
    return [r for r in rows if r and not r[0].startswith('#')]

def idx_table(rows, keycol=0):
    d = {}
    for r in rows[1:]:
        if len(r) <= keycol: continue
        d.setdefault(r[keycol], []).append(r)
    return d

# ---- entries from source of truth ----
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
    name = json.loads(re.search(r'name = ("(?:[^"\\]|\\.)*")', p).group(1))
    tr = re.search(r'trigger = "([a-z0-9_]+)"', p).group(1)
    ka = re.search(r'keys = \{([^}]*)\}', p)
    keys = re.findall(r'"([^"\\]+)"', ka.group(1))
    entries.append({'marker':marker,'name':name,'trigger':tr,'keys':keys})
print("entries parsed:", len(entries))
mine = entries[0:58]
print("slice:", len(mine), mine[0]['marker'], "..", mine[-1]['marker'])

# ---- game tables ----
spec = load_tsv(os.path.join(T,'unit_spec_abil.tsv')); spec_hdr = spec[0]; spec_idx = idx_table(spec)
PJ = load_tsv(os.path.join(T,'phase_junc.tsv')); pj_idx = idx_table(PJ, 1)
PH = load_tsv(os.path.join(T,'phases.tsv')); ph_hdr = PH[0]; ph_idx = idx_table(PH)
UAE_LOC = load_tsv(os.path.join(U,'unit_abilities_additional_ui_effects__.loc.tsv')); ual = {}
for r in UAE_LOC[1:]:
    ual[r[0]] = r[1]
UB = load_tsv(os.path.join(T,'unit_abilities.tsv'))
UB_LOC = load_tsv(os.path.join(T,'unit_abilities.loc.tsv')); ubl = {}
for r in UB_LOC[1:]:
    ubl[r[0]] = r[1]
JUNC = load_tsv(os.path.join(U,'unit_abilities_to_ui_effects_juncs.tsv')); junc_idx = idx_table(JUNC, 0)
BP = load_tsv(os.path.join(U,'ui_unit_bullet_point_enums__.loc.tsv')); bp = {}
for r in BP[1:]:
    bp[r[0]] = r[1]
INVU = load_tsv(os.path.join(T,'special_ability_to_invalid_usage_flags_tables.tsv')); invu_idx = idx_table(INVU, 1)
INVT = load_tsv(os.path.join(T,'special_ability_to_invalid_target_flags_tables.tsv')); invt_idx = idx_table(INVT, 1)
ADR = load_tsv(os.path.join(T,'special_ability_to_auto_deactivate_flags_tables.tsv')); adr_idx = idx_table(ADR, 1)
SAGJ = load_tsv(os.path.join(T,'sag_to_abilities.tsv')); sagj_idx = idx_table(SAGJ, 1)
USB = load_tsv(os.path.join(T,'uset_ability.tsv')); usb_idx = idx_table(USB, 1)
LAND = load_tsv(os.path.join(T,'land_abil.tsv')); land_idx = idx_table(LAND, 0)
G2 = json.load(open(os.path.join(T,'grouped2.json'), encoding='utf-8'))
g2_idx = {r[0]: r for r in G2}

def phase_detail(pid):
    rows = ph_idx.get(pid)
    if not rows: return None
    r = rows[0]
    d = {ph_hdr[j]: (r[j] if j < len(r) else '') for j in range(len(ph_hdr))}
    keep = ['effect_type','duration','heal_amount','barrier_heal_amount','damage_amount',
            'max_damaged_entities','affects_allies','affects_enemies','resurrect',
            'fatigue_change_ratio','imbue_magical','imbue_ignition','imbue_contact',
            'requested_stance','cant_move','hp_change_frequency','execute_ratio','spreading']
    return {k: d.get(k,'') for k in keep}
# phase localised names
SPL = load_tsv(os.path.join(U,'special_ability_phases__.loc.tsv')); spl = {}
for r in SPL[1:]:
    spl[r[0]] = r[1]
# phase displays (buffs/debuffs text?)
PDIS = load_tsv(os.path.join(U,'phase_displays.tsv')); pdis_idx = idx_table(PDIS)

out = []
missing = []
for i, e in enumerate(mine, start=1):
    blk = {'n': i, **e, 'keys_data': {}}
    for k in e['keys']:
        kd = {}
        rows = spec_idx.get(k)
        if rows:
            r = rows[0]
            kd['spec'] = {spec_hdr[j]: (r[j] if j < len(r) else '') for j in range(len(spec_hdr))}
        else:
            missing.append((i, k))
        # grouped2 classification
        g = g2_idx.get(k)
        kd['grouped2'] = (dict(zip(['key','trigger_cat','target_cat','owner_cat','family'], g)) if g else None)
        # phase junc + details
        phs = []
        for r in pj_idx.get(k, []):
            phase = r[5] if len(r) > 5 else ''
            rec = {'target_self': r[2] if len(r) > 2 else '', 'target_friends': r[3] if len(r) > 3 else '',
                   'target_enemies': r[4] if len(r) > 4 else '', 'phase': phase,
                   'phase_name': spl.get('special_ability_phases_onscreen_name_' + phase, '')}
            det = phase_detail(phase)
            if det: rec['detail'] = det
            phs.append(rec)
        kd['phase_junc'] = phs
        kd['invalid_usage'] = [r[0] for r in invu_idx.get(k, [])]
        kd['invalid_target'] = [r[0] for r in invt_idx.get(k, [])]
        kd['auto_deactivate'] = [r[0] for r in adr_idx.get(k, [])]
        eff = [r[1] for r in junc_idx.get(k, [])]
        kd['ui_effects'] = eff
        kd['ui_effects_text'] = [ual.get('unit_abilities_additional_ui_effects_localised_text_' + x, '??' + x) for x in eff]
        kd['loc_name'] = ubl.get('unit_abilities_onscreen_name_' + k)
        kd['loc_tooltip'] = ubl.get('unit_abilities_tooltip_text_' + k)
        urows = [r for r in UB[1:] if r and r[0] == k]
        if urows:
            kd['ub_row'] = urows[0]
            if len(urows[0]) > 4: kd['ub_type'] = urows[0][4]
        kd['sag_groups'] = [r[0] for r in sagj_idx.get(k, [])]
        kd['uset'] = [r[2] for r in usb_idx.get(k, [])]
        kd['land_units'] = sorted({r[1] for r in land_idx.get(k, [])})
        blk['keys_data'][k] = kd
    out.append(blk)

print("missing from unit_spec_abil:", missing)
json.dump(out, open(r'C:\Users\vlady\Desktop\WH3_mod\audit\_slice01_gamedata.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("wrote _slice01_gamedata.json")

# ---- compact eyeball summary ----
for blk in out:
    print("=" * 100)
    print(f"[{blk['n']:2d}] {blk['marker']} | {blk['name']} | trigger={blk['trigger']}")
    for k, kd in blk['keys_data'].items():
        sp = kd.get('spec', {})
        g = kd.get('grouped2') or {}
        print(f"  KEY {k}")
        print(f"    loc_name={kd.get('loc_name')!r} ub_type={kd.get('ub_type')} family={g.get('family')} target_cat={g.get('target_cat')} trig_cat={g.get('trigger_cat')} owner={g.get('owner_cat')}")
        if sp:
            print(f"    spec: passive={sp.get('passive')} tgt_self={sp.get('target_self')} tgt_friends={sp.get('target_friends')} tgt_enemies={sp.get('target_enemies')} tgt_ground={sp.get('target_ground')} affect_self={sp.get('affect_self')} always_self={sp.get('always_affect_self')} only_target={sp.get('only_affect_target')} n_friend={sp.get('num_effected_friendly_units')} n_enemy={sp.get('num_effected_enemy_units')} range={sp.get('effect_range')} active={sp.get('active_time')} recharge={sp.get('recharge_time')} uses={sp.get('num_uses')} minr={sp.get('min_range')}")
        pj = kd.get('phase_junc', [])
        for p in pj:
            d = p.get('detail', {})
            print(f"    phase self={p['target_self']} fr={p['target_friends']} en={p['target_enemies']} id={p['phase']} name={p['phase_name']!r} | {d}")
        if kd.get('ui_effects_text'):
            print(f"    bullets: {kd['ui_effects_text']}")
        for flag in ('invalid_usage','invalid_target','auto_deactivate'):
            if kd.get(flag): print(f"    {flag}: {kd[flag]}")
print("=" * 100)
print("DONE")
