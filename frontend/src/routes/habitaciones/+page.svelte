<script lang="ts">
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { habitacionesApi } from '$lib/services/habitaciones';
  
  // Componentes
  import Loading from '$lib/components/Loading.svelte';
  import RoomCard from '$lib/components/habitaciones/RoomCard.svelte';
  import RoomModal from '$lib/components/habitaciones/RoomModal.svelte';

  // ── Tipos ─────────────────────────────────────────────────────────────────
  type EstadoHabitacion = 'libre' | 'limpia' | 'sucia' | 'ocupada' | 'mantenimiento' | 'construccion';

  interface Habitacion {
    id: number; numero: string; piso: number; tipo: number;
    tipo_nombre?: string; estado: EstadoHabitacion;
  }

  interface TipoHabitacion {
    id: number; nombre: string;
  }

  // ── Estado (Runes) ────────────────────────────────────────────────────────
  let habitaciones = $state<Habitacion[]>([]);
  let tipos = $state<TipoHabitacion[]>([]);
  let cargando = $state(true);
  let errorCarga = $state('');

  // Filtros
  let filtroEstado = $state('todos');
  let filtroTipo = $state('todos');
  let busqueda = $state('');

  const ESTADOS_MAP = [
    { value: 'todos', label: 'Todas' },
    { value: 'libre', label: 'Libre' },
    { value: 'limpia', label: 'Limpia' },
    { value: 'sucia', label: 'Sucia' },
    { value: 'ocupada', label: 'Ocupada' },
    { value: 'mantenimiento', label: 'Mantenim.' }
  ];

  // ── Derivados (Computed) ──────────────────────────────────────────────────
  const habitacionesFiltradas = $derived(
    habitaciones.filter(h => {
      const matchEstado = filtroEstado === 'todos' || h.estado === filtroEstado;
      const matchTipo = filtroTipo === 'todos' || String(h.tipo) === filtroTipo;
      const matchBusq = !busqueda || h.numero.toLowerCase().includes(busqueda.toLowerCase());
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

  // ── Modales & Acciones ────────────────────────────────────────────────────
  let habitacionSeleccionada = $state<Habitacion | null>(null);
  let mostrarModalCrear = $state(false);

  const abrirDetalle = (h: Habitacion) => habitacionSeleccionada = h;
  const cerrarModales = () => { habitacionSeleccionada = null; mostrarModalCrear = false; };
  
  const resetFiltros = () => { filtroEstado = 'todos'; filtroTipo = 'todos'; busqueda = ''; };

  // ── Datos ─────────────────────────────────────────────────────────────────
  async function cargarDatos() {
    try {
      const [h, t] = await Promise.all([habitacionesApi.getAll(), habitacionesApi.getTipos()]);
      habitaciones = h; tipos = t;
    } catch {
      errorCarga = 'Error de conexión con el servidor.';
    } finally {
      cargando = false;
    }
  }

  onMount(cargarDatos);
</script>

<svelte:head>
  <title>Habitaciones | SalmaSuites</title>
</svelte:head>

{#if cargando}
  <Loading />
{:else if errorCarga}
  <div class="flex flex-col items-center justify-center h-[60vh] gap-4">
    <p class="text-hotel-error-light font-bold text-xs tracking-tighter uppercase">{errorCarga}</p>
    <button onclick={cargarDatos} class="btn-gold px-8">Reintentar</button>
  </div>
{:else}
  <div class="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-700">
    
    <!-- Header -->
    <header class="flex justify-between items-end">
      <div>
        <h1 class="text-3xl font-display font-bold italic text-hotel-text-primary">Habitaciones</h1>
        <p class="text-xs text-hotel-text-tertiary mt-1">
          {habitaciones.length} Unidades · 
          <span class="text-hotel-gold">{habitacionesFiltradas.length} resultados</span>
        </p>
      </div>
      {#if isAdmin}
        <button class="btn-gold" onclick={() => mostrarModalCrear = true}>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14" stroke-width="2.5" stroke-linecap="round"/></svg>
          Nueva habitación
        </button>
      {/if}
    </header>

    <!-- Filtros -->
    <section class="bg-hotel-surface border border-hotel-border rounded-2xl p-4 shadow-sm">
      <div class="flex flex-wrap gap-3 items-center">
        <div class="relative flex-1 max-w-sm">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 text-hotel-text-tertiary w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35" stroke-width="2.5"/></svg>
          <input bind:value={busqueda} type="text" placeholder="Buscar unidad..." class="input-hotel pl-10 w-full" />
        </div>

        <select bind:value={filtroTipo} class="input-hotel min-w-180px">
          <option value="todos">Todos los tipos</option>
          {#each tipos as t} <option value={String(t.id)}>{t.nombre}</option> {/each}
        </select>

        {#if tieneFiltrosActivos}
          <button onclick={resetFiltros} class="text-xs font-bold text-hotel-error-light hover:underline px-2">
            Limpiar filtros
          </button>
        {/if}
      </div>

      <div class="flex flex-wrap gap-2 mt-4 pt-4 border-t border-hotel-border/50">
        {#each ESTADOS_MAP as est}
          {@const count = est.value === 'todos' ? habitaciones.length : (conteos[est.value] ?? 0)}
          <button 
            class="estado-filter-chip {filtroEstado === est.value ? 'active' : ''}"
            onclick={() => filtroEstado = est.value}
          >
            {est.label} <span class="chip-count">{count}</span>
          </button>
        {/each}
      </div>
    </section>

    <!-- Grid -->
    {#if habitacionesFiltradas.length === 0}
      <div class="py-20 text-center opacity-40">
        <p class="text-sm font-semibold">No se encontraron unidades</p>
      </div>
    {:else}
      <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        {#each habitacionesFiltradas as hab (hab.id)}
          <RoomCard {hab} onclick={() => abrirDetalle(hab)} />
        {/each}
      </div>
    {/if}
  </div>
{/if}

<!-- Modales -->
{#if habitacionSeleccionada}
  <RoomModal data={habitacionSeleccionada} modo="ver" {tipos} onclose={cerrarModales} onupdated={cargarDatos} />
{/if}

{#if mostrarModalCrear}
  <RoomModal data={null} modo="crear" {tipos} onclose={cerrarModales} onupdated={cargarDatos} />
{/if}

<style>
  @reference "../../app.css"; 

  .estado-filter-chip {
    @apply inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-hotel-bg border border-hotel-border text-hotel-text-tertiary transition-all hover:border-hotel-gold-dark;
  }

  .estado-filter-chip.active {
    @apply bg-hotel-gold border-hotel-gold text-hotel-bg;
  }

  .chip-count {
    @apply bg-black/20 px-1.5 py-0.5 rounded-full text-[9px];
  }
</style>