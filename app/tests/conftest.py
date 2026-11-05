"""Fixtures compartidos por las pruebas de la aplicación de gestión de empleados."""

import os
import sqlite3
import uuid
from datetime import date
from pathlib import Path

import httpx
import pytest

URL_API = os.environ.get("URL_API", "http://localhost:8000")
URL_WEB = os.environ.get("URL_WEB", "http://localhost:8080")

RUTA_BASE_DATOS = Path(__file__).resolve().parent.parent / "backend" / "datos" / "empleados.db"


@pytest.fixture
def url_api() -> str:
    return URL_API


@pytest.fixture
def url_web() -> str:
    return URL_WEB


@pytest.fixture
def crear_empleado(url_api):
    """Registra un empleado vía la API y devuelve el recurso creado (incluye su id).

    Cada llamada usa un correo único (uuid) para que las pruebas puedan repetirse
    sin chocar con datos de ejecuciones anteriores.
    """

    def _crear(nombre: str | None = None, puesto: str = "Analista",
               departamento: str = "Tecnología", correo: str | None = None,
               fecha_ingreso: str | None = None) -> dict:
        sufijo = uuid.uuid4().hex[:8]
        datos = {
            "nombre": nombre or f"Empleada Prueba {sufijo}",
            "correo": correo or f"prueba.{sufijo}@empresa.com",
            "puesto": puesto,
            "departamento": departamento,
            "fecha_ingreso": fecha_ingreso or date.today().isoformat(),
        }
        respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)
        respuesta.raise_for_status()
        return respuesta.json()

    return _crear


@pytest.fixture
def marcar_baja():
    """Marca un empleado como 'baja' directamente en la base de datos.

    HU-03 (editar y dar de baja) todavía no está implementada: la API no tiene
    ningún endpoint para cambiar el estado de un empleado. Para preparar esta
    precondición, la prueba actualiza el registro directamente en la base de
    datos SQLite que usa el backend.
    """

    def _marcar(correo: str, fecha_baja: str | None = None) -> None:
        fecha_baja = fecha_baja or date.today().isoformat()
        conexion = sqlite3.connect(RUTA_BASE_DATOS)
        try:
            conexion.execute(
                "UPDATE empleados SET estado = 'baja', fecha_baja = ? WHERE correo = ?",
                (fecha_baja, correo),
            )
            conexion.commit()
        finally:
            conexion.close()

    return _marcar
