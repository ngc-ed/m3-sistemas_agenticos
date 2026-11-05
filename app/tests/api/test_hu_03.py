"""Pruebas de API para HU-03: editar y dar de baja empleados."""

import httpx


def test_cp01_editar_puesto_y_departamento_de_empleado_activo(url_api, crear_empleado):
    """CP-01: Editar puesto y departamento de un empleado activo."""
    empleado = crear_empleado(puesto="Analista", departamento="Ventas")

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}",
        json={"puesto": "Analista Senior", "departamento": "Tecnología"},
    )

    assert respuesta.status_code == 200
    actualizado = respuesta.json()
    assert actualizado["puesto"] == "Analista Senior"
    assert actualizado["departamento"] == "Tecnología"

    respuesta_get = httpx.get(f"{url_api}/api/empleados/{empleado['numero_empleado']}")
    assert respuesta_get.status_code == 200
    datos = respuesta_get.json()
    assert datos["numero_empleado"] == empleado["numero_empleado"]
    assert datos["correo"] == empleado["correo"]


def test_cp03_error_al_editar_con_departamento_no_permitido(url_api, crear_empleado):
    """CP-03: Error al editar con un departamento que no está en la lista permitida."""
    empleado = crear_empleado(puesto="Analista", departamento="Ventas")

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}",
        json={"puesto": empleado["puesto"], "departamento": "Marketing"},
    )

    assert respuesta.status_code == 422
    cuerpo = respuesta.json()
    assert cuerpo.get("campo") == "departamento"

    respuesta_get = httpx.get(f"{url_api}/api/empleados/{empleado['numero_empleado']}")
    assert respuesta_get.json()["departamento"] == "Ventas"


def test_cp05_error_al_editar_empleado_dado_de_baja(url_api, crear_empleado, marcar_baja):
    """CP-05: Error al intentar editar a un empleado dado de baja."""
    empleado = crear_empleado(puesto="Analista", departamento="Ventas")
    marcar_baja(empleado["correo"])

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}",
        json={"puesto": "Gerente", "departamento": empleado["departamento"]},
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "No se puede editar a un empleado dado de baja"

    respuesta_get = httpx.get(f"{url_api}/api/empleados/{empleado['numero_empleado']}")
    datos = respuesta_get.json()
    assert datos["puesto"] == "Analista"
    assert datos["estado"] == "baja"


def test_cp07_dar_de_baja_a_un_empleado_activo(url_api, crear_empleado):
    """CP-07: Dar de baja a un empleado activo."""
    empleado = crear_empleado(fecha_ingreso="2022-01-10")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/baja",
        json={"fecha_baja": "2024-05-15"},
    )

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["estado"] == "baja"
    assert datos["fecha_baja"] == "2024-05-15"

    respuesta_lista = httpx.get(f"{url_api}/api/empleados")
    numeros = {item["numero_empleado"] for item in respuesta_lista.json()}
    assert empleado["numero_empleado"] in numeros


def test_cp09_error_al_dar_de_baja_con_fecha_anterior_a_ingreso(url_api, crear_empleado):
    """CP-09: Error al dar de baja con una fecha de baja anterior a la fecha de ingreso."""
    empleado = crear_empleado(fecha_ingreso="2022-01-10")

    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['numero_empleado']}/baja",
        json={"fecha_baja": "2021-12-01"},
    )

    assert respuesta.status_code == 422
    cuerpo = respuesta.json()
    assert cuerpo.get("campo") == "fecha_baja"

    respuesta_get = httpx.get(f"{url_api}/api/empleados/{empleado['numero_empleado']}")
    assert respuesta_get.json()["estado"] == "activo"
