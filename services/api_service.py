"""
api_service.py - Servicio generico que consume la API REST.

Contiene los 4 metodos CRUD (Listar, Crear, Actualizar, Eliminar)
que se reutilizan en todos los Blueprints/rutas.
Cada metodo retorna los datos o una tupla (exito, mensaje).
"""

# requests: libreria de Python para hacer peticiones HTTP (GET, POST, PUT, DELETE)
import requests

# API_BASE_URL: URL base de la API, importada desde config.py (ej: "http://localhost:5034")
from config import API_BASE_URL


# Clase que encapsula las 4 operaciones CRUD contra la API REST.
# Se instancia en cada Blueprint con: api = ApiService()
class ApiService:
    """
    Servicio generico para consumir la API REST.

    Metodos:
        listar(tabla, limite)           → lista de diccionarios
        crear(tabla, datos, ...)        → (bool, str)
        actualizar(tabla, clave, ...)   → (bool, str)
        eliminar(tabla, clave, valor)   → (bool, str)
    """

    # Constructor: se ejecuta al crear una instancia con ApiService()
    def __init__(self):
        # Guarda la URL base como atributo de la instancia para usarla en todos los metodos
        self.base_url = API_BASE_URL

    def _get_headers(self):
        """Construye los headers HTTP incluyendo el JWT de la sesion de Flask."""
        headers = {}
        token = None
        
        try:
            from flask import session
            token = session.get("jwt_token")
        except Exception:
            pass # Fuera del contexto de request
            
        if not token:
            # Fallback para rutas públicas (ej: dashboard sin login)
            try:
                import jwt
                from datetime import datetime, timedelta, timezone
                import os
                # Misma clave usada por la API C#
                secret = "MySuperSecretKey1234567890!@#$%^&*()_+"
                payload = {
                    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name": "public_viewer@sieva.com",
                    "tabla": "usuarios",
                    "campoUsuario": "email",
                    "exp": int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()),
                    "iss": "MyApp",
                    "aud": "MyAppUsers"
                }
                token = jwt.encode(payload, secret, algorithm="HS256")
            except Exception as e:
                print(f"Error generando token público de fallback: {e}")

        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    # ──────────────────────────────────────────────
    # LISTAR: GET /api/{tabla}
    # Obtiene todos los registros de una tabla.
    # Opcionalmente limita la cantidad con ?limite=N
    # ──────────────────────────────────────────────
    def listar(self, tabla, limite=None):
        """
        Consulta la API y retorna la lista de registros.

        Args:
            tabla:  nombre de la tabla (ej: 'empresa')
            limite: cantidad maxima de registros (opcional)

        Returns:
            Lista de diccionarios con los datos, o lista vacia si hay error.
        """
        try:
            # Construir la URL del endpoint: ej → "http://localhost:5034/api/empresa"
            url = f"{self.base_url}/api/{tabla}"

            # Diccionario para los query params de la URL (ej: ?limite=5)
            params = {}
            # Solo agregar el parametro limite si el usuario lo proporciono
            if limite:
                params['limite'] = limite

            # requests.get(, headers=self._get_headers()) hace una peticion HTTP GET a la URL indicada
            # params se agrega automaticamente como query string (ej: ?limite=5)
            respuesta = requests.get(url, params=params, headers=self._get_headers())

            # .json() convierte el cuerpo de la respuesta de texto JSON a diccionario Python
            datos_json = respuesta.json()

            # La API retorna: { "datos": [...], "mensaje": "..." }
            # .get("datos", []) extrae la lista; si no existe la clave, retorna lista vacia
            return datos_json.get("datos", [])

        # RequestException: captura cualquier error de conexion (timeout, DNS, servidor caido)
        except requests.RequestException as ex:
            # Imprimir el error en la consola del servidor para depuracion
            print(f"Error al listar {tabla}: {ex}")
            # Retornar lista vacia para que el template muestre "No se encontraron registros"
            return []

    # ──────────────────────────────────────────────
    # CREAR: POST /api/{tabla}
    # Envia los datos del formulario como JSON.
    # Retorna una tupla (exito, mensaje).
    # ──────────────────────────────────────────────
    def crear(self, tabla, datos, campos_encriptar=None):
        """
        Crea un nuevo registro en la tabla.

        Args:
            tabla:             nombre de la tabla
            datos:             diccionario con los campos del registro
            campos_encriptar:  nombre del campo a encriptar (opcional, ej: 'contrasena')

        Returns:
            Tupla (exito: bool, mensaje: str)
        """
        try:
            # Construir la URL del endpoint: ej → "http://localhost:5034/api/usuario"
            url = f"{self.base_url}/api/{tabla}"

            # Diccionario para los query params opcionales
            params = {}
            # Si hay un campo a encriptar, agregarlo como parametro en la URL
            # La API recibe ?camposEncriptar=contrasena y encripta ese campo con bcrypt
            if campos_encriptar:
                params['camposEncriptar'] = campos_encriptar

            # requests.post(, headers=self._get_headers()) hace una peticion HTTP POST.
            # json=datos: convierte el diccionario Python a JSON y lo envia en el cuerpo.
            # params: agrega los query params a la URL si existen.
            respuesta = requests.post(url, json=datos, params=params, headers=self._get_headers())

            # Convertir la respuesta JSON a diccionario Python
            contenido = respuesta.json()

            # Extraer el mensaje de la respuesta (ej: "Registro creado exitosamente.")
            # Si no viene el campo "mensaje", usar un texto por defecto
            mensaje = contenido.get("mensaje", "Operacion completada.")

            # respuesta.ok es True si el codigo HTTP esta entre 200-299 (exito)
            # Retorna una tupla: (True/False, "texto del mensaje")
            return (respuesta.ok, mensaje)

        # Capturar errores de conexion (API apagada, timeout, error de red)
        except requests.RequestException as ex:
            # Retornar False y el texto del error para mostrarlo como alerta roja
            return (False, f"Error de conexion: {ex}")

    # ──────────────────────────────────────────────
    # ACTUALIZAR: PUT /api/{tabla}/{nombre_clave}/{valor_clave}
    # Envia los campos a modificar como JSON.
    # La clave primaria va en la URL, no en el cuerpo.
    # ──────────────────────────────────────────────
    def actualizar(self, tabla, nombre_clave, valor_clave, datos, campos_encriptar=None):
        """
        Actualiza un registro existente.

        Args:
            tabla:             nombre de la tabla
            nombre_clave:      nombre del campo clave (ej: 'codigo', 'id', 'email')
            valor_clave:       valor de la clave del registro a actualizar (ej: 'PR001')
            datos:             diccionario con los campos a modificar
            campos_encriptar:  nombre del campo a encriptar (opcional)

        Returns:
            Tupla (exito: bool, mensaje: str)
        """
        try:
            # Construir la URL con la clave primaria en la ruta
            # Ejemplo: "http://localhost:5034/api/producto/codigo/PR001"
            url = f"{self.base_url}/api/{tabla}/{nombre_clave}/{valor_clave}"

            # Diccionario para query params opcionales (encriptacion)
            params = {}
            # Agregar parametro de encriptacion si fue solicitado
            if campos_encriptar:
                params['camposEncriptar'] = campos_encriptar

            # requests.put(, headers=self._get_headers()) hace una peticion HTTP PUT para modificar un recurso existente.
            # json=datos: envia solo los campos que cambiaron (sin la clave primaria).
            respuesta = requests.put(url, json=datos, params=params, headers=self._get_headers())

            # Intentar convertir la respuesta JSON a diccionario Python
            try:
                contenido = respuesta.json()
                mensaje = contenido.get("mensaje", "Operacion completada.")
            except ValueError:
                # Si falla la decodificacion JSON (ej: string vacio o texto plano)
                if respuesta.status_code == 401:
                    mensaje = "No autorizado. Su sesión puede haber expirado."
                else:
                    mensaje = f"Operacion completada con estado {respuesta.status_code}" if respuesta.ok else f"Error HTTP {respuesta.status_code}"

            # Retornar tupla (exito, mensaje) para que el Blueprint muestre la alerta
            return (respuesta.ok, mensaje)

        # Capturar errores de conexion
        except requests.RequestException as ex:
            return (False, f"Error de conexion: {ex}")

    # ──────────────────────────────────────────────
    # ELIMINAR: DELETE /api/{tabla}/{nombre_clave}/{valor_clave}
    # Solo necesita la clave primaria para identificar el registro.
    # ──────────────────────────────────────────────
    def eliminar(self, tabla, nombre_clave, valor_clave):
        """
        Elimina un registro de la tabla.

        Args:
            tabla:        nombre de la tabla
            nombre_clave: nombre del campo clave (ej: 'codigo')
            valor_clave:  valor de la clave del registro a eliminar (ej: 'PR001')

        Returns:
            Tupla (exito: bool, mensaje: str)
        """
        try:
            # Construir la URL con la clave primaria
            # Ejemplo: "http://localhost:5034/api/empresa/codigo/E001"
            url = f"{self.base_url}/api/{tabla}/{nombre_clave}/{valor_clave}"

            # requests.delete(, headers=self._get_headers()) hace una peticion HTTP DELETE para borrar el recurso.
            respuesta = requests.delete(url, headers=self._get_headers())

            # Convertir la respuesta JSON a diccionario Python
            contenido = respuesta.json()

            # Extraer el mensaje de la API (ej: "Registro eliminado exitosamente.")
            mensaje = contenido.get("mensaje", "Operacion completada.")

            # Retornar tupla (exito, mensaje)
            return (respuesta.ok, mensaje)

        # Capturar errores de conexion
        except requests.RequestException as ex:
            return (False, f"Error de conexion: {ex}")
        except Exception as ex:
            return (False, f"Error al procesar la respuesta: {ex}")

    # ──────────────────────────────────────────────
    # ACTUALIZAR COMPUESTA: PUT /api/{tabla}/{clave1}/{valor1}?clave2=valor2&...
    # Para tablas con claves compuestas (múltiples campos clave)
    # ──────────────────────────────────────────────
    def actualizar_compuesta(self, tabla, filtros, datos):
        """
        Actualiza un registro con clave compuesta usando path + query parameters.

        Args:
            tabla:    nombre de la tabla
            filtros:  diccionario con {nombre_clave1: valor1, nombre_clave2: valor2, ...}
                     Ejemplo: {"caso_id": 5, "especialidad_id": 3}
            datos:    diccionario con los campos a actualizar
                     Ejemplo: {"descartado": True}

        Returns:
            Tupla (exito: bool, mensaje: str)
        """
        try:
            if not filtros:
                return (False, "No se proporcionaron filtros para actualizar.")

            keys = list(filtros.keys())
            values = list(filtros.values())

            # Usar primer clave en la ruta, resto en query params
            url = f"{self.base_url}/api/{tabla}/{keys[0]}/{values[0]}"
            params = {k: v for k, v in zip(keys[1:], values[1:])}

            respuesta = requests.put(url, json=datos, params=params, headers=self._get_headers())

            contenido = None
            try:
                contenido = respuesta.json()
                mensaje = contenido.get("mensaje", "Operacion completada.")
            except Exception:
                mensaje = None

            if mensaje is None:
                if respuesta.ok:
                    mensaje = "✅ Registro actualizado exitosamente."
                else:
                    mensaje = f"❌ Error en la solicitud (código {respuesta.status_code})"

            return (respuesta.ok, mensaje)
        except Exception as ex:
            return (False, f"Error de conexión: {str(ex)}")

    # ──────────────────────────────────────────────
    # ELIMINAR COMPUESTA: DELETE /api/{tabla}?clave1=valor1&clave2=valor2
    # Para tablas con claves compuestas (múltiples campos clave)
    # ──────────────────────────────────────────────
    def eliminar_compuesta(self, tabla, parametros):
        """
        Elimina un registro con clave compuesta usando query parameters.

        Args:
            tabla:       nombre de la tabla
            parametros:  diccionario con {nombre_clave1: valor1, nombre_clave2: valor2}
                        Ejemplo: {"usuario_id": 5, "rol_id": 3}

        Returns:
            Tupla (exito: bool, mensaje: str)
        """
        try:
            # Construir URL base: /api/usuario_rol
            url = f"{self.base_url}/api/{tabla}"
            
            # Usar query parameters para la clave compuesta
            # Esto genera: /api/usuario_rol?usuario_id=5&rol_id=3
            respuesta = requests.delete(url, params=parametros, headers=self._get_headers())
            
            # Definir mensaje por defecto basado en status code
            mensaje = None

            # Intentar parsear JSON de la respuesta
            try:
                contenido = respuesta.json()
                mensaje = contenido.get("mensaje", "Operacion completada.")
            except (ValueError, Exception) as json_error:
                # Si no es JSON válido, usar el status code para determinar el error
                pass

            # Si no se obtuvo mensaje del JSON, usar status code para determinar el error
            if mensaje is None:
                if respuesta.status_code == 409:
                    mensaje = "⚠️ No se puede eliminar este registro. Tiene asociaciones o dependencias con otros registros. Por favor, elimine primero los registros relacionados."
                elif respuesta.status_code == 404:
                    mensaje = "❌ El registro no fue encontrado."
                elif respuesta.status_code == 400:
                    mensaje = "❌ Datos inválidos. Verifique que el registro exista."
                elif respuesta.ok:
                    mensaje = "✅ Registro eliminado exitosamente."
                else:
                    mensaje = f"❌ Error en la solicitud (código {respuesta.status_code})"
            
            if respuesta.ok:
                return (True, mensaje)

            # Fallback attempts for composite primary keys and pivot tables
            if len(parametros) == 2:
                keys = list(parametros.keys())
                values = list(parametros.values())

                # Try route using both key names in canonical order
                url_path = f"{self.base_url}/api/{tabla}/{keys[0]}/{values[0]}/{keys[1]}/{values[1]}"
                respuesta_path = requests.delete(url_path, headers=self._get_headers())
                mensaje_path = None
                try:
                    contenido_path = respuesta_path.json()
                    mensaje_path = contenido_path.get("mensaje", "Operacion completada.")
                except Exception:
                    pass
                if mensaje_path is None:
                    mensaje_path = "Operacion completada." if respuesta_path.ok else f"Error en la solicitud (código {respuesta_path.status_code})"
                if respuesta_path.ok:
                    return (True, mensaje_path)

                # Try route using both key names in reverse order
                url_path_rev = f"{self.base_url}/api/{tabla}/{keys[1]}/{values[1]}/{keys[0]}/{values[0]}"
                respuesta_path_rev = requests.delete(url_path_rev, headers=self._get_headers())
                mensaje_path_rev = None
                try:
                    contenido_path_rev = respuesta_path_rev.json()
                    mensaje_path_rev = contenido_path_rev.get("mensaje", "Operacion completada.")
                except Exception:
                    pass
                if mensaje_path_rev is None:
                    mensaje_path_rev = "Operacion completada." if respuesta_path_rev.ok else f"Error en la solicitud (código {respuesta_path_rev.status_code})"
                if respuesta_path_rev.ok:
                    return (True, mensaje_path_rev)

                # Try numeric-only path if the API expects direct id values
                url_numeric = f"{self.base_url}/api/{tabla}/{values[0]}/{values[1]}"
                respuesta_numeric = requests.delete(url_numeric, headers=self._get_headers())
                mensaje_numeric = None
                try:
                    contenido_numeric = respuesta_numeric.json()
                    mensaje_numeric = contenido_numeric.get("mensaje", "Operacion completada.")
                except Exception:
                    pass
                if mensaje_numeric is None:
                    mensaje_numeric = "Operacion completada." if respuesta_numeric.ok else f"Error en la solicitud (código {respuesta_numeric.status_code})"
                if respuesta_numeric.ok:
                    return (True, mensaje_numeric)

                # Try numeric-only path with reversed order
                url_numeric_rev = f"{self.base_url}/api/{tabla}/{values[1]}/{values[0]}"
                respuesta_numeric_rev = requests.delete(url_numeric_rev, headers=self._get_headers())
                mensaje_numeric_rev = None
                try:
                    contenido_numeric_rev = respuesta_numeric_rev.json()
                    mensaje_numeric_rev = contenido_numeric_rev.get("mensaje", "Operacion completada.")
                except Exception:
                    pass
                if mensaje_numeric_rev is None:
                    mensaje_numeric_rev = "Operacion completada." if respuesta_numeric_rev.ok else f"Error en la solicitud (código {respuesta_numeric_rev.status_code})"
                if respuesta_numeric_rev.ok:
                    return (True, mensaje_numeric_rev)

                # Last fallback: return the most informative message from the last attempt
                return (False, mensaje_numeric_rev or mensaje_numeric or mensaje_path_rev or mensaje_path or mensaje)

            return (respuesta.ok, mensaje)
        except Exception as ex:
            return (False, f"Error de conexión: {str(ex)}")

    # ──────────────────────────────────────────────
    # EJECUTAR SP: POST /api/procedimientos/ejecutarsp
    # Llama a un procedimiento almacenado a traves de la API.
    # ──────────────────────────────────────────────
    def ejecutar_sp(self, nombre_sp, parametros=None):
        """
        Ejecuta un stored procedure via la API.

        Args:
            nombre_sp:   nombre del procedimiento
            parametros:  diccionario con los parametros del SP (sin nombreSP)

        Returns:
            Tupla (exito: bool, datos_o_mensaje)
        """
        try:
            import json as json_mod
            url = f"{self.base_url}/api/procedimientos/ejecutarsp"

            payload = {"nombreSP": nombre_sp}
            if parametros:
                payload.update(parametros)

            respuesta = requests.post(url, json=payload, headers=self._get_headers())
            contenido = respuesta.json()

            if not respuesta.ok:
                mensaje = contenido.get("mensaje", "Error al ejecutar el procedimiento.")
                return (False, mensaje)

            resultados = contenido.get("resultados", [])
            if resultados and "p_resultado" in resultados[0]:
                p_resultado = resultados[0]["p_resultado"]
                if isinstance(p_resultado, str):
                    return (True, json_mod.loads(p_resultado))
                return (True, p_resultado)

            return (True, contenido)

        except requests.RequestException as ex:
            return (False, f"Error de conexion: {ex}")
        except Exception as ex:
            return (False, f"Error procesando respuesta: {ex}")