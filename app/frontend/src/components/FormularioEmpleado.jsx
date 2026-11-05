import { useEffect, useState } from 'react'
import { obtenerDepartamentos, registrarEmpleado } from '../api.js'

const VALORES_INICIALES = {
  nombre: '',
  correo: '',
  puesto: '',
  departamento: '',
  fecha_ingreso: '',
}

export default function FormularioEmpleado({ onEmpleadoRegistrado }) {
  const [departamentos, setDepartamentos] = useState([])
  const [valores, setValores] = useState(VALORES_INICIALES)
  const [mensajeExito, setMensajeExito] = useState('')
  const [mensajeError, setMensajeError] = useState('')

  useEffect(() => {
    obtenerDepartamentos()
      .then(setDepartamentos)
      .catch(() => setDepartamentos([]))
  }, [])

  function actualizarCampo(campo, valor) {
    setValores((anteriores) => ({ ...anteriores, [campo]: valor }))
  }

  async function manejarEnvio(evento) {
    evento.preventDefault()
    setMensajeExito('')
    setMensajeError('')
    try {
      const empleado = await registrarEmpleado(valores)
      setMensajeExito(`Empleado ${empleado.numero_empleado} registrado con éxito`)
      setValores(VALORES_INICIALES)
      onEmpleadoRegistrado?.(empleado)
    } catch (error) {
      setMensajeError(error.detail || 'Ocurrió un error inesperado')
    }
  }

  return (
    <form onSubmit={manejarEnvio}>
      <h2>Registrar empleado</h2>

      <label htmlFor="empleado-nombre">Nombre</label>
      <input
        id="empleado-nombre"
        data-testid="empleado-nombre"
        type="text"
        value={valores.nombre}
        onChange={(evento) => actualizarCampo('nombre', evento.target.value)}
        required
      />

      <label htmlFor="empleado-correo">Correo</label>
      <input
        id="empleado-correo"
        data-testid="empleado-correo"
        type="email"
        value={valores.correo}
        onChange={(evento) => actualizarCampo('correo', evento.target.value)}
        required
      />

      <label htmlFor="empleado-puesto">Puesto</label>
      <input
        id="empleado-puesto"
        data-testid="empleado-puesto"
        type="text"
        value={valores.puesto}
        onChange={(evento) => actualizarCampo('puesto', evento.target.value)}
        required
      />

      <label htmlFor="empleado-departamento">Departamento</label>
      <select
        id="empleado-departamento"
        data-testid="empleado-departamento"
        value={valores.departamento}
        onChange={(evento) => actualizarCampo('departamento', evento.target.value)}
        required
      >
        <option value="" disabled>
          Selecciona un departamento
        </option>
        {departamentos.map((departamento) => (
          <option key={departamento} value={departamento}>
            {departamento}
          </option>
        ))}
      </select>

      <label htmlFor="empleado-fecha-ingreso">Fecha de ingreso</label>
      <input
        id="empleado-fecha-ingreso"
        data-testid="empleado-fecha-ingreso"
        type="date"
        value={valores.fecha_ingreso}
        onChange={(evento) => actualizarCampo('fecha_ingreso', evento.target.value)}
        required
      />

      <button type="submit" data-testid="empleado-guardar">
        Guardar
      </button>

      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}
    </form>
  )
}
