"""
usuarios.py - Blueprint CRUD para la tabla Usuarios.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
import requests
from services import create_service

bp = Blueprint('usuarios', __name__)
api = create_service()

TABLA = 'usuarios'
CLAVE = 'id'

@bp.route('/usuarios')
def index():
    limite = request.args.get('limite', type=int)
    accion = request.args.get('accion', '')
    valor_clave = request.args.get('clave', '')

    registros = api.listar(TABLA, limite)
    roles_todos = api.listar('roles')
    usuario_roles = api.listar('usuario_rol')

    # Mapeo para nombres de roles
    map_roles = {r['id']: r['nombre'] for r in roles_todos}
    
    # Mapeo de roles por usuario
    roles_por_usuario = {}
    for ur in usuario_roles:
        u_id = ur['usuario_id']
        r_id = ur['rol_id']
        if u_id not in roles_por_usuario:
            roles_por_usuario[u_id] = []
        roles_por_usuario[u_id].append({
            'id': r_id,
            'nombre': map_roles.get(r_id, f"Rol {r_id}")
        })

    mostrar_formulario = accion in ('nuevo', 'editar')
    editando = accion == 'editar'

    registro = None
    if editando and valor_clave:
        registro = next(
            (r for r in registros if str(r.get(CLAVE)) == valor_clave),
            None
        )

    return render_template('pages/usuarios.html',
        registros=registros,
        roles_todos=roles_todos,
        roles_por_usuario=roles_por_usuario,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite
    )

@bp.route('/usuarios/crear', methods=['POST'])
def crear():
    # Verificar si el checkbox de encriptar está marcado
    encriptar = request.form.get('encriptar')
    campos_encriptar = 'password_hash' if encriptar else None

    datos = {
        'nombre': request.form.get('nombre', ''),
        'email': request.form.get('email', ''),
        'password_hash': request.form.get('password_hash', ''),
        'activo': request.form.get('activo') == 'on'
    }

    exito, mensaje = api.crear(TABLA, datos, campos_encriptar)
    
    if exito:
        # Buscar el ID del usuario recien creado para asignarle los roles
        usuarios = api.listar(TABLA)
        nuevo_user = next((u for u in usuarios if u['email'] == datos['email']), None)
        if nuevo_user:
            u_id = nuevo_user['id']
            roles_marcados = request.form.getlist('roles[]')
            for rid in roles_marcados:
                api.crear('usuario_rol', {'usuario_id': u_id, 'rol_id': int(rid)})

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('usuarios.index'))

@bp.route('/usuarios/actualizar', methods=['POST'])
def actualizar():
    valor = request.form.get('id', 0, type=int)
    
    # Verificar si el checkbox de encriptar está marcado
    encriptar = request.form.get('encriptar')
    campos_encriptar = 'password_hash' if encriptar else None
    
    datos = {
        'nombre': request.form.get('nombre', ''),
        'email': request.form.get('email', ''),
        'password_hash': request.form.get('password_hash', ''),
        'activo': request.form.get('activo') == 'on'
    }
    
    # Si la contraseña se dejó en blanco en edición, no actualizarla
    if not datos['password_hash']:
        del datos['password_hash']
        campos_encriptar = None

    exito, mensaje = api.actualizar(TABLA, CLAVE, valor, datos, campos_encriptar)
    
    if exito:
        roles_marcados = [int(rid) for rid in request.form.getlist('roles[]')]
        
        # Obtener roles actuales
        usuario_roles_actuales = api.listar('usuario_rol')
        roles_actuales = [ur['rol_id'] for ur in usuario_roles_actuales if ur['usuario_id'] == valor]
        
        roles_a_borrar = set(roles_actuales) - set(roles_marcados)
        roles_a_agregar = set(roles_marcados) - set(roles_actuales)
        
        # Borrar desmarcados usando request directo a la API con clave compuesta
        for r_id in roles_a_borrar:
            url = f"{api.base_url}/api/usuario_rol/usuario_id/{valor}/rol_id/{r_id}"
            try:
                requests.delete(url, headers=api._get_headers())
            except Exception as e:
                print(f"Error borrando rol {r_id}: {e}")
                
        # Agregar los nuevos
        for r_id in roles_a_agregar:
            api.crear('usuario_rol', {'usuario_id': valor, 'rol_id': r_id})

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('usuarios.index'))

@bp.route('/usuarios/eliminar', methods=['POST'])
def eliminar():
    valor = request.form.get('id', 0, type=int)

    exito, mensaje = api.eliminar(TABLA, CLAVE, valor)
    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('usuarios.index'))