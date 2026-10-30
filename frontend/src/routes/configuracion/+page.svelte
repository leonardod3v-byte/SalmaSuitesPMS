<script lang="ts">
    import { onMount } from 'svelte';
    import { toast } from '$lib/stores/toast';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Loading from '$components/ui/Loading.svelte';
    import InputHotel from '$components/ui/Input.svelte';
    import Select from '$components/ui/Select.svelte';
    import Button from '$components/ui/Button.svelte';
    import ColorConfig from '$components/configuracion/ColorConfig.svelte';
    import { fetchConfiguracion, saveConfiguracion } from '$lib/services/configuracion';
    import type { ConfiguracionGeneral } from '$lib/types/configuracion';

    let config = $state<ConfiguracionGeneral>({});
    let cargando = $state(true);
    let guardando = $state(false);
    let error = $state('');

    // Variables unificadas para el formulario
    let nombre = $state('');
    let rif = $state('');
    let direccion = $state('');
    let telefono = $state('');
    let email = $state('');
    let simbolo = $state('$');
    let posicion = $state('antes');
    let separadorMiles = $state(',');
    let separadorDecimal = $state('.');

    const posiciones = [
        { value: 'antes', label: 'Antes del número ($100)' },
        { value: 'despues', label: 'Después del número (100$)' },
    ];

    async function cargar() {
        cargando = true;
        try {
            config = await fetchConfiguracion();

            nombre = config.nombre_hotel || '';
            rif = config.rif || '';
            direccion = config.direccion || '';
            telefono = config.telefono || '';
            email = config.email || '';
            simbolo = config.simbolo_moneda || '$';
            posicion = config.posicion_simbolo || 'antes';
            separadorMiles = config.separador_miles || ',';
            separadorDecimal = config.separador_decimal || '.';

        } catch (e: any) {
            error = e.message;
        } finally {
            cargando = false;
        }
    }

    async function guardarTodo() {
        guardando = true;
        try {
            await saveConfiguracion({
                nombre_hotel: nombre,
                rif,
                direccion,
                telefono,
                email,
                simbolo_moneda: simbolo,
                posicion_simbolo: posicion,
                separador_miles: separadorMiles,
                separador_decimal: separadorDecimal,
            });
            toast.success('Configuración guardada correctamente.');
            await cargar();
        } catch (e: any) {
            toast.error(e.message || 'Error al guardar la configuración.');
        } finally {
            guardando = false;
        }
    }

    onMount(() => cargar());
</script>

<svelte:head>
    <title>Configuración | SalmaSuitesPMS</title>
</svelte:head>

<PageHeader title="Configuración" subtitle="Personaliza los datos del hotel y el sistema" />

{#if cargando}
    <Loading type="dashboard" message="Cargando configuración..." />
{:else if error}
    <div class="text-center p-8 bg-hotel-error/5 border border-hotel-error/20 rounded-2xl">
        <p class="text-hotel-error-light font-bold uppercase tracking-widest text-xs mb-4">{error}</p>
        <Button variant="gold" onclick={cargar}>Reintentar</Button>
    </div>
{:else}
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">

        <section class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm p-6 space-y-8 h-full">

            <div>
                <h3 class="font-display text-xl text-hotel-text-primary italic mb-1">Datos del Hotel</h3>
                <p class="text-xs text-hotel-text-tertiary mb-4">Información fiscal y de contacto que aparecerá en los reportes PDF.</p>

                <div class="space-y-4">
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <InputHotel label="Nombre del Hotel" bind:value={nombre} placeholder="Ej: Salma Suite VIP" />
                        <InputHotel label="RIF" bind:value={rif} placeholder="Ej: J-12345678-9" />
                    </div>
                    <InputHotel label="Dirección Fiscal" bind:value={direccion} placeholder="Av. Principal, Zona Hotelera..." />
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <InputHotel label="Teléfono Principal" bind:value={telefono} placeholder="0212-5551234" />
                        <InputHotel label="Email de Contacto" type="email" bind:value={email} placeholder="info@salmasuite.com" />
                    </div>
                </div>
            </div>

            <div class="border-t border-hotel-border/50"></div>

            <div>
                <h3 class="font-display text-xl text-hotel-text-primary italic mb-1">Moneda y Formato</h3>
                <p class="text-xs text-hotel-text-tertiary mb-4">Define cómo se muestran los precios y números en el sistema.</p>

                <div class="space-y-4">
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <InputHotel label="Símbolo de Moneda" bind:value={simbolo} placeholder="$" />
                        <Select label="Posición del Símbolo" options={posiciones} bind:value={posicion} />
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <InputHotel label="Separador de Miles" bind:value={separadorMiles} placeholder="," />
                        <InputHotel label="Separador Decimal" bind:value={separadorDecimal} placeholder="." />
                    </div>
                </div>
            </div>

            <div class="pt-6 border-t border-hotel-border/50">
                <Button variant="gold" onclick={guardarTodo} loading={guardando}>
                    Guardar Cambios
                </Button>
            </div>
        </section>

        <section class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm p-6 h-full">
            <h3 class="font-display text-xl text-hotel-text-primary italic mb-1">Colores del Sistema</h3>
            <p class="text-xs text-hotel-text-tertiary mb-6">Personaliza los colores visuales para los tipos de cliente y estados de las habitaciones.</p>
            <ColorConfig />
        </section>
    </div>
{/if}
