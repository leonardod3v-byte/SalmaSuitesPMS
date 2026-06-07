<script lang="ts">
  import { habitacionesApi } from '$lib/services/habitaciones';
  import { toast } from '$lib/stores/toast';
  import { auth } from '$lib/stores/auth';
  import ModalShell from '$lib/components/ModalShell.svelte';
  import Button from '$lib/components/Button.svelte';
  import InputHotel from '$lib/components/InputHotel.svelte';
  import Icon from '$lib/components/Icons.svelte';
   // Ajusta según tus tipos

  let { data = null, modo = 'ver', tipos = [], onclose, onupdated } = $props();

  const isAdmin = $derived($auth?.user?.role === 'admin');
  // svelte-ignore state_referenced_locally
  let vista = $state<'detalle' | 'form'>(modo === 'crear' ? 'form' : 'detalle');

  // Definir tipo para los estados
  type EstadoKey = 'libre' | 'limpia' | 'sucia' | 'ocupada' | 'mantenimiento' | 'construccion';

  const ESTADO_META: Record<EstadoKey, { label: string; color: string; bg: string }> = {
    libre:         { label: 'Disponible', color: 'var(--color-hotel-success-light)', bg: 'rgba(45,106,79,0.1)' },
    limpia:        { label: 'Limpia',     color: 'var(--color-hotel-success-light)', bg: 'rgba(45,106,79,0.1)' },
    sucia:         { label: 'Sucia',      color: 'var(--color-hotel-gold)',        bg: 'rgba(179,142,93,0.1)' },
    ocupada:       { label: 'Ocupada',    color: 'var(--color-hotel-error-light)', bg: 'rgba(155,34,38,0.1)' },
    mantenimiento: { label: 'Mantenimiento', color: 'var(--color-hotel-vip-light)', bg: 'rgba(88,47,126,0.1)' },
    construccion:  { label: 'Obra',       color: 'var(--color-hotel-text-tertiary)', bg: 'rgba(130,112,102,0.1)' },
  };

  // Estado seleccionado para cambio rápido (solo en modo detalle)
  // svelte-ignore state_referenced_locally
  let nuevoEstado = $state<EstadoKey>((data?.estado as EstadoKey) ?? 'libre');
  let guardando = $state(false);

  // Formulario de creación/edición
  let form = $state({
    numero: '',
    piso: '',
    tipo: '',
    estado: 'limpia' as EstadoKey,
    tiene_minibar: false,
    notas: ''
  });

  // Sincronizar formulario cuando cambian los props
  $effect(() => {
    if (data) {
      form.numero = data.numero ?? '';
      form.piso = data.piso ?? '';
      form.tipo = data.tipo ?? (tipos[0]?.id ?? '');
      form.estado = (data.estado as EstadoKey) ?? 'limpia';
      form.tiene_minibar = data.tiene_minibar ?? false;
      form.notas = data.notas ?? '';
      nuevoEstado = form.estado;
    } else {
      // Reiniciar formulario para creación
      form.numero = '';
      form.piso = '';
      form.tipo = tipos[0]?.id ?? '';
      form.estado = 'limpia';
      form.tiene_minibar = false;
      form.notas = '';
      nuevoEstado = 'limpia';
    }
  });

  // Obtener el precio base del tipo seleccionado
  const tipoSeleccionado = $derived(tipos.find(t => t.id === Number(form.tipo)));
  const precioBase = $derived(tipoSeleccionado?.precio_base_noche ?? 0);

  // Validar si se puede cambiar el estado (no permitir si está ocupada)
  const noSePuedeCambiarEstado = $derived(data?.estado === 'ocupada');

  const precioFormateado = $derived(
    data?.tipo_precio ? parseFloat(String(data.tipo_precio)).toFixed(2) : '0.00'
  );

  // svelte-ignore state_referenced_locally
  let estadoActual = $state(data?.estado as EstadoKey);
  $effect(() => { estadoActual = data?.estado as EstadoKey; });
  const estadoCambiado = $derived(nuevoEstado !== estadoActual);

  async function handleGuardar() {
    if (!form.numero || !form.piso || !form.tipo) {
      toast.send('Todos los campos marcados con * son obligatorios', 'error');
      return;
    }
    guardando = true;
    try {
      const payload = {
        numero: form.numero,
        piso: Number(form.piso),
        tipo: Number(form.tipo),
        estado: form.estado,
        tiene_minibar: form.tiene_minibar,
        notas: form.notas
      };
      if (data?.id) {
        await habitacionesApi.update(data.id, payload);
        toast.send('Cambios guardados correctamente', 'success');
      } else {
        await habitacionesApi.create(payload);
        toast.send('Habitación creada exitosamente', 'success');
      }
      onupdated();
      onclose();
    } catch (err: any) {
      console.error(err);
      toast.send(err?.message || 'Error al procesar la solicitud', 'error');
    } finally {
      guardando = false;
    }
  }

  async function quickStatusUpdate() {
    if (!data?.id) return;
    if (noSePuedeCambiarEstado) {
      toast.send('No se puede cambiar el estado de una habitación ocupada', 'warning');
      return;
    }
    guardando = true;
    try {
      await habitacionesApi.updateStatus(data.id, nuevoEstado);
      toast.send(`Estado actualizado a ${ESTADO_META[nuevoEstado].label}`, 'success');
      onupdated();
      onclose();
    } catch (err: any) {
      console.error(err);
      toast.send(err?.message || 'No se pudo actualizar el estado', 'error');
    } finally {
      guardando = false;
    }
  }
</script>

<ModalShell
  title={modo === 'crear' ? 'Nueva Unidad' : `Habitación #${data?.numero}`}
  subtitle={modo === 'crear' ? 'Registro de habitación' : data?.tipo_nombre ?? ''}
  onclose={onclose}
>
  <div class="p-6 space-y-6 overflow-y-auto max-h-[70vh]">
    {#if vista === 'detalle' && data}
      <!-- Vista de detalle: muestra toda la información -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div class="space-y-4">
          <div class="p-4 bg-hotel-bg rounded-xl border border-hotel-border">
            <p class="text-[10px] font-bold text-hotel-text-tertiary uppercase tracking-tighter">Ubicación</p>
            <p class="text-lg font-semibold text-hotel-text-primary mt-1">Piso {data.piso}</p>
          </div>
          <div class="p-4 bg-hotel-bg rounded-xl border border-hotel-border">
            <p class="text-[10px] font-bold text-hotel-text-tertiary uppercase tracking-tighter">Estado actual</p>
            <div class="flex items-center gap-2 mt-1">
              <span class="w-3 h-3 rounded-full" style="background: {ESTADO_META[data.estado as EstadoKey]?.color}"></span>
              <span class="text-lg font-semibold text-hotel-text-primary">{ESTADO_META[data.estado as EstadoKey]?.label ?? data.estado}</span>
            </div>
          </div>
        </div>
        <div class="space-y-4">
          <div class="p-4 bg-hotel-bg rounded-xl border border-hotel-border">
            <p class="text-[10px] font-bold text-hotel-text-tertiary uppercase tracking-tighter">Tipo</p>
            <p class="text-lg font-semibold text-hotel-gold mt-1">{data.tipo_nombre}</p>
            <p class="text-xs text-hotel-text-tertiary mt-1">Capacidad: {Number(data.capacidad_maxima)} personas</p>
            <p class="text-sm font-bold text-hotel-gold mt-2">${precioFormateado} / noche</p>
          </div>
          {#if data.notas}
            <div class="p-4 bg-hotel-bg rounded-xl border border-hotel-border">
              <p class="text-[10px] font-bold text-hotel-text-tertiary uppercase tracking-tighter">Notas</p>
              <p class="text-sm text-hotel-text-secondary mt-1 italic">{data.notas}</p>
            </div>
          {/if}
        </div>
      </div>

      <!-- Selector de estado (solo si admin y la habitación no está ocupada) -->
      <div>
        <!-- svelte-ignore a11y_label_has_associated_control -->
        <label class="text-[10px] font-bold text-hotel-text-tertiary uppercase tracking-widest block mb-3">Actualizar Estado Operativo</label>
        {#if noSePuedeCambiarEstado}
          <div class="flex items-center gap-2 p-3 bg-hotel-error/10 border border-hotel-error/30 rounded-lg text-hotel-error-light text-sm">
            <Icon name="alert" class="w-4 h-4" />
            <span>No se puede cambiar el estado de una habitación ocupada. La reserva debe finalizar primero.</span>
          </div>
        {/if}
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-2">
          {#each Object.entries(ESTADO_META) as [key, val]}
            <button 
              onclick={() => nuevoEstado = key as EstadoKey}
              disabled={noSePuedeCambiarEstado}
              class="flex items-center gap-2 p-2 rounded-lg border transition-all text-[11px] font-bold uppercase disabled:opacity-50 disabled:cursor-not-allowed"
              style="
                background: {nuevoEstado === key ? val.bg : 'transparent'};
                border-color: {nuevoEstado === key ? val.color : 'var(--color-hotel-border)'};
                color: {nuevoEstado === key ? val.color : 'var(--color-hotel-text-secondary)'};
              "
            >
              <span class="w-1.5 h-1.5 rounded-full" style="background: {val.color}"></span>
              {val.label}
            </button>
          {/each}
        </div>
      </div>

    {:else}
      <!-- Formulario de creación/edición -->
      <div class="space-y-5">
        <div class="grid grid-cols-2 gap-4">
          <InputHotel
            label="Número *"
            bind:value={form.numero}
            placeholder="Ej: 101"
          />
          <InputHotel
            label="Piso *"
            type="number"
            bind:value={form.piso}
            placeholder="Ej: 1"
          />
        </div>
        <div class="space-y-1">
          <!-- svelte-ignore a11y_label_has_associated_control -->
          <label class="text-[10px] font-bold text-hotel-text-tertiary uppercase">Categoría *</label>
          <select bind:value={form.tipo} class="input-hotel appearance-none">
            {#each tipos as t}
              <option value={t.id}>{t.nombre} - ${t.precio_base_noche}/noche</option>
            {/each}
          </select>
          <p class="text-xs text-hotel-text-tertiary mt-1">Precio base: ${precioBase} por noche (definido por el tipo)</p>
        </div>
        <div class="space-y-1">
          <!-- svelte-ignore a11y_label_has_associated_control -->
          <label class="text-[10px] font-bold text-hotel-text-tertiary uppercase">Estado inicial</label>
          <select bind:value={form.estado} class="input-hotel">
            {#each Object.entries(ESTADO_META) as [key, val]}
              <option value={key}>{val.label}</option>
            {/each}
          </select>
        </div>
      </div>
    {/if}
  </div>

  <footer class="p-6 border-t border-hotel-border bg-hotel-bg/50 flex justify-between items-center">
    {#if vista === 'detalle'}
      <div class="flex gap-3">
        <Button variant="secondary" size="sm" onclick={() => vista = 'form'}>
          Editar Registro
        </Button>
      </div>
      <Button 
        variant="gold" 
        loading={guardando}
        disabled={guardando || !estadoCambiado || noSePuedeCambiarEstado}
        onclick={quickStatusUpdate}
      >
        Aplicar Estado
      </Button>
    {:else}
      <Button variant="secondary" size="sm" onclick={() => vista = 'detalle'}>
        Atrás
      </Button>
      <Button 
        variant="gold" 
        loading={guardando}
        onclick={handleGuardar}
      >
        {data?.id ? 'Guardar Cambios' : 'Crear Habitación'}
      </Button>
    {/if}
  </footer>
</ModalShell>