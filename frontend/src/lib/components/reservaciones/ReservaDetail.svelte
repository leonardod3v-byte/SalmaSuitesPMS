<script lang="ts">
    import { goto } from '$app/navigation';
    import Button from '$components/ui/Button.svelte';
    import type { Reservacion } from '$lib/types/reservacion';

    let {
        reservacion,
    }: {
        reservacion: Reservacion;
    } = $props();

    const estadoClases: Record<string, string> = {
        'Confirmada': 'bg-hotel-info/10 text-hotel-info-light border-hotel-info/30',
        'EnCurso': 'bg-hotel-gold/10 text-hotel-gold-light border-hotel-gold/30',
        'Finalizada': 'bg-hotel-success/10 text-hotel-success-light border-hotel-success/30',
        'Cancelada': 'bg-hotel-error/10 text-hotel-error-light border-hotel-error/30',
        'NoShow': 'bg-hotel-error/10 text-hotel-error-light border-hotel-error/30',
    };

    function verDetalle() {
        goto(`/reservaciones/${reservacion.id}`);
    }
</script>

<div
    onclick={verDetalle}
    onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') verDetalle(); }}
    role="button"
    tabindex="0"
    class="bg-hotel-surface rounded-2xl border border-hotel-border p-5 transition-all hover:border-hotel-gold/50 cursor-pointer"
>
    <div class="flex justify-between items-start mb-3">
        <div>
            <p class="font-bold text-hotel-text-primary">Reserva #{reservacion.id}</p>
            <p class="text-xs text-hotel-text-secondary">{reservacion.huesped_nombre}</p>
        </div>
        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border {estadoClases[reservacion.estado] || ''}">{reservacion.estado}</span>
    </div>
    <div class="grid grid-cols-2 gap-2 text-xs text-hotel-text-secondary">
        <p>Hab: <span class="font-bold text-hotel-text-primary">#{reservacion.habitacion_numero}</span></p>
        <p>Entrada: <span class="font-bold text-hotel-text-primary">{reservacion.fecha_entrada}</span></p>
        <p>Salida: <span class="font-bold text-hotel-text-primary">{reservacion.fecha_salida}</span></p>
        <p>Total: <span class="font-bold text-hotel-gold">${reservacion.monto_total_final}</span></p>
    </div>
</div>