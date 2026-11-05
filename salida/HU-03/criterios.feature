# language: es

Característica: Editar y dar de baja a un empleado
  Como persona del área de Recursos Humanos
  quiero cambiar el puesto y el departamento de un empleado, y poder darlo de baja
  para mantener el directorio al día sin perder el historial

  Escenario: Editar puesto y departamento de un empleado activo
    Dado un empleado con número "EMP-0001" en estado "activo" con puesto "Analista" y departamento "Ventas"
    Cuando edito su puesto a "Analista Senior" y su departamento a "Tecnología"
    Entonces el sistema responde 200
    Y el empleado "EMP-0001" tiene puesto "Analista Senior" y departamento "Tecnología"
    Y su número de empleado sigue siendo "EMP-0001"
    Y su correo sigue siendo "lucia.perez@empresa.com"

  Escenario: Error al editar con un departamento que no está en la lista permitida
    Dado un empleado con número "EMP-0001" en estado "activo" con departamento "Ventas"
    Cuando edito su departamento a "Marketing"
    Entonces el sistema responde 422
    Y el mensaje indica que el campo "departamento" debe corregirse
    Y el departamento del empleado "EMP-0001" sigue siendo "Ventas"

  Escenario: Error al intentar editar a un empleado dado de baja
    Dado un empleado con número "EMP-0002" en estado "baja"
    Cuando intento editar su puesto a "Gerente"
    Entonces el sistema responde 409 con el mensaje "No se puede editar a un empleado dado de baja"
    Y los datos del empleado "EMP-0002" no cambian

  Escenario: Dar de baja a un empleado activo
    Dado un empleado con número "EMP-0001" en estado "activo" con fecha de ingreso "2022-01-10"
    Cuando lo doy de baja con fecha de baja "2024-05-15"
    Entonces el sistema responde 200
    Y el empleado "EMP-0001" tiene estado "baja" y fecha de baja "2024-05-15"
    Y el empleado "EMP-0001" sigue apareciendo en el directorio

  Escenario: Error al dar de baja con una fecha de baja anterior a la fecha de ingreso
    Dado un empleado con número "EMP-0001" en estado "activo" con fecha de ingreso "2022-01-10"
    Cuando intento darlo de baja con fecha de baja "2021-12-01"
    Entonces el sistema responde 422
    Y el mensaje indica que el campo "fecha_baja" debe corregirse
    Y el estado del empleado "EMP-0001" sigue siendo "activo"

# Preguntas abiertas
# - ¿Qué debe pasar si en la edición se envían valores distintos para numero_empleado o correo?
#   Las reglas dicen que no se editan, pero no se especifica si el sistema debe ignorar
#   esos campos silenciosamente, devolver un error 422/409, o algún otro comportamiento.
# - ¿Qué debe pasar si se intenta dar de baja a un empleado que ya está en estado "baja"?
#   No hay una regla que indique si debe responder con error (y con qué mensaje/código)
#   o si la operación simplemente no tiene efecto.
