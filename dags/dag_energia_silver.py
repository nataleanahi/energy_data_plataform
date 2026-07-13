from datetime import datetime, timedelta
import sys
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from src.pipeline.pozos_pipeline import PozosPipeline
from src.pipeline.produccion_pipeline import ProduccionPipeline
import logging

logger = logging.getLogger(__name__)

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROYECTO) not in sys.path:
    sys.path.append(str(RAIZ_PROYECTO))

def ejecutar_pipeline_pozos():
    pipeline = PozosPipeline()
    pipeline.run()

def ejecutar_pipeline_produccion():
    pipeline = ProduccionPipeline()
    pipeline.run()

def etapa_gold_placeholder():
    logger.info(
        "¡Capa Silver completada con éxito! Listo para procesar métricas Gold (GOR, Declive)."
    )

default_args = {
    "owner": "data_engineering_team",
    "depends_on_past": False,
    "start_date": datetime(2026, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    "pipeline_energia_silver",
    default_args=default_args,
    description="Orquestación de las transformaciones Silver para Pozos y Producción de Oil & Gas",
    schedule_interval="@monthly",
    catchup=False,
) as dag:

    task_pozos = PythonOperator(
        task_id="transformar_pozos_silver",
        python_callable=ejecutar_pipeline_pozos,
    )

    task_produccion = PythonOperator(
        task_id="transformar_produccion_silver",
        python_callable=ejecutar_pipeline_produccion,
    )

    trigger_gold = TriggerDagRunOperator(
        task_id='disparar_pipeline_gold',
        trigger_dag_id='pipeline_energia_gold',
        wait_for_completion=False
    )

    [task_pozos, task_produccion] >> trigger_gold
