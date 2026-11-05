// Cliente de la API de gestión de empleados. Siempre usa rutas relativas /api/...
// para que funcione tanto con el proxy de Vite (desarrollo) como con el proxy de Docker.

async function manejarRespuesta(respuesta) {
  const cuerpo = await respuesta.json().catch(() => ({}))
  if (!respuesta.ok) {
    const error = new Error(cuerpo.detail || 'Ocurrió un error inesperado')
    error.detail = cuerpo.detail
    error.campo = cuerpo.campo
    error.status = respuesta.status
    throw error
  }
  return cuerpo
}

export async function obtenerEmpleados({ busqueda, departamento } = {}) {
  const parametros = new URLSearchParams()
  if (busqueda) parametros.set('busqueda', busqueda)
  if (departamento) parametros.set('departamento', departamento)
  const query = parametros.toString()
  const respuesta = await fetch(`/api/empleados${query ? `?${query}` : ''}`)
  return manejarRespuesta(respuesta)
}

export async function obtenerDepartamentos() {
  const respuesta = await fetch('/api/departamentos')
  return manejarRespuesta(respuesta)
}

export async function registrarEmpleado(datos) {
  const respuesta = await fetch('/api/empleados', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos),
  })
  return manejarRespuesta(respuesta)
}

export async function obtenerEmpleado(numeroEmpleado) {
  const respuesta = await fetch(`/api/empleados/${numeroEmpleado}`)
  return manejarRespuesta(respuesta)
}

export async function actualizarEmpleado(numeroEmpleado, datos) {
  const respuesta = await fetch(`/api/empleados/${numeroEmpleado}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos),
  })
  return manejarRespuesta(respuesta)
}

export async function darDeBajaEmpleado(numeroEmpleado, fechaBaja) {
  const respuesta = await fetch(`/api/empleados/${numeroEmpleado}/baja`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fecha_baja: fechaBaja }),
  })
  return manejarRespuesta(respuesta)
}
