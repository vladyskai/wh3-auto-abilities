import re, json
from collections import Counter, defaultdict

TSV='WH3_project_archive/research/wh3/unit_spec_abil.tsv'
MOD='WH3_mod/mod_source/script/battle/mod/zz_test_deadly_onslaught.lua'

# --- TSV ---
rows=open(TSV,encoding='utf-8').read().split('\n')
hdr=rows[0].split('\t')
idx={h:i for i,h in enumerate(hdr)}
tsv={}
for r in rows[1:]:
    if not r.strip(): continue
    c=r.split('\t')
    if len(c)<=idx['target_intercept_range']: continue
    key=c[0]
    def g(f):
        i=idx[f]
        return c[i] if i<len(c) else ''
    tsv[key]={'intercept':g('target_intercept_range'),'effect':g('effect_range'),
              'ground':g('target_ground'),'enemies':g('target_enemies'),
              'num_enemy':g('num_effected_enemy_units'),'self':g('target_self'),
              'friends':g('target_friends'),'gund_enern':g('target_ground_under_enemies'),
              'gund_allies':g('target_ground_under_allies')}
print('TSV keys:', len(tsv))

# --- report Class A ---
recs=json.load(open('WH3_audit/_classA_parsed.json',encoding='utf-8'))

# --- mod ABILITIES table entries ---
modtxt=open(MOD,encoding='utf-8').read()
ent_re=re.compile(r'\{\s*marker\s*=\s*"([^"]+)"\s*,\s*name\s*=\s*"([^"]*)"\s*,\s*trigger\s*=\s*"([^"]+)"\s*,\s*\n\s*badge\s*=\s*"([^"]*)"\s*,\s*\n\s*keys\s*=\s*\{([^}]*)\}', re.S)
mod_entries=[]
for m in ent_re.finditer(modtxt):
    keys=re.findall(r'"([^"]+)"', m.group(5))
    mod_entries.append({'marker':m.group(1),'name':m.group(2),'trigger':m.group(3),'keys':keys})
print('mod entries parsed:', len(mod_entries))
trig_ct=Counter(e['trigger'] for e in mod_entries)
print('triggers:', dict(trig_ct))
key2me=defaultdict(list)
for e in mod_entries:
    for k in e['keys']: key2me[k].append(e)

# --- join ---
out=[]
unmapped=[]
for r in recs:
    keys=r['keys']
    # real range: prefer report intercept, else TSV intercept
    range_real=r['intercept']
    src='report'
    ground=r['ground']
    area=r['area']
    # enrich from TSV per key
    tkeys=[tsv.get(k) for k in keys]
    if any(t is None for t in tkeys):
        miss=[k for k,t in zip(keys,tkeys) if t is None]
    else:
        miss=[]
    if range_real is None:
        for t,k in zip(tkeys,keys):
            if t and t['intercept'] not in ('','0.0000'):
                range_real=float(t['intercept']); src='tsv'; break
        if range_real is None and tkeys and tkeys[0]:
            range_real=float(tkeys[0]['intercept']); src='tsv0'
    # ground from TSV
    tg = any((t and t['ground']=='true') for t in tkeys)
    if tg: ground=True
    bound=None if range_real is None else int(range_real*0.70)
    # mod entry match
    mes=[]
    for k in keys:
        mes += key2me.get(k,[])
    mes_uniq={}
    for e in mes: mes_uniq[e['marker']]=e
    out.append({'num':r['num'],'name':r['name'],'keys':keys,'range_real':range_real,
                'rsrc':src,'ground':ground,'area':area,'bound':bound,
                'mod_markers':list(mes_uniq.keys()),
                'mod_triggers':sorted(set(e['trigger'] for e in mes_uniq.values())),
                'missing_keys':miss})
json.dump(out, open('WH3_audit/_classA_joined.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)

print('\n== range from report:', sum(1 for o in out if o['rsrc']=='report'),
      ' from tsv:', sum(1 for o in out if o['rsrc'].startswith('tsv')))
print('== range_real still None:', [(o['num'],o['name'],o['keys']) for o in out if o['range_real'] is None])
print('== ground (report or tsv):', [(o['num'],o['name'],o['range_real']) for o in out if o['ground']])
print('== bound distribution:', dict(sorted(Counter(o['bound'] for o in out).items(), key=lambda x:(x[0] is None,x[0]))))
print('== entries with NO mod marker:', [(o['num'],o['name'],o['keys']) for o in out if not o['mod_markers']])
print('== entries missing TSV key:', [(o['num'],o['name'],o['missing_keys']) for o in out if o['missing_keys']])
print('== entries whose mod trigger is already enemy:', [(o['num'],o['name'],o['mod_triggers']) for o in out if o['mod_triggers'] and o['mod_triggers']!=['melee_unwavering']])
print('== all mod_triggers set:', dict(Counter(tuple(o['mod_triggers']) for o in out)))
