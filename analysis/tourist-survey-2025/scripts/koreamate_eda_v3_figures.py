"""Generate four aggregate-only visuals for v3 report."""
from pathlib import Path
import json
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/'KoreaMate_EDA_v3_추가분석_집계.json').read_text())
plt.rcParams.update({'font.family':'NanumGothic','axes.unicode_minus':False,'figure.facecolor':'white','axes.titlesize':16,'axes.labelsize':11,'xtick.labelsize':10,'ytick.labelsize':10,'savefig.dpi':175})
NAVY='#1e4266';TEAL='#18878c';RED='#c25d5c';INK='#263749';GREY='#cbd5df';LIGHT='#eaf1f5';GOLD='#b8812b'

def plot_save(name):plt.savefig(ROOT/name,bbox_inches='tight',facecolor='white');plt.close();print(name)

# 1 overall adjusted first/repeat effects
items=[x for x in r['first_repeat'] if x['activity'] in ['자연경관','고궁·역사','전통문화체험','박물관·전시','K-pop·촬영지','공연','뷰티·미용서비스','식도락','쇼핑']]
items.sort(key=lambda x:x['adjusted_pp'])
fig,ax=plt.subplots(figsize=(10.2,6.1))
ys=np.arange(len(items));v=np.array([x['adjusted_pp'] for x in items]);lo=np.array([x['hc3_approx_95_low_pp'] for x in items]);hi=np.array([x['hc3_approx_95_high_pp'] for x in items]);cc=[RED if f<0 else TEAL for f in v]
ax.axvline(0,color=INK,lw=1.1);ax.errorbar(v,ys,xerr=[v-lo,hi-v],fmt='none',capsize=3,ecolor=INK,elinewidth=1.1,zorder=1)
ax.scatter(v,ys,c=cc,s=80,zorder=2,edgecolor='white',linewidth=1)
ax.set_yticks(ys,labels=[x['activity'] for x in items]);ax.set_xlim(-23,14)
ax.grid(axis='x',alpha=.18);ax.set_axisbelow(True)
for i,val in enumerate(v):ax.text((hi[i]+0.55) if val>=0 else (lo[i]-0.55),i,f'{val:+.1f}%p',ha='left' if val>=0 else 'right',va='center',fontsize=10,color=INK)
ax.set_title('재방문객 - 첫 방문객: 특성 통제 후 활동 참여 차이',loc='left',pad=20,fontweight='bold',color=NAVY)
ax.set_xlabel('가중 선형확률모형의 조정된 차이 (%p)');ax.set_ylim(-.7,len(items)-.3)
fig.text(.11,.017,'국적·연령·성별·여행목적·여행형태·조사월 통제 / 가로선: HC3 근사 95% 구간(공식 복합표본 신뢰구간 아님)',fontsize=9,color='#607080')
plot_save('13_v3_visit_adjusted.png')

# 2 activity differences by six markets
nats=['중국','일본','대만','미국','홍콩','베트남'];activities=['K-pop·촬영지','고궁·역사']
fig,ax=plt.subplots(figsize=(10.3,5.1));x=np.arange(len(nats));width=.34
for j,act in enumerate(activities):
 rec=[next(q for q in r['country_first_repeat'] if q['country']==c and q['activity']==act) for c in nats]
 y=np.array([z['adjusted_pp'] for z in rec]);ls=np.array([z['hc3_approx_95_low_pp'] for z in rec]);hs=np.array([z['hc3_approx_95_high_pp'] for z in rec]);pos=x+(-width/2 if j==0 else width/2)
 ax.bar(pos,y,width,color=TEAL if j==0 else RED,label=act,alpha=.86)
 ax.errorbar(pos,y,yerr=np.array([y-ls,hs-y]),fmt='none',ecolor=INK,capsize=2,linewidth=.8)
ax.axhline(0,lw=1,color=INK);ax.set_xticks(x,nats);ax.legend(loc='lower left',frameon=False)
ax.set_title('국가별 방문경험 차이: K-pop 장소 vs 고궁·역사',loc='left',pad=15,fontweight='bold',color=NAVY)
ax.set_ylabel('재방문객 - 첫 방문객 (%p)');ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
fig.text(.11,.01,'국가별로 연령·성별·방문목적·여행형태·조사월 통제 / 근사 95% 구간; 일부 국가별 표본 불확실성 주의',fontsize=9,color='#607080')
plot_save('14_v3_country_visit.png')

# 3 information gap - specific type vs any
cases=[('식도락','정보 부족 유형 1개 이상'),('식도락','음식·맛집'),('식도락','방문지·운영정보'),('쇼핑','정보 부족 유형 1개 이상'),('쇼핑','쇼핑'),('K-pop·촬영지','정보 부족 유형 1개 이상'),('K-pop·촬영지','한류문화 체험'),('K-pop·촬영지','방문지·운영정보'),('뷰티·미용서비스','정보 부족 유형 1개 이상'),('뷰티·미용서비스','방문지·운영정보')]
it=[next(a for a in r['activity_friction'] if a['activity']==c and a['info_type']==inf) for c,inf in cases]
fig,ax=plt.subplots(figsize=(11,6.7));y=np.arange(len(it));vals=np.array([q['adjusted_pp'] for q in it]);lo=np.array([q['hc3_approx_95_low_pp'] for q in it]);hi=np.array([q['hc3_approx_95_high_pp'] for q in it])
col=[NAVY if q['info_code']=='any' else TEAL for q in it]
ax.axvline(0,color=INK,lw=1);ax.errorbar(vals,y,xerr=[vals-lo,hi-vals],fmt='none',ecolor='#495463',capsize=3,elinewidth=1.1)
ax.scatter(vals,y,c=col,s=75,edgecolor='white',linewidth=1.1,zorder=3)
ax.set_yticks(y,[q['activity']+' / '+q['info_type'] for q in it]);ax.invert_yaxis();ax.set_xlim(-6,30)
for k,z in enumerate(vals):ax.text(hi[k]+.6,k,f'{z:+.1f}%p',fontsize=9,va='center',color=INK)
ax.set_title('관심 후 미참여자 - 참여자: 정보 부족 응답 차이',loc='left',fontweight='bold',color=NAVY,pad=16)
ax.set_xlabel('국적·연령·성별·방문경험·목적·형태·월 통제 (%p)')
ax.grid(axis='x',alpha=.18);ax.set_axisbelow(True)
fig.text(.11,.008,'방문 실패 이유 조사 아님 / 한류 정보 유형과 미용서비스 전용 정보 유형은 분리 측정되지 않음',fontsize=9,color='#607080')
plot_save('15_v3_friction_types.png')

# 4 satisfaction among eligible survey answerers
sat=[t for t in r['satisfaction'] if t['group']=='전체'];texts=[t['item'] for t in sat];y=np.arange(len(sat));low=np.array([t['low_1_2_pct'] for t in sat]);neutral=np.array([t['neutral_3_pct'] for t in sat]);high=np.array([t['satisfied_4_5_pct'] for t in sat])
fig,ax=plt.subplots(figsize=(10,4.4));ax.barh(y,low,color=RED,label='불만족(1~2)');ax.barh(y,neutral,left=low,color=GOLD,label='보통(3)');ax.barh(y,high,left=low+neutral,color=TEAL,label='만족(4~5)')
ax.set_yticks(y,texts);ax.invert_yaxis();ax.set_xlim(0,100);ax.legend(ncol=3,bbox_to_anchor=(0,-.16),loc='upper left',frameon=False);ax.grid(axis='x',alpha=.15)
for i,z in enumerate(high):ax.text(100-z/2,i,f'{z:.1f}%',ha='center',va='center',color='white',fontweight='bold')
ax.set_title('여행 전반 만족도는 높음: 불편 문제를 과장하면 안 되는 이유',loc='left',fontweight='bold',color=NAVY,pad=14)
fig.text(.11,.02,'여가·친지 방문객 기준 / 디지털 관광정보 항목은 해당 없음·무응답 제외한 유효 응답자 분모',fontsize=9,color='#607080')
plot_save('16_v3_satisfaction.png')