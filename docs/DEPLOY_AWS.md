# Guía de Despliegue: Latinex Data Hub (Aplicación WTP)

Microservicio standalone (**FastAPI + PostgreSQL 16**) para la captura confidencial de encuestas de sensibilidad tarifaria (Van Westendorp + NMS) y consola administrativa protegida por contraseña.

## Rutas del Servicio

- **`GET /`**: Encuesta pública institucional (5 pasos). No contiene enlaces ni código de la consola administrativa ni datos de otros encuestados.
- **`GET /api/v1/services`**: Devuelve los servicios complementarios activos desde PostgreSQL.
- **`POST /api/v1/responses`**: Registra una respuesta en PostgreSQL validando la desigualdad estricta `0 < tooCheap < cheap < expensive < tooExpensive`.
- **`GET /admin`**: Consola de Inteligencia Tarifaria y Catálogo de Servicios (protegida por contraseña).
- **`POST /api/v1/admin/login`** / **`POST /api/v1/admin/logout`**: Autenticación mediante cookie `HttpOnly` firmada con `HMAC-SHA256` (con límite de intentos fallidos por IP).
- **`GET /api/v1/admin/responses`** / **`GET /api/v1/admin/export.csv`**: Endpoints protegidos (`401 Unauthorized` sin sesión válida).
- **`GET/POST/PUT/DELETE /api/v1/admin/services`**: Gestión persistente del catálogo de servicios complementarios (`401 Unauthorized` sin sesión válida).
- **`GET /api/v1/health`**: Healthcheck de aplicación y conectividad PostgreSQL (`200 OK`).

---

## Prueba Local con Docker

1. Copia `.env.example` a `.env` y define tus credenciales:
   ```bash
   cp .env.example .env
   ```
2. Levanta ambos contenedores (la base de datos ejecuta `database/schema.sql` automáticamente en el primer arranque):
   ```bash
   docker compose up -d --build
   ```
3. Verifica en el navegador:
   - Encuesta pública: `http://localhost:8080/`
   - Consola Admin: `http://localhost:8080/admin`
   - Healthcheck: `http://localhost:8080/api/v1/health`

---

## Despliegue en AWS (Para el Senior Developer)

1. **Base de datos:** Crear una instancia **Amazon RDS PostgreSQL 16** (o usar un RDS existente con una base dedicada `latinex_wtp`) y ejecutar `database/schema.sql` una única vez.
2. **Imagen Docker:** Construir y subir el `Dockerfile` a **Amazon ECR**:
   ```bash
   docker build -t latinex-wtp-app .
   ```
3. **Ejecución:** Desplegar en **AWS App Runner** o **Amazon ECS (Fargate)** detrás de un **ALB con certificado ACM (HTTPS)** en el dominio corporativo (ej. `https://encuesta.latinexhub.com`).
4. **Variables de entorno obligatorias (Secrets Manager / SSM):**
   - `DATABASE_URL`: `postgresql://<user>:<pass>@<rds-endpoint>:5432/latinex_wtp?sslmode=require`
   - `ADMIN_PASSWORD`: Contraseña robusta para acceder a `/admin`
   - `SESSION_SECRET`: Cadena aleatoria de 64 caracteres hexadecimales
   - `COOKIE_SECURE`: `true` (obligatorio en producción detrás de HTTPS)
5. **Healthcheck:** Configurar `/api/v1/health` en el Target Group / App Runner.
