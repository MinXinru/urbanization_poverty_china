from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"data"/"urbanisation_aggregate.csv"; OUT=ROOT/"output"; OUT.mkdir(parents=True,exist_ok=True)
COLORS={"community":"#0072B2","hukou":"#D55E00","indiv_work":"#009E73","hh_work":"#E69F00"}
LABELS={"community":"Community (CFPS urban / rural)","hukou":"Hukou (non-agri / agri)","indiv_work":"Individual work (non-agri main job / agri)","hh_work":"Household work (no agri production / agri)"}
plt.rcParams.update({"font.family":"serif","font.serif":["Times New Roman","DejaVu Serif"],"font.size":10,"axes.labelsize":10,"xtick.labelsize":9,"ytick.labelsize":9,"legend.fontsize":7})
df=pd.read_csv(DATA).sort_values(["caliber","year"]); fig,axes=plt.subplots(1,2,figsize=(10,4.2)); nbs=df.drop_duplicates("year").sort_values("year")
axes[0].plot(nbs.year,100*nbs.nbs_Su,color="#000000",lw=2,label="NBS (HIST)",zorder=5); axes[1].plot(nbs.year,100*nbs.dSu_nbs,color="#000000",lw=2,marker="s",ms=3,label="NBS (HIST)",zorder=5)
for key,label in LABELS.items():
 g=df[df.caliber==key].sort_values("year"); axes[0].plot(g.year,100*g.cfps_Su,color=COLORS[key],marker="o",ms=3,lw=1.5,label=label); axes[1].plot(g.year,100*g.dSu_cfps,color=COLORS[key],marker="o",ms=3,lw=1.5,label=label)
axes[0].set_ylabel("Urbanisation rate $S_u$ (%)"); axes[0].set_title("(a) Levels $S_u$"); axes[1].axhline(0,color="#222222",lw=.8,ls="--"); axes[1].set_ylabel("Change in urbanisation (percentage points)"); axes[1].set_title("(b) Wave-to-wave change $\\Delta S_u$")
for ax in axes:
 ax.set_xlabel("Year"); ax.set_xticks(sorted(df.year.unique())); ax.grid(axis="y",alpha=.25,linestyle=":"); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False); ax.legend(frameon=False,fontsize=6.5)
fig.tight_layout(); fig.savefig(OUT/"figure.tiff",dpi=600,bbox_inches="tight",pil_kwargs={"compression":"tiff_lzw"}); fig.savefig(OUT/"preview.jpg",dpi=180,bbox_inches="tight"); plt.close(fig)
