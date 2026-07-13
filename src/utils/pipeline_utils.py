from pathlib import Path
import logging
import unicodedata

import pandas as pd

logger = logging.getLogger(__name__)


def cargar_csvs(origen: Path, patron: str) -> pd.DataFrame:
    archivos = list(origen.glob(patron))

    if not archivos:
        logger.error("No se encontraron archivos con el patrón '%s'.", patron)
        raise FileNotFoundError(f"No existen archivos con el patrón '{patron}'.")

    logger.info("Archivos encontrados: %s", len(archivos))

    lista = []

    for archivo in archivos:
        logger.info("Leyendo archivo: %s", archivo.name)
        lista.append(pd.read_csv(archivo))

    df = pd.concat(lista, ignore_index=True)

    logger.info("Registros cargados: %s", len(df))

    return df


def limpiar_texto(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)

    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )

    return texto.lower().replace(" ", "_")


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Normalizando nombres de columnas.")

    df.columns = [limpiar_texto(col) for col in df.columns]

    return df


def eliminar_duplicados(df: pd.DataFrame) -> pd.DataFrame:
    antes = len(df)

    df = df.drop_duplicates()

    logger.info(
        "Duplicados eliminados: %s",
        antes - len(df)
    )

    return df

"""
def eliminar_sin_id(df: pd.DataFrame) -> pd.DataFrame:
    antes = len(df)

    df = df.dropna(subset=["idpozo"]).reset_index(drop=True)

    logger.info(
        "Registros eliminados por idpozo nulo: %s",
        antes - len(df)
    )

    return df
"""

def validar_columnas(df: pd.DataFrame, columnas: list[str]) -> None:
    faltantes = [c for c in columnas if c not in df.columns]

    if faltantes:
        logger.error("Columnas faltantes: %s", ", ".join(faltantes))
        raise ValueError(
            f"Faltan columnas obligatorias: {faltantes}"
        )

    logger.info("Validación de columnas correcta.")


def validar_no_nulos(df: pd.DataFrame, columnas: list[str]) -> pd.DataFrame:
    antes = len(df)

    df_filtrado = df.copy()

    for col in columnas:
        if col in df_filtrado.columns and df_filtrado[col].dtype == "object":
            df_filtrado[col] = df_filtrado[col].astype(str).str.strip().replace(["", "None", "nan", "NaN"], pd.NA)

    df_filtrado = df_filtrado.dropna(subset=columnas).reset_index(drop=True)

    descartados = antes - len(df_filtrado)
    if descartados > 0:
        logger.warning(
            "Se eliminaron %s registros por contener nulos u omitidos obligatorios en %s.",
            descartados, columnas
        )

    return df_filtrado


def validar_rangos_numericos(df: pd.DataFrame,
                             columna: str,
                             min_val: float,
                             max_val: float) -> pd.DataFrame:
    antes = len(df)
    condicion = (df[columna] >= min_val) & (df[columna] <= max_val)
    df_filtrado = df[condicion].reset_index(drop=True)

    descartados = antes - len(df_filtrado)
    if descartados > 0:
        logger.warning(
            "Se eliminaron %s registros en '%s' fuera del rango [%s, %s].",
            descartados, columna, min_val, max_val
        )

    return df_filtrado

def guardar_parquet(
    df: pd.DataFrame,
    destino: Path,
    nombre_archivo: str
) -> None:

    destino.mkdir(parents=True, exist_ok=True)

    ruta = destino / nombre_archivo

    logger.info("Guardando archivo %s", ruta.name)

    df.to_parquet(
        ruta,
        engine="pyarrow",
        compression="snappy"
    )

    logger.info("Archivo guardado correctamente.")