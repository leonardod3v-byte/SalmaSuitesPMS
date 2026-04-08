# ?? Resumen del Proyecto � Sistema PMS Hotel Salma Suite VIP

## ?? Objetivo del Sistema

Sistema de gesti�n hotelera (PMS - Property Management System) dise�ado
exclusivamente para uso interno del personal del Hotel Salma Suites VIP.
Permite gestionar habitaciones, hu�spedes, reservaciones, consumos, pagos,
inventario y reportes desde una interfaz web moderna y elegante.

El acceso est� restringido solo al personal del hotel (administrador y
recepcionistas). No hay registro p�blico ni acceso externo.

---

## ??? Stack Tecnol�gico

### Frontend

| Tecnolog�a        | Versi�n      | Uso                  |
| ----------------- | ------------ | -------------------- |
| SvelteKit         | 5 (Runes)    | Framework principal  |
| TailwindCSS       | v4           | Estilos y responsive |
| Plus Jakarta Sans | Google Fonts | Tipograf�a UI        |
| Playfair Display  | Google Fonts | Tipograf�a t�tulos   |

### Backend

| Tecnolog�a                    | Versi�n | Uso                                        |
| ----------------------------- | ------- | ------------------------------------------ |
| Django                        | 6.0.3   | Framework principal                        |
| Django REST Framework         | 3.x     | API REST                                   |
| rest_framework.authtoken      | �       | Autenticaci�n por token                    |
| djangorestframework-simplejwt | 5.x     | Tokens JWT para recuperaci�n de contrase�a |
| django-cors-headers           | 4.x     | CORS entre frontend y backend              |

### Base de Datos

| Entorno    | Motor                             |
| ---------- | --------------------------------- |
| Desarrollo | SQLite                            |
| Producci�n | PostgreSQL / Supabase (pendiente) |

### Servicios Externos

| Servicio        | Uso                        | Estado                    |
| --------------- | -------------------------- | ------------------------- |
| Gmail SMTP      | Recuperaci�n de contrase�a | ? Funcionando             |
| Twilio WhatsApp | Notificaciones autom�ticas | ? Configurado, sin probar |
| ReportLab       | Generaci�n de PDFs         | ? Instalado               |
| openpyxl        | Exportaci�n Excel          | ? Instalado               |

### Entorno de Desarrollo

- **OS:** Windows (MiniOS 10)
- **Hardware:** Intel Celeron 1.46GHz, 4GB RAM, SSD 128GB
- **Backend:** `localhost:8000`
- **Frontend:** `localhost:5173`
- **Gestor de Procesos:** Se implementó concurrently para la ejecución simultánea de servicios desde una única terminal   integrada en VS Code.
- **Script de Inicio:** Centralizado en el package.json de la raíz para evitar la apertura de ventanas de consola externas.

---

## ?? Dise�o

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
| Verde              | `#2D6A4F` | �xito, disponible    |
| Rojo               | `#9B2226` | Error, alerta        |
| Azul               | `#1E3A5F` | Info, reservas       |
| P�rpura            | `#582F7E` | VIP                  |

### Tipograf�as

- **T�tulos y nombres:** Playfair Display (serif)
- **UI, botones, datos:** Plus Jakarta Sans (sans-serif)

---

## ?? Estructura del Proyecto

hotel-pms/
+-- backend/
� +-- apps/
� � +-- users/ # Autenticaci�n y roles
� � +-- habitaciones/ # CRUD habitaciones
� � +-- guests/ # CRUD hu�spedes
� � +-- reservaciones/ # Reservas, consumos, actividades
� � +-- pagos/ # Pagos y cierre de caja
� � +-- inventario/ # Stock de productos
� � +-- dashboard/ # Stats y datos para el dashboard
� � +-- reportes/ # PDF y Excel
� � +-- notificaciones/ # WhatsApp y registro de env�os
� +-- config/
� � +-- settings.py
� � +-- urls.py
� � +-- wsgi.py
� � +-- asgi.py
� +-- database/db.sqlite3
� +-- seed.py # Script de datos de prueba
� +-- .env
� +-- manage.py
+-- frontend/
+-- src/
+-- lib/
� +-- components/
� � +-- habitaciones/
� � � +-- RoomCard.svelte
� � � +-- RoomModal.svelte
� � +-- ButtonGold.svelte
� � +-- CardHotel.svelte
� � +-- Header.svelte
� � +-- Icons.svelte
� � +-- InputHotel.svelte
� � +-- KPICard.svelte
� � +-- Loading.svelte
� � +-- Sidebar.svelte
� � +-- Toast.svelte
� � +-- WelcomeBanner.svelte
� +-- services/
� � +-- api.ts # Servicios globales de la API
� � +-- dashboard.ts # Endpoints de dashboard
� � +-- habitaciones.ts # Endpoints de habitaciones
� +-- stores/
� +-- auth.ts # Store de autenticaci�n
� +-- toast.ts # Store de toasts
+-- routes/
+-- +layout.svelte # Protecci�n de rutas
+-- +page.svelte # Redirecci�n a /login
+-- login/
+-- recuperar/
+-- dashboard/
+-- habitaciones/

---

## ??? Modelos de Base de Datos

### `users.User` (AbstractUser)

- `role`: `admin` | `recepcionista`
- `phone`, `created_at`, `updated_at`

### `habitaciones.TipoHabitacion`

- Tipos: matrimonial, doble_individual, doble_matrimonial,
  triple_individual, suite
- `precio_base_noche`, `capacidad_maxima`

### `habitaciones.Habitacion`

- `numero`, `piso`, `tipo` (FK)
- `estado`: libre | limpia | sucia | ocupada | mantenimiento | construccion
- `qr_code` (generado autom�ticamente), `tiene_minibar`

### `guests.Huesped`

- `tipo_documento`: V | E | J | G | P
- `numero_documento`, `nombre`, `apellido`
- `telefono`, `email`, `es_vip`
- `acompanantes`: JSONField

### `reservaciones.Reserva`

- `estados`: pendiente | sin_pagar | confirmada | pagada | cancelada | no_show
- `metodos_pago`: efectivo_usd | efectivo_ves | transferencia |
  tarjeta | pago_movil | zelle | binance
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

- Un cierre por recepcionista por d�a
- Desglose por m�todo: efectivo_usd, efectivo_ves, transferencias,
  tarjetas, pago_movil, zelle, binance
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

## ?? API Endpoints

POST /api/auth/login/
POST /api/auth/logout/
GET /api/auth/profile/
POST /api/auth/password-reset/request/
POST /api/auth/password-reset/verify/
POST /api/auth/password-reset/reset/

GET /api/dashboard/stats/
GET /api/dashboard/ocupacion-semanal/
GET /api/dashboard/habitaciones-grid/
GET /api/dashboard/actividades/
GET /api/dashboard/alertas/

GET/POST /api/habitaciones/
GET/PUT/DELETE /api/habitaciones/<id>/
GET /api/habitaciones/tipos/

GET/POST /api/huespedes/
GET/PUT/DELETE /api/huespedes/<id>/
GET /api/huespedes/buscar/?documento=

GET/POST /api/reservaciones/
GET/PUT/DELETE /api/reservaciones/<id>/
POST /api/reservaciones/<id>/no-show/
POST /api/reservaciones/<id>/consumo/
POST /api/reservaciones/<id>/cambiar-habitacion/
GET /api/reservaciones/actividades/

GET/POST /api/pagos/
GET /api/pagos/resumen-hoy/
POST /api/pagos/cierre/
GET /api/pagos/cierres/

GET/POST /api/inventario/
GET/PUT /api/inventario/<id>/
POST /api/inventario/<id>/entrada/
POST /api/inventario/<id>/ajuste/
GET /api/inventario/alertas/

GET /api/reportes/consumos/<huesped_id>/
GET /api/reportes/reservas/
GET /api/reportes/ingresos/
GET /api/reportes/historial/

GET /api/notificaciones/
POST /api/notificaciones/reserva/<id>/
POST /api/notificaciones/personalizada/
POST /api/notificaciones/recordatorios/
`

---

## ? Requisitos Funcionales

| ID   | M�dulo                                                | Estado                           |
| ---- | ----------------------------------------------------- | -------------------------------- |
| RF01 | Autenticaci�n por roles (Admin / Recepcionista)       | ? Completo                       |
| RF01 | Recuperaci�n de contrase�a por Gmail                  | ? Completo                       |
| RF02 | Dashboard con KPIs, gr�fico, habitaciones, timeline   | ? Completo                       |
| RF03 | CRUD Habitaciones con estados din�micos e historial   | ? Backend ? / Frontend pendiente |
| RF04 | Registro de hu�spedes con acompa�antes                | ? Backend ? / Frontend pendiente |
| RF05 | Gesti�n de reservas con check-in/out y factura Seniat | ? Backend ? / Frontend pendiente |
| RF06 | Registro de consumos por hu�sped                      | ? Backend ? / Frontend pendiente |
| RF07 | Cierre de caja con PDF firmado                        | ? Backend ? / Frontend pendiente |
| RF08 | Acta No-Show autom�tica                               | ? Backend ? / Frontend pendiente |
| RF09 | Reportes PDF (consumos, reservas, ingresos)           | ? Backend ? / Frontend pendiente |
| RF10 | Calendario visual de habitaciones                     | ? Pendiente                      |
| RF11 | Notificaciones WhatsApp autom�ticas (Twilio)          | ? Backend ? / Sin probar         |
| RF12 | C�digos QR por habitaci�n                             | ? Backend ? / Frontend pendiente |
| RF13 | Inventario b�sico con alertas de stock                | ? Backend ? / Frontend pendiente |
| RF14 | Exportaci�n Excel/CSV de todos los reportes           | ? Backend ? / Frontend pendiente |

---

## ?? Decisiones T�cnicas Importantes

### Autenticaci�n

- Se us� rest_framework.authtoken (Token fijo por usuario) en lugar
  de JWT para las sesiones normales. JWT solo se usa para el flujo
  temporal de recuperaci�n de contrase�a.
- El token se guarda en localStorage y se env�a en cada request
  como Authorization: Token <key>.
- Se cre� CsrfExemptSessionAuthentication para evitar problemas
  de CSRF en requests cross-origin durante el desarrollo.

### Estructura de Apps Django

- Una app por m�dulo de negocio para mantener el c�digo organizado
  y facilitar el mantenimiento.
- apps/users/authentication.py centraliza la clase de autenticaci�n
  personalizada usada globalmente en REST_FRAMEWORK.

### Frontend

- Migración a Svelte 5 (Runes)
  Se sustituyó la reactividad $: por los nuevos Runes: $state, $derived y $props.
  Esto optimiza el rendimiento en el renderizado del grid de habitaciones y reduce el "ruido" de código
- Configuración de Estilos (Vite & PostCSS)
  PostCSS: Se configuró postcss.config.cjs usando module.exports (CommonJS) para evitar conflictos de sintaxis con Node.js.
  Tailwind v4: Se migró al plugin @tailwindcss/postcss para compatibilidad con la nueva versión del motor de Tailwind.

### Carga del Dashboard

- Se eliminó el archivo único api.js en favor de servicios especializados (dashboard.ts, habitaciones.ts, etc.) para mejorar la mantenibilidad y reducir el tamaño de los bundles.
- El núcleo de comunicación ahora incluye un interceptor automático que inyecta el Token de autenticación y maneja de forma global los errores 401/403, forzando el cierre de sesión y redirección a /login.
- Se mantiene el uso de Promise.allSettled en el Dashboard, pero ahora integrado con Runes de Svelte 5 ($state), permitiendo que la UI reaccione de forma independiente a medida que cada servicio responde.
- La carga de KPIs y el grid de habitaciones se gestionan como estados independientes para que el loading desaparezca progresivamente, optimizando la experiencia en dispositivos de bajo rendimiento.

### Datos de Prueba

- Script seed.py en la ra�z del backend carga todos los datos
  iniciales: tipos de habitaci�n, habitaciones, hu�spedes,
  reservas, actividades y pagos.

---

## ?? Pendiente / En Progreso

### Frontend (p�ginas por crear)

- /habitaciones � listado, CRUD, cambio de estado, historial, QR
- /huespedes � listado, ficha completa con historial de consumos
- /reservas � listado, check-in/out, no-show, cambio de habitaci�n
- /inventario � listado, entrada de stock, alertas
- /reportes � descarga PDF/Excel
- /perfil � edici�n de datos del usuario
- /admin � gesti�n de usuarios (solo admin)
- /configuracion � ajustes del sistema (solo admin)

### Calendario (RF10)

- Pendiente de dise�o e implementaci�n completa

### Producci�n

Antes de desplegar se debe:

- Cambiar DEBUG = False
- Definir ALLOWED_HOSTS con el dominio real
- Migrar de SQLite a PostgreSQL/Supabase
- Cambiar CORS_ALLOWED_ORIGINS al dominio de producci�n
- Configurar HTTPS obligatorio
- Mover API_URL del frontend a variable de entorno (.env)
- Eliminar todos los console.log de debug
- Desplegar en red local del hotel o VPS privado con acceso
  restringido por IP para que solo el personal pueda acceder

### Optimizaciones Pendientes

- Implementar caché con sessionStorage en los servicios para evitar re-fetch de datos estáticos (como tipos de habitación) al navegar entre vistas.
- Refactorizar los componentes antiguos de Svelte 4 para estandarizar el uso de $props, $state y $derived en todo el proyecto.
- Conectar el Header con notificacionesApi.getAll() para mostrar alertas reales de stock bajo o reservas pendientes.
- Crear los archivos de servicio faltantes (huespedes.ts, reservaciones.ts, pagos.ts) siguiendo el nuevo patrón de apiFetch exportado.
- Ejecutar el flujo completo de notificaciones de WhatsApp una vez que el backend sea desplegado fuera de localhost.

---

## ?? Usuario del Sistema

| Rol           | Acceso                                                           |
| ------------- | ---------------------------------------------------------------- |
| admin         | Todo el sistema incluyendo configuraci�n y administraci�n        |
| recepcionista | Dashboard, habitaciones, hu�spedes, reservas, consumos, reportes |

Usuario de prueba: basquiatdev (rol: admin)
`
