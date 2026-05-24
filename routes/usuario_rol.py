"""
usuario_rol.py - Blueprint CRUD para la tabla pivote usuario_rol.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
import requests
from services.api_service import ApiService

bp = Blueprint('usuario_rol', __name__)
api = ApiService()

TABLA = 'usuario_rol'

@bp.route('/usuario_rol')
def index():
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')
    usuario_id = request.args.get('usuario_id', '')
    rol_id = request.args.get('rol_id', '')

    registros = api.listar(TABLA, limite)
    
    # Obtener listados para los combos
    usuarios = api.listar('usuarios')
    roles = api.listar('roles')

    mostrar_formulario = accion in ('nuevo', 'editar')
    editando = accion == 'editar'

    registro = None
    if editando and usuario_id and rol_id:
        registro = next(
            (r for r in registros if str(r.get('usuario_id')) == usuario_id 
             and str(r.get('rol_id')) == rol_id),
            None
        )

    return render_template('pages/usuario_rol.html',
        registros=registros,
        usuarios=usuarios,
        roles=roles,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite
    )

@bp.route('/usuario_rol/crear', methods=['POST'])
def crear():
    datos = {
        'usuario_id': request.form.get('usuario_id', 0, type=int),
        'rol_id': request.form.get('rol_id', 0, type=int)
    }

    exito, mensaje = api.crear(TABLA, datos)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('usuario_rol.index'))

@bp.route('/usuario_rol/eliminar', methods=['POST'])
def eliminar():
    usuario_id = request.form.get('usuario_id', 0, type=int)
    rol_id = request.form.get('rol_id', 0, type=int)

    # Construir URL para eliminar con clave compuesta
    url = f"{api.base_url}/api/{TABLA}/usuario_id/{usuario_id}/rol_id/{rol_id}"
    
    try:
        respuesta = requests.delete(url)
        
        # Intentar parsear JSON de la respuesta
        try:
            contenido = respuesta.json()
            mensaje = contenido.get("mensaje", "Operacion completada.")
        except (ValueError, Exception):
            # Si la API no devuelve JSON válido, usar mensaje por status code
            if respuesta.status_code == 200:
                mensaje = " Registro eliminado exitosamente."
            elif respuesta.status_code == 409:
                mensaje = "⚠️ No se puede eliminar este registro. Tiene asociaciones o dependencias con otros registros. Por favor, elimine primero los registros relacionados."
            elif respuesta.status_code == 404:
                # 404 probablemente significa que no se pudo eliminar por dependencias
                mensaje = "⚠️ No se puede eliminar este registro. Tiene asociaciones o dependencias con otros registros. Por favor, elimine primero los registros relacionados."
            else:
                mensaje = f" Error en la solicitud (código {respuesta.status_code})"
        
        # Mostrar mensaje con color apropiado según el resultado
        flash(mensaje, 'success' if respuesta.ok else 'danger')
    except Exception as ex:
        flash(f" Error de conexión: {str(ex)}", 'danger')
    
    return redirect(url_for('usuario_rol.index'))