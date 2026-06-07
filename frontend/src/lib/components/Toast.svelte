<script lang="ts">
  import { fly } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import { toast, type ToastType } from '$lib/stores/toast';
  import Icon from './Icons.svelte';

  const iconsMap: Record<ToastType, string> = {
    success: 'check',
    error: 'close',
    info: 'info',
    warning: 'alert'
  };

  const getColorVar = (type: ToastType): string => {
    switch (type) {
      case 'success': return 'var(--color-hotel-success)';
      case 'error': return 'var(--color-hotel-error)';
      case 'warning': return '#E07C2A';
      default: return 'var(--color-hotel-gold)';
    }
  };
</script>

<div class="fixed top-6 right-6 z-100 flex flex-col gap-3 w-full max-w-[320px] pointer-events-none">
  {#each $toast as t (t.id)}
    <div
      animate:flip={{ duration: 300 }}
      transition:fly={{ x: 50, duration: 400 }}
      class="pointer-events-auto relative overflow-hidden bg-hotel-surface border border-hotel-border/50 p-4 rounded-xl shadow-hotel-lg flex items-start gap-3"
      role="alert"
    >
      <div class="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center bg-hotel-bg border border-hotel-border"
          style="color: {getColorVar(t.type)}">
        <Icon name={iconsMap[t.type] as any} class="w-5 h-5" />
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
        <Icon name="close" class="w-4 h-4" />
      </button>

      <div class="absolute bottom-0 left-0 right-0 h-[3px] bg-hotel-border/20">
        <div class="h-full animate-shrink origin-left"
            style="background: {getColorVar(t.type)}; animation-duration: {t.duration}ms;"></div>
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