<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { toast } from '$lib/stores/toast';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import Modal from '$components/ui/Modal.svelte';
    import Loading from '$components/ui/Loading.svelte';
    import Icon from '$components/ui/Icons.svelte';
    import CheckInForm from '$components/reservaciones/CheckInForm.svelte';
    import CheckOutForm from '$components/reservaciones/CheckOutForm.svelte';
    import ConsumoSelector from '$components/reservaciones/ConsumoSelector.svelte';
    import PagoRegistro from '$components/reservaciones/PagoRegistro.svelte';
    import {
        fetchReservacion,
        fetchConsumos,
        fetchPagos,
        cancelarReservacion,
    } from '$lib/services/reservaciones';
    import type { Reservacion, Consumo, Pago } from '$lib/types/reservacion';

    let reservacion = $state<Reservacion | null>(null);
    let consumos = $state<Consumo[]>([]);
    let pagos = $state<Pago[]>([]);
    let cargando = $state(true);
    let error = $state('');

    // Modales
    let mostrarCheckin = $state(false);
    let mostrarCheckout = $state(false);
    let mostrarConsumo = $state(false);
    let mostrarPago = $state(false);

    let saldoPendiente = $derived(parseFloat(reservacion?.saldo_pendiente || '0'));

    // Colores del badge de estado
    const estadoClases: Record<string, string> = {
        'Confirmada': 'bg-hotel-info/10 text-hotel-info-light border-hotel-info/30',
        'EnCurso': 'bg-hotel-gold/10 text-hotel-gold-light border-hotel-gold/30',
        'Finalizada': 'bg-hotel-success/10 text-hotel-success-light border-hotel-success/30',
        'Cancelada': 'bg-hotel-error/10 text-hotel-error-light border-hotel-error/30',
        'NoShow': 'bg-hotel-error/10 text-hotel-error-light border-hotel-error/30',
    };

    onMount(async () => {
        const id = Number($page.params.id);
        await cargarDatos(id);
    });

    async function cargarDatos(id: number) {
        cargando = true;
        try {
            const [r, c, p] = await Promise.all([
                fetchReservacion(id),
                fetchConsumos(id),
                fetchPagos(id),
            ]);
            reservacion = r;
            consumos = c;
            pagos = p;
        } catch (e: any) {
            error = e.message;
        } finally {
            cargando = false;
        }
    }

    async function refrescar() {
        if (!reservacion) return;
        await cargarDatos(reservacion.id);
    }

    async function cancelar() {
        const motivo = prompt('Motivo de cancelación:');
        if (!motivo) return;
        try {
            await cancelarReservacion(reservacion!.id, motivo);
            toast.success('Reserva cancelada.');
            goto('/reservaciones', { invalidateAll: true });
        } catch (e: any) {
            toast.error(e.message);
        }
    }

    function volver() {
        goto('/reservaciones', { invalidateAll: true });
    }

    async function abrirHojaRegistro() {
        if (!reservacion) return;
        try {
            const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';
            const token = localStorage.getItem('auth_token');

            const res = await fetch(`${apiUrl}/reportes/hoja-huesped/${reservacion.id}/`, {
                headers: { 'Authorization': `Token ${token}` }
            });

            if (!res.ok) throw new Error('Error al generar la hoja');

            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            window.open(url, '_blank');
            setTimeout(() => URL.revokeObjectURL(url), 10000);
        } catch (err: any) {
            toast.error(err.message || 'Error al abrir la hoja');
        }
    }
</script>

<svelte:head>
    <title>Reserva #{reservacion?.id || '...'} | SalmaSuitesPMS</title>
</svelte:head>

{#if cargando}
    <Loading type="dashboard" message="Cargando reserva..." />
{:else if error}
    <div class="text-center p-8">
        <p class="text-hotel-error-light font-bold uppercase tracking-widest text-xs mb-4">{error}</p>
        <Button variant="gold" size="md" onclick={volver}>Volver</Button>
    </div>
{:else if reservacion}
    <PageHeader
        title="Reserva #{reservacion.id}"
        subtitle="{reservacion.huesped_nombre} · Habitación #{reservacion.habitacion_numero}"
    >
        <div class="flex flex-wrap gap-2">
            {#if reservacion.estado === 'Confirmada'}
                <Button variant="success" size="md" onclick={() => mostrarCheckin = true}>
                    <span class="flex items-center gap-1.5">
                        <Icon name="checkIn" class="w-4 h-4" /> Check-in
                    </span>
                </Button>
                <Button variant="danger" size="md" onclick={cancelar}>
                    <span class="flex items-center gap-1.5">
                        <Icon name="close" class="w-4 h-4" /> Cancelar
                    </span>
                </Button>
            {:else if reservacion.estado === 'EnCurso'}
                <Button variant="gold" size="md" onclick={() => mostrarCheckout = true}>
                    <span class="flex items-center gap-1.5">
                        <Icon name="checkOut" class="w-4 h-4" /> Check-out
                    </span>
                </Button>
                <Button variant="secondary" size="md" onclick={() => mostrarConsumo = true}>
                    <span class="flex items-center gap-1.5">
                        <Icon name="plus" class="w-4 h-4" /> Consumo
                    </span>
                </Button>
                {#if saldoPendiente > 0}
                    <Button variant="secondary" size="md" onclick={() => mostrarPago = true}>
                        <span class="flex items-center gap-1.5">
                            <Icon name="dinero" class="w-4 h-4" /> Pago
                        </span>
                    </Button>
                {/if}
            {/if}

            <Button variant="secondary" size="sm" onclick={abrirHojaRegistro}>
                <span class="flex items-center gap-1.5">
                    <Icon name="file" class="w-4 h-4" /> Hoja de Registro
                </span>
            </Button>

            <Button variant="ghost" size="md" onclick={volver}>Volver</Button>
        </div>
    </PageHeader>

    <div class="space-y-6">

        <!-- Tarjeta Superior: Estado y Totales -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

            <!-- Columna Izquierda: Info básica -->
            <div class="lg:col-span-2 bg-hotel-surface rounded-2xl border border-hotel-border p-6">
                <div class="flex justify-between items-start mb-6">
                    <div>
                        <p class="text-[10px] uppercase text-hotel-text-tertiary mb-1">Huésped Titular</p>
                        <p class="font-display text-xl italic font-bold text-hotel-text-primary">{reservacion.huesped_nombre}</p>
                    </div>
                    <span class="px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider border {estadoClases[reservacion.estado] || ''}">
                        {reservacion.estado}
                    </span>
                </div>

                <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <div>
                        <p class="text-[10px] uppercase text-hotel-text-tertiary mb-0.5">Habitación</p>
                        <p class="font-bold text-hotel-text-primary text-lg">#{reservacion.habitacion_numero}</p>
                    </div>
                    <div>
                        <p class="text-[10px] uppercase text-hotel-text-tertiary mb-0.5">Entrada</p>
                        <p class="font-bold text-hotel-text-primary">{reservacion.fecha_entrada}</p>
                    </div>
                    <div>
                        <p class="text-[10px] uppercase text-hotel-text-tertiary mb-0.5">Salida</p>
                        <p class="font-bold text-hotel-text-primary">{reservacion.fecha_salida}</p>
                    </div>
                    <div>
                        <p class="text-[10px] uppercase text-hotel-text-tertiary mb-0.5">Noches</p>
                        <p class="font-bold text-hotel-text-primary">{reservacion.numero_noches}</p>
                    </div>
                </div>
            </div>

            <!-- Columna Derecha: Resumen Financiero -->
            <div class="bg-hotel-surface rounded-2xl border border-hotel-border p-6 space-y-3">
                <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold mb-2">Resumen Financiero</p>

                <div class="flex justify-between text-sm">
                    <span class="text-hotel-text-secondary">Habitación</span>
                    <span class="font-medium text-hotel-text-primary">${reservacion.total_habitacion}</span>
                </div>
                <div class="flex justify-between text-sm">
                    <span class="text-hotel-text-secondary">Consumos</span>
                    <span class="font-medium text-hotel-text-primary">${reservacion.monto_total_consumos}</span>
                </div>
                <div class="flex justify-between text-sm pt-2 border-t border-hotel-border/50">
                    <span class="font-bold text-hotel-text-primary">Total General</span>
                    <span class="font-bold text-hotel-gold">${reservacion.monto_total_final}</span>
                </div>
                <div class="flex justify-between text-sm">
                    <span class="text-hotel-text-secondary">Pagado</span>
                    <span class="font-medium text-hotel-success-light">- ${reservacion.monto_pagado}</span>
                </div>

                <div class="p-3 rounded-xl {saldoPendiente > 0 ? 'bg-hotel-error/5 border border-hotel-error/20' : 'bg-hotel-success/5 border border-hotel-success/20'} mt-2">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold uppercase tracking-wider {saldoPendiente > 0 ? 'text-hotel-error-light' : 'text-hotel-success-light'}">
                            {saldoPendiente > 0 ? 'Saldo Pendiente' : 'Saldado'}
                        </span>
                        <span class="text-lg font-bold {saldoPendiente > 0 ? 'text-hotel-error-light' : 'text-hotel-success-light'}">
                            ${reservacion.saldo_pendiente}
                        </span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Consumos -->
        <div class="bg-hotel-surface rounded-2xl border border-hotel-border overflow-hidden">
            <div class="p-4 border-b border-hotel-border/50 flex justify-between items-center bg-hotel-bg/20">
                <h3 class="font-display text-lg text-hotel-text-primary italic flex items-center gap-2">
                    <Icon name="box" class="w-5 h-5 text-hotel-gold" /> Consumos
                </h3>
                <span class="text-[10px] uppercase font-bold text-hotel-text-tertiary bg-hotel-surface px-2 py-1 rounded-md border border-hotel-border">
                    {consumos.length} registrados
                </span>
            </div>

            {#if consumos.length > 0}
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead>
                            <tr class="text-[10px] uppercase text-hotel-text-tertiary text-left border-b border-hotel-border/30">
                                <th class="p-3 font-bold">Fecha</th>
                                <th class="p-3 font-bold">Tipo</th>
                                <th class="p-3 font-bold hidden sm:table-cell">Producto</th>
                                <th class="p-3 font-bold">Descripción</th>
                                <th class="p-3 font-bold text-right">Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each consumos as c}
                                <tr class="border-b border-hotel-border/20 hover:bg-hotel-surface-hover/50 transition-colors">
                                    <td class="p-3 text-hotel-text-secondary text-xs">{new Date(c.fecha_hora).toLocaleDateString()}</td>
                                    <td class="p-3">
                                        <span class="px-2 py-0.5 rounded-md bg-hotel-bg border border-hotel-border text-[10px] font-medium text-hotel-text-secondary">
                                            {c.tipo_consumo}
                                        </span>
                                    </td>
                                    <td class="p-3 hidden sm:table-cell">
                                        {#if c.producto_nombre}
                                            <span class="text-hotel-gold font-bold">{c.producto_nombre}</span>
                                        {:else}
                                            <span class="text-hotel-text-tertiary">—</span>
                                        {/if}
                                    </td>
                                    <td class="p-3 text-hotel-text-secondary text-xs">{c.descripcion}</td>
                                    <td class="p-3 text-right font-bold text-hotel-text-primary">${c.total}</td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            {:else}
                <div class="p-8 text-center text-hotel-text-tertiary">
                    <p class="text-xs uppercase tracking-widest">Sin consumos registrados</p>
                </div>
            {/if}
        </div>

        <!-- Pagos -->
        <div class="bg-hotel-surface rounded-2xl border border-hotel-border overflow-hidden">
            <div class="p-4 border-b border-hotel-border/50 flex justify-between items-center bg-hotel-bg/20">
                <h3 class="font-display text-lg text-hotel-text-primary italic flex items-center gap-2">
                    <Icon name="dinero" class="w-5 h-5 text-hotel-gold" /> Pagos
                </h3>
                <span class="text-[10px] uppercase font-bold text-hotel-text-tertiary bg-hotel-surface px-2 py-1 rounded-md border border-hotel-border">
                    {pagos.length} registrados
                </span>
            </div>

            {#if pagos.length > 0}
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead>
                            <tr class="text-[10px] uppercase text-hotel-text-tertiary text-left border-b border-hotel-border/30">
                                <th class="p-3 font-bold">Fecha</th>
                                <th class="p-3 font-bold">Método</th>
                                <th class="p-3 font-bold hidden sm:table-cell">Referencia</th>
                                <th class="p-3 font-bold text-right">Monto</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each pagos as p}
                                <tr class="border-b border-hotel-border/20 hover:bg-hotel-surface-hover/50 transition-colors">
                                    <td class="p-3 text-hotel-text-secondary text-xs">{new Date(p.fecha_hora).toLocaleDateString()}</td>
                                    <td class="p-3">
                                        <span class="px-2 py-0.5 rounded-md bg-hotel-bg border border-hotel-border text-[10px] font-medium text-hotel-text-secondary">
                                            {p.metodo_pago}
                                        </span>
                                    </td>
                                    <td class="p-3 hidden sm:table-cell text-hotel-text-secondary text-xs">
                                        {p.numero_referencia || '—'}
                                    </td>
                                    <td class="p-3 text-right font-bold text-hotel-success-light">${p.monto}</td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            {:else}
                <div class="p-8 text-center text-hotel-text-tertiary">
                    <p class="text-xs uppercase tracking-widest">Sin pagos registrados</p>
                </div>
            {/if}
        </div>
    </div>
{/if}

<!-- Modales -->
{#if mostrarCheckin && reservacion}
    <Modal title="Check‑in" onclose={() => { mostrarCheckin = false; refrescar(); }}>
        <CheckInForm reservacion={reservacion} onclose={() => { mostrarCheckin = false; refrescar(); }} />
    </Modal>
{/if}
{#if mostrarCheckout && reservacion}
    <Modal title="Check‑out" onclose={() => { mostrarCheckout = false; refrescar(); }}>
        <CheckOutForm reservacion={reservacion} onclose={() => { mostrarCheckout = false; refrescar(); }} />
    </Modal>
{/if}
{#if mostrarConsumo && reservacion}
    <Modal title="Registrar Consumo" onclose={() => { mostrarConsumo = false; refrescar(); }}>
        <ConsumoSelector reservaId={reservacion.id} onclose={() => { mostrarConsumo = false; refrescar(); }} />
    </Modal>
{/if}
{#if mostrarPago && reservacion}
    <Modal title="Registrar Pago" onclose={() => { mostrarPago = false; refrescar(); }}>
        <PagoRegistro reservaId={reservacion.id} onclose={() => { mostrarPago = false; refrescar(); }} />
    </Modal>
{/if}
