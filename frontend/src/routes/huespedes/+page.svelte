<script lang="ts">
    import { onMount } from 'svelte';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import Modal from '$components/ui/Modal.svelte';
    import Loading from '$components/ui/Loading.svelte';
    import FilterBar from '$components/ui/FilterBar.svelte';
    import Icon from '$components/ui/Icons.svelte';
    import GuestTable from '$components/huespedes/GuestTable.svelte';
    import GuestForm from '$components/huespedes/GuestForm.svelte';
    import { fetchHuespedes, getExportUrl } from '$lib/services/huespedes';
    import type { Huesped } from '$lib/types/huesped';

    let huespedes = $state<Huesped[]>([]);
    let cargando = $state(true);
    let error = $state('');
    let mostrarForm = $state(false);
    let busqueda = $state('');
    let soloVip = $state(false);

    let filtrados = $derived(
        huespedes.filter(h => {
            const matchBusqueda = !busqueda.trim() ||
                h.nombres.toLowerCase().includes(busqueda.toLowerCase()) ||
                h.apellidos.toLowerCase().includes(busqueda.toLowerCase()) ||
                h.numero_documento.includes(busqueda);
            const matchVip = !soloVip || h.categoria === 'VIP';
            return matchBusqueda && matchVip;
        })
    );

    let tieneFiltros = $derived(soloVip);

    onMount(async () => {
        try {
            huespedes = await fetchHuespedes();
        } catch (e: any) {
            error = e.message || 'Error al cargar huéspedes';
        } finally {
            cargando = false;
        }
    });

    async function refrescar() {
        try {
            huespedes = await fetchHuespedes();
        } catch { }
    }

    function resetFiltros() {
        soloVip = false;
        busqueda = '';
    }

    function exportarXLS() {
        const url = getExportUrl();
        window.open(url, '_blank');
    }
</script>

<svelte:head>
    <title>Gestión de Huéspedes | SalmaSuitesPMS</title>
</svelte:head>

<PageHeader title="Huéspedes" subtitle="{filtrados.length} Registros">
    <div class="flex items-center gap-3">
        <Button variant="secondary" size="md" onclick={exportarXLS}>
            <span class="flex items-center gap-1.5">
                <Icon name="export" class="w-4 h-4" />
                Exportar XLS
            </span>
        </Button>
        <Button variant="gold" size="md" onclick={() => mostrarForm = true}>
            <span class="flex items-center gap-1.5">
                <Icon name="plus" class="w-4 h-4" />
                Nuevo huésped
            </span>
        </Button>
    </div>
</PageHeader>

{#if cargando}
    <Loading type="dashboard" message="Cargando huéspedes..." />
{:else if error}
    <div class="text-center p-8 bg-hotel-error/5 border border-hotel-error/20 rounded-2xl">
        <p class="text-hotel-error-light font-bold uppercase tracking-widest text-xs mb-4">{error}</p>
        <Button variant="gold" size="sm" onclick={() => window.location.reload()}>Reintentar</Button>
    </div>
{:else}
    <div class="space-y-6">
        <FilterBar placeholder="Buscar por nombre o documento..." bind:busqueda tieneFiltros onclear={resetFiltros}>
            <button
                onclick={() => soloVip = !soloVip}
                class="flex-1 lg:flex-none inline-flex items-center justify-center gap-2 px-6 h-12 rounded-xl text-[10px] font-black uppercase tracking-widest border transition-all duration-300
                {soloVip
                    ? 'bg-hotel-vip/20 border-hotel-vip/50 text-hotel-vip-light'
                    : 'bg-hotel-bg border-hotel-border text-hotel-text-tertiary hover:border-hotel-gold/50'}"
            >
                <svg class="w-3.5 h-3.5 {soloVip ? 'fill-hotel-vip' : 'fill-transparent stroke-current'}" viewBox="0 0 24 24">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                </svg>
                Filtrar VIP
            </button>
        </FilterBar>

        <div class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm overflow-hidden">
            <GuestTable huespedes={filtrados} />
        </div>
    </div>
{/if}

{#if mostrarForm}
    <Modal title="Registrar Huésped" subtitle="Completa todos los campos requeridos" onclose={() => mostrarForm = false}>
        <GuestForm onclose={() => { mostrarForm = false; refrescar(); }} />
    </Modal>
{/if}