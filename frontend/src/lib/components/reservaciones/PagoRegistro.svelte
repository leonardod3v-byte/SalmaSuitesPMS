<script lang="ts">
    import { onMount } from 'svelte';
    import { toast } from '$lib/stores/toast';
    import InputHotel from '$components/ui/Input.svelte';
    import Select from '$components/ui/Select.svelte';
    import Button from '$components/ui/Button.svelte';
    import { registrarPago, fetchSaldo } from '$lib/services/reservaciones';
    import type { ResumenCheckout } from '$lib/types/reservacion';

    let {
        reservaId,
        onclose,
    }: {
        reservaId: number;
        onclose: () => void;
    } = $props();

    let loading = $state(false);
    let resumen = $state<ResumenCheckout | null>(null);
    let errorResumen = $state('');

    let monto = $state(0);
    let metodoPago = $state<'Efectivo' | 'Tarjeta' | 'PagoMovil'>('Efectivo');
    let numeroReferencia = $state('');

    let saldoPendiente = $state(0);

    const metodos = [
        { value: 'Efectivo', label: 'Efectivo' },
        { value: 'Tarjeta', label: 'Tarjeta' },
        { value: 'PagoMovil', label: 'Pago Móvil' },
    ];

    onMount(async () => {
        try {
            const r = await fetchSaldo(reservaId);
            resumen = r;
            saldoPendiente = parseFloat(r.saldo_pendiente) || 0;
            monto = saldoPendiente;
        } catch (e: any) {
            errorResumen = e.message || 'Error al cargar el saldo.';
        }
    });

    function formatNumber(val: number): string {
        return isNaN(val) ? '0.00' : val.toFixed(2);
    }

    async function guardar() {
        if (monto <= 0) {
            toast.error('El monto debe ser mayor a 0.');
            return;
        }
        if (monto > saldoPendiente) {
            toast.error(`El monto no puede exceder el saldo pendiente ($${formatNumber(saldoPendiente)}).`);
            return;
        }
        if (metodoPago !== 'Efectivo' && !numeroReferencia.trim()) {
            toast.error('El número de referencia es obligatorio para este método de pago.');
            return;
        }

        loading = true;
        try {
            await registrarPago(reservaId, {
                monto,
                metodo_pago: metodoPago,
                numero_referencia: numeroReferencia,
            });
            toast.success('Pago registrado correctamente.');
            onclose();
        } catch (e: any) {
            toast.error(e.message || 'Error al registrar pago.');
        } finally {
            loading = false;
        }
    }
</script>

<div class="space-y-5">
    {#if errorResumen}
        <div class="flex items-center gap-2 p-3 rounded-xl bg-hotel-error/10 border border-hotel-error/20 text-hotel-error-light text-sm">
            {errorResumen}
        </div>
    {:else if resumen}
        <!-- Estado de Cuenta -->
        <div class="p-4 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-3">
            <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Estado de Cuenta</p>

            <div class="grid grid-cols-2 gap-3 text-sm">
                <div>
                    <p class="text-[10px] uppercase text-hotel-text-tertiary">Total Habitación</p>
                    <p class="font-bold text-hotel-text-primary">${resumen.total_habitacion}</p>
                </div>
                <div>
                    <p class="text-[10px] uppercase text-hotel-text-tertiary">Total Consumos</p>
                    <p class="font-bold text-hotel-text-primary">${resumen.total_consumos}</p>
                </div>
                <div>
                    <p class="text-[10px] uppercase text-hotel-text-tertiary">Total General</p>
                    <p class="font-bold text-hotel-gold text-lg">${resumen.total_final}</p>
                </div>
                <div>
                    <p class="text-[10px] uppercase text-hotel-text-tertiary">Ya Pagado</p>
                    <p class="font-bold text-hotel-success-light">${resumen.monto_pagado}</p>
                </div>
            </div>

            <div class="p-3 rounded-xl {saldoPendiente > 0 ? 'bg-hotel-error/5 border border-hotel-error/20' : 'bg-hotel-success/5 border border-hotel-success/20'}">
                <div class="flex items-center justify-between">
                    <span class="text-sm font-bold {saldoPendiente > 0 ? 'text-hotel-error-light' : 'text-hotel-success-light'}">
                        {saldoPendiente > 0 ? 'Saldo Pendiente' : 'Cuenta Saldada'}
                    </span>
                    <span class="text-xl font-bold {saldoPendiente > 0 ? 'text-hotel-error-light' : 'text-hotel-success-light'}">
                        ${formatNumber(saldoPendiente)}
                    </span>
                </div>
            </div>
        </div>

        <!-- Formulario de Pago -->
        <div class="p-4 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
            <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Registrar Pago</p>

            <InputHotel label="Monto a pagar ($)" type="number" bind:value={monto} />

            {#if monto > saldoPendiente}
                <p class="text-xs text-hotel-error-light flex items-center gap-1.5">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                    El monto excede el saldo pendiente (${formatNumber(saldoPendiente)})
                </p>
            {/if}

            {#if saldoPendiente === 0}
                <p class="text-xs text-hotel-success-light flex items-center gap-1.5">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                    Esta cuenta ya está saldada.
                </p>
            {/if}

            <Select label="Método de pago" options={metodos} bind:value={metodoPago} />

            {#if metodoPago !== 'Efectivo'}
                <InputHotel label="Nº Referencia o Voucher" bind:value={numeroReferencia} placeholder="Ej: 123456" />
            {/if}
        </div>
    {/if}

    <div class="flex gap-3 pt-4 border-t border-hotel-border/50">
        <Button variant="gold" onclick={guardar} loading={loading} fullWidth>
            Pagar
        </Button>
        <Button variant="ghost" onclick={onclose}>Cancelar</Button>
    </div>
</div>