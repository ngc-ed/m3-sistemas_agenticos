"""Pruebas E2E para HU-02: consultar el directorio de empleados."""

import uuid

from playwright.sync_api import expect


def test_cp02_ver_tabla_completa_del_directorio(page, url_web, crear_empleado):
    """CP-02: Ver el directorio completo de empleados."""
    empleado_1 = crear_empleado(nombre="Ana Torres", puesto="Analista", departamento="Tecnología")
    empleado_2 = crear_empleado(nombre="Luis Gómez", puesto="Ejecutivo Ventas", departamento="Ventas")

    page.goto(url_web)

    expect(page.get_by_test_id("tabla-empleados")).to_be_visible()

    fila_1 = page.get_by_test_id(f"fila-empleado-{empleado_1['id']}")
    expect(fila_1).to_be_visible()
    expect(page.get_by_test_id(f"numero-empleado-{empleado_1['id']}")).to_have_text(empleado_1["numero_empleado"])
    expect(page.get_by_test_id(f"estado-empleado-{empleado_1['id']}")).to_have_text("Activo")

    fila_2 = page.get_by_test_id(f"fila-empleado-{empleado_2['id']}")
    expect(fila_2).to_be_visible()
    expect(page.get_by_test_id(f"numero-empleado-{empleado_2['id']}")).to_have_text(empleado_2["numero_empleado"])
    expect(page.get_by_test_id(f"estado-empleado-{empleado_2['id']}")).to_have_text("Activo")


def test_cp04_buscar_por_nombre_en_la_tabla(page, url_web, crear_empleado):
    """CP-04: Buscar un empleado por nombre sin distinguir mayúsculas de minúsculas."""
    sufijo = uuid.uuid4().hex[:8]
    nombre = f"Ana Torres {sufijo}"
    empleado = crear_empleado(nombre=nombre)

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(nombre.upper())

    tabla = page.get_by_test_id("tabla-empleados")
    expect(tabla).to_be_visible()
    expect(tabla.locator("tbody tr")).to_have_count(1)
    expect(page.get_by_test_id(f"numero-empleado-{empleado['id']}")).to_have_text(empleado["numero_empleado"])


def test_cp06_buscar_por_correo_en_la_tabla(page, url_web, crear_empleado):
    """CP-06: Buscar un empleado por correo sin distinguir mayúsculas de minúsculas."""
    empleado = crear_empleado()

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(empleado["correo"].upper())

    tabla = page.get_by_test_id("tabla-empleados")
    expect(tabla).to_be_visible()
    expect(tabla.locator("tbody tr")).to_have_count(1)
    expect(page.get_by_test_id(f"numero-empleado-{empleado['id']}")).to_have_text(empleado["numero_empleado"])


def test_cp08_filtrar_por_departamento_en_la_tabla(page, url_web, crear_empleado):
    """CP-08: Filtrar empleados por departamento."""
    sufijo = uuid.uuid4().hex[:8]
    tecnologia_1 = crear_empleado(nombre=f"Persona Tecnologia Uno {sufijo}", departamento="Tecnología")
    tecnologia_2 = crear_empleado(nombre=f"Persona Tecnologia Dos {sufijo}", departamento="Tecnología")
    ventas = crear_empleado(nombre=f"Persona Ventas {sufijo}", departamento="Ventas")

    page.goto(url_web)
    page.get_by_test_id("filtro-departamento").select_option("Tecnología")

    expect(page.get_by_test_id(f"fila-empleado-{tecnologia_1['id']}")).to_be_visible()
    expect(page.get_by_test_id(f"fila-empleado-{tecnologia_2['id']}")).to_be_visible()
    expect(page.get_by_test_id(f"fila-empleado-{ventas['id']}")).not_to_be_attached()


def test_cp10_buscar_texto_sin_resultados(page, url_web, crear_empleado):
    """CP-10: Buscar un texto que no coincide con ningún empleado."""
    crear_empleado(nombre="Ana Torres")
    texto_busqueda = f"zzz-no-existe-{uuid.uuid4().hex[:8]}"

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(texto_busqueda)

    expect(page.get_by_test_id("sin-resultados")).to_have_text("No se encontraron empleados")
    expect(page.get_by_test_id("tabla-empleados")).not_to_be_attached()


def test_cp12_empleado_baja_aparece_en_la_tabla(page, url_web, crear_empleado, marcar_baja):
    """CP-12: Un empleado dado de baja sigue apareciendo en el directorio."""
    empleado = crear_empleado(nombre="Carlos Pérez")
    marcar_baja(empleado["correo"])

    page.goto(url_web)

    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_be_visible()
    expect(page.get_by_test_id(f"numero-empleado-{empleado['id']}")).to_have_text(empleado["numero_empleado"])
    expect(page.get_by_test_id(f"estado-empleado-{empleado['id']}")).to_have_text("Baja")
