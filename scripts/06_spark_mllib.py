"""
Step 6: Machine Learning with Spark MLlib.
- Regression: Predict video views using RandomForestRegressor & LinearRegression.
  Evaluates RMSE, R2, and MAE via RegressionEvaluator.
- Clustering: K-Means clustering on video engagement dimensions
  (views, likes, comments, engagement_rate) with StandardScaler.
  Reports Silhouette Score and cluster centroid characteristics.
Exports model performance reports and cluster assignments to output/tables/.
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
    RANDOM_SEED,
    RF_NUM_TREES,
    RF_MAX_DEPTH,
    KMEANS_K,
)

def create_spark_session():
    """Initializes SparkSession for MLlib pipelines."""
    from pyspark.sql import SparkSession
    
    spark = (
        SparkSession.builder.appName(f"{SPARK_APP_NAME}_MLlib")
        .master(SPARK_MASTER)
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.driver.memory", "4g")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark

def run_regression_pipeline(df):
    """
    Builds and evaluates Regression models (Random Forest and Linear Regression)
    to predict video views based on engagement and metadata features.
    """
    from pyspark.ml import Pipeline
    from pyspark.ml.feature import StringIndexer, VectorAssembler, StandardScaler
    from pyspark.ml.regression import RandomForestRegressor, LinearRegression
    from pyspark.ml.evaluation import RegressionEvaluator
    from pyspark.sql import functions as F
    import pandas as pd
    
    print("\n" + "="*70)
    print(" MLlib Task 1: View Prediction via Regression")
    print("="*70)
    
    # Filter valid rows for regression
    ml_df = df.filter(
        F.col("views").isNotNull() &
        F.col("likes").isNotNull() &
        F.col("comment_count").isNotNull()
    )
    
    # 1. Feature Indexing for Categoricals
    cat_indexer = StringIndexer(
        inputCol="category_title",
        outputCol="cat_idx",
        handleInvalid="keep"
    )
    country_indexer = StringIndexer(
        inputCol="country",
        outputCol="country_idx",
        handleInvalid="keep"
    )
    weekday_indexer = StringIndexer(
        inputCol="publish_weekday",
        outputCol="weekday_idx",
        handleInvalid="keep"
    )
    
    # 2. Vector Assembler
    feature_cols = [
        "likes",
        "comment_count",
        "days_to_trend",
        "title_length",
        "tag_count",
        "cat_idx",
        "country_idx",
        "weekday_idx",
    ]
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features", handleInvalid="skip")
    
    # 3. Train/Test Split (80/20)
    train_data, test_data = ml_df.randomSplit([0.8, 0.2], seed=RANDOM_SEED)
    print(f"[*] Train set size: {train_data.count():,} | Test set size: {test_data.count():,}")
    
    # 4. Model 1: Random Forest Regressor
    rf = RandomForestRegressor(
        featuresCol="features",
        labelCol="views",
        numTrees=RF_NUM_TREES,
        maxDepth=RF_MAX_DEPTH,
        seed=RANDOM_SEED
    )
    
    # 5. Model 2: Linear Regression
    lr = LinearRegression(
        featuresCol="features",
        labelCol="views",
        maxIter=20,
        regParam=0.1
    )
    
    # Pipelines
    rf_pipeline = Pipeline(stages=[cat_indexer, country_indexer, weekday_indexer, assembler, rf])
    lr_pipeline = Pipeline(stages=[cat_indexer, country_indexer, weekday_indexer, assembler, lr])
    
    # Fit Models
    print("[*] Training Random Forest Regressor...")
    rf_model = rf_pipeline.fit(train_data)
    rf_preds = rf_model.transform(test_data)
    
    print("[*] Training Linear Regression...")
    lr_model = lr_pipeline.fit(train_data)
    lr_preds = lr_model.transform(test_data)
    
    # Evaluators
    rmse_eval = RegressionEvaluator(labelCol="views", predictionCol="prediction", metricName="rmse")
    r2_eval = RegressionEvaluator(labelCol="views", predictionCol="prediction", metricName="r2")
    mae_eval = RegressionEvaluator(labelCol="views", predictionCol="prediction", metricName="mae")
    
    rf_rmse = rmse_eval.evaluate(rf_preds)
    rf_r2 = r2_eval.evaluate(rf_preds)
    rf_mae = mae_eval.evaluate(rf_preds)
    
    lr_rmse = rmse_eval.evaluate(lr_preds)
    lr_r2 = r2_eval.evaluate(lr_preds)
    lr_mae = mae_eval.evaluate(lr_preds)
    
    results = [
        {"Model": "Random Forest Regressor", "RMSE": round(rf_rmse, 2), "R2": round(rf_r2, 4), "MAE": round(rf_mae, 2)},
        {"Model": "Linear Regression", "RMSE": round(lr_rmse, 2), "R2": round(lr_r2, 4), "MAE": round(lr_mae, 2)},
    ]
    results_pdf = pd.DataFrame(results)
    print("\n--- Regression Model Evaluation Metrics ---")
    print(results_pdf.to_string(index=False))
    results_pdf.to_csv(TABLES_DIR / "mllib_regression_metrics.csv", index=False)
    
    # Feature Importances from Random Forest
    rf_stage = rf_model.stages[-1]
    importances = rf_stage.featureImportances.toArray()
    feat_imp = pd.DataFrame({
        "Feature": feature_cols,
        "Importance": [round(val, 4) for val in importances]
    }).sort_values(by="Importance", ascending=False)
    
    print("\n--- Feature Importances (Random Forest) ---")
    print(feat_imp.to_string(index=False))
    feat_imp.to_csv(TABLES_DIR / "mllib_feature_importances.csv", index=False)
    
    return results_pdf

def run_clustering_pipeline(df):
    """
    Performs K-Means clustering on video engagement metrics
    to discover behavioral clusters of trending videos.
    """
    from pyspark.ml.feature import VectorAssembler, StandardScaler
    from pyspark.ml.clustering import KMeans
    from pyspark.ml.evaluation import ClusteringEvaluator
    from pyspark.sql import functions as F
    import pandas as pd
    
    print("\n" + "="*70)
    print(" MLlib Task 2: Engagement Behavior Clustering via K-Means")
    print("="*70)
    
    cluster_features = ["views", "likes", "comment_count", "engagement_rate"]
    assembler = VectorAssembler(inputCols=cluster_features, outputCol="raw_features", handleInvalid="skip")
    scaler = StandardScaler(inputCol="raw_features", outputCol="scaled_features", withStd=True, withMean=True)
    
    prepared_df = assembler.transform(df)
    scaler_model = scaler.fit(prepared_df)
    scaled_df = scaler_model.transform(prepared_df)
    
    kmeans = KMeans(featuresCol="scaled_features", predictionCol="cluster", k=KMEANS_K, seed=RANDOM_SEED)
    model = kmeans.fit(scaled_df)
    clustered_df = model.transform(scaled_df)
    
    # Evaluate Silhouette
    evaluator = ClusteringEvaluator(featuresCol="scaled_features", predictionCol="cluster", metricName="silhouette")
    silhouette = evaluator.evaluate(clustered_df)
    print(f"[+] K-Means (k={KMEANS_K}) Silhouette Score: {silhouette:.4f}")
    
    # Compute Cluster Summaries
    cluster_summary = clustered_df.groupBy("cluster").agg(
        F.count("video_id").alias("video_count"),
        F.round(F.avg("views"), 0).alias("avg_views"),
        F.round(F.avg("likes"), 0).alias("avg_likes"),
        F.round(F.avg("comment_count"), 0).alias("avg_comments"),
        F.round(F.avg("engagement_rate"), 4).alias("avg_engagement_rate")
    ).orderBy("cluster")
    
    summary_pdf = cluster_summary.toPandas()
    
    # Assign intuitive cluster labels based on avg_views and avg_engagement
    labels = []
    for _, row in summary_pdf.iterrows():
        v = row["avg_views"]
        eng = row["avg_engagement_rate"]
        if v > 1_000_000:
            labels.append("Mega Viral Blockbuster")
        elif eng > 0.05:
            labels.append("High Community Engagement")
        elif v > 200_000:
            labels.append("Consistent Mid-Tier Performer")
        else:
            labels.append("Emerging / Niche Trending")
    summary_pdf["cluster_label"] = labels
    
    print("\n--- K-Means Engagement Cluster Summary ---")
    print(summary_pdf.to_string(index=False))
    summary_pdf.to_csv(TABLES_DIR / "mllib_kmeans_clusters.csv", index=False)
    
    # Save a sample of clustered videos for plotting
    sample_clustered = clustered_df.select(
        "video_id", "title", "channel_title", "country", "category_title",
        "views", "likes", "comment_count", "engagement_rate", "cluster"
    ).limit(500).toPandas()
    sample_clustered.to_csv(TABLES_DIR / "mllib_clustered_samples.csv", index=False)
    print(f"[+] Saved clustered sample points to: {TABLES_DIR / 'mllib_clustered_samples.csv'}")

def run_mllib():
    spark = create_spark_session()
    
    if USE_HDFS:
        input_parquet = f"{HDFS_CLEAN_DIR}/youtube_features.parquet"
    else:
        input_parquet = str(CLEAN_DATA_DIR / "youtube_features.parquet")
        
    print(f"[*] Reading dataset for MLlib from: {input_parquet}")
    df = spark.read.parquet(input_parquet)
    
    run_regression_pipeline(df)
    run_clustering_pipeline(df)
    
    print("\n[+] MLlib Regression and Clustering pipelines successfully executed!")
    spark.stop()

if __name__ == "__main__":
    run_mllib()

