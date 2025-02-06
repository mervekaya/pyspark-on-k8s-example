import json
import os
from pyspark.sql import SparkSession

def create_spark_session(app_name="MyPySparkApp", master="local[*]", config_file="configs/spark_config.json"):
    """
    Reads Spark configurations from a JSON file and initializes a SparkSession with log level from config.

    :param app_name: Name of the Spark application.
    :param master: Spark master URL (e.g., "local[*]", "yarn", "k8s://...").
    :param config_file: Path to the JSON configuration file.
    :return: Initialized SparkSession.
    """
    # Define a different config path for the Kubernetes environment
    K8S_CONFIG_PATH = "/app/configs/spark_config.json"
    config_path = K8S_CONFIG_PATH if os.path.exists(K8S_CONFIG_PATH) else config_file

    # Read the JSON configuration file
    try:
        with open(config_path, "r") as f:
            spark_configs = json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Warning: {config_path} not found, using default settings.")
        spark_configs = {}

    # Create a SparkSession with the given application name and master URL
    spark = SparkSession.builder.appName(app_name).master(master)

    # Apply configurations from the JSON file to Spark
    for key, value in spark_configs.items():
        spark = spark.config(key, value)

    spark = spark.getOrCreate()

    # Set log level if specified in the config
    log_level = spark.conf.get("spark.log.level", "INFO")
    spark.sparkContext.setLogLevel(log_level)

    # Print the applied Spark configurations
    print(f"✅ Spark Initialized (App Name: {app_name}, Master: {master}). Applied Configurations:")
    for key, value in spark_configs.items():
        print(f"{key}: {spark.conf.get(key, 'Not Set')}")

    print(f"🔧 Log level set to: {log_level}")

    return spark
