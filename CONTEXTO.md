# 🏨 Resumen del Proyecto — Sistema PMS Hotel Salma Suite VIP

## 🎯 Objetivo del Sistema

Sistema de gestión hotelera (PMS - Property Management System) diseñado
exclusivamente para uso interno del personal del Hotel Salma Suites VIP.
Permite gestionar habitaciones, huéspedes, reservaciones, consumos, pagos,
inventario y reportes desde una interfaz web moderna y elegante.

El acceso está restringido solo al personal del hotel (administrador y
recepcionistas). No hay registro público ni acceso externo.

---

## 🛠️ Stack Tecnológico

### Frontend

| Tecnología        | Versión      | Uso                  |
| ----------------- | ------------ | -------------------- |
| SvelteKit         | 5 (Runes)    | Framework principal  |
| TailwindCSS       | v4           | Estilos y responsive |
| Plus Jakarta Sans | Google Fonts | Tipografía UI        |
| Playfair Display  | Google Fonts | Tipografía títulos   |

### Backend

| Tecnología                    | Versión | Uso                                        |
| ----------------------------- | ------- | ------------------------------------------ |
| Django                        | 6.0.3   | Framework principal                        |
| Django REST Framework         | 3.x     | API REST                                   |
| rest_framework.authtoken      | —       | Autenticación por token en cookie HttpOnly |
| djangorestframework-simplejwt | 5.x     | Tokens JWT para recuperación de contraseña |
| django-cors-headers           | 4.x     | CORS entre frontend y backend              |

### Base de Datos

| Entorno    | Motor                             |
| ---------- | --------------------------------- |
| Desarrollo | SQLite                            |
| Producción | PostgreSQL / Supabase (pendiente) |

### Servicios Externos

| Servicio        | Uso                        | Estado                     |
| --------------- | -------------------------- | -------------------------- |
| Gmail SMTP      | Recuperación de contraseña | ✅ Funcionando             |
| Twilio WhatsApp | Notificaciones automáticas | ⚙️ Configurado, sin probar |
| ReportLab       | Generación de PDFs         | ✅ Instalado               |
| openpyxl        | Exportación Excel          | ✅ Instalado               |

### Entorno de Desarrollo

- **OS:** Windows (MiniOS 10)
- **Hardware:** Intel Celeron 1.46GHz, 4GB RAM, SSD 128GB
- **Backend:** `localhost:8000`
- **Frontend:** `localhost:5173`
- **Gestor de Procesos:** `concurrently` para ejecución simultánea desde una única terminal integrada en VS Code.
- **Script de Inicio:** Centralizado en el `package.json` de la raíz.

---

## 🎨 Diseño

### Paleta de Colores

| Color              | HEX       | Uso                  |
| ------------------ | --------- | -------------------- |
| Chocolate profundo | `#1A0F0A` | Fondo principal      |
| Café suave         | `#2D1B14` | Cards y contenedores |
| Café hover         | `#3D261C` | Estados hover        |
| Borde              | `#4A352C` | Bordes y separadores |
| Texto terciario    | `#827066` | Textos de apoyo      |
| Texto secundario   | `#BDB2A7` | Labels, subtextos    |
| Texto principal    | `#F2EFE9` | Textos principales   |
| Dorado primario    | `#B38E5D` | Color de marca, CTAs |
| Dorado hover       | `#D9C5A3` | Estados hover dorado |
| Dorado oscuro      | `#735C3D` | Gradientes, bordes   |
| Verde              | `#2D6A4F` | Éxito, disponible    |
| Rojo               | `#9B2226` | Error, alerta        |
| Azul               | `#1E3A5F` | Info, reservas       |
| Púrpura            | `#582F7E` | VIP                  |

### Tipografías

- **Títulos y nombres:** Playfair Display (serif)
- **UI, botones, datos:** Plus Jakarta Sans (sans-serif)

---

## 📁 Estructura del Proyecto

```
hotel-pms/
├── backend/
│   ├── apps/
│   │   ├── users/
│   │   │   ├── authentication.py   # CookieTokenAuthentication + CsrfExemptSessionAuthentication
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py            # login/logout con HttpOnly cookie + reset por caché
│   │   │   └── urls.py
│   │   ├── habitaciones/
│   │   ├── guests/
│   │   ├── reservaciones/
│   │   │   ├── models.py           # Incluye campo tipo_cliente
│   │   │   ├── serializers.py      # tipo_cliente en ReservaListSerializer
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   ├── pagos/
│   │   ├── inventario/
│   │   ├── dashboard/
│   │   ├── reportes/
│   │   └── notificaciones/
│   ├── config/
│   │   ├── settings.py             # CACHES, CookieTokenAuthentication, cookie settings
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── database/db.sqlite3
│   ├── seed.py
│   ├── .env
│   └── manage.py
├── frontend/
│   └── src/
│       ├── app.css
│       ├── app.d.ts                # Locals.user tipado completo
│       ├── app.html
│       ├── hooks.server.ts         # Validación de cookie + caché de usuario en memoria
│       └── lib/
│           ├── components/
│           │   ├── habitaciones/
│           │   │   ├── RoomCard.svelte
│           │   │   └── RoomModal.svelte
│           │   ├── huespedes/
│           │   │   ├── GuestTable.svelte
│           │   │   ├── GuestModal.svelte
│           │   │   └── VIPToggle.svelte
│           │   ├── reservaciones/
│           │   │   ├── BookingCalendar.svelte
│           │   │   ├── CheckInForm.svelte
│           │   │   ├── ConsumoSelector.svelte
│           │   │   └── NoShowModal.svelte
│           │   ├── ButtonGold.svelte
│           │   ├── CardHotel.svelte
│           │   ├── Header.svelte
│           │   ├── Icons.svelte
│           │   ├── InputHotel.svelte
│           │   ├── KPICard.svelte
│           │   ├── Loading.svelte
│           │   ├── Sidebar.svelte
│           │   ├── Skeleton.svelte
│           │   ├── Toast.svelte
│           │   └── WelcomeBanner.svelte
│           ├── services/
│           │   ├── api.ts              # apiFetch con credentials: 'include'
│           │   ├── dashboard.ts
│           │   ├── habitaciones.ts
│           │   ├── huespedes.ts        # NUEVO
│           │   └── reservaciones.ts    # NUEVO — incluye TIPOS_CLIENTE con colores
│           ├── stores/
│           │   ├── auth.ts             # Sin localStorage — hidratado desde SSR
│           │   └── toast.ts
│           └── index.ts
│       └── routes/
│           ├── +layout.svelte          # Hidrata auth store desde data.user SSR
│           ├── +layout.server.ts       # NUEVO — expone locals.user a todas las rutas
│           ├── +page.svelte            # Redirección a /login
│           ├── login/
│           │   └── +page.svelte
│           ├── recuperar/
│           │   └── +page.svelte
│           ├── dashboard/
│           │   ├── +page.svelte        # Datos via $props desde servidor
│           │   └── +page.server.ts     # NUEVO — SSR con Promise.allSettled
│           ├── habitaciones/
│           │   ├── +page.svelte        # SSR + invalidateAll() para RoomModal
│           │   └── +page.server.ts     # NUEVO
│           ├── huespedes/
│           │   ├── +page.svelte        # NUEVO — tabla + filtros + VIP toggle optimista
│           │   └── +page.server.ts     # NUEVO — filtros search/vip en URL
│           └── reservaciones/
│               ├── +page.svelte        # NUEVO — BookingCalendar estilo papel
│               └── +page.server.ts     # NUEVO — navegación semanal por URL
├── package.json                        # Scripts raíz con concurrently
└── package-lock.json
```

---

## 🔐 Autenticación — Cambios Importantes (migración a HttpOnly cookies)

### Situación anterior (⚠️ insegura)

- Token guardado en `localStorage` + `document.cookie` (JS podía leerlo)
- `hooks.server.ts` leía la cookie pero **no validaba** el token contra Django
- `apiFetch` leía el token de `localStorage` y lo enviaba en header `Authorization`
- SSR imposible en rutas protegidas → datos cargados en `onMount` → "Loading..." en cada visita

### Situación actual (✅ segura + SSR)

- Django devuelve el token en una **cookie HttpOnly** al hacer login
- JS nunca puede leer el token (protección XSS total)
- `hooks.server.ts` valida el token contra `/api/auth/profile/` con caché en memoria (5 min)
- `apiFetch` usa `credentials: 'include'` — el browser envía la cookie automáticamente
- Rutas protegidas pre-cargan datos en `+page.server.ts` → sin "Loading..." visible

### Configuración de la cookie (Django)

```python
COOKIE_NAME    = 'auth_token'
COOKIE_MAX_AGE = 60 * 60 * 24 * 7   # 7 días
httponly       = True                 # JS no puede leerla
secure         = not settings.DEBUG  # True solo en producción (HTTPS)
samesite       = 'Lax'               # Protección CSRF básica
```

### Archivos modificados para la migración

| Archivo                                 | Cambio                                                                                         |
| --------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `backend/apps/users/authentication.py`  | Nueva clase `CookieTokenAuthentication` que lee el token de la cookie                          |
| `backend/apps/users/views.py`           | `login_view` usa `response.set_cookie()`, `logout_view` usa `response.delete_cookie()`         |
| `backend/config/settings.py`            | `DEFAULT_AUTHENTICATION_CLASSES` con `CookieTokenAuthentication` primero; `CACHES` configurado |
| `frontend/src/hooks.server.ts`          | Valida token contra Django, caché en memoria de 5 min, expone `locals.user`                    |
| `frontend/src/app.d.ts`                 | `Locals.user` tipado con `username`, `email`, `role`, `first_name`, `last_name`                |
| `frontend/src/lib/stores/auth.ts`       | Sin `localStorage`; método `init()` para hidratar desde SSR; `logout()` llama al backend       |
| `frontend/src/lib/services/api.ts`      | `credentials: 'include'` en todos los fetch; sin header `Authorization` manual                 |
| `frontend/src/routes/+layout.server.ts` | **NUEVO** — expone `locals.user` como `data.user` a todas las rutas                            |
| `frontend/src/routes/+layout.svelte`    | `$effect(() => auth.init(data.user))` — hidrata el store desde SSR                             |

---

## 🔑 Recuperación de Contraseña — Correcciones

### Problemas corregidos en `backend/apps/users/views.py`

1. **`reset_codes` era un dict en memoria** → se pierde al reiniciar Django en desarrollo.
   - **Solución:** Migrado a `django.core.cache` con `cache.set(key, value, timeout=900)`.
   - El TTL del caché reemplaza el manejo manual de `datetime.now() + timedelta(minutes=15)`.

2. **`get_tokens_for_user` como función auxiliar separada** → innecesario, solo se usaba en un lugar.
   - **Solución:** Código JWT inline directamente en `verify_reset_code`.

3. **`reset_password` no validaba el token** → cualquiera con el email podía cambiar la contraseña.
   - **Solución:** `verify_reset_code` guarda el `access` token en caché; `reset_password` lo compara antes de proceder.

4. **Tokens DRF no se invalidaban al cambiar contraseña.**
   - **Solución:** `Token.objects.filter(user=user).delete()` al final de `reset_password`.

### Constantes usadas

```python
RESET_CACHE_PREFIX = 'pwd_reset:'
RESET_TTL          = 60 * 15   # 15 minutos
```

---

## 🗄️ Modelos de Base de Datos

### `users.User` (AbstractUser)

- `role`: `admin` | `recepcionista`
- `phone`, `created_at`, `updated_at`

### `habitaciones.TipoHabitacion`

- Tipos: matrimonial, doble_individual, doble_matrimonial, triple_individual, suite
- `precio_base_noche`, `capacidad_maxima`

### `habitaciones.Habitacion`

- `numero`, `piso`, `tipo` (FK)
- `estado`: libre | limpia | sucia | ocupada | mantenimiento | construccion
- `qr_code` (generado automáticamente), `tiene_minibar`

### `guests.Huesped`

- `tipo_documento`: V | E | J | G | P
- `numero_documento`, `nombre`, `apellido`
- `telefono`, `email`, `es_vip`
- `acompanantes`: JSONField `[{"nombre": "...", "documento": "...", "edad": 0}]`

### `reservaciones.Reserva`

- `estados`: pendiente | sin_pagar | confirmada | pagada | cancelada | no_show
- `metodos_pago`: efectivo_usd | efectivo_ves | transferencia | tarjeta | pago_movil | zelle | binance
- `tipo_cliente`: **NUEVO** — particular | militar | politico | artista | empresarial | deportista | diplomatico | medico | religioso | turista
- `monto_total`, `monto_pagado`, `referencia_pago`
- `requiere_factura_seniat`, `datos_factura` (JSONField)
- `no_show_motivo`, `no_show_fecha`

### `reservaciones.Consumo`

- `reserva` (FK), `producto`, `cantidad`, `precio_unitario`
- `noches_asociadas`, `registrado_por`

### `reservaciones.Actividad`

- Timeline de acciones del sistema para el dashboard
- `tipo`, `descripcion`, `detalle`
- FKs opcionales: habitacion, reserva, huesped, usuario

### `pagos.Pago`

- `reserva` (FK), `monto`, `metodo`, `concepto`, `referencia`

### `pagos.CierreCaja`

- Un cierre por recepcionista por día
- Desglose por método: efectivo_usd, efectivo_ves, transferencias, tarjetas, pago_movil, zelle, binance
- `total_caja`, `pdf_generado`

### `inventario.Producto`

- `nombre`, `categoria`, `precio_venta`, `precio_costo`
- `stock_actual`, `stock_minimo`, `stock_maximo`
- `sin_stock`, `stock_bajo` (calculados en `save()`)

### `notificaciones.Notificacion`

- `tipo`, `canal` (whatsapp/email/sistema), `estado`
- `destinatario_nombre`, `destinatario_telefono`
- `mensaje`, `respuesta_api`, `error_detalle`

---

## 🌐 API Endpoints

```
POST   /api/auth/login/
POST   /api/auth/logout/
GET    /api/auth/profile/
POST   /api/auth/password-reset/request/
POST   /api/auth/password-reset/verify/
POST   /api/auth/password-reset/reset/

GET    /api/dashboard/stats/
GET    /api/dashboard/ocupacion-semanal/
GET    /api/dashboard/habitaciones-grid/
GET    /api/dashboard/actividades/
GET    /api/dashboard/alertas/

GET    /api/habitaciones/
POST   /api/habitaciones/
GET    /api/habitaciones/<id>/
PUT    /api/habitaciones/<id>/
DELETE /api/habitaciones/<id>/
GET    /api/habitaciones/tipos/

GET    /api/huespedes/
POST   /api/huespedes/
GET    /api/huespedes/<id>/
PUT    /api/huespedes/<id>/
DELETE /api/huespedes/<id>/
GET    /api/huespedes/buscar/?documento=

GET    /api/reservaciones/
POST   /api/reservaciones/
GET    /api/reservaciones/<id>/
PUT    /api/reservaciones/<id>/
DELETE /api/reservaciones/<id>/
POST   /api/reservaciones/<id>/no-show/
POST   /api/reservaciones/<id>/consumo/
POST   /api/reservaciones/<id>/cambiar-habitacion/
GET    /api/reservaciones/actividades/

GET    /api/pagos/
POST   /api/pagos/
GET    /api/pagos/resumen-hoy/
POST   /api/pagos/cierre/
GET    /api/pagos/cierres/

GET    /api/inventario/
POST   /api/inventario/
GET    /api/inventario/<id>/
PUT    /api/inventario/<id>/
POST   /api/inventario/<id>/entrada/
POST   /api/inventario/<id>/ajuste/
GET    /api/inventario/alertas/

GET    /api/reportes/consumos/<huesped_id>/
GET    /api/reportes/reservas/
GET    /api/reportes/ingresos/
GET    /api/reportes/historial/

GET    /api/notificaciones/
POST   /api/notificaciones/reserva/<id>/
POST   /api/notificaciones/personalizada/
POST   /api/notificaciones/recordatorios/
```

---

## ✅ Requisitos Funcionales

| ID   | Módulo                                                | Estado                             |
| ---- | ----------------------------------------------------- | ---------------------------------- |
| RF01 | Autenticación por roles (Admin / Recepcionista)       | ✅ Completo                        |
| RF01 | Recuperación de contraseña por Gmail                  | ✅ Completo + corregido (caché)    |
| RF01 | Migración a HttpOnly cookies (SSR seguro)             | ✅ Completo                        |
| RF02 | Dashboard con KPIs, gráfico, habitaciones, timeline   | ✅ Completo (SSR)                  |
| RF03 | CRUD Habitaciones con estados dinámicos e historial   | ✅ Backend ✅ / Frontend ✅ (SSR)  |
| RF04 | Registro de huéspedes con acompañantes                | ✅ Backend ✅ / Frontend ✅ (SSR)  |
| RF05 | Gestión de reservas con check-in/out y factura Seniat | ✅ Backend ✅ / Frontend ✅ (SSR)  |
| RF06 | Registro de consumos por huésped                      | ✅ Backend ✅ / Frontend ✅        |
| RF07 | Cierre de caja con PDF firmado                        | ⚙️ Backend ✅ / Frontend pendiente |
| RF08 | Acta No-Show automática                               | ✅ Backend ✅ / Frontend ✅        |
| RF09 | Reportes PDF (consumos, reservas, ingresos)           | ⚙️ Backend ✅ / Frontend pendiente |
| RF10 | Calendario visual de habitaciones (tipo papel)        | ✅ Completo (BookingCalendar)      |
| RF11 | Notificaciones WhatsApp automáticas (Twilio)          | ⚙️ Backend ✅ / Sin probar         |
| RF12 | Códigos QR por habitación                             | ⚙️ Backend ✅ / Frontend pendiente |
| RF13 | Inventario básico con alertas de stock                | ⚙️ Backend ✅ / Frontend pendiente |
| RF14 | Exportación Excel/CSV de todos los reportes           | ⚙️ Backend ✅ / Frontend pendiente |

---

## 🔧 Decisiones Técnicas Importantes

### Autenticación (actualizado)

- **Antes:** Token en `localStorage` + `document.cookie` manual desde JS.
- **Ahora:** Token en cookie `HttpOnly` enviada por Django en el `Set-Cookie` del login.
- `CookieTokenAuthentication` en `authentication.py` lee el token de `request.COOKIES` antes que el header `Authorization` (que se mantiene como fallback).
- `credentials: 'include'` en todo `apiFetch` para que el browser envíe la cookie automáticamente en requests cross-origin.
- `CORS_ALLOW_CREDENTIALS = True` ya estaba configurado.
- En desarrollo: `Secure=False` (sin HTTPS). En producción: `Secure=True`.

### Caché de Validación de Token (hooks.server.ts)

- `hooks.server.ts` valida el token contra Django **máximo una vez cada 5 minutos** por token.
- Caché en memoria del proceso Node/Vite: `Map<token, { user, expiry }>`.
- Evita el problema de hacer un request a Django en cada navegación del usuario.
- Al hacer logout, Django borra el token de la BD y el browser elimina la cookie → la caché expira sola.

### Caché de Recuperación de Contraseña (Django)

- Antes: `reset_codes = {}` (dict global en memoria → se borra al reiniciar).
- Ahora: `django.core.cache` con `LocMemCache` en desarrollo, preparado para Redis en producción.
- TTL de 15 minutos gestionado por el caché (sin comparar fechas manualmente).
- Flujo de 3 pasos con token de verificación: `request` → `verify` (emite JWT) → `reset` (valida JWT).

### Patrón SSR en SvelteKit (todos los módulos)

Todas las rutas protegidas siguen este patrón:

```
/ruta/
├── +page.server.ts   → load() corre en el servidor
│                       lee cookie, llama a Django, retorna data
└── +page.svelte      → recibe data via $props(), sin onMount para datos
                        usa invalidateAll() para recargar tras mutaciones
```

- **Nunca** se usa `onMount` para cargar datos iniciales en rutas protegidas.
- `$derived(data.campo)` en lugar de `$state` para datos del servidor.
- `invalidateAll()` re-ejecuta el `load` del servidor tras crear/editar/borrar.
- Mutaciones optimistas para acciones rápidas (ej: toggle VIP) sin esperar recarga completa.

### Módulo de Huéspedes

- `GuestTable.svelte`: tabla desktop + cards mobile con layout responsive.
- `VIPToggle.svelte`: actualización optimista del estado VIP sin recargar la tabla.
- `GuestModal.svelte`: wizard con validación de tipos de documento venezolanos (V/E/J/G/P) y acompañantes dinámicos.
- Filtros de búsqueda sincronizados con la URL (`?search=...&vip=true`) para que el servidor los lea en SSR.
- Debounce de 350ms en la búsqueda para evitar un request por tecla.

### Módulo de Reservaciones — Calendario tipo papel

- `BookingCalendar.svelte` replica exactamente el formato del registro físico del hotel:
  - Filas = habitaciones agrupadas por piso
  - Columnas = días de la semana (Lun–Dom) con fecha
  - Celda ocupada = círculo coloreado según tipo de cliente
  - Símbolo de entrada (→) en el primer día, salida (✓) en el último, punto (●) en días intermedios
  - Columna "Nombre / Empresa" y columna "Neo Ledok" igual que el papel
  - Círculo vacío (○) en celdas libres
- 10 tipos de cliente con colores definidos en `TIPOS_CLIENTE`:

| Tipo              | Color                  |
| ----------------- | ---------------------- |
| Particular        | Púrpura `#7340A0`      |
| Militar / GN      | Verde `#2D6A4F`        |
| Político / Gov.   | Rojo `#9B2226`         |
| Artista / Medios  | Azul marino `#1E3A5F`  |
| Empresarial       | Dorado `#B38E5D`       |
| Deportista        | Verde oscuro `#1B5E20` |
| Diplomático       | Índigo `#4A148C`       |
| Personal Médico   | Teal `#006064`         |
| Religioso         | Naranja `#E65100`      |
| Turista / Agencia | Gris azul `#37474F`    |

- Navegación semanal vía URL (`?semana=YYYY-MM-DD`) → SSR re-ejecuta el `load`.
- `CheckInForm.svelte`: wizard de 4 pasos (Huésped → Habitación → Detalles → Confirmar).
- `NoShowModal.svelte`: muestra vista previa del acta antes de confirmar; irreversible.
- `ConsumoSelector.svelte`: catálogo de productos del inventario con carrito, agrega múltiples consumos en paralelo.
- Botón "Exportar registro" visible en la página (implementación pendiente — endpoint Django ya existe).

### Estructura de Apps Django

- Una app por módulo de negocio para mantener el código organizado.
- `apps/users/authentication.py` centraliza las clases de autenticación.

### Frontend — Svelte 5 Runes

- `$state` para estado local mutable (filtros, modales, formularios).
- `$derived` para valores computados y datos que vienen del servidor.
- `$effect` para efectos secundarios (sincronizar store con data SSR, debounce).
- `$props()` para recibir props de componentes padre y `data` de SvelteKit.
- **Nunca** se mezcla `onMount` con `$effect` para el mismo propósito.

---

## ⚠️ Migraciones Pendientes de BD

Tras agregar `tipo_cliente` al modelo `Reserva`, correr:

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

Y agregar `tipo_cliente` al `fields` de `ReservaListSerializer` en `serializers.py`.

---

## 🚀 Pendiente / En Progreso

### Frontend (páginas por crear)

- `/inventario` — listado, entrada de stock, alertas de stock bajo
- `/pagos` — registro de pagos y cierre de caja con PDF
- `/reportes` — descarga PDF/Excel (botón de exportar ya visible en reservaciones)
- `/perfil` — edición de datos del usuario
- `/admin` — gestión de usuarios (solo admin)
- `/configuracion` — ajustes del sistema (solo admin)

### Componentes pendientes

- Header: conectar con `notificacionesApi.getAll()` para mostrar alertas reales de stock y reservas pendientes
- QR: visualización del código QR de cada habitación en el modal

### Exportación de Reservaciones

- Botón "Exportar registro" ya está en `/reservaciones`
- Backend tiene `openpyxl` instalado y endpoints en `/api/reportes/`
- Falta implementar el handler del `onclick` con la llamada al API y descarga del archivo

### Producción

Antes de desplegar:

- Cambiar `DEBUG = False`
- Definir `ALLOWED_HOSTS` con el dominio real
- Migrar de SQLite a PostgreSQL/Supabase
- Cambiar `CORS_ALLOWED_ORIGINS` al dominio de producción
- Configurar HTTPS obligatorio (`Secure=True` en cookies automáticamente)
- Mover `VITE_API_URL` del frontend a variable de entorno `.env`
- Eliminar todos los `console.log` de debug
- Cambiar `CACHES` de `LocMemCache` a Redis (`django-redis`)
- Desplegar en red local del hotel o VPS privado con acceso restringido por IP

### Optimizaciones identificadas pero no urgentes

- Paginación en listados (esperar a tener datos reales para calibrar el límite)
- WebSockets para actualización en tiempo real del calendario
- Tests automatizados (cuando las features estén estables)
- Docker para simplificar el despliegue

---

## 👤 Usuarios del Sistema

| Rol           | Acceso                                                           |
| ------------- | ---------------------------------------------------------------- |
| admin         | Todo el sistema incluyendo configuración y administración        |
| recepcionista | Dashboard, habitaciones, huéspedes, reservas, consumos, reportes |

Usuario de prueba: `basquiatdev` (rol: admin)
