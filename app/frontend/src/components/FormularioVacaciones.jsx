import { useEffect, useState } from 'react'
import { obtenerSaldoVacaciones, solicitarVacaciones } from '../api.js'

export default function FormularioVacaciones({ empleadoId, onCancelar }) {
  const [fechaInicio, setFechaInicio] = useState('')
  const [fechaFin, setFechaFin] = useState('')
  const [diasDisponibles, setDiasDisponibles] = useState(null)
  const [mensaje, setMensaje] = useState('')

  function cargarSaldo() {
    obtenerSaldoVacaciones(empleadoId)
      .then((saldo) => setDiasDisponibles(saldo.dias_disponibles))
      .catch(() => setDiasDisponibles(null))
  }

  useEffect(() => {
    setMensaje('')
    cargarSaldo()
  }, [empleadoId])

  async function manejarEnvio(evento) {
    evento.preventDefault()
    setMensaje('')
    try {
      const resultado = await solicitarVacaciones(empleadoId, {
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin,
      })
      const anio = resultado.fecha_inicio.slice(0, 4)
      setMensaje(
        `Solicitud registrada: ${resultado.dias_habiles} días hábiles. Te quedan ${resultado.dias_restantes} días hábiles en ${anio}.`
      )
      cargarSaldo()
    } catch (error) {
      setMensaje(error.detail || 'Ocurrió un error inesperado')
    }
  }

  return (
    <form onSubmit={manejarEnvio}>
      <h2>Solicitar vacaciones</h2>

      <p>
        Días disponibles en el año:{' '}
        <span data-testid="vacaciones-disponibles">{diasDisponibles ?? ''}</span>
      </p>

      <label htmlFor="vacaciones-fecha-inicio">Fecha de inicio</label>
      <input
        id="vacaciones-fecha-inicio"
        data-testid="vacaciones-fecha-inicio"
        type="date"
        value={fechaInicio}
        onChange={(evento) => setFechaInicio(evento.target.value)}
        required
      />

      <label htmlFor="vacaciones-fecha-fin">Fecha de fin</label>
      <input
        id="vacaciones-fecha-fin"
        data-testid="vacaciones-fecha-fin"
        type="date"
        value={fechaFin}
        onChange={(evento) => setFechaFin(evento.target.value)}
        required
      />

      <button type="submit" data-testid="vacaciones-enviar">
        Enviar solicitud
      </button>
      <button type="button" onClick={onCancelar}>
        Cancelar
      </button>

      {mensaje && <p data-testid="vacaciones-mensaje">{mensaje}</p>}
    </form>
  )
}
