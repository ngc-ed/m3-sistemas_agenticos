"""Sesión 2 · Agente 3, desarrollador: requisitos -> base de datos, API y front-end, con Claude Code.

Uso:  python -m agentes.desarrollador HU-01
"""
import shutil
import sys

from agentes.base import APP, RAIZ, SALIDA
from agentes.claude_code import EDICION, SOLO_LECTURA, ejecutar_claude_code

INSTRUCCIONES = """Eres el desarrollador full stack del equipo. Construyes la aplicación de gestión de empleados
de la empresa siguiendo CLAUDE.md al pie de la letra (stack, puertos y data-testid).
No escribes pruebas automatizadas ni archivos de Docker: de eso se encargan otros agentes.
Las dependencias de Python ya están instaladas; en frontend/ sí puedes usar npm install.
Los data-testid y los mensajes se copian de CLAUDE.md (copia de contexto/convenciones_app.md) letra por letra;
no inventas ninguno.

En vacaciones (HU-10):
- Los días hábiles se calculan en el backend, con la tabla de festivos de 2026 y 2027 de las reglas de negocio
  (contexto/reglas_negocio.md, te llegan en el prompt).
- Las validaciones siguen el orden de la tabla de errores de CLAUDE.md: se devuelve el primer error que aplique.
- Agregas la tabla vacaciones y, si falta, el campo fecha_ingreso, sin cambiar el comportamiento de HU-01 a HU-03.
- La pantalla muestra en vacaciones-mensaje el detail exacto que devuelve la API, o el mensaje de éxito exacto.
- El botón vacaciones-abrir-{empleado_id} solo aparece en empleados activos.
- El POST responde dias_restantes y el GET responde dias_disponibles. Si no se manda anio, se usa el año en curso."""

ESCRITURA = ["backend/*", "frontend/*"]
PROGRAMAS = {"cd", "ls", "cat", "mkdir", "npm", "npx", "node", "python", "python3", "curl", "sleep", "kill"}


def preparar_app() -> None:
    """Crea app/ y le copia las convenciones como CLAUDE.md (la memoria de proyecto de Claude Code)."""
    APP.mkdir(exist_ok=True)
    shutil.copy(RAIZ / "contexto" / "convenciones_app.md", APP / "CLAUDE.md")


def requisitos(hu: str) -> str:
    carpeta = SALIDA / hu
    return (f"## Reglas de negocio\n{(RAIZ / 'contexto' / 'reglas_negocio.md').read_text(encoding='utf-8')}\n"
            f"## Criterios de aceptación de {hu}\n{(carpeta / 'criterios.feature').read_text(encoding='utf-8')}\n"
            f"## Casos de prueba que deberán pasar\n{(carpeta / 'casos_prueba.json').read_text(encoding='utf-8')}")


def planificar(hu: str, comentarios: str = "") -> tuple[str, float]:
    """Solo lectura: Claude Code revisa app/ y propone un plan, sin tocar archivos."""
    preparar_app()
    prompt = (f"{requisitos(hu)}\n\nRevisa el código que ya existe en esta carpeta y propone un plan para "
              f"implementar {hu}: modelo de datos, endpoints, componentes de React y data-testid. "
              "No escribas código. Responde solo con el plan en Markdown, en menos de 40 líneas.")
    if comentarios:
        prompt += f"\n\nComentarios de la persona que revisó tu plan anterior:\n{comentarios}"
    return ejecutar_claude_code(prompt, agente="desarrollador-plan", cwd=APP, herramientas=SOLO_LECTURA,
                                escritura=[], programas=set(), instrucciones=INSTRUCCIONES)


def construir(hu: str, plan: str, errores: str = "") -> tuple[str, float]:
    """Edición: Claude Code implementa el plan aprobado en backend/ y frontend/."""
    preparar_app()
    prompt = (f"{requisitos(hu)}\n\n## Plan aprobado\n{plan}\n\nImplementa {hu} siguiendo el plan aprobado. "
              "Al terminar, comprueba que el backend arranca (`python -m uvicorn main:app` desde backend/) "
              "y que `npm run build` funciona en frontend/. Responde con un resumen de los archivos que cambiaste.")
    if errores:
        prompt += f"\n\n## La verificación anterior falló; corrige esto\n{errores}"
    return ejecutar_claude_code(prompt, agente="desarrollador", cwd=APP, herramientas=EDICION,
                                escritura=ESCRITURA, programas=PROGRAMAS, instrucciones=INSTRUCCIONES)


if __name__ == "__main__":
    hu = sys.argv[1]
    plan, _ = planificar(hu)
    print("\n--- PLAN ---\n" + plan)
    if input("\n¿Aprobar y construir? (si/no): ").strip().lower() == "si":
        resumen, _ = construir(hu, plan)
        print("\n--- RESUMEN ---\n" + resumen)
