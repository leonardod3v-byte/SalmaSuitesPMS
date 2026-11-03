<script lang="ts">
    import { auth } from '$lib/stores/auth.svelte';
    import { toast } from '$lib/stores/toast';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import Icon from '$components/ui/Icons.svelte';
    import { cambiarPassword } from '$lib/services/usuarios';

    let oldPassword = $state('');
    let newPassword = $state('');
    let confirmPassword = $state('');
    let loading = $state(false);

    // Ojitos
    let mostrarOldPassword = $state(false);
    let mostrarNewPassword = $state(false);
    let mostrarConfirmPassword = $state(false);

    // Medidor de fuerza
    let passwordStrength = $derived((() => {
        if (!newPassword) return 0;
        let score = 0;
        if (newPassword.length >= 8) score++;
        if (/[A-Z]/.test(newPassword) && /[a-z]/.test(newPassword)) score++;
        if (/[0-9]/.test(newPassword) || /[^A-Za-z0-9]/.test(newPassword)) score++;
        return score;
    })());

    const strengthConfig: Record<number, { label: string; color: string }> = {
        0: { label: 'Débil', color: '#ef4444' },
        1: { label: 'Aceptable', color: '#f97316' },
        2: { label: 'Buena', color: '#eab308' },
        3: { label: 'Fuerte', color: '#22c55e' }
    };

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

    <!-- Columna 1: Info del usuario + Seguridad -->
    <div class="space-y-6">

        <!-- Info personal -->
        <section class="bg-hotel-surface rounded-2xl border border-hotel-border p-6">
            <div class="flex items-center gap-4 mb-5">
                <div class="w-14 h-14 rounded-full bg-linear-to-br from-hotel-gold to-hotel-gold-dark text-hotel-bg flex items-center justify-center font-bold text-xl">
                    {auth.user?.username?.charAt(0).toUpperCase() || '?'}
                </div>
                <div class="min-w-0">
                    <h3 class="text-lg font-semibold text-hotel-text-primary truncate">
                        {auth.user?.username || 'Usuario'}
                    </h3>
                    <p class="text-xs text-hotel-text-tertiary">
                        {auth.user?.role === 'admin' ? 'Administrador' : 'Recepción'}
                    </p>
                </div>
            </div>

            <div class="space-y-3 pt-4 border-t border-hotel-border/50">
                <div>
                    <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Correo electrónico</p>
                    <p class="text-sm text-hotel-text-primary">{auth.user?.email || 'No registrado'}</p>
                </div>
                <div>
                    <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Rol en el sistema</p>
                    <p class="text-sm text-hotel-text-primary">{auth.user?.role === 'admin' ? 'Administrador' : 'Recepcionista'}</p>
                </div>
            </div>
        </section>

        <!-- Seguridad info -->
        <section class="bg-hotel-surface rounded-2xl border border-hotel-border p-6">
            <h3 class="text-base font-semibold text-hotel-text-primary mb-3">Seguridad</h3>
            <p class="text-xs text-hotel-text-tertiary leading-relaxed">
                Tu contraseña es personal e intransferible. Si sospechas que alguien más la conoce, cámbiala inmediatamente.
            </p>
            <div class="mt-4 p-3 rounded-lg bg-hotel-info/5 border border-hotel-info/20">
                <p class="text-[11px] text-hotel-info-light flex items-start gap-2">
                    <Icon name="info" class="w-4 h-4 shrink-0 mt-0.5" />
                    La contraseña debe tener al menos 8 caracteres y combinaciones de letras y números para mayor seguridad.
                </p>
            </div>
        </section>
    </div>

    <!-- Columna 2: Cambiar contraseña -->
    <section class="bg-hotel-surface rounded-2xl border border-hotel-border p-6">
        <h3 class="text-base font-semibold text-hotel-text-primary mb-1">Cambiar contraseña</h3>
        <p class="text-xs text-hotel-text-tertiary mb-5">
            Ingresa tu contraseña actual y define una nueva.
        </p>

        <form onsubmit={handleSubmit} class="space-y-4">

            <!-- Contraseña actual -->
            <div>
                <label for="old-password" class="block text-sm font-medium text-hotel-text-secondary mb-1.5">
                    Contraseña actual <span class="text-hotel-gold">*</span>
                </label>
                <div class="relative">
                    <input
                        id="old-password"
                        type={mostrarOldPassword ? 'text' : 'password'}
                        placeholder="••••••••"
                        bind:value={oldPassword}
                        required
                        class="w-full rounded-lg px-4 py-3 pr-12 text-sm bg-hotel-bg text-hotel-text-primary outline-none border border-hotel-border focus:border-hotel-gold focus:ring-4 focus:ring-hotel-gold/10"
                    />
                    <button
                        type="button"
                        onclick={() => mostrarOldPassword = !mostrarOldPassword}
                        class="absolute right-3 top-1/2 -translate-y-1/2 text-hotel-text-tertiary hover:text-hotel-gold transition-colors"
                        tabindex="-1"
                    >
                        <Icon name={mostrarOldPassword ? 'eye' : 'eye'} class="w-5 h-5" />
                    </button>
                </div>
            </div>

            <!-- Nueva contraseña -->
            <div>
                <label for="new-password" class="block text-sm font-medium text-hotel-text-secondary mb-1.5">
                    Nueva contraseña <span class="text-hotel-gold">*</span>
                </label>
                <div class="relative">
                    <input
                        id="new-password"
                        type={mostrarNewPassword ? 'text' : 'password'}
                        placeholder="Mínimo 8 caracteres"
                        bind:value={newPassword}
                        required
                        class="w-full rounded-lg px-4 py-3 pr-12 text-sm bg-hotel-bg text-hotel-text-primary outline-none border border-hotel-border focus:border-hotel-gold focus:ring-4 focus:ring-hotel-gold/10"
                    />
                    <button
                        type="button"
                        onclick={() => mostrarNewPassword = !mostrarNewPassword}
                        class="absolute right-3 top-1/2 -translate-y-1/2 text-hotel-text-tertiary hover:text-hotel-gold transition-colors"
                        tabindex="-1"
                    >
                        <Icon name={mostrarNewPassword ? 'eye' : 'eye'} class="w-5 h-5" />
                    </button>
                </div>

                <!-- Medidor de fuerza -->
                {#if newPassword}
                    <div class="mt-2 space-y-1.5">
                        <div class="flex gap-1">
                            {#each [1, 2, 3, 4] as nivel}
                                <div
                                    class="flex-1 h-1.5 rounded-full transition-all duration-300"
                                    style="background-color: {passwordStrength >= nivel ? strengthConfig[passwordStrength].color : 'var(--color-hotel-border)'}; opacity: {passwordStrength >= nivel ? '1' : '0.3'}"
                                ></div>
                            {/each}
                        </div>
                        <div class="flex justify-between items-center">
                            <p class="text-[10px] font-bold uppercase tracking-wider" style="color: {strengthConfig[passwordStrength].color}">
                                {strengthConfig[passwordStrength].label}
                            </p>
                            <p class="text-[10px] text-hotel-text-tertiary">
                                {passwordStrength < 3 ? 'Usa mayúsculas, minúsculas y números' : '¡Contraseña segura!'}
                            </p>
                        </div>
                    </div>
                {/if}
            </div>

            <!-- Confirmar contraseña -->
            <div>
                <label for="confirm-password" class="block text-sm font-medium text-hotel-text-secondary mb-1.5">
                    Confirmar contraseña <span class="text-hotel-gold">*</span>
                </label>
                <div class="relative">
                    <input
                        id="confirm-password"
                        type={mostrarConfirmPassword ? 'text' : 'password'}
                        placeholder="Repite la contraseña"
                        bind:value={confirmPassword}
                        required
                        class="w-full rounded-lg px-4 py-3 pr-12 text-sm bg-hotel-bg text-hotel-text-primary outline-none border border-hotel-border focus:border-hotel-gold focus:ring-4 focus:ring-hotel-gold/10"
                    />
                    <button
                        type="button"
                        onclick={() => mostrarConfirmPassword = !mostrarConfirmPassword}
                        class="absolute right-3 top-1/2 -translate-y-1/2 text-hotel-text-tertiary hover:text-hotel-gold transition-colors"
                        tabindex="-1"
                    >
                        <Icon name={mostrarConfirmPassword ? 'eye' : 'eye'} class="w-5 h-5" />
                    </button>
                </div>

                {#if confirmPassword && newPassword !== confirmPassword}
                    <p class="text-[11px] text-hotel-error-light flex items-center gap-1.5 mt-2">
                        <Icon name="close" class="w-3.5 h-3.5" />
                        Las contraseñas no coinciden
                    </p>
                {:else if confirmPassword && newPassword === confirmPassword && passwordStrength >= 2}
                    <p class="text-[11px] text-hotel-success-light flex items-center gap-1.5 mt-2">
                        <Icon name="check" class="w-3.5 h-3.5" />
                        Las contraseñas coinciden
                    </p>
                {/if}
            </div>

            <div class="pt-4 border-t border-hotel-border/50">
                <Button type="submit" variant="gold" loading={loading}>
                    Actualizar contraseña
                </Button>
            </div>
        </form>
    </section>
</div>
