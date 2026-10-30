<script lang="ts">
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Tabs from '$components/ui/Tabs.svelte';
    import CierreCaja from '$components/reportes/CierreCaja.svelte';
    import IngresosChart from '$components/reportes/IngresosChart.svelte';
    import Icon from '$components/ui/Icons.svelte';

    let vista = $state<'diario' | 'ingresos'>('diario');
</script>

<svelte:head>
    <title>Reportes | SalmaSuitesPMS</title>
</svelte:head>

<PageHeader title="Reportes" subtitle="Análisis financiero y cierres de caja" />

<div class="space-y-6">
    <div class="flex justify-between items-center">
        <Tabs
            tabs={[
                { key: 'diario', label: 'Cierre Diario' },
                { key: 'ingresos', label: 'Ingresos por Período' },
            ]}
            active={vista}
            onchange={(k: string) => vista = k as 'diario' | 'ingresos'}
        />
    </div>

    {#if vista === 'diario'}
        <CierreCaja />
    {:else}
        <IngresosChart />
    {/if}
</div>
