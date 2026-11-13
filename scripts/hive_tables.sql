-- ============================================================================
-- Apache Hive DDL & HiveQL Exploration Script
-- Defines external tables over HDFS raw CSV, cleaned Parquet, and analytical marts.
-- ============================================================================

CREATE DATABASE IF NOT EXISTS youtube_db;
USE youtube_db;

-- ----------------------------------------------------------------------------
-- 1. External Raw CSV Table (Direct query on HDFS raw files)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS raw_youtube_videos;
CREATE EXTERNAL TABLE IF NOT EXISTS raw_youtube_videos (
    video_id STRING,
    trending_date STRING,
    title STRING,
    channel_title STRING,
    category_id INT,
    publish_time STRING,
    tags STRING,
    views BIGINT,
    likes BIGINT,
    dislikes BIGINT,
    comment_count BIGINT,
    thumbnail_link STRING,
    comments_disabled BOOLEAN,
    ratings_disabled BOOLEAN,
    video_error_or_removed BOOLEAN,
    description STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
   "separatorChar" = ",",
   "quoteChar"     = "\"",
   "escapeChar"    = "\\"
)
STORED AS TEXTFILE
LOCATION '/youtube/raw'
TBLPROPERTIES ("skip.header.line.count"="1");

-- ----------------------------------------------------------------------------
-- 2. Cleaned & Enriched Feature Parquet Table (Partitioned by Country)
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS youtube_features;
CREATE EXTERNAL TABLE IF NOT EXISTS youtube_features (
    video_id STRING,
    trending_date_parsed DATE,
    publish_timestamp TIMESTAMP,
    publish_date DATE,
    title STRING,
    channel_title STRING,
    category_id INT,
    category_title STRING,
    views BIGINT,
    likes BIGINT,
    dislikes BIGINT,
    comment_count BIGINT,
    like_ratio DOUBLE,
    dislike_ratio DOUBLE,
    comment_ratio DOUBLE,
    engagement_rate DOUBLE,
    days_to_trend INT,
    publish_hour INT,
    publish_weekday STRING,
    publish_year_month STRING,
    tag_count INT,
    title_length INT,
    comments_disabled BOOLEAN,
    ratings_disabled BOOLEAN
)
PARTITIONED BY (country STRING)
STORED AS PARQUET
LOCATION '/youtube/clean/youtube_features.parquet';

-- Recover partitions after table creation
MSCK REPAIR TABLE youtube_features;

-- ----------------------------------------------------------------------------
-- 3. Analytical Hive Views / Tables
-- ----------------------------------------------------------------------------

-- Top 10 Trending Videos Across All Regions
CREATE OR REPLACE VIEW v_top_10_videos AS
SELECT
    country,
    video_id,
    title,
    channel_title,
    category_title,
    MAX(views) AS peak_views,
    MAX(likes) AS peak_likes,
    ROUND(MAX(engagement_rate), 4) AS engagement_rate
FROM youtube_features
GROUP BY country, video_id, title, channel_title, category_title
ORDER BY peak_views DESC
LIMIT 10;

-- Category Performance Summary
CREATE OR REPLACE VIEW v_category_summary AS
SELECT
    category_title,
    COUNT(DISTINCT video_id) AS total_videos,
    ROUND(AVG(views), 0) AS avg_views,
    ROUND(AVG(likes), 0) AS avg_likes,
    ROUND(AVG(engagement_rate), 4) AS avg_engagement_rate
FROM youtube_features
GROUP BY category_title
ORDER BY avg_views DESC;

-- Country Velocity Comparison
CREATE OR REPLACE VIEW v_country_velocity AS
SELECT
    country,
    COUNT(DISTINCT video_id) AS video_count,
    ROUND(AVG(views), 0) AS avg_views,
    ROUND(AVG(days_to_trend), 2) AS avg_days_to_trend,
    ROUND(AVG(engagement_rate), 4) AS avg_engagement
FROM youtube_features
GROUP BY country
ORDER BY avg_views DESC;

-- Sample queries to verify
SELECT * FROM v_top_10_videos;
SELECT * FROM v_category_summary LIMIT 10;
SELECT * FROM v_country_velocity;

