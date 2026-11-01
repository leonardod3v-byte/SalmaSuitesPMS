<script lang="ts">
    import { toast } from '$lib/stores/toast';
    import { deleteUsuario, updateUsuario } from '$lib/services/usuarios';
    import { auth } from '$lib/stores/auth.svelte';
    import Modal from '$components/ui/Modal.svelte';
    import Button from '$components/ui/Button.svelte';
    import Icon from '$components/ui/Icons.svelte';
    import type { Usuario } from '$lib/types/usuario';

    let {
        usuarios,
        onedit,
        onrefresh,
    }: {
        usuarios: Usuario[];
        onedit: (u: Usuario) => void;
        onrefresh: () => void;
    } = $props();

    let usuarioADesactivar = $state<Usuario | null>(null);
    let procesando = $state(false);

    let usuarioActual = $derived(auth.user);

    function pedirConfirmacion(u: Usuario) {
        usuarioADesactivar = u;
    }

    async function confirmarDesactivacion() {
        if (!usuarioADesactivar) return;
        procesando = true;
        try {
            await deleteUsuario(usuarioADesactivar.id);
            toast.success(`Usuario ${usuarioADesactivar.username} desactivado.`);
            usuarioADesactivar = null;
            onrefresh();
        } catch (e: any) {
            toast.error(e.message);
        } finally {
            procesando = false;
        }
    }

    async function reactivar(u: Usuario) {
        try {
            await updateUsuario(u.id, { is_active: true } as any);
            toast.success(`Usuario ${u.username} reactivado.`);
            onrefresh();
        } catch (e: any) {
            toast.error(e.message);
        }
    }
</script>

<div class="overflow-x-auto">
    <table class="w-full text-sm">
        <thead>
            <tr class="border-b border-hotel-border text-[10px] uppercase tracking-widest text-hotel-text-tertiary text-left">
                <th class="p-3 font-bold">Usuario</th>
                <th class="p-3 font-bold hidden sm:table-cell">Rol</th>
                <th class="p-3 font-bold hidden md:table-cell">Email</th>
                <th class="p-3 font-bold hidden lg:table-cell">Último Acceso</th>
                <th class="p-3 font-bold text-right">Acciones</th>
            </tr>
        </thead>
        <tbody>
            {#each usuarios as u (u.id)}
                <tr class="border-b border-hotel-border/30 hover:bg-hotel-surface-hover transition-colors {!u.is_active ? 'opacity-60' : ''}">
                    <td class="p-3">
                        <p class="font-bold text-hotel-text-primary flex items-center gap-2">
                            {u.username}
                            {#if !u.is_active}
                                <span class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-hotel-text-tertiary/20 text-hotel-text-tertiary">INACTIVO</span>
                            {/if}
                        </p>
                        <p class="text-[10px] text-hotel-text-tertiary sm:hidden">{u.role === 'admin' ? 'Admin' : 'Recepción'}</p>
                    </td>
                    <td class="p-3 hidden sm:table-cell">
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold {u.role === 'admin' ? 'bg-hotel-vip/10 text-hotel-vip-light border border-hotel-vip/20' : 'bg-hotel-success/10 text-hotel-success-light border border-hotel-success/20'}">
                            {u.role === 'admin' ? 'Administrador' : 'Recepción'}
                        </span>
                    </td>
                    <td class="p-3 text-hotel-text-secondary hidden md:table-cell text-xs">{u.email || '—'}</td>
                    <td class="p-3 text-hotel-text-tertiary text-xs hidden lg:table-cell">
                        {u.last_login ? new Date(u.last_login).toLocaleDateString('es-VE', { day: '2-digit', month: '2-digit', year: 'numeric' }) : 'Nunca'}
                    </td>
                    <td class="p-3 text-right">
                        <div class="flex items-center justify-end gap-2">
                            <button onclick={() => onedit(u)} class="text-hotel-gold hover:text-hotel-gold-light text-[10px] font-bold uppercase tracking-wider">Editar</button>

                            {#if u.id !== usuarioActual?.id}
                                {#if u.is_active}
                                    <button onclick={() => pedirConfirmacion(u)} class="text-hotel-error-light hover:text-hotel-error text-[10px] font-bold uppercase tracking-wider">Desactivar</button>
                                {:else}
                                    <button onclick={() => reactivar(u)} class="text-hotel-success-light hover:text-hotel-success text-[10px] font-bold uppercase tracking-wider">Reactivar</button>
                                {/if}
                            {:else}
                                <span class="text-hotel-text-tertiary/50 text-[10px] uppercase tracking-wider cursor-not-allowed" title="No puedes desactivar tu propio usuario">Actual</span>
                            {/if}
                        </div>
                    </td>
                </tr>
            {:else}
                <tr>
                    <td colspan="5" class="p-10 text-center text-hotel-text-tertiary uppercase tracking-widest text-xs">Sin usuarios</td>
                </tr>
            {/each}
        </tbody>
    </table>
</div>

{#if usuarioADesactivar}
    <Modal onclose={() => usuarioADesactivar = null}>
        <div class="p-6 space-y-5">
            <div class="flex items-start gap-4">
                <div class="w-12 h-12 rounded-full bg-hotel-warning/10 flex items-center justify-center shrink-0">
                    <Icon name="alert" class="w-6 h-6 text-hotel-warning-light" />
                </div>
                <div class="flex-1">
                    <h3 class="text-lg font-bold text-hotel-text-primary">Desactivar usuario</h3>
                    <p class="text-sm text-hotel-text-secondary mt-1">
                        El usuario no podrá iniciar sesión, pero su historial se conservará y podrás reactivarlo después.
                    </p>
                </div>
            </div>

            <div class="p-3 rounded-xl bg-hotel-bg border border-hotel-border space-y-1">
                <div class="flex items-center justify-between">
                    <p class="text-sm font-bold text-hotel-text-primary">{usuarioADesactivar.username}</p>
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold {usuarioADesactivar.role === 'admin' ? 'bg-hotel-vip/10 text-hotel-vip-light border border-hotel-vip/20' : 'bg-hotel-success/10 text-hotel-success-light border border-hotel-success/20'}">
                        {usuarioADesactivar.role === 'admin' ? 'Administrador' : 'Recepción'}
                    </span>
                </div>
                {#if usuarioADesactivar.email}
                    <p class="text-xs text-hotel-text-tertiary">{usuarioADesactivar.email}</p>
                {/if}
            </div>

            <div class="flex gap-3 pt-2">
                <Button variant="ghost" onclick={() => usuarioADesactivar = null} fullWidth>
                    Cancelar
                </Button>
                <Button variant="danger" onclick={confirmarDesactivacion} loading={procesando} fullWidth>
                    Sí, desactivar
                </Button>
            </div>
        </div>
    </Modal>
{/if}
