<script lang="ts">
    import { onMount } from 'svelte';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import Modal from '$components/ui/Modal.svelte';
    import Loading from '$components/ui/Loading.svelte';
    import FilterBar from '$components/ui/FilterBar.svelte';
    import EmpresaTable from '$components/empresas/EmpresaTable.svelte';
    import EmpresaForm from '$components/empresas/EmpresaForm.svelte';
    import { fetchEmpresas } from '$lib/services/empresas';
    import type { Empresa } from '$lib/types/empresa';

    let empresas = $state<Empresa[]>([]);
    let cargando = $state(true);
    let error = $state('');
    let mostrarForm = $state(false);
    let busqueda = $state('');

    let filtradas = $derived(
        empresas.filter(e => {
            const matchBusqueda = !busqueda.trim() ||
                e.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
                e.rif.includes(busqueda);
            return matchBusqueda;
        })
    );

    let tieneFiltros = $derived(busqueda.trim().length > 0);

    onMount(cargar);

    async function cargar() {
        cargando = true;
        try {
            empresas = await fetchEmpresas();
        } catch (e: any) {
            error = e.message || 'Error al cargar empresas';
        } finally {
            cargando = false;
        }
    }

    function resetFiltros() {
        busqueda = '';
    }
</script>

<svelte:head>
    <title>Empresas | SalmaSuitesPMS</title>
</svelte:head>

<PageHeader title="Empresas" subtitle="{filtradas.length} empresas registradas">
    <Button variant="gold" size="md" onclick={() => mostrarForm = true}>
        <span class="flex items-center gap-1.5">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            Nueva empresa
        </span>
    </Button>
</PageHeader>

{#if cargando}
    <Loading type="dashboard" message="Cargando empresas..." />
{:else if error}
    <div class="text-center p-8 bg-hotel-error/5 border border-hotel-error/20 rounded-2xl">
        <p class="text-hotel-error-light font-bold uppercase tracking-widest text-xs mb-4">{error}</p>
        <Button variant="gold" size="sm" onclick={cargar}>Reintentar</Button>
    </div>
{:else}
    <div class="space-y-6">
        <FilterBar placeholder="Buscar por nombre o RIF..." bind:busqueda tieneFiltros onclear={resetFiltros} />

        <div class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm overflow-hidden">
            <EmpresaTable empresas={filtradas} />
        </div>
    </div>
{/if}

{#if mostrarForm}
    <Modal title="Nueva Empresa" onclose={() => { mostrarForm = false; cargar(); }}>
        <EmpresaForm id={null} onclose={() => { mostrarForm = false; cargar(); }} />
    </Modal>
{/if}
