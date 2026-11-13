"""
Step 1 (Optional): YouTube Data API v3 Ingestion.
Pulls fresh, live trending video statistics using Google API client library,
reads API key from .env, and saves formatted CSV matching Kaggle schema.
"""

import os
import sys
import csv
from datetime import datetime
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load .env variables if python-dotenv is present
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")

from config.config import RAW_DATA_DIR, YOUTUBE_API_KEY

def get_youtube_service(api_key: str):
    """Initializes Google API client service for YouTube Data API v3."""
    try:
        from googleapiclient.discovery import build
        service = build("youtube", "v3", developerKey=api_key)
        return service
    except ImportError:
        print("[-] google-api-python-client is not installed. Install via: pip install google-api-python-client")
        return None
    except Exception as e:
        print(f"[-] Failed to initialize YouTube API client: {e}")
        return None

def fetch_most_popular_videos(service, region_code: str = "US", max_results: int = 50):
    """Fetches popular videos for a given country code using videos.list."""
    print(f"[*] Querying YouTube Data API v3 for region: {region_code} (max: {max_results})...")
    try:
        request = service.videos().list(
            part="snippet,contentDetails,statistics",
            chart="mostPopular",
            regionCode=region_code,
            maxResults=min(max_results, 50)
        )
        response = request.execute()
        items = response.get("items", [])
        print(f"[+] Retrieved {len(items)} trending videos for region '{region_code}'.")
        return items
    except Exception as e:
        print(f"[-] Error calling YouTube API: {e}")
        return []

def format_video_item_to_row(item: dict) -> dict:
    """Transforms YouTube API JSON response item into Kaggle CSV schema format."""
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    
    video_id = item.get("id", "")
    now = datetime.utcnow()
    # Kaggle format: yy.dd.MM
    trending_date = now.strftime("%y.%d.%m")
    
    title = snippet.get("title", "")
    channel_title = snippet.get("channelTitle", "")
    category_id = snippet.get("categoryId", "0")
    publish_time = snippet.get("publishedAt", "")
    
    tags_list = snippet.get("tags", [])
    if tags_list:
        tags_str = "|".join(f'"{t}"' for t in tags_list)
    else:
        tags_str = "[none]"
        
    views = int(stats.get("viewCount", 0))
    likes = int(stats.get("likeCount", 0))
    # Note: YouTube API deprecated public dislikeCount in late 2021, defaulted to 0
    dislikes = int(stats.get("dislikeCount", 0))
    comment_count = int(stats.get("commentCount", 0))
    
    thumbnails = snippet.get("thumbnails", {})
    thumbnail_link = thumbnails.get("default", {}).get("url", "")
    
    comments_disabled = "False" if "commentCount" in stats else "True"
    ratings_disabled = "False" if "likeCount" in stats else "True"
    
    description = snippet.get("description", "")
    
    return {
        "video_id": video_id,
        "trending_date": trending_date,
        "title": title,
        "channel_title": channel_title,
        "category_id": category_id,
        "publish_time": publish_time,
        "tags": tags_str,
        "views": views,
        "likes": likes,
        "dislikes": dislikes,
        "comment_count": comment_count,
        "thumbnail_link": thumbnail_link,
        "comments_disabled": comments_disabled,
        "ratings_disabled": ratings_disabled,
        "video_error_or_removed": "False",
        "description": description,
    }

def save_to_csv(rows: list, output_filepath: Path):
    """Saves records to CSV matching Kaggle quoting and column standard."""
    if not rows:
        print("[-] No rows to save.")
        return
        
    fieldnames = list(rows[0].keys())
    with open(output_filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)
    print(f"[+] Saved {len(rows)} records to: {output_filepath}")

def main():
    print("=" * 60)
    print("YouTube Video Statistics - Step 1: Live API Data Ingestion")
    print("=" * 60)
    
    api_key = os.getenv("YOUTUBE_API_KEY", YOUTUBE_API_KEY)
    
    if not api_key or api_key == "your_youtube_api_key_here":
        print("[!] No valid YOUTUBE_API_KEY found in .env or environment.")
        print("    To fetch live data, obtain a key from Google Cloud Console:")
        print("    https://console.cloud.google.com/apis/library/youtube.googleapis.com")
        print("    Then add 'YOUTUBE_API_KEY=AIzaSy...' to your .env file.")
        print("[*] Skipping live API extraction and proceeding with existing raw data.")
        return
        
    service = get_youtube_service(api_key)
    if not service:
        return
        
    for region in ["US", "IN", "GB"]:
        items = fetch_most_popular_videos(service, region_code=region, max_results=50)
        if items:
            rows = [format_video_item_to_row(item) for item in items]
            out_path = RAW_DATA_DIR / f"{region}_api_videos.csv"
            save_to_csv(rows, out_path)

if __name__ == "__main__":
    main()

