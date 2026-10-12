# -*- coding: utf-8 -*-
"""Supplementary Table S1: holdout comparison of nested OD gravity specifications.

Prints a markdown table from the frozen comparison CSV (Approach 2 nested specs).
Does not re-fit gravity models (full holdout re-run is overnight-scale; see
`5_predicting_future/code/_pack_01/20260722_four_schemes_poc.py`).
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
# Locate pack _shared (Github_upload/_shared) from code/
_pack = HERE
while _pack != _pack.parent and not (_pack / "_shared" / "pack_paths.py").is_file():
    _pack = _pack.parent
sys.path.insert(0, str(_pack / "_shared"))
from pack_paths import ensure_shared_on_path  # noqa: E402
_paths = ensure_shared_on_path(__file__)
HERE = _paths.code
DATA = _paths.data
OUT = _paths.output
SHARED = _paths.shared
ROOT = _paths.pack_root
CSV = DATA / "TableS1_gravity_spec_comparison.csv"


def main() -> None:
    df = pd.read_csv(CSV)
    OUT.mkdir(parents=True, exist_ok=True)
    out_csv = OUT / "TableS1_gravity_spec_comparison.csv"
    df.to_csv(out_csv, index=False)
    md = OUT / "TableS1_gravity_spec_comparison.md"
    try:
        md.write_text(df.to_markdown(index=False) + "\n", encoding="utf-8")
    except Exception:
        # no tabulate: plain text
        md.write_text(df.to_string(index=False) + "\n", encoding="utf-8")
    print(f"Wrote {out_csv}")
    print(f"Wrote {md}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
