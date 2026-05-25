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

import difflib

def text_similarity(text1, text2):
    if not text1 or not text2:
        return 0.0
    return difflib.SequenceMatcher(None, str(text1).lower(), str(text2).lower()).ratio() * 100.0

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
    caso_clinico_especialidad = api.listar('caso_clinico_especialidad') or []

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

        # Precisión Global (Similitud de textos) — independiente de la calificación del doctor
        # Se calcula para TODOS los casos del modelo que tengan ambos diagnósticos llenos
        cases_m_con_diag = [c for c in cases_m if c.get('diagnostico_ia') and c.get('diagnostico_humano')]
        sim_scores = [text_similarity(c.get('diagnostico_ia'), c.get('diagnostico_humano')) for c in cases_m_con_diag]
        precision_global_m = (sum(sim_scores) / len(sim_scores)) if sim_scores else 0.0

        # Precisión por dificultad — también independiente de calificación
        precision_by_diff = {}
        for d_level in ['Bajo', 'Medio', 'Alto']:
            cases_m_d = [c for c in cases_m_con_diag if norm_diff(c.get('nivel_dificultad')) == d_level]
            sim_scores_d = [text_similarity(c.get('diagnostico_ia'), c.get('diagnostico_humano')) for c in cases_m_d]
            precision_by_diff[d_level] = round((sum(sim_scores_d) / len(sim_scores_d)), 1) if sim_scores_d else 0.0

        # Mejor dificultad
        mejor_diff_m = max(['Bajo', 'Medio', 'Alto'], key=lambda d: precision_by_diff[d])
        if precision_by_diff[mejor_diff_m] == 0.0:
            mejor_diff_m = 'Bajo'

        tabla_modelos.append({
            'id':           mid,
            'corto':        m_name,
            'largo':        f"{m_name} ({m['version']})" if m.get('version') else m_name,
            'mejor_en':     mejor_diff_m,
            'bajo':         precision_by_diff['Bajo'],
            'medio':        precision_by_diff['Medio'],
            'alto':         precision_by_diff['Alto'],
            'global':       round(precision_global_m, 1),
            'veracidad':    round(veracidad_m, 2),
            'stars_full':   stars_full,
            'stars_half':   stars_half,
            'stars_empty':  stars_empty,
            'graded_count': len(graded_m),
            'diag_count':   len(cases_m_con_diag),  # casos con ambos diagnósticos (para precisión)
        })

    # Ordenar por precisión global descendente, luego veracidad, y finalmente ID
    tabla_modelos.sort(key=lambda x: (-x['global'], -x['veracidad'], x['id']))
    for i, item in enumerate(tabla_modelos):
        item['rank'] = i + 1

    # 5. KPIs Globales
    total_correct = sum(1 for cid, stars in casos_calificados_dict.items() if stars >= 4)
    total_incorrect = sum(1 for cid, stars in casos_calificados_dict.items() if stars <= 2)
    total_partial = sum(1 for cid, stars in casos_calificados_dict.items() if stars == 3)
    
    # Precisión global: todos los casos con ambos diagnósticos, sin depender de calificación
    total_sim_scores = [
        text_similarity(c.get('diagnostico_ia'), c.get('diagnostico_humano'))
        for c in casos if c.get('diagnostico_ia') and c.get('diagnostico_humano')
    ]
    precision_global = round((sum(total_sim_scores) / len(total_sim_scores)), 1) if total_sim_scores else 0.0
    
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

    # 5d. Precision promedio por dificultad (todos los modelos combinados)
    # Precisión promedio por dificultad — todos los casos con ambos diagnósticos
    prec_avg_diff = {}
    for d in ['Bajo','Medio','Alto']:
        cases_d = [
            c for c in casos
            if norm_diff(c.get('nivel_dificultad')) == d
            and c.get('diagnostico_ia') and c.get('diagnostico_humano')
        ]
        sim_scores_d = [text_similarity(c.get('diagnostico_ia'), c.get('diagnostico_humano')) for c in cases_d]
        prec_avg_diff[d] = round(sum(sim_scores_d)/len(sim_scores_d), 1) if sim_scores_d else 0.0

    # 6. Datos para Gráficos
    nombres = [item['corto'] for item in tabla_modelos]
    bar_precision_labels = nombres
    bar_precision_bajo = [item['bajo'] for item in tabla_modelos]
    bar_precision_medio = [item['medio'] for item in tabla_modelos]
    bar_precision_alto = [item['alto'] for item in tabla_modelos]

    # Ordenar veracidad de mayor a menor para la barra horizontal
    ver_sorted = sorted(tabla_modelos, key=lambda x: -x['veracidad'])
    bar_ver_labels = [item['corto'] for item in ver_sorted]
    bar_ver_values = [item['veracidad'] for item in ver_sorted]

    # Datos Scatter (correlación)
    COLORES_SCATTER = [
        '#c0ca33', '#ff7043', '#ab47bc', '#5c6bc0',
        '#f4a261', '#26a69a', '#ef5350', '#42a5f5',
        '#8d6e63', '#66bb6a',
    ]
    scatter_data = []
    for i, item in enumerate(tabla_modelos):
        scatter_data.append({
            'label':           item['corto'],
            'x':               item['global'],
            'y':               item['veracidad'],
            'backgroundColor': COLORES_SCATTER[i % len(COLORES_SCATTER)],
            'pointRadius':     14,
            'pointHoverRadius': 18,
        })

    # Heatmap data
    heatmap_rows = []
    niveles = [('Bajo', 'bajo'), ('Medio', 'medio'), ('Alto', 'alto')]
    for nivel_label, nivel_key in niveles:
        row = {'nivel': nivel_label, 'celdas': []}
        for item in tabla_modelos:
            val = item[nivel_key]
            intensity = min(int(val), 100)
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
        mejor_ver_precision = mejor_ver_item['global']
    else:
        mejor_ver_modelo = "Pendiente"
        mejor_ver_val = 0.0
        mejor_ver_precision = 0.0

    # Mejor Precisión en Casos Alto
    if graded_models:
        mejor_prec_alto_item = max(graded_models, key=lambda x: x['alto'])
        mejor_prec_alto_modelo = mejor_prec_alto_item['corto']
        mejor_prec_alto_val = mejor_prec_alto_item['alto']
    else:
        mejor_prec_alto_modelo = "Pendiente"
        mejor_prec_alto_val = 0.0

    # Mayor Reto Global (Nivel con menor precisión promedio real)
    if total_graded > 0:
        graded_by_diff = {'Bajo': 0, 'Medio': 0, 'Alto': 0}
        correct_by_diff = {'Bajo': 0, 'Medio': 0, 'Alto': 0}
        for case in casos:
            cid = case.get('id')
            if cid in casos_calificados_dict:
                d = norm_diff(case.get('nivel_dificultad'))
                graded_by_diff[d] += 1
                if casos_calificados_dict[cid] >= 4:
                    correct_by_diff[d] += 1
        
        promedios = {}
        for d in ['Bajo', 'Medio', 'Alto']:
            promedios[d] = (correct_by_diff[d] / graded_by_diff[d] * 100.0) if graded_by_diff[d] > 0 else 0.0
        
        active_diffs = [d for d in ['Bajo', 'Medio', 'Alto'] if graded_by_diff[d] > 0]
        if active_diffs:
            mayor_reto_key = min(active_diffs, key=lambda d: promedios[d])
            mayor_reto_label = f"Casos {mayor_reto_key}"
            mayor_reto_val = round(promedios[mayor_reto_key], 1)
        else:
            mayor_reto_label = "Pendiente"
            mayor_reto_val = 0.0
    else:
        mayor_reto_label = "Pendiente"
        mayor_reto_val = 0.0

    # Especialidad más evaluada
    esp_mas_frecuente = especialidades_data[0][0] if especialidades_data else "Ninguna"
    esp_mas_freq_count = especialidades_data[0][1] if especialidades_data else 0

    # Casos con AMBOS diagnósticos llenos (para gráfico de precisión textual)
    total_con_diagnostico = sum(
        1 for item in tabla_modelos if item.get('diag_count', 0) > 0
    )

    return render_template(
        'pages/dashboard.html',
        total_casos=total_casos,
        total_modelos=total_modelos,
        total_especialidades=total_especialidades,
        total_graded=total_graded,
        total_pending=total_pending,
        total_con_diagnostico=total_con_diagnostico,
        progreso_evaluacion=progreso_evaluacion,
        precision_global=precision_global,
        veracidad_prom_global=veracidad_prom_global,
        total_correct=total_correct,
        total_incorrect=total_incorrect,
        total_partial=total_partial,
        tabla_modelos=tabla_modelos,
        bar_precision_labels=json.dumps(bar_precision_labels),
        bar_precision_bajo=json.dumps(bar_precision_bajo),
        bar_precision_medio=json.dumps(bar_precision_medio),
        bar_precision_alto=json.dumps(bar_precision_alto),
        bar_ver_labels=json.dumps(bar_ver_labels),
        bar_ver_values=json.dumps(bar_ver_values),
        scatter_data=json.dumps(scatter_data),
        heatmap_rows=heatmap_rows,
        especialidades=especialidades_data,
        max_esp_count=max_esp_count,
        dist_dificultad=dist_dificultad,
        dist_dificultad_pct=dist_dificultad_pct,
        errores_labels=json.dumps(errores_labels),
        errores_values=json.dumps(errores_values),
        aciertos_values=json.dumps(aciertos_values),
        parciales_values=json.dumps(parciales_values),
        prec_avg_diff=prec_avg_diff,
        mejor_ver_modelo=mejor_ver_modelo,
        mejor_ver_val=mejor_ver_val,
        mejor_ver_precision=mejor_ver_precision,
        mejor_prec_alto_modelo=mejor_prec_alto_modelo,
        mejor_prec_alto_val=mejor_prec_alto_val,
        mayor_reto_label=mayor_reto_label,
        mayor_reto_val=mayor_reto_val,
        esp_mas_frecuente=esp_mas_frecuente,
        esp_mas_freq_count=esp_mas_freq_count,
    )
