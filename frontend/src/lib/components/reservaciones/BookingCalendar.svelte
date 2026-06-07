<script lang="ts">
  import { TIPOS_CLIENTE, type ReservaListItem } from '$lib/services/reservaciones';
  import Icon from '$lib/components/Icons.svelte';

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
</script>

<div class="overflow-hidden rounded-2xl border border-hotel-border bg-hotel-surface shadow-hotel-lg">
  <div class="overflow-x-auto custom-scrollbar">
    <table class="w-full border-collapse text-xs min-w-[900px]">
      <thead>
        <tr class="bg-hotel-bg/50 backdrop-blur-sm">
          <th class="sticky left-0 z-20 bg-hotel-bg border-b border-r border-hotel-border px-4 py-4 text-left w-44 shadow-[4px_0_10px_-5px_rgba(0,0,0,0.1)]">
            <div class="space-y-1">
              <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Habitación</p>
              <p class="text-[9px] font-medium text-hotel-text-tertiary">Categoría y Nivel</p>
            </div>
          </th>

          {#each diasSemana as dia, i}
            {@const isToday = toISO(dia) === hoy}
            <th class="border-b border-hotel-border px-2 py-4 text-center min-w-[100px] transition-colors {isToday ? 'bg-hotel-gold/10' : ''}">
              <p class="font-black uppercase tracking-widest {isToday ? 'text-hotel-gold' : 'text-hotel-text-secondary'}">{DIAS_ES[i]}</p>
              <p class="text-hotel-text-tertiary font-mono text-[10px]">{fmtCabecera(dia)}</p>
            </th>
          {/each}

          <th class="border-b border-l border-hotel-border px-4 py-4 text-left min-w-[180px] bg-hotel-bg/30">
            <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-text-tertiary">Huésped Titular</p>
          </th>
          <th class="border-b border-l border-hotel-border px-4 py-4 text-center w-20 bg-hotel-bg/30">
            <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-text-tertiary leading-tight">Estado</p>
          </th>
        </tr>
      </thead>

      <tbody>
        {#each [...pisos.entries()].sort((a, b) => a[0] - b[0]) as [piso, habs]}
          <tr class="select-none">
            <td colspan="10" class="bg-hotel-bg/80 px-4 py-1.5 text-[9px] font-black uppercase tracking-[0.3em] text-hotel-gold/70 border-y border-hotel-border/50">
              Nivel {piso} — Planta {piso === 1 ? 'Principal' : 'Superior'}
            </td>
          </tr>

          {#each habs as hab}
            {@const rSemana = diasSemana.map(d => mapaReservas.get(`${hab.numero}-${toISO(d)}`))}
            {@const pReserva = rSemana.find(r => r)}

            <tr class="group hover:bg-hotel-surface-hover/40 transition-colors border-b border-hotel-border/20">
              <td class="sticky left-0 z-10 bg-hotel-surface group-hover:bg-hotel-bg border-r border-hotel-border px-4 py-3 shadow-[4px_0_10px_-5px_rgba(0,0,0,0.1)] transition-colors">
                <p class="font-display font-black italic text-base text-hotel-text-primary group-hover:text-hotel-gold transition-colors">
                  {hab.numero}
                </p>
                <p class="text-[9px] font-bold text-hotel-text-tertiary uppercase truncate leading-none mt-1">{hab.tipo_nombre}</p>
              </td>

              {#each diasSemana as dia, i}
                {@const reserva = rSemana[i]}
                {@const isToday = toISO(dia) === hoy}
                {@const isStart = reserva?.fecha_entrada === toISO(dia)}
                {@const isEnd = reserva?.fecha_salida === toISO(new Date(dia.getTime() + 86400000))}
                {@const config = reserva ? TIPOS_CLIENTE[reserva.tipo_cliente as keyof typeof TIPOS_CLIENTE] : null}

                <td 
                  class="border-r border-hotel-border/10 p-1 text-center cursor-pointer relative transition-all duration-200 {isToday ? 'bg-hotel-gold/0.03' : ''} {!reserva ? 'hover:bg-hotel-gold/10' : ''}"
                  onclick={() => onCeldaClick(hab.numero, toISO(dia))}
                >
                  <div class="flex items-center justify-center h-10">
                    {#if reserva}
                      <div 
                        class="w-8 h-8 rounded-full border-2 flex items-center justify-center transition-transform group-hover/cell:scale-110 shadow-sm"
                        style="background: {config?.bg}; border-color: {config?.color}; color: {config?.text}"
                      >
                        {#if isStart}
                          <Icon name="arrow-right" class="w-4 h-4" />
                        {:else if isEnd}
                          <Icon name="check" class="w-4 h-4" />
                        {:else}
                          <div class="w-2.5 h-2.5 rounded-full" style="background: {config?.text}"></div>
                        {/if}
                      </div>
                    {:else}
                      <div class="w-8 h-8 rounded-full border-2 border-dashed border-hotel-border/40 opacity-20 hover:opacity-100 hover:border-hotel-gold/50 transition-all"></div>
                    {/if}
                  </div>
                </td>
              {/each}

              <td class="border-l border-hotel-border/40 px-4 py-2 bg-hotel-bg/10">
                {#if pReserva}
                  <p class="text-[11px] font-black text-hotel-text-primary truncate max-w-[160px] uppercase">{pReserva.huesped_nombre}</p>
                  <p class="text-[9px] font-mono text-hotel-text-tertiary">{pReserva.huesped_documento}</p>
                {/if}
              </td>

              <td class="border-l border-hotel-border/40 px-4 py-2 text-center bg-hotel-bg/10">
                {#if pReserva}
                  <span class="inline-block px-2 py-0.5 rounded-md bg-hotel-surface border border-hotel-border text-[8px] font-black uppercase tracking-tighter text-hotel-text-secondary">
                    {pReserva.estado.slice(0, 8)}
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
  {#each Object.entries(TIPOS_CLIENTE) as [, cfg]}
    <div class="flex items-center gap-2 px-3 py-1.5 rounded-2xl bg-hotel-surface border border-hotel-border shadow-sm">
      <div class="w-3 h-3 rounded-full shadow-inner" style="background: {cfg.color}"></div>
      <span class="text-[10px] font-bold text-hotel-text-secondary uppercase tracking-tight">{cfg.label}</span>
    </div>
  {/each}
</div>

<style>
  @reference "../../../app.css";
  .custom-scrollbar::-webkit-scrollbar { height: 6px; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #d4af3720; border-radius: 20px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
</style>