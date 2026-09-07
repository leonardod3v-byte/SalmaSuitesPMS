<script lang="ts">
    import { onMount } from 'svelte';
    import { auth } from '$lib/stores/auth.svelte';
    import { goto } from '$app/navigation';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import Loading from '$components/ui/Loading.svelte';
    import { fetchMovimientos } from '$lib/services/inventario';
    import type { MovimientoInventario } from '$lib/types/producto';

    let movimientos = $state<MovimientoInventario[]>([]);
    let cargando = $state(true);
    let error = $state('');

    onMount(async () => {
        if (!auth.isAdmin) {
            goto('/inventario', { replaceState: true });
            return;
        }
        try {
            movimientos = await fetchMovimientos();
        } catch (e: any) {
            error = e.message;
        } finally {
            cargando = false;
        }
    });

    const tipoBadge: Record<string, string> = {
        'entrada': 'bg-hotel-success/10 text-hotel-success-light border-hotel-success/20',
        'salida': 'bg-hotel-error/10 text-hotel-error-light border-hotel-error/20',
        'ajuste': 'bg-hotel-info/10 text-hotel-info-light border-hotel-info/20',
    };
</script>

<svelte:head>
    <title>Movimientos | SalmaSuitesPMS</title>
</svelte:head>

<PageHeader title="Movimientos de Inventario" subtitle="{movimientos.length} registros">
    <Button variant="ghost" size="sm" onclick={() => goto('/inventario')}>← Volver</Button>
</PageHeader>

{#if cargando}
    <Loading type="dashboard" message="Cargando movimientos..." />
{:else if error}
    <div class="text-center p-8 bg-hotel-error/5 border border-hotel-error/20 rounded-2xl">
        <p class="text-hotel-error-light font-bold uppercase tracking-widest text-xs mb-4">{error}</p>
        <Button variant="gold" size="sm" onclick={() => window.location.reload()}>Reintentar</Button>
    </div>
{:else}
    <div class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm overflow-hidden">
        <div class="overflow-x-auto">
            <table class="w-full text-sm">
                <thead>
                    <tr class="border-b border-hotel-border text-[10px] uppercase tracking-widest text-hotel-text-tertiary text-left">
                        <th class="p-3 font-bold">Fecha</th>
                        <th class="p-3 font-bold">Producto</th>
                        <th class="p-3 font-bold">Tipo</th>
                        <th class="p-3 font-bold text-right">Cantidad</th>
                        <th class="p-3 font-bold hidden md:table-cell">Motivo</th>
                        <th class="p-3 font-bold hidden lg:table-cell">Usuario</th>
                    </tr>
                </thead>
                <tbody>
                    {#each movimientos as m (m.id)}
                        <tr class="border-b border-hotel-border/30">
                            <td class="p-3 text-hotel-text-secondary text-xs">{new Date(m.fecha).toLocaleString()}</td>
                            <td class="p-3 font-bold text-hotel-text-primary">{m.producto_nombre}</td>
                            <td class="p-3">
                                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border {tipoBadge[m.tipo] || ''}">
                                    {m.tipo}
                                </span>
                            </td>
                            <td class="p-3 text-right font-bold {parseFloat(m.cantidad) >= 0 ? 'text-hotel-success-light' : 'text-hotel-error-light'}">
                                {parseFloat(m.cantidad) > 0 ? '+' : ''}{m.cantidad}
                            </td>
                            <td class="p-3 text-hotel-text-secondary text-xs hidden md:table-cell">{m.motivo}</td>
                            <td class="p-3 text-hotel-text-tertiary text-xs hidden lg:table-cell">{m.usuario_nombre}</td>
                        </tr>
                    {:else}
                        <tr>
                            <td colspan="6" class="p-10 text-center text-hotel-text-tertiary uppercase tracking-widest text-xs">Sin movimientos registrados</td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    </div>
{/if}