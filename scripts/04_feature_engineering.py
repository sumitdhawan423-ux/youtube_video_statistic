"""
Step 4: PySpark Feature Engineering.
Derives critical behavioral, temporal, and text-based features:
- like_ratio, dislike_ratio, engagement_rate
- days_to_trend, publish_hour, publish_weekday, publish_year_month
- tag_count, title_length, title_word_count, is_viral
Exports the enriched dataset to Parquet for Spark SQL analytics & MLlib.
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.config import (
    CLEAN_DATA_DIR,
    USE_HDFS,
    HDFS_CLEAN_DIR,
    SPARK_APP_NAME,
    SPARK_MASTER,
)

def create_spark_session():
    """Initializes SparkSession for feature engineering."""
    from pyspark.sql import SparkSession
    
    spark = (
        SparkSession.builder.appName(f"{SPARK_APP_NAME}_Feature_Engineering")
        .master(SPARK_MASTER)
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.driver.memory", "4g")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark

def run_feature_engineering():
    from pyspark.sql import functions as F
    from pyspark.sql.types import DoubleType, IntegerType
    
    spark = create_spark_session()
    
    # 1. Resolve paths
    if USE_HDFS:
        input_parquet = f"{HDFS_CLEAN_DIR}/youtube_cleaned.parquet"
        output_parquet = f"{HDFS_CLEAN_DIR}/youtube_features.parquet"
    else:
        input_parquet = str(CLEAN_DATA_DIR / "youtube_cleaned.parquet")
        output_parquet = str(CLEAN_DATA_DIR / "youtube_features.parquet")
        
    print(f"[*] Reading cleaned Parquet from: {input_parquet}")
    df = spark.read.parquet(input_parquet)
    
    total_records = df.count()
    print(f"[+] Loaded {total_records:,} cleaned records for feature engineering.")
    
    # 2. Ratio & Engagement Features
    # Protect against divide-by-zero with when / otherwise
    safe_views = F.when(F.col("views") > 0, F.col("views")).otherwise(F.lit(1.0))
    
    df = df.withColumn(
        "like_ratio",
        F.round(F.col("likes") / safe_views, 6)
    )
    df = df.withColumn(
        "dislike_ratio",
        F.round(F.col("dislikes") / safe_views, 6)
    )
    df = df.withColumn(
        "comment_ratio",
        F.round(F.col("comment_count") / safe_views, 6)
    )
    df = df.withColumn(
        "engagement_rate",
        F.round((F.col("likes") + F.col("dislikes") + F.col("comment_count")) / safe_views, 6)
    )
    
    # 3. Temporal & Velocity Features
    # Days from publish to trending appearance
    df = df.withColumn(
        "days_to_trend",
        F.when(
            F.col("trending_date_parsed").isNotNull() & F.col("publish_date").isNotNull(),
            F.greatest(F.lit(0), F.datediff(F.col("trending_date_parsed"), F.col("publish_date")))
        ).otherwise(F.lit(0))
    )
    
    df = df.withColumn("publish_hour", F.hour(F.col("publish_timestamp")))
    df = df.withColumn("publish_weekday", F.date_format(F.col("publish_timestamp"), "E"))
    df = df.withColumn("publish_day_of_week", F.dayofweek(F.col("publish_timestamp")))
    df = df.withColumn("publish_year_month", F.date_format(F.col("publish_timestamp"), "yyyy-MM"))
    
    # 4. Text & Metadata Metrics
    df = df.withColumn("title_length", F.length(F.coalesce(F.col("title"), F.lit(""))))
    df = df.withColumn(
        "title_word_count",
        F.size(F.split(F.trim(F.coalesce(F.col("title"), F.lit(""))), r"\s+"))
    )
    
    # Tag count extraction (tags are pipe-separated e.g. "a"|"b"|"c")
    df = df.withColumn(
        "tag_count",
        F.when(
            (F.col("tags") == "[none]") | F.col("tags").isNull() | (F.length(F.trim(F.col("tags"))) == 0),
            F.lit(0)
        ).otherwise(
            F.size(F.split(F.col("tags"), r"\|"))
        )
    )
    
    # Description length
    df = df.withColumn("description_length", F.length(F.coalesce(F.col("description"), F.lit(""))))
    
    # Viral threshold indicator (1 if >= 1M views, else 0)
    df = df.withColumn("is_viral", F.when(F.col("views") >= 1_000_000, 1).otherwise(0))
    
    # 5. Export Enriched Feature Parquet
    print(f"[*] Exporting feature-engineered Parquet to: {output_parquet}...")
    (
        df.write.mode("overwrite")
        .partitionBy("country")
        .parquet(output_parquet)
    )
    
    print("[+] Feature engineering complete! Saved enriched Parquet.")
    print("\n--- Summary of Engineered Features ---")
    df.select(
        "title", "views", "like_ratio", "engagement_rate",
        "days_to_trend", "publish_hour", "publish_weekday", "tag_count", "title_length"
    ).show(5, truncate=30)
    
    spark.stop()
    return output_parquet

if __name__ == "__main__":
    run_feature_engineering()

