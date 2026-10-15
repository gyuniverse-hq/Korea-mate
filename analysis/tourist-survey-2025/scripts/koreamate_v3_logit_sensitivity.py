"""Logistic standardization sensitivity check for EDA v3 weighted LPM.
Executes the v3 script for the in-memory parsed arrays and writes aggregate JSON only.
"""
import contextlib,io,runpy,json,numpy as np
from sklearn.linear_model import LogisticRegression
from pathlib import Path
ROOT=Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):
 m=runpy.run_path(str(ROOT/'koreamate_eda_v3_controls.py'))
d=m['d'];w=m['w'];makeX=m['makeX'];ACT=m['ACT'];W=m['W'];I=m['I'];main=m['main'];no_info=m['no_info'];info_known=m['info_known']

def adjusted_risk_difference(idx,exp,y,controls):
    xx,_=makeX(idx,exp,adjusters=controls)
    yy=y.astype(int)
    ww=w[idx] / np.mean(w[idx])
    # Regularized only gently for numerical stability among rare groups
    mod=LogisticRegression(fit_intercept=False,C=100.,solver='lbfgs',max_iter=600,tol=1e-8)
    mod.fit(xx,yy,sample_weight=ww)
    x0=xx.copy(); x1=xx.copy(); x0[:,1]=0.;x1[:,1]=1.
    p0=np.average(mod.predict_proba(x0)[:,1],weights=ww)
    p1=np.average(mod.predict_proba(x1)[:,1],weights=ww)
    return round(float((p1-p0)*100),2),round(float(p0*100),2),round(float(p1*100),2),int(mod.n_iter_[0])

s={'first_repeat':[],'activity_info_any_gap':[]}
idx=np.flatnonzero(main);rep=(d['D_NUM'][idx]>1).astype(int)
for code in [1,2,3,5,6,7,8,9,13]:
 y=(d[f'Q8a{code:02d}'][idx]==code).astype(int)
 val=adjusted_risk_difference(idx,rep,y,['D_NAT','D_AGE','D_SEX','Q1','TYP','D_MON'])
 s['first_repeat'].append({'activity':ACT[code],'logit_adjusted_diff_pp':val[0],'std_first_pct':val[1],'std_repeat_pct':val[2],'iterations':val[3]})
for code in [1,2,8,13]:
 idx=np.flatnonzero(main&np.any(W==code,axis=1))
 exp=(d[f'Q8a{code:02d}'][idx]!=code).astype(int)
 val=adjusted_risk_difference(idx,exp,info_known[idx].astype(int),['D_NAT','D_AGE','D_SEX','D_NUM','Q1','TYP','D_MON'])
 s['activity_info_any_gap'].append({'activity':ACT[code],'logit_adjusted_diff_pp':val[0],'std_done_pct':val[1],'std_notdone_pct':val[2],'iterations':val[3]})
(ROOT/'KoreaMate_EDA_v3_로지스틱_민감도.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(s,ensure_ascii=False,indent=2))