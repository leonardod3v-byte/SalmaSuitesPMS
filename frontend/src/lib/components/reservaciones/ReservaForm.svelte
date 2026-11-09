<script lang="ts">
    import { onMount } from 'svelte';
    import { toast } from '$lib/stores/toast';
    import InputHotel from '$components/ui/Input.svelte';
    import Select from '$components/ui/Select.svelte';
    import DatePicker from '$components/ui/DatePicker.svelte';
    import Button from '$components/ui/Button.svelte';
    import Modal from '$components/ui/Modal.svelte';
    import Icon from '$components/ui/Icons.svelte';
    import NuevoHuespedRapido from './NuevoHuespedRapido.svelte';
    import { createReservacion } from '$lib/services/reservaciones';
    import { fetchHuespedes, checkDisponibilidad } from '$lib/services/huespedes';
    import { fetchEmpresas } from '$lib/services/empresas';
    import { fetchDisponibles } from '$lib/services/habitaciones';
    import { fetchOcupaciones, type Ocupacion } from '$lib/services/ocupaciones';
    import type { Huesped } from '$lib/types/huesped';
    import type { Habitacion } from '$lib/types/habitacion';
    import type { Empresa } from '$lib/types/empresa';

    let {
        onclose = () => {},
        habitacionPreseleccionada = null,
    }: {
        onclose?: () => void;
        habitacionPreseleccionada?: number | null;
    } = $props();

    let paso = $state(1);
    let loading = $state(false);
    let error = $state('');

    let esEmpresa = $state(false);
    let empresaSeleccionada = $state<Empresa | null>(null);
    let empresas = $state<Empresa[]>([]);

    let busquedaHuesped = $state('');
    let huespedes = $state<Huesped[]>([]);
    let titularSeleccionado = $state<Huesped | null>(null);
    let mostrarDropdownTitular = $state(false);

    let busquedaAcompanante = $state('');
    let huespedesAcompanantes = $state<Huesped[]>([]);
    let acompanantes = $state<Huesped[]>([]);
    let mostrarDropdownAcompanante = $state(false);

    let mostrarFormNuevoAcompanante = $state(false);
    let ocupaciones = $state<Ocupacion[]>([]);

    let habitaciones = $state<Habitacion[]>([]);
    let habitacionSeleccionada = $state<Habitacion | null>(null);
    let filtroTipoHabitacion = $state('');

    let totalPersonas = $derived(1 + acompanantes.length);

    let habitacionesDisponibles = $derived(
        habitaciones.filter(h => h.capacidad_maxima >= totalPersonas)
    );

    let tiposHabitacionDisponibles = $derived(
        [...new Set(habitacionesDisponibles.map(h => h.categoria_tipo || 'Sin categoría'))].sort()
    );

    let habitacionesFiltradas = $derived(
        filtroTipoHabitacion
            ? habitacionesDisponibles.filter(h => (h.categoria_tipo || 'Sin categoría') === filtroTipoHabitacion)
            : habitacionesDisponibles
    );

    let fechaEntrada = $state(new Date().toISOString().split('T')[0]);
    let fechaSalida = $state(new Date(Date.now() + 86400000).toISOString().split('T')[0]);

    let modalidadPago = $state<'Contado' | 'Abono' | 'Crédito'>('Contado');
    let metodoPago = $state<'Efectivo' | 'Tarjeta' | 'PagoMovil'>('Efectivo');
    let numeroReferencia = $state('');
    let montoAbonado = $state<number>(0);
    let requiereFactura = $state(false);

    let noches = $derived(Math.max(0, (new Date(fechaSalida).getTime() - new Date(fechaEntrada).getTime()) / 86400000));
    let precioBase = $derived(
        (esEmpresa && habitacionSeleccionada?.precio_empresa)
            ? parseFloat(habitacionSeleccionada.precio_empresa)
            : parseFloat(habitacionSeleccionada?.precio_por_noche || '0')
    );
    let totalHabitacion = $derived(noches * precioBase);

    async function buscarHuespedes() {
        if (busquedaHuesped.length < 2) { huespedes = []; mostrarDropdownTitular = false; return; }
        try {
            huespedes = await fetchHuespedes(`search=${busquedaHuesped}`);
            mostrarDropdownTitular = huespedes.length > 0;
        } catch { }
    }

    async function buscarAcompanantes() {
        if (busquedaAcompanante.length < 2) { huespedesAcompanantes = []; mostrarDropdownAcompanante = false; return; }
        try {
            huespedesAcompanantes = await fetchHuespedes(`search=${busquedaAcompanante}`);
            mostrarDropdownAcompanante = huespedesAcompanantes.length > 0;
        } catch { }
    }

    function seleccionarTitular(h: Huesped) {
        titularSeleccionado = h;
        mostrarDropdownTitular = false;
        busquedaHuesped = '';
    }

    function seleccionarAcompanante(h: Huesped) {
        if (h.id === titularSeleccionado?.id) {
            toast.error('El titular no puede ser acompañante.');
            return;
        }
        if (acompanantes.find(a => a.id === h.id)) {
            toast.error('Ese huésped ya está agregado.');
            return;
        }
        acompanantes = [...acompanantes, h];
        mostrarDropdownAcompanante = false;
        busquedaAcompanante = '';

        if (habitacionSeleccionada && habitacionSeleccionada.capacidad_maxima < (1 + acompanantes.length)) {
            habitacionSeleccionada = null;
        }
    }

    async function cargarHabitaciones() {
        try {
            habitaciones = await fetchDisponibles();
            if (habitacionPreseleccionada) {
                habitacionSeleccionada = habitaciones.find(h => h.id === habitacionPreseleccionada) || null;
            }
        } catch { }
    }

    onMount(async () => {
        cargarHabitaciones();
        try { empresas = await fetchEmpresas(); } catch { }
        try { ocupaciones = await fetchOcupaciones(); } catch { }
    });

    function seleccionarEmpresa(e: Event) {
        const id = Number((e.target as HTMLSelectElement).value);
        empresaSeleccionada = empresas.find(emp => emp.id === id) || null;
    }

    function onNuevoAcompananteCreado(nuevo: Huesped) {
        acompanantes = [...acompanantes, nuevo];
        mostrarFormNuevoAcompanante = false;
        toast.success(`${nuevo.nombres} agregado como acompañante.`);

        if (habitacionSeleccionada && habitacionSeleccionada.capacidad_maxima < (1 + acompanantes.length)) {
            habitacionSeleccionada = null;
        }
    }

    async function siguientePaso() {
        error = '';
        if (paso === 1 && !titularSeleccionado) { error = 'Selecciona un huésped titular.'; return; }
        if (paso === 2) {
            for (const a of acompanantes) {
                try {
                    const d = await checkDisponibilidad(a.id);
                    if (!d.disponible) { error = `El huésped ${a.nombres} ya tiene estancia activa.`; return; }
                } catch { }
            }
        }
        if (paso === 3 && !habitacionSeleccionada) { error = 'Selecciona una habitación.'; return; }
        if (paso === 4 && noches <= 0) { error = 'La fecha de salida debe ser posterior a la de entrada.'; return; }
        paso++;
    }

    async function confirmarReserva() {
        loading = true;
        error = '';
        try {
            const payload = {
                id_huesped_titular: titularSeleccionado!.id,
                id_empresa: esEmpresa && empresaSeleccionada ? empresaSeleccionada.id : null,
                id_habitacion: habitacionSeleccionada!.id,
                fecha_entrada: fechaEntrada,
                fecha_salida: fechaSalida,
                modalidad_pago: modalidadPago,
                requiere_factura: requiereFactura,
                acompanantes: acompanantes.map(a => a.id),
                metodo_pago_inicial: modalidadPago !== 'Crédito' ? metodoPago : null,
                numero_referencia_inicial: numeroReferencia,
                monto_abonado: modalidadPago === 'Abono' ? montoAbonado : 0,
            };
            await createReservacion(payload);
            toast.success('Reservación creada correctamente.');
            onclose();
        } catch (e: any) {
            error = e.message || 'Error al crear reservación';
        } finally {
            loading = false;
        }
    }
</script>

<form onsubmit={(e) => { e.preventDefault(); paso < 5 ? siguientePaso() : confirmarReserva(); }} class="space-y-6">
    {#if error}
        <div class="flex items-center gap-2 p-3 rounded-xl bg-hotel-error/10 border border-hotel-error/20 text-hotel-error-light text-sm">
            <Icon name="alert" class="w-4 h-4 shrink-0" />
            {error}
        </div>
    {/if}

    <div class="flex gap-2">
        {#each [1, 2, 3, 4, 5] as p}
            <div class="flex-1 h-1 rounded-full transition-all {p <= paso ? 'bg-hotel-gold' : 'bg-hotel-border'}"></div>
        {/each}
    </div>

    <!-- PASO 1 -->
    {#if paso === 1}
        <div class="p-5 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
            <p class="text-[10px] font-black uppercase tracking-wider text-hotel-gold">Paso 1 — ¿A nombre de quién es la reserva?</p>

            <div class="flex gap-4 mb-4">
                <label class="flex items-center gap-2 cursor-pointer">
                    <input type="radio" bind:group={esEmpresa} value={false} class="text-hotel-gold focus:ring-hotel-gold" />
                    <span class="text-sm text-hotel-text-primary">Persona Natural</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer">
                    <input type="radio" bind:group={esEmpresa} value={true} class="text-hotel-gold focus:ring-hotel-gold" />
                    <span class="text-sm text-hotel-text-primary">Empresa / Corporativo</span>
                </label>
            </div>

            {#if esEmpresa}
                <div class="mb-4 p-3 rounded-xl bg-hotel-vip/5 border border-hotel-vip/20">
                    <p class="text-[10px] text-hotel-vip-light uppercase mb-2 font-bold">Facturar a la empresa:</p>
                    <Select
                        options={[{value: '', label: 'Seleccione empresa...'}, ...empresas.map(e => ({value: String(e.id), label: `${e.nombre} (${e.rif})`}))]}
                        value={String(empresaSeleccionada?.id || '')}
                        onchange={seleccionarEmpresa}
                    />
                </div>
            {/if}

            <div class="border-t border-hotel-border/50 pt-4 relative">
                <p class="text-[10px] font-black uppercase tracking-wider text-hotel-gold mb-2">Huésped Titular</p>
                <InputHotel
                    placeholder="Buscar por nombre o documento..."
                    bind:value={busquedaHuesped}
                    oninput={() => { buscarHuespedes(); mostrarDropdownTitular = true; }}
                />
                {#if mostrarDropdownTitular && huespedes.length > 0}
                    <div class="absolute z-10 w-full mt-1 bg-hotel-surface border border-hotel-border rounded-lg shadow-xl max-h-40 overflow-y-auto custom-scrollbar">
                        {#each huespedes as h}
                            <button type="button" onclick={() => seleccionarTitular(h)} class="w-full text-left p-2 hover:bg-hotel-gold/10 transition-colors border-b border-hotel-border/50 last:border-0">
                                <p class="text-sm font-bold text-hotel-text-primary">{h.nombres} {h.apellidos}</p>
                                <p class="text-[10px] text-hotel-text-tertiary">{h.tipo_documento}-{h.numero_documento}</p>
                            </button>
                        {/each}
                    </div>
                {/if}
                {#if titularSeleccionado}
                    <div class="p-2 mt-2 rounded-lg bg-hotel-gold/10 text-sm font-bold text-hotel-gold flex items-center justify-between gap-2">
                        <div class="flex items-center gap-2">
                            <Icon name="check" class="w-4 h-4" />
                            Titular: {titularSeleccionado.nombres} {titularSeleccionado.apellidos}
                        </div>
                        <button type="button" onclick={() => titularSeleccionado = null} class="text-[10px] text-hotel-error-light hover:underline">Cambiar</button>
                    </div>
                {/if}
            </div>
        </div>
    {/if}

    <!-- PASO 2 -->
    {#if paso === 2}
        <div class="p-5 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
            <div class="flex items-center justify-between">
                <p class="text-[10px] font-black uppercase tracking-wider text-hotel-gold">Paso 2 — Acompañantes (opcional)</p>
                <p class="text-xs text-hotel-text-secondary">Total personas: <b class="text-hotel-gold">{totalPersonas}</b></p>
            </div>

            <div class="flex gap-2">
                <div class="flex-1 relative">
                    <InputHotel
                        placeholder="Buscar huésped existente..."
                        bind:value={busquedaAcompanante}
                        oninput={() => { buscarAcompanantes(); mostrarDropdownAcompanante = true; }}
                    />
                    {#if mostrarDropdownAcompanante && huespedesAcompanantes.length > 0}
                        <div class="absolute z-10 w-full mt-1 bg-hotel-surface border border-hotel-border rounded-lg shadow-xl max-h-36 overflow-y-auto custom-scrollbar">
                            {#each huespedesAcompanantes as h}
                                {#if h.id !== titularSeleccionado?.id && !acompanantes.find(a => a.id === h.id)}
                                    <button type="button" onclick={() => seleccionarAcompanante(h)} class="w-full text-left p-2 hover:bg-hotel-gold/10 transition-colors border-b border-hotel-border/50 last:border-0">
                                        <p class="text-sm font-bold text-hotel-text-primary">{h.nombres} {h.apellidos}</p>
                                        <p class="text-[10px] text-hotel-text-tertiary">{h.tipo_documento}-{h.numero_documento}</p>
                                    </button>
                                {/if}
                            {/each}
                        </div>
                    {/if}
                </div>
                <Button type="button" variant="secondary" onclick={() => mostrarFormNuevoAcompanante = true}>
                    <span class="flex items-center gap-1.5">
                        <Icon name="plus" class="w-4 h-4" />
                        Nuevo
                    </span>
                </Button>
            </div>

            {#if acompanantes.length > 0}
                <div class="space-y-2 mt-4 pt-4 border-t border-hotel-border/50">
                    <p class="text-[10px] font-bold uppercase text-hotel-text-tertiary">Acompañantes agregados:</p>
                    {#each acompanantes as a}
                        <div class="flex items-center justify-between p-2 rounded-lg bg-hotel-gold/5 border border-hotel-gold/20">
                            <div>
                                <p class="text-sm font-bold text-hotel-text-primary">{a.nombres} {a.apellidos}</p>
                                <p class="text-[10px] text-hotel-text-tertiary">{a.tipo_documento}-{a.numero_documento}</p>
                            </div>
                            <button type="button" onclick={() => acompanantes = acompanantes.filter(x => x.id !== a.id)} class="text-hotel-error-light text-xs font-bold hover:underline">Quitar</button>
                        </div>
                    {/each}
                </div>
            {:else}
                <p class="text-xs text-hotel-text-tertiary italic text-center py-4">No hay acompañantes agregados</p>
            {/if}
        </div>
    {/if}

    <!-- PASO 3 -->
    {#if paso === 3}
        <div class="p-5 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
            <p class="text-[10px] font-black uppercase tracking-wider text-hotel-gold">Paso 3 — Habitación</p>

            <Select
                label="Filtrar por tipo"
                options={[
                    { value: '', label: 'Todos los tipos' },
                    ...tiposHabitacionDisponibles.map(t => ({ value: t, label: t }))
                ]}
                bind:value={filtroTipoHabitacion}
            />

            {#if habitacionesFiltradas.length === 0}
                <div class="p-4 text-center rounded-xl border border-dashed border-hotel-border">
                    <p class="text-sm text-hotel-text-secondary">
                        No hay habitaciones disponibles con capacidad para {totalPersonas} {(totalPersonas === 1 ? 'persona' : 'personas')}.
                    </p>
                </div>
            {:else}
                <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 max-h-64 overflow-y-auto custom-scrollbar p-1">
                    {#each habitacionesFiltradas as h}
                        <button type="button" onclick={() => habitacionSeleccionada = h} class="p-3 rounded-xl border text-left transition-all {habitacionSeleccionada?.id === h.id ? 'border-hotel-gold bg-hotel-gold/5' : 'border-hotel-border hover:border-hotel-gold/50'}">
                            <p class="font-bold text-sm text-hotel-text-primary">#{h.numero}</p>
                            <p class="text-[10px] text-hotel-text-tertiary">{h.categoria_tipo || 'Sin categoría'}</p>

                            {#if esEmpresa && h.precio_empresa}
                                <p class="text-[10px] text-hotel-success-light font-bold mt-1">${h.precio_empresa}/noche (Empresa)</p>
                            {:else}
                                <p class="text-[10px] text-hotel-gold font-bold mt-1">${h.precio_por_noche}/noche</p>
                            {/if}
                            <p class="text-[9px] text-hotel-text-tertiary mt-1 flex items-center gap-1">
                                <Icon name="users" class="w-3 h-3" /> Cap: {h.capacidad_maxima} pers.
                            </p>
                        </button>
                    {/each}
                </div>
            {/if}
        </div>
    {/if}

    <!-- PASO 4 -->
    {#if paso === 4}
        <div class="p-5 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
            <p class="text-[10px] font-black uppercase tracking-wider text-hotel-gold">Paso 4 — Fechas</p>
            <div class="grid grid-cols-2 gap-4">
                <DatePicker label="Entrada" bind:value={fechaEntrada} />
                <DatePicker label="Salida" bind:value={fechaSalida} />
            </div>
            <div class="flex justify-between items-center p-3 rounded-xl bg-hotel-gold/5 border border-hotel-gold/20 mt-4">
                <div>
                    <p class="text-[10px] uppercase text-hotel-text-tertiary">Noches</p>
                    <p class="font-bold text-hotel-text-primary">{noches}</p>
                </div>
                <div class="text-right">
                    <p class="text-[10px] uppercase text-hotel-text-tertiary">Total Habitación</p>
                    <p class="font-bold text-hotel-gold text-lg">${totalHabitacion.toFixed(2)}</p>
                </div>
            </div>
        </div>
    {/if}

    <!-- PASO 5 -->
    {#if paso === 5}
        <div class="p-5 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
            <p class="text-[10px] font-black uppercase tracking-wider text-hotel-gold">Paso 5 — Pago</p>
            <Select label="Modalidad" options={[{value:'Contado',label:'Contado'},{value:'Abono',label:'Abono'},{value:'Crédito',label:'Crédito'}]} bind:value={modalidadPago} />

            {#if modalidadPago !== 'Crédito'}
                <Select label="Método de pago" options={[{value:'Efectivo',label:'Efectivo'},{value:'Tarjeta',label:'Tarjeta'},{value:'PagoMovil',label:'Pago Móvil'}]} bind:value={metodoPago} />
                {#if metodoPago !== 'Efectivo'}
                    <InputHotel label="Nº Referencia" bind:value={numeroReferencia} placeholder="Ej: 123456" />
                {/if}
            {/if}

            {#if modalidadPago === 'Abono'}
                <InputHotel label="Monto a abonar ($)" type="number" bind:value={montoAbonado} />
            {/if}

            <label class="flex items-center gap-2 text-sm mt-2 text-hotel-text-primary cursor-pointer">
                <input type="checkbox" bind:checked={requiereFactura} class="rounded border-hotel-border text-hotel-gold focus:ring-hotel-gold" /> ¿Requiere factura legal?
            </label>
        </div>
    {/if}

    <div class="flex gap-3 pt-4 border-t border-hotel-border/50">
        {#if paso > 1}
            <Button type="button" variant="ghost" onclick={() => paso--}>Anterior</Button>
        {/if}
        <Button type="submit" variant="gold" loading={loading} fullWidth>
            {paso < 5 ? 'Siguiente' : 'Confirmar Reservación'}
        </Button>
        <Button type="button" variant="ghost" onclick={onclose}>Cancelar</Button>
    </div>
</form>

{#if mostrarFormNuevoAcompanante}
    <Modal title="Nuevo Acompañante" subtitle="Se registrará como huésped" onclose={() => mostrarFormNuevoAcompanante = false}>
        <NuevoHuespedRapido
            {ocupaciones}
            oncreado={onNuevoAcompananteCreado}
            oncancel={() => mostrarFormNuevoAcompanante = false}
        />
    </Modal>
{/if}
