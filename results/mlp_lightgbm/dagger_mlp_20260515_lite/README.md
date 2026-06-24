# DAgger MLP run, 2026-05-15

Carpeta ligera con los artefactos útiles del run principal de DAgger:

`results/mlp_lightgbm/dagger_mlp_20260515_lite`

Se copian resúmenes, resultados de validación, resultados de recogida, logs de entrenamiento, modelos exportados y cabeceras de integración. No se copian `combined_states.csv` ni `combined_labels.npz`, porque el run completo ocupa 2.7 GB y esos ficheros son artefactos pesados de reconstrucción.

Contenido principal:

- `summary.csv`
- `models_progress.csv`
- `test_by_trace.csv`
- `test_progress_summary.csv`
- `iterXX/combined/sample_counts.csv`
- `iterXX/labeled_rows.csv`
- `iterXX/collect/train_20M_20M_*.csv`
- `iterXX/val/*/val_40M_20M_*.csv`
- `iterXX/models/*/train*.log`
- `iterXX/models/*/candidate_*`
- `iterXX/headers/mlp/*.h`

La iteración de referencia del documento es `iter03`.
