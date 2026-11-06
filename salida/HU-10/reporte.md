# Reporte · HU-10

**Estado:** LISTA
**Costo de agentes:** 2.31 USD
**Ciclos de corrección:** 2

## Bitácora
- Filtro de historia: OK
- Criterios escritos en criterios.feature
- Preguntas abiertas: la persona respondió 'si'
- Casos de prueba escritos en casos_prueba.json
- Plan rechazado: No. 1) La ruta usa el id numérico del contrato: /api/empleados/{empleado_id}/vacaciones con empleado_id = Empleado.id, y la respuesta devuelve empleado_id como entero; acepta también EMP-000N como alias para ser consistente con HU-03, pero el contrato es el id numérico. 2) Usa los códigos y textos exactos de la tabla de CLAUDE.md: 404, 409 y 400; el 422 solo para formato de fecha inválido. 3) GET sin anio usa el año en curso. 4) Antigüedad: si fecha_ingreso es 29 de febrero, el aniversario en año no bisiesto es el 1 de marzo. 5) En pantalla, el éxito es exactamente "Solicitud registrada: N días hábiles. Te quedan M días hábiles en AAAA." y vacaciones-disponibles se actualiza después de registrar. No cambies las rutas de HU-01 a HU-03.
- Plan aprobado por una persona
- Construcción 1
- Verificación: OK
- Pruebas automatizadas: OK (25 casos)
- Despliegue: OK
- Despliegue y pruebas listos
- Pruebas E2E: 1 failed, 46 passed, 1 warning in 88.53s (0:01:28)
- Triage → desarrollador: El elemento con test id "vacaciones-abrir-156" no aparece en pantalla para el empleado dado de baja "EMP-0015", lo que impide iniciar el flujo de solicitud de vacaciones. Esto sugiere que la UI no está renderizando correctamente el control para abrir el formulario de solicitud cuando el empleado está dado de baja, cuando según el criterio de aceptación la solicitud debe poder intentarse y ser rechazada con código 409 y el mensaje "No se pueden solicitar vacaciones para un empleado dado de baja" mostrado en el campo "vacaciones-mensaje".
- Código corregido; redespliegue OK
- Pruebas E2E: 1 failed, 46 passed, 1 warning in 87.74s (0:01:27)
- Triage → desarrollador: El test espera poder hacer clic en el elemento con test id "vacaciones-abrir-208" para abrir el formulario de solicitud de vacaciones del empleado EMP-0015, pero el elemento nunca aparece (timeout de 30s esperando el locator). Según el escenario "Rechazar la solicitud de un empleado dado de baja", debe poder intentarse la solicitud (el sistema la rechaza con 409), por lo que la UI debería permitir abrir el formulario para un empleado dado de baja y luego mostrar el mensaje de error al enviarlo; si el botón "vacaciones-abrir-208" no se renderiza (p.ej. porque la aplicación oculta o deshabilita la opción de solicitar vacaciones para empleados dados de baja en lugar de permitir la solicitud y mostrar el error 409 esperado), la aplicación no está cumpliendo el criterio de aceptación.
- Código corregido; redespliegue OK
- Pruebas E2E: 47 passed, 1 warning in 57.33s

## Última ejecución de pruebas
```
47 passed, 1 warning in 57.33s

```