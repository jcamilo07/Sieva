"""
casos_clinicos.py - Blueprint CRUD para la tabla Casos Clínicos.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from services import create_service
from config import API_BASE_URL

bp = Blueprint('casos_clinicos', __name__)
api = create_service()

TABLA     = 'casos_clinicos'
TABLA_ESP = 'caso_clinico_especialidad'
CLAVE     = 'id'


import sqlite3
import os

DB_PATH = 'data.db'

def init_local_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS local_casos_clinicos (id INTEGER PRIMARY KEY, calificacion_ia INTEGER, observacion TEXT)')
    conn.commit()
    conn.close()

init_local_db()

def _eliminar_relacion(caso_id, especialidad_id):
    import sys
    try:
        caso_id = int(caso_id)
        especialidad_id = int(especialidad_id)

        print(f"[DEBUG] Intentando eliminar relacion: caso_id={caso_id}, esp_id={especialidad_id}", file=sys.stderr, flush=True)

        # Intentar borrado físico primero
        exito, mensaje = api.eliminar_compuesta(TABLA_ESP, {
            'caso_id': caso_id,
            'especialidad_id': especialidad_id
        })

        print(f"[DEBUG] Resultado eliminación física: exito={exito}, mensaje={mensaje}", file=sys.stderr, flush=True)

        if exito:
            return True, mensaje

        # Fallback: borrado lógico — marcar como descartado=True
        print(f"[DEBUG] DELETE falló, intentando soft-delete (descartado=True)", file=sys.stderr, flush=True)
        exito2, mensaje2 = api.actualizar_compuesta(TABLA_ESP, {
            'caso_id': caso_id,
            'especialidad_id': especialidad_id
        }, {'descartado': True})

        print(f"[DEBUG] Resultado soft-delete: exito={exito2}, mensaje={mensaje2}", file=sys.stderr, flush=True)
        if not exito2:
            print(f"Error en soft-delete relacion: {mensaje2}", file=sys.stderr, flush=True)

        return exito2, mensaje2

    except Exception as ex:
        print(f"Excepción eliminando relacion: {ex}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return False, str(ex)


def _crear_relacion(caso_id, especialidad_id):
    try:
        caso_id_int = int(caso_id)
        especialidad_id_int = int(especialidad_id)
        
        relaciones = api.listar(TABLA_ESP, limite=10000)
        # Extraer existentes de forma segura
        existente = next(
            (r for r in relaciones
             if int(r.get('caso_id', 0)) == caso_id_int
             and int(r.get('especialidad_id', 0)) == especialidad_id_int),
            None
        )

        if existente:
            if existente.get('descartado', False):
                # Reactivar la relación descartada
                exito, mensaje = api.actualizar_compuesta(TABLA_ESP, {
                    'caso_id': caso_id_int,
                    'especialidad_id': especialidad_id_int
                }, {'descartado': False})
                if not exito:
                    print(f"Error reactivando relacion caso {caso_id} esp {especialidad_id}: {mensaje}")
                return exito
            # Ya existe y está activa
            return True

        # Fetch the specialty name to save it in the pivot table
        especialidades_lista = api.listar('especialidades')
        nombre_esp = ""
        if especialidades_lista:
            for e in especialidades_lista:
                if e.get('id') == especialidad_id:
                    nombre_esp = e.get('nombre', '')
            # (buscar nombre real si es necesario, o la API/UI lo asume)
            exito, mensaje = api.crear(TABLA_ESP, {
                'caso_id':         caso_id_int,
                'especialidad_id': especialidad_id_int,
                'descartado':      False,
                'especialidad_nombre': nombre_esp
            })
        if not exito:
            print(f"Error creando relacion caso {caso_id} esp {especialidad_id}: {mensaje}")
        return exito
    except Exception as ex:
        print(f"Error creando relacion caso {caso_id} esp {especialidad_id}: {ex}")
        return False
# ─────────────────────────────────────────────────────────────
# RUTAS AJAX PARA ESPECIALIDADES INLINE EN LA TABLA
# ─────────────────────────────────────────────────────────────

@bp.route('/casos_clinicos/especialidad/agregar', methods=['POST'])
def especialidad_agregar():
    datos  = request.get_json() or {}
    caso_id = datos.get('caso_id')
    esp_id  = datos.get('esp_id')

    if not caso_id or not esp_id:
        return jsonify({'ok': False, 'error': 'Faltan datos de caso u especialidad.'}), 400

    exito = _crear_relacion(caso_id, esp_id)
    if not exito:
        return jsonify({'ok': False, 'error': 'No se pudo guardar la especialidad seleccionada.'}), 500

    return jsonify({'ok': True})


@bp.route('/casos_clinicos/especialidad/quitar', methods=['POST'])
def especialidad_quitar():
    datos   = request.get_json() or {}
    caso_id = datos.get('caso_id')
    esp_id  = datos.get('esp_id')

    if not caso_id or not esp_id:
        return jsonify({'ok': False, 'error': 'Faltan datos de caso u especialidad.'}), 400

    exito, mensaje = _eliminar_relacion(caso_id, esp_id)
    if not exito:
        return jsonify({'ok': False, 'error': f'No se pudo quitar la especialidad seleccionada. {mensaje}'}), 500

    return jsonify({'ok': True})


# ─────────────────────────────────────────────────────────────
# CRUD PRINCIPAL
# ─────────────────────────────────────────────────────────────

@bp.route('/casos_clinicos')
def index():
    limite      = request.args.get('limite', type=int)
    accion      = request.args.get('accion', '')
    valor_clave = request.args.get('clave', '')
    
    # Paginación
    page        = request.args.get('page', 1, type=int)
    per_page    = request.args.get('per_page', 50, type=int)
    
    # Obtener todos los registros para calcular paginación
    todos_los_registros = api.listar(TABLA, limite)
    todos_los_registros = sorted(todos_los_registros, key=lambda x: x['id'])
    
    total_registros = len(todos_los_registros)
    total_paginas = (total_registros + per_page - 1) // per_page
    
    # Obtener registros de la página actual
    inicio = (page - 1) * per_page
    fin = inicio + per_page
    registros = todos_los_registros[inicio:fin]

    # MODELOS
    modelos      = api.listar('modelos')
    modelos_dict = {m['id']: m['nombre'] for m in modelos}
    for r in registros:
        r['modelo_nombre'] = modelos_dict.get(r.get('modelo_id'))

    # ESPECIALIDADES
    especialidades     = api.listar('especialidades')
    casos_especialidad = api.listar(TABLA_ESP, limite=10000)
    esp_dict           = {e['id']: e['nombre'] for e in especialidades}

    caso_esp_map = {}
    for ce in casos_especialidad:
        if ce.get('descartado', False):
            continue
        cid = ce['caso_id']
        eid = ce['especialidad_id']
        if cid not in caso_esp_map:
            caso_esp_map[cid] = []
        caso_esp_map[cid].append(esp_dict.get(eid))

    # CARGAR CALIFICACIONES (caché local SQLite para respuesta rápida)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM local_casos_clinicos')
    locales = {row['id']: row for row in c.fetchall()}
    conn.close()

    # Cargar calificaciones desde la base de datos PostgreSQL (tabla puntajes_casos)
    puntajes_bd = api.listar('puntajes_casos')
    puntajes_dict = {}
    if puntajes_bd and isinstance(puntajes_bd, list):
        for p in puntajes_bd:
            cid = p.get('caso_id')
            if cid:
                puntajes_dict[cid] = p.get('puntaje')

    for r in registros:
        r['especialidades'] = caso_esp_map.get(r.get('id'), [])
        rid = r.get('id')

        # ── observacion: viene directamente de la BD PostgreSQL ────────────
        # Si hay valor en caché local más reciente, usarlo; si no, el de la API
        if rid in locales and locales[rid]['observacion']:
            r['observacion'] = locales[rid]['observacion']
        else:
            # Usar el valor que ya viene del campo observacion en casos_clinicos
            r['observacion'] = r.get('observacion') or ''

        # ── calificacion_ia: viene del caché local o de la BD PostgreSQL ───
        if rid in locales and locales[rid]['calificacion_ia'] is not None:
            r['calificacion_ia'] = locales[rid]['calificacion_ia']
        else:
            r['calificacion_ia'] = puntajes_dict.get(rid)

    mostrar_formulario = accion in ('nuevo', 'editar')
    editando           = accion == 'editar'

    registro = None
    if editando and valor_clave:
        registro = next(
            (r for r in registros if str(r.get(CLAVE)) == valor_clave),
            None
        )

    return render_template('pages/casos_clinicos.html',
        registros=registros,
        mostrar_formulario=mostrar_formulario,
        editando=editando,
        registro=registro,
        limite=limite,
        modelos=modelos,
        especialidades=especialidades,
        page=page,
        per_page=per_page,
        total_registros=total_registros,
        total_paginas=total_paginas
    )


@bp.route('/casos_clinicos/crear', methods=['POST'])
def crear():
    datos = {
        'id_caso':            request.form.get('id_caso', type=int),
        'modelo_id':          request.form.get('modelo_id', type=int),
        'historia':           request.form.get('historia', ''),
        'diagnostico_ia':     request.form.get('diagnostico_ia', ''),
        'diagnostico_humano': request.form.get('diagnostico_humano', ''),
        'nivel_dificultad':   request.form.get('nivel_dificultad', 'bajo'),
        'fecha_creacion':     request.form.get('fecha_creacion')
    }

    exito, mensaje = api.crear(TABLA, datos)

    if exito:
        especialidades_ids = request.form.getlist('especialidades')
        if especialidades_ids:
            casos    = api.listar(TABLA)
            if casos:
                ultimo_id = max(c['id'] for c in casos)
                for esp_id in especialidades_ids:
                    _crear_relacion(ultimo_id, int(esp_id))

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('casos_clinicos.index'))


@bp.route('/casos_clinicos/actualizar', methods=['POST'])
def actualizar():
    valor = request.form.get('id', 0, type=int)

    datos = {
        'id_caso':            request.form.get('id_caso', type=int),
        'modelo_id':          request.form.get('modelo_id', type=int),
        'historia':           request.form.get('historia', ''),
        'diagnostico_ia':     request.form.get('diagnostico_ia', ''),
        'diagnostico_humano': request.form.get('diagnostico_humano', ''),
        'nivel_dificultad':   request.form.get('nivel_dificultad', 'bajo'),
        'fecha_creacion':     request.form.get('fecha_creacion')
    }

    exito, mensaje = api.actualizar(TABLA, CLAVE, valor, datos)

    if exito:
        # Descartar relaciones anteriores activas
        relaciones = api.listar(TABLA_ESP)
        for r in relaciones:
            if r['caso_id'] == valor and not r.get('descartado', False):
                _eliminar_relacion(valor, r['especialidad_id'])

        # Insertar / reactivar nuevas
        especialidades_ids = request.form.getlist('especialidades')
        for esp_id in especialidades_ids:
            _crear_relacion(valor, int(esp_id))

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('casos_clinicos.index'))


@bp.route('/casos_clinicos/eliminar', methods=['POST'])
def eliminar():
    valor = request.form.get('id', 0, type=int)

    # Eliminar relaciones primero
    relaciones = api.listar(TABLA_ESP)
    for r in relaciones:
        if r['caso_id'] == valor:
            _eliminar_relacion(valor, r['especialidad_id'])

    exito, mensaje = api.eliminar(TABLA, CLAVE, valor)

    flash(mensaje, 'success' if exito else 'danger')
    return redirect(url_for('casos_clinicos.index'))


# ─────────────────────────────────────────────────────────────
# EXPORTAR CSV TOTAL
# ─────────────────────────────────────────────────────────────
@bp.route('/casos_clinicos/exportar_csv')
def exportar_csv():
    import csv
    from io import StringIO
    from flask import Response

    # 1. Obtener todos los registros y modelos/especialidades
    todos = api.listar(TABLA)
    modelos = {m['id']: f"{m['nombre']} (v{m['version']})" for m in api.listar('modelos')}
    especialidades = {e['id']: e['nombre'] for e in api.listar('especialidades')}
    
    # Mapa de especialidades reales
    rel_raw = api.listar(TABLA_ESP)
    caso_esp_map = {}
    for r in rel_raw:
        if not r.get('descartado'):
            cid = r['caso_id']
            ename = especialidades.get(r['especialidad_id'], 'N/A')
            caso_esp_map.setdefault(cid, []).append(ename)

    # Calificaciones y observaciones desde PostgreSQL (fuente de verdad)
    puntajes_lista = api.listar('puntajes_casos')
    puntajes_map = {}  # caso_id -> {puntaje, observacion}
    for p in puntajes_lista:
        cid = p.get('caso_id')
        if cid:
            puntajes_map[cid] = {
                'puntaje':    p.get('puntaje', ''),
                'observacion': p.get('observacion', '') or ''
            }

    # 2. Construir el CSV en memoria
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'ID Caso', 'Modelo', 'Especialidades', 'Dificultad', 'Estrellas', 'Observacion', 'Historia', 'Dx IA', 'Dx Humano'])

    for r in sorted(todos, key=lambda x: x['id']):
        rid = r['id']
        m_name = modelos.get(r.get('modelo_id'), '-')
        esps = ", ".join(caso_esp_map.get(rid, []))
        
        # Data de PostgreSQL
        pg_data = puntajes_map.get(rid, {})
        stars = pg_data.get('puntaje', '')
        obs = pg_data.get('observacion', '')

        cw.writerow([
            rid,
            f"{r.get('id_caso')}",
            m_name,
            esps,
            str(r.get('nivel_dificultad', '')).upper(),
            stars,
            obs,
            r.get('historia', ''),
            r.get('diagnostico_ia', ''),
            r.get('diagnostico_humano', '')
        ])

    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=todos_los_casos.csv"}
    )


# ─────────────────────────────────────────────────────────────
# RUTA AJAX PARA GUARDAR CALIFICACIÓN Y JUSTIFICACIÓN
# ─────────────────────────────────────────────────────────────

@bp.route('/casos_clinicos/calificacion/guardar', methods=['POST'])
def guardar_calificacion():
    """
    Guarda la calificación y la observación directamente en PostgreSQL.
    - puntaje     → tabla puntajes_casos, columna puntaje      (POST o PUT)
    - observacion → tabla puntajes_casos, columna observacion  (POST o PUT)
    El SQLite solo se usa como caché de visualización rápida.
    """
    datos = request.get_json()
    caso_id      = datos.get('caso_id')
    calificacion = datos.get('calificacion')
    observacion  = datos.get('observacion', '')

    if not caso_id:
        return jsonify({'ok': False, 'error': 'Falta el ID del caso'}), 400

    errores = []

    # ── Resolver medico_experto_id ─────────────────────────────────────────
    from flask import session
    email_usuario = session.get('usuario')
    medico_id = None
    if email_usuario:
        medicos_buscar = api.listar(f'medico_experto/email/{email_usuario}')
        if medicos_buscar and isinstance(medicos_buscar, list) and len(medicos_buscar) > 0:
            medico_id = medicos_buscar[0].get('id')
    if not medico_id:
        todos_medicos = api.listar('medico_experto')
        if todos_medicos and isinstance(todos_medicos, list) and len(todos_medicos) > 0:
            medico_id = todos_medicos[0].get('id', 1)
    if not medico_id:
        medico_id = 1

    # ── Resolver modelo_id del caso ───────────────────────────────────────
    modelo_id = 1
    caso_list = api.listar(f'casos_clinicos/id/{caso_id}')
    if caso_list and isinstance(caso_list, list) and len(caso_list) > 0:
        modelo_id = caso_list[0].get('modelo_id', 1)

    criterio_id = 1

    # ── Buscar si ya existe un puntaje para este caso ─────────────────────
    existentes = api.listar(f'puntajes_casos/caso_id/{caso_id}')
    reg_id = None
    if existentes and isinstance(existentes, list) and len(existentes) > 0:
        reg = existentes[0] if isinstance(existentes[0], dict) else {}
        reg_id = reg.get('id')

    # ── Guardar o actualizar en puntajes_casos (puntaje + observacion) ────
    if calificacion is None or calificacion == 0:
        # Deselección: eliminar el registro si existe
        if reg_id:
            exito_punt, msg_punt = api.eliminar('puntajes_casos', 'id', reg_id)
            if not exito_punt:
                errores.append(f'Puntaje BD (Eliminar): {msg_punt}')
    else:
        if reg_id:
            # Actualizar puntaje Y observacion en el registro existente
            exito_punt, msg_punt = api.actualizar(
                'puntajes_casos', 'id', reg_id,
                {
                    'puntaje':     int(calificacion),
                    'observacion': observacion or '',
                    'modelo_id':   int(modelo_id),
                    'caso_id':     int(caso_id),
                    'criterio_id': int(criterio_id),
                    'medico_experto_id': int(medico_id)
                }
            )
            if not exito_punt:
                errores.append(f'Puntaje BD (Actualizar): {msg_punt}')
        else:
            # Crear nuevo registro con puntaje Y observacion
            nuevo_puntaje = {
                'modelo_id':         int(modelo_id),
                'caso_id':           int(caso_id),
                'criterio_id':       int(criterio_id),
                'medico_experto_id': int(medico_id),
                'puntaje':           int(calificacion),
                'observacion':       observacion or ''
            }
            exito_punt, msg_punt = api.crear('puntajes_casos', nuevo_puntaje)
            if not exito_punt:
                errores.append(f'Puntaje BD (Crear): {msg_punt}')

    # ── Actualizar caché SQLite local (solo para visualización rápida) ────
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id FROM local_casos_clinicos WHERE id = ?', (caso_id,))
        existe = c.fetchone()
        val_calif = int(calificacion) if calificacion and calificacion != 0 else None
        if existe:
            c.execute(
                'UPDATE local_casos_clinicos SET calificacion_ia = ?, observacion = ? WHERE id = ?',
                (val_calif, observacion or '', caso_id)
            )
        else:
            c.execute(
                'INSERT INTO local_casos_clinicos (id, calificacion_ia, observacion) VALUES (?, ?, ?)',
                (caso_id, val_calif, observacion or '')
            )
        conn.commit()
        conn.close()
    except Exception as ex_local:
        print(f'[WARN] Cache SQLite: {ex_local}')  # No bloquear por error de caché

    if errores:
        return jsonify({'ok': False, 'errores': errores}), 500

    return jsonify({'ok': True, 'mensaje': 'Guardado correctamente en PostgreSQL'})