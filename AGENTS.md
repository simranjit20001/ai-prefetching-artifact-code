# Orientación para agentes

Repositorio de artefactos de un TFM sobre prebúsqueda de datos con aprendizaje automático.
Lee `README.md` para el mapa completo. Esto es lo mínimo para no romper nada.

## Qué es este repositorio

Datos, modelos y scripts que respaldan las cifras de una memoria académica ya escrita.
El objetivo del paquete es que un tercero pueda **verificar** esas cifras, no explorarlas.
Las cifras publicadas están congeladas: si un cambio las mueve, el cambio está mal.

## Comprobación única

```bash
scripts/reproduce.sh
```

Salida esperada: `OK: el artefacto reproduce exactamente las métricas de la memoria`.
Código 0 = correcto, 1 = divergencia. **Ejecútalo antes y después de cualquier cambio.**

## Invariantes

1. `data/` es la fuente de verdad. `results/` es una copia curada para lectura humana y
   **ningún script la lee**. Si cambias un dato, cámbialo en `data/`.
2. `figures/`, `generated_metrics.tex` y `MANIFEST.csv` son **generados**. No los edites a mano.
   - figuras y métricas: `scripts/rebuild_figures.sh`
   - manifiesto: `python3 scripts/build_manifest.py`
3. `reference/generated_metrics.expected.tex` contiene las cifras **publicadas**. No lo toques
   salvo que la memoria cambie de verdad; es el patrón contra el que se verifica todo.
4. **Cuatro ficheros de `data/` son salidas, no entradas.** El generador los reescribe en
   cada ejecución, aunque estén versionados:
   `all_methods_by_trace_speedup.csv`, `dagger_12_common_metrics.csv`,
   `dagger_same_traces_compare.csv` y `online_berti_l2_winner_counts.csv`.
   Contienen justo las cifras publicadas, así que invitan a editarlos; no lo hagas, se
   sobrescriben. Los números salen de la campaña final: `data/final_60m80m_by_trace.csv`
   y `data/final_60m80m_summary.csv`. Si falta el primero, el generador aborta con un error.
5. Hay **dos campañas** con números distintos y ambas son legítimas:
   - `final_60m80m_test` (60M calentamiento + 20M medidos) → **es la de la memoria**;
   - `classic` (20M+20M) → campaña previa, en los ficheros con sufijo `_campana_classic`
     y en `data/classic_champsim_*.csv`.
   Si una cifra no cuadra con el documento, comprueba primero de qué campaña viene.

Comprobado: alterar `ipc` en `data/final_60m80m_by_trace.csv` hace que
`reproduce.sh` salga con código 1 y muestre el diff. La verificación es real.

## Dónde está cada cosa

- Correspondencia figura/tabla de la memoria → fichero de datos: tabla «Mapa» en `README.md`.
- Wiring exacto figura → CSV: `scripts/build_figures.py`, una función por figura
  (`figure_<nombre>`).
- Código propio: `prefetchers/` (LLM en C++, MLP como checkpoint y cabecera exportada,
  LightGBM como modelo tabular).

## Lo que este repositorio no contiene

Trazas de ChampSim, el simulador completo y las salidas brutas de simulación. No intentes
reejecutar la campaña desde aquí: hace falta ChampSim y las trazas de DPC-4 en un entorno
externo. Lo que sí se puede hacer por completo es regenerar figuras y métricas desde los CSV.
