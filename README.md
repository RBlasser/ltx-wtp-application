# Latinex Data Hub: Aplicación WTP (Sensibilidad Tarifaria)

Microservicio standalone (**FastAPI + PostgreSQL 16**) para capturar de forma confidencial encuestas institucionales de disposición a pagar (**Van Westendorp + Newton-Miller-Smith**) y administrar el catálogo de servicios complementarios desde una consola protegida por contraseña.

---

## Arquitectura y Estructura del Repositorio

```text
ltx-wtp-application/
├── backend/
│   ├── auth.py              # Cookie HttpOnly firmada (HMAC-SHA256) y verificación constant-time
│   ├── config.py            # Carga estricta (fail-fast) de variables de entorno
│   ├── db.py                # Pool PostgreSQL (psycopg3) y consultas transaccionales
│   ├── main.py              # API FastAPI, cabeceras de seguridad, rate limiting de login y archivos estáticos
│   └── requirements.txt
├── frontend/
│   ├── index.html           # Encuesta pública (5 pasos), sin controles ni código administrativo
│   └── admin.html           # Consola protegida: analítica Van Westendorp/NMS + catálogo de servicios
├── src/assets/              # Logos institucionales oficiales de Latinex
├── database/
│   └── schema.sql           # DDL PostgreSQL con restricción estricta chk_strict_van_westendorp_inequality
├── docs/
│   ├── DEPLOY_AWS.md        # Guía de despliegue en Amazon ECS / App Runner + RDS
│   ├── spec_arquitectura_wtp_app.md
│   └── mockups_flujo_wizard.md
├── Dockerfile               # Imagen python:3.12-slim con usuario no-root y HEALTHCHECK
├── docker-compose.yml       # Orquestación de wtp-app + wtp-db (postgres:16-alpine, volumen persistente)
├── .dockerignore
├── .env.example
└── .gitignore
```

---

## Rutas Principales

| Ruta | Acceso | Propósito |
|---|---|---|
| `GET /` | Público | Encuesta institucional de 5 pasos |
| `GET /api/v1/services` | Público | Catálogo de servicios complementarios activos |
| `POST /api/v1/responses` | Público | Persiste sesión y respuesta validada en PostgreSQL |
| `GET /api/v1/health` | Público | Healthcheck de aplicación y base de datos |
| `GET /admin` | Público (Login) | Consola administrativa con autenticación por contraseña |
| `POST /api/v1/admin/login` | Público (Rate-limited) | Emite cookie de sesión `HttpOnly` |
| `GET /api/v1/admin/responses` | Protegido (`401`) | Consulta respuestas para analítica |
| `GET /api/v1/admin/export.csv` | Protegido (`401`) | Exportación CSV de respuestas |
| `GET/POST/PUT/DELETE /api/v1/admin/services` | Protegido (`401`) | CRUD persistente del catálogo de servicios |

---

## Arranque Rápido Local (Docker)

1. Copiar `.env.example` a `.env` y configurar las credenciales locales:
   ```bash
   cp .env.example .env
   ```
2. Construir y levantar los contenedores:
   ```bash
   docker compose up -d --build
   ```
3. Acceder a:
   - Encuesta pública: `http://localhost:8080/`
   - Consola administrativa: `http://localhost:8080/admin`
   - Healthcheck: `http://localhost:8080/api/v1/health`

Para instrucciones detalladas de despliegue productivo en AWS (ECS Fargate / App Runner, RDS PostgreSQL, Secrets Manager y HTTPS), consultar [`docs/DEPLOY_AWS.md`](./docs/DEPLOY_AWS.md).
