# Logs metodológicos de la línea LLM

Esta carpeta documenta la línea LLM sin copiar todas las interacciones.

## Criterio

Se conserva:

- el contexto inicial de trabajo;
- un resumen de instrucciones del sistema de agentes;
- la estructura relevante del repositorio `champsim_llm`;
- la localización del código final del prefetcher generado.

No se conservan todas las conversaciones ni todos los mensajes intermedios. Para auditar el método, el contexto inicial, las reglas de iteración y la estructura del sistema son más útiles que una transcripción larga.

## Contenido

- `initial_context.md`: resumen del contexto inicial usado para arrancar la iteración 1.
- `agent_instructions_summary.md`: instrucciones operativas resumidas.
- `folder_structure_relevant.txt`: estructura relevante del repositorio LLM.
- `../../prefetchers/LLM/`: código final del prefetcher LLM.

Nota metodológica. Algunos ficheros internos usan terminología operativa propia del experimento. En el documento principal esa terminología se resume como búsqueda offline de diseños evaluados en ChampSim.
