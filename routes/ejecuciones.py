"""
ejecuciones.py - Blueprint CRUD para la tabla ejecuciones.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService

bp = Blueprint('ejecuciones', __name__)
api = ApiService()

TABLA = 'ejecuciones'
CLAVE = 'id'

@bp.route('/ejecuciones')
def index():
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')
    valor_clave = request.args.get('clave', '')

    registros = api.listar(TABLA, limite)
    
    # Obtener listados para los combos
    modelos = api.listar('modelos')
    casos = api.listar('casos_clinicos')

    mostrar_formulario = accion in ('nuevo', 'editar')
    editando = accion == 'editar'

    registro = None
    if editando and valor_clave:
        registro = next(
            (r for r in registros if str(r.get(CLAVE)) == valor_clave),
            None
        )

    return render_template('pages/ejecuciones.html',
        registros=registros,
        modelos=modelos,
        casos=casos,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite
    )

@bp.route('/ejecuciones/crear', methods=['POST'])
def crear():
    datos = {
        'modelo_id': request.form.get('modelo_id', 0, type=int),
        'caso_id': request.form.get('caso_id', 0, type=int),
        'prompt': request.form.get('prompt', ''),
        'respuesta': request.form.get('respuesta', ''),
        'tiempo_respuesta_ms': request.form.get('tiempo_respuesta_ms', 0, type=int),
        'temperatura': request.form.get('temperatura', 0, type=float),
        'tokens_entrada': request.form.get('tokens_entrada', 0, type=int),
        'tokens_salida': request.form.get('tokens_salida', 0, type=int)
    }

    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('ejecuciones.index'))

@bp.route('/ejecuciones/actualizar', methods=['POST'])
def actualizar():
    valor = request.form.get('id', 0, type=int)
    datos = {
        'modelo_id': request.form.get('modelo_id', 0, type=int),
        'caso_id': request.form.get('caso_id', 0, type=int),
        'prompt': request.form.get('prompt', ''),
        'respuesta': request.form.get('respuesta', ''),
        'tiempo_respuesta_ms': request.form.get('tiempo_respuesta_ms', 0, type=int),
        'temperatura': request.form.get('temperatura', 0, type=float),
        'tokens_entrada': request.form.get('tokens_entrada', 0, type=int),
        'tokens_salida': request.form.get('tokens_salida', 0, type=int)
    }

    exito, mensaje = api.actualizar(TABLA, CLAVE, valor, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('ejecuciones.index'))

@bp.route('/ejecuciones/eliminar', methods=['POST'])
def eliminar():
    valor = request.form.get('id', 0, type=int)

    exito, mensaje = api.eliminar(TABLA, CLAVE, valor)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('ejecuciones.index'))