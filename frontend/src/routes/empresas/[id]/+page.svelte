<script lang="ts">
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import Loading from '$components/ui/Loading.svelte';
    import EmpresaForm from '$components/empresas/EmpresaForm.svelte';
    import { fetchEmpresa } from '$lib/services/empresas';
    import type { Empresa } from '$lib/types/empresa';

    let empresa = $state<Empresa | null>(null);
    let cargando = $state(true);
    let error = $state('');

    onMount(async () => {
        const id = Number($page.params.id);
        try {
            empresa = await fetchEmpresa(id);
        } catch (e: any) {
            error = e.message || 'Empresa no encontrada';
        } finally {
            cargando = false;
        }
    });

    function volver() {
        goto('/empresas', { invalidateAll: true });
    }
</script>

<svelte:head>
    <title>{empresa ? empresa.nombre : 'Empresa'} | SalmaSuitesPMS</title>
</svelte:head>

<PageHeader
    title={empresa ? empresa.nombre : 'Cargando...'}
    subtitle="Ficha de la empresa"
>
    <Button variant="ghost" size="md" onclick={volver}>
        <span class="flex items-center gap-1.5">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
            Volver a la lista
        </span>
    </Button>
</PageHeader>

{#if cargando}
    <Loading type="dashboard" message="Cargando empresa..." />
{:else if error}
    <div class="text-center p-8 bg-hotel-error/5 border border-hotel-error/20 rounded-2xl">
        <p class="text-hotel-error-light font-bold uppercase tracking-widest text-xs mb-4">{error}</p>
        <Button variant="gold" size="sm" onclick={volver}>Volver a la lista</Button>
    </div>
{:else if empresa}
    <div class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm p-6 sm:p-8">
        <EmpresaForm id={empresa.id} onclose={volver} />
    </div>
{/if}
