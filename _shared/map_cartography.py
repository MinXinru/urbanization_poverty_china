# -*- coding: utf-8 -*-
"""Shared province choropleth helpers for SI map figures."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import matplotlib.patches as mpatches
import numpy as np
import shapefile
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.path import Path as MplPath

from okabe_ito_style import OKABE_ITO
from province_names import PROV_CN_TO_EN

HERE = Path(__file__).resolve().parent
GEO_DIR = HERE / "province_boundaries"
SHP = GEO_DIR / "china_provinces.shp"
SCS_DIR = HERE / "scs_overlay"
SCS_SHP = SCS_DIR / "china_national_boundary.shp"

# Hainan southern tip in the Lambert China frame (province layer).
_HAINAN_YMIN = 2_361_294.8651292175
# Open polylines shorter than this (projected metres) are skipped as noise.
_SCS_DASH_MIN_LENGTH = 25_000.0
_SCS_PAD_FRAC = 0.02

CMAP_H = LinearSegmentedColormap.from_list(
    "okabe_h",
    ["#FFFFFF", OKABE_ITO["sky_blue"], OKABE_ITO["blue"], OKABE_ITO["vermillion"]],
)
CMAP_DIV = LinearSegmentedColormap.from_list(
    "okabe_div",
    [OKABE_ITO["blue"], "#FFFFFF", OKABE_ITO["vermillion"]],
)


def shape_to_paths(shape) -> list[MplPath]:
    pts = np.asarray(shape.points, dtype=float)
    parts = list(shape.parts) + [len(pts)]
    paths = []
    for i in range(len(parts) - 1):
        ring = pts[parts[i] : parts[i + 1]]
        if len(ring) < 3:
            continue
        codes = np.full(len(ring), MplPath.LINETO, dtype=np.uint8)
        codes[0] = MplPath.MOVETO
        if not np.allclose(ring[0], ring[-1]):
            ring = np.vstack([ring, ring[0]])
            codes = np.append(codes, MplPath.CLOSEPOLY)
        else:
            codes[-1] = MplPath.CLOSEPOLY
        paths.append(MplPath(ring, codes))
    return paths


def load_geoms(shp: Path | None = None):
    """Load province polygons from ``china_provinces.shp`` (user-supplied)."""
    shp = Path(shp) if shp else SHP
    if not shp.exists():
        raise FileNotFoundError(
            f"Shapefile not found: {shp}. Place china_provinces.* under "
            f"{GEO_DIR} (see _shared/province_boundaries/README.md)."
        )
    r = shapefile.Reader(str(shp), encoding="utf-8", encodingErrors="replace")
    geoms = []
    xmin = ymin = np.inf
    xmax = ymax = -np.inf
    for shape, rec in zip(r.shapes(), r.records()):
        cn = str(rec[0]).strip()
        en = PROV_CN_TO_EN.get(cn)
        paths = shape_to_paths(shape)
        if not paths:
            continue
        for p in paths:
            xs, ys = p.vertices[:, 0], p.vertices[:, 1]
            xmin = min(xmin, float(xs.min()))
            xmax = max(xmax, float(xs.max()))
            ymin = min(ymin, float(ys.min()))
            ymax = max(ymax, float(ys.max()))
        geoms.append({"cn": cn, "province": en, "paths": paths})
    return geoms, (xmin, xmax, ymin, ymax)


@lru_cache(maxsize=2)
def load_scs_overlay(shp: str | None = None) -> dict:
    """Load South China Sea islands (closed) and nine-dash-style dashes (open).

    Features are taken from the national-boundary line layer, retaining only
    geometries whose entire extent lies south of Hainan.
    """
    path = Path(shp) if shp else SCS_SHP
    if not path.exists():
        raise FileNotFoundError(
            f"SCS boundary shapefile not found: {path}. "
            f"Place china_national_boundary.* under {SCS_DIR}."
        )
    r = shapefile.Reader(str(path))
    islands: list[np.ndarray] = []
    dashes: list[np.ndarray] = []
    scs_ymin = np.inf
    scs_ymax = -np.inf
    scs_xmin = np.inf
    scs_xmax = -np.inf
    for shape in r.shapes():
        pts = np.asarray(shape.points, dtype=float)
        if len(pts) < 2:
            continue
        ymin = float(pts[:, 1].min())
        ymax = float(pts[:, 1].max())
        if ymax >= _HAINAN_YMIN:
            continue
        xmin = float(pts[:, 0].min())
        xmax = float(pts[:, 0].max())
        scs_ymin = min(scs_ymin, ymin)
        scs_ymax = max(scs_ymax, ymax)
        scs_xmin = min(scs_xmin, xmin)
        scs_xmax = max(scs_xmax, xmax)
        closed = bool(np.allclose(pts[0], pts[-1]))
        if closed:
            islands.append(pts)
            continue
        seg = np.diff(pts, axis=0)
        length = float(np.sqrt((seg * seg).sum(axis=1)).sum())
        if length >= _SCS_DASH_MIN_LENGTH:
            dashes.append(pts)
    return {
        "islands": tuple(islands),
        "dashes": tuple(dashes),
        "bounds": (scs_xmin, scs_xmax, scs_ymin, scs_ymax),
    }


def expand_bounds_for_scs(
    bounds: tuple[float, float, float, float],
    scs: dict | None = None,
) -> tuple[float, float, float, float]:
    """Full-frame south expansion. Prefer ``add_scs_inset`` to keep mainland aspect."""
    xmin, xmax, ymin, ymax = bounds
    scs = scs if scs is not None else load_scs_overlay()
    sxmin, sxmax, symin, symax = scs["bounds"]
    pad_y = _SCS_PAD_FRAC * (ymax - symin)
    pad_x = _SCS_PAD_FRAC * (xmax - xmin)
    return (
        min(xmin, sxmin) - pad_x,
        max(xmax, sxmax) + pad_x,
        symin - pad_y,
        ymax + pad_y * 0.25,
    )


def figsize_for_map_grid(
    bounds: tuple[float, float, float, float],
    nrows: int,
    ncols: int,
    *,
    panel_width: float = 4.2,
    cbar_width: float = 0.85,
    row_gap: float = 0.35,
    col_gap: float = 0.15,
) -> tuple[float, float]:
    """Figure size so each panel axes matches data aspect (no geographic stretch)."""
    xmin, xmax, ymin, ymax = bounds
    dx = max(float(xmax - xmin), 1.0)
    dy = max(float(ymax - ymin), 1.0)
    panel_height = panel_width * (dy / dx)
    fig_w = ncols * panel_width + (ncols - 1) * col_gap + cbar_width
    fig_h = nrows * panel_height + (nrows - 1) * row_gap
    return (fig_w, fig_h)


def draw_scs_overlay(ax, scs: dict | None = None) -> None:
    """Dashed SCS boundary + filled island markers (no choropleth fill)."""
    scs = scs if scs is not None else load_scs_overlay()
    color = OKABE_ITO["black"]
    if scs["dashes"]:
        lc = LineCollection(
            list(scs["dashes"]),
            colors=color,
            linewidths=0.7,
            linestyles=(0, (3.5, 2.5)),
            zorder=3,
        )
        ax.add_collection(lc)
    island_patches = []
    for pts in scs["islands"]:
        island_patches.append(mpatches.Polygon(pts, closed=True))
    if island_patches:
        pc = PatchCollection(
            island_patches,
            facecolors=color,
            edgecolors=color,
            linewidths=0.2,
            zorder=3,
        )
        ax.add_collection(pc)


def add_scs_inset(
    ax,
    scs: dict | None = None,
    *,
    bounds_axes: tuple[float, float, float, float] = (0.70, 0.02, 0.28, 0.30),
) -> object:
    """Bottom-right SCS inset; main axes keep original mainland crop/aspect.

    ``bounds_axes`` is ``(x0, y0, width, height)`` in parent-axes fraction.
    """
    scs = scs if scs is not None else load_scs_overlay()
    sxmin, sxmax, symin, symax = scs["bounds"]
    pad_x = _SCS_PAD_FRAC * (sxmax - sxmin)
    pad_y = _SCS_PAD_FRAC * (symax - symin)
    inset = ax.inset_axes(bounds_axes)
    draw_scs_overlay(inset, scs)
    inset.set_xlim(sxmin - pad_x, sxmax + pad_x)
    inset.set_ylim(symin - pad_y, symax + pad_y)
    inset.set_aspect("equal", adjustable="box")
    inset.set_xticks([])
    inset.set_yticks([])
    for spine in inset.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.6)
        spine.set_edgecolor(OKABE_ITO["black"])
    inset.set_facecolor("white")
    inset.set_zorder(5)
    return inset


def finish_map_axes(ax, bounds: tuple[float, float, float, float]) -> None:
    xmin, xmax, ymin, ymax = bounds
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    # adjustable='box': reshape axes to data aspect — no stretch of China.
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def draw_choropleth(
    ax,
    geoms,
    bounds,
    value_by_province,
    cmap,
    norm,
    *,
    with_scs: bool = True,
    scs_mode: str = "expand",
):
    """Province choropleth.

    ``scs_mode``:
      - ``expand`` (default): one frame including SCS; caller must size figure via
        ``figsize_for_map_grid(expand_bounds_for_scs(...), ...)`` so mainland is not stretched.
      - ``inset``: original mainland crop + bottom-right SCS inset.
      - ``off``: no SCS.
    """
    patches, colors = [], []
    for g in geoms:
        for path in g["paths"]:
            patches.append(mpatches.PathPatch(path, linewidth=0.35))
            key = g["province"]
            if key is None or key not in value_by_province.index:
                colors.append((0.85, 0.85, 0.85, 1.0))
            else:
                v = float(value_by_province.loc[key])
                if not np.isfinite(v):
                    colors.append((0.85, 0.85, 0.85, 1.0))
                else:
                    colors.append(cmap(norm(v)))
    pc = PatchCollection(
        patches, match_original=False, edgecolors=OKABE_ITO["black"], linewidths=0.35
    )
    pc.set_facecolor(colors)
    ax.add_collection(pc)
    plot_bounds = bounds
    if with_scs and scs_mode == "expand":
        scs = load_scs_overlay()
        plot_bounds = expand_bounds_for_scs(bounds, scs)
        draw_scs_overlay(ax, scs)
        finish_map_axes(ax, plot_bounds)
    elif with_scs and scs_mode == "inset":
        finish_map_axes(ax, plot_bounds)
        add_scs_inset(ax)
    else:
        finish_map_axes(ax, plot_bounds)
