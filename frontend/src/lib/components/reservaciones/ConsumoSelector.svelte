<script lang="ts">
  import { apiFetch } from '$lib/services/api';
  import { reservacionesApi } from '$lib/services/reservaciones';
  import { toast } from '$lib/stores/toast';
  import Button from '$lib/components/Button.svelte';
  import Icon from '$lib/components/Icons.svelte';

  interface Producto {
    id: number; nombre: string; categoria: string;
    precio_venta: string; stock_actual: number; activo: boolean;
  }

  let { reservaId, onaguardado }: {
    reservaId: number;
    onaguardado: () => void;
  } = $props();

  let productos = $state<Producto[]>([]);
  let cargando = $state(true);
  let guardando = $state(false);
  let busqueda = $state('');
  let lineas = $state<{ producto: Producto; cantidad: number; nota: string }[]>([]);
  let lineasConsumo = $state<{ producto: { id: number; nombre: string; precio_venta: string }; cantidad: number; nota: string }[]>([]);

  const CATS: Record<string, { label: string, icon: string }> = {
    bebida:  { label: 'Bebidas', icon: '🍺' },
    comida:  { label: 'Comida', icon: '🍽️' },
    snack:   { label: 'Snacks', icon: '🍿' },
    licor:   { label: 'Licores', icon: '🥃' },
    higiene: { label: 'Higiene', icon: '🧴' },
    otro:    { label: 'Otros', icon: '📦' },
  };

  $effect(() => {
    apiFetch<Producto[]>('/inventario/?activo=true')
      .then(d => { productos = d; })
      .catch(() => toast.send('Error al cargar inventario', 'error'))
      .finally(() => cargando = false);
  });

  const productosFiltrados = $derived(
    productos.filter(p =>
      p.activo && p.stock_actual > 0 &&
      (!busqueda || p.nombre.toLowerCase().includes(busqueda.toLowerCase()))
    )
  );

  const porCategoria = $derived(
    productosFiltrados.reduce((acc, p) => {
      const cat = p.categoria;
      if (!acc[cat]) acc[cat] = [];
      acc[cat].push(p);
      return acc;
    }, {} as Record<string, Producto[]>)
  );

  function agregarLinea(producto: Producto) {
    const existe = lineas.find(l => l.producto.id === producto.id);
    if (existe) {
      lineas = lineas.map(l =>
        l.producto.id === producto.id ? { ...l, cantidad: l.cantidad + 1 } : l
      );
    } else {
      lineas = [...lineas, { producto, cantidad: 1, nota: '' }];
    }
  }

  function quitarLinea(id: number) {
    lineas = lineas.filter(l => l.producto.id !== id);
  }

  const totalCarrito = $derived(
    lineasConsumo.reduce((acc, l) => acc + l.cantidad * parseFloat(l.producto.precio_venta), 0)
  );

  async function confirmarConsumos() {
    if (lineas.length === 0) return;
    guardando = true;
    try {
      await Promise.all(
        lineas.map(l =>
          reservacionesApi.agregarConsumo(reservaId, {
            producto:        l.producto.nombre,
            cantidad:        l.cantidad,
            precio_unitario: l.producto.precio_venta as unknown as number,
            noches_asociadas: 1,
            nota:            l.nota,
          })
        )
      );
      toast.send('Consumos registrados', 'success');
      lineas = [];
      onaguardado();
    } catch {
      toast.send('Error al registrar consumos', 'error');
    } finally {
      guardando = false;
    }
  }
</script>

<div class="space-y-6">
  <div class="bg-hotel-surface/40 rounded-2xl p-6 border border-hotel-border">
    <div class="relative mb-4">
      <Icon name="search" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-hotel-text-tertiary" />
      <input
        type="text"
        bind:value={busqueda}
        placeholder="Buscar producto..."
        class="w-full bg-hotel-bg border border-hotel-border rounded-xl py-2 pl-10 pr-4 text-sm focus:border-hotel-gold outline-none"
      />
    </div>

    {#if cargando}
      <div class="flex justify-center py-12">
        <div class="w-8 h-8 border-2 border-hotel-gold border-t-transparent rounded-full animate-spin"></div>
      </div>
    {:else if Object.keys(porCategoria).length === 0}
      <div class="text-center py-12 text-hotel-text-tertiary">
        <Icon name="box" class="w-12 h-12 mx-auto mb-3 opacity-30" />
        <p class="text-xs">No hay productos disponibles</p>
      </div>
    {:else}
      <div class="space-y-6 max-h-80 overflow-y-auto custom-scrollbar pr-2">
        {#each Object.entries(porCategoria) as [cat, prods]}
          <div>
            <h4 class="text-[10px] font-black uppercase tracking-widest text-hotel-gold mb-2 flex items-center gap-1">
              <span>{CATS[cat]?.icon}</span> {CATS[cat]?.label ?? cat}
            </h4>
            <div class="grid grid-cols-2 gap-2">
              {#each prods as p (p.id)}
                <button
                  onclick={() => agregarLinea(p)}
                  class="flex justify-between items-center p-2 rounded-xl border border-hotel-border hover:border-hotel-gold/50 transition-all"
                >
                  <span class="text-xs font-bold text-hotel-text-primary truncate">{p.nombre}</span>
                  <span class="text-[10px] font-mono text-hotel-gold">${p.precio_venta}</span>
                </button>
              {/each}
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>

{#if lineas.length > 0}
    <div class="bg-hotel-surface/40 rounded-2xl p-4">
      <div class="flex justify-between items-center mb-3">
        <span class="text-xs font-bold uppercase">Carrito ({lineas.length})</span>
        <span class="text-lg font-black text-hotel-gold">${totalCarrito.toFixed(2)}</span>
      </div>
      <div class="space-y-2 max-h-48 overflow-y-auto">
        {#each lineas as l}
          <div class="flex justify-between items-center p-2 bg-hotel-bg/30 rounded-lg">
            <div class="flex items-center gap-2">
              <button onclick={() => l.cantidad = Math.max(1, l.cantidad-1)} class="w-6 h-6 rounded bg-hotel-surface">−</button>
              <span class="w-6 text-center">{l.cantidad}</span>
              <button onclick={() => l.cantidad++} class="w-6 h-6 rounded bg-hotel-surface">+</button>
              <span class="text-sm">{l.producto.nombre}</span>
            </div>
            <div class="flex items-center gap-2">
              <span>${(l.cantidad * parseFloat(l.producto.precio_venta)).toFixed(2)}</span>
              <button onclick={() => quitarLinea(l.producto.id)} class="text-hotel-error-light">✕</button>
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}

  <div class="flex justify-end gap-3">
    <Button variant="ghost" onclick={onaguardado}>Cancelar</Button>
    <Button variant="gold" onclick={confirmarConsumos} disabled={guardando || lineas.length === 0}>
      {guardando ? 'Procesando...' : 'Confirmar'}
    </Button>
  </div>
</div>