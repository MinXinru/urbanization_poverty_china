# -*- coding: utf-8 -*-
"""Supplementary Fig. S9: province choropleth from frozen analysis CSV.

Purpose
-------
Reproduce the published SI map panel from the figure-ready provincial CSV
(schedule = 2010 Dibao-scaled × 50% median unless noted).

Inputs:  data/*.csv
Outputs: output/Supplementary_Figure_S9.*
Geo:     ../_shared/province_boundaries/china_provinces.shp  (or data/geo/)
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import Normalize

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
from map_cartography import CMAP_DIV, CMAP_H, draw_choropleth, load_geoms  # noqa: E402

CSV = DATA / "S9_provincial.csv"
STEM = "Supplementary_Figure_S9"
VALUE_COL = "dH"
MODE = "rh_ap"  # levels | rh | filter_*
LABEL = "ΔH (pp)"
PUBLISHED_SCALE_AS_PCT = True


def _resolve_shp():
    for p in (
        DATA / "geo" / "china_provinces.shp",
        SHARED / "province_boundaries" / "china_provinces.shp",
    ):
        if p.exists():
            return p
    raise FileNotFoundError("china_provinces.shp not found under data/geo or _shared/")



def _load():
    df = pd.read_csv(CSV)
    # Harmonize column names across SI map CSVs
    rename = {}
    if "map_year" in df.columns and "year" not in df.columns:
        rename["map_year"] = "year"
    if "map_scenario" in df.columns and "scenario" not in df.columns:
        rename["map_scenario"] = "scenario"
    if "dP_u" in df.columns and "dPu" not in df.columns:
        rename["dP_u"] = "dPu"
    if rename:
        df = df.rename(columns=rename)
    return df



def _to_plot_units(s: pd.Series) -> pd.Series:
    s = s.astype(float)
    if PUBLISHED_SCALE_AS_PCT and s.abs().max() <= 1.5:
        return 100.0 * s
    return s


def plot_levels(df: pd.DataFrame) -> None:
    years = []
    col = VALUE_COL
    # keep rows that have the column
    if "metric" in df.columns:
        df = df[df["metric"] == col].copy() if col not in df.columns else df
    if col not in df.columns:
        # wide alternative names
        for alt in (col, col.replace("P_u_", "Pu_"), "value"):
            if alt in df.columns:
                col = alt
                break
    sub = df[df["year"].isin(years)].copy()
    sub["_v"] = _to_plot_units(sub[col])
    geoms, bounds = load_geoms(_resolve_shp())
    apply_matplotlib_style(svg_editable_text=False)
    vmax = float(np.nanmax(sub["_v"]))
    vmax = max(vmax, 1.0)
    norm = Normalize(0.0, vmax)
    ncols = len(years)
    fig, axes = plt.subplots(1, ncols, figsize=(2.3 * ncols + 2.0, 4.4), dpi=200)
    if ncols == 1:
        axes = [axes]
    for ax, year in zip(axes, years):
        year_vals = sub[sub["year"] == year].drop_duplicates("province").set_index("province")["_v"]
        draw_choropleth(ax, geoms, bounds, year_vals, CMAP_H, norm)
        ax.text(0.02, 0.98, str(year), transform=ax.transAxes, ha="left", va="top",
                fontsize=11, fontweight="bold")
    sm = plt.cm.ScalarMappable(cmap=CMAP_H, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=list(axes), fraction=0.035, pad=0.02)
    cbar.set_label(LABEL, fontsize=10)
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{STEM}.tiff", dpi=600, format="tiff", bbox_inches="tight",
                pil_kwargs={"compression": "tiff_lzw"})
    fig.savefig(OUT / f"{STEM}_preview.jpg", dpi=200, format="jpg", bbox_inches="tight",
                pil_kwargs={"quality": 95})
    plt.close(fig)
    print(f"Wrote {OUT / (STEM + '.tiff')}")


def plot_window_maps(df: pd.DataFrame) -> None:
    """Multi-window fill+border style (simplified single-channel fill)."""
    # Prefer pre-shaped long CSV with columns: province, window, value
    value_col = VALUE_COL
    if value_col not in df.columns:
        # try generic
        for c in df.columns:
            if c.startswith("dH") or c.startswith("dPu") or c.startswith("dP") or c in ("value", "pp", "dH", "dPu", "dP_u"):
                value_col = c
                break
    win_col = "window" if "window" in df.columns else ("horizon" if "horizon" in df.columns else None)
    if win_col is None:
        raise RuntimeError(f"No window/horizon column in {CSV}")
    windows = list(pd.unique(df[win_col]))
    # keep a stable order if recognizable
    preferred = [
        "2000_2016_HIST", "2016_2022_HIST", "2022_2025_HIST",
        "2025_2030_BAU", "2030_2100_BAU", "2030_2100_LSD",
    ]
    windows = [w for w in preferred if w in windows] or windows
    geoms, bounds = load_geoms(_resolve_shp())
    apply_matplotlib_style(svg_editable_text=False)
    vals = _to_plot_units(df[value_col])
    lim = float(np.nanpercentile(np.abs(vals.to_numpy(float)), 98))
    lim = max(lim, 0.5)
    norm = Normalize(-lim, lim)
    n = len(windows)
    ncols = min(3, n)
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.2 * ncols, 3.0 * nrows), dpi=200)
    axes = np.atleast_1d(axes).ravel()
    for ax, w in zip(axes, windows):
        sub = df[df[win_col] == w].drop_duplicates("province").set_index("province")
        year_vals = _to_plot_units(sub[value_col])
        draw_choropleth(ax, geoms, bounds, year_vals, CMAP_DIV, norm)
        ax.set_title(str(w).replace("_", " "), fontsize=9)
    for ax in axes[len(windows):]:
        ax.axis("off")
    sm = plt.cm.ScalarMappable(cmap=CMAP_DIV, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=list(axes[:len(windows)]), fraction=0.03, pad=0.02)
    cbar.set_label(LABEL, fontsize=10)
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{STEM}.tiff", dpi=600, format="tiff", bbox_inches="tight",
                pil_kwargs={"compression": "tiff_lzw"})
    fig.savefig(OUT / f"{STEM}_preview.jpg", dpi=200, format="jpg", bbox_inches="tight",
                pil_kwargs={"quality": 95})
    plt.close(fig)
    print(f"Wrote {OUT / (STEM + '.tiff')}")


def main() -> None:
    df = _load()
    # Optional stratum filters encoded in CSV
    if "stratum" in df.columns and MODE.endswith("ap"):
        df = df[df["stratum"].astype(str).str.upper().eq("AP")]
    if "stratum" in df.columns and MODE.endswith("rpo"):
        df = df[df["stratum"].astype(str).str.upper().eq("RPO")]
    if MODE.startswith("levels") or MODE.startswith("filter"):
        plot_levels(df)
    else:
        plot_window_maps(df)


if __name__ == "__main__":
    main()
