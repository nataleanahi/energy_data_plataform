import logging
import os
import pandas as pd
from src.pipeline.base_pipeline import BasePipeline

logger = logging.getLogger(__name__)


class GoldPipeline(BasePipeline):
    def __init__(self):
        self.ruta_silver_pozos = 'data/silver/pozos.parquet'
        self.ruta_silver_prod = 'data/silver/produccion.parquet'
        self.carpeta_output = 'data/gold'
        self.ruta_output = os.path.join(self.carpeta_output, 'metricas_pozos_mensual.parquet')

    def transformar(self, df_pozos: pd.DataFrame, df_prod: pd.DataFrame) -> pd.DataFrame:
        logger.info("Realizando merge de pozos y producción...")

        columna_union = 'idpozo'

        columnas_pozos = [col for col in df_pozos.columns if
                          col not in ['prod_pet', 'prod_gas', 'prod_agua'] or col == columna_union]
        df_pozos_filtrado = df_pozos[columnas_pozos]

        df_gold = pd.merge(df_prod, df_pozos_filtrado, on=columna_union, how='inner')

        logger.info("Calculando GOR y Water Cut sobre los datos reales...")

        df_gold['gor'] = df_gold['prod_gas'] / df_gold['prod_pet'].replace(0, pd.NA)

        columna_agua = 'prod_agua'
        if columna_agua in df_gold.columns:
            liquido_total = df_gold['prod_pet'] + df_gold[columna_agua]
            df_gold['water_cut'] = df_gold[columna_agua] / liquido_total.replace(0, pd.NA)
        else:
            logger.warning(f"No se encontró la columna {columna_agua} para calcular el Water Cut.")

        return df_gold

    def run(self):
        logger.info("Inicio del pipeline GOLD...")

        try:
            logger.info(f"Leyendo parquets desde Silver...")
            df_pozos = pd.read_parquet(self.ruta_silver_pozos)
            df_prod = pd.read_parquet(self.ruta_silver_prod)
        except Exception as e:
            logger.error(f"Error al leer los archivos de la capa Silver: {str(e)}")
            raise e

        df_resultado = self.transformar(df_pozos, df_prod)

        logger.info(f"Guardando archivo final en la capa Gold: {self.ruta_output}")
        os.makedirs(self.carpeta_output, exist_ok=True)
        df_resultado.to_parquet(self.ruta_output, index=False)

        logger.info("Pipeline GOLD finalizado con éxito.")