<script lang="ts">
    interface Actividad {
        id: number;
        fecha_hora: string;
        usuario: string;
        tipo: string;
        descripcion: string;
        id_referencia: string;
    }

    interface Props {
        actividades: Actividad[];
    }

    let { actividades }: Props = $props();

    function formatearFecha(fechaISO: string): string {
        const fecha = new Date(fechaISO);
        const ahora = new Date();
        const diffMs = ahora.getTime() - fecha.getTime();
        const diffMin = Math.floor(diffMs / 60000);
        const diffHoras = Math.floor(diffMin / 60);

        if (fecha.toDateString() === ahora.toDateString()) {
            if (diffMin < 1) return 'Ahora';
            if (diffMin < 60) return `${diffMin} min`;
            if (diffHoras < 24) return `${diffHoras}h`;
        }

        const ayer = new Date(ahora);
        ayer.setDate(ayer.getDate() - 1);
        if (fecha.toDateString() === ayer.toDateString()) {
            return `Ayer ${fecha.toLocaleTimeString('es-VE', { hour: '2-digit', minute: '2-digit' })}`;
        }

        return fecha.toLocaleDateString('es-VE', { day: '2-digit', month: 'short' });
    }

    function getColorPunto(tipo: string): string {
        const t = tipo.toLowerCase();
        if (t.includes('check-in') || t.includes('check‑in')) return 'bg-hotel-success';
        if (t.includes('check-out') || t.includes('check‑out')) return 'bg-hotel-info';
        if (t.includes('pago') || t.includes('cierre')) return 'bg-hotel-gold';
        if (t.includes('cancelación') || t.includes('no-show')) return 'bg-hotel-error';
        if (t.includes('consumo')) return 'bg-purple-400';
        return 'bg-hotel-text-tertiary';
    }

    function getHoverColor(tipo: string): string {
        const t = tipo.toLowerCase();
        if (t.includes('check-in') || t.includes('check‑in')) return 'hover:bg-hotel-success/5';
        if (t.includes('check-out') || t.includes('check‑out')) return 'hover:bg-hotel-info/5';
        if (t.includes('pago') || t.includes('cierre')) return 'hover:bg-hotel-gold/5';
        if (t.includes('cancelación') || t.includes('no-show')) return 'hover:bg-hotel-error/5';
        if (t.includes('consumo')) return 'hover:bg-purple-400/5';
        return 'hover:bg-hotel-text-tertiary/5';
    }
</script>

<section class="bg-hotel-surface rounded-2xl p-6 border border-hotel-border h-100 flex flex-col">
    <div class="flex justify-between items-baseline mb-4 shrink-0">
        <h3 class="font-display text-lg text-hotel-text-primary">Actividad</h3>
        <p class="text-[10px] uppercase tracking-[0.2em] text-hotel-text-tertiary">{actividades.length} registros</p>
    </div>

    <div class="flex-1 overflow-y-auto pr-1 custom-scrollbar min-h-0 -mr-1">
        {#if actividades.length === 0}
            <p class="text-xs text-hotel-text-tertiary text-center py-8">Sin actividad reciente</p>
        {:else}
            <ul class="space-y-1">
                {#each actividades as act}
                    <li class="group flex gap-3 items-start py-2 px-2 -mx-2 rounded-md transition-colors {getHoverColor(act.tipo)}">
                        <div class="pt-1.5 shrink-0">
                            <div class="w-1.5 h-1.5 rounded-full {getColorPunto(act.tipo)}"></div>
                        </div>
                        <div class="flex-1 min-w-0">
                            <div class="flex items-baseline justify-between gap-2 mb-0.5">
                                <p class="text-[11px] font-bold uppercase tracking-wider text-hotel-text-primary truncate">
                                    {act.tipo}
                                </p>
                                <span class="text-[10px] text-hotel-text-tertiary font-mono shrink-0 tabular-nums">
                                    {formatearFecha(act.fecha_hora)}
                                </span>
                            </div>
                            <p class="text-xs text-hotel-text-secondary leading-snug line-clamp-2">
                                {act.descripcion}
                            </p>
                            <p class="text-[10px] text-hotel-text-tertiary mt-1 font-medium">
                                {act.usuario}
                            </p>
                        </div>
                    </li>
                {/each}
            </ul>
        {/if}
    </div>
</section>
