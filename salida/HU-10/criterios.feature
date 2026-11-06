# language: es

Característica: Solicitar vacaciones
  Como empleado de la empresa
  Quiero solicitar días de vacaciones indicando una fecha de inicio y una de fin
  Para que mi solicitud quede registrada y sepa cuántos días me quedan en el año

  Escenario: Solicitud válida de vacaciones se registra y descuenta los días hábiles
    Dado un empleado activo con id 7, fecha de ingreso "2024-03-10" y 0 días usados en 2026
    Y el empleado abre el formulario con el botón "vacaciones-abrir-7"
    Y el campo "vacaciones-disponibles" muestra "12" días disponibles para 2026
    Cuando escribe "2026-07-06" en "vacaciones-fecha-inicio"
    Y escribe "2026-07-10" en "vacaciones-fecha-fin"
    Y presiona "vacaciones-enviar"
    Entonces la API responde con código 201
    Y el cuerpo de la respuesta indica "dias_habiles": 5 y "dias_restantes": 7
    Y el campo "vacaciones-mensaje" muestra "Solicitud registrada: 5 días hábiles. Te quedan 7 días hábiles en 2026."

  Escenario: Los sábados, domingos y festivos dentro del periodo no se descuentan
    Dado un empleado activo con id 7, fecha de ingreso "2024-03-10" y 0 días usados en 2026
    Y el empleado abre el formulario con el botón "vacaciones-abrir-7"
    Cuando escribe "2026-12-21" en "vacaciones-fecha-inicio"
    Y escribe "2026-12-31" en "vacaciones-fecha-fin"
    Y presiona "vacaciones-enviar"
    Entonces la API responde con código 201
    Y el cuerpo de la respuesta indica "dias_habiles": 8 y "dias_restantes": 4
    Y el campo "vacaciones-mensaje" muestra "Solicitud registrada: 8 días hábiles. Te quedan 4 días hábiles en 2026."

  Escenario: Solicitud que usa exactamente los días que quedan deja el saldo en cero
    Dado un empleado activo con id 7, fecha de ingreso "2024-03-10"
    Y que para el año 2026 ya registró solicitudes con 7 días hábiles usados en total
    Y el campo "vacaciones-disponibles" muestra "5" días disponibles para 2026
    Y el empleado abre el formulario con el botón "vacaciones-abrir-7"
    Cuando escribe "2026-07-06" en "vacaciones-fecha-inicio"
    Y escribe "2026-07-10" en "vacaciones-fecha-fin"
    Y presiona "vacaciones-enviar"
    Entonces la API responde con código 201
    Y el cuerpo de la respuesta indica "dias_habiles": 5 y "dias_restantes": 0
    Y el campo "vacaciones-mensaje" muestra "Solicitud registrada: 5 días hábiles. Te quedan 0 días hábiles en 2026."

  Escenario: Rechazo por antigüedad menor a un año (Regla 1)
    Dado un empleado activo con id 9 y fecha de ingreso "2025-12-21"
    Y el empleado abre el formulario con el botón "vacaciones-abrir-9"
    Cuando escribe "2026-12-18" en "vacaciones-fecha-inicio"
    Y escribe "2026-12-18" en "vacaciones-fecha-fin"
    Y presiona "vacaciones-enviar"
    Entonces la API responde con código 400 y detail "Se requiere al menos un año de antigüedad a la fecha de inicio"
    Y el campo "vacaciones-mensaje" muestra "Se requiere al menos un año de antigüedad a la fecha de inicio"

  Escenario: Rechazo por rebasar el tope anual de 12 días hábiles (Regla 2)
    Dado un empleado activo con id 7, fecha de ingreso "2024-03-10"
    Y que para el año 2026 ya registró una solicitud del "2026-12-21" al "2026-12-31" con 8 días hábiles
    Y el campo "vacaciones-disponibles" muestra "4" días disponibles para 2026
    Y el empleado abre el formulario con el botón "vacaciones-abrir-7"
    Cuando escribe "2026-07-06" en "vacaciones-fecha-inicio"
    Y escribe "2026-07-10" en "vacaciones-fecha-fin"
    Y presiona "vacaciones-enviar"
    Entonces la API responde con código 400 y detail "La solicitud excede los días disponibles: quedan 4 días hábiles"
    Y el campo "vacaciones-mensaje" muestra "La solicitud excede los días disponibles: quedan 4 días hábiles"

  Escenario: Rechazo por periodo sin ningún día hábil (Regla 3)
    Dado un empleado activo con id 7, fecha de ingreso "2024-03-10" y 0 días usados en 2026
    Y el empleado abre el formulario con el botón "vacaciones-abrir-7"
    Cuando escribe "2026-07-11" en "vacaciones-fecha-inicio"
    Y escribe "2026-07-12" en "vacaciones-fecha-fin"
    Y presiona "vacaciones-enviar"
    Entonces la API responde con código 400 y detail "El periodo no incluye días hábiles"
    Y el campo "vacaciones-mensaje" muestra "El periodo no incluye días hábiles"

  Escenario: Rechazo cuando la fecha de fin es anterior a la fecha de inicio
    Dado un empleado activo con id 7, fecha de ingreso "2024-03-10" y 0 días usados en 2026
    Y el empleado abre el formulario con el botón "vacaciones-abrir-7"
    Cuando escribe "2026-07-10" en "vacaciones-fecha-inicio"
    Y escribe "2026-07-06" en "vacaciones-fecha-fin"
    Y presiona "vacaciones-enviar"
    Entonces la API responde con código 400 y detail "La fecha de fin no puede ser anterior a la fecha de inicio"
    Y el campo "vacaciones-mensaje" muestra "La fecha de fin no puede ser anterior a la fecha de inicio"

  Escenario: Rechazo cuando el periodo cruza de un año a otro
    Dado un empleado activo con id 7, fecha de ingreso "2024-03-10" y 0 días usados en 2026
    Y el empleado abre el formulario con el botón "vacaciones-abrir-7"
    Cuando escribe "2026-12-28" en "vacaciones-fecha-inicio"
    Y escribe "2027-01-08" en "vacaciones-fecha-fin"
    Y presiona "vacaciones-enviar"
    Entonces la API responde con código 400 y detail "Las vacaciones deben estar dentro de un mismo año calendario"
    Y el campo "vacaciones-mensaje" muestra "Las vacaciones deben estar dentro de un mismo año calendario"

  Escenario: Rechazo cuando el año solicitado no está en la tabla de festivos
    Dado un empleado activo con id 7, fecha de ingreso "2024-03-10" y 0 días usados en 2028
    Y el empleado abre el formulario con el botón "vacaciones-abrir-7"
    Cuando escribe "2028-07-06" en "vacaciones-fecha-inicio"
    Y escribe "2028-07-10" en "vacaciones-fecha-fin"
    Y presiona "vacaciones-enviar"
    Entonces la API responde con código 400 y detail "Solo se pueden solicitar vacaciones en 2026 y 2027"
    Y el campo "vacaciones-mensaje" muestra "Solo se pueden solicitar vacaciones en 2026 y 2027"

  Escenario: Rechazo cuando el empleado no existe
    Dado que no existe ningún empleado con id 9999
    Cuando se envía la petición "POST /api/empleados/9999/vacaciones" con fecha_inicio "2026-07-06" y fecha_fin "2026-07-10"
    Entonces la API responde con código 404 y detail "Empleado no encontrado"

  Escenario: Rechazo cuando el empleado está dado de baja
    Dado un empleado con id 12 en estado "baja"
    Cuando se envía la petición "POST /api/empleados/12/vacaciones" con fecha_inicio "2026-07-06" y fecha_fin "2026-07-10"
    Entonces la API responde con código 409 y detail "No se pueden solicitar vacaciones para un empleado dado de baja"

# Preguntas abiertas
# Ninguna: la historia, las reglas de negocio y las convenciones de vacaciones documentan
# todos los mensajes, códigos y datos necesarios para los escenarios anteriores.
