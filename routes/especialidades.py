"""
especialidades.py - Blueprint CRUD para la tabla Especialidades.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services import create_service

bp = Blueprint('especialidades', __name__)
api = create_service()

TABLA = 'especialidades'
CLAVE = 'id'

@bp.route('/especialidades')
def index():
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')
    valor_clave = request.args.get('clave', '')

    registros = api.listar(TABLA, limite)
    mostrar_formulario = accion in ('nuevo', 'editar')
    editando = accion == 'editar'

    registro = None
    if editando and valor_clave:
        registro = next(
            (r for r in registros if str(r.get(CLAVE)) == valor_clave),
            None
        )

    return render_template('pages/especialidades.html',
        registros=registros,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite
    )

@bp.route('/especialidades/crear', methods=['POST'])
def crear():
    datos = {
        'nombre': request.form.get('nombre', ''),
        'descripcion': request.form.get('descripcion', '')
    }

    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('especialidades.index'))

@bp.route('/especialidades/actualizar', methods=['POST'])
def actualizar():
    valor = request.form.get('id', 0, type=int)
    datos = {
        'nombre': request.form.get('nombre', ''),
        'descripcion': request.form.get('descripcion', '')
    }

    exito, mensaje = api.actualizar(TABLA, CLAVE, valor, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('especialidades.index'))

@bp.route('/especialidades/eliminar', methods=['POST'])
def eliminar():
    valor = request.form.get('id', 0, type=int)

    exito, mensaje = api.eliminar(TABLA, CLAVE, valor)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('especialidades.index'))