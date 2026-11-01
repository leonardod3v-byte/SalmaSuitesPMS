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
    }: {
        usuario?: Usuario | null;
        onclose: () => void;
    } = $props();

    let loading = $state(false);
    let username = $state('');
    let password = $state('');
    let confirmPassword = $state('');
    let role = $state('recepcionista');
    let email = $state('');

    // Ojitos
    let mostrarPassword = $state(false);
    let mostrarConfirmPassword = $state(false);

    $effect(() => {
        if (usuario) {
            username = usuario.username;
            role = usuario.role;
            email = usuario.email || '';
        }
    });

    const roles = [
        { value: 'admin', label: 'Administrador' },
        { value: 'recepcionista', label: 'Recepción' },
    ];

    let esNuevo = $derived(!usuario);

    let passwordStrength = $derived((() => {
        if (!password) return 0;
        let score = 0;
        if (password.length >= 8) score++;
        if (/[A-Z]/.test(password) && /[a-z]/.test(password)) score++;
        if (/[0-9]/.test(password) || /[^A-Za-z0-9]/.test(password)) score++;
        return score;
    })());

    const strengthConfig: Record<number, { label: string; color: string }> = {
        0: { label: 'Débil', color: '#ef4444' },
        1: { label: 'Aceptable', color: '#f97316' },
        2: { label: 'Buena', color: '#eab308' },
        3: { label: 'Fuerte', color: '#22c55e' }
    };

    async function guardar() {
        if (!username.trim()) { toast.error('El nombre de usuario es obligatorio.'); return; }

        if (esNuevo) {
            if (!password.trim()) { toast.error('La contraseña es obligatoria.'); return; }
            if (password.length < 8) { toast.error('La contraseña debe tener al menos 8 caracteres.'); return; }
            if (password !== confirmPassword) { toast.error('Las contraseñas no coinciden.'); return; }
        } else if (password) {
            if (password.length < 8) { toast.error('La contraseña debe tener al menos 8 caracteres.'); return; }
            if (password !== confirmPassword) { toast.error('Las contraseñas no coinciden.'); return; }
        }

        loading = true;
        try {
            const payloadBase = {
                username,
                role,
                email,
                nombre_completo: username
            };

            if (esNuevo) {
                await createUsuario({ ...payloadBase, password });
                toast.success('Usuario creado correctamente.');
            } else {
                const data: any = payloadBase;
                if (password) data.password = password;
                await updateUsuario(usuario!.id, data);
                toast.success('Usuario actualizado correctamente.');
            }
            onclose();
        } catch (e: any) {
            toast.error(e?.message || 'Error al guardar usuario.');
        } finally {
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
            <InputHotel label="Nombre de Usuario" bind:value={username} required placeholder="Ej: recepcion" />
        {:else}
            <InputHotel label="Nombre de Usuario" bind:value={username} required />
            <p class="text-[10px] text-hotel-text-tertiary">El nombre de usuario no se puede cambiar.</p>
        {/if}

        <div class="space-y-1.5 w-full">
            <label for="password" class="block text-sm font-medium tracking-wide text-hotel-text-secondary select-none">
                Contraseña {#if esNuevo}<span class="text-hotel-gold ml-0.5">*</span>{/if}
            </label>
            <div class="relative group">
                <input
                    id="password"
                    type={mostrarPassword ? 'text' : 'password'}
                    placeholder={esNuevo ? 'Mínimo 8 caracteres' : 'Dejar vacío para no cambiar'}
                    bind:value={password}
                    class="w-full rounded-lg px-4 py-3.5 pr-12 text-sm transition-all duration-200 bg-hotel-bg text-hotel-text-primary outline-none border border-hotel-border focus:border-hotel-gold focus:ring-4 focus:ring-hotel-gold/10 hover:border-hotel-gold-dark"
                />
                <button
                    type="button"
                    onclick={() => mostrarPassword = !mostrarPassword}
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-hotel-text-tertiary hover:text-hotel-gold transition-colors focus:outline-none"
                    aria-label={mostrarPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                >
                    {#if mostrarPassword}
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                    {:else}
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                    {/if}
                </button>
            </div>
        </div>

        {#if password}
            <div class="space-y-2">
                <div class="flex gap-1">
                    {#each [1, 2, 3, 4] as nivel}
                        <div class="flex-1 h-1.5 rounded-full transition-all duration-300"
                            style="background-color: {passwordStrength >= nivel ? strengthConfig[passwordStrength].color : 'var(--color-hotel-border)'}; opacity: {passwordStrength >= nivel ? '1' : '0.3'}">
                        </div>
                    {/each}
                </div>
                <div class="flex justify-between items-center">
                    <p class="text-[10px] font-bold uppercase" style="color: {strengthConfig[passwordStrength].color}">
                        {strengthConfig[passwordStrength].label}
                    </p>
                    <p class="text-[9px] text-hotel-text-tertiary">
                        {passwordStrength < 3 ? 'Usa mayúsculas, minúsculas y números' : '¡Contraseña segura!'}
                    </p>
                </div>
            </div>
        {/if}

        {#if esNuevo || password}
            <div class="space-y-1.5 w-full">
                <label for="confirm-password" class="block text-sm font-medium tracking-wide text-hotel-text-secondary select-none">
                    Confirmar contraseña {#if esNuevo}<span class="text-hotel-gold ml-0.5">*</span>{/if}
                </label>
                <div class="relative group">
                    <input
                        id="confirm-password"
                        type={mostrarConfirmPassword ? 'text' : 'password'}
                        placeholder="Repite la contraseña"
                        bind:value={confirmPassword}
                        class="w-full rounded-lg px-4 py-3.5 pr-12 text-sm transition-all duration-200 bg-hotel-bg text-hotel-text-primary outline-none border border-hotel-border focus:border-hotel-gold focus:ring-4 focus:ring-hotel-gold/10 hover:border-hotel-gold-dark"
                    />
                    <button
                        type="button"
                        onclick={() => mostrarConfirmPassword = !mostrarConfirmPassword}
                        class="absolute right-3 top-1/2 -translate-y-1/2 text-hotel-text-tertiary hover:text-hotel-gold transition-colors focus:outline-none"
                        aria-label={mostrarConfirmPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                    >
                        {#if mostrarConfirmPassword}
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                        {:else}
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                        {/if}
                    </button>
                </div>
            </div>

            {#if confirmPassword && password !== confirmPassword}
                <p class="text-xs text-hotel-error-light flex items-center gap-1.5">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                    Las contraseñas no coinciden
                </p>
            {/if}

            {#if confirmPassword && password === confirmPassword && passwordStrength >= 2}
                <p class="text-xs text-hotel-success-light flex items-center gap-1.5">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                    Las contraseñas coinciden
                </p>
            {/if}
        {/if}

        <InputHotel label="Email" type="email" bind:value={email} placeholder="ejemplo@hotel.com" />
        <Select label="Rol" options={roles} bind:value={role} required />
    </div>

    <div class="flex gap-3 pt-4 border-t border-hotel-border/50">
        <Button variant="gold" onclick={guardar} loading={loading} fullWidth>
            {esNuevo ? 'Crear Usuario' : 'Actualizar Usuario'}
        </Button>
        <Button variant="ghost" onclick={onclose}>Cancelar</Button>
    </div>
</div>
