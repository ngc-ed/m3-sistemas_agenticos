# language: es
# HU-01 · Registrar empleado

Característica: Registrar empleado
  Como persona del área de Recursos Humanos
  quiero registrar a un empleado con su nombre, correo corporativo, puesto, departamento y fecha de ingreso
  para darlo de alta en la empresa

  Escenario: Registrar un empleado con datos válidos asigna número de empleado y confirma el alta
    Dado que no existe ningún empleado con correo "ana.lopez@empresa.com"
    Y que el último número de empleado asignado es "EMP-0007"
    Cuando registro un empleado con los siguientes datos:
      | nombre        | Ana López              |
      | correo        | Ana.Lopez@empresa.com  |
      | puesto        | Analista de Datos      |
      | departamento  | Tecnología             |
      | fecha_ingreso | 2024-05-01             |
    Entonces el sistema responde con código 201
    Y el empleado queda registrado con número "EMP-0008"
    Y el correo del empleado se guarda como "ana.lopez@empresa.com"
    Y el estado del empleado es "activo"
    Y la pantalla muestra el mensaje "Empleado EMP-0008 registrado con éxito"

  Escenario: No se puede registrar un empleado con un correo ya existente
    Dado que ya existe un empleado registrado con correo "ana.lopez@empresa.com"
    Cuando registro un empleado con correo "ANA.LOPEZ@empresa.com", nombre "Ana López Reyes", puesto "Analista Senior", departamento "Tecnología" y fecha de ingreso "2024-05-01"
    Entonces el sistema responde con código 409
    Y la pantalla muestra el mensaje "El correo ya está registrado"
    Y no se crea un nuevo empleado

  Escenario: El correo debe terminar en @empresa.com
    Dado que no existe ningún empleado con correo "carlos.ruiz@gmail.com"
    Cuando registro un empleado con correo "carlos.ruiz@gmail.com", nombre "Carlos Ruiz", puesto "Vendedor", departamento "Ventas" y fecha de ingreso "2024-01-10"
    Entonces el sistema responde con código 422
    Y la pantalla muestra el mensaje "Usa el correo corporativo @empresa.com"
    Y no se crea un nuevo empleado

  Escenario: La fecha de ingreso no puede ser futura
    Dado que la fecha actual del sistema es "2024-06-01"
    Y que no existe ningún empleado con correo "laura.gomez@empresa.com"
    Cuando registro un empleado con correo "laura.gomez@empresa.com", nombre "Laura Gómez", puesto "Contadora", departamento "Finanzas" y fecha de ingreso "2024-06-15"
    Entonces el sistema responde con código 422
    Y la pantalla muestra el mensaje "La fecha de ingreso no puede ser futura"
    Y no se crea un nuevo empleado

  Escenario: El nombre debe tener entre 2 y 80 caracteres
    Dado que no existe ningún empleado con correo "jp@empresa.com"
    Cuando registro un empleado con correo "jp@empresa.com", nombre "J", puesto "Soporte Técnico", departamento "Operaciones" y fecha de ingreso "2024-02-01"
    Entonces el sistema responde con código 422
    Y la pantalla indica que el campo "nombre" debe corregirse
    Y no se crea un nuevo empleado

  Escenario: El puesto debe tener entre 2 y 60 caracteres
    Dado que no existe ningún empleado con correo "mario.diaz@empresa.com"
    Cuando registro un empleado con correo "mario.diaz@empresa.com", nombre "Mario Díaz", puesto "A", departamento "Recursos Humanos" y fecha de ingreso "2024-03-01"
    Entonces el sistema responde con código 422
    Y la pantalla indica que el campo "puesto" debe corregirse
    Y no se crea un nuevo empleado

  Escenario: El departamento debe ser uno de los valores permitidos
    Dado que no existe ningún empleado con correo "sofia.torres@empresa.com"
    Cuando registro un empleado con correo "sofia.torres@empresa.com", nombre "Sofía Torres", puesto "Diseñadora", departamento "Marketing" y fecha de ingreso "2024-04-01"
    Entonces el sistema responde con código 422
    Y la pantalla indica que el campo "departamento" debe corregirse
    Y no se crea un nuevo empleado

  Escenario: La fecha de ingreso es obligatoria
    Dado que no existe ningún empleado con correo "pedro.luna@empresa.com"
    Cuando registro un empleado con correo "pedro.luna@empresa.com", nombre "Pedro Luna", puesto "Operador", departamento "Operaciones" y sin fecha de ingreso
    Entonces el sistema responde con código 422
    Y la pantalla indica que el campo "fecha_ingreso" debe corregirse
    Y no se crea un nuevo empleado

# Preguntas abiertas
# - No se especifica el formato exacto de fecha esperado en la pantalla/API (DD/MM/AAAA vs AAAA-MM-DD).
# - No se especifica si el campo "nombre" admite números o caracteres especiales, solo el rango de longitud.
# - No se indica si el mensaje de confirmación debe mostrarse en pantalla, como notificación, o ambos.
