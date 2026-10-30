<script lang="ts">
    import { goto } from '$app/navigation';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import Icon from '$components/ui/Icons.svelte';
    import CierreCaja from '$components/reportes/CierreCaja.svelte';
</script>

<svelte:head>
    <title>Cierre de Caja | SalmaSuitesPMS</title>
</svelte:head>

<PageHeader title="Cierre de Caja" subtitle="Registro diario de ingresos y transacciones">
    <Button variant="ghost" size="md" onclick={() => goto('/reportes')}>
        <span class="flex items-center gap-1.5">
            <Icon name="flecha" class="w-4 h-4 rotate-180" />
            Volver a Reportes
        </span>
    </Button>
</PageHeader>

<div class="max-w-6xl mx-auto w-full">
    <CierreCaja />
</div>
