<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { toast } from '$lib/stores/toast';
    import InputHotel from '$components/ui/Input.svelte';
    import Textarea from '$components/ui/Textarea.svelte';
    import Button from '$components/ui/Button.svelte';
    import { createEmpresa, updateEmpresa, fetchEmpresa } from '$lib/services/empresas';

    let { id = null, onclose = () => {} }: { id?: number | null; onclose?: () => void } = $props();
    let loading = $state(false);
    let error = $state('');
    let nombre = $state('');
    let rif = $state('');
    let direccion_fiscal = $state('');
    let telefono = $state('');
    let email = $state('');

    let errorNombre = $state('');
    let errorRif = $state('');
    let errorDireccion = $state('');
    let errorTelefono = $state('');
    let errorEmail = $state('');

    onMount(async () => {
        if (id) {
            try {
                const data = await fetchEmpresa(id);
                nombre = data.nombre;
                rif = data.rif;
                direccion_fiscal = data.direccion_fiscal;
                telefono = data.telefono;
                email = data.email;
            } catch (e: any) { error = e.message || 'Error al cargar empresa'; }
        }
    });

    async function handleSubmit(e: Event) {
        e.preventDefault();
        error = '';
        errorNombre = '';
        errorRif = '';
        errorDireccion = '';
        errorTelefono = '';
        errorEmail = '';

        if (!nombre.trim()) {
            errorNombre = 'El nombre es obligatorio.';
            return;
        }
        if (!/^[VEJPG]-\d{8}-\d$/.test(rif)) {
            errorRif = 'El formato del RIF debe ser J-12345678-9.';
            return;
        }
        if (!direccion_fiscal.trim() || direccion_fiscal.trim().length < 5) {
            errorDireccion = 'La dirección debe tener al menos 5 caracteres.';
            return;
        }
        if (telefono && !/^[\+]?[\d\s\-\(\)]{7,20}$/.test(telefono)) {
            errorTelefono = 'El teléfono solo puede contener números, espacios, guiones, paréntesis y +.';
            return;
        }
        if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            errorEmail = 'Ingresa un correo electrónico válido.';
            return;
        }

        loading = true;
        const payload = { nombre, rif, direccion_fiscal, telefono, email };
        try {
            if (id) { await updateEmpresa(id, payload); toast.success('Empresa actualizada.'); }
            else { await createEmpresa(payload); toast.success('Empresa registrada.'); }
            onclose();
            setTimeout(() => goto('/empresas', { invalidateAll: true }), 800);
        } catch (e: any) {
            const msg = e.message || 'Error al guardar';
            if (msg.toLowerCase().includes('rif')) errorRif = msg;
            else if (msg.toLowerCase().includes('correo') || msg.toLowerCase().includes('email')) errorEmail = msg;
            else if (msg.toLowerCase().includes('teléfono')) errorTelefono = msg;
            else if (msg.toLowerCase().includes('dirección')) errorDireccion = msg;
            else if (msg.toLowerCase().includes('nombre')) errorNombre = msg;
            else error = msg;
        } finally { loading = false; }
    }
</script>

<form onsubmit={handleSubmit} class="space-y-6">
    {#if error}
        <div class="p-3 rounded-xl bg-hotel-error/10 border border-hotel-error/20 text-hotel-error-light text-sm">{error}</div>
    {/if}

    <div class="p-4 rounded-xl bg-hotel-bg/40 border border-hotel-border space-y-4">
        <p class="text-[10px] font-black uppercase tracking-wider text-hotel-gold">Datos Fiscales</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <InputHotel label="Nombre o Razón Social" bind:value={nombre} required placeholder="Ej: Inversiones ABC, C.A." error={errorNombre} />
            <InputHotel label="RIF" bind:value={rif} required placeholder="Ej: J-12345678-9" error={errorRif} />
        </div>
        <Textarea label="Dirección Fiscal" bind:value={direccion_fiscal} required placeholder="Av. Principal, Edificio..." rows={2} error={errorDireccion} />
    </div>

    <div class="p-4 rounded-xl bg-hotel-bg/40 border border-hotel-border space-y-4">
        <p class="text-[10px] font-black uppercase tracking-wider text-hotel-gold">Contacto</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <InputHotel label="Teléfono" bind:value={telefono} placeholder="0212-5551234" error={errorTelefono} />
            <InputHotel label="Email" type="email" bind:value={email} placeholder="contacto@empresa.com" error={errorEmail} />
        </div>
    </div>

    <div class="flex gap-3 pt-4 border-t border-hotel-border/50">
        <Button type="submit" variant="gold" loading={loading}>{id ? 'Actualizar Empresa' : 'Registrar Empresa'}</Button>
        <Button type="button" variant="ghost" onclick={onclose}>Cancelar</Button>
    </div>
</form>
