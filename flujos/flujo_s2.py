"""Sesión 2 · Flujo con estado: historia -> criterios -> casos -> plan aprobado -> código verificado.

Uso:  python -m flujos.flujo_s2 historias/HU-01-registrar-empleado.md
"""
import operator
import sys
from pathlib import Path
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from agentes import desarrollador
from agentes.analista import generar_criterios, preguntas_abiertas
from agentes.base import hu_de
from agentes.disenador_pruebas import disenar_casos
from flujos.verificacion import verificar_app
from flujos.util import crear_checkpointer, dibuja_grafo
MAX_INTENTOS = 2


class Estado(TypedDict, total=False):
    historia: str
    hu: str
    criterios: str
    preguntas: list[str]
    casos: str
    plan: str
    comentarios: str
    plan_aprobado: bool
    intentos: int
    app_ok: bool
    log_verificacion: str
    costo_usd: Annotated[float, operator.add]   # reducer: cada nodo suma su costo
    bitacora: Annotated[list[str], operator.add]


# --- Nodos -----------------------------------------------------------------
def analizar(s: Estado) -> Estado:
    ruta = generar_criterios(Path(s["historia"]))                      # Agente 1
    return {"hu": hu_de(Path(s["historia"])), "criterios": str(ruta), "intentos": 0, "costo_usd": 0.0,
            "preguntas": preguntas_abiertas(ruta.read_text(encoding="utf-8")),
            "bitacora": [f"Criterios escritos en {ruta.name}"]}


def despues_de_analizar(s: Estado) -> Literal["pedir_aclaracion", "disenar_casos"]:
    return "pedir_aclaracion" if s["preguntas"] else "disenar_casos"


def pedir_aclaracion(s: Estado) -> Estado:
    respuesta = interrupt({"preguntas": s["preguntas"],
                           "pregunta": "Hay preguntas abiertas. ¿Continuar de todos modos? (si/no)"})
    return {"bitacora": [f"Preguntas abiertas: la persona respondió '{respuesta}'"],
            "comentarios": "" if respuesta.strip().lower() == "si" else "detener"}


def despues_de_aclarar(s: Estado) -> Literal["disenar_casos", "__end__"]:
    return END if s.get("comentarios") == "detener" else "disenar_casos"


def disenar(s: Estado) -> Estado:
    ruta = disenar_casos(Path(s["criterios"]))                         # Agente 2
    return {"casos": str(ruta), "bitacora": [f"Casos de prueba escritos en {ruta.name}"]}


def planificar(s: Estado) -> Estado:
    plan, costo = desarrollador.planificar(s["hu"], s.get("comentarios", ""))   # Agente 3, solo lectura
    return {"plan": plan, "costo_usd": costo}


def aprobar_plan(s: Estado) -> Estado:
    decision = interrupt({"plan": s["plan"], "pregunta": "¿Aprobar el plan? Escribe 'si' o tus comentarios"})
    if decision.strip().lower() == "si":
        return {"plan_aprobado": True, "bitacora": ["Plan aprobado por una persona"]}
    return {"plan_aprobado": False, "comentarios": decision, "bitacora": [f"Plan rechazado: {decision}"]}


def despues_de_aprobar(s: Estado) -> Literal["construir", "planificar"]:
    return "construir" if s["plan_aprobado"] else "planificar"


def construir(s: Estado) -> Estado:
    errores = "" if s.get("app_ok", True) else s.get("log_verificacion", "")
    resumen, costo = desarrollador.construir(s["hu"], s["plan"], errores)      # Agente 3, edición
    return {"intentos": s["intentos"] + 1, "costo_usd": costo, "bitacora": [f"Construcción {s['intentos'] + 1}"]}


def verificar(s: Estado) -> Estado:
    ok, log = verificar_app()                                          # determinista, sin LLM
    return {"app_ok": ok, "log_verificacion": log, "bitacora": [f"Verificación: {'OK' if ok else 'FALLA'}"]}


def despues_de_verificar(s: Estado) -> Literal["construir", "fin"]:
    return "construir" if not s["app_ok"] and s["intentos"] < MAX_INTENTOS else "fin"


def fin(s: Estado) -> Estado:
    print(f"\n=== {s['hu']} · app {'LISTA' if s.get('app_ok') else 'ESCALAR A UNA PERSONA'} "
          f"· {s.get('costo_usd', 0):.2f} USD ===")
    for linea in s.get("bitacora", []):
        print(" -", linea)
    return {}


def construir_grafo():
    g = StateGraph(Estado)
    for nombre, fn in [("analizar", analizar), ("pedir_aclaracion", pedir_aclaracion),
                       ("disenar_casos", disenar), ("planificar", planificar), ("aprobar_plan", aprobar_plan),
                       ("construir", construir), ("verificar", verificar), ("fin", fin)]:
        g.add_node(nombre, fn)
    g.add_edge(START, "analizar")
    g.add_conditional_edges("analizar", despues_de_analizar)
    g.add_conditional_edges("pedir_aclaracion", despues_de_aclarar)
    g.add_edge("disenar_casos", "planificar")
    g.add_edge("planificar", "aprobar_plan")
    g.add_conditional_edges("aprobar_plan", despues_de_aprobar)
    g.add_edge("construir", "verificar")
    g.add_conditional_edges("verificar", despues_de_verificar)
    g.add_edge("fin", END)
    app = g.compile(checkpointer=crear_checkpointer(), name="s2")   # name: prefijo del thread_id
    #YA DIBUJA EL GRAFO ! 
    dibuja_grafo(app,"flujo_s2")
    return app


def _preguntar(texto: str, opciones: tuple[str, ...] = ()) -> str:
    """Pregunta en la terminal hasta recibir una respuesta no vacía y, si hay opciones, una de ellas."""
    while True:
        respuesta = input(texto).strip()
        if not respuesta:
            print("La respuesta no puede ir vacía.")
        elif opciones and respuesta.lower() not in opciones:
            print(f"Responde {' o '.join(opciones)}.")
        else:
            return respuesta.lower() if opciones else respuesta


def ejecutar(app, historia: str) -> dict:
    """Corre el flujo y atiende cada pausa humana desde la terminal.

    El hilo (thread_id) es el nombre del flujo más el de la historia, por ejemplo
    «s4:HU-10-solicitar-vacaciones», así que una pausa de flujo_s3 no se ofrece al correr flujo_s4.
    Su estado se guarda en checkpoints/flujo.db (ver flujos.util.crear_checkpointer). Regla para retomar:
    - Si el hilo tiene una pausa pendiente (por ejemplo, la aprobación del plan), se pregunta en la
      terminal si se retoma. Con «si», el flujo sigue desde esa pausa sin repetir los nodos que ya
      terminaron, y la bitácora registra «Ejecución retomada desde el checkpoint».
    - Con «no», o si no hay pausa pendiente, el hilo se borra y la ejecución empieza de cero. Así la
      bitácora y el costo, que se acumulan, no se mezclan con la ejecución anterior.
    """
    hilo = f"{app.name}:{Path(historia).stem}"
    cfg = {"configurable": {"thread_id": hilo}}
    pendientes = [i for tarea in app.get_state(cfg).tasks for i in tarea.interrupts]
    retomar = bool(pendientes) and _preguntar(
        f"Hay una ejecución en pausa de {hu_de(Path(historia))}. ¿Retomar? (si/no): ", ("si", "no")) == "si"
    if retomar:
        out = {"__interrupt__": pendientes}             # se vuelve a mostrar la pausa guardada
    else:
        app.checkpointer.delete_thread(hilo)            # de cero: nada de la ejecución anterior
        out = app.invoke({"historia": str(Path(historia).resolve())}, cfg)
    while "__interrupt__" in out:
        pausa = out["__interrupt__"][0].value
        for clave in ("preguntas", "plan", "diagnostico"):
            if clave in pausa:
                print(f"\n--- {clave.upper()} ---\n{pausa[clave]}")
        aviso = {"bitacora": ["Ejecución retomada desde el checkpoint"]} if retomar else None
        out = app.invoke(Command(resume=_preguntar(pausa["pregunta"] + ": "), update=aviso), cfg)
        retomar = False                                 # el aviso se escribe una sola vez
    return out


if __name__ == "__main__":
    #NO NECESITA COLOCAR --grafo, ya lo hace
    ejecutar(construir_grafo(), sys.argv[1])
