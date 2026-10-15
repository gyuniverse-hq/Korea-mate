"""Diagnostic robustness checks of interim findings; produces only aggregate JSON."""
import json,csv,numpy as np
from pathlib import Path
base=Path(__file__).resolve().parent
columns=['weight','Q1','D_NAT','D_NUM','D_AGE','D_SEX','Q4_2a_dk','Q3_1a1','Q3_1a2','Q3_1a3','Q8a01','Q8a02','Q8a05','Q8a06','Q8a07','Q8a08','Q8a09','Q8a13','Q4_2a1','Q4_2a2','Q4_2a3']
vals=[]
for r in csv.DictReader(open(base/'2025_eda_raw.csv',encoding='utf8',newline='')):
 vals.append([float(r[k]) if r[k] else np.nan for k in columns])
z=np.asarray(vals);d={k:z[:,i] for i,k in enumerate(columns)}
w=d['weight'];elig=np.isin(d['Q1'],[1,2])&np.isfinite(w)&(w>0);W=np.column_stack([d[f'Q3_1a{i}'] for i in range(1,4)])
no_gap=d['Q4_2a_dk']==11
rng=np.random.default_rng(321)
res={'activity_info_gaps':[],'country_associations':[]}
for code,name in [(1,'식도락'),(2,'쇼핑'),(8,'K-pop·촬영지'),(13,'뷰티·미용서비스')]:
 want=np.any(W==code,axis=1);done=d[f'Q8a{code:02d}']==code
 m=elig&want; ids=np.flatnonzero(m)
 def delta(t):
  ww=w[t];is_gap=~done[t]; is_done=done[t]
  return (np.sum(ww[is_gap]*no_gap[t][is_gap])/ww[is_gap].sum() -np.sum(ww[is_done]*no_gap[t][is_done])/ww[is_done].sum())*100
 estimate=delta(ids)
 b=[]
 for _ in range(850):
  take=rng.choice(ids,size=len(ids),replace=True)
  if (~done[take]).any() and done[take].any():b.append(delta(take))
 ci=np.quantile(b,[.025,.975])
 res['activity_info_gaps'].append({'activity':name,'want_n':int(m.sum()),'gap_n':int((m&~done).sum()),'done_n':int((m&done).sum()),'none_gap_minus_completed_pp':round(float(estimate),2),'bootstrap95_approx_pp':[round(float(ci[0]),2),round(float(ci[1]),2)]})

for nat,name in [(1,'중국'),(2,'일본'),(3,'대만'),(4,'미국')]:
 m=elig&(d['D_NAT']==nat)
 if not m.any():continue
 wt=w[m]
 for a,b,name_a,name_b in [(8,9,'K-pop·촬영지','공연'),(6,7,'전통문화','박물관·전시'),(13,2,'뷰티·미용서비스','쇼핑')]:
  A=(d[f'Q8a{a:02d}']==a)[m];B=(d[f'Q8a{b:02d}']==b)[m]
  pA=np.sum(wt*A)/wt.sum();pB=np.sum(wt*B)/wt.sum();pAB=np.sum(wt*A*B)/wt.sum()
  lift=pAB/pA/pB if pA*pB else None
  res['country_associations'].append({'country':name,'activity_a':name_a,'activity_b':name_b,'n_country':int(m.sum()),'n_a':int(A.sum()),'n_b':int(B.sum()),'n_both':int((A&B).sum()),'lift':round(float(lift),2) if lift is not None else None})

(base/'KoreaMate_중간검토_강건성점검.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf8')
for r in res['activity_info_gaps']:print('INFO',r)
for r in res['country_associations']:print('LIFT',r)