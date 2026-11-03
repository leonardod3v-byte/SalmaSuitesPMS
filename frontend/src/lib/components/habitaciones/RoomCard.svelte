<script lang="ts">
    import { goto } from '$app/navigation';
    import { toast } from '$lib/stores/toast';
    import { cambiarEstadoHabitacion } from '$lib/services/habitaciones';
    import type { Habitacion } from '$lib/types/habitacion';
    import RoomStatusBadge from './RoomStatusBadge.svelte';

    let {
        habitacion,
        onchange = () => {},
    }: {
        habitacion: Habitacion;
        onchange?: () => void;
    } = $props();

    const MEDIA_URL = import.meta.env.VITE_MEDIA_URL ?? 'http://localhost:8000';

    const imagenSrc = $derived(
        habitacion.imagen_url
            ? `${MEDIA_URL}${habitacion.imagen_url}`
            : 'https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&q=80&w=600'
    );

    const precioFormateado = $derived(
        parseFloat(habitacion.precio_por_noche).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    );

    function verDetalle() {
        goto(`/habitaciones/${habitacion.id}`);
    }

    async function marcarDisponible(e: MouseEvent) {
        e.stopPropagation();
        try {
            await cambiarEstadoHabitacion(habitacion.id, 'Disponible');
            toast.success('Habitación marcada como Disponible.');
            onchange();
        } catch (err: any) {
            toast.error(err.message || 'Error al cambiar estado.');
        }
    }

    async function enviarMantenimiento(e: MouseEvent) {
        e.stopPropagation();
        try {
            await cambiarEstadoHabitacion(habitacion.id, 'Mantenimiento');
            toast.success('Habitación enviada a Mantenimiento.');
            onchange();
        } catch (err: any) {
            toast.error(err.message || 'Error al cambiar estado.');
        }
    }
</script>

<div
    onclick={verDetalle}
    onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') verDetalle(); }}
    role="button"
    tabindex="0"
    class="group relative flex flex-col w-full bg-hotel-surface border border-hotel-border rounded-2xl overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:border-hotel-gold/50 hover:shadow-hotel-lg focus:outline-none focus:ring-2 focus:ring-hotel-gold/50 text-left cursor-pointer"
    aria-label="Habitación {habitacion.numero}"
>
    <!-- Imagen -->
    <div class="relative h-48 w-full overflow-hidden">
        <img
            src={imagenSrc}
            alt="Habitación {habitacion.categoria_tipo}"
            loading="lazy"
            class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
        />
        <div class="absolute inset-0 bg-linear-to-t from-black/80 via-black/30 to-transparent"></div>

        <!-- Badge de estado -->
        <div class="absolute top-4 right-4">
            <RoomStatusBadge estado={habitacion.estado} />
        </div>

        <!-- Número y piso -->
        <div class="absolute bottom-4 left-4">
            <span class="text-4xl font-display font-bold text-white italic drop-shadow-md">#{habitacion.numero}</span>
            <div class="flex items-center gap-1 mt-1 text-white/80 text-xs">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
                <span>Piso {habitacion.piso}</span>
            </div>
        </div>
    </div>

    <!-- Información -->
    <div class="p-5 flex flex-col gap-4">
        <div class="flex justify-between items-start">
            <div class="flex-1">
                <h3 class="text-sm font-bold text-hotel-text-primary tracking-wide">{habitacion.categoria_tipo}</h3>
                <div class="flex items-center gap-4 mt-2 text-xs text-hotel-text-tertiary">
                    <span class="flex items-center gap-1.5">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
                        {habitacion.capacidad_maxima} pers.
                    </span>
                    <span class="flex items-center gap-1.5">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
                        {habitacion.cantidad_camas} camas
                    </span>
                </div>
            </div>
            <div class="text-right">
                <p class="text-2xl font-bold text-hotel-gold leading-tight">${precioFormateado}</p>
                <p class="text-[10px] text-hotel-text-tertiary uppercase tracking-wider">/ noche</p>
            </div>
        </div>

        <!-- Acciones -->
        <div class="flex gap-2 pt-3 border-t border-hotel-border/60">
            {#if habitacion.estado === 'Limpieza'}
                <button onclick={marcarDisponible} class="flex-1 text-[10px] font-bold uppercase tracking-wider px-3 py-2 rounded-lg bg-hotel-success/10 text-hotel-success-light border border-hotel-success/20 hover:bg-hotel-success/20 transition-all">
                    Marcar Disponible
                </button>
            {:else if habitacion.estado === 'Disponible'}
                <button onclick={enviarMantenimiento} class="flex-1 text-[10px] font-bold uppercase tracking-wider px-3 py-2 rounded-lg bg-orange-500/10 text-orange-400 border border-orange-500/20 hover:bg-orange-500/20 transition-all">
                    Mantenimiento
                </button>
            {/if}
            <span class="flex-1 text-[10px] font-bold uppercase tracking-wider px-3 py-2 rounded-lg bg-hotel-bg/50 text-hotel-text-secondary border border-hotel-border group-hover:border-hotel-gold/50 group-hover:text-hotel-gold transition-all text-center">
                Detalle
            </span>
        </div>
    </div>
</div>
