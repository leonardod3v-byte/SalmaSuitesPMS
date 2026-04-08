<script lang="ts">
  import type { Snippet } from 'svelte';

  type ButtonVariant = 'primary' | 'secondary' | 'ghost';
  type ButtonType = 'button' | 'submit' | 'reset';

  let {
    type = 'button' as ButtonType,
    loading = false,
    disabled = false,
    variant = 'primary' as ButtonVariant,
    fullWidth = false,
    onclick,
    children,
  }: {
    type?: ButtonType;
    loading?: boolean;
    disabled?: boolean;
    variant?: ButtonVariant;
    fullWidth?: boolean;
    onclick?: (e: MouseEvent) => void;
    children?: Snippet;
  } = $props();

  const variants = {
    primary: "bg-hotel-gold text-hotel-bg hover:bg-hotel-gold-light hover:shadow-hotel-gold active:scale-95",
    secondary: "bg-hotel-surface text-hotel-gold border border-hotel-gold-dark hover:border-hotel-gold hover:bg-hotel-surface-hover",
    ghost: "bg-transparent text-hotel-text-secondary hover:text-hotel-gold"
  };
</script>

<button
  {type}
  {disabled}
  onclick={onclick}
  class="
    relative overflow-hidden rounded-lg font-ui font-semibold
    transition-all duration-200 px-6 py-3.5 text-sm tracking-wide
    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-hotel-gold
    {variants[variant]}
    {fullWidth ? 'w-full' : 'w-auto'}
    {(disabled || loading) ? 'opacity-50 cursor-not-allowed pointer-events-none' : ''}
  "
>
  {#if loading}
    <div class="flex items-center justify-center gap-2">
      <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
      </svg>
      <span class="animate-pulse">Procesando...</span>
    </div>
  {:else}
    {@render children?.()}
  {/if}
</button>