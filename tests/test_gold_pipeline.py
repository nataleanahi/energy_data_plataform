import pandas as pd
import numpy as np
import pytest
from src.pipeline.gold_pipeline import GoldPipeline


@pytest.fixture
def pipeline_gold():
    return GoldPipeline()


@pytest.fixture
def datos_prueba_silver():
    df_pozos = pd.DataFrame({
        'idpozo': [1, 2],
        'sigla': ['PZO-01', 'PZO-02'],
        'empresa': ['YSUR', 'YPF'],
        'provincia': ['NEUQUEN', 'NEUQUEN']
    })

    df_prod = pd.DataFrame({
        'idpozo': [1, 1, 2],
        'anio': [2024, 2024, 2024],
        'mes': [1, 2, 1],
        'prod_pet': [100.0, 50.0, 0.0],
        'prod_gas': [500.0, 300.0, 100.0],
        'prod_agua': [20.0, 10.0, 5.0],
        'tef': [30.0, 15.0, 0.0]
    })

    return df_pozos, df_prod


def test_transformar_calculos_metricas(pipeline_gold, datos_prueba_silver):
    df_pozos, df_prod = datos_prueba_silver

    df_resultado = pipeline_gold.transformar(df_pozos, df_prod)

    assert len(df_resultado) == 3

    assert df_resultado.loc[0, 'liquido_total'] == 120.0

    assert df_resultado.loc[0, 'gor'] == 5.0

    assert pd.isna(df_resultado.loc[2, 'gor'])

    pozo_1_rows = df_resultado[df_resultado['idpozo'] == 1].sort_values(by='mes')
    assert list(pozo_1_rows['np_acum_pet']) == [100.0, 150.0]

    assert np.isclose(pozo_1_rows.iloc[1]['caudal_diario_pet'], 50.0 / 15.0)

    assert list(pozo_1_rows['mes_vida_pozo']) == [1, 2]


def test_evitar_colision_columnas(pipeline_gold):
    df_pozos = pd.DataFrame({
        'idpozo': [1],
        'prod_pet': [999.0],
        'provincia': ['NEUQUEN']
    })

    df_prod = pd.DataFrame({
        'idpozo': [1],
        'anio': [2024],
        'mes': [1],
        'prod_pet': [100.0],
        'prod_gas': [200.0],
        'prod_agua': [10.0]
    })

    df_resultado = pipeline_gold.transformar(df_pozos, df_prod)

    assert df_resultado.loc[0, 'prod_pet'] == 100.0