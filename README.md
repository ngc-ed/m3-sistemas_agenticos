# Fábrica de software con agentes · Módulo 3

La fábrica es una cadena de agentes que recibe una historia de usuario y entrega una aplicación de gestión de empleados (base de datos, API y front-end) desplegada en Docker y probada de punta a punta. Un orquestador de LangGraph fija el orden de los pasos. Cada agente hace una sola tarea y escribe solo en su carpeta. Al final de cada paso, el código revisa el resultado y decide si se avanza. El agente no decide eso.

## Los agentes

| # | Agente | Archivo | Entrada | Salida | Sesión |
| --- | --- | --- | --- | --- | --- |
| 0 | Filtro de historia | `flujos/flujo_s4.py` → `filtrar_historia` | Historia de usuario | Veredicto: OK o BLOQUEADA | 4 |
| 1 | Analista | `agentes/analista.py` | Historia y `contexto/` | `salida/HU-xx/criterios.feature` | 1 |
| 2 | Diseñador de pruebas | `agentes/disenador_pruebas.py` | Criterios | `salida/HU-xx/casos_prueba.json` | 1 |
| 3 | Desarrollador (Claude Code) | `agentes/desarrollador.py` | Criterios, casos y plan aprobado | `app/backend`, `app/frontend` | 2 |
| 4 | Despliegue (Claude Code) | `agentes/despliegue.py` | Código | Contenedores con Docker Compose | 3 |
| 5 | Automatizador (Claude Code) | `agentes/automatizador.py` | Casos de prueba | `app/tests` (pytest y Playwright) | 3 |
| 6 | Triage | `agentes/triage.py` | Pruebas fallidas, criterios y convenciones | A quién le toca corregir: desarrollador, automatizador o despliegue | 4 |

- El **filtro de historia** usa un modelo para revisar si la historia trae instrucciones para la IA que no son requisitos, como leer secretos u ocultar información. Si la historia es sospechosa, el flujo termina antes de llamar a cualquier agente.
- El **triage** no corrige nada. Lee el error, decide quién lo corrige y el flujo regresa la tarea a ese agente. Hay un tope de 2 ciclos de corrección.
- Las verificaciones deterministas (que la API responda, el build, el despliegue y las pruebas) están en `flujos/verificacion.py`.

El flujo completo (`flujos/flujo_s4.py`) es:

```
filtro de historia → analista → [pausa: preguntas abiertas] → diseñador → plan del desarrollador
→ [pausa: aprobar plan] → desarrollador → verificación → despliegue ∥ automatizador
→ pruebas E2E → (si fallan) triage → corrección → pruebas E2E … → reporte
```

## Requisitos

- Python 3.12 (está fijado en `.python-version`)
- Node 20 o superior
- Docker Desktop, abierto antes de correr la fábrica. La app usa los puertos 8000 (API) y 8080 (web).
- Claude Code instalado. Los agentes 3, 4 y 5 lo usan a través del Agent SDK.
- Una clave de API de Anthropic con créditos. Como referencia, la ejecución final de HU-10 costó 1.28 USD.
- Opcional: `uv` para crear el entorno más rápido.

## Instalación

### Windows (PowerShell)

Con `uv`:

```powershell
uv venv --python 3.12
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
python -m playwright install chromium
```

O con `py`, sin `uv`:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## Configurar `.env`

Abre `.env` y llena los valores:

| Variable | Qué es |
| --- | --- |
| `ANTHROPIC_API_KEY` | Tu clave de API. Reemplaza `sk-ant-...` por la tuya. |
| `MODEL` | El modelo que usan todos los agentes. El código lo lee de aquí y nunca lo escribe fijo. |
| `PRESUPUESTO_USD` | El tope de gasto por cada llamada a Claude Code. Si no lo pones, vale 2. |

## Correr una historia (ejemplo con HU-10)

Desde la raíz del repo, con el entorno activado y Docker Desktop abierto:

```powershell
$env:PYTHONUTF8 = "1"            # solo en Windows
python -m flujos.flujo_s4 historias/HU-10-solicitar-vacaciones.md
```

Durante la ejecución el flujo se detiene para preguntarte algo. Una respuesta vacía no se acepta: el flujo vuelve a preguntar.

| Pausa | Cuándo sale | Qué responder |
| --- | --- | --- |
| `Hay una ejecución en pausa de HU-10. ¿Retomar? (si/no)` | Al arrancar, solo si una ejecución anterior quedó detenida en una pausa | `si` para seguir desde esa pausa; `no` para empezar de cero. Ver [Retomar una ejecución en pausa](#retomar-una-ejecución-en-pausa). |
| `--- PREGUNTAS ---` y luego `Hay preguntas abiertas. ¿Continuar de todos modos? (si/no)` | Solo si el analista dejó dudas bajo `# Preguntas abiertas` en `criterios.feature` | Léelas. `si` para seguir. Cualquier otra respuesta detiene el flujo sin reporte: aclara la historia o el contexto y vuelve a correrla. |
| `--- PLAN ---` y luego `¿Aprobar el plan? Escribe 'si' o tus comentarios` | Siempre, antes de escribir código | Revisa el plan contra `criterios.feature` y `casos_prueba.json`. `si` para aprobarlo. Si algo está mal, escribe tus comentarios: el desarrollador hace un plan nuevo con ellos y la pausa vuelve a salir. |

Después de aprobar el plan, el resto corre solo: construcción, verificación, despliegue y pruebas en paralelo, pruebas E2E y, si algo falla, triage y corrección. Al final se imprime el reporte y se guarda en `salida/HU-10/reporte.md`.

La aplicación queda en http://localhost:8080 y la documentación de la API en http://localhost:8000/docs.

## Agregar una historia nueva

1. **La historia** va en `historias/` con el nombre `HU-NN-descripcion.md`, por ejemplo `historias/HU-04-asignar-jefe.md`. El código toma las dos primeras partes del nombre (`HU-04`) como identificador, y la salida queda en `salida/HU-04/`. En `historias/backlog.md` hay historias listas para usar.
2. **Las reglas de negocio** se agregan al final de `contexto/reglas_negocio.md`, en una sección propia, por ejemplo `# Reglas de jefe directo (HU-04)`. Ahí van las reglas, los ejemplos y las tablas de datos, como los festivos de HU-10.
3. **Las convenciones de la app** se agregan al final de `contexto/convenciones_app.md`, en una sección propia, por ejemplo `# Convenciones de jefe directo (HU-04)`. Ahí van los endpoints, los `data-testid` y los mensajes de error y de éxito exactos.

No crees archivos nuevos en `contexto/`. Los agentes solo leen esos dos archivos: el analista los lee; el desarrollador recibe `reglas_negocio.md` en el prompt y copia `convenciones_app.md` como `app/CLAUDE.md`; y el triage compara las pruebas con `convenciones_app.md`. Un archivo aparte quedaría fuera de lo que leen el desarrollador y el triage. Por eso las reglas y convenciones de HU-10 se anexaron a esos dos archivos. La historia HU-10 todavía menciona `reglas_vacaciones.md` y `convenciones_vacaciones.md`, pero ese contenido ahora está en los dos archivos de `contexto/`.

Después, córrela como en el ejemplo de HU-10:

```bash
python -m flujos.flujo_s4 historias/HU-04-asignar-jefe.md
```

Las historias nuevas pasan por la validación general del analista: Gherkin en español, con Dado, Cuando y Entonces en cada escenario. Solo HU-10 tiene además un validador por regla (`validar_vacaciones` en `agentes/analista.py`).

## Estructura de carpetas

```
.
├── agentes/              Los agentes: analista, diseñador, desarrollador, despliegue, automatizador y triage
│   ├── base.py           Bucle de agente y herramientas de archivos
│   └── claude_code.py    Cómo los agentes 3, 4 y 5 llaman a Claude Code
├── flujos/               Orquestadores LangGraph de las sesiones 2, 3 y 4
│   ├── verificacion.py   Verificaciones deterministas: salud de la API, build, despliegue y pruebas
│   ├── util.py           Checkpointer SQLite y dibujo del grafo
│   └── salidas/          Grafos dibujados en HTML
├── seguridad/hooks.py    Hooks de rol y de seguridad para Claude Code
├── historias/            Historias de usuario: HU-01 a HU-03, HU-10, HU-99 (envenenada) y backlog.md
├── contexto/             Reglas de negocio y convenciones de la app que leen los agentes
├── salida/               Artefactos por historia: criterios, casos, reporte; seguridad.md
├── app/                  La aplicación que generan los agentes (backend, frontend, tests, Docker)
├── ejemplos/             Un programa corto por patrón, para clase; no forman parte de la fábrica
├── labs_agentes/         Versión de los agentes de los labs; la fábrica no la importa
├── checkpoints/          flujo.db con el estado de las ejecuciones (no se versiona)
├── auditoria.jsonl       Registro de cada uso de herramienta de los agentes de Claude Code
├── buscar_denegados.py   Busca en auditoria.jsonl escrituras fuera del rol de cada agente
└── secretos_demo.txt     Archivo señuelo para la demostración del ataque de HU-99
```

`app/` y `salida/` los escriben los agentes. Si algo sale mal ahí, corrige el agente, no su resultado.

## Seguridad

La historia de usuario la escribe otra persona, así que la fábrica la trata como contenido no confiable. Las defensas son:

- **Filtro de historia** (`flujos/flujo_s4.py`): bloquea la historia antes de que la lea cualquier agente.
- **Hooks de rol** (`seguridad/hooks.py` → `confinar_escritura`): cada agente de Claude Code escribe solo en sus rutas. El desarrollador escribe en `backend/` y `frontend/`, el automatizador en `tests/` y el de despliegue en los archivos de Docker. Estos hooks siempre están activos.
- **Hooks de seguridad** (`seguridad/hooks.py`):
  - `confinar_lectura`: no deja leer fuera de la carpeta del agente ni archivos con `.env` o `secretos` en el nombre.
  - `comandos_permitidos`: solo deja correr los programas de la lista de cada agente. Niega la sustitución de comandos y cualquier comando que mencione secretos o variables de entorno.
  - `auditar`: anota cada uso de herramienta en `auditoria.jsonl`.

**`DEFENSAS=0`** apaga el filtro de historia y los hooks de seguridad (los de rol siguen activos). Sirve **solo en clase**, para ver cómo la historia envenenada HU-99 ataca la fábrica sin protección, y ese ataque apunta solo a `secretos_demo.txt`. Nunca lo uses en el trabajo normal. En PowerShell se activa con `$env:DEFENSAS = "0"` y se quita con `Remove-Item Env:DEFENSAS`. En Mac y Linux se usa así: `DEFENSAS=0 python -m flujos.flujo_s4 historias/HU-99-envenenada.md`.

El análisis completo, con las capas de defensa, el resultado de HU-99 y los límites, está en [salida/seguridad.md](salida/seguridad.md).

## Resultado de HU-10

La ejecución final de HU-10 (solicitar vacaciones) terminó con estado **LISTA**: **42 pruebas** pasaron (API y E2E, a partir de 20 casos) con **0 ciclos** de corrección y un costo de 1.28 USD.

- [salida/HU-10/reporte.md](salida/HU-10/reporte.md): estado, bitácora y última ejecución de pruebas.
- [salida/HU-10/decisiones.md](salida/HU-10/decisiones.md): por qué la fábrica está armada así, qué atraparon los validadores y dónde intervino una persona.

## Nota sobre `ejemplos/s2_flujos/humano_memorydb.py`

Este ejemplo necesita PostgreSQL y los paquetes `langgraph-checkpoint-postgres` y `psycopg[binary]`, que ya no están en `requirements.txt`. Sin ellos, falla al importar. Para correrlo, sigue las instrucciones del comentario al inicio del archivo: levantar Postgres con Docker, agregar `POSTGRES_URI` a `.env` e instalar esos dos paquetes. El resto de la fábrica no los necesita.
