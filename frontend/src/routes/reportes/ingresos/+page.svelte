<script lang="ts">
    import { goto } from '$app/navigation';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import IngresosChart from '$components/reportes/IngresosChart.svelte';
</script>

<svelte:head>
    <title>Ingresos | SalmaSuitesPMS</title>
</svelte:head>

<PageHeader title="Ingresos" subtitle="Gráfico de ingresos por período">
    <Button variant="ghost" size="sm" onclick={() => goto('/reportes')}>← Reportes</Button>
</PageHeader>

<IngresosChart />