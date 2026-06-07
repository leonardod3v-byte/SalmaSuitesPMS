<script lang="ts">
  import { habitacionesApi } from '$lib/services/habitaciones';
  import { toast } from '$lib/stores/toast';
  import { auth } from '$lib/stores/auth';
  import ModalShell from '$lib/components/ModalShell.svelte';
  import Button from '$lib/components/Button.svelte';
  import InputHotel from '$lib/components/InputHotel.svelte';
  import Icon from '$lib/components/Icons.svelte';

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
  <div class="p-6 space-y-6 overflow-y-auto max-h-[70vh] custom-scrollbar">
    {#if errorForm}
      <div class="flex items-center gap-2 p-3 bg-hotel-error/10 border border-hotel-error/20 rounded-lg text-hotel-error-light text-sm">
        <Icon name="alert" class="w-4 h-4 shrink-0" />
        <span>{errorForm}</span>
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
          <label class="text-[10px] font-bold text-hotel-text-tertiary uppercase">Categoría *</label>
          <select bind:value={form.tipo} class="input-hotel appearance-none">
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
      <Button variant="secondary" size="sm" onclick={() => vista = 'form'}>
        Editar Registro
      </Button>
      <Button 
        variant="gold" 
        loading={guardando}
        disabled={guardando || nuevoEstado === data?.estado}
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