"""Rutas de la API para solicitar y consultar vacaciones (HU-10)."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from base_datos import obtener_sesion
from esquemas import (
    SaldoVacacionesRespuesta,
    SolicitudVacacionesResumen,
    VacacionesCrear,
    VacacionesRespuesta,
)
from festivos import FESTIVOS
from modelos import Empleado, Vacaciones
from vacaciones_reglas import (
    DIAS_TOPE_ANUAL,
    contar_dias_habiles,
    cumple_antiguedad,
    dias_usados_en_anio,
)

router = APIRouter()


def obtener_empleado_vacaciones_o_404(empleado_id: str, sesion: Session) -> Empleado:
    """Busca al empleado por id numérico o por numero_empleado; responde 404 si no existe."""
    empleado = None
    if empleado_id.isdigit():
        empleado = sesion.get(Empleado, int(empleado_id))
    if empleado is None:
        empleado = (
            sesion.query(Empleado)
            .filter(Empleado.numero_empleado == empleado_id)
            .first()
        )
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado


@router.post(
    "/empleados/{empleado_id}/vacaciones",
    response_model=VacacionesRespuesta,
    status_code=201,
)
def registrar_vacaciones(
    empleado_id: str,
    datos: VacacionesCrear,
    sesion: Session = Depends(obtener_sesion),
):
    empleado = obtener_empleado_vacaciones_o_404(empleado_id, sesion)

    if empleado.estado == "baja":
        raise HTTPException(
            status_code=409,
            detail="No se pueden solicitar vacaciones para un empleado dado de baja",
        )

    if datos.fecha_fin < datos.fecha_inicio:
        raise HTTPException(
            status_code=400,
            detail="La fecha de fin no puede ser anterior a la fecha de inicio",
        )

    if datos.fecha_inicio.year != datos.fecha_fin.year:
        raise HTTPException(
            status_code=400,
            detail="Las vacaciones deben estar dentro de un mismo año calendario",
        )

    anio = datos.fecha_inicio.year
    if anio not in FESTIVOS:
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden solicitar vacaciones en 2026 y 2027",
        )

    if not cumple_antiguedad(empleado.fecha_ingreso, datos.fecha_inicio):
        raise HTTPException(
            status_code=400,
            detail="Se requiere al menos un año de antigüedad a la fecha de inicio",
        )

    dias_solicitados = contar_dias_habiles(datos.fecha_inicio, datos.fecha_fin)
    if dias_solicitados == 0:
        raise HTTPException(
            status_code=400,
            detail="El periodo no incluye días hábiles",
        )

    usados = dias_usados_en_anio(sesion, empleado.id, anio)
    disponibles = DIAS_TOPE_ANUAL - usados
    if dias_solicitados > disponibles:
        raise HTTPException(
            status_code=400,
            detail=f"La solicitud excede los días disponibles: quedan {disponibles} días hábiles",
        )

    solicitud = Vacaciones(
        empleado_id=empleado.id,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
        dias_habiles=dias_solicitados,
    )
    sesion.add(solicitud)
    sesion.commit()
    sesion.refresh(solicitud)

    return VacacionesRespuesta(
        id=solicitud.id,
        empleado_id=empleado.id,
        fecha_inicio=solicitud.fecha_inicio,
        fecha_fin=solicitud.fecha_fin,
        dias_habiles=solicitud.dias_habiles,
        dias_restantes=disponibles - dias_solicitados,
    )


@router.get(
    "/empleados/{empleado_id}/vacaciones",
    response_model=SaldoVacacionesRespuesta,
)
def consultar_saldo_vacaciones(
    empleado_id: str,
    anio: int | None = None,
    sesion: Session = Depends(obtener_sesion),
):
    empleado = obtener_empleado_vacaciones_o_404(empleado_id, sesion)
    anio_consulta = anio or date.today().year

    solicitudes = (
        sesion.query(Vacaciones)
        .filter(
            Vacaciones.empleado_id == empleado.id,
            Vacaciones.fecha_inicio >= date(anio_consulta, 1, 1),
            Vacaciones.fecha_inicio <= date(anio_consulta, 12, 31),
        )
        .order_by(Vacaciones.fecha_inicio)
        .all()
    )
    dias_usados = sum(solicitud.dias_habiles for solicitud in solicitudes)

    return SaldoVacacionesRespuesta(
        empleado_id=empleado.id,
        anio=anio_consulta,
        dias_usados=dias_usados,
        dias_disponibles=DIAS_TOPE_ANUAL - dias_usados,
        solicitudes=[
            SolicitudVacacionesResumen(
                id=solicitud.id,
                fecha_inicio=solicitud.fecha_inicio,
                fecha_fin=solicitud.fecha_fin,
                dias_habiles=solicitud.dias_habiles,
            )
            for solicitud in solicitudes
        ],
    )
