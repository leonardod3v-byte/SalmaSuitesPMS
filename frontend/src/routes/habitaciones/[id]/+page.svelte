<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import Loading from '$components/ui/Loading.svelte';
    import RoomForm from '$components/habitaciones/RoomForm.svelte';
    import { fetchHabitacion } from '$lib/services/habitaciones';
    import type { Habitacion } from '$lib/types/habitacion';

    let habitacion = $state<Habitacion | null>(null);
    let cargando = $state(true);
    let error = $state('');

    onMount(async () => {
        const id = Number($page.params.id);
        try {
            habitacion = await fetchHabitacion(id);
        } catch (e: any) {
            error = e.message || 'Habitación no encontrada';
        } finally {
            cargando = false;
        }
    });

    function volver() {
        goto('/habitaciones', { invalidateAll: true });
    }
</script>

<svelte:head>
    <title>{habitacion ? `Habitación ${habitacion.numero}` : 'Habitación'} | SalmaSuitesPMS</title>
</svelte:head>

{#if cargando}
    <Loading type="dashboard" message="Cargando habitación..." />
{:else if error}
    <div class="text-center p-8 bg-hotel-error/5 border border-hotel-error/20 rounded-2xl">
        <p class="text-hotel-error-light font-bold uppercase tracking-widest text-xs mb-4">{error}</p>
        <Button variant="gold" size="sm" onclick={volver}>Volver a habitaciones</Button>
    </div>
{:else if habitacion}
    <PageHeader title="Habitación {habitacion.numero}" subtitle="{habitacion.categoria_tipo} — Piso {habitacion.piso}">
        <Button variant="ghost" size="sm" onclick={volver}>← Volver</Button>
    </PageHeader>

    <div class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm p-6">
        <RoomForm id={habitacion.id} onclose={volver} />
    </div>
{/if}
