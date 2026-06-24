# Contexto inicial de la línea LLM

Este fichero resume el contexto usado para iniciar la primera iteración de la línea LLM. No reproduce todas las conversaciones. Su objetivo es dejar constancia del punto de partida metodológico.

## Objetivo operativo

Diseñar y evaluar una política de prebúsqueda L2 en ChampSim a partir de un repositorio de trabajo ya preparado. La política debía ejecutarse sobre trazas representativas, producir resultados cuantitativos y documentar cada iteración.

El contexto inicial fijaba además restricciones operativas: la política debía actuar en L2, mantener fija la prebúsqueda L1, respetar un presupuesto de estado persistente inferior a 32 KiB y seguir el protocolo de simulación usado en la campaña, con 20 millones de instrucciones de calentamiento y 20 millones de medición.

## Material proporcionado

- Código fuente de ChampSim y del prefetcher LLM.
- Resultados previos de PPF, Pythia, uMAMA y baseline sin prebúsqueda L2.
- CSV de métricas agregadas y por traza.
- Logs de iteraciones previas cuando existían.
- Estructura de carpetas del repositorio `champsim_llm`.
- Carpeta de papers y referencias útiles para evitar propuestas desligadas del estado del arte.
- Restricción de documentar cambios, resultados y decisiones.

## Criterio de evaluación

La política generada debía compararse con referencias online existentes sobre las mismas trazas cuando fuera posible. La métrica principal era IPC geométrico. También se registraban actividad de prebúsqueda, precisión agregada y número de prebúsquedas emitidas y útiles.

## Alcance

El experimento se trató como una línea exploratoria. El interés no era solo obtener una política concreta, sino observar si los agentes podían sostener un ciclo trazable de propuesta, modificación, ejecución y análisis.
