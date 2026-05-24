import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.auth_service import AuthService

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    auth = AuthService()
    
    # Si ya está autenticado, redirigir al inicio
    if auth.esta_autenticado():
        return redirect(url_for('home.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        exito, mensaje = auth.login_usuario(email, password)
        
        if exito:
            return redirect(url_for('home.index'))
        else:
            flash(mensaje, 'danger')
            
    return render_template('pages/login.html')

@bp.route('/logout')
def logout():
    auth = AuthService()
    auth.logout_usuario()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('auth.login'))

@bp.route('/recuperar-contrasena', methods=['GET', 'POST'])
def recuperar_contrasena():
    if request.method == 'POST':
        email = request.form.get('email')
        auth = AuthService()
        exito, msj = auth.recuperar_contrasena(email)
        
        if exito:
            flash(msj, 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(msj, 'danger')
            
    return render_template('pages/recuperar_contrasena.html')

@bp.route('/cambiar-contrasena', methods=['GET', 'POST'])
def cambiar_contrasena():
    auth = AuthService()
    
    if request.method == 'POST':
        nueva = request.form.get('nueva_contrasena')
        confirmacion = request.form.get('confirmar_contrasena')
        
        if nueva != confirmacion:
            flash("Las contraseñas no coinciden.", "danger")
        elif len(nueva) < 6:
            flash("Mínimo 6 caracteres.", "danger")
        elif not re.search(r'[A-Z]', nueva):
            flash("Debe incluir al menos una mayúscula.", "danger")
        elif not re.search(r'\d', nueva):
            flash("Debe incluir al menos un número.", "danger")
        else:
            email = session.get('usuario')
            if not email:
                flash("Sesión inválida.", "danger")
                return redirect(url_for('auth.login'))
                
            exito, msj = auth.actualizar_contrasena(email, nueva)
            if exito:
                session.pop('debe_cambiar_contrasena', None)
                flash("Contraseña actualizada exitosamente. Ahora puedes navegar normalmente.", "success")
                return redirect(url_for('home.index'))
            else:
                flash(msj, "danger")
                
    return render_template('pages/cambiar_contrasena.html')
