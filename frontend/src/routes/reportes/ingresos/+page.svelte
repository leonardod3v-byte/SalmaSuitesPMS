<script lang="ts">
    import { goto } from '$app/navigation';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import Icon from '$components/ui/Icons.svelte';
    import IngresosChart from '$components/reportes/IngresosChart.svelte';
</script>

<svelte:head>
    <title>Ingresos | SalmaSuitesPMS</title>
</svelte:head>

<PageHeader title="Ingresos por Período" subtitle="Análisis gráfico de los ingresos del hotel">
    <Button variant="ghost" size="md" onclick={() => goto('/reportes')}>
        <span class="flex items-center gap-1.5">
            <Icon name="flecha" class="w-4 h-4 rotate-180" />
            Volver a Reportes
        </span>
    </Button>
</PageHeader>

<div class="max-w-6xl mx-auto w-full">
    <IngresosChart />
</div>
