"""Create aggregate-only EDA illustrations from audit output; no respondent data."""
from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import PercentFormatter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs';FIG=ROOT/'figures';FIG.mkdir(exist_ok=True)
plt.rcParams['font.family']='NanumSquare'
plt.rcParams['axes.unicode_minus']=False
plt.rcParams['font.size']=11

def read(name):
    with (OUT/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

rows=[x for x in read('region_overall.csv') if x['population']=='여가·친지'];top=sorted(rows,key=lambda r:-float(r['weighted_visitor_pct']))[:10]
fig,ax=plt.subplots(figsize=(10,6.3))
ax.barh([x['region'] for x in top[::-1]],[float(x['weighted_visitor_pct']) for x in top[::-1]])
for i,x in enumerate(top[::-1]):ax.text(float(x['weighted_visitor_pct'])+1,i,x['weighted_visitor_pct']+'%',va='center',fontsize=10)
ax.set_xlim(0,93);ax.set_xlabel('가중 방문율 (%)');ax.set_title('2025 외래관광객조사 — 여가·친지 방문자의 지역 방문율 (복수응답)')
ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True);fig.tight_layout();fig.savefig(FIG/'01_region_top10.png',dpi=160,bbox_inches='tight');plt.close(fig)

reg=read('region_month.csv');standard=read('region_standardized_month.csv')
fig,ax=plt.subplots(figsize=(11,5.8))
for city in ['서울','부산','제주','강원']:
    vals=sorted([x for x in reg if x['region']==city],key=lambda x:int(x['month']))
    ax.plot([int(x['month']) for x in vals],[float(x['visitor_pct']) for x in vals],label=city,marker='o',markersize=3)
ax.set_xticks(range(1,13));ax.set_xlabel('조사 월 (2025년)');ax.set_ylabel('가중 지역 방문율 (%)');ax.set_title('월별 지역 방문율 — 여가·친지 방문객');ax.legend(ncol=4);ax.grid(alpha=.22)
fig.tight_layout();fig.savefig(FIG/'02_month_region_patterns.png',dpi=160,bbox_inches='tight');plt.close(fig)

countries=['중국','일본','대만','미국','홍콩','베트남'];regions=['서울','부산','제주','경기','인천','강원']
ct=read('region_country.csv');lookup={(r['country'],r['region']):r for r in ct}
mat=np.zeros((len(countries),len(regions)));mask=np.zeros_like(mat,dtype=bool)
for i,c in enumerate(countries):
 for j,r in enumerate(regions):
    val=lookup.get((c,r),{}).get('visited_pct');mat[i,j]=float(val) if val else np.nan;mask[i,j]=bool(val)
fig,ax=plt.subplots(figsize=(10.5,5.6));im=ax.imshow(mat,aspect='auto',vmin=0,vmax=100)
ax.set_xticks(range(len(regions)),regions);ax.set_yticks(range(len(countries)),countries)
for i in range(len(countries)):
 for j in range(len(regions)):
    if mask[i,j]:ax.text(j,i,f'{mat[i,j]:.1f}%',ha='center',va='center',fontsize=10,color='black' if mat[i,j]<52 else 'white')
    else:ax.text(j,i,'표본 적음',ha='center',va='center',fontsize=8)
ax.set_title('국적별 주요 방문 지역 분포 (각 국적 관광객 중 선택 비율)');cbar=fig.colorbar(im,ax=ax,shrink=.76);cbar.set_label('가중 방문율 (%)');fig.tight_layout();fig.savefig(FIG/'03_country_region_heatmap.png',dpi=160,bbox_inches='tight');plt.close(fig)

am=read('activity_month.csv')
fig,ax=plt.subplots(figsize=(10.7,5.6))
for label in ['K-pop·촬영지','뷰티·미용서비스','지역 축제']:
    a=sorted([r for r in am if r['activity']==label],key=lambda r:int(r['month']))
    ax.plot([int(x['month']) for x in a],[float(x['country_std_participation_pct']) for x in a],label=label,marker='o',markersize=3)
ax.set_xticks(range(1,13));ax.set_xlabel('조사 월');ax.set_ylabel('국적 구성 단순 표준화 참여율 (%)');ax.set_title('2025 관광활동 참여율의 월별 차이 (실시간 트렌드 아님)');ax.legend();ax.grid(alpha=.2)
fig.tight_layout();fig.savefig(FIG/'04_month_activity_std.png',dpi=160,bbox_inches='tight');plt.close(fig)
print('Created', len(list(FIG.glob('*.png'))),'charts')
