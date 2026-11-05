import { useEffect, useState } from 'react'
import { obtenerDepartamentos } from '../api.js'

export default function FiltrosDirectorio({ busqueda, departamento, onCambiarFiltros }) {
  const [departamentos, setDepartamentos] = useState([])

  useEffect(() => {
    obtenerDepartamentos()
      .then(setDepartamentos)
      .catch(() => setDepartamentos([]))
  }, [])

  return (
    <div>
      <label htmlFor="buscar-empleados">Buscar</label>
      <input
        id="buscar-empleados"
        data-testid="buscar-empleados"
        type="text"
        value={busqueda}
        onChange={(evento) => onCambiarFiltros({ busqueda: evento.target.value, departamento })}
        placeholder="Nombre o correo"
      />

      <label htmlFor="filtro-departamento">Departamento</label>
      <select
        id="filtro-departamento"
        data-testid="filtro-departamento"
        value={departamento}
        onChange={(evento) => onCambiarFiltros({ busqueda, departamento: evento.target.value })}
      >
        <option value="">Todos</option>
        {departamentos.map((item) => (
          <option key={item} value={item}>
            {item}
          </option>
        ))}
      </select>
    </div>
  )
}
