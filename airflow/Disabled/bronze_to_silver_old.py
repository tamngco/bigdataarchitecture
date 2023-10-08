import logging
import os
from datetime import datetime
from pyspark import SparkContext
from pyspark.sql import SparkSession
import pyspark.sql.functions as sf
from pyspark.sql.functions import when
from pyspark.sql.types import *


def load_config(spark_context: SparkContext):
  print("START CONNECTING")
  spark_context._jsc.hadoopConfiguration().set("fs.s3a.access.key", os.getenv("AWS_ACCESS_KEY_ID", minio_access_key))
  spark_context._jsc.hadoopConfiguration().set("fs.s3a.secret.key", os.getenv("AWS_SECRET_ACCESS_KEY", minio_secret_key))
  spark_context._jsc.hadoopConfiguration().set("fs.s3a.endpoint", os.getenv("ENDPOINT", minio_endpoint))
  spark_context._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")
  spark_context._jsc.hadoopConfiguration().set("fs.s3a.attempts.maximum", "1")
  spark_context._jsc.hadoopConfiguration().set("fs.s3a.connection.establish.timeout", "5000")
  spark_context._jsc.hadoopConfiguration().set("fs.s3a.connection.timeout", "10000")
  print("CONNECTED")

def add_missing_column(data):
    data = data.withColumn("datetime_created_at", str2date_spark_udf(sf.col("created_at")))
    data = data.withColumn("suggested_deli_supplier", 
                    sf.when (sf.col("final_deli_supplier").isNotNull(), sf.col("final_deli_supplier")).otherwise(sf.col("suggested_deli_supplier")))

    data = data.withColumn("dow_created_time", sf.date_format(sf.col("datetime_created_at"), "EEEE"))

    data = data.withColumn("dow_created_time", 
                   when(sf.date_format(sf.col("datetime_created_at"), "E") == "Mon", 0)
                   .when(sf.date_format(sf.col("datetime_created_at"), "E") == "Tue", 1)
                   .when(sf.date_format(sf.col("datetime_created_at"), "E") == "Wed", 2)
                   .when(sf.date_format(sf.col("datetime_created_at"), "E") == "Thu", 3)
                   .when(sf.date_format(sf.col("datetime_created_at"), "E") == "Fri", 4)
                   .when(sf.date_format(sf.col("datetime_created_at"), "E") == "Sat", 5)
                   .when(sf.date_format(sf.col("datetime_created_at"), "E") == "Sun", 6)
                   .otherwise(None))
    data = data.withColumn("hour_created_time", sf.hour(sf.col("datetime_created_at")))
    return data

def preprocess_data(df):
    # Calculate today's datetime
    today_str = df.agg({"created_at": "max"}).collect()[0][0]
    today = datetime.strptime(today_str, "%Y-%m-%d %H:%M:%S.0")
    today = datetime(today.year, today.month, today.day, 0, 0, 0)
    # df = df.withColumn("created_at", sf.unix_timestamp(sf.col("created_at")))
    # Calculate day_diff_today and time_weight
    df = df.withColumn("day_diff_today", sf.lit(1))
    df = df.withColumn("time_weight", sf.lit(0))
    
    # Fill missing values in "destination_district" and calculate "des_weight"
    df = df.withColumn("destination_district", sf.col("destination_district").cast(DoubleType()))
    des_weight_mapping = df.groupBy("destination_district").count()
    des_weight_mapping = des_weight_mapping.withColumn("des_weight", 10 - sf.log2(df.count() / sf.col("count")))
    df = df.join(des_weight_mapping, on="destination_district", how="left")
    df = df.fillna({"des_weight": 10.0})
    
    # Calculate "weight" column
    df = df.withColumn("weight", sf.col("time_weight") * sf.col("des_weight"))
    
    # Apply the add_missing_column function
    df = add_missing_column(df)
    return df

feature = [
         'distance',
         'dow_created_time',
         'hour_created_time',
         'suggested_deli_supplier',
         'destination_address_type',
         'destination_district',
         'seller_id',
         'suggested_pickup_supplier',
         'departure_region',
         'route'
            ]
encoder_column = [
                 'suggested_deli_supplier',
                 'suggested_pickup_supplier',
                 'destination_address_type',
                 'destination_district',
                 'departure_region',
                 'route'
                    ]

# Define the UDFs for your functions
def str2date_udf(x):
    return datetime.strptime(x[:19], "%Y-%m-%d %H:%M:%S")

def decay_weight_udf(days, half=14):
    return 0.5 ** (days / half)

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
  logger = logging.getLogger("MinioSparkJob")
  # spark = SparkSession.builder.getOrCreate()

  # Initialize a Spark session
  spark = SparkSession.builder.config("spark.driver.host", "localhost").appName("MinioDataTransformation").getOrCreate()
  print("START CONNECTING")

  # Set your Minio credentials and endpoint
  minio_access_key = "LylKyYWSyQzErR3pSXaa"
  minio_secret_key = "gdu1sWlu5BPhbskEazDeIOJSv3ZCxwuTrXqAKTkb"
  minio_endpoint = "http://nginx:9000"
  minio_bucket_name = "bronze"
  # Register UDFs with Spark
  str2date_spark_udf = sf.udf(str2date_udf, TimestampType())
  decay_weight_spark_udf = sf.udf(decay_weight_udf)

  load_config(spark.sparkContext)

  print("READ FILE")
  # Read data from Minio
  data = spark.read.json(f"s3a://{minio_bucket_name}/daily_orders_20230802.json")
  data.show()

  preprocessed_data = preprocess_data(data)
  print("PREPROCESSED DATA")
  preprocessed_data.show()

  # Write the transformed data back to Minio
  preprocessed_data.write \
      .mode("overwrite") \
      .option("header","true") \
      .csv(f"s3a://silver/output_data/")
  print("DONE")

  # Stop the Spark session
  spark.stop()