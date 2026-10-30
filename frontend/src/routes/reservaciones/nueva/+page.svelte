<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import ReservaForm from '$components/reservaciones/ReservaForm.svelte';
    import Icon from '$components/ui/Icons.svelte';

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

<PageHeader title="Nueva Reservación" subtitle="Completa todos los pasos para registrar al huésped">
    <Button variant="ghost" size="md" onclick={volver}>
        <span class="flex items-center gap-1.5">
            <Icon name="flecha" class="w-4 h-4 rotate-180" />
            Volver
        </span>
    </Button>
</PageHeader>

<div class="max-w-5xl mx-auto w-full">
    <div class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-lg p-6 md:p-8">
        <ReservaForm onclose={volver} habitacionPreseleccionada={habitacionPreseleccionada} />
    </div>
</div>
