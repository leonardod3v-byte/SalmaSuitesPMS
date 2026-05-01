<script lang="ts">
  import { habitacionesApi } from '$lib/services/habitaciones';
  import { toast } from '$lib/stores/toast';
  import { auth } from '$lib/stores/auth';
  import ModalShell from '$lib/components/ModalShell.svelte';

  // Props con desestructuración reactiva
  let { data = null, modo = 'ver', tipos = [], onclose, onupdated } = $props();

  const isAdmin = $derived($auth?.user?.role === 'admin');
  let vista = $state<'detalle' | 'form'>(modo === 'crear' ? 'form' : 'detalle');

  const ESTADO_META = {
    libre:         { label: 'Disponible', color: 'var(--color-hotel-success-light)', bg: 'rgba(45,106,79,0.1)' },
    limpia:        { label: 'Limpia',     color: 'var(--color-hotel-success-light)', bg: 'rgba(45,106,79,0.1)' },
    sucia:         { label: 'Sucia',      color: 'var(--color-hotel-gold)',        bg: 'rgba(179,142,93,0.1)' },
    ocupada:       { label: 'Ocupada',    color: 'var(--color-hotel-error-light)', bg: 'rgba(155,34,38,0.1)' },
    mantenimiento: { label: 'Mantenimiento', color: 'var(--color-hotel-vip-light)', bg: 'rgba(88,47,126,0.1)' },
    construccion:  { label: 'Obra',       color: 'var(--color-hotel-text-tertiary)', bg: 'rgba(130,112,102,0.1)' },
  };

  let nuevoEstado = $state(data?.estado ?? 'libre');
  let guardando = $state(false);
  let errorForm = $state('');

  // Sincronizar estado cuando la data cambie (Solución líneas 21-30)
  let form = $state({
    numero: '',
    piso: '',
    tipo: '',
    estado: ''
  });

  $effect(() => {
    form.numero = data?.numero ?? '';
    form.piso = data?.piso ?? '';
    form.tipo = data?.tipo ?? (tipos[0]?.id ?? '');
    form.estado = data?.estado ?? 'libre';
    nuevoEstado = data?.estado ?? 'libre';
  });

  async function handleGuardar() {
    if (!form.numero || !form.piso || !form.tipo) {
      errorForm = 'Todos los campos marcados con * son obligatorios';
      return;
    }
    guardando = true;
    try {
      const payload = { ...form, piso: Number(form.piso), tipo: Number(form.tipo) };
      if (data?.id) {
        await habitacionesApi.update(data.id, payload);
        toast.send('Cambios guardados', 'success');
      } else {
        await habitacionesApi.create(payload);
        toast.send('Habitación creada', 'success');
      }
      onupdated();
      onclose();
    } catch (err) {
      errorForm = 'Error al procesar la solicitud.';
    } finally {
      guardando = false;
    }
  }

  async function quickStatusUpdate() {
    if (!data?.id) return;
    guardando = true;
    try {
      await habitacionesApi.updateStatus(data.id, nuevoEstado);
      toast.send('Estado actualizado', 'success');
      onupdated();
      onclose();
    } catch (err) {
      errorForm = 'No se pudo actualizar el estado';
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
        {#if errorForm}
          <div class="p-3 bg-hotel-error/10 border border-hotel-error/20 rounded-lg text-hotel-error-light text-sm flex items-center gap-2">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"/></svg>
            {errorForm}
          </div>
        {/if}

        {#if vista === 'detalle'}
          <div class="grid grid-cols-2 gap-4">
            <div class="p-4 bg-hotel-bg rounded-xl border border-hotel-border">
              <p class="text-[10px] font-bold text-hotel-text-tertiary uppercase tracking-tighter">Tipo de Habitación</p>
              <p class="text-lg font-semibold text-hotel-gold mt-1">{data?.tipo_nombre ?? 'Standard'}</p>
            </div>
            <div class="p-4 bg-hotel-bg rounded-xl border border-hotel-border">
              <p class="text-[10px] font-bold text-hotel-text-tertiary uppercase tracking-tighter">Ubicación</p>
              <p class="text-lg font-semibold text-hotel-text-primary mt-1">Piso {data?.piso}</p>
            </div>
          </div>

          <div>
            <label class="text-[10px] font-bold text-hotel-text-tertiary uppercase tracking-widest block mb-3">Actualizar Estado Operativo</label>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {#each Object.entries(ESTADO_META) as [key, val]}
                <button 
                  onclick={() => nuevoEstado = key}
                  class="flex items-center gap-2 p-2 rounded-lg border transition-all text-[11px] font-bold uppercase"
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
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-1">
                <label for="room-num" class="text-[10px] font-bold text-hotel-text-tertiary uppercase">Número *</label>
                <input id="room-num" bind:value={form.numero} type="text" class="input-hotel" />
              </div>
              <div class="space-y-1">
                <label for="room-floor" class="text-[10px] font-bold text-hotel-text-tertiary uppercase">Piso *</label>
                <input id="room-floor" bind:value={form.piso} type="number" class="input-hotel" />
              </div>
            </div>
            <div class="space-y-1">
              <label for="room-cat" class="text-[10px] font-bold text-hotel-text-tertiary uppercase">Categoría *</label>
              <select id="room-cat" bind:value={form.tipo} class="input-hotel appearance-none">
                {#each tipos as t}
                  <option value={t.id}>{t.nombre}</option>
                {/each}
              </select>
            </div>
          </div>
        {/if}
      </div>

      <footer class="p-6 border-t border-hotel-border bg-hotel-bg/50 flex justify-between items-center">
        {#if vista === 'detalle'}
          <button onclick={() => vista = 'form'} class="text-xs font-bold text-hotel-gold hover:text-hotel-gold-light transition-colors uppercase tracking-widest">
            Editar Registro
          </button>
          <button 
            onclick={quickStatusUpdate}
            disabled={guardando || nuevoEstado === data?.estado}
            class="btn-gold shadow-hotel-gold"
          >
            {guardando ? 'Procesando...' : 'Aplicar Estado'}
          </button>
        {:else}
          <button onclick={() => vista = 'detalle'} class="text-xs font-bold text-hotel-text-tertiary uppercase tracking-widest">Atrás</button>
          <button onclick={handleGuardar} disabled={guardando} class="btn-gold px-8">
            {guardando ? 'Guardando...' : (data?.id ? 'Guardar Cambios' : 'Crear Habitación')}
          </button>
        {/if}
      </footer>
</ModalShell>