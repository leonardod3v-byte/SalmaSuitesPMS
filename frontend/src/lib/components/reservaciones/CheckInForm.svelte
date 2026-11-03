<script lang="ts">
    import { onMount } from 'svelte';
    import { toast } from '$lib/stores/toast';
    import Button from '$components/ui/Button.svelte';
    import Icon from '$components/ui/Icons.svelte';
    import Modal from '$components/ui/Modal.svelte';
    import { realizarCheckin } from '$lib/services/reservaciones';
    import { fetchOcupaciones, type Ocupacion } from '$lib/services/ocupaciones';
    import NuevoHuespedRapido from './NuevoHuespedRapido.svelte';
    import type { Reservacion, Acompanante } from '$lib/types/reservacion';

    let {
        reservacion,
        onclose,
    }: {
        reservacion: Reservacion;
        onclose: () => void;
    } = $props();

    let loading = $state(false);
    let error = $state('');
    let ocupaciones = $state<Ocupacion[]>([]);
    let mostrarFormNuevo = $state(false);

    let acompanantesExtra = $state<Acompanante[]>([]);

    let acompanantesExistentes = $derived(reservacion.acompanantes || []);

    let totalPersonas = $derived(1 + acompanantesExistentes.length + acompanantesExtra.length);

    let horaActual = $state(new Date().toLocaleTimeString('es-VE', { hour: '2-digit', minute: '2-digit' }));

    onMount(async () => {
        try { ocupaciones = await fetchOcupaciones(); } catch { }
    });

    function onNuevoAcompananteCreado(nuevo: any) {
        const nuevoAcomp: Acompanante = {
            id: Date.now(),
            id_huesped: nuevo.id,
            rol: 'Acompañante',
            huesped_detalle: nuevo,
        };
        acompanantesExtra = [...acompanantesExtra, nuevoAcomp];
        mostrarFormNuevo = false;
        toast.success(`${nuevo.nombres} agregado.`);
    }

    async function confirmar() {
        loading = true;
        error = '';
        try {
            const idsExtra = acompanantesExtra.map(a => a.id_huesped);
            await realizarCheckin(reservacion.id, idsExtra);
            toast.success('Check‑in realizado correctamente.');
            onclose();
        } catch (e: any) {
            error = e.message || 'Error al hacer check‑in';
        } finally {
            loading = false;
        }
    }
</script>

<div class="space-y-6">
    {#if error}
        <div class="flex items-center gap-2 p-3 rounded-xl bg-hotel-error/10 border border-hotel-error/20 text-hotel-error-light text-sm">
            <Icon name="alert" class="w-4 h-4 shrink-0" />
            {error}
        </div>
    {/if}

    <div class="p-5 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
        <div class="flex items-center gap-3 border-b border-hotel-border/50 pb-4 mb-4">
            <div class="w-12 h-12 rounded-full bg-hotel-gold/10 flex items-center justify-center text-hotel-gold">
                <Icon name="user" class="w-6 h-6" />
            </div>
            <div>
                <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Confirmar Check‑in</p>
                <p class="text-lg font-display italic text-hotel-text-primary">{reservacion.huesped_nombre}</p>
                <p class="text-[10px] text-hotel-text-tertiary mt-0.5">{totalPersonas} personas en total</p>
            </div>
        </div>

        <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
                <p class="text-[10px] uppercase text-hotel-text-tertiary mb-1">Habitación</p>
                <p class="font-bold text-hotel-text-primary text-lg">#{reservacion.habitacion_numero}</p>
            </div>
            <div>
                <p class="text-[10px] uppercase text-hotel-text-tertiary mb-1">Noches</p>
                <p class="font-bold text-hotel-text-primary">{reservacion.numero_noches} noches</p>
            </div>
            <div>
                <p class="text-[10px] uppercase text-hotel-text-tertiary mb-1">Fecha de Entrada</p>
                <p class="font-bold text-hotel-text-primary">{reservacion.fecha_entrada}</p>
            </div>
            <div>
                <p class="text-[10px] uppercase text-hotel-text-tertiary mb-1">Fecha de Salida</p>
                <p class="font-bold text-hotel-text-primary">{reservacion.fecha_salida}</p>
            </div>
        </div>

        <!-- Acompañantes existentes -->
        <div class="border-t border-hotel-border/50 pt-4">
            <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary font-bold mb-3">
                Acompañantes registrados ({acompanantesExistentes.length})
            </p>
            {#if acompanantesExistentes.length === 0}
                <p class="text-xs text-hotel-text-tertiary italic">Sin acompañantes registrados</p>
            {:else}
                <div class="space-y-2">
                    {#each acompanantesExistentes as a}
                        <div class="flex items-center justify-between p-2 rounded-lg bg-hotel-bg/40 border border-hotel-border">
                            <div class="flex items-center gap-2 min-w-0">
                                <div class="w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0"
                                    style="background-color: {(a.huesped_detalle?.ocupacion_color || '#9E9E9E')}15; color: {a.huesped_detalle?.ocupacion_color || '#9E9E9E'}">
                                    {a.huesped_detalle?.nombres?.charAt(0)}{a.huesped_detalle?.apellidos?.charAt(0)}
                                </div>
                                <div class="min-w-0">
                                    <p class="text-sm font-bold text-hotel-text-primary truncate">
                                        {a.huesped_detalle?.nombres} {a.huesped_detalle?.apellidos}
                                    </p>
                                    <p class="text-[10px] text-hotel-text-tertiary">
                                        {a.huesped_detalle?.tipo_documento}-{a.huesped_detalle?.numero_documento}
                                        {#if a.huesped_detalle?.ocupacion_nombre}
                                            · {a.huesped_detalle.ocupacion_nombre}
                                        {/if}
                                    </p>
                                </div>
                            </div>
                        </div>
                    {/each}
                </div>
            {/if}
        </div>

        <!-- Acompañantes -->
        <div class="border-t border-hotel-border/50 pt-4">
            <div class="flex items-center justify-between mb-3">
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary font-bold">
                    Agregar al Check-in ({acompanantesExtra.length})
                </p>
                <Button type="button" variant="ghost" size="sm" onclick={() => mostrarFormNuevo = true}>
                    + Agregar
                </Button>
            </div>
            {#if acompanantesExtra.length === 0}
                <p class="text-xs text-hotel-text-tertiary italic">Puedes agregar más personas aquí si llegan al check-in</p>
            {:else}
                <div class="space-y-2">
                    {#each acompanantesExtra as a}
                        <div class="flex items-center justify-between p-2 rounded-lg bg-hotel-gold/5 border border-hotel-gold/20">
                            <div class="flex items-center gap-2 min-w-0">
                                <div class="w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-bold shrink-0"
                                    style="background-color: {(a.huesped_detalle?.ocupacion_color || '#9E9E9E')}15; color: {a.huesped_detalle?.ocupacion_color || '#9E9E9E'}">
                                    {a.huesped_detalle?.nombres?.charAt(0)}{a.huesped_detalle?.apellidos?.charAt(0)}
                                </div>
                                <div class="min-w-0">
                                    <p class="text-sm font-bold text-hotel-text-primary truncate">
                                        {a.huesped_detalle?.nombres} {a.huesped_detalle?.apellidos}
                                    </p>
                                    <p class="text-[10px] text-hotel-text-tertiary">
                                        {a.huesped_detalle?.tipo_documento}-{a.huesped_detalle?.numero_documento}
                                    </p>
                                </div>
                            </div>
                            <button type="button" onclick={() => acompanantesExtra = acompanantesExtra.filter(x => x.id !== a.id)} class="text-hotel-error-light text-xs font-bold">Quitar</button>
                        </div>
                    {/each}
                </div>
            {/if}
        </div>

        <div class="flex items-center gap-2 p-3 rounded-xl bg-hotel-info/5 border border-hotel-info/20 text-xs text-hotel-info-light mt-4">
            <Icon name="clock" class="w-4 h-4 shrink-0" />
            Se registrará la entrada con la hora actual: <b class="ml-1">{horaActual}</b>
        </div>
    </div>

    <div class="flex gap-3">
        <Button variant="gold" onclick={confirmar} loading={loading} fullWidth>
            Confirmar Check‑in
        </Button>
        <Button variant="ghost" onclick={onclose}>Cancelar</Button>
    </div>
</div>

{#if mostrarFormNuevo}
    <Modal title="Nuevo Acompañante" subtitle="Se registrará como huésped" onclose={() => mostrarFormNuevo = false}>
        <NuevoHuespedRapido
            {ocupaciones}
            oncreado={onNuevoAcompananteCreado}
            oncancel={() => mostrarFormNuevo = false}
        />
    </Modal>
{/if}
