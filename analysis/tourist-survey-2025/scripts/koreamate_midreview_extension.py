"""Additional exploratory analyses for Korea Mate interim EDA review.

Input: 2025_eda_raw.csv (respondent-level private original; never published).
Output: only aggregated stats JSON; no identifying records.
"""
from pathlib import Path
import json, csv
import numpy as np

ROOT=Path(__file__).parent
NEED=['weight','Q1','D_NUM','D_NAT','D_SEX','D_AGE','D_MON','TYP', 'Q4_2a_dk']
NEED += [f'Q3_1a{i}' for i in (1,2,3)]
NEED += [f'Q8a{i:02d}' for i in range(1,17)]
NEED += [f'Q4_2a{i}' for i in (1,2,3)]
NEED += [f'Q4_1a{i}' for i in (1,2,3)]
DATA=[]
with open(ROOT/'2025_eda_raw.csv','r',encoding='utf-8',newline='') as f:
    reader=csv.DictReader(f)
    for row in reader:
        DATA.append([float(row[k]) if row[k] not in ('',None) else np.nan for k in NEED])
a=np.asarray(DATA,dtype=float)
d={k:a[:,i] for i,k in enumerate(NEED)}
w=d['weight'];ok=np.isfinite(w)&(w>0);eligible=ok&np.isin(d['Q1'],(1,2))
wants=np.stack([d[f'Q3_1a{i}'] for i in range(1,4)],axis=1)
lacks=np.stack([d[f'Q4_2a{i}'] for i in range(1,4)],axis=1)
source=np.stack([d[f'Q4_1a{i}'] for i in range(1,4)],axis=1)
ACT={1:'식도락',2:'쇼핑',3:'자연경관',5:'고궁·역사',7:'박물관·전시',8:'K-pop·촬영지',10:'지역 축제',13:'뷰티·미용서비스'}

def pct(mask,base):
    b=base&ok
    return round(100*w[b&mask].sum()/w[b].sum(),2) if b.any() else None

def n_eff(m):
    z=w[m&ok]
    return round(z.sum()**2/(z*z).sum(),1) if len(z) else None

def group_num(m):
    return {'n':int(m.sum()),'n_eff':n_eff(m)}

out={'source':'2025년 외래관광객조사 원자료, 응답자별 CSV를 집계 후 폐기 가능','n_total':len(w),'n_eligible':int(eligible.sum()),'elig_q3_answered':int((eligible&np.isfinite(d['Q3_1a1'])).sum()),'analysis_date':'2026-10-15','group':{},'activity_conversion':[],'monthly':[],'conditional_info_gap':[],'country_visit':[]}

for v,label in [(eligible,'여가·친지 방문'),(eligible&(d['D_NUM']==1),'첫 방문 (여가/친지)'),(eligible&(d['D_NUM']>1),'재방문 (여가/친지)')]:
    out['group'][label]={**group_num(v),'no_info_gap_pct':pct(d['Q4_2a_dk']==11,v),'sns_platform_pct':pct(np.any(source==5,axis=1),v)}

for c,name in ACT.items():
    want=np.any(wants==c,axis=1)
    done=d[f'Q8a{c:02d}']==c
    gap=eligible&want&~done
    completed=eligible&want&done
    nogap=d['Q4_2a_dk']==11
    hallyu=np.any(lacks==7,axis=1)
    trans=np.any(lacks==2,axis=1)
    visiting=np.any(lacks==1,axis=1)
    r={'code':c,'activity':name,'n_want':int((eligible&want).sum()),'want_weight_pct':pct(want,eligible),'do_given_want_pct':pct(done,eligible&want),'missing_action_given_want_pct':pct(~done,eligible&want),'n_gap':int(gap.sum()),'gap_neff':n_eff(gap),'n_done':int(completed.sum()),'done_neff':n_eff(completed)}
    for k,m in [('considered_not_done',gap),('considered_done',completed)]:
        r[k]={'n':int(m.sum()),'no_info_gap_pct':pct(nogap,m),'lack_hallyu_pct':pct(hallyu,m),'lack_transport_pct':pct(trans,m),'lack_visiting_pct':pct(visiting,m)}
    out['activity_conversion'].append(r)

for month in range(1,13):
    m=eligible&(d['D_MON']==month)
    result={'month':month,'n':int(m.sum()),'weighted_sample_pct':pct(m,eligible)}
    for c,name in ACT.items():result[name]=pct(d[f'Q8a{c:02d}']==c,m)
    out['monthly'].append(result)

for c,cname in [(1,'중국'),(2,'일본'),(3,'대만'),(4,'미국')]:
    for rep,desc in [(False,'첫 방문'),(True,'재방문')]:
        m=eligible&(d['D_NAT']==c)&((d['D_NUM']>1) if rep else (d['D_NUM']==1))
        r={'country':cname,'visit':desc,**group_num(m)}
        for activity,name in [(3,'자연경관'),(7,'박물관·전시'),(8,'K-pop·촬영지'),(13,'뷰티·미용서비스')]:r[name]=pct(d[f'Q8a{activity:02d}']==activity,m)
        out['country_visit'].append(r)

(ROOT/'KoreaMate_중간검토_추가집계.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('group',json.dumps(out['group'],ensure_ascii=False))
for z in out['activity_conversion']:
    print(z['activity'],'want_n',z['n_want'],'do among wanted',z['do_given_want_pct'],'n not done',z['n_gap'],'info no gap',z['considered_not_done']['no_info_gap_pct'],'vs done',z['considered_done']['no_info_gap_pct'],'hallyu gaps',z['considered_not_done']['lack_hallyu_pct'],z['considered_done']['lack_hallyu_pct'])
print('monthly examples',json.dumps(out['monthly'][:2]+out['monthly'][-2:],ensure_ascii=False))