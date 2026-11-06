const ETIQUETAS_ESTADO = {
  activo: 'Activo',
  baja: 'Baja',
}

export default function TablaEmpleados({ empleados, onEditar, onDarBaja, onSolicitarVacaciones }) {
  if (empleados.length === 0) {
    return <p data-testid="sin-resultados">No se encontraron empleados</p>
  }

  return (
    <table data-testid="tabla-empleados">
      <thead>
        <tr>
          <th>Número</th>
          <th>Nombre</th>
          <th>Correo</th>
          <th>Puesto</th>
          <th>Departamento</th>
          <th>Fecha de ingreso</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {empleados.map((empleado) => (
          <tr key={empleado.id} data-testid={`fila-empleado-${empleado.id}`}>
            <td data-testid={`numero-empleado-${empleado.id}`}>{empleado.numero_empleado}</td>
            <td>{empleado.nombre}</td>
            <td>{empleado.correo}</td>
            <td>{empleado.puesto}</td>
            <td>{empleado.departamento}</td>
            <td>{empleado.fecha_ingreso}</td>
            <td data-testid={`estado-empleado-${empleado.id}`}>
              {ETIQUETAS_ESTADO[empleado.estado] || empleado.estado}
            </td>
            <td>
              <button
                type="button"
                data-testid={`editar-empleado-${empleado.id}`}
                onClick={() => onEditar?.(empleado)}
              >
                Editar
              </button>
              <button
                type="button"
                data-testid={`baja-empleado-${empleado.id}`}
                onClick={() => onDarBaja?.(empleado)}
              >
                Dar de baja
              </button>
              <button
                type="button"
                data-testid={`vacaciones-abrir-${empleado.id}`}
                onClick={() => onSolicitarVacaciones?.(empleado)}
              >
                Solicitar vacaciones
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
