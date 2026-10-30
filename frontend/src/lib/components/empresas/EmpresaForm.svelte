<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { toast } from '$lib/stores/toast';
    import InputHotel from '$components/ui/Input.svelte';
    import Textarea from '$components/ui/Textarea.svelte';
    import Button from '$components/ui/Button.svelte';
    import { createEmpresa, updateEmpresa, fetchEmpresa } from '$lib/services/empresas';
    import type { Empresa } from '$lib/types/empresa';

    let {
        id = null,
        onclose = () => {},
    }: {
        id?: number | null;
        onclose?: () => void;
    } = $props();

    let loading = $state(false);
    let error = $state('');

    let nombre = $state('');
    let rif = $state('');
    let direccion_fiscal = $state('');
    let telefono = $state('');
    let email = $state('');

    onMount(async () => {
        if (id) {
            try {
                const data = await fetchEmpresa(id);
                nombre = data.nombre;
                rif = data.rif;
                direccion_fiscal = data.direccion_fiscal;
                telefono = data.telefono;
                email = data.email;
            } catch (e: any) {
                error = e.message || 'Error al cargar empresa';
            }
        }
    });

    async function handleSubmit(e: Event) {
        e.preventDefault();
        error = '';
        loading = true;

        const payload = {
            nombre,
            rif,
            direccion_fiscal,
            telefono,
            email,
        };

        try {
            if (id) {
                await updateEmpresa(id, payload);
                toast.success('Empresa actualizada correctamente.');
            } else {
                await createEmpresa(payload);
                toast.success('Empresa registrada correctamente.');
            }
            onclose();
            setTimeout(() => goto('/empresas', { invalidateAll: true }), 800);
        } catch (e: any) {
            error = e.message || 'Error al guardar';
            toast.error(e.message || 'Error al guardar la empresa.');
        } finally {
            loading = false;
        }
    }
</script>

<form onsubmit={handleSubmit} class="space-y-6">
    {#if error}
        <div class="flex items-center gap-2 p-3 rounded-xl bg-hotel-error/10 border border-hotel-error/20 text-hotel-error-light text-sm">
            {error}
        </div>
    {/if}

    <div class="p-5 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
        <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Información de la Empresa</p>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <InputHotel label="Nombre o Razón Social" bind:value={nombre} required placeholder="Ej: Inversiones ABC, C.A." />
            <InputHotel label="RIF" bind:value={rif} required placeholder="Ej: J-12345678-9" />
        </div>

        <Textarea label="Dirección Fiscal" bind:value={direccion_fiscal} required placeholder="Av. Principal, Edificio..." rows={2} />

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <InputHotel label="Teléfono" bind:value={telefono} placeholder="0212-5551234" />
            <InputHotel label="Email" type="email" bind:value={email} placeholder="contacto@empresa.com" />
        </div>
    </div>

    <div class="flex gap-3 pt-4 border-t border-hotel-border/50">
        <Button type="submit" variant="gold" loading={loading}>
            {id ? 'Actualizar Empresa' : 'Registrar Empresa'}
        </Button>
        <Button type="button" variant="ghost" onclick={onclose}>Cancelar</Button>
    </div>
</form>
