FrontFlask_AppiGenericaCsharp/

La aplicación frontal **depende exclusivamente de la API REST genérica**
que usted tenga corriendo (en su caso, un servicio PostgreSQL).  

El valor de `config.API_BASE_URL` debe apuntar a esa API (por ejemplo
`http://localhost:5034`).  Si la API no responde, las operaciones CRUD
fallarán con un error de conexión y el desarrollador deberá revisarlo del
lado del backend.

El método `services.create_service()` simplemente devuelve un `ApiService`
que envía peticiones HTTP a la URL indicada; no hay ninguna base local ni
mecanismo de conmutación.

**Formato esperado de la API**  
Las llamadas de listado (`GET /api/<tabla>`) pueden devolver uno de estos dos
formatos:

- Un arreglo JSON de objetos, p.ej. `[{...},{...}]`
- Un objeto envolvente con propiedad `datos`, p.e. `{"datos":[{...}]}`

La versión más reciente del servicio detecta automáticamente ambos casos para
maximizar compatibilidad con APIs genéricas distintas.

**Registro de actividad**  
En la consola verá líneas como:

```
[ApiService] listar tabla=modelos limite=None base=http://localhost:5034
```

que indican que se está llamando al backend remoto. Esto sirve para
comprobar que las peticiones salen y qué respuestas devuelven.

Si alguna llamada falla, la aplicación mostrará un mensaje flash explicando el
error. No hay ningún fallback automático.

Para levantar el servidor front-end:

```bash
pip install -r requirements.txt
python app.py
```

Abrir http://localhost:5100 en el navegador.

La estructura general del proyecto es:

FrontFlask_AppiGenericaCsharp/
│
├── app.py
├── config.py              # configuraciones (API_BASE_URL, SECRET_KEY)
├── requirements.txt
│
├── services/
│   ├── __init__.py
│   └── api_service.py      # servicio que consume la API REST genérica
│
├── routes/
│   ├── __init__.py
│   ├── home.py
│   ├── modelos.py
│   ├── especialidades.py
│   ├── casos_clinicos.py
│   ├── criterios.py
│   ├── roles.py
│   └── usuarios.py
│
├── templates/
│   ├── layout/
│   │   └── base.html
│   ├── components/
│   │   └── nav_menu.html
│   └── pages/
│       ├── home.html
│       ├── modelos.html
│       ├── especialidades.html
│       ├── casos_clinicos.html
│       ├── criterios.html
│       ├── roles.html
│       └── usuarios.html
│
└── static/
    └── css/
        └── app.css  