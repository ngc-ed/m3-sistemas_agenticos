# Reporte · HU-03

**Estado:** LISTA
**Costo de agentes:** 2.70 USD
**Ciclos de corrección:** 2

## Bitácora
- Filtro de historia: OK
- Criterios escritos en criterios.feature
- Preguntas abiertas: la persona respondió 'si'
- Casos de prueba escritos en casos_prueba.json
- Plan rechazado: No cambies los data-testid existentes: según contexto/convenciones_app.md son fila-empleado-{id}, numero-empleado-{id}, estado-empleado-{id}, editar-empleado-{id} y baja-empleado-{id} con el id numérico, y cambiarlos rompe las pruebas de HU-02. No modifiques el comportamiento de HU-01 y HU-02. Si el formulario de edición reutiliza empleado-puesto, empleado-departamento y empleado-guardar, el formulario de alta no debe estar visible al mismo tiempo.
- Plan aprobado por una persona
- Construcción 1
- Verificación: OK
- Pruebas automatizadas: OK (10 casos)
- Despliegue: OK
- Despliegue y pruebas listos
- Pruebas E2E: 4 failed, 18 passed, 1 warning in 94.46s (0:01:34)
- Triage → automatizador: El test de API test_cp03_error_al_editar_con_departamento_no_permitido falla con AttributeError: 'str' object has no attribute 'get', lo cual indica un error en el código de la prueba (está tratando una respuesta string como si fuera un diccionario/objeto), no un fallo de la aplicación ni de infraestructura.
- Pruebas corregidas
- Pruebas E2E: 3 failed, 19 passed, 1 warning in 117.99s (0:01:57)
- Triage → desarrollador: En los escenarios de editar puesto/departamento de un empleado activo y de dar de baja a un empleado activo, la aplicación no muestra el mensaje de éxito (get_by_test_id("mensaje-exito") no se encuentra), y en el caso de departamento no permitido, el sistema permite guardar "Marketing" en el select en vez de rechazar el valor y mantener "Ventas". Esto indica que la UI/backend no está devolviendo o reflejando correctamente las respuestas 200/422 definidas en los criterios de aceptación.
- Código corregido; redespliegue OK
- Pruebas E2E: 22 passed, 1 warning in 78.55s (0:01:18)

## Última ejecución de pruebas
```
22 passed, 1 warning in 78.55s (0:01:18)

```