"""Rutas de la API para la gestión de empleados."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from base_datos import obtener_sesion
from constantes import DEPARTAMENTOS_VALIDOS
from esquemas import EmpleadoActualizar, EmpleadoBaja, EmpleadoCrear, EmpleadoRespuesta
from modelos import Empleado

router = APIRouter()


def generar_numero_empleado(sesion: Session) -> str:
    """Asigna el siguiente número de empleado consecutivo (EMP-0001, EMP-0002, ...)."""
    ultimo = sesion.query(Empleado).order_by(Empleado.id.desc()).first()
    if ultimo is None:
        return "EMP-0001"
    numero_actual = int(ultimo.numero_empleado.split("-")[1])
    return f"EMP-{numero_actual + 1:04d}"


def obtener_empleado_o_404(numero_empleado: str, sesion: Session) -> Empleado:
    """Busca un empleado por su numero_empleado; responde 404 si no existe."""
    empleado = (
        sesion.query(Empleado)
        .filter(Empleado.numero_empleado == numero_empleado)
        .first()
    )
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado


@router.get("/departamentos")
def listar_departamentos() -> list[str]:
    return DEPARTAMENTOS_VALIDOS


@router.get("/empleados", response_model=list[EmpleadoRespuesta])
def listar_empleados(
    busqueda: str | None = None,
    departamento: str | None = None,
    sesion: Session = Depends(obtener_sesion),
):
    consulta = sesion.query(Empleado)
    if busqueda:
        texto = f"%{busqueda.strip().lower()}%"
        consulta = consulta.filter(
            func.lower(Empleado.nombre).like(texto) | func.lower(Empleado.correo).like(texto)
        )
    if departamento in DEPARTAMENTOS_VALIDOS:
        consulta = consulta.filter(Empleado.departamento == departamento)
    return consulta.order_by(Empleado.id).all()


@router.post("/empleados", response_model=EmpleadoRespuesta, status_code=201)
def registrar_empleado(datos: EmpleadoCrear, sesion: Session = Depends(obtener_sesion)):
    existe = (
        sesion.query(Empleado)
        .filter(func.lower(Empleado.correo) == datos.correo)
        .first()
    )
    if existe is not None:
        raise HTTPException(status_code=409, detail="El correo ya está registrado")

    empleado = Empleado(
        numero_empleado=generar_numero_empleado(sesion),
        nombre=datos.nombre,
        correo=datos.correo,
        puesto=datos.puesto,
        departamento=datos.departamento,
        fecha_ingreso=datos.fecha_ingreso,
        estado="activo",
    )
    sesion.add(empleado)
    try:
        sesion.commit()
    except IntegrityError:
        sesion.rollback()
        raise HTTPException(status_code=409, detail="El correo ya está registrado")
    sesion.refresh(empleado)
    return empleado


@router.get("/empleados/{numero_empleado}", response_model=EmpleadoRespuesta)
def obtener_empleado(numero_empleado: str, sesion: Session = Depends(obtener_sesion)):
    return obtener_empleado_o_404(numero_empleado, sesion)


@router.put("/empleados/{numero_empleado}", response_model=EmpleadoRespuesta)
def actualizar_empleado(
    numero_empleado: str,
    datos: EmpleadoActualizar,
    sesion: Session = Depends(obtener_sesion),
):
    empleado = obtener_empleado_o_404(numero_empleado, sesion)
    if empleado.estado == "baja":
        raise HTTPException(
            status_code=409, detail="No se puede editar a un empleado dado de baja"
        )
    empleado.puesto = datos.puesto
    empleado.departamento = datos.departamento
    sesion.commit()
    sesion.refresh(empleado)
    return empleado


@router.post("/empleados/{numero_empleado}/baja", response_model=EmpleadoRespuesta)
def dar_de_baja_empleado(
    numero_empleado: str,
    datos: EmpleadoBaja,
    sesion: Session = Depends(obtener_sesion),
):
    empleado = obtener_empleado_o_404(numero_empleado, sesion)
    if empleado.estado == "baja":
        # La regla de negocio no define un error para este caso; se trata como
        # operación idempotente y se devuelve el estado actual sin cambios.
        return empleado
    if datos.fecha_baja < empleado.fecha_ingreso:
        return JSONResponse(
            status_code=422,
            content={
                "detail": "La fecha de baja no puede ser anterior a la fecha de ingreso",
                "campo": "fecha_baja",
            },
        )
    empleado.estado = "baja"
    empleado.fecha_baja = datos.fecha_baja
    sesion.commit()
    sesion.refresh(empleado)
    return empleado
