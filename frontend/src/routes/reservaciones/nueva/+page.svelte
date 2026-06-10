<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import ReservaForm from '$components/reservaciones/ReservaForm.svelte';

    let habitacionPreseleccionada = $state<number | null>(null);

    onMount(() => {
        const habParam = $page.url.searchParams.get('habitacion');
        if (habParam) habitacionPreseleccionada = Number(habParam);
    });

    function volver() {
        goto('/reservaciones', { invalidateAll: true });
    }
</script>

<svelte:head>
    <title>Nueva Reservación | SalmaSuitesPMS</title>
</svelte:head>

<PageHeader title="Nueva Reservación" subtitle="Completa todos los pasos">
    <Button variant="ghost" size="sm" onclick={volver}>← Volver</Button>
</PageHeader>

<div class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm p-6">
    <ReservaForm onclose={volver} habitacionPreseleccionada={habitacionPreseleccionada} />
</div>