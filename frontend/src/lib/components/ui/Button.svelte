<script lang="ts">
  import type { Snippet } from 'svelte';

  type ButtonVariant = 'gold' | 'danger' | 'success' | 'secondary' | 'ghost';
  type ButtonType = 'button' | 'submit' | 'reset';
  type ButtonSize = 'sm' | 'md' | 'lg';

  let {
    type = 'button' as ButtonType,
    loading = false,
    disabled = false,
    variant = 'gold' as ButtonVariant,
    size = 'md' as ButtonSize,
    fullWidth = false,
    onclick,
    children,
  }: {
    type?: ButtonType;
    loading?: boolean;
    disabled?: boolean;
    variant?: ButtonVariant;
    size?: ButtonSize;
    fullWidth?: boolean;
    onclick?: (e: MouseEvent) => void;
    children?: Snippet;
  } = $props();

  // Mapeo de variantes
  const variantClasses: Record<ButtonVariant, string> = {
    gold: 'bg-hotel-gold text-hotel-bg hover:bg-hotel-gold-light hover:shadow-hotel-gold active:scale-95',
    danger: 'bg-hotel-error text-white hover:bg-hotel-error-light active:scale-95',
    success: 'bg-hotel-success text-white hover:bg-hotel-success-light active:scale-95',
    secondary: 'bg-hotel-surface text-hotel-gold border border-hotel-gold-dark hover:border-hotel-gold hover:bg-hotel-surface-hover',
    ghost: 'bg-transparent text-hotel-text-secondary hover:text-hotel-gold hover:bg-hotel-surface/20 border border-transparent hover:border-hotel-gold/30',
  };

  // Mapeo de tamaños
  const sizeClasses: Record<ButtonSize, string> = {
    sm: 'px-3 py-2 text-xs',
    md: 'px-6 py-3.5 text-sm',
    lg: 'px-8 py-4 text-base',
  };

  // Clases computadas (derived implícito)
  const buttonClasses = [
    'relative overflow-hidden rounded-lg font-ui font-semibold transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-hotel-gold',
    // svelte-ignore state_referenced_locally
    variantClasses[variant],
    // svelte-ignore state_referenced_locally
    sizeClasses[size],
    // svelte-ignore state_referenced_locally
    fullWidth ? 'w-full' : 'w-auto',
    // svelte-ignore state_referenced_locally
    (disabled || loading) ? 'opacity-50 cursor-not-allowed pointer-events-none' : '',
  ].join(' ');
</script>

<button
  {type}
  disabled={disabled || loading}
  onclick={onclick}
  class={buttonClasses}
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