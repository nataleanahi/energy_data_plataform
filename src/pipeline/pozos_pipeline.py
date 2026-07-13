import pandas as pd

import src.config.logging_config

from src.pipeline.base_pipeline import BasePipeline
from src.utils.pipeline_utils import validar_columnas, validar_no_nulos


class PozosPipeline(BasePipeline):

    def __init__(self):

        super().__init__(
            patron_archivos="pozos*.csv",
            archivo_salida="pozos.parquet"
        )

    def transformar(self, df: pd.DataFrame) -> pd.DataFrame:

        self.logger.info("Transformando dataset Pozos")

        columnas_fecha = [
            "adjiv_fecha_inicio_perf",
            "adjiv_fecha_fin_perf",
            "adjiv_fecha_inicio_term",
            "adjiv_fecha_fin_term"
        ]

        validar_columnas(
            df,
            ["idpozo"] + columnas_fecha
        )

        df = validar_no_nulos(df, ["idpozo"])

        for columna in columnas_fecha:

            df[columna] = pd.to_datetime(
                df[columna],
                errors="coerce"
            )

        self.logger.info("Transformación finalizada.")

        return df


if __name__ == "__main__":

    PozosPipeline().run()