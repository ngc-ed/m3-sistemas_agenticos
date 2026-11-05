import { useEffect, useState } from 'react'
import { actualizarEmpleado, obtenerDepartamentos, obtenerEmpleado } from '../api.js'

export default function FormularioEdicion({ numeroEmpleado, onActualizado, onCancelar }) {
  const [departamentos, setDepartamentos] = useState([])
  const [puesto, setPuesto] = useState('')
  const [departamento, setDepartamento] = useState('')
  const [mensajeExito, setMensajeExito] = useState('')
  const [mensajeError, setMensajeError] = useState('')

  useEffect(() => {
    obtenerDepartamentos()
      .then(setDepartamentos)
      .catch(() => setDepartamentos([]))
  }, [])

  useEffect(() => {
    setMensajeExito('')
    setMensajeError('')
    obtenerEmpleado(numeroEmpleado).then((empleado) => {
      setPuesto(empleado.puesto)
      setDepartamento(empleado.departamento)
    })
  }, [numeroEmpleado])

  async function manejarEnvio(evento) {
    evento.preventDefault()
    setMensajeExito('')
    setMensajeError('')
    try {
      const empleado = await actualizarEmpleado(numeroEmpleado, { puesto, departamento })
      setMensajeExito(`Empleado ${empleado.numero_empleado} actualizado con éxito`)
      onActualizado?.(empleado)
    } catch (error) {
      setMensajeError(error.detail || 'Ocurrió un error inesperado')
    }
  }

  return (
    <form onSubmit={manejarEnvio}>
      <h2>Editar empleado {numeroEmpleado}</h2>

      <label htmlFor="empleado-puesto">Puesto</label>
      <input
        id="empleado-puesto"
        data-testid="empleado-puesto"
        type="text"
        value={puesto}
        onChange={(evento) => setPuesto(evento.target.value)}
        required
      />

      <label htmlFor="empleado-departamento">Departamento</label>
      <select
        id="empleado-departamento"
        data-testid="empleado-departamento"
        value={departamento}
        onChange={(evento) => setDepartamento(evento.target.value)}
        required
      >
        <option value="" disabled>
          Selecciona un departamento
        </option>
        {departamentos.map((item) => (
          <option key={item} value={item}>
            {item}
          </option>
        ))}
      </select>

      <button type="submit" data-testid="empleado-guardar">
        Guardar
      </button>
      <button type="button" onClick={onCancelar}>
        Cancelar
      </button>

      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}
    </form>
  )
}
