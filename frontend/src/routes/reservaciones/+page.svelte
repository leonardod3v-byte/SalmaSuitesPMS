<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import Modal from '$components/ui/Modal.svelte';
    import Loading from '$components/ui/Loading.svelte';
    import Tabs from '$components/ui/Tabs.svelte';
    import DatePicker from '$components/ui/DatePicker.svelte';
    import Icon from '$components/ui/Icons.svelte';
    import BookingCalendar from '$components/reservaciones/BookingCalendar.svelte';
    import ReservaForm from '$components/reservaciones/ReservaForm.svelte';
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

    let fechaDesde = $state('');
    let fechaHasta = $state('');
    let filtroEstado = $state<string>('todas');

    let mostrarForm = $state(false);

    function getLunes(): Date {
        const hoy = new Date();
        const dia = hoy.getDay();
        const diff = dia === 0 ? -6 : 1 - dia;
        const lunes = new Date(hoy);
        lunes.setDate(hoy.getDate() + diff);
        lunes.setHours(0, 0, 0, 0);
        return lunes;
    }

    async function cargarReservaciones() {
        cargando = true;
        try {
            let params = [];
            if (fechaDesde) params.push(`desde=${fechaDesde}`);
            if (fechaHasta) params.push(`hasta=${fechaHasta}`);

            const query = params.length > 0 ? `?${params.join('&')}` : '';

            const [r, h] = await Promise.all([
                fetchReservaciones(query),
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

    onMount(() => {
        cargarReservaciones();
    });

    function filtrarPorFecha() {
        cargarReservaciones();
    }

    function limpiarFiltros() {
        fechaDesde = '';
        fechaHasta = '';
        filtroEstado = 'todas';
        cargarReservaciones();
    }

    async function refrescar() {
        await cargarReservaciones();
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

    async function descargarRegistroSemanal() {
        try {
            const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';
            const token = localStorage.getItem('auth_token');
            const fecha = semanaInicio.toISOString().split('T')[0];

            const res = await fetch(`${apiUrl}/reportes/registro-reservaciones/?fecha=${fecha}`, {
                headers: {
                    'Authorization': `Token ${token}`
                }
            });

            if (!res.ok) {
                throw new Error('Error al generar el reporte');
            }

            const blob = await res.blob();
            const url = URL.createObjectURL(blob);

            window.open(url, '_blank');

            setTimeout(() => URL.revokeObjectURL(url), 10000);
        } catch (err: any) {
            toast.error(err.message || 'Error al abrir el PDF');
        }
    }

    // Filtrado local por estado
    let filtradas = $derived(
        filtroEstado === 'todas'
            ? reservaciones
            : reservaciones.filter(r => r.estado === filtroEstado)
    );

    // Colores para el badge del estado
    const estadoClases: Record<string, string> = {
        'Confirmada': 'bg-hotel-info/10 text-hotel-info-light border-hotel-info/30',
        'EnCurso': 'bg-hotel-gold/10 text-hotel-gold-light border-hotel-gold/30',
        'Finalizada': 'bg-hotel-success/10 text-hotel-success-light border-hotel-success/30',
        'Cancelada': 'bg-hotel-error/10 text-hotel-error-light border-hotel-error/30',
        'NoShow': 'bg-hotel-text-tertiary/10 text-hotel-text-tertiary border-hotel-text-tertiary/30',
    };

    function formatFecha(fecha: string) {
        const d = new Date(fecha + 'T12:00:00');
        return d.toLocaleDateString('es-VE', { day: '2-digit', month: 'short', year: 'numeric' });
    }
</script>

<svelte:head>
    <title>Reservaciones | SalmaSuitesPMS</title>
</svelte:head>

<PageHeader title="Reservaciones" subtitle="{reservaciones.length} reservas en el sistema">
    <div class="flex items-center gap-2">
        <Button variant="secondary" size="md" onclick={descargarRegistroSemanal}>
            <span class="flex items-center gap-1.5">
                <Icon name="file" class="w-4 h-4" />
                Registro Semanal
            </span>
        </Button>

        <Button variant="gold" size="md" onclick={() => mostrarForm = true}>
            <span class="flex items-center gap-1.5">
                <Icon name="plus" class="w-4 h-4" />
                Nueva reservación
            </span>
        </Button>
    </div>
</PageHeader>

{#if cargando}
    <Loading type="dashboard" message="Cargando reservaciones..." />
{:else if error}
    <div class="text-center p-8 bg-hotel-error/5 border border-hotel-error/20 rounded-2xl">
        <p class="text-hotel-error-light font-bold uppercase tracking-widest text-xs mb-4">{error}</p>
        <Button variant="gold" size="sm" onclick={cargarReservaciones}>Reintentar</Button>
    </div>
{:else}
    <div class="space-y-6">

        <!-- Barra de Filtros Unificada -->
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 p-4 rounded-2xl bg-hotel-surface/40 border border-hotel-border">
            <!-- Inputs de fecha alineados al fondo -->
            <div class="flex flex-wrap items-end gap-3">
                <div class="w-full sm:w-auto">
                    <DatePicker label="Desde" bind:value={fechaDesde} />
                </div>
                <div class="w-full sm:w-auto">
                    <DatePicker label="Hasta" bind:value={fechaHasta} />
                </div>
                <Button variant="gold" size="md" onclick={filtrarPorFecha}>
                    <Icon name="search" class="w-4 h-4" />
                </Button>
                {#if fechaDesde || fechaHasta}
                    <Button variant="ghost" size="md" onclick={limpiarFiltros}>Limpiar</Button>
                {/if}
            </div>

            <!-- Tabs de vista a la derecha -->
            <div class="flex items-center gap-2">
                <Tabs
                    tabs={[{ key: 'calendario', label: 'Calendario' }, { key: 'lista', label: 'Lista' }]}
                    active={vista}
                    onchange={(k: string) => vista = k as 'calendario' | 'lista'}
                />
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
                    tipo_cliente: r.tipo_cliente || 'Particular',
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
            <!-- Vista de Lista -->
            <div class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm overflow-hidden">

                <!-- Filtros rápidos por estado -->
                <div class="p-4 border-b border-hotel-border/50 flex flex-wrap gap-2 bg-hotel-bg/20">
                    <button
                        onclick={() => filtroEstado = 'todas'}
                        class="px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all border
                        {filtroEstado === 'todas' ? 'bg-hotel-gold text-hotel-bg border-hotel-gold' : 'bg-transparent border-transparent text-hotel-text-tertiary hover:text-hotel-text-secondary'}"
                    >
                        Todas ({reservaciones.length})
                    </button>
                    {#each ['Confirmada', 'EnCurso', 'Finalizada', 'Cancelada', 'NoShow'] as estado}
                        {@const count = reservaciones.filter(r => r.estado === estado).length}
                        {#if count > 0}
                            <button
                                onclick={() => filtroEstado = estado}
                                class="px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all border
                                {filtroEstado === estado ? 'bg-hotel-surface text-hotel-text-primary border-hotel-border shadow-sm' : 'bg-transparent border-transparent text-hotel-text-tertiary hover:text-hotel-text-secondary'}"
                            >
                                {estado === 'EnCurso' ? 'En Curso' : estado} ({count})
                            </button>
                        {/if}
                    {/each}
                </div>

                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead>
                            <tr class="border-b border-hotel-border text-[10px] uppercase tracking-widest text-hotel-text-tertiary text-left bg-hotel-bg/10">
                                <th class="p-4 font-bold">Reserva</th>
                                <th class="p-4 font-bold">Huésped</th>
                                <th class="p-4 font-bold">Habitación</th>
                                <th class="p-4 font-bold hidden md:table-cell">Estadía</th>
                                <th class="p-4 font-bold text-right">Total</th>
                                <th class="p-4 font-bold text-center">Estado</th>
                                <th class="p-4 font-bold text-right">Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each filtradas as r (r.id)}
                                <tr class="border-b border-hotel-border/30 hover:bg-hotel-surface-hover transition-colors group">

                                    <!-- ID y Factura -->
                                    <td class="p-4">
                                        <p class="font-display font-bold italic text-base text-hotel-text-primary group-hover:text-hotel-gold transition-colors">
                                            #{r.id}
                                        </p>
                                        {#if r.requiere_factura}
                                            <span class="inline-block mt-1 px-1.5 py-0.5 rounded text-[8px] font-black uppercase bg-hotel-vip/20 text-hotel-vip-light border border-hotel-vip/30">
                                                Factura
                                            </span>
                                        {/if}
                                    </td>

                                    <!-- Huésped -->
                                    <td class="p-4">
                                        <p class="font-bold text-hotel-text-primary text-sm">{r.huesped_nombre}</p>
                                        <p class="text-[10px] text-hotel-text-tertiary">{r.huesped_documento}</p>
                                    </td>

                                    <!-- Habitación (rediseñada) -->
                                    <td class="p-4">
                                        <span class="text-hotel-text-primary font-bold text-sm">
                                            Hab. <span class="text-hotel-gold">{r.habitacion_numero}</span>
                                        </span>
                                    </td>

                                    <!-- Fechas -->
                                    <td class="p-4 hidden md:table-cell">
                                        <p class="text-xs text-hotel-text-secondary">{formatFecha(r.fecha_entrada)}</p>
                                        <p class="text-[10px] text-hotel-text-tertiary my-0.5">al {formatFecha(r.fecha_salida)}</p>
                                        <p class="text-[9px] font-bold text-hotel-gold uppercase tracking-wider">{r.numero_noches} noches</p>
                                    </td>

                                    <!-- Total -->
                                    <td class="p-4 text-right">
                                        <p class="font-bold text-hotel-text-primary text-sm">${r.monto_total_final}</p>
                                        {#if parseFloat(r.saldo_pendiente) > 0}
                                            <p class="text-[10px] font-bold text-hotel-error-light mt-1">Saldo: ${r.saldo_pendiente}</p>
                                        {:else}
                                            <p class="text-[10px] font-bold text-hotel-success-light mt-1">Saldado</p>
                                        {/if}
                                    </td>

                                    <!-- Estado -->
                                    <td class="p-4 text-center">
                                        <span class="inline-block px-2.5 py-1 rounded-full text-[9px] font-black uppercase tracking-wider border {estadoClases[r.estado] || ''}">
                                            {r.estado === 'EnCurso' ? 'En Curso' : r.estado}
                                        </span>
                                    </td>

                                    <!-- Acciones -->
                                    <td class="p-4 text-right">
                                        <Button variant="ghost" size="sm" onclick={() => goto(`/reservaciones/${r.id}`)}>
                                            Ver Detalle →
                                        </Button>
                                    </td>
                                </tr>
                            {:else}
                                <tr>
                                    <td colspan="7" class="p-10 text-center">
                                        <p class="text-hotel-text-tertiary text-xs uppercase tracking-widest mb-2">
                                            No hay reservas {filtroEstado !== 'todas' ? `en estado "${filtroEstado}"` : 'registradas'}
                                        </p>
                                        {#if filtroEstado !== 'todas'}
                                            <Button variant="ghost" size="sm" onclick={() => filtroEstado = 'todas'}>Ver todas</Button>
                                        {/if}
                                    </td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            </div>
        {/if}
    </div>
{/if}

{#if mostrarForm}
    <Modal title="Nueva Reservación" onclose={() => { mostrarForm = false; refrescar(); }}>
        <ReservaForm onclose={() => { mostrarForm = false; refrescar(); }} />
    </Modal>
{/if}
