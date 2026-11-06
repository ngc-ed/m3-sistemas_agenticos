# Historial de cambios

Armado a partir de `git log`. Las fechas van de la más reciente a la más antigua.

## 2026-11-06

### Agregado
- Ejecución final de HU-10 con estado LISTA: 42 pruebas pasan y 0 ciclos de triage (`salida/HU-10/reporte.md`).
- Prueba de seguridad con HU-99: el filtro de historia la bloquea (`salida/bloqueada/reporte.md`).
- Ejecución 2 de HU-10: backend, frontend y pruebas de vacaciones generados por los agentes; 47 pruebas pasan.
- Analista y diseñador imprimen los problemas del validador cuando rechazan un intento.
- Lab 4B con HU-99: prompt ingenuo contra endurecido y analista sin filtro (`salida/HU-99/criterios.feature`).
- Tabla de ataques y checklist de producción en `salida/seguridad.md`.

### Cambiado
- Criterios, casos y pruebas de HU-10 regenerados en la ejecución final (20 casos).
- Redacción más natural en `salida/HU-10/decisiones.md` y `salida/seguridad.md`.

### Corregido
- Analista: no escribe pasos de pantalla que la app no permite; esos escenarios se prueban solo por API.
- Triage: compara la prueba con `contexto/convenciones_app.md` antes de culpar al desarrollador.
- Pausas del flujo: no aceptan respuestas vacías y piden `si` o `no` donde aplica.
- Botón `vacaciones-abrir-{id}`: vuelve a mostrarse solo en empleados activos.

## 2026-11-05

### Agregado
- Checkpoints persistentes con `SqliteSaver` en `checkpoints/flujo.db`.
- Opción de retomar una ejecución en pausa al volver a correr el flujo.
- Validador de HU-10 por regla en el analista: mensajes exactos, festivos y tope de días.
- `.gitattributes` con finales de línea LF.

### Cambiado
- El `thread_id` incluye el nombre del flujo (`s2`, `s3`, `s4`) más el de la historia.
- `requirements.txt`: entra `langgraph-checkpoint-sqlite`; salen `langgraph-checkpoint-postgres`, `psycopg[binary]` y `chromium`.
- `checkpoints/` agregado a `.gitignore`.
- El analista hace 3 intentos en HU-10; las demás historias siguen con 2.
- Prompts de desarrollador, diseñador y automatizador con instrucciones de vacaciones (HU-10).
- El diseñador y el automatizador usan una `fecha_ingreso` fija tomada de los casos.

### Corregido
- Convenciones de vacaciones anexadas a `contexto/convenciones_app.md` en lugar de un archivo aparte.
- Referencias de contexto: las reglas de vacaciones apuntan a `contexto/reglas_negocio.md`.

## 2026-11-04

### Agregado
- Base de la fábrica con HU-01 a HU-03: agentes, flujos de las sesiones 2 a 4, hooks y app (labs 1 a 4).
- Historia HU-10 (solicitar vacaciones).
- Reglas de vacaciones y festivos de 2026 y 2027 en `contexto/reglas_negocio.md`.
