<script lang="ts">
    import { onMount } from 'svelte';
    import { toast } from '$lib/stores/toast';
    import InputHotel from '$components/ui/Input.svelte';
    import Select from '$components/ui/Select.svelte';
    import Button from '$components/ui/Button.svelte';
    import { agregarConsumo } from '$lib/services/reservaciones';
    import { fetchProductos } from '$lib/services/inventario';
    import type { Producto } from '$lib/types/producto';

    let {
        reservaId,
        onclose,
    }: {
        reservaId: number;
        onclose: () => void;
    } = $props();

    let loading = $state(false);
    let productos = $state<Producto[]>([]);
    let productoId = $state<number | null>(null);
    let cantidad = $state(1);

    // Producto seleccionado
    let productoSeleccionado = $derived(
        productos.find(p => p.id === productoId) || null
    );

    // Tipo derivado del producto
    let tipoConsumo = $derived(productoSeleccionado?.categoria || 'Otro');

    // Precio derivado del producto
    let precioUnitario = $derived(
        productoSeleccionado ? parseFloat(productoSeleccionado.precio_venta) : 0
    );

    // Total
    let total = $derived(cantidad * precioUnitario);

    // Productos agrupados por categoría para el Select
    let opcionesProductos = $derived([
        { value: '', label: 'Seleccionar producto/servicio...' },
        ...productos
            .filter(p => p.activo !== false)
            .map(p => ({
                value: String(p.id),
                label: `${p.nombre} — $${p.precio_venta} (${p.categoria})`
            }))
    ]);

    onMount(async () => {
        try {
            productos = await fetchProductos();
        } catch { }
    });

    function seleccionarProducto(value: string) {
        productoId = Number(value) || null;
        cantidad = 1; // Resetear cantidad al cambiar producto
    }

    async function guardar() {
        if (!productoId) {
            toast.error('Selecciona un producto o servicio.');
            return;
        }
        if (cantidad <= 0) {
            toast.error('La cantidad debe ser mayor a 0.');
            return;
        }

        loading = true;
        try {
            await agregarConsumo(reservaId, {
                tipo_consumo: tipoConsumo,
                descripcion: productoSeleccionado!.nombre,
                cantidad,
                precio_unitario: precioUnitario,
                producto_id: productoId,
            });
            toast.success('Consumo registrado correctamente.');
            onclose();
        } catch (e: any) {
            toast.error(e.message || 'Error al registrar consumo.');
        } finally {
            loading = false;
        }
    }
</script>

<div class="space-y-5">
    <!-- Producto/Servicio -->
    <div class="p-4 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
        <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Producto o Servicio</p>
        <Select
            label="Seleccionar"
            options={opcionesProductos}
            value={String(productoId || '')}
            onchange={(e: any) => seleccionarProducto(e.target.value)}
        />
    </div>

    <!-- Info del producto seleccionado -->
    {#if productoSeleccionado}
        <div class="p-4 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-3">
            <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Detalle</p>

            <div class="grid grid-cols-2 gap-3 text-sm">
                <div>
                    <p class="text-[10px] uppercase text-hotel-text-tertiary">Tipo</p>
                    <p class="font-bold text-hotel-text-primary">{tipoConsumo}</p>
                </div>
                <div>
                    <p class="text-[10px] uppercase text-hotel-text-tertiary">Precio Unitario</p>
                    <p class="font-bold text-hotel-gold">${precioUnitario.toFixed(2)}</p>
                </div>
                <div>
                    <p class="text-[10px] uppercase text-hotel-text-tertiary">Stock disponible</p>
                    <p class="font-bold text-hotel-text-primary">
                        {productoSeleccionado.maneja_stock ? productoSeleccionado.stock_actual : 'Ilimitado'}
                    </p>
                </div>
                <div>
                    <p class="text-[10px] uppercase text-hotel-text-tertiary">Unidad</p>
                    <p class="font-bold text-hotel-text-primary">{productoSeleccionado.unidad}</p>
                </div>
            </div>

            <InputHotel label="Cantidad" type="number" bind:value={cantidad} />

            <div class="flex items-center justify-between p-3 rounded-xl bg-hotel-gold/5 border border-hotel-gold/20">
                <span class="text-sm text-hotel-text-secondary">Total</span>
                <span class="text-lg font-bold text-hotel-gold">${total.toFixed(2)}</span>
            </div>
        </div>
    {/if}

    <div class="flex gap-3 pt-4 border-t border-hotel-border/50">
        <Button variant="gold" onclick={guardar} loading={loading} fullWidth>
            Registrar Consumo
        </Button>
        <Button variant="ghost" onclick={onclose}>Cancelar</Button>
    </div>
</div>