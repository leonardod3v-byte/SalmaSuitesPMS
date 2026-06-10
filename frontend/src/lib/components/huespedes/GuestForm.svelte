<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { toast } from '$lib/stores/toast';
    import InputHotel from '$components/ui/Input.svelte';
    import Select from '$components/ui/Select.svelte';
    import DatePicker from '$components/ui/DatePicker.svelte';
    import Textarea from '$components/ui/Textarea.svelte';
    import Button from '$components/ui/Button.svelte';
    import VIPToggle from './VIPToggle.svelte';
    import { createHuesped, updateHuesped, fetchHuesped } from '$lib/services/huespedes';
    import type { Huesped } from '$lib/types/huesped';

    let {
        id = null,
        onclose = () => {},
    }: {
        id?: number | null;
        onclose?: () => void;
    } = $props();

    let loading = $state(false);
    let error = $state('');

    // Campos del formulario
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
    let procedencia = $state('');
    let tipo_cliente_profesion = $state('Particular');
    let categoria = $state('Estándar');
    let credito_autorizado = $state(false);
    let limite_credito = $state<number | ''>('');
    let observaciones = $state('');

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

    const tiposCliente = [
        { value: 'Particular', label: 'Particular' },
        { value: 'Empresario', label: 'Empresario' },
        { value: 'Turista', label: 'Turista' },
        { value: 'Militar', label: 'Militar' },
        { value: 'Político', label: 'Político' },
        { value: 'Artista', label: 'Artista' },
        { value: 'Deportista', label: 'Deportista' },
        { value: 'Diplomático', label: 'Diplomático' },
        { value: 'Médico', label: 'Médico' },
        { value: 'Religioso', label: 'Religioso' },
        { value: 'Ejecutivo de Ventas', label: 'Ejecutivo de Ventas' },
        { value: 'Comerciante', label: 'Comerciante' },
    ];

    function calcularEdad(fecha: string): number {
        if (!fecha) return 0;
        const hoy = new Date();
        const nac = new Date(fecha);
        let edadCalc = hoy.getFullYear() - nac.getFullYear();
        const mes = hoy.getMonth() - nac.getMonth();
        if (mes < 0 || (mes === 0 && hoy.getDate() < nac.getDate())) {
            edadCalc--;
        }
        return edadCalc;
    }

    function handleFechaChange() {
        if (fecha_nacimiento) {
            edad = calcularEdad(fecha_nacimiento);
        }
    }

    $effect(() => {
        if (fecha_nacimiento) {
            edad = calcularEdad(fecha_nacimiento);
        }
    });

    onMount(async () => {
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
                procedencia = data.procedencia;
                tipo_cliente_profesion = data.tipo_cliente_profesion;
                categoria = data.categoria;
                credito_autorizado = data.credito_autorizado;
                limite_credito = data.limite_credito ?? '';
                observaciones = data.observaciones || '';
            } catch (e: any) {
                error = e.message || 'Error al cargar huésped';
            }
        }
    });

    async function handleSubmit(e: Event) {
        e.preventDefault();
        error = '';
        loading = true;

        const payload = {
            tipo_documento,
            numero_documento,
            nombres,
            apellidos,
            fecha_nacimiento,
            edad: edad || calcularEdad(fecha_nacimiento),
            nacionalidad,
            estado_civil,
            telefono,
            email,
            procedencia,
            tipo_cliente_profesion,
            categoria,
            credito_autorizado,
            limite_credito: limite_credito || null,
            observaciones,
        };

        try {
            if (id) {
                await updateHuesped(id, payload);
                toast.success('Huésped actualizado correctamente.');
            } else {
                await createHuesped(payload as any);
                toast.success('Huésped registrado correctamente.');
            }
            onclose();
            setTimeout(() => {
                goto('/huespedes', { invalidateAll: true });
            }, 800);
        } catch (e: any) {
            error = e.message || 'Error al guardar';
            toast.error(e.message || 'Error al guardar el huésped.');
        } finally {
            loading = false;
        }
    }
</script>

<form onsubmit={handleSubmit} class="space-y-6">
    {#if error}
        <div class="flex items-center gap-2 p-3 rounded-xl bg-hotel-error/10 border border-hotel-error/20 text-hotel-error-light text-sm">
            <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            {error}
        </div>
    {/if}

    <!-- Documento -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div class="sm:col-span-1">
            <Select label="Tipo Doc." options={tiposDocumento} bind:value={tipo_documento} required />
        </div>
        <div class="sm:col-span-2">
            <InputHotel label="Número de Documento" bind:value={numero_documento} required placeholder="Ej: 12345678" />
        </div>
    </div>

    <!-- Nombres -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <InputHotel label="Nombres" bind:value={nombres} required placeholder="Ej: Carlos Andrés" />
        <InputHotel label="Apellidos" bind:value={apellidos} required placeholder="Ej: González Pérez" />
    </div>

    <!-- Nacimiento y edad -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div class="sm:col-span-2">
            <DatePicker label="Fecha de Nacimiento" bind:value={fecha_nacimiento} required />
        </div>
        <div class="sm:col-span-1">
            <InputHotel label="Edad" type="number" bind:value={edad} placeholder="Auto" />
        </div>
    </div>

    <!-- Nacionalidad y Estado Civil -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <InputHotel label="Nacionalidad" bind:value={nacionalidad} required placeholder="Ej: Venezolana" />
        <Select label="Estado Civil" options={estadosCiviles} bind:value={estado_civil} required />
    </div>

    <!-- Contacto -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <InputHotel label="Teléfono" bind:value={telefono} required placeholder="Ej: 0412-1234567" />
        <InputHotel label="Email" type="email" bind:value={email} placeholder="ejemplo@correo.com" />
    </div>

    <!-- Procedencia y Tipo Cliente -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <InputHotel label="Procedencia" bind:value={procedencia} required placeholder="Ej: Caracas" />
        <Select label="Tipo de Cliente / Profesión" options={tiposCliente} bind:value={tipo_cliente_profesion} required />
    </div>

    <!-- Categoría VIP -->
    <div class="flex items-center justify-between p-4 rounded-xl bg-hotel-bg/50 border border-hotel-border">
        <div>
            <p class="text-sm font-bold text-hotel-text-primary">Categoría del huésped</p>
            <p class="text-[10px] text-hotel-text-tertiary uppercase tracking-wider">Define si es VIP o Estándar</p>
        </div>
        <VIPToggle bind:categoria />
    </div>

    <!-- Crédito -->
    <div class="p-4 rounded-xl bg-hotel-bg/50 border border-hotel-border space-y-4">
        <label class="flex items-center gap-3 cursor-pointer">
            <input type="checkbox" bind:checked={credito_autorizado} class="w-4 h-4 rounded border-hotel-border bg-hotel-bg text-hotel-gold focus:ring-hotel-gold" />
            <span class="text-sm font-bold text-hotel-text-primary">Crédito autorizado</span>
        </label>
        {#if credito_autorizado}
            <InputHotel label="Límite de crédito ($)" type="number" bind:value={limite_credito} placeholder="Ej: 500.00" />
        {/if}
    </div>

    <!-- Observaciones -->
    <Textarea label="Observaciones" bind:value={observaciones} placeholder="Notas adicionales sobre el huésped..." />

    <!-- Botones -->
    <div class="flex gap-3 pt-4 border-t border-hotel-border/50">
        <Button type="submit" variant="gold" loading={loading}>
            {id ? 'Actualizar Huésped' : 'Registrar Huésped'}
        </Button>
        <Button type="button" variant="ghost" onclick={onclose}>Cancelar</Button>
    </div>
</form>