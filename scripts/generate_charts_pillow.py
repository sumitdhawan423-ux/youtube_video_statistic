"""
Standalone Chart Generator using Pillow (PIL)
Reads analytical CSV tables from output/tables/ and renders publication-ready
PNG charts directly to output/charts/ with zero third-party dependencies.
"""

import os
import sys
import csv
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TABLES_DIR = PROJECT_ROOT / "output" / "tables"
CHARTS_DIR = PROJECT_ROOT / "output" / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# Helper functions for drawing
def get_font(size: int = 14):
    try:
        # Standard Windows fonts
        for font_name in ["arial.ttf", "segoeui.ttf", "calibri.ttf", "DejaVuSans.ttf"]:
            try:
                return ImageFont.truetype(font_name, size)
            except Exception:
                continue
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()

def draw_header(draw, title: str, subtitle: str, width: int):
    f_title = get_font(20)
    f_sub = get_font(13)
    draw.text((40, 25), title, fill=(30, 41, 59), font=f_title)
    draw.text((40, 55), subtitle, fill=(100, 116, 139), font=f_sub)
    draw.line([(40, 80), (width - 40, 80)], fill=(226, 232, 240), width=2)

def generate_top_10_videos_chart():
    csv_file = TABLES_DIR / "01_top_10_videos.csv"
    if not csv_file.exists():
        return
        
    rows = []
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
            
    width, height = 1000, 650
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    draw_header(draw, "Top 10 Most Viewed Trending Videos", "Maximum views accumulated across all geographical regions", width)
    
    max_val = max(int(r["max_views"]) for r in rows) if rows else 1
    f_label = get_font(12)
    f_val = get_font(12)
    
    chart_x, chart_y = 320, 110
    bar_h = 36
    gap = 14
    max_bar_w = 540
    
    for i, r in enumerate(rows[:10]):
        y = chart_y + i * (bar_h + gap)
        views = int(r["max_views"])
        bar_w = int((views / max_val) * max_bar_w)
        
        # Label
        title_str = r["title"][:32] + "..." if len(r["title"]) > 32 else r["title"]
        label = f"[{r['country']}] {title_str}"
        draw.text((40, y + 8), label, fill=(51, 65, 85), font=f_label)
        
        # Bar
        draw.rounded_rectangle([(chart_x, y), (chart_x + bar_w, y + bar_h)], radius=4, fill=(59, 130, 246))
        
        # Value text
        val_str = f"{views/1e6:.2f}M views"
        draw.text((chart_x + bar_w + 12, y + 8), val_str, fill=(30, 41, 59), font=f_val)
        
    out_path = CHARTS_DIR / "01_top_10_videos_views.png"
    img.save(out_path)
    print(f"[+] Rendered: {out_path.name}")

def generate_category_chart():
    csv_file = TABLES_DIR / "03_category_aggregates.csv"
    if not csv_file.exists():
        return
        
    rows = []
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
            
    rows = rows[:8]
    width, height = 1000, 600
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    draw_header(draw, "Category Performance: Average Views & Engagement Rate", "Comparative metrics across top video genres", width)
    
    max_views = max(int(r["avg_views"]) for r in rows) if rows else 1
    f_label = get_font(13)
    f_val = get_font(12)
    
    chart_x, chart_y = 250, 110
    bar_h = 42
    gap = 14
    max_bar_w = 560
    
    for i, r in enumerate(rows):
        y = chart_y + i * (bar_h + gap)
        views = int(r["avg_views"])
        eng = float(r["avg_engagement_rate"])
        bar_w = int((views / max_views) * max_bar_w)
        
        # Category label
        draw.text((40, y + 10), r["category_title"][:22], fill=(51, 65, 85), font=f_label)
        
        # Bar
        draw.rounded_rectangle([(chart_x, y), (chart_x + bar_w, y + bar_h)], radius=5, fill=(16, 185, 129))
        
        # Value label
        val_str = f"{views/1e3:.0f}k avg views  |  {eng*100:.1f}% engagement"
        draw.text((chart_x + bar_w + 12, y + 10), val_str, fill=(30, 41, 59), font=f_val)
        
    out_path = CHARTS_DIR / "02_category_engagement_analysis.png"
    img.save(out_path)
    print(f"[+] Rendered: {out_path.name}")

def generate_country_chart():
    csv_file = TABLES_DIR / "04_country_comparison.csv"
    if not csv_file.exists():
        return
        
    rows = []
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
            
    width, height = 900, 520
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    draw_header(draw, "Geographical Comparison: Average Views by Country", "Cross-country analysis of trending video reach", width)
    
    max_views = max(int(r["avg_views"]) for r in rows) if rows else 1
    f_label = get_font(14)
    f_val = get_font(12)
    
    chart_x, chart_y = 160, 120
    bar_h = 45
    gap = 20
    max_bar_w = 520
    
    colors = [(99, 102, 241), (236, 72, 153), (245, 158, 11), (20, 184, 166), (139, 92, 246)]
    
    for i, r in enumerate(rows):
        y = chart_y + i * (bar_h + gap)
        views = int(r["avg_views"])
        bar_w = int((views / max_views) * max_bar_w)
        color = colors[i % len(colors)]
        
        draw.text((60, y + 12), f"Region: {r['country']}", fill=(51, 65, 85), font=f_label)
        draw.rounded_rectangle([(chart_x, y), (chart_x + bar_w, y + bar_h)], radius=5, fill=color)
        
        val_str = f"{views:,} views ({r['unique_videos']} videos, ~{r['avg_days_to_trend']} days to trend)"
        draw.text((chart_x + bar_w + 12, y + 12), val_str, fill=(30, 41, 59), font=f_val)
        
    out_path = CHARTS_DIR / "03_country_comparison.png"
    img.save(out_path)
    print(f"[+] Rendered: {out_path.name}")

def generate_correlation_matrix_chart():
    csv_file = TABLES_DIR / "07_correlation_matrix.csv"
    if not csv_file.exists():
        return
        
    rows = []
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
            
    width, height = 750, 650
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    draw_header(draw, "Pearson Correlation Heatmap", "Correlation across Views, Likes, Dislikes, and Comments", width)
    
    f_axis = get_font(13)
    f_cell = get_font(13)
    
    metrics = ["views", "likes", "dislikes", "comment_count"]
    start_x, start_y = 180, 140
    cell_size = 110
    
    for j, m in enumerate(metrics):
        draw.text((start_x + j * cell_size + 20, start_y - 30), m, fill=(71, 85, 105), font=f_axis)
        draw.text((40, start_y + j * cell_size + 40), m, fill=(71, 85, 105), font=f_axis)
        
    for i, r in enumerate(rows):
        for j, m in enumerate(metrics):
            val = float(r.get(m, 0.0))
            x0 = start_x + j * cell_size
            y0 = start_y + i * cell_size
            x1 = x0 + cell_size - 4
            y1 = y0 + cell_size - 4
            
            # Color intensity from cool blue to vibrant coral
            intensity = int(max(0.0, min(1.0, val)) * 200)
            cell_color = (255 - intensity // 2, 230 - intensity // 3, 255 - intensity)
            
            draw.rectangle([(x0, y0), (x1, y1)], fill=cell_color)
            txt = f"{val:.3f}"
            draw.text((x0 + 32, y0 + 44), txt, fill=(15, 23, 42), font=f_cell)
            
    out_path = CHARTS_DIR / "06_correlation_matrix_heatmap.png"
    img.save(out_path)
    print(f"[+] Rendered: {out_path.name}")

def generate_mllib_importances_chart():
    csv_file = TABLES_DIR / "mllib_feature_importances.csv"
    if not csv_file.exists():
        return
        
    rows = []
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
            
    width, height = 850, 500
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    draw_header(draw, "Spark MLlib: Random Forest Feature Importances", "Relative Gini importance of predictive variables for video view volume", width)
    
    max_imp = max(float(r["Importance"]) for r in rows) if rows else 1
    f_label = get_font(13)
    f_val = get_font(12)
    
    chart_x, chart_y = 220, 110
    bar_h = 36
    gap = 14
    max_bar_w = 460
    
    for i, r in enumerate(rows):
        y = chart_y + i * (bar_h + gap)
        imp = float(r["Importance"])
        bar_w = int((imp / max_imp) * max_bar_w)
        
        draw.text((40, y + 8), r["Feature"], fill=(51, 65, 85), font=f_label)
        draw.rounded_rectangle([(chart_x, y), (chart_x + bar_w, y + bar_h)], radius=4, fill=(14, 165, 233))
        
        val_str = f"{imp:.4f} ({imp*100:.1f}%)"
        draw.text((chart_x + bar_w + 12, y + 8), val_str, fill=(30, 41, 59), font=f_val)
        
    out_path = CHARTS_DIR / "07_mllib_feature_importances.png"
    img.save(out_path)
    print(f"[+] Rendered: {out_path.name}")

def generate_kmeans_cluster_chart():
    csv_file = TABLES_DIR / "mllib_kmeans_clusters.csv"
    if not csv_file.exists():
        return
        
    rows = []
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
            
    width, height = 950, 550
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    draw_header(draw, "Spark MLlib: K-Means Engagement Clusters", "Behavioral segmentation of trending videos by view scale and interaction density", width)
    
    f_title = get_font(14)
    f_body = get_font(12)
    
    colors = [(239, 68, 68), (59, 130, 246), (16, 185, 129), (168, 85, 247)]
    card_w, card_h = 410, 160
    coords = [(50, 110), (490, 110), (50, 310), (490, 310)]
    
    for i, r in enumerate(rows[:4]):
        x, y = coords[i]
        c = colors[i % len(colors)]
        
        # Draw card background
        draw.rounded_rectangle([(x, y), (x + card_w, y + card_h)], radius=8, fill=(248, 250, 252), outline=(226, 232, 240), width=2)
        # Left accent stripe
        draw.rounded_rectangle([(x, y), (x + 8, y + card_h)], radius=4, fill=c)
        
        # Title
        draw.text((x + 24, y + 16), f"Cluster {r['cluster']}: {r['cluster_label']}", fill=c, font=f_title)
        
        # Details
        v = int(r["avg_views"])
        l = int(r["avg_likes"])
        cm = int(r["avg_comments"])
        eng = float(r["avg_engagement_rate"]) * 100
        
        draw.text((x + 24, y + 48), f"- Video Volume: {r['video_count']} videos", fill=(71, 85, 105), font=f_body)
        draw.text((x + 24, y + 72), f"- Average Views: {v:,}", fill=(71, 85, 105), font=f_body)
        draw.text((x + 24, y + 96), f"- Average Likes: {l:,} | Comments: {cm:,}", fill=(71, 85, 105), font=f_body)
        draw.text((x + 24, y + 120), f"- Mean Engagement Rate: {eng:.2f}%", fill=(71, 85, 105), font=f_body)
        
    out_path = CHARTS_DIR / "08_mllib_engagement_clusters.png"
    img.save(out_path)
    print(f"[+] Rendered: {out_path.name}")

def main():
    print("=" * 60)
    print("Rendering High-Resolution Charts to output/charts/")
    print("=" * 60)
    generate_top_10_videos_chart()
    generate_category_chart()
    generate_country_chart()
    generate_correlation_matrix_chart()
    generate_mllib_importances_chart()
    generate_kmeans_cluster_chart()
    print("[+] All charts successfully written!")

if __name__ == "__main__":
    main()

