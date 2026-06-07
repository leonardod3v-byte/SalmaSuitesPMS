<script lang="ts">
  import type { PageData } from './$types';
  import { goto, invalidateAll } from '$app/navigation';
  import { type ReservaListItem, reservacionesApi } from '$lib/services/reservaciones';
  import BookingCalendar from '$lib/components/reservaciones/BookingCalendar.svelte';
  import ReservaManagementModal from '$lib/components/reservaciones/ReservaManagementModal.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import Button from '$lib/components/Button.svelte';
  import Icon from '$lib/components/Icons.svelte';
  import KPICard from '$lib/components/KPICard.svelte';

  let { data }: { data: PageData } = $props();

  let reservas = $derived((data.reservas ?? []) as ReservaListItem[]);
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

  let modalCheckin = $state(false);
  let reservaSeleccionada = $state<ReservaListItem | null>(null);

  function onCeldaClick(hab: string, fecha: string) {
    const reserva = reservas.find(r => 
      r.habitacion_numero === hab && r.fecha_entrada <= fecha && r.fecha_salida > fecha
    );
    if (reserva) {
      reservaSeleccionada = reserva;
    } else {
      modalCheckin = true;
    }
  }

  function cerrarModalGestion() {
    reservaSeleccionada = null;
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

<div class="max-w-[1600px] mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-1000">

  <PageHeader title="Reservaciones" subtitle="Gestión de Estancias y Check-ins">
    <Button variant="gold" onclick={() => modalCheckin = true}>
      <Icon name="plus" class="w-4 h-4" />
      Nuevo Check-In
    </Button>
  </PageHeader>

  <!-- KPIs Cards -->
  <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
    <KPICard
      title="Check-ins Hoy"
      value={statsHoy().checkins}
      subtitle="Ingresos pendientes"
      iconName="checkIn"
      color="success"
    />
    <KPICard
      title="Check-outs Hoy"
      value={statsHoy().checkouts}
      subtitle="Salidas programadas"
      iconName="checkOut"
      color="error"
    />
    <KPICard
      title="Huéspedes en Casa"
      value={statsHoy().ocupadas}
      subtitle="Habitaciones ocupadas"
      iconName="hotel"
      color="gold"
    />
  </div>

  <!-- Calendario semanal -->
  <section class="bg-hotel-surface border border-hotel-border rounded-3xl overflow-hidden shadow-hotel-lg">
    <div class="p-6 border-b border-hotel-border bg-hotel-bg/40 flex flex-col sm:flex-row justify-between items-center gap-4">
      <div class="space-y-1">
        <span class="text-[9px] font-black uppercase tracking-[0.3em] text-hotel-gold/80">Control Semanal</span>
        <p class="font-display text-2xl italic text-hotel-text-primary tracking-tight">
          {rangoFechaTexto()}
        </p>
      </div>
      <nav class="flex items-center gap-2 p-1 bg-hotel-bg rounded-xl border border-hotel-border">
        <Button variant="ghost" size="sm" onclick={() => navegarSemana(-1)}>
          <Icon name="chevron-left" class="w-5 h-5" />
        </Button>
        <Button variant="ghost" size="sm" onclick={() => goto('/reservaciones')}>
          Hoy
        </Button>
        <Button variant="ghost" size="sm" onclick={() => navegarSemana(1)}>
          <Icon name="chevron-right" class="w-5 h-5" />
        </Button>
      </nav>
    </div>
    <div class="p-2 bg-hotel-surface">
      <BookingCalendar {reservas} {habitaciones} {semanaInicio} {onCeldaClick} />
    </div>
  </section>
</div>

{#if modalCheckin}
  <ReservaManagementModal
    onclose={() => {
      modalCheckin = false;
      invalidateAll();
    }}
    onsave={() => {
      modalCheckin = false;
      invalidateAll();
    }}
  />
{/if}

{#if reservaSeleccionada}
  <ReservaManagementModal
    reserva={reservaSeleccionada}
    onclose={cerrarModalGestion}
  />
{/if}