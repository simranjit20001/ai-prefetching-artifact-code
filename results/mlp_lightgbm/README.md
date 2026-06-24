# ChampSimMLP_LightGBM

Artefactos de la linea de aprendizaje offline mediante DAgger, MLP y LightGBM.

Esta carpeta agrupa los CSV de validacion, comparacion y analisis de modelos. Tambien incluye una copia ligera del run principal de DAgger en `dagger_mlp_20260515_lite`, con iteraciones, validaciones, recogida de datos, modelos exportados y cabeceras de integracion.

Ficheros principales:

- `ml_dagger_summary.csv`: resumen de iteraciones DAgger.
- `ml_models_progress.csv`: progreso de modelos y seleccion de validacion.
- `ml_validation_by_trace.csv`: validacion por traza.
- `dagger_same_traces_compare.csv`: comparacion de MLP con referencias online.
- `dagger_12_common_metrics.csv`: metricas de rendimiento y actividad en la seleccion compartida.
- `ml_lgbm_treeshap.csv` y `ml_lgbm_top15_val_summary.json`: analisis de LightGBM.
- `dagger_mlp_20260515_lite/`: copia ligera del run principal.

La iteracion de referencia del documento es `iter03`.

