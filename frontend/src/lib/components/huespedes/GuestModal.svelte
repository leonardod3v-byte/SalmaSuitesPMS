<script lang="ts">
  import { huespedesApi, type Huesped, type HuespedPayload } from '$lib/services/huespedes';
  import { toast } from '$lib/stores/toast';
  import InputHotel from '$lib/components/InputHotel.svelte';
  import ModalShell from '$lib/components/ModalShell.svelte';
  import Button from '$lib/components/Button.svelte';
  import Icon from '$lib/components/Icons.svelte';

  let { data = null, modo = 'crear', onclose, onupdated } = $props();

  // estados internos
  // svelte-ignore state_referenced_locally
  let vista = $state<'ficha' | 'formulario'>(modo === 'crear' ? 'formulario' : 'ficha');
  let guardando = $state(false);
  let errores = $state<Partial<Record<keyof typeof form | 'general', string>>>({});

  const TIPOS_DOC = [
    { value: 'V', label: 'V — Venezolano' },
    { value: 'E', label: 'E — Extranjero' },
    { value: 'J', label: 'J — Jurídico' },
    { value: 'G', label: 'G — Gubernamental' },
    { value: 'P', label: 'P — Pasaporte' },
  ];

  const ESTADO_CIVIL = [
    { value: 'soltero', label: 'Soltero' },
    { value: 'casado', label: 'Casado' },
    { value: 'divorciado', label: 'Divorciado' },
    { value: 'viudo', label: 'Viudo' },
  ];

  // Formulario completo (incluye campos opcionales del perfil extendido)
  let form = $state<HuespedPayload & {
    procedencia: string;
    profesion: string;
    edad: number | null;
    nacionalidad: string;
    estado_civil: string;
    fecha_nacimiento: string;
    telefono_contacto: string;
    profesion_otro: string;
  }>({
    tipo_documento: 'V',
    numero_documento: '',
    nombre: '',
    apellido: '',
    telefono: '',
    email: '',
    notas: '',
    acompanantes: [],
    procedencia: '',
    profesion: '',
    edad: null,
    nacionalidad: '',
    estado_civil: '',
    fecha_nacimiento: '',
    telefono_contacto: '',
    profesion_otro: '',
  });

  // Sincronizar datos del huésped cuando se abre el modal (edición)
  $effect(() => {
    if (data && modo === 'editar') {
      form.tipo_documento = data.tipo_documento ?? 'V';
      form.numero_documento = data.numero_documento ?? '';
      form.nombre = data.nombre ?? '';
      form.apellido = data.apellido ?? '';
      form.telefono = data.telefono ?? '';
      form.email = data.email ?? '';
      form.notas = data.notas ?? '';
      form.acompanantes = data.acompanantes ? [...data.acompanantes] : [];
      form.procedencia = data.procedencia ?? '';
      form.profesion = data.profesion ?? '';
      form.edad = data.edad ?? null;
      form.nacionalidad = data.nacionalidad ?? '';
      form.estado_civil = data.estado_civil ?? '';
      form.fecha_nacimiento = data.fecha_nacimiento ?? '';
      form.telefono_contacto = data.telefono_contacto ?? '';
      form.profesion_otro = (data as any).profesion_otro ?? '';
    } else if (modo === 'crear') {
      // Resetear formulario para nuevo huésped
      form = {
        tipo_documento: 'V',
        numero_documento: '',
        nombre: '',
        apellido: '',
        telefono: '',
        email: '',
        notas: '',
        acompanantes: [],
        procedencia: '',
        profesion: '',
        edad: null,
        nacionalidad: '',
        estado_civil: '',
        fecha_nacimiento: '',
        telefono_contacto: '',
        profesion_otro: '',
      };
    }
  });

  // Validaciones
  function validar(): boolean {
    errores = {};
    if (!form.nombre.trim()) errores.nombre = 'El nombre es requerido';
    if (!form.apellido.trim()) errores.apellido = 'El apellido es requerido';
    if (!form.numero_documento.trim()) errores.numero_documento = 'Documento requerido';
    if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errores.email = 'Email inválido';
    if (form.edad !== null && (form.edad < 0 || form.edad > 120)) errores.edad = 'Edad inválida (0-120)';
    if (form.profesion === 'otro' && !form.profesion_otro.trim()) {
      errores.profesion_otro = 'Debes especificar la profesión';
    }
    return Object.keys(errores).length === 0;
  }

  async function handleGuardar() {
    if (!validar()) return;
    guardando = true;
    try {
      const payload = { ...form };
      if (modo === 'editar' && data?.id) {
        await huespedesApi.update(data.id, payload);
        toast.send('Huésped actualizado', 'success');
      } else {
        await huespedesApi.create(payload);
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

  // Computar nombre completo y documento formateado para la ficha
  const nombreCompleto = $derived(`${form.nombre} ${form.apellido}`.trim());
  const documentoFormateado = $derived(`${form.tipo_documento}-${form.numero_documento}`);
</script>

<ModalShell
  title={modo === 'crear' ? 'Nuevo Huésped' : vista === 'ficha' ? 'Ficha del Huésped' : 'Editar Huésped'}
  subtitle={modo === 'crear' ? 'Registro de huésped' : vista === 'ficha' ? nombreCompleto : `${data?.nombre ?? ''} ${data?.apellido ?? ''}`}
  onclose={onclose}
>
  <!-- El contenido interior ya no tiene overflow propio, lo maneja ModalShell -->
  <div class="p-6 space-y-6">
    {#if errores.general}
      <div class="p-3 bg-hotel-error/10 border border-hotel-error/20 rounded-lg text-hotel-error-light text-sm flex items-center gap-2">
        <Icon name="alert" class="w-4 h-4" />
        {errores.general}
      </div>
    {/if}

    {#if vista === 'ficha' && data}
      <!-- ========== VISTA FICHA (detalle) ========== -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Columna izquierda -->
        <div class="space-y-4">
          <!-- Información básica -->
          <div class="bg-hotel-bg/40 rounded-xl border border-hotel-border p-4">
            <h4 class="text-[10px] font-black uppercase tracking-widest text-hotel-gold-light mb-3 flex items-center gap-2">
              <Icon name="user" class="w-4 h-4" />
              Identidad
            </h4>
            <div class="space-y-2 text-sm">
              <p><span class="text-hotel-text-tertiary">Nombre completo:</span> <span class="font-medium">{nombreCompleto}</span></p>
              <p><span class="text-hotel-text-tertiary">Documento:</span> <span class="font-mono">{documentoFormateado}</span></p>
              <p><span class="text-hotel-text-tertiary">Edad:</span> {form.edad ?? '—'} años</p>
              <p><span class="text-hotel-text-tertiary">Fecha nac.:</span> {form.fecha_nacimiento || '—'}</p>
              <p><span class="text-hotel-text-tertiary">Nacionalidad:</span> {form.nacionalidad || '—'}</p>
              <p><span class="text-hotel-text-tertiary">Estado civil:</span> {ESTADO_CIVIL.find(ec => ec.value === form.estado_civil)?.label || form.estado_civil || '—'}</p>
            </div>
          </div>

          <!-- Contacto -->
          <div class="bg-hotel-bg/40 rounded-xl border border-hotel-border p-4">
            <h4 class="text-[10px] font-black uppercase tracking-widest text-hotel-gold-light mb-3 flex items-center gap-2">
              <Icon name="smartphone" class="w-4 h-4" />
              Contacto
            </h4>
            <div class="space-y-2 text-sm">
              <p><span class="text-hotel-text-tertiary">Teléfono principal:</span> {form.telefono || '—'}</p>
              <p><span class="text-hotel-text-tertiary">Teléfono contacto:</span> {form.telefono_contacto || '—'}</p>
              <p><span class="text-hotel-text-tertiary">Email:</span> {form.email || '—'}</p>
              <p><span class="text-hotel-text-tertiary">Procedencia:</span> {form.procedencia || '—'}</p>
            </div>
          </div>
        </div>

        <!-- Columna derecha -->
        <div class="space-y-4">
          <!-- Profesión -->
          <div class="bg-hotel-bg/40 rounded-xl border border-hotel-border p-4">
            <h4 class="text-[10px] font-black uppercase tracking-widest text-hotel-gold-light mb-3 flex items-center gap-2">
              <Icon name="briefcase" class="w-4 h-4" />
              Perfil Profesional
            </h4>
            <div class="space-y-2 text-sm">
              <p><span class="text-hotel-text-tertiary">Categoría:</span> 
                {form.profesion === 'otro' ? 'Otro' : form.profesion || '—'}
              </p>
              {#if form.profesion === 'otro' && form.profesion_otro}
                <p><span class="text-hotel-text-tertiary">Especificación:</span> {form.profesion_otro}</p>
              {/if}
            </div>
          </div>

          <!-- Acompañantes -->
          <div class="bg-hotel-bg/40 rounded-xl border border-hotel-border p-4">
            <h4 class="text-[10px] font-black uppercase tracking-widest text-hotel-gold-light mb-3 flex items-center gap-2">
              <Icon name="group" class="w-4 h-4" />
              Acompañantes ({form.acompanantes.length})
            </h4>
            {#if form.acompanantes.length === 0}
              <p class="text-sm text-hotel-text-tertiary italic">No registrados</p>
            {:else}
              <ul class="space-y-2 text-sm">
                {#each form.acompanantes as acomp}
                  <li class="flex justify-between border-b border-hotel-border/30 pb-1 last:border-0">
                    <span>{acomp.nombre || '—'}</span>
                    <span class="text-hotel-text-tertiary">{acomp.documento || '—'}</span>
                  </li>
                {/each}
              </ul>
            {/if}
          </div>

          <!-- Observaciones -->
          {#if form.notas}
            <div class="bg-hotel-bg/40 rounded-xl border border-hotel-border p-4">
              <h4 class="text-[10px] font-black uppercase tracking-widest text-hotel-gold-light mb-2 flex items-center gap-2">
                <Icon name="note" class="w-4 h-4" />
                Notas
              </h4>
              <p class="text-sm text-hotel-text-secondary italic whitespace-pre-wrap">{form.notas}</p>
            </div>
          {/if}
        </div>
      </div>

      <footer class="flex justify-end gap-4 pt-4 border-t border-hotel-border/50 mt-4">
        <Button variant="gold" onclick={() => vista = 'formulario'} icon="edit">
          Editar datos
        </Button>
      </footer>

    {:else}
      <!-- ========== FORMULARIO (creación y edición) ========== -->
      <!-- Identificación Legal -->
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

      <!-- Datos Personales -->
      <section class="space-y-4">
        <h3 class="text-[10px] font-black uppercase tracking-widest text-hotel-gold-light border-b border-hotel-gold/20 pb-2">Datos Personales</h3>
        <div class="grid grid-cols-2 gap-4">
          <InputHotel label="Nombre" bind:value={form.nombre} error={errores.nombre} required />
          <InputHotel label="Apellido" bind:value={form.apellido} error={errores.apellido} required />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <InputHotel label="Edad" type="number" bind:value={form.edad} error={errores.edad} />
          <InputHotel label="Fecha de nacimiento" type="date" bind:value={form.fecha_nacimiento} />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <InputHotel label="Nacionalidad" bind:value={form.nacionalidad} placeholder="Venezolana" />
          <div class="space-y-1">
            <label for="estado_civil" class="text-[10px] font-bold text-hotel-text-tertiary uppercase">Estado civil</label>
            <select id="estado_civil" bind:value={form.estado_civil} class="input-hotel">
              <option value="">Seleccionar</option>
              {#each ESTADO_CIVIL as ec}<option value={ec.value}>{ec.label}</option>{/each}
            </select>
          </div>
        </div>
      </section>

      <!-- Contacto y Procedencia -->
      <section class="space-y-4">
        <h3 class="text-[10px] font-black uppercase tracking-widest text-hotel-gold-light border-b border-hotel-gold/20 pb-2">Contacto y Procedencia</h3>
        <div class="grid grid-cols-2 gap-4">
          <InputHotel label="Teléfono principal" bind:value={form.telefono} />
          <InputHotel label="Teléfono de contacto" bind:value={form.telefono_contacto} />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <InputHotel label="Email" type="email" bind:value={form.email} error={errores.email} />
          <InputHotel label="Procedencia" bind:value={form.procedencia} placeholder="Ciudad, País" />
        </div>

        <!-- Profesión con selector -->
        <div class="space-y-2">
          <label class="text-[10px] font-black uppercase tracking-widest text-hotel-text-tertiary">Profesión / Tipo de Cliente</label>
          <select bind:value={form.profesion} class="input-hotel">
            <option value="">Seleccionar</option>
            <option value="particular">Particular</option>
            <option value="militar">Militar / GN</option>
            <option value="politico">Político / Gov.</option>
            <option value="artista">Artista / Medios</option>
            <option value="empresarial">Empresarial</option>
            <option value="deportista">Deportista</option>
            <option value="diplomatico">Diplomático</option>
            <option value="medico">Médico</option>
            <option value="religioso">Religioso</option>
            <option value="turista">Turista / Agencia</option>
            <option value="ejecutivo_ventas">Ejecutivo de Ventas</option>
            <option value="comerciante">Comerciante</option>
            <option value="otro">Otro (especificar)</option>
          </select>
        </div>

        {#if form.profesion === 'otro'}
          <InputHotel label="Especificar profesión" bind:value={form.profesion_otro} placeholder="Ej: Ingeniero, Abogado..." error={errores.profesion_otro} />
        {/if}
      </section>

      <!-- Acompañantes -->
      <section class="space-y-4">
        <div class="flex items-center justify-between border-b border-hotel-gold/20 pb-2">
          <h3 class="text-[10px] font-black uppercase tracking-widest text-hotel-gold-light">Acompañantes ({form.acompanantes.length})</h3>
          <button onclick={agregarAcompanante} class="text-[10px] font-black text-hotel-gold hover:text-hotel-gold-light transition-all flex items-center gap-1 uppercase">
            <Icon name="plus" class="w-3.5 h-3.5" />
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
                <Icon name="close" class="w-4 h-4" />
              </button>
            </div>
          {/each}
        </div>
      </section>

      <!-- Observaciones VIP -->
      <section class="space-y-4">
        <h3 class="text-[10px] font-black uppercase tracking-widest text-hotel-gold-light border-b border-hotel-gold/20 pb-2">Observaciones</h3>
        <textarea
          bind:value={form.notas}
          rows="2"
          class="input-hotel resize-none h-20 py-3"
          placeholder="Preferencias, alergias, necesidades especiales..."
        ></textarea>
      </section>
    {/if}
  </div>

  <!-- Footer con acciones (solo cuando se muestra el formulario) -->
  {#if vista === 'formulario' || modo === 'crear'}
    <footer class="p-6 border-t border-hotel-border bg-hotel-bg/50 flex justify-between items-center">
      <button onclick={onclose} class="text-xs font-bold text-hotel-text-tertiary uppercase tracking-widest hover:text-hotel-text-secondary transition-colors">
        Cancelar
      </button>
      <Button variant="gold" onclick={handleGuardar} disabled={guardando}>
        {#if guardando}
          <div class="w-4 h-4 border-2 border-hotel-bg/30 border-t-hotel-bg rounded-full animate-spin"></div>
          Procesando...
        {:else}
          {modo === 'crear' ? 'Registrar Huésped' : 'Guardar Cambios'}
        {/if}
      </Button>
    </footer>
  {/if}
</ModalShell>