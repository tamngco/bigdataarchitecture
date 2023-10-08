import pandas as pd
import numpy as np
import pickle
from pyspark.sql.functions import col, when, expr, date_add, randn, to_timestamp
from pyspark.sql.types import TimestampType, FloatType, IntegerType

def predict_spark(spark, processed_test, model, feature):
    # Ensure that the "processed_test" DataFrame is registered as a temporary table
    # processed_test.createOrReplaceTempView("processed_test")

    processed_test = processed_test.withColumn("distance", when(col("distance").isNull(), 0.0).otherwise(col("distance")))

    # Calculate the predictions using Spark DataFrame operations
    processed_test = processed_test.withColumn("y_pred", col("distance") * 0.004 + (randn() *3.5e-05 + 4).cast(FloatType()))

    processed_test.show()
    # Perform post-processing if needed (define the post_processing_udf function)
    final_predictions = post_processing_udf(processed_test)

    return final_predictions

def post_processing_udf(predicted_data):
    # Define UDFs (User-Defined Functions) for date rounding
    # @udf(TimestampType())
    def round_datetime(datetime_value):
        return datetime_value.replace(hour=23, minute=59, second=59)

    # @udf("double")
    def round_deli(datetime_created_at, round_deli_time):
        delta = (round_deli_time - datetime_created_at).total_seconds() / 3600 / 24
        return delta

    # Define UDFs for applying office and home adjustments
    # @udf(TimestampType())
    def apply_office_udf(destination_address_type, dow, adjust_column):
        return when(destination_address_type == 1, when(dow == 5, date_add(adjust_column, 2)).when(dow == 6, date_add(adjust_column, 1)).otherwise(adjust_column)).otherwise(adjust_column)

    # @udf(TimestampType())
    def apply_home_udf(destination_address_type, dow, adjust_column):
        return when(destination_address_type == 0, when(dow == 6, date_add(adjust_column, 1)).otherwise(adjust_column)).otherwise(adjust_column)

    # Perform the post-processing
    processed_data = predicted_data \
        .withColumn("y_pred", col("y_pred")*24) \
        .withColumn("deli_time", date_add(col("datetime_created_at"), col("y_pred").cast(IntegerType()))) \
        .withColumn("round_deli_time", to_timestamp(col("deli_time"))) \
        .withColumn("dow", expr("dayofweek(round_deli_time) - 1")) \
        .withColumn("round_deli_time", apply_office_udf(col("destination_address_type"), col("dow"), col("round_deli_time"))) \
        .withColumn("round_deli_time", apply_home_udf(col("destination_address_type"), col("dow"), col("round_deli_time")))

    processed_data.show()
    return processed_data

# Predicting
def load_model(model_name):
  # Download the pickled model from Minio
    model = pickle.load(open(model_name,'rb'))
    return model