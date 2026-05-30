"""
puntajes_casos.py - Blueprint CRUD para la tabla puntajes_casos.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.api_service import ApiService

bp = Blueprint('puntajes_casos', __name__)
api = ApiService()

# ------------------------------------------------------------------
# Helper global: obtener médico válido (fallback al primero si no hay sesión)
# ------------------------------------------------------------------
def _obtener_medico_id():
    """Devuelve el id de médico asociado al usuario logueado.
    Si no hay sesión o el email no coincide, devuelve el primer médico
    disponible. Lanza RuntimeError si la tabla está vacía.
    """
    email_usuario = session.get('usuario')
    medicos = api.listar('medico_experto')
    # 1️⃣ Intentar coincidencia por email
    medico = next((m for m in medicos if m.get('email') == email_usuario), None)
    if medico:
        return medico['id']
    # 2️⃣ Fallback al primer médico activo (evita NULL en la FK)
    if medicos:
        return medicos[0]['id']
    # 3️⃣ No hay médicos registrados
    raise RuntimeError('No hay médicos registrados en la base de datos')

TABLA = 'puntajes_casos'
CLAVE = 'id'

@bp.route('/puntajes_casos')
def index():
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')
    valor_clave = request.args.get('clave', '')

    registros = api.listar(TABLA, limite)

    # Datos auxiliares para el formulario de creación/edición
    criterios = api.listar('criterios_evaluacion')
    casos     = api.listar('casos_clinicos')
    modelos   = api.listar('modelos')
    medicos   = api.listar('medico_experto')

    # Diccionario id → nombre para resolución rápida en la tabla
    medicos_dict = {m['id']: m.get('nombre', 'Sin nombre') for m in medicos}

    mostrar_formulario = accion in ('nuevo', 'editar')
    editando = accion == 'editar'

    registro = None
    if editando and valor_clave:
        registro = next((r for r in registros if str(r.get(CLAVE)) == valor_clave), None)

    return render_template('pages/puntajes_casos.html',
        registros=registros,
        criterios=criterios,
        casos=casos,
        modelos=modelos,
        medicos=medicos,
        medicos_dict=medicos_dict,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite
    )

@bp.route('/puntajes_casos/crear', methods=['POST'])
def crear():
    try:
        medico_id = _obtener_medico_id()
    except RuntimeError as err:
        flash(str(err), 'danger')
        return redirect(url_for('puntajes_casos.index'))

    datos = {
        'caso_id':           request.form.get('caso_id', 0, type=int),
        'criterio_id':       request.form.get('criterio_id', 0, type=int),
        'modelo_id':         request.form.get('modelo_id', 1, type=int),
        'puntaje':           request.form.get('puntaje', 1, type=int),
        'observacion':       request.form.get('observacion', ''),
        'medico_experto_id': medico_id
    }
    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('puntajes_casos.index'))

@bp.route('/puntajes_casos/actualizar', methods=['POST'])
def actualizar():
    valor = request.form.get('id', 0, type=int)
    try:
        medico_id = _obtener_medico_id()
    except RuntimeError as err:
        flash(str(err), 'danger')
        return redirect(url_for('puntajes_casos.index'))

    datos = {
        'caso_id':           request.form.get('caso_id', 0, type=int),
        'criterio_id':       request.form.get('criterio_id', 0, type=int),
        'modelo_id':         request.form.get('modelo_id', 1, type=int),
        'puntaje':           request.form.get('puntaje', 1, type=int),
        'observacion':       request.form.get('observacion', ''),
        'medico_experto_id': medico_id
    }
    exito, mensaje = api.actualizar(TABLA, CLAVE, valor, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('puntajes_casos.index'))

@bp.route('/puntajes_casos/eliminar', methods=['POST'])
def eliminar():
    valor = request.form.get('id', 0, type=int)
    exito, mensaje = api.eliminar(TABLA, CLAVE, valor)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('puntajes_casos.index'))
