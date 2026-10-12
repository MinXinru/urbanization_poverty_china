# -*- coding: utf-8 -*-
"""
Okabe–Ito color-blind-friendly palette and dissertation figure style.

Source: color_blind.pdf (Kei Ito & Masataka Okabe, 2002)
        color_blind_friendly_figure.txt in productivity template folder.

Main-text figure grammar (locked to Fig.1, 2026-07-18)
----------------------------------------------------
Use for ALL main-text figures (Fig.1–Fig.4 composites and subpanels):
  - Canvas: landscape golden ratio (width:height = φ:1), default 10.0 × 6.18 in
  - Axes labels: 13 pt; tick labels: 12 pt; panel letters: 14 pt
  - Legend: 9 pt (two sizes smaller than axes)
SI figures should reuse the same type sizes via apply_matplotlib_style();
dense SI grids may use a different figsize.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# RGB(0–255) → hex
OKABE_ITO = {
    "black": "#000000",
    "orange": "#E69F00",
    "sky_blue": "#56B4E9",
    "bluish_green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermillion": "#D55E00",
    "reddish_purple": "#CC79A7",
}

PALETTE_8 = [
    OKABE_ITO["blue"],
    OKABE_ITO["vermillion"],
    OKABE_ITO["bluish_green"],
    OKABE_ITO["orange"],
    OKABE_ITO["sky_blue"],
    OKABE_ITO["reddish_purple"],
    OKABE_ITO["yellow"],
    OKABE_ITO["black"],
]

REGION_ORDER = ["Eastern", "Central", "Western"]
REGION_COLORS = {
    "Eastern": OKABE_ITO["blue"],
    "Central": OKABE_ITO["vermillion"],
    "Western": OKABE_ITO["bluish_green"],
}

# Diverging: blue (negative) → white → vermillion (positive)
OKABE_DIV = LinearSegmentedColormap.from_list(
    "okabe_div",
    [OKABE_ITO["blue"], "#FFFFFF", OKABE_ITO["vermillion"]],
)

# ---------------------------------------------------------------------------
# Locked main-text figure grammar (= Fig.1)
# ---------------------------------------------------------------------------
GOLDEN_RATIO = (1.0 + 5.0**0.5) / 2.0  # φ ≈ 1.618
FIG_WIDTH_IN = 10.0
FIG_HEIGHT_IN = FIG_WIDTH_IN / GOLDEN_RATIO  # ≈ 6.18 in
FIGSIZE_GOLDEN = (FIG_WIDTH_IN, FIG_HEIGHT_IN)
FIGSIZE_MAIN = FIGSIZE_GOLDEN  # alias for main-text composites
FIG_DPI = 200

FS_AXES = 13
FS_TICK = 12
FS_LEGEND = 9  # two sizes smaller than FS_AXES
FS_PANEL = 14

# Back-compat aliases (older scripts import FONT_*)
FONT_TITLE = FS_PANEL
FONT_XLABEL = FS_AXES
FONT_YLABEL = FS_AXES
FONT_TICK = FS_TICK
FONT_LEGEND = FS_LEGEND
FONT_PANEL = FS_PANEL
FONT_ANNOT = FS_TICK


def figsize_golden(width_in: float = FIG_WIDTH_IN) -> tuple[float, float]:
    """Landscape golden-ratio figsize (width, height) in inches."""
    return (float(width_in), float(width_in) / GOLDEN_RATIO)


def apply_matplotlib_style(*, svg_editable_text: bool = True) -> None:
    """Apply main-text type + Okabe–Ito colors (Times New Roman serif)."""
    rc = {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif", "Times"],
        "font.size": FS_TICK,
        "axes.labelsize": FS_AXES,
        "axes.titlesize": FS_PANEL,
        "xtick.labelsize": FS_TICK,
        "ytick.labelsize": FS_TICK,
        "legend.fontsize": FS_LEGEND,
        "axes.edgecolor": OKABE_ITO["black"],
        "axes.labelcolor": OKABE_ITO["black"],
        "text.color": OKABE_ITO["black"],
        "xtick.color": OKABE_ITO["black"],
        "ytick.color": OKABE_ITO["black"],
        "figure.dpi": FIG_DPI,
        "savefig.dpi": FIG_DPI,
    }
    if svg_editable_text:
        rc["svg.fonttype"] = "none"
    plt.rcParams.update(rc)


def new_main_figure(*args, **kwargs):
    """
    Create a main-text figure with locked golden canvas + style.

    Usage:
        fig, ax = new_main_figure()
        fig, axes = new_main_figure(2, 2)
    """
    apply_matplotlib_style(svg_editable_text=kwargs.pop("svg_editable_text", True))
    kwargs.setdefault("figsize", FIGSIZE_MAIN)
    kwargs.setdefault("dpi", FIG_DPI)
    return plt.subplots(*args, **kwargs)
