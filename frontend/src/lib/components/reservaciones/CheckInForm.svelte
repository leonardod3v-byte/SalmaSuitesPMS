<script lang="ts">
  import { reservacionesApi, TIPOS_CLIENTE, type TipoCliente, type ReservaPayload } from '$lib/services/reservaciones';
  import { huespedesApi, type HuespedListItem } from '$lib/services/huespedes';
  import { apiFetch } from '$lib/services/api';
  import { toast } from '$lib/stores/toast';
  import InputHotel from '$lib/components/InputHotel.svelte';

  interface HabitacionLibre {
    id: number; numero: string; piso: number;
    tipo_nombre: string; estado: string;
  }

  let { onguardado, oncancel }: {
    onguardado: () => void;
    oncancel:   () => void;
  } = $props();

  // ── Lógica de Wizard ──────────────────────────────────────────────────────
  let paso = $state(1); 

  // Paso 1: Huésped
  let busquedaDoc = $state('');
  let huespedEncontrado = $state<HuespedListItem | null>(null);
  let buscandoHuesped = $state(false);
  let errorHuesped = $state('');

  async function buscarHuesped() {
    if (!busquedaDoc.trim()) return;
    buscandoHuesped = true;
    errorHuesped = '';
    try {
      const res = await huespedesApi.buscarPorDocumento(busquedaDoc);
      if (res.encontrado && res.huesped) {
        huespedEncontrado = res.huesped as unknown as HuespedListItem;
      } else {
        errorHuesped = 'No registrado. Debe crearlo en el módulo de Huéspedes.';
      }
    } catch {
      errorHuesped = 'Error en la conexión con la base de datos.';
    } finally {
      buscandoHuesped = false;
    }
  }

  // Paso 2: Habitación
  let habitaciones = $state<HabitacionLibre[]>([]);
  let habitacionElegida = $state<HabitacionLibre | null>(null);
  let cargandoHabs = $state(false);

  async function cargarHabitacionesLibres() {
    cargandoHabs = true;
    try {
      const res = await apiFetch<HabitacionLibre[]>('/habitaciones/?estado=libre');
      habitaciones = res;
    } catch {
      toast.send('Error al consultar disponibilidad', 'error');
    } finally {
      cargandoHabs = false;
    }
  }

  // Paso 3: Detalles Financieros
  let form = $state({
    fecha_entrada:  new Date().toISOString().split('T')[0],
    fecha_salida:   '',
    tipo_cliente:   'particular' as TipoCliente,
    metodo_pago:    'efectivo_usd',
    referencia_pago: '',
    monto_total:    '',
    monto_pagado:   '',
    notas:          '',
    requiere_factura_seniat: false,
  });

  const METODOS_PAGO = [
    { value: 'efectivo_usd', label: 'Efectivo USD'   },
    { value: 'efectivo_ves', label: 'Efectivo Bs.'   },
    { value: 'transferencia', label: 'Transferencia'  },
    { value: 'pago_movil',   label: 'Pago Móvil'      },
    { value: 'zelle',        label: 'Zelle'            },
  ];

  const noches = $derived(() => {
    if (!form.fecha_entrada || !form.fecha_salida) return 0;
    const diff = new Date(form.fecha_salida).getTime() - new Date(form.fecha_entrada).getTime();
    return Math.max(0, Math.floor(diff / 86400000));
  });

  // Navegación con validación silenciosa
  function irAPaso(n: number) {
    if (n === 2 && !huespedEncontrado) return;
    if (n === 3 && !habitacionElegida) return;
    if (n === 2) cargarHabitacionesLibres();
    paso = n;
  }

  let guardando = $state(false);

  async function confirmarReserva() {
    if (!huespedEncontrado || !habitacionElegida) return;
    guardando = true;
    try {
      const payload: ReservaPayload = {
        habitacion:      habitacionElegida.id,
        huesped:         huespedEncontrado.id,
        fecha_entrada:   form.fecha_entrada,
        fecha_salida:    form.fecha_salida,
        estado:          'confirmada',
        metodo_pago:     form.metodo_pago,
        referencia_pago: form.referencia_pago,
        monto_total:     parseFloat(form.monto_total) || 0,
        monto_pagado:    parseFloat(form.monto_pagado) || 0,
        tipo_cliente:    form.tipo_cliente,
        notas:           form.notas,
        requiere_factura_seniat: form.requiere_factura_seniat,
      };
      await reservacionesApi.create(payload);
      toast.send('Reserva masterizada con éxito', 'success');
      onguardado();
    } catch {
      toast.send('Error crítico al procesar reserva', 'error');
    } finally {
      guardando = false;
    }
  }

  const tipoActual = $derived(TIPOS_CLIENTE[form.tipo_cliente]);
</script>

<div class="space-y-8 py-2">

  <nav class="relative flex justify-between">
    <div class="absolute top-4 left-0 w-full h-1px bg-hotel-border z-0"></div>
    {#each [
      { n: 1, label: 'Huésped' },
      { n: 2, label: 'Unidad' },
      { n: 3, label: 'Tarifa' },
      { n: 4, label: 'Resumen' },
    ] as s}
      <button 
        onclick={() => irAPaso(s.n)}
        disabled={s.n > paso}
        class="relative z-10 flex flex-col items-center gap-2 group"
      >
        <div class="w-9 h-9 rounded-full border-2 flex items-center justify-center text-[11px] font-black transition-all duration-500
          {paso >= s.n ? 'bg-hotel-gold border-hotel-gold text-hotel-bg shadow-hotel-gold/20' : 'bg-hotel-surface border-hotel-border text-hotel-text-tertiary'}
          {paso === s.n ? 'ring-4 ring-hotel-gold/10 scale-110' : ''}">
          {paso > s.n ? '✓' : s.n}
        </div>
        <span class="text-[9px] font-black uppercase tracking-[0.2em] {paso >= s.n ? 'text-hotel-gold' : 'text-hotel-text-tertiary'}">
          {s.label}
        </span>
      </button>
    {/each}
  </nav>

  <div class="bg-hotel-bg/30 rounded-2xl p-1">
    {#if paso === 1}
      <div class="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
        <div class="flex gap-3 items-end">
          <div class="flex-1">
            <InputHotel
              label="Documento de Identidad"
              placeholder="V-00000000"
              bind:value={busquedaDoc}
              error={errorHuesped}
            />
          </div>
          <button 
            onclick={buscarHuesped}
            disabled={buscandoHuesped}
            class="h-12 px-6 btn-gold shrink-0 mb-2px"
          >
            {buscandoHuesped ? '...' : 'Verificar'}
          </button>
        </div>

        {#if huespedEncontrado}
          <div class="p-5 bg-hotel-surface border border-hotel-gold/30 rounded-2xl flex items-center gap-4 shadow-sm">
            <div class="w-12 h-12 rounded-xl bg-hotel-gold/10 border border-hotel-gold/20 flex items-center justify-center text-hotel-gold font-display text-xl italic font-black">
              {huespedEncontrado.nombre_completo.charAt(0)}
            </div>
            <div class="flex-1">
              <p class="text-[11px] font-black uppercase tracking-widest text-hotel-gold-light mb-1">Huésped Validado</p>
              <h4 class="font-display text-lg italic text-hotel-text-primary leading-none">{huespedEncontrado.nombre_completo}</h4>
              <p class="text-[10px] font-mono text-hotel-text-tertiary mt-1">{huespedEncontrado.documento_formateado}</p>
            </div>
            <button onclick={() => huespedEncontrado = null} class="p-2 hover:bg-hotel-error/10 text-hotel-text-tertiary hover:text-hotel-error-light rounded-lg transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M6 18L18 6M6 6l12 12" stroke-width="2"/></svg>
            </button>
          </div>
        {/if}

        <div class="flex justify-end pt-4">
          <button onclick={() => irAPaso(2)} disabled={!huespedEncontrado} class="btn-gold group px-8 py-3 disabled:opacity-30">
            <span>Disponibilidad</span>
            <svg class="w-4 h-4 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M13 7l5 5m0 0l-5 5m5-5H6" stroke-width="2.5"/></svg>
          </button>
        </div>
      </div>
    {/if}

    {#if paso === 2}
      <div class="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
        <header class="flex justify-between items-center">
          <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-text-tertiary">Seleccione Habitación Libre</p>
          <span class="text-[10px] font-bold text-hotel-gold">{habitaciones.length} disponibles</span>
        </header>

        {#if cargandoHabs}
          <div class="h-48 flex flex-col items-center justify-center gap-4 border border-dashed border-hotel-border rounded-3xl">
            <div class="w-8 h-8 border-2 border-hotel-gold border-t-transparent rounded-full animate-spin"></div>
            <p class="text-[10px] font-black uppercase tracking-widest text-hotel-text-tertiary">Consultando Rack...</p>
          </div>
        {:else}
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 max-h-340px overflow-y-auto pr-2 custom-scrollbar">
            {#each habitaciones as hab (hab.id)}
              <button
                onclick={() => habitacionElegida = hab}
                class="relative p-5 rounded-2xl border-2 text-left transition-all duration-300 group
                       {habitacionElegida?.id === hab.id
                         ? 'bg-hotel-gold/10 border-hotel-gold shadow-hotel-gold/10'
                         : 'bg-hotel-surface border-hotel-border hover:border-hotel-gold/40'}"
              >
                <div class="flex justify-between items-start mb-2">
                  <p class="font-display text-2xl font-black italic {habitacionElegida?.id === hab.id ? 'text-hotel-gold' : 'text-hotel-text-primary'}">#{hab.numero}</p>
                  <span class="text-[9px] font-black opacity-40">PISO {hab.piso}</span>
                </div>
                <p class="text-[10px] font-bold uppercase tracking-widest text-hotel-text-secondary">{hab.tipo_nombre}</p>
              </button>
            {/each}
          </div>
        {/if}

        <footer class="flex justify-between pt-4 border-t border-hotel-border/50">
          <button onclick={() => paso = 1} class="text-[10px] font-black uppercase tracking-widest text-hotel-text-tertiary hover:text-hotel-text-primary transition-colors">← Volver</button>
          <button onclick={() => irAPaso(3)} disabled={!habitacionElegida} class="btn-gold px-8 py-3 disabled:opacity-30 uppercase text-[10px] font-black tracking-widest">Definir Estancia</button>
        </footer>
      </div>
    {/if}

    {#if paso === 3}
      <div class="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
        <div class="grid grid-cols-2 gap-6 bg-hotel-surface p-6 rounded-3xl border border-hotel-border">
          <InputHotel label="Fecha de Entrada" type="date" bind:value={form.fecha_entrada} />
          <InputHotel label="Fecha de Salida"  type="date" bind:value={form.fecha_salida} />
          
          {#if noches() > 0}
            <div class="col-span-2 py-2 px-4 bg-hotel-gold/5 border border-hotel-gold/20 rounded-xl text-center">
              <span class="text-[11px] font-black uppercase tracking-[0.3em] text-hotel-gold">Estancia de {noches()} Noches</span>
            </div>
          {/if}
        </div>

        <div class="space-y-3">
          <label class="text-10px font-black uppercase tracking-0.2em text-hotel-text-tertiary">Segmento de Cliente</label>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {#each Object.entries(TIPOS_CLIENTE) as [key, cfg]}
              <button
                onclick={() => form.tipo_cliente = key as TipoCliente}
                class="px-4 py-3 rounded-xl border text-[10px] font-black uppercase tracking-wider transition-all"
                style="
                  background: {form.tipo_cliente === key ? cfg.bg : 'var(--color-hotel-surface)'};
                  border-color: {form.tipo_cliente === key ? cfg.color : 'var(--color-hotel-border)'};
                  color: {form.tipo_cliente === key ? cfg.text : 'var(--color-hotel-text-tertiary)'};
                "
              >
                {cfg.label}
              </button>
            {/each}
          </div>
        </div>

        <div class="grid grid-cols-2 gap-6">
          <InputHotel label="Inversión Total ($)" type="number" bind:value={form.monto_total} />
          <InputHotel label="Abono Inicial ($)" type="number" bind:value={form.monto_pagado} />
        </div>

        <footer class="flex justify-between pt-4">
          <button onclick={() => paso = 2} class="text-[10px] font-black uppercase tracking-widest text-hotel-text-tertiary hover:text-hotel-text-primary transition-colors">← Habitación</button>
          <button 
            onclick={() => irAPaso(4)} 
            disabled={!form.fecha_entrada || !form.fecha_salida || !form.monto_total} 
            class="btn-gold px-10 py-3 disabled:opacity-30 uppercase text-[10px] font-black tracking-widest"
          >
            Revisar Transacción
          </button>
        </footer>
      </div>
    {/if}

    {#if paso === 4}
      <div class="space-y-6 animate-in zoom-in-95 duration-500">
        <div class="relative overflow-hidden p-8 rounded-2rem border-2 shadow-2xl"
             style="background: {tipoActual.bg}; border-color: {tipoActual.color}30;">
          
          <div class="absolute top-0 right-0 p-6 opacity-10">
            <svg class="w-32 h-32" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L1 21h22L12 2zm0 3.45L19.15 19H4.85L12 5.45z"/></svg>
          </div>

          <div class="relative z-10 space-y-6">
            <header class="border-b pb-4 flex justify-between items-end" style="border-color: {tipoActual.color}20">
              <div>
                <span class="text-[9px] font-black uppercase tracking-[0.4em]" style="color: {tipoActual.text}">Confirmación de Reserva</span>
                <h3 class="font-display text-3xl italic font-black text-hotel-text-primary leading-tight mt-1">{huespedEncontrado?.nombre_completo}</h3>
              </div>
              <div class="text-right">
                <p class="text-[10px] font-black uppercase tracking-widest text-hotel-text-tertiary">Unidad</p>
                <p class="text-2xl font-display font-black italic text-hotel-gold">#{habitacionElegida?.numero}</p>
              </div>
            </header>

            <div class="grid grid-cols-2 gap-y-6 text-[11px]">
              <div>
                <p class="font-black uppercase tracking-widest text-hotel-text-tertiary mb-1">Check-In</p>
                <p class="font-bold text-hotel-text-primary">{form.fecha_entrada}</p>
              </div>
              <div>
                <p class="font-black uppercase tracking-widest text-hotel-text-tertiary mb-1">Check-Out</p>
                <p class="font-bold text-hotel-text-primary">{form.fecha_salida} ({noches()} noches)</p>
              </div>
              <div>
                <p class="font-black uppercase tracking-widest text-hotel-text-tertiary mb-1">Inversión</p>
                <p class="text-lg font-black text-hotel-gold">${parseFloat(form.monto_total || '0').toFixed(2)}</p>
              </div>
              <div>
                <p class="font-black uppercase tracking-widest text-hotel-text-tertiary mb-1">Estado Pago</p>
                <p class="font-bold text-hotel-text-secondary">Abonado: ${parseFloat(form.monto_pagado || '0').toFixed(2)}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="flex flex-col gap-3">
          <button 
            onclick={confirmarReserva} 
            disabled={guardando} 
            class="btn-gold w-full py-4 text-[12px] font-black uppercase tracking-[0.3em] shadow-hotel-gold/20"
          >
            {#if guardando} Procesando... {:else} Finalizar Registro {/if}
          </button>
          <button onclick={() => paso = 3} class="text-[10px] font-black uppercase tracking-widest text-hotel-text-tertiary hover:text-hotel-error-light transition-colors text-center py-2">
            Corregir Datos
          </button>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  @reference "../../../app.css";
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #d4af3720; border-radius: 10px; }
</style>