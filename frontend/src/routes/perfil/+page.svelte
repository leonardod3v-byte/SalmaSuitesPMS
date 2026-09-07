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

    async function handleSubmit(e: Event) {
        e.preventDefault();
        if (newPassword !== confirmPassword) {
            toast.error('Las contraseñas no coinciden.');
            return;
        }
        if (newPassword.length < 8) {
            toast.error('La contraseña debe tener al menos 8 caracteres.');
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
            toast.error(e.message);
        } finally {
            loading = false;
        }
    }
</script>

<svelte:head>
    <title>Perfil | SalmaSuitesPMS</title>
</svelte:head>

<PageHeader title="Mi Perfil" subtitle="Información personal y seguridad" />

<div class="space-y-6">
    <!-- Datos del usuario -->
    <section class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm p-6">
        <h3 class="font-display text-xl text-hotel-text-primary italic mb-6">Información Personal</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            <div>
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Nombre Completo</p>
                <p class="font-bold text-hotel-text-primary">{auth.user?.nombre_completo || '—'}</p>
            </div>
            <div>
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Usuario</p>
                <p class="font-bold text-hotel-text-primary">{auth.user?.username || '—'}</p>
            </div>
            <div>
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Rol</p>
                <p class="font-bold text-hotel-text-primary">{auth.user?.role === 'admin' ? 'Administrador' : 'Recepcionista'}</p>
            </div>
            <div>
                <p class="text-[10px] uppercase tracking-wider text-hotel-text-tertiary mb-1">Email</p>
                <p class="font-bold text-hotel-text-primary">{auth.user?.email || '—'}</p>
            </div>
        </div>
    </section>

    <!-- Cambiar contraseña -->
    <section class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm p-6">
        <h3 class="font-display text-xl text-hotel-text-primary italic mb-6">Cambiar Contraseña</h3>
        <form onsubmit={handleSubmit} class="space-y-4">
            <InputHotel label="Contraseña Actual" type="password" bind:value={oldPassword} required placeholder="••••••••" />
            <InputHotel label="Nueva Contraseña" type="password" bind:value={newPassword} required placeholder="Mínimo 8 caracteres" />
            <InputHotel label="Confirmar Nueva Contraseña" type="password" bind:value={confirmPassword} required placeholder="Repite la contraseña" />
            <div class="pt-4 border-t border-hotel-border/50">
                <Button type="submit" variant="gold" loading={loading}>Actualizar Contraseña</Button>
            </div>
        </form>
    </section>
</div>