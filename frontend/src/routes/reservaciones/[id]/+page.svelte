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

    let mostrarCheckin = $state(false);
    let mostrarCheckout = $state(false);
    let mostrarConsumo = $state(false);
    let mostrarPago = $state(false);

    let saldoPendiente = $derived(parseFloat(reservacion?.saldo_pendiente || '0'));
    let acompanantes = $derived(reservacion?.acompanantes || []);
    let totalPersonas = $derived(1 + acompanantes.length);
    let esEmpresa = $derived(!!reservacion?.empresa_nombre);

    const estadoClases: Record<string, string> = {
        'Confirmada': 'bg-hotel-info/10 text-hotel-info-light border-hotel-info/30',
        'EnCurso': 'bg-hotel-gold/10 text-hotel-gold-light border-hotel-gold/30',
        'Finalizada': 'bg-hotel-success/10 text-hotel-success-light border-hotel-success/30',
        'Cancelada': 'bg-hotel-error/10 text-hotel-error-light border-hotel-error/30',
        'NoShow': 'bg-hotel-text-tertiary/10 text-hotel-text-tertiary border-hotel-text-tertiary/30',
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
        subtitle="{reservacion.huesped_nombre} · Hab. #{reservacion.habitacion_numero} · {totalPersonas} {(totalPersonas === 1 ? 'persona' : 'personas')}"
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

        <!-- FILA SUPERIOR: Info + Finanzas -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

            <!-- Info de la reserva -->
            <div class="lg:col-span-2 bg-hotel-surface rounded-2xl border border-hotel-border p-6">
                <!-- Encabezado -->
                <div>
                    <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Huésped Titular</p>
                    <div class="flex items-center gap-2">
                        <p class="text-lg font-bold text-hotel-text-primary">{reservacion.huesped_nombre}</p>
                        {#if reservacion.huesped_titular_detalle?.categoria === 'VIP'}
                            <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-wider bg-hotel-vip/10 text-hotel-vip-light border border-hotel-vip/30">
                                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
                                VIP
                            </span>
                        {/if}
                    </div>
                    {#if reservacion.huesped_titular_detalle?.ocupacion_nombre}
                        <p class="text-[11px] text-hotel-text-tertiary mt-0.5">
                            {reservacion.huesped_titular_detalle.ocupacion_nombre}
                        </p>
                    {/if}
                </div>

                <!-- Datos -->
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                    <div>
                        <p class="text-[10px] uppercase text-hotel-text-tertiary mb-1">Habitación</p>
                        <p class="font-bold text-hotel-text-primary">#{reservacion.habitacion_numero}</p>
                    </div>
                    <div>
                        <p class="text-[10px] uppercase text-hotel-text-tertiary mb-1">Entrada</p>
                        <p class="font-medium text-hotel-text-primary text-sm">{reservacion.fecha_entrada}</p>
                    </div>
                    <div>
                        <p class="text-[10px] uppercase text-hotel-text-tertiary mb-1">Salida</p>
                        <p class="font-medium text-hotel-text-primary text-sm">{reservacion.fecha_salida}</p>
                    </div>
                    <div>
                        <p class="text-[10px] uppercase text-hotel-text-tertiary mb-1">Noches</p>
                        <p class="font-medium text-hotel-text-primary text-sm">{reservacion.numero_noches}</p>
                    </div>
                </div>

                <!-- Empresa (si aplica) -->
                {#if esEmpresa}
                    <div class="pt-4 border-t border-hotel-border/50">
                        <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-2">Empresa</p>
                        <div class="flex flex-wrap items-center gap-x-6 gap-y-1">
                            <div>
                                <p class="text-sm font-medium text-hotel-text-primary">{reservacion.empresa_nombre}</p>
                            </div>
                            {#if reservacion.empresa_rif}
                                <div class="flex items-center gap-1.5 text-xs text-hotel-text-tertiary">
                                    <span class="font-semibold">RIF</span>
                                    <span class="font-mono">{reservacion.empresa_rif}</span>
                                </div>
                            {/if}
                            {#if reservacion.requiere_factura}
                                <span class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary border-l border-hotel-border pl-3">
                                    Requiere factura
                                </span>
                            {/if}
                        </div>
                    </div>
                {/if}

                <!-- Acompañantes -->
                <div class="pt-4 border-t border-hotel-border/50">
                    <div class="flex items-center justify-between mb-3">
                        <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary">
                            Acompañantes <span class="text-hotel-text-primary font-semibold">{acompanantes.length}</span>
                        </p>
                    </div>

                    {#if acompanantes.length === 0}
                        <p class="text-xs text-hotel-text-tertiary italic">Sin acompañantes registrados</p>
                    {:else}
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {#each acompanantes as a}
                                <div class="flex items-center gap-3 p-2.5 rounded-lg bg-hotel-bg/40 border border-hotel-border">
                                    <div
                                        class="w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0"
                                        style="background-color: {(a.huesped_detalle?.ocupacion_color || '#9E9E9E')}15; color: {a.huesped_detalle?.ocupacion_color || '#9E9E9E'}"
                                    >
                                        {a.huesped_detalle?.nombres?.charAt(0)}{a.huesped_detalle?.apellidos?.charAt(0)}
                                    </div>
                                    <div class="min-w-0 flex-1">
                                        <p class="text-xs font-medium text-hotel-text-primary truncate">
                                            {a.huesped_detalle?.nombres} {a.huesped_detalle?.apellidos}
                                        </p>
                                        <p class="text-[10px] text-hotel-text-tertiary truncate">
                                            {a.huesped_detalle?.tipo_documento}-{a.huesped_detalle?.numero_documento}
                                            {#if a.huesped_detalle?.edad}
                                                · {a.huesped_detalle.edad} años
                                            {/if}
                                        </p>
                                    </div>
                                </div>
                            {/each}
                        </div>
                    {/if}
                </div>
            </div>

            <!-- Resumen Financiero -->
            <div class="bg-hotel-surface rounded-2xl border border-hotel-border p-6 flex flex-col">
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-4">Resumen Financiero</p>

                <div class="space-y-2 text-sm flex-1">
                    <div class="flex justify-between">
                        <span class="text-hotel-text-secondary">Habitación</span>
                        <span class="text-hotel-text-primary">${reservacion.total_habitacion}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-hotel-text-secondary">Consumos</span>
                        <span class="text-hotel-text-primary">${reservacion.monto_total_consumos}</span>
                    </div>
                    <div class="flex justify-between pt-2 border-t border-hotel-border/50">
                        <span class="font-semibold text-hotel-text-primary">Total</span>
                        <span class="font-bold text-hotel-text-primary">${reservacion.monto_total_final}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-hotel-text-secondary">Pagado</span>
                        <span class="text-hotel-success-light">- ${reservacion.monto_pagado}</span>
                    </div>
                </div>

                <div class="mt-4 pt-4 border-t border-hotel-border/50">
                    <div class="flex justify-between items-baseline">
                        <span class="text-xs uppercase tracking-wider text-hotel-text-tertiary">
                            {saldoPendiente > 0 ? 'Saldo pendiente' : 'Saldado'}
                        </span>
                        <span class="text-xl font-bold {saldoPendiente > 0 ? 'text-hotel-error-light' : 'text-hotel-success-light'}">
                            ${reservacion.saldo_pendiente}
                        </span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Consumos -->
        <div class="bg-hotel-surface rounded-2xl border border-hotel-border overflow-hidden">
            <div class="px-6 py-4 border-b border-hotel-border/50 flex justify-between items-center">
                <h3 class="text-sm font-semibold text-hotel-text-primary">Consumos</h3>
                <span class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary">
                    {consumos.length} {(consumos.length === 1 ? 'registro' : 'registros')}
                </span>
            </div>

            {#if consumos.length > 0}
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead>
                            <tr class="text-[10px] uppercase text-hotel-text-tertiary text-left border-b border-hotel-border/30">
                                <th class="px-6 py-3 font-medium">Fecha</th>
                                <th class="px-6 py-3 font-medium">Tipo</th>
                                <th class="px-6 py-3 font-medium hidden sm:table-cell">Producto</th>
                                <th class="px-6 py-3 font-medium">Descripción</th>
                                <th class="px-6 py-3 font-medium text-right">Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each consumos as c}
                                <tr class="border-b border-hotel-border/20 last:border-0">
                                    <td class="px-6 py-3 text-hotel-text-secondary text-xs">{new Date(c.fecha_hora).toLocaleDateString()}</td>
                                    <td class="px-6 py-3 text-xs text-hotel-text-secondary">{c.tipo_consumo}</td>
                                    <td class="px-6 py-3 hidden sm:table-cell text-xs text-hotel-text-secondary">
                                        {c.producto_nombre || '—'}
                                    </td>
                                    <td class="px-6 py-3 text-xs text-hotel-text-secondary">{c.descripcion}</td>
                                    <td class="px-6 py-3 text-right font-medium text-hotel-text-primary">${c.total}</td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            {:else}
                <div class="px-6 py-8 text-center">
                    <p class="text-xs text-hotel-text-tertiary">Sin consumos registrados</p>
                </div>
            {/if}
        </div>

        <!-- Pagos -->
        <div class="bg-hotel-surface rounded-2xl border border-hotel-border overflow-hidden">
            <div class="px-6 py-4 border-b border-hotel-border/50 flex justify-between items-center">
                <h3 class="text-sm font-semibold text-hotel-text-primary">Pagos</h3>
                <span class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary">
                    {pagos.length} {(pagos.length === 1 ? 'registro' : 'registros')}
                </span>
            </div>

            {#if pagos.length > 0}
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead>
                            <tr class="text-[10px] uppercase text-hotel-text-tertiary text-left border-b border-hotel-border/30">
                                <th class="px-6 py-3 font-medium">Fecha</th>
                                <th class="px-6 py-3 font-medium">Método</th>
                                <th class="px-6 py-3 font-medium hidden sm:table-cell">Referencia</th>
                                <th class="px-6 py-3 font-medium text-right">Monto</th>
                            </tr>
                        </thead>
                        <tbody>
                            {#each pagos as p}
                                <tr class="border-b border-hotel-border/20 last:border-0">
                                    <td class="px-6 py-3 text-hotel-text-secondary text-xs">{new Date(p.fecha_hora).toLocaleDateString()}</td>
                                    <td class="px-6 py-3 text-xs text-hotel-text-secondary">{p.metodo_pago}</td>
                                    <td class="px-6 py-3 hidden sm:table-cell text-xs text-hotel-text-secondary">{p.numero_referencia || '—'}</td>
                                    <td class="px-6 py-3 text-right font-medium text-hotel-text-primary">${p.monto}</td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                </div>
            {:else}
                <div class="px-6 py-8 text-center">
                    <p class="text-xs text-hotel-text-tertiary">Sin pagos registrados</p>
                </div>
            {/if}
        </div>
    </div>
{/if}

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
