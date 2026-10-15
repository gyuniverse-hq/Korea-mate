"""Korea Mate 2025 visitor survey: integration audit + WHEN & WHERE descriptive EDA.

Local execution (requires Python 3.10+ / NumPy):
    python koreamate_step9_10_audit.py --input /path/to/2025_eda_raw.csv --out /path/to/outputs

Privacy: reads individual survey rows locally, writes *only* aggregate tables. The
source microdata and codebook are never copied into the output folder.
No geographic attribution of activities or causal interpretation is possible.
"""
from __future__ import annotations
import argparse, csv, json, math, hashlib, pathlib, collections
import numpy as np

REGIONS = ['서울','경기','인천','강원','대전','충북','충남','세종','경북','경남','대구','울산','부산','광주','전북','전남','제주']
ACTIVITIES = {1:'식도락',2:'쇼핑',3:'자연경관',5:'고궁·역사',7:'박물관·전시',8:'K-pop·촬영지',10:'지역 축제',13:'뷰티·미용서비스'}
CODES = ['pnid','D_MON','D_BUN','D_NAT','D_AGE','D_SEX','D_NUM','Q1','TYP','weight','weight1','weight2','weight3','weight4','Q1_1a1','Q1_1a2','Q1_1a3']
CODES += [f'Q9_2a{i:02d}' for i in range(1,18)]
CODES += [f'Q8a{i:02d}' for i in ACTIVITIES]
NAT_NAMES={1:'중국',2:'일본',3:'대만',4:'미국',5:'홍콩',6:'태국',7:'베트남',8:'말레이시아',9:'필리핀',10:'싱가포르',11:'러시아',12:'중동',13:'인도네시아',14:'캐나다',15:'호주',16:'영국',17:'몽골',18:'독일',19:'프랑스',20:'인도',97:'기타'}

def load(path):
    columns={c:[] for c in CODES}
    with open(path,'r',encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        missing=set(CODES)-set(reader.fieldnames or [])
        if missing: raise ValueError('Missing columns: '+', '.join(sorted(missing)))
        colcount=len(reader.fieldnames)
        for r in reader:
            for c in CODES:
                v=(r[c] or '').strip()
                columns[c].append(float(v) if v else np.nan)
    data={c:np.asarray(v,dtype=np.float64) for c,v in columns.items()}
    return data, colcount

def wmean(mask,indicator,w):
    if not np.any(mask):return None
    x=w[mask];y=indicator[mask]
    return float(np.dot(x,y)/x.sum())

def kish(mask,w):
    a=w[mask]
    return float(a.sum()**2 / np.dot(a,a)) if len(a) else 0.

def write_csv(path,rows):
    if not rows:return
    keys=list(rows[0])
    with open(path,'w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows(rows)

def safe_r(v,d=2): return round(float(v),d) if v is not None and np.isfinite(v) else None

def main(src,out):
    out.mkdir(parents=True,exist_ok=True)
    d,num_columns=load(src)
    n=len(d['pnid']);w=d['weight'];m=d['D_MON'];q=d['D_BUN'];eligible=np.isin(d['Q1'],[1,2]);all_=np.ones(n,dtype=bool)
    region_cols=[f'Q9_2a{i:02d}' for i in range(1,18)]
    rmat=np.column_stack([d[c]==i for i,c in enumerate(region_cols,1)])
    activities={i:(d[f'Q8a{i:02d}']==i) for i in ACTIVITIES}
    qvalid=np.isin(m,range(1,13)) & (q == np.floor((m-1)/3)+1)
    weight_branch=np.column_stack([d['weight1'],d['weight2'],d['weight3'],d['weight4']])
    wwok=[]
    for i in range(4):
        quarter=(q==i+1)
        correct=np.isfinite(weight_branch[:,i]) & np.isclose(weight_branch[:,i],w,atol=1e-5,rtol=1e-9)
        blank_outside=np.all(~np.isfinite(weight_branch[~quarter,i]))
        wwok.append(bool(np.all(correct[quarter]) and blank_outside))
    invalid_region=[];rvals=[]
    for i,c in enumerate(region_cols,1):
        arr=d[c];invalid=int(np.sum(np.isfinite(arr)&(arr!=i)))
        if invalid:invalid_region.append((c,invalid))
        rvals.append(int(np.isfinite(arr).sum()))
    activity_invalid=[]
    for i in ACTIVITIES:
        arr=d[f'Q8a{i:02d}']
        if np.any(np.isfinite(arr)&(arr!=i)):
            activity_invalid.append(i)
    ids=d['pnid']
    qa={'expected_sample':16110,'observed_sample':n,'column_count':num_columns,'unique_ids':int(len(np.unique(ids))),'duplicate_ids':int(n-len(np.unique(ids))),
        'valid_weights':bool(np.all(np.isfinite(w)&(w>0))),'weight_sum':safe_r(w.sum(),2),
        'weight_kish_effective_n':safe_r(kish(all_,w),1),'eligible_n':int(eligible.sum()),
        'eligible_kish_effective_n':safe_r(kish(eligible,w),1),
        'monthly_quarter_consistency':bool(np.all(qvalid)),'quarter_weight_consistency':wwok,
        'invalid_region_codes':invalid_region,'invalid_activity_codes':activity_invalid,
        'region_question_missing_n':int(np.sum(rmat.sum(axis=1)==0)),
        'multi_region_n':int(np.sum(rmat.sum(axis=1)>=2)),
        'multiplicity_warning':'Q9_2 visits are multiresponse; 17 rates need not sum to 100%.',
        'month_warning':'D_MON denotes survey month, not exact date of a specific visit or event.',
        'geo_warning':'Q9_2 visited region and Q8 activity occur on the same respondent, not the same recorded location.'}
    if not (n==16110 and num_columns==408 and qa['duplicate_ids']==0 and qa['valid_weights'] and qa['monthly_quarter_consistency'] and all(wwok) and not invalid_region and not activity_invalid):
        raise ValueError('Source quality gates failed: '+json.dumps(qa,ensure_ascii=False))
    # Core-v1 metrics to cross-check previous reports; weighted percent of total unless stated.
    qa['baseline_crosscheck']={
      'women_pct':safe_r(wmean(all_,d['D_SEX']==2,w)*100),
      'age_20s_pct':safe_r(wmean(all_,d['D_AGE']==2,w)*100),
      'age_30s_pct':safe_r(wmean(all_,d['D_AGE']==3,w)*100),
      'revisit_pct':safe_r(wmean(all_,d['D_NUM']>1,w)*100),
      'FIT_pct':safe_r(wmean(all_,d['TYP']==1,w)*100),
      'Food_pct':safe_r(wmean(all_,activities[1],w)*100),
      'Shopping_pct':safe_r(wmean(all_,activities[2],w)*100),
      'BeautyService_pct':safe_r(wmean(all_,activities[13],w)*100),
      'KpopPlace_pct':safe_r(wmean(all_,activities[8],w)*100)}

    # Overlap and geographic breadth use leisure-and-family visitors as product audience.
    region_count=rmat.sum(axis=1)
    qa['regional_breadth_eligible']={
       'zero_region_pct':safe_r(wmean(eligible,region_count==0,w)*100),
       'exactly_one_pct':safe_r(wmean(eligible,region_count==1,w)*100),
       'two_plus_pct':safe_r(wmean(eligible,region_count>=2,w)*100),
       'three_plus_pct':safe_r(wmean(eligible,region_count>=3,w)*100),
       'average_regions':safe_r(np.average(region_count[eligible],weights=w[eligible]),3)}

    # Month population composition: survey month weighted shares not necessarily exact arrivals.
    month_summary=[]
    for month in range(1,13):
       mask=m==month; sub=mask&eligible
       month_summary.append({'month':month,'sample_n':int(mask.sum()),'leisure_n':int(sub.sum()),
         'n_eff_leisure':safe_r(kish(sub,w),1),'weighted_month_share_all_pct':safe_r(100*w[mask].sum()/w.sum()),
         'leisure_share_month_pct':safe_r(wmean(mask,eligible,w)*100),
         'repeat_share_leisure_pct':safe_r(wmean(sub,d['D_NUM']>1,w)*100),
         'Kpop_participation_pct':safe_r(wmean(sub,activities[8],w)*100),
         'Beauty_service_pct':safe_r(wmean(sub,activities[13],w)*100),
         'Local_festival_pct':safe_r(wmean(sub,activities[10],w)*100)})

    # Descriptive (NOT event co-location) region rates; no false normalization across regions.
    region_overall=[];region_month=[];region_country=[];region_first_repeat=[]
    major_country=[('중국',1),('일본',2),('대만',3),('미국',4),('홍콩',5),('베트남',7)]
    for i,name in enumerate(REGIONS):
        seen=rmat[:,i]
        for popname,msk in [('전체',all_),('여가·친지',eligible)]:
            region_overall.append({'population':popname,'region':name,'sample_n':int(np.sum(msk)),'visited_n':int(np.sum(msk&seen)),
                'weighted_visitor_pct':safe_r(wmean(msk,seen,w)*100),'denom_effective_n':safe_r(kish(msk,w),1)})
        for month in range(1,13):
            sub=eligible&(m==month)
            region_month.append({'month':month,'region':name,'eligible_n':int(sub.sum()),'visited_n':int(np.sum(sub&seen)),
                'eligible_effective_n':safe_r(kish(sub,w),1),
                'visitor_pct':safe_r(wmean(sub,seen,w)*100) if np.sum(sub&seen)>=30 else None,'sparse_visited_n_lt_30':bool(np.sum(sub&seen)<30)})
        for natname,natcode in major_country:
            group=eligible&(d['D_NAT']==natcode)
            region_country.append({'country':natname,'region':name,'n_country':int(group.sum()),'visited_n':int(np.sum(group&seen)),
               'visited_pct':safe_r(wmean(group,seen,w)*100) if np.sum(group&seen)>=30 else None,'group_effective_n':safe_r(kish(group,w),1),'sparse_visited_n_lt_30':bool(np.sum(group&seen)<30)})
        for visitlabel,visitmask in [('첫방문',d['D_NUM']==1),('재방문',d['D_NUM']>1)]:
            group=eligible&visitmask
            region_first_repeat.append({'visit_group':visitlabel,'region':name,'n_group':int(group.sum()),'visited_n':int(np.sum(group&seen)),
               'visited_pct':safe_r(wmean(group,seen,w)*100)})

    # Nationality-standardized regional rates: weighted annual nationality composition
    # as standard population; other nationalities merged to sufficient group sizes.
    country_bucket=np.where(np.isin(d['D_NAT'],[1,2,3,4,5]),d['D_NAT'],97).astype(int)
    groups=[1,2,3,4,5,97]
    share={g:w[eligible&(country_bucket==g)].sum()/w[eligible].sum() for g in groups}
    std_month_region=[]
    for mon in range(1,13):
        for j,name in enumerate(REGIONS):
            parts=[];min_n=999999
            for g in groups:
                mask=eligible&(m==mon)&(country_bucket==g)
                min_n=min(min_n,int(mask.sum()))
                if np.any(mask): parts.append(share[g]*wmean(mask,rmat[:,j],w))
            std_rate=100*sum(parts) if len(parts)==len(groups) else None
            crude=wmean(eligible&(m==mon),rmat[:,j],w)
            std_month_region.append({'month':mon,'region':name,'crude_pct':safe_r(100*crude),
                'nationality_standardized_pct':safe_r(std_rate) if np.sum(eligible&(m==mon)&rmat[:,j])>=30 else None,
                'std_minus_crude_pp':safe_r(std_rate-100*crude) if std_rate is not None and np.sum(eligible&(m==mon)&rmat[:,j])>=30 else None,
                'min_n_per_nat_stratum':min_n,
                'method':'국가 5개 + 기타, 연간 여가방문자 국가비중을 공통 분포로 적용; 통계적 인과통제 아님'})

    # Country-mix standardized activity rates by survey month, not real-time trend.
    activity_month=[]
    for mon in range(1,13):
        for code in [8,10,13]:
            parts=[]
            for g in groups:
                mask=eligible&(m==mon)&(country_bucket==g)
                if np.any(mask):parts.append(share[g]*wmean(mask,activities[code],w))
            sub=eligible&(m==mon)
            act=activities[code]
            raw_rate=wmean(sub,act,w)
            activity_month.append({'month':mon,'activity_code':code,'activity':ACTIVITIES[code],
                   'observed_n':int(np.sum(sub&act)),'raw_participation_pct':safe_r(raw_rate*100),
                   'country_std_participation_pct':safe_r(100*sum(parts)) if len(parts)==len(groups) else None,
                   'caution':'국가 구성만 단순 표준화; 연령/방문횟수/조사 방식의 차이는 남음'})

    # Co-visit region pair lift: non-directional geographic co-visitation within same trip.
    pairs=[];popw=w[eligible];p=(popw[:,None]*rmat[eligible]).sum(axis=0)/popw.sum();base=rmat[eligible].astype(float)
    for a in range(len(REGIONS)):
        for b in range(a+1,len(REGIONS)):
            actual=int(np.sum(eligible&rmat[:,a]&rmat[:,b]))
            joint=float(np.dot(popw,base[:,a]*base[:,b])/popw.sum())
            if actual<30:continue
            lift=joint/(p[a]*p[b]) if p[a]>0 and p[b]>0 else 0
            pairs.append({'region_a':REGIONS[a],'region_b':REGIONS[b],
              'sample_covisited_n':actual,'weighted_joint_pct':safe_r(joint*100),
              'lift':safe_r(lift,3),'weighted_share_a_pct':safe_r(p[a]*100),'weighted_share_b_pct':safe_r(p[b]*100),
              'sufficient_support':actual>=60})
    pairs.sort(key=lambda x:(-x['weighted_joint_pct'],x['region_a']))

    # Insight QA: Q8 activity AND Q9 visit-region association does NOT imply activity there.
    example={}
    for reg in ['서울','부산','제주']:
      ix=REGIONS.index(reg)
      group=eligible&rmat[:,ix]
      example[reg]={'n_visited':int(group.sum()),'Kpop_also_pct':safe_r(wmean(group,activities[8],w)*100),
             'NOT_interpretable_as':'이 지역에서 K-pop 활동을 했다는 비율로 해석할 수 없음'}
    qa['example_activity_region_overlap']=example
    qa['schema_signature_sha256']=hashlib.sha256('|'.join(CODES).encode()).hexdigest()[:16]

    tables={'qa_audit.json':qa,'month_summary.csv':month_summary,'region_overall.csv':region_overall,
       'region_month.csv':region_month,'region_country.csv':region_country,
       'region_first_repeat.csv':region_first_repeat,'region_standardized_month.csv':std_month_region,
       'region_pairs.csv':pairs,'activity_month.csv':activity_month}
    for filename,obj in tables.items():
        if filename.endswith('.json'): (out/filename).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
        else:write_csv(out/filename,obj)
    print(json.dumps({'quality':{k:v for k,v in qa.items() if k not in ('example_activity_region_overlap','baseline_crosscheck')},
       'baselines':qa['baseline_crosscheck'],
       'breadth':qa['regional_breadth_eligible'],
       'top_leisure_regions':sorted([x for x in region_overall if x['population']=='여가·친지'],key=lambda x:-x['weighted_visitor_pct'])[:8],
       'top_region_pairs':pairs[:8],
       'monthly_kpop':[{'month':x['month'],'pct':x['Kpop_participation_pct']} for x in month_summary]},ensure_ascii=False,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=pathlib.Path,required=True);p.add_argument('--out',type=pathlib.Path,required=True)
    args=p.parse_args();main(args.input,args.out)
