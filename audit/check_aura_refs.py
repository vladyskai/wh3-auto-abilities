# -*- coding: utf-8 -*-
import csv, os
T = os.path.expandvars(r'%LOCALAPPDATA%\Temp\wh3')
def load_tsv(path):
    rows = []
    with open(path, encoding='utf-8-sig', newline='') as f:
        for r in csv.reader(f, delimiter='\t'):
            rows.append(r)
    return [r for r in rows if r and not r[0].startswith('#')]
spec = load_tsv(os.path.join(T, 'unit_spec_abil.tsv')); hdr = spec[0]
sel = ['target_friends','target_enemies','target_ground','target_self','target_ground_under_allies','affect_self','always_affect_self','only_affect_target','effect_range','num_effected_friendly_units','num_effected_enemy_units','target_intercept_range','ai_usage','wind_up_time','passive']
want = ["wh_main_character_abilities_deadly_onslaught","wh_main_character_abilities_foe_seeker","wh_main_spell_bound_hammer_of_sigmar","wh3_dlc29_spell_bound_prayer_winters_chill","wh3_dlc29_ability_bound_prayer_winters_chill","wh3_dlc29_unit_abilities_blood_omens","wh3_dlc29_item_abilities_armour_of_the_burrows"]
for k in want:
    row = next((r for r in spec[1:] if r and r[0] == k), None)
    if not row:
        print("###", k, "NOT FOUND"); continue
    d = {hdr[i]: (row[i] if i < len(row) else '') for i in range(len(hdr))}
    shown = " ; ".join("{0}={1}".format(f, d.get(f)) for f in sel if d.get(f) not in ('', 'false'))
    print("###", k)
    print("   ", shown)
PJ = load_tsv(os.path.join(T, 'phase_junc.tsv'))
for k in ["wh_main_character_abilities_deadly_onslaught","wh_main_character_abilities_foe_seeker"]:
    for r in PJ[1:]:
        if r[1] == k:
            print("PJ:", k, "self=", r[2], "friends=", r[3], "enemies=", r[4], "phase=", r[5])
