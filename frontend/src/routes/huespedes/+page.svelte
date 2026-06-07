<script lang="ts">
  import type { PageData } from './$types';
  import { invalidateAll, goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { auth } from '$lib/stores/auth';
  import { type HuespedListItem, type Huesped } from '$lib/services/huespedes';
  import GuestTable from '$lib/components/huespedes/GuestTable.svelte';
  import GuestModal from '$lib/components/huespedes/GuestModal.svelte';
  import Button from '$lib/components/Button.svelte';
  import Icon from '$lib/components/Icons.svelte';
  import InputHotel from '$lib/components/InputHotel.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';

  let { data }: { data: PageData } = $props();

  // Los datos vienen como array gracias al load corregido
  let huespedes = $state<HuespedListItem[]>([]);
  // Sincronizar cuando data.huespedes cambie (filtros, recarga)
  $effect(() => {
    huespedes = data.huespedes ?? [];
  });

  // Para evitar la advertencia "captura solo el valor inicial", usamos $derived
  // o sincronizamos con $effect. Pero como son valores que vienen de la URL,
  // los tomamos directamente de $page.url.searchParams
  let busqueda = $state('');
  let soloVip = $state(false);

  // Sincronizar con los parámetros de la URL cada vez que cambia la página
  $effect(() => {
    const params = $page.url.searchParams;
    busqueda = params.get('search') ?? '';
    soloVip = params.get('vip') === 'true';
  });

  const tieneFiltros = $derived(busqueda !== '' || soloVip);
  const isAdmin = $derived($auth?.user?.role === 'admin');

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

  let modalCrear = $state(false);
  let huespedEditando = $state<Huesped | null>(null);

  function onVipToggled(id: number, nuevoEstado: boolean) {
    huespedes = huespedes.map(h => h.id === id ? { ...h, es_vip: nuevoEstado } : h);
  }

  // Exportar a CSV (datos actualmente visibles en la tabla)
  function exportarCSV() {
    const columnas = ['ID', 'Nombre completo', 'Documento', 'Teléfono', 'Email', 'VIP', 'Fecha registro'];
    const filas = huespedes.map(h => [
      h.id,
      h.nombre_completo,
      h.documento_formateado,
      h.telefono,
      h.email,
      h.es_vip ? 'Sí' : 'No',
      new Date(h.created_at).toLocaleDateString('es-VE')
    ]);
    const csvContent = [columnas, ...filas].map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.href = url;
    link.setAttribute('download', `huespedes_${new Date().toISOString().slice(0,19)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }
</script>

<svelte:head>
  <title>Gestión de Huéspedes | SalmaSuitesPMS</title>
</svelte:head>

<div class="max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">

  <PageHeader title="Huéspedes" subtitle={`${huespedes.length} Registros`}>
    {#if isAdmin}
      <div class="flex items-center gap-3">
        <Button variant="secondary" onclick={exportarCSV}>
          <Icon name="export" class="w-4 h-4" />
          Exportar registro
        </Button>
        <Button variant="gold" onclick={() => modalCrear = true}>
          <Icon name="plus" class="w-4 h-4" />
          Registrar huésped
        </Button>
      </div>
    {/if}
  </PageHeader>

  <section class="grid grid-cols-1 lg:grid-cols-4 gap-4 items-center bg-hotel-surface/40 p-2 rounded-2xl border border-hotel-border shadow-hotel-sm backdrop-blur-md">
    
    <div class="lg:col-span-2">
      <InputHotel
        type="search"
        placeholder="Buscar por nombre, documento o contacto..."
        bind:value={busqueda}
        oninput={onSearch}
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
        <Icon name="star" class="w-3.5 h-3.5 {soloVip ? 'fill-hotel-vip' : 'fill-transparent stroke-current'}" />
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

  <main class="min-h-[400px]">
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