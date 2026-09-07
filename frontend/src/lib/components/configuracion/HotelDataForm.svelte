<script lang="ts">
    import { toast } from '$lib/stores/toast';
    import InputHotel from '$components/ui/Input.svelte';
    import Button from '$components/ui/Button.svelte';
    import { saveConfiguracion } from '$lib/services/configuracion';
    import type { ConfiguracionGeneral } from '$lib/types/configuracion';

    let {
        config,
        onsave,
    }: {
        config: ConfiguracionGeneral;
        onsave: () => void;
    } = $props();

    let loading = $state(false);

    // svelte-ignore state_referenced_locally
    let nombre = $state(config.nombre_hotel || '');
    // svelte-ignore state_referenced_locally
    let rif = $state(config.rif || '');
    // svelte-ignore state_referenced_locally
    let direccion = $state(config.direccion || '');
    // svelte-ignore state_referenced_locally
    let telefono = $state(config.telefono || '');
    // svelte-ignore state_referenced_locally
    let telefono2 = $state(config.telefono_2 || '');
    // svelte-ignore state_referenced_locally
    let email = $state(config.email || '');
    // svelte-ignore state_referenced_locally
    let logo = $state(config.logo || '');

    async function guardar() {
        loading = true;
        try {
            await saveConfiguracion({
                nombre_hotel: nombre,
                rif,
                direccion,
                telefono,
                telefono_2: telefono2,
                email,
                logo,
            });
            toast.success('Datos del hotel actualizados.');
            onsave();
        } catch (e: any) {
            toast.error(e.message);
        } finally {
            loading = false;
        }
    }
</script>

<div class="space-y-4">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <InputHotel label="Nombre del Hotel" bind:value={nombre} placeholder="Salma Suite VIP" />
        <InputHotel label="RIF" bind:value={rif} placeholder="J-12345678-9" />
    </div>
    <InputHotel label="Dirección Fiscal" bind:value={direccion} placeholder="Av. Principal, Zona Hotelera, Caracas" />
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <InputHotel label="Teléfono Principal" bind:value={telefono} placeholder="0212-5551234" />
        <InputHotel label="Teléfono Secundario" bind:value={telefono2} placeholder="0412-5555678" />
    </div>
    <InputHotel label="Email de Contacto" bind:value={email} placeholder="info@salmasuite.com" />
    <InputHotel label="URL del Logo" bind:value={logo} placeholder="/media/logo.png" />

    <div class="pt-4 border-t border-hotel-border/50">
        <Button variant="gold" onclick={guardar} loading={loading}>Guardar Datos del Hotel</Button>
    </div>
</div>