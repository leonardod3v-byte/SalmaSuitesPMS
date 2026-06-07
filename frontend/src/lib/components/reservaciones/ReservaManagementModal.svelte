<script lang="ts">
    import { reservacionesApi, type ReservaListItem, TIPOS_CLIENTE, type TipoCliente } from '$lib/services/reservaciones';
    import { pagosApi } from '$lib/services/pagos';
    import { apiFetch } from '$lib/services/api';
    import { toast } from '$lib/stores/toast';
    import ModalShell from '$lib/components/ModalShell.svelte';
    import Button from '$lib/components/Button.svelte';
    import Icon from '$lib/components/Icons.svelte';
    import InputHotel from '$lib/components/InputHotel.svelte';
    import CheckInForm from './CheckInForm.svelte';

    let { reserva = null, onclose, onsave }: {
        reserva?: ReservaListItem | null;
        onclose: () => void;
        onsave?: () => void;
    } = $props();

    let activeTab = $state<'detalle' | 'pagos' | 'consumos' | 'noshow'>('detalle');
    let detail = $state<any>(null);
    let loading = $state(true);
    let pagos = $state<any[]>([]);
    let consumos = $state<any[]>([]);
    let saldoPendiente = $state(0);
    let productos = $state<any[]>([]);

    let nuevoPago = $state({ monto: 0, metodo: 'efectivo', referencia: '' });
    let guardandoPago = $state(false);
    let motivoNoShow = $state('');
    let registrandoNoShow = $state(false);
    let errorNoShow = $state('');
    let lineasConsumo = $state<{ producto: any; cantidad: number; nota: string }[]>([]);
    let busquedaProducto = $state('');
    let cargandoProductos = $state(true);
    let guardandoConsumo = $state(false);

    async function loadDetail() {
        if (!reserva) return;
        loading = true;
        try {
        const detalle = await reservacionesApi.get(reserva.id);
        detail = detalle;
        pagos = detalle.pagos || [];
        consumos = detalle.consumos || [];
        saldoPendiente = parseFloat(detalle.saldo_pendiente || 0);
        } catch {
        toast.send('Error al cargar detalle', 'error');
        } finally {
        loading = false;
        }
    }

    async function loadProductos() {
        cargandoProductos = true;
        try {
        const prods = await apiFetch<any[]>('/inventario/?activo=true');
        productos = prods.filter(p => p.activo && p.stock_actual > 0);
        } catch {
        productos = [];
        } finally {
        cargandoProductos = false;
        }
    }

    $effect(() => {
        if (reserva) loadDetail();
        loadProductos();
    });

    async function refreshData() {
        if (reserva) await loadDetail();
    }

    async function registrarPago() {
        if (nuevoPago.monto <= 0) return toast.send('Monto inválido', 'error');
        if (nuevoPago.monto > saldoPendiente) return toast.send('El monto no puede superar el saldo pendiente', 'error');
        guardandoPago = true;
        try {
        await pagosApi.registrar({ reserva: reserva.id, monto: nuevoPago.monto, metodo: nuevoPago.metodo, referencia: nuevoPago.referencia });
        toast.send('Pago registrado', 'success');
        nuevoPago = { monto: 0, metodo: 'efectivo', referencia: '' };
        await refreshData();
        } catch {
        toast.send('Error al registrar pago', 'error');
        } finally {
        guardandoPago = false;
        }
    }

    async function registrarNoShow() {
        if (motivoNoShow.trim().length < 10) {
        errorNoShow = 'El motivo debe tener al menos 10 caracteres';
        return;
        }
        registrandoNoShow = true;
        try {
        await reservacionesApi.registrarNoShow(reserva.id, motivoNoShow);
        toast.send('No-Show registrado', 'success');
        onclose();
        } catch {
        toast.send('Error al registrar No-Show', 'error');
        } finally {
        registrandoNoShow = false;
        }
    }

    const productosFiltrados = $derived(productos.filter(p => !busquedaProducto || p.nombre.toLowerCase().includes(busquedaProducto.toLowerCase())));
    const porCategoria = $derived(productosFiltrados.reduce((acc, p) => { const cat = p.categoria || 'otro'; if (!acc[cat]) acc[cat] = []; acc[cat].push(p); return acc; }, {} as Record<string, any[]>));
    const totalCarrito = $derived(lineasConsumo.reduce((acc, l) => acc + l.cantidad * Number(l.producto.precio_venta), 0));

    function agregarLinea(producto: any) {
        const existe = lineasConsumo.find(l => l.producto.id === producto.id);
        if (existe) {
        lineasConsumo = lineasConsumo.map(l => l.producto.id === producto.id ? { ...l, cantidad: l.cantidad + 1 } : l);
        } else {
        lineasConsumo = [...lineasConsumo, { producto, cantidad: 1, nota: '' }];
        }
    }
    function quitarLinea(id: number) { lineasConsumo = lineasConsumo.filter(l => l.producto.id !== id); }

    async function confirmarConsumos() {
        if (lineasConsumo.length === 0) return;
        guardandoConsumo = true;
        try {
        await Promise.all(lineasConsumo.map(l => reservacionesApi.agregarConsumo(reserva.id, {
            producto: l.producto.nombre,
            cantidad: l.cantidad,
            precio_unitario: l.producto.precio_venta,
            noches_asociadas: 1,
            nota: l.nota
        })));
        toast.send('Consumos registrados', 'success');
        lineasConsumo = [];
        await refreshData();
        } catch {
        toast.send('Error al registrar consumos', 'error');
        } finally {
        guardandoConsumo = false;
        }
    }

    const formatDate = (d: string) => new Date(d).toLocaleDateString('es-VE', { day: '2-digit', month: 'short', year: 'numeric' });
    function handleSave() { if (onsave) onsave(); onclose(); }
</script>

{#if !reserva}
    <ModalShell title="Nuevo Check-In" subtitle="Registro rápido de huésped" maxWidth="max-w-3xl" onclose={onclose}>
        <CheckInForm onguardado={handleSave} oncancel={onclose} />
    </ModalShell>
    {:else}
    <ModalShell
        title={`Reserva #${reserva.id} · ${reserva.huesped_nombre.split(' ')[0]}`}
        subtitle={`Hab. ${reserva.habitacion_numero} · ${formatDate(reserva.fecha_entrada)} → ${formatDate(reserva.fecha_salida)}`}
        maxWidth="max-w-4xl"
        onclose={onclose}
    >
        {#if loading}
        <div class="flex justify-center py-16"><div class="w-10 h-10 border-3 border-hotel-gold border-t-transparent rounded-full animate-spin"></div></div>
        {:else if detail}
        <div class="space-y-2 max-h-48 overflow-y-auto">
            <!-- Pestañas -->
            <div class="border-b border-hotel-border">
            <div class="flex gap-1">
                <button onclick={() => activeTab = 'detalle'} class="flex items-center gap-2 px-5 py-3 text-[11px] font-black uppercase tracking-wider rounded-t-lg {activeTab === 'detalle' ? 'bg-hotel-gold/10 text-hotel-gold border-b-2 border-hotel-gold' : 'text-hotel-text-tertiary hover:text-hotel-text-secondary'}">
                <Icon name="list" class="w-4 h-4" /> Detalles
                </button>
                <button onclick={() => activeTab = 'pagos'} class="flex items-center gap-2 px-5 py-3 ..."><Icon name="credit-card" class="w-4 h-4" /> Pagos</button>
                <button onclick={() => activeTab = 'consumos'} class="flex items-center gap-2 px-5 py-3 ..."><Icon name="shopping-cart" class="w-4 h-4" /> Consumos</button>
                <button onclick={() => activeTab = 'noshow'} class="flex items-center gap-2 px-5 py-3 ..."><Icon name="x-circle" class="w-4 h-4" /> No-Show</button>
            </div>
            </div>

            {#if activeTab === 'detalle'}
            <div class="space-y-6">
                <!-- Tarjetas de resumen -->
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="bg-linear-to-br from-hotel-surface to-hotel-bg/50 rounded-2xl border border-hotel-border p-5">
                    <p class="text-[9px] font-black uppercase tracking-wider text-hotel-text-tertiary">Saldo Pendiente</p>
                    <p class="text-3xl font-display font-black text-hotel-gold mt-2">${saldoPendiente.toFixed(2)}</p>
                </div>
                <div class="bg-linear-to-br from-hotel-surface to-hotel-bg/50 rounded-2xl border border-hotel-border p-5">
                    <p class="text-[9px] font-black uppercase tracking-wider text-hotel-text-tertiary">Modalidad</p>
                    <p class="text-xl font-bold text-hotel-text-primary mt-2">{detail.modalidad_pago?.toUpperCase() ?? 'CONTADO'}</p>
                </div>
                <div class="bg-linear-to-br from-hotel-surface to-hotel-bg/50 rounded-2xl border border-hotel-border p-5">
                    <p class="text-[9px] font-black uppercase tracking-wider text-hotel-text-tertiary">Profesión</p>
                    <p class="text-xl font-bold text-hotel-text-primary mt-2">{detail.huesped_data?.profesion || 'No especificada'}</p>
                </div>
                <div class="bg-linear-to-br from-hotel-surface to-hotel-bg/50 rounded-2xl border border-hotel-border p-5">
                    <p class="text-[9px] font-black uppercase tracking-wider text-hotel-text-tertiary">Factura</p>
                    <p class="text-xl font-bold text-hotel-text-primary mt-2">{detail.requiere_factura ? 'Sí' : 'No'}</p>
                </div>
                </div>

                <!-- Datos del huésped -->
                <div class="bg-hotel-surface/40 rounded-2xl border border-hotel-border p-6">
                <h3 class="text-sm font-bold uppercase tracking-wider mb-4 flex items-center gap-2">
                    <Icon name="user" class="w-4 h-4" /> Datos del Huésped
                </h3>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                    <div><span class="text-hotel-text-tertiary">Nombre completo:</span> <span class="font-bold">{detail.huesped_data?.nombre_completo}</span></div>
                    <div><span class="text-hotel-text-tertiary">Documento:</span> <span class="font-mono">{detail.huesped_data?.documento_formateado}</span></div>
                    <div><span class="text-hotel-text-tertiary">Teléfono:</span> {detail.huesped_data?.telefono || '—'}</div>
                    <div><span class="text-hotel-text-tertiary">Email:</span> {detail.huesped_data?.email || '—'}</div>
                    <div><span class="text-hotel-text-tertiary">Procedencia:</span> {detail.huesped_data?.procedencia || '—'}</div>
                    <div><span class="text-hotel-text-tertiary">Profesión:</span> {detail.huesped_data?.profesion || '—'}</div>
                </div>
                </div>

                <!-- Estancia -->
                <div class="bg-hotel-surface/40 rounded-2xl border border-hotel-border p-6">
                <h3 class="text-sm font-bold uppercase tracking-wider mb-4 flex items-center gap-2">
                    <Icon name="calendar" class="w-4 h-4" /> Estancia
                </h3>
                <div class="flex flex-wrap justify-between gap-4">
                    <div><span class="text-hotel-text-tertiary">Check-in:</span> <span class="font-bold">{formatDate(detail.fecha_entrada)}</span></div>
                    <div><span class="text-hotel-text-tertiary">Check-out:</span> <span class="font-bold">{formatDate(detail.fecha_salida)}</span></div>
                    <div><span class="text-hotel-text-tertiary">Noches:</span> <span class="font-bold">{detail.noches}</span></div>
                    <div><span class="text-hotel-text-tertiary">Monto total:</span> <span class="font-bold text-hotel-gold">${detail.monto_total}</span></div>
                </div>
                </div>
            </div>
            {:else if activeTab === 'pagos'}
            <div class="space-y-6">
                <div class="bg-hotel-surface/40 rounded-2xl border p-5 flex justify-between items-center">
                <span class="text-sm font-bold uppercase">Saldo pendiente</span>
                <span class="text-2xl font-display font-black text-hotel-gold">${saldoPendiente.toFixed(2)}</span>
                </div>
                <div>
                <h4 class="text-xs font-bold uppercase mb-3 flex items-center gap-2"><Icon name="credit-card" class="w-4 h-4" /> Pagos realizados</h4>
                {#if pagos.length === 0}
                    <div class="text-center py-6 bg-hotel-bg/20 rounded-xl border border-dashed">
                    <Icon name="credit-card" class="w-8 h-8 mx-auto mb-2 opacity-30" />
                    <p class="text-xs">No hay pagos registrados</p>
                    </div>
                {:else}
                    <div class="space-y-2">
                    {#each pagos as p}
                        <div class="flex justify-between items-center p-3 bg-hotel-bg/30 rounded-xl border border-hotel-border/50">
                        <div><span class="text-sm font-bold">{p.metodo.toUpperCase()}</span><p class="text-[10px] text-hotel-text-tertiary">Ref: {p.referencia || 'N/A'} · {new Date(p.fecha).toLocaleString()}</p></div>
                        <span class="text-sm font-mono font-black text-hotel-gold">${p.monto}</span>
                        </div>
                    {/each}
                    </div>
                {/if}
                </div>
                {#if saldoPendiente > 0}
                <div class="bg-hotel-surface/40 rounded-2xl border p-5 space-y-4">
                    <h4 class="text-xs font-bold uppercase">Registrar nuevo pago</h4>
                    <div class="grid grid-cols-2 gap-4">
                    <InputHotel label="Monto a pagar ($)" type="number" bind:value={nuevoPago.monto} />
                    <div>
                        <!-- svelte-ignore a11y_label_has_associated_control -->
                        <label class="text-[10px] font-black uppercase tracking-widest">Método</label>
                        <div class="grid grid-cols-3 gap-2 mt-1">
                        <button onclick={() => nuevoPago.metodo = 'efectivo'} class="p-2 rounded-xl border {nuevoPago.metodo === 'efectivo' ? 'border-hotel-gold bg-hotel-gold/10' : 'border-hotel-border'} text-xs">Efectivo</button>
                        <button onclick={() => nuevoPago.metodo = 'tarjeta'} class="p-2 rounded-xl border {nuevoPago.metodo === 'tarjeta' ? 'border-hotel-gold bg-hotel-gold/10' : 'border-hotel-border'} text-xs">Tarjeta</button>
                        <button onclick={() => nuevoPago.metodo = 'pago_movil'} class="p-2 rounded-xl border {nuevoPago.metodo === 'pago_movil' ? 'border-hotel-gold bg-hotel-gold/10' : 'border-hotel-border'} text-xs">Pago Móvil</button>
                        </div>
                    </div>
                    </div>
                    <InputHotel label="Referencia (opcional)" placeholder="Nº de operación" bind:value={nuevoPago.referencia} />
                    <Button variant="gold" fullWidth onclick={registrarPago} disabled={guardandoPago}>
                    {guardandoPago ? 'Procesando...' : 'Registrar Pago'}
                    </Button>
                </div>
                {/if}
            </div>
            {:else if activeTab === 'consumos'}
            <div class="space-y-6">
                <div>
                <h4 class="text-xs font-bold uppercase mb-3 flex items-center gap-2"><Icon name="shopping-cart" class="w-4 h-4" /> Consumos realizados</h4>
                {#if consumos.length === 0}
                    <div class="text-center py-6 bg-hotel-bg/20 rounded-xl border border-dashed">
                    <Icon name="shopping-cart" class="w-8 h-8 mx-auto mb-2 opacity-30" />
                    <p class="text-xs">No hay consumos registrados</p>
                    </div>
                {:else}
                    <div class="space-y-2">
                    {#each consumos as c}
                        <div class="flex justify-between items-center p-3 bg-hotel-bg/30 rounded-xl border border-hotel-border/50">
                        <div><span class="text-sm font-bold">{c.producto}</span><p class="text-[10px] text-hotel-text-tertiary">x{c.cantidad} · {new Date(c.fecha_consumo).toLocaleString()}</p></div>
                        <span class="text-sm font-mono font-black text-hotel-gold">${c.total}</span>
                        </div>
                    {/each}
                    </div>
                {/if}
                </div>

                <div class="bg-hotel-surface/40 rounded-2xl border p-5 space-y-4">
                <h4 class="text-xs font-bold uppercase">Añadir consumos</h4>
                <div class="relative">
                    <Icon name="search" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-hotel-text-tertiary" />
                    <input type="text" bind:value={busquedaProducto} placeholder="Buscar producto..." class="w-full bg-hotel-bg border border-hotel-border rounded-xl py-2 pl-10 pr-4 text-sm focus:border-hotel-gold outline-none" />
                </div>
                {#if cargandoProductos}
                    <div class="flex justify-center py-8"><div class="w-8 h-8 border-2 border-hotel-gold border-t-transparent rounded-full animate-spin"></div></div>
                {:else if Object.keys(porCategoria).length === 0}
                    <div class="text-center py-8"><p class="text-sm text-hotel-text-tertiary">No hay productos disponibles</p></div>
                {:else}
                    <div class="space-y-4 max-h-64 overflow-y-auto">
                    {#each Object.entries(porCategoria) as [cat, prods]}
                        <div>
                        <h5 class="text-[10px] font-black uppercase tracking-widest text-hotel-gold mb-2">{cat}</h5>
                        <div class="grid grid-cols-2 gap-2">
                            {#each prods as p}
                            <button onclick={() => agregarLinea(p)} class="flex justify-between items-center p-2 rounded-xl border border-hotel-border hover:border-hotel-gold/50 transition-all">
                                <span class="text-xs font-bold truncate">{p.nombre}</span>
                                <span class="text-[10px] font-mono text-hotel-gold">${p.precio_venta}</span>
                            </button>
                            {/each}
                        </div>
                        </div>
                    {/each}
                    </div>
                {/if}
                </div>

                {#if lineasConsumo.length > 0}
                <div class="bg-hotel-surface/40 rounded-2xl border p-5 space-y-4">
                    <div class="flex justify-between items-center">
                    <h4 class="text-xs font-bold uppercase">Carrito ({lineasConsumo.length})</h4>
                    <span class="text-lg font-black text-hotel-gold">${totalCarrito.toFixed(2)}</span>
                    </div>
                    <div class="space-y-2 max-h-48 overflow-y-auto">
                    {#each lineasConsumo as l}
                        <div class="flex justify-between items-center p-2 bg-hotel-bg/30 rounded-lg">
                        <div class="flex items-center gap-2">
                            <button onclick={() => { l.cantidad = Math.max(1, l.cantidad - 1); }} class="w-6 h-6 rounded bg-hotel-surface text-hotel-text-tertiary hover:text-hotel-gold">−</button>
                            <span class="text-sm font-bold w-6 text-center">{l.cantidad}</span>
                            <button onclick={() => l.cantidad++} class="w-6 h-6 rounded bg-hotel-surface text-hotel-text-tertiary hover:text-hotel-gold">+</button>
                            <span class="text-xs">{l.producto.nombre}</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <span class="text-xs font-mono">${(l.cantidad * Number(l.producto.precio_venta)).toFixed(2)}</span>
                            <button onclick={() => quitarLinea(l.producto.id)} class="text-hotel-error-light hover:opacity-70"><Icon name="close" class="w-3 h-3" /></button>
                        </div>
                        </div>
                    {/each}
                    </div>
                    <Button variant="gold" fullWidth onclick={confirmarConsumos} disabled={guardandoConsumo}>
                    {guardandoConsumo ? 'Procesando...' : 'Confirmar Consumos'}
                    </Button>
                </div>
                {/if}
            </div>
            {:else if activeTab === 'noshow'}
            <div class="space-y-6">
                <div class="relative bg-hotel-bg p-6 rounded-2xl border border-hotel-border/60 shadow-inner">
                <div class="absolute top-0 right-8 w-12 h-4 bg-hotel-surface border border-hotel-border border-t-0 rounded-b-xl opacity-20"></div>
                <header class="mb-4 flex justify-between items-start">
                    <span class="text-[8px] font-black uppercase tracking-[0.4em] text-hotel-text-tertiary">Documento Digital</span>
                    <span class="text-[10px] font-mono text-hotel-gold">ID-{reserva.id}</span>
                </header>
                <div class="space-y-3 font-mono text-[10px] leading-relaxed">
                    <div class="flex justify-between border-b border-hotel-border/30 pb-1"><span class="text-hotel-text-tertiary uppercase">Hotel</span><span class="text-hotel-text-primary font-bold">SALMA SUITE VIP</span></div>
                    <div class="flex justify-between border-b border-hotel-border/30 pb-1"><span class="text-hotel-text-tertiary uppercase">Fecha Emisión</span><span class="text-hotel-text-primary uppercase">{new Date().toLocaleDateString('es-VE', { day: '2-digit', month: 'long', year: 'numeric' })}</span></div>
                    <div class="flex justify-between border-b border-hotel-border/30 pb-1"><span class="text-hotel-text-tertiary uppercase">Huésped Titular</span><span class="text-hotel-text-primary font-bold">{detail.huesped_data?.nombre_completo}</span></div>
                    <div class="flex justify-between border-b border-hotel-border/30 pb-1"><span class="text-hotel-text-tertiary uppercase">Unidad Asignada</span><span class="text-hotel-text-primary">HABITACIÓN #{reserva.habitacion_numero}</span></div>
                    <div class="mt-4 pt-2"><p class="text-hotel-text-tertiary uppercase mb-2">Declaratoria de Motivo:</p><p class="text-hotel-text-primary italic whitespace-pre-wrap min-h-[40px] border-l-2 border-hotel-gold/30 pl-3">{motivoNoShow || 'Esperando entrada de datos...'}</p></div>
                </div>
                </div>
                <div class="space-y-3">
                <!-- svelte-ignore a11y_label_has_associated_control -->
                <label class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-text-secondary">Justificación del Incumplimiento</label>
                <textarea bind:value={motivoNoShow} rows="3" placeholder="Ej: El huésped no respondió a las llamadas de confirmación tras 4 horas de retraso..." class="w-full rounded-xl px-5 py-4 text-xs bg-hotel-bg text-hotel-text-primary border-2 border-hotel-border focus:border-hotel-gold/50 outline-none resize-none"></textarea>
                {#if errorNoShow}<p class="text-[9px] font-bold text-hotel-error-light uppercase tracking-widest animate-pulse">{errorNoShow}</p>{/if}
                </div>
                <div class="flex justify-end gap-3">
                <Button variant="ghost" onclick={() => activeTab = 'detalle'}>Cancelar</Button>
                <Button variant="danger" onclick={registrarNoShow} disabled={registrandoNoShow}>{registrandoNoShow ? 'Registrando...' : 'Registrar No-Show'}</Button>
                </div>
            </div>
            {/if}
        </div>
        {/if}
    </ModalShell>
{/if}