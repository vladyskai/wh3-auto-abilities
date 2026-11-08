# -*- coding: utf-8 -*-
"""Slice 9 (entries 465-522) game-data extractor - audit support.

Mirrors the sibling slices' extractors (01/05/06) for entries [464:522] and
writes _slice09_gamedata.json + _slice09_gamedata.txt into WH3_audit/.
Read-only: touches nothing outside WH3_audit/ (and reads Temp/wh3 + the mod).
"""
import csv, json, os, re

T = os.path.expandvars(r'%LOCALAPPDATA%\Temp\wh3')
U = os.path.join(T, 'uieff')
OUT = r'C:\Users\vlady\Desktop\WH3_mod\audit'

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
for i in range(start + 1, len(lines)):
    if lines[i].startswith('}'):
        end = i; break
region = '\n'.join(lines[start:end + 1])
parts = re.split(r'\t\{ marker = "', region)[1:]
entries = []
for p in parts:
    marker = p.split('"', 1)[0]
    name = json.loads(re.search(r'name = ("(?:[^"\\]|\\.)*")', p).group(1))
    tr = re.search(r'trigger = "([a-z0-9_]+)"', p).group(1)
    ka = re.search(r'keys = \{([^}]*)\}', p)
    keys = re.findall(r'"([^"\\]+)"', ka.group(1))
    entries.append({'marker': marker, 'name': name, 'trigger': tr, 'keys': keys})
print("entries parsed:", len(entries))
mine = entries[464:522]
print("slice:", len(mine), mine[0]['marker'], "..", mine[-1]['marker'])

# cross-check vs sibling parse if present
p_all = os.path.join(OUT, 'entries_all.json')
if os.path.exists(p_all):
    dall = json.load(open(p_all, encoding='utf-8'))
    ok = all(dall[464 + i]['marker'] == e['marker'] for i, e in enumerate(mine))
    print("cross-check vs entries_all.json:", ok)

# ---- game tables ----
spec = load_tsv(os.path.join(T, 'unit_spec_abil.tsv')); spec_hdr = spec[0]; spec_idx = idx_table(spec)
PJ = load_tsv(os.path.join(T, 'phase_junc.tsv')); pj_idx = idx_table(PJ, 1)
PH = load_tsv(os.path.join(T, 'phases.tsv')); ph_hdr = PH[0]; ph_idx = idx_table(PH)
SPS = load_tsv(os.path.join(U, 'special_ability_phase_stat_effects.tsv')); sps_idx = idx_table(SPS, 0)
PAE = load_tsv(os.path.join(U, 'phase_attribute_effects.tsv')); pae_idx = idx_table(PAE, 1)
UAE_LOC = load_tsv(os.path.join(U, 'unit_abilities_additional_ui_effects__.loc.tsv')); ual = {r[0]: r[1] for r in UAE_LOC[1:]}
UB = load_tsv(os.path.join(T, 'unit_abilities.tsv')); ub_idx = idx_table(UB, 0)
UB_LOC = load_tsv(os.path.join(T, 'unit_abilities.loc.tsv')); ubl = {r[0]: r[1] for r in UB_LOC[1:]}
JUNC = load_tsv(os.path.join(U, 'unit_abilities_to_ui_effects_juncs.tsv')); junc_idx = idx_table(JUNC, 0)
P2U = load_tsv(os.path.join(U, 'phases_to_ui_effects_juncs.tsv')); p2u_idx = idx_table(P2U, 1)
STATLOC = load_tsv(os.path.join(U, 'unit_stat_localisations__.loc.tsv')); statloc = {r[0]: r[1] for r in STATLOC[1:]}
ATTRLOC = load_tsv(os.path.join(U, 'unit_attributes__.loc.tsv')); attrloc = {r[0]: r[1] for r in ATTRLOC[1:]}
INVU = load_tsv(os.path.join(T, 'special_ability_to_invalid_usage_flags_tables.tsv')); invu_idx = idx_table(INVU, 1)
INVT = load_tsv(os.path.join(T, 'special_ability_to_invalid_target_flags_tables.tsv')); invt_idx = idx_table(INVT, 1)
ADR = load_tsv(os.path.join(T, 'special_ability_to_auto_deactivate_flags_tables.tsv')); adr_idx = idx_table(ADR, 1)
G2 = json.load(open(os.path.join(T, 'grouped2.json'), encoding='utf-8'))
g2_idx = {r[0]: r for r in G2}

def stat_disp(s):
    key = 'unit_stat_localisations_onscreen_name_' + s
    return statloc.get(key, s)

def attr_disp(a):
    key = 'unit_attributes_bullet_text_' + a
    v = attrloc.get(key, a)
    return v.split('||')[0]

out = []
for i, e in enumerate(mine, start=465):
    blk = {'n': i, **e, 'keys_data': {}}
    for k in e['keys']:
        kd = {}
        rows = spec_idx.get(k)
        if rows:
            r = rows[0]
            kd['spec'] = {spec_hdr[j]: (r[j] if j < len(r) else '') for j in range(len(spec_hdr))}
        g = g2_idx.get(k)
        kd['grouped2'] = (dict(zip(['key', 'trigger_cat', 'target_cat', 'owner_cat', 'family'], g)) if g else None)
        urows = ub_idx.get(k)
        if urows and len(urows[0]) > 4:
            kd['ub_type'] = urows[0][4]
            kd['ub_uniqueness'] = urows[0][7] if len(urows[0]) > 7 else ''
            kd['ub_source_type'] = urows[0][9] if len(urows[0]) > 9 else ''
        kd['onscreen_name'] = ubl.get('unit_abilities_onscreen_name_' + k)
        kd['tooltip'] = ubl.get('unit_abilities_tooltip_text_' + k)
        # phase junctions + phase rows
        phs = []
        for r in pj_idx.get(k, []):
            phase = r[5] if len(r) > 5 else ''
            prec = {'phase': phase, 't_self': r[2], 't_friends': r[3], 't_enemies': r[4]}
            det = None
            drows = ph_idx.get(phase)
            if drows:
                d = {ph_hdr[j]: (drows[0][j] if j < len(drows[0]) else '') for j in range(len(ph_hdr))}
                keep = ['effect_type', 'duration', 'heal_amount', 'barrier_heal_amount', 'damage_amount',
                        'max_damaged_entities', 'affects_allies', 'affects_enemies', 'resurrect',
                        'fatigue_change_ratio', 'imbue_magical', 'imbue_ignition', 'imbue_contact',
                        'requested_stance', 'cant_move', 'hp_change_frequency', 'execute_ratio', 'spreading']
                det = {kk: d.get(kk, '') for kk in keep}
            prec['detail'] = det
            phs.append(prec)
        kd['phase_junc'] = phs
        # stat effects + attributes for all phases
        se = []
        for r in pj_idx.get(k, []):
            phase = r[5] if len(r) > 5 else ''
            for s in sps_idx.get(phase, []):
                se.append(f"{stat_disp(s[1])}: {s[2]} ({s[3]}) [phase {phase}]")
        kd['stat_effects'] = se
        at = []
        for r in pj_idx.get(k, []):
            phase = r[5] if len(r) > 5 else ''
            for a in pae_idx.get(phase, []):
                at.append(f"{attr_disp(a[0])} ({a[2]}) [phase {phase}]")
        kd['attributes'] = at
        eff = [r[1] for r in junc_idx.get(k, [])]
        kd['ui_effects'] = eff
        kd['ui_effects_text'] = [ual.get('unit_abilities_additional_ui_effects_localised_text_' + x, '??' + x) for x in eff]
        kd['phase_ui_effects'] = [r[0] for r in p2u_idx.get(k, [])]
        kd['invalid_usage'] = [r[0] for r in invu_idx.get(k, [])]
        kd['invalid_target'] = [r[0] for r in invt_idx.get(k, [])]
        kd['auto_deactivate'] = [r[0] for r in adr_idx.get(k, [])]
        blk['keys_data'][k] = kd
    out.append(blk)

json.dump(out, open(os.path.join(OUT, '_slice09_gamedata.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("wrote _slice09_gamedata.json")

# ---- readable dump ----
buf = []
for blk in out:
    buf.append("=" * 100)
    buf.append(f"### [{blk['n']}] {blk['marker']}  |  {blk['name']}  |  trigger={blk['trigger']}")
    for k, kd in blk['keys_data'].items():
        buf.append(f"  --- KEY: {k}")
        sp = kd.get('spec')
        if sp:
            keep = ['active_time', 'recharge_time', 'num_uses', 'effect_range', 'affect_self',
                    'num_effected_friendly_units', 'num_effected_enemy_units', 'target_friends',
                    'target_enemies', 'target_ground', 'target_intercept_range', 'always_affect_self',
                    'only_affect_target', 'wind_up_time', 'passive', 'bombardment', 'activated_projectile',
                    'mana_cost', 'min_range', 'ai_usage', 'miscast_chance']
            buf.append("      spec: " + " ; ".join(f"{x}={sp.get(x,'')}" for x in keep))
        g = kd.get('grouped2')
        if g:
            buf.append(f"      grouped2: trigger_cat={g.get('trigger_cat')} target_cat={g.get('target_cat')} owner={g.get('owner_cat')} family={g.get('family')}")
        buf.append(f"      ub_type={kd.get('ub_type')} source={kd.get('ub_source_type')} uniqueness={kd.get('ub_uniqueness')}")
        for p in kd.get('phase_junc', []):
            buf.append(f"      phase_junc: {p['phase']} self={p['t_self']} friends={p['t_friends']} enemies={p['t_enemies']}")
            d = p.get('detail')
            if d:
                buf.append("        phase_row: " + " ; ".join(f"{a}={b}" for a, b in d.items() if b not in ('', 'false', '0', '0.0000')))
        for s in kd.get('stat_effects', []):
            buf.append("      stat: " + s)
        for a in kd.get('attributes', []):
            buf.append("      attr: " + a)
        for t in kd.get('ui_effects_text', []):
            buf.append("      ui: " + t)
        for t in kd.get('phase_ui_effects', []):
            buf.append("      phase_ui: " + t)
        if kd.get('invalid_usage'): buf.append("      invalid_usage: " + ", ".join(kd['invalid_usage']))
        if kd.get('invalid_target'): buf.append("      invalid_target: " + ", ".join(kd['invalid_target']))
        if kd.get('auto_deactivate'): buf.append("      auto_deactivate: " + ", ".join(kd['auto_deactivate']))
        if kd.get('tooltip'): buf.append("      tooltip: " + kd['tooltip'])
        if kd.get('onscreen_name'): buf.append("      loc_name: " + kd['onscreen_name'])
open(os.path.join(OUT, '_slice09_gamedata.txt'), 'w', encoding='utf-8').write("\n".join(buf))
print("wrote _slice09_gamedata.txt")
print("missing keys:", [ (blk['n'], k) for blk in out for k in blk['keys_data'] if 'spec' not in blk['keys_data'][k] ])
