<script lang="ts">
    import { toast } from '$lib/stores/toast';
    import InputHotel from '$components/ui/Input.svelte';
    import Select from '$components/ui/Select.svelte';
    import Button from '$components/ui/Button.svelte';
    import { createUsuario, updateUsuario } from '$lib/services/usuarios';
    import type { Usuario } from '$lib/types/usuario';

    let {
        usuario = null,
        onclose,
        onsuccess,
    }: {
        usuario?: Usuario | null;
        onclose?: () => void;
        onsuccess?: () => void;
    } = $props();

    let loading = $state(false);
    let username = $state('');
    let password = $state('');
    let role = $state('recepcionista');
    let nombreCompleto = $state('');
    let email = $state('');

    // Inicializar desde usuario si existe
    $effect(() => {
        if (usuario) {
            username = usuario.username;
            role = usuario.role;
            nombreCompleto = usuario.nombre_completo || '';
            email = usuario.email || '';
        }
    });

    const roles = [
        { value: 'admin', label: 'Administrador' },
        { value: 'recepcionista', label: 'Recepcionista' },
    ];

    let esNuevo = $derived(!usuario);

    async function guardar() {
        if (!username.trim()) { toast.error('El nombre de usuario es obligatorio.'); return; }
        if (esNuevo && !password.trim()) { toast.error('La contraseña es obligatoria.'); return; }
        if (!nombreCompleto.trim()) { toast.error('El nombre completo es obligatorio.'); return; }

        loading = true;
        let success = false;
        
        try {
            if (esNuevo) {
                await createUsuario({ username, password, role, nombre_completo: nombreCompleto, email });
                toast.success('Usuario creado correctamente.');
            } else {
                const data: any = { role, nombre_completo: nombreCompleto, email };
                if (password) data.password = password;
                await updateUsuario(usuario!.id, data);
                toast.success('Usuario actualizado correctamente.');
            }
            
            loading = false;
            if (onsuccess) onsuccess();
        } catch (e: any) {
            toast.error(e?.message || 'Error al guardar usuario.');
            loading = false;
        }
    }
</script>

<div class="space-y-5">
    <div class="p-4 rounded-2xl bg-hotel-bg/40 border border-hotel-border space-y-4">
        <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">
            {esNuevo ? 'Nuevo Usuario' : 'Editar Usuario'}
        </p>

        {#if esNuevo}
            <InputHotel label="Nombre de Usuario" bind:value={username} required placeholder="ej: recepcion_01" />
        {:else}
            <InputHotel label="Nombre de Usuario" bind:value={username} required />
            <p class="text-[10px] text-hotel-text-tertiary">El nombre de usuario no se puede cambiar (se ignora al guardar).</p>
        {/if}

        <InputHotel label="Contraseña" type="password" bind:value={password} placeholder={esNuevo ? 'Contraseña' : 'Dejar vacío para no cambiar'} />
        <InputHotel label="Nombre Completo" bind:value={nombreCompleto} required placeholder="Ej: María Rodríguez" />
        <InputHotel label="Email" type="email" bind:value={email} placeholder="ejemplo@hotel.com" />
        <Select label="Rol" options={roles} bind:value={role} required />
    </div>

    <div class="flex gap-3 pt-4 border-t border-hotel-border/50">
        <Button variant="gold" onclick={guardar} loading={loading} fullWidth>
            {esNuevo ? 'Crear Usuario' : 'Actualizar Usuario'}
        </Button>
        <Button variant="ghost" onclick={onclose || (() => {})}>Cancelar</Button>
    </div>
</div>