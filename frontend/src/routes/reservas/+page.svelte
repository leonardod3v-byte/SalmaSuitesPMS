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
      modoGestion = 'menu'; // Abrimos el menú de opciones primero
    } else {
      modalCheckin = true;
    }
  }

    function cerrarGestion() {
    reservaSeleccionada = null;
    modoGestion = null;
    invalidateAll(); // Refresca los datos (saldos, estados, etc.)
  }

  // Estadísticas en tiempo real del Dashboard
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

  <header class="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-hotel-border/50 pb-8">
    <div class="space-y-1">
      <h1 class="text-4xl font-display font-black italic text-hotel-text-primary tracking-tight">
        Reservaciones
      </h1>
      <p class="text-xs font-medium text-hotel-text-tertiary flex items-center gap-2 uppercase tracking-0.1em">
        <span class="w-2 h-2 rounded-full bg-hotel-gold animate-pulse"></span>
        Rack de Control
      </p>
    </div>

    <div class="flex items-center gap-3">
      <button class="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-hotel-border
               text-xs font-bold text-hotel-text-secondary hover:border-hotel-gold/40
               hover:text-hotel-gold transition-all" onclick={() => {}}>
        <svg class="w-4 h-4 text-hotel-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        <span class="font-black uppercase text-[10px] tracking-widest text-hotel-text-secondary">Exportar registro</span>
      </button>

      <button class="btn-gold group px-6 py-3" onclick={() => modalCheckin = true}>
        <svg class="w-4 h-4 transition-transform group-hover:rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 5v14M5 12h14"/>
        </svg>
        <span class="font-black uppercase text-[10px] tracking-widest text-hotel-bg">Nueva Reserva</span>
      </button>
    </div>
  </header>

  <section class="grid grid-cols-1 md:grid-cols-3 gap-6">
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

{#if modalCheckin}
  <div class="fixed inset-0 z-100 flex items-center justify-center p-4 bg-hotel-bg/90 backdrop-blur-md animate-in fade-in duration-300">
    <div class="w-full max-w-2xl max-h-[90vh] bg-hotel-surface border border-hotel-border rounded-3xl shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-300">
      <div class="p-8 border-b border-hotel-border flex justify-between items-center bg-hotel-bg/20">
        <div>
          <h2 class="font-display text-3xl italic text-hotel-text-primary tracking-tight">Check-In</h2>
          <span class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Registro de Nueva Reserva</span>
        </div>
        <button onclick={() => modalCheckin = false} class="w-10 h-10 rounded-full border border-hotel-border flex items-center justify-center hover:bg-hotel-error/10 hover:text-hotel-error-light transition-all">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="p-8 overflow-y-auto custom-scrollbar">
        <CheckInForm onguardado={() => { modalCheckin = false; invalidateAll(); }} oncancel={() => modalCheckin = false} />
      </div>
    </div>
  </div>
{/if}

{#if reservaSeleccionada && modoGestion}
  <div class="fixed inset-0 z-100 flex items-center justify-center p-4 bg-hotel-bg/95 backdrop-blur-md animate-in fade-in duration-300">
    <div class="w-full max-w-lg bg-hotel-surface border border-hotel-border rounded-[2.5rem] shadow-2xl overflow-hidden animate-in zoom-in-95">
      
      <div class="p-6 border-b border-hotel-border flex justify-between items-center bg-hotel-bg/30">
        <div>
          <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">
            {modoGestion === 'menu' ? 'Gestión de Estancia' : 'Procesando ' + modoGestion}
          </p>
          <h2 class="font-display text-2xl italic text-hotel-text-primary uppercase tracking-tighter">
            {reservaSeleccionada.huesped_nombre.split(' ')[0]} - Hab. {reservaSeleccionada.habitacion_numero}
          </h2>
        </div>
        <button onclick={cerrarGestion} class="w-10 h-10 rounded-full border border-hotel-border flex items-center justify-center hover:bg-hotel-error/10 text-hotel-text-tertiary">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <div class="p-6">
        {#if modoGestion === 'menu'}
          <div class="grid grid-cols-1 gap-3">
            <div class="flex justify-between items-center p-4 bg-hotel-bg rounded-2xl border border-hotel-border mb-2">
              <span class="text-xs font-bold text-hotel-text-tertiary uppercase">Saldo Pendiente:</span>
              <span class="text-xl font-display font-black text-hotel-gold">${reservaSeleccionada.saldo_pendiente}</span>
            </div>

            <button onclick={() => modoGestion = 'pago'} class="btn-action">
              <span class="text-lg"></span> Registrar Pago / Abono
            </button>
            <button onclick={() => modoGestion = 'consumo'} class="btn-action">
              <span class="text-lg"></span> Añadir Consumo (Minibar/Rest)
            </button>
            <button onclick={() => modoGestion = 'noshow'} class="btn-action text-hotel-error-light opacity-50 hover:opacity-100">
              <span class="text-lg"></span> Marcar como No-Show
            </button>
          </div>

        {:else if modoGestion === 'pago'}
          <PagoRegistro 
            reservaId={reservaSeleccionada.id} 
            totalPendiente={parseFloat(reservaSeleccionada.saldo_pendiente)} 
            onpago={cerrarGestion} 
          />
        
        {:else if modoGestion === 'consumo'}
          <ConsumoSelector 
            reservaId={reservaSeleccionada.id} 
            onaguardado={cerrarGestion} 
          />

        {:else if modoGestion === 'noshow'}
           <NoShowModal 
            reserva={reservaSeleccionada} 
            onconfirm={() => { modoGestion = null; reservaSeleccionada = null; invalidateAll(); }}
            oncancel={() => modoGestion = 'menu'}
           />
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  @reference "../../app.css";
  
  .custom-scrollbar::-webkit-scrollbar { width: 6px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #d4af3720; border-radius: 10px; }
  .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #d4af3740; }
  .btn-action {
    @apply flex items-center gap-4 w-full p-4 bg-hotel-surface border border-hotel-border rounded-2xl 
           text-xs font-black uppercase tracking-widest text-hotel-text-primary 
           hover:border-hotel-gold hover:bg-hotel-gold/5 transition-all text-left;
  }
</style>