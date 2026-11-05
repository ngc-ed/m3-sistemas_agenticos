"""Punto de entrada de la API de gestión de empleados."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from base_datos import Base, motor
from rutas_empleados import router as router_empleados

Base.metadata.create_all(bind=motor)

app = FastAPI(title="Gestión de empleados")


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(request: Request, exc: RequestValidationError):
    """Convierte los errores de validación de Pydantic en el formato {"detail": "mensaje"}."""
    primer_error = exc.errors()[0]
    campo = primer_error["loc"][-1] if primer_error["loc"] else None
    mensaje = primer_error["msg"]
    if mensaje.startswith("Value error, "):
        mensaje = mensaje.removeprefix("Value error, ")
    elif primer_error["type"] == "missing":
        mensaje = f"El campo '{campo}' es obligatorio"
    return JSONResponse(status_code=422, content={"detail": mensaje, "campo": campo})


@app.get("/api/salud")
def salud():
    return {"estado": "ok"}


app.include_router(router_empleados, prefix="/api")
