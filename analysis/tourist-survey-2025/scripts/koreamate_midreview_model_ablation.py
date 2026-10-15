"""Sensitivity review of registration fields. Returns aggregated metrics only.
Same 2025 month holdout as v2: train+val Jan-Oct; test Nov-Dec.
No tuning is done on test; reuse prechosen LightGBM leaf count 7.
"""
from pathlib import Path
import json
import numpy as np
from analyze_koreamate_v2 import load,ACT_REC,train_gbm,ndcg_recall,mk_dense

root=Path(__file__).parent
d=load()
Y=np.column_stack([np.isfinite(d[f'Q8a{i:02d}']) & (d[f'Q8a{i:02d}']==i) for i in ACT_REC]).astype(int)
valid=np.isfinite(d['weight'])&(d['weight']>0)&np.isin(d['Q1'],[1,2]);months=d['D_MON']
tr=valid&(months<=10);te=valid&(months>=11)
fields=['D_NAT','D_AGE','D_SEX','D_NUM','Q1','TYP']
F=np.array([[int(d[col][i]) if np.isfinite(d[col][i]) else -1 for col in fields] for i in range(len(months))],dtype=np.int32)
Xtr,Xte=F[tr],F[te];Ytr,Yte=Y[tr],Y[te];wtr=d['weight'][tr];wt=d['weight'][te]
exidx=np.array([j for j,code in enumerate(ACT_REC) if code not in (1,2,14)])
features={
    '6개: 국가·연령·성별·방문횟수·목적·여행형태':[0,1,2,3,4,5],
    '5개: 성별 제외':[0,1,3,4,5],
    '4개: 국가·연령·성별·방문횟수':[0,1,2,3],
    '3개: 국가·연령·방문횟수':[0,1,3],
    '2개: 국가·방문횟수':[0,3],
}

def perrow(y,s):
    y=y[:,exidx];s=s[:,exidx]
    idx=np.argsort(-s,axis=1,kind='stable')[:,:3]
    hit=np.take_along_axis(y,idx,axis=1)
    c=y.sum(axis=1)
    discounted=(hit*np.array([1,1/np.log2(3),.5])).sum(axis=1)
    ideal=np.array([0,1,1+1/np.log2(3),1+1/np.log2(3)+.5])[np.minimum(c,3)]
    return np.divide(discounted,ideal,out=np.zeros(len(y)),where=ideal>0),c>0

out={'data_split':'Train+Validation 2025 Jan-Oct, Test Nov-Dec','n_trainval':int(tr.sum()),'n_test':int(te.sum()),'leaves':7,'models':{},'contrasts':{},'note':'All variants share same test and training; explorative ablation after prior v2, not a new untouched evaluation.'}
persons={};validrow=None
for label,col_idx in features.items():
    pred=train_gbm(mk_dense(Xtr[:,col_idx]),mk_dense(Xte[:,col_idx]),Ytr,wtr/wtr.mean(),leaves=7)
    res=ndcg_recall(Yte,pred,wt,act_indices=exidx)
    per,active=perrow(Yte,pred);validrow=active
    persons[label]=per
    out['models'][label]={'input_features':[fields[i] for i in col_idx],**res}
    print(label,round(res['ndcg_at_3'],6),'Recall',res['recall_at_3'],'n',res['n_valid'],flush=True)

rng=np.random.default_rng(20261015)
valid_ids=np.flatnonzero(validrow)
for short,long in [
 ('3개: 국가·연령·방문횟수','4개: 국가·연령·성별·방문횟수'),
 ('5개: 성별 제외','6개: 국가·연령·성별·방문횟수·목적·여행형태'),
 ('2개: 국가·방문횟수','3개: 국가·연령·방문횟수'),
 ('3개: 국가·연령·방문횟수','6개: 국가·연령·성별·방문횟수·목적·여행형태'),
]:
    diff=persons[short]-persons[long]
    delta=np.average(diff[valid_ids],weights=wt[valid_ids])*100
    boot=[]
    for i in range(600):
        ids=rng.choice(valid_ids,size=len(valid_ids),replace=True)
        boot.append(np.average(diff[ids],weights=wt[ids])*100)
    a,b=np.quantile(boot,[.025,.975]);key=short+' minus '+long
    out['contrasts'][key]={'delta_pp':round(float(delta),3),'approx_ci95_pp':[round(float(a),3),round(float(b),3)]}
    print(key,round(delta,3),tuple(np.round([a,b],3)),flush=True)

(root/'KoreaMate_중간검토_온보딩실험.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')