"""Configuración de la base de datos SQLite y la fábrica de sesiones."""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

CARPETA_DATOS = Path(__file__).parent / "datos"
CARPETA_DATOS.mkdir(exist_ok=True)

RUTA_BASE_DATOS = CARPETA_DATOS / "empleados.db"
URL_BASE_DATOS = f"sqlite:///{RUTA_BASE_DATOS}"

motor = create_engine(URL_BASE_DATOS, connect_args={"check_same_thread": False})
FabricaSesiones = sessionmaker(bind=motor, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def obtener_sesion():
    sesion: Session = FabricaSesiones()
    try:
        yield sesion
    finally:
        sesion.close()
