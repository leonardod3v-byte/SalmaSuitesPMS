<script lang="ts">
    import { toast } from '$lib/stores/toast';
    import InputHotel from '$components/ui/Input.svelte';
    import Select from '$components/ui/Select.svelte';
    import Button from '$components/ui/Button.svelte';
    import { saveConfiguracion } from '$lib/services/configuracion';
    import type { ConfiguracionGeneral } from '$lib/types/configuracion';

    let {
        config,
        onsave,
    }: {
        config: ConfiguracionGeneral;
        onsave: () => void;
    } = $props();

    let loading = $state(false);

    // svelte-ignore state_referenced_locally
    let simbolo = $state(config.simbolo_moneda || '$');
    // svelte-ignore state_referenced_locally
    let posicion = $state(config.posicion_simbolo || 'antes');
    // svelte-ignore state_referenced_locally
    let separadorMiles = $state(config.separador_miles || ',');
    // svelte-ignore state_referenced_locally
    let separadorDecimal = $state(config.separador_decimal || '.');
    // svelte-ignore state_referenced_locally
    let formatoFecha = $state(config.formato_fecha || 'DD/MM/AAAA');
    // svelte-ignore state_referenced_locally
    let formatoHora = $state(config.formato_hora || '24h');
    // svelte-ignore state_referenced_locally
    let limiteCierre = $state(config.limite_dias_cierre_recepcion || '7');

    const posiciones = [
        { value: 'antes', label: 'Antes del número ($100)' },
        { value: 'despues', label: 'Después del número (100$)' },
    ];

    const formatosFecha = [
        { value: 'DD/MM/AAAA', label: 'DD/MM/AAAA' },
        { value: 'MM/DD/AAAA', label: 'MM/DD/AAAA' },
    ];

    const formatosHora = [
        { value: '12h', label: '12 horas (AM/PM)' },
        { value: '24h', label: '24 horas' },
    ];

    async function guardar() {
        loading = true;
        try {
            await saveConfiguracion({
                simbolo_moneda: simbolo,
                posicion_simbolo: posicion,
                separador_miles: separadorMiles,
                separador_decimal: separadorDecimal,
                formato_fecha: formatoFecha,
                formato_hora: formatoHora,
                limite_dias_cierre_recepcion: limiteCierre,
            });
            toast.success('Formato actualizado.');
            onsave();
        } catch (e: any) {
            toast.error(e.message);
        } finally {
            loading = false;
        }
    }
</script>

<div class="space-y-4">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <InputHotel label="Símbolo de Moneda" bind:value={simbolo} placeholder="$" />
        <Select label="Posición del Símbolo" options={posiciones} bind:value={posicion} />
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <InputHotel label="Separador de Miles" bind:value={separadorMiles} placeholder="," />
        <InputHotel label="Separador Decimal" bind:value={separadorDecimal} placeholder="." />
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Select label="Formato de Fecha" options={formatosFecha} bind:value={formatoFecha} />
        <Select label="Formato de Hora" options={formatosHora} bind:value={formatoHora} />
    </div>
    <InputHotel label="Límite días cierre (Recepción)" type="number" bind:value={limiteCierre} placeholder="7" />

    <div class="pt-4 border-t border-hotel-border/50">
        <Button variant="gold" onclick={guardar} loading={loading}>Guardar Formato</Button>
    </div>
</div>