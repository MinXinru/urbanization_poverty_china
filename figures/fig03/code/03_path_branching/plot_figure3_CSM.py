# -*- coding: utf-8 -*-
"""8. Combined Fig.3: wave-annualised curves | personal-line trails (4×4).

Layout (reading order left→right, top→bottom):
  Columns: curve_AP | trail_AP | curve_RPO | trail_RPO
  Rows:    Total | urban intra-sectoral | rural intra-sectoral | cross-sectional

Panel letters (a)–(p) in reading order:
  Row1: (a) curve AP  (b) trail AP  (c) curve RPO  (d) trail RPO
  Row2: (e)–(h) urban intra-sectoral; Row3: (i)–(l) rural intra-sectoral;
  Row4: (m)–(p) cross-sectional (CS-entrants / CS-exiters / CS-stayers).

Trails: CFPS individual 2010–2022 endpoints; Urban/Rural on LEFT;
coloured NP / RPO / AP on RIGHT; no flow % digits or flow arrows;
SST callouts on urban/rural/movers trail panels only (N-left / E-right);
Total trail panels (b)(d) have no SST callouts.

Curves: Method-1 national stock-weighted volumes (CFPS dual rates × Lei
six-state stocks); schedule envelope excl LMI/UMI (S07–S18); focal S23.
Legends on both curve columns (AP and RPO). Reuses logic from
7_plot_figure3_wave_curves.py.

Does not modify 6_plot_figure3.py / 7_plot_figure3_wave_curves.py outputs.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.font_manager import FontProperties

HERE = Path(__file__).resolve().parent
PACKAGE_ROOT = HERE.parents[1]
PROJECT_ROOT = HERE.parents[1]
STYLE_DIR = PROJECT_ROOT / "7_output" / "code" / "style"
sys.path.insert(0, str(HERE / "_helpers"))
sys.path.insert(0, str(STYLE_DIR))

from okabe_ito_style import (  # noqa: E402
    FS_AXES,
    FS_LEGEND,
    FS_PANEL,
    FS_TICK,
    apply_matplotlib_style,
)

# ---- trail helper (script 6) ----
_spec_t = importlib.util.spec_from_file_location(
    "m10_trails", HERE / "_helpers" / "_plot_fig3_trails_2points.py"
)
m10 = importlib.util.module_from_spec(_spec_t)
assert _spec_t.loader is not None
_spec_t.loader.exec_module(m10)

# ---- curve module (script 7) ----
_spec_c = importlib.util.spec_from_file_location(
    "fig3_curves", HERE / "7_plot_figure3_wave_curves.py"
)
curves = importlib.util.module_from_spec(_spec_c)
assert _spec_c.loader is not None
_spec_c.loader.exec_module(curves)

OUT = HERE / "fig3_plot_outputs"
OUT.mkdir(parents=True, exist_ok=True)

WINDOW = [2010, 2022]
SAMPLE = None

# Printed size: Fig.1/2 floor FS_LEGEND=9 @ ~10.2"; prior Fig.3 used ~13 pt
# on ~15″ canvas so on-page type matches. Combined figure is wider (~16″).
FIGSIZE = (16.0, 11.2)
_REF_WIDTH = 10.2
_FS_FLOOR = float(FS_LEGEND)  # 9
FS_MIN = max(13, int(round(_FS_FLOOR * FIGSIZE[0] / _REF_WIDTH)))  # → 13 floor
# Cap scale so 16″ does not blow past the established Fig.3 print floor.
FS_MIN = 13
FS_PANEL_C = max(FS_PANEL, FS_MIN + 3)  # 16
FS_AXES_C = max(FS_AXES, FS_MIN + 2)  # 15
FS_TICK_C = max(FS_TICK, FS_MIN + 1)  # 14
FS_LEGEND_C = FS_MIN  # 13
FS_SST = FS_MIN  # 13 — Stayers / Intra-sectoral turnover / Movers (bold roman)
# Trail-only SST codes (IS-entrants / IS-exiters; CS-entrants / CS-exiters on movers): smaller italic
# than hierarchy labels. Curve legends stay uniform (no special code style).
FS_SST_CODE = FS_MIN - 1  # 12

# Patch trail helper fonts for this combined canvas
m10.FS_PANEL = FS_PANEL_C
m10.FS_AXES = FS_AXES_C
m10.FS_TICK = FS_TICK_C
m10.FS_LEGEND = FS_LEGEND_C

# Curve module font floor
curves.FS_PANEL = FS_PANEL_C
curves.FS_AXES = FS_AXES_C
curves.FS_TICK = FS_TICK_C
curves.FS_LEGEND = FS_LEGEND_C

ROW_META = [
    ("all", "Total", "total"),
    ("uu", "urban intra-sectoral", "intra"),
    ("rr", "rural intra-sectoral", "intra"),
    ("movers", "cross-sectional", "cross"),
]
STRATA = ["AP", "RPO"]
COL_TITLES = {
    "AP": "AP",
    "RPO": "RPO",
}
# Right-side NP/RPO/AP labels: default helper x=1.02; shift left by 0.03.
STATUS_LABEL_X = 1.02 - 0.03  # 0.99
# Trail-RPO SST: raise Intra-sectoral turnover / IS-entrants / IS-exiters collectively.
SST_RPO_DY = 0.10
# Curve-column legends: left-align to a shared axes-x (row-1 reference).
# Row 1 is drawn with loc="upper right"; its left edge becomes the column
# anchor so rows 2–4 share the same left edge (not right-edge drift).
CURVE_LEGEND_LOC_REF = "upper right"
CURVE_LEGEND_LOC_ALIGNED = "upper left"
# (a)–(p) reading order
LETTERS = [
    ["a", "b", "c", "d"],
    ["e", "f", "g", "h"],
    ["i", "j", "k", "l"],
    ["m", "n", "o", "p"],
]


def _sector_filter(pairs: pd.DataFrame, kind: str) -> pd.DataFrame:
    if kind == "uu":
        return pairs[(pairs.sector0 == "urban") & (pairs.sector1 == "urban")]
    if kind == "rr":
        return pairs[(pairs.sector0 == "rural") & (pairs.sector1 == "rural")]
    if kind == "movers":
        return pairs[pairs.sector0 != pairs.sector1]
    return pairs


def _sst_callouts(ax, mode: str, *, trail_rpo: bool = False) -> None:
    cat_kw = dict(
        fontsize=FS_SST,
        fontweight="bold",
        fontstyle="normal",
        family="serif",
        transform=ax.transAxes,
        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="0.55", alpha=0.92),
        zorder=8,
        clip_on=False,
    )
    # Serif italic, smaller than bold hierarchy labels (Stayers / Movers / …).
    code_fp = FontProperties(
        family="serif",
        style="italic",
        size=FS_SST_CODE,
        weight="normal",
    )
    code_kw = dict(
        fontproperties=code_fp,
        transform=ax.transAxes,
        bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="0.55", alpha=0.92),
        zorder=8,
        clip_on=False,
    )
    if mode == "total":
        # Total trail panels (b)(d): no on-canvas SST callouts.
        return
    elif mode == "intra":
        dy = SST_RPO_DY if trail_rpo else 0.0
        if trail_rpo:
            # Align Stayers with RPO status-band centre (data y=1.0 → axes ~0.5).
            # ylim is (-0.55, 2.55); (1.0+0.55)/(2.55+0.55)=0.5.
            ax.text(0.50, 0.50, "IS-stayers", ha="center", va="center", color="0.25", **cat_kw)
        else:
            ax.text(0.50, 0.08, "IS-stayers", ha="center", va="bottom", color="0.25", **cat_kw)
        ax.text(0.16, 0.52 + dy, "IS-entrants", ha="center", va="center", color="0.20", **code_kw)
        ax.text(0.84, 0.52 + dy, "IS-exiters", ha="center", va="center", color="0.20", **code_kw)
        ax.text(
            0.50, 0.62 + dy, "Intra-sectoral turnover",
            ha="center", va="bottom", color="0.25", **cat_kw,
        )
    elif mode == "cross":
        ax.text(0.16, 0.52, "CS-entrants", ha="center", va="center", color="0.20", **code_kw)
        ax.text(0.84, 0.52, "CS-exiters", ha="center", va="center", color="0.20", **code_kw)
        ax.text(0.50, 0.62, "Movers", ha="center", va="bottom", color="0.25", **cat_kw)
        if trail_rpo:
            ax.text(0.50, 0.36, "CS-stayers", ha="center", va="center", color="0.20", **code_kw)


def _draw_trail(
    ax,
    pairs: pd.DataFrame,
    sf: str,
    letter: str,
    *,
    sst_mode: str | None,
    show_year_xlabel: bool,
) -> None:
    """Personal-line trails; no flow arrows / no flow % digits."""
    sub = pairs[(pairs.status0 == sf) | (pairs.status1 == sf)]
    tr = sub if (SAMPLE is None or len(sub) <= SAMPLE) else sub.sample(n=SAMPLE, random_state=7)
    tr = tr.copy()
    tr["y0"] = tr.apply(lambda r: m10._y(r.status0, r.sector0), axis=1)
    tr["y1"] = tr.apply(lambda r: m10._y(r.status1, r.sector1), axis=1)
    m10._draw_highlight_both(
        ax,
        tr,
        letter,
        sf,
        WINDOW,
        show_status_labels=True,
        status_label_side="right",  # NP / RPO / AP on RIGHT (coloured)
        status_label_x=STATUS_LABEL_X,
        show_year_xlabel=show_year_xlabel,
    )
    if sst_mode:
        _sst_callouts(ax, sst_mode, trail_rpo=(sf == "RPO"))


def _curve_legend_handles(row: int) -> list:
    series = curves._panel_map(row)
    handles = [
        Line2D(
            [0], [0], color=c, lw=curves.LW_FOCAL,
            marker="o", markersize=3.5, label=lab,
        )
        for _, c, lab in series
    ]
    # Percentile detail (2.5–97.5%) lives in the caption only.
    handles.append(
        Patch(
            facecolor="0.55",
            edgecolor="none",
            alpha=0.35,
            label="Schedule envelope",
        )
    )
    return handles


def _place_curve_legend(
    ax,
    row: int,
    *,
    loc: str,
    bbox_to_anchor: tuple[float, float] | None = None,
):
    """Uniform legend font for all entries (no special IS/CS italic/size)."""
    kw = dict(
        handles=_curve_legend_handles(row),
        loc=loc,
        fontsize=FS_LEGEND_C,
        frameon=False,
        borderaxespad=0.2,
    )
    if bbox_to_anchor is not None:
        kw["bbox_to_anchor"] = bbox_to_anchor
        kw["borderaxespad"] = 0.0
    return ax.legend(**kw)


def _legend_left_top_axes(ax, leg) -> tuple[float, float]:
    """Legend box left/top in axes fraction (needs a drawn renderer)."""
    fig = ax.figure
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bbox = leg.get_window_extent(renderer).transformed(ax.transAxes.inverted())
    return float(bbox.x0), float(bbox.y1)


def _draw_curve(
    ax,
    agg: pd.DataFrame,
    stratum: str,
    row: int,
    letter: str,
    *,
    ylabel: bool,
    show_legend: bool,
    show_xlabel: bool,
    col_title: str | None,
    legend_loc: str | None = None,
    legend_bbox: tuple[float, float] | None = None,
) -> object | None:
    sub = agg[agg["stratum"] == stratum].copy()
    for col, color, lab in curves._panel_map(row):
        curves._draw_series(ax, sub, col, color, label=lab)
    ax.set_xlim(2010.5, 2022.5)
    ax.set_xticks([2012, 2014, 2016, 2018, 2020, 2022])
    ax.tick_params(axis="both", labelsize=FS_TICK_C)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.text(
        0.02,
        0.96,
        letter,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=FS_PANEL_C,
        fontweight="bold",
        zorder=20,
    )
    if ylabel:
        ax.set_ylabel(
            "Annual volume\n(million persons/year)",
            fontsize=FS_AXES_C,
        )
    if col_title is not None:
        ax.set_title(col_title, fontsize=FS_AXES_C, pad=4)
    if show_xlabel:
        ax.set_xlabel("Year", fontsize=FS_AXES_C)
    leg = None
    if show_legend:
        leg = _place_curve_legend(
            ax,
            row,
            loc=legend_loc or CURVE_LEGEND_LOC_REF,
            bbox_to_anchor=legend_bbox,
        )
    y0, y1 = ax.get_ylim()
    ax.set_ylim(max(0.0, y0), y1 * 1.05 if y1 > 0 else 1.0)
    return leg


def _caption() -> str:
    return (
        "Fig. 3 | Linked-person transition trails and wave-annualised national "
        "flow volumes for absolute poverty (AP) and relatively-poor-only poverty "
        "(RPO), 2010–2022. Within each poverty block, columns pair national "
        "curves (left) with companion personal-line trails (right) for AP "
        "(left block) and RPO (right block); column headers mark AP and RPO. "
        "Rows (top to bottom): Total; urban intra-sectoral; rural "
        "intra-sectoral; cross-sectional (panels a–p). Trail panels plot CFPS "
        "individuals observed at the 2010 and 2022 endpoints: Urban/Rural on "
        "the left within each status band; non-poor (NP), RPO and AP coloured "
        "on the right. Urban and rural trails carry italic IS-entrants (left) and "
        "IS-exiters (right) callouts with IS-stayers and Intra-sectoral turnover labels; "
        "cross-sectional curves separate CS-entrants, CS-exiters and CS-stayers. Movers trails "
        "retain CS-entrants (left) and CS-exiters (right) labels; panel (p) additionally labels "
        "CS-stayers. Total trails (b, d) omit these labels; flow percentages are "
        "not shown. Curve panels report national volumes under stock-weighted "
        "transition shares (Method 1; million persons/year)—CFPS dual "
        "exit/entry rates applied to Lei schedule-specific six-state stocks "
        "over consecutive CFPS biennial windows, annualised by ÷2—not raw "
        "CFPS sample counts. Thick coloured lines mark the focal 2010 "
        "Dibao-scaled × 50% median schedule (S23); thin same-colour lines and "
        "shaded bands show other absolute×relative schedules (S01–S06, "
        "S19–S24; World Bank LMI/UMI schedules S07–S18 excluded), with the "
        "shaded schedule envelope spanning the 2.5th–97.5th percentile across "
        "those schedules. Legends appear on both AP and RPO curve columns. "
        "Points mark each window’s end year."
    )


def main() -> None:
    np.random.seed(7)
    apply_matplotlib_style(svg_editable_text=True)

    pair_path = m10.resolve_pair_file()
    print(f"trails pairs: {pair_path}")
    print(f"curves Method-1: {curves.M1_PATH}")
    print(
        f"fonts: min={FS_MIN} tick={FS_TICK_C} axes={FS_AXES_C} "
        f"panel={FS_PANEL_C} legend={FS_LEGEND_C} "
        f"sst_hierarchy={FS_SST} sst_code_italic={FS_SST_CODE} "
        f"(Fig1/2 floor {_FS_FLOOR} @ {_REF_WIDTH}\"; canvas {FIGSIZE[0]}\")"
    )

    pr = m10._pairs_from_window_file(pair_path, WINDOW[0], WINDOW[1])
    if pr.empty:
        raise RuntimeError(
            f"Empty {WINDOW[0]}–{WINDOW[1]} pairs — run scripts 1–2 first."
        )
    print(f"trail window {WINDOW[0]}–{WINDOW[1]}: n={len(pr):,}")

    agg = curves._load_agg()
    print(
        f"curves: {len(agg):,} rows; specs={sorted(agg['spec_id'].unique())}; "
        f"years={sorted(agg['year_plot'].unique())}"
    )

    fig = plt.figure(figsize=FIGSIZE)
    # Equal 4×4 axes boxes (same width & height). Left margin reserves a
    # fixed figure-x column for rotated row labels so long/short strings
    # share one vertical line (ha=center at ROW_LABEL_X).
    ROW_LABEL_X = 0.028
    gs = GridSpec(
        4,
        4,
        figure=fig,
        width_ratios=[1, 1, 1, 1],
        height_ratios=[1, 1, 1, 1],
        wspace=0.30,
        hspace=0.28,
        left=0.10,
        right=0.985,
        top=0.94,
        bottom=0.05,
    )

    axes = [[fig.add_subplot(gs[r, c]) for c in range(4)] for r in range(4)]

    # Col 0: was COL0_DX=-0.02; move right by 0.03 → COL0_DX=+0.01.
    # Then equalize the three inter-column gaps (col0–1, 1–2, 2–3).
    # After equalization, shift col 1 (trail AP) by COL1_DX (was +0.02; now 0).
    # Geometric spacing unchanged from trail|curve era (curve|trail content).
    COL0_DX = 0.01
    COL1_DX = 0.0
    pos0 = [axes[r][0].get_position() for r in range(4)]
    pos3 = [axes[r][3].get_position() for r in range(4)]
    box_w = pos0[0].width
    left_edge = pos0[0].x0 + COL0_DX
    right_edge = pos3[0].x1
    gap = (right_edge - left_edge - 4.0 * box_w) / 3.0
    for c in range(4):
        x0 = left_edge + c * (box_w + gap)
        for r in range(4):
            p = axes[r][c].get_position()
            axes[r][c].set_position([x0, p.y0, box_w, p.height])
    # Col 1 (trail AP: b,f,j,n): post-equalization nudge (COL1_DX).
    for r in range(4):
        p = axes[r][1].get_position()
        axes[r][1].set_position([p.x0 + COL1_DX, p.y0, box_w, p.height])
    # Report layout params for audit / chat
    xs = [axes[0][c].get_position().x0 for c in range(4)]
    x1s = [axes[0][c].get_position().x1 for c in range(4)]
    gaps = [xs[c + 1] - x1s[c] for c in range(3)]
    print(
        f"layout: COL0_DX={COL0_DX} COL1_DX={COL1_DX} GridSpec.wspace=0.30 "
        f"box_w={box_w:.4f} equal_gap={gap:.4f} "
        f"x0={[round(x, 4) for x in xs]} gaps={[round(g, 4) for g in gaps]}"
    )

    for r, (kind, row_title, sst_mode) in enumerate(ROW_META):
        pf = _sector_filter(pr, kind)
        for block, stratum in enumerate(STRATA):
            # curve | trail within each AP / RPO block
            c_curve = 0 if block == 0 else 2
            c_trail = 1 if block == 0 else 3
            ax_t = axes[r][c_trail]
            ax_c = axes[r][c_curve]
            let_t = LETTERS[r][c_trail]
            let_c = LETTERS[r][c_curve]

            # SST on trail columns for rows 2–4 only (Total b/d: none)
            _draw_trail(
                ax_t,
                pf,
                stratum,
                let_t,
                sst_mode=None if r == 0 else sst_mode,
                show_year_xlabel=(r == 3),
            )
            # Row-1 legends first (upper right); rows 2–4 get shared left
            # anchor after measurement below.
            _draw_curve(
                ax_c,
                agg,
                stratum,
                r,
                let_c,
                ylabel=(block == 0),  # Annual volume on AP curve column
                show_legend=(r == 0),
                show_xlabel=(r == 3),
                col_title=None,
                legend_loc=CURVE_LEGEND_LOC_REF,
            )

            if r == 0:
                # Block titles centred over curve|trail pair
                mid = 0.5 * (
                    ax_c.get_position().x0
                    + ax_t.get_position().x1
                )
                fig.text(
                    mid,
                    0.965,
                    COL_TITLES[stratum],
                    ha="center",
                    va="bottom",
                    fontsize=FS_AXES_C,
                    fontweight="bold",
                )

        # Shared figure-x column: long vs short labels stay vertically aligned
        pos = axes[r][0].get_position()
        fig.text(
            ROW_LABEL_X,
            pos.y0 + 0.5 * pos.height,
            row_title,
            ha="center",
            va="center",
            fontsize=FS_AXES_C,
            fontweight="bold",
            rotation=90,
        )

    # Left-align curve-column legends to row-1 left edge (AP col=0, RPO col=2).
    fig.canvas.draw()
    legend_report: dict[str, dict] = {}
    for block, stratum in enumerate(STRATA):
        c_curve = 0 if block == 0 else 2
        ax_ref = axes[0][c_curve]
        leg_ref = ax_ref.get_legend()
        if leg_ref is None:
            raise RuntimeError(f"Missing row-1 legend on {stratum} curve column")
        x_left, y_top = _legend_left_top_axes(ax_ref, leg_ref)
        # Re-place row 1 with upper-left + measured anchor so all four
        # rows share identical loc/bbox (true left-edge alignment).
        for r in range(4):
            ax_c = axes[r][c_curve]
            _place_curve_legend(
                ax_c,
                r,
                loc=CURVE_LEGEND_LOC_ALIGNED,
                bbox_to_anchor=(x_left, y_top),
            )
        legend_report[stratum] = {
            "col": c_curve + 1,  # 1-based column in 4×4
            "ref_loc": CURVE_LEGEND_LOC_REF,
            "aligned_loc": CURVE_LEGEND_LOC_ALIGNED,
            "bbox_to_anchor": (round(x_left, 4), round(y_top, 4)),
        }
    print(
        "curve legends (left-aligned to row-1 left edge): "
        + "; ".join(
            f"{k}: loc={v['aligned_loc']} bbox_to_anchor={v['bbox_to_anchor']} "
            f"(ref was {v['ref_loc']}, col {v['col']})"
            for k, v in legend_report.items()
        )
    )

    base = OUT / "Fig3_trails_plus_curves_4x4"
    fig.savefig(
        str(base) + ".tiff",
        format="tiff",
        dpi=600,
        bbox_inches="tight",
        facecolor="white",
        pil_kwargs={"compression": "tiff_lzw"},
    )
    print("saved", str(base) + ".tiff")
    fig.savefig(
        str(base) + ".jpg",
        dpi=m10.FIG_DPI,
        format="jpg",
        bbox_inches="tight",
        facecolor="white",
        pil_kwargs={"quality": 95},
    )
    print("saved", str(base) + ".jpg")
    svg_path = OUT / "Figure3_CSM_updated.svg"
    fig.savefig(svg_path, format="svg", bbox_inches="tight", facecolor="white")
    print("saved", svg_path)
    plt.close(fig)

    cap = _caption()
    (OUT / "Fig3_trails_plus_curves_caption.txt").write_text(cap + "\n", encoding="utf-8")
    print("saved", OUT / "Fig3_trails_plus_curves_caption.txt")
    print(cap)


if __name__ == "__main__":
    main()
