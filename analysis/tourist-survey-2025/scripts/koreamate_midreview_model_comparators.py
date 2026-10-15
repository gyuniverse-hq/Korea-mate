"""Post-hoc paired comparison of candidate recommendation models; aggregated only."""
from pathlib import Path
import json
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from analyze_koreamate_v2 import load,ACT_REC,train_gbm,train_logistic,smooth_rank_train,ndcg_recall,mk_dense
root=Path(__file__).resolve().parent;d=load();n=len(d['weight'])
Y=np.column_stack([np.isfinite(d[f'Q8a{i:02d}'])&(d[f'Q8a{i:02d}']==i) for i in ACT_REC]).astype(int)
valid=np.isfinite(d['weight'])&(d['weight']>0)&np.isin(d['Q1'],[1,2]);months=d['D_MON']
tr=valid&(months<=10);te=valid&(months>=11)
keys=['D_NAT','D_AGE','D_SEX','D_NUM','Q1','TYP']
F=np.asarray([[str(int(d[k][i])) if np.isfinite(d[k][i]) else '미응답' for k in keys] for i in range(n)],dtype=object)
Xtr=F[tr];Xte=F[te];Ytr=Y[tr];Yte=Y[te];wtr=d['weight'][tr];wte=d['weight'][te]
N=Y.shape[1];eval_idx=[j for j,code in enumerate(ACT_REC) if code not in [1,2,14]]
enc=OneHotEncoder(handle_unknown='ignore',sparse_output=True)
trx=enc.fit_transform(Xtr);tex=enc.transform(Xte)
pred={
 'segment':smooth_rank_train(Xtr,Ytr,wtr,alpha=25)(Xte),
 'logistic':train_logistic(trx,tex,Ytr,wtr/wtr.mean()),
 'lightgbm':train_gbm(mk_dense(Xtr),mk_dense(Xte),Ytr,wtr/wtr.mean(),leaves=7),
}

def per(y,s):
 y=y[:,eval_idx];s=s[:,eval_idx]
 ids=np.argsort(-s,axis=1,kind='stable')[:,:3]
 hits=np.take_along_axis(y,ids,axis=1)
 cnt=y.sum(axis=1);disc=np.array([1,1/np.log2(3),.5]);dcg=(hits*disc).sum(axis=1)
 idcg=np.array([0,*np.cumsum(disc)])[np.minimum(cnt,3)]
 return np.divide(dcg,idcg,out=np.zeros(len(y)),where=idcg>0),cnt>0

per_person={m:per(Yte,pr)[0] for m,pr in pred.items()};eligible=per(Yte,pred['segment'])[1];goodids=np.flatnonzero(eligible)
rng=np.random.default_rng(4001)
out={'notes':'Post-hoc, respondent paired bootstrap with fixed model predictions. Not complex-survey variance, no formal superiority claims.','n_valid':int(eligible.sum()),'results':[]}
for a,b in [('lightgbm','logistic'),('lightgbm','segment'),('logistic','segment')]:
 diff=per_person[a]-per_person[b]
 delta=100*np.average(diff[goodids],weights=wte[goodids]);bt=[]
 for _ in range(950):
  ids=rng.choice(goodids,len(goodids),replace=True)
  bt.append(100*np.average(diff[ids],weights=wte[ids]))
 lo,hi=np.quantile(bt,[.025,.975])
 rec={'pair':a+' minus '+b,'delta_pp':round(float(delta),3),'approx_ci95_pp':[round(float(lo),3),round(float(hi),3)]}
 out['results'].append(rec);print(rec,flush=True)
(root/'KoreaMate_중간검토_모델간비교.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')