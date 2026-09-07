<script lang="ts">
    import { goto } from '$app/navigation';
    import StockBadge from './StockBadge.svelte';
    import type { Producto } from '$lib/types/producto';

    let {
        productos,
    }: {
        productos: Producto[];
    } = $props();

    function verDetalle(id: number) {
        goto(`/inventario?id=${id}`);
    }
</script>

<div class="overflow-x-auto custom-scrollbar">
    <table class="w-full text-sm">
        <thead>
            <tr class="border-b border-hotel-border text-[10px] uppercase tracking-widest text-hotel-text-tertiary text-left">
                <th class="p-3 font-bold">Producto</th>
                <th class="p-3 font-bold hidden sm:table-cell">Categoría</th>
                <th class="p-3 font-bold hidden md:table-cell">Precio</th>
                <th class="p-3 font-bold">Stock</th>
                <th class="p-3 font-bold hidden lg:table-cell">Estado</th>
            </tr>
        </thead>
        <tbody>
            {#each productos as p (p.id)}
                <tr class="border-b border-hotel-border/30 hover:bg-hotel-surface-hover transition-colors">
                    <td class="p-3">
                        <div>
                            <p class="font-bold text-hotel-text-primary">{p.nombre}</p>
                            <p class="text-[10px] text-hotel-text-tertiary sm:hidden">{p.categoria}</p>
                        </div>
                    </td>
                    <td class="p-3 text-hotel-text-secondary hidden sm:table-cell">{p.categoria}</td>
                    <td class="p-3 text-hotel-gold font-bold hidden md:table-cell">${p.precio_venta}</td>
                    <td class="p-3">
                        <p class="font-bold text-hotel-text-primary">{p.stock_actual}</p>
                        <p class="text-[10px] text-hotel-text-tertiary">min: {p.stock_minimo}</p>
                    </td>
                    <td class="p-3 hidden lg:table-cell">
                        <StockBadge estado={p.estado_stock || 'Normal'} />
                    </td>
                </tr>
            {:else}
                <tr>
                    <td colspan="6" class="p-10 text-center text-hotel-text-tertiary uppercase tracking-widest text-xs">Sin productos registrados</td>
                </tr>
            {/each}
        </tbody>
    </table>
</div>