<script lang="ts">
  import { fly } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import { toast, type ToastType } from '$lib/stores/toast';

  const icons: Record<ToastType, string> = {
    success: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>`,
    error: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>`,
    info: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`,
    warning: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>`
  };

  const colors: Record<ToastType, string> = {
    success: 'var(--color-hotel-success)',
    error: 'var(--color-hotel-error)',
    info: 'var(--color-hotel-gold)',
    warning: '#E07C2A'
  };
</script>

<div class="fixed top-6 right-6 z-100 flex flex-col gap-3 w-full max-w-320px pointer-events-none">
  {#each $toast as t (t.id)}
    <div
      animate:flip={{ duration: 300 }}
      transition:fly={{ x: 50, duration: 400 }}
      class="pointer-events-auto relative overflow-hidden bg-hotel-surface border border-hotel-border/50 p-4 rounded-xl shadow-hotel-lg flex items-start gap-3"
      role="alert"
    >
      <div class="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center bg-hotel-bg border border-hotel-border"
           style="color: {colors[t.type]}">
        {@html icons[t.type]}
      </div>

      <div class="flex-1 min-w-0 pt-1">
        <p class="text-xs font-bold text-hotel-text-primary leading-tight uppercase tracking-widest">
          {t.type === 'error' ? 'Atención' : t.type}
        </p>
        <p class="text-[13px] text-hotel-text-secondary mt-1 leading-snug">
          {t.message}
        </p>
      </div>

      <button 
        onclick={() => toast.dismiss(t.id)}
        class="shrink-0 text-hotel-text-tertiary hover:text-hotel-text-primary transition-colors p-1"
        aria-label="Cerrar notificación"
        title="Cerrar"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>

      <div class="absolute bottom-0 left-0 right-0 h-3px bg-hotel-border/20">
        <div class="h-full animate-shrink origin-left"
             style="background: {colors[t.type]}; animation-duration: {t.duration}ms;"></div>
      </div>
    </div>
  {/each}
</div>

<style>
  @keyframes shrink {
    from { transform: scaleX(1); }
    to { transform: scaleX(0); }
  }
  .animate-shrink {
    animation-name: shrink;
    animation-timing-function: linear;
    animation-fill-mode: forwards;
  }
</style>