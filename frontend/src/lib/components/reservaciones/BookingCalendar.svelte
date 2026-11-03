<script lang="ts">
  import type { ReservaListItem } from '$lib/types/reservacion';
  import Icon from '$components/ui/Icons.svelte';

  let { reservas, habitaciones, semanaInicio, onCeldaClick }: {
    reservas:      ReservaListItem[];
    habitaciones:  { numero: string; tipo_nombre: string; piso: number }[];
    semanaInicio:  Date;
    onCeldaClick:  (hab: string, fecha: string) => void;
  } = $props();

  const DIAS_ES = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
  const hoy = new Date().toISOString().split('T')[0];

  const toISO = (d: Date) => d.toISOString().split('T')[0];

  const diasSemana = $derived(
    Array.from({ length: 7 }, (_, i) => {
      const d = new Date(semanaInicio);
      d.setDate(d.getDate() + i);
      return d;
    })
  );

  const mapaReservas = $derived.by(() => {
    const map = new Map<string, ReservaListItem>();
    reservas.forEach(r => {
      let current = new Date(r.fecha_entrada + 'T12:00:00');
      const end = new Date(r.fecha_salida + 'T12:00:00');
      while (current < end) {
        map.set(`${r.habitacion_numero}-${toISO(current)}`, r);
        current.setDate(current.getDate() + 1);
      }
    });
    return map;
  });

  const pisos = $derived(
    habitaciones.reduce((acc, h) => {
      if (!acc.has(h.piso)) acc.set(h.piso, []);
      acc.get(h.piso)!.push(h);
      return acc;
    }, new Map<number, typeof habitaciones>())
  );

  const fmtCabecera = (d: Date) =>
    d.toLocaleDateString('es-VE', { day: '2-digit', month: '2-digit' });

  const getEstadoBadge = (estado: string) => {
    switch (estado) {
      case 'Confirmada': return 'bg-hotel-info/10 text-hotel-info-light border-hotel-info/30';
      case 'EnCurso': return 'bg-hotel-gold/10 text-hotel-gold-light border-hotel-gold/30';
      case 'Finalizada': return 'bg-hotel-success/10 text-hotel-success-light border-hotel-success/30';
      case 'Cancelada': return 'bg-hotel-error/10 text-hotel-error-light border-hotel-error/30';
      case 'NoShow': return 'bg-hotel-text-tertiary/10 text-hotel-text-tertiary border-hotel-text-tertiary/30';
      default: return 'bg-hotel-surface border-hotel-border text-hotel-text-secondary';
    }
  };

  const leyenda = $derived.by(() => {
    const map = new Map<string, string>();
    reservas.forEach(r => {
      if (r.ocupacion_nombre && r.ocupacion_color) {
        map.set(r.ocupacion_nombre, r.ocupacion_color);
      }
    });
    return Array.from(map.entries()).map(([nombre, color]) => ({ nombre, color }));
  });
</script>

<div class="overflow-hidden rounded-2xl border border-hotel-border bg-hotel-surface shadow-hotel-lg">
  <div class="overflow-x-auto custom-scrollbar">
    <table class="w-full border-collapse text-xs min-w-225">
      <thead>
        <tr class="bg-hotel-bg/50 backdrop-blur-sm">
          <th class="sticky left-0 z-20 bg-hotel-bg border-b border-r border-hotel-border px-4 py-4 text-left w-32 shadow-[4px_0_10px_-5px_rgba(0,0,0,0.1)]">
            <div class="space-y-1">
              <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Hab.</p>
              <p class="text-[9px] font-medium text-hotel-text-tertiary">Nivel</p>
            </div>
          </th>

          {#each diasSemana as dia, i}
            {@const isToday = toISO(dia) === hoy}
            {@const isWeekend = dia.getDay() === 0 || dia.getDay() === 6}
            <th class="border-b border-r border-hotel-border/50 px-2 py-4 text-center min-w-22.5 transition-colors
              {isToday ? 'bg-hotel-gold/15' : isWeekend ? 'bg-hotel-bg/40' : ''}">
              <p class="font-black uppercase tracking-widest {isToday ? 'text-hotel-gold' : 'text-hotel-text-secondary'}">{DIAS_ES[i]}</p>
              <p class="text-hotel-text-tertiary font-mono text-[10px]">{fmtCabecera(dia)}</p>
            </th>
          {/each}

          <th class="border-b border-l border-hotel-border px-4 py-4 text-left min-w-45 bg-hotel-bg/30">
            <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-text-tertiary">Huésped Titular</p>
          </th>
          <th class="border-b border-l border-hotel-border px-4 py-4 text-center w-28 bg-hotel-bg/30">
            <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-text-tertiary leading-tight">Estado</p>
          </th>
        </tr>
      </thead>

      <tbody>
        {#each [...pisos.entries()].sort((a, b) => a[0] - b[0]) as [piso, habs]}
          <tr class="select-none">
            <td colspan="10" class="bg-hotel-bg/80 px-4 py-1.5 text-[9px] font-black uppercase tracking-[0.3em] text-hotel-gold/70 border-y border-hotel-border/50">
              Piso {piso} — {piso === 1 ? 'Planta Principal' : 'Planta Superior'}
            </td>
          </tr>

          {#each habs as hab}
            {@const rSemana = diasSemana.map(d => mapaReservas.get(`${hab.numero}-${toISO(d)}`))}
            {@const pReserva = rSemana.find(r => r)}

            <tr class="group hover:bg-hotel-surface-hover/60 transition-colors border-b border-hotel-border/20">
              <td class="sticky left-0 z-10 bg-hotel-surface group-hover:bg-hotel-bg border-r border-hotel-border px-4 py-3 shadow-[4px_0_10px_-5px_rgba(0,0,0,0.1)] transition-colors">
                <p class="font-display font-black italic text-base text-hotel-text-primary group-hover:text-hotel-gold transition-colors">
                  {hab.numero}
                </p>
                <p class="text-[9px] font-bold text-hotel-text-tertiary uppercase truncate leading-none mt-1">{hab.tipo_nombre}</p>
              </td>

              {#each diasSemana as dia, i}
                {@const reserva = rSemana[i]}
                {@const isToday = toISO(dia) === hoy}
                {@const isWeekend = dia.getDay() === 0 || dia.getDay() === 6}
                {@const isStart = reserva?.fecha_entrada === toISO(dia)}
                {@const isEnd = reserva?.fecha_salida === toISO(new Date(dia.getTime() + 86400000))}

                <td
                  class="border-r border-hotel-border/20 p-1 text-center cursor-pointer relative transition-all duration-200
                    {isToday ? 'bg-hotel-gold/5' : isWeekend ? 'bg-hotel-bg/20' : ''}
                    {!reserva ? 'hover:bg-hotel-gold/10' : 'hover:bg-black/5'}"
                  onclick={() => onCeldaClick(hab.numero, toISO(dia))}
                >
                  <div class="flex items-center justify-center h-10">
                    {#if reserva}
                      <div
                          class="w-8 h-8 rounded-full border-2 flex items-center justify-center transition-transform hover:scale-110 shadow-md relative group/tooltip"
                          style="background: {reserva.ocupacion_color || '#9E9E9E'}15; border-color: {reserva.ocupacion_color || '#9E9E9E'}; color: {reserva.ocupacion_color || '#9E9E9E'}"
                      >
                        {#if isStart}
                          <Icon name="arrow-right" class="w-4 h-4" />
                        {:else if isEnd}
                          <Icon name="check" class="w-4 h-4" />
                        {:else}
                          <div class="w-2.5 h-2.5 rounded-full" style="background: {reserva.ocupacion_color || '#9E9E9E'}"></div>
                        {/if}

                        <!-- Tooltip con nombre y empresa -->
                        <div class="absolute bottom-full mb-1 hidden group-hover/tooltip:block bg-hotel-bg border border-hotel-border text-white text-[9px] px-2 py-1 rounded shadow-lg whitespace-nowrap z-50 pointer-events-none">
                          {reserva.huesped_nombre}
                          {#if reserva.empresa_nombre}
                            <span class="block text-[8px] text-hotel-vip-light mt-0.5">🏢 {reserva.empresa_nombre}</span>
                          {/if}
                        </div>
                      </div>
                    {:else}
                      <div class="w-8 h-8 rounded-full border-2 border-dashed border-hotel-border/40 opacity-0 group-hover:opacity-100 hover:border-hotel-gold/50 transition-all"></div>
                    {/if}
                  </div>
                </td>
              {/each}

              <td class="border-l border-hotel-border/40 px-4 py-2 bg-hotel-bg/10">
                {#if pReserva}
                  <div class="flex items-center gap-1.5">
                    <p class="text-[11px] font-black text-hotel-text-primary truncate max-w-40 uppercase" title="{pReserva.huesped_nombre}">
                      {pReserva.huesped_nombre}
                    </p>
                    {#if pReserva.empresa_nombre}
                      <span class="shrink-0 px-1 py-0.5 rounded text-[8px] font-black uppercase bg-hotel-vip/20 text-hotel-vip-light border border-hotel-vip/30" title="{pReserva.empresa_nombre}">
                        Empresa
                      </span>
                    {/if}
                  </div>
                  <p class="text-[9px] font-mono text-hotel-text-tertiary">{pReserva.huesped_documento}</p>
                {/if}
              </td>

              <td class="border-l border-hotel-border/40 px-4 py-2 text-center bg-hotel-bg/10">
                {#if pReserva}
                  <span class="inline-block px-2 py-0.5 rounded-md border text-[9px] font-black uppercase tracking-tighter {getEstadoBadge(pReserva.estado)}">
                    {pReserva.estado === 'EnCurso' ? 'En Curso' : pReserva.estado}
                  </span>
                {/if}
              </td>
            </tr>
          {/each}
        {/each}
      </tbody>
    </table>
  </div>
</div>

<div class="flex flex-wrap items-center gap-4 mt-6 px-2">
  <span class="text-[9px] font-black uppercase tracking-[0.2em] text-hotel-text-tertiary mr-2 border-r border-hotel-border pr-4">Simbología:</span>
  {#each leyenda as cfg}
    <div class="flex items-center gap-2 px-3 py-1.5 rounded-2xl bg-hotel-surface border border-hotel-border shadow-sm">
      <div class="w-3 h-3 rounded-full shadow-inner" style="background: {cfg.color}"></div>
      <span class="text-[10px] font-bold text-hotel-text-secondary uppercase tracking-tight">{cfg.nombre}</span>
    </div>
  {/each}
</div>
