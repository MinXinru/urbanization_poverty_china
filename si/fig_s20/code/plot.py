from pathlib import Path
import csv
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"
OUT = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)

crosswalk = {}
with (DATA / "s20_crosswalk_weighted_counts.csv").open(encoding="utf-8-sig", newline="") as f:
    for row in csv.DictReader(f):
        crosswalk[(row["community"], row["household_type"])] = float(row["weighted_person_waves"])
waves = []
with (DATA / "s20_wave_agreement.csv").open(encoding="utf-8-sig", newline="") as f:
    for row in csv.DictReader(f):
        waves.append((int(row["year"]), float(row["weighted_agreement"])))

communities = ["rural", "urban", "unavailable"]
households = ["rural", "urban"]
grand_total = sum(crosswalk.values())
cell_share = {(c, h): crosswalk.get((c, h), 0.0) / grand_total for c in communities for h in households}
both_total = sum(crosswalk.get((c, h), 0.0) for c in communities[:2] for h in households)
agree_total = sum(crosswalk.get((c, c), 0.0) for c in communities[:2])
pooled_agreement = agree_total / both_total

font_dir = Path("C:/Windows/Fonts")
def font(px, bold=False):
    path = font_dir / ("timesbd.ttf" if bold else "times.ttf")
    if not path.exists():
        # Common Linux fallback for reproducible rendering outside Windows.
        path = Path("/usr/share/fonts/truetype/msttcorefonts") / ("Times_New_Roman_Bold.ttf" if bold else "Times_New_Roman.ttf")
    return ImageFont.truetype(str(path), px)

W, H = 3000, 1400
im = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(im)
ink, pale_green, pale_orange, gray = "#202020", "#DCEFE9", "#FBE7DF", "#ECEFF2"
f_axis, f_tick, f_cell, f_small = font(53), font(41), font(58, True), font(41)
f_panel = font(58, True)

# (a) Weighted cross-classification; all shares use the retained sample denominator.
gx, gy, cw, ch = 560, 310, 395, 290
d.text((210, 105), "(a)", font=f_panel, fill=ink, anchor="lt")
d.text((gx + cw, 155), "Household economic type", font=f_axis, fill=ink, anchor="mm")
for j, title in enumerate(["Agricultural", "Non-agricultural"]):
    d.text((gx + (j + .5) * cw, 217), title, font=f_tick, fill=ink, anchor="mm")
    d.text((gx + (j + .5) * cw, 263), "household", font=f_tick, fill=ink, anchor="mm")
ylab = Image.new("RGBA", (800, 75), (255, 255, 255, 0))
ImageDraw.Draw(ylab).text((400, 37), "Community classification", font=f_axis, fill=ink, anchor="mm")
ylab = ylab.rotate(90, expand=True)
im.paste(ylab, (115, int(gy + 1.5 * ch - ylab.height / 2)), ylab)
for i, (key, label) in enumerate(zip(communities, ["Rural", "Urban", "Unavailable"])):
    y = gy + i * ch
    d.text((gx - 32, y + ch / 2), label, font=f_tick, fill=ink, anchor="rm")
    for j, hh in enumerate(households):
        x = gx + j * cw
        fill = gray if key == "unavailable" else (pale_green if key == hh else pale_orange)
        d.rectangle((x, y, x + cw, y + ch), fill=fill, outline="white", width=9)
        d.text((x + cw / 2, y + ch / 2), f"{cell_share[(key, hh)] * 100:.1f}%", font=f_cell, fill=ink, anchor="mm")

# (b) Weighted wave-specific agreement among records with both labels observed.
rx0, rx1, ry0, ry1 = 1710, 2890, 300, 1180
d.text((1610, 105), "(b)", font=f_panel, fill=ink, anchor="lt")
ylab2 = Image.new("RGBA", (600, 58), (255, 255, 255, 0))
ImageDraw.Draw(ylab2).text((300, 29), "Agreement (%)", font=f_axis, fill=ink, anchor="mm")
ylab2 = ylab2.rotate(90, expand=True)
im.paste(ylab2, (1545, int((ry0 + ry1) / 2 - ylab2.height / 2)), ylab2)
for tick in [0, 25, 50, 75, 100]:
    yy = ry1 - (ry1 - ry0) * tick / 100
    d.line((rx0, yy, rx1, yy), fill="#D8DDE2" if tick else ink, width=3 if tick == 0 else 2)
    d.text((rx0 - 20, yy), str(tick), font=f_small, fill=ink, anchor="rm")
bar_w = 94
step = (rx1 - rx0) / len(waves)
for i, (year, rate) in enumerate(waves):
    x = rx0 + i * step + (step - bar_w) / 2
    h = (ry1 - ry0) * rate
    d.rounded_rectangle((x, ry1 - h, x + bar_w, ry1), radius=8, fill="#009E73")
    d.text((x + bar_w / 2, ry1 - h - 30), f"{rate * 100:.1f}", font=f_small, fill=ink, anchor="mm")
    d.text((x + bar_w / 2, ry1 + 45), str(year), font=f_small, fill=ink, anchor="mm")

im.save(OUT / "figure.tiff", dpi=(300, 300), compression="tiff_lzw")
im.save(OUT / "figure_preview.jpg", quality=95, dpi=(180, 180))
print(f"Pooled weighted agreement: {pooled_agreement:.1%}")
print(f"Saved figure to {OUT}")
