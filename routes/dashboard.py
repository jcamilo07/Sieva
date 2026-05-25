"""
dashboard.py - Blueprint para el dashboard de Veracidad (Criterio #1).
Datos reales en tiempo real obtenidos de la API REST (PostgreSQL) y base local SQLite.
"""

from flask import Blueprint, render_template
import json
import sqlite3
from services import create_service

bp = Blueprint('dashboard', __name__)
api = create_service()

DB_PATH = 'data.db'

def norm_diff(d):
    """Normaliza el nivel de dificultad a primera letra mayúscula."""
    if not d:
        return 'Bajo'
    d_str = str(d).strip().capitalize()
    return d_str if d_str in ['Bajo', 'Medio', 'Alto'] else 'Bajo'

@bp.route('/dashboard')
def index():
    """Dashboard de Veracidad / Criterio #1 en tiempo real."""

    # 1. Obtener datos estructurales reales de la API REST (PostgreSQL)
    modelos = api.listar('modelos') or []
    casos = api.listar('casos_clinicos') or []
    especialidades = api.listar('especialidades') or []
    caso_clinico_especialidad = api.listar('caso_clinico_especialidad', limite=10000) or []

    # 2. Cargar calificaciones locales del evaluador médico (SQLite)
    locales = {}
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT id, calificacion_ia, observacion FROM local_casos_clinicos')
        locales = {row['id']: dict(row) for row in c.fetchall()}
        conn.close()
    except Exception as ex:
        print(f"[ERROR] No se pudo leer local_casos_clinicos de SQLite: {ex}")

    # 3. Determinar casos evaluados reales
    total_casos = len(casos)
    total_modelos = len(modelos)
    total_especialidades = len(especialidades)

    casos_calificados_dict = {}
    for case in casos:
        cid = case.get('id')
        local_data = locales.get(cid)
        if local_data:
            cal = local_data.get('calificacion_ia')
            if cal is not None and cal > 0:
                casos_calificados_dict[cid] = cal

    total_graded = len(casos_calificados_dict)
    total_pending = total_casos - total_graded
    progreso_evaluacion = round((total_graded / total_casos * 100), 1) if total_casos > 0 else 0.0

    # 4. Procesar rendimiento y veracidad por cada modelo
    tabla_modelos = []
    for m in modelos:
        mid = m['id']
        m_name = m['nombre']
        
        # Casos de este modelo
        cases_m = [c for c in casos if c.get('modelo_id') == mid]
        graded_m = [c for c in cases_m if c.get('id') in casos_calificados_dict]
        
        # Veracidad Promedio (1-5 estrellas)
        veracidad_m = sum(casos_calificados_dict[c['id']] for c in graded_m) / len(graded_m) if len(graded_m) > 0 else 0.0
        
        stars_full = int(veracidad_m)
        stars_half = 1 if (veracidad_m - stars_full) >= 0.25 else 0
        stars_empty = 5 - stars_full - stars_half

        # Veracidad por dificultad
        veracidad_by_diff = {}
        for d_level in ['Bajo', 'Medio', 'Alto']:
            cases_m_d = [c for c in cases_m if norm_diff(c.get('nivel_dificultad')) == d_level]
            graded_m_d = [c for c in cases_m_d if c.get('id') in casos_calificados_dict]
            veracidad_by_diff[d_level] = round(sum(casos_calificados_dict[c['id']] for c in graded_m_d) / len(graded_m_d), 2) if len(graded_m_d) > 0 else 0.0

        # Mejor dificultad
        mejor_diff_m = max(['Bajo', 'Medio', 'Alto'], key=lambda d: veracidad_by_diff[d])
        if veracidad_by_diff[mejor_diff_m] == 0.0:
            mejor_diff_m = 'Bajo'

        tabla_modelos.append({
            'id':           mid,
            'corto':        m_name,
            'largo':        f"{m_name} ({m['version']})" if m.get('version') else m_name,
            'mejor_en':     mejor_diff_m,
            'bajo':         veracidad_by_diff['Bajo'],
            'medio':        veracidad_by_diff['Medio'],
            'alto':         veracidad_by_diff['Alto'],
            'veracidad':    round(veracidad_m, 2),
            'stars_full':   stars_full,
            'stars_half':   stars_half,
            'stars_empty':  stars_empty,
            'graded_count': len(graded_m),
        })

    # Ordenar por veracidad media descendente, y finalmente ID
    tabla_modelos.sort(key=lambda x: (-x['veracidad'], x['id']))
    for i, item in enumerate(tabla_modelos):
        item['rank'] = i + 1

    # 5. KPIs Globales
    total_correct = sum(1 for cid, stars in casos_calificados_dict.items() if stars >= 4)
    total_incorrect = sum(1 for cid, stars in casos_calificados_dict.items() if stars <= 2)
    total_partial = sum(1 for cid, stars in casos_calificados_dict.items() if stars == 3)
    
    veracidad_prom_global = round(sum(stars for cid, stars in casos_calificados_dict.items()) / total_graded, 2) if total_graded > 0 else 0.0

    # 5b. Distribucion por dificultad
    dist_dificultad = {'Bajo': 0, 'Medio': 0, 'Alto': 0}
    for case in casos:
        d = norm_diff(case.get('nivel_dificultad'))
        dist_dificultad[d] += 1
    total_dist = sum(dist_dificultad.values()) or 1
    dist_dificultad_pct = {k: round(v/total_dist*100,1) for k,v in dist_dificultad.items()}

    # 5c. Errores por modelo (score <= 2)
    errores_labels = [item['corto'] for item in tabla_modelos]
    errores_values = []
    aciertos_values = []
    parciales_values = []
    for item in tabla_modelos:
        mid = item['id']
        cases_m = [c for c in casos if c.get('modelo_id') == mid]
        graded_m = [c for c in cases_m if c.get('id') in casos_calificados_dict]
        errores_values.append(sum(1 for c in graded_m if casos_calificados_dict[c['id']] <= 2))
        parciales_values.append(sum(1 for c in graded_m if casos_calificados_dict[c['id']] == 3))
        aciertos_values.append(sum(1 for c in graded_m if casos_calificados_dict[c['id']] >= 4))

    # 5d. Veracidad promedio por dificultad (todos los modelos combinados)
    ver_avg_diff = {}
    for d in ['Bajo','Medio','Alto']:
        cases_d = [c for c in casos if norm_diff(c.get('nivel_dificultad')) == d and c.get('id') in casos_calificados_dict]
        ver_avg_diff[d] = round(sum(casos_calificados_dict[c['id']] for c in cases_d)/len(cases_d), 2) if cases_d else 0.0

    # 6. Datos para Gráficos
    nombres = [item['corto'] for item in tabla_modelos]
    bar_ver_labels = nombres
    bar_ver_values = [item['veracidad'] for item in tabla_modelos]

    # Heatmap data (Veracidad por dificultad)
    heatmap_rows = []
    niveles = [('Bajo', 'bajo'), ('Medio', 'medio'), ('Alto', 'alto')]
    for nivel_label, nivel_key in niveles:
        row = {'nivel': nivel_label, 'celdas': []}
        for item in tabla_modelos:
            val = item[nivel_key]
            # Mapeamos un puntaje de 1-5 a intensidad de 0-100 para la visualización del color
            intensity = min(int(val * 20), 100)
            row['celdas'].append({'modelo': item['corto'], 'valor': val, 'intensity': intensity})
        heatmap_rows.append(row)

    # 7. Distribución Real de Especialidades
    esp_dict = {e['id']: e['nombre'] for e in especialidades}
    from collections import Counter
    esp_counts = Counter()
    for ce in caso_clinico_especialidad:
        if ce.get('descartado', False):
            continue
        eid = ce.get('especialidad_id')
        esp_name = esp_dict.get(eid)
        if esp_name:
            esp_counts[esp_name] += 1

    especialidades_data = esp_counts.most_common()
    max_esp_count = max(e[1] for e in especialidades_data) if especialidades_data else 1

    # 8. KPIs Dinámicos de Pie de Página (Footer)
    # Mejor Veracidad
    graded_models = [item for item in tabla_modelos if item['graded_count'] > 0]
    if graded_models:
        mejor_ver_item = max(graded_models, key=lambda x: x['veracidad'])
        mejor_ver_modelo = mejor_ver_item['corto']
        mejor_ver_val = mejor_ver_item['veracidad']
    else:
        mejor_ver_modelo = "Pendiente"
        mejor_ver_val = 0.0

    # Mejor Consistencia (Modelo con mayor Veracidad en Casos de dificultad Alto)
    if graded_models:
        mejor_prec_alto_item = max(graded_models, key=lambda x: x['alto'])
        mejor_prec_alto_modelo = mejor_prec_alto_item['corto']
        mejor_prec_alto_val = mejor_prec_alto_item['alto']
    else:
        mejor_prec_alto_modelo = "Pendiente"
        mejor_prec_alto_val = 0.0

    # Mayor Reto Global (Nivel con menor veracidad promedio real)
    if total_graded > 0:
        promedios = {}
        for d in ['Bajo', 'Medio', 'Alto']:
            cases_d = [c for c in casos if norm_diff(c.get('nivel_dificultad')) == d and c.get('id') in casos_calificados_dict]
            promedios[d] = round(sum(casos_calificados_dict[c['id']] for c in cases_d)/len(cases_d), 2) if cases_d else 0.0
        
        active_diffs = [d for d in ['Bajo', 'Medio', 'Alto'] if promedios[d] > 0]
        if active_diffs:
            mayor_reto_key = min(active_diffs, key=lambda d: promedios[d])
            mayor_reto_label = f"Casos {mayor_reto_key}"
            mayor_reto_val = promedios[mayor_reto_key]
        else:
            mayor_reto_label = "Pendiente"
            mayor_reto_val = 0.0
    else:
        mayor_reto_label = "Pendiente"
        mayor_reto_val = 0.0

    # Especialidad más evaluada
    esp_mas_frecuente = especialidades_data[0][0] if especialidades_data else "Ninguna"
    esp_mas_freq_count = especialidades_data[0][1] if especialidades_data else 0

    return render_template(
        'pages/dashboard.html',
        total_casos=total_casos,
        total_modelos=total_modelos,
        total_especialidades=total_especialidades,
        total_graded=total_graded,
        total_pending=total_pending,
        progreso_evaluacion=progreso_evaluacion,
        veracidad_prom_global=veracidad_prom_global,
        total_correct=total_correct,
        total_incorrect=total_incorrect,
        total_partial=total_partial,
        tabla_modelos=tabla_modelos,
        bar_ver_labels=json.dumps(bar_ver_labels),
        bar_ver_values=json.dumps(bar_ver_values),
        heatmap_rows=heatmap_rows,
        especialidades=especialidades_data,
        max_esp_count=max_esp_count,
        dist_dificultad=dist_dificultad,
        dist_dificultad_pct=dist_dificultad_pct,
        errores_labels=json.dumps(errores_labels),
        errores_values=json.dumps(errores_values),
        aciertos_values=json.dumps(aciertos_values),
        parciales_values=json.dumps(parciales_values),
        ver_avg_diff=ver_avg_diff,
        mejor_ver_modelo=mejor_ver_modelo,
        mejor_ver_val=mejor_ver_val,
        mejor_prec_alto_modelo=mejor_prec_alto_modelo,
        mejor_prec_alto_val=mejor_prec_alto_val,
        mayor_reto_label=mayor_reto_label,
        mayor_reto_val=mayor_reto_val,
        esp_mas_frecuente=esp_mas_frecuente,
        esp_mas_freq_count=esp_mas_freq_count,
    )
