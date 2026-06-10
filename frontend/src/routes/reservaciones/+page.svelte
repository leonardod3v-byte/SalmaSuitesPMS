<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import Modal from '$components/ui/Modal.svelte';
    import Loading from '$components/ui/Loading.svelte';
    import Tabs from '$components/ui/Tabs.svelte';
    import DatePicker from '$components/ui/DatePicker.svelte';
    import BookingCalendar from '$components/reservaciones/BookingCalendar.svelte';
    import ReservaDetail from '$components/reservaciones/ReservaDetail.svelte';
    import ReservaForm from '$components/reservaciones/ReservaForm.svelte';
    import CheckInForm from '$components/reservaciones/CheckInForm.svelte';
    import CheckOutForm from '$components/reservaciones/CheckOutForm.svelte';
    import ConsumoSelector from '$components/reservaciones/ConsumoSelector.svelte';
    import PagoRegistro from '$components/reservaciones/PagoRegistro.svelte';
    import { fetchReservaciones } from '$lib/services/reservaciones';
    import { fetchHabitaciones } from '$lib/services/habitaciones';
    import type { Reservacion } from '$lib/types/reservacion';
    import type { Habitacion } from '$lib/types/habitacion';

    let reservaciones = $state<Reservacion[]>([]);
    let habitaciones = $state<Habitacion[]>([]);
    let cargando = $state(true);
    let error = $state('');
    let vista = $state<'calendario' | 'lista'>('calendario');
    let semanaInicio = $state(getLunes());

    let mostrarForm = $state(false);
    let mostrarCheckin = $state<Reservacion | null>(null);
    let mostrarCheckout = $state<Reservacion | null>(null);
    let mostrarConsumo = $state<number | null>(null);
    let mostrarPago = $state<number | null>(null);

    let fechaDesde = $state('');
    let fechaHasta = $state('');

    function getLunes(): Date {
        const hoy = new Date();
        const dia = hoy.getDay();
        const diff = dia === 0 ? -6 : 1 - dia;
        const lunes = new Date(hoy);
        lunes.setDate(hoy.getDate() + diff);
        lunes.setHours(0, 0, 0, 0);
        return lunes;
    }

    onMount(async () => {
        await cargarReservaciones();
    });

    async function cargarReservaciones() {
        cargando = true;
        try {
            let params = '';
            if (fechaDesde) params += `&desde=${fechaDesde}`;
            if (fechaHasta) params += `&hasta=${fechaHasta}`;
            const query = params ? `?${params.substring(1)}` : '';
            console.log('URL:', `/reservaciones/${query}`);
            
            const [r, h] = await Promise.all([
                fetchReservaciones(params ? `?${params.substring(1)}` : ''),
                fetchHabitaciones(),
            ]);
            reservaciones = r;
            habitaciones = h;
        } catch (e: any) {
            error = e.message;
        } finally {
            cargando = false;
        }
    }

    async function refrescar() {
        try {
            reservaciones = await fetchReservaciones();
        } catch { }
    }

    function onCeldaClick(habNum: string, fecha: string) {
        const reserva = reservaciones.find(r => {
            const entrada = new Date(r.fecha_entrada + 'T12:00:00');
            const salida = new Date(r.fecha_salida + 'T12:00:00');
            const clic = new Date(fecha + 'T12:00:00');
            return r.habitacion_numero === habNum && clic >= entrada && clic < salida;
        });
        
        if (reserva) {
            goto(`/reservaciones/${reserva.id}`);
        }
    }
</script>

<svelte:head>
    <title>Reservaciones | SalmaSuitesPMS</title>
</svelte:head>

<PageHeader title="Reservaciones" subtitle="{reservaciones.length} reservas">
    <Button variant="gold" size="md" onclick={() => mostrarForm = true}>
        <span class="flex items-center gap-1.5">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            Nueva Reserva
        </span>
    </Button>
</PageHeader>

{#if cargando}
    <Loading type="dashboard" message="Cargando reservaciones..." />
{:else if error}
    <div class="text-center p-8 bg-hotel-error/5 border border-hotel-error/20 rounded-2xl">
        <p class="text-hotel-error-light font-bold uppercase tracking-widest text-xs mb-4">{error}</p>
        <Button variant="gold" size="sm" onclick={() => window.location.reload()}>Reintentar</Button>
    </div>
{:else}
    <div class="space-y-6">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <Tabs
                tabs={[{ key: 'calendario', label: 'Calendario' }, { key: 'lista', label: 'Lista' }]}
                active={vista}
                onchange={(k: string) => vista = k as 'calendario' | 'lista'}
            />
            
            <div class="flex items-center gap-2">
                <DatePicker bind:value={fechaDesde} />
                <span class="text-hotel-text-tertiary text-xs">—</span>
                <DatePicker bind:value={fechaHasta} />
                <Button variant="gold" size="md" onclick={cargarReservaciones}>
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                </Button>
                {#if fechaDesde || fechaHasta}
                    <Button variant="ghost" size="md" onclick={() => { fechaDesde = ''; fechaHasta = ''; cargarReservaciones(); }}>
                        ✕
                    </Button>
                {/if}
            </div>
        </div>

        {#if vista === 'calendario'}
            <BookingCalendar
                reservas={reservaciones.map(r => ({
                    id: r.id,
                    fecha_entrada: r.fecha_entrada,
                    fecha_salida: r.fecha_salida,
                    estado: r.estado,
                    habitacion_numero: r.habitacion_numero || '',
                    huesped_nombre: r.huesped_nombre || '',
                    huesped_documento: r.huesped_documento || '',
                    tipo_cliente: 'Particular',
                }))}
                habitaciones={habitaciones.map(h => ({
                    numero: h.numero,
                    tipo_nombre: h.categoria_tipo,
                    piso: h.piso,
                }))}
                semanaInicio={semanaInicio}
                onCeldaClick={onCeldaClick}
            />
        {:else}
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {#each reservaciones as r}
                    <ReservaDetail reservacion={r} />
                {/each}
            </div>
        {/if}
    </div>
{/if}

{#if mostrarForm}
    <Modal title="Nueva Reservación" onclose={() => { mostrarForm = false; refrescar(); }}>
        <ReservaForm onclose={() => { mostrarForm = false; refrescar(); }} />
    </Modal>
{/if}

{#if mostrarCheckin}
    <Modal title="Check‑in" onclose={() => { mostrarCheckin = null; refrescar(); }}>
        <CheckInForm reservacion={mostrarCheckin} onclose={() => { mostrarCheckin = null; refrescar(); }} />
    </Modal>
{/if}

{#if mostrarCheckout}
    <Modal title="Check‑out" onclose={() => { mostrarCheckout = null; refrescar(); }}>
        <CheckOutForm reservacion={mostrarCheckout} onclose={() => { mostrarCheckout = null; refrescar(); }} />
    </Modal>
{/if}

{#if mostrarConsumo}
    <Modal title="Registrar Consumo" onclose={() => { mostrarConsumo = null; refrescar(); }}>
        <ConsumoSelector reservaId={mostrarConsumo} onclose={() => { mostrarConsumo = null; refrescar(); }} />
    </Modal>
{/if}

{#if mostrarPago}
    <Modal title="Registrar Pago" onclose={() => { mostrarPago = null; refrescar(); }}>
        <PagoRegistro reservaId={mostrarPago} onclose={() => { mostrarPago = null; refrescar(); }} />
    </Modal>
{/if}