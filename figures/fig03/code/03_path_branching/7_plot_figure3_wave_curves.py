# -*- coding: utf-8 -*-
"""7. Plot Fig.3 4×2 wave-annualised curves with poverty-line envelope.

Layout (screenshot blue boxes; Row 4 = Movers CS-entrants / CS-exiters):
  Row 1 (a)(b) Total — Intra-sectoral turnover, Intra-sectoral stayers,
                       Cross-sectoral movers (CS-stayers + CS-exiters + CS-entrants)
  Row 2 (c)(d) Urban — IS-entrants, IS-exiters, urban intra-sectoral Stayers
  Row 3 (e)(f) Rural — IS-entrants, IS-exiters, rural intra-sectoral Stayers
  Row 4 (g)(h) Movers — CS-entrants, CS-exiters (national totals)

Data: stock-weighted Method 1 32-flow detail (CFPS dual exit/entry rates ×
Lei schedule-specific six-state stocks), HIST biennial windows 2010–2022.
Schedules: S01–S06, S19–S24 (exclude LMI/UMI S07–S18). Focal: S23.
Volumes already annualised in source (`out_annual` / `in_annual` = 2-yr mass ÷ 2);
plot year = year1 (window end), matching S12 / Fig.4 HIST convention.

Visual: thick coloured focal curves; thin same-colour other schedules;
2.5–97.5% envelope fill (Fig.1 / S11 grammar). No on-canvas long title.
JPG preview + TIFF @ 600 dpi LZW. No SVG.

Keeps trails script ``6_plot_figure3.py`` untouched (archived separately).
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
PACKAGE_ROOT = HERE.parents[1]  # 20260723_submission_files/
PROJECT_ROOT = HERE.parents[1]  # nature/
STYLE_DIR = PROJECT_ROOT / "7_output" / "code" / "style"
sys.path.insert(0, str(STYLE_DIR))
from okabe_ito_style import (  # noqa: E402
    FS_AXES,
    FS_LEGEND,
    FS_PANEL,
    FS_TICK,
    OKABE_ITO,
    apply_matplotlib_style,
)

OUT = HERE / "fig3_plot_outputs"
OUT.mkdir(parents=True, exist_ok=True)

M1_PATH = (
    PACKAGE_ROOT
    / "_scratch_exports"
    / "exit_entry_scaling"
    / "all_specs"
    / "method1_32flow_detail_annual_main_ols_clip01.csv"
)

FOCAL = "S23"
LMI_UMI = {f"S{i:02d}" for i in range(7, 19)}
KEEP_SPECS = {f"S{i:02d}" for i in list(range(1, 7)) + list(range(19, 25))}

FIGSIZE = (10.5, 11.0)
LW_FOCAL = 2.4
LW_OTHER = 0.55
ALPHA_OTHER = 0.28
ALPHA_ENV = 0.14

# Series colours (Okabe–Ito); N before E in legend order
C_N = OKABE_ITO["bluish_green"]
C_E = OKABE_ITO["vermillion"]
C_STAY = OKABE_ITO["orange"]
C_MOVE = OKABE_ITO["blue"]
C_TURN = OKABE_ITO["bluish_green"]

ROW_TITLES = {
    0: "Total",
    1: "Urban",
    2: "Rural",
    3: "Movers",
}
COL_TITLES = {"AP": "Absolute poverty (AP)", "RPO": "Relatively-poor-only (RPO)"}
LETTERS = [
    ["a", "b"],
    ["c", "d"],
    ["e", "f"],
    ["g", "h"],
]


def _usecols() -> list[str]:
    return [
        "spec_id",
        "scenario",
        "year0",
        "year1",
        "origin",
        "dest",
        "flow",
        "is_stay",
        "out_annual",
        "in_annual",
        "AP_PE",
        "AP_RISE_out",
        "AP_RISE_in",
        "AP_UISE_out",
        "AP_UISE_in",
        "RPO_PE",
        "RPO_RISE_out",
        "RPO_RISE_in",
        "RPO_UISE_out",
        "RPO_UISE_in",
    ]


def _agg_components(df: pd.DataFrame) -> pd.DataFrame:
    """IS-exiters/N (urban/rural), CS-exiters/N (urban/rural), stayers — same as Fig.4."""
    d = df[~df["is_stay"]].copy()
    d["o_sec"] = d["origin"].str.split("_").str[-1]
    d["d_sec"] = d["dest"].str.split("_").str[-1]
    gkeys = ["spec_id", "year0", "year1"]
    rows = []
    for stratum in ("AP", "RPO"):
        tmp = d.copy()
        tmp["IS_E_urban"] = tmp[f"{stratum}_UISE_out"].astype(float) * tmp["out_annual"]
        tmp["IS_N_urban"] = tmp[f"{stratum}_UISE_in"].astype(float) * tmp["in_annual"]
        tmp["IS_E_rural"] = tmp[f"{stratum}_RISE_out"].astype(float) * tmp["out_annual"]
        tmp["IS_N_rural"] = tmp[f"{stratum}_RISE_in"].astype(float) * tmp["in_annual"]
        pe = tmp[f"{stratum}_PE"].astype(float)
        tmp["CS_E_urban"] = pe * (tmp["o_sec"] == "urban").astype(float) * tmp["out_annual"]
        tmp["CS_E_rural"] = pe * (tmp["o_sec"] == "rural").astype(float) * tmp["out_annual"]
        tmp["CS_N_urban"] = pe * (tmp["d_sec"] == "urban").astype(float) * tmp["in_annual"]
        tmp["CS_N_rural"] = pe * (tmp["d_sec"] == "rural").astype(float) * tmp["in_annual"]
        # Mutually exclusive SST mover classes, restricted to cross-sector flows.
        o_status = tmp["origin"].str.split("_").str[0]
        d_status = tmp["dest"].str.split("_").str[0]
        cross = tmp["o_sec"] != tmp["d_sec"]
        tmp["CS_E_transition"] = (cross & (o_status == stratum) & (d_status != stratum)).astype(float) * tmp["out_annual"]
        tmp["CS_N_transition"] = (cross & (o_status != stratum) & (d_status == stratum)).astype(float) * tmp["in_annual"]
        tmp["CS_M_transition"] = (cross & (o_status == stratum) & (d_status == stratum)).astype(float) * 0.5 * (tmp["out_annual"] + tmp["in_annual"])
        cols = [
            "IS_E_urban",
            "IS_N_urban",
            "IS_E_rural",
            "IS_N_rural",
            "CS_E_urban",
            "CS_N_urban",
            "CS_E_rural",
            "CS_N_rural",
            "CS_E_transition",
            "CS_N_transition",
            "CS_M_transition",
        ]
        s = tmp.groupby(gkeys, as_index=False)[cols].sum()
        s["stratum"] = stratum
        rows.append(s)
    comp = pd.concat(rows, ignore_index=True)

    stay = df[df["is_stay"]].copy()
    stay["stratum"] = np.where(
        stay["flow"].str.startswith("AP_"),
        "AP",
        np.where(stay["flow"].str.startswith("RPO_"), "RPO", "other"),
    )
    stay = stay[stay["stratum"].isin(["AP", "RPO"])].copy()
    stay["sector"] = np.where(stay["flow"].str.contains("urban"), "urban", "rural")
    stay["stay"] = 0.5 * (
        stay["out_annual"].astype(float) + stay["in_annual"].astype(float)
    )
    st = (
        stay.groupby(gkeys + ["stratum", "sector"], as_index=False)["stay"]
        .sum()
    )
    st_w = (
        st.pivot_table(
            index=gkeys + ["stratum"], columns="sector", values="stay", fill_value=0.0
        )
        .reset_index()
        .rename(columns={"rural": "stay_rural", "urban": "stay_urban"})
    )
    for c in ("stay_rural", "stay_urban"):
        if c not in st_w.columns:
            st_w[c] = 0.0
    out = comp.merge(st_w, on=gkeys + ["stratum"], how="left")
    for c in ("stay_rural", "stay_urban"):
        out[c] = out[c].fillna(0.0)

    # Panel aggregates (persons/year)
    out["turnover_total"] = (
        out["IS_N_urban"]
        + out["IS_E_urban"]
        + out["IS_N_rural"]
        + out["IS_E_rural"]
    )
    out["stayer_total"] = out["stay_urban"] + out["stay_rural"]
    # Total movers use the mutually exclusive SST flow classes. The earlier
    # PE-weighted aggregate captured only the persistent-mover component.
    out["mover_total"] = (
        out["CS_N_transition"]
        + out["CS_E_transition"]
        + out["CS_M_transition"]
    )
    out["IS_N_total"] = out["IS_N_urban"] + out["IS_N_rural"]
    out["IS_E_total"] = out["IS_E_urban"] + out["IS_E_rural"]
    out["CS_N_total"] = out["CS_N_urban"] + out["CS_N_rural"]
    out["CS_E_total"] = out["CS_E_urban"] + out["CS_E_rural"]
    out["CS_E_transition_total"] = out["CS_E_transition"]
    out["CS_N_transition_total"] = out["CS_N_transition"]
    out["CS_M_transition_total"] = out["CS_M_transition"]
    out["is_focus"] = out["spec_id"].eq(FOCAL)
    out["year_plot"] = out["year1"].astype(int)
    return out


def _load_agg() -> pd.DataFrame:
    if not M1_PATH.is_file():
        raise FileNotFoundError(f"Missing Method-1 detail: {M1_PATH}")
    raw = pd.read_csv(M1_PATH, usecols=_usecols())
    for c in _usecols():
        if c.startswith(("AP_", "RPO_")) or c == "is_stay":
            raw[c] = raw[c].astype(bool)
    hist = raw[
        (raw["scenario"] == "HIST")
        & (raw["year0"] >= 2010)
        & (raw["year1"] <= 2022)
        & (raw["spec_id"].isin(KEEP_SPECS))
        & (~raw["spec_id"].isin(LMI_UMI))
    ].copy()
    return _agg_components(hist)


def _to_m(s: pd.Series) -> pd.Series:
    return s.astype(float) / 1.0e6


def _envelope(sub: pd.DataFrame, col: str) -> pd.DataFrame:
    rows = []
    for y, g in sub.groupby("year_plot"):
        vals = _to_m(g[col]).to_numpy(dtype=float)
        vals = vals[np.isfinite(vals)]
        if vals.size == 0:
            continue
        rows.append(
            {
                "year_plot": int(y),
                "lo": float(np.percentile(vals, 2.5)),
                "hi": float(np.percentile(vals, 97.5)),
                "n_specs": int(vals.size),
            }
        )
    return pd.DataFrame(rows)


def _draw_series(
    ax,
    sub: pd.DataFrame,
    col: str,
    color: str,
    *,
    label: str | None = None,
    z_base: int = 3,
) -> None:
    """Thin other-spec lines + envelope + thick focal."""
    others = sub[~sub["is_focus"]]
    for _, g in others.groupby("spec_id"):
        g = g.sort_values("year_plot")
        ax.plot(
            g["year_plot"],
            _to_m(g[col]),
            color=color,
            lw=LW_OTHER,
            alpha=ALPHA_OTHER,
            zorder=z_base,
        )
    env = _envelope(sub, col)
    if not env.empty:
        ax.fill_between(
            env["year_plot"],
            env["lo"],
            env["hi"],
            color=color,
            alpha=ALPHA_ENV,
            linewidth=0,
            zorder=z_base + 1,
        )
    focal = sub[sub["is_focus"]].sort_values("year_plot")
    ax.plot(
        focal["year_plot"],
        _to_m(focal[col]),
        color=color,
        lw=LW_FOCAL,
        zorder=z_base + 3,
        marker="o",
        markersize=3.5,
        label=label,
    )


def _panel_map(row: int) -> list[tuple[str, str, str]]:
    """Return list of (column, color, legend label) for a row. N left of E."""
    if row == 0:
        return [
            ("turnover_total", C_TURN, "Intra-sectoral turnover"),
            ("stayer_total", C_STAY, "Intra-sectoral stayers"),
            ("mover_total", C_MOVE, "Cross-sectoral movers"),
        ]
    if row == 1:
        return [
            ("IS_N_urban", C_N, "IS-entrants"),
            ("IS_E_urban", C_E, "IS-exiters"),
            ("stay_urban", C_STAY, "IS-stayers"),
        ]
    if row == 2:
        return [
            ("IS_N_rural", C_N, "IS-entrants"),
            ("IS_E_rural", C_E, "IS-exiters"),
            ("stay_rural", C_STAY, "IS-stayers"),
        ]
    if row == 3:
        return [
            ("CS_N_transition_total", C_N, "CS-entrants"),
            ("CS_E_transition_total", C_E, "CS-exiters"),
            ("CS_M_transition_total", C_MOVE, "CS-stayers"),
        ]
    raise KeyError(row)


def _style_ax(ax, letter: str, *, ylabel: bool, col_title: str | None, row_title: str | None):
    ax.set_xlim(2010.5, 2022.5)
    ax.set_xticks([2012, 2014, 2016, 2018, 2020, 2022])
    ax.tick_params(axis="both", labelsize=FS_TICK)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
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
    if ylabel:
        ax.set_ylabel(
            "Annual volume\n(million persons/year)",
            fontsize=FS_AXES,
        )
    if col_title is not None:
        ax.set_title(col_title, fontsize=FS_AXES, pad=4)
    if row_title is not None:
        ax.text(
            -0.28,
            0.5,
            row_title,
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=FS_AXES,
            fontweight="bold",
            rotation=90,
            clip_on=False,
        )


def _legend_panel(ax, row: int) -> None:
    series = _panel_map(row)
    handles = [
        Line2D([0], [0], color=c, lw=LW_FOCAL, marker="o", markersize=3.5, label=lab)
        for _, c, lab in series
    ]
    handles.append(
        Patch(
            facecolor="0.55",
            edgecolor="none",
            alpha=0.35,
            label="Schedule envelope (2.5–97.5%)",
        )
    )
    ax.legend(
        handles=handles,
        loc="upper right",
        fontsize=FS_LEGEND,
        frameon=False,
        borderaxespad=0.2,
    )


def main() -> None:
    apply_matplotlib_style(svg_editable_text=False)
    agg = _load_agg()
    print(
        f"Loaded {len(agg):,} rows; specs={sorted(agg['spec_id'].unique())}; "
        f"years={sorted(agg['year_plot'].unique())}"
    )

    fig, axes = plt.subplots(
        4, 2, figsize=FIGSIZE, sharex=True, gridspec_kw=dict(hspace=0.28, wspace=0.22)
    )
    strata = ["AP", "RPO"]

    for r in range(4):
        for c, stratum in enumerate(strata):
            ax = axes[r, c]
            sub = agg[agg["stratum"] == stratum].copy()
            for col, color, lab in _panel_map(r):
                _draw_series(ax, sub, col, color, label=lab if c == 0 else None)
            _style_ax(
                ax,
                LETTERS[r][c],
                ylabel=(c == 0),
                col_title=COL_TITLES[stratum] if r == 0 else None,
                row_title=ROW_TITLES[r] if c == 0 else None,
            )
            if c == 1:
                _legend_panel(ax, r)
            # Independent y-scale per panel (AP vs RPO magnitudes differ sharply).
            y0, y1 = ax.get_ylim()
            ax.set_ylim(max(0.0, y0), y1 * 1.05 if y1 > 0 else 1.0)

    axes[-1, 0].set_xlabel("Year", fontsize=FS_AXES)
    axes[-1, 1].set_xlabel("Year", fontsize=FS_AXES)

    fig.subplots_adjust(left=0.14, right=0.98, top=0.96, bottom=0.05)

    jpg = OUT / "Fig3_wave_curves_4x2.jpg"
    tif = OUT / "Fig3_wave_curves_4x2.tiff"
    fig.savefig(jpg, dpi=300, format="jpg", pil_kwargs={"quality": 95})
    fig.savefig(tif, dpi=600, format="tiff", pil_kwargs={"compression": "tiff_lzw"})
    plt.close(fig)
    print(f"Wrote {jpg.name} and {tif.name}")

    # Long panel data for caption / audit
    long_rows = []
    for r in range(4):
        for stratum in strata:
            sub = agg[agg["stratum"] == stratum]
            for col, _color, lab in _panel_map(r):
                for _, row in sub.iterrows():
                    long_rows.append(
                        {
                            "row": r + 1,
                            "row_label": ROW_TITLES[r],
                            "stratum": stratum,
                            "series": lab,
                            "metric": col,
                            "spec_id": row["spec_id"],
                            "is_focus": bool(row["is_focus"]),
                            "year0": int(row["year0"]),
                            "year1": int(row["year1"]),
                            "year_plot": int(row["year_plot"]),
                            "vol_annual": float(row[col]),
                            "vol_annual_M": float(row[col]) / 1.0e6,
                        }
                    )
    long = pd.DataFrame(long_rows)
    csv_path = OUT / "Fig3_wave_curves_panel_data.csv"
    long.to_csv(csv_path, index=False)
    print(f"Wrote {csv_path.name} ({len(long):,} rows)")

    cap = OUT / "Fig3_wave_curves_caption.txt"
    caption = (
        "Fig. 3 | Wave-annualised volumes of intra-sectoral turnover, stayers and "
        "movers for absolute poverty (AP) and relatively-poor-only poverty (RPO), "
        "2010–2022. Columns: AP (left) and RPO (right). Rows: (a,b) national totals — "
        "Intra-sectoral turnover (IS-entrants + IS-exiters), intra-sectoral stayers, and "
        "cross-sectoral movers (CS-stayers + CS-exiters + CS-entrants); (c,d) urban — IS-entrants, IS-exiters and IS-stayers; "
        "(e,f) rural — IS-entrants, IS-exiters and IS-stayers; (g,h) cross-sectional — CS-stayers, CS-exiters "
        "and CS-entrants (national totals). Thick coloured curves: focal schedule S23 "
        "(2010 Dibao-scaled × 50% median). Thin same-colour curves and shaded "
        "bands: other absolute×relative schedules (S01–S06, S19–S24; LMI/UMI "
        "S07–S18 excluded), with the band marking the 2.5–97.5% envelope across "
        "schedules. Values are stock-weighted Method 1 annual volumes (million "
        "persons/year): CFPS dual exit/entry rates applied to Lei schedule-specific "
        "six-state stocks over consecutive CFPS biennial windows; 2-year window "
        "masses are annualised by ÷2 (same convention as Supplementary Fig. S12 / "
        "Fig. 4 historical windows). Points are plotted at the window end year. "
        "The six transition labels are IS-stayers, IS-exiters, IS-entrants, CS-stayers, CS-exiters and CS-entrants."
    )
    cap.write_text(caption + "\n", encoding="utf-8")
    print(f"Wrote {cap.name}")
    print(caption)


if __name__ == "__main__":
    main()
