<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { toast } from '$lib/stores/toast';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Loading from '$components/ui/Loading.svelte';
    import InputHotel from '$components/ui/Input.svelte';
    import Select from '$components/ui/Select.svelte';
    import Button from '$components/ui/Button.svelte';
    import { fetchConfiguracion, saveConfiguracion } from '$lib/services/configuracion';
    import type { ConfiguracionGeneral } from '$lib/types/configuracion';

    let config = $state<ConfiguracionGeneral>({});
    let cargando = $state(true);
    let guardando = $state(false);
    let error = $state('');

    // Datos de la empresa
    let nombre = $state('');
    let rif = $state('');
    let rtn = $state('');
    let direccion = $state('');
    let telefono = $state('');
    let email = $state('');

    // Moneda
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
            rtn = config.rtn || '';
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
                rtn,
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

<PageHeader title="Configuración" subtitle="Datos del hotel y preferencias del sistema" />

{#if cargando}
    <Loading type="dashboard" message="Cargando configuración..." />
{:else if error}
    <div class="text-center p-8 bg-hotel-error/5 border border-hotel-error/20 rounded-2xl">
        <p class="text-hotel-error-light font-bold uppercase tracking-widest text-xs mb-4">{error}</p>
        <Button variant="gold" onclick={cargar}>Reintentar</Button>
    </div>
{:else}
    <div class="w-full space-y-6">

        <!-- Grid de 2 columnas en pantallas grandes -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

            <!-- SECCIÓN 1: Datos de la Empresa -->
            <section class="bg-hotel-surface rounded-2xl border border-hotel-border p-6">
                <div class="mb-5">
                    <h3 class="text-base font-semibold text-hotel-text-primary">Datos de la Empresa</h3>
                    <p class="text-xs text-hotel-text-tertiary mt-0.5">
                        Información fiscal y de contacto que se imprime en los reportes PDF.
                    </p>
                </div>

                <div class="space-y-4">
                    <InputHotel label="Razón Social" bind:value={nombre} placeholder="Ej: Hotel Salma Suites VIP" />
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <InputHotel label="RIF" bind:value={rif} placeholder="J-12345678-9" />
                        <InputHotel label="RTN" bind:value={rtn} placeholder="12220" />
                    </div>
                    <InputHotel label="Dirección Fiscal" bind:value={direccion} placeholder="Av. Principal, Zona Hotelera..." />
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <InputHotel label="Teléfono" bind:value={telefono} placeholder="0212-5551234" />
                        <InputHotel label="Email" type="email" bind:value={email} placeholder="info@salmasuite.com" />
                    </div>
                </div>
            </section>

            <!-- SECCIÓN 2: Moneda y Formato -->
            <section class="bg-hotel-surface rounded-2xl border border-hotel-border p-6 flex flex-col">
                <div class="mb-5">
                    <h3 class="text-base font-semibold text-hotel-text-primary">Moneda y Formato</h3>
                    <p class="text-xs text-hotel-text-tertiary mt-0.5">
                        Define cómo se muestran los precios en el sistema.
                    </p>
                </div>

                <div class="space-y-4">
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <InputHotel label="Símbolo" bind:value={simbolo} placeholder="$" />
                        <Select label="Posición" options={posiciones} bind:value={posicion} />
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <InputHotel label="Separador de miles" bind:value={separadorMiles} placeholder="," />
                        <InputHotel label="Separador decimal" bind:value={separadorDecimal} placeholder="." />
                    </div>
                </div>

                <!-- Preview del formato -->
                <div class="mt-5 p-4 rounded-lg bg-hotel-bg/50 border border-hotel-border">
                    <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Vista previa</p>
                    <p class="font-mono text-lg text-hotel-text-primary">
                        {posicion === 'antes' ? simbolo : ''}{separadorMiles === ',' ? '1.234' : '1,234'}{separadorDecimal}{'50'}{posicion === 'despues' ? simbolo : ''}
                    </p>
                </div>

                <!-- Botón de guardado dentro de la card de moneda -->
                <div class="mt-auto pt-5 flex justify-end">
                    <Button variant="gold" size="md" onclick={guardarTodo} loading={guardando}>
                        Guardar cambios
                    </Button>
                </div>
            </section>
        </div>

        <!-- SECCIÓN 3: Ocupaciones (ancho completo) -->
        <section class="bg-hotel-surface rounded-2xl border border-hotel-border p-6">
            <div class="flex items-center justify-between">
                <div>
                    <h3 class="text-base font-semibold text-hotel-text-primary">Ocupaciones</h3>
                    <p class="text-xs text-hotel-text-tertiary mt-0.5">
                        Administra los tipos de ocupación y sus colores para el calendario y los huéspedes.
                    </p>
                </div>
                <Button variant="secondary" size="md" onclick={() => goto('/configuracion/ocupaciones')}>
                    Gestionar ocupaciones
                </Button>
            </div>
        </section>
    </div>
{/if}
