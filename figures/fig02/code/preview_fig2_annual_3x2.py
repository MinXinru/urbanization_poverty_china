# -*- coding: utf-8 -*-
"""Fig.2: 3×2 annual RH channels (Fig.1 type + future insets).

Layout:
  cols: AP | RPO  (column headers on top row only)
  rows: UISE, RISE, PE  (vertical y-axis labels on left column)

Main: annual change 2000–2100 (Focal HIST+SSPs + grey other schedules + envelopes).
Inset: zoom on 2025–2100; vertical mark at 2030.
Panel letters / fonts match Fig.1 (okabe_ito_style).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
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
SHARED = _paths.shared
from okabe_ito_style import (  # noqa: E402
    FS_AXES,
    FS_LEGEND,
    FS_PANEL,
    FS_TICK,
    OKABE_ITO,
    apply_matplotlib_style,
)

YOY = ROOT / "data" / "rh_national_yoy.csv"
OUT = ROOT / "output"
FINAL_DIR = OUT / "final"
OUT_JPG = OUT / "preview_fig2_annual_3x2_fig1style.jpg"
OUT_TIFF = FINAL_DIR / "Figure2_annual_3x2_600dpi.tiff"
LAYOUT_DIR = OUT / "layout_tune"
OUT_COORD = LAYOUT_DIR / "Fig2_coordinate_preview.jpg"
OUT_COORDS_TXT = LAYOUT_DIR / "Fig2_layout_coords.txt"
# Main panels (a)–(f); insets continue as (g)–(l).
INSET_LETTER = {"a": "g", "b": "h", "c": "i", "d": "j", "e": "k", "f": "l"}

LMI_UMI = {f"S{i:02d}" for i in range(7, 19)}
CHANNELS = ["UISE", "RISE", "PE"]
STRATA = ["AP", "RPO"]
SCEN_COLOR = {
    "HQD": OKABE_ITO["bluish_green"],
    "BAU": OKABE_ITO["blue"],
    "LSD": OKABE_ITO["orange"],
    "HSD": OKABE_ITO["vermillion"],
}
SCEN_ORDER = ["HQD", "BAU", "LSD", "HSD"]
PROJ_START = 2026
# Inset: parent-axes fraction (x0, y0, w, h)
INSET_BOUNDS_DEFAULT = (0.47, 0.14, 0.47, 0.50)  # a/c → insets g/i; +0.01 vs prior 0.13
INSET_BOUNDS = {
    "a": INSET_BOUNDS_DEFAULT,
    "b": (0.47, 0.43, 0.47, 0.50),  # +0.03 vs prior 0.40
    "c": INSET_BOUNDS_DEFAULT,
    "d": (0.47, 0.43, 0.47, 0.50),  # +0.03 vs prior 0.40
    "e": (0.47, 0.16, 0.47, 0.50),  # inset (k); −0.01 vs prior 0.17
    "f": (0.47, 0.19, 0.47, 0.50),  # +0.06 vs default
}
# Force positive y-axis headroom (pp/yr); tick at the limit need not be shown.
YMAX_POS = {"a": 0.5, "f": 0.15}
# Locked main-panel figure-fraction positions (rows lowered to cut gap above legend).
MAIN_POS = {
    "a": (0.100, 0.660, 0.404, 0.240),
    "b": (0.556, 0.660, 0.404, 0.240),
    "c": (0.100, 0.390, 0.404, 0.240),
    "d": (0.556, 0.390, 0.404, 0.240),
    "e": (0.100, 0.120, 0.404, 0.240),
    "f": (0.556, 0.120, 0.404, 0.240),
}
# Bottom legend: −0.02 + 0.02 up.
LEGEND_ANCHOR = (0.5, 0.00)
SUBPLOT_ADJUST = dict(left=0.10, right=0.98, top=0.96, bottom=0.11, hspace=0.28, wspace=0.18)
FIGSIZE = (10.0, 7.0)


def _savefig_trim_bottom(fig, path: Path, **kwargs) -> None:
    """Crop to content; keep ~0.03 figure-fraction pad under the legend bottom."""
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


def _envelope(
    df: pd.DataFrame, channel: str, *, exclude_lmi_umi: bool = True
) -> pd.DataFrame:
    """2.5–97.5% across schedules; optionally drop LMI/UMI (S07–S18)."""
    g = df[~df["spec_id"].isin(LMI_UMI)].copy() if exclude_lmi_umi else df.copy()
    rows = []
    for y, sub in g.groupby("year_mid"):
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


def _apply_pos_ymax(ax, letter: str) -> None:
    """Ensure positive y-axis length; do not require a labeled tick at the limit."""
    if letter not in YMAX_POS:
        return
    ylo, yhi = ax.get_ylim()
    ax.set_ylim(ylo, max(yhi, float(YMAX_POS[letter])))


def _draw_panel(
    ax,
    df: pd.DataFrame,
    stratum: str,
    channel: str,
    letter: str,
    *,
    show_ylabel: bool,
    col_title: str | None,
):
    sub = df[df["stratum"] == stratum].copy()
    hist = sub[sub["scenario"] == "HIST"]
    fut = sub[sub["scenario"].isin(SCEN_ORDER)]

    others_h = hist[(~hist["is_focus"]) & (~hist["spec_id"].isin(LMI_UMI))]
    for _, g in others_h.groupby("spec_id"):
        g = g.sort_values("year_mid")
        ax.plot(
            g["year_mid"],
            100.0 * g[channel],
            color="#B0B0B0",
            lw=0.45,
            alpha=0.35,
            zorder=1,
        )
    # Projections: retain full schedule set (incl. LMI/UMI), matching Fig.1 / caption.
    others_f = fut[(~fut["is_focus"]) & (fut["scenario"] == "BAU")]
    for _, g in others_f.groupby("spec_id"):
        g = g.sort_values("year_mid")
        ax.plot(
            g["year_mid"],
            100.0 * g[channel],
            color="#B0B0B0",
            lw=0.45,
            alpha=0.30,
            zorder=1,
        )

    env_h = _envelope(hist, channel, exclude_lmi_umi=True)
    if not env_h.empty:
        ax.fill_between(
            env_h["year_mid"],
            env_h["lo"],
            env_h["hi"],
            color=OKABE_ITO["black"],
            alpha=0.14,
            zorder=2,
            linewidth=0,
        )
    env_b = _envelope(fut[fut["scenario"] == "BAU"], channel, exclude_lmi_umi=False)
    if not env_b.empty:
        ax.fill_between(
            env_b["year_mid"],
            env_b["lo"],
            env_b["hi"],
            color=OKABE_ITO["blue"],
            alpha=0.16,
            zorder=2,
            linewidth=0,
        )

    focal_h = hist[hist["is_focus"]].sort_values("year_mid")
    ax.plot(
        focal_h["year_mid"],
        100.0 * focal_h[channel],
        color=OKABE_ITO["black"],
        lw=2.2,
        zorder=4,
    )
    for scen in SCEN_ORDER:
        g = fut[(fut["is_focus"]) & (fut["scenario"] == scen)].sort_values("year_mid")
        if g.empty:
            continue
        ax.plot(
            g["year_mid"],
            100.0 * g[channel],
            color=SCEN_COLOR[scen],
            lw=1.55 if scen == "BAU" else 1.25,
            zorder=3,
        )

    ax.axhline(0.0, color="#444444", lw=0.6, zorder=0)
    ax.axvline(PROJ_START, color=OKABE_ITO["black"], ls=":", lw=1.0, zorder=3)
    ax.set_xlim(2000, 2100)
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

    ax_in = inset_axes(
        ax,
        width="100%",
        height="100%",
        loc="lower left",
        bbox_to_anchor=INSET_BOUNDS[letter],
        bbox_transform=ax.transAxes,
        borderpad=0,
    )
    for _, g in others_f.groupby("spec_id"):
        g = g.sort_values("year_mid")
        ax_in.plot(
            g["year_mid"], 100.0 * g[channel], color="#B0B0B0", lw=0.4, alpha=0.30, zorder=1
        )
    if not env_b.empty:
        ax_in.fill_between(
            env_b["year_mid"],
            env_b["lo"],
            env_b["hi"],
            color=OKABE_ITO["blue"],
            alpha=0.16,
            zorder=2,
            linewidth=0,
        )
    for scen in SCEN_ORDER:
        g = fut[(fut["is_focus"]) & (fut["scenario"] == scen)].sort_values("year_mid")
        if g.empty:
            continue
        ax_in.plot(
            g["year_mid"],
            100.0 * g[channel],
            color=SCEN_COLOR[scen],
            lw=1.4 if scen == "BAU" else 1.15,
            zorder=3,
        )

    ax_in.axhline(0.0, color="#666666", lw=0.5)
    ax_in.axvline(2030.0, color="#666666", ls="--", lw=0.85, zorder=2)
    ax_in.axvline(PROJ_START, color="#666666", ls=":", lw=0.7, zorder=2)
    ax_in.set_xlim(PROJ_START, 2100)
    ax_in.set_xticks([2030, 2050, 2100])
    ax_in.tick_params(axis="both", labelsize=FS_TICK)
    ax_in.set_xlabel("")
    ax_in.set_ylabel("")
    ax_in.text(
        0.97,
        0.03,
        f"({INSET_LETTER[letter]})",
        transform=ax_in.transAxes,
        ha="right",
        va="bottom",
        fontsize=FS_PANEL,
        fontweight="bold",
        zorder=10,
    )
    for spine in ax_in.spines.values():
        spine.set_linewidth(0.6)
    ax_in.patch.set_facecolor("none")
    ax_in.patch.set_alpha(0.0)

    _apply_pos_ymax(ax, letter)
    return ax_in


def _write_coordinate_preview(fig, axes, inset_map) -> None:
    """Overlay figure-fraction + parent-axes-fraction grids for layout tuning."""
    for x in np.arange(0.0, 1.01, 0.1):
        fig.add_artist(
            plt.Line2D(
                [x, x],
                [0.0, 1.0],
                transform=fig.transFigure,
                color="#1F77B4",
                lw=0.5,
                alpha=0.45,
                zorder=100,
                clip_on=False,
            )
        )
        fig.add_artist(
            plt.Line2D(
                [0.0, 1.0],
                [x, x],
                transform=fig.transFigure,
                color="#1F77B4",
                lw=0.5,
                alpha=0.45,
                zorder=100,
                clip_on=False,
            )
        )
        fig.text(
            x,
            0.005,
            f"{x:.1f}",
            transform=fig.transFigure,
            ha="center",
            va="bottom",
            fontsize=7,
            color="#1F77B4",
            fontweight="bold",
            zorder=101,
        )
        fig.text(
            0.005,
            x,
            f"{x:.1f}",
            transform=fig.transFigure,
            ha="left",
            va="center",
            fontsize=7,
            color="#1F77B4",
            fontweight="bold",
            zorder=101,
        )

    lines = [
        "MAIN panels — figure fraction bbox (x0, y0, w, h); origin = figure lower-left.",
        f"Current MAIN_POS: {MAIN_POS}",
        f"Current INSET_BOUNDS (parent-axes fraction): {INSET_BOUNDS}",
        f"INSET_LETTER: {INSET_LETTER}",
        f"LEGEND_ANCHOR: {LEGEND_ANCHOR}",
        f"FIGSIZE: {FIGSIZE}",
        f"YMAX_POS (forced positive headroom): {YMAX_POS}",
        "",
    ]
    letters = [["a", "b"], ["c", "d"], ["e", "f"]]
    for r in range(3):
        for c in range(2):
            letter = letters[r][c]
            ax = axes[r, c]
            pos = ax.get_position()
            x0, y0, w, h = pos.x0, pos.y0, pos.width, pos.height
            fig.add_artist(
                Rectangle(
                    (x0, y0),
                    w,
                    h,
                    transform=fig.transFigure,
                    fill=False,
                    edgecolor="#1F77B4",
                    lw=1.6,
                    ls="-",
                    zorder=102,
                    clip_on=False,
                )
            )
            fig.text(
                x0 + 0.01,
                y0 + h - 0.02,
                f"MAIN ({letter}) fig=({x0:.3f},{y0:.3f},{w:.3f},{h:.3f})",
                transform=fig.transFigure,
                ha="left",
                va="top",
                fontsize=8,
                color="#1F77B4",
                fontweight="bold",
                zorder=103,
                bbox=dict(
                    boxstyle="round,pad=0.15",
                    facecolor="white",
                    edgecolor="#1F77B4",
                    alpha=0.9,
                ),
            )
            lines.append(f"  MAIN ({letter}): ({x0:.3f}, {y0:.3f}, {w:.3f}, {h:.3f})")

    lines += ["", "INSET panels — parent-axes fraction bbox (x0, y0, w, h).", ""]
    for ax in axes.ravel():
        for x in np.arange(0.0, 1.01, 0.1):
            ax.plot(
                [x, x],
                [0.0, 1.0],
                transform=ax.transAxes,
                color="#888888",
                lw=0.35,
                alpha=0.45,
                zorder=20,
                clip_on=False,
            )
            ax.plot(
                [0.0, 1.0],
                [x, x],
                transform=ax.transAxes,
                color="#888888",
                lw=0.35,
                alpha=0.45,
                zorder=20,
                clip_on=False,
            )

    for letter, (ax, bounds) in inset_map.items():
        x0, y0, w, h = bounds
        ax.add_patch(
            Rectangle(
                (x0, y0),
                w,
                h,
                transform=ax.transAxes,
                fill=False,
                edgecolor="magenta",
                lw=1.2,
                ls="--",
                zorder=22,
            )
        )
        ax.plot([x0], [y0], "o", color="magenta", ms=4, transform=ax.transAxes, zorder=23)
        ax.text(
            x0,
            max(y0 - 0.04, 0.01),
            f"INSET ({INSET_LETTER[letter]}) under ({letter}) ({x0:.2f},{y0:.2f},{w:.2f},{h:.2f})",
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=7,
            color="magenta",
            fontweight="bold",
            zorder=23,
            clip_on=False,
        )
        lines.append(
            f"  INSET ({INSET_LETTER[letter]}) under ({letter}): ({x0:.2f}, {y0:.2f}, {w:.2f}, {h:.2f})"
        )

    LAYOUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_COORD, dpi=200, format="jpg", pil_kwargs={"quality": 92})
    OUT_COORDS_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_COORD}")
    print(f"Wrote {OUT_COORDS_TXT}")


def main() -> None:
    apply_matplotlib_style(svg_editable_text=False)
    df = pd.read_csv(YOY).copy()
    df["year_mid"] = df["year_to"].astype(float)

    fig, axes = plt.subplots(3, 2, figsize=FIGSIZE, dpi=200, sharex="col")
    letters = [["a", "b"], ["c", "d"], ["e", "f"]]
    inset_map = {}
    for r, ch in enumerate(CHANNELS):
        for c, stratum in enumerate(STRATA):
            letter = letters[r][c]
            ax_in = _draw_panel(
                axes[r, c],
                df,
                stratum,
                ch,
                letter,
                show_ylabel=(c == 0),
                col_title=(stratum if r == 0 else None),
            )
            inset_map[letter] = (axes[r, c], INSET_BOUNDS[letter])

    axes[2, 0].set_xlabel("Year", fontsize=FS_AXES)
    axes[2, 1].set_xlabel("Year", fontsize=FS_AXES)

    handles = [
        Line2D([0], [0], color=OKABE_ITO["black"], lw=2.2, label="HIST(Focal line)"),
        Line2D([0], [0], color="#B0B0B0", lw=1.1, label="Other Abs.×rel. schedules"),
        Patch(facecolor=OKABE_ITO["black"], alpha=0.14, label="HIST envelope (2.5–97.5%)"),
        Patch(facecolor=OKABE_ITO["blue"], alpha=0.16, label="BAU envelope (2.5–97.5%)"),
        Line2D([0], [0], color=SCEN_COLOR["HQD"], lw=1.55, label="HQD(Focal line)"),
        Line2D([0], [0], color=SCEN_COLOR["BAU"], lw=2.0, label="BAU(Focal line)"),
        Line2D([0], [0], color=SCEN_COLOR["LSD"], lw=1.55, label="LSD(Focal Line)"),
        Line2D([0], [0], color=SCEN_COLOR["HSD"], lw=1.55, label="HSD(Focal Line)"),
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=4,
        frameon=False,
        fontsize=FS_LEGEND,
        bbox_to_anchor=LEGEND_ANCHOR,
        handlelength=1.4,
        labelspacing=0.28,
        borderpad=0.35,
        borderaxespad=0.0,
    )
    fig.subplots_adjust(**SUBPLOT_ADJUST)
    for r in range(3):
        for c in range(2):
            axes[r, c].set_position(MAIN_POS[letters[r][c]])
    OUT.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    _savefig_trim_bottom(fig, OUT_JPG, dpi=300, format="jpg", pil_kwargs={"quality": 95})
    print(f"Wrote {OUT_JPG}")
    _savefig_trim_bottom(
        fig, OUT_TIFF, dpi=600, format="tiff", pil_kwargs={"compression": "tiff_lzw"}
    )
    print(f"Wrote {OUT_TIFF}")

    _write_coordinate_preview(fig, axes, inset_map)
    plt.close(fig)


if __name__ == "__main__":
    main()
