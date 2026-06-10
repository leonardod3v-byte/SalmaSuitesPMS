<script lang="ts">
    import { toast } from '$lib/stores/toast';
    import Button from '$components/ui/Button.svelte';
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
        <div class="flex items-center gap-2 p-3 rounded-xl bg-hotel-error/10 border border-hotel-error/20 text-hotel-error-light text-sm">{error}</div>
    {/if}

    <div class="p-5 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-3">
        <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Confirmar Check‑in</p>
        <p class="text-sm text-hotel-text-secondary">Habitación <span class="font-bold text-hotel-text-primary">#{reservacion.habitacion_numero}</span></p>
        <p class="text-sm text-hotel-text-secondary">Huésped: <span class="font-bold text-hotel-text-primary">{reservacion.huesped_nombre}</span></p>
        <p class="text-sm text-hotel-text-secondary">Entrada: <span class="font-bold text-hotel-text-primary">{reservacion.fecha_entrada}</span></p>
    </div>

    <div class="flex gap-3">
        <Button variant="gold" onclick={confirmar} loading={loading}>Confirmar Check‑in</Button>
        <Button variant="ghost" onclick={onclose}>Cancelar</Button>
    </div>
</div>