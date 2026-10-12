# -*- coding: utf-8 -*-
"""Figure 1 — national headcount + urban share of stock (AP / RPO).

Inputs and outputs live in this folder.

Run::

    python3 figure1_plot.py

Writes ``outputs/Figure1_national_H_Pu.jpg``.
Historical panels drop LMI/UMI World Bank schedules (S07–S18); future keeps all.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

HERE = Path(__file__).resolve().parent
_pack = HERE
while _pack != _pack.parent and not (_pack / "_shared" / "pack_paths.py").is_file():
    _pack = _pack.parent
sys.path.insert(0, str(_pack / "_shared"))
from pack_paths import ensure_shared_on_path  # noqa: E402
_paths = ensure_shared_on_path(__file__)
HERE = _paths.code
ROOT = _paths.figure
DATA = _paths.data
OUT = _paths.output
SHARED = _paths.shared

from okabe_ito_style import (  # noqa: E402
    FIGSIZE_MAIN,
    FS_AXES,
    FS_LEGEND,
    FS_PANEL,
    FS_TICK,
    OKABE_ITO,
    apply_matplotlib_style,
)

H_LONG = DATA / "fig1ab_national_H_long.csv"
H_ENV = DATA / "fig1ab_national_H_spec_envelope.csv"
PU_LONG = DATA / "fig1ef_national_Pu_long.csv"
PU_ENV = DATA / "fig1ef_national_Pu_spec_envelope.csv"
MC_CI = DATA / "fig1_focal_future_mc_ci.csv"

OUT_JPG = OUT / "Figure1_national_H_Pu.jpg"
OUT_TIFF = OUT / "Figure1_national_H_Pu.tiff"

PROJ_START = 2026
SCEN_ORDER = ["HQD", "BAU", "LSD", "HSD"]
SCEN_COLOR = {
    "HQD": OKABE_ITO["bluish_green"],
    "BAU": OKABE_ITO["blue"],
    "LSD": OKABE_ITO["orange"],
    "HSD": OKABE_ITO["vermillion"],
}
SCEN_LABEL = {
    "HQD": "HQD(Focal line)",
    "BAU": "BAU (SSP2)",
    "LSD": "LSD(Focal Line)",
    "HSD": "HSD(Focal Line)",
}
OBS_LABEL = "HIST(Focal line)"
OTHER_LABEL = "Other Abs.×rel. schedules"
ENV_LABEL = "Abs.×rel. schedule envelope (2.5–97.5%)"

INSET_YEAR_TICKS = [2030, 2050, 2100]
INSET_LOC = {
    "a": (0.55, 0.48, 0.43, 0.48),
    "c": (0.52, 0.48, 0.45, 0.48),
    "e": (0.08, 0.48, 0.45, 0.48),
    "g": (0.52, 0.08, 0.45, 0.48),
}

# LMI ($3.65/$4.20) and UMI ($6.85/$8.30) World Bank lines: S07-S18.
HIST_FILTER_SPECS = {f"S{i:02d}" for i in range(7, 19)}


def _recompute_hist_envelope(long: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Recompute HIST envelope excluding HIST_FILTER_SPECS."""
    sub = long[(long["scenario"] == "HIST") & (~long["spec_id"].isin(HIST_FILTER_SPECS))]
    sub = sub.dropna(subset=[metric])
    rows = []
    for year, g in sub.groupby("year"):
        vals = g[metric].to_numpy(dtype=float)
        vals = vals[np.isfinite(vals)]
        if vals.size == 0:
            continue
        rows.append({
            "scenario": "HIST",
            "year": year,
            f"{metric}_p2_5": float(np.percentile(vals, 2.5)),
            f"{metric}_p50": float(np.percentile(vals, 50.0)),
            f"{metric}_p97_5": float(np.percentile(vals, 97.5)),
            "n_specs": int(vals.size),
        })
    return pd.DataFrame(rows)


def _draw_main(
    ax,
    long: pd.DataFrame,
    env: pd.DataFrame,
    env_hist_filtered: pd.DataFrame,
    metric: str,
    ylabel: str,
    panel_letter: str,
    *,
    ylim=None,
    show_legend: bool = False,
) -> None:
    others = long[~long["is_focus"]].copy()
    mask_hist_filtered = (
        (others["scenario"] == "HIST")
        & (others["spec_id"].isin(HIST_FILTER_SPECS))
    )
    others = others[~mask_hist_filtered]
    for (_, _scen), g in others.groupby(["spec_id", "scenario"]):
        g = g.dropna(subset=[metric]).sort_values("year")
        if g.empty:
            continue
        ax.plot(g["year"], 100.0 * g[metric], color="#B0B0B0", lw=0.5, alpha=0.40, zorder=1)

    for scen, alpha, color, env_src in [
        ("HIST", 0.25, OKABE_ITO["black"], env_hist_filtered),
        ("BAU", 0.20, OKABE_ITO["blue"], env),
    ]:
        e = env_src[env_src["scenario"] == scen].sort_values("year")
        lo_c, hi_c = f"{metric}_p2_5", f"{metric}_p97_5"
        if lo_c not in e.columns:
            continue
        e = e.dropna(subset=[lo_c, hi_c])
        if e.empty:
            continue
        ax.fill_between(
            e["year"], 100.0 * e[lo_c], 100.0 * e[hi_c],
            color=color, alpha=alpha, linewidth=0, zorder=2,
        )

    hist = (
        long[(long["is_focus"]) & (long["scenario"] == "HIST")]
        .dropna(subset=[metric]).sort_values("year")
    )
    ax.plot(hist["year"], 100.0 * hist[metric], color=OKABE_ITO["black"],
            lw=2.3, zorder=5, label=OBS_LABEL)

    for scen in SCEN_ORDER:
        g = (long[(long["is_focus"]) & (long["scenario"] == scen)]
             .dropna(subset=[metric]).sort_values("year"))
        if g.empty:
            continue
        ax.plot(g["year"], 100.0 * g[metric], color=SCEN_COLOR[scen],
                lw=2.0 if scen == "BAU" else 1.55, zorder=4, label=SCEN_LABEL[scen])

    ax.axvline(PROJ_START, color=OKABE_ITO["black"], ls=":", lw=1.0, zorder=3)
    ax.set_xlim(2000, 2100)
    if ylim is not None:
        ax.set_ylim(*ylim)
    ax.set_xlabel("Year", fontsize=FS_AXES)
    ax.set_ylabel(ylabel, fontsize=FS_AXES)
    ax.tick_params(axis="both", labelsize=FS_TICK)
    ax.text(0.02, 0.98, f"({panel_letter})", transform=ax.transAxes,
            ha="left", va="top", fontsize=FS_PANEL, fontweight="bold", zorder=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    if show_legend:
        handles, labels = ax.get_legend_handles_labels()
        extra = [
            Line2D([0], [0], color="#B0B0B0", lw=1.1, label=OTHER_LABEL),
            Patch(facecolor=OKABE_ITO["blue"], alpha=0.18, label=ENV_LABEL),
        ]
        ax.legend(handles + extra, labels + [h.get_label() for h in extra],
                  frameon=True, fancybox=False, edgecolor="#CCCCCC", framealpha=0.92,
                  loc="upper left", bbox_to_anchor=(0.02, 0.92), fontsize=FS_LEGEND,
                  borderaxespad=0.0, handlelength=1.4, labelspacing=0.28, borderpad=0.35)


def _draw_inset_mc(ax_parent, long, mc, metric, panel_letter, bounds, ylabel):
    x0, y0, w, h = bounds
    ax = inset_axes(ax_parent, width="100%", height="100%", loc="lower left",
                    bbox_to_anchor=(x0, y0, w, h), bbox_transform=ax_parent.transAxes,
                    borderpad=0)
    vals = []
    for scen in SCEN_ORDER:
        g = (long[(long["is_focus"]) & (long["scenario"] == scen) & (long["year"] >= PROJ_START)]
             .dropna(subset=[metric]).sort_values("year"))
        if g.empty:
            continue
        y = 100.0 * g[metric].to_numpy(dtype=float)
        years = g["year"].to_numpy()
        vals.append(y)
        if mc is not None:
            m = mc[(mc["metric"] == metric) & (mc["scenario"] == scen)].sort_values("year")
            if not m.empty:
                mm = m.set_index("year").reindex(years)
                ok = mm["p50"].notna() & (mm["p50"] > 0)
                lo = y.copy()
                hi = y.copy()
                lo[ok.to_numpy()] = y[ok.to_numpy()] * (
                    mm.loc[ok, "p2_5"].to_numpy() / mm.loc[ok, "p50"].to_numpy()
                )
                hi[ok.to_numpy()] = y[ok.to_numpy()] * (
                    mm.loc[ok, "p97_5"].to_numpy() / mm.loc[ok, "p50"].to_numpy()
                )
                ax.fill_between(years, lo, hi, color=SCEN_COLOR[scen], alpha=0.35,
                                linewidth=0, zorder=2)
                vals.extend([lo, hi])
        ax.plot(years, y, color=SCEN_COLOR[scen],
                lw=1.5 if scen == "BAU" else 1.2, zorder=3)
    if vals:
        stacked = np.concatenate(vals)
        ymin, ymax = float(np.nanmin(stacked)), float(np.nanmax(stacked))
        pad = max((ymax - ymin) * 0.12, 0.02)
        y0_lim = max(0.0, ymin - pad)
        y1_lim = ymax + pad
        if "Urban" in ylabel:
            y1_lim = min(100.0, y1_lim)
        ax.set_ylim(y0_lim, y1_lim)
    ax.set_xlim(PROJ_START, 2100)
    ax.set_xticks(INSET_YEAR_TICKS)
    ax.tick_params(axis="both", labelsize=FS_TICK)
    ax.set_xlabel("Year", fontsize=FS_AXES)
    ax.set_ylabel(ylabel, fontsize=FS_AXES)
    ax.text(0.03, 0.97, f"({panel_letter})", transform=ax.transAxes,
            ha="left", va="top", fontsize=FS_PANEL, fontweight="bold", zorder=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.patch.set_alpha(0.92)


def _ap_ylim(long, env_hist_filtered):
    metric = "H_AP"
    focus_vals = long.loc[long["is_focus"], metric] * 100.0
    ymax = float(np.nanmax(focus_vals.to_numpy(dtype=float))) * 1.08
    ymax = max(ymax, 10.0)
    hist_hi = env_hist_filtered.loc[
        env_hist_filtered["scenario"] == "HIST", f"{metric}_p97_5"
    ]
    if len(hist_hi):
        ymax = max(ymax, float(100.0 * hist_hi.max()) * 0.55)
    return 0.0, min(ymax, 70.0)


def main() -> None:
    if not H_LONG.exists() or not PU_LONG.exists():
        raise SystemExit(f"Missing Fig1 long CSVs under {HERE}")

    long_h = pd.read_csv(H_LONG)
    env_h = pd.read_csv(H_ENV)
    long_p = pd.read_csv(PU_LONG)
    env_p = pd.read_csv(PU_ENV)
    mc = pd.read_csv(MC_CI) if MC_CI.exists() else None

    env_h_hist_f = _recompute_hist_envelope(long_h, "H_AP")
    env_h_hist_f_rpo = _recompute_hist_envelope(long_h, "H_RPO")
    env_h_hist_f = env_h_hist_f.merge(
        env_h_hist_f_rpo, on=["scenario", "year", "n_specs"], how="outer"
    )
    env_p_hist_f = _recompute_hist_envelope(long_p, "P_u_AP")
    env_p_hist_f_rpo = _recompute_hist_envelope(long_p, "P_u_RPO")
    env_p_hist_f = env_p_hist_f.merge(
        env_p_hist_f_rpo, on=["scenario", "year", "n_specs"], how="outer"
    )

    apply_matplotlib_style(svg_editable_text=False)
    fig, axes = plt.subplots(2, 2, figsize=FIGSIZE_MAIN, dpi=200, layout="none")
    ax_a, ax_c = axes[0, 0], axes[0, 1]
    ax_e, ax_g = axes[1, 0], axes[1, 1]

    _draw_main(ax_a, long_h, env_h, env_h_hist_f, "H_AP", "Headcount ratio (%)",
               "a", ylim=_ap_ylim(long_h, env_h_hist_f), show_legend=True)
    _draw_main(ax_c, long_h, env_h, env_h_hist_f, "H_RPO", "Headcount ratio (%)",
               "c", ylim=None, show_legend=False)
    _draw_main(ax_e, long_p, env_p, env_p_hist_f, "P_u_AP", "Urban share of stock (%)",
               "e", ylim=(0, 100), show_legend=False)
    _draw_main(ax_g, long_p, env_p, env_p_hist_f, "P_u_RPO", "Urban share of stock (%)",
               "g", ylim=(0, 100), show_legend=False)

    _draw_inset_mc(ax_a, long_h, mc, "H_AP", "b", INSET_LOC["a"], "Headcount (%)")
    _draw_inset_mc(ax_c, long_h, mc, "H_RPO", "d", INSET_LOC["c"], "Headcount (%)")
    _draw_inset_mc(ax_e, long_p, mc, "P_u_AP", "f", INSET_LOC["e"], "Urban share (%)")
    _draw_inset_mc(ax_g, long_p, mc, "P_u_RPO", "h", INSET_LOC["g"], "Urban share (%)")

    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.08, top=0.97, wspace=0.22, hspace=0.28)

    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_JPG, dpi=300, format="jpg", pil_kwargs={"quality": 95})
    fig.savefig(
        OUT_TIFF,
        dpi=600,
        format="tiff",
        pil_kwargs={"compression": "tiff_lzw"},
    )
    print(f"Wrote {OUT_JPG}")
    print(f"Wrote {OUT_TIFF}")
    plt.close(fig)


if __name__ == "__main__":
    main()
