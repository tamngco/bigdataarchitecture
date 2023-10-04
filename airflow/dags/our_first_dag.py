from datetime import timedelta, datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'Tamnguyen',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}

def greet():
    print("Hello World")

with DAG(
    dag_id='my_first_dag_v3',
    default_args=default_args,
    description='my first dag',
    start_date=datetime(2023, 10, 4, 2),
    schedule_interval = '@daily'
) as dag:
    task1 = BashOperator(
        task_id='first_task',
        bash_command="echo helloworld"
    )
    task2 = BashOperator(
        task_id='second_test',
        bash_command='ok'
    )
    task3 = PythonOperator(
        task_id='greet',
        python_callable=greet
    )

    task1.set_downstream(task3)
    #task1 >> task2