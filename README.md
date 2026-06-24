# Artefacto del TFM: AI Prefetching

Artefactos del TFM sobre técnicas de prebúsqueda de datos con aprendizaje automático.

## Organización

- `prefetchers/`: código y modelos propios.
  - `LLM/`: código del prefetcher de la línea LLM.
  - `MLP/`: checkpoint y cabecera C++ exportada del modelo MLP.
  - `LightGBM/`: modelo LightGBM de referencia.
- `data/`: CSV/JSON usados por los scripts de figuras.
- `results/`: resultados resumidos.
  - `online/`: resultados de PPF, Pythia y uMAMA.
  - `mlp_lightgbm/`: resultados de DAgger, MLP y LightGBM.
  - `llm/`: resultados de la línea LLM.
- `scripts/`: scripts para reconstruir figuras.
- `MANIFEST.csv`: tamaño y SHA-256 de los ficheros incluidos.

## Figuras

```bash
python3 -m pip install -r requirements.txt
scripts/rebuild_figures.sh
```

El script genera `figures/` y `generated_metrics.tex`.
