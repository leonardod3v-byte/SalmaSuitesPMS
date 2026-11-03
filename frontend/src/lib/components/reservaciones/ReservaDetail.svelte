<script lang="ts">
    import { goto } from '$app/navigation';
    import Icon from '$components/ui/Icons.svelte';
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
        'NoShow': 'bg-hotel-text-tertiary/10 text-hotel-text-tertiary border-hotel-text-tertiary/30',
    };

    function formatFecha(fecha: string) {
        const d = new Date(fecha + 'T12:00:00');
        return d.toLocaleDateString('es-VE', { day: '2-digit', month: 'short' });
    }

    function verDetalle() {
        goto(`/reservaciones/${reservacion.id}`);
    }

    let acompanantes = $derived(reservacion.acompanantes || []);
</script>

<div
    onclick={verDetalle}
    onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') verDetalle(); }}
    role="button"
    tabindex="0"
    class="bg-hotel-surface rounded-2xl border border-hotel-border p-5 transition-all hover:border-hotel-gold/50 hover:shadow-hotel-md cursor-pointer flex flex-col h-full"
>
    <!-- Cabecera: Reserva #, Estado y Huésped -->
    <div class="flex justify-between items-start mb-4">
        <div class="flex-1 min-w-0 pr-2">
            <div class="flex items-center gap-2 mb-1">
                <span class="font-display font-bold italic text-lg text-hotel-text-primary">
                    #{reservacion.id}
                </span>
                {#if reservacion.requiere_factura}
                    <span class="px-1.5 py-0.5 rounded text-[8px] font-black uppercase bg-hotel-vip/20 text-hotel-vip-light border border-hotel-vip/30" title="Requiere factura">
                        Factura
                    </span>
                {/if}
            </div>
            <p class="text-sm font-bold text-hotel-text-primary truncate">{reservacion.huesped_nombre}</p>
            {#if reservacion.id_empresa}
                <p class="text-[10px] font-medium text-hotel-text-tertiary uppercase tracking-wider truncate flex items-center gap-1">
                    <Icon name="empresas" class="w-3 h-3" /> Corporativo
                </p>
            {/if}
        </div>
        <span class="px-2.5 py-1 rounded-full text-[9px] font-black uppercase tracking-wider border {estadoClases[reservacion.estado] || ''}">
            {reservacion.estado === 'EnCurso' ? 'En Curso' : reservacion.estado}
        </span>
    </div>

    <!-- Cuerpo: Habitación y Fechas -->
    <div class="flex items-center gap-4 mb-4">
        <div class="w-12 h-12 rounded-xl bg-hotel-bg border border-hotel-border flex items-center justify-center shrink-0">
            <span class="font-display font-black text-lg text-hotel-gold">#{reservacion.habitacion_numero}</span>
        </div>
        <div class="flex-1">
            <div class="flex items-center gap-2 text-xs text-hotel-text-secondary">
                <span class="font-bold text-hotel-text-primary">{formatFecha(reservacion.fecha_entrada)}</span>
                <Icon name="arrow-right" class="w-3 h-3 text-hotel-text-tertiary" />
                <span class="font-bold text-hotel-text-primary">{formatFecha(reservacion.fecha_salida)}</span>
            </div>
            <p class="text-[10px] text-hotel-text-tertiary mt-1 uppercase tracking-wider">
                {reservacion.numero_noches} {reservacion.numero_noches === 1 ? 'noche' : 'noches'}
                {#if acompanantes.length > 0}
                    · {1 + acompanantes.length} pers.
                {/if}
            </p>
        </div>
    </div>

    <!-- Acompañantes -->
    {#if acompanantes.length > 0}
        <div class="mb-3 pt-3 border-t border-hotel-border/50">
            <p class="text-[9px] uppercase tracking-wider text-hotel-text-tertiary mb-2">
                Acompañantes ({acompanantes.length})
            </p>
            <div class="flex flex-wrap gap-1.5">
                {#each acompanantes as a}
                    <div
                        class="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-hotel-bg/60 border border-hotel-border"
                        title="{a.huesped_detalle?.nombres} {a.huesped_detalle?.apellidos} · {a.huesped_detalle?.tipo_documento}-{a.huesped_detalle?.numero_documento}"
                    >
                        <div
                            class="w-1.5 h-1.5 rounded-full"
                            style="background-color: {a.huesped_detalle?.ocupacion_color || '#9E9E9E'}"
                        ></div>
                        <span class="text-[10px] font-bold text-hotel-text-secondary truncate max-w-25">
                            {a.huesped_detalle?.nombres}
                        </span>
                    </div>
                {/each}
            </div>
        </div>
    {/if}

    <!-- Footer: Total y Saldo -->
    <div class="mt-auto pt-3 border-t border-hotel-border/50 flex justify-between items-end">
        <div>
            <p class="text-[9px] uppercase tracking-wider text-hotel-text-tertiary mb-0.5">Total</p>
            <p class="font-bold text-hotel-text-primary text-sm">${reservacion.monto_total_final}</p>
        </div>
        <div class="text-right">
            <p class="text-[9px] uppercase tracking-wider text-hotel-text-tertiary mb-0.5">Saldo</p>
            <p class="font-bold text-sm {parseFloat(reservacion.saldo_pendiente) > 0 ? 'text-hotel-error-light' : 'text-hotel-success-light'}">
                ${reservacion.saldo_pendiente}
            </p>
        </div>
    </div>
</div>
