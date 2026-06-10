<script lang="ts">
  import type { Snippet } from 'svelte';
  import { fade, scale } from 'svelte/transition';
  import Icon from './Icons.svelte';

  let {
    title,
    subtitle = '',
    maxWidth = 'max-w-2xl',
    onclose,
    children,
  }: {
    title: string;
    subtitle?: string;
    maxWidth?: string;
    onclose: () => void;
    children: Snippet;
  } = $props();

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') onclose();
  }
</script>

<svelte:window onkeydown={onKeydown} />

<!-- svelte-ignore a11y_interactive_supports_focus -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<div
  transition:fade={{ duration: 200 }}
  role="dialog"
  aria-modal="true"
  aria-label={title}
  class="fixed inset-0 z-100 flex items-center justify-center p-4 bg-hotel-bg/90 backdrop-blur-md"
  onclick={(e) => { if (e.target === e.currentTarget) onclose(); }}
>
  <div
    transition:scale={{ duration: 250, start: 0.96 }}
    class="w-full {maxWidth} max-h-[90vh] bg-hotel-surface border border-hotel-border rounded-3xl shadow-2xl flex flex-col overflow-hidden"
    role="presentation"
    onclick={(e) => e.stopPropagation()}
  >
    <div class="p-6 lg:p-8 border-b border-hotel-border flex justify-between items-center bg-hotel-bg/20 shrink-0">
      <div>
        <h2 class="font-display text-2xl lg:text-3xl italic text-hotel-text-primary tracking-tight">
          {title}
        </h2>
        {#if subtitle}
          <span class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold">
            {subtitle}
          </span>
        {/if}
      </div>
      <button
        onclick={onclose}
        class="w-10 h-10 rounded-full border border-hotel-border flex items-center justify-center hover:bg-hotel-error/10 hover:border-hotel-error/40 hover:text-hotel-error-light text-hotel-text-tertiary transition-all"
        aria-label="Cerrar"
      >
        <Icon name="close" class="w-5 h-5" />
      </button>
    </div>

    <div class="flex-1 overflow-y-auto p-6 lg:p-8 custom-scrollbar">
      {@render children()}
    </div>
  </div>
</div>