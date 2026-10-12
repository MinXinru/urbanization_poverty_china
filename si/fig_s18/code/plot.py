from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"; OUT=ROOT/"output"; OUT.mkdir(parents=True,exist_ok=True)
BLUE="#0072B2"; ORANGE="#D55E00"; VARIANTS=[("−10%",0.9),("Baseline",1.0),("+10%",1.1)]
PANEL_SPECS = [
    ("a", "urban_IS_exiters_M", "Urban IS-exiters"),
    ("b", "urban_IS_entrants_M", "Urban IS-entrants"),
    ("c", "rural_intra_turnover_M", "Rural intra-sectoral turnover (IS-entrants + IS-exiters)"),
    ("d", "urban_IS_stayers_M", "Urban IS-stayers"),
    ("e", "rural_IS_stayers_M", "Rural IS-stayers"),
    ("f", "cross_sectoral_movers_M", "Cross-sectoral movers (CS-exiters, CS-entrants, CS-stayers)"),
]

def plot_figure(summary, path, title):
    # Pillow rendering at 600 dpi preserves the dimensions and typography of S16.
    dpi = 600
    W, H = 7200, 6120
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)
    serif = r"C:\Windows\Fonts\times.ttf"
    serif_bold = r"C:\Windows\Fonts\timesbd.ttf"
    font_tick = ImageFont.truetype(serif, 84)
    font_axis = ImageFont.truetype(serif, 86)
    font_title = ImageFont.truetype(serif, 94)
    font_panel = ImageFont.truetype(serif_bold, 112)
    font_legend = ImageFont.truetype(serif, 82)
    left, right, top, bottom = 275, 130, 255, 140
    gap_x, gap_y = 270, 200
    panel_w = (W-left-right-gap_x)//2
    panel_h = (H-top-bottom-2*gap_y)//3
    # Shared horizon legend, positioned like Supplementary Fig. S16.
    leg_y = 74
    draw.line((left, leg_y+31, left+135, leg_y+31), fill=BLUE, width=13)
    draw.ellipse((left+53,leg_y+9,left+97,leg_y+53),fill=BLUE)
    draw.text((left+153,leg_y-18),"Near-term (to 2030)",font=font_legend,fill="black")
    x2=left+830
    draw.line((x2,leg_y+31,x2+135,leg_y+31),fill=ORANGE,width=13)
    draw.ellipse((x2+53,leg_y+9,x2+97,leg_y+53),fill=ORANGE)
    draw.text((x2+153,leg_y-18),"Late-century (2030–2100)",font=font_legend,fill="black")

    def nice_step(mx):
        if mx <= 0: return 1.0
        raw = mx/4.0
        power = 10**np.floor(np.log10(raw))
        frac = raw/power
        base = 1 if frac <= 1 else (2 if frac <= 2 else (5 if frac <= 5 else 10))
        return base*power

    for idx,(letter,metric,paneltitle) in enumerate(PANEL_SPECS):
        row, col = divmod(idx,2)
        px=left+col*(panel_w+gap_x); py=top+row*(panel_h+gap_y)
        chart_left=px+170; chart_right=px+panel_w-55
        chart_top=py+215; chart_bottom=py+panel_h-190
        vals_all=[]
        for horizon in ("near","late"):
            g=summary[summary.horizon==horizon].set_index("variant")
            vals_all += [float(g.loc[v,metric]) for v,_ in VARIANTS]
        mx=max(vals_all) if vals_all else 1.0
        step=nice_step(mx*1.08); ymax=max(step,step*np.ceil(mx*1.08/step))
        # Panel title and letter.
        draw.text((chart_left,py+30),paneltitle,font=font_title,fill="black")
        draw.text((px+18,py+22),f"({letter})",font=font_panel,fill="black")
        # Horizontal grid and y ticks.
        tick=0.0
        while tick <= ymax+1e-9:
            yy=chart_bottom-int((tick/ymax)*(chart_bottom-chart_top))
            draw.line((chart_left,yy,chart_right,yy),fill=(220,220,220),width=3)
            lab=f"{tick:g}"
            box=draw.textbbox((0,0),lab,font=font_tick); tw=box[2]-box[0]
            draw.text((chart_left-22-tw,yy-(box[3]-box[1])//2),lab,font=font_tick,fill="black")
            tick+=step
        # Left and bottom axes.
        draw.line((chart_left,chart_top,chart_left,chart_bottom),fill="black",width=4)
        draw.line((chart_left,chart_bottom,chart_right,chart_bottom),fill="black",width=4)
        # Rotated y-axis label.
        lab_img=Image.new("RGBA",(650,110),(255,255,255,0)); ImageDraw.Draw(lab_img).text((0,0),"Million persons / year",font=font_axis,fill="black")
        lab_img=lab_img.rotate(90,expand=True)
        img.paste(lab_img,(max(8,px-250),(chart_top+chart_bottom-lab_img.height)//2),lab_img)
        # Three sensitivity settings and central reference line.
        xs=[chart_left+int((chart_right-chart_left)*q) for q in (.12,.50,.88)]
        draw.line((xs[1],chart_top,xs[1],chart_bottom),fill=(145,145,145),width=4)
        for xpt,label in zip(xs,[v for v,_ in VARIANTS]):
            draw.line((xpt,chart_bottom,xpt,chart_bottom+18),fill="black",width=3)
            box=draw.textbbox((0,0),label,font=font_tick); tw=box[2]-box[0]
            draw.text((xpt-tw//2,chart_bottom+27),label,font=font_tick,fill="black")
        for horizon,color in (("near",BLUE),("late",ORANGE)):
            g=summary[summary.horizon==horizon].set_index("variant")
            vals=[float(g.loc[v,metric]) for v,_ in VARIANTS]
            pts=[]
            for xpt,value in zip(xs,vals):
                yy=chart_bottom-int((value/ymax)*(chart_bottom-chart_top))
                pts.append((xpt,yy))
            draw.line(pts,fill=color,width=14)
            radius=24
            for xpt,yy in pts:
                draw.ellipse((xpt-radius,yy-radius,xpt+radius,yy+radius),fill=color)
    img.save(path,format="TIFF",compression="tiff_lzw",dpi=(dpi,dpi))
    preview=path.with_name(path.stem+"_preview.jpg")
    img.resize((2160,1836),Image.Resampling.LANCZOS).save(preview,format="JPEG",quality=93,optimize=True)
    print(f"Wrote {path}"); print(f"Preview {preview}")

def main():
    values=pd.read_csv(DATA/"summary_values.csv")
    plot_figure(values,OUT/"figure.tiff","S18 sensitivity")
if __name__=="__main__": main()
