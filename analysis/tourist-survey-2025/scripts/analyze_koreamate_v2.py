"""Korea Mate 2025 inbound survey, v2; reproducible weighted association, clusters & cold-start evaluation.

Usage: python analyze_koreamate_v2.py
Inputs: 2025_eda_raw.csv, metadata_codes.json (from user source files).
Outputs: koreamate_v2_metrics.json, koreamate_v2_*.csv, model tables; contains NO respondent-level outputs.
"""
from __future__ import annotations
import csv, json, math, itertools, os, warnings
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score, roc_auc_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from lightgbm import LGBMClassifier, early_stopping, log_evaluation

BASE = Path(__file__).resolve().parent
SEED = 42
rng=np.random.default_rng(SEED)
ACT={1:'식도락',2:'쇼핑',3:'자연경관',4:'휴양·휴식',5:'고궁·역사',6:'전통문화체험',7:'박물관·전시',8:'K-pop·촬영지',9:'공연',10:'지역축제',11:'유흥·나이트라이프',12:'테마파크·오락',13:'뷰티·미용서비스',14:'의료·건강검진',15:'스포츠 관람',16:'스포츠 참여'}
# Keep medical (#14) OUT of experience recommendation models due to scope and sensitive domain.
ACT_REC=[i for i in range(1,17) if i!=14]
COLS=['D_MON','D_NAT','D_AGE','D_SEX','D_NUM','TYP','Q1','weight','pnid']+[f'Q8a{i:02d}' for i in range(1,17)]

def load():
    dat=[]
    with open(BASE/'2025_eda_raw.csv',encoding='utf-8',newline='') as f:
        reader=csv.DictReader(f)
        assert all(c in reader.fieldnames for c in COLS), 'Required survey columns missing'
        for r in reader:
            dat.append([float(r[c]) if r[c] else np.nan for c in COLS])
    a=np.asarray(dat,dtype=np.float64)
    return {c:a[:,i].copy() for i,c in enumerate(COLS)}

def weighted_pct(event, base, w):
    z=w[base].sum();return float(w[base & event].sum()/z*100) if z else float('nan')

def eff_n(idx,w):
    a=w[idx]; return float(a.sum()**2/np.sum(a*a)) if len(a) else 0.0

def make_associations(Y,w,activity_ids,min_pair_count=60):
    n=len(Y);d=w.sum(); y=Y.astype(float); ww=w[:,None]; p=(ww*y).sum(axis=0)/d
    pair=(y*ww).T@y/d
    raw_count=(Y.T@Y).astype(int)
    all_pairs=[]
    for a in range(len(activity_ids)):
        for b in range(len(activity_ids)):
            if a==b:continue
            support=float(pair[a,b]); pa=float(p[a]);pb=float(p[b]);
            lift=support/pa/pb if pa*pb else 0
            confidence=support/pa if pa else 0
            all_pairs.append({'source_code':activity_ids[a],'source':ACT[activity_ids[a]],'target_code':activity_ids[b],'target':ACT[activity_ids[b]],'support_pct':round(support*100,3),'source_pct':round(pa*100,3),'target_pct':round(pb*100,3),'cooccur_n':int(raw_count[a,b]),'confidence_pct':round(confidence*100,2),'lift':round(lift,3),'increase_pp':round((confidence-pb)*100,2),'eligible_rule': bool(raw_count[a,b]>=min_pair_count and support>=.01 and pa>=.04 and pb>=.04)})
    best=sorted([r for r in all_pairs if r['eligible_rule'] and r['lift']>1.0],key=lambda r:(-r['lift'],-r['support_pct']))
    return all_pairs,best,p,pair


def kmeans_clustering(Y,weights):
    # Treatment: behavioral segmentation only, not feature inputs at registration.
    # Thin rare activities and clinical medicine out of motif discovery. Retain key cultural domains.
    codes=[1,2,3,4,5,6,7,8,9,10,11,12,13]
    ix=np.array([ACT_REC.index(c) for c in codes],dtype=int)
    X=Y[:,ix].astype(float)
    weights=weights/np.mean(weights)
    means=np.average(X,axis=0,weights=weights)
    scale=np.minimum(3.,1/np.sqrt(np.maximum(means*(1-means),.025)))
    Z=X*scale[None,:]
    subset=rng.choice(len(Y),size=min(1250,len(Y)),replace=False)
    search=[];fits={}
    for k in range(3,8):
        m=KMeans(n_clusters=k,n_init=12,random_state=SEED,max_iter=300)
        lab=m.fit_predict(Z,sample_weight=weights)
        shares=np.bincount(lab,weights=weights,minlength=k)/weights.sum()
        sil=silhouette_score(Z[subset],lab[subset],metric='euclidean') if len(np.unique(lab[subset]))>=2 else -1
        search.append({'k':k,'silhouette':round(float(sil),4),'min_weighted_share':round(float(shares.min()),4),'max_weighted_share':round(float(shares.max()),4),'inertia':round(float(m.inertia_),2)})
        fits[k]=(m,lab)
    # Prefer separation without tiny clusters and number of clusters not fixed in advance.
    viable=[s for s in search if s['min_weighted_share']>=.045]
    chosen=max(viable if viable else search,key=lambda s:s['silhouette'])['k']
    model,labs=fits[chosen]
    # Seed stability, labels may permute; ARI invariant to labels.
    m2=KMeans(n_clusters=chosen,n_init=12,random_state=24,max_iter=300)
    labels2=m2.fit_predict(Z,sample_weight=weights)
    ari=adjusted_rand_score(labs,labels2)
    profile=[]
    for k in range(chosen):
        ms=labs==k
        share=weighted_pct(ms,np.ones(len(ms),dtype=bool),weights)
        prior=np.average(X,axis=0,weights=weights)
        cond=np.average(X[ms],axis=0,weights=weights[ms])
        lifts=cond/np.maximum(prior,.005)
        prominent=sorted(range(len(codes)),key=lambda j:((cond[j]-prior[j]) if cond[j]>=.055 else -100),reverse=True)
        top=[ACT[codes[t]] for t in prominent[:3]]
        profile.append({'cluster_id':k+1,'n':int(ms.sum()),'effective_n':round(eff_n(ms,weights),1),'weighted_share_pct':round(share,2),'suggested_label':' · '.join(top[:2]),'top_relative':top,'activities_pct':{ACT[codes[j]]:round(100*float(cond[j]),2) for j in range(len(codes))},'vs_population_pp':{ACT[codes[j]]:round(100*float(cond[j]-prior[j]),2) for j in range(len(codes))}})
    return {'search':search,'k':int(chosen),'seed_ari':float(ari),'feature_codes':codes,'base_pct':{ACT[codes[i]]:round(float(means[i])*100,2) for i in range(len(codes))},'profiles':profile},labs


def encoder_and_features(d):
    fields=['D_NAT','D_AGE','D_SEX','D_NUM','Q1','TYP']
    feats=[]
    for i in range(len(d['weight'])):
        feats.append([str(int(d[k][i])) if np.isfinite(d[k][i]) else '미응답' for k in fields])
    feats=np.asarray(feats,dtype=object)
    # Full visit count is a meaningful pre-trip known value.
    return fields,feats


def smooth_rank_train(F,Y,w,alpha=80.0):
    # Smoothed country-age-first-visit posterior, backed by country-age and global.
    w=w/w.mean();g=(w[:,None]*Y).sum(axis=0)/w.sum();
    acc={}
    for level,keys in [('country',[0]),('country-age',[0,1]),('country-age-repeat',[0,1,3])]:
        agg={}
        for i,key in enumerate(F):
            kk=tuple(key[j] for j in keys)
            if kk not in agg:agg[kk]=[0.,np.zeros(Y.shape[1],dtype=float)]
            agg[kk][0]+=w[i];agg[kk][1]+=w[i]*Y[i]
        acc[level]=(keys,agg)
    def predict(X):
        result=np.tile(g,(len(X),1))
        for level,shrink in [('country',alpha),('country-age',alpha*1.2),('country-age-repeat',alpha*1.5)]:
            keys,agg=acc[level]
            for i,key in enumerate(X):
                kk=tuple(key[j] for j in keys)
                if kk not in agg:continue
                weight,positives=agg[kk]
                result[i]=(positives+shrink*result[i])/(weight+shrink)
        return result
    return predict


def mk_dense(cat):
    return np.asarray(cat,dtype=np.int32)


def ndcg_recall(y,score,w,k=3,act_indices=None):
    if act_indices is not None:
        y=y[:,act_indices];score=score[:,act_indices]
    k=min(k,y.shape[1]);order=np.argsort(-score,axis=1,kind='stable')[:,:k]
    hits=np.take_along_axis(y,order,axis=1)
    cnt=y.sum(axis=1)
    valid=cnt>0
    disc=1/np.log2(np.arange(2,k+2)); dcg=(hits*disc).sum(axis=1)
    ids=np.cumsum(disc)[np.minimum(cnt,k)-1] if len(cnt) else np.empty(0)
    ndcg=np.divide(dcg,ids,out=np.zeros_like(dcg,dtype=float),where=ids>0)
    metric=lambda v:round(float(np.average(v[valid],weights=w[valid])),6) if valid.any() else None
    # recall denominator per user; zero-target rows excluded
    recall=np.divide(hits.sum(axis=1),cnt,out=np.zeros(len(y),dtype=float),where=valid)
    return {'ndcg_at_3':metric(ndcg),'recall_at_3':metric(recall),'hit_at_3':metric((hits.sum(axis=1)>0).astype(float)), 'coverage_pct':round(float(w[valid].sum()/w.sum()*100),3),'n_valid':int(valid.sum())}


def train_logistic(X_tr,X_val,Y_tr,w_tr):
    output=[]
    for i in range(Y_tr.shape[1]):
        lr=LogisticRegression(C=0.75,max_iter=300,solver='lbfgs',random_state=SEED)
        lr.fit(X_tr,Y_tr[:,i],sample_weight=w_tr)
        output.append(lr.predict_proba(X_val)[:,1])
    return np.asarray(output).T

def train_gbm(X_tr,X_val,Y_tr,w_tr,leaves=12,estimators=130):
    output=[]
    for i in range(Y_tr.shape[1]):
        m=LGBMClassifier(n_estimators=estimators,num_leaves=leaves,max_depth=-1,min_child_samples=100,learning_rate=.055,reg_lambda=3.,verbosity=-1,n_jobs=2,random_state=SEED)
        m.fit(X_tr,Y_tr[:,i],sample_weight=w_tr,categorical_feature=list(range(X_tr.shape[1])))
        output.append(m.predict_proba(X_val)[:,1])
    return np.asarray(output).T

def evaluate_models(d,Y,eligible):
    fields,F=encoder_and_features(d)
    months=d['D_MON'].astype(int)
    train=eligible&(months<=8);val=eligible&(months>=9)&(months<=10);test=eligible&(months>=11)
    out={'split':{'train':int(train.sum()),'validation':int(val.sum()),'test':int(test.sum())},'fields':fields,'activities':[ACT[x] for x in ACT_REC], 'target_definition':'2025 관광활동 실제 참여 Q8a01..16; 의료/건강검진 제외', 'model_input_definition':'방문 전에 응답 가능한 D_NAT,D_AGE,D_SEX,D_NUM,Q1,TYP', 'validation':{},'test':{},'test_segments':[]}
    xtr,xval,xt=F[train],F[val],F[test]
    ytr,yval,yt=Y[train].astype(int),Y[val].astype(int),Y[test].astype(int)
    wtr,wval,wt=d['weight'][train],d['weight'][val],d['weight'][test]
    def base_global(y,w,n):return np.tile(np.average(y,axis=0,weights=w),(n,1))
    all_important=[ACT_REC.index(i) for i in range(1,17) if i not in [1,2,14]]
    # validation: lock hyperparam before test.
    candidates={}
    candidates['전체 인기순']=base_global(ytr,wtr,len(yval))
    for alp in [25,80,180]:
        candidates[f'세그먼트 인기순 α={alp}']=smooth_rank_train(xtr,ytr,wtr,alpha=alp)(xval)
    enc=OneHotEncoder(handle_unknown='ignore',sparse_output=True)
    Xtr=enc.fit_transform(xtr);Xval=enc.transform(xval)
    candidates['로지스틱 회귀']=train_logistic(Xtr,Xval,ytr,wtr/np.mean(wtr))
    for leaves in [7,15]:
        candidates[f'LightGBM leaves={leaves}']=train_gbm(mk_dense(xtr).astype(int),mk_dense(xval).astype(int),ytr,wtr/np.mean(wtr),leaves=leaves)
    # Minimal-onboarding ablation: four demographic/history fields, excluding trip purpose/style.
    candidates['LightGBM 최소입력']=train_gbm(mk_dense(xtr[:,:4]),mk_dense(xval[:,:4]),ytr,wtr/np.mean(wtr),leaves=7)
    # choose hyperparams by niche recommendation (beyond universal Food, Shopping).
    for name,preds in candidates.items():
        out['validation'][name]={'all':ndcg_recall(yval,preds,wval), 'exploration':ndcg_recall(yval,preds,wval,act_indices=all_important)}
    choices={
      '세그먼트 인기순':max([n for n in candidates if n.startswith('세그먼트 인기순')],key=lambda n:out['validation'][n]['exploration']['ndcg_at_3']),
      'LightGBM':max([n for n in candidates if n.startswith('LightGBM leaves=')],key=lambda n:out['validation'][n]['exploration']['ndcg_at_3'])
    }
    out['validation_choices']=choices
    # train+val, final untouched test, at pre-chosen hp.
    tv=train|val;xtrain=F[tv];yy=Y[tv].astype(int); ww=d['weight'][tv]
    predictions={}
    predictions['전체 인기순']=base_global(yy,ww,len(xt))
    alp=int(choices['세그먼트 인기순'].split('=')[1]);predictions['세그먼트 인기순']=smooth_rank_train(xtrain,yy,ww,alpha=alp)(xt)
    enc=OneHotEncoder(handle_unknown='ignore',sparse_output=True)
    xx=enc.fit_transform(xtrain);xxt=enc.transform(xt)
    predictions['로지스틱 회귀']=train_logistic(xx,xxt,yy,ww/np.mean(ww))
    leaves=int(choices['LightGBM'].split('=')[1]);predictions['LightGBM']=train_gbm(mk_dense(xtrain),mk_dense(xt),yy,ww/np.mean(ww),leaves=leaves)
    predictions['LightGBM 최소입력']=train_gbm(mk_dense(xtrain[:,:4]),mk_dense(xt[:,:4]),yy,ww/np.mean(ww),leaves=7)
    for name,pred in predictions.items():
        out['test'][name]={'all':ndcg_recall(yt,pred,wt), 'exploration':ndcg_recall(yt,pred,wt,act_indices=all_important)}
    out['test_lifts_pp']={name:{group:round(100*(out['test'][name][group]['ndcg_at_3']-out['test']['전체 인기순'][group]['ndcg_at_3']),2) for group in ['all','exploration']} for name in out['test']}
    # Pairwise respondent bootstrap, approximate uncertainty only (not full complex survey design).
    def perperson_ndcg(y,score,indices):
        y=y[:,indices];score=score[:,indices]
        order=np.argsort(-score,axis=1,kind='stable')[:,:3]
        hits=np.take_along_axis(y,order,axis=1)
        counts=y.sum(axis=1)
        discounted=(hits*np.array([1.,1/np.log2(3),.5])).sum(axis=1)
        idcg=np.array([0.,1.,1+1/np.log2(3),1+1/np.log2(3)+.5])[np.minimum(counts,3)]
        out=np.divide(discounted,idcg,out=np.zeros(len(y)),where=idcg>0)
        return out, counts>0
    out['paired_bootstrap_approx_ci']={}
    for scope,ix in [('all',np.arange(Y.shape[1])),('exploration',np.array(all_important))]:
        ref,valid=perperson_ndcg(yt,predictions['전체 인기순'],ix)
        for name in ['세그먼트 인기순','로지스틱 회귀','LightGBM','LightGBM 최소입력']:
            scores,_=perperson_ndcg(yt,predictions[name],ix)
            diff=scores-ref
            valid_ids=np.flatnonzero(valid)
            delta=100*np.average(diff[valid_ids],weights=wt[valid_ids])
            boots=[]
            for i in range(500):
                take=rng.choice(valid_ids,size=len(valid_ids),replace=True)
                boots.append(float(100*np.average(diff[take],weights=wt[take])))
            bounds=np.quantile(boots,[.025,.975]);out['paired_bootstrap_approx_ci'][f'{scope}/{name}']={'observed_pp':round(float(delta),3),'lower_pp':round(float(bounds[0]),3),'upper_pp':round(float(bounds[1]),3),'bootstrap_repetitions':500,'caution':'독립 응답자 단위 재표집; 층화·가중치 추정 불확실성을 완전 반영하지 않음'}
    # subgroup comparison; not inferential claims, w & ESS shown.
    group_selectors=[('중국 20대 여성',(d['D_NAT']==1)&(d['D_SEX']==2)&(d['D_AGE']==2)),('일본 20대 여성',(d['D_NAT']==2)&(d['D_SEX']==2)&(d['D_AGE']==2)),('대만 20대 여성',(d['D_NAT']==3)&(d['D_SEX']==2)&(d['D_AGE']==2)),('첫 방문',(d['D_NUM']==1)),('재방문',(d['D_NUM']>1)),('20대',(d['D_AGE']==2)),('30대',(d['D_AGE']==3)),('여성',(d['D_SEX']==2)),('남성',(d['D_SEX']==1))]
    g_ids=np.flatnonzero(test)
    for group_name,ms in group_selectors:
        take=ms[g_ids]
        if take.sum()<35:continue
        stats={'group':group_name,'n':int(take.sum()),'neff':round(eff_n(take,wt),1),'metric':{}}
        for name,pred in predictions.items():
            stats['metric'][name]=ndcg_recall(yt[take],pred[take],wt[take],act_indices=all_important)
        out['test_segments'].append(stats)
    out['train_month_activity_rate']={ACT[ACT_REC[j]]:round(float(np.average(Y[train,j],weights=d['weight'][train]))*100,2) for j in range(Y.shape[1])}
    out['test_month_activity_rate']={ACT[ACT_REC[j]]:round(float(np.average(Y[test,j],weights=d['weight'][test]))*100,2) for j in range(Y.shape[1])}
    # calibration and top-3 examples by single pre-trip profile, with no personal data used.
    row_profiles=[('중국·20대·여성·첫방문·여가·개별',[1,2,2,1,1,1]),('일본·20대·여성·재방문·여가·개별',[2,2,2,2,1,1]),('미국·30대·남성·첫방문·여가·개별',[4,3,1,1,1,1])]
    prof=np.array([[str(t) for t in tup] for _,tup in row_profiles],dtype=object)
    profile_pred=smooth_rank_train(xtrain,yy,ww,alpha=alp)(prof)
    out['profile_examples']=[{'input':row_profiles[i][0],'top5':[{'activity':ACT[ACT_REC[j]],'estimated_p':round(float(profile_pred[i,j]),3)} for j in np.argsort(-profile_pred[i])[:5]]} for i in range(len(prof))]
    return out


def main():
    d=load();n=len(d['weight']);weights=d['weight']; valid=np.isfinite(weights)&(weights>0)
    eligible=valid&np.isin(d['Q1'],[1,2])
    Y=np.column_stack([np.isfinite(d[f'Q8a{i:02d}']) & (d[f'Q8a{i:02d}']==i) for i in ACT_REC]).astype(int)
    assert len(np.unique(d['pnid']))==n and n==16110
    print('Data',n,'eligible',eligible.sum(),'weights',weights.sum(),'ess',eff_n(eligible,weights),flush=True)
    assoc,top,p,pair=make_associations(Y[eligible],weights[eligible],ACT_REC)
    print('Top association',top[:12],flush=True)
    clustering,clusters=kmeans_clustering(Y[eligible],weights[eligible])
    print('Clusters k',clustering['k'],'silhouette',clustering['search'],'stability',clustering['seed_ari'],flush=True)
    for profile in clustering['profiles']:
        print('Cluster',profile['cluster_id'],profile['weighted_share_pct'],profile['suggested_label'],flush=True)
    model=evaluate_models(d,Y,eligible)
    print('Validation choices:',model['validation_choices'],flush=True)
    print('TEST',json.dumps(model['test'],ensure_ascii=False,indent=2),flush=True)
    output={'source':'2025 foreign visitor survey, user supplied raw / codebook','n_all':n,'n_eligible':int(eligible.sum()),'n_eff_eligible':round(eff_n(eligible,weights),1),'population':'Leisure/recreation/visit relatives (Q1 in 1,2)','activity_codes':ACT_REC,'activities':[ACT[i] for i in ACT_REC],'activity_pct':{ACT[i]:round(float(p[j])*100,2) for j,i in enumerate(ACT_REC)},'association_top':top[:35],'cluster':clustering,'recommendation':model, 'cautions':['사후 실제 경험(Q8)은 군집 설명과 정답으로만 사용','연관규칙은 인과·선호·필요를 증명하지 않음','가중치 반영, 원조사 복합표본 분산설계 미반영','예측 정답은 실제 여행활동이지 클릭/저장/만족/추천 성과가 아님','아직 앱 로그가 없어 행동 기반 추천 성능 미평가','의료/건강검진 활동은 추천 후보에서 제외']}
    (BASE/'koreamate_v2_metrics.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    def csvwrite(path,rec):
        if not rec:return
        ks=list(rec[0]);
        with open(BASE/path,'w',newline='',encoding='utf-8-sig') as f:
            wri=csv.DictWriter(f,fieldnames=ks);wri.writeheader();wri.writerows(rec)
    csvwrite('koreamate_v2_associations.csv',assoc)
    csvwrite('koreamate_v2_cluster_summary.csv',[{k:v for k,v in a.items() if k!='activities_pct' and k!='vs_population_pp' and k!='top_relative'} for a in clustering['profiles']])
    print('Wrote metrics JSON + association CSV',flush=True)
if __name__=='__main__':main()