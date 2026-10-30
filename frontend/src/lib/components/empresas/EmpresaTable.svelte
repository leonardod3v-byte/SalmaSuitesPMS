<script lang="ts">
    import { goto } from '$app/navigation';
    import type { Empresa } from '$lib/types/empresa';

    let {
        empresas,
    }: {
        empresas: Empresa[];
    } = $props();

    function verDetalle(id: number) {
        goto(`/empresas?id=${id}`);
    }
</script>

<div class="overflow-x-auto custom-scrollbar">
    <table class="w-full text-sm">
        <thead>
            <tr class="border-b border-hotel-border text-[10px] uppercase tracking-widest text-hotel-text-tertiary text-left">
                <th class="p-3 font-bold">Empresa</th>
                <th class="p-3 font-bold hidden sm:table-cell">RIF</th>
                <th class="p-3 font-bold hidden md:table-cell">Contacto</th>
                <th class="p-3 font-bold text-right"></th>
            </tr>
        </thead>
        <tbody>
            {#each empresas as e (e.id)}
                <tr class="border-b border-hotel-border/30 hover:bg-hotel-surface-hover transition-colors cursor-pointer" onclick={() => verDetalle(e.id)}>
                    <td class="p-3">
                        <div>
                            <p class="font-bold text-hotel-text-primary">{e.nombre}</p>
                            <p class="text-[10px] text-hotel-text-tertiary sm:hidden">{e.rif}</p>
                        </div>
                    </td>
                    <td class="p-3 text-hotel-text-secondary hidden sm:table-cell">{e.rif}</td>
                    <td class="p-3 hidden md:table-cell">
                        <div class="text-hotel-text-secondary text-xs space-y-0.5">
                            <p>{e.telefono || '—'}</p>
                            <p class="text-hotel-text-tertiary text-[10px]">{e.email || '—'}</p>
                        </div>
                    </td>
                    <td class="p-3 text-right">
                        <button onclick={(ev) => { ev.stopPropagation(); verDetalle(e.id); }} class="text-hotel-gold hover:text-hotel-gold-light text-[10px] font-bold uppercase tracking-wider transition-colors">
                            Editar
                        </button>
                    </td>
                </tr>
            {:else}
                <tr>
                    <td colspan="4" class="p-10 text-center text-hotel-text-tertiary uppercase tracking-widest text-xs">Sin empresas registradas</td>
                </tr>
            {/each}
        </tbody>
    </table>
</div>
