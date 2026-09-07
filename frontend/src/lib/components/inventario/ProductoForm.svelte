<script lang="ts">
    import { onMount } from 'svelte';
    import { toast } from '$lib/stores/toast';
    import InputHotel from '$components/ui/Input.svelte';
    import Select from '$components/ui/Select.svelte';
    import Textarea from '$components/ui/Textarea.svelte';
    import Button from '$components/ui/Button.svelte';
    import { createProducto, updateProducto, fetchProducto } from '$lib/services/inventario';
    import type { Producto } from '$lib/types/producto';

    let {
        id = null,
        onclose = () => {},
    }: {
        id?: number | null;
        onclose?: () => void;
    } = $props();

    let loading = $state(false);
    let error = $state('');

    let nombre = $state('');
    let descripcion = $state('');
    let categoria = $state('Bebida');
    let precio_venta = $state<number | ''>('');
    let stock_minimo = $state<number>(0);
    let unidad = $state('unidad');
    let manejaStock = $state(true);

    const categorias = [
        { value: 'Comida', label: 'Comida (Restaurante)' },
        { value: 'Bebida', label: 'Bebida (Restaurante/Bar)' },
        { value: 'Snack', label: 'Snack (Minibar)' },
        { value: 'Lavandería', label: 'Lavandería' },
        { value: 'Llamadas', label: 'Llamadas' },
    ];

    const unidades = [
        { value: 'unidad', label: 'Unidad' },
        { value: 'porción', label: 'Porción' },
        { value: 'kg', label: 'Kg' },
        { value: 'servicio', label: 'Servicio' },
    ];

    onMount(async () => {
        if (id) {
            try {
                const p = await fetchProducto(id);
                nombre = p.nombre;
                descripcion = p.descripcion || '';
                categoria = p.categoria;
                precio_venta = parseFloat(p.precio_venta);
                stock_minimo = parseFloat(p.stock_minimo);
                unidad = p.unidad;
            } catch (e: any) {
                error = e.message;
            }
        }
    });

    async function handleSubmit(e: Event) {
        e.preventDefault();
        loading = true;
        error = '';

        const payload = {
            nombre,
            descripcion,
            categoria,
            precio_venta: Number(precio_venta),
            stock_minimo: Number(stock_minimo),
            unidad,
            maneja_stock: manejaStock,
        };

        try {
            if (id) {
                await updateProducto(id, payload);
                toast.success('Producto actualizado.');
            } else {
                await createProducto(payload);
                toast.success('Producto registrado.');
            }
            onclose();
        } catch (e: any) {
            error = e.message;
            toast.error(e.message);
        } finally {
            loading = false;
        }
    }
</script>

<form onsubmit={handleSubmit} class="space-y-6">
    {#if error}
        <div class="flex items-center gap-2 p-3 rounded-xl bg-hotel-error/10 border border-hotel-error/20 text-hotel-error-light text-sm">{error}</div>
    {/if}

    <div class="p-5 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
        <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Información del Producto</p>
        <InputHotel label="Nombre" bind:value={nombre} required placeholder="Ej: Agua Mineral" />
        <Textarea label="Descripción" bind:value={descripcion} placeholder="Descripción breve..." rows={2} />
    </div>

    <div class="p-5 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
        <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Precio y Stock</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <InputHotel label="Precio de Venta ($)" type="number" bind:value={precio_venta} required placeholder="0.00" />
            <InputHotel label="Stock Mínimo" type="number" bind:value={stock_minimo} required placeholder="5" />
            <label class="flex items-center gap-3 cursor-pointer pt-2">
                <input type="checkbox" bind:checked={manejaStock} class="w-4 h-4 rounded border-hotel-border bg-hotel-bg text-hotel-gold focus:ring-hotel-gold" />
                <span class="text-sm text-hotel-text-secondary">Maneja stock</span>
            </label>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Select label="Categoría" options={categorias} bind:value={categoria} required />
            <Select label="Unidad" options={unidades} bind:value={unidad} required />
        </div>
    </div>

    <div class="flex gap-3 pt-4 border-t border-hotel-border/50">
        <Button type="submit" variant="gold" loading={loading}>
            {id ? 'Actualizar Producto' : 'Registrar Producto'}
        </Button>
        <Button type="button" variant="ghost" onclick={onclose}>Cancelar</Button>
    </div>
</form>