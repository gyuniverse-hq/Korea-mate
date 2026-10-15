"""Korea Mate EDA v3: respondent-level raw input -> anonymous aggregate JSON/CSV.
No respondent-level data is exported. Requires user-provided 2025_eda_raw.csv next to this script.
Model: survey-weighted linear probability descriptive association, HC3 exploratory variance
(no full complex survey design available; no causal identification).
"""
from pathlib import Path
import csv, json
import numpy as np

BASE=Path(__file__).resolve().parent
ACT={1:'식도락',2:'쇼핑',3:'자연경관',4:'휴양·휴식',5:'고궁·역사',6:'전통문화체험',7:'박물관·전시',8:'K-pop·촬영지',9:'공연',10:'지역 축제',11:'유흥',12:'테마파크·오락',13:'뷰티·미용서비스'}
INFO={1:'방문지·운영정보',2:'교통·동선',3:'음식·맛집',4:'쇼핑',5:'숙박',6:'지역 축제·행사',7:'한류문화 체험',8:'금융·환전',9:'통신·인터넷',10:'기타'}
NAT={1:'중국',2:'일본',3:'대만',4:'미국',5:'홍콩',6:'태국',7:'베트남',8:'말레이시아',9:'필리핀',10:'싱가포르',11:'러시아',12:'중동',13:'인도네시아',14:'캐나다',15:'호주',16:'영국',17:'몽골',18:'독일',19:'프랑스',20:'인도',97:'기타'}
need=['weight','Q1','D_NUM','D_NAT','D_AGE','D_SEX','TYP','D_MON','Q4_2a_dk']+[f'Q4_2a{i}' for i in range(1,4)]+[f'Q3_1a{i}' for i in range(1,4)]+[f'Q8a{i:02d}' for i in ACT]+['Q12a18','Q12a22','Q12a23','Q12a26']
raw=[]
with (BASE/'2025_eda_raw.csv').open(encoding='utf-8',newline='') as f:
 reader=csv.DictReader(f)
 assert set(need)<=set(reader.fieldnames),set(need)-set(reader.fieldnames)
 for record in reader:
  raw.append([float(record[k]) if record[k] else np.nan for k in need])
z=np.asarray(raw,dtype=np.float64)
d={k:z[:,i] for i,k in enumerate(need)}
n=len(z);w=d['weight']
assert n==16110 and np.all(np.isfinite(w)) and np.all(w>0)
main=np.isin(d['Q1'],(1,2))
assert int(main.sum())==12339
W=np.column_stack([d[f'Q3_1a{i}'] for i in range(1,4)])
I=np.column_stack([d[f'Q4_2a{i}'] for i in range(1,4)])
no_info=d['Q4_2a_dk']==11
info_known=np.any(np.isin(I,list(INFO)),axis=1)
assert np.all(no_info != info_known),'no gap response must match any specified gap'

# Matrix columns are interpretable dummies with a single prefix. Exclude the first category in each factor.
def makeX(ids,predictor,adjusters=['D_NAT','D_AGE','D_SEX','Q1','TYP','D_MON']):
 cols=['intercept','exposure']; x=[np.ones(len(ids)),np.asarray(predictor,dtype=float)]
 for name in adjusters:
  v=d[name][ids]
  un=np.sort(np.unique(v[np.isfinite(v)]))
  for code in un[1:]:
   x.append((v==code).astype(float))
   cols.append(f'{name}={int(code)}')
 return np.column_stack(x),cols

def wstats(ids,outcome):
 ww=w[ids];yy=np.asarray(outcome,dtype=float)
 return float(np.average(yy,weights=ww)) if len(yy) else None

def ess(ids):
 ww=w[ids]
 return float((ww.sum()**2)/(ww@ww)) if len(ww) else 0

def adj_estimation(ids,exposure,outcomes,adjusters,alpha=0.05):
 """LPM exposure coefficient = covariate-adjusted percentage-point difference.
    HC3 approximate confidence bands, NOT official design-based intervals."""
 xx,names=makeX(ids,exposure,adjusters)
 yy=np.asarray(outcomes,dtype=float)
 if yy.ndim==1:yy=yy[:,None]
 wi=w[ids]/np.mean(w[ids]); N,p=xx.shape
 try:
  inv=np.linalg.inv(xx.T@(wi[:,None]*xx))
 except np.linalg.LinAlgError:
  return None
 beta=inv@(xx.T@(wi[:,None]*yy))
 fitted=xx@beta
 resid=yy-fitted
 leverage=wi*np.sum((xx@inv)*xx,axis=1)
 q=xx@inv[:,1]
 contrib=wi*q
 # HC3 adjustment, weighted least squares as pseudoweights for exploratory comparison
 stderr=np.sqrt((np.square(contrib[:,None]*resid)/np.square(np.maximum(1-leverage,1e-5)[:,None])).sum(axis=0))
 out=[]
 for k in range(yy.shape[1]):
  effect=float(beta[1,k]);se=float(stderr[k]);
  out.append({'adjusted_pp':round(100*effect,2),'hc3_approx_95_low_pp':round(100*(effect-1.96*se),2),'hc3_approx_95_high_pp':round(100*(effect+1.96*se),2),'approx_se_pp':round(100*se,2)})
 return {'out':out,'num_controls':p-2,'max_leverage':round(float(leverage.max()),4),'n':N}

out={'metadata':{'source':'사용자 제공 2025 외래관광객조사 원자료 16110명/코드북','analysis_population':'Q1=1 또는 2 (여가·친지 방문), 12339명','method':'Σ(wy)/Σ(w), 조정 비교: 국가/연령/성별/주목적/여행형태/조사월을 포함한 가중 LPM 및 HC3 근사 범위','inference_caveat':'전후적 인과관계 미검증, 가중치 재추정/층화/집락 없는 근사적 구간, 동시 조사한 사후 응답','n_all':n,'n_main':int(main.sum()),'eff_n_main':round(ess(main),1),'no_info_match':bool(np.all(no_info!=info_known))},'first_repeat':[],'country_first_repeat':[],'activity_friction':[],'info_overview':[],'satisfaction':[]}
# 1) visitation adjustment: first=0, repeat=1
ids=np.flatnonzero(main)
rep=(d['D_NUM'][ids]>1).astype(float)
y=np.column_stack([(d[f'Q8a{k:02d}'][ids]==k).astype(float) for k in ACT])
fit=adj_estimation(ids,rep,y,['D_NAT','D_AGE','D_SEX','Q1','TYP','D_MON'])
for j,(code,label) in enumerate(ACT.items()):
 a=ids[rep==0];b=ids[rep==1]
 first=wstats(a,y[rep==0,j]);repeat=wstats(b,y[rep==1,j]);curr=fit['out'][j]
 out['first_repeat'].append({'code':code,'activity':label,'n_first':len(a),'n_repeat':len(b),'first_pct':round(100*first,2),'repeat_pct':round(100*repeat,2),'crude_diff_pp':round(100*(repeat-first),2),**curr,'interval_crosses_zero':bool(curr['hc3_approx_95_low_pp']<=0<=curr['hc3_approx_95_high_pp'])})

# 2) four major markets, descriptive adjusted after controlling age sex purpose type and month.
for nat,name in [(1,'중국'),(2,'일본'),(3,'대만'),(4,'미국'),(5,'홍콩'),(7,'베트남')]:
 country_ids=np.flatnonzero(main&(d['D_NAT']==nat));r=(d['D_NUM'][country_ids]>1).astype(float)
 if (r==0).sum()<70 or (r==1).sum()<70:continue
 selected=[3,5,7,8,13]
 Y=np.column_stack([(d[f'Q8a{k:02d}'][country_ids]==k).astype(float) for k in selected])
 fitted=adj_estimation(country_ids,r,Y,['D_AGE','D_SEX','Q1','TYP','D_MON'])
 for j,code in enumerate(selected):
  raw0=wstats(country_ids[r==0],Y[r==0,j]);raw1=wstats(country_ids[r==1],Y[r==1,j]);rr=fitted['out'][j]
  out['country_first_repeat'].append({'country':name,'n_country':len(country_ids),'n_first':int((r==0).sum()),'n_repeat':int((r==1).sum()),'activity':ACT[code],'first_pct':round(raw0*100,2),'repeat_pct':round(raw1*100,2),'crude_diff_pp':round(100*(raw1-raw0),2),**rr})

# 3) Information-gaps overall -> categories by eligibility and first/repeat
for code,label in INFO.items():
 select=np.any(I[main]==code,axis=1)
 out['info_overview'].append({'info_code':code,'information':label,'n':int(select.sum()),'weighted_pct':round(wstats(ids,select)*100,2),'among_any_gap_pct':round(wstats(ids[info_known[ids]],np.any(I[ids[info_known[ids]]]==code,axis=1))*100,2)})

# 4) Friction: among those who selected activity in top3 before trip, how info lack relates to not completing
#  EDA only; no reason for missed experience asked. Control country/age/sex/first-repeat/purpose/type/month.
paired={1:[3,1,2],2:[4,1,2],8:[7,6,1,2],13:[1,2,4]}
for code,info_codes in paired.items():
 wanted=main&np.any(W==code,axis=1);s=np.flatnonzero(wanted)
 miss=(d[f'Q8a{code:02d}'][s]!=code).astype(float)
 if len(s)==0:continue
 na=s[miss==1];nb=s[miss==0]
 # adjust D_NUM separately; includes visitation count as categories to reduce cofounding
 targets=[('any',info_known[s]),('none',no_info[s])]+[(c,np.any(I[s]==c,axis=1)) for c in info_codes]
 yy=np.column_stack([v.astype(float) for _,v in targets]);adj=adj_estimation(s,miss,yy,['D_NAT','D_AGE','D_SEX','D_NUM','Q1','TYP','D_MON'])
 for j,(c,vec) in enumerate(targets):
  raw_missing=wstats(na,vec[miss==1]);raw_done=wstats(nb,vec[miss==0]);stat=adj['out'][j]
  pos_m=int(vec[miss==1].sum());pos_d=int(vec[miss==0].sum())
  out['activity_friction'].append({'activity':ACT[code],'activity_code':code,'info_type':'정보 부족 유형 1개 이상' if c=='any' else '부족 정보 없음' if c=='none' else INFO[c], 'info_code':c,'n_wanted':len(s),'n_notdone':len(na),'n_done':len(nb),'positive_notdone':pos_m,'positive_done':pos_d,'rate_notdone_pct':round(100*raw_missing,2),'rate_done_pct':round(100*raw_done,2),'crude_diff_pp':round(100*(raw_missing-raw_done),2),**stat,'sparse_flag':bool(min(pos_m,pos_d)<25),'survey_question_limitation':'사후 응답 정보 부족은 해당 활동 전용 질문이 아니며, 미참여 이유를 직접 묻지 않음'})

# 5) Additional context: perceived satisfaction; don't confuse with info availability or usability
sats={'Q12a18':'언어소통 만족도','Q12a22':'대중교통 만족도','Q12a23':'길찾기 만족도','Q12a26':'디지털 관광정보 만족도'}
for k,name in sats.items():
 v=d[k][ids]; valid=np.isin(v,(1,2,3,4,5)); t=ids[valid]
 if len(t)==0:continue
 rt=d[k][t];exp=d['D_NUM'][t]>1
 for sub,mask in [('전체',np.ones(len(t),bool)),('첫 방문',~exp),('재방문',exp)]:
  rr=rt[mask];ss=t[mask];
  out['satisfaction'].append({'item':name,'group':sub,'n_valid':len(ss),'n_invalid_in_main':int(len(ids)-len(t)),'low_1_2_pct':round(100*wstats(ss,rr<=2),2),'neutral_3_pct':round(100*wstats(ss,rr==3),2),'satisfied_4_5_pct':round(100*wstats(ss,rr>=4),2),'valid_share_in_main_pct':round(100*w[ss].sum()/w[ids].sum(),2)})

JSON=BASE/'KoreaMate_EDA_v3_추가분석_집계.json'
JSON.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
for k in ['first_repeat','country_first_repeat','activity_friction','info_overview','satisfaction']:
 rows=out[k];path=BASE/f'KoreaMate_EDA_v3_{k}.csv'
 with path.open('w',newline='',encoding='utf-8-sig') as f:
  ww=csv.DictWriter(f,fieldnames=list(rows[0].keys()));ww.writeheader();ww.writerows(rows)
 print(k,len(rows),'->',path.name)
print('VISIT')
for r in out['first_repeat']:print(r['activity'],r['crude_diff_pp'],r['adjusted_pp'],r['hc3_approx_95_low_pp'],r['hc3_approx_95_high_pp'])
print('FRICTION')
for r in out['activity_friction']:print(r['activity'],r['info_type'],r['n_notdone'],r['rate_notdone_pct'],r['rate_done_pct'],r['adjusted_pp'],r['hc3_approx_95_low_pp'],r['hc3_approx_95_high_pp'],r['sparse_flag'])
print('SAT')
for r in out['satisfaction']:
 if r['group']=='전체':print(r)