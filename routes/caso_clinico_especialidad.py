"""
caso_clinico_especialidad.py - Blueprint CRUD para la tabla pivote caso_clinico_especialidad.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.api_service import ApiService

bp = Blueprint('caso_clinico_especialidad', __name__)
api = ApiService()

TABLA = 'caso_clinico_especialidad'

@bp.route('/caso_clinico_especialidad')
def index():
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')
    caso_id = request.args.get('caso_id', '')
    especialidad_id = request.args.get('especialidad_id', '')

    registros = api.listar(TABLA, limite)
    
    # Filtrar relaciones marcadas como descartadas (solo mostrar activas)
    registros = [r for r in registros if not r.get('descartado', False)]
    
    # Obtener listados para los combos
    casos = api.listar('casos_clinicos')
    especialidades = api.listar('especialidades')

    mostrar_formulario = accion in ('nuevo', 'editar')
    editando = accion == 'editar'

    registro = None
    if editando and caso_id and especialidad_id:
        registro = next(
            (r for r in registros if str(r.get('caso_id')) == caso_id 
             and str(r.get('especialidad_id')) == especialidad_id),
            None
        )

    return render_template('pages/caso_clinico_especialidad.html',
        registros=registros,
        casos=casos,
        especialidades=especialidades,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite
    )

@bp.route('/caso_clinico_especialidad/crear', methods=['POST'])
def crear():
    datos = {
        'caso_id': request.form.get('caso_id', 0, type=int),
        'especialidad_id': request.form.get('especialidad_id', 0, type=int)
    }

    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('caso_clinico_especialidad.index'))

@bp.route('/caso_clinico_especialidad/eliminar', methods=['POST'])
def eliminar():
    caso_id = request.form.get('caso_id', 0, type=int)
    especialidad_id = request.form.get('especialidad_id', 0, type=int)

    # Construir URL para eliminar con clave compuesta
    url = f"{api.base_url}/api/{TABLA}/caso_id/{caso_id}/especialidad_id/{especialidad_id}"
    
    try:
        exito, mensaje = api.eliminar_compuesta(TABLA, {
            'caso_id': caso_id,
            'especialidad_id': especialidad_id
        })
        flash(mensaje, 'success' if exito else 'danger')
    except Exception as ex:
        flash(f" Error de conexión: {str(ex)}", 'danger')
    
    return redirect(url_for('caso_clinico_especialidad.index'))
