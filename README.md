# SalmaSuitesPMS

Sistema de gestión hotelera (PMS) para uso interno del **Hotel Salma Suite VIP**.  
Desarrollado con SvelteKit 5 + Django 6 · Solo personal autorizado.

---

## Inicio rápido

### Requisitos previos

| Herramienta | Versión mínima | Verificar con      |
| ----------- | -------------- | ------------------ |
| Python      | 3.11+          | `python --version` |
| Node.js     | 18+            | `node --version`   |
| npm         | 9+             | `npm --version`    |

### Primera vez (setup completo)

```bash
# 1. Clonar o descomprimir el proyecto
cd SalmaSuitesPMS

# 2. Instalar dependencia raíz (concurrently)
npm install

# 3. Ejecutar el script de configuración automática
scripts/setup.bat
```

`setup.bat` hace lo siguiente por ti:

- Crea el entorno virtual de Python (`backend/venv`)
- Instala todas las dependencias del backend (`requirements.txt`)
- Ejecuta las migraciones de base de datos
- Te pide crear el superusuario administrador
- Instala las dependencias del frontend (`npm install` en `/frontend`)

### Configurar variables de entorno

Copia el archivo de ejemplo y edítalo:

```bash
copy backend\.env.example backend\.env
```

Edita `backend/.env` con tus datos reales:

```env
SECRET_KEY=tu_clave_secreta_larga_aqui
DEBUG=True

# Email para recuperación de contraseña
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password_de_gmail
DEFAULT_FROM_EMAIL=Sistema PMS <tu_correo@gmail.com>
```

> **Nota Gmail:** Debes usar una [contraseña de aplicación](https://myaccount.google.com/apppasswords), no tu contraseña normal.

### Iniciar el sistema (uso diario)

```bash
# Desde la raíz del proyecto — levanta backend y frontend simultáneamente
npm run dev
```

| Servicio     | URL                         |
| ------------ | --------------------------- |
| Frontend     | http://localhost:5173       |
| Backend      | http://localhost:8000       |
| Django Admin | http://localhost:8000/admin |

---

## Estructura del proyecto

```
SalmaSuitesPMS/
├── backend/          # Django 6 + DRF
│   ├── apps/         # Un módulo por app de negocio
│   │   ├── huespedes/
│   │   ├── habitaciones/
│   │   ├── reservaciones/
│   │   ├── inventario/
│   │   ├── usuarios/
│   │   ├── configuracion/
│   │   ├── bitacora/
│   │   ├── dashboard/
│   │   └── reportes/
│   ├── config/       # settings.py, urls.py
│   ├── .env          # Variables de entorno (NO subir a git)
│   ├── manage.py
│   └── seed.py
├── frontend/         # SvelteKit 5 (Runes) + TailwindCSS
│   └── src/
│       ├── lib/
│       │   ├── components/   # UI reutilizable
│       │   │   ├── ui/       # Botones, inputs, modales, tabs, toast
│       │   │   ├── dashboard/
│       │   │   ├── habitaciones/
│       │   │   ├── huespedes/
│       │   │   ├── reservaciones/
│       │   │   ├── inventario/
│       │   │   ├── reportes/
│       │   │   ├── configuracion/
│       │   │   └── usuarios/
│       │   ├── services/     # Llamadas a la API
│       │   ├── stores/       # Estado global (auth, toast)
│       │   └── types/        # Interfaces TypeScript
│       ├── routes/           # Páginas del sistema
│       │   ├── login/
│       │   ├── recuperar/
│       │   ├── dashboard/
│       │   ├── habitaciones/
│       │   ├── huespedes/
│       │   ├── reservaciones/
│       │   ├── inventario/
│       │   ├── reportes/
│       │   ├── configuracion/
│       │   ├── usuarios/
│       │   └── perfil/
│       └── hooks.server.ts   # Validación de sesión SSR
├── database/         # SQLite (desarrollo)
├── scripts/
│   └── setup.bat     # Configuración inicial (Windows)
├── LOGICA.md         # Especificación funcional completa
└── package.json      # Scripts raíz con concurrently
```

---

## Módulos del sistema

| Módulo        | Funcionalidades                                                                                 |
| ------------- | ----------------------------------------------------------------------------------------------- |
| Dashboard     | KPIs, ocupación semanal, actividades en tiempo real, mapa de habitaciones interactivo           |
| Habitaciones  | CRUD, estados (Limpia/Ocupada/Sucia/Mantenimiento/Obra), imágenes, filtros                      |
| Huéspedes     | CRUD, categoría VIP/Estándar, crédito autorizado, exportación CSV                               |
| Reservaciones | Calendario semanal, flujo completo (crear → check‑in → consumos/pagos → check‑out), cancelación |
| Inventario    | Productos, stock, movimientos (entradas/salidas/ajustes), alertas de stock bajo                 |
| Reportes      | Cierre de caja diario, gráfico de ingresos por período                                          |
| Configuración | Datos del hotel, moneda, colores por tipo de cliente y estado de habitación                     |
| Usuarios      | Gestión de cuentas (admin), roles (admin/recepcionista), perfil con cambio de contraseña        |

---

## Cargar datos de prueba

```bash
cd backend
venv\Scripts\activate
python seed.py
```

Crea 18 habitaciones, 5 huéspedes, configuración inicial y colores por defecto.

---

## Usuarios del sistema

| Rol             | Usuario por defecto          | Acceso                                                        |
| --------------- | ---------------------------- | ------------------------------------------------------------- |
| `admin`         | `admin` / `admin123`         | Todo el sistema + configuración + administración              |
| `recepcionista` | `recepcion` / `recepcion123` | Dashboard, habitaciones, huéspedes, reservas, consumos, pagos |

---

## Seguridad en desarrollo

- El token de sesión viaja en una **cookie `HttpOnly`** — JS nunca puede leerlo.
- `DEBUG=True` deshabilita `Secure` en la cookie (necesario sin HTTPS local).
- `CORS_ALLOWED_ORIGINS` está configurado solo para `localhost:5173`.
- **No exponer el puerto 8000 fuera de la red local durante desarrollo.**

---

## Antes de ir a producción

- [ ] `DEBUG=False` en `.env`
- [ ] `ALLOWED_HOSTS` con el dominio real
- [ ] `SECRET_KEY` larga y aleatoria (nunca la del `.env.example`)
- [ ] Migrar SQLite → PostgreSQL y actualizar `DATABASES` en `settings.py`
- [ ] `CORS_ALLOWED_ORIGINS` con el dominio real
- [ ] Configurar HTTPS — la cookie pasará a `Secure=True` automáticamente
- [ ] Cambiar `CACHES` de `LocMemCache` a Redis
- [ ] Crear `frontend/.env` con `VITE_API_URL=https://tu-dominio.com/api`
- [ ] Restringir acceso por IP (solo red interna del hotel)

---

## Comandos útiles

```bash
# Backend — crear migración tras cambiar un modelo
cd backend && venv\Scripts\activate
python manage.py makemigrations
python manage.py migrate

# Backend — abrir shell de Django
python manage.py shell

# Frontend — build de producción
cd frontend && npm run build

# Instalar nueva dependencia Python
pip install nombre-paquete
pip freeze > requirements.txt
```

---

## Tecnologías

| Capa       | Tecnología                                  |
| ---------- | ------------------------------------------- |
| Frontend   | SvelteKit 5 (Runes), TailwindCSS 4          |
| Backend    | Django 6, Django REST Framework             |
| Auth       | DRF Token Authentication + HttpOnly cookies |
| Base datos | SQLite (dev), PostgreSQL (prod)             |
| Gráficos   | Chart.js                                    |

```

```
