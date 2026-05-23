"""
puntajes_ejecucion.py - Blueprint CRUD para la tabla puntajes_ejecucion.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService

bp = Blueprint('puntajes_ejecucion', __name__)
api = ApiService()

TABLA = 'puntajes_casos'
CLAVE = 'id'

@bp.route('/puntajes_ejecucion')
def index():
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')
    valor_clave = request.args.get('clave', '')

    registros = api.listar(TABLA, limite)
    
    # Obtener listados para los combos y datos relacionados
    ejecuciones = api.listar('ejecuciones')
    criterios = api.listar('criterios_evaluacion')
    casos = api.listar('casos_clinicos')
    modelos = api.listar('modelos')

    mostrar_formulario = accion in ('nuevo', 'editar')
    editando = accion == 'editar'

    registro = None
    if editando and valor_clave:
        registro = next(
            (r for r in registros if str(r.get(CLAVE)) == valor_clave),
            None
        )

    return render_template('pages/puntajes_ejecucion.html',
        registros=registros,
        ejecuciones=ejecuciones,
        criterios=criterios,
        casos=casos,
        modelos=modelos,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite
    )

@bp.route('/puntajes_ejecucion/crear', methods=['POST'])
def crear():
    datos = {
        'ejecucion_id': request.form.get('ejecucion_id', 0, type=int),
        'criterio_id': request.form.get('criterio_id', 0, type=int),
        'puntaje': request.form.get('puntaje', 1, type=int)
    }

    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('puntajes_ejecucion.index'))

@bp.route('/puntajes_ejecucion/actualizar', methods=['POST'])
def actualizar():
    valor = request.form.get('id', 0, type=int)
    datos = {
        'ejecucion_id': request.form.get('ejecucion_id', 0, type=int),
        'criterio_id': request.form.get('criterio_id', 0, type=int),
        'puntaje': request.form.get('puntaje', 1, type=int)
    }

    exito, mensaje = api.actualizar(TABLA, CLAVE, valor, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('puntajes_ejecucion.index'))

@bp.route('/puntajes_ejecucion/eliminar', methods=['POST'])
def eliminar():
    valor = request.form.get('id', 0, type=int)

    exito, mensaje = api.eliminar(TABLA, CLAVE, valor)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('puntajes_ejecucion.index'))