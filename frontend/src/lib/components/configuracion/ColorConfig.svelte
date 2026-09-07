<script lang="ts">
    import { onMount } from 'svelte';
    import { toast } from '$lib/stores/toast';
    import Button from '$components/ui/Button.svelte';
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

<div class="space-y-6">
    <!-- Colores por Tipo de Cliente -->
    <div>
        <h3 class="font-display text-lg text-hotel-text-primary italic mb-4">Colores por Tipo de Cliente</h3>
        <div class="space-y-3">
            {#each coloresTipo as item}
                <div class="flex items-center gap-4 p-3 rounded-xl bg-hotel-bg/40 border border-hotel-border">
                    <div class="w-8 h-8 rounded-lg border" style="background-color: {item.color}"></div>
                    <span class="flex-1 text-sm font-bold text-hotel-text-primary">{item.tipo_cliente_profesion}</span>
                    <input
                        type="color"
                        value={item.color}
                        onchange={async (e) => {
                            const nuevo = (e.target as HTMLInputElement).value;
                            item.color = nuevo;
                            await guardarColorTipo(item.tipo_cliente_profesion, nuevo);
                        }}
                        class="w-10 h-10 rounded-lg border border-hotel-border cursor-pointer bg-hotel-bg"
                    />
                </div>
            {/each}
        </div>
    </div>

    <!-- Colores por Estado de Habitación -->
    <div>
        <h3 class="font-display text-lg text-hotel-text-primary italic mb-4">Colores por Estado de Habitación</h3>
        <div class="space-y-3">
            {#each coloresEstado as item}
                <div class="flex items-center gap-4 p-3 rounded-xl bg-hotel-bg/40 border border-hotel-border">
                    <div class="w-8 h-8 rounded-lg border" style="background-color: {item.color}"></div>
                    <span class="flex-1 text-sm font-bold text-hotel-text-primary">{item.estado}</span>
                    <input
                        type="color"
                        value={item.color}
                        onchange={async (e) => {
                            const nuevo = (e.target as HTMLInputElement).value;
                            item.color = nuevo;
                            await guardarColorEstado(item.estado, nuevo);
                        }}
                        class="w-10 h-10 rounded-lg border border-hotel-border cursor-pointer bg-hotel-bg"
                    />
                </div>
            {/each}
        </div>
    </div>
</div>