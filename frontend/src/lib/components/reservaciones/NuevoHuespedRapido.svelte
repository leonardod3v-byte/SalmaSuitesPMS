<script lang="ts">
    import { toast } from '$lib/stores/toast';
    import InputHotel from '$components/ui/Input.svelte';
    import Select from '$components/ui/Select.svelte';
    import DatePicker from '$components/ui/DatePicker.svelte';
    import Button from '$components/ui/Button.svelte';
    import { createHuesped } from '$lib/services/huespedes';
    import type { Huesped } from '$lib/types/huesped';
    import type { Ocupacion } from '$lib/services/ocupaciones';

    let {
        ocupaciones = [],
        oncreado = () => {},
        oncancel = () => {},
    }: {
        ocupaciones?: Ocupacion[];
        oncreado?: (h: Huesped) => void;
        oncancel?: () => void;
    } = $props();

    let loading = $state(false);
    let error = $state('');

    let tipo_documento = $state('V');
    let numero_documento = $state('');
    let nombres = $state('');
    let apellidos = $state('');
    let fecha_nacimiento = $state('');
    let nacionalidad = $state('Venezolana');
    let estado_civil = $state('Soltero');
    let telefono = $state('');
    let email = $state('');
    let direccion = $state('');
    let ocupacion_id = $state<number | ''>('');
    let alergias = $state('');
    let medio_transporte = $state('');

    const tiposDocumento = [
        { value: 'V', label: 'V - Venezolano' },
        { value: 'E', label: 'E - Extranjero' },
        { value: 'J', label: 'J - Jurídico' },
        { value: 'P', label: 'P - Pasaporte' },
    ];

    const estadosCiviles = [
        { value: 'Soltero', label: 'Soltero' },
        { value: 'Casado', label: 'Casado' },
        { value: 'Divorciado', label: 'Divorciado' },
        { value: 'Viudo', label: 'Viudo' },
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

    async function guardar(e: Event) {
        e.preventDefault();
        error = '';
        if (!nombres.trim() || !apellidos.trim() || !numero_documento.trim() || !fecha_nacimiento) {
            error = 'Complete los campos obligatorios.';
            return;
        }
        loading = true;
        try {
            const payload = {
                tipo_documento,
                numero_documento,
                nombres,
                apellidos,
                fecha_nacimiento,
                nacionalidad,
                estado_civil,
                telefono,
                email,
                direccion,
                ocupacion: ocupacion_id || null,
                alergias,
                medio_transporte: medio_transporte || null,
                categoria: 'Estándar',
                credito_autorizado: false,
            };
            const nuevo = await createHuesped(payload as any);
            oncreado(nuevo);
        } catch (e: any) {
            error = e.message || 'Error al crear huésped';
        } finally {
            loading = false;
        }
    }
</script>

<form onsubmit={guardar} class="space-y-4">
    {#if error}
        <div class="p-3 rounded-xl bg-hotel-error/10 border border-hotel-error/20 text-hotel-error-light text-sm">{error}</div>
    {/if}

    <div class="grid grid-cols-3 gap-3">
        <Select label="Tipo Doc." options={tiposDocumento} bind:value={tipo_documento} required />
        <div class="col-span-2"><InputHotel label="Número" bind:value={numero_documento} required placeholder="Ej: 12345678" /></div>
    </div>

    <div class="grid grid-cols-2 gap-3">
        <InputHotel label="Nombres" bind:value={nombres} required />
        <InputHotel label="Apellidos" bind:value={apellidos} required />
    </div>

    <div class="grid grid-cols-2 gap-3">
        <DatePicker label="Fecha de Nacimiento" bind:value={fecha_nacimiento} required />
        <InputHotel label="Nacionalidad" bind:value={nacionalidad} required />
    </div>

    <div class="grid grid-cols-2 gap-3">
        <Select label="Estado Civil" options={estadosCiviles} bind:value={estado_civil} required />
        <InputHotel label="Teléfono" bind:value={telefono} placeholder="Ej: 0412-1234567" />
    </div>

    <div class="grid grid-cols-2 gap-3">
        <InputHotel label="Email" type="email" bind:value={email} placeholder="correo@ejemplo.com" />
        <InputHotel label="Dirección" bind:value={direccion} placeholder="Av. Principal, Edificio..." />
    </div>

    <div class="grid grid-cols-2 gap-3">
        <Select
            label="Ocupación"
            options={[{value: '', label: 'Seleccione...'}, ...ocupaciones.map(o => ({value: String(o.id), label: o.nombre}))]}
            bind:value={ocupacion_id}
        />
        <InputHotel label="Alergias" bind:value={alergias} placeholder="Ej: Penicilina" />
    </div>

    <Select label="Medio de Transporte" options={mediosTransporte} bind:value={medio_transporte} />

    <div class="flex gap-3 pt-2">
        <Button type="submit" variant="gold" loading={loading} fullWidth>Guardar y agregar</Button>
        <Button type="button" variant="ghost" onclick={oncancel}>Cancelar</Button>
    </div>
</form>
