<script lang="ts">
    let nextId = 0;
    const getUniqueId = () => `select-${nextId++}`;

    let {
        value = $bindable(''),
        options = [],
        placeholder = 'Seleccionar...',
        label = '',
        error = $bindable(''),
        required = false,
        id = getUniqueId(),
    }: {
        value?: string;
        options: { value: string; label: string }[];
        placeholder?: string;
        label?: string;
        error?: string;
        required?: boolean;
        id?: string;
    } = $props();
</script>

<div class="space-y-2 w-full">
    {#if label}
        <label for={id} class="block text-sm font-medium tracking-wide text-hotel-text-secondary select-none">
            {label}
            {#if required}<span class="text-hotel-gold ml-0.5">*</span>{/if}
        </label>
    {/if}
    <select
        {id}
        bind:value
        onchange={() => error = ''}
        class="w-full rounded-lg px-4 py-3.5 text-sm bg-hotel-bg text-hotel-text-primary border {error ? 'border-hotel-error' : 'border-hotel-border'} outline-none focus:border-hotel-gold focus:ring-4 focus:ring-hotel-gold/10"
    >
        <option value="" disabled>{placeholder}</option>
        {#each options as opt}
            <option value={opt.value}>{opt.label}</option>
        {/each}
    </select>
    {#if error}
        <p class="text-xs text-hotel-error">{error}</p>
    {/if}
</div>