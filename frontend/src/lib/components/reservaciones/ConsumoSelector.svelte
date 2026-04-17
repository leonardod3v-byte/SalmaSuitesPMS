<script lang="ts">
  import { reservacionesApi } from '$lib/services/reservaciones';
  import { apiFetch } from '$lib/services/api';
  import { toast } from '$lib/stores/toast';

  interface Producto {
    id: number; nombre: string; categoria: string;
    precio_venta: string; stock_actual: number; activo: boolean;
  }

  let { reservaId, onaguardado }: {
    reservaId:  number;
    onaguardado: () => void;
  } = $props();

  let productos      = $state<Producto[]>([]);
  let cargando       = $state(true);
  let guardando      = $state(false);
  let busqueda       = $state('');

  // Líneas del pedido
  let lineas = $state<{ producto: Producto; cantidad: number; nota: string }[]>([]);

  const CATS: Record<string, { label: string, icon: string }> = {
    bebida:  { label: 'Bebidas', icon: '🥤' },
    comida:  { label: 'Comida', icon: '🍽️' },
    snack:   { label: 'Snacks', icon: '🍿' },
    licor:   { label: 'Licores', icon: '🥂' },
    higiene: { label: 'Higiene', icon: '🧼' },
    otro:    { label: 'Otros', icon: '📦' },
  };

  $effect(() => {
    apiFetch<Producto[]>('/inventario/?activo=true')
      .then(d => { productos = d; })
      .catch(() => toast.send('Error al sincronizar inventario', 'error'))
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
    lineas.reduce((acc, l) => acc + l.cantidad * parseFloat(l.producto.precio_venta), 0)
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
      toast.send('Comanda registrada en cuenta del huésped', 'success');
      lineas = [];
      onaguardado();
    } catch {
      toast.send('Error al procesar la comanda', 'error');
    } finally {
      guardando = false;
    }
  }
</script>

<div class="grid grid-cols-1 lg:grid-cols-12 gap-6 h-full min-h-500px">

  <div class="lg:col-span-8 flex flex-col gap-4">
    <div class="relative group">
      <span class="absolute inset-y-0 left-4 flex items-center text-hotel-text-tertiary">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
      </span>
      <input
        bind:value={busqueda}
        type="search"
        placeholder="Buscar por nombre de producto..."
        class="w-full bg-hotel-surface border-2 border-hotel-border rounded-2xl py-4 pl-12 pr-4 text-sm text-hotel-text-primary focus:border-hotel-gold outline-none transition-all placeholder:text-hotel-text-tertiary/50 shadow-sm"
      />
    </div>

    {#if cargando}
      <div class="flex-1 flex flex-col items-center justify-center gap-4 text-hotel-text-tertiary animate-pulse">
        <div class="w-10 h-10 border-2 border-hotel-gold border-t-transparent rounded-full animate-spin"></div>
        <p class="text-[10px] font-black uppercase tracking-[0.2em]">Consultando Inventario...</p>
      </div>
    {:else if Object.keys(porCategoria).length === 0}
      <div class="flex-1 flex flex-col items-center justify-center text-hotel-text-tertiary grayscale opacity-50">
        <span class="text-4xl mb-2">📦</span>
        <p class="text-xs font-bold uppercase tracking-widest">Sin stock disponible</p>
      </div>
    {:else}
      <div class="flex-1 overflow-y-auto pr-2 custom-scrollbar space-y-8">
        {#each Object.entries(porCategoria) as [cat, prods]}
          <div class="space-y-4">
            <h3 class="flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.3em] text-hotel-gold border-l-2 border-hotel-gold pl-3">
              <span>{CATS[cat]?.icon ?? '✨'}</span>
              <span>{CATS[cat]?.label ?? cat}</span>
            </h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
              {#each prods as p (p.id)}
                <button
                  onclick={() => agregarLinea(p)}
                  class="group flex flex-col p-4 rounded-2xl bg-hotel-surface border-2 border-hotel-border hover:border-hotel-gold/50 hover:shadow-lg hover:shadow-hotel-gold/5 transition-all duration-300 text-left"
                >
                  <div class="flex justify-between items-start mb-1">
                    <p class="text-xs font-black text-hotel-text-primary group-hover:text-hotel-gold transition-colors truncate pr-2">
                      {p.nombre}
                    </p>
                    <span class="text-[10px] font-mono text-hotel-gold-light">${parseFloat(p.precio_venta).toFixed(2)}</span>
                  </div>
                  <div class="flex justify-between items-center mt-auto">
                    <span class="text-[9px] font-bold text-hotel-text-tertiary uppercase tracking-tighter">Stock: {p.stock_actual}</span>
                    <span class="w-6 h-6 rounded-lg bg-hotel-gold/10 flex items-center justify-center text-hotel-gold group-hover:bg-hotel-gold group-hover:text-hotel-bg transition-all">
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M12 4v16m8-8H4"/></svg>
                    </span>
                  </div>
                </button>
              {/each}
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>

  <div class="lg:col-span-4 bg-hotel-surface rounded-[2.5rem] border border-hotel-border shadow-xl flex flex-col overflow-hidden">
    <header class="p-6 bg-hotel-bg/50 border-b border-hotel-border">
      <p class="text-[10px] font-black uppercase tracking-[0.3em] text-hotel-text-tertiary">Comanda de Consumo</p>
      <div class="flex justify-between items-baseline mt-1">
        <h4 class="font-display text-xl italic font-black text-hotel-text-primary">Reserva #{reservaId}</h4>
        <span class="text-[10px] font-bold text-hotel-gold">{lineas.length} ítems</span>
      </div>
    </header>

    <div class="flex-1 overflow-y-auto p-6 custom-scrollbar space-y-4">
      {#if lineas.length === 0}
        <div class="h-full flex flex-col items-center justify-center text-center opacity-40">
          <div class="w-16 h-16 border-2 border-dashed border-hotel-text-tertiary rounded-full flex items-center justify-center mb-4 text-2xl">🛒</div>
          <p class="text-[10px] font-black uppercase tracking-widest leading-relaxed">Añada productos<br/>del catálogo</p>
        </div>
      {:else}
        {#each lineas as l (l.producto.id)}
          <div class="flex flex-col gap-3 p-4 bg-hotel-bg rounded-2xl border border-hotel-border/60 animate-in slide-in-from-right-4">
            <div class="flex justify-between items-start">
              <p class="text-[11px] font-bold text-hotel-text-primary leading-tight">{l.producto.nombre}</p>
              <button
                onclick={() => quitarLinea(l.producto.id)}
                class="p-1 hover:text-hotel-error-light text-hotel-text-tertiary transition-colors"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M6 18L18 6M6 6l12 12" stroke-width="2.5"/></svg>
              </button>
            </div>
            
            <div class="flex items-center justify-between">
              <div class="flex items-center bg-hotel-surface rounded-lg p-1 border border-hotel-border">
                <button
                  onclick={() => l.cantidad = Math.max(1, l.cantidad - 1)}
                  class="w-7 h-7 flex items-center justify-center text-hotel-text-tertiary hover:text-hotel-gold transition-colors font-black"
                >−</button>
                <span class="w-8 text-center text-xs font-black text-hotel-gold">{l.cantidad}</span>
                <button
                  onclick={() => l.cantidad++}
                  class="w-7 h-7 flex items-center justify-center text-hotel-text-tertiary hover:text-hotel-gold transition-colors font-black"
                >+</button>
              </div>
              <span class="text-xs font-black text-hotel-text-primary">
                ${(l.cantidad * parseFloat(l.producto.precio_venta)).toFixed(2)}
              </span>
            </div>
          </div>
        {/each}
      {/if}
    </div>

    {#if lineas.length > 0}
      <footer class="p-6 bg-hotel-bg/50 border-t border-hotel-border space-y-4">
        <div class="flex justify-between items-center px-2">
          <span class="text-[10px] font-black uppercase tracking-[0.4em] text-hotel-text-tertiary">Total Cargo</span>
          <span class="text-2xl font-display font-black italic text-hotel-gold">${totalCarrito.toFixed(2)}</span>
        </div>
        
        <button
          onclick={confirmarConsumos}
          disabled={guardando}
          class="w-full btn-gold py-4 text-[11px] font-black uppercase tracking-[0.3em] shadow-hotel-gold/10"
        >
          {#if guardando} Cargando Cuenta... {:else} Confirmar Consumos {/if}
        </button>
      </footer>
    {/if}
  </div>
</div>

<style>
  @reference "../../../app.css";
  .custom-scrollbar::-webkit-scrollbar { width: 3px; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #d4af3730; border-radius: 10px; }
</style>