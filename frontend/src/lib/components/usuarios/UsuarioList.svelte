<script lang="ts">
    import { toast } from '$lib/stores/toast';
    import { deleteUsuario } from '$lib/services/usuarios';
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

    async function eliminar(u: Usuario) {
        if (!confirm(`¿Eliminar permanentemente al usuario "${u.username}"?`)) return;
        try {
            await deleteUsuario(u.id);
            toast.success('Usuario eliminado.');
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
                <th class="p-3 font-bold hidden md:table-cell">Nombre</th>
                <th class="p-3 font-bold hidden sm:table-cell">Rol</th>
                <th class="p-3 font-bold hidden lg:table-cell">Estado</th>
                <th class="p-3 font-bold hidden xl:table-cell">Último Acceso</th>
                <th class="p-3 font-bold text-right">Acciones</th>
            </tr>
        </thead>
        <tbody>
            {#each usuarios as u (u.id)}
                <tr class="border-b border-hotel-border/30">
                    <td class="p-3">
                        <p class="font-bold text-hotel-text-primary">{u.username}</p>
                        <p class="text-[10px] text-hotel-text-tertiary sm:hidden">{u.role === 'admin' ? 'Admin' : 'Recepcionista'}</p>
                    </td>
                    <td class="p-3 text-hotel-text-secondary hidden md:table-cell">{u.nombre_completo}</td>
                    <td class="p-3 hidden sm:table-cell">
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold {u.role === 'admin' ? 'bg-hotel-vip/10 text-hotel-vip-light border border-hotel-vip/20' : 'bg-hotel-success/10 text-hotel-success-light border border-hotel-success/20'}">
                            {u.role === 'admin' ? 'Admin' : 'Recepcionista'}
                        </span>
                    </td>
                    <td class="p-3 hidden lg:table-cell">
                        {#if u.is_active}
                            <span class="text-hotel-success-light text-[10px] font-bold">Activo</span>
                        {:else}
                            <span class="text-hotel-error-light text-[10px] font-bold">Inactivo</span>
                        {/if}
                    </td>
                    <td class="p-3 text-hotel-text-tertiary text-xs hidden xl:table-cell">
                        {u.last_login ? new Date(u.last_login).toLocaleDateString() : 'Nunca'}
                    </td>
                    <td class="p-3 text-right">
                        <div class="flex items-center justify-end gap-2">
                            <button onclick={() => onedit(u)} class="text-hotel-gold hover:text-hotel-gold-light text-[10px] font-bold uppercase tracking-wider">Editar</button>
                            <button onclick={() => eliminar(u)} class="text-hotel-error-light hover:text-hotel-error text-[10px] font-bold uppercase tracking-wider">Eliminar</button>
                        </div>
                    </td>
                </tr>
            {:else}
                <tr>
                    <td colspan="6" class="p-10 text-center text-hotel-text-tertiary uppercase tracking-widest text-xs">Sin usuarios</td>
                </tr>
            {/each}
        </tbody>
    </table>
</div>