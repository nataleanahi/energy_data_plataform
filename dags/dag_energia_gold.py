from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from src.pipeline.gold_pipeline import GoldPipeline

def ejecutar_pipeline_gold():
    pipeline = GoldPipeline()
    pipeline.run()

with DAG(
    dag_id='pipeline_energia_gold',
    start_date=datetime(2026, 6, 1),
    schedule_interval=None,
    catchup=False,
    tags=['oil_and_gas', 'gold']
) as dag:

    task_gold = PythonOperator(
        task_id='calcular_metricas_gold',
        python_callable=ejecutar_pipeline_gold
    )

    task_gold