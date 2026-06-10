<script lang="ts">
    let nextId = 0;
    const getUniqueId = () => `textarea-${nextId++}`;

    let {
        value = $bindable(''),
        placeholder = '',
        label = '',
        error = $bindable(''),
        required = false,
        rows = 3,
        id = getUniqueId(),
    }: {
        value?: string;
        placeholder?: string;
        label?: string;
        error?: string;
        required?: boolean;
        rows?: number;
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
    <textarea
        {id}
        bind:value
        {placeholder}
        {rows}
        oninput={() => error = ''}
        class="w-full rounded-lg px-4 py-3.5 text-sm bg-hotel-bg text-hotel-text-primary border {error ? 'border-hotel-error' : 'border-hotel-border'} outline-none focus:border-hotel-gold focus:ring-4 focus:ring-hotel-gold/10 resize-none"
    ></textarea>
    {#if error}
        <p class="text-xs text-hotel-error">{error}</p>
    {/if}
</div>