from spark_utils import create_spark_session

def main():
    # Start Spark with a custom app name and master
    spark = create_spark_session(app_name="PySparkOnK8S",
                                 master="k8s://https://kubernetes.default.svc")

    # Example DataFrame operation
    data = [("Alice", 1), ("Bob", 2), ("Cathy", 3), ("Merve", 4)]
    df = spark.createDataFrame(data, ["Name", "Value"])
    df.show()

    spark.stop()

if __name__ == "__main__":
    main()