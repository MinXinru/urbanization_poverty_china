# GitHub upload pack — figures and tables (20260807 resubmission)

Self-contained plotting pack for **main-text Figures 1–4**, **Supplementary Figures S1–S18**, and **Supplementary Table S1**, numbered to match the 20260807 revised manuscript and Supplementary materials.

**What each panel includes:** plot-ready analysis tables the figure scripts read, plotting code, and published TIFF/JPG under `output/`. **No raw survey microdata** (CFPS person-level extracts, census microdata) are included.

**Maps:** Province boundary and national-outline shapefiles are omitted. Map plot scripts expect relative paths such as `_shared/province_boundaries/china_provinces.shp` and `_shared/scs_overlay/china_national_boundary.shp`; place your own files there (or edit the path) only if you need to regenerate S1–S5 / S9–S10. Published TIFF/JPG for those panels are already under each figure’s `output/`.

**Fig. 4 / Supp. Fig. S14:** Published TIFF/JPG and the small panel-(f) violin summary CSV are included. Full Method 1–3 dual-endpoint annual detail CSVs (`*_32flow_detail_annual*.csv`) are large OD/flow dumps omitted here; regenerating the 6-panel layout from scratch needs those Method outputs locally.

## Layout

```
Github_upload/
  README.md
  SOURCE_MAPPING.md
  requirements.txt
  _shared/                 # style + path helper; map folders are placeholders only
  figures/
    fig01/ … fig04/        # each: code/  data/  output/  README.md
  si/
    fig_s01/ … fig_s18/    # each: code/  data/  output/  README.md
  tables/
    table_s01/
```

## Index

| Label | Folder | Short title |
|-------|--------|-------------|
| Figure 1 | `figures/fig01/` | National AP/RPO headcounts and urban shares |
| Figure 2 | `figures/fig02/` | Annual Ravallion–Huppi decomposition |
| Figure 3 | `figures/fig03/` | CFPS trails + national flow volumes |
| Figure 4 | `figures/fig04/` | RPO intra-sectoral turnover / stayers / movers (6-panel) |
| Supp. Fig. S1 | `si/fig_s01/` | Provincial AP headcount, LSD 2050 & 2100 |
| Supp. Fig. S2 | `si/fig_s02/` | Provincial AP headcount 2000–2100 |
| Supp. Fig. S3 | `si/fig_s03/` | Provincial RPO headcount 2000–2100 |
| Supp. Fig. S4 | `si/fig_s04/` | Provincial AP urban share 2000–2100 |
| Supp. Fig. S5 | `si/fig_s05/` | Provincial RPO urban share 2000–2100 |
| Supp. Fig. S6 | `si/fig_s06/` | RΩ growth-rate sensitivity (national H, Pu) |
| Supp. Fig. S7 | `si/fig_s07/` | Income-bridge κ sensitivity |
| Supp. Fig. S8 | `si/fig_s08/` | GDP-deflator smoother sensitivity |
| Supp. Fig. S9 | `si/fig_s09/` | Province-level RH AP ΔH |
| Supp. Fig. S10 | `si/fig_s10/` | Province-level RH RPO ΔH |
| Supp. Fig. S11 | `si/fig_s11/` | CFPS national H and urban share, 2010–2022 |
| Supp. Fig. S12 | `si/fig_s12/` | CFPS annual Ravallion–Huppi, 2010–2022 |
| Supp. Fig. S13 | `si/fig_s13/` | CFPS biennial person trails (TIFF + row counts) |
| Supp. Fig. S14 | `si/fig_s14/` | AP 6-panel (same grammar as Fig. 4) |
| Supp. Fig. S15 | `si/fig_s15/` | RPO × RΩ growth-rate × three approaches |
| Supp. Fig. S16 | `si/fig_s16/` | RPO × CFPS transition-share sensitivity |
| Supp. Fig. S17 | `si/fig_s17/` | CFPS urbanisation definitions vs NBS |
| Supp. Fig. S18 | `si/fig_s18/` | Urban–rural Dibao ratio RΩ |
| Supp. Table S1 | `tables/table_s01/` | Gravity holdout comparison |

## Shared assets

| Path | Role |
|------|------|
| `_shared/pack_paths.py` | Resolve `../data`, `../output`, pack `_shared` from any `code/*.py` |
| `_shared/okabe_ito_style.py` | Okabe–Ito colours + matplotlib style |
| `_shared/province_names.py` | Chinese→English province names |
| `_shared/map_cartography.py` | Choropleth helpers (expects shapefile paths below) |
| `_shared/province_boundaries/` | **Placeholder only** — supply `china_provinces.shp` yourself |
| `_shared/scs_overlay/` | **Placeholder only** — supply `china_national_boundary.shp` yourself |

## Software

- Python **3.10+**
- `pip install -r requirements.txt`

## How to run (examples)

Scripts resolve paths relative to the pack (no machine-absolute paths). Run from each figure’s `code/` directory:

```bash
cd figures/fig04/code && python3 plot_fig4_rise_uise_pe.py
cd ../../si/fig_s06/code && python3 plot_s6.py
cd ../../si/fig_s15/code && python3 plot_s15_s16.py
cd ../../tables/table_s01/code && python3 build_table_s1.py
```

Frozen `output/*.tiff` / `*_preview.jpg` are the published panels if you do not regenerate.

## Regeneration notes

| Folder | Notes |
|--------|-------|
| `si/fig_s13` | Ships published TIFF + row counts; regenerating trails needs CFPS microdata |
| `figures/fig03` | TIFF/JPG only; person-window trails CSV not redistributed (same as S13) |
| Map figures S1–S5, S9–S10 | Need user-supplied shapefile at the documented relative path; TIFF already in `output/` |
| `si/fig_s14` / `figures/fig04` | Ships published TIFF + panel-(f) violin CSV; full Method annual detail omitted — use `output/*.tiff` or supply Method CSVs locally to regenerate |
| `si/fig_s15` / `si/fig_s16` | Shared plot script `fig_s15/code/plot_s15_s16.py`; S16 data under `fig_s16/data/` |
| `tables/table_s01` | Frozen holdout CSV; gravity re-fit not re-run here |

## Licence / data

CFPS microdata, multi-GB raw inputs, and map shapefiles are not included.
