"""Sesión 1 · Agente 1, analista: historia de usuario -> criterios de aceptación en Gherkin.

Uso:  python -m agentes.analista historias/HU-01-registrar-empleado.md
"""
import re
import sys
from datetime import date, timedelta
from pathlib import Path

from agentes.base import RAIZ, SALIDA, ejecutar_agente, herramientas_archivos, hu_de, rel

SISTEMA = """Eres analista de producto en un equipo de software. Conviertes historias de usuario
en criterios de aceptación escritos en Gherkin, en español.

Cómo trabajas:
1. Lee la historia, contexto/reglas_negocio.md y contexto/convenciones_app.md (ahí están la API y los
   mensajes exactos). Copia los mensajes de error y de éxito letra por letra y escribe las fechas como AAAA-MM-DD.
2. Escribe {destino}. La primera línea es `# language: es` y usas las palabras clave
   Característica, Escenario, Dado, Cuando, Entonces, Y.
3. Incluye el camino feliz y un escenario de error por cada regla de negocio que aplique a ESTA historia.
4. Cada escenario se puede verificar desde la pantalla o la API: datos concretos, nada de «funciona bien».
5. Solo escribe pasos de pantalla si contexto/convenciones_app.md deja llegar a esa pantalla. Si la pantalla
   no ofrece esa acción, el escenario se prueba solo por API (la petición HTTP, el código y el `detail`).
   Ejemplo: solicitar vacaciones para un empleado de baja; solo los empleados activos tienen el botón
   `vacaciones-abrir-{{empleado_id}}`, así que ese escenario no lleva pasos de pantalla.
6. No inventes reglas. Si falta información, agrégala al final como comentarios bajo `# Preguntas abiertas`.
7. Responde al final con una sola línea: cuántos escenarios escribiste."""


def escenarios(gherkin: str) -> list[str]:
    return re.findall(r"^\s*Escenario:\s*(.+?)\s*$", gherkin, flags=re.MULTILINE)


def preguntas_abiertas(gherkin: str) -> list[str]:
    """Recibe el texto Gherkin y devuelve las preguntas bajo «# Preguntas abiertas» (lista vacía si no hay).

    Valida que «Ninguna», «No hay» o «N/A» en la primera línea cuenten como cero preguntas,
    para que el flujo no pause sin necesidad.
    """
    if "# Preguntas abiertas" not in gherkin:
        return []
    bloque = gherkin.split("# Preguntas abiertas", 1)[1]
    lineas = [l.lstrip("# -").strip() for l in bloque.splitlines() if l.strip().lstrip("#").strip()]
    # «Ninguna», «No hay», «N/A»... dicen que no hay preguntas; la nota puede seguir en otras líneas
    if lineas and re.match(r"(ninguna|ninguno|no hay|sin preguntas|n/?a)\b", lineas[0], flags=re.IGNORECASE):
        return []
    return lineas


def validar_gherkin(texto: str, hu: str = "") -> list[str]:
    """Evaluador determinista: devuelve los problemas encontrados; vacío = válido."""
    problemas = []
    if not texto.lstrip().startswith("# language: es"):
        problemas.append("La primera línea debe ser '# language: es'.")
    if "Característica:" not in texto:
        problemas.append("Falta 'Característica:'.")
    bloques = re.split(r"^\s*Escenario:", texto, flags=re.MULTILINE)[1:]
    if len(bloques) < 2:
        problemas.append("Se esperan al menos 2 escenarios (camino feliz y un error).")
    for i, bloque in enumerate(bloques, 1):
        for clave in ("Dado", "Cuando", "Entonces"):
            if not re.search(rf"^\s*{clave}\b", bloque, flags=re.MULTILINE):
                problemas.append(f"El escenario {i} no tiene '{clave}'.")
    if hu == "HU-10":                      # las demás historias se validan igual que antes
        problemas += validar_vacaciones(bloques)
    return problemas


# --- HU-10 · Vacaciones: todo se lee de contexto/, nada se escribe de memoria ---

def _leer_contexto(nombre: str) -> str:
    """Recibe el nombre de un archivo de contexto/ y devuelve su texto en UTF-8. No valida nada."""
    return (RAIZ / "contexto" / nombre).read_text(encoding="utf-8")


def errores_vacaciones() -> list[tuple[str, str, str]]:
    """(caso, código, detail) de la tabla «Errores: mensajes exactos» de convenciones_app.md, en su orden."""
    seccion = _leer_contexto("convenciones_app.md").split("## Errores: mensajes exactos", 1)[1].split("\n## ", 1)[0]
    filas = re.findall(r"^\|\s*(.+?)\s*\|\s*(\d{3})\s*\|\s*`(.+?)`\s*\|\s*$", seccion, flags=re.MULTILINE)
    if not filas:
        raise ValueError("No se pudo leer la tabla de errores de vacaciones en contexto/convenciones_app.md.")
    return filas


def mensaje_exito_vacaciones() -> str:
    """El mensaje de éxito exacto de convenciones_app.md, con sus marcadores N, M y AAAA."""
    # La línea es «Mensaje de éxito exacto en `vacaciones-mensaje`: `Solicitud registrada: ...`»: va después de los dos puntos
    return re.search(r"Mensaje de éxito exacto[^:]*:\s*`(.+?)`", _leer_contexto("convenciones_app.md")).group(1)


def festivos() -> set[date]:
    """Fechas de la tabla «Festivos oficiales» de reglas_negocio.md."""
    seccion = _leer_contexto("reglas_negocio.md").split("## Festivos oficiales", 1)[1]
    return {date.fromisoformat(f) for f in re.findall(r"\d{4}-\d{2}-\d{2}", seccion)}


def patron(mensaje: str) -> str:
    """Mensaje literal -> regex; los marcadores N, M y AAAA aceptan cualquier número (grupos en ese orden)."""
    return re.sub(r"\b(N|M|AAAA)\b", r"(\\d+)", re.escape(mensaje))


def dias_habiles(inicio: date, fin: date, feriados: set[date]) -> int:
    """Regla 3: cuenta inicio y fin; no cuentan sábados, domingos ni festivos."""
    return sum(1 for i in range((fin - inicio).days + 1)
               if (dia := inicio + timedelta(days=i)).weekday() < 5 and dia not in feriados)


def periodos(bloque: str) -> list[tuple[date, date]]:
    """Pares (inicio, fin) del mismo año formados con las fechas AAAA-MM-DD del escenario."""
    fechas = []
    for texto in re.findall(r"\b\d{4}-\d{2}-\d{2}\b", bloque):
        try:
            fechas.append(date.fromisoformat(texto))
        except ValueError:                 # una fecha inválida a propósito no es un periodo
            pass
    return [(a, b) for i, a in enumerate(fechas) for b in fechas[i + 1:] if a.year == b.year and a <= b]


def validar_vacaciones(bloques: list[str]) -> list[str]:
    """Cobertura mínima de HU-10. No depende del orden de los escenarios ni de frases enteras."""
    problemas = []
    errores = errores_vacaciones()
    for caso, codigo, detail in errores:
        if not any(re.search(patron(detail), b) for b in bloques):
            problemas.append(f"Falta un escenario para «{caso}» ({codigo}) con el mensaje exacto: {detail}")

    exito = patron(mensaje_exito_vacaciones())
    exceso = next(d for _, _, d in errores if re.search(r"\bN\b", d))   # el único error con un número variable
    feriados = festivos()

    def quedan(bloque: str) -> list[int]:
        """Días que quedan tras una solicitud aceptada: del mensaje de éxito o de dias_restantes con 201."""
        valores = [int(m.group(2)) for m in re.finditer(exito, bloque)]
        if re.search(r"\b201\b", bloque):
            valores += [int(n) for n in re.findall(r"dias_restantes\D{0,10}?(\d+)", bloque)]
        return valores

    def pide_uno_mas(bloque: str) -> bool:
        """Rechazado por exceso y con un periodo de exactamente N+1 días hábiles."""
        return any(dias_habiles(i, f, feriados) == int(m.group(1)) + 1
                   for m in re.finditer(patron(exceso), bloque) for i, f in periodos(bloque))

    def cuenta_festivo(bloque: str) -> bool:
        """Periodo con un festivo entre semana y el número correcto de días hábiles escrito en el escenario."""
        return any(any(i <= f <= fin and f.weekday() < 5 for f in feriados)
                   and re.search(rf"\b{dias_habiles(i, fin, feriados)}\b", bloque)
                   for i, fin in periodos(bloque))

    if not any(v > 0 for b in bloques for v in quedan(b)):
        problemas.append("Falta el camino feliz: una solicitud aceptada (201) en la que todavía quedan días. "
                         f"Usa el mensaje de éxito exacto: {mensaje_exito_vacaciones()}")
    if not any(v == 0 for b in bloques for v in quedan(b)):
        problemas.append("Falta un escenario que use justo los días que quedan: solicitud aceptada (201) "
                         "y al final quedan 0 días hábiles.")
    if not any(pide_uno_mas(b) for b in bloques):
        problemas.append("Falta un escenario que pida un día hábil más de los que quedan: debe tener el mensaje "
                         f"«{exceso}» y un periodo (fechas AAAA-MM-DD) de N+1 días hábiles contados con la "
                         "tabla de festivos de contexto/reglas_negocio.md.")
    if not any(cuenta_festivo(b) for b in bloques):
        problemas.append("Falta un escenario con un festivo entre semana dentro del periodo (fechas AAAA-MM-DD) "
                         "que diga cuántos días hábiles cuenta, según la tabla de festivos de contexto/reglas_negocio.md.")
    return problemas


def generar_criterios(historia: Path, max_intentos: int | None = None) -> Path:
    """Recibe la ruta de la historia y devuelve la ruta de salida/HU-xx/criterios.feature.

    Valida cada intento con validar_gherkin (y las reglas de HU-10 si aplica). Si hay problemas,
    se los regresa al agente y reintenta: 3 intentos para HU-10, 2 para las demás.
    Lanza ValueError si ningún intento pasa.
    """
    hu = hu_de(historia)
    # HU-10 exige muchos más escenarios: le damos un intento extra; las demás siguen con 2
    max_intentos = max_intentos or (3 if hu == "HU-10" else 2)
    carpeta = SALIDA / hu
    destino = carpeta / "criterios.feature"
    herramientas = herramientas_archivos(lectura=[RAIZ / "historias", RAIZ / "contexto"], escritura=carpeta)
    tarea = f"Historia de usuario: {rel(historia)}"
    for intento in range(1, max_intentos + 1):
        print(f"Analista · intento {intento}")
        ejecutar_agente(SISTEMA.format(destino=rel(destino)), herramientas, tarea, nombre="analista")
        problemas = validar_gherkin(destino.read_text(encoding="utf-8"), hu) if destino.exists() \
            else [f"No se escribió {rel(destino)}."]
        if not problemas:
            return destino
        print(f"  Intento {intento} rechazado. Problemas del validador:\n  - " + "\n  - ".join(problemas))
        # Reflexión guiada por un evaluador determinista: el agente recibe los problemas y corrige
        tarea += "\n\nTu versión anterior tiene estos problemas; corrígelos:\n- " + "\n- ".join(problemas)
    raise ValueError("Criterios inválidos tras varios intentos:\n- " + "\n- ".join(problemas))


if __name__ == "__main__":
    ruta = generar_criterios(Path(sys.argv[1]).resolve())
    texto = ruta.read_text(encoding="utf-8")
    print(f"\nListo: {rel(ruta)} · {len(escenarios(texto))} escenarios")
    for p in preguntas_abiertas(texto):
        print("  Pregunta abierta:", p)
