"""Sesión 4 · Triage: ante pruebas fallidas, decide qué agente debe corregir.

Es el supervisor del flujo E2E: no corrige nada, solo enruta con una justificación.
"""
import os
from typing import Literal

from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel

from agentes.base import RAIZ, SALIDA


class Diagnostico(BaseModel):
    responsable: Literal["desarrollador", "automatizador", "despliegue"]
    causa: str          # qué falló, en una o dos frases
    criterio: str       # escenario de aceptación que se usa como referencia
    instruccion: str    # qué debe corregir el responsable


PROMPT = """Eres líder técnico. Unas pruebas automatizadas fallaron. Decide quién debe corregir:
- "desarrollador": la aplicación no cumple un criterio de aceptación.
- "automatizador": la prueba contradice el criterio, usa un selector incorrecto o es frágil.
- "despliegue": la aplicación no responde (conexión rechazada, 502, contenedor caído).

Antes de culpar al desarrollador, compara lo que pide la prueba con CLAUDE.md (convenciones de la app, abajo).
Si la prueba pide algo que la convención no permite (por ejemplo, el botón de vacaciones, que solo tienen los
empleados activos, usado con un empleado de baja), la falla es de la prueba: responsable "automatizador".

Qué manda cuando chocan:
1. Si un criterio o una prueba contradice CLAUDE.md, manda CLAUDE.md y la falla va al "automatizador".
2. En los demás casos manda el criterio de aceptación: si la prueba y la aplicación no coinciden,
   gana quien siga el criterio.

## CLAUDE.md (convenciones de la app)
{convenciones}

## Criterios de aceptación
{criterios}

## Pruebas fallidas
{fallos}"""


def diagnosticar(hu: str, fallos: str) -> Diagnostico:
    llm = ChatAnthropic(model=os.environ["MODEL"], max_tokens=2000)
    criterios = (SALIDA / hu / "criterios.feature").read_text(encoding="utf-8")
    # El original del que app/CLAUDE.md es copia: así no depende de un archivo que vive dentro de app/
    convenciones = (RAIZ / "contexto" / "convenciones_app.md").read_text(encoding="utf-8")
    return llm.with_structured_output(Diagnostico).invoke(
        PROMPT.format(convenciones=convenciones, criterios=criterios, fallos=fallos[:6000]))
