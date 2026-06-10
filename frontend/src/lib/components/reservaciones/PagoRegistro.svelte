<script lang="ts">
    import { toast } from '$lib/stores/toast';
    import InputHotel from '$components/ui/Input.svelte';
    import Select from '$components/ui/Select.svelte';
    import Button from '$components/ui/Button.svelte';
    import { registrarPago } from '$lib/services/reservaciones';

    let {
        reservaId,
        onclose,
    }: {
        reservaId: number;
        onclose: () => void;
    } = $props();

    let loading = $state(false);
    let monto = $state(0);
    let metodoPago = $state<'Efectivo' | 'Tarjeta' | 'PagoMovil'>('Efectivo');
    let numeroReferencia = $state('');

    const metodos = [
        { value: 'Efectivo', label: 'Efectivo' },
        { value: 'Tarjeta', label: 'Tarjeta' },
        { value: 'PagoMovil', label: 'Pago Móvil' },
    ];

    async function guardar() {
        loading = true;
        try {
            await registrarPago(reservaId, {
                monto,
                metodo_pago: metodoPago,
                numero_referencia: numeroReferencia,
            });
            toast.success('Pago registrado.');
            onclose();
        } catch (e: any) {
            toast.error(e.message);
        } finally {
            loading = false;
        }
    }
</script>

<div class="space-y-4">
    <InputHotel label="Monto ($)" type="number" bind:value={monto} />
    <Select label="Método de pago" options={metodos} bind:value={metodoPago} />
    {#if metodoPago !== 'Efectivo'}
        <InputHotel label="Nº Referencia" bind:value={numeroReferencia} />
    {/if}

    <div class="flex gap-3 pt-4 border-t border-hotel-border/50">
        <Button variant="gold" onclick={guardar} loading={loading}>Registrar Pago</Button>
        <Button variant="ghost" onclick={onclose}>Cancelar</Button>
    </div>
</div>