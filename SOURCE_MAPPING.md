# Source mapping (figures / SI → this pack)

Labels match the 20260807 revised manuscript and Supplementary materials.

| Label | Folder | Code | Data (plot-ready) | Output |
|-------|--------|------|-------------------|--------|
| Fig. 1 | `figures/fig01/` | `code/plot_figure1.py` | `fig1ab_national_H_long.csv`, `fig1ab_national_H_spec_envelope.csv`, `fig1ef_national_Pu_long.csv`, `fig1ef_national_Pu_spec_envelope.csv`, `fig1_focal_future_mc_ci.csv` | `output/Figure1.tiff` |
| Fig. 2 | `figures/fig02/` | `code/preview_fig2_annual_3x2.py` | `rh_national_yoy.csv` | `output/Figure2.tiff` |
| Fig. 3 | `figures/fig03/` | `code/plot_figure3.py` (+ `_plot_fig3_trails_2points.py`) | **TIFF/JPG only** — person-window trails CSV not redistributed (needs CFPS). Use `output/Figure3.tiff`. | `output/Figure3.tiff` |
| Fig. 4 | `figures/fig04/` | `code/plot_fig4_rise_uise_pe.py` | `fig4_panel_f_violin_values.csv`; published TIFF (full Method annual detail omitted) | `output/Figure4.tiff` |
| S1 | `si/fig_s01/` | `code/plot_s1.py` | `S1_provincial.csv` | TIFF |
| S2 | `si/fig_s02/` | `code/plot_s2.py` | `S2_provincial.csv` | TIFF |
| S3 | `si/fig_s03/` | `code/plot_s3.py` | `S3_provincial.csv` | TIFF |
| S4 | `si/fig_s04/` | `code/plot_s4.py` | `S4_provincial.csv` | TIFF |
| S5 | `si/fig_s05/` | `code/plot_s5.py` | `S5_provincial.csv` | TIFF |
| S6 | `si/fig_s06/` | `code/plot_s6.py` | `11_r_omega_national_series.csv` | TIFF |
| S7 | `si/fig_s07/` | `code/plot_s7.py` | `15_kappa_national_series.csv` | TIFF |
| S8 | `si/fig_s08/` | `code/plot_s8.py` | `16_deflator_national_series.csv` | TIFF |
| S9 | `si/fig_s09/` | `code/plot_s9.py` | `S9_provincial.csv` | TIFF |
| S10 | `si/fig_s10/` | `code/plot_s10.py` | `S10_provincial.csv` | TIFF |
| S11 | `si/fig_s11/` | `code/plot_s11.py` | `FigS11_cfps_national_H_Pu_long.csv` | TIFF |
| S12 | `si/fig_s12/` | `code/plot_s12.py` | `FigS12_cfps_annual_RH.csv` | TIFF |
| S13 | `si/fig_s13/` | (microdata required to regenerate) | `figs13_row_counts.csv` (docs only) | TIFF only |
| S14 | `si/fig_s14/` | `code/plot_s14_ap_6panel.py` | `fig4_panel_f_violin_values.csv`; published TIFF (full Method annual detail omitted) | TIFF |
| S15 | `si/fig_s15/` | `code/plot_s15_s16.py` | `c_r_omega_a123_full_rerun_detail.csv` | TIFF |
| S16 | `si/fig_s16/` | (see fig_s15 script) | `d_entry_exit_share_sensitivity_detail.csv` | TIFF |
| S17 | `si/fig_s17/` | `code/plot_s17.py` | `24_2_cfps_4caliber_urbanization_gap.csv` | TIFF |
| S18 | `si/fig_s18/` | `code/plot_s18.py` | `18_build_dibao_ratio.xlsx` | TIFF |
| Table S1 | `tables/table_s01/` | `code/build_table_s1.py` | `TableS1_gravity_spec_comparison.csv` | CSV/MD |

## Map geometry

Province / national shapefiles are omitted from this pack. Map scripts keep relative paths under `_shared/province_boundaries/` and `_shared/scs_overlay/`; supply your own `.shp` to regenerate S1–S5 / S9–S10. Published TIFF/JPG for those panels are already under each figure’s `output/`.
