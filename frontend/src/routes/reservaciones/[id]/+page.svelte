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
        marcarNoshow,
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

    let {
        onclose,
    }: {
        onclose: () => void;
    } = $props();

    onMount(async () => {
        const id = Number($page.params.id);
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
    });

    async function refrescar() {
        if (!reservacion) return;
        try {
            const [r, c, p] = await Promise.all([
                fetchReservacion(reservacion.id),
                fetchConsumos(reservacion.id),
                fetchPagos(reservacion.id),
            ]);
            reservacion = r;
            consumos = c;
            pagos = p;
        } catch { }
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
    <PageHeader title="Reserva #{reservacion.id}" subtitle="{reservacion.estado} — {reservacion.huesped_nombre}">
        <div class="flex gap-2">
            {#if reservacion.estado === 'Confirmada'}
                <Button variant="success" size="md" onclick={() => mostrarCheckin = true}>Check‑in</Button>
                <Button variant="danger" size="md" onclick={cancelar}>Cancelar</Button>
            {:else if reservacion.estado === 'EnCurso'}
                <Button variant="gold" size="md" onclick={() => mostrarCheckout = true}>Check‑out</Button>
                <Button variant="secondary" size="md" onclick={() => mostrarConsumo = true}>+ Consumo</Button>
                <Button variant="secondary" size="md" onclick={() => mostrarPago = true}>+ Pago</Button>
            {/if}
            <Button variant="secondary" size="md" onclick={() => window.print()}>
                <span class="flex items-center gap-1.5">
                    <Icon name="export" class="w-4 h-4" />
                    Imprimir Hoja
                </span>
            </Button>
            <Button variant="ghost" size="md" onclick={volver}>Volver</Button>
        </div>
    </PageHeader>

    <div class="space-y-6">
        <!-- Datos -->
        <div class="p-5 rounded-2xl bg-hotel-surface border border-hotel-border grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
            <div><p class="text-[10px] uppercase text-hotel-text-tertiary">Habitación</p><p class="font-bold">#{reservacion.habitacion_numero}</p></div>
            <div><p class="text-[10px] uppercase text-hotel-text-tertiary">Entrada</p><p class="font-bold">{reservacion.fecha_entrada}</p></div>
            <div><p class="text-[10px] uppercase text-hotel-text-tertiary">Salida</p><p class="font-bold">{reservacion.fecha_salida}</p></div>
            <div><p class="text-[10px] uppercase text-hotel-text-tertiary">Noches</p><p class="font-bold">{reservacion.numero_noches}</p></div>
            <div><p class="text-[10px] uppercase text-hotel-text-tertiary">Total Hab.</p><p class="font-bold text-hotel-gold">${reservacion.total_habitacion}</p></div>
            <div><p class="text-[10px] uppercase text-hotel-text-tertiary">Consumos</p><p class="font-bold">${reservacion.monto_total_consumos}</p></div>
            <div><p class="text-[10px] uppercase text-hotel-text-tertiary">Pagado</p><p class="font-bold text-hotel-success-light">${reservacion.monto_pagado}</p></div>
            <div><p class="text-[10px] uppercase text-hotel-text-tertiary">Saldo</p><p class="font-bold text-hotel-error-light">${reservacion.saldo_pendiente}</p></div>
        </div>

        <!-- Consumos -->
        <div class="p-5 rounded-2xl bg-hotel-surface border border-hotel-border">
            <h3 class="font-display text-lg text-hotel-text-primary mb-4">Consumos</h3>
            {#if consumos.length > 0}
                <table class="w-full text-xs">
                    <thead><tr class="text-[10px] uppercase text-hotel-text-tertiary text-left"><th class="p-2">Fecha</th><th class="p-2">Tipo</th><th class="p-2">Descripción</th><th class="p-2 text-right">Total</th></tr></thead>
                    <tbody>
                        {#each consumos as c}
                            <tr class="border-t border-hotel-border/30"><td class="p-2">{new Date(c.fecha_hora).toLocaleDateString()}</td><td class="p-2">{c.tipo_consumo}</td><td class="p-2">{c.descripcion}</td><td class="p-2 text-right font-bold">${c.total}</td></tr>
                        {/each}
                    </tbody>
                </table>
            {:else}
                <p class="text-xs text-hotel-text-tertiary">Sin consumos.</p>
            {/if}
        </div>

        <!-- Pagos -->
        <div class="p-5 rounded-2xl bg-hotel-surface border border-hotel-border">
            <h3 class="font-display text-lg text-hotel-text-primary mb-4">Pagos</h3>
            {#if pagos.length > 0}
                <table class="w-full text-xs">
                    <thead><tr class="text-[10px] uppercase text-hotel-text-tertiary text-left"><th class="p-2">Fecha</th><th class="p-2">Método</th><th class="p-2 text-right">Monto</th></tr></thead>
                    <tbody>
                        {#each pagos as p}
                            <tr class="border-t border-hotel-border/30"><td class="p-2">{new Date(p.fecha_hora).toLocaleDateString()}</td><td class="p-2">{p.metodo_pago}</td><td class="p-2 text-right font-bold text-hotel-gold">${p.monto}</td></tr>
                        {/each}
                    </tbody>
                </table>
            {:else}
                <p class="text-xs text-hotel-text-tertiary">Sin pagos.</p>
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