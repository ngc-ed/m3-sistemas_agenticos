"""Pruebas de API para HU-02: consultar el directorio de empleados."""

import uuid

import httpx


def test_cp01_ver_directorio_completo(url_api, crear_empleado):
    """CP-01: Ver el directorio completo de empleados."""
    empleado_1 = crear_empleado(nombre="Ana Torres", puesto="Analista", departamento="Tecnología")
    empleado_2 = crear_empleado(nombre="Luis Gómez", puesto="Ejecutivo Ventas", departamento="Ventas")

    respuesta = httpx.get(f"{url_api}/api/empleados")

    assert respuesta.status_code == 200
    por_correo = {empleado["correo"]: empleado for empleado in respuesta.json()}

    for creado in (empleado_1, empleado_2):
        encontrado = por_correo[creado["correo"]]
        assert encontrado["numero_empleado"] == creado["numero_empleado"]
        assert encontrado["nombre"] == creado["nombre"]
        assert encontrado["puesto"] == creado["puesto"]
        assert encontrado["departamento"] == creado["departamento"]
        assert encontrado["estado"] == "activo"


def test_cp03_buscar_por_nombre_sin_distinguir_mayusculas(url_api, crear_empleado):
    """CP-03: Buscar un empleado por nombre sin distinguir mayúsculas de minúsculas."""
    sufijo = uuid.uuid4().hex[:8]
    nombre = f"Ana Torres {sufijo}"
    empleado = crear_empleado(nombre=nombre)

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"busqueda": nombre.upper()})

    assert respuesta.status_code == 200
    resultados = respuesta.json()
    assert len(resultados) == 1
    assert resultados[0]["numero_empleado"] == empleado["numero_empleado"]
    assert resultados[0]["nombre"] == nombre


def test_cp05_buscar_por_correo_sin_distinguir_mayusculas(url_api, crear_empleado):
    """CP-05: Buscar un empleado por correo sin distinguir mayúsculas de minúsculas."""
    empleado = crear_empleado()
    correo = empleado["correo"]

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"busqueda": correo.upper()})

    assert respuesta.status_code == 200
    resultados = respuesta.json()
    assert len(resultados) == 1
    assert resultados[0]["numero_empleado"] == empleado["numero_empleado"]
    assert resultados[0]["correo"] == correo


def test_cp07_filtrar_por_departamento(url_api, crear_empleado):
    """CP-07: Filtrar empleados por departamento."""
    sufijo = uuid.uuid4().hex[:8]
    tecnologia_1 = crear_empleado(nombre=f"Persona Tecnologia Uno {sufijo}", departamento="Tecnología")
    tecnologia_2 = crear_empleado(nombre=f"Persona Tecnologia Dos {sufijo}", departamento="Tecnología")
    crear_empleado(nombre=f"Persona Ventas {sufijo}", departamento="Ventas")

    respuesta = httpx.get(
        f"{url_api}/api/empleados",
        params={"busqueda": sufijo, "departamento": "Tecnología"},
    )

    assert respuesta.status_code == 200
    resultados = respuesta.json()
    assert len(resultados) == 2
    numeros = {empleado["numero_empleado"] for empleado in resultados}
    assert numeros == {tecnologia_1["numero_empleado"], tecnologia_2["numero_empleado"]}
    assert all(empleado["departamento"] == "Tecnología" for empleado in resultados)


def test_cp09_buscar_texto_sin_coincidencias(url_api, crear_empleado):
    """CP-09: Buscar un texto que no coincide con ningún empleado."""
    crear_empleado(nombre="Ana Torres")
    texto_busqueda = f"zzz-no-existe-{uuid.uuid4().hex[:8]}"

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"busqueda": texto_busqueda})

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_cp11_empleado_baja_sigue_en_el_directorio(url_api, crear_empleado, marcar_baja):
    """CP-11: Un empleado dado de baja sigue apareciendo en el directorio."""
    empleado = crear_empleado(nombre="Carlos Pérez")
    marcar_baja(empleado["correo"])

    respuesta = httpx.get(f"{url_api}/api/empleados")

    assert respuesta.status_code == 200
    por_correo = {item["correo"]: item for item in respuesta.json()}
    assert por_correo[empleado["correo"]]["estado"] == "baja"
