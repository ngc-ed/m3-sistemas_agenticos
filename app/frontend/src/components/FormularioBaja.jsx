import { useState } from 'react'
import { darDeBajaEmpleado } from '../api.js'

export default function FormularioBaja({ numeroEmpleado, onDadoDeBaja, onCancelar }) {
  const [fechaBaja, setFechaBaja] = useState('')
  const [mensajeExito, setMensajeExito] = useState('')
  const [mensajeError, setMensajeError] = useState('')

  async function manejarEnvio(evento) {
    evento.preventDefault()
    setMensajeExito('')
    setMensajeError('')
    try {
      const empleado = await darDeBajaEmpleado(numeroEmpleado, fechaBaja)
      setMensajeExito(`Empleado ${empleado.numero_empleado} dado de baja con éxito`)
      onDadoDeBaja?.(empleado)
    } catch (error) {
      setMensajeError(error.detail || 'Ocurrió un error inesperado')
    }
  }

  return (
    <form onSubmit={manejarEnvio}>
      <h2>Dar de baja a {numeroEmpleado}</h2>

      <label htmlFor="empleado-fecha-baja">Fecha de baja</label>
      <input
        id="empleado-fecha-baja"
        data-testid="empleado-fecha-baja"
        type="date"
        value={fechaBaja}
        onChange={(evento) => setFechaBaja(evento.target.value)}
        required
      />

      <button type="submit" data-testid="confirmar-baja">
        Confirmar baja
      </button>
      <button type="button" onClick={onCancelar}>
        Cancelar
      </button>

      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}
    </form>
  )
}
