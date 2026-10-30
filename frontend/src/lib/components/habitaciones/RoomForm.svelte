<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { toast } from '$lib/stores/toast';
    import InputHotel from '$components/ui/Input.svelte';
    import Select from '$components/ui/Select.svelte';
    import Button from '$components/ui/Button.svelte';
    import { createHabitacion, updateHabitacion, fetchHabitacion } from '$lib/services/habitaciones';
    import type { Habitacion } from '$lib/types/habitacion';
    import { apiFetch } from '$lib/services/api';

    let {
        id = null,
        onclose = () => {},
    }: {
        id?: number | null;
        onclose?: () => void;
    } = $props();

    let loading = $state(false);
    let error = $state('');

    let numero = $state('');
    let piso = $state<number | ''>(1);
    let cantidad_camas = $state<number | ''>(1);
    let capacidad_maxima = $state<number | ''>(1);
    let categoria_tipo = $state('Uni-Familiar');
    let precio_por_noche = $state<number | ''>('');
    let estado = $state('Disponible'); // CAMBIADO
    let notas = $state('');
    let imagenFile = $state<File | null>(null);
    let imagenPreview = $state<string | null>(null);

    const tiposHabitacion = [
        { value: 'Uni-Familiar', label: 'Uni-Familiar' },
        { value: 'Doble Individual', label: 'Doble Individual' },
        { value: 'Doble Matrimonial', label: 'Doble Matrimonial' },
        { value: 'Triple Individual', label: 'Triple Individual' },
        { value: 'Suite', label: 'Suite' },
        { value: 'Queen', label: 'Queen' },
        { value: 'Matrimonial', label: 'Matrimonial' },
    ];

    // CAMBIADO
    const estadosHabitacion = [
        { value: 'Disponible', label: 'Disponible' },
        { value: 'Limpieza', label: 'Limpieza' },
        { value: 'Mantenimiento', label: 'Mantenimiento' },
        { value: 'Obra', label: 'Obra' },
    ];

    onMount(async () => {
        if (id) {
            try {
                const data = await fetchHabitacion(id);
                numero = data.numero;
                piso = data.piso;
                cantidad_camas = data.cantidad_camas;
                capacidad_maxima = data.capacidad_maxima;
                categoria_tipo = data.categoria_tipo;
                precio_por_noche = Number(data.precio_por_noche) || ''; // Arreglo del Bug 1
                estado = data.estado;
                notas = data.notas || '';
            } catch (e: any) {
                error = e.message || 'Error al cargar habitación';
            }
        }
    });

    async function handleSubmit(e: Event) {
        e.preventDefault();
        error = '';
        loading = true;

        const formData = new FormData();
        formData.append('numero', numero);
        formData.append('piso', String(piso));
        formData.append('cantidad_camas', String(cantidad_camas));
        formData.append('capacidad_maxima', String(capacidad_maxima));
        formData.append('categoria_tipo', categoria_tipo);
        formData.append('precio_por_noche', String(precio_por_noche));
        formData.append('estado', estado);
        formData.append('notas', notas);
        if (imagenFile) {
            formData.append('imagen', imagenFile);
        }

        try {
            const url = id ? `/habitaciones/${id}/` : '/habitaciones/';
            const method = id ? 'PUT' : 'POST';

            const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
            const res = await fetch(`${import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'}${url}`, {
                method,
                headers: token ? { 'Authorization': `Token ${token}` } : {},
                body: formData,
                credentials: 'include',
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.error || errData.detail || 'Error al guardar');
            }

            toast.success(id ? 'Habitación actualizada correctamente.' : 'Habitación registrada correctamente.');
            onclose();
            setTimeout(() => goto('/habitaciones', { invalidateAll: true }), 800);
        } catch (e: any) {
            error = e.message || 'Error al guardar';
            toast.error(e.message || 'Error al guardar la habitación.');
        } finally {
            loading = false;
        }
    }

    function handleImagen(e: Event) {
        const input = e.target as HTMLInputElement;
        if (input.files && input.files[0]) {
            imagenFile = input.files[0];
            imagenPreview = URL.createObjectURL(imagenFile);
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

    <div class="p-5 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
        <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Identificación</p>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="sm:col-span-1">
                <InputHotel label="Número" bind:value={numero} required placeholder="Ej: 201" />
            </div>
            <div class="sm:col-span-1">
                <InputHotel label="Piso" type="number" bind:value={piso} required />
            </div>
            <div class="sm:col-span-1">
                <Select label="Estado" options={estadosHabitacion} bind:value={estado} required />
            </div>
        </div>

        <div class="p-5 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
            <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Imagen</p>
            <input
                type="file"
                accept="image/*"
                onchange={handleImagen}
                class="w-full text-sm text-hotel-text-secondary file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-[10px] file:font-bold file:uppercase file:tracking-wider file:bg-hotel-gold file:text-hotel-bg hover:file:bg-hotel-gold-light file:transition-colors file:cursor-pointer"
            />
            {#if imagenPreview}
                <img src={imagenPreview} alt="Preview" class="w-full h-32 object-cover rounded-lg" />
            {/if}
        </div>
    </div>

    <div class="p-5 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
        <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Configuración</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <InputHotel label="Cantidad de Camas" type="number" bind:value={cantidad_camas} required />
            <InputHotel label="Capacidad Máxima" type="number" bind:value={capacidad_maxima} required />
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Select label="Categoría / Tipo" options={tiposHabitacion} bind:value={categoria_tipo} required />
            <InputHotel label="Precio por Noche ($)" type="number" bind:value={precio_por_noche} required={!id} placeholder="Ej: 45.00" />
        </div>
    </div>

    <div class="p-5 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
        <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">Notas</p>
        <InputHotel label="Observaciones" bind:value={notas} placeholder="Información adicional..." />
    </div>

    <div class="flex gap-3 pt-4 border-t border-hotel-border/50">
        <Button type="submit" variant="gold" loading={loading}>
            {id ? 'Actualizar Habitación' : 'Registrar Habitación'}
        </Button>
        <Button type="button" variant="ghost" onclick={onclose}>Cancelar</Button>
    </div>
</form>
