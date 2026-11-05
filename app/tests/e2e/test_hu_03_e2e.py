"""Pruebas E2E para HU-03: editar y dar de baja empleados."""

from playwright.sync_api import expect


def test_cp02_editar_puesto_y_departamento_en_la_tabla(page, url_web, crear_empleado):
    """CP-02: Editar puesto y departamento de un empleado activo."""
    empleado = crear_empleado(puesto="Analista", departamento="Ventas")

    page.goto(url_web)
    expect(page.get_by_test_id(f"fila-empleado-{empleado['id']}")).to_be_visible()

    page.get_by_test_id(f"editar-empleado-{empleado['id']}").click()

    campo_puesto = page.get_by_test_id("empleado-puesto")
    expect(campo_puesto).to_have_value("Analista")
    campo_puesto.fill("Analista Senior")

    campo_departamento = page.get_by_test_id("empleado-departamento")
    expect(campo_departamento).to_have_value("Ventas")
    campo_departamento.select_option("Tecnología")

    page.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("mensaje-exito")).to_be_visible()
    expect(page.get_by_test_id(f"numero-empleado-{empleado['id']}")).to_have_text(empleado["numero_empleado"])


def test_cp04_error_al_editar_con_departamento_no_permitido_en_la_tabla(page, url_web, crear_empleado):
    """CP-04: Error al editar con un departamento que no está en la lista permitida."""
    empleado = crear_empleado(puesto="Analista", departamento="Ventas")

    page.goto(url_web)
    page.get_by_test_id(f"editar-empleado-{empleado['id']}").click()

    campo_departamento = page.get_by_test_id("empleado-departamento")
    expect(campo_departamento).to_have_value("Ventas")
    opciones = campo_departamento.locator("option").all_inner_texts()
    assert "Marketing" not in opciones

    campo_departamento.evaluate(
        """(elemento) => {
            const opcion = document.createElement('option')
            opcion.value = 'Marketing'
            opcion.textContent = 'Marketing'
            elemento.appendChild(opcion)
            elemento.value = 'Marketing'
            elemento.dispatchEvent(new Event('change', { bubbles: true }))
        }"""
    )
    page.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("mensaje-error")).to_be_visible()

    page.get_by_test_id(f"editar-empleado-{empleado['id']}").click()
    expect(page.get_by_test_id("empleado-departamento")).to_have_value("Ventas")


def test_cp06_error_al_editar_empleado_dado_de_baja(page, url_web, crear_empleado, marcar_baja):
    """CP-06: Error al intentar editar a un empleado dado de baja."""
    empleado = crear_empleado(puesto="Analista", departamento="Ventas")
    marcar_baja(empleado["correo"])

    page.goto(url_web)
    page.get_by_test_id(f"editar-empleado-{empleado['id']}").click()
    page.get_by_test_id("empleado-puesto").fill("Gerente")
    page.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("mensaje-error")).to_have_text("No se puede editar a un empleado dado de baja")
    expect(page.get_by_test_id(f"estado-empleado-{empleado['id']}")).to_have_text("Baja")


def test_cp08_dar_de_baja_a_un_empleado_activo_en_la_tabla(page, url_web, crear_empleado):
    """CP-08: Dar de baja a un empleado activo."""
    empleado = crear_empleado(fecha_ingreso="2022-01-10")

    page.goto(url_web)
    page.get_by_test_id(f"baja-empleado-{empleado['id']}").click()
    page.get_by_test_id("empleado-fecha-baja").fill("2024-05-15")
    page.get_by_test_id("confirmar-baja").click()

    expect(page.get_by_test_id("mensaje-exito")).to_be_visible()
    expect(page.get_by_test_id(f"estado-empleado-{empleado['id']}")).to_have_text("Baja")
    expect(page.get_by_test_id(f"fila-empleado-{empleado['id']}")).to_be_visible()


def test_cp10_error_al_dar_de_baja_con_fecha_anterior_a_ingreso(page, url_web, crear_empleado):
    """CP-10: Error al dar de baja con una fecha de baja anterior a la fecha de ingreso."""
    empleado = crear_empleado(fecha_ingreso="2022-01-10")

    page.goto(url_web)
    page.get_by_test_id(f"baja-empleado-{empleado['id']}").click()
    page.get_by_test_id("empleado-fecha-baja").fill("2021-12-01")
    page.get_by_test_id("confirmar-baja").click()

    expect(page.get_by_test_id("mensaje-error")).to_be_visible()
    expect(page.get_by_test_id(f"estado-empleado-{empleado['id']}")).to_have_text("Activo")
