"""
Sample Dataset Generator for YouTube Video Statistics Analysis.
Generates realistic multi-country CSV datasets (USvideos.csv, INvideos.csv, GBvideos.csv, CAvideos.csv)
with multiline text, unicode characters, and edge cases to test PySpark pipeline end-to-end.
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CHANNELS_DATA = {
    "US": [
        ("CaseyNeistat", 22, ["vlog", "tech", "nyc", "gear", "film"]),
        ("Marques Brownlee", 28, ["mkbhd", "smartphone", "apple", "tesla", "gadgets"]),
        ("Vox", 25, ["explain", "journalism", "politics", "culture", "graphics"]),
        ("EminemVEVO", 10, ["rap", "hiphop", "revival", "music video", "vevo"]),
        ("Dude Perfect", 17, ["trick shots", "basketball", "sports", "comedy"]),
        ("Veritasium", 27, ["science", "physics", "experiments", "curiosity", "atoms"]),
        ("PewDiePie", 20, ["gaming", "meme review", "reaction", "funny"]),
        ("Tasty", 26, ["recipes", "food", "cooking", "tasty", "buzzfeed"]),
        ("Saturday Night Live", 23, ["snl", "comedy", "parody", "sketch", "cold open"]),
        ("Warner Bros. Pictures", 1, ["trailer", "movies", "cinema", "official"]),
    ],
    "IN": [
        ("T-Series", 10, ["bollywood", "hindi songs", "music video", "remix"]),
        ("CarryMinati", 23, ["roast", "comedy", "parody", "hindi roasting"]),
        ("Technical Guruji", 28, ["tech", "unboxing", "hindi tech", "smartphones"]),
        ("NDTV", 25, ["breaking news", "india politics", "news today", "analysis"]),
        ("BB Ki Vines", 23, ["bhuvan bam", "comedy sketches", "funny video"]),
        ("Amit Bhadana", 24, ["desi comedy", "humor", "entertainment"]),
        ("Sandeep Maheshwari", 27, ["motivation", "life guidance", "inspiration"]),
        ("Sanjeev Kapoor Khazana", 26, ["indian recipe", "curry", "masterchef"]),
        ("Star Sports", 17, ["cricket", "ipl", "match highlights", "kohli"]),
        ("YRF", 1, ["bollywood movies", "trailer", "teaser", "yrf films"]),
    ],
    "GB": [
        ("BBC News", 25, ["bbc", "uk news", "world news", "politics"]),
        ("Ed Sheeran", 10, ["pop music", "acoustic", "divide", "lyrics"]),
        ("Sidemen", 24, ["challenges", "sidemen sunday", "entertainment"]),
        ("Gordon Ramsay", 26, ["kitchen nightmares", "cooking tips", "chef"]),
        ("Top Gear", 2, ["cars", "supercars", "track test", "stewart"]),
    ],
    "CA": [
        ("Linus Tech Tips", 28, ["linus", "pc build", "gpu", "benchmarks"]),
        ("The Weeknd", 10, ["r&b", "pop", "blinding lights", "vevo"]),
        ("AsapSCIENCE", 27, ["science questions", "biology", "animation"]),
        ("Unbox Therapy", 28, ["gadgets", "unbox", "cool tech"]),
    ],
}

TITLES = [
    "I Bought A Floating House!",
    "The Truth About The New Smartphone Review",
    "How The Global Supply Chain Broke Down",
    "Official Music Video - Track #4",
    "Real Life Trick Shots | Insane Edition",
    "Why The World's Biggest Supercomputer Was Built Here",
    "Reacting To The Funniest Internet Memes",
    "Easy 15-Minute Dinner Recipes You Need To Try",
    "Weekend Update: Political Headlines & Comedy Sketch",
    "Official Movie Teaser Trailer [HD]",
    "Unboxing The Most Expensive Laptop Ever Made",
    "Breaking News: Live Coverage & Expert Analysis",
    "Every Student Before The Exams | Comedy Drama",
    "Master Class: Perfect Butter Chicken From Scratch",
    "Full Match Highlights - Final Thriller",
    "How Neural Networks Actually Work Under The Hood",
    "Top 10 Hidden Car Features You Didn't Know About",
    "Mindset Reset: How To Overcome Self-Doubt",
    "24-Hour Road Trip Challenge Across The Country",
    "Behind The Scenes: Making Of A Blockbuster",
]

DESCRIPTIONS = [
    "Thank you guys so much for watching!\nDon't forget to like and subscribe for more weekly episodes.\nFollow on Instagram: @channel\nTwitter: @channel",
    "Special thanks to our sponsors.\nTimestamps:\n0:00 - Intro\n1:20 - Deep Dive\n5:45 - Benchmark Results\n8:10 - Final Verdict",
    "Full details and references cited in this video are available at https://example.com/sources.\nJoin the conversation below in the comments!",
    "Stream or download the new album right now.\nProduced, mixed and mastered by Studio X.\nCopyright 2017-2018 All Rights Reserved.",
    "This was hands down one of the hardest videos we have ever filmed.\nHit the notification bell so you never miss another upload!",
]

def generate_country_dataset(country: str, num_records: int = 150):
    channels = CHANNELS_DATA.get(country, CHANNELS_DATA["US"])
    filename = DATA_DIR / f"{country}videos.csv"
    
    random.seed(42 + hash(country) % 1000)
    
    fieldnames = [
        "video_id",
        "trending_date",
        "title",
        "channel_title",
        "category_id",
        "publish_time",
        "tags",
        "views",
        "likes",
        "dislikes",
        "comment_count",
        "thumbnail_link",
        "comments_disabled",
        "ratings_disabled",
        "video_error_or_removed",
        "description",
    ]
    
    rows = []
    base_date = datetime(2017, 11, 14)
    
    for i in range(num_records):
        channel_name, cat_id, base_tags = random.choice(channels)
        vid_id = f"{country}_{random.randint(10000, 99999)}_{i:04d}"
        
        # Publish date within last 1 to 14 days
        pub_offset_days = random.randint(1, 14)
        pub_hour = random.randint(0, 23)
        pub_min = random.randint(0, 59)
        pub_sec = random.randint(0, 59)
        
        trend_offset_days = random.randint(pub_offset_days, pub_offset_days + 7)
        trend_dt = base_date + timedelta(days=trend_offset_days)
        pub_dt = trend_dt - timedelta(days=random.randint(1, 10), hours=pub_hour, minutes=pub_min)
        
        # Kaggle format: yy.dd.MM
        trending_date_str = trend_dt.strftime("%y.%d.%m")
        # ISO timestamp: yyyy-MM-dd'T'HH:mm:ss.SSS'Z'
        publish_time_str = pub_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        
        title = random.choice(TITLES)
        if random.random() < 0.2:
            title = f"{title} (Part {random.randint(1, 3)})"
            
        tags_list = base_tags + [f"tag_{random.randint(1, 20)}" for _ in range(random.randint(2, 6))]
        tags_str = "|".join(f'"{t}"' for t in tags_list)
        
        # Realistic power law views
        views = int(random.paretovariate(1.2) * 20000) + 1000
        # Engagement rates
        like_ratio = random.uniform(0.015, 0.08)
        dislike_ratio = random.uniform(0.001, 0.015)
        comment_ratio = random.uniform(0.002, 0.02)
        
        likes = int(views * like_ratio)
        dislikes = int(views * dislike_ratio)
        comments = int(views * comment_ratio)
        
        # Edge cases: disabled comments or ratings
        comments_disabled = "True" if random.random() < 0.03 else "False"
        ratings_disabled = "True" if random.random() < 0.02 else "False"
        video_error = "True" if random.random() < 0.01 else "False"
        
        if comments_disabled == "True":
            comments = 0
        if ratings_disabled == "True":
            likes = 0
            dislikes = 0
            
        thumbnail = f"https://i.ytimg.com/vi/{vid_id}/default.jpg"
        desc = random.choice(DESCRIPTIONS)
        
        row = {
            "video_id": vid_id,
            "trending_date": trending_date_str,
            "title": title,
            "channel_title": channel_name,
            "category_id": cat_id,
            "publish_time": publish_time_str,
            "tags": tags_str,
            "views": views,
            "likes": likes,
            "dislikes": dislikes,
            "comment_count": comments,
            "thumbnail_link": thumbnail,
            "comments_disabled": comments_disabled,
            "ratings_disabled": ratings_disabled,
            "video_error_or_removed": video_error,
            "description": desc,
        }
        rows.append(row)
        
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Generated {len(rows)} sample records for {country} -> {filename}")

if __name__ == "__main__":
    for c in ["US", "IN", "GB", "CA"]:
        generate_country_dataset(c, num_records=200)
    print("All sample country datasets generated successfully in data/raw/!")

