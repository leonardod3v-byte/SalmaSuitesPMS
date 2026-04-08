### Gestión de Huéspedes (/huespedes)

**Servicio:** src/lib/services/huespedes.ts

**Componentes:**

- GuestTable.svelte: Lista optimizada con filtros por documento o nombre.
- GuestModal.svelte: Formulario para crear/editar con validación de tipos de documento (V, E, J, P).
- VIPToggle.svelte: Componente pequeño para cambiar el estado es_vip sin recargar la página.

---

### Reservaciones (/reservas)

**Servicio:** src/lib/services/reservaciones.ts

**Componentes:**

- BookingCalendar.svelte: Una vista visual (Grid) para ver la ocupación por fechas.
- CheckInForm.svelte: Formulario paso a paso para asignar habitación a un huésped.
- ConsumoSelector.svelte: Para añadir productos del inventario a la cuenta de la reserva.
- NoShowModal.svelte: Para registrar el motivo y generar el acta automática.

---

### Pagos y Caja (/pagos)

**Servicio:** src/lib/services/pagos.ts

**Componentes:**

- PaymentForm.svelte: Selector de métodos (Zelle, Efectivo, Pago Móvil) y registro de referencia.
- CierreCajaModal.svelte: Resumen del día por moneda y método antes de generar el PDF.
- HistorialPagos.svelte: Tabla con filtros de fecha y usuario (recepcionista).

---

### Inventario (/inventario)

Control de stock y alertas de reposición.

**Servicio:** src/lib/services/inventario.ts

**Componentes:**

- ProductCard.svelte: Visualización de stock con indicadores de color (Rojo si sin_stock).
- StockAdjustModal.svelte: Para registrar entradas de mercancía o ajustes manuales.
- InventoryAlerts.svelte: Widget para la parte superior que muestra productos bajo el mínimo.

---

### Reportes y Notificaciones (/reportes y /notificaciones)

**Servicios**: src/lib/services/reportes.ts y src/lib/services/notificaciones.ts

**Componentes:**

- ReportGenerator.svelte: Selector de tipo de reporte (Ingresos, Reservas) y rango de fechas.
- NotificationLog.svelte: Lista de mensajes enviados por WhatsApp/Email con su estado (Error/Enviado).
- WhatsAppTemplateEditor.svelte: (Solo Admin) Para editar los mensajes automáticos.

---

### Estructura de Stores

Hasta ahora tienes auth.ts. No satures el sistema con stores, pero podrías considerar:

- src/lib/stores/ui.ts: Para manejar si el Sidebar está abierto o cerrado en móvil de forma global.

- src/lib/stores/cart.ts: Si decides que el registro de consumos funcione como un "carrito de compras" antes de confirmar el cargo a la habitación.
