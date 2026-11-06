import { useEffect, useState } from 'react'
import FormularioEmpleado from './components/FormularioEmpleado.jsx'
import FormularioEdicion from './components/FormularioEdicion.jsx'
import FormularioBaja from './components/FormularioBaja.jsx'
import FormularioVacaciones from './components/FormularioVacaciones.jsx'
import FiltrosDirectorio from './components/FiltrosDirectorio.jsx'
import TablaEmpleados from './components/TablaEmpleados.jsx'
import { obtenerEmpleados } from './api.js'

export default function App() {
  const [empleados, setEmpleados] = useState([])
  const [busqueda, setBusqueda] = useState('')
  const [departamento, setDepartamento] = useState('')
  const [modo, setModo] = useState('alta')
  const [empleadoSeleccionado, setEmpleadoSeleccionado] = useState(null)
  const [intentoAccion, setIntentoAccion] = useState(0)

  function cargarEmpleados(filtros = { busqueda, departamento }) {
    obtenerEmpleados(filtros)
      .then(setEmpleados)
      .catch(() => setEmpleados([]))
  }

  useEffect(() => {
    cargarEmpleados({ busqueda, departamento })
  }, [busqueda, departamento])

  function manejarCambioFiltros({ busqueda: nuevaBusqueda, departamento: nuevoDepartamento }) {
    setBusqueda(nuevaBusqueda)
    setDepartamento(nuevoDepartamento)
  }

  function volverAAlta() {
    setModo('alta')
    setEmpleadoSeleccionado(null)
    cargarEmpleados()
  }

  return (
    <main>
      <h1>Gestión de empleados</h1>

      {modo === 'alta' && (
        <FormularioEmpleado onEmpleadoRegistrado={() => cargarEmpleados()} />
      )}

      {modo === 'editar' && empleadoSeleccionado && (
        <FormularioEdicion
          key={intentoAccion}
          numeroEmpleado={empleadoSeleccionado.numero_empleado}
          onActualizado={() => cargarEmpleados()}
          onCancelar={volverAAlta}
        />
      )}

      {modo === 'baja' && empleadoSeleccionado && (
        <FormularioBaja
          key={intentoAccion}
          numeroEmpleado={empleadoSeleccionado.numero_empleado}
          onDadoDeBaja={() => cargarEmpleados()}
          onCancelar={volverAAlta}
        />
      )}

      {modo === 'vacaciones' && empleadoSeleccionado && (
        <FormularioVacaciones
          key={intentoAccion}
          empleadoId={empleadoSeleccionado.id}
          onCancelar={volverAAlta}
        />
      )}

      <FiltrosDirectorio
        busqueda={busqueda}
        departamento={departamento}
        onCambiarFiltros={manejarCambioFiltros}
      />
      <TablaEmpleados
        empleados={empleados}
        onEditar={(empleado) => {
          setEmpleadoSeleccionado(empleado)
          setModo('editar')
          setIntentoAccion((valor) => valor + 1)
        }}
        onDarBaja={(empleado) => {
          setEmpleadoSeleccionado(empleado)
          setModo('baja')
          setIntentoAccion((valor) => valor + 1)
        }}
        onSolicitarVacaciones={(empleado) => {
          setEmpleadoSeleccionado(empleado)
          setModo('vacaciones')
          setIntentoAccion((valor) => valor + 1)
        }}
      />
    </main>
  )
}
