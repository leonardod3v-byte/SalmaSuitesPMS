<script lang="ts">
    import { onMount } from 'svelte';
    import { toast } from '$lib/stores/toast';
    import {
        fetchColoresTipoCliente,
        saveColorTipoCliente,
        fetchColoresEstadoHabitacion,
        saveColorEstadoHabitacion,
    } from '$lib/services/configuracion';
    import type { ColorTipoCliente, ColorEstadoHabitacion } from '$lib/types/configuracion';

    let coloresTipo = $state<ColorTipoCliente[]>([]);
    let coloresEstado = $state<ColorEstadoHabitacion[]>([]);
    let cargando = $state(true);

    onMount(async () => {
        try {
            const [t, e] = await Promise.all([
                fetchColoresTipoCliente(),
                fetchColoresEstadoHabitacion(),
            ]);
            coloresTipo = t;
            coloresEstado = e;
        } catch { } finally {
            cargando = false;
        }
    });

    async function guardarColorTipo(tipo: string, color: string) {
        try {
            await saveColorTipoCliente(tipo, color);
            toast.success(`Color para "${tipo}" actualizado.`);
        } catch (e: any) {
            toast.error(e.message);
        }
    }

    async function guardarColorEstado(estado: string, color: string) {
        try {
            await saveColorEstadoHabitacion(estado, color);
            toast.success(`Color para "${estado}" actualizado.`);
        } catch (e: any) {
            toast.error(e.message);
        }
    }
</script>

{#if cargando}
    <p class="text-sm text-hotel-text-tertiary">Cargando colores...</p>
{:else}
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">

        <div>
            <h4 class="text-sm font-bold uppercase tracking-wider text-hotel-text-secondary mb-3 border-b border-hotel-border pb-2">Tipos de Cliente</h4>
            <div class="space-y-2">
                {#each coloresTipo as item}
                    <div class="flex items-center gap-3 p-2 rounded-lg hover:bg-hotel-bg/40 transition-colors">
                        <div class="w-6 h-6 rounded-md border border-hotel-border shadow-sm" style="background-color: {item.color}"></div>
                        <span class="flex-1 text-xs font-medium text-hotel-text-primary">{item.tipo_cliente_profesion}</span>
                        <input
                            type="color"
                            value={item.color}
                            onchange={async (e) => {
                                const nuevo = (e.target as HTMLInputElement).value;
                                item.color = nuevo;
                                await guardarColorTipo(item.tipo_cliente_profesion, nuevo);
                            }}
                            class="w-8 h-8 rounded cursor-pointer bg-transparent border-0"
                        />
                    </div>
                {/each}
            </div>
        </div>

        <div>
            <h4 class="text-sm font-bold uppercase tracking-wider text-hotel-text-secondary mb-3 border-b border-hotel-border pb-2">Estados de Habitación</h4>
            <div class="space-y-2">
                {#each coloresEstado as item}
                    <div class="flex items-center gap-3 p-2 rounded-lg hover:bg-hotel-bg/40 transition-colors">
                        <div class="w-6 h-6 rounded-md border border-hotel-border shadow-sm" style="background-color: {item.color}"></div>
                        <span class="flex-1 text-xs font-medium text-hotel-text-primary">{item.estado}</span>
                        <input
                            type="color"
                            value={item.color}
                            onchange={async (e) => {
                                const nuevo = (e.target as HTMLInputElement).value;
                                item.color = nuevo;
                                await guardarColorEstado(item.estado, nuevo);
                            }}
                            class="w-8 h-8 rounded cursor-pointer bg-transparent border-0"
                        />
                    </div>
                {/each}
            </div>
        </div>
    </div>
{/if}
