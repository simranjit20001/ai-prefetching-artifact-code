# Artefacto del TFM: AI Prefetching

Código y artefactos públicos del TFM sobre técnicas de prebúsqueda de datos con aprendizaje automático.

Repositorio público: <https://github.com/simranjit20001/ai-prefetching-artifact-code>

## Organización

- `prefetchers/`: código y modelos propios.
  - `LLM/`: código del prefetcher de la línea LLM.
  - `MLP/`: checkpoint y cabecera C++ exportada del modelo MLP.
  - `LightGBM/`: modelo LightGBM de referencia.
- `data/`: CSV/JSON usados por los scripts de figuras.
- `results/`: resultados resumidos.
  - `online/`: resultados de PPF, Pythia y uMAMA.
  - `mlp_lightgbm/`: resultados de DAgger, MLP y LightGBM.
  - `llm/`: resultados de la línea LLM y logs metodológicos resumidos.
- `scripts/`: scripts para reconstruir figuras.
- `MANIFEST.csv`: tamaño y SHA-256 de los ficheros incluidos.

## Figuras

```bash
python3 -m pip install -r requirements.txt
scripts/rebuild_figures.sh
```

El script genera `figures/` y `generated_metrics.tex`.

## Alcance

El repositorio incluye el código propio, los modelos ligeros, los CSV usados por las figuras, resultados resumidos y logs ligeros de entrenamiento o iteración. No incluye trazas ChampSim completas, repositorios externos completos ni salidas brutas masivas de simulación.

La repetición completa de todas las simulaciones requiere un entorno externo con ChampSim y las trazas correspondientes. Este paquete permite auditar el código incluido y reconstruir las figuras y métricas del documento a partir de los datos empaquetados.
