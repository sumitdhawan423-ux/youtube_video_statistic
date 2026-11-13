"""
Step 3: PySpark Ingestion, Data Cleaning, Category Mapping, and Parquet Export.
- Reads multi-country CSVs with multiline and quote escaping.
- Extracts 'country' code from file path.
- Deduplicates on (video_id, trending_date), handles nulls, casts types.
- Parses 'trending_date' (yy.dd.MM) and 'publish_time' (ISO 8601).
- Maps category_id to human-readable category names from JSON.
- Writes cleaned dataset to Partitioned Parquet (local or HDFS).
"""

import os
import sys
import json
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.config import (
    RAW_DATA_DIR,
    CLEAN_DATA_DIR,
    USE_HDFS,
    HDFS_RAW_DIR,
    HDFS_CLEAN_DIR,
    SPARK_APP_NAME,
    SPARK_MASTER,
)

def create_spark_session():
    """Builds an optimized SparkSession for local or cluster execution."""
    from pyspark.sql import SparkSession
    
    builder = (
        SparkSession.builder.appName(f"{SPARK_APP_NAME}_Ingest_Clean")
        .master(SPARK_MASTER)
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.driver.memory", "4g")
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
    )
    
    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    print(f"[+] SparkSession initialized: Spark version {spark.version}")
    return spark

def load_category_mappings(spark):
    """
    Parses all category JSON files in data/raw to create a unified DataFrame
    mapping (country, category_id) -> category_title.
    """
    from pyspark.sql.types import StructType, StructField, StringType, IntegerType
    
    print("[*] Loading category ID JSON mappings...")
    json_files = list(RAW_DATA_DIR.glob("*category_id.json"))
    category_records = []
    
    for jf in json_files:
        country_code = jf.name.split("_")[0].upper()
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data.get("items", []):
                    cat_id = int(item.get("id"))
                    title = item.get("snippet", {}).get("title", "Unknown")
                    category_records.append((country_code, cat_id, title))
        except Exception as e:
            print(f"[-] Warning: Failed to parse {jf.name}: {e}")
            
    # Default fallback mapping
    default_categories = [
        (1, "Film & Animation"), (2, "Autos & Vehicles"), (10, "Music"),
        (15, "Pets & Animals"), (17, "Sports"), (18, "Short Movies"),
        (19, "Travel & Events"), (20, "Gaming"), (21, "Videoblogging"),
        (22, "People & Blogs"), (23, "Comedy"), (24, "Entertainment"),
        (25, "News & Politics"), (26, "Howto & Style"), (27, "Education"),
        (28, "Science & Technology"), (29, "Nonprofits & Activism"),
        (30, "Movies"), (43, "Shows"), (44, "Trailers")
    ]
    for cid, title in default_categories:
        category_records.append(("DEFAULT", cid, title))
        
    schema = StructType([
        StructField("cat_country", StringType(), False),
        StructField("cat_id", IntegerType(), False),
        StructField("category_title", StringType(), False),
    ])
    
    cat_df = spark.createDataFrame(category_records, schema).distinct()
    print(f"[+] Loaded {cat_df.count()} category lookup entries.")
    return cat_df

def run_ingest_and_clean():
    from pyspark.sql import functions as F
    from pyspark.sql.types import (
        IntegerType,
        LongType,
        BooleanType,
        StringType,
        TimestampType,
    )
    
    spark = create_spark_session()
    
    # 1. Resolve Input & Output Paths
    if USE_HDFS:
        input_pattern = f"{HDFS_RAW_DIR}/*videos.csv"
        output_path = f"{HDFS_CLEAN_DIR}/youtube_cleaned.parquet"
        print(f"[*] Reading raw datasets from HDFS: {input_pattern}")
    else:
        input_pattern = str(RAW_DATA_DIR / "*videos.csv")
        output_path = str(CLEAN_DATA_DIR / "youtube_cleaned.parquet")
        print(f"[*] Reading raw datasets from local path: {input_pattern}")
        
    # 2. PySpark Multiline CSV Ingestion
    raw_df = (
        spark.read.option("header", True)
        .option("multiLine", True)
        .option("escape", '"')
        .option("mode", "PERMISSIVE")
        .csv(input_pattern, inferSchema=True)
    )
    
    initial_count = raw_df.count()
    print(f"[+] Raw records ingested across all country CSVs: {initial_count:,}")
    
    # 3. Extract Country Code from file name
    # Matches patterns like 'USvideos.csv' or 'IN_api_videos.csv'
    df = raw_df.withColumn(
        "country",
        F.upper(
            F.coalesce(
                F.regexp_extract(F.input_file_name(), r"([A-Za-z]{2})(?:videos|_api)", 1),
                F.lit("US")
            )
        )
    )
    
    # 4. Data Cleaning & Type Casting
    print("[*] Deduplicating and casting types...")
    # Drop duplicates on (video_id, trending_date)
    df = df.dropDuplicates(["video_id", "trending_date"])
    
    # Filter null or corrupted video_id
    df = df.filter(F.col("video_id").isNotNull() & (F.length(F.trim(F.col("video_id"))) > 0))
    
    # Numeric column casting
    for col_name in ["views", "likes", "dislikes", "comment_count", "category_id"]:
        df = df.withColumn(col_name, F.col(col_name).cast(LongType()))
        
    # Boolean casting
    for bool_col in ["comments_disabled", "ratings_disabled", "video_error_or_removed"]:
        if bool_col in df.columns:
            df = df.withColumn(bool_col, F.col(bool_col).cast(BooleanType()))
        else:
            df = df.withColumn(bool_col, F.lit(False))
            
    # Handle nulls in numerics
    df = df.fillna({
        "views": 0,
        "likes": 0,
        "dislikes": 0,
        "comment_count": 0,
        "category_id": 0,
        "comments_disabled": False,
        "ratings_disabled": False,
        "video_error_or_removed": False,
    })
    
    # Filter non-positive views (corrupt records)
    df = df.filter(F.col("views") >= 0)
    
    # 5. Date Parsing
    # trending_date in Kaggle format is yy.dd.MM (e.g., 17.14.11 -> 2017-11-14)
    # Also parse publish_time timestamp (e.g. 2017-11-13T17:13:01.000Z)
    df = df.withColumn(
        "trending_date_parsed",
        F.to_date(F.col("trending_date"), "yy.dd.MM")
    )
    # Fallback for yyyy-MM-dd if already standard
    df = df.withColumn(
        "trending_date_parsed",
        F.coalesce(F.col("trending_date_parsed"), F.to_date(F.col("trending_date"), "yyyy-MM-dd"))
    )
    
    df = df.withColumn(
        "publish_timestamp",
        F.coalesce(
            F.to_timestamp(F.col("publish_time"), "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"),
            F.to_timestamp(F.col("publish_time"), "yyyy-MM-dd'T'HH:mm:ss'Z'"),
            F.to_timestamp(F.col("publish_time"))
        )
    )
    df = df.withColumn("publish_date", F.to_date(F.col("publish_timestamp")))
    
    # 6. Category Mapping Join
    cat_df = load_category_mappings(spark)
    
    # First attempt country-specific match
    df = df.join(
        cat_df.select(
            F.col("cat_country"),
            F.col("cat_id"),
            F.col("category_title").alias("matched_cat_title")
        ),
        (df.country == F.col("cat_country")) & (df.category_id == F.col("cat_id")),
        "left"
    ).drop("cat_country", "cat_id")
    
    # Second attempt default fallback match
    default_cat_df = cat_df.filter(F.col("cat_country") == "DEFAULT").select(
        F.col("cat_id").alias("def_id"),
        F.col("category_title").alias("default_cat_title")
    )
    
    df = df.join(
        default_cat_df,
        df.category_id == F.col("def_id"),
        "left"
    ).drop("def_id")
    
    df = df.withColumn(
        "category_title",
        F.coalesce(
            F.col("matched_cat_title"),
            F.col("default_cat_title"),
            F.lit("Unknown / Other")
        )
    ).drop("matched_cat_title", "default_cat_title")
    
    cleaned_count = df.count()
    print(f"[+] Records retained after cleaning & deduplication: {cleaned_count:,} (Removed {initial_count - cleaned_count:,})")
    
    # 7. Write Cleaned Data to Partitioned Parquet
    print(f"[*] Writing cleaned dataset to Parquet partitioned by 'country': {output_path}...")
    (
        df.write.mode("overwrite")
        .partitionBy("country")
        .parquet(output_path)
    )
    
    print("[+] Successfully written partitioned Parquet dataset!")
    print("\n--- Cleaned Data Sample Schema & Records ---")
    df.printSchema()
    df.select(
        "country", "video_id", "title", "channel_title", "category_title",
        "trending_date_parsed", "publish_date", "views", "likes"
    ).show(5, truncate=30)
    
    spark.stop()
    return output_path

if __name__ == "__main__":
    run_ingest_and_clean()

