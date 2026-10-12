# Figure 3 — SST transition flows and poverty trajectories

This folder includes the editable final SVG, plotting source, style/helper code, and processed data. No raw CFPS file or individual-level records are included.

## Contents

- `output/Figure3.svg`: editable final vector figure with the agreed labels: IS-stayers, IS-exiters, IS-entrants, CS-stayers, CS-exiters, CS-entrants; the bottom row is labelled “cross-sectional”.
- `_scratch_exports/.../method1_32flow_detail_annual_main_ols_clip01.csv`: modelled schedule-by-flow annual estimates used for the curve panels. These are aggregated outputs, not person-level records.
- `data/endpoint_transition_aggregates.csv`: 107 grouped status-by-sector transition cells with weighted totals. Person identifiers and row-level records were removed before export.
- `code/03_path_branching/`: plotting source and helper code.

## Reproduction note

The curve data and the grouped transition table are safe aggregate outputs. The original trail panels were drawn from linked person-level CFPS endpoint records. Those records are deliberately not included. Therefore, the provided final SVG is the reproducible publication artifact for the complete 4×4 figure; rerunning the original `plot_figure3_CSM.py` to regenerate individual trail lines requires access to the source CFPS endpoint file in the protected analysis environment. Do not add that file to this folder or the public repository.

To regenerate only the annual curve panels from the included modelled aggregate data, run:

```bash
python code/03_path_branching/7_plot_figure3_wave_curves.py
```

Dependencies: Python 3.10+, matplotlib, numpy, pandas.
