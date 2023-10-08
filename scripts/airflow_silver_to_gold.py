import logging
import numpy as np
import lightgbm
import boto3
import os
import pickle
from ml_function import *
from pyspark import SparkContext
from pyspark.sql import SparkSession
import pyspark.sql.functions as sf
from pyspark.sql.functions import col
from pyspark.sql.types import * 
from pyspark.ml.linalg import Vectors

# Set your Minio credentials and endpoint
minio_access_key = "LylKyYWSyQzErR3pSXaa"
minio_secret_key = "gdu1sWlu5BPhbskEazDeIOJSv3ZCxwuTrXqAKTkb"
minio_endpoint = "http://nginx:9000"
minio_bucket_name = "silver/output_data"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MinioSparkJob")

# Initialize a Spark session
spark = SparkSession.builder.config("spark.driver.host", "localhost")\
  .appName("MinioDataTransformation")\
    .getOrCreate()

session = boto3.Session(
  aws_access_key_id=minio_access_key,
  aws_secret_access_key=minio_secret_key
)

minio_client = session.client(
    's3',
    endpoint_url=minio_endpoint,
    use_ssl=False,
    verify=False
)


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
sub_feature = [
    'datetime_created_at',
    'destination_address_type'
]

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


def load_model(model_name):
  # Download the pickled model from Minio
    model = pickle.load(open(model_name,'rb'))
    return model


def transformer_df_spark(df, encoder_column):
    transformed_df = df
    for col_name in encoder_column:
        if col_name in ['suggested_deli_supplier', 'suggested_pickup_supplier']:
            # Generate random integers between 0 and 2
            random_values = sf.when(sf.lit(True), sf.lit(0) + (sf.lit(2) - sf.lit(0))*sf.rand()).cast(IntegerType())
        else:
            # Generate random integers between 0 and 4
            random_values = sf.when(sf.lit(True), sf.lit(0) + (sf.lit(4) - sf.lit(0))*sf.rand()).cast(IntegerType())
        
        # Update the DataFrame with the random values
        transformed_df = transformed_df.withColumn(col_name, random_values)
    return transformed_df


if __name__ == '__main__':
  load_config(spark.sparkContext)

  model_data = minio_client.get_object(Bucket="mlmodel",
                                     Key="logistic_model.pkl")['Body']

  model_lightgbm = pickle.loads(model_data.read())

# Read data from Minio
  data = spark.read\
  .option("header", "true")\
    .option("inferschema", "true")\
      .csv("s3a://silver/output_data/*.csv")
  
  data.show()
  # Perform data transformations
  print("LOAD DATA")
  df = transformer_df_spark(df=data, encoder_column=encoder_column)

  # data["predicted_delivery_leadtime"], data["predicted_delivery_time"] = 
  data = predict_spark(spark = spark, processed_test=df, model=model_lightgbm, feature=feature)
  print("PREDICTED DATA")
  data.show()

  # # Write the transformed data back to Minio

  #data.write \
  #    .mode("overwrite") \
  #    .option("header","true") \
  #    .csv(f"s3a://gold/predicted_data/")

  #data.write \
  #    .mode("overwrite") \
  #    .option("header", "true") \
  #    .option("repartition", 1) \
  #    .csv(f"s3a://gold/predicted_data2/")

  df.coalesce(1).write \
      .mode("overwrite") \
      .option("header", "true") \
      .csv(f"s3a://gold/predicted_data/")

  print("DONE")
  # Stop the Spark session
  spark.stop()