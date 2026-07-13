from abc import ABC, abstractmethod
import logging

import pandas as pd

from src.config.paths import BRONZE_DIR, SILVER_DIR
from src.utils.pipeline_utils import (
    cargar_csvs,
    normalizar_columnas,
    eliminar_duplicados,
    guardar_parquet,
)

logger = logging.getLogger(__name__)


class BasePipeline(ABC):

    def __init__(self, patron_archivos: str, archivo_salida: str):

        self.patron_archivos = patron_archivos
        self.archivo_salida = archivo_salida

        self.logger = logging.getLogger(self.__class__.__name__)

    def run(self):

        self.logger.info("=" * 60)
        self.logger.info("Inicio del pipeline")

        df = cargar_csvs(
            BRONZE_DIR,
            self.patron_archivos
        )

        df = normalizar_columnas(df)

        df = eliminar_duplicados(df)

        df = self.transformar(df)

        guardar_parquet(
            df,
            SILVER_DIR,
            self.archivo_salida
        )

        self.logger.info("Pipeline finalizado")
        self.logger.info("=" * 60)

    @abstractmethod
    def transformar(self, df: pd.DataFrame) -> pd.DataFrame:
        pass