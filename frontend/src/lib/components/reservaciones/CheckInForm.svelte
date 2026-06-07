<script lang="ts">
  import { reservacionesApi, TIPOS_CLIENTE, type TipoCliente, type ReservaPayload } from '$lib/services/reservaciones';
  import { huespedesApi, type HuespedListItem } from '$lib/services/huespedes';
  import { apiFetch } from '$lib/services/api';
  import { toast } from '$lib/stores/toast';
  import InputHotel from '$lib/components/InputHotel.svelte';
  import Button from '$lib/components/Button.svelte';
  import Icon from '$lib/components/Icons.svelte';

  let { onguardado, oncancel } = $props();

  let paso = $state(1);

  // ----- PASO 1: Búsqueda de huésped -----
  let busquedaTexto = $state('');
  let resultadosBusqueda = $state<HuespedListItem[]>([]);
  let buscando = $state(false);
  let mostrarResultados = $state(false);
  let timer: ReturnType<typeof setTimeout>;
  let huespedEncontrado = $state<HuespedListItem | null>(null);
  let puedeAvanzarPaso1 = $derived(!!huespedEncontrado);
  let errorHuesped = $state('');

  async function buscarHuéspedes(query: string) {
    if (!query.trim()) {
      resultadosBusqueda = [];
      mostrarResultados = false;
      return;
    }
    buscando = true;
    try {
      const res = await huespedesApi.search(query);
      resultadosBusqueda = res;
      mostrarResultados = true;
    } catch {
      resultadosBusqueda = [];
    } finally {
      buscando = false;
    }
  }

  function onBusquedaInput() {
    clearTimeout(timer);
    if (busquedaTexto.trim() === '') {
      resultadosBusqueda = [];
      mostrarResultados = false;
      return;
    }
    timer = setTimeout(() => buscarHuéspedes(busquedaTexto), 300);
  }

  function seleccionarHuesped(h: HuespedListItem) {
    huespedEncontrado = { ...h };
    busquedaTexto = h.nombre_completo;
    mostrarResultados = false;
    errorHuesped = '';
  }

  function limpiarHuesped() {
    huespedEncontrado = null;
    busquedaTexto = '';
    resultadosBusqueda = [];
    mostrarResultados = false;
  }

  // ----- PASO 2: Selección de habitación -----
  let habitaciones = $state<any[]>([]);
  let habitacionElegida = $state<any | null>(null);
  let cargandoHabs = $state(false);
  let precioPorNoche = $derived(habitacionElegida?.tipo_precio ? parseFloat(habitacionElegida.tipo_precio) : 0);
  let montoTotalCalculado = $derived(precioPorNoche * noches());

  async function cargarHabitacionesLibres() {
    cargandoHabs = true;
    try {
      const res = await apiFetch<any[]>('/habitaciones/?estado=libre');
      habitaciones = res;
    } catch {
      toast.send('Error al consultar disponibilidad', 'error');
    } finally {
      cargandoHabs = false;
    }
  }

  // ----- PASO 3: Detalles financieros -----
  let form = $state({
    fecha_entrada: new Date().toISOString().split('T')[0],
    fecha_salida: '',
    metodo_pago: 'efectivo',
    referencia_pago: '',
    monto_pagado: '',
    notas: '',
    modalidad_pago: 'contado' as 'contado' | 'abono' | 'credito',
    requiere_factura: false,
    datos_fiscales: { rif: '', razon_social: '', direccion: '' }
  });

  const METODOS_PAGO = [
    { value: 'efectivo', label: 'Efectivo' },
    { value: 'tarjeta', label: 'Tarjeta' },
    { value: 'pago_movil', label: 'Pago Móvil' },
  ];

  const noches = $derived(() => {
    if (!form.fecha_entrada || !form.fecha_salida) return 0;
    const diff = new Date(form.fecha_salida).getTime() - new Date(form.fecha_entrada).getTime();
    return Math.max(0, Math.floor(diff / 86400000));
  });

  const errorModalidad = $derived(() => {
    const total = montoTotalCalculado;
    const pagado = parseFloat(form.monto_pagado) || 0;
    if (form.modalidad_pago === 'contado' && pagado !== total) return 'Contado: abono debe ser igual al total.';
    if (form.modalidad_pago === 'abono' && (pagado <= 0 || pagado >= total)) return 'Abono: pago inicial >0 y menor al total.';
    if (form.modalidad_pago === 'credito' && pagado !== 0) return 'Crédito: no debe registrar pago inicial.';
    return '';
  });

  // ----- Navegación entre pasos -----
  function irAPaso(n: number) {
    if (n === 2 && !huespedEncontrado) return;
    if (n === 3 && !habitacionElegida) return;
    if (n === 2) cargarHabitacionesLibres();
    paso = n;
  }

  // ----- Confirmar reserva -----
  let guardando = $state(false);

  async function confirmarReserva() {
    if (!huespedEncontrado || !habitacionElegida) return;
    if (errorModalidad()) {
      toast.send(errorModalidad(), 'error');
      return;
    }
    guardando = true;
    try {
      const payload: ReservaPayload = {
        habitacion: habitacionElegida.id,
        huesped: huespedEncontrado.id,
        fecha_entrada: form.fecha_entrada,
        fecha_salida: form.fecha_salida,
        estado: 'confirmada',
        metodo_pago: form.metodo_pago,
        referencia_pago: form.referencia_pago,
        monto_total: montoTotalCalculado,
        monto_pagado: parseFloat(form.monto_pagado) || 0,
        notas: form.notas,
        modalidad_pago: form.modalidad_pago,
        requiere_factura: form.requiere_factura,
        datos_fiscales: form.requiere_factura ? form.datos_fiscales : undefined,
        tipo_cliente: 'particular'
      };
      await reservacionesApi.create(payload);
      toast.send('Reserva creada con éxito', 'success');
      onguardado();
    } catch {
      toast.send('Error al crear reserva', 'error');
    } finally {
      guardando = false;
    }
  }

</script>

<div class="space-y-8 py-2">
  <!-- Navegación por pasos -->
  <nav class="relative flex justify-between">
    <div class="absolute top-4 left-0 w-full h-px bg-hotel-border z-0"></div>
    {#each [
      { n: 1, label: 'Huésped' },
      { n: 2, label: 'Unidad' },
      { n: 3, label: 'Tarifa' },
      { n: 4, label: 'Resumen' }
    ] as s}
      <button onclick={() => irAPaso(s.n)} disabled={s.n > paso} class="relative z-10 flex flex-col items-center gap-2 group">
        <div class="w-9 h-9 rounded-full border-2 flex items-center justify-center text-[11px] font-black transition-all
          {paso >= s.n ? 'bg-hotel-gold border-hotel-gold text-hotel-bg' : 'bg-hotel-surface border-hotel-border text-hotel-text-tertiary'}
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
    <!-- PASO 1: Búsqueda huésped -->
    {#if paso === 1}
      <div class="space-y-6">
        <div class="relative">
          <InputHotel
            label="Buscar huésped (nombre o cédula)"
            placeholder="Ej: Carlos Rodríguez o V-12345678"
            bind:value={busquedaTexto}
            oninput={onBusquedaInput}
            error={errorHuesped}
          />
          {#if mostrarResultados && resultadosBusqueda.length > 0}
            <div class="absolute z-20 mt-1 w-full bg-hotel-surface border border-hotel-border rounded-xl shadow-lg max-h-60 overflow-y-auto custom-scrollbar">
              {#each resultadosBusqueda as h}
                <button onclick={() => seleccionarHuesped(h)} class="w-full text-left px-4 py-3 hover:bg-hotel-gold/10 transition-colors border-b border-hotel-border/50 last:border-0 flex justify-between items-center">
                  <div>
                    <p class="text-sm font-bold text-hotel-text-primary">{h.nombre_completo}</p>
                    <p class="text-[10px] font-mono text-hotel-text-tertiary">{h.documento_formateado}</p>
                  </div>
                  {#if h.es_vip}<Icon name="star" class="w-4 h-4 text-hotel-vip-light fill-hotel-vip" />{/if}
                </button>
              {/each}
            </div>
          {:else if mostrarResultados && !buscando && resultadosBusqueda.length === 0 && busquedaTexto.trim() !== ''}
            <div class="absolute z-20 mt-1 w-full bg-hotel-surface border border-hotel-border rounded-xl shadow-lg p-3 text-center">
              <p class="text-xs text-hotel-text-tertiary">No se encontraron huéspedes</p>
            </div>
          {/if}
          {#if buscando}<div class="absolute right-3 top-9"><div class="w-4 h-4 border-2 border-hotel-gold border-t-transparent rounded-full animate-spin"></div></div>{/if}
        </div>

        {#if huespedEncontrado}
          <div class="p-5 bg-hotel-surface border border-hotel-gold/30 rounded-2xl flex items-center gap-4">
            <div class="w-12 h-12 rounded-xl bg-hotel-gold/10 border border-hotel-gold/20 flex items-center justify-center text-hotel-gold font-display text-xl italic font-black">{huespedEncontrado.nombre_completo.charAt(0)}</div>
            <div class="flex-1">
              <p class="text-[11px] font-black uppercase tracking-widest text-hotel-gold-light mb-1">Huésped Validado</p>
              <h4 class="font-display text-lg italic text-hotel-text-primary leading-none">{huespedEncontrado.nombre_completo}</h4>
              <p class="text-[10px] font-mono text-hotel-text-tertiary mt-1">{huespedEncontrado.documento_formateado}</p>
            </div>
            <button onclick={limpiarHuesped} class="p-2 hover:bg-hotel-error/10 text-hotel-text-tertiary hover:text-hotel-error-light rounded-lg"><Icon name="close" class="w-5 h-5" /></button>
          </div>
        {/if}

        <div class="flex justify-end pt-4">
          {#key huespedEncontrado}
            <Button variant="gold" onclick={() => irAPaso(2)} disabled={!huespedEncontrado}>
              Siguiente <Icon name="arrow-right" class="w-4 h-4" />
            </Button>
          {/key}
        </div>
      </div>
    {/if}

    <!-- PASO 2: Selección habitación -->
    {#if paso === 2}
      <div class="space-y-6">
        <header class="flex justify-between items-center"><p class="text-[10px] font-black uppercase tracking-[0.2em]">Seleccione Habitación Libre</p><span class="text-[10px] font-bold text-hotel-gold">{habitaciones.length} disponibles</span></header>
        {#if cargandoHabs}
          <div class="h-48 flex flex-col items-center justify-center gap-4 border border-dashed border-hotel-border rounded-3xl"><div class="w-8 h-8 border-2 border-hotel-gold border-t-transparent rounded-full animate-spin"></div><p class="text-[10px] font-black uppercase tracking-widest">Consultando...</p></div>
        {:else}
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 max-h-[340px] overflow-y-auto pr-2 custom-scrollbar">
            {#each habitaciones as hab}
              <button onclick={() => habitacionElegida = hab} class="relative p-5 rounded-2xl border-2 text-left transition-all {habitacionElegida?.id === hab.id ? 'bg-hotel-gold/10 border-hotel-gold' : 'bg-hotel-surface border-hotel-border hover:border-hotel-gold/40'}">
                <div class="flex justify-between items-start mb-2"><p class="font-display text-2xl font-black italic">#{hab.numero}</p><span class="text-[9px] font-black opacity-40">PISO {hab.piso}</span></div>
                <p class="text-[10px] font-bold uppercase tracking-widest">{hab.tipo_nombre}</p>
              </button>
            {/each}
          </div>
        {/if}
        <footer class="flex justify-between pt-4 border-t border-hotel-border/50">
          <Button variant="ghost" onclick={() => paso = 1}>← Volver</Button>
            {#key habitacionElegida}
              <Button variant="gold" onclick={() => irAPaso(3)} disabled={!habitacionElegida}>
                Definir Estancia
              </Button>
            {/key}
        </footer>
      </div>
    {/if}

    <!-- PASO 3: Detalles financieros -->
    {#if paso === 3}
      <div class="space-y-6">
        <div class="grid grid-cols-2 gap-6 bg-hotel-surface p-6 rounded-3xl border border-hotel-border">
          <InputHotel label="Fecha de Entrada" type="date" bind:value={form.fecha_entrada} />
          <InputHotel label="Fecha de Salida"  type="date" bind:value={form.fecha_salida} />
          {#if noches() > 0}<div class="col-span-2 py-2 px-4 bg-hotel-gold/5 border border-hotel-gold/20 rounded-xl text-center"><span class="text-[11px] font-black uppercase tracking-[0.3em] text-hotel-gold">Estancia de {noches()} Noches</span></div>{/if}
        </div>

        <div class="space-y-3">
        <!-- svelte-ignore a11y_label_has_associated_control -->
          <label class="text-[10px] font-black uppercase tracking-[0.2em]">Modalidad de Pago</label>
          <div class="flex gap-3">
            {#each ['contado', 'abono', 'credito'] as modalidad}
              <label class="flex items-center gap-2 cursor-pointer text-sm"><input type="radio" bind:group={form.modalidad_pago} value={modalidad} class="w-4 h-4 text-hotel-gold" /> {modalidad.charAt(0).toUpperCase() + modalidad.slice(1)}</label>
            {/each}
          </div>
        </div>

        <div class="space-y-3">
          <!-- svelte-ignore a11y_label_has_associated_control -->
          <label class="text-[10px] font-black uppercase tracking-[0.2em]">Método de Pago</label>
          <div class="grid grid-cols-3 gap-2">
            {#each METODOS_PAGO as mp}
              <label class="flex flex-col items-center gap-1 p-2 rounded-xl border cursor-pointer {form.metodo_pago === mp.value ? 'bg-hotel-gold/10 border-hotel-gold' : 'border-hotel-border'}">
                <input type="radio" bind:group={form.metodo_pago} value={mp.value} class="hidden" />
                <Icon name={mp.value === 'efectivo' ? 'efectivo' : mp.value === 'tarjeta' ? 'credit-card' : 'pago_movil'} class="w-5 h-5" />
                <span class="text-[9px] font-bold">{mp.label}</span>
              </label>
            {/each}
          </div>
        </div>

        <div class="grid grid-cols-2 gap-6">
          <div class="bg-hotel-surface rounded-xl p-4 border border-hotel-gold/20 text-center">
            <p class="text-[10px] font-black uppercase tracking-widest text-hotel-text-tertiary">Inversión Total</p>
            <p class="text-3xl font-display font-black text-hotel-gold mt-1">${montoTotalCalculado.toFixed(2)}</p>
            <p class="text-[9px] text-hotel-text-tertiary mt-1">{precioPorNoche} x {noches()} noches</p>
          </div>
          <InputHotel label="Abono Inicial ($)" type="number" bind:value={form.monto_pagado} />
          {#if errorModalidad()}<div class="col-span-2 text-[10px] text-hotel-error-light bg-hotel-error/5 p-2 rounded-lg">{errorModalidad()}</div>{/if}
        </div>

        <div class="flex items-center gap-3">
          <input type="checkbox" bind:checked={form.requiere_factura} class="w-4 h-4 rounded border-hotel-border text-hotel-gold" />
          <span class="text-xs font-bold uppercase">Requerir factura legal</span>
        </div>

        {#if form.requiere_factura}
          <div class="space-y-3 p-4 bg-hotel-surface rounded-xl border border-hotel-border/50">
            <h4 class="text-[10px] font-black uppercase tracking-widest text-hotel-gold-light">Datos Fiscales</h4>
            <InputHotel label="RIF" placeholder="J-12345678-0" bind:value={form.datos_fiscales.rif} />
            <InputHotel label="Razón Social" bind:value={form.datos_fiscales.razon_social} />
            <InputHotel label="Dirección Fiscal" bind:value={form.datos_fiscales.direccion} />
          </div>
        {/if}

        <footer class="flex justify-between pt-4">
          <Button variant="ghost" onclick={() => paso = 2}>← Habitación</Button>
          {#key { fecha_entrada: form.fecha_entrada, fecha_salida: form.fecha_salida, monto_total: form.monto_total, error: errorModalidad() }}
            <Button variant="gold" onclick={() => irAPaso(4)} disabled={!form.fecha_entrada || !form.fecha_salida || !montoTotalCalculado || !!errorModalidad()}>
              Revisar Transacción
            </Button>
          {/key}
        </footer>
      </div>
    {/if}

    <!-- PASO 4: Resumen y confirmación -->
    {#if paso === 4}
      <div class="space-y-6 animate-in zoom-in-95 duration-500">
        <div class="relative overflow-hidden p-8 rounded-2xl border-2 shadow-2xl">
          <div class="absolute top-0 right-0 p-6 opacity-10"><Icon name="hotel" class="w-32 h-32" /></div>
          <div class="relative z-10 space-y-6">
            <div class="grid grid-cols-2 gap-y-6 text-[11px]">
              <div><p class="font-black uppercase tracking-widest text-hotel-text-tertiary mb-1">Check-In</p><p class="font-bold text-hotel-text-primary">{form.fecha_entrada}</p></div>
              <div><p class="font-black uppercase tracking-widest text-hotel-text-tertiary mb-1">Check-Out</p><p class="font-bold text-hotel-text-primary">{form.fecha_salida} ({noches()} noches)</p></div>
              <div><p class="text-lg font-black text-hotel-gold">${montoTotalCalculado.toFixed(2)}</p><p class="text-lg font-black text-hotel-gold">${parseFloat(form.monto_total || '0').toFixed(2)}</p></div>
              <div><p class="font-black uppercase tracking-widest text-hotel-text-tertiary mb-1">Pagado</p><p class="font-bold text-hotel-text-secondary">${parseFloat(form.monto_pagado || '0').toFixed(2)}</p></div>
              <div><p class="font-black uppercase tracking-widest text-hotel-text-tertiary mb-1">Modalidad</p><p class="font-bold text-hotel-text-secondary">{form.modalidad_pago}</p></div>
              <div><p class="font-black uppercase tracking-widest text-hotel-text-tertiary mb-1">Factura</p><p class="font-bold text-hotel-text-secondary">{form.requiere_factura ? 'Sí' : 'No'}</p></div>
            </div>
          </div>
        </div>
        <div class="flex flex-col gap-3">
          <Button variant="gold" fullWidth onclick={confirmarReserva} disabled={guardando}>{guardando ? 'Procesando...' : 'Finalizar Registro'}</Button>
          <Button variant="ghost" fullWidth onclick={() => paso = 3}>Corregir Datos</Button>
        </div>
      </div>
    {/if}
  </div>
</div>