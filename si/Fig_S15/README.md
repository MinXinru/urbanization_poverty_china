# Supplementary Fig. S15 plotting package

This folder contains the editable Python plotting script, the plot-ready derived RPO flow table, the 600-dpi TIFF, preview, and caption. The CSV contains model-level aggregated flows by sector and forecast interval; it contains no person-level records or raw source data.

Run from this folder with Python 3.11 or later after installing `matplotlib`, `numpy`, and `pandas`:

```powershell
python .\code\plot_s15.py
```

The script saves a fresh TIFF and preview in `output`. Cross-sectoral movers are recalculated from the six-state projected flow matrix and include CS-exiters, CS-entrants, and CS-stayers; each flow is attributed to its origin sector.
