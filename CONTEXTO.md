# 🏨 PMS Hotel Salma Suite VIP

Sistema de gestión hotelera (PMS) para uso interno del Hotel Salma Suites VIP.  
Permite gestionar habitaciones, huéspedes, reservas, consumos, pagos, inventario y reportes.

---

## 🛠️ Stack

| Frontend            | Backend                | BD           | Servicios            |
| ------------------- | ---------------------- | ------------ | -------------------- |
| SvelteKit 5 (Runes) | Django 6.0.3           | SQLite (dev) | Gmail SMTP           |
| TailwindCSS v4      | DRF 3.x                | PostgreSQL   | Twilio WhatsApp      |
| Plus Jakarta Sans   | JWT + HttpOnly cookies | (prod)       | ReportLab / openpyxl |
| Playfair Display    | django-cors-headers    |              |                      |

Hardware objetivo: Celeron 1.46GHz, 4GB RAM → optimizado para bajos recursos.

---

## 🎨 Paleta

- Fondo: `#1A0F0A`
- Cards: `#2D1B14`
- Dorado: `#B38E5D`
- Éxito: `#2D6A4F`
- Error: `#9B2226`
- VIP: `#582F7E`

Tipografías: Playfair Display (títulos) + Plus Jakarta Sans (UI).

---

## 🔐 Autenticación (HttpOnly Cookie + SSR)

- Token JWT almacenado en cookie **HttpOnly** (inaccesible para JS).
- `hooks.server.ts` valida token contra Django con caché en memoria (5 min).
- `apiFetch` usa `credentials: 'include'`.
- Rutas protegidas usan `+page.server.ts` → SSR sin `onMount`.
- Recuperación de contraseña con caché de Django (`django.core.cache`) y verificación en 3 pasos.

---

## 📁 Estructura clave (frontend)

SalmaSuitesPMS/
├── backend/
│ ├── apps/
│ │ ├── users/
│ │ │ ├── authentication.py # CookieTokenAuthentication + CsrfExemptSessionAuthentication
│ │ │ ├── models.py
│ │ │ ├── serializers.py
│ │ │ ├── views.py # login/logout con HttpOnly cookie + reset por caché
│ │ │ └── urls.py
│ │ ├── habitaciones/
│ │ ├── guests/
│ │ ├── reservaciones/
│ │ │ ├── models.py # Incluye campo tipo_cliente
│ │ │ ├── serializers.py # tipo_cliente en ReservaListSerializer
│ │ │ ├── views.py
│ │ │ └── urls.py
│ │ ├── pagos/
│ │ ├── inventario/
│ │ ├── dashboard/
│ │ ├── reportes/
│ │ └── notificaciones/
│ ├── config/
│ │ ├── settings.py # CACHES, CookieTokenAuthentication, cookie settings
│ │ ├── urls.py
│ │ ├── wsgi.py
│ │ └── asgi.py
│ ├── database/db.sqlite3
│ ├── seed.py
│ ├── .env
│ └── manage.py
├── frontend/
│ └── src/
│ ├── app.css
│ ├── app.d.ts # Locals.user tipado completo
│ ├── app.html
│ ├── hooks.server.ts # Validación de cookie + caché de usuario en memoria
│ └── lib/
│ ├── components/
│ │ ├── habitaciones/
│ │ │ ├── RoomCard.svelte
│ │ │ └── RoomModal.svelte
│ │ ├── huespedes/
│ │ │ ├── GuestTable.svelte
│ │ │ ├── GuestModal.svelte
│ │ │ └── VIPToggle.svelte
│ │ ├── reservaciones/
│ │ │ ├── BookingCalendar.svelte
│ │ │ ├── CheckInForm.svelte
│ │ │ ├── ConsumoSelector.svelte
│ │ │ └── NoShowModal.svelte
│ │ ├── ButtonGold.svelte
│ │ ├── CardHotel.svelte
│ │ ├── Header.svelte
│ │ ├── Icons.svelte
│ │ ├── InputHotel.svelte
│ │ ├── KPICard.svelte
│ │ ├── Loading.svelte
│ │ ├── Sidebar.svelte
│ │ ├── Skeleton.svelte
│ │ ├── Toast.svelte
│ │ └── WelcomeBanner.svelte
│ ├── services/
│ │ ├── api.ts # apiFetch con credentials: 'include'
│ │ ├── dashboard.ts
│ │ ├── habitaciones.ts
│ │ ├── huespedes.ts # NUEVO
│ │ └── reservaciones.ts # NUEVO — incluye TIPOS_CLIENTE con colores
│ ├── stores/
│ │ ├── auth.ts # Sin localStorage — hidratado desde SSR
│ │ └── toast.ts
│ └── index.ts
│ └── routes/
│ ├── +layout.svelte # Hidrata auth store desde data.user SSR
│ ├── +layout.server.ts # NUEVO — expone locals.user a todas las rutas
│ ├── +page.svelte # Redirección a /login
│ ├── login/
│ │ └── +page.svelte
│ ├── recuperar/
│ │ └── +page.svelte
│ ├── dashboard/
│ │ ├── +page.svelte # Datos via $props desde servidor
│ │ └── +page.server.ts # NUEVO — SSR con Promise.allSettled
│ ├── habitaciones/
│ │ ├── +page.svelte # SSR + invalidateAll() para RoomModal
│ │ └── +page.server.ts # NUEVO
│ ├── huespedes/
│ │ ├── +page.svelte # NUEVO — tabla + filtros + VIP toggle optimista
│ │ └── +page.server.ts # NUEVO — filtros search/vip en URL
│ └── reservaciones/
│ ├── +page.svelte # NUEVO — BookingCalendar estilo papel
│ └── +page.server.ts # NUEVO — navegación semanal por URL
├── package.json # Scripts raíz con concurrently
└── package-lock.json

---

## ✅ Principales features completadas

- Login/logout con cookie HttpOnly y SSR
- Dashboard con KPIs, ocupación semanal, mapa de habitaciones, timeline de actividad
- CRUD habitaciones (estados: libre, limpia, sucia, ocupada, mantenimiento)
- CRUD huéspedes (documento V/E/J/G/P, acompañantes, VIP toggle optimista)
- Gestión de reservas (check-in wizard, calendario visual tipo papel, 10 tipos de cliente)
- Registro de consumos (catálogo de productos + carrito)
- Acta No‑Show (irreversible, con vista previa)
- Registro de pagos y abonos
- Notificaciones básicas (toast)
- Prefetch de enlaces (`data-sveltekit-prefetch`) para navegación instantánea

---

## ⚙️ Decisiones técnicas clave (actualizadas)

- **SSR obligatorio**: nunca `onMount` para cargar datos iniciales → usar `+page.server.ts` + `$derived`.
- **Mutaciones**: `invalidateAll()` para recargar datos tras crear/editar/borrar.
- **Optimismo**: solo para toggles (ej. VIP).
- **Componentes refactorizados** (Svelte 5 Runes):
  - `Button`: variantes `gold`, `danger`, `success`, `secondary`.
  - `Icon`: un solo componente con mapa de strings SVG.
  - `InputHotel`: `bind:value`, `error`, `label`, soporta `number`.
  - `KPICard`: desacoplado del dashboard, recibe `iconName`.
  - `ModalShell`, `PageHeader`, `Toast`, `Skeleton` estandarizados.
- **Caché**: `django.core.cache` para códigos de recuperación; caché en memoria (Node) para validación de token.
- **Prefetch**: `data-sveltekit-prefetch` en todos los enlaces de `Sidebar` y `Header`.

---

## 🚧 Pendientes inmediatos

- Módulo `/inventario` (frontend)
- Módulo `/pagos` + cierre de caja PDF
- QR por habitación (frontend)
- Exportar Excel (endpoint Django listo, falta handler en frontend)
- Despliegue: PostgreSQL, Redis (caché), HTTPS, variables de entorno.

---

## 👤 Usuarios

- **admin** (leonardodev): acceso total
- **recepcionista**: dashboard, habitaciones, huéspedes, reservas, consumos, reportes
