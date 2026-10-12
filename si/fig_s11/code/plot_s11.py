# -*- coding: utf-8 -*-
"""Supplementary Fig. S11 — CFPS national H and urban share, 2010–2022.

Figure-1 grammar (2×2: H_AP | H_RPO / P_u_AP | P_u_RPO), historical CFPS
wave snapshots only. All absolute×relative schedules in the CFPS wave panel
(S01–S06, S19–S24; LMI/UMI S07–S18 absent). Focal schedule S23 in black;
grey other schedules + 2.5–97.5% envelope. No SSP projections / insets.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
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
OUT_DIR = OUT
LONG_CSV = DATA / "FigS11_cfps_national_H_Pu_long.csv"
from okabe_ito_style import (  # noqa: E402
    FS_AXES,
    FS_LEGEND,
    FS_PANEL,
    FS_TICK,
    OKABE_ITO,
    apply_matplotlib_style,
)

FOCAL = "S23"
# LMI/UMI excluded by construction in the CFPS wave panel; keep explicit.
LMI_UMI = {f"S{i:02d}" for i in range(7, 19)}
FIGSIZE = (10.2, 7.4)
MAIN_POS = {
    "a": (0.080, 0.575, 0.410, 0.355),
    "b": (0.560, 0.575, 0.410, 0.355),
    "c": (0.080, 0.115, 0.410, 0.355),
    "d": (0.560, 0.115, 0.410, 0.355),
}
OBS_LABEL = "HIST(Focal line)"
OTHER_LABEL = "Other Abs.×rel. schedules"
ENV_LABEL = "Abs.×rel. schedule envelope (2.5–97.5%)"


def _envelope(long: pd.DataFrame, metric: str) -> pd.DataFrame:
    rows = []
    for year, g in long.groupby("year"):
        vals = g[metric].to_numpy(dtype=float)
        vals = vals[np.isfinite(vals)]
        if vals.size == 0:
            continue
        rows.append(
            {
                "year": int(year),
                "lo": float(np.percentile(vals, 2.5)),
                "hi": float(np.percentile(vals, 97.5)),
                "n_specs": int(vals.size),
            }
        )
    return pd.DataFrame(rows)


def _draw(
    ax,
    long: pd.DataFrame,
    env: pd.DataFrame,
    metric: str,
    ylabel: str,
    letter: str,
    *,
    ylim=None,
    col_title: str | None = None,
) -> None:
    others = long[~long["is_focus"]]
    for _, g in others.groupby("spec_id"):
        g = g.dropna(subset=[metric]).sort_values("year")
        if g.empty:
            continue
        ax.plot(
            g["year"],
            100.0 * g[metric],
            color="#B0B0B0",
            lw=0.5,
            alpha=0.40,
            zorder=1,
        )
    if not env.empty:
        ax.fill_between(
            env["year"],
            100.0 * env["lo"],
            100.0 * env["hi"],
            color=OKABE_ITO["black"],
            alpha=0.25,
            linewidth=0,
            zorder=2,
        )
    hist = long[long["is_focus"]].dropna(subset=[metric]).sort_values("year")
    ax.plot(
        hist["year"],
        100.0 * hist[metric],
        color=OKABE_ITO["black"],
        lw=2.3,
        zorder=5,
        marker="o",
        markersize=4.5,
        label=OBS_LABEL,
    )
    ax.set_xlim(2009.5, 2022.5)
    ax.set_xticks([2010, 2012, 2014, 2016, 2018, 2020, 2022])
    if ylim is not None:
        ax.set_ylim(*ylim)
    ax.set_xlabel("Year", fontsize=FS_AXES)
    ax.set_ylabel(ylabel, fontsize=FS_AXES)
    ax.tick_params(axis="both", labelsize=FS_TICK)
    ax.text(
        0.02,
        0.98,
        f"({letter})",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=FS_PANEL,
        fontweight="bold",
        zorder=10,
    )
    if col_title is not None:
        ax.set_title(col_title, fontsize=FS_AXES, pad=4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def main() -> None:
    if not LONG_CSV.is_file():
        raise SystemExit(f"Missing plot-ready CSV: {LONG_CSV}")
    panel = pd.read_csv(LONG_CSV)
    panel = panel[~panel["spec_id"].isin(LMI_UMI)].copy()
    panel["is_focus"] = panel["spec_id"].eq(FOCAL) | panel["is_focus"].astype(bool)

    env_h_ap = _envelope(panel, "H_AP")
    env_h_rpo = _envelope(panel, "H_RPO")
    env_p_ap = _envelope(panel, "P_u_AP")
    env_p_rpo = _envelope(panel, "P_u_RPO")

    apply_matplotlib_style(svg_editable_text=False)
    fig, axes = plt.subplots(2, 2, figsize=FIGSIZE, dpi=200, layout="none")
    ax_a, ax_b = axes[0, 0], axes[0, 1]
    ax_c, ax_d = axes[1, 0], axes[1, 1]

    ymax_ap = float(np.nanmax(100.0 * panel["H_AP"].to_numpy(float))) * 1.08
    _draw(ax_a, panel, env_h_ap, "H_AP", "Headcount ratio (%)", "a",
          ylim=(0.0, max(10.0, ymax_ap)), col_title="AP")
    _draw(ax_b, panel, env_h_rpo, "H_RPO", "Headcount ratio (%)", "b",
          ylim=None, col_title="RPO")
    _draw(ax_c, panel, env_p_ap, "P_u_AP", "Urban share of stock (%)", "c",
          ylim=(0, 100))
    _draw(ax_d, panel, env_p_rpo, "P_u_RPO", "Urban share of stock (%)", "d",
          ylim=(0, 100))

    for letter, ax in [("a", ax_a), ("b", ax_b), ("c", ax_c), ("d", ax_d)]:
        ax.set_position(MAIN_POS[letter])

    handles = [
        Line2D([0], [0], color=OKABE_ITO["black"], lw=2.3, marker="o",
               markersize=4, label=OBS_LABEL),
        Line2D([0], [0], color="#B0B0B0", lw=1.1, label=OTHER_LABEL),
        Patch(facecolor=OKABE_ITO["black"], alpha=0.25, label=ENV_LABEL),
    ]
    fig.legend(
        handles=handles,
        loc="upper center",
        ncol=3,
        frameon=False,
        fontsize=FS_LEGEND,
        bbox_to_anchor=(0.5, 0.055),
        handlelength=1.4,
        labelspacing=0.35,
        borderpad=0.40,
        columnspacing=1.0,
    )

    OUT.mkdir(parents=True, exist_ok=True)
    jpg = OUT / "Supplementary_Figure_S11_preview.jpg"
    tif = OUT / "Supplementary_Figure_S11.tiff"
    fig.savefig(jpg, dpi=300, format="jpg", pil_kwargs={"quality": 95})
    fig.savefig(tif, dpi=600, format="tiff", pil_kwargs={"compression": "tiff_lzw"})
    plt.close(fig)
    print(f"Wrote {jpg}")
    print(f"Wrote {tif}")
    print(f"specs={sorted(panel['spec_id'].unique())} years={sorted(panel['year'].unique())}")


if __name__ == "__main__":
    main()
