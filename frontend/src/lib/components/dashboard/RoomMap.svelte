<script lang="ts">
    import { apiFetch } from '$lib/services/api';
    import Modal from '$components/ui/Modal.svelte';
    import Button from '$components/ui/Button.svelte';
    import Icon from '$components/ui/Icons.svelte';

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

    const estadoClases: Record<string, string> = {
        'Disponible': 'bg-hotel-success/10 border-hotel-success/40 text-hotel-success-light hover:bg-hotel-success/20',
        'Ocupada': 'bg-hotel-gold/10 border-hotel-gold/40 text-hotel-gold-light hover:bg-hotel-gold/20',
        'Limpieza': 'bg-hotel-info/10 border-hotel-info/40 text-hotel-info-light hover:bg-hotel-info/20',
        'Mantenimiento': 'bg-orange-500/10 border-orange-500/40 text-orange-400 hover:bg-orange-500/20',
        'Obra': 'bg-hotel-error/10 border-hotel-error/40 text-hotel-error-light hover:bg-hotel-error/20',
    };

    const estadoDots: Record<string, string> = {
        'Disponible': 'bg-hotel-success',
        'Ocupada': 'bg-hotel-gold',
        'Limpieza': 'bg-hotel-info-light',
        'Mantenimiento': 'bg-orange-500',
        'Obra': 'bg-hotel-error',
    };

    const estadoLabels: Record<string, string> = {
        'Disponible': 'Disponible',
        'Ocupada': 'Ocupada',
        'Limpieza': 'Limpieza',
        'Mantenimiento': 'Mantenimiento',
        'Obra': 'Obra',
    };

    const filtros = [
        { key: 'todas', label: 'Todas', color: 'bg-hotel-text-tertiary' },
        { key: 'Disponible', label: 'Disponibles', color: 'bg-hotel-success' },
        { key: 'Ocupada', label: 'Ocupadas', color: 'bg-hotel-gold' },
        { key: 'Limpieza', label: 'Limpieza', color: 'bg-hotel-info-light' },
        { key: 'Mantenimiento', label: 'Mantenimiento', color: 'bg-orange-500' },
        { key: 'Obra', label: 'Obra', color: 'bg-hotel-error' },
    ];

    let filtradas = $derived(
        filtroActivo === 'todas'
            ? habitaciones
            : habitaciones.filter((h) => h.estado === filtroActivo)
    );

    let conteoEstados = $derived(
        habitaciones.reduce((acc, h) => {
            acc[h.estado] = (acc[h.estado] || 0) + 1;
            return acc;
        }, {} as Record<string, number>)
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
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
        <div>
            <h3 class="font-display text-xl text-hotel-text-primary italic flex items-center gap-2">
                Mapa de Habitaciones
            </h3>
            <p class="text-[10px] uppercase tracking-[0.2em] text-hotel-text-tertiary mt-1">
                {habitaciones.length} habitaciones en total
            </p>
        </div>

        <div class="flex p-1 bg-hotel-bg rounded-xl border border-hotel-border flex-wrap gap-1">
            {#each filtros as f}
                {@const count = f.key === 'todas' ? habitaciones.length : (conteoEstados[f.key] || 0)}
                <button
                    onclick={() => filtroActivo = f.key}
                    class="px-2.5 py-1.5 text-[10px] uppercase font-bold rounded-lg transition-all flex items-center gap-1.5
                    {filtroActivo === f.key
                        ? (f.key === 'todas' ? 'bg-hotel-gold text-hotel-bg' : `bg-${f.color.replace('bg-', '')} text-white`)
                        : 'text-hotel-text-tertiary hover:text-hotel-text-secondary'}"
                    style={filtroActivo === f.key && f.key !== 'todas' ? `background-color: var(--color-${f.color.replace('bg-', '')})` : ''}
                >
                    <span class="w-1.5 h-1.5 rounded-full {f.color}"></span>
                    {f.label}
                    <span class="opacity-70">({count})</span>
                </button>
            {/each}
        </div>
    </div>

    <div class="grid grid-cols-6 sm:grid-cols-8 md:grid-cols-10 lg:grid-cols-12 gap-2">
        {#each filtradas as hab}
            <button
                onclick={() => abrirPopup(hab)}
                class="aspect-square rounded-lg border-2 flex flex-col items-center justify-center text-[11px] font-black transition-all hover:scale-105 hover:shadow-lg cursor-pointer relative group {getClase(hab.estado)}"
                title="Habitación {hab.numero} — {hab.estado}"
            >
                <span>{hab.numero}</span>
                <span class="text-[7px] font-bold uppercase opacity-60 group-hover:opacity-100 leading-none mt-0.5">
                    {hab.estado.substring(0, 3)}
                </span>
            </button>
        {:else}
            <div class="col-span-full p-10 text-center text-hotel-text-tertiary uppercase tracking-widest text-xs">
                Sin habitaciones en este estado
            </div>
        {/each}
    </div>

    <div class="mt-6 pt-4 border-t border-hotel-border/50 flex flex-wrap gap-2">
        {#each Object.entries(estadoLabels) as [estado, label]}
            <div class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-[10px] font-bold {getClase(estado)}">
                <div class="w-1.5 h-1.5 rounded-full {estadoDots[estado] || 'bg-hotel-text-tertiary'}"></div>
                {label}
                <span class="opacity-60">({conteoEstados[estado] || 0})</span>
            </div>
        {/each}
    </div>
</section>

{#if mostrarModal && habSeleccionada}
    <Modal title="Habitación {habSeleccionada.numero}" subtitle="{habSeleccionada.categoria_tipo} — Piso {habSeleccionada.piso}" onclose={cerrarPopup}>
        <div class="space-y-5">
            <div class="grid grid-cols-3 gap-3">
                <div class="p-3 rounded-lg bg-hotel-bg/40 border border-hotel-border">
                    <p class="text-hotel-text-tertiary text-[9px] uppercase tracking-wider mb-0.5">Precio / Noche</p>
                    <p class="font-bold text-hotel-text-primary text-sm">${habSeleccionada.precio_por_noche}</p>
                </div>
                <div class="p-3 rounded-lg bg-hotel-bg/40 border border-hotel-border">
                    <p class="text-hotel-text-tertiary text-[9px] uppercase tracking-wider mb-0.5">Capacidad</p>
                    <p class="font-bold text-hotel-text-primary text-sm">{habSeleccionada.capacidad_maxima} pers.</p>
                </div>
                <div class="p-3 rounded-lg bg-hotel-bg/40 border border-hotel-border">
                    <p class="text-hotel-text-tertiary text-[9px] uppercase tracking-wider mb-0.5">Estado</p>
                    <span class="inline-block px-2 py-0.5 rounded-full text-[9px] font-bold border {getClase(habSeleccionada.estado)}">
                        {habSeleccionada.estado}
                    </span>
                </div>
            </div>

            <div class="flex flex-wrap gap-2 pt-4 border-t border-hotel-border/50">
                {#if habSeleccionada.estado === 'Disponible'}
                    <a href="/reservaciones/nueva?habitacion={habSeleccionada.id}" class="no-underline">
                        <Button variant="gold" size="md">
                            <span class="flex items-center gap-1.5">
                                <Icon name="plus" class="w-4 h-4" />
                                Nueva Reservación
                            </span>
                        </Button>
                    </a>
                    <Button variant="secondary" size="md" onclick={() => cambiarEstado(habSeleccionada!.id, 'Mantenimiento')}>Mantenimiento</Button>
                    <Button variant="danger" size="md" onclick={() => cambiarEstado(habSeleccionada!.id, 'Obra')}>Enviar a Obra</Button>
                {:else if habSeleccionada.estado === 'Limpieza'}
                    <Button variant="success" size="md" onclick={() => cambiarEstado(habSeleccionada!.id, 'Disponible')}>
                        <span class="flex items-center gap-1.5">
                            <Icon name="check" class="w-4 h-4" />
                            Marcar como Disponible
                        </span>
                    </Button>
                {:else if habSeleccionada.estado === 'Ocupada'}
                    <a href="/reservaciones?habitacion={habSeleccionada.id}" class="no-underline">
                        <Button variant="gold" size="md">Ver reservación</Button>
                    </a>
                {:else if habSeleccionada.estado === 'Mantenimiento' || habSeleccionada.estado === 'Obra'}
                    <Button variant="success" size="md" onclick={() => cambiarEstado(habSeleccionada!.id, 'Limpieza')}>
                        Finalizar → Limpieza
                    </Button>
                    <Button variant="secondary" size="md" onclick={() => cambiarEstado(habSeleccionada!.id, 'Disponible')}>
                        Finalizar → Disponible
                    </Button>
                {/if}
                <Button variant="ghost" size="md" onclick={cerrarPopup}>Cerrar</Button>
            </div>
        </div>
    </Modal>
{/if}
