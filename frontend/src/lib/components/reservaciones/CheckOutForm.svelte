<script lang="ts">
    import { onMount } from 'svelte';
    import { toast } from '$lib/stores/toast';
    import Button from '$components/ui/Button.svelte';
    import { fetchResumenCheckout, realizarCheckout, registrarPago } from '$lib/services/reservaciones';
    import type { Reservacion, ResumenCheckout } from '$lib/types/reservacion';

    let {
        reservacion,
        onclose,
    }: {
        reservacion: Reservacion;
        onclose: () => void;
    } = $props();

    let loading = $state(false);
    let error = $state('');
    let resumen = $state<ResumenCheckout | null>(null);
    let montoPago = $state(0);
    let metodoPago = $state<'Efectivo' | 'Tarjeta' | 'PagoMovil'>('Efectivo');

    let saldoPendiente = $derived(parseFloat(resumen?.saldo_pendiente || '0'));

    onMount(async () => {
        try {
            resumen = await fetchResumenCheckout(reservacion.id);
        } catch (e: any) {
            error = e.message;
        }
    });

    async function confirmar() {
        loading = true;
        error = '';
        try {
            if (saldoPendiente > 0 && reservacion.modalidad_pago !== 'Crédito') {
                await registrarPago(reservacion.id, {
                    monto: saldoPendiente,
                    metodo_pago: metodoPago,
                });
            }
            await realizarCheckout(reservacion.id);
            toast.success('Check‑out realizado correctamente.');
            onclose();
        } catch (e: any) {
            error = e.message || 'Error al hacer check‑out';
        } finally {
            loading = false;
        }
    }
</script>

<div class="space-y-6">
    {#if error}
        <div class="flex items-center gap-2 p-3 rounded-xl bg-hotel-error/10 border border-hotel-error/20 text-hotel-error-light text-sm">{error}</div>
    {/if}

    {#if resumen}
        <div class="p-5 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-3">
            <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Resumen de Cuenta</p>
            <div class="grid grid-cols-2 gap-3 text-sm">
                <p class="text-hotel-text-secondary">Habitación:</p>
                <p class="font-bold text-hotel-text-primary text-right">${resumen.total_habitacion}</p>
                <p class="text-hotel-text-secondary">Consumos:</p>
                <p class="font-bold text-hotel-text-primary text-right">${resumen.total_consumos}</p>
                <p class="text-hotel-text-secondary">Total:</p>
                <p class="font-bold text-hotel-gold text-right">${resumen.total_final}</p>
                <p class="text-hotel-text-secondary">Pagado:</p>
                <p class="font-bold text-hotel-success-light text-right">${resumen.monto_pagado}</p>
                <p class="text-hotel-text-secondary">Saldo:</p>
                <p class="font-bold text-hotel-error-light text-right">${resumen.saldo_pendiente}</p>
            </div>
        </div>

        {#if saldoPendiente > 0 && reservacion.modalidad_pago !== 'Crédito'}
            <div class="p-5 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-3">
                <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Pagar saldo pendiente</p>
                <p class="text-sm text-hotel-text-secondary">Monto: <span class="font-bold text-hotel-gold">${saldoPendiente.toFixed(2)}</span></p>
            </div>
        {/if}
    {/if}

    <div class="flex gap-3">
        <Button variant="gold" onclick={confirmar} loading={loading}>Confirmar Check‑out</Button>
        <Button variant="ghost" onclick={onclose}>Cancelar</Button>
    </div>
</div>