<script lang="ts">
    import { goto } from '$app/navigation';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import CierreCaja from '$components/reportes/CierreCaja.svelte';
</script>

<svelte:head>
    <title>Cierre de Caja | SalmaSuitesPMS</title>
</svelte:head>

<PageHeader title="Cierre de Caja" subtitle="Registro diario de ingresos">
    <Button variant="ghost" size="sm" onclick={() => goto('/reportes')}>← Reportes</Button>
</PageHeader>

<CierreCaja />