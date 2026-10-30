<script lang="ts">
    import { onMount } from 'svelte';
    import { toast } from '$lib/stores/toast';
    import InputHotel from '$components/ui/Input.svelte';
    import Select from '$components/ui/Select.svelte';
    import Button from '$components/ui/Button.svelte';
    import Icon from '$components/ui/Icons.svelte';
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
    let filtroCategoria = $state('');

    // Categorías disponibles
    const categorias = [
        { value: '', label: 'Todas las categorías' },
        { value: 'Comida', label: 'Comida / Restaurante' },
        { value: 'Bebida', label: 'Bebidas' },
        { value: 'Snack', label: 'Snacks / Minibar' },
        { value: 'Lavandería', label: 'Lavandería' },
        { value: 'Llamadas', label: 'Llamadas' },
    ];

    // Producto seleccionado
    let productoSeleccionado = $derived(
        productos.find(p => p.id === productoId) || null
    );

    let tipoConsumo = $derived(productoSeleccionado?.categoria || 'Otro');
    let precioUnitario = $derived(productoSeleccionado ? parseFloat(productoSeleccionado.precio_venta) : 0);
    let total = $derived(cantidad * precioUnitario);

    // Filtrar productos por categoría
    let productosFiltrados = $derived(
        filtroCategoria
            ? productos.filter(p => p.categoria === filtroCategoria && p.activo !== false)
            : productos.filter(p => p.activo !== false)
    );

    let opcionesProductos = $derived([
        { value: '', label: 'Seleccionar producto/servicio...' },
        ...productosFiltrados.map(p => ({
            value: String(p.id),
            label: `${p.nombre} — $${p.precio_venta}`
        }))
    ]);

    // Evaluar si hay stock bajo
    let stockBajo = $derived(
        productoSeleccionado?.maneja_stock &&
        parseFloat(productoSeleccionado.stock_actual) <= parseFloat(productoSeleccionado.stock_minimo)
    );

    onMount(async () => {
        try {
            productos = await fetchProductos();
        } catch { }
    });

    function seleccionarProducto(value: string) {
        productoId = Number(value) || null;
        cantidad = 1;
    }

    // Resetear producto si cambia la categoría
    function cambiarCategoria() {
        productoId = null;
        cantidad = 1;
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
    <!-- Selección de categoría y producto -->
    <div class="p-4 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
        <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">1. ¿Qué desea consumir?</p>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
                <Select
                    label="Categoría"
                    options={categorias}
                    bind:value={filtroCategoria}
                    onchange={cambiarCategoria}
                />
            </div>
            <div>
                <Select
                    label="Producto / Servicio"
                    options={opcionesProductos}
                    value={String(productoId || '')}
                    onchange={(e: any) => seleccionarProducto(e.target.value)}
                />
            </div>
        </div>
    </div>

    <!-- Detalles del producto seleccionado -->
    {#if productoSeleccionado}
        <div class="p-4 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4 animate-in fade-in slide-in-from-top-2">
            <div class="flex items-start justify-between">
                <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">2. Detalles del Consumo</p>
                <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-bold bg-hotel-surface border border-hotel-border text-hotel-text-tertiary uppercase">
                    {tipoConsumo}
                </span>
            </div>

            <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                    <p class="text-[10px] uppercase text-hotel-text-tertiary mb-0.5">Precio Unitario</p>
                    <p class="font-bold text-hotel-gold text-lg">${precioUnitario.toFixed(2)}</p>
                </div>
                <div>
                    <p class="text-[10px] uppercase text-hotel-text-tertiary mb-0.5">Stock disponible</p>
                    {#if productoSeleccionado.maneja_stock}
                        <p class="font-bold {stockBajo ? 'text-hotel-error-light' : 'text-hotel-text-primary'} flex items-center gap-1.5">
                            {productoSeleccionado.stock_actual} {productoSeleccionado.unidad}s
                            {#if stockBajo}
                                <Icon name="alert" class="w-3.5 h-3.5" />
                            {/if}
                        </p>
                    {:else}
                        <p class="font-bold text-hotel-success-light">Ilimitado</p>
                    {/if}
                </div>
            </div>

            <div class="pt-2">
                <InputHotel label="Cantidad a consumir" type="number" bind:value={cantidad} />
            </div>

            <!-- Total -->
            <div class="flex items-center justify-between p-3 rounded-xl bg-hotel-gold/5 border border-hotel-gold/20">
                <span class="text-sm font-medium text-hotel-text-secondary">Total a cargar</span>
                <span class="text-xl font-bold text-hotel-gold">${total.toFixed(2)}</span>
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
