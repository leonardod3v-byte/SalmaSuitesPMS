<script lang="ts">
  import type { PageData } from './$types';
  import RoomCard from '$lib/components/habitaciones/RoomCard.svelte';
  import RoomModal from '$lib/components/habitaciones/RoomModal.svelte';
  import { auth } from '$lib/stores/auth';
  import { invalidateAll } from '$app/navigation';

  type EstadoHabitacion = 'libre' | 'limpia' | 'sucia' | 'ocupada' | 'mantenimiento' | 'construccion';

  interface Habitacion {
    id: number; numero: string; piso: number; tipo: number;
    tipo_nombre?: string; estado: EstadoHabitacion;
  }

  interface TipoHabitacion {
    id: number; nombre: string;
  }

  let { data }: { data: PageData } = $props();

  // Datos reactivos de Svelte 5
  let habitaciones = $derived((data.habitaciones ?? []) as Habitacion[]);
  let tipos        = $derived((data.tipos ?? []) as TipoHabitacion[]);

  // Filtros locales
  let filtroEstado = $state('todos');
  let filtroTipo   = $state('todos');
  let busqueda     = $state('');

  const ESTADOS_MAP = [
    { value: 'todos',         label: 'Todas'      },
    { value: 'libre',         label: 'Libres'      },
    { value: 'limpia',        label: 'Limpias'     },
    { value: 'sucia',         label: 'Sucias'      },
    { value: 'ocupada',       label: 'Ocupadas'    },
    { value: 'mantenimiento', label: 'Mantenim.'   },
  ];

  const habitacionesFiltradas = $derived(
    habitaciones.filter(h => {
      const matchEstado = filtroEstado === 'todos' || h.estado === filtroEstado;
      const matchTipo   = filtroTipo === 'todos'   || String(h.tipo) === filtroTipo;
      const matchBusq   = !busqueda || h.numero.toLowerCase().includes(busqueda.toLowerCase());
      return matchEstado && matchTipo && matchBusq;
    })
  );

  const conteos = $derived(
    habitaciones.reduce((acc, h) => {
      acc[h.estado] = (acc[h.estado] || 0) + 1;
      return acc;
    }, {} as Record<string, number>)
  );

  const isAdmin = $derived($auth?.user?.role === 'admin');
  const tieneFiltrosActivos = $derived(filtroEstado !== 'todos' || filtroTipo !== 'todos' || busqueda !== '');

  // Modales
  let habitacionSeleccionada = $state<Habitacion | null>(null);
  let mostrarModalCrear      = $state(false);

  const cerrarModales = () => { habitacionSeleccionada = null; mostrarModalCrear = false; };
  const resetFiltros  = () => { filtroEstado = 'todos'; filtroTipo = 'todos'; busqueda = ''; };
  const recargarDatos = () => invalidateAll();
</script>

<svelte:head>
  <title>Inventario de Habitaciones | SalmaSuitesPMS</title>
</svelte:head>

<div class="max-w-1600px mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">

  <header class="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-hotel-border/50 pb-8">
    <div class="space-y-1">
      <h1 class="text-4xl font-display font-black italic text-hotel-text-primary tracking-tight">
        Habitaciones
      </h1>
      <p class="text-xs font-medium text-hotel-text-tertiary flex items-center gap-2 uppercase tracking-0.1em">
        <span class="w-2 h-2 rounded-full bg-hotel-gold animate-pulse"></span>
        {habitaciones.length} Unidades Totales
        {#if tieneFiltrosActivos}
          <span class="text-hotel-gold-light border-l border-hotel-border pl-2">
            {habitacionesFiltradas.length} Filtradas
          </span>
        {/if}
      </p>
    </div>

    {#if isAdmin}
      <button 
        class="btn-gold group px-6 py-3 shadow-hotel-gold/10 hover:shadow-hotel-gold/20" 
        onclick={() => mostrarModalCrear = true}
      >
        <svg class="w-4 h-4 transition-transform group-hover:rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 5v14M5 12h14"/>
        </svg>
        <span class="font-black uppercase text-[11px] tracking-widest">Nueva Unidad</span>
      </button>
    {/if}
  </header>

  <section class="space-y-4">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 bg-hotel-surface/40 p-2 rounded-2xl border border-hotel-border shadow-hotel-sm backdrop-blur-md">
      
      <div class="relative group">
        <div class="absolute left-4 top-1/2 -translate-y-1/2 text-hotel-text-tertiary group-focus-within:text-hotel-gold transition-colors">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
        </div>
        <input 
          bind:value={busqueda} 
          type="text" 
          placeholder="Buscar unidad..."
          class="input-hotel pl-12 bg-hotel-bg border-transparent focus:border-hotel-gold/30 w-full h-12" 
        />
      </div>

      <select bind:value={filtroTipo} class="input-hotel h-12 bg-hotel-bg border-transparent focus:border-hotel-gold/30 font-bold text-[11px] uppercase tracking-wider px-4">
        <option value="todos">Todos los tipos</option>
        {#each tipos as t}
          <option value={String(t.id)}>{t.nombre}</option>
        {/each}
      </select>

      <div class="flex items-center justify-end px-2">
        {#if tieneFiltrosActivos}
          <button 
            onclick={resetFiltros}
            class="h-10 px-6 text-[9px] font-black uppercase tracking-widest text-hotel-error-light hover:bg-hotel-error/5 rounded-xl transition-all"
          >
            Limpiar filtros
          </button>
        {/if}
      </div>
    </div>

    <div class="flex flex-wrap items-center gap-2 px-1">
      <span class="text-[9px] font-black uppercase tracking-[0.2em] text-hotel-text-tertiary mr-2">Estado:</span>
      {#each ESTADOS_MAP as est}
        {@const count = est.value === 'todos' ? habitaciones.length : (conteos[est.value] ?? 0)}
        <button
          onclick={() => filtroEstado = est.value}
          class="flex items-center gap-3 px-4 py-2 rounded-full border text-[10px] font-black uppercase tracking-wider transition-all duration-300
                 {filtroEstado === est.value 
                   ? 'bg-hotel-gold border-hotel-gold text-hotel-bg shadow-md scale-105' 
                   : 'bg-hotel-surface border-hotel-border text-hotel-text-secondary hover:border-hotel-gold/50 hover:text-hotel-gold-light'}"
        >
          {est.label}
          <span class="text-[9px] opacity-60 {filtroEstado === est.value ? 'text-hotel-bg' : 'text-hotel-gold'}">
            {count}
          </span>
        </button>
      {/each}
    </div>
  </section>

  {#if habitacionesFiltradas.length === 0}
    <div class="py-32 text-center bg-hotel-surface/20 rounded-3xl border border-dashed border-hotel-border">
      <p class="text-sm font-display italic text-hotel-text-tertiary">No hay unidades que coincidan con los criterios</p>
    </div>
  {:else}
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-5">
      {#each habitacionesFiltradas as hab (hab.id)}
        <RoomCard {hab} onclick={() => habitacionSeleccionada = hab} />
      {/each}
    </div>
  {/if}
</div>

{#if habitacionSeleccionada}
  <RoomModal data={habitacionSeleccionada} modo="ver" {tipos} onclose={cerrarModales} onupdated={recargarDatos} />
{/if}

{#if mostrarModalCrear}
  <RoomModal data={null} modo="crear" {tipos} onclose={cerrarModales} onupdated={recargarDatos} />
{/if}