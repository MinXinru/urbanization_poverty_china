# -*- coding: utf-8 -*-
"""Private Fig.3 trail drawing helpers (imported by 6_plot_figure3.py).

Self-contained STATUS_Y / colors; reads pipeline outputs when present.
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # 03_path_branching/
# parents: [0]=code, [1]=20260723_submission_files, [2]=project root
PROJECT_ROOT = ROOT.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PROJECT_ROOT / "7_output" / "code" / "style"))

from common import FIG_OUT, OUT_DIR  # noqa: E402

try:
    from okabe_ito_style import (  # noqa: E402
        FIG_DPI,
        FS_AXES,
        FS_LEGEND,
        FS_PANEL,
        FS_TICK,
        OKABE_ITO,
        apply_matplotlib_style,
    )
except ImportError:  # mirror locked Fig.1 grammar if style module missing
    FIG_DPI = 200
    FS_AXES, FS_TICK, FS_LEGEND, FS_PANEL = 13, 12, 9, 14
    OKABE_ITO = {
        "black": "#000000",
        "vermillion": "#D55E00",
        "blue": "#0072B2",
        "bluish_green": "#009E73",
    }

    def apply_matplotlib_style(svg_editable_text: bool = True) -> None:
        rc = {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif", "Times"],
            "font.size": FS_TICK,
            "axes.labelsize": FS_AXES,
            "axes.titlesize": FS_PANEL,
            "xtick.labelsize": FS_TICK,
            "ytick.labelsize": FS_TICK,
            "legend.fontsize": FS_LEGEND,
            "figure.dpi": FIG_DPI,
            "savefig.dpi": FIG_DPI,
        }
        if svg_editable_text:
            rc["svg.fonttype"] = "none"
        plt.rcParams.update(rc)


STATUS_Y = {"AP": 0.0, "RPO": 1.0, "NP": 2.0}
STATUS_COLOR = {
    "AP": OKABE_ITO["vermillion"],
    "RPO": OKABE_ITO["blue"],
    "NP": OKABE_ITO["bluish_green"],
}

OUT = FIG_OUT
PAIR_FILE = Path(os.environ.get("FIG3_PAIR_FILE", OUT_DIR / "2_AP_RPO_NP_window.csv"))
_WAVE_PANEL = OUT_DIR / "1_AP_RPO_NP_wave_panel.csv"
# Living-project fallback if pipeline not yet run
_LEGACY_WAVE = (
    PROJECT_ROOT
    / "7_output"
    / "data"
    / "fig3_micro_mechanisms"
    / "data"
    / "_pack_02"
    / "fig3_cfps_allspecs_wave_panel_hhwork_internalmedian.csv"
)
_LEGACY_PAIRS = (
    PROJECT_ROOT
    / "4_path_branching"
    / "01_transitions"
    / "outputs"
    / "1_classify_link_pairs_cfps_hhwork_internalmedian.csv"
)


def resolve_pair_file() -> Path:
    if PAIR_FILE.exists():
        return PAIR_FILE
    if _LEGACY_PAIRS.exists():
        return _LEGACY_PAIRS
    raise FileNotFoundError(
        f"No pair file. Run scripts 1–2 first ({PAIR_FILE.name}) "
        f"or provide legacy pairs."
    )


def resolve_wave_panel() -> Path:
    if _WAVE_PANEL.exists():
        return _WAVE_PANEL
    if _LEGACY_WAVE.exists():
        return _LEGACY_WAVE
    raise FileNotFoundError(f"No wave panel at {_WAVE_PANEL}")


def _person_wave(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Pipeline window file already has year0/year1; legacy consecutive pairs too
    if "window" in df.columns:
        # Already endpoint pairs — stack endpoints
        a = df[["pid", "year0", "status0", "sector0", "w0"]].rename(
            columns={"year0": "year", "status0": "status", "sector0": "sector", "w0": "w"}
        )
        b = df[["pid", "year1", "status1", "sector1", "w1"]].rename(
            columns={"year1": "year", "status1": "status", "sector1": "sector", "w1": "w"}
        )
        return pd.concat([a, b]).drop_duplicates(["pid", "year"])
    a = df[["pid", "year0", "status0", "sector0", "weight0"]].rename(
        columns={"year0": "year", "status0": "status", "sector0": "sector", "weight0": "w"}
    )
    b = df[["pid", "year1", "status1", "sector1", "weight1"]].rename(
        columns={"year1": "year", "status1": "status", "sector1": "sector", "weight1": "w"}
    )
    return pd.concat([a, b]).drop_duplicates(["pid", "year"])


def _pairs_from_window_file(path: Path, y0: int, y1: int) -> pd.DataFrame:
    """Prefer direct rows from script-2 window file."""
    df = pd.read_csv(path)
    if "window" in df.columns:
        tag = f"{y0}-{y1}"
        sub = df[df["window"] == tag].copy()
        if sub.empty:
            return pd.DataFrame()
        # Ensure w0/w1
        if "w0" not in sub.columns:
            sub["w0"] = sub.get("weight0", sub.get("weight", np.nan))
        if "w1" not in sub.columns:
            sub["w1"] = sub.get("weight1", sub.get("weight", np.nan))
        return sub
    # Legacy consecutive-wave pairs → rebuild endpoints via person-wave
    pw = _person_wave(path)
    return _pairs(pw, y0, y1)


def _pairs(pw: pd.DataFrame, y0: int, y1: int) -> pd.DataFrame:
    a = pw[pw.year == y0][["pid", "status", "sector", "w"]].rename(
        columns={"status": "status0", "sector": "sector0", "w": "w0"}
    )
    b = pw[pw.year == y1][["pid", "status", "sector", "w"]].rename(
        columns={"status": "status1", "sector": "sector1", "w": "w1"}
    )
    m = a.merge(b, on="pid", how="inner")
    m["year0"], m["year1"] = y0, y1
    return m


def _sample(pairs: pd.DataFrame, n: int) -> pd.DataFrame:
    if len(pairs) <= n:
        return pairs
    return pairs.sample(n=n, random_state=7)


def _y(status: str, sector: str) -> float:
    base = STATUS_Y.get(status, 0.0)
    off = 0.15 if sector == "urban" else -0.15
    return base + off + np.random.uniform(-0.12, 0.12)


def _full_pu_by_year() -> dict:
    path = resolve_wave_panel()
    df = pd.read_csv(path)
    out = {}
    if "is_focus" in df.columns:
        df = df[df.is_focus]
        for _, r in df.iterrows():
            out[(int(r.year), "AP")] = float(r.P_u_AP) * 100
            out[(int(r.year), "RPO")] = float(r.P_u_RPO) * 100
    else:
        for _, r in df.iterrows():
            out[(int(r.year), "AP")] = float(r.P_u_AP) * 100
            out[(int(r.year), "RPO")] = float(r.P_u_RPO) * 100
    return out


def _full_h_by_year() -> dict:
    path = resolve_wave_panel()
    df = pd.read_csv(path)
    out = {}
    if "is_focus" in df.columns:
        df = df[df.is_focus]
    for _, r in df.iterrows():
        out[(int(r.year), "AP")] = float(r.H_AP) * 100
        out[(int(r.year), "RPO")] = float(r.H_RPO) * 100
    return out


def _style_ax(ax) -> None:
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def _style_frame(
    ax,
    letter: str,
    years: list[int],
    *,
    show_status_labels: bool = True,
    status_label_side: str = "left",
    status_label_x: float | None = None,
    show_year_xlabel: bool = True,
) -> None:
    """Frame for trail panels.

    Left y-ticks are always Urban/Rural within each status band.
    Coloured NP / RPO / AP go on ``status_label_side`` ('left', 'right', or
    'none'); prefer 'right' so they do not overlap Urban/Rural.
    ``status_label_x`` is axes-fraction x via ``get_yaxis_transform``
    (default −0.02 left / 1.02 right).
    """
    for st, y in STATUS_Y.items():
        ax.axhline(y, color=STATUS_COLOR[st], lw=0.8, alpha=0.35)
    ax.set_xlim(years[0] - 1.5, years[1] + 1.5)
    ax.set_ylim(-0.55, 2.55)
    ax.set_yticks([-0.15, 0.15, 0.85, 1.15, 1.85, 2.15])
    ax.set_yticklabels(["Rural", "Urban", "Rural", "Urban", "Rural", "Urban"])
    side = (status_label_side or "left").lower()
    if not show_status_labels:
        side = "none"
    if side == "left":
        x_lab = -0.02 if status_label_x is None else float(status_label_x)
        for st, y in STATUS_Y.items():
            ax.text(
                x_lab, y, st, transform=ax.get_yaxis_transform(),
                va="center", ha="right", fontsize=FS_TICK, color=STATUS_COLOR[st],
                fontweight="bold", clip_on=False,
            )
    elif side == "right":
        # Top→bottom: NP (green), RPO (blue), AP (orange/vermillion)
        x_lab = 1.02 if status_label_x is None else float(status_label_x)
        for st, y in STATUS_Y.items():
            ax.text(
                x_lab, y, st, transform=ax.get_yaxis_transform(),
                va="center", ha="left", fontsize=FS_TICK, color=STATUS_COLOR[st],
                fontweight="bold", clip_on=False,
            )
    if show_year_xlabel:
        ax.set_xlabel("Year", fontsize=FS_AXES)
    else:
        ax.set_xlabel("")
    ax.set_xticks(years)
    ax.set_xticklabels([str(y) for y in years])
    ax.tick_params(axis="both", labelsize=FS_TICK)
    ax.text(
        0.02, 0.98, letter, transform=ax.transAxes,
        ha="left", va="top", fontsize=FS_PANEL, fontweight="bold",
    )
    _style_ax(ax)


def _draw_highlight_both(
    ax,
    trails,
    letter,
    hl_status,
    years,
    *,
    show_status_labels: bool = True,
    status_label_side: str = "left",
    status_label_x: float | None = None,
    show_year_xlabel: bool = True,
) -> None:
    gray = (0.4, 0.4, 0.4)
    base_segs, base_cols, hl_segs, hl_cols = [], [], [], []
    for _, r in trails.iterrows():
        seg = [(r["year0"], r["y0"]), (r["year1"], r["y1"])]
        is_hl = (
            ((r["status0"] == hl_status) and (r["sector0"] == "rural"))
            or ((r["status1"] == hl_status) and (r["sector1"] == "rural"))
        )
        if is_hl:
            hl_segs.append(seg)
            hl_cols.append((*gray, 0.05))
        else:
            base_segs.append(seg)
            base_cols.append((*mcolors.to_rgb(STATUS_COLOR.get(r["status0"], "#888")), 0.10))
    if hl_segs:
        ax.add_collection(LineCollection(hl_segs, colors=hl_cols, linewidths=0.45, rasterized=False))
    if base_segs:
        ax.add_collection(LineCollection(base_segs, colors=base_cols, linewidths=0.45, rasterized=False))
    _style_frame(
        ax, letter, years,
        show_status_labels=show_status_labels,
        status_label_side=status_label_side,
        status_label_x=status_label_x,
        show_year_xlabel=show_year_xlabel,
    )
