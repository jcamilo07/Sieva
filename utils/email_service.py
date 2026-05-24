"""
email_service.py - Servicio para envio de correos electronicos via SMTP.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM

def enviar_correo_recuperacion(email_destino, contrasena_temporal):
    """
    Envia un correo electronico con la contraseña temporal usando la configuracion SMTP.
    """
    if not SMTP_PASS or SMTP_PASS == "kgym mfnp ahqm jfok" and not SMTP_USER:
        # Si no hay credenciales reales configuradas, fallar gracefully para entorno dev
        return False, "Las credenciales SMTP no están configuradas correctamente."

    msg = MIMEMultipart()
    msg['From'] = SMTP_FROM
    msg['To'] = email_destino
    msg['Subject'] = "Recuperación de Contraseña - SIEVA"
    
    body = f"""Hola,

Se ha solicitado una recuperación de contraseña para tu cuenta.

Tu contraseña temporal es: {contrasena_temporal}

Por razones de seguridad, deberás cambiar esta contraseña inmediatamente después de iniciar sesión.

Saludos,
El equipo de SIEVA.
"""
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        return True, "Correo enviado correctamente."
    except Exception as e:
        return False, str(e)
