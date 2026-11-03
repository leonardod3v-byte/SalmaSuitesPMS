<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { toast } from '$lib/stores/toast';
    import InputHotel from '$components/ui/Input.svelte';
    import Select from '$components/ui/Select.svelte';
    import DatePicker from '$components/ui/DatePicker.svelte';
    import Button from '$components/ui/Button.svelte';
    import VIPToggle from './VIPToggle.svelte';
    import { createHuesped, updateHuesped, fetchHuesped } from '$lib/services/huespedes';
    import { fetchOcupaciones, type Ocupacion } from '$lib/services/ocupaciones';

    let {
        id = null,
        onclose = () => {},
    }: {
        id?: number | null;
        onclose?: () => void;
    } = $props();

    let loading = $state(false);
    let error = $state('');
    let ocupaciones = $state<Ocupacion[]>([]);

    // Campos
    let tipo_documento = $state('V');
    let numero_documento = $state('');
    let nombres = $state('');
    let apellidos = $state('');
    let fecha_nacimiento = $state('');
    let edad = $state<number | ''>('');
    let nacionalidad = $state('Venezolana');
    let estado_civil = $state('Soltero');
    let telefono = $state('');
    let email = $state('');
    let direccion = $state('');
    let ocupacion_id = $state<number | ''>('');
    let alergias = $state('');
    let medio_transporte = $state('');
    let categoria = $state('Estándar');
    let credito_autorizado = $state(false);
    let limite_credito = $state<number | ''>('');

    const tiposDocumento = [
        { value: 'V', label: 'V - Venezolano' },
        { value: 'E', label: 'E - Extranjero' },
        { value: 'J', label: 'J - Jurídico' },
        { value: 'P', label: 'P - Pasaporte' },
    ];

    const estadosCiviles = [
        { value: 'Soltero', label: 'Soltero' }, { value: 'Casado', label: 'Casado' },
        { value: 'Divorciado', label: 'Divorciado' }, { value: 'Viudo', label: 'Viudo' },
        { value: 'Concubino', label: 'Concubino' },
    ];

    const mediosTransporte = [
        { value: '', label: 'Seleccione...' },
        { value: 'Propio', label: 'Propio' },
        { value: 'Aéreo', label: 'Aéreo' },
        { value: 'Terrestre', label: 'Terrestre' },
        { value: 'Marítimo', label: 'Marítimo' },
        { value: 'Taxi', label: 'Taxi' },
        { value: 'Autobús', label: 'Autobús' },
        { value: 'Otro', label: 'Otro' },
    ];

    function calcularEdad(fecha: string): number {
        if (!fecha) return 0;
        const hoy = new Date();
        const nac = new Date(fecha);
        let edadCalc = hoy.getFullYear() - nac.getFullYear();
        const mes = hoy.getMonth() - nac.getMonth();
        if (mes < 0 || (mes === 0 && hoy.getDate() < nac.getDate())) edadCalc--;
        return edadCalc;
    }

    $effect(() => { if (fecha_nacimiento) edad = calcularEdad(fecha_nacimiento); });

    onMount(async () => {
        try { ocupaciones = await fetchOcupaciones(); } catch { }
        if (id) {
            try {
                const data = await fetchHuesped(id);
                tipo_documento = data.tipo_documento;
                numero_documento = data.numero_documento;
                nombres = data.nombres;
                apellidos = data.apellidos;
                fecha_nacimiento = data.fecha_nacimiento;
                edad = data.edad;
                nacionalidad = data.nacionalidad;
                estado_civil = data.estado_civil;
                telefono = data.telefono;
                email = data.email;
                direccion = data.direccion || '';
                ocupacion_id = data.ocupacion || '';
                alergias = data.alergias || '';
                medio_transporte = data.medio_transporte || '';
                categoria = data.categoria;
                credito_autorizado = data.credito_autorizado;
                limite_credito = data.limite_credito ?? '';
            } catch (e: any) {
                error = e.message || 'Error al cargar huésped';
            }
        }
    });

    async function handleSubmit(e: Event) {
        e.preventDefault();
        error = '';
        if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            error = 'Ingresa un correo electrónico válido.';
            return;
        }
        loading = true;
        const payload = {
            tipo_documento, numero_documento, nombres, apellidos, fecha_nacimiento,
            edad: edad || calcularEdad(fecha_nacimiento), nacionalidad, estado_civil,
            telefono, email, direccion, ocupacion: ocupacion_id || null, alergias,
            medio_transporte: medio_transporte || null,
            categoria, credito_autorizado, limite_credito: limite_credito || null,
        };
        try {
            if (id) { await updateHuesped(id, payload); toast.success('Huésped actualizado.'); }
            else { await createHuesped(payload as any); toast.success('Huésped registrado.'); }
            onclose();
            setTimeout(() => goto('/huespedes', { invalidateAll: true }), 800);
        } catch (e: any) {
            error = e.message || 'Error al guardar';
        } finally { loading = false; }
    }
</script>

<form onsubmit={handleSubmit} class="space-y-6">
    {#if error}
        <div class="p-3 rounded-xl bg-hotel-error/10 border border-hotel-error/20 text-hotel-error-light text-sm">{error}</div>
    {/if}

    <!-- SECCIÓN: DATOS PERSONALES -->
    <div class="p-4 rounded-xl bg-hotel-bg/40 border border-hotel-border space-y-4">
        <p class="text-[10px] font-black uppercase tracking-wider text-hotel-gold">Datos Personales</p>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Select label="Tipo Doc." options={tiposDocumento} bind:value={tipo_documento} required />
            <div class="sm:col-span-2"><InputHotel label="Número de Documento" bind:value={numero_documento} required placeholder="Ej: 12345678" /></div>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <InputHotel label="Nombres" bind:value={nombres} required placeholder="Ej: Carlos Andrés" />
            <InputHotel label="Apellidos" bind:value={apellidos} required placeholder="Ej: González Pérez" />
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="sm:col-span-2"><DatePicker label="Fecha de Nacimiento" bind:value={fecha_nacimiento} required /></div>
            <InputHotel label="Edad" type="number" bind:value={edad} readonly class="bg-hotel-border/20 cursor-not-allowed" />
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <InputHotel label="Nacionalidad" bind:value={nacionalidad} required />
            <Select label="Estado Civil" options={estadosCiviles} bind:value={estado_civil} required />
        </div>
    </div>

    <!-- SECCIÓN: CONTACTO -->
    <div class="p-4 rounded-xl bg-hotel-bg/40 border border-hotel-border space-y-4">
        <p class="text-[10px] font-black uppercase tracking-wider text-hotel-gold">Contacto y Ubicación</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <InputHotel label="Teléfono" bind:value={telefono} required placeholder="Ej: 0412-1234567" />
            <InputHotel label="Email" type="email" bind:value={email} placeholder="ejemplo@correo.com" />
        </div>
        <InputHotel label="Dirección" bind:value={direccion} placeholder="Ej: Av. Principal, Edificio..." />
        <Select label="Medio de Transporte" options={mediosTransporte} bind:value={medio_transporte} />
    </div>

    <!-- SECCIÓN: PERFIL Y SALUD -->
    <div class="p-4 rounded-xl bg-hotel-bg/40 border border-hotel-border space-y-4">
        <p class="text-[10px] font-black uppercase tracking-wider text-hotel-gold">Perfil y Salud</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Select
                label="Ocupación"
                options={[{value: '', label: 'Seleccione...'}, ...ocupaciones.map(o => ({value: String(o.id), label: o.nombre}))]}
                bind:value={ocupacion_id}
            />
            <InputHotel label="Alergias" bind:value={alergias} placeholder="Ej: Penicilina" />
        </div>
    </div>

    <!-- SECCIÓN: CATEGORÍA Y CRÉDITO -->
    <div class="p-4 rounded-xl bg-hotel-bg/40 border border-hotel-border space-y-4">
        <p class="text-[10px] font-black uppercase tracking-wider text-hotel-gold">Categoría y Crédito</p>
        <div class="flex items-center justify-between p-3 rounded-lg bg-hotel-surface border border-hotel-border">
            <div>
                <p class="text-sm font-bold text-hotel-text-primary">Categoría VIP</p>
                <p class="text-[10px] text-hotel-text-tertiary">Define si es VIP o Estándar</p>
            </div>
            <VIPToggle bind:categoria />
        </div>
        <label class="flex items-center gap-3 cursor-pointer">
            <input type="checkbox" bind:checked={credito_autorizado} class="w-4 h-4 rounded border-hotel-border bg-hotel-bg text-hotel-gold focus:ring-hotel-gold" />
            <span class="text-sm font-bold text-hotel-text-primary">Crédito autorizado</span>
        </label>
        {#if credito_autorizado}
            <InputHotel label="Límite de crédito ($)" type="number" bind:value={limite_credito} placeholder="Ej: 500.00" />
        {/if}
    </div>

    <div class="flex gap-3 pt-4 border-t border-hotel-border/50">
        <Button type="submit" variant="gold" loading={loading}>{id ? 'Actualizar Huésped' : 'Registrar Huésped'}</Button>
        <Button type="button" variant="ghost" onclick={onclose}>Cancelar</Button>
    </div>
</form>
