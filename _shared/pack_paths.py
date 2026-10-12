# -*- coding: utf-8 -*-
"""Resolve Github_upload pack paths from any figure ``code/*.py`` script.

Layout expected::

    Github_upload/
      _shared/          # this module + style + geo
      figures/figXX/{code,data,output}/
      si/fig_sXX/{code,data,output}/
      tables/table_sXX/{code,data,output}/

Usage (from a plot script)::

    from pathlib import Path
    import sys

    HERE = Path(__file__).resolve().parent
    # Walk up until _shared/pack_paths.py is importable, or:
    sys.path.insert(0, str(HERE.parents[n] / "_shared"))  # prefer ensure_shared_on_path

    from pack_paths import figure_dirs
    paths = figure_dirs(__file__)
    DATA, OUT, SHARED = paths.data, paths.output, paths.shared
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FigurePaths:
    """Pack-local directories for one figure / table folder."""

    code: Path
    figure: Path
    data: Path
    output: Path
    shared: Path
    pack_root: Path


def find_pack_root(start: Path | str) -> Path:
    """Walk parents until a directory containing ``_shared/okabe_ito_style.py``."""
    cur = Path(start).resolve()
    if cur.is_file():
        cur = cur.parent
    for p in [cur, *cur.parents]:
        marker = p / "_shared" / "okabe_ito_style.py"
        if marker.is_file():
            return p
    raise FileNotFoundError(
        f"Could not find Github_upload/_shared from {start!s}. "
        "Run scripts from inside the uploaded pack."
    )


def figure_dirs(script_file: Path | str) -> FigurePaths:
    """Return data/output/shared dirs for the figure folder that owns ``script_file``.

    ``script_file`` should live in ``.../<fig>/code/<name>.py``.
    """
    code = Path(script_file).resolve().parent
    figure = code.parent
    pack_root = find_pack_root(code)
    shared = pack_root / "_shared"
    return FigurePaths(
        code=code,
        figure=figure,
        data=figure / "data",
        output=figure / "output",
        shared=shared,
        pack_root=pack_root,
    )


def ensure_shared_on_path(script_file: Path | str) -> FigurePaths:
    """Insert ``_shared`` (and the script's ``code/``) on ``sys.path``; return dirs."""
    paths = figure_dirs(script_file)
    for p in (paths.shared, paths.code):
        s = str(p)
        if s not in sys.path:
            sys.path.insert(0, s)
    return paths
