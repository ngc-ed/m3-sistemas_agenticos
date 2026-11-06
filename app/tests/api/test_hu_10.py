"""Pruebas de API para HU-10: vacaciones."""

import httpx


def test_cp01_registrar_solicitud_valida_descuenta_dias_habiles(url_api, crear_empleado):
    """CP-01: Solicitud válida de vacaciones se registra y descuenta los días hábiles."""
    empleado = crear_empleado(fecha_ingreso="2024-03-10")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10"},
    )

    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["dias_habiles"] == 5
    assert datos["dias_restantes"] == 7


def test_cp03_festivos_y_fines_de_semana_no_se_descuentan(url_api, crear_empleado):
    """CP-03: Los sábados, domingos y festivos dentro del periodo no se descuentan."""
    empleado = crear_empleado(fecha_ingreso="2024-03-10")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-12-21", "fecha_fin": "2026-12-31"},
    )

    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["dias_habiles"] == 8
    assert datos["dias_restantes"] == 4


def test_cp05_solicitud_usa_exactamente_los_dias_que_quedan(url_api, crear_empleado):
    """CP-05: Una solicitud que usa exactamente los días que quedan deja el saldo en cero."""
    empleado = crear_empleado(fecha_ingreso="2024-03-10")

    previa = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-01-05", "fecha_fin": "2026-01-13"},
    )
    assert previa.status_code == 201
    assert previa.json()["dias_habiles"] == 7

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10"},
    )

    assert respuesta.status_code == 201
    datos = respuesta.json()
    assert datos["dias_habiles"] == 5
    assert datos["dias_restantes"] == 0


def test_cp07_rechazar_antiguedad_menor_a_un_anio(url_api, crear_empleado):
    """CP-07: Rechazo por antigüedad menor a un año (Regla 1)."""
    empleado = crear_empleado(fecha_ingreso="2025-12-21")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-12-18", "fecha_fin": "2026-12-18"},
    )

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "Se requiere al menos un año de antigüedad a la fecha de inicio"


def test_cp09_rechazar_por_rebasar_el_tope_anual(url_api, crear_empleado):
    """CP-09: Rechazo por rebasar el tope anual de 12 días hábiles (Regla 2)."""
    empleado = crear_empleado(fecha_ingreso="2024-03-10")

    previa = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-12-21", "fecha_fin": "2026-12-31"},
    )
    assert previa.status_code == 201
    assert previa.json()["dias_habiles"] == 8

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10"},
    )

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "La solicitud excede los días disponibles: quedan 4 días hábiles"


def test_cp11_rechazar_periodo_sin_dias_habiles(url_api, crear_empleado):
    """CP-11: Rechazo por periodo sin ningún día hábil (Regla 3)."""
    empleado = crear_empleado(fecha_ingreso="2024-03-10")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-07-11", "fecha_fin": "2026-07-12"},
    )

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "El periodo no incluye días hábiles"


def test_cp13_rechazar_fecha_fin_anterior_a_fecha_inicio(url_api, crear_empleado):
    """CP-13: Rechazo cuando la fecha de fin es anterior a la fecha de inicio."""
    empleado = crear_empleado(fecha_ingreso="2024-03-10")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-07-10", "fecha_fin": "2026-07-06"},
    )

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "La fecha de fin no puede ser anterior a la fecha de inicio"


def test_cp15_rechazar_periodo_que_cruza_de_anio(url_api, crear_empleado):
    """CP-15: Rechazo cuando el periodo cruza de un año a otro."""
    empleado = crear_empleado(fecha_ingreso="2024-03-10")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-12-28", "fecha_fin": "2027-01-08"},
    )

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "Las vacaciones deben estar dentro de un mismo año calendario"


def test_cp17_rechazar_anio_fuera_de_la_tabla_de_festivos(url_api, crear_empleado):
    """CP-17: Rechazo cuando el año solicitado no está en la tabla de festivos."""
    empleado = crear_empleado(fecha_ingreso="2024-03-10")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2028-07-06", "fecha_fin": "2028-07-10"},
    )

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "Solo se pueden solicitar vacaciones en 2026 y 2027"


def test_cp19_rechazar_empleado_que_no_existe(url_api):
    """CP-19: Rechazo cuando el empleado no existe."""
    respuesta = httpx.post(
        f"{url_api}/api/empleados/9999/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10"},
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Empleado no encontrado"


def test_cp20_rechazar_empleado_dado_de_baja(url_api, crear_empleado):
    """CP-20: Rechazo cuando el empleado está dado de baja."""
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
