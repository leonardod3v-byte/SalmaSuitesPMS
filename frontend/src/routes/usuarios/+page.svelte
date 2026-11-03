<script lang="ts">
    import { onMount } from 'svelte';
    import PageHeader from '$components/ui/PageHeader.svelte';
    import Button from '$components/ui/Button.svelte';
    import Modal from '$components/ui/Modal.svelte';
    import Loading from '$components/ui/Loading.svelte';
    import UsuarioList from '$components/usuarios/UsuarioList.svelte';
    import UsuarioForm from '$components/usuarios/UsuarioForm.svelte';
    import { fetchUsuarios } from '$lib/services/usuarios';
    import type { Usuario } from '$lib/types/usuario';

    let usuarios = $state<Usuario[]>([]);
    let cargando = $state(true);
    let error = $state('');

    let mostrarForm = $state(false);
    let usuarioEditar = $state<Usuario | null>(null);

    async function cargar() {
        cargando = true;
        try {
            usuarios = await fetchUsuarios();
        } catch (e: any) {
            error = e.message;
        } finally {
            cargando = false;
        }
    }

    onMount(() => cargar());

    function abrirNuevo() {
        usuarioEditar = null;
        mostrarForm = true;
    }

    function abrirEditar(u: Usuario) {
        usuarioEditar = u;
        mostrarForm = true;
    }

    function cerrarForm() {
        mostrarForm = false;
        usuarioEditar = null;
        cargar();
    }
</script>

<svelte:head>
    <title>Usuarios | SalmaSuitesPMS</title>
</svelte:head>

<PageHeader title="Usuarios" subtitle="{usuarios.length} usuarios">
    <Button variant="gold" size="md" onclick={abrirNuevo}>
        <span class="flex items-center gap-1.5">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            Nuevo Usuario
        </span>
    </Button>
</PageHeader>

{#if cargando}
    <Loading type="dashboard" message="Cargando usuarios..." />
{:else if error}
    <div class="text-center p-8 bg-hotel-error/5 border border-hotel-error/20 rounded-2xl">
        <p class="text-hotel-error-light font-bold uppercase tracking-widest text-xs mb-4">{error}</p>
        <Button variant="gold" size="sm" onclick={cargar}>Reintentar</Button>
    </div>
{:else}
    <div class="bg-hotel-surface rounded-2xl border border-hotel-border shadow-hotel-sm overflow-hidden">
        <UsuarioList {usuarios} onedit={abrirEditar} onrefresh={cargar} />
    </div>
{/if}

{#if mostrarForm}
    <Modal
        title={usuarioEditar ? 'Editar Usuario' : 'Nuevo Usuario'}
        onclose={cerrarForm}
    >
        <UsuarioForm
            usuario={usuarioEditar}
            onclose={cerrarForm}
        />
    </Modal>
{/if}
