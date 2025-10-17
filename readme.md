# Backend Marketplace + BIO-ID

Backend completo para marketplace con sistema de autenticación biométrica.

## 🚀 Tecnologías

- **FastAPI** - Framework web
- **PostgreSQL** - Base de datos
- **SQLAlchemy** - ORM
- **Docker** - Contenedores
- **JWT** - Autenticación

## 📦 Estructura del Proyecto
```
├── app/
│   ├── models/          # Modelos SQLAlchemy
│   ├── schemas/         # Validaciones Pydantic
│   ├── routers/         # Endpoints API
│   ├── dependencies.py  # Funciones compartidas
│   └── main.py         # Aplicación principal
├── docs/
│   └── bio-id/         # Documentación biométrica
├── init.sql            # Script inicial BD
├── biometric_test_data.sql  # Datos de prueba
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## 🏃 Cómo ejecutar
```bash
# Levantar servicios
docker-compose up -d

# Ver logs
docker logs tienda-github-web-1

# Acceder a la API
http://localhost:8001/docs
```

## 📊 Base de Datos

- **Puerto:** 5432
- **Base de datos:** becarios_db
- **Usuario:** postgres
- **13 tablas:** users, products, orders, notifications, etc.

## 🔐 Endpoints principales

- **Users:** 13 endpoints (CRUD, login, profile)
- **Products:** 8 endpoints (CRUD, búsqueda)
- **Orders:** 11 endpoints (CRUD, stats)
- **Notifications:** 11 endpoints (CRUD, unread)

## 📚 Documentación BIO-ID

- [Investigación de librerías](docs/bio-id/investigacion_librerias.md)
- [Análisis tabla biometric_data](docs/bio-id/analisis_tabla_biometric.md)

## 👤 Autor

Adrián Carretero - Legal Intermedia