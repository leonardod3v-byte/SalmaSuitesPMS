<script lang="ts">
    import { onMount } from 'svelte';
    import { apiFetch } from '$lib/services/api';
    import Modal from '$components/ui/Modal.svelte';
    import Button from '$components/ui/Button.svelte';

    interface Habitacion {
        id: number;
        numero: string;
        piso: number;
        categoria_tipo: string;
        precio_por_noche: string;
        estado: string;
        capacidad_maxima: number;
    }

    interface Props {
        habitaciones: Habitacion[];
    }

    let { habitaciones }: Props = $props();

    let filtroActivo = $state<string>('todas');
    let habSeleccionada = $state<Habitacion | null>(null);
    let mostrarModal = $state(false);

    // Colores de estados
    const estadoClases: Record<string, string> = {
        'Limpia': 'bg-hotel-success/10 border-hotel-success/30 text-hotel-success-light',
        'Ocupada': 'bg-hotel-gold/10 border-hotel-gold/30 text-hotel-gold-light',
        'Sucia': 'bg-hotel-info/10 border-hotel-info/30 text-hotel-info-light',
        'Mantenimiento': 'bg-hotel-error/10 border-hotel-error/30 text-hotel-error-light',
        'Obra': 'bg-hotel-error/10 border-hotel-error/30 text-hotel-error-light',
    };

    // Colores de badge
    const estadoDots: Record<string, string> = {
        'Limpia': 'bg-hotel-success',
        'Ocupada': 'bg-hotel-gold',
        'Sucia': 'bg-hotel-info-light',
        'Mantenimiento': 'bg-hotel-error',
        'Obra': 'bg-hotel-error',
    };

    const estadoLabels: Record<string, string> = {
        'Limpia': 'Limpia',
        'Ocupada': 'Ocupada',
        'Sucia': 'Sucia',
        'Mantenimiento': 'Mantenimiento',
        'Obra': 'Obra',
    };

    let filtradas = $derived(
        filtroActivo === 'todas'
            ? habitaciones
            : habitaciones.filter((h) => h.estado === filtroActivo)
    );

    function getClase(estado: string): string {
        return estadoClases[estado] || 'bg-hotel-surface border-hotel-border text-hotel-text-tertiary';
    }

    function abrirPopup(hab: Habitacion) {
        habSeleccionada = hab;
        mostrarModal = true;
    }

    function cerrarPopup() {
        mostrarModal = false;
        habSeleccionada = null;
    }

    async function cambiarEstado(habId: number, nuevoEstado: string) {
        try {
            await apiFetch(`/habitaciones/${habId}/cambiar-estado/`, {
                method: 'POST',
                body: JSON.stringify({ estado: nuevoEstado }),
            });
            window.location.reload();
        } catch (e: any) {
            alert('Error: ' + (e.message || 'No se pudo cambiar el estado'));
        }
    }
</script>

<section class="bg-hotel-surface rounded-2xl p-6 border border-hotel-border shadow-hotel-sm">
    <div class="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
        <h3 class="font-display text-xl text-hotel-text-primary italic">Mapa de Habitaciones</h3>
        <div class="flex p-1 bg-hotel-bg rounded-xl border border-hotel-border flex-wrap gap-1">
            <button onclick={() => filtroActivo = 'todas'} class="px-3 py-1.5 text-[10px] uppercase font-bold rounded-lg transition-all {filtroActivo === 'todas' ? 'bg-hotel-gold text-hotel-bg' : 'text-hotel-text-tertiary hover:text-hotel-text-secondary'}">Todas</button>
            <button onclick={() => filtroActivo = 'Limpia'} class="px-3 py-1.5 text-[10px] uppercase font-bold rounded-lg transition-all {filtroActivo === 'Limpia' ? 'bg-hotel-success text-white' : 'text-hotel-text-tertiary hover:text-hotel-text-secondary'}">Limpias</button>
            <button onclick={() => filtroActivo = 'Ocupada'} class="px-3 py-1.5 text-[10px] uppercase font-bold rounded-lg transition-all {filtroActivo === 'Ocupada' ? 'bg-hotel-gold text-hotel-bg' : 'text-hotel-text-tertiary hover:text-hotel-text-secondary'}">Ocupadas</button>
            <button onclick={() => filtroActivo = 'Sucia'} class="px-3 py-1.5 text-[10px] uppercase font-bold rounded-lg transition-all {filtroActivo === 'Sucia' ? 'bg-hotel-info text-white' : 'text-hotel-text-tertiary hover:text-hotel-text-secondary'}">Sucias</button>
            <button onclick={() => filtroActivo = 'Mantenimiento'} class="px-3 py-1.5 text-[10px] uppercase font-bold rounded-lg transition-all {filtroActivo === 'Mantenimiento' ? 'bg-hotel-error text-white' : 'text-hotel-text-tertiary hover:text-hotel-text-secondary'}">Mantenimiento</button>
            <button onclick={() => filtroActivo = 'Obra'} class="px-3 py-1.5 text-[10px] uppercase font-bold rounded-lg transition-all {filtroActivo === 'Obra' ? 'bg-hotel-error text-white' : 'text-hotel-text-tertiary hover:text-hotel-text-secondary'}">Obra</button>
        </div>
    </div>

    <div class="grid grid-cols-6 sm:grid-cols-8 md:grid-cols-10 lg:grid-cols-12 gap-3">
        {#each filtradas as hab}
            <button
                onclick={() => abrirPopup(hab)}
                class="aspect-square rounded-lg border-2 flex items-center justify-center text-[10px] font-black transition-all hover:scale-110 shadow-sm cursor-pointer {getClase(hab.estado)}"
                title="Habitación {hab.numero} - {hab.estado}"
            >
                {hab.numero}
            </button>
        {/each}
    </div>

    <div class="mt-6 pt-4 border-t border-hotel-border/50 flex flex-wrap gap-3">
        {#each Object.entries(estadoLabels) as [estado, label]}
            <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl border text-[10px] font-bold {getClase(estado)}">
                <div class="w-2 h-2 rounded-full {estadoDots[estado] || 'bg-hotel-text-tertiary'}"></div>
                {label}
            </div>
        {/each}
    </div>
</section>

{#if mostrarModal && habSeleccionada}
    <Modal title="Habitación {habSeleccionada.numero}" subtitle="{habSeleccionada.categoria_tipo} — Piso {habSeleccionada.piso}" onclose={cerrarPopup}>
        <div class="space-y-5">
            <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                    <p class="text-hotel-text-tertiary text-[10px] uppercase tracking-wider mb-0.5">Precio / Noche</p>
                    <p class="font-bold text-hotel-text-primary">${habSeleccionada.precio_por_noche}</p>
                </div>
                <div>
                    <p class="text-hotel-text-tertiary text-[10px] uppercase tracking-wider mb-0.5">Capacidad</p>
                    <p class="font-bold text-hotel-text-primary">{habSeleccionada.capacidad_maxima} personas</p>
                </div>
            </div>

            <div class="flex items-center gap-2">
                <span class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary">Estado:</span>
                <span class="px-2.5 py-1 rounded-full text-[10px] font-bold border {getClase(habSeleccionada.estado)}">
                    {habSeleccionada.estado}
                </span>
            </div>

            <div class="flex flex-wrap gap-2 pt-4 border-t border-hotel-border/50">
                {#if habSeleccionada.estado === 'Limpia'}
                    <a href="/reservaciones/nueva?habitacion={habSeleccionada.id}" class="no-underline"><Button variant="gold" size="md">Nueva Reservación</Button></a>
                    <Button variant="danger" size="md" onclick={() => cambiarEstado(habSeleccionada!.id, 'Mantenimiento')}>Mantenimiento</Button>
                    <Button variant="secondary" size="md" onclick={() => cambiarEstado(habSeleccionada!.id, 'Obra')}>Enviar a Obra</Button>
                {:else if habSeleccionada.estado === 'Sucia'}
                    <Button variant="success" size="md" onclick={() => cambiarEstado(habSeleccionada!.id, 'Limpia')}>Marcar como Limpia</Button>
                {:else if habSeleccionada.estado === 'Ocupada'}
                    <a href="/reservaciones?habitacion={habSeleccionada.id}" class="no-underline"><Button variant="gold" size="md">Ver reservación</Button></a>
                {:else if habSeleccionada.estado === 'Mantenimiento' || habSeleccionada.estado === 'Obra'}
                    <Button variant="success" size="md" onclick={() => cambiarEstado(habSeleccionada!.id, 'Limpia')}>Finalizar → Limpia</Button>
                    <Button variant="secondary" size="md" onclick={() => cambiarEstado(habSeleccionada!.id, 'Sucia')}>Finalizar → Sucia</Button>
                {/if}
                <Button variant="ghost" size="md" onclick={cerrarPopup}>Cerrar</Button>
            </div>
        </div>
    </Modal>
{/if}