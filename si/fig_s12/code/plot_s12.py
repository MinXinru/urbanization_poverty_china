# -*- coding: utf-8 -*-
"""Supplementary Fig. S12 — CFPS annual Ravallion–Huppi ΔH, 2010–2022.

Figure-2 grammar (3×2: UISE / RISE / PE × AP | RPO). Consecutive CFPS waves
(biennial) are annualised by dividing endpoint RH terms by Δt (=2 yr).
Schedules: S01–S06, S19–S24 (LMI/UMI S07–S18 excluded). Historical only.
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
RH_CSV = DATA / "FigS12_cfps_annual_RH.csv"
from okabe_ito_style import (  # noqa: E402
    FS_AXES,
    FS_LEGEND,
    FS_PANEL,
    FS_TICK,
    OKABE_ITO,
    apply_matplotlib_style,
)

FOCAL = "S23"
LMI_UMI = {f"S{i:02d}" for i in range(7, 19)}
CHANNELS = ["UISE", "RISE", "PE"]
STRATA = ["AP", "RPO"]
FIGSIZE = (10.0, 7.0)
MAIN_POS = {
    "a": (0.100, 0.660, 0.404, 0.240),
    "b": (0.556, 0.660, 0.404, 0.240),
    "c": (0.100, 0.390, 0.404, 0.240),
    "d": (0.556, 0.390, 0.404, 0.240),
    "e": (0.100, 0.120, 0.404, 0.240),
    "f": (0.556, 0.120, 0.404, 0.240),
}
LEGEND_ANCHOR = (0.5, 0.00)


def _rh_terms(hu0, hr0, su0, hu1, hr1, su1) -> dict[str, float]:
    hu0, hr0, su0 = float(hu0), float(hr0), float(su0)
    hu1, hr1, su1 = float(hu1), float(hr1), float(su1)
    sr1 = 1.0 - su1
    rise = sr1 * (hr1 - hr0)
    uise = su1 * (hu1 - hu0)
    pe = (hu0 - hr0) * (su1 - su0)
    h0 = su0 * hu0 + (1.0 - su0) * hr0
    h1 = su1 * hu1 + sr1 * hr1
    return {"RISE": rise, "UISE": uise, "PE": pe, "dH": h1 - h0, "H_0": h0, "H_1": h1}


def build_annual_rh(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sid, g in panel.groupby("spec_id"):
        g = g.sort_values("year")
        years = g["year"].astype(int).tolist()
        meta = g.iloc[0]
        for y0, y1 in zip(years[:-1], years[1:]):
            r0 = g[g["year"] == y0].iloc[0]
            r1 = g[g["year"] == y1].iloc[0]
            dt = float(y1 - y0)
            for stratum in STRATA:
                rh = _rh_terms(
                    r0[f"H_u_{stratum}"],
                    r0[f"H_r_{stratum}"],
                    r0["S_u"],
                    r1[f"H_u_{stratum}"],
                    r1[f"H_r_{stratum}"],
                    r1["S_u"],
                )
                rows.append(
                    {
                        "spec_id": sid,
                        "abs_id": meta["abs_id"],
                        "rel_share": meta["rel_share"],
                        "is_focus": bool(meta["is_focus"]) or sid == FOCAL,
                        "stratum": stratum,
                        "year_from": int(y0),
                        "year_to": int(y1),
                        "year_mid": float(y1),  # Fig.2 annual plot uses year_to
                        "dt": dt,
                        "RISE": rh["RISE"] / dt,
                        "UISE": rh["UISE"] / dt,
                        "PE": rh["PE"] / dt,
                        "dH": rh["dH"] / dt,
                        "H_0": rh["H_0"],
                        "H_1": rh["H_1"],
                    }
                )
    return pd.DataFrame(rows)


def _envelope(df: pd.DataFrame, channel: str) -> pd.DataFrame:
    rows = []
    for y, sub in df.groupby("year_mid"):
        v = 100.0 * sub[channel].to_numpy(float)
        v = v[np.isfinite(v)]
        if len(v) < 2:
            continue
        rows.append(
            {
                "year_mid": float(y),
                "lo": float(np.nanpercentile(v, 2.5)),
                "hi": float(np.nanpercentile(v, 97.5)),
            }
        )
    return pd.DataFrame(rows)


def _draw_panel(
    ax,
    df: pd.DataFrame,
    stratum: str,
    channel: str,
    letter: str,
    *,
    show_ylabel: bool,
    col_title: str | None,
) -> None:
    sub = df[df["stratum"] == stratum].copy()
    others = sub[~sub["is_focus"]]
    for _, g in others.groupby("spec_id"):
        g = g.sort_values("year_mid")
        ax.plot(
            g["year_mid"],
            100.0 * g[channel],
            color="#B0B0B0",
            lw=0.45,
            alpha=0.35,
            zorder=1,
        )
    env = _envelope(sub, channel)
    if not env.empty:
        ax.fill_between(
            env["year_mid"],
            env["lo"],
            env["hi"],
            color=OKABE_ITO["black"],
            alpha=0.14,
            zorder=2,
            linewidth=0,
        )
    focal = sub[sub["is_focus"]].sort_values("year_mid")
    ax.plot(
        focal["year_mid"],
        100.0 * focal[channel],
        color=OKABE_ITO["black"],
        lw=2.2,
        zorder=4,
        marker="o",
        markersize=4.0,
    )
    ax.axhline(0.0, color="#444444", lw=0.6, zorder=0)
    ax.set_xlim(2011.5, 2022.5)
    ax.set_xticks([2012, 2014, 2016, 2018, 2020, 2022])
    if show_ylabel:
        ax.set_ylabel(channel, fontsize=FS_AXES, rotation=90)
    if col_title is not None:
        ax.set_title(col_title, fontsize=FS_AXES, pad=4)
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
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _savefig_trim_bottom(fig, path: Path, **kwargs) -> None:
    from matplotlib.transforms import Bbox

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    boxes = [ax.get_tightbbox(renderer) for ax in fig.axes if ax.get_visible()]
    for leg in fig.legends:
        boxes.append(leg.get_window_extent(renderer))
    union = Bbox.union([b for b in boxes if b is not None])
    union = union.transformed(fig.dpi_scale_trans.inverted())
    pad_in = 0.03 * FIGSIZE[1]
    side = 0.04
    bbox = Bbox.from_extents(
        max(0.0, float(union.x0) - side),
        max(0.0, float(union.y0) - pad_in),
        min(FIGSIZE[0], float(union.x1) + side),
        min(FIGSIZE[1], float(union.y1) + side),
    )
    fig.savefig(path, bbox_inches=bbox, **kwargs)


def main() -> None:
    if not RH_CSV.is_file():
        raise SystemExit(f"Missing plot-ready CSV: {RH_CSV}")
    rh = pd.read_csv(RH_CSV)
    rh = rh[~rh["spec_id"].isin(LMI_UMI)].copy()
    if "is_focus" in rh.columns:
        rh["is_focus"] = rh["spec_id"].eq(FOCAL) | rh["is_focus"].astype(bool)
    else:
        rh["is_focus"] = rh["spec_id"].eq(FOCAL)
    chk = rh[(rh["spec_id"] == FOCAL) & (rh["stratum"] == "AP")].copy()
    if not chk.empty and {"RISE", "UISE", "PE", "dH"}.issubset(chk.columns):
        err = (chk["RISE"] + chk["UISE"] + chk["PE"] - chk["dH"]).abs().max()
        print(f"Verify annual RH: max |RISE+UISE+PE−dH| = {err:.3e}")

    apply_matplotlib_style(svg_editable_text=False)
    fig, axes = plt.subplots(3, 2, figsize=FIGSIZE, dpi=200, sharex="col")
    letters = [["a", "b"], ["c", "d"], ["e", "f"]]
    for r, ch in enumerate(CHANNELS):
        for c, stratum in enumerate(STRATA):
            letter = letters[r][c]
            _draw_panel(
                axes[r, c],
                rh,
                stratum,
                ch,
                letter,
                show_ylabel=(c == 0),
                col_title=(stratum if r == 0 else None),
            )
    axes[2, 0].set_xlabel("Year", fontsize=FS_AXES)
    axes[2, 1].set_xlabel("Year", fontsize=FS_AXES)

    handles = [
        Line2D([0], [0], color=OKABE_ITO["black"], lw=2.2, marker="o",
               markersize=4, label="HIST(Focal line)"),
        Line2D([0], [0], color="#B0B0B0", lw=1.1, label="Other Abs.×rel. schedules"),
        Patch(facecolor=OKABE_ITO["black"], alpha=0.14, label="HIST envelope (2.5–97.5%)"),
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=3,
        frameon=False,
        fontsize=FS_LEGEND,
        bbox_to_anchor=LEGEND_ANCHOR,
        handlelength=1.4,
        labelspacing=0.28,
        borderpad=0.35,
        borderaxespad=0.0,
    )
    for r in range(3):
        for c in range(2):
            axes[r, c].set_position(MAIN_POS[letters[r][c]])

    OUT.mkdir(parents=True, exist_ok=True)
    jpg = OUT / "Supplementary_Figure_S12_preview.jpg"
    tif = OUT / "Supplementary_Figure_S12.tiff"
    _savefig_trim_bottom(fig, jpg, dpi=300, format="jpg", pil_kwargs={"quality": 95})
    _savefig_trim_bottom(
        fig, tif, dpi=600, format="tiff", pil_kwargs={"compression": "tiff_lzw"}
    )
    plt.close(fig)
    print(f"Wrote {jpg}")
    print(f"Wrote {tif}")
        print(f"n rows={len(rh)} windows={sorted(rh['year_to'].unique())}")


if __name__ == "__main__":
    main()
