"""Pruebas de API para HU-10: vacaciones."""

import httpx


def test_cp01_registrar_solicitud_valida_de_vacaciones(url_api, crear_empleado):
    """CP-01: Registrar una solicitud válida de vacaciones."""
    empleado = crear_empleado(fecha_ingreso="2023-01-10")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-12-21", "fecha_fin": "2026-12-31"},
    )

    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["dias_habiles"] == 8
    assert datos["dias_restantes"] == 4


def test_cp03_festivos_y_fines_de_semana_no_se_descuentan(url_api, crear_empleado):
    """CP-03: Los festivos y fines de semana dentro del periodo no se descuentan."""
    empleado = crear_empleado(fecha_ingreso="2022-05-01")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-09-14", "fecha_fin": "2026-09-18"},
    )

    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["dias_habiles"] == 4
    assert datos["dias_restantes"] == 8


def test_cp05_solicitud_usa_exactamente_los_dias_que_quedan(url_api, crear_empleado):
    """CP-05: Registrar una solicitud que usa exactamente los días hábiles que quedan."""
    empleado = crear_empleado(fecha_ingreso="2022-03-15")

    previa = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10"},
    )
    assert previa.status_code == 201
    assert previa.json()["dias_habiles"] == 5

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-07-13", "fecha_fin": "2026-07-21"},
    )

    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["dias_habiles"] == 7
    assert datos["dias_restantes"] == 0


def test_cp07_rechazar_solicitud_con_menos_de_un_anio_de_antiguedad(url_api, crear_empleado):
    """CP-07: Rechazar la solicitud de un empleado con menos de un año de antigüedad."""
    empleado = crear_empleado(fecha_ingreso="2025-12-21")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-12-18", "fecha_fin": "2026-12-18"},
    )

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "Se requiere al menos un año de antigüedad a la fecha de inicio"


def test_cp09_rechazar_periodo_sin_dias_habiles(url_api, crear_empleado):
    """CP-09: Rechazar un periodo sin ningún día hábil."""
    empleado = crear_empleado(fecha_ingreso="2022-01-01")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-07-11", "fecha_fin": "2026-07-12"},
    )

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "El periodo no incluye días hábiles"


def test_cp11_rechazar_solicitud_sin_dias_disponibles(url_api, crear_empleado):
    """CP-11: Rechazar una solicitud que rebasa los días disponibles del año cuando ya no queda ninguno."""
    empleado = crear_empleado(fecha_ingreso="2023-01-05")

    previa = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-01-05", "fecha_fin": "2026-01-20"},
    )
    assert previa.status_code == 201
    assert previa.json()["dias_habiles"] == 12

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-11-02", "fecha_fin": "2026-11-03"},
    )

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "La solicitud excede los días disponibles: quedan 0 días hábiles"


def test_cp13_rechazar_solicitud_que_pide_un_dia_mas_de_los_que_quedan(url_api, crear_empleado):
    """CP-13: Rechazar una solicitud que pide un día hábil más de los que quedan."""
    empleado = crear_empleado(fecha_ingreso="2022-06-01")

    previa = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-12-21", "fecha_fin": "2026-12-31"},
    )
    assert previa.status_code == 201
    assert previa.json()["dias_habiles"] == 8

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-08-03", "fecha_fin": "2026-08-07"},
    )

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "La solicitud excede los días disponibles: quedan 4 días hábiles"


def test_cp15_rechazar_fecha_fin_anterior_a_fecha_inicio(url_api, crear_empleado):
    """CP-15: Rechazar una fecha de fin anterior a la fecha de inicio."""
    empleado = crear_empleado(fecha_ingreso="2022-01-01")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-07-10", "fecha_fin": "2026-07-05"},
    )

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "La fecha de fin no puede ser anterior a la fecha de inicio"


def test_cp17_rechazar_periodo_que_cruza_de_anio(url_api, crear_empleado):
    """CP-17: Rechazar un periodo que cruza de un año a otro."""
    empleado = crear_empleado(fecha_ingreso="2022-01-01")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-12-28", "fecha_fin": "2027-01-08"},
    )

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "Las vacaciones deben estar dentro de un mismo año calendario"


def test_cp19_rechazar_anio_fuera_del_catalogo_de_festivos(url_api, crear_empleado):
    """CP-19: Rechazar un año fuera del catálogo de festivos."""
    empleado = crear_empleado(fecha_ingreso="2020-01-01")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2025-07-07", "fecha_fin": "2025-07-11"},
    )

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "Solo se pueden solicitar vacaciones en 2026 y 2027"


def test_cp21_rechazar_solicitud_de_empleado_que_no_existe(url_api):
    """CP-21: Rechazar la solicitud de un empleado que no existe."""
    respuesta = httpx.post(
        f"{url_api}/api/empleados/9999/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10"},
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Empleado no encontrado"


def test_cp22_rechazar_solicitud_de_empleado_dado_de_baja(url_api, crear_empleado):
    """CP-22: Rechazar la solicitud de un empleado dado de baja."""
    empleado = crear_empleado(fecha_ingreso="2020-01-01")

    baja = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/baja",
        json={"fecha_baja": "2024-01-15"},
    )
    assert baja.status_code == 200

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10"},
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "No se pueden solicitar vacaciones para un empleado dado de baja"


def test_cp24_consultar_saldo_tras_registrar_una_solicitud(url_api, crear_empleado):
    """CP-24: Consultar el saldo de vacaciones del año tras registrar una solicitud."""
    empleado = crear_empleado(fecha_ingreso="2023-01-10")

    previa = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-12-21", "fecha_fin": "2026-12-31"},
    )
    assert previa.status_code == 201
    assert previa.json()["dias_habiles"] == 8

    respuesta = httpx.get(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        params={"anio": 2026},
    )

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["dias_usados"] == 8
    assert datos["dias_disponibles"] == 4
