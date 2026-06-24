# Datos resumidos

Esta carpeta contiene datos resumidos y ligeros usados para construir las figuras del documento.

## Grupos de ficheros

- `classic_champsim_*.csv`: resultados resumidos y por traza de PPF, Pythia y uMAMA.
- `ml_*.csv` y `ml_*.json`: datos de DAgger, validación MLP/LightGBM, selección de modelos y análisis SHAP.
- `dagger_12_common_metrics.csv`: comparación de IPC y speedup en la selección compartida de 12 trazas. Incluye MLP, referencias online y la política LLM restringida a esas mismas trazas. Las columnas de precisión, cobertura y tráfico L2 están disponibles para las políticas con contadores exportados en esa campaña.
- `llm_*.csv`: resultados resumidos de iteraciones de la línea LLM.
- `prefetcher_geomeans.csv`: resumen compacto de métricas geométricas usadas en el texto.

Estos datos no sustituyen a las trazas completas ni al clúster de simulación. Sirven para reproducir las figuras y los números presentados en el documento.

Las columnas operativas no usadas en el documento se han eliminado para que el paquete sea más claro al revisarlo o reutilizarlo en nuevas gráficas.
