"""
home.py - Blueprint para la pagina de inicio.
"""

from flask import Blueprint, render_template

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    """Renderiza la pagina de inicio."""
    return render_template('pages/home.html')