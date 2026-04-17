<script lang="ts">
  import type { PageData } from './$types';
  import WelcomeBanner from '$lib/components/WelcomeBanner.svelte';
  import KPICard from '$lib/components/KPICard.svelte';
  import Loading from '$lib/components/Loading.svelte';

  interface Stats {
    ocupacion: { porcentaje: number; ocupadas: number; total: number; trend: { valor: string; subio: boolean } };
    reservas_hoy: { total: number; check_ins_pendientes: number; check_outs_pendientes: number };
    ingresos_dia: { monto: number; trend: { valor: string; subio: boolean } };
    vip_hoy: { total: number };
  }
  interface Habitacion { num: string; estado: 'libre' | 'ocupada' | 'mantenimiento'; tipo: string; piso: number; }
  interface Actividad { descripcion: string; created_at: string; }

  let { data }: { data: PageData } = $props();

  // Datos pre-cargados desde el servidor — sin onMount, sin "Loading..."
  let stats = $derived(data.stats as Stats | null);
  let habitaciones = $derived((data.habitaciones ?? []) as Habitacion[]);
  let actividades = $derived((data.actividades ?? []) as Actividad[]);
  let ocupacionSemanal = $derived((data.ocupacionSemanal as any)?.valores ?? [] as number[]);
  let diasSemana = $derived((data.ocupacionSemanal as any)?.dias ?? [] as string[]);

  let filtroActivo = $state<string>('todas');

  let habitacionesFiltradas = $derived(
    filtroActivo === 'todas'
      ? habitaciones
      : habitaciones.filter(h => h.estado === filtroActivo)
  );

  let totalPorEstado = $derived({
    libre:         habitaciones.filter(h => h.estado === 'libre').length,
    ocupada:       habitaciones.filter(h => h.estado === 'ocupada').length,
    mantenimiento: habitaciones.filter(h => h.estado === 'mantenimiento').length,
  });

  const getEstadoClass = (estado: Habitacion['estado']) => {
    const map: Record<string, string> = {
      libre:         'bg-hotel-success/10 border-hotel-success/30 text-hotel-success-light',
      ocupada:       'bg-hotel-gold/10 border-hotel-gold/30 text-hotel-gold-light',
      mantenimiento: 'bg-hotel-error/10 border-hotel-error/30 text-hotel-error-light',
    };
    return map[estado] || 'bg-hotel-surface border-hotel-border text-hotel-text-tertiary';
  };
</script>

<svelte:head>
  <title>Panel de Control | SalmaSuitesPMS</title>
</svelte:head>

{#if !stats}
  <div class="flex items-center justify-center h-[60vh]">
    <div class="text-center p-8 bg-hotel-error/5 border border-hotel-error/20 rounded-2xl">
      <p class="text-hotel-error-light font-bold uppercase tracking-widest text-xs mb-4">
        Error al cargar el panel
      </p>
      <a href="/dashboard" class="btn-gold-outline py-2 px-6 text-xs">Reintentar</a>
    </div>
  </div>
{:else}
  <div class="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-700">
    <WelcomeBanner />

    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <KPICard
        title="Ocupación Real"
        value="{stats?.ocupacion?.porcentaje ?? 0}%"
        subtitle="{stats?.ocupacion?.ocupadas ?? 0} de {stats?.ocupacion?.total ?? 0} unidades"
        trend={stats?.ocupacion?.trend?.valor}
        trendUp={stats?.ocupacion?.trend?.subio}
        icon="hotel"
        color="gold"
      />
      <KPICard
        title="Check-In Hoy"
        value={stats?.reservas_hoy?.total ?? 0}
        subtitle="{stats?.reservas_hoy?.check_ins_pendientes ?? 0} ingresos pendientes"
        icon="calendar"
        color="success"
      />
      <KPICard
        title="Ingresos"
        value="${stats?.ingresos_dia?.monto?.toLocaleString(undefined, { minimumFractionDigits: 2 }) ?? '0.00'}"
        subtitle="Flujo de caja del día"
        trend={stats?.ingresos_dia?.trend?.valor}
        trendUp={stats?.ingresos_dia?.trend?.subio}
        icon="money"
        color="gold"
      />
      <KPICard
        title="Clientes VIP"
        value={stats?.vip_hoy?.total ?? 0}
        subtitle="Servicios preferenciales"
        icon="crown"
        color="vip"
      />
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <section class="lg:col-span-2 bg-hotel-surface rounded-2xl p-6 border border-hotel-border shadow-hotel-sm overflow-hidden">
        <h3 class="font-display text-xl text-hotel-text-primary mb-8 italic">Ocupación Semanal</h3>
        <div class="flex items-end justify-between gap-3 h-64 px-2">
          {#each ocupacionSemanal as val, i}
            <div class="flex-1 flex flex-col items-center gap-3 group relative">
              <div class="absolute -top-10 left-1/2 -translate-x-1/2 bg-hotel-bg border border-hotel-gold/50 px-2 py-1 rounded text-[10px] text-hotel-gold font-bold opacity-0 group-hover:opacity-100 transition-all duration-300 pointer-events-none z-10 shadow-hotel-gold">
                {val}%
              </div>
              <div class="w-full relative h-full flex flex-col justify-end bg-hotel-bg/30 rounded-t-md overflow-hidden">
                <div
                  class="w-full bg-linear-to-t from-hotel-gold-dark via-hotel-gold to-hotel-gold-light transition-all duration-1000 ease-out"
                  style="height: {val}%"
                ></div>
              </div>
              <span class="text-[9px] text-hotel-text-tertiary font-black uppercase tracking-tighter transition-colors group-hover:text-hotel-gold">
                {diasSemana[i] || '--'}
              </span>
            </div>
          {/each}
        </div>
      </section>

      <section class="bg-hotel-surface rounded-2xl p-6 border border-hotel-border flex flex-col shadow-hotel-sm">
        <h3 class="font-display text-xl text-hotel-text-primary mb-6 italic">Actividad</h3>
        <div class="flex-1 space-y-0 overflow-y-auto pr-2 custom-scrollbar max-h-320px">
          {#each actividades as act, i}
            <div class="flex gap-4 group relative pb-6 last:pb-0">
              {#if i !== actividades.length - 1}
                <div class="absolute left-11px top-7 w-px h-full bg-hotel-border/50 group-hover:bg-hotel-gold/20 transition-colors"></div>
              {/if}
              <div class="relative z-10">
                <div class="w-22px h-22px rounded-full bg-hotel-bg border border-hotel-gold/30 flex items-center justify-center group-hover:border-hotel-gold transition-all duration-300 shadow-sm">
                  <div class="w-1.5 h-1.5 rounded-full bg-hotel-gold/50 group-hover:bg-hotel-gold animate-pulse"></div>
                </div>
              </div>
              <div class="flex-1 bg-hotel-bg/20 p-3 rounded-xl border border-transparent group-hover:border-hotel-border/30 group-hover:bg-hotel-surface-hover transition-all duration-300">
                <p class="text-xs text-hotel-text-secondary leading-relaxed">{act.descripcion}</p>
                <div class="mt-2 text-[9px] text-hotel-text-tertiary font-mono opacity-60">
                  {new Date(act.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          {:else}
            <p class="text-[10px] text-hotel-text-tertiary text-center italic py-10 uppercase tracking-widest">Sin registros recientes</p>
          {/each}
        </div>
      </section>
    </div>

    <section class="bg-hotel-surface rounded-2xl p-6 border border-hotel-border shadow-hotel-sm">
      <div class="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
        <h3 class="font-display text-xl text-hotel-text-primary italic">Mapa de Habitaciones</h3>
        <div class="flex p-1 bg-hotel-bg rounded-xl border border-hotel-border">
          {#each ['todas', 'libre', 'ocupada', 'mantenimiento'] as f}
            <button
              onclick={() => filtroActivo = f}
              class="px-4 py-1.5 text-[10px] uppercase font-bold rounded-lg transition-all {filtroActivo === f ? 'bg-hotel-gold text-hotel-bg shadow-hotel-sm' : 'text-hotel-text-tertiary hover:text-hotel-text-secondary'}"
            >
              {f}
            </button>
          {/each}
        </div>
      </div>

      <div class="grid grid-cols-6 sm:grid-cols-10 lg:grid-cols-12 xl:grid-cols-15 gap-3">
        {#each habitacionesFiltradas as hab}
          <div class="aspect-square rounded-lg border flex items-center justify-center text-[10px] font-black transition-all hover:scale-110 shadow-sm {getEstadoClass(hab.estado)}">
            {hab.num}
          </div>
        {/each}
      </div>


      <div class="mt-3 pt-6 border-t border-hotel-border/50 flex flex-wrap gap-2">
        <div class="flex flex-wrap gap-3">
          {#each [
            { label: 'Libre', class: 'bg-hotel-success/10 border-hotel-success/30 text-hotel-success-light', dot: 'bg-hotel-success' },
            { label: 'Ocupada', class: 'bg-hotel-gold/10 border-hotel-gold/30 text-hotel-gold-light', dot: 'bg-hotel-gold' },
            { label: 'Mantenimiento/Limpieza', class: 'bg-hotel-error/10 border-hotel-error/30 text-hotel-error-light', dot: 'bg-hotel-error' },
          ] as item}
            <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl border text-[10px] font-bold transition-opacity hover:opacity-80 {item.class}">
              <div class="w-2 h-2 rounded-full {item.dot} animate-pulse-slow"></div>
                {item.label}
            </div>
          {/each}
        </div>
      </div>
    </section>
  </div>
{/if}

<style>
  .custom-scrollbar::-webkit-scrollbar { width: 3px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: var(--color-hotel-border); border-radius: 10px; }
  .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: var(--color-hotel-gold); }
</style>