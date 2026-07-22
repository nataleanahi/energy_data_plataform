import logging
import os
import calendar
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

        columnas_pozos = [
            col for col in df_pozos.columns
            if col not in ['prod_pet', 'prod_gas', 'prod_agua'] or col == columna_union
        ]
        df_pozos_filtrado = df_pozos[columnas_pozos]

        df_gold = pd.merge(df_prod, df_pozos_filtrado, on=columna_union, how='inner')

        logger.info("Ordenando cronológicamente para cálculos temporales...")
        df_gold = df_gold.sort_values(by=[columna_union, 'anio', 'mes']).reset_index(drop=True)

        logger.info("Calculando métricas analíticas de Oil & Gas...")

        df_gold['liquido_total'] = df_gold['prod_pet'] + df_gold['prod_agua']

        # Barrel of Oil Equivalent 1000 m3 gas ~= 6.29 bbl / ~1 m3 pet = 1 m3 OE
        df_gold['prod_m3_oe'] = df_gold['prod_pet'] + (df_gold['prod_gas'] * 6.29)

        df_gold['gor'] = df_gold['prod_gas'] / df_gold['prod_pet'].replace(0, pd.NA)
        df_gold['water_cut'] = df_gold['prod_agua'] / df_gold['liquido_total'].replace(0, pd.NA)
        df_gold['wgr'] = df_gold['prod_agua'] / df_gold['prod_gas'].replace(0, pd.NA)

        if 'tef' in df_gold.columns:
            df_gold['dias_mes'] = df_gold.apply(lambda row: calendar.monthrange(int(row['anio']), int(row['mes']))[1],
                                                axis=1)

            df_gold['uptime_pct'] = (df_gold['tef'] / df_gold['dias_mes']).clip(upper=1.0)
            df_gold['downtime_dias'] = df_gold['dias_mes'] - df_gold['tef']

            df_gold['caudal_diario_pet'] = df_gold['prod_pet'] / df_gold['tef'].replace(0, pd.NA)
            df_gold['caudal_diario_gas'] = df_gold['prod_gas'] / df_gold['tef'].replace(0, pd.NA)
            df_gold['caudal_diario_agua'] = df_gold['prod_agua'] / df_gold['tef'].replace(0, pd.NA)

        df_gold['np_acum_pet'] = df_gold.groupby(columna_union)['prod_pet'].cumsum()
        df_gold['gp_acum_gas'] = df_gold.groupby(columna_union)['prod_gas'].cumsum()
        df_gold['wp_acum_agua'] = df_gold.groupby(columna_union)['prod_agua'].cumsum()

        df_gold['mes_vida_pozo'] = df_gold.groupby(columna_union).cumcount() + 1

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