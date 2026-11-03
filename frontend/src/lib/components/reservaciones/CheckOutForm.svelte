<script lang="ts">
    import { onMount } from 'svelte';
    import { toast } from '$lib/stores/toast';
    import Button from '$components/ui/Button.svelte';
    import Select from '$components/ui/Select.svelte';
    import Icon from '$components/ui/Icons.svelte';
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
    let metodoPago = $state<'Efectivo' | 'Tarjeta' | 'PagoMovil'>('Efectivo');
    let referencia = $state('');

    let saldoPendiente = $derived(parseFloat(resumen?.saldo_pendiente || '0'));
    let requierePago = $derived(saldoPendiente > 0 && reservacion.modalidad_pago !== 'Crédito');

    const metodos = [
        { value: 'Efectivo', label: 'Efectivo' },
        { value: 'Tarjeta', label: 'Tarjeta' },
        { value: 'PagoMovil', label: 'Pago Móvil' },
    ];

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
            if (requierePago) {
                await registrarPago(reservacion.id, {
                    monto: saldoPendiente,
                    metodo_pago: metodoPago,
                    numero_referencia: referencia,
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
        <div class="flex items-center gap-2 p-3 rounded-xl bg-hotel-error/10 border border-hotel-error/20 text-hotel-error-light text-sm">
            <Icon name="alert" class="w-4 h-4 shrink-0" />
            {error}
        </div>
    {/if}

    <!-- Tarjeta de Contexto -->
    <div class="p-4 rounded-2xl bg-hotel-surface border border-hotel-border space-y-3">
        <div class="flex items-center justify-between">
            <div>
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary">Huésped</p>
                <p class="font-bold text-hotel-text-primary">{reservacion.huesped_nombre}</p>
            </div>
            <div class="text-right">
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary">Habitación</p>
                <p class="font-bold text-hotel-text-primary text-lg">#{reservacion.habitacion_numero}</p>
            </div>
        </div>
        <div class="flex gap-4 text-xs text-hotel-text-secondary pt-2 border-t border-hotel-border/50">
            <span>Entrada: {reservacion.fecha_entrada}</span>
            <span>Salida: {reservacion.fecha_salida}</span>
        </div>
    </div>

    {#if resumen}
        <!-- Resumen de Cuenta -->
        <div class="p-5 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
            <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Resumen de Cuenta</p>

            <div class="space-y-2 text-sm">
                <div class="flex justify-between text-hotel-text-secondary">
                    <span>Habitación</span>
                    <span class="font-medium text-hotel-text-primary">${resumen.total_habitacion}</span>
                </div>
                <div class="flex justify-between text-hotel-text-secondary">
                    <span>Consumos</span>
                    <span class="font-medium text-hotel-text-primary">${resumen.total_consumos}</span>
                </div>
                <div class="flex justify-between pt-2 border-t border-hotel-border/50">
                    <span class="font-bold text-hotel-text-primary">Total General</span>
                    <span class="font-bold text-hotel-gold text-lg">${resumen.total_final}</span>
                </div>
                <div class="flex justify-between text-hotel-text-secondary">
                    <span>Ya Pagado</span>
                    <span class="font-medium text-hotel-success-light">- ${resumen.monto_pagado}</span>
                </div>
            </div>

            <!-- Saldo Pendiente Destacado -->
            <div class="p-4 rounded-xl {saldoPendiente > 0 ? 'bg-hotel-error/10 border border-hotel-error/20' : 'bg-hotel-success/10 border border-hotel-success/20'}">
                <div class="flex items-center justify-between">
                    <span class="text-sm font-bold {saldoPendiente > 0 ? 'text-hotel-error-light' : 'text-hotel-success-light'}">
                        {saldoPendiente > 0 ? 'Saldo Pendiente' : 'Cuenta Saldada'}
                    </span>
                    <span class="text-xl font-bold {saldoPendiente > 0 ? 'text-hotel-error-light' : 'text-hotel-success-light'}">
                        ${saldoPendiente.toFixed(2)}
                    </span>
                </div>
            </div>
        </div>

        <!-- Sección de Pago -->
        {#if requierePago}
            <div class="p-5 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
                <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Cobrar Saldo Pendiente</p>

                <Select label="Método de Pago" options={metodos} bind:value={metodoPago} />

                {#if metodoPago !== 'Efectivo'}
                    <div class="space-y-2">
                        <label for="referencia-input" class="block text-sm font-medium text-hotel-text-secondary">Nº Referencia o Voucher</label>
                        <input
                            id="referencia-input"
                            type="text"
                            bind:value={referencia}
                            placeholder="Ej: 123456"
                            class="w-full rounded-lg px-4 py-3 text-sm bg-hotel-bg text-hotel-text-primary border border-hotel-border focus:border-hotel-gold outline-none"
                        />
                    </div>
                {/if}
            </div>
        {/if}
    {/if}

    <div class="flex gap-3 pt-2">
        <Button variant="gold" onclick={confirmar} loading={loading} fullWidth>
            {requierePago ? `Cobrar $${saldoPendiente.toFixed(2)} y Cerrar` : 'Confirmar Check-out'}
        </Button>
        <Button variant="ghost" onclick={onclose}>Cancelar</Button>
    </div>
</div>
