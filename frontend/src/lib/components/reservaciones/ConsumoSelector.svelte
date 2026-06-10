<script lang="ts">
    import { toast } from '$lib/stores/toast';
    import InputHotel from '$components/ui/Input.svelte';
    import Select from '$components/ui/Select.svelte';
    import Button from '$components/ui/Button.svelte';
    import { agregarConsumo } from '$lib/services/reservaciones';

    let {
        reservaId,
        onclose,
    }: {
        reservaId: number;
        onclose: () => void;
    } = $props();

    let loading = $state(false);
    let tipo = $state('Restaurante');
    let descripcion = $state('');
    let cantidad = $state(1);
    let precioUnitario = $state(0);

    const tipos = [
        { value: 'Restaurante', label: 'Restaurante' },
        { value: 'Minibar', label: 'Minibar' },
        { value: 'Lavandería', label: 'Lavandería' },
        { value: 'Llamadas', label: 'Llamadas' },
        { value: 'Otro', label: 'Otro' },
    ];

    async function guardar() {
        loading = true;
        try {
            await agregarConsumo(reservaId, {
                tipo_consumo: tipo,
                descripcion,
                cantidad,
                precio_unitario: precioUnitario,
            });
            toast.success('Consumo registrado.');
            onclose();
        } catch (e: any) {
            toast.error(e.message);
        } finally {
            loading = false;
        }
    }
</script>

<div class="space-y-4">
    <Select label="Tipo" options={tipos} bind:value={tipo} />
    <InputHotel label="Descripción" bind:value={descripcion} />
    <InputHotel label="Cantidad" type="number" bind:value={cantidad} />
    <InputHotel label="Precio Unitario ($)" type="number" bind:value={precioUnitario} />
    <p class="text-sm text-hotel-text-secondary">
        Total: <span class="font-bold text-hotel-gold">${(cantidad * precioUnitario).toFixed(2)}</span>
    </p>

    <div class="flex gap-3 pt-4 border-t border-hotel-border/50">
        <Button variant="gold" onclick={guardar} loading={loading}>Registrar Consumo</Button>
        <Button variant="ghost" onclick={onclose}>Cancelar</Button>
    </div>
</div>