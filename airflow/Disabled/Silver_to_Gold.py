from datetime import timedelta, datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'Big Data K32',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}

# Import function
def doImport():
    import clickhouse_connect

    client = clickhouse_connect.get_client(host='clickhouse_server', username='clickhouse_admin', password='password')

    command = """INSERT INTO logistics_bi.orders
                 SELECT *
                 FROM s3('http://nginx:9000/gold/predicted_data/*.csv', 'LylKyYWSyQzErR3pSXaa','gdu1sWlu5BPhbskEazDeIOJSv3ZCxwuTrXqAKTkb', 'CSVWithNames')"""

    client.command(command)


with DAG(
    dag_id='Silver_to_Gold',
    default_args=default_args,
    description='Import data from Minio (Data Lake) to Clickhouse (OLAP)',
    start_date=datetime(2023, 10, 4, 2),
    schedule_interval = '@daily'
) as dag:
    #task1 = BashOperator(
    #    task_id='first_task',
    #    bash_command="echo helloworld"
    #)
    #task2 = BashOperator(
    #    task_id='second_test',
    #    bash_command='ok'
    #)
    task1 = PythonOperator(
        task_id='import_data',
        python_callable=doImport
    )

    #task1.set_downstream(task3)
    #task1 >> task2