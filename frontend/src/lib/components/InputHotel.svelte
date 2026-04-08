<script lang="ts">
  import type { HTMLInputAttributes } from 'svelte/elements';

  // ── Props ──────────────────────────────────────────────────────────────────
  let {
    type = 'text',
    value = $bindable(''),
    placeholder = '',
    label = '',
    error = $bindable(''),
    required = false,
    autocomplete = undefined,
    id = `input-${Math.random().toString(36).slice(2, 10)}`,
  }: {
    type?: string;
    value?: string;
    placeholder?: string;
    label?: string;
    error?: string;
    required?: boolean;
    autocomplete?: HTMLInputAttributes['autocomplete'];
    id?: string;
  } = $props();

  const handleInput = () => { if (error) error = ''; };
</script>

<div class="space-y-2 w-full">
  {#if label}
    <label for={id} class="block text-sm font-medium tracking-wide text-hotel-text-secondary select-none">
      {label}
      {#if required}
        <span class="text-hotel-gold ml-0.5">*</span>
      {/if}
    </label>
  {/if}

  <div class="relative group">
    <input
      {id}
      {type}
      {placeholder}
      {required}
      {autocomplete}
      bind:value
      oninput={handleInput}
      class="
        w-full rounded-lg px-4 py-3.5 text-sm transition-all duration-200
        bg-hotel-bg text-hotel-text-primary outline-none border
        placeholder:text-hotel-text-tertiary
        {error 
          ? 'border-hotel-error focus:ring-4 focus:ring-hotel-error/15' 
          : 'border-hotel-border focus:border-hotel-gold focus:ring-4 focus:ring-hotel-gold/10 hover:border-hotel-gold-dark'}
      "
    />

    {#if error}
      <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-hotel-error">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
      </div>
    {/if}
  </div>

  {#if error}
    <p class="text-xs flex items-center gap-1.5 text-hotel-error animate-in fade-in slide-in-from-top-1">
      <span class="w-1 h-1 rounded-full bg-current shrink-0"></span>
      {error}
    </p>
  {/if}
</div>