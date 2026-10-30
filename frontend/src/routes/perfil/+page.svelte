<script lang="ts">
    import { auth } from '$lib/stores/auth.svelte';
    import { toast } from '$lib/stores/toast';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import InputHotel from '$components/ui/Input.svelte';
    import Button from '$components/ui/Button.svelte';
    import { cambiarPassword } from '$lib/services/usuarios';

    let oldPassword = $state('');
    let newPassword = $state('');
    let confirmPassword = $state('');
    let loading = $state(false);

    // Variables para el botón del ojito
    let mostrarOldPassword = $state(false);
    let mostrarNewPassword = $state(false);
    let mostrarConfirmPassword = $state(false);

    async function handleSubmit(e: Event) {
        e.preventDefault();

        if (newPassword !== confirmPassword) {
            toast.error('Las contraseñas nuevas no coinciden.');
            return;
        }
        if (newPassword.length < 8) {
            toast.error('La nueva contraseña debe tener al menos 8 caracteres.');
            return;
        }
        if (newPassword === oldPassword) {
            toast.error('La nueva contraseña debe ser diferente a la actual.');
            return;
        }

        loading = true;
        try {
            await cambiarPassword(oldPassword, newPassword, confirmPassword);
            toast.success('Contraseña actualizada correctamente.');
            oldPassword = '';
            newPassword = '';
            confirmPassword = '';
        } catch (e: any) {
            toast.error(e.message || 'Error al cambiar la contraseña.');
        } finally {
            loading = false;
        }
    }
</script>

<svelte:head>
    <title>Mi Perfil | SalmaSuitesPMS</title>
</svelte:head>

<PageHeader title="Mi Perfil" subtitle="Información de tu cuenta y seguridad" />

<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">

    <!-- Columna 1: Datos del Usuario -->
    <section class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm p-6">
        <h3 class="font-display text-xl text-hotel-text-primary italic mb-6">Información Personal</h3>

        <div class="space-y-5">
            <div>
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Usuario</p>
                <p class="font-bold text-hotel-text-primary text-lg">{auth.user?.username || '—'}</p>
            </div>

            <div>
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Rol en el Sistema</p>
                <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold {auth.user?.role === 'admin' ? 'bg-hotel-vip/10 text-hotel-vip-light border border-hotel-vip/20' : 'bg-hotel-success/10 text-hotel-success-light border border-hotel-success/20'}">
                    {auth.user?.role === 'admin' ? 'Administrador' : 'Recepción'}
                </span>
            </div>

            <div>
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Correo Electrónico</p>
                <p class="font-bold text-hotel-text-primary">{auth.user?.email || 'No registrado'}</p>
            </div>
        </div>
    </section>

    <!-- Columna 2: Cambiar Contraseña -->
    <section class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm p-6">
        <h3 class="font-display text-xl text-hotel-text-primary italic mb-6">Cambiar Contraseña</h3>

        <form onsubmit={handleSubmit} class="space-y-5">
            <!-- Contraseña Actual -->
            <div class="space-y-2 w-full">
                <label for="old-password" class="block text-sm font-medium tracking-wide text-hotel-text-secondary select-none">
                    Contraseña Actual <span class="text-hotel-gold ml-0.5">*</span>
                </label>
                <div class="relative group">
                    <input
                        id="old-password"
                        type={mostrarOldPassword ? 'text' : 'password'}
                        placeholder="••••••••"
                        bind:value={oldPassword}
                        required
                        class="w-full rounded-lg px-4 py-3.5 pr-12 text-sm transition-all duration-200 bg-hotel-bg text-hotel-text-primary outline-none border border-hotel-border focus:border-hotel-gold focus:ring-4 focus:ring-hotel-gold/10 hover:border-hotel-gold-dark"
                    />
                    <button
                        type="button"
                        onclick={() => mostrarOldPassword = !mostrarOldPassword}
                        class="absolute right-3 top-1/2 -translate-y-1/2 text-hotel-text-tertiary hover:text-hotel-gold transition-colors focus:outline-none"
                    >
                        {#if mostrarOldPassword}
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                        {:else}
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                        {/if}
                    </button>
                </div>
            </div>

            <!-- Nueva Contraseña -->
            <div class="space-y-2 w-full">
                <label for="new-password" class="block text-sm font-medium tracking-wide text-hotel-text-secondary select-none">
                    Nueva Contraseña <span class="text-hotel-gold ml-0.5">*</span>
                </label>
                <div class="relative group">
                    <input
                        id="new-password"
                        type={mostrarNewPassword ? 'text' : 'password'}
                        placeholder="Mínimo 8 caracteres"
                        bind:value={newPassword}
                        required
                        class="w-full rounded-lg px-4 py-3.5 pr-12 text-sm transition-all duration-200 bg-hotel-bg text-hotel-text-primary outline-none border border-hotel-border focus:border-hotel-gold focus:ring-4 focus:ring-hotel-gold/10 hover:border-hotel-gold-dark"
                    />
                    <button
                        type="button"
                        onclick={() => mostrarNewPassword = !mostrarNewPassword}
                        class="absolute right-3 top-1/2 -translate-y-1/2 text-hotel-text-tertiary hover:text-hotel-gold transition-colors focus:outline-none"
                    >
                        {#if mostrarNewPassword}
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                        {:else}
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                        {/if}
                    </button>
                </div>
            </div>

            <!-- Confirmar Nueva Contraseña -->
            <div class="space-y-2 w-full">
                <label for="confirm-password" class="block text-sm font-medium tracking-wide text-hotel-text-secondary select-none">
                    Confirmar Nueva Contraseña <span class="text-hotel-gold ml-0.5">*</span>
                </label>
                <div class="relative group">
                    <input
                        id="confirm-password"
                        type={mostrarConfirmPassword ? 'text' : 'password'}
                        placeholder="Repite la contraseña"
                        bind:value={confirmPassword}
                        required
                        class="w-full rounded-lg px-4 py-3.5 pr-12 text-sm transition-all duration-200 bg-hotel-bg text-hotel-text-primary outline-none border border-hotel-border focus:border-hotel-gold focus:ring-4 focus:ring-hotel-gold/10 hover:border-hotel-gold-dark"
                    />
                    <button
                        type="button"
                        onclick={() => mostrarConfirmPassword = !mostrarConfirmPassword}
                        class="absolute right-3 top-1/2 -translate-y-1/2 text-hotel-text-tertiary hover:text-hotel-gold transition-colors focus:outline-none"
                    >
                        {#if mostrarConfirmPassword}
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                        {:else}
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                        {/if}
                    </button>
                </div>
            </div>

            {#if confirmPassword && newPassword !== confirmPassword}
                <p class="text-xs text-hotel-error-light flex items-center gap-1.5 mt-2">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                    Las contraseñas no coinciden
                </p>
            {/if}

            <div class="pt-4 border-t border-hotel-border/50">
                <Button type="submit" variant="gold" loading={loading}>
                    Actualizar Contraseña
                </Button>
            </div>
        </form>
    </section>
</div>
