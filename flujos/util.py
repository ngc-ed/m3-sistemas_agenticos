import os
import html
import sqlite3
import webbrowser

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
RUTA_CHECKPOINTS = RAIZ / "checkpoints" / "flujo.db"


def crear_checkpointer() -> SqliteSaver:
    """Crea el checkpointer que comparten flujo_s2, flujo_s3 y flujo_s4.

    Un checkpointer guarda una foto del estado del grafo después de cada paso, separada por hilo
    (thread_id). Gracias a eso el flujo puede pausarse con interrupt() y retomarse más tarde, incluso
    desde otro proceso: la pausa no se pierde si se cierra la terminal.

    SqliteSaver guarda esas fotos en un archivo SQLite: checkpoints/flujo.db, en la raíz del proyecto.
    La carpeta se crea si no existe y está en .gitignore. La regla para retomar o empezar de cero
    está en flujos.flujo_s2.ejecutar().
    """
    RUTA_CHECKPOINTS.parent.mkdir(exist_ok=True)
    # check_same_thread=False: LangGraph corre nodos en hilos distintos (por ejemplo, las ramas paralelas de flujo_s3)
    return SqliteSaver(sqlite3.connect(RUTA_CHECKPOINTS, check_same_thread=False))


def dibuja_grafo(app, nombre: str) -> Path:
    """Guarda el grafo de LangGraph como página HTML (Mermaid) en flujos/salidas/grafo_<nombre>.html.

    Las aristas sólidas son add_edge; las punteadas, add_conditional_edges.
    Con abrir=True además lo muestra en el navegador.
    """
    texto = app.get_graph().draw_mermaid()
    pagina = f"""<!doctype html><meta charset="utf-8"><title>Grafo · {nombre}</title>
    <body style="font-family:sans-serif;display:flex;justify-content:center;padding:2rem">
    <pre class="mermaid">{html.escape(texto)}</pre>
    <script type="module">
    import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
    mermaid.initialize({{ startOnLoad: true }});
    </script>"""
    carpeta = RAIZ / "flujos" / "salidas"
    carpeta.mkdir(exist_ok=True)
    ruta = carpeta / f"grafo_{nombre}.html"
    ruta.write_text(pagina, encoding="utf-8")
    return ruta    
