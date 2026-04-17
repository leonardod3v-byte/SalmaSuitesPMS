<script lang="ts">
  import { huespedesApi, type Huesped, type HuespedPayload } from '$lib/services/huespedes';
  import { toast } from '$lib/stores/toast';
  import InputHotel from '$lib/components/InputHotel.svelte';

  let { data = null, modo = 'crear', onclose, onupdated } = $props();

  const TIPOS_DOC = [
    { value: 'V', label: 'V — Venezolano' },
    { value: 'E', label: 'E — Extranjero' },
    { value: 'J', label: 'J — Jurídico' },
    { value: 'G', label: 'G — Gubernamental' },
    { value: 'P', label: 'P — Pasaporte' },
  ];

  // ── Formulario Reactivo (Svelte 5) ──
  let form = $state<HuespedPayload>({
    tipo_documento: 'V',
    numero_documento: '',
    nombre: '',
    apellido: '',
    telefono: '',
    email: '',
    notas: '',
    acompanantes: [],
  });

  // Sincronizar cuando 'data' cambie (Evita el error de "initial value only")
  $effect(() => {
    form.tipo_documento = data?.tipo_documento ?? 'V';
    form.numero_documento = data?.numero_documento ?? '';
    form.nombre = data?.nombre ?? '';
    form.apellido = data?.apellido ?? '';
    form.telefono = data?.telefono ?? '';
    form.email = data?.email ?? '';
    form.notas = data?.notas ?? '';
    form.acompanantes = data?.acompanantes ? [...data.acompanantes] : [];
  });

  let errores = $state<Partial<Record<keyof HuespedPayload | 'general', string>>>({});
  let guardando = $state(false);

  function validar(): boolean {
    errores = {};
    if (!form.nombre.trim()) errores.nombre = 'El nombre es requerido';
    if (!form.apellido.trim()) errores.apellido = 'El apellido es requerido';
    if (!form.numero_documento.trim()) errores.numero_documento = 'Documento requerido';
    if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errores.email = 'Email inválido';
    return Object.keys(errores).length === 0;
  }

  async function handleGuardar() {
    if (!validar()) return;
    guardando = true;
    try {
      if (modo === 'editar' && data?.id) {
        await huespedesApi.update(data.id, form);
        toast.send('Huésped actualizado', 'success');
      } else {
        await huespedesApi.create(form);
        toast.send('Huésped registrado', 'success');
      }
      onupdated();
      onclose();
    } catch (err: any) {
      if (err?.data?.numero_documento) errores.numero_documento = 'Ya registrado';
      else errores.general = 'Error al guardar. Verifica los datos.';
    } finally {
      guardando = false;
    }
  }

  const agregarAcompanante = () => form.acompanantes = [...form.acompanantes, { nombre: '', documento: '', edad: 0 }];
  const quitarAcompanante = (i: number) => form.acompanantes = form.acompanantes.filter((_, idx) => idx !== i);
</script>

<svelte:window onkeydown={(e) => e.key === 'Escape' && onclose()} />

<div
  class="fixed inset-0 z-200 flex items-center justify-center p-4 bg-hotel-bg/90 backdrop-blur-sm"
  onclick={(e) => e.target === e.currentTarget && onclose()}
  onkeydown={(e) => e.key === 'Enter' && e.target === e.currentTarget && onclose()}
  role="button"
  tabindex="-1"
>
  <div 
    class="relative w-full max-w-2xl max-h-[90vh] flex flex-col bg-hotel-surface border border-hotel-border rounded-2xl shadow-hotel-lg overflow-hidden animate-in fade-in zoom-in-95 duration-200"
    onclick={(e) => e.stopPropagation()}
    role="dialog"
    aria-modal="true"
    tabindex="0"
  >
    <header class="p-6 border-b border-hotel-border flex justify-between items-center bg-gradient-to-r from-hotel-surface to-hotel-bg">
      <div>
        <h2 class="font-display text-2xl italic font-bold text-hotel-text-primary">
          {modo === 'crear' ? 'Nuevo Huésped' : 'Editar Registro'}
        </h2>
        <p class="text-[10px] text-hotel-text-tertiary uppercase tracking-[0.2em] mt-1">
          {modo === 'crear' ? 'Módulo de Recepción' : `ID: ${data?.numero_documento}`}
        </p>
      </div>
      <button onclick={onclose} aria-label="Cerrar" class="p-2 hover:bg-hotel-surface-hover rounded-full border border-hotel-border text-hotel-text-tertiary transition-colors">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
      </button>
    </header>

    <div class="overflow-y-auto flex-1 p-8 space-y-8">
      
      <section class="space-y-4">
        <h3 class="text-[10px] font-black uppercase tracking-widest text-hotel-gold-light border-b border-hotel-gold/20 pb-2">Identificación Legal</h3>
        <div class="flex gap-4">
          <div class="w-1/3 space-y-1">
            <label for="doc_tipo" class="text-[10px] font-bold text-hotel-text-tertiary uppercase">Tipo</label>
            <select id="doc_tipo" bind:value={form.tipo_documento} class="input-hotel">
              {#each TIPOS_DOC as t}<option value={t.value}>{t.label}</option>{/each}
            </select>
          </div>
          <div class="flex-1">
            <InputHotel
              id="doc_num"
              label="Número de documento"
              placeholder="12345678"
              bind:value={form.numero_documento}
              error={errores.numero_documento}
              required
            />
          </div>
        </div>
      </section>

      <section class="space-y-4">
        <h3 class="text-[10px] font-black uppercase tracking-widest text-hotel-gold-light border-b border-hotel-gold/20 pb-2">Información de Contacto</h3>
        <div class="grid grid-cols-2 gap-4">
          <InputHotel id="h_nom" label="Nombre" bind:value={form.nombre} error={errores.nombre} required />
          <InputHotel id="h_ape" label="Apellido" bind:value={form.apellido} error={errores.apellido} required />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <InputHotel id="h_tel" label="Teléfono" bind:value={form.telefono} error={errores.telefono} />
          <InputHotel id="h_mail" label="Email" type="email" bind:value={form.email} error={errores.email} />
        </div>
        <div class="space-y-1">
          <label for="h_notas" class="text-[10px] font-bold text-hotel-text-tertiary uppercase">Observaciones VIP</label>
          <textarea
            id="h_notas"
            bind:value={form.notas}
            rows="2"
            class="input-hotel resize-none h-20 py-3"
            placeholder="Preferencias de habitación, alergias..."
          ></textarea>
        </div>
      </section>

      <section class="space-y-4">
        <div class="flex items-center justify-between border-b border-hotel-gold/20 pb-2">
          <h3 class="text-[10px] font-black uppercase tracking-widest text-hotel-gold-light">Acompañantes ({form.acompanantes.length})</h3>
          <button onclick={agregarAcompanante} class="text-[10px] font-black text-hotel-gold hover:text-hotel-gold-light transition-all flex items-center gap-1 uppercase">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-width="3" d="M12 5v14M5 12h14"/></svg>
            Añadir
          </button>
        </div>

        <div class="grid gap-3">
          {#each form.acompanantes as acomp, i (i)}
            <div class="flex gap-3 p-4 bg-hotel-bg/50 rounded-xl border border-hotel-border group animate-in slide-in-from-right-2">
              <div class="flex-1 grid grid-cols-2 gap-3">
                <input bind:value={acomp.nombre} placeholder="Nombre Completo" class="input-hotel bg-hotel-surface h-9" />
                <input bind:value={acomp.documento} placeholder="Documento" class="input-hotel bg-hotel-surface h-9" />
              </div>
              <button onclick={() => quitarAcompanante(i)} class="p-2 text-hotel-text-tertiary hover:text-hotel-error-light transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>
          {/each}
        </div>
      </section>
    </div>

    <footer class="p-6 border-t border-hotel-border bg-hotel-bg/50 flex justify-between items-center">
      <button onclick={onclose} class="text-xs font-bold text-hotel-text-tertiary uppercase tracking-widest hover:text-hotel-text-secondary transition-colors">
        Cancelar
      </button>
      <button 
        onclick={handleGuardar} 
        disabled={guardando} 
        class="btn-gold px-10 shadow-hotel-gold disabled:opacity-50"
      >
        {#if guardando}
          <div class="w-4 h-4 border-2 border-hotel-bg/30 border-t-hotel-bg rounded-full animate-spin"></div>
          Procesando...
        {:else}
          {modo === 'crear' ? 'Registrar Huésped' : 'Actualizar Datos'}
        {/if}
      </button>
    </footer>
  </div>
</div>