# Energy Production Data Platform

Proyecto de Ingeniería de Datos orientado a la industria energética.

El objetivo es construir una plataforma de datos end-to-end que integre
información pública de producción hidrocarburífera argentina, aplicando
conceptos reales de Data Engineering: ingestión, arquitectura por capas,
transformación, modelado dimensional y exposición de datos para
análisis.

------------------------------------------------------------------------

## 1. Fuentes de datos (Data Sources)

### Producción de Pozos de Gas y Petróleo No Convencional

Origen: Datos Argentina (datos.gob.ar)

Descripción:

Dataset con registros mensuales de producción de pozos
hidrocarburíferos.

Granularidad:

> Una fila representa la producción mensual registrada de un pozo.

Campos relevantes:

-   id_empresa
-   id_pozo
-   año
-   mes
-   producción petróleo
-   producción gas
-   producción agua
-   inyección
-   tipo de extracción
-   estado del pozo
-   formación
-   yacimiento
-   cuenca
-   provincia

Uso:

Alimenta:

-   fact_produccion
-   dimensiones relacionadas al pozo

------------------------------------------------------------------------

### Capítulo IV - Pozos

Origen: Datos Argentina (datos.gob.ar)

Descripción:

Dataset maestro de pozos declarados.

Granularidad:

> Una fila representa una entidad pozo.

Campos relevantes:

-   id_pozo
-   sigla
-   empresa
-   yacimiento
-   cuenca
-   provincia
-   formación
-   profundidad
-   tipo de pozo
-   estado
-   ubicación geográfica

Uso:

Alimenta:

-   dim_pozo
-   dim_yacimiento
-   dim_empresa
-   dim_cuenca

------------------------------------------------------------------------

# 2. Objetivo del proyecto (Business Goal)

Construir una plataforma de datos energética capaz de integrar
información pública de producción hidrocarburífera para analizar:

-   evolución temporal de producción
-   rendimiento por pozo
-   producción por cuenca
-   producción por empresa
-   distribución geográfica
-   comportamiento de recursos energéticos

------------------------------------------------------------------------

# 3. Arquitectura de datos

Modelo:

**Data Lake + Data Warehouse dimensional**

Flujo:

    Fuentes externas
            |
            v
    Bronze Layer
    (Raw Data)
            |
            v
    Silver Layer
    (Clean Data)
            |
            v
    Gold Layer
    (Data Warehouse)
            |
            v
    Analytics / API

------------------------------------------------------------------------

# 4. Capas de datos

## Bronze Layer

Objetivo:

Preservar los datos originales.

Características:

-   datos sin modificar
-   mismo formato que origen
-   trazabilidad y auditoría

Ejemplo:

    bronze/

    production/
      production_raw.csv

    wells/
      wells_raw.csv

Estrategia de carga:

Producción: - incremental

Pozos: - full inicial - posibilidad de CDC

------------------------------------------------------------------------

## Silver Layer

Objetivo:

Transformar los datos para consumo interno.

Procesos:

-   limpieza
-   normalización
-   validación
-   eliminación de duplicados
-   transformación de formatos

Ejemplo:

Transformación de producción:

Antes:

    prod_gas
    prod_pet
    prod_agua

Después:

    recurso
    volumen
    unidad
    tipo_medicion

------------------------------------------------------------------------

# 5. Modelo dimensional (Gold Layer)

Tipo:

**Star Schema**

------------------------------------------------------------------------

## Tabla de hechos

### fact_produccion

Grano:

> Una fila representa la producción mensual de un recurso energético en
> un pozo determinado.

Campos:

    produccion_id

    fecha_id
    pozo_id
    recurso_id
    unidad_id

    volumen_producido

------------------------------------------------------------------------

## Dimensiones

### dim_pozo

Contiene:

-   identificación del pozo
-   yacimiento
-   ubicación
-   formación
-   tipo de extracción

Estrategia histórica:

Slowly Changing Dimension Tipo 2.

Motivo:

Conservar cambios históricos.

------------------------------------------------------------------------

### dim_fecha

Permite análisis temporal:

-   año
-   mes
-   trimestre

------------------------------------------------------------------------

### dim_recurso

Ejemplos:

-   petróleo
-   gas
-   agua

------------------------------------------------------------------------

### dim_unidad

Ejemplos:

-   barriles
-   m3
-   MMm3

------------------------------------------------------------------------

### dim_empresa

Contiene información del operador.

------------------------------------------------------------------------

# 6. Estrategia de actualización

## Producción

Tipo:

Incremental Load

Motivo:

Los datos representan nuevos eventos de producción.

Clave:

    id_pozo + año + mes

------------------------------------------------------------------------

## Pozos

Tipo:

Full inicial + actualización incremental.

Aplicación:

Slowly Changing Dimension Tipo 2.

Permite mantener historial de cambios.

------------------------------------------------------------------------

# 7. Tecnologías propuestas

Ingesta:

-   Python
-   Pandas
-   APIs / CSV

Procesamiento:

-   Python
-   SQL

Warehouse:

-   PostgreSQL

API:

-   FastAPI

Orquestación futura:

-   Airflow

Visualización:

-   Power BI / Streamlit

------------------------------------------------------------------------

# 8. Futuras extensiones

## Módulo IoT

Simulación de sensores industriales:

-   presión
-   temperatura
-   caudal

Arquitectura futura:

    IoT Sensors
          |
    Streaming
          |
    Data Lake
          |
    Time Series Database
          |
    Alertas / Analytics

------------------------------------------------------------------------

## Estado actual del proyecto

Fase completada:

-   definición del caso de negocio
-   análisis inicial de fuentes
-   diseño conceptual
-   definición de arquitectura

Próxima fase:

-   Data Dictionary
-   diseño físico del Warehouse
-   implementación ETL
-   construcción del pipeline end-to-end
