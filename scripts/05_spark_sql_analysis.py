"""
Step 5: Analysis Using Spark SQL and PySpark DataFrame API.
Performs 8 key analytical queries:
1. Top 10 Trending Videos by Views & Likes
2. Top 10 Channels by Views and Total Engagement
3. Category-level Aggregates (Average Views, Likes, Engagement Rate)
4. Country-level Comparison
5. Engagement Trends Over Time (Daily / Monthly / Yearly)
6. Best Publish Day and Hour for Trending Videos
7. Statistical Correlation Matrix (Views, Likes, Dislikes, Comments)
8. Impact of Tags, Title Length, and Disabled Comments/Ratings
Exports all results to CSV/JSON tables in output/tables/ (and HDFS /youtube/output/).
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.config import (
    CLEAN_DATA_DIR,
    TABLES_DIR,
    USE_HDFS,
    HDFS_CLEAN_DIR,
    HDFS_OUTPUT_DIR,
    SPARK_APP_NAME,
    SPARK_MASTER,
)

def create_spark_session():
    """Initializes SparkSession with Hive/SQL support."""
    from pyspark.sql import SparkSession
    
    spark = (
        SparkSession.builder.appName(f"{SPARK_APP_NAME}_Analysis")
        .master(SPARK_MASTER)
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.driver.memory", "4g")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark

def export_df(df, name: str):
    """Exports a small aggregated PySpark DataFrame to local CSV/JSON."""
    local_csv_path = TABLES_DIR / f"{name}.csv"
    pdf = df.toPandas()
    pdf.to_csv(local_csv_path, index=False)
    print(f"[+] Saved table: {local_csv_path} ({len(pdf)} rows)")
    
    if USE_HDFS:
        hdfs_path = f"{HDFS_OUTPUT_DIR}/{name}"
        df.write.mode("overwrite").option("header", True).csv(hdfs_path)
        print(f"[+] Saved HDFS table: {hdfs_path}")

def run_analysis():
    from pyspark.sql import functions as F
    
    spark = create_spark_session()
    
    if USE_HDFS:
        input_parquet = f"{HDFS_CLEAN_DIR}/youtube_features.parquet"
    else:
        input_parquet = str(CLEAN_DATA_DIR / "youtube_features.parquet")
        
    print(f"[*] Reading feature-engineered dataset from: {input_parquet}")
    df = spark.read.parquet(input_parquet)
    df.createOrReplaceTempView("youtube_features")
    
    print("\n" + "="*70)
    print(" 1. Top 10 Videos by Views & Likes")
    print("="*70)
    query_top_videos = """
        SELECT
            country,
            video_id,
            title,
            channel_title,
            category_title,
            MAX(views) AS max_views,
            MAX(likes) AS max_likes,
            MAX(comment_count) AS max_comments,
            ROUND(MAX(engagement_rate), 4) AS engagement_rate
        FROM youtube_features
        GROUP BY country, video_id, title, channel_title, category_title
        ORDER BY max_views DESC
        LIMIT 10
    """
    top_videos_df = spark.sql(query_top_videos)
    top_videos_df.show(10, truncate=35)
    export_df(top_videos_df, "01_top_10_videos")
    
    print("\n" + "="*70)
    print(" 2. Top Channels by Views and Total Engagement (Global & by Country)")
    print("="*70)
    query_top_channels = """
        SELECT
            'ALL' AS country,
            channel_title,
            COUNT(DISTINCT video_id) AS video_count,
            SUM(views) AS total_views,
            SUM(likes) AS total_likes,
            SUM(comment_count) AS total_comments,
            ROUND(AVG(engagement_rate), 4) AS avg_engagement_rate
        FROM youtube_features
        GROUP BY channel_title
        UNION ALL
        SELECT
            country,
            channel_title,
            COUNT(DISTINCT video_id) AS video_count,
            SUM(views) AS total_views,
            SUM(likes) AS total_likes,
            SUM(comment_count) AS total_comments,
            ROUND(AVG(engagement_rate), 4) AS avg_engagement_rate
        FROM youtube_features
        GROUP BY country, channel_title
        ORDER BY total_views DESC
    """
    top_channels_df = spark.sql(query_top_channels)
    top_channels_df.show(10, truncate=30)
    export_df(top_channels_df, "02_top_10_channels")
    
    print("\n" + "="*70)
    print(" 3. Average Views, Likes, and Engagement by Category (Global & by Country)")
    print("="*70)
    query_category_stats = """
        SELECT
            'ALL' AS country,
            category_title,
            COUNT(video_id) AS video_count,
            ROUND(AVG(views), 0) AS avg_views,
            ROUND(AVG(likes), 0) AS avg_likes,
            ROUND(AVG(dislikes), 0) AS avg_dislikes,
            ROUND(AVG(like_ratio), 4) AS avg_like_ratio,
            ROUND(AVG(engagement_rate), 4) AS avg_engagement_rate
        FROM youtube_features
        GROUP BY category_title
        UNION ALL
        SELECT
            country,
            category_title,
            COUNT(video_id) AS video_count,
            ROUND(AVG(views), 0) AS avg_views,
            ROUND(AVG(likes), 0) AS avg_likes,
            ROUND(AVG(dislikes), 0) AS avg_dislikes,
            ROUND(AVG(like_ratio), 4) AS avg_like_ratio,
            ROUND(AVG(engagement_rate), 4) AS avg_engagement_rate
        FROM youtube_features
        GROUP BY country, category_title
        ORDER BY avg_views DESC
    """
    category_stats_df = spark.sql(query_category_stats)
    category_stats_df.show(15, truncate=30)
    export_df(category_stats_df, "03_category_aggregates")
    
    print("\n" + "="*70)
    print(" 4. Country-Wise Comparison")
    print("="*70)
    query_country_stats = """
        SELECT
            country,
            COUNT(DISTINCT video_id) AS unique_videos,
            ROUND(AVG(views), 0) AS avg_views,
            ROUND(AVG(likes), 0) AS avg_likes,
            ROUND(AVG(comment_count), 0) AS avg_comments,
            ROUND(AVG(engagement_rate), 4) AS avg_engagement_rate,
            ROUND(AVG(days_to_trend), 1) AS avg_days_to_trend
        FROM youtube_features
        GROUP BY country
        ORDER BY avg_views DESC
    """
    country_stats_df = spark.sql(query_country_stats)
    country_stats_df.show(10, truncate=25)
    export_df(country_stats_df, "04_country_comparison")
    
    print("\n" + "="*70)
    print(" 5. Engagement Trends Over Time (Monthly - Global & by Country)")
    print("="*70)
    query_trends = """
        SELECT
            'ALL' AS country,
            publish_year_month,
            COUNT(video_id) AS uploads_count,
            ROUND(AVG(views), 0) AS avg_views,
            ROUND(AVG(likes), 0) AS avg_likes,
            ROUND(AVG(engagement_rate), 4) AS avg_engagement_rate
        FROM youtube_features
        WHERE publish_year_month IS NOT NULL
        GROUP BY publish_year_month
        UNION ALL
        SELECT
            country,
            publish_year_month,
            COUNT(video_id) AS uploads_count,
            ROUND(AVG(views), 0) AS avg_views,
            ROUND(AVG(likes), 0) AS avg_likes,
            ROUND(AVG(engagement_rate), 4) AS avg_engagement_rate
        FROM youtube_features
        WHERE publish_year_month IS NOT NULL
        GROUP BY country, publish_year_month
        ORDER BY publish_year_month ASC
    """
    trends_df = spark.sql(query_trends)
    trends_df.show(12, truncate=25)
    export_df(trends_df, "05_monthly_trends")
    
    print("\n" + "="*70)
    print(" 6. Best Publish Day and Hour for Trending (Global & by Country)")
    print("="*70)
    query_publish_timing = """
        SELECT
            'ALL' AS country,
            publish_weekday,
            publish_hour,
            COUNT(video_id) AS video_count,
            ROUND(AVG(views), 0) AS avg_views,
            ROUND(AVG(engagement_rate), 4) AS avg_engagement_rate
        FROM youtube_features
        WHERE publish_weekday IS NOT NULL AND publish_hour IS NOT NULL
        GROUP BY publish_weekday, publish_hour
        UNION ALL
        SELECT
            country,
            publish_weekday,
            publish_hour,
            COUNT(video_id) AS video_count,
            ROUND(AVG(views), 0) AS avg_views,
            ROUND(AVG(engagement_rate), 4) AS avg_engagement_rate
        FROM youtube_features
        WHERE publish_weekday IS NOT NULL AND publish_hour IS NOT NULL
        GROUP BY country, publish_weekday, publish_hour
        ORDER BY avg_views DESC
    """
    timing_df = spark.sql(query_publish_timing)
    timing_df.show(15, truncate=25)
    export_df(timing_df, "06_publish_timing")
    
    print("\n" + "="*70)
    print(" 7. Correlation Matrix (Views, Likes, Dislikes, Comments)")
    print("="*70)
    metrics = ["views", "likes", "dislikes", "comment_count"]
    correlation_rows = []
    from pyspark.sql.types import StructType, StructField, StringType, DoubleType
    
    for m1 in metrics:
        row = {"metric": m1}
        for m2 in metrics:
            corr_val = df.stat.corr(m1, m2)
            row[m2] = round(corr_val, 4) if corr_val is not None else 0.0
        correlation_rows.append(row)
        
    import pandas as pd
    corr_pdf = pd.DataFrame(correlation_rows)
    print(corr_pdf.to_string(index=False))
    corr_pdf.to_csv(TABLES_DIR / "07_correlation_matrix.csv", index=False)
    print(f"[+] Saved correlation table: {TABLES_DIR / '07_correlation_matrix.csv'}")
    
    print("\n" + "="*70)
    print(" 8. Impact of Tags, Title Length, and Disabled Interactions")
    print("="*70)
    query_metadata_impact = """
        SELECT
            CASE
                WHEN tag_count = 0 THEN '0: No Tags'
                WHEN tag_count BETWEEN 1 AND 5 THEN '1: Low (1-5)'
                WHEN tag_count BETWEEN 6 AND 15 THEN '2: Medium (6-15)'
                ELSE '3: High (16+)'
            END AS tag_bucket,
            CASE
                WHEN title_length < 30 THEN 'Short (<30)'
                WHEN title_length BETWEEN 30 AND 60 THEN 'Medium (30-60)'
                ELSE 'Long (>60)'
            END AS title_length_bucket,
            comments_disabled,
            ratings_disabled,
            COUNT(video_id) AS count,
            ROUND(AVG(views), 0) AS avg_views,
            ROUND(AVG(engagement_rate), 4) AS avg_engagement_rate
        FROM youtube_features
        GROUP BY 1, 2, comments_disabled, ratings_disabled
        ORDER BY avg_views DESC
    """
    metadata_df = spark.sql(query_metadata_impact)
    metadata_df.show(15, truncate=30)
    export_df(metadata_df, "08_metadata_impact")
    
    print("\n[+] All 8 analytical steps successfully processed and tables exported!")
    spark.stop()

if __name__ == "__main__":
    run_analysis()

