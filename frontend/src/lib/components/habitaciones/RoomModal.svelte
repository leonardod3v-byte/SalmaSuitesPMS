<script lang="ts">
  import { habitacionesApi } from '$lib/services/habitaciones';
  import { toast } from '$lib/stores/toast';
  import { auth } from '$lib/stores/auth';

  let { data = null, modo = 'ver', tipos = [], onclose, onupdated } = $props();

  const isAdmin = $derived($auth?.user?.role === 'admin');
  let vista = $state<'detalle' | 'form'>(modo === 'crear' ? 'form' : 'detalle');

  // Estados con paleta de app.css
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

  // Formulario reactivo
  let form = $state({
    numero: data?.numero ?? '',
    piso: data?.piso ?? '',
    tipo: data?.tipo ?? (tipos[0]?.id ?? ''),
    estado: data?.estado ?? 'libre'
  });

  async function handleGuardar() {
    if (!form.numero || !form.piso || !form.tipo) {
      errorForm = 'Todos los campos marcados con * son obligatorios';
      return;
    }

    guardando = true;
    errorForm = '';

    try {
      const payload = {
        numero: form.numero,
        piso: Number(form.piso),
        tipo: Number(form.tipo),
        estado: form.estado
      };

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
      errorForm = 'Error al procesar la solicitud. Revisa los datos.';
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

<div class="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-hotel-bg/90 backdrop-blur-sm" onclick={onclose}>
  <div 
    class="bg-hotel-surface border border-hotel-border w-full max-w-lg rounded-2xl shadow-hotel-lg overflow-hidden flex flex-col animate-in fade-in zoom-in duration-200"
    onclick={e => e.stopPropagation()}
  >
    <!-- Header VIP -->
    <header class="p-6 border-b border-hotel-border flex justify-between items-center bg-gradient-to-r from-hotel-surface to-hotel-bg">
      <div>
        <h2 class="text-2xl font-display font-bold text-hotel-text-primary italic">
          {vista === 'form' ? (data?.id ? 'Editar Registro' : 'Nueva Habitación') : `Habitación #${data?.numero}`}
        </h2>
        <p class="text-xs text-hotel-text-tertiary uppercase tracking-widest mt-1">Gestión de Activos Operativos</p>
      </div>
      <button onclick={onclose} class="p-2 hover:bg-hotel-surface-hover rounded-full border border-hotel-border text-hotel-text-tertiary transition-colors">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
      </button>
    </header>

    <div class="p-6 space-y-6 overflow-y-auto max-h-[70vh]">
      {#if errorForm}
        <div class="p-3 bg-hotel-error/10 border border-hotel-error/20 rounded-lg text-hotel-error-light text-sm flex items-center gap-2">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"/></svg>
          {errorForm}
        </div>
      {/if}

      {#if vista === 'detalle'}
        <!-- Grid de Info Elegante -->
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

        <!-- Selector de Estado Moderno -->
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
        <!-- Formulario de Edición/Creación -->
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-1">
              <label class="text-[10px] font-bold text-hotel-text-tertiary uppercase">Número *</label>
              <input bind:value={form.numero} type="text" class="w-full bg-hotel-bg border border-hotel-border rounded-lg p-2.5 text-hotel-text-primary focus:border-hotel-gold outline-none transition-all" />
            </div>
            <div class="space-y-1">
              <label class="text-[10px] font-bold text-hotel-text-tertiary uppercase">Piso *</label>
              <input bind:value={form.piso} type="number" class="w-full bg-hotel-bg border border-hotel-border rounded-lg p-2.5 text-hotel-text-primary focus:border-hotel-gold outline-none transition-all" />
            </div>
          </div>
          <div class="space-y-1">
            <label class="text-[10px] font-bold text-hotel-text-tertiary uppercase">Categoría *</label>
            <select bind:value={form.tipo} class="w-full bg-hotel-bg border border-hotel-border rounded-lg p-2.5 text-hotel-text-primary focus:border-hotel-gold outline-none appearance-none">
              {#each tipos as t}
                <option value={t.id}>{t.nombre}</option>
              {/each}
            </select>
          </div>
        </div>
      {/if}
    </div>

    <!-- Footer de Acciones -->
    <footer class="p-6 border-t border-hotel-border bg-hotel-bg/50 flex justify-between items-center">
      {#if vista === 'detalle'}
        <button 
          onclick={() => vista = 'form'}
          class="text-xs font-bold text-hotel-gold hover:text-hotel-gold-light transition-colors uppercase tracking-widest"
        >
          Editar Registro
        </button>
        <button 
          onclick={quickStatusUpdate}
          disabled={guardando || nuevoEstado === data?.estado}
          class="bg-hotel-gold text-hotel-bg px-6 py-2 rounded-lg font-bold text-xs uppercase tracking-widest hover:bg-hotel-gold-light disabled:opacity-50 transition-all shadow-hotel-gold"
        >
          {guardando ? 'Procesando...' : 'Aplicar Estado'}
        </button>
      {:else}
        <button onclick={() => vista = 'detalle'} class="text-xs font-bold text-hotel-text-tertiary uppercase tracking-widest">Atrás</button>
        <button 
          onclick={handleGuardar}
          disabled={guardando}
          class="bg-hotel-gold text-hotel-bg px-8 py-2 rounded-lg font-bold text-xs uppercase tracking-widest hover:bg-hotel-gold-light disabled:opacity-50 transition-all"
        >
          {guardando ? 'Guardando...' : (data?.id ? 'Guardar Cambios' : 'Crear Habitación')}
        </button>
      {/if}
    </footer>
  </div>
</div>
