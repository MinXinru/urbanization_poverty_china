#!/usr/bin/env python3
"""Fig. 4 — RPO (main) and AP (companion) 6-panel layout (3×2).

(a–e) Method 1 stock-weighted focal S23 trajectories + Abs.×rel.
      schedule envelopes (2.5–97.5%): filled grey HIST / blue future for
      solid-line series; blue thin dashed outline for dashed-line series.
(f)   Three-method violins for six RPO/AP flow series in windows
      2000–2030 and 2030–2100; pool schedules × SSPs.
      Units: mean annual million persons / year (not interval-summed).
      Short x-ticks: stock-weighted / gravity / demographic
      (full Glossary §7 names in caption only).
      Markers: Focal (S23), LIC (S05), LMI (S11), UMI (S17) at BAU.

JPG preview + TIFF @ 600 dpi LZW. No SVG. No on-canvas figure title.
Bottom scenario legend matches Fig.1 labels / order / line weights.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"
from okabe_ito_style import (  # noqa: E402
    FS_AXES as _FS_AXES_BASE,
    FS_LEGEND as _FS_LEGEND_BASE,
    FS_PANEL as _FS_PANEL_BASE,
    FS_TICK as _FS_TICK_BASE,
    OKABE_ITO,
    apply_matplotlib_style,
)

# Print floor like Fig.3: Fig.1/2 FS_LEGEND=9 @ ~10.2" → min 13 pt on ~16"
# three-column canvas so printed type matches Fig.3 (not tiny Fig.1/2 pt).
FIGSIZE = (16.2, 10.2)
_REF_WIDTH = 10.2
FS_MIN = 13  # same established Fig.3 print floor
FS_PANEL = max(_FS_PANEL_BASE, FS_MIN + 3)  # 16
FS_AXES = max(_FS_AXES_BASE, FS_MIN + 2)  # 15
FS_TICK = max(_FS_TICK_BASE, FS_MIN + 1)  # 14
FS_LEGEND = FS_MIN  # 13

OUT = ROOT / "output"
FOCAL_SPEC = "S23"
# Fig.1 scenario grammar (labels, order, colours, line weights).
SSP = ["BAU", "LSD", "HSD", "HQD"]
SCEN_ORDER = ["HQD", "BAU", "LSD", "HSD"]  # Fig.1 legend order
SCN_COLORS = {
    "HQD": OKABE_ITO["bluish_green"],
    "BAU": OKABE_ITO["blue"],
    "LSD": OKABE_ITO["orange"],
    "HSD": OKABE_ITO["vermillion"],
}
SCEN_LABEL = {
    "HQD": "HQD(Focal line)",
    "BAU": "BAU(Focal line)",
    "LSD": "LSD(Focal Line)",
    "HSD": "HSD(Focal Line)",
}
OBS_LABEL = "HIST(Focal line)"
ENV_LABEL = "Abs.×rel. schedule envelope"
ENV_LABEL_DASHED = "Abs.×rel. schedule envelope, dashed series"
HIST_COLOR = OKABE_ITO["black"]
ENV_COLOR_HIST = "#808080"  # grey schedule envelope (pre-projection)
ENV_COLOR_FUT = OKABE_ITO["blue"]  # blue schedule envelope (post-projection)
ENV_ALPHA_HIST = 0.25
ENV_ALPHA_FUT = 0.18
ENV_LW_DASHED = 0.90  # thin dashed outline for dashed-line series envelopes
PROJ_START = 2026
LW_FOCAL = 2.0  # Fig.1 BAU
LW_OTHER = 1.55  # Fig.1 HQD/LSD/HSD
LW_HIST = 2.3  # Fig.1 HIST

# LMI/UMI World Bank schedules — exclude from HIST-style envelopes (Fig.1/3).
LMI_UMI = {f"S{i:02d}" for i in range(7, 19)}
ALL_SPECS = [f"S{i:02d}" for i in range(1, 25)]
HIST_ENV_SPECS = [s for s in ALL_SPECS if s not in LMI_UMI]

LS_N = "-"
LS_E = "--"
LS_URBAN = "-"
LS_RURAL = "--"

# Method labels used for the already-grouped panel (f) values.
METHOD_META: list[tuple[str, str, str, Path | None]] = [
    ("M1", "stock-weighted", "Stock-weighted transition shares", None),
    ("M2", "gravity", "Gravity-based transition model", None),
    ("M3", "demographic", "Demographic composition-based projection", None),
]

# Focal / income-group markers at BAU (same grammar as 3-method violin SI figure).
MARKER_SPECS: list[tuple[str, str, str, str]] = [
    ("focal", "S23", "Focal", "*"),
    ("lic", "S05", "LIC", "o"),
    ("lmi", "S11", "LMI", "s"),
    ("umi", "S17", "UMI", "D"),
]
MARKER_EDGE = {
    "focal": OKABE_ITO["black"],
    "lic": OKABE_ITO["blue"],
    "lmi": OKABE_ITO["orange"],
    "umi": OKABE_ITO["reddish_purple"],
}
FOCAL_SCENARIO = "BAU"

OUT_RPO_JPG = "fig4_RPO_6panel_preview.jpg"
OUT_RPO_TIF = "fig4_RPO_6panel_preview.tiff"
OUT_AP_JPG = "fig4_AP_6panel_preview.jpg"
OUT_AP_TIF = "fig4_AP_6panel_preview.tiff"
VALUES_CSV = DATA / "fig4_panel_f_rpo_violin_values.csv"

INTERVALS = [
    ("2000–2030", "early"),
    ("2030–2100", "late"),
]

# Panel (f) series: short legend (= caption short gloss); full phrases in caption.
VIOLIN_SERIES = [
    ("IS_N_urban", "urban IS-entrants", OKABE_ITO["vermillion"]),
    ("IS_E_urban", "urban IS-exiters", OKABE_ITO["bluish_green"]),
    ("stay_urban", "urban IS-stayers", OKABE_ITO["sky_blue"]),
    ("rural_origin_movers", "rural-origin movers", OKABE_ITO["orange"]),
    ("urban_origin_movers", "urban-origin movers", OKABE_ITO["reddish_purple"]),
]


def _to_m(s: pd.Series | np.ndarray) -> pd.Series:
    return pd.Series(s).astype(float) / 1.0e6


def _panel_letter(ax, letter: str) -> None:
    ax.text(
        0.02,
        0.96,
        f"({letter})",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=FS_PANEL,
        fontweight="bold",
        zorder=20,
    )


def _get_series(agg: pd.DataFrame, scenario: str, stratum: str) -> pd.DataFrame:
    return (
        agg[(agg["scenario"] == scenario) & (agg["stratum"] == stratum)]
        .sort_values("year1")
        .copy()
    )


def _role_cols(kind: str) -> list[tuple[str, str]]:
    if kind == "turnover_urban":
        return [("N", "IS_N_urban"), ("E", "IS_E_urban")]
    if kind == "turnover_rural":
        return [("N", "IS_N_rural"), ("E", "IS_E_rural")]
    if kind == "stayers":
        return [("urban", "stay_urban"), ("rural", "stay_rural")]
    if kind == "movers_rural_origin":
        return [("N", "CS_N_rural_origin"), ("E", "CS_E_rural_origin"), ("M", "CS_M_rural_origin")]
    if kind == "movers_urban_origin":
        return [("N", "CS_N_urban_origin"), ("E", "CS_E_urban_origin"), ("M", "CS_M_urban_origin")]
    raise KeyError(kind)


def _linestyle(key: str) -> str:
    if key == "N":
        return LS_N
    if key == "E":
        return LS_E
    if key == "M":
        return ":"
    if key == "urban":
        return LS_URBAN
    if key == "rural":
        return LS_RURAL
    raise KeyError(key)


def _envelope_band(
    agg: pd.DataFrame,
    *,
    stratum: str,
    col: str,
    scenario: str,
    specs: list[str],
    year_min: int | None = None,
    year_max: int | None = None,
) -> pd.DataFrame:
    """2.5–97.5% across poverty-line schedules for one scenario."""
    sub = agg[
        (agg["stratum"] == stratum)
        & (agg["scenario"] == scenario)
        & (agg["spec_id"].isin(specs))
    ]
    if year_min is not None:
        sub = sub[sub["year1"] >= year_min]
    if year_max is not None:
        sub = sub[sub["year1"] <= year_max]
    rows = []
    for y, g in sub.groupby("year1"):
        vals = _to_m(g[col]).to_numpy(dtype=float)
        vals = vals[np.isfinite(vals)]
        if vals.size == 0:
            continue
        rows.append(
            {
                "year1": int(y),
                "lo": float(np.percentile(vals, 2.5)),
                "hi": float(np.percentile(vals, 97.5)),
                "n_specs": int(vals.size),
            }
        )
    return pd.DataFrame(rows)


def _draw_envelope_outline(ax, env: pd.DataFrame, *, color: str) -> None:
    """Blue/grey thin dashed outline of 2.5–97.5% band (no fill)."""
    if env is None or env.empty:
        return
    kw = dict(color=color, ls="--", lw=ENV_LW_DASHED, alpha=0.90, zorder=2.5)
    ax.plot(env["year1"], env["lo"], **kw)
    ax.plot(env["year1"], env["hi"], **kw)


def _draw_schedule_envelopes(
    ax,
    agg_all: pd.DataFrame,
    stratum: str,
    kind: str,
) -> None:
    """Abs.×rel. schedule envelopes.

    Solid-line series (IS-entrants / urban stayers): filled grey HIST + blue future.
    Dashed-line series (IS-exiters / rural stayers): thin dashed outline only
    (grey HIST edge, blue future edge) — avoids a second heavy filled band.
    """
    for key, col in _role_cols(kind):
        hist = _envelope_band(
            agg_all,
            stratum=stratum,
            col=col,
            scenario="HIST",
            specs=HIST_ENV_SPECS,
            year_max=PROJ_START,
        )
        fut = _envelope_band(
            agg_all,
            stratum=stratum,
            col=col,
            scenario="BAU",
            specs=ALL_SPECS,
            year_min=PROJ_START,
        )
        if _linestyle(key) in ("--", ":"):
            _draw_envelope_outline(ax, hist, color=ENV_COLOR_HIST)
            _draw_envelope_outline(ax, fut, color=ENV_COLOR_FUT)
            continue
        for env, color, alpha in (
            (hist, ENV_COLOR_HIST, ENV_ALPHA_HIST),
            (fut, ENV_COLOR_FUT, ENV_ALPHA_FUT),
        ):
            if env is None or env.empty:
                continue
            ax.fill_between(
                env["year1"],
                env["lo"],
                env["hi"],
                color=color,
                alpha=alpha,
                linewidth=0,
                zorder=2,
            )


def _draw_kind(
    ax,
    agg_focal: pd.DataFrame,
    agg_all: pd.DataFrame,
    stratum: str,
    kind: str,
) -> None:
    _draw_schedule_envelopes(ax, agg_all, stratum, kind)
    roles = _role_cols(kind)
    for scn in ["HIST", *SSP]:
        g = _get_series(agg_focal, scn, stratum)
        if g.empty:
            continue
        if scn != "HIST":
            g = g[g["year1"] >= PROJ_START]
        color = HIST_COLOR if scn == "HIST" else SCN_COLORS[scn]
        lw = LW_HIST if scn == "HIST" else (LW_FOCAL if scn == "BAU" else LW_OTHER)
        for key, col in roles:
            ax.plot(
                g["year1"],
                _to_m(g[col]),
                color=color,
                ls=_linestyle(key),
                lw=lw,
                zorder=6 if scn == "BAU" else (5 if scn == "HIST" else 4),
            )
    ax.axvline(PROJ_START, color="0.75", ls=":", lw=0.8, zorder=1)
    ax.set_xlim(2000, 2100)
    # Print floor = Fig.3 (FS_TICK=14).
    ax.tick_params(labelsize=FS_TICK)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def _colour_legend_handles() -> list:
    """Fig.1 bottom-legend grammar (labels, order, weights) + envelope styles."""
    return [
        Line2D([0], [0], color=HIST_COLOR, lw=LW_HIST, label=OBS_LABEL),
        *[
            Line2D(
                [0],
                [0],
                color=SCN_COLORS[s],
                lw=LW_FOCAL if s == "BAU" else LW_OTHER,
                label=SCEN_LABEL[s],
            )
            for s in SCEN_ORDER
        ],
        # Fig.1 envelope patch (filled band for solid-line series; future blue).
        Patch(facecolor=ENV_COLOR_FUT, alpha=0.18, label=ENV_LABEL),
        # Dashed-line series: thin dashed outline instead of a second filled band.
        Line2D(
            [0],
            [0],
            color=ENV_COLOR_FUT,
            ls="--",
            lw=ENV_LW_DASHED,
            label=ENV_LABEL_DASHED,
        ),
    ]


def _line_legend_handles(kind: str) -> list:
    # On-canvas: short paren gloss only; full wording in caption.
    if kind == "turnover_urban":
        specs = [
            ("N", "urban IS-entrants"),
            ("E", "urban IS-exiters"),
        ]
    elif kind == "turnover_rural":
        specs = [
            ("N", "rural IS-entrants"),
            ("E", "rural IS-exiters"),
        ]
    elif kind == "stayers":
        specs = [
            ("urban", "urban IS-stayers"),
            ("rural", "rural IS-stayers"),
        ]
    elif kind == "movers_rural_origin":
        specs = [
            ("N", "CS-entrants"),
            ("E", "CS-exiters"),
            ("M", "CS-stayers"),
        ]
    elif kind == "movers_urban_origin":
        specs = [
            ("N", "CS-entrants"),
            ("E", "CS-exiters"),
            ("M", "CS-stayers"),
        ]
    else:
        raise KeyError(kind)
    return [
        Line2D([0], [0], color="0.35", lw=1.6, ls=_linestyle(key), label=lab)
        for key, lab in specs
    ]


def _add_panel_line_legend(ax, kind: str) -> None:
    # Upper-center on each (a–e); print floor = Fig.3 FS_MIN (13).
    ax.legend(
        handles=_line_legend_handles(kind),
        loc="upper center",
        fontsize=FS_LEGEND,
        frameon=True,
        fancybox=False,
        edgecolor="#CCCCCC",
        framealpha=0.92,
        borderaxespad=0.15,
        handlelength=2.0,
        labelspacing=0.18,
        handletextpad=0.30,
    )


def _interval_mask(df: pd.DataFrame, key: str) -> pd.Series:
    if key == "early":
        return (df["year1"] >= 2000) & (df["year1"] <= 2030)
    if key == "late":
        return (df["year0"] >= 2030) & (df["year1"] <= 2100)
    raise KeyError(key)


def _violin_at(ax, data: np.ndarray, x: float, *, color: str, width: float = 0.12) -> None:
    v = np.asarray(data, dtype=float)
    v = v[np.isfinite(v) & (v > 0)]
    if v.size < 2:
        if v.size == 1:
            ax.scatter([x], [v[0]], color=color, s=14, zorder=4)
        return
    w = width if v.size >= 8 else min(width, 0.09)
    parts = ax.violinplot(
        [v],
        positions=[x],
        widths=w,
        showmeans=False,
        showmedians=True,
        showextrema=True,
    )
    for body in parts["bodies"]:
        body.set_facecolor(color)
        body.set_edgecolor(color)
        body.set_alpha(0.48)
    for key in ("cbars", "cmins", "cmaxes", "cmedians"):
        if key in parts and parts[key] is not None:
            parts[key].set_color(color)
            parts[key].set_linewidth(0.7)



def _scatter_marker(ax, x: float, y: float, *, key: str, marker: str) -> None:
    edge = MARKER_EDGE[key]
    ax.scatter(
        [x],
        [y],
        marker=marker,
        s=36 if key == "focal" else 19,  # halved vs prior 72 / 38
        facecolors="white" if key != "focal" else edge,
        edgecolors=edge,
        linewidths=0.58 if key != "focal" else 0.60,  # halved vs 1.15 / 1.2
        zorder=7,
    )


def _annotate_markers(ax, totals: pd.DataFrame, col: str, x: float) -> None:
    """Focal/LIC/LMI/UMI at BAU × named schedules (same style as 3-method violins)."""
    # Slight x jitter so markers do not stack exactly on the median line.
    offsets = {"focal": 0.0, "lic": -0.028, "lmi": 0.028, "umi": 0.0}
    mark = totals
    if "scenario" in mark.columns:
        mark = mark[mark["scenario"] == FOCAL_SCENARIO]
    for key, sid, _lab, marker in MARKER_SPECS:
        row = mark.loc[mark["spec_id"] == sid]
        if row.empty:
            continue
        y = float(row.iloc[0][col]) / 1e6
        if not np.isfinite(y) or y <= 0:
            continue
        _scatter_marker(ax, x + offsets.get(key, 0.0), y, key=key, marker=marker)



def _draw_violin_panel(ax, values: pd.DataFrame) -> None:
    """Compact 2-window × 3-method layout; 6 series as coloured thin violins."""
    n_series = len(VIOLIN_SERIES)
    n_methods = len(METHOD_META)
    interval_gap = 3.55
    method_gap = 1.12  # slight + so tilted short names do not AABB-collide
    series_half = 0.055
    interval_centers = [i * interval_gap for i in range(len(INTERVALS))]
    method_offsets = (np.arange(n_methods) - (n_methods - 1) / 2.0) * method_gap
    series_offsets = (np.arange(n_series) - (n_series - 1) / 2.0) * (2.0 * series_half)

    vals_all: list[float] = []
    for i_int, (_ilab, ikey) in enumerate(INTERVALS):
        for i_m, (code, _short, _full, _p) in enumerate(METHOD_META):
            pack = values[
                (values["method_code"] == code) & (values["interval_key"] == ikey)
            ]
            if pack.empty:
                continue
            cx = interval_centers[i_int] + method_offsets[i_m]
            for i_s, (col, _lab, color) in enumerate(VIOLIN_SERIES):
                x = cx + series_offsets[i_s]
                arr = pack[col].to_numpy(float) / 1e6
                vals_all.extend(arr.tolist())
                _violin_at(ax, arr, x, color=color, width=0.10)
                _annotate_markers(ax, pack, col, x)

    # Short method names under each cluster (full names in caption only).
    tick_x: list[float] = []
    tick_lab: list[str] = []
    for i_int in range(len(INTERVALS)):
        for i_m, (_c, short, _f, _p) in enumerate(METHOD_META):
            tick_x.append(interval_centers[i_int] + method_offsets[i_m])
            tick_lab.append(short)
    ax.set_xticks(tick_x)

    # Time-interval labels ON TOP of panel (f), just inside the top frame.
    # y raised +0.02 vs prior 0.95.
    for i_int, (ilabel, _ikey) in enumerate(INTERVALS):
        ax.text(
            interval_centers[i_int],
            0.97,
            ilabel,
            transform=ax.get_xaxis_transform(),
            fontsize=FS_TICK,
            ha="center",
            va="top",
            clip_on=False,
            fontweight="medium",
            zorder=8,
        )
    if len(interval_centers) >= 2:
        mid = 0.5 * (interval_centers[0] + interval_centers[1])
        ax.axvline(mid, color="#B0B0B0", linewidth=0.7, linestyle=":", zorder=0)

    ax.set_yscale("log")
    good = [v for v in vals_all if v > 0 and np.isfinite(v)]
    if good:
        ymin = max(min(good) / 2.2, 1e-4)
        ymax = max(good) * 1.45
        ax.set_ylim(ymin, ymax)
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda y, _pos: f"{y:g}" if y < 1000 else f"{y:.0f}")
    )
    # Left pad −2.0 (was −1.45) so leftmost violin clears the y spine.
    ax.set_xlim(interval_centers[0] - 2.0, interval_centers[-1] + 1.45)
    # Y ticks at FS_TICK; x method labels set after so rotation/FS_LEGEND survive.
    ax.tick_params(axis="y", labelsize=FS_TICK, length=2.4, pad=1.0)
    # Large pad so the tilted-label pivot sits fully below the x spine
    # (ha=center + clockwise tilt; pad clears the elevated corner).
    ax.tick_params(axis="x", length=2.4, pad=12.0)
    # Method short names at Fig.3 print floor (FS_LEGEND=13).
    ax.set_xticklabels(
        tick_lab,
        fontsize=FS_LEGEND,
        rotation=-15,
        ha="center",
        va="top",
        rotation_mode="anchor",
    )
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    # labelpad +6 so ylabel clears tick numbers (was default ~4, crowded).
    ax.set_ylabel(
        "Mean annual volume\n(million persons / year, log)",
        fontsize=FS_AXES,
        labelpad=10,
    )


def _violin_series_legend() -> list:
    handles: list = [
        mpatches.Patch(facecolor=c, edgecolor=c, alpha=0.65, label=lab)
        for _col, lab, c in VIOLIN_SERIES
    ]
    for key, _sid, lab, marker in MARKER_SPECS:
        edge = MARKER_EDGE[key]
        handles.append(
            Line2D(
                [0],
                [0],
                marker=marker,
                color="none",
                markerfacecolor=edge if key == "focal" else "white",
                markeredgecolor=edge,
                markeredgewidth=0.55,  # halved vs 1.1
                markersize=3.75 if key == "focal" else 3.0,  # halved vs 7.5 / 6.0
                label=lab,
            )
        )
    return handles


PANEL_SPECS = [
    ("a", "turnover_urban", "Urban intra-sectoral turnover\n(million persons / year)"),
    ("b", "stayers", "intra-sectoral stayers\n(million persons / year)"),
    ("c", "turnover_rural", "Rural intra-sectoral turnover\n(million persons / year)"),
    ("d", "movers_rural_origin", "Movers, rural origin\n(million persons / year)"),
    ("e", "movers_urban_origin", "Movers, urban origin\n(million persons / year)"),
]

CAPTION_RPO = (
    "Fig. 4 | Relatively-poor-only poverty (RPO) status turnover and mover volumes "
    "are dominated by intra-sectoral status entrants and exiters (IS-entrants / IS-exiters) "
    "and status-persistent stayers (IS-stayers); cross-sectoral movers (CS-entrants / CS-exiters / CS-stayers) "
    "are typically several-fold to about an order of magnitude smaller across "
    "stock-weighted, gravity and demographic flow-composition approaches. "
    "Mean annual urban IS-entrants / IS-exiters under pooled schedules×scenarios are on the "
    "order of tens of millions of persons per year in 2000–2030 and rise toward "
    "tens–about one hundred million per year in 2030–2100 (panel f; ranges span "
    "schedules and SSPs). "
    "(a) Urban intra-sectoral turnover (urban IS-entrants, urban IS-exiters); "
    "(b) urban and rural IS-stayers; "
    "(c) rural intra-sectoral turnover (rural IS-entrants, rural IS-exiters); "
    "(d) movers with rural origin (CS-entrants, CS-exiters, CS-stayers); "
    "(e) movers with urban origin (CS-entrants, CS-exiters, CS-stayers); "
    "(f) mean annual volumes (million persons / year, log) for urban IS-entrants, urban IS-exiters, "
    "urban IS-stayers, rural-origin movers and urban-origin movers under "
    "three methods — Stock-weighted transition shares, Gravity-based transition "
    "model, and Demographic composition-based projection (short x-axis labels: "
    "stock-weighted / gravity / demographic) — pooled across 24 absolute×relative "
    "poverty-line schedules × BAU, LSD, HSD and HQD for windows 2000–2030 and "
    "2030–2100 (mean across annual window endpoints, not interval sums). "
    "Markers at BAU: Focal (S23; star), LIC (S05; circle), LMI (S11; square) and "
    "UMI (S17; diamond). "
    "(a–e) use Method 1 (stock-weighted) trajectories for the focal 2010 "
    "Dibao-scaled × 50% median schedule (S23); HIST/HQD/BAU/LSD/HSD(Focal line) "
    "colours match Fig. 1. Abs.×rel. schedule envelopes (2.5–97.5%) for solid-line "
    "series are filled grey historically (excluding LMI/UMI schedules S07–S18) and "
    "filled blue under BAU after 2026; dashed- and dotted-line series show the same "
    "percentile band as thin outlines. Entrants / urban stayers solid; exiters / rural "
    "stayers dashed; status-persistent movers dotted. Directed origin–destination "
    "volumes average exit- and "
    "entry-side predictions for the 12 AP/RPO status-persistent stays and all "
    "AP↔RPO transitions; NP-linked flows remain single-sided. Dotted line: 2026."
)

CAPTION_AP = (
    "Fig. 4 companion | Absolute poverty (AP) status turnover and mover volumes "
    "follow the same six-panel map as Fig. 4, with intra-sectoral IS-entrants / IS-exiters / IS-stayers "
    "again far larger than cross-sectoral CS-entrants / CS-exiters / CS-stayers movers across the three "
    "flow-composition approaches. "
    "(a–e) Method 1 (stock-weighted) trajectories for focal schedule S23 "
    "(2010 Dibao-scaled × 50% median); "
    "(f) mean annual volumes (million persons / year, log) under Stock-weighted "
    "transition shares, Gravity-based transition model, and Demographic "
    "composition-based projection (short labels stock-weighted / gravity / "
    "demographic; 24 schedules × BAU/LSD/HSD/HQD; windows 2000–2030 and "
    "2030–2100; mean across annual endpoints). Markers at BAU: Focal (S23), "
    "LIC (S05), LMI (S11), UMI (S17). Grey HIST / blue future Abs.×rel. schedule "
    "envelopes (2.5–97.5%), Fig. 1 scenario colours, dual-endpoint averaging and "
    "2026 mark as in Fig. 4."
)


def plot_fig4(
    m1_focal: pd.DataFrame,
    m1_all: pd.DataFrame,
    violin_vals: pd.DataFrame,
    stratum: str,
    out_jpg: str,
    out_tif: str,
    out_svg: str | None = None,
) -> tuple[Path, Path]:
    apply_matplotlib_style(svg_editable_text=False)
    # Right margin restored (no side legend); extra bottom so aligned legends clear.
    # Scenario legend top at y=0.128 (+0.02 vs prior 0.108); (f) bottoms-aligned.
    fig = plt.figure(figsize=FIGSIZE, dpi=160)
    print(
        f"  Fonts [Fig.3 print floor]: min={FS_MIN} tick={FS_TICK} "
        f"axes={FS_AXES} panel={FS_PANEL} legend={FS_LEGEND} "
        f"(base floor {_FS_LEGEND_BASE} @ {_REF_WIDTH}\"; canvas {FIGSIZE[0]}\")"
    )
    # Tighter L/R margins so panels fill the canvas; wspace kept for gaps.
    gs = GridSpec(
        2,
        3,
        figure=fig,
        left=0.048,
        right=0.995,
        top=0.98,
        bottom=0.200,
        hspace=0.22,
        wspace=0.14,
    )
    axes = [fig.add_subplot(gs[i, j]) for i in range(2) for j in range(3)]

    # Keep prior inter-column gaps (col2 +0.02; col3 +0.04), then equal-widen
    # panels so each row spans left_m→right_m without changing those gaps.
    for idx, dx in ((1, 0.02), (4, 0.02), (2, 0.04), (5, 0.04)):
        pos = axes[idx].get_position()
        axes[idx].set_position([pos.x0 + dx, pos.y0, pos.width, pos.height])

    # Raise bottom row (d,e,f) by +0.03 figure fraction after column shifts.
    for idx in (3, 4, 5):
        pos = axes[idx].get_position()
        axes[idx].set_position([pos.x0, pos.y0 + 0.03, pos.width, pos.height])

    left_m, right_m = 0.048, 0.995
    for row in (0, 1):
        idxs = [row * 3, row * 3 + 1, row * 3 + 2]
        pos = [axes[i].get_position() for i in idxs]
        gap01 = pos[1].x0 - (pos[0].x0 + pos[0].width)
        gap12 = pos[2].x0 - (pos[1].x0 + pos[1].width)
        avail = right_m - left_m - gap01 - gap12
        w_new = avail / 3.0
        x = left_m
        for k, i in enumerate(idxs):
            p = axes[i].get_position()
            axes[i].set_position([x, p.y0, w_new, p.height])
            x += w_new + (gap01 if k == 0 else gap12 if k == 1 else 0)

    for ax, (letter, kind, ylab) in zip(axes[:5], PANEL_SPECS):
        _draw_kind(ax, m1_focal, m1_all, stratum, kind)
        _panel_letter(ax, letter)
        _add_panel_line_legend(ax, kind)
        ax.set_ylabel(ylab, fontsize=FS_AXES)
        # X-label only on bottom row — avoids "Window end year" floating above (f).
        if letter in ("d", "e"):
            ax.set_xlabel("Window end year", fontsize=FS_AXES)
        else:
            ax.set_xlabel("")

    ax_f = axes[5]
    _draw_violin_panel(ax_f, violin_vals)
    _panel_letter(ax_f, "f")
    ax_f.set_xlabel("")

    # 1) Bottom scenario legend: y raised +0.02 (0.108 → 0.128); under a/b/d/e.
    leg_scen = fig.legend(
        handles=_colour_legend_handles(),
        loc="upper center",
        bbox_to_anchor=(0.3, 0.128),
        ncol=4,
        frameon=False,
        fontsize=FS_LEGEND,
        handlelength=1.4,
        labelspacing=0.35,
        borderpad=0.40,
        columnspacing=1.0,
    )

    # 2) Series legend under (f); start lower so tilted method ticks have a
    # gap; bottoms later flush-aligned with the scenario legend.
    leg_f = ax_f.legend(
        handles=_violin_series_legend(),
        loc="upper center",
        bbox_to_anchor=(0.5, -0.16),
        fontsize=FS_LEGEND,
        frameon=True,
        fancybox=False,
        edgecolor="#CCCCCC",
        framealpha=0.92,
        borderaxespad=0.0,
        labelspacing=0.18,
        handlelength=1.05,
        handletextpad=0.35,
        columnspacing=0.8,
        ncol=2,
    )

    # 3) Align (f) legend bottom edge with scenario legend bottom (figure coords).
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bb_scen = leg_scen.get_window_extent(renderer).transformed(fig.transFigure.inverted())
    bb_f = leg_f.get_window_extent(renderer).transformed(fig.transFigure.inverted())
    x_f = 0.5 * (bb_f.x0 + bb_f.x1)
    y0_f_before = bb_f.y0
    # lower center at (x_f, scenario y0) → bottoms flush.
    leg_f.set_bbox_to_anchor((x_f, bb_scen.y0), transform=fig.transFigure)
    leg_f._loc = 8  # lower center
    fig.canvas.draw()
    bb_f2 = leg_f.get_window_extent(renderer).transformed(fig.transFigure.inverted())
    print(
        f"  Legend align [{stratum}]: scen y0={bb_scen.y0:.4f}; "
        f"(f) y0 {y0_f_before:.4f} → {bb_f2.y0:.4f} (target={bb_scen.y0:.4f})"
    )

    jpg = OUT / out_jpg
    tif = OUT / out_tif
    fig.savefig(
        jpg,
        dpi=220,
        bbox_inches="tight",
        facecolor="white",
        format="jpg",
        pil_kwargs={"quality": 95},
    )
    fig.savefig(
        tif,
        dpi=600,
        bbox_inches="tight",
        facecolor="white",
        format="tiff",
        pil_kwargs={"compression": "tiff_lzw"},
    )
    if out_svg is not None:
        with plt.rc_context({"svg.fonttype": "none"}):
            fig.savefig(OUT / out_svg, format="svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return jpg, tif


def update_figure_docx(
    doc_path: Path,
    tiff_path: Path,
    caption: str,
    bak_path: Path,
    *,
    width_in: float = 6.5,
) -> None:
    """Replace the embedded figure TIFF and refresh the caption paragraph."""
    import shutil

    from omml_helpers import (  # noqa: E402
        assert_word_not_locking,
        finalize_docx_for_word,
        safe_save_docx,
    )
    from docx import Document  # noqa: E402
    from docx.oxml.ns import qn  # noqa: E402
    from docx.shared import Inches  # noqa: E402

    assert_word_not_locking(doc_path)
    if not tiff_path.exists():
        raise FileNotFoundError(tiff_path)
    bak_path.parent.mkdir(parents=True, exist_ok=True)
    if not bak_path.exists():
        shutil.copy2(doc_path, bak_path)

    doc = Document(str(doc_path))
    blip_tag = qn("a:blip")
    img_para = None
    cap_para = None
    for p in doc.paragraphs:
        if img_para is None and p._element.findall(".//" + blip_tag):
            img_para = p
        t = p.text.strip()
        if cap_para is None and t.startswith("Fig. 4"):
            cap_para = p

    if img_para is None:
        # No prior image — insert a new paragraph before the caption (or at end).
        if cap_para is not None:
            img_para = cap_para.insert_paragraph_before("")
        else:
            img_para = doc.add_paragraph("")
    else:
        # Delete old drawing(s) from the image paragraph.
        for child in list(img_para._element):
            img_para._element.remove(child)

    run = img_para.add_run()
    run.add_picture(str(tiff_path), width=Inches(width_in))
    print(f"  Inserted {tiff_path.name} @ {width_in}\" into {doc_path.name}")

    if cap_para is None:
        cap_para = doc.add_paragraph("")
    for r in cap_para.runs:
        r.text = ""
    if cap_para.runs:
        cap_para.runs[0].text = caption
    else:
        cap_para.add_run(caption)

    safe_save_docx(doc, doc_path)
    finalize_docx_for_word(doc_path)
    print(f"Updated {doc_path.name} caption + image from {tiff_path.name}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    aggregate_path = DATA / "fig4_method1_rpo_aggregates.csv"
    if not aggregate_path.exists() or not VALUES_CSV.exists():
        raise FileNotFoundError(
            "Required grouped RPO data are missing. Keep both CSV files in ../data/."
        )
    m1_all = pd.read_csv(aggregate_path)
    m1_focal = m1_all[m1_all["spec_id"] == FOCAL_SPEC].copy()
    violin_rpo = pd.read_csv(VALUES_CSV)
    plot_fig4(
        m1_focal, m1_all, violin_rpo, "RPO",
        "Figure4_preview.jpg", "Figure4_preview.tiff",
        out_svg="Figure4.svg",
    )
    (OUT / "Figure4_caption.txt").write_text(CAPTION_RPO + "\n", encoding="utf-8")
    print("Wrote Figure 4 RPO SVG, preview, TIFF, and caption to", OUT)


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
