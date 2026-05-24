"""
modelos.py - Blueprint CRUD para la tabla Modelos.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from services import create_service

bp = Blueprint('modelos', __name__)
api = create_service()

TABLA = 'modelos'
CLAVE = 'id'  # La clave primaria es id (autoincremental)

@bp.route('/modelos')
def index():
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')
    valor_clave = request.args.get('clave', '')

    registros = api.listar(TABLA, limite)

    mostrar_formulario = accion in ('nuevo', 'editar')
    editando = accion == 'editar'

    registro = None
    if editando and valor_clave:
        # Buscar por id (entero)
        registro = next(
            (r for r in registros if str(r.get(CLAVE)) == valor_clave),
            None
        )

    return render_template('pages/modelos.html',
        registros=registros,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite
    )

@bp.route('/modelos/crear', methods=['POST'])
def crear():
    datos = {
        'nombre': request.form.get('nombre', ''),
        'proveedor': request.form.get('proveedor', ''),
        'version': request.form.get('version', ''),
        'activo': request.form.get('activo') == 'on'  # Checkbox
    }

    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('modelos.index'))

@bp.route('/modelos/actualizar', methods=['POST'])
def actualizar():
    valor = request.form.get('id', 0, type=int)
    datos = {
        'nombre': request.form.get('nombre', ''),
        'proveedor': request.form.get('proveedor', ''),
        'version': request.form.get('version', ''),
        'activo': request.form.get('activo') == 'on'
    }

    exito, mensaje = api.actualizar(TABLA, CLAVE, valor, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('modelos.index'))

@bp.route('/modelos/eliminar', methods=['POST'])
def eliminar():
    valor = request.form.get('id', 0, type=int)

    exito, mensaje = api.eliminar(TABLA, CLAVE, valor)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('modelos.index'))