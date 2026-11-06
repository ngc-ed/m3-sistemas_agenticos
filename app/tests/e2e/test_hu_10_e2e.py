"""Pruebas E2E para HU-10: vacaciones."""

import httpx
from playwright.sync_api import expect


def test_cp02_registrar_solicitud_valida_de_vacaciones(page, url_web, crear_empleado):
    """CP-02: Registrar una solicitud válida de vacaciones."""
    empleado = crear_empleado(fecha_ingreso="2023-01-10")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-12-21")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-12-31")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Solicitud registrada: 8 días hábiles. Te quedan 4 días hábiles en 2026."
    )


def test_cp04_festivos_y_fines_de_semana_no_se_descuentan(page, url_web, crear_empleado):
    """CP-04: Los festivos y fines de semana dentro del periodo no se descuentan."""
    empleado = crear_empleado(fecha_ingreso="2022-05-01")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-09-14")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-09-18")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Solicitud registrada: 4 días hábiles. Te quedan 8 días hábiles en 2026."
    )


def test_cp06_solicitud_usa_exactamente_los_dias_que_quedan(page, url_web, url_api, crear_empleado):
    """CP-06: Registrar una solicitud que usa exactamente los días hábiles que quedan."""
    empleado = crear_empleado(fecha_ingreso="2022-03-15")

    previa = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10"},
    )
    assert previa.status_code == 201

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-13")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-21")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Solicitud registrada: 7 días hábiles. Te quedan 0 días hábiles en 2026."
    )


def test_cp08_rechazar_solicitud_con_menos_de_un_anio_de_antiguedad(page, url_web, crear_empleado):
    """CP-08: Rechazar la solicitud de un empleado con menos de un año de antigüedad."""
    empleado = crear_empleado(fecha_ingreso="2025-12-21")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-12-18")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-12-18")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Se requiere al menos un año de antigüedad a la fecha de inicio"
    )


def test_cp10_rechazar_periodo_sin_dias_habiles(page, url_web, crear_empleado):
    """CP-10: Rechazar un periodo sin ningún día hábil."""
    empleado = crear_empleado(fecha_ingreso="2022-01-01")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-11")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-12")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text("El periodo no incluye días hábiles")


def test_cp12_rechazar_solicitud_sin_dias_disponibles(page, url_web, url_api, crear_empleado):
    """CP-12: Rechazar una solicitud que rebasa los días disponibles del año cuando ya no queda ninguno."""
    empleado = crear_empleado(fecha_ingreso="2023-01-05")

    previa = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-01-05", "fecha_fin": "2026-01-20"},
    )
    assert previa.status_code == 201

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-11-02")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-11-03")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "La solicitud excede los días disponibles: quedan 0 días hábiles"
    )


def test_cp14_rechazar_solicitud_que_pide_un_dia_mas_de_los_que_quedan(page, url_web, url_api, crear_empleado):
    """CP-14: Rechazar una solicitud que pide un día hábil más de los que quedan."""
    empleado = crear_empleado(fecha_ingreso="2022-06-01")

    previa = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-12-21", "fecha_fin": "2026-12-31"},
    )
    assert previa.status_code == 201

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-08-03")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-08-07")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "La solicitud excede los días disponibles: quedan 4 días hábiles"
    )


def test_cp16_rechazar_fecha_fin_anterior_a_fecha_inicio(page, url_web, crear_empleado):
    """CP-16: Rechazar una fecha de fin anterior a la fecha de inicio."""
    empleado = crear_empleado(fecha_ingreso="2022-01-01")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-10")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-05")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "La fecha de fin no puede ser anterior a la fecha de inicio"
    )


def test_cp18_rechazar_periodo_que_cruza_de_anio(page, url_web, crear_empleado):
    """CP-18: Rechazar un periodo que cruza de un año a otro."""
    empleado = crear_empleado(fecha_ingreso="2022-01-01")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-12-28")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2027-01-08")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Las vacaciones deben estar dentro de un mismo año calendario"
    )


def test_cp20_rechazar_anio_fuera_del_catalogo_de_festivos(page, url_web, crear_empleado):
    """CP-20: Rechazar un año fuera del catálogo de festivos."""
    empleado = crear_empleado(fecha_ingreso="2020-01-01")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2025-07-07")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2025-07-11")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Solo se pueden solicitar vacaciones en 2026 y 2027"
    )


def test_cp23_rechazar_solicitud_de_empleado_dado_de_baja(page, url_web, crear_empleado):
    """CP-23: Rechazar la solicitud de un empleado dado de baja."""
    empleado = crear_empleado(fecha_ingreso="2020-01-01")

    page.goto(url_web)
    page.get_by_test_id(f"baja-empleado-{empleado['id']}").click()
    page.get_by_test_id("empleado-fecha-baja").fill("2024-01-15")
    page.get_by_test_id("confirmar-baja").click()
    expect(page.get_by_test_id(f"estado-empleado-{empleado['id']}")).to_have_text("Baja")

    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-06")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-10")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "No se pueden solicitar vacaciones para un empleado dado de baja"
    )


def test_cp25_consultar_saldo_tras_registrar_una_solicitud(page, url_web, url_api, crear_empleado):
    """CP-25: Consultar el saldo de vacaciones del año tras registrar una solicitud."""
    empleado = crear_empleado(fecha_ingreso="2023-01-10")

    previa = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-12-21", "fecha_fin": "2026-12-31"},
    )
    assert previa.status_code == 201

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()

    expect(page.get_by_test_id("vacaciones-disponibles")).to_have_text("4")
