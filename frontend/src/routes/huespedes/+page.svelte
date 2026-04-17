<script lang="ts">
  import type { PageData } from './$types';
  import { invalidateAll, goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { auth } from '$lib/stores/auth';
  import { type HuespedListItem, type Huesped } from '$lib/services/huespedes';
  import GuestTable from '$lib/components/huespedes/GuestTable.svelte';
  import GuestModal from '$lib/components/huespedes/GuestModal.svelte';

  let { data }: { data: PageData } = $props();

  // Reactividad Svelte 5: Sincronización limpia con los datos del Load Function
  let huespedes = $state<HuespedListItem[]>([]);
  $effect(() => { huespedes = data.huespedes ?? []; });

  // Estado de Filtros (Derivados de la URL para consistencia en recarga)
  let busqueda = $state(data.search ?? '');
  let soloVip = $state(data.vip === 'true');

  const tieneFiltros = $derived(busqueda !== '' || soloVip);
  const isAdmin = $derived($auth?.user?.role === 'admin');

  // Lógica de Navegación y Filtros (Debounce integrado)
  let timer: ReturnType<typeof setTimeout>;
  
  function updateURL() {
    const params = new URLSearchParams($page.url.searchParams);
    if (busqueda.trim()) params.set('search', busqueda.trim()); else params.delete('search');
    if (soloVip) params.set('vip', 'true'); else params.delete('vip');
    
    goto(`?${params.toString()}`, { 
      keepFocus: true, 
      replaceState: true, 
      noScroll: true 
    });
  }

  function onSearch() {
    clearTimeout(timer);
    timer = setTimeout(updateURL, 300);
  }

  function resetFiltros() {
    busqueda = '';
    soloVip = false;
    goto($page.url.pathname);
  }

  // Modales
  let modalCrear = $state(false);
  let huespedEditando = $state<Huesped | null>(null);

  // Mutación Optimista: UI instantánea antes de que el servidor responda
  function onVipToggled(id: number, nuevoEstado: boolean) {
    huespedes = huespedes.map(h => h.id === id ? { ...h, es_vip: nuevoEstado } : h);
  }
</script>

<svelte:head>
  <title>Gestión de Huéspedes | SalmaSuitesPMS</title>
</svelte:head>

<div class="max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">

  <header class="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-hotel-border/50 pb-8">
    <div class="space-y-1">
      <h1 class="text-4xl font-display font-black italic text-hotel-text-primary tracking-tight">
        Huéspedes
      </h1>
      <p class="text-xs font-medium text-hotel-text-tertiary flex items-center gap-2 uppercase tracking-0.1em">
        <span class="w-2 h-2 rounded-full bg-hotel-gold animate-pulse"></span>
        {huespedes.length} Registros
        {#if tieneFiltros}
          <span class="text-hotel-gold-light border-l border-hotel-border pl-2">Vista Filtrada</span>
        {/if}
      </p>
    </div>

    {#if isAdmin}
    <div class="flex items-center gap-3">
      <button class="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-hotel-border
               text-xs font-bold text-hotel-text-secondary hover:border-hotel-gold/40
               hover:text-hotel-gold transition-all" onclick={() => {}}>
        <svg class="w-4 h-4 text-hotel-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        <span class="font-black uppercase text-[10px] tracking-widest text-hotel-text-secondary">Exportar registro</span>
      </button>

      <button class="btn-gold group px-6 py-3" onclick={() => modalCrear = true}>
        <svg class="w-4 h-4 transition-transform group-hover:rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 5v14M5 12h14"/>
        </svg>
        <span class="font-black uppercase text-[10px] tracking-widest text-hotel-bg">Registrar huésped</span>
      </button>
    </div>
    {/if}
  </header>

  <section class="grid grid-cols-1 lg:grid-cols-4 gap-4 items-center bg-hotel-surface/40 p-2 rounded-2xl border border-hotel-border shadow-hotel-sm backdrop-blur-md">
    
    <div class="lg:col-span-2 relative group">
      <div class="absolute left-4 top-1/2 -translate-y-1/2 text-hotel-text-tertiary group-focus-within:text-hotel-gold transition-colors">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <circle cx="11" cy="11" r="8" stroke-width="2.5"/><path d="m21 21-4.35-4.35" stroke-width="2.5"/>
        </svg>
      </div>
      <input
        bind:value={busqueda}
        oninput={onSearch}
        type="search"
        placeholder="Buscar por nombre, documento o contacto..."
        class="input-hotel pl-12 bg-hotel-bg border-transparent focus:border-hotel-gold/30 w-full h-12"
      />
    </div>

    <div class="flex items-center gap-2 lg:justify-end lg:col-span-2 px-2">
      <button
        onclick={() => { soloVip = !soloVip; updateURL(); }}
        class="flex-1 lg:flex-none inline-flex items-center justify-center gap-2 px-6 h-12 rounded-xl text-[10px] font-black
               uppercase tracking-widest border transition-all duration-300
               {soloVip
                 ? 'bg-hotel-vip/20 border-hotel-vip/50 text-hotel-vip-light'
                 : 'bg-hotel-bg border-hotel-border text-hotel-text-tertiary hover:border-hotel-gold/50'}"
      >
        <svg class="w-3.5 h-3.5 {soloVip ? 'fill-hotel-vip' : 'fill-transparent stroke-current'}" viewBox="0 0 24 24">
          <path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z"/>
        </svg>
        Filtrar VIP
      </button>

      {#if tieneFiltros}
        <button 
          onclick={resetFiltros}
          class="h-12 px-4 text-[9px] font-black uppercase tracking-widest text-hotel-error-light hover:bg-hotel-error/5 rounded-xl transition-all"
        >
          Limpiar
        </button>
      {/if}
    </div>
  </section>

  <main class="min-h-400px">
    <GuestTable
      {huespedes}
      {onVipToggled}
      onVerDetalle={(h) => huespedEditando = h as unknown as Huesped}
    />
  </main>
</div>

{#if modalCrear}
  <GuestModal
    modo="crear"
    onclose={() => modalCrear = false}
    onupdated={() => { modalCrear = false; invalidateAll(); }}
  />
{/if}

{#if huespedEditando}
  <GuestModal
    modo="editar"
    data={huespedEditando}
    onclose={() => huespedEditando = null}
    onupdated={() => { huespedEditando = null; invalidateAll(); }}
  />
{/if}