# -*- coding: utf-8 -*-
import json, os, csv
T = os.path.expandvars(r'%LOCALAPPDATA%\Temp\wh3')
U = os.path.join(T, 'uieff')

def load_tsv(path):
    rows=[]
    with open(path, encoding='utf-8-sig', newline='') as f:
        for r in csv.reader(f, delimiter='\t'):
            rows.append(r)
    return [r for r in rows if r and not r[0].startswith('#')]

PH = load_tsv(os.path.join(T,'phases.tsv')); ph_hdr = PH[0]
ph_idx = {}
for r in PH[1:]:
    ph_idx.setdefault(r[0], []).append(r)
SPS = load_tsv(os.path.join(U,'special_ability_phase_stat_effects.tsv')); sps_idx={}
for r in SPS[1:]:
    sps_idx.setdefault(r[0], []).append(r)
PAE = load_tsv(os.path.join(U,'phase_attribute_effects.tsv')); pae_idx={}
for r in PAE[1:]:
    pae_idx.setdefault(r[1], []).append(r)

data = json.load(open(r'C:\Users\vlady\Desktop\WH3_mod\audit\_slice05_gamedata.json', encoding='utf-8'))

SPEC_FIELDS = ['active_time','recharge_time','num_uses','effect_range','affect_self',
 'num_effected_friendly_units','num_effected_enemy_units','target_friends','target_enemies',
 'target_ground','target_self','target_ground_under_allies','target_ground_under_enemies',
 'always_affect_self','only_affect_target','passive','mana_cost','min_range','ai_usage',
 'special_ability_display','additional_melee_cp','additional_missile_cp','affect_siege_equipment',
 'intensity_based_activation','can_be_copied_to_transformation_unit','unique_id']
PH_FIELDS = ['duration','effect_type','requested_stance','cant_move','freeze_fatigue','hp_change_frequency',
 'damage_amount','max_damaged_entities','resurrect','mana_regen_mod','imbue_magical','imbue_ignition','imbue_contact',
 'is_hidden_in_ui','affects_allies','affects_enemies','replenish_ammo','spreading','freeze_recharge','heal_amount',
 'barrier_heal_amount','remove_magical','execute_ratio']

out = []
for blk in data:
    L = []
    L.append("="*100)
    L.append(f"### [{blk['n']}] {blk['marker']}  |  {blk['name']}  |  trigger={blk['trigger']}")
    for k, kd in blk['keys_data'].items():
        L.append(f"  --- KEY: {k}")
        if kd.get('loc_name'): L.append(f"      loc_name: {kd['loc_name']}")
        sp = kd.get('spec') or {}
        vals = []
        for f in SPEC_FIELDS:
            v = sp.get(f, '')
            if v not in ('', 'false', '0', '0.0000', None):
                vals.append(f"{f}={v}")
        L.append("      spec: " + " ; ".join(vals))
        for pj in kd.get('phase_junc', []):
            L.append(f"      phase_junc: phase={pj['phase']} self={pj['target_self']} friends={pj['target_friends']} enemies={pj['target_enemies']}")
            for pr in ph_idx.get(pj['phase'], []):
                row = {ph_hdr[i]: (pr[i] if i < len(pr) else '') for i in range(len(ph_hdr))}
                vv = []
                for f in PH_FIELDS:
                    v = row.get(f, '')
                    if v not in ('', 'false', '0', '0.0000', None):
                        vv.append(f"{f}={v}")
                L.append("        phase_row: " + " ; ".join(vv))
                # stat effects / attributes for this phase
                se = sps_idx.get(pj['phase'])
                if se:
                    L.append("        stat_effects: " + " ; ".join(f"{r[1]} {r[3]} {r[2]}" for r in se))
                ae = pae_idx.get(pj['phase'])
                if ae:
                    L.append("        attributes: " + " ; ".join(f"{r[0]}({r[2]})" for r in ae))
        if kd.get('ui_effects_text'):
            L.append("      ui_effects: " + " | ".join(kd['ui_effects_text']))
        if kd.get('invalid_usage'): L.append("      invalid_usage_flags: " + ", ".join(kd['invalid_usage']))
        if kd.get('invalid_target'): L.append("      invalid_target_flags: " + ", ".join(kd['invalid_target']))
        if kd.get('auto_deactivate'): L.append("      auto_deactivate: " + ", ".join(kd['auto_deactivate']))
        if kd.get('sag_groups'): L.append("      sag_groups: " + ", ".join(kd['sag_groups']))
        if kd.get('uset'): L.append("      unit_sets: " + ", ".join(kd['uset']))
        if kd.get('ub_type'): L.append("      ub_type: " + kd['ub_type'])
        if kd.get('loc_tooltip'): L.append("      tooltip: " + kd['loc_tooltip'])
    out.append("\n".join(L))

open(r'C:\Users\vlady\Desktop\WH3_mod\audit\_slice05_gamedata.txt','w',encoding='utf-8').write("\n".join(out))
print("wrote _slice05_gamedata.txt;", len(out), "blocks")
