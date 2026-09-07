<script lang="ts">
    import { onMount } from 'svelte';
    import { toast } from '$lib/stores/toast';
    import InputHotel from '$components/ui/Input.svelte';
    import Select from '$components/ui/Select.svelte';
    import Textarea from '$components/ui/Textarea.svelte';
    import Button from '$components/ui/Button.svelte';
    import { fetchProductos, registrarEntrada, registrarAjuste } from '$lib/services/inventario';
    import type { Producto } from '$lib/types/producto';

    let {
        tipo = 'entrada',
        onclose = () => {},
    }: {
        tipo?: 'entrada' | 'ajuste';
        onclose?: () => void;
    } = $props();

    let loading = $state(false);
    let productos = $state<Producto[]>([]);
    let productoId = $state<number | null>(null);
    let cantidad = $state<number>(1);
    let motivo = $state('');

    onMount(async () => {
        try {
            productos = await fetchProductos();
        } catch { }
    });

    async function handleSubmit(e: Event) {
        e.preventDefault();
        if (!productoId) return;

        loading = true;
        try {
            if (tipo === 'entrada') {
                await registrarEntrada({
                    producto_id: productoId,
                    cantidad,
                    motivo: motivo || 'Entrada manual',
                });
                toast.success('Entrada registrada.');
            } else {
                await registrarAjuste({
                    producto_id: productoId,
                    cantidad,
                    motivo: motivo || 'Ajuste manual',
                });
                toast.success('Ajuste registrado.');
            }
            onclose();
        } catch (e: any) {
            toast.error(e.message);
        } finally {
            loading = false;
        }
    }

    const opcionesProductos = $derived(
        productos.map(p => ({ value: String(p.id), label: `${p.nombre} (Stock: ${p.stock_actual})` }))
    );
</script>

<form onsubmit={handleSubmit} class="space-y-6">
    <div class="p-5 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
        <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">
            {tipo === 'entrada' ? 'Registrar Entrada' : 'Registrar Ajuste'}
        </p>
        <Select
            label="Producto"
            options={[{ value: '', label: 'Seleccionar producto...' }, ...opcionesProductos]}
            bind:value={productoId as any}
            required
        />
        <InputHotel
            label={tipo === 'entrada' ? 'Cantidad a ingresar' : 'Cantidad (+ entrada, - salida)'}
            type="number"
            bind:value={cantidad}
            required
        />
        <Textarea label="Motivo" bind:value={motivo} placeholder="Motivo del movimiento..." rows={2} />
    </div>

    <div class="flex gap-3 pt-4 border-t border-hotel-border/50">
        <Button type="submit" variant="gold" loading={loading}>
            {tipo === 'entrada' ? 'Registrar Entrada' : 'Registrar Ajuste'}
        </Button>
        <Button type="button" variant="ghost" onclick={onclose}>Cancelar</Button>
    </div>
</form>