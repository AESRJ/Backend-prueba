# Base de datos MySQL — Focus IA

Documentación completa del proceso de migración de SQL Server a MySQL y la
conexión con el frontend desplegado en Vercel.

---

## Índice

1. [Arquitectura general](#arquitectura-general)
2. [Schema de la base de datos](#schema-de-la-base-de-datos)
3. [Proveedores recomendados](#proveedores-recomendados)
4. [Configuración paso a paso](#configuración-paso-a-paso)
5. [Variables de entorno](#variables-de-entorno)
6. [Cambios realizados al proyecto](#cambios-realizados-al-proyecto)
7. [Verificación](#verificación)
8. [Seguridad](#seguridad)

---

## Arquitectura general

```
┌─────────────────────┐        HTTPS         ┌──────────────────────┐
│   Frontend          │ ──────────────────── │   Backend API        │
│   (Vercel)          │   REST / JSON         │   FastAPI            │
│   login.html        │                      │   (Railway u otro)   │
│   prueba.html       │                      │   Puerto 8000        │
└─────────────────────┘                      └──────────┬───────────┘
                                                        │
                                              aiomysql (async)
                                                        │
                                             ┌──────────▼───────────┐
                                             │   MySQL 8.0+         │
                                             │   Base de datos:     │
                                             │   focusia            │
                                             │   Tabla: users       │
                                             └──────────────────────┘
```

> El frontend en Vercel **no se conecta directamente** a la base de datos.
> Toda la comunicación pasa por el backend FastAPI.

---

## Schema de la base de datos

El archivo `database/schema.sql` contiene el schema completo listo para ejecutar.

### Tabla `users`

| Columna          | Tipo          | Nulo | Valor por defecto    | Descripción                        |
|------------------|---------------|------|----------------------|------------------------------------|
| `id`             | INT           | NO   | AUTO_INCREMENT       | Identificador único                |
| `email`          | VARCHAR(255)  | NO   | —                    | Correo electrónico (único)         |
| `hashed_password`| VARCHAR(255)  | NO   | —                    | Contraseña en bcrypt               |
| `name`           | VARCHAR(100)  | NO   | —                    | Nombre del usuario                 |
| `profile_data`   | JSON          | SÍ   | NULL                 | Datos adicionales del perfil       |
| `created_at`     | DATETIME      | NO   | CURRENT_TIMESTAMP    | Fecha de creación                  |
| `is_active`      | TINYINT(1)    | NO   | 1                    | Cuenta activa (fastapi-users)      |
| `is_superuser`   | TINYINT(1)    | NO   | 0                    | Permisos de administrador          |
| `is_verified`    | TINYINT(1)    | NO   | 0                    | Email verificado                   |

---

## Proveedores recomendados

### Opción A — Railway MySQL (recomendado, misma plataforma)

Railway ya aloja el backend del proyecto. Añadir MySQL es la opción más sencilla.

1. Ir al proyecto en [Railway](https://railway.app)
2. Clic en **+ New** → **Database** → **MySQL**
3. Railway crea la base de datos y genera las variables de entorno automáticamente
4. Copiar la variable `MYSQL_URL` y adaptarla al formato `mysql+aiomysql://...`

### Opción B — PlanetScale (free tier generoso)

1. Registrarse en [PlanetScale](https://planetscale.com)
2. Crear una base de datos → rama `main`
3. Ir a **Connect** → seleccionar **SQLAlchemy** para obtener la cadena de conexión
4. La URL tendrá el formato:
   ```
   mysql+aiomysql://usuario:password@aws.connect.psdb.cloud/focusia?ssl_ca=/etc/ssl/certs/ca-certificates.crt
   ```

### Opción C — Aiven for MySQL (free trial)

1. Registrarse en [Aiven](https://aiven.io)
2. Crear servicio MySQL 8.0
3. Descargar el certificado CA (`ca.pem`)
4. Usar la URL con parámetro `ssl_ca`

### Opción D — Local (desarrollo)

```bash
# Instalar MySQL localmente
sudo apt install mysql-server   # Ubuntu/Debian
brew install mysql              # macOS

# Crear la base de datos
mysql -u root -p < database/schema.sql
```

URL local:
```
DATABASE_URL=mysql+aiomysql://root:TU_CONTRASEÑA@localhost:3306/focusia
```

---

## Configuración paso a paso

### 1. Crear la base de datos en el proveedor elegido

Ejecutar el schema:

```bash
mysql -h HOST -u USUARIO -p NOMBRE_DB < database/schema.sql
```

O pegarlo directamente en la consola SQL del proveedor (Railway, PlanetScale, etc.).

### 2. Configurar el `.env` del backend

Editar `backend/.env` con las credenciales reales:

```env
DATABASE_URL=mysql+aiomysql://USUARIO:CONTRASEÑA@HOST:3306/focusia
JWT_SECRET=65b90e784de1a987221685645a729c4954e120306778403e9ba50b899b5e1eb1a64648c985ff62937ccc96de8b3b48bbb1168d08f29b11a80ff70e60c3957c21
```

### 3. Configurar variables de entorno en Railway

En el panel de Railway del servicio backend:

1. Ir a la pestaña **Variables**
2. Agregar `DATABASE_URL` con la cadena de conexión MySQL
3. Agregar `JWT_SECRET` con el mismo valor del `.env`
4. Railway reinicia el servicio automáticamente

### 4. Verificar la conexión

Al iniciar la aplicación, SQLAlchemy crea la tabla `users` automáticamente.
Compruébalo con:

```bash
# Desde el proveedor MySQL
SELECT * FROM information_schema.tables WHERE table_schema = 'focusia';
```

---

## Variables de entorno

| Variable       | Descripción                      | Ejemplo                                                      |
|----------------|----------------------------------|--------------------------------------------------------------|
| `DATABASE_URL` | Cadena de conexión MySQL async   | `mysql+aiomysql://user:pass@host:3306/focusia`               |
| `JWT_SECRET`   | Secreto para firmar tokens JWT   | Cadena hexadecimal de 64+ caracteres                         |

Ver `backend/.env.example` para más ejemplos por proveedor.

---

## Cambios realizados al proyecto

### `backend/requirements.txt`

| Antes (SQL Server)   | Después (MySQL)   |
|----------------------|-------------------|
| `aioodbc`            | `aiomysql==0.2.0` |
| `pyodbc`             | `PyMySQL==1.1.1`  |

### `backend/app/main.py`

Eliminada la línea que transformaba la URL de `mssql+pyodbc://` a `mssql+aioodbc://`:

```python
# ANTES (SQL Server)
DATABASE_URL = settings.DATABASE_URL.replace("mssql+pyodbc://", "mssql+aioodbc://")

# DESPUÉS (MySQL)
DATABASE_URL = settings.DATABASE_URL
```

### `backend/.env`

Actualizado el formato de la URL de conexión de SQL Server a MySQL:

```env
# ANTES
DATABASE_URL=mssql+pyodbc://usuario:contraseña@host.database.windows.net/db?driver=...

# DESPUÉS
DATABASE_URL=mysql+aiomysql://USUARIO:CONTRASEÑA@HOST:3306/focusia
```

### `backend/Dockerfile`

Eliminadas las dependencias de Microsoft ODBC Driver. Ahora instala solo las
librerías de cliente MySQL:

```dockerfile
# ANTES — instalaba unixodbc, curl, gnupg2, msodbcsql18 (~500 MB extra)
# DESPUÉS — solo instala default-libmysqlclient-dev + gcc (~50 MB)
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
```

---

## Verificación

Una vez desplegado, probar los endpoints desde el frontend o con `curl`:

```bash
# 1. Registrar un usuario
curl -X POST https://TU_BACKEND_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"prueba@ejemplo.com","password":"Contraseña123","name":"Usuario Prueba"}'

# 2. Iniciar sesión (obtener token JWT)
curl -X POST https://TU_BACKEND_URL/auth/jwt/login \
  -d "username=prueba@ejemplo.com&password=Contraseña123"

# 3. Ver datos del usuario autenticado
curl https://TU_BACKEND_URL/users/me \
  -H "Authorization: Bearer TOKEN_AQUI"
```

---

## Seguridad

- **No subas `.env` a GitHub.** Está en `.gitignore` por convención; verifica que sea así.
- Usa `.env.example` como plantilla pública sin valores reales.
- En producción, configura las variables de entorno directamente en Railway (o el proveedor elegido), nunca en archivos del repositorio.
- El `JWT_SECRET` actual ya es seguro (128 caracteres hex). No lo cambies sin invalidar todas las sesiones activas.
- Considera restringir `allow_origins` en CORS a solo el dominio de tu frontend Vercel una vez en producción:
  ```python
  # backend/app/main.py
  allow_origins=["https://tu-app.vercel.app"]
  ```
