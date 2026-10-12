# -*- coding: utf-8 -*-
"""Supplementary Fig. S18: urban-to-rural Dibao ratio RΩ (national + six provinces).

Reads `data/18_build_dibao_ratio.xlsx`. After 2021, each path continues from its
2021 level at that unit’s 2016–2021 compound annual growth rate (as in the SI).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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

XLSX = DATA / "18_build_dibao_ratio.xlsx"
PROVINCES = [
    "National",
    "Beijing Municipality",
    "Shanghai Municipality",
    "Guangdong Province",
    "Henan Province",
    "Sichuan Province",
    "Guizhou Province",
]


def main() -> None:
    # Try common sheet / column layouts
    xl = pd.ExcelFile(XLSX)
    print("Sheets:", xl.sheet_names)
    df = pd.read_excel(XLSX, sheet_name=0)
    print("Columns:", list(df.columns))
    apply_matplotlib_style(svg_editable_text=False)
    # Heuristic long panel
    year_col = next((c for c in ("year", "Year") if c in df.columns), None)
    r_col = next((c for c in ("R_omega", "RΩ", "R_Omega", "ratio", "R") if c in df.columns), None)
    prov_col = next((c for c in ("province", "Province", "unit", "name") if c in df.columns), None)
    if year_col is None or r_col is None:
        # wide: year index
        if "year" in [c.lower() for c in df.columns]:
            year_col = [c for c in df.columns if c.lower() == "year"][0]
        else:
            raise RuntimeError("Cannot parse dibao ratio workbook; use published TIFF in outputs/")
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    if prov_col:
        for name, g in df.groupby(prov_col):
            if PROVINCES and str(name) not in PROVINCES and "ational" not in str(name):
                # keep national + any of the six if names differ slightly
                pass
            g = g.sort_values(year_col)
            ax.plot(g[year_col], g[r_col], label=str(name), lw=1.5)
    else:
        ax.plot(df[year_col], df[r_col], color=OKABE_ITO["blue"])
    ax.axvline(2021, color="0.5", lw=0.8, ls="--")
    ax.set_ylabel("Urban-to-rural Dibao ratio")
    ax.set_xlabel("Year")
    ax.legend(frameon=False, fontsize=8, ncol=2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    OUT.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT / "Supplementary_Figure_S18.tiff", dpi=600, format="tiff",
                bbox_inches="tight", pil_kwargs={"compression": "tiff_lzw"})
    fig.savefig(OUT / "Supplementary_Figure_S18_preview.jpg", dpi=180, format="jpeg",
                bbox_inches="tight", pil_kwargs={"quality": 93})
    plt.close(fig)
    print("Wrote output/Supplementary_Figure_S18.*")
    print("Note: published TIFF in outputs/ (from pipeline) is the SI layout if labels differ.")


if __name__ == "__main__":
    main()
