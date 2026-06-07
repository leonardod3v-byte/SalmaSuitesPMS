<script lang="ts">
  import type { PageData } from './$types';
  import RoomCard from '$lib/components/habitaciones/RoomCard.svelte';
  import RoomModal from '$lib/components/habitaciones/RoomModal.svelte';
  import { auth } from '$lib/stores/auth';
  import { invalidateAll } from '$app/navigation';
  import Button from '$lib/components/Button.svelte';
  import Icon from '$lib/components/Icons.svelte';
  import InputHotel from '$lib/components/InputHotel.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';

  type EstadoHabitacion = 'libre' | 'limpia' | 'sucia' | 'ocupada' | 'mantenimiento' | 'construccion';

  interface Habitacion {
    id: number; numero: string; piso: number; tipo: number;
    tipo_nombre?: string; estado: EstadoHabitacion;
  }

  interface TipoHabitacion {
    id: number; nombre: string;
  }

  let { data }: { data: PageData } = $props();

  let habitaciones = $derived((data.habitaciones ?? []) as Habitacion[]);
  let tipos        = $derived((data.tipos ?? []) as TipoHabitacion[]);

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

  let habitacionSeleccionada = $state<Habitacion | null>(null);
  let mostrarModalCrear      = $state(false);

  const cerrarModales = () => { habitacionSeleccionada = null; mostrarModalCrear = false; };
  const resetFiltros  = () => { filtroEstado = 'todos'; filtroTipo = 'todos'; busqueda = ''; };
  const recargarDatos = () => invalidateAll();
</script>

<svelte:head>
  <title>Inventario de Habitaciones | SalmaSuitesPMS</title>
</svelte:head>

<div class="max-w-[1600px] mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">

  <PageHeader title="Habitaciones" subtitle={`${habitaciones.length} Unidades Totales`}>
    {#if isAdmin}
      <Button variant="gold" onclick={() => mostrarModalCrear = true}>
        <Icon name="plus" class="w-4 h-4" />
        Nueva Unidad
      </Button>
    {/if}
  </PageHeader>

  <section class="space-y-4">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 bg-hotel-surface/40 p-2 rounded-2xl border border-hotel-border shadow-hotel-sm backdrop-blur-md">
      
      <InputHotel
        type="text"
        placeholder="Buscar unidad..."
        bind:value={busqueda}
      />

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