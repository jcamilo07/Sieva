from flask import request, redirect, url_for, session, render_template

def setup_auth_middleware(app):
    """
    Configura el middleware global de autenticación y autorización para la aplicación,
    así como el procesador de contexto para las plantillas.
    """
    @app.before_request
    def requerir_autenticacion():
        # Rutas que no requieren autenticación
        rutas_publicas = ['auth.login', 'auth.recuperar_contrasena', 'static']
        endpoint = request.endpoint
        blueprint = request.blueprint
        
        if not endpoint or endpoint in rutas_publicas:
            return

        # Verificar Autenticación (¿Quién eres?)
        if 'jwt_token' not in session:
            return redirect(url_for('auth.login'))

        # Verificación de cambio de contraseña obligatorio
        # Si el usuario debe cambiar su contraseña, solo puede acceder a 'cambiar_contrasena' o 'logout'
        if session.get('debe_cambiar_contrasena') and endpoint not in ['auth.cambiar_contrasena', 'auth.logout']:
            return redirect(url_for('auth.cambiar_contrasena'))

        # Verificar Autorización por Roles (¿Qué puedes hacer?)
        roles_usuario = session.get('roles', [])
        
        # Rutas generales permitidas para cualquier usuario autenticado
        rutas_generales = ['auth.logout', 'auth.cambiar_contrasena', 'home.index']
        if endpoint in rutas_generales:
            return
            
        # Administrador tiene acceso total
        if 'Administrador' in roles_usuario:
            return
            
        # Lógica para Médico u otros roles (basado en Blueprints)
        if 'Medico' in roles_usuario or 'Medico experto' in roles_usuario:
            blueprints_medico = ['home', 'dashboard', 'casos_clinicos', 'modelos', 'especialidades']
            if blueprint in blueprints_medico:
                return
                
        # Si no tiene permisos, mostrar error 403
        return render_template('pages/403.html'), 403

    # Inyectar datos del usuario a todos los templates
    @app.context_processor
    def inyectar_usuario():
        return {
            'usuario_actual': session.get('usuario'),
            'roles_actuales': session.get('roles', [])
        }
