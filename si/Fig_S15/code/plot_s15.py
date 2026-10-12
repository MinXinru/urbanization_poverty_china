# -*- coding: utf-8 -*-
"""Plot Supplementary Figs. S15–S16 (RPO, 6-panel).

S15 — post-2021 growth rate of the urban–rural subsistence ratio R_Ω
      (low / central / high) × three flow-prediction approaches; BAU; RPO.
S16 — CFPS transition-share specification (pooled / 2020–22 / ±20%) under
      stock-weighted shares; BAU; RPO.

Panel map (3×2, both figures):
    (a) Urban IS-exiters
    (b) Urban IS-entrants
    (c) Rural intra-sectoral turnover (IS-exiters + IS-entrants)
    (d) Urban IS-stayers
    (e) Rural IS-stayers
    (f) Total movers (CS-exiters + CS-entrants + CS-stayers)

Scale alignment with Fig. 4 (annual dual-endpoint / dual-share stack):
  sensitivity CSVs store 2-year-window volumes after ``calibrate_inout_to_lei``
  (lei_scale on flows and peeled IS/CS). Convert to Fig.4-like annual M/yr as:
      flow_annual = xstay / (year1−year0) / lei_scale
      stayer_annual = stayer / (year1−year0)   # keep lei-scaled stayers
  IS/CS peeled via Fig. 4 channel flags (RISE/UISE vs PE) before plotting.

JPG + TIFF @ 600 dpi LZW; no SVG.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "_shared"))
DATA = ROOT / "data"
S16_DATA = ROOT / "data"
OUT = ROOT / "output"
S16_OUT = ROOT / "output"
from okabe_ito_style import (  # noqa: E402
    FS_AXES,
    FS_LEGEND,
    FS_PANEL,
    FS_TICK,
    OKABE_ITO,
    apply_matplotlib_style,
)

R_OMEGA_DETAIL = DATA / "S15_RPO_aggregated_flows.csv"
SHARE_DETAIL = S16_DATA / "S16_RPO_aggregated_flows.csv"

APPROACH_ORDER = ["A1", "A2", "A3"]
APPROACH_LABELS = {
    "A1": "Stock-weighted",
    "A2": "O–D gravity",
    "A3": "Demographic\ncell rates",
}
GROWTH_ORDER = ["lo", "central", "hi"]
GROWTH_LABELS = {
    "lo": "Low",
    "central": "Central",
    "hi": "High",
}
GROWTH_COLORS = {
    "lo": OKABE_ITO["sky_blue"],
    "central": OKABE_ITO["blue"],
    "hi": OKABE_ITO["vermillion"],
}
HORIZON_LABELS = {
    "near": "Near-term (to ~2030)",
    "late": "Late-century (2030–2100)",
}
HORIZON_HATCH = {"near": "", "late": "///"}

VARIANT_ORDER = [
    "exit_pooled",
    "exit_2020_2022",
    "exit_minus20",
    "exit_plus20",
    "entry_pooled",
    "entry_2020_2022",
    "entry_minus20",
    "entry_plus20",
]
VARIANT_LABELS = {
    "exit_pooled": "pooled",
    "exit_2020_2022": "2020–22",
    "exit_minus20": "−20%",
    "exit_plus20": "+20%",
    "entry_pooled": "pooled",
    "entry_2020_2022": "2020–22",
    "entry_minus20": "−20%",
    "entry_plus20": "+20%",
}
SIDE_COLORS = {"exit": OKABE_ITO["orange"], "entry": OKABE_ITO["bluish_green"]}
HORIZON_COLORS = {"near": OKABE_ITO["blue"], "late": OKABE_ITO["vermillion"]}

NEAR_YEARS = {2027, 2028, 2030}
SAVE_KW = dict(bbox_inches="tight", pad_inches=0.04, facecolor="white")

PANEL_SPECS = [
    ("a", "IS_E_urban_M", "Urban IS-exiters"),
    ("b", "IS_N_urban_M", "Urban IS-entrants"),
    ("c", "rural_TO_M", "Rural intra-sectoral turnover"),
    ("d", "stay_urban_M", "Urban IS-stayers"),
    ("e", "stay_rural_M", "Rural IS-stayers"),
    ("f", "movers_M", "Total movers\n(CS-exiters + CS-entrants + CS-stayers)"),
]

CAPTION_S15 = (
    "Supplementary Fig. S15 | Sensitivity of relatively-poor-only (RPO) "
    "poverty-transition volumes to alternative post-2021 growth paths for the "
    "urban–rural subsistence ratio (RΩ), estimated with three flow-prediction "
    "approaches under BAU. Panels show (a) urban intra-sectoral status exiters "
    "(IS-exiters); (b) urban intra-sectoral status entrants (IS-entrants); "
    "(c) rural intra-sectoral turnover, the sum of IS-exiters and IS-entrants; "
    "(d) urban intra-sectoral status-persistent stayers (IS-stayers); "
    "(e) rural IS-stayers; and (f) total cross-sectoral movers, the sum of "
    "cross-sectoral status exiters (CS-exiters), entrants (CS-entrants), and "
    "stayers (CS-stayers), attributed to the origin sector. The three "
    "post-2021 RΩ paths (low, central, high) are crossed with stock-weighted "
    "transition shares, the origin–destination gravity model, and demographic "
    "cell-rate projection. Mean annual volumes are in million persons per "
    "year. Near-term means the BAU windows ending in 2027, 2028, and 2030; "
    "late-century means windows from 2030–2032 through 2098–2100. Flow "
    "volumes are annualised by interval length and expressed on the "
    "Lei-calibrated scale."
)

CAPTION_S16 = (
    "Supplementary Fig. S16 | Sensitivity of relatively-poor-only (RPO) "
    "poverty-transition volumes to CFPS transition-share specifications under "
    "the stock-weighted approach and BAU. Panels show (a) urban intra-sectoral "
    "status exiters (IS-exiters); (b) urban intra-sectoral status entrants "
    "(IS-entrants); (c) rural intra-sectoral turnover, the sum of IS-exiters "
    "and IS-entrants; (d) urban intra-sectoral status-persistent stayers "
    "(IS-stayers); (e) rural IS-stayers; and (f) total cross-sectoral movers, "
    "the sum of cross-sectoral status exiters (CS-exiters), entrants "
    "(CS-entrants), and stayers (CS-stayers), attributed to the origin sector. "
    "For the exit side, pooled shares, 2020–2022 shares, or ±20% scalings of "
    "pooled non-stay shares are used while the entry side is held at pooled "
    "values; the entry-side variants apply the corresponding changes to entry "
    "shares while holding exit shares pooled. Future BAU six-state stocks are "
    "held fixed under the 2010 Dibao-scaled × 50% median schedule. Volumes "
    "are mean annual millions of persons per year, annualised by interval "
    "length on the Lei-calibrated scale. Near-term and late-century horizons "
    "are as defined in Supplementary Fig. S15. Pooled exit and entry variants "
    "coincide with the baseline by construction."
)


def _panel_letter(ax, letter: str) -> None:
    ax.text(
        0.02,
        0.98,
        f"({letter})",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=FS_PANEL - 1,
        fontweight="bold",
        zorder=10,
    )


def _style_ax(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, axis="y", alpha=0.28, zorder=0)
    ax.tick_params(axis="both", labelsize=FS_TICK - 2)


def _require_peel_cols(df: pd.DataFrame, path: Path) -> None:
    need = ["IS_N_xstay", "IS_E_xstay", "CS_N_xstay", "CS_E_xstay", "CS_M_xstay"]
    missing = [c for c in need if c not in df.columns]
    if missing:
        raise RuntimeError(
            f"{path.name} missing peeled columns {missing}. "
            "Re-run execute_four c_fig4_r_omega_three_methods.py and "
            "d_entry_exit_share_sensitivity.py after extending "
            "sst_components_from_flows."
        )


def _agg_rpo_sector(path: Path, *, key_cols: list[str]) -> pd.DataFrame:
    """RPO sector-split volumes on Fig.4-like annual M/yr scale (peeled IS/CS)."""
    df = pd.read_csv(path)
    _require_peel_cols(df, path)
    df = df[df["stratum"] == "RPO"].copy()
    df["horizon"] = df["year1"].map(
        lambda y: (
            "near"
            if int(y) in NEAR_YEARS
            else ("late" if int(y) >= 2032 else "drop")
        )
    )
    df = df[df["horizon"] != "drop"].copy()
    dt = (df["year1"].astype(int) - df["year0"].astype(int)).clip(lower=1).astype(float)
    lei = df["lei_scale"].astype(float).replace(0.0, np.nan).fillna(1.0)
    # Peeled IS / CS: undo Lei flow scale; annualise by window length.
    df["IS_N_M"] = df["IS_N_xstay"].astype(float) / dt / lei / 1e6
    df["IS_E_M"] = df["IS_E_xstay"].astype(float) / dt / lei / 1e6
    df["CS_N_M"] = df["CS_N_xstay"].astype(float) / dt / lei / 1e6
    df["CS_E_M"] = df["CS_E_xstay"].astype(float) / dt / lei / 1e6
    df["CS_M_M"] = df["CS_M_xstay"].astype(float) / dt / lei / 1e6
    df["stayer_M"] = df["stayer"].astype(float) / dt / 1e6

    # One row per key × horizon × year1 × sector, then mean over windows.
    g = (
        df.groupby(key_cols + ["horizon", "year1", "sector"], as_index=False)[
            ["IS_N_M", "IS_E_M", "CS_N_M", "CS_E_M", "CS_M_M", "stayer_M"]
        ]
        .sum()
    )
    sec = (
        g.groupby(key_cols + ["horizon", "sector"], as_index=False)[
            ["IS_N_M", "IS_E_M", "CS_N_M", "CS_E_M", "CS_M_M", "stayer_M"]
        ]
        .mean()
    )
    urb = sec[sec["sector"] == "urban"].rename(
        columns={
            "IS_N_M": "IS_N_urban_M",
            "IS_E_M": "IS_E_urban_M",
            "CS_N_M": "CS_N_urban_M",
            "CS_E_M": "CS_E_urban_M",
            "CS_M_M": "CS_M_urban_M",
            "stayer_M": "stay_urban_M",
        }
    )
    rur = sec[sec["sector"] == "rural"].rename(
        columns={
            "IS_N_M": "IS_N_rural_M",
            "IS_E_M": "IS_E_rural_M",
            "CS_N_M": "CS_N_rural_M",
            "CS_E_M": "CS_E_rural_M",
            "CS_M_M": "CS_M_rural_M",
            "stayer_M": "stay_rural_M",
        }
    )
    out = urb[
        key_cols
        + [
            "horizon",
            "IS_N_urban_M",
            "IS_E_urban_M",
            "CS_N_urban_M",
            "CS_E_urban_M",
            "CS_M_urban_M",
            "stay_urban_M",
        ]
    ].merge(
        rur[
            key_cols
            + [
                "horizon",
                "IS_N_rural_M",
                "IS_E_rural_M",
                "CS_N_rural_M",
                "CS_E_rural_M",
                "CS_M_rural_M",
                "stay_rural_M",
            ]
        ],
        on=key_cols + ["horizon"],
        how="outer",
    )
    out["rural_TO_M"] = out["IS_N_rural_M"] + out["IS_E_rural_M"]
    out["urban_TO_M"] = out["IS_N_urban_M"] + out["IS_E_urban_M"]
    out["turnover_M"] = out["urban_TO_M"] + out["rural_TO_M"]
    out["stayer_M"] = out["stay_urban_M"] + out["stay_rural_M"]
    out["movers_M"] = (
        out["CS_E_urban_M"]
        + out["CS_N_urban_M"]
        + out["CS_E_rural_M"]
        + out["CS_N_rural_M"]
        + out["CS_M_urban_M"]
        + out["CS_M_rural_M"]
    )
    return out



def _save(out_dir: Path, stem: str, fig: plt.Figure) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    tiff = out_dir / f"{stem}.tiff"
    jpg = out_dir / f"{stem}_preview.jpg"
    fig.savefig(
        tiff, dpi=600, format="tiff", pil_kwargs={"compression": "tiff_lzw"}, **SAVE_KW
    )
    fig.savefig(jpg, dpi=180, format="jpeg", pil_kwargs={"quality": 93}, **SAVE_KW)
    plt.close(fig)
    print(f"Wrote {tiff}")
    return tiff


def plot_s15() -> tuple[Path, pd.DataFrame]:
    tot = _agg_rpo_sector(R_OMEGA_DETAIL, key_cols=["approach", "r_variant"])
    apply_matplotlib_style(svg_editable_text=False)
    fig, axes = plt.subplots(3, 2, figsize=(11.8, 10.2), sharex=False)
    n_appr = len(APPROACH_ORDER)
    n_growth = len(GROWTH_ORDER)
    bar_w = 0.10
    cluster_gap = 0.10
    cluster_span = n_growth * bar_w
    x = np.arange(n_appr, dtype=float)

    for ax, (letter, metric, title) in zip(axes.ravel(), PANEL_SPECS):
        _panel_letter(ax, letter)
        ax.set_title(title, fontsize=FS_AXES - 2, pad=4, loc="left", x=0.10)
        for hi, horizon in enumerate(("near", "late")):
            cluster_shift = (hi - 0.5) * (cluster_span + cluster_gap)
            for gi, variant in enumerate(GROWTH_ORDER):
                vals = []
                for ap in APPROACH_ORDER:
                    r = tot[
                        (tot["approach"] == ap)
                        & (tot["r_variant"] == variant)
                        & (tot["horizon"] == horizon)
                    ]
                    vals.append(float(r.iloc[0][metric]) if len(r) else np.nan)
                offset = cluster_shift + (gi - (n_growth - 1) / 2.0) * bar_w
                ax.bar(
                    x + offset,
                    vals,
                    width=bar_w * 0.92,
                    color=GROWTH_COLORS[variant],
                    hatch=HORIZON_HATCH[horizon],
                    edgecolor="0.2",
                    linewidth=0.45,
                    alpha=0.92,
                    zorder=3,
                )
        ax.set_xticks(x)
        ax.set_xticklabels(
            [APPROACH_LABELS[a] for a in APPROACH_ORDER],
            fontsize=FS_TICK - 3,
        )
        ax.set_ylim(bottom=0)
        ax.set_ylabel("Million persons / year", fontsize=FS_AXES - 3)
        _style_ax(ax)

    growth_handles = [
        Patch(
            facecolor=GROWTH_COLORS[v],
            edgecolor="0.2",
            linewidth=0.45,
            label=GROWTH_LABELS[v],
        )
        for v in GROWTH_ORDER
    ]
    horizon_handles = [
        Patch(
            facecolor="0.75",
            edgecolor="0.2",
            linewidth=0.45,
            hatch=HORIZON_HATCH[h],
            label=HORIZON_LABELS[h],
        )
        for h in ("near", "late")
    ]
    fig.tight_layout(rect=(0.02, 0.02, 0.99, 0.90))
    top = float(axes[0, 0].get_position().y1)
    leg_y = top + 0.015
    leg1 = fig.legend(
        handles=growth_handles,
        title="Growth rate of the urban–rural subsistence ratio (R_Ω)",
        frameon=False,
        fontsize=FS_LEGEND - 1,
        title_fontsize=FS_LEGEND - 1,
        loc="lower left",
        bbox_to_anchor=(0.04, leg_y),
        ncol=3,
    )
    fig.add_artist(leg1)
    fig.legend(
        handles=horizon_handles,
        title="Horizon",
        frameon=False,
        fontsize=FS_LEGEND - 1,
        title_fontsize=FS_LEGEND - 1,
        loc="lower right",
        bbox_to_anchor=(0.98, leg_y),
        ncol=2,
    )
    tiff = _save(OUT, "Supplementary_Figure_S15", fig)
    (OUT / "caption.txt").write_text(
        CAPTION_S15 + "\n", encoding="utf-8"
    )
    return tiff, tot


def plot_s16() -> tuple[Path, pd.DataFrame]:
    tot = _agg_rpo_sector(SHARE_DETAIL, key_cols=["variant"])
    plot_tot = tot[tot["variant"].isin(VARIANT_ORDER)].copy()
    apply_matplotlib_style(svg_editable_text=False)
    fig, axes = plt.subplots(3, 2, figsize=(12.0, 10.2), sharex=False)
    x = np.arange(len(VARIANT_ORDER))
    split_x = (3 + 4) / 2.0

    for ax, (letter, metric, title) in zip(axes.ravel(), PANEL_SPECS):
        _panel_letter(ax, letter)
        ax.set_title(title, fontsize=FS_AXES - 2, pad=4, loc="left", x=0.10)
        for horizon, color in HORIZON_COLORS.items():
            vals = []
            for v in VARIANT_ORDER:
                r = plot_tot[
                    (plot_tot["variant"] == v) & (plot_tot["horizon"] == horizon)
                ]
                vals.append(float(r.iloc[0][metric]) if len(r) else np.nan)
            ax.plot(x, vals, "o-", color=color, lw=1.7, ms=5.5)
        ax.axvline(split_x, color="0.55", ls="--", lw=0.9)
        ax.set_xticks(x)
        ax.set_xticklabels(
            [VARIANT_LABELS[v] for v in VARIANT_ORDER],
            fontsize=FS_TICK - 3,
            rotation=28,
            ha="right",
        )
        for tick, v in zip(ax.get_xticklabels(), VARIANT_ORDER):
            tick.set_color(
                SIDE_COLORS["entry" if v.startswith("entry") else "exit"]
            )
        ax.set_ylim(bottom=0)
        ax.set_ylabel("Million persons / year", fontsize=FS_AXES - 3)
        _style_ax(ax)

    fig.tight_layout(rect=(0.02, 0.07, 0.99, 0.92))
    top = float(axes[0, 0].get_position().y1)
    leg_y = top + 0.012
    leg1 = fig.legend(
        handles=[
            Patch(facecolor=c, edgecolor="0.2", linewidth=0.45, label=lab)
            for c, lab in zip(
                (HORIZON_COLORS["near"], HORIZON_COLORS["late"]),
                (HORIZON_LABELS["near"], HORIZON_LABELS["late"]),
            )
        ],
        frameon=False,
        fontsize=FS_LEGEND - 1,
        loc="lower left",
        bbox_to_anchor=(0.04, leg_y),
        ncol=2,
    )
    fig.add_artist(leg1)
    fig.legend(
        handles=[
            Patch(
                facecolor=SIDE_COLORS["exit"],
                edgecolor="none",
                label="Exit-side shares (IS-exiters)",
            ),
            Patch(
                facecolor=SIDE_COLORS["entry"],
                edgecolor="none",
                label="Entry-side shares (IS-entrants)",
            ),
        ],
        frameon=False,
        fontsize=FS_LEGEND - 1,
        loc="lower center",
        ncol=2,
        bbox_to_anchor=(0.55, 0.01),
    )
    tiff = _save(S16_OUT, "Supplementary_Figure_S16", fig)
    (S16_OUT / "caption.txt").write_text(
        CAPTION_S16 + "\n", encoding="utf-8"
    )
    return tiff, tot


def main() -> None:
    if not R_OMEGA_DETAIL.exists():
        raise FileNotFoundError(R_OMEGA_DETAIL)
    tiff, _ = plot_s15()
    print(f"Wrote {tiff}")


if __name__ == "__main__":
    main()

