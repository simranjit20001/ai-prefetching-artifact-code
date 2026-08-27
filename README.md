# Artefacto del TFM — Prebúsqueda de datos con aprendizaje automático

Código, modelos y datos que respaldan las cifras y figuras de la memoria
*«Aprendizaje automático para la prebúsqueda de datos en procesadores»*
(Máster Universitario en Inteligencia Artificial, UNIR).

Repositorio: <https://github.com/simranjit20001/ai-prefetching-artifact-code>

---

## Empezar en 30 segundos

```bash
python3 -m pip install -r requirements.txt
scripts/verify_reproduction.sh
```

Si imprime `OK: el artefacto reproduce exactamente las métricas de la memoria`, todo lo que
afirma el documento se ha regenerado desde los datos de este repositorio. Es la única
comprobación que hace falta ejecutar para auditar el trabajo.

Para regenerar además los PDF de las figuras:

```bash
scripts/rebuild_figures.sh
```

---

## Qué es autoritativo

Esto es lo primero que hay que saber antes de tocar nada:

| Carpeta | Papel | ¿La leen los scripts? |
|---|---|---|
| `data/` | **Fuente de verdad.** Todo lo que aparece en la memoria se calcula desde aquí | Sí |
| `results/` | Copia curada y organizada por línea de trabajo, para lectura humana | **No** |
| `figures/` | Salida generada. Se sobrescribe en cada ejecución | Escritura |
| `generated_metrics.tex` | Salida generada: macros LaTeX con las cifras del documento | Escritura |
| `reference/generated_metrics.expected.tex` | Congelado: las cifras tal y como se publicaron | Solo comparación |

**No edites a mano `figures/`, `generated_metrics.tex` ni `MANIFEST.csv`.** Se regeneran.

### Dos campañas, no confundirlas

| Campaña | Ventana | Dónde | Uso |
|---|---|---|---|
| `final_60m80m_test` | 60M calentamiento + 20M medidos | `data/` | **La de la memoria.** Todas las cifras publicadas |
| `classic` | 20M + 20M | `results/mlp_lightgbm/*_campana_classic.csv`, `data/classic_champsim_*.csv` | Campaña previa, exploratoria |

Las dos existen a propósito y dan números distintos. Si una cifra no cuadra con la memoria,
lo más probable es que venga de la campaña `classic`.

---

## Mapa: de la memoria al fichero

Cada figura y cada tabla del documento, con su origen.

### Figuras

| Memoria | Fichero generado | Datos de partida |
|---|---|---|
| Figura 2.2 | `figures/diagram_ppf.pdf` | Diagrama, dibujado por código |
| Figura 2.3 | `figures/diagram_pythia.pdf` | Diagrama, dibujado por código |
| Figura 2.4 | `figures/diagram_mab.pdf` | Diagrama, dibujado por código |
| Figura 4.2 | `figures/diagram_dagger.pdf` | Diagrama, dibujado por código |
| Figura 5.1 | `figures/fig_online_speedup.pdf` | **campaña final** |
| Figura 5.2 | `figures/fig_dagger_data.pdf` | `data/ml_models_progress.csv` |
| Figura 5.3 | `figures/fig_dagger_offline_online.pdf` | `data/ml_models_progress.csv`, `data/dagger_offline_metrics.csv` |
| Figura 5.4 | `figures/fig_dagger_same_traces.pdf` | **campaña final** |
| Figura 5.5 | `figures/fig_threshold_matrix.pdf` | `data/ml_best_validation_by_iteration_policy.csv` |
| Figura 5.6 | `figures/fig_lgbm_shap.pdf` | `data/ml_lgbm_treeshap.csv` |
| Figura 5.7 | `figures/fig_llm_methods_12.pdf` | **campaña final** |
| Figura 5.8 | `figures/fig_all_methods_by_trace.pdf` | `data/all_methods_by_trace_speedup.csv` |
| Figura 5.9 | `figures/fig_intel_l2_history.pdf` | `data/intel_l2_history.csv` |

**campaña final** = `data/final_60m80m_by_trace.csv` y `data/final_60m80m_summary.csv`.

La Figura 2.1 y la Figura 4.1 se dibujan dentro del propio documento LaTeX y no dependen
de este paquete.

### Tablas

Las cifras de las tablas no están escritas a mano en la memoria: entran como macros LaTeX
desde `generated_metrics.tex`, que produce `scripts/build_figures.py`.

| Memoria | Datos de partida |
|---|---|
| Tabla 5.1 (resumen online) | campaña final |
| Tabla 5.2 (métricas offline DAgger) | `data/dagger_offline_metrics.csv` |
| Tabla 5.3 (12 trazas, actividad) | campaña final |
| Tabla 5.4 (comparación principal) | campaña final |
| Tabla 5.5 (coste hardware) | Trabajos originales de cada política y estructuras evaluadas aquí |
| Tabla A.1 (campañas) | `data/simulation_time_summary.csv` |

### Cuidado con los ficheros de reserva

`data/dagger_12_common_metrics.csv` y `data/dagger_same_traces_compare.csv` contienen valores
muy parecidos a los publicados, pero **no son la fuente de las cifras de la memoria**.
`scripts/build_figures.py` los usa solo como reserva, cuando `data/final_60m80m_by_trace.csv`
no existe (`final_results_available()`). Con el repositorio completo esa reserva nunca se activa.

Consecuencia práctica: si editas uno de esos dos ficheros no cambiará ninguna cifra y
`verify_reproduction.sh` seguirá pasando. Para tocar los números publicados hay que editar
los ficheros de la campaña final.

Las tablas 2.x, 3.x y 4.x son descriptivas y no consumen datos del artefacto.

---

## Organización

```
data/          fuente de verdad: CSV/JSON de los que salen todas las cifras
results/       misma información agrupada por línea de trabajo, para leer
  online/        PPF, Pythia, uMAMA
  mlp_lightgbm/  DAgger, MLP, LightGBM (+ copia ligera del run principal)
  llm/           línea de agentes LLM y logs metodológicos
prefetchers/   código y modelos propios
  LLM/           prebuscador generado por los agentes (C++)
  MLP/           checkpoint PyTorch y cabecera C++ exportada
  LightGBM/      modelo tabular de contraste
scripts/       generación de figuras, métricas, manifiesto y verificación
figures/       salida generada
reference/     cifras congeladas tal como se publicaron
MANIFEST.csv   tamaño y SHA-256 de cada fichero
```

---

## Los tres experimentos

| Línea | Aprende | Infiere | Qué se ejecuta en el procesador |
|---|---|---|---|
| Políticas online (PPF, Pythia, uMAMA) | online | online | política adaptativa |
| Offline (MLP, LightGBM vía DAgger) | offline | online | modelo con parámetros fijos |
| Agentes LLM | offline | offline | prebuscador generado, sin inferencia de IA |

Resultado principal, IPC geométrico sobre 12 trazas de DPC-4, ventana 60M–80M:
uMAMA 9,3 % · MLP 9,1 % · Pythia 7,6 % · LLM 3,5 % · SPP+PPF −2,8 %.
MLP alcanza casi el mismo rendimiento que uMAMA emitiendo diez veces menos prebúsquedas,
con 52,5 % de precisión frente al 5,3 % de uMAMA.

---

## Qué se comprueba y qué no

`scripts/verify_reproduction.sh` regenera las métricas y las compara byte a byte con
`reference/generated_metrics.expected.tex`. Sale con código 0 si coinciden y 1 ante cualquier
divergencia. Cubre todas las cifras numéricas que la memoria toma del artefacto: IPC geométrico
y mejora por método, prebúsquedas emitidas y útiles, precisión, cobertura, recuentos de
victorias por traza y agregados por familia de carga.

Las figuras se regeneran con el mismo contenido, pero los PDF no son idénticos byte a byte
entre máquinas porque el rasterizado depende de la versión de matplotlib y de las fuentes
instaladas. Por eso la verificación automática se hace sobre las métricas y no sobre el binario
de las figuras.

### Entorno

La campaña original se ejecutó con Python 3.13. La verificación se ha comprobado también con
Python 3.11 y 3.14, matplotlib 3.10, numpy 2.4 y pandas 3.0, con métricas idénticas. `requirements.txt`
no fija versiones porque el resultado no depende de ellas dentro de esos rangos; si una versión
futura introdujese divergencias, `verify_reproduction.sh` las detectaría.

---

## Alcance

Se incluye el código propio, los modelos ligeros, los CSV que alimentan las figuras, resultados
resumidos y logs de entrenamiento e iteración.

**No** se incluyen las trazas de ChampSim (por tamaño y condiciones de distribución), los
repositorios externos completos ni las salidas brutas de simulación. Repetir la campaña completa
requiere un entorno externo con ChampSim y las trazas de DPC-4. Este paquete permite auditar el
código incluido y reconstruir las figuras y las cifras del documento a partir de los datos
empaquetados.

## Disposición de carpetas

`scripts/build_figures.py` funciona en dos disposiciones sin editarlo:

- artefacto autónomo (este repositorio): lee de `data/` y `results/`, escribe en `figures/` y `generated_metrics.tex`;
- paquete de entrega del TFM: lee de `02_artifacts/` y escribe además dentro de `00_latex_src/` cuando ese directorio existe.

El directorio de datos puede forzarse con la variable de entorno `TFM_DATA_DIR`.
