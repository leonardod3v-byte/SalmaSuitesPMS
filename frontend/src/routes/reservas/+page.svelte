<script lang="ts">
  import type { PageData } from './$types';
  import { goto, invalidateAll } from '$app/navigation';
  import { auth } from '$lib/stores/auth';
  import { type ReservaListItem } from '$lib/services/reservaciones';
  import BookingCalendar from '$lib/components/reservaciones/BookingCalendar.svelte';
  import CheckInForm     from '$lib/components/reservaciones/CheckInForm.svelte';
  import NoShowModal     from '$lib/components/reservaciones/NoShowModal.svelte';
  import ConsumoSelector from '$lib/components/reservaciones/ConsumoSelector.svelte';
  import PagoRegistro from '$lib/components/reservaciones/PagoRegistro.svelte';
  import ModalShell from '$lib/components/ModalShell.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import { reservacionesApi } from '$lib/services/reservaciones';

  let { data }: { data: PageData } = $props();

  let reservas     = $derived((data.reservas     ?? []) as ReservaListItem[]);
  let habitaciones = $derived((data.habitaciones ?? []) as { numero: string; tipo_nombre: string; piso: number }[]);
  let semanaInicio = $derived(new Date(data.semanaInicio + 'T00:00:00'));


  function navegarSemana(delta: number) {
    const nueva = new Date(semanaInicio);
    nueva.setDate(nueva.getDate() + delta * 7);
    goto(`?semana=${nueva.toISOString().split('T')[0]}`, { invalidateAll: true, noScroll: true });
  }

  const rangoFechaTexto = $derived(() => {
    const fin = new Date(semanaInicio);
    fin.setDate(fin.getDate() + 6);
    const opciones: Intl.DateTimeFormatOptions = { day: '2-digit', month: 'short' };
    return `${semanaInicio.toLocaleDateString('es-VE', opciones)} — ${fin.toLocaleDateString('es-VE', { ...opciones, year: 'numeric' })}`;
  });


  let modalCheckin  = $state(false);
  let modalNoShow   = $state<ReservaListItem | null>(null);
  let modalConsumo  = $state<number | null>(null);
  let reservaSeleccionada = $state<ReservaListItem | null>(null);
  let modoGestion = $state<'menu' | 'pago' | 'consumo' | 'noshow' | null>(null);

  function onCeldaClick(hab: string, fecha: string) {
    const reserva = reservas.find(r => 
      r.habitacion_numero === hab && r.fecha_entrada <= fecha && r.fecha_salida > fecha
    );

    if (reserva) {
      reservaSeleccionada = reserva;
      modoGestion = 'menu';
    } else {
      modalCheckin = true;
    }
  }

    function cerrarGestion() {
    reservaSeleccionada = null;
    modoGestion = null;
    invalidateAll();
  }


  const statsHoy = $derived(() => {
    const hoy = new Date().toISOString().split('T')[0];
    return {
      checkins:  reservas.filter(r => r.fecha_entrada === hoy).length,
      checkouts: reservas.filter(r => r.fecha_salida === hoy).length,
      ocupadas:  reservas.filter(r => r.estado === 'confirmada' || r.estado === 'pagada').length,
    };
  });
</script>

<svelte:head>
  <title>Gestión de Reservaciones | SalmaSuitesPMS</title>
</svelte:head>

<div class="max-w-1600px mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">

  <PageHeader title="Reservaciones" subtitle="Gestión de Estancias y Check-ins">
    {#snippet actions()}
      <button onclick={() => modalCheckin = true} class="btn-gold">
        <svg class="w-4 h-4 transition-transform group-hover:rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 5v14M5 12h14"/>
        </svg>
        Nuevo Check-In
      </button>
    {/snippet}
  </PageHeader>

  <section class="grid grid-cols-1 lg:grid-cols-4 gap-4 items-center bg-hotel-surface/40 p-2 rounded-2xl border border-hotel-border shadow-hotel-sm backdrop-blur-md">
    {#each [
      { label: 'Check-ins Hoy',  value: statsHoy().checkins,  icon: 'M11 16l-4-4m0 0l4-4m-4 4h14', color: 'text-hotel-success-light' },
      { label: 'Check-outs Hoy', value: statsHoy().checkouts, icon: 'M13 8l4 4m0 0l-4 4m4-4H3',   color: 'text-hotel-error-light'   },
      { label: 'Huéspedes en Casa', value: statsHoy().ocupadas,  icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6', color: 'text-hotel-gold' }
    ] as kpi}
      <div class="bg-hotel-surface/40 border border-hotel-border p-6 rounded-2xl flex items-center gap-5 backdrop-blur-sm shadow-hotel-sm">
        <div class="w-12 h-12 rounded-xl bg-hotel-bg border border-hotel-border flex items-center justify-center {kpi.color}">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d={kpi.icon}/></svg>
        </div>
        <div>
          <p class="text-3xl font-display font-black italic {kpi.color} leading-none">{kpi.value}</p>
          <p class="text-[9px] font-black uppercase tracking-[0.2em] text-hotel-text-tertiary mt-2">{kpi.label}</p>
        </div>
      </div>
    {/each}
  </section>

  <section class="bg-hotel-surface border border-hotel-border rounded-3xl overflow-hidden shadow-hotel-lg">
    <div class="p-6 border-b border-hotel-border bg-hotel-bg/40 flex flex-col sm:flex-row justify-between items-center gap-4">
      <div class="space-y-1">
        <span class="text-[9px] font-black uppercase tracking-[0.3em] text-hotel-gold/80">Control Semanal</span>
        <p class="font-display text-2xl italic text-hotel-text-primary tracking-tight">
          {rangoFechaTexto()}
        </p>
      </div>

      <nav class="flex items-center gap-2 p-1 bg-hotel-bg rounded-xl border border-hotel-border">
        <button onclick={() => navegarSemana(-1)} class="p-2 hover:bg-hotel-surface rounded-lg transition-colors text-hotel-text-tertiary hover:text-hotel-gold">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/></svg>
        </button>
        <button onclick={() => goto('/reservaciones')} class="px-6 py-2 text-[10px] font-black uppercase tracking-widest text-hotel-text-secondary hover:text-hotel-gold transition-colors">
          Hoy
        </button>
        <button onclick={() => navegarSemana(1)} class="p-2 hover:bg-hotel-surface rounded-lg transition-colors text-hotel-text-tertiary hover:text-hotel-gold">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/></svg>
        </button>
      </nav>
    </div>

    <div class="p-2 bg-hotel-surface">
      <BookingCalendar {reservas} {habitaciones} {semanaInicio} {onCeldaClick} />
    </div>
  </section>
</div>

{#if reservaSeleccionada && modoGestion && modoGestion !== 'noshow'}
  <ModalShell
    title="{reservaSeleccionada.huesped_nombre.split(' ')[0]} — Hab. {reservaSeleccionada.habitacion_numero}"
    subtitle={modoGestion === 'menu' ? 'Gestión de Estancia' : 'Procesando ' + modoGestion}
    maxWidth="max-w-lg"
    onclose={cerrarGestion}
  >
    {#if modoGestion === 'menu'}
      <div class="grid grid-cols-1 gap-3">
        <div class="flex justify-between items-center p-4 bg-hotel-bg rounded-2xl border border-hotel-border mb-2">
          <span class="text-xs font-bold text-hotel-text-tertiary uppercase">Saldo Pendiente:</span>
          <span class="text-xl font-display font-black text-hotel-gold">${reservaSeleccionada.saldo_pendiente}</span>
        </div>
        <button onclick={() => modoGestion = 'pago'} class="btn-action">
          <span class="text-lg">💳</span> Registrar Pago / Abono
        </button>
        <button onclick={() => modoGestion = 'consumo'} class="btn-action">
          <span class="text-lg">🛒</span> Añadir Consumo (Minibar/Rest)
        </button>
        <button onclick={() => modoGestion = 'noshow'} class="btn-action text-hotel-error-light opacity-50 hover:opacity-100">
          <span class="text-lg">🚫</span> Marcar como No-Show
        </button>
      </div>
    {:else if modoGestion === 'pago'}
      <PagoRegistro
        reservaId={reservaSeleccionada.id}
        totalPendiente={parseFloat(reservaSeleccionada.saldo_pendiente)}
        onpago={cerrarGestion}
      />
    {:else if modoGestion === 'consumo'}
      <ConsumoSelector reservaId={reservaSeleccionada.id} onaguardado={cerrarGestion} />
    {/if}
  </ModalShell>
{/if}

{#if reservaSeleccionada && modoGestion === 'noshow'}
  <NoShowModal
    reserva={reservaSeleccionada}
    onclose={() => modoGestion = 'menu'} 
    onregistrado={() => { 
      modoGestion = null; 
      reservaSeleccionada = null; 
      invalidateAll(); 
    }}
  />
{/if}