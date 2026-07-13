import logging

import pandas as pd

import src.config.logging_config

from src.pipeline.base_pipeline import BasePipeline
from src.utils.pipeline_utils import validar_columnas


class ProduccionPipeline(BasePipeline):

    def __init__(self):

        super().__init__(
            patron_archivos="produccion*.csv",
            archivo_salida="produccion.parquet"
        )

    def transformar(self, df: pd.DataFrame) -> pd.DataFrame:

        self.logger.info("Transformando dataset Producción")

        validar_columnas(
            df,
            [
                "idpozo",
                "anio",
                "mes",
                "fecha_data",
                "fechaingreso",
                "habilitado",
                "rectificado",
            ]
        )

        if df["fecha_data"].isnull().any():

            df["fecha_data"] = (
                df["anio"].astype(str)
                + "-"
                + df["mes"].astype(str).str.zfill(2)
                + "-01"
            )

        df["fecha_data"] = pd.to_datetime(
            df["fecha_data"],
            errors="coerce"
        )

        df["fechaingreso"] = pd.to_datetime(
            df["fechaingreso"],
            errors="coerce"
        )

        from src.utils.pipeline_utils import validar_no_nulos, validar_rangos_numericos
        df = validar_no_nulos(df, ["fecha_data", "idpozo", "idempresa"])

        df = validar_rangos_numericos(df, "anio", min_val=1900, max_val=2026)
        df = validar_rangos_numericos(df, "mes", min_val=1, max_val=12)

        mapa = {
            "t": True,
            "f": False
        }

        df["habilitado"] = (
            df["habilitado"]
            .astype(str)
            .str.lower()
            .map(mapa)
        )

        df["rectificado"] = (
            df["rectificado"]
            .astype(str)
            .str.lower()
            .map(mapa)
        )

        df["habilitado"] = df["habilitado"].fillna(False).astype(bool)
        df["rectificado"] = df["rectificado"].fillna(False).astype(bool)

        self.logger.info("Transformación finalizada.")

        return df


if __name__ == "__main__":

    ProduccionPipeline().run()