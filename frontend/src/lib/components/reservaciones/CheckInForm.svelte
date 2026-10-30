<script lang="ts">
    import { onMount } from 'svelte';
    import { toast } from '$lib/stores/toast';
    import Button from '$components/ui/Button.svelte';
    import Icon from '$components/ui/Icons.svelte';
    import { realizarCheckin } from '$lib/services/reservaciones';
    import type { Reservacion } from '$lib/types/reservacion';

    let {
        reservacion,
        onclose,
    }: {
        reservacion: Reservacion;
        onclose: () => void;
    } = $props();

    let loading = $state(false);
    let error = $state('');

    let horaActual = $state(new Date().toLocaleTimeString('es-VE', { hour: '2-digit', minute: '2-digit' }));

    async function confirmar() {
        loading = true;
        error = '';
        try {
            await realizarCheckin(reservacion.id);
            toast.success('Check‑in realizado correctamente.');
            onclose();
        } catch (e: any) {
            error = e.message || 'Error al hacer check‑in';
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

    <div class="p-5 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
        <div class="flex items-center gap-3 border-b border-hotel-border/50 pb-4 mb-4">
            <div class="w-12 h-12 rounded-full bg-hotel-gold/10 flex items-center justify-center text-hotel-gold">
                <Icon name="user" class="w-6 h-6" />
            </div>
            <div>
                <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Confirmar Check‑in</p>
                <p class="text-lg font-display italic text-hotel-text-primary">{reservacion.huesped_nombre}</p>
            </div>
        </div>

        <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
                <p class="text-[10px] uppercase text-hotel-text-tertiary mb-1">Habitación</p>
                <p class="font-bold text-hotel-text-primary text-lg">#{reservacion.habitacion_numero}</p>
            </div>
            <div>
                <p class="text-[10px] uppercase text-hotel-text-tertiary mb-1">Noches</p>
                <p class="font-bold text-hotel-text-primary">{reservacion.numero_noches} noches</p>
            </div>
            <div>
                <p class="text-[10px] uppercase text-hotel-text-tertiary mb-1">Fecha de Entrada</p>
                <p class="font-bold text-hotel-text-primary">{reservacion.fecha_entrada}</p>
            </div>
            <div>
                <p class="text-[10px] uppercase text-hotel-text-tertiary mb-1">Fecha de Salida</p>
                <p class="font-bold text-hotel-text-primary">{reservacion.fecha_salida}</p>
            </div>
        </div>

        <div class="flex items-center gap-2 p-3 rounded-xl bg-hotel-info/5 border border-hotel-info/20 text-xs text-hotel-info-light mt-4">
            <Icon name="clock" class="w-4 h-4 shrink-0" />
            Se registrará la entrada con la hora actual: <b class="ml-1">{horaActual}</b>
        </div>
    </div>

    <div class="flex gap-3">
        <Button variant="gold" onclick={confirmar} loading={loading} fullWidth>
            Confirmar Check‑in
        </Button>
        <Button variant="ghost" onclick={onclose}>Cancelar</Button>
    </div>
</div>
