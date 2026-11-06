# Decisiones · HU-10 Solicitar vacaciones

## 1. ¿Qué pasos son workflow y cuáles son agente?

El grafo de LangGraph (`flujos/flujo_s4.py`) es workflow: el código fija el orden, los reintentos, el tope de 2 ciclos de triage y las pausas para una persona. El filtro de la historia y la verificación son pasos fijos. Dentro de ese orden, cada etapa es un agente que decide qué leer y qué escribir: analista y diseñador (API de Anthropic con herramientas), desarrollador, despliegue y automatizador (Claude Code con permisos por rol) y triage (decide a quién regresar una falla). Ejemplo: el analista es agente, pero si reintenta lo decide `validar_gherkin`.

## 2. ¿Cómo se validó cada salida? ¿Qué atrapó algún validador?

Tres niveles. Esquema: Gherkin con `# language: es` y Dado/Cuando/Entonces; casos con el modelo Pydantic `CasoPrueba` dentro de la herramienta `guardar_casos`. Reglas: para HU-10, `validar_gherkin` exige los 8 mensajes de error literales, el camino feliz, usar justo los días que quedan, pedir uno de más y un festivo bien contado; mensajes y festivos se leen de `contexto/`. Pruebas: arranque y build, luego pytest y Playwright. En la ejecución final el validador rechazó el intento 1 del analista porque faltaban el escenario del año fuera de la tabla y el de usar justo los días que quedan (log de la ejecución final, líneas 11 a 13); el intento 2 pasó. Resultado: 20 casos, 42 pruebas pasan, estado LISTA.

## 3. ¿Dónde intervine y qué vi para decidir?

En la aprobación del plan. En la ejecución 2 rechacé el plan porque identificaba al empleado por `numero_empleado` (EMP-0007), copiando HU-03, cuando el contrato usa el `id` numérico; las pruebas de la API habrían dado 404. En la ejecución final el plan ya devolvía el botón solo a empleados activos, pero no decía si había comparado el código con los criterios y casos nuevos. Lo rechacé para pedirlo; el segundo plan comparó los 20 casos, confirmó el `id` y el alias, y lo aprobé. En la ejecución 1 el analista preguntó si dos solicitudes pueden traslaparse; seguí, porque ni las reglas ni la tabla de errores lo contemplan.

## 4. ¿Qué arquitectura usa la fábrica y por qué no otra?

Un orquestador con flujo fijo en LangGraph: el supervisor es código, no un modelo. El orden de las etapas no cambia entre historias; un supervisor con LLM agregaría costo y variación sin ganar nada. Despliegue y automatizador corren en paralelo y su estado se une con reductores. No usé red ni pizarra: cada agente tiene un contrato de entrada y salida y no necesitan negociar. Los checkpoints van en SQLite (`SqliteSaver`, un hilo por flujo e historia), así la pausa del plan sobrevive a cerrar la terminal.

## 5. ¿Qué corregí en el agente y por qué no en su resultado?

En la ejecución 2 una prueba E2E buscaba el botón de vacaciones en un empleado de baja; la convención solo lo da a activos. El triage culpó dos veces al desarrollador y este mostró el botón a todos. El error nació en el analista (un paso de pantalla imposible en el escenario del 409) y lo propagó el triage (no comparaba la prueba con `CLAUDE.md`). Corregí a los dos: el analista prueba por API lo que la pantalla no permite, y el triage manda la falla al automatizador cuando la prueba contradice la convención. En la ejecución final el escenario del 409 quedó solo por API, no hubo ciclos de triage y el botón volvió a ser solo para activos. No edité `TablaEmpleados.jsx` a mano: la auditoría lo habría mostrado y la fábrica habría repetido el error en la siguiente historia.
