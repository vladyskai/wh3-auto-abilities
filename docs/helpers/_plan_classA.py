import json, math
o=json.load(open('WH3_audit/_classA_joined.json',encoding='utf-8'))

# real range -> constant NAME (value computed with the epsilon floor the build asserts)
def bound(real): return int(real*0.70 + 1e-9)
CR = {15:'FOURTH.ENEMY_CAST_R15',20:'FOURTH.ENEMY_CAST_R20',30:'FOURTH.ENEMY_CAST_R30',
      35:'FOURTH.ENEMY_CAST_R35',50:'FOURTH.ENEMY_CAST_R50',70:'FOURTH.ENEMY_CAST_R70',
      75:'FOURTH.ENEMY_CAST_R75',100:'FOURTH.ENEMY_CAST_R100',150:'FOURTH.ENEMY_CAST_R150',
      180:'FOURTH.ENEMY_CAST_R180',200:'FOURTH.ENEMY_CAST_R200',500:'FOURTH.ENEMY_CAST_R500'}

plan=[]
for x in o:
    if x['num']==263: continue
    real=int(round(x['range_real']))
    assert real in CR, (x['num'], real)
    trig='enemy_ground_area' if x['ground'] else 'enemy_engaged_or_shot'
    plan.append({'num':x['num'],'name':x['name'],'marker':x['mod_markers'][0],
                 'keys':x['keys'],'real':real,'const':CR[real],'bound':bound(real),
                 'trigger':trig,'ground':x['ground']})
json.dump(plan, open('WH3_audit/_classA_impl_plan.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
from collections import Counter
print('plan entries:', len(plan))
print('unit:', sum(1 for p in plan if not p['ground']), 'ground:', sum(1 for p in plan if p['ground']))
print('trigger counts:', Counter(p['trigger'] for p in plan))
print('constant counts:', Counter(p['const'] for p in plan))
# ground keys
gkeys=[k for p in plan if p['ground'] for k in p['keys']]
print('ground keys (%d):'%len(gkeys))
for k in gkeys: print('  ',k)
# constants
seenc={}
for p in plan:
    seenc[p['const']]=p['bound']
print('constants:')
for c in sorted(seenc, key=lambda c:int(''.join(ch for ch in c if ch.isdigit()))):
    print('  ',c,'=',seenc[c])
