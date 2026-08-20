# AI Prefetching

Código y artefactos públicos del TFM sobre técnicas de prebúsqueda de datos con aprendizaje automático.

Repositorio público: <https://github.com/simranjit20001/ai-prefetching-artifact-code>

## Organización

- `prefetchers/`: código y modelos propios.
  - `LLM/`: código del prefetcher de la línea LLM.
  - `MLP/`: checkpoint y cabecera C++ exportada del modelo MLP.
  - `LightGBM/`: modelo LightGBM de referencia.
- `data/`: CSV/JSON usados por los scripts de figuras, incluida la evaluación final 60M--80M.
- `results/`: resultados resumidos.
  - `online/`: resultados de PPF, Pythia y uMAMA.
  - `mlp_lightgbm/`: resultados de DAgger, MLP y LightGBM.
  - `llm/`: resultados de la línea LLM y logs metodológicos resumidos.
- `scripts/`: scripts para reconstruir figuras y verificar la reproducción.
- `reference/generated_metrics.expected.tex`: métricas publicadas en la memoria, usadas como referencia de verificación.
- `MANIFEST.csv`: tamaño y SHA-256 de los ficheros incluidos.

## Reproducir las figuras y las métricas

```bash
python3 -m pip install -r requirements.txt
scripts/rebuild_figures.sh
```

El script genera `figures/` y `generated_metrics.tex` a partir de los CSV incluidos en `data/` y `results/`.

## Verificar la reproducción

```bash
scripts/verify_reproduction.sh
```

Regenera las métricas y las compara con `reference/generated_metrics.expected.tex`, que contiene exactamente los valores publicados en la memoria. El script sale con código 0 si coinciden byte a byte y con código 1 si aparece cualquier divergencia. Es la comprobación recomendada tras clonar el repositorio.

### Qué se comprueba y qué no

La verificación cubre todas las cifras numéricas que la memoria toma del artefacto: IPC geométrico y mejora relativa por método, prebúsquedas emitidas y útiles, precisión y cobertura, recuentos de victorias por traza y métricas agregadas por familia de carga.

Las figuras se regeneran a partir de los mismos datos, pero los PDF resultantes no son idénticos byte a byte entre máquinas, porque el rasterizado y las métricas de fuente dependen de la versión de matplotlib y de las fuentes instaladas. El contenido (series, etiquetas y valores) sí es idéntico. Por eso la verificación automática se hace sobre las métricas y no sobre el binario de las figuras.

### Entorno de referencia

La campaña original se ejecutó con Python 3.13. La verificación se ha comprobado también con Python 3.11 y con `matplotlib` 3.10, `numpy` 2.4 y `pandas` 3.0, obteniendo métricas idénticas. `requirements.txt` no fija versiones porque el resultado no depende de ellas dentro de estos rangos; si una versión futura introdujese divergencias, `verify_reproduction.sh` las detectaría.

## Disposición de carpetas

`scripts/build_figures.py` funciona en dos disposiciones sin necesidad de editarlo:

- artefacto autónomo (este repositorio): lee de `data/` y `results/`, escribe en `figures/` y `generated_metrics.tex`;
- paquete de entrega del TFM: lee de `02_artifacts/`, y además escribe las figuras y `generated_metrics.tex` dentro de `00_latex_src/` cuando ese directorio existe.

El directorio de datos puede forzarse con la variable de entorno `TFM_DATA_DIR`.

## Alcance

El repositorio incluye el código propio, los modelos ligeros, los CSV usados por las figuras, resultados resumidos y logs ligeros de entrenamiento o iteración. No incluye trazas ChampSim completas, repositorios externos completos ni salidas brutas masivas de simulación.

La repetición completa de todas las simulaciones requiere un entorno externo con ChampSim y las trazas correspondientes. Este paquete permite auditar el código incluido y reconstruir las figuras y métricas del documento a partir de los datos empaquetados.
