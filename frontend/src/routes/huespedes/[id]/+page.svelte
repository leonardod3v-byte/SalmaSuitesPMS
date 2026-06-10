<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import Loading from '$components/ui/Loading.svelte';
    import GuestForm from '$components/huespedes/GuestForm.svelte';
    import { fetchHuesped } from '$lib/services/huespedes';
    import type { Huesped } from '$lib/types/huesped';

    let huesped = $state<Huesped | null>(null);
    let cargando = $state(true);
    let error = $state('');

    onMount(async () => {
        const id = Number($page.params.id);
        try {
            huesped = await fetchHuesped(id);
        } catch (e: any) {
            error = e.message || 'Huésped no encontrado';
        } finally {
            cargando = false;
        }
    });

    function volver() {
        goto('/huespedes', { invalidateAll: true });
    }
</script>

<svelte:head>
    <title>{huesped ? `${huesped.nombres} ${huesped.apellidos}` : 'Huésped'} | SalmaSuitesPMS</title>
</svelte:head>

{#if cargando}
    <Loading type="dashboard" message="Cargando huésped..." />
{:else if error}
    <div class="text-center p-8 bg-hotel-error/5 border border-hotel-error/20 rounded-2xl">
        <p class="text-hotel-error-light font-bold uppercase tracking-widest text-xs mb-4">{error}</p>
        <Button variant="gold" size="sm" onclick={volver}>Volver a huéspedes</Button>
    </div>
{:else if huesped}
    <PageHeader title="{huesped.nombres} {huesped.apellidos}" subtitle="Editar información del huésped">
        <Button variant="ghost" size="sm" onclick={volver}>← Volver</Button>
    </PageHeader>

    <div class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm p-6">
        <GuestForm id={huesped.id} onclose={volver} />
    </div>
{/if}