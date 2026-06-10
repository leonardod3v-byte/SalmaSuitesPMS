<script lang="ts">
    import type { Snippet } from 'svelte';
    import InputHotel from '$components/ui/Input.svelte';

    let {
        placeholder = 'Buscar...',
        busqueda = $bindable(''),
        onsearch = () => {},
        tieneFiltros = false,
        onclear = () => {},
        children,
    }: {
        placeholder?: string;
        busqueda?: string;
        onsearch?: () => void;
        tieneFiltros?: boolean;
        onclear?: () => void;
        children?: Snippet;
    } = $props();
</script>

<section class="grid grid-cols-1 lg:grid-cols-4 gap-4 items-center bg-hotel-surface/40 p-2 rounded-2xl border border-hotel-border shadow-hotel-sm backdrop-blur-md">
    <div class="lg:col-span-2">
        <InputHotel
            type="search"
            {placeholder}
            bind:value={busqueda}
            oninput={onsearch}
        />
    </div>
    <div class="flex items-center gap-2 lg:justify-end lg:col-span-2 px-2">
        {#if children}
            {@render children()}
        {/if}
        {#if tieneFiltros}
            <button
                onclick={onclear}
                class="h-12 px-4 text-[9px] font-black uppercase tracking-widest text-hotel-error-light hover:bg-hotel-error/5 rounded-xl transition-all"
            >
                Limpiar
            </button>
        {/if}
    </div>
</section>