"""Pruebas E2E para HU-10: vacaciones."""

import httpx
from playwright.sync_api import expect


def test_cp02_registrar_solicitud_valida_descuenta_dias_habiles(page, url_web, crear_empleado):
    """CP-02: Solicitud válida de vacaciones se registra y descuenta los días hábiles."""
    empleado = crear_empleado(fecha_ingreso="2024-03-10")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()

    expect(page.get_by_test_id("vacaciones-disponibles")).to_have_text("12")

    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-06")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-10")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Solicitud registrada: 5 días hábiles. Te quedan 7 días hábiles en 2026."
    )


def test_cp04_festivos_y_fines_de_semana_no_se_descuentan(page, url_web, crear_empleado):
    """CP-04: Los sábados, domingos y festivos dentro del periodo no se descuentan."""
    empleado = crear_empleado(fecha_ingreso="2024-03-10")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-12-21")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-12-31")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Solicitud registrada: 8 días hábiles. Te quedan 4 días hábiles en 2026."
    )


def test_cp06_solicitud_usa_exactamente_los_dias_que_quedan(page, url_web, url_api, crear_empleado):
    """CP-06: Una solicitud que usa exactamente los días que quedan deja el saldo en cero."""
    empleado = crear_empleado(fecha_ingreso="2024-03-10")

    previa = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-01-05", "fecha_fin": "2026-01-13"},
    )
    assert previa.status_code == 201
    assert previa.json()["dias_habiles"] == 7

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()

    expect(page.get_by_test_id("vacaciones-disponibles")).to_have_text("5")

    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-06")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-10")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Solicitud registrada: 5 días hábiles. Te quedan 0 días hábiles en 2026."
    )


def test_cp08_rechazar_antiguedad_menor_a_un_anio(page, url_web, crear_empleado):
    """CP-08: Rechazo por antigüedad menor a un año (Regla 1)."""
    empleado = crear_empleado(fecha_ingreso="2025-12-21")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-12-18")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-12-18")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Se requiere al menos un año de antigüedad a la fecha de inicio"
    )


def test_cp10_rechazar_por_rebasar_el_tope_anual(page, url_web, url_api, crear_empleado):
    """CP-10: Rechazo por rebasar el tope anual de 12 días hábiles (Regla 2)."""
    empleado = crear_empleado(fecha_ingreso="2024-03-10")

    previa = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/vacaciones",
        json={"fecha_inicio": "2026-12-21", "fecha_fin": "2026-12-31"},
    )
    assert previa.status_code == 201
    assert previa.json()["dias_habiles"] == 8

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()

    expect(page.get_by_test_id("vacaciones-disponibles")).to_have_text("4")

    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-06")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-10")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "La solicitud excede los días disponibles: quedan 4 días hábiles"
    )


def test_cp12_rechazar_periodo_sin_dias_habiles(page, url_web, crear_empleado):
    """CP-12: Rechazo por periodo sin ningún día hábil (Regla 3)."""
    empleado = crear_empleado(fecha_ingreso="2024-03-10")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-11")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-12")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text("El periodo no incluye días hábiles")


def test_cp14_rechazar_fecha_fin_anterior_a_fecha_inicio(page, url_web, crear_empleado):
    """CP-14: Rechazo cuando la fecha de fin es anterior a la fecha de inicio."""
    empleado = crear_empleado(fecha_ingreso="2024-03-10")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-10")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-06")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "La fecha de fin no puede ser anterior a la fecha de inicio"
    )


def test_cp16_rechazar_periodo_que_cruza_de_anio(page, url_web, crear_empleado):
    """CP-16: Rechazo cuando el periodo cruza de un año a otro."""
    empleado = crear_empleado(fecha_ingreso="2024-03-10")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-12-28")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2027-01-08")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Las vacaciones deben estar dentro de un mismo año calendario"
    )


def test_cp18_rechazar_anio_fuera_de_la_tabla_de_festivos(page, url_web, crear_empleado):
    """CP-18: Rechazo cuando el año solicitado no está en la tabla de festivos."""
    empleado = crear_empleado(fecha_ingreso="2024-03-10")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2028-07-06")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2028-07-10")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Solo se pueden solicitar vacaciones en 2026 y 2027"
    )
