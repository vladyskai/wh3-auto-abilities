import re, json
from collections import Counter
lines = open('WH3_audit_report.md',encoding='utf-8').read().split('\n')
start = next(i for i,l in enumerate(lines) if l.startswith('## Class A'))
end   = next(i for i,l in enumerate(lines) if l.startswith('## Class B'))
sec = lines[start:end]
blocks=[]; cur=None
for l in sec:
    m=re.match(r'^####\s+(\d+)\.\s+(.*?)\s{0,3}\(slice\s+\d+\)\s*$', l)
    if m:
        if cur: blocks.append(cur)
        cur={'num':int(m.group(1)),'name':m.group(2).strip(),'text':[]}
    elif cur is not None:
        cur['text'].append(l)
if cur: blocks.append(cur)
print('entries parsed:', len(blocks))
nums=[b['num'] for b in blocks]
print('first/last nums:', nums[0], nums[-1], 'unique', len(set(nums)))
def getkeys(t):
    ks=[]
    for l in t:
        if l.startswith('- **Key(s):**') or l.startswith('- **Keys:**'):
            ks+=re.findall(r'`([^`]+)`', l)
    return ks
recs=[]
for b in blocks:
    t=b['text']; txt='\n'.join(t)
    ks=getkeys(t)
    m=re.search(r'intercept\s+([\d.]+)\s*m', txt)
    intercept=float(m.group(1)) if m else None
    if intercept is None:
        m=re.search(r'([\d.]+)\s*m range', txt) or re.search(r'\b([\d.]+)\s*m\b', txt)
        intercept=float(m.group(1)) if m else None
    ground = ('target_ground = true' in txt) or ('GROUND' in txt) or ('enemy ground' in txt.lower())
    area = ('num_effected_enemy_units = -1' in txt) or (re.search(r'\d+\s*m area', txt) is not None)
    recs.append({'num':b['num'],'name':b['name'],'keys':ks,'intercept':intercept,'ground':ground,'area':area})
print('with keys:', sum(1 for r in recs if r['keys']), 'no keys:', sum(1 for r in recs if not r['keys']))
print('intercept missing:', [r['num'] for r in recs if r['intercept'] is None])
print('ground:', [(r['num'],r['name'],r['intercept']) for r in recs if r['ground']])
print('area(no ground):', [(r['num'],r['name']) for r in recs if r['area'] and not r['ground']])
print('intercept dist:', dict(sorted(Counter(r['intercept'] for r in recs).items(), key=lambda x:(x[0] is None,x[0]))))
json.dump(recs, open('WH3_audit/_classA_parsed.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote')
