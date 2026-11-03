<script lang="ts">
    import { goto } from '$app/navigation';
    import type { Huesped } from '$lib/types/huesped';

    let {
        huespedes,
    }: {
        huespedes: Huesped[];
    } = $props();

    function verDetalle(id: number) {
        goto(`/huespedes/${id}`);
    }
</script>

<div class="overflow-x-auto custom-scrollbar">
    <table class="w-full text-sm">
        <thead>
            <tr class="border-b border-hotel-border text-[10px] uppercase tracking-widest text-hotel-text-tertiary text-left">
                <th class="p-3 font-bold">Huésped</th>
                <th class="p-3 font-bold hidden md:table-cell">Ocupación</th>
                <th class="p-3 font-bold hidden lg:table-cell">Contacto</th>
                <th class="p-3 font-bold">Categoría</th>
                <th class="p-3 font-bold hidden xl:table-cell">Crédito</th>
                <th class="p-3 font-bold text-right"></th>
            </tr>
        </thead>
        <tbody>
            {#each huespedes as h (h.id)}
                <tr class="border-b border-hotel-border/30 hover:bg-hotel-surface-hover transition-colors cursor-pointer" onclick={() => verDetalle(h.id)}>
                    <td class="p-3">
                        <div class="flex items-center gap-3">
                            <div class="w-9 h-9 rounded-lg flex items-center justify-center text-xs font-bold shrink-0"
                                style="background-color: {(h.ocupacion_detalle?.color || '#9E9E9E')}15; color: {h.ocupacion_detalle?.color || '#9E9E9E'}">
                                {h.nombres.charAt(0)}{h.apellidos.charAt(0)}
                            </div>
                            <div>
                                <p class="font-bold text-hotel-text-primary">{h.nombres} {h.apellidos}</p>
                                <p class="text-[10px] text-hotel-text-tertiary">{h.tipo_documento}-{h.numero_documento}</p>
                            </div>
                        </div>
                    </td>
                    <td class="p-3 hidden md:table-cell">
                        {#if h.ocupacion_detalle}
                            <span class="inline-flex items-center gap-1.5 px-2 py-1 rounded-lg text-[10px] font-bold"
                                style="background-color: {h.ocupacion_detalle.color}15; color: {h.ocupacion_detalle.color}">
                                <span class="w-1.5 h-1.5 rounded-full" style="background-color: {h.ocupacion_detalle.color}"></span>
                                {h.ocupacion_detalle.nombre}
                            </span>
                        {:else}
                            <span class="text-[10px] text-hotel-text-tertiary">—</span>
                        {/if}
                    </td>
                    <td class="p-3 hidden lg:table-cell">
                        <div class="text-hotel-text-secondary text-xs space-y-0.5">
                            <p>{h.telefono}</p>
                            <p class="text-hotel-text-tertiary text-[10px]">{h.email || '—'}</p>
                        </div>
                    </td>
                    <td class="p-3">
                        {#if h.categoria === 'VIP'}
                            <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-hotel-vip/10 text-hotel-vip-light border border-hotel-vip/20">
                                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
                                VIP
                            </span>
                        {:else}
                            <span class="text-[10px] text-hotel-text-tertiary">Estándar</span>
                        {/if}
                    </td>
                    <td class="p-3 hidden xl:table-cell">
                        {#if h.credito_autorizado}
                            <span class="text-hotel-success-light text-[10px] font-bold">${h.limite_credito ?? '∞'}</span>
                        {:else}
                            <span class="text-hotel-text-tertiary text-[10px]">—</span>
                        {/if}
                    </td>
                    <td class="p-3 text-right">
                        <button onclick={(e) => { e.stopPropagation(); verDetalle(h.id); }} class="text-hotel-gold hover:text-hotel-gold-light text-[10px] font-bold uppercase tracking-wider transition-colors">
                            Editar
                        </button>
                    </td>
                </tr>
            {:else}
                <tr>
                    <td colspan="6" class="p-10 text-center text-hotel-text-tertiary uppercase tracking-widest text-xs">Sin huéspedes registrados</td>
                </tr>
            {/each}
        </tbody>
    </table>
</div>
