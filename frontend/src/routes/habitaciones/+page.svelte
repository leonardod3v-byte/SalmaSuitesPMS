<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import Modal from '$components/ui/Modal.svelte';
    import Loading from '$components/ui/Loading.svelte';
    import FilterBar from '$components/ui/FilterBar.svelte';
    import RoomCard from '$components/habitaciones/RoomCard.svelte';
    import RoomForm from '$components/habitaciones/RoomForm.svelte';
    import { fetchHabitaciones } from '$lib/services/habitaciones';
    import type { Habitacion } from '$lib/types/habitacion';

    let habitaciones = $state<Habitacion[]>([]);
    let cargando = $state(true);
    let error = $state('');
    let mostrarForm = $state(false);
    let busqueda = $state('');
    let filtroEstado = $state<string | null>(null);

    let filtradas = $derived(
        habitaciones.filter(h => {
            const matchBusqueda = !busqueda.trim() ||
                h.numero.includes(busqueda) ||
                h.categoria_tipo.toLowerCase().includes(busqueda.toLowerCase());
            const matchEstado = !filtroEstado || h.estado === filtroEstado;
            return matchBusqueda && matchEstado;
        })
    );

    let tieneFiltros = $derived(filtroEstado !== null);

    const estadosFiltro = [
        { value: 'Disponible', label: 'Disponibles', color: 'bg-hotel-success' },
        { value: 'Ocupada', label: 'Ocupadas', color: 'bg-hotel-gold' },
        { value: 'Limpieza', label: 'Limpieza', color: 'bg-hotel-info-light' },
        { value: 'Mantenimiento', label: 'Mantenimiento', color: 'bg-orange-500' },
        { value: 'Obra', label: 'Obra', color: 'bg-hotel-error' },
    ];

    onMount(async () => {
        try {
            habitaciones = await fetchHabitaciones();
        } catch (e: any) {
            error = e.message || 'Error al cargar habitaciones';
        } finally {
            cargando = false;
        }
    });

    async function refrescar() {
        try {
            habitaciones = await fetchHabitaciones();
        } catch { }
    }

    function resetFiltros() {
        filtroEstado = null;
        busqueda = '';
    }
</script>

<svelte:head>
    <title>Habitaciones | SalmaSuitesPMS</title>
</svelte:head>

<PageHeader title="Habitaciones" subtitle="{filtradas.length} habitaciones">
    <Button variant="gold" size="md" onclick={() => mostrarForm = true}>
        <span class="flex items-center gap-1.5">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            Nueva habitación
        </span>
    </Button>
</PageHeader>

{#if cargando}
    <Loading type="dashboard" message="Cargando habitaciones..." />
{:else if error}
    <div class="text-center p-8 bg-hotel-error/5 border border-hotel-error/20 rounded-2xl">
        <p class="text-hotel-error-light font-bold uppercase tracking-widest text-xs mb-4">{error}</p>
        <Button variant="gold" size="md" onclick={() => window.location.reload()}>Reintentar</Button>
    </div>
{:else}
    <div class="space-y-6">
        <FilterBar placeholder="Buscar por número o tipo..." bind:busqueda tieneFiltros onclear={resetFiltros}>
            {#each estadosFiltro as f}
                <button
                    onclick={() => filtroEstado = filtroEstado === f.value ? null : f.value}
                    class="flex-1 lg:flex-none inline-flex items-center justify-center gap-1.5 px-3 h-8 rounded-xl text-[9px] font-black uppercase tracking-widest border transition-all duration-300
                    {filtroEstado === f.value
                        ? 'border-hotel-gold/50 text-hotel-gold'
                        : 'bg-hotel-bg border-hotel-border text-hotel-text-tertiary hover:border-hotel-gold/50'}"
                >
                    <span class="w-2 h-2 rounded-full {f.color}"></span>
                    {f.label}
                </button>
            {/each}
        </FilterBar>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {#each filtradas as hab}
                <RoomCard habitacion={hab} onchange={refrescar} />
            {:else}
                <div class="col-span-full p-10 text-center text-hotel-text-tertiary uppercase tracking-widest text-xs bg-hotel-surface rounded-2xl border border-hotel-border">
                    Sin habitaciones registradas
                </div>
            {/each}
        </div>
    </div>
{/if}

{#if mostrarForm}
    <Modal title="Registrar Habitación" subtitle="Completa todos los campos requeridos" onclose={() => mostrarForm = false}>
        <RoomForm onclose={() => { mostrarForm = false; refrescar(); }} />
    </Modal>
{/if}
