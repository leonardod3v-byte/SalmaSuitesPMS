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
</script>

<section class="bg-hotel-surface rounded-2xl p-6 border border-hotel-border flex flex-col shadow-hotel-sm h-[400px]">
    <h3 class="font-display text-xl text-hotel-text-primary mb-6 italic shrink-0">Actividad</h3>
    <div class="flex-1 overflow-y-auto pr-2 custom-scrollbar min-h-0">
        {#each actividades as act, i}
            <div class="flex gap-4 group relative pb-6 last:pb-0">
                {#if i !== actividades.length - 1}
                    <div class="absolute left-[11px] top-7 w-px h-full bg-hotel-border/50 group-hover:bg-hotel-gold/20 transition-colors"></div>
                {/if}
                <div class="relative z-10">
                    <div class="w-[22px] h-[22px] rounded-full bg-hotel-bg border border-hotel-gold/30 flex items-center justify-center group-hover:border-hotel-gold transition-all duration-300 shadow-sm">
                        <div class="w-1.5 h-1.5 rounded-full bg-hotel-gold/50 group-hover:bg-hotel-gold animate-pulse"></div>
                    </div>
                </div>
                <div class="flex-1 bg-hotel-bg/20 p-3 rounded-xl border border-transparent group-hover:border-hotel-border/30 group-hover:bg-hotel-surface-hover transition-all duration-300">
                    <p class="text-xs text-hotel-text-secondary leading-relaxed">
                        <span class="text-hotel-gold font-bold">{act.tipo}</span>: {act.descripcion}
                    </p>
                    <div class="mt-2 text-[9px] text-hotel-text-tertiary font-mono opacity-60">
                        {new Date(act.fecha_hora).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        <span class="ml-2 text-hotel-gold/60">{act.usuario}</span>
                    </div>
                </div>
            </div>
        {:else}
            <p class="text-[10px] text-hotel-text-tertiary text-center italic py-10 uppercase tracking-widest">Sin registros recientes</p>
        {/each}
    </div>
</section>