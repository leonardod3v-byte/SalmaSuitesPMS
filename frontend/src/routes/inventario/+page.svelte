<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { auth } from '$lib/stores/auth.svelte';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import Modal from '$components/ui/Modal.svelte';
    import Loading from '$components/ui/Loading.svelte';
    import FilterBar from '$components/ui/FilterBar.svelte';
    import ProductoList from '$components/inventario/ProductoList.svelte';
    import ProductoForm from '$components/inventario/ProductoForm.svelte';
    import MovimientoForm from '$components/inventario/MovimientoForm.svelte';
    import StockBadge from '$components/inventario/StockBadge.svelte';
    import { fetchProductos } from '$lib/services/inventario';
    import type { Producto } from '$lib/types/producto';

    let productos = $state<Producto[]>([]);
    let cargando = $state(true);
    let error = $state('');
    let busqueda = $state('');
    let filtroCategoria = $state('');
    let filtroEstado = $state('');

    // Modales
    let mostrarForm = $state(false);
    let productoEditar = $state<number | null>(null);
    let mostrarEntrada = $state(false);
    let mostrarAjuste = $state(false);

    let filtrados = $derived(
        productos.filter(p => {
            const matchBusqueda = !busqueda.trim() ||
                p.nombre.toLowerCase().includes(busqueda.toLowerCase());
            const matchCategoria = !filtroCategoria || p.categoria === filtroCategoria;
            const matchEstado = !filtroEstado || p.estado_stock === filtroEstado;
            return matchBusqueda && matchCategoria && matchEstado;
        })
    );

    let tieneFiltros = $derived(!!(filtroCategoria || filtroEstado));

    const categorias = ['Bebida', 'Snack', 'Comida', 'Lavandería', 'Otro'];

    onMount(async () => {
        await refrescar();

        // Si viene un ID en query params, abrir edición
        const idParam = $page.url.searchParams.get('id');
        if (idParam) {
            productoEditar = Number(idParam);
            mostrarForm = true;
        }
    });

    async function refrescar() {
        cargando = true;
        try {
            productos = await fetchProductos();
        } catch (e: any) {
            error = e.message;
        } finally {
            cargando = false;
        }
    }

    function resetFiltros() {
        filtroCategoria = '';
        filtroEstado = '';
        busqueda = '';
    }

    function abrirEdicion(id: number) {
        productoEditar = id;
        mostrarForm = true;
    }
</script>

<svelte:head>
    <title>Inventario | SalmaSuitesPMS</title>
</svelte:head>

<PageHeader title="Inventario" subtitle="{filtrados.length} productos">
    {#if auth.isAdmin}
        <div class="flex items-center gap-2">
            <Button variant="gold" size="md" onclick={() => { productoEditar = null; mostrarForm = true; }}>
                <span class="flex items-center gap-1.5">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
                    Nuevo Producto
                </span>
            </Button>
            <Button variant="secondary" size="md" onclick={() => mostrarEntrada = true} title="Registrar entrada de mercancía (aumenta stock)">
                <span class="flex items-center gap-1.5">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"/></svg>
                    Entrada de Mercancía
                </span>
            </Button>
            <Button variant="secondary" size="md" onclick={() => mostrarAjuste = true} title="Ajustar stock manualmente (puede aumentar o disminuir)">
                <span class="flex items-center gap-1.5">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/></svg>
                    Ajustar Stock
                </span>
            </Button>
        </div>
    {/if}
</PageHeader>

{#if cargando}
    <Loading type="dashboard" message="Cargando inventario..." />
{:else if error}
    <div class="text-center p-8 bg-hotel-error/5 border border-hotel-error/20 rounded-2xl">
        <p class="text-hotel-error-light font-bold uppercase tracking-widest text-xs mb-4">{error}</p>
        <Button variant="gold" size="md" onclick={() => window.location.reload()}>Reintentar</Button>
    </div>
{:else}
    <div class="space-y-6">
        <FilterBar placeholder="Buscar producto..." bind:busqueda tieneFiltros onclear={resetFiltros}>
            <select bind:value={filtroCategoria} class="h-12 px-4 rounded-xl bg-hotel-bg border border-hotel-border text-[10px] font-bold uppercase tracking-wider text-hotel-text-secondary">
                <option value="">Categoría</option>
                {#each categorias as cat}
                    <option value={cat}>{cat}</option>
                {/each}
            </select>
            <select bind:value={filtroEstado} class="h-12 px-4 rounded-xl bg-hotel-bg border border-hotel-border text-[10px] font-bold uppercase tracking-wider text-hotel-text-secondary">
                <option value="">Estado</option>
                <option value="Normal">Normal</option>
                <option value="Bajo">Bajo</option>
                <option value="Agotado">Agotado</option>
            </select>
        </FilterBar>

        <div class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm overflow-hidden">
            <ProductoList productos={filtrados} />
        </div>
    </div>
{/if}

{#if mostrarForm}
    <Modal title={productoEditar ? 'Editar Producto' : 'Nuevo Producto'} onclose={() => { mostrarForm = false; refrescar(); }}>
        <ProductoForm id={productoEditar} onclose={() => { mostrarForm = false; refrescar(); }} />
    </Modal>
{/if}

{#if mostrarEntrada}
    <Modal title="Registrar Entrada" onclose={() => { mostrarEntrada = false; refrescar(); }}>
        <MovimientoForm tipo="entrada" onclose={() => { mostrarEntrada = false; refrescar(); }} />
    </Modal>
{/if}

{#if mostrarAjuste}
    <Modal title="Registrar Ajuste" onclose={() => { mostrarAjuste = false; refrescar(); }}>
        <MovimientoForm tipo="ajuste" onclose={() => { mostrarAjuste = false; refrescar(); }} />
    </Modal>
{/if}