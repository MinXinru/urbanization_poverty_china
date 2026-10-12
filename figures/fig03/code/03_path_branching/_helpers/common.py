from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT_DIR = ROOT / "outputs"
FIG_OUT = ROOT / "fig3_plot_outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_OUT.mkdir(parents=True, exist_ok=True)
