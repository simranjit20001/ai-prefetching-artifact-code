# Instrucciones resumidas de agentes LLM

Este documento recoge las reglas metodológicas usadas para la línea LLM. Se conserva una versión resumida porque resulta más útil para auditoría académica que una transcripción completa de mensajes.

## Reglas de trabajo

- Revisar el contexto antes de modificar código.
- Formular una hipótesis de cambio antes de implementarla.
- Editar únicamente los módulos relacionados con la política de prebúsqueda.
- Ejecutar o preparar evaluaciones con trazas definidas.
- Registrar resultados en CSV o logs reutilizables.
- Documentar la interpretación de cada iteración.
- No considerar una mejora como válida sin medición empírica.

## Ciclo de iteración

1. Leer resultados y código disponible.
2. Proponer una modificación de política.
3. Implementar el cambio en el prefetcher.
4. Ejecutar la evaluación o dejarla preparada.
5. Comparar IPC y actividad de prebúsqueda.
6. Registrar la decisión para la siguiente iteración.

## Supervisión experimental

La supervisión se limitó a fijar el objetivo experimental, mantener separados los roles de implementación y revisión, y corregir decisiones operativas que afectaban a la ejecución, especialmente la necesidad de paralelizar campañas cuando ejecutar trazas de forma secuencial era demasiado costoso.
