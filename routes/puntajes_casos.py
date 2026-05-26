"""
puntajes_casos.py - Blueprint CRUD para la tabla puntajes_casos.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.api_service import ApiService

bp = Blueprint('puntajes_casos', __name__)
api = ApiService()

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
    # Buscar el ID del médico basado en el email del usuario logueado
    email_usuario = session.get('usuario')
    medicos = api.listar('medico_experto')
    medico_id = next((m['id'] for m in medicos if m.get('email') == email_usuario), None)

    datos = {
        'caso_id':           request.form.get('caso_id', 0, type=int),
        'criterio_id':       request.form.get('criterio_id', 0, type=int),
        'modelo_id':         request.form.get('modelo_id', 1, type=int),
        'puntaje':           request.form.get('puntaje', 1, type=int),
        'medico_experto_id': medico_id
    }
    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('puntajes_casos.index'))

@bp.route('/puntajes_casos/actualizar', methods=['POST'])
def actualizar():
    valor = request.form.get('id', 0, type=int)
    # Buscar el ID del médico basado en el email del usuario logueado
    email_usuario = session.get('usuario')
    medicos = api.listar('medico_experto')
    medico_id = next((m['id'] for m in medicos if m.get('email') == email_usuario), None)

    datos = {
        'caso_id':           request.form.get('caso_id', 0, type=int),
        'criterio_id':       request.form.get('criterio_id', 0, type=int),
        'puntaje':           request.form.get('puntaje', 1, type=int),
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
