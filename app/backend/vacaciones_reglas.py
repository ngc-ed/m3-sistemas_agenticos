"""Reglas de negocio de vacaciones (HU-10): días hábiles, antigüedad y saldo anual."""

from datetime import date, timedelta

from sqlalchemy.orm import Session

from festivos import FESTIVOS
from modelos import Vacaciones

DIAS_TOPE_ANUAL = 12


def contar_dias_habiles(inicio: date, fin: date) -> int:
    """Cuenta los días hábiles entre inicio y fin, ambos incluidos."""
    festivos = FESTIVOS.get(inicio.year, set())
    dias = 0
    actual = inicio
    while actual <= fin:
        if actual.weekday() < 5 and actual not in festivos:
            dias += 1
        actual += timedelta(days=1)
    return dias


def cumple_antiguedad(fecha_ingreso: date, fecha_inicio: date) -> bool:
    """Verifica al menos un año cumplido entre fecha_ingreso y fecha_inicio.

    Si fecha_ingreso cae en 29 de febrero, el aniversario en un año no
    bisiesto se recorre al 1 de marzo.
    """
    try:
        aniversario = fecha_ingreso.replace(year=fecha_ingreso.year + 1)
    except ValueError:
        aniversario = date(fecha_ingreso.year + 1, 3, 1)
    return fecha_inicio >= aniversario


def dias_usados_en_anio(sesion: Session, empleado_id: int, anio: int) -> int:
    """Suma los días hábiles de todas las solicitudes del empleado en ese año."""
    solicitudes = (
        sesion.query(Vacaciones)
        .filter(
            Vacaciones.empleado_id == empleado_id,
            Vacaciones.fecha_inicio >= date(anio, 1, 1),
            Vacaciones.fecha_inicio <= date(anio, 12, 31),
        )
        .all()
    )
    return sum(solicitud.dias_habiles for solicitud in solicitudes)
