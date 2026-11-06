# language: es

Característica: Solicitar vacaciones
  Como empleado de la empresa
  quiero solicitar días de vacaciones indicando una fecha de inicio y una de fin
  para que mi solicitud quede registrada y sepa cuántos días me quedan en el año

  Escenario: Registrar una solicitud válida de vacaciones
    Dado un empleado activo "EMP-0007" con fecha_ingreso "2023-01-10"
    Y el empleado no tiene solicitudes de vacaciones registradas en 2026
    Cuando solicita vacaciones del "2026-12-21" al "2026-12-31"
    Entonces la API responde con código 201
    Y el campo "dias_habiles" de la respuesta es 8
    Y el campo "dias_restantes" de la respuesta es 4
    Y en la pantalla el campo "vacaciones-mensaje" muestra "Solicitud registrada: 8 días hábiles. Te quedan 4 días hábiles en 2026."

  Escenario: Los festivos y fines de semana dentro del periodo no se descuentan
    Dado un empleado activo "EMP-0008" con fecha_ingreso "2022-05-01"
    Y el empleado no tiene solicitudes de vacaciones registradas en 2026
    Cuando solicita vacaciones del "2026-09-14" al "2026-09-18"
    Entonces la API responde con código 201
    Y el campo "dias_habiles" de la respuesta es 4
    Y el campo "dias_restantes" de la respuesta es 8
    Y en la pantalla el campo "vacaciones-mensaje" muestra "Solicitud registrada: 4 días hábiles. Te quedan 8 días hábiles en 2026."

  Escenario: Registrar una solicitud que usa exactamente los días hábiles que quedan
    Dado un empleado activo "EMP-0017" con fecha_ingreso "2022-03-15"
    Y el empleado ya registró una solicitud de vacaciones del "2026-07-06" al "2026-07-10" que consumió 5 días hábiles
    Cuando solicita vacaciones del "2026-07-13" al "2026-07-21"
    Entonces la API responde con código 201
    Y el campo "dias_habiles" de la respuesta es 7
    Y el campo "dias_restantes" de la respuesta es 0
    Y en la pantalla el campo "vacaciones-mensaje" muestra "Solicitud registrada: 7 días hábiles. Te quedan 0 días hábiles en 2026."

  Escenario: Rechazar la solicitud de un empleado con menos de un año de antigüedad
    Dado un empleado activo "EMP-0009" con fecha_ingreso "2025-12-21"
    Cuando solicita vacaciones del "2026-12-18" al "2026-12-18"
    Entonces la API responde con código 400
    Y el mensaje de error es "Se requiere al menos un año de antigüedad a la fecha de inicio"
    Y en la pantalla el campo "vacaciones-mensaje" muestra "Se requiere al menos un año de antigüedad a la fecha de inicio"

  Escenario: Rechazar un periodo sin ningún día hábil
    Dado un empleado activo "EMP-0010" con fecha_ingreso "2022-01-01"
    Cuando solicita vacaciones del "2026-07-11" al "2026-07-12"
    Entonces la API responde con código 400
    Y el mensaje de error es "El periodo no incluye días hábiles"
    Y en la pantalla el campo "vacaciones-mensaje" muestra "El periodo no incluye días hábiles"

  Escenario: Rechazar una solicitud que rebasa los días disponibles del año cuando ya no queda ninguno
    Dado un empleado activo "EMP-0011" con fecha_ingreso "2023-01-05"
    Y el empleado ya registró una solicitud de vacaciones del "2026-01-05" al "2026-01-20" que consumió 12 días hábiles
    Cuando solicita vacaciones del "2026-11-02" al "2026-11-03"
    Entonces la API responde con código 400
    Y el mensaje de error es "La solicitud excede los días disponibles: quedan 0 días hábiles"
    Y en la pantalla el campo "vacaciones-mensaje" muestra "La solicitud excede los días disponibles: quedan 0 días hábiles"

  Escenario: Rechazar una solicitud que pide un día hábil más de los que quedan
    Dado un empleado activo "EMP-0018" con fecha_ingreso "2022-06-01"
    Y el empleado ya registró una solicitud de vacaciones del "2026-12-21" al "2026-12-31" que consumió 8 días hábiles
    Cuando solicita vacaciones del "2026-08-03" al "2026-08-07"
    Entonces la API responde con código 400
    Y el mensaje de error es "La solicitud excede los días disponibles: quedan 4 días hábiles"
    Y en la pantalla el campo "vacaciones-mensaje" muestra "La solicitud excede los días disponibles: quedan 4 días hábiles"

  Escenario: Rechazar una fecha de fin anterior a la fecha de inicio
    Dado un empleado activo "EMP-0012" con fecha_ingreso "2022-01-01"
    Cuando solicita vacaciones del "2026-07-10" al "2026-07-05"
    Entonces la API responde con código 400
    Y el mensaje de error es "La fecha de fin no puede ser anterior a la fecha de inicio"
    Y en la pantalla el campo "vacaciones-mensaje" muestra "La fecha de fin no puede ser anterior a la fecha de inicio"

  Escenario: Rechazar un periodo que cruza de un año a otro
    Dado un empleado activo "EMP-0013" con fecha_ingreso "2022-01-01"
    Cuando solicita vacaciones del "2026-12-28" al "2027-01-08"
    Entonces la API responde con código 400
    Y el mensaje de error es "Las vacaciones deben estar dentro de un mismo año calendario"
    Y en la pantalla el campo "vacaciones-mensaje" muestra "Las vacaciones deben estar dentro de un mismo año calendario"

  Escenario: Rechazar un año fuera del catálogo de festivos
    Dado un empleado activo "EMP-0014" con fecha_ingreso "2020-01-01"
    Cuando solicita vacaciones del "2025-07-07" al "2025-07-11"
    Entonces la API responde con código 400
    Y el mensaje de error es "Solo se pueden solicitar vacaciones en 2026 y 2027"
    Y en la pantalla el campo "vacaciones-mensaje" muestra "Solo se pueden solicitar vacaciones en 2026 y 2027"

  Escenario: Rechazar la solicitud de un empleado que no existe
    Dado que no existe un empleado con id 9999
    Cuando se solicitan vacaciones del "2026-07-06" al "2026-07-10" para el empleado 9999
    Entonces la API responde con código 404
    Y el mensaje de error es "Empleado no encontrado"

  Escenario: Rechazar la solicitud de un empleado dado de baja
    Dado un empleado dado de baja "EMP-0015" con fecha_ingreso "2020-01-01"
    Cuando solicita vacaciones del "2026-07-06" al "2026-07-10"
    Entonces la API responde con código 409
    Y el mensaje de error es "No se pueden solicitar vacaciones para un empleado dado de baja"
    Y en la pantalla el campo "vacaciones-mensaje" muestra "No se pueden solicitar vacaciones para un empleado dado de baja"

  Escenario: Consultar el saldo de vacaciones del año tras registrar una solicitud
    Dado un empleado activo "EMP-0016" con fecha_ingreso "2023-01-10"
    Y el empleado registró una solicitud de vacaciones del "2026-12-21" al "2026-12-31" que consumió 8 días hábiles
    Cuando consulta su saldo de vacaciones del año 2026
    Entonces la API responde con código 200
    Y el campo "dias_usados" de la respuesta es 8
    Y el campo "dias_disponibles" de la respuesta es 4
    Y en la pantalla el campo "vacaciones-disponibles" muestra "4"

# Preguntas abiertas
# Ninguna: la información de contexto/reglas_negocio.md y contexto/convenciones_app.md cubrió
# todos los datos necesarios (reglas, mensajes exactos, formato de fechas y festivos 2026-2027).
