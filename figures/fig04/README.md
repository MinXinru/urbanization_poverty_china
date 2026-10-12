# Figure 4 (RPO) — GitHub upload package

This folder contains the current editable Figure 4 SVG, its preview and TIFF export, standalone plotting code, and the compact grouped data needed to reproduce the figure. It contains **no original/raw data and no individual-level records or identifiers**.

## Contents

- `code/plot_figure4.py` — standalone plotting script for Figure 4.
- `code/okabe_ito_style.py` — the figure style and palette used by the script.
- `data/fig4_method1_rpo_aggregates.csv` — method 1 RPO flow totals grouped by poverty-line schedule, scenario, and time interval.
- `data/fig4_panel_f_rpo_violin_values.csv` — grouped RPO values used for panel (f), pooled by method, schedule, scenario, and projection window.
- `output/Figure4.svg` — editable vector figure.
- `output/Figure4_preview.jpg` and `output/Figure4_preview.tiff` — rendered exports.
- `output/Figure4_caption.txt` — figure caption.

The CSVs contain model-derived aggregates only. They do not contain respondent records, household records, person IDs, or raw CFPS observations.

## Reproduce

From this folder, install the packages in `requirements.txt`, then run:

```bash
python code/plot_figure4.py
```

The script writes the SVG, preview, TIFF and caption into `output/`.
