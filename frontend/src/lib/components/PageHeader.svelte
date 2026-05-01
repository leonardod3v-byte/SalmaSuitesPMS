<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    title,
    subtitle = '',
    actions
  }: {
    title: string;
    subtitle?: string;
    actions?: Snippet;
  } = $props();
</script>

<header class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
  <div>
    <h1 class="text-4xl font-display font-black italic text-hotel-text-primary tracking-tight">
      {title}
    </h1>
    {#if subtitle}
      <p class="text-[10px] font-black uppercase tracking-[0.2em] text-hotel-gold mt-1">
      <span class="w-2 h-2 rounded-full bg-hotel-gold animate-pulse"></span>
        {subtitle}
      </p>
    {/if}
  </div>

  {#if actions}
    <div class="flex items-center gap-3 w-full sm:w-auto">
      {@render actions()}
    </div>
  {/if}
</header>