<script lang="ts">
    import { onMount } from 'svelte';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Loading from '$components/ui/Loading.svelte';
    import HotelDataForm from '$components/configuracion/HotelDataForm.svelte';
    import MonedaForm from '$components/configuracion/MonedaForm.svelte';
    import ColorConfig from '$components/configuracion/ColorConfig.svelte';
    import { fetchConfiguracion } from '$lib/services/configuracion';
    import type { ConfiguracionGeneral } from '$lib/types/configuracion';

    let config = $state<ConfiguracionGeneral>({});
    let cargando = $state(true);
    let error = $state('');

    async function cargar() {
        cargando = true;
        try {
            config = await fetchConfiguracion();
        } catch (e: any) {
            error = e.message;
        } finally {
            cargando = false;
        }
    }

    onMount(() => cargar());
</script>

<svelte:head>
    <title>Configuración | SalmaSuitesPMS</title>
</svelte:head>

<PageHeader title="Configuración" subtitle="Personaliza el sistema" />

{#if cargando}
    <Loading type="dashboard" message="Cargando configuración..." />
{:else if error}
    <div class="text-center p-8 bg-hotel-error/5 border border-hotel-error/20 rounded-2xl">
        <p class="text-hotel-error-light font-bold uppercase tracking-widest text-xs mb-4">{error}</p>
        <button class="btn-base btn-gold" onclick={cargar}>Reintentar</button>
    </div>
{:else}
    <div class="space-y-6">
        <!-- Datos del Hotel -->
        <section class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm p-6">
            <h3 class="font-display text-xl text-hotel-text-primary italic mb-6">Datos del Hotel</h3>
            <p class="text-xs text-hotel-text-tertiary mb-4">Información fiscal y de contacto para reportes PDF.</p>
            <HotelDataForm config={config} onsave={cargar} />
        </section>

        <!-- Moneda y Formato -->
        <section class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm p-6">
            <h3 class="font-display text-xl text-hotel-text-primary italic mb-6">Moneda y Formato</h3>
            <p class="text-xs text-hotel-text-tertiary mb-4">Define cómo se muestran los precios, fechas y horas en el sistema.</p>
            <MonedaForm config={config} onsave={cargar} />
        </section>

        <!-- Colores -->
        <section class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm p-6">
            <h3 class="font-display text-xl text-hotel-text-primary italic mb-6">Colores del Sistema</h3>
            <p class="text-xs text-hotel-text-tertiary mb-4">Personaliza los colores por tipo de cliente y estado de habitación.</p>
            <ColorConfig />
        </section>
    </div>
{/if}