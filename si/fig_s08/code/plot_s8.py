# -*- coding: utf-8 -*-
"""Supplementary Fig. S8: national H / Pu sensitivity panel.

Reads the frozen national series CSV and draws the 2×2 panel used in the SI
(AP/RPO × headcount/urban share; SSP colours; variant line styles).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
# Locate pack _shared (Github_upload/_shared) from code/
_pack = HERE
while _pack != _pack.parent and not (_pack / "_shared" / "pack_paths.py").is_file():
    _pack = _pack.parent
sys.path.insert(0, str(_pack / "_shared"))
from pack_paths import ensure_shared_on_path  # noqa: E402
_paths = ensure_shared_on_path(__file__)
HERE = _paths.code
DATA = _paths.data
OUT = _paths.output
SHARED = _paths.shared
ROOT = _paths.pack_root
from okabe_ito_style import OKABE_ITO, apply_matplotlib_style  # noqa: E402

NAT_CSV = DATA / "16_deflator_national_series.csv"
VAR_COL = "d_variant"
OUT_TIFF = OUT / "Supplementary_Figure_S8.tiff"
OUT_JPG = OUT / "Supplementary_Figure_S8_preview.jpg"

PROJ_SCENARIOS = ("HQD", "BAU", "LSD", "HSD")
SCEN_COLOR = {
    "HQD": OKABE_ITO["bluish_green"],
    "BAU": OKABE_ITO["blue"],
    "LSD": OKABE_ITO["orange"],
    "HSD": OKABE_ITO["vermillion"],
}
SCEN_LABEL = {
    "HQD": "HQD (SSP1)",
    "BAU": "BAU (SSP2)",
    "LSD": "LSD (SSP3)",
    "HSD": "HSD (SSP5)",
}
HIST_COLOR = OKABE_ITO["black"]
PANELS = [
    ("H_AP", "AP headcount (%)", "a"),
    ("H_RPO", "RPO headcount (%)", "b"),
    ("P_u_AP", "AP urban share (%)", "c"),
    ("P_u_RPO", "RPO urban share (%)", "d"),
]


def _variants(nat: pd.DataFrame):
    vals = list(pd.unique(nat[VAR_COL].astype(str)))
    preferred = ["mono", "centered10", "forward5", "raw", "central", "lo", "hi", "main", "base"]
    ordered = [v for v in preferred if v in vals]
    for v in vals:
        if v not in ordered:
            ordered.append(v)
    return ordered


def _style_map(variants):
    styles = {"central": "-", "main": "-", "mono": "-", "base": "-"}
    dashes = ["--", ":", "-.", (0, (3, 1, 1, 1))]
    out = {}
    di = 0
    for v in variants:
        if v in styles:
            out[v] = styles[v]
        else:
            out[v] = dashes[di % len(dashes)]
            di += 1
    return out


def _scale(s: pd.Series) -> pd.Series:
    s = s.astype(float)
    if s.abs().max() <= 1.5:
        return 100.0 * s
    return s


def plot(nat: pd.DataFrame) -> None:
    apply_matplotlib_style(svg_editable_text=False)
    variants = _variants(nat)
    styles = _style_map(variants)
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.8), sharex=True)
    for ax, (metric, ylabel, letter) in zip(axes.ravel(), PANELS):
        for v in variants:
            h = nat[(nat[VAR_COL].astype(str) == v) & (nat["scenario"] == "HIST") & (nat["year"] <= 2025)]
            h = h.sort_values("year")
            if not h.empty and metric in h.columns:
                ax.plot(h["year"], _scale(h[metric]), color=HIST_COLOR, ls=styles[v], lw=1.6 if v in ("central", "main", "mono", "base") else 1.2)
            for scen in PROJ_SCENARIOS:
                p = nat[(nat[VAR_COL].astype(str) == v) & (nat["scenario"] == scen) & (nat["year"] >= 2025)]
                p = p.sort_values("year")
                if p.empty or metric not in p.columns:
                    continue
                ax.plot(p["year"], _scale(p[metric]), color=SCEN_COLOR[scen], ls=styles[v], lw=1.8 if v in ("central", "main", "mono", "base") else 1.25)
        ax.axvline(2025, color="0.5", lw=0.8)
        ax.set_ylabel(ylabel)
        ax.text(0.02, 0.98, f"({letter})", transform=ax.transAxes, ha="left", va="top", fontweight="bold")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    # legends
    scen_handles = [Line2D([0], [0], color=SCEN_COLOR[s], lw=2, label=SCEN_LABEL[s]) for s in PROJ_SCENARIOS]
    scen_handles.insert(0, Line2D([0], [0], color=HIST_COLOR, lw=2, label="Historical"))
    var_handles = [Line2D([0], [0], color="0.2", ls=styles[v], lw=1.6, label=str(v)) for v in variants]
    axes[0, 0].legend(handles=scen_handles, frameon=False, fontsize=8, loc="best")
    axes[0, 1].legend(handles=var_handles, frameon=False, fontsize=8, loc="best", title=VAR_COL)
    OUT.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT_TIFF, dpi=600, format="tiff", bbox_inches="tight", pil_kwargs={"compression": "tiff_lzw"})
    fig.savefig(OUT_JPG, dpi=180, format="jpeg", bbox_inches="tight", pil_kwargs={"quality": 93})
    plt.close(fig)
    print(f"Wrote {OUT_TIFF}")
    print(f"Wrote {OUT_JPG}")


def main() -> None:
    nat = pd.read_csv(NAT_CSV)
    # harmonize metric names
    rename = {}
    for a, b in [("H_AP", "H_AP"), ("Pu_AP", "P_u_AP"), ("P_u_AP", "P_u_AP"),
                 ("H_RPO", "H_RPO"), ("Pu_RPO", "P_u_RPO"), ("P_u_RPO", "P_u_RPO")]:
        if a in nat.columns and b not in nat.columns:
            rename[a] = b
    if rename:
        nat = nat.rename(columns=rename)
    plot(nat)


if __name__ == "__main__":
    main()
