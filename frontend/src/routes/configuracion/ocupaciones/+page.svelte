<script lang="ts">
    import { onMount } from 'svelte';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import InputHotel from '$components/ui/Input.svelte';
    import Modal from '$components/ui/Modal.svelte';
    import Icon from '$components/ui/Icons.svelte';
    import { toast } from '$lib/stores/toast';
    import { fetchOcupaciones, createOcupacion, updateOcupacion, deleteOcupacion, type Ocupacion } from '$lib/services/ocupaciones';

    let ocupaciones = $state<Ocupacion[]>([]);
    let cargando = $state(true);
    let mostrarForm = $state(false);
    let editando = $state<Ocupacion | null>(null);
    let formNombre = $state('');
    let formColor = $state('#3b82f6');
    let loading = $state(false);

    async function cargar() {
        cargando = true;
        try {
            ocupaciones = await fetchOcupaciones();
        } catch {
            toast.error('Error al cargar ocupaciones');
        } finally {
            cargando = false;
        }
    }

    onMount(cargar);

    function abrirNuevo() {
        editando = null;
        formNombre = '';
        formColor = '#3b82f6';
        mostrarForm = true;
    }

    function abrirEditar(o: Ocupacion) {
        editando = o;
        formNombre = o.nombre;
        formColor = o.color;
        mostrarForm = true;
    }

    async function guardar() {
        if (!formNombre.trim()) { toast.error('El nombre es obligatorio'); return; }
        loading = true;
        try {
            if (editando) {
                await updateOcupacion(editando.id, { nombre: formNombre, color: formColor });
                toast.success('Ocupación actualizada');
            } else {
                await createOcupacion({ nombre: formNombre, color: formColor });
                toast.success('Ocupación creada');
            }
            mostrarForm = false;
            await cargar();
        } catch (e: any) {
            toast.error(e.message);
        } finally {
            loading = false;
        }
    }

    async function eliminar(o: Ocupacion) {
        if (!confirm(`¿Eliminar la ocupación "${o.nombre}"?`)) return;
        try {
            await deleteOcupacion(o.id);
            toast.success('Ocupación eliminada');
            await cargar();
        } catch (e: any) {
            toast.error(e.message);
        }
    }
</script>

<svelte:head>
    <title>Ocupaciones | SalmaSuitesPMS</title>
</svelte:head>

<PageHeader title="Ocupaciones" subtitle="Gestiona los tipos de ocupación y sus colores">
    <Button variant="gold" onclick={abrirNuevo}>
        <span class="flex items-center gap-1.5"><Icon name="plus" class="w-4 h-4" /> Nueva ocupación</span>
    </Button>
</PageHeader>

{#if cargando}
    <p class="text-center text-hotel-text-tertiary">Cargando...</p>
{:else}
    <div class="bg-hotel-surface rounded-2xl border border-hotel-border overflow-hidden">
        <table class="w-full text-sm">
            <thead>
                <tr class="border-b border-hotel-border text-[10px] uppercase tracking-widest text-hotel-text-tertiary text-left">
                    <th class="p-3">Color</th>
                    <th class="p-3">Nombre</th>
                    <th class="p-3 text-right">Acciones</th>
                </tr>
            </thead>
            <tbody>
                {#each ocupaciones as o (o.id)}
                    <tr class="border-b border-hotel-border/30">
                        <td class="p-3">
                            <div class="w-8 h-8 rounded-full border-2 border-hotel-border" style="background-color: {o.color}"></div>
                        </td>
                        <td class="p-3 font-bold text-hotel-text-primary">{o.nombre}</td>
                        <td class="p-3 text-right">
                            <button onclick={() => abrirEditar(o)} class="text-hotel-gold text-[10px] font-bold uppercase mr-3">Editar</button>
                            <button onclick={() => eliminar(o)} class="text-hotel-error-light text-[10px] font-bold uppercase">Eliminar</button>
                        </td>
                    </tr>
                {:else}
                    <tr><td colspan="3" class="p-10 text-center text-hotel-text-tertiary uppercase text-xs">Sin ocupaciones</td></tr>
                {/each}
            </tbody>
        </table>
    </div>
{/if}

{#if mostrarForm}
    <Modal title={editando ? 'Editar Ocupación' : 'Nueva Ocupación'} onclose={() => mostrarForm = false}>
        <div class="space-y-4 p-4">
            <InputHotel label="Nombre" bind:value={formNombre} placeholder="Ej: Estudiante" required />
            <div>
                <label for="color-input" class="block text-sm font-medium text-hotel-text-secondary mb-1">Color</label>
                <input id="color-input" type="color" bind:value={formColor} class="w-full h-12 rounded-lg cursor-pointer bg-hotel-bg border border-hotel-border" />
            </div>
            <div class="flex gap-3 pt-2">
                <Button variant="gold" onclick={guardar} loading={loading} fullWidth>{editando ? 'Actualizar' : 'Crear'}</Button>
                <Button variant="ghost" onclick={() => mostrarForm = false}>Cancelar</Button>
            </div>
        </div>
    </Modal>
{/if}
