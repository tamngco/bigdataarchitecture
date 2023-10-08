from airflow.models.dag import DAG
from datetime import datetime, timedelta
#from airflow.providers.apache.spark.operators.spark_sql import SparkSqlOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
#from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator

default_args = {
    'owner': 'Big Data K32',
    'start_date': datetime(2023, 10, 7),
    'retries':2,
    'retry_delay': timedelta(hours=5),
}
with DAG('Bronze_to_Silver_DAG_v5',
                  default_args=default_args,
                  schedule_interval='@daily',
                  tags=["SparkSubmit"],
                  catchup=False

                ) as dag:

    # spark = SparkSession(SparkContext(conf=SparkConf()).getOrCreate())

    SparkSubmitOps= SparkSubmitOperator(
        task_id='sparkSubmitOps',
        conn_id='spark_master',
        application="/opt/airflow/dags/bronze_to_silver_old.py",
        packages="org.apache.hadoop:hadoop-aws:3.2.1",
        total_executor_cores=3,
        executor_memory="2G",
        executor_cores=1,
        driver_memory="2G",
        num_executors=6,
        env_vars=None,
        dag=dag
    )

    SparkSubmitOps