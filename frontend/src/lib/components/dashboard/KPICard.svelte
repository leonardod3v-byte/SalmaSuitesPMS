<script lang="ts">
  import Icon from '../ui/Icons.svelte';

  let {
    title,
    value,
    subtitle,
    iconName,
    trend,
    trendUp,
    color = 'gold',
  }: {
    title: string;
    value: string | number;
    subtitle?: string;
    iconName: string;
    trend?: string;
    trendUp?: boolean;
    color?: 'gold' | 'success' | 'error' | 'vip';
  } = $props();

  const colorMap = {
    gold: 'text-hotel-gold border-hotel-gold/20 group-hover:bg-hotel-gold group-hover:shadow-hotel-gold/30',
    success: 'text-hotel-success-light border-hotel-success/20 group-hover:bg-hotel-success group-hover:shadow-hotel-success/30',
    error: 'text-hotel-error-light border-hotel-error/20 group-hover:bg-hotel-error group-hover:shadow-hotel-error/30',
    vip: 'text-hotel-vip-light border-hotel-vip/20 group-hover:bg-hotel-vip group-hover:shadow-hotel-vip/30'
  };

  const glowMap = {
    gold: 'bg-hotel-gold/5 group-hover:bg-hotel-gold/10',
    success: 'bg-hotel-success/5 group-hover:bg-hotel-success/10',
    error: 'bg-hotel-error/5 group-hover:bg-hotel-error/10',
    vip: 'bg-hotel-vip/5 group-hover:bg-hotel-vip/10'
  };
</script>

<div class="group relative overflow-hidden rounded-2xl border border-hotel-border bg-hotel-surface p-5 transition-all duration-500 hover:-translate-y-1.5 hover:shadow-[0_20px_40px_-15px_rgba(0,0,0,0.5)]">
  
  <div class="absolute -right-4 -top-4 h-24 w-24 rounded-full blur-3xl transition-all duration-700 {glowMap[color]}"></div>

  <div class="relative flex flex-col gap-5">
    <div class="flex items-center justify-between">
      <div class="flex h-12 w-12 items-center justify-center rounded-xl border bg-hotel-bg/50 backdrop-blur-sm transition-all duration-500 group-hover:scale-110 group-hover:text-hotel-bg {colorMap[color]}">
        <Icon name={iconName} class="h-6 w-6" />
      </div>

      {#if trend}
        <div class="flex items-center gap-1 rounded-full px-2.5 py-1 text-[10px] font-black uppercase tracking-tighter shadow-sm {trendUp ? 'bg-hotel-success/10 text-hotel-success-light border border-hotel-success/20' : 'bg-hotel-error/10 text-hotel-error-light border border-hotel-error/20'}">
          {trendUp ? '↑' : '↓'} {trend}
        </div>
      {/if}
    </div>

    <div class="space-y-1.5">
      <p class="text-[10px] font-bold uppercase tracking-[0.2em] text-hotel-text-tertiary">
        {title}
      </p>
      <h3 class="font-display text-3xl font-bold text-hotel-text-primary tabular-nums tracking-tighter">
        {value}
      </h3>
      {#if subtitle}
        <p class="text-[11px] font-medium text-hotel-text-secondary line-clamp-1 opacity-70 group-hover:opacity-100 transition-opacity">
          {subtitle}
        </p>
      {/if}
    </div>
  </div>

  <div class="absolute bottom-0 left-0 h-0.5 w-0 transition-all duration-700 group-hover:w-full"
      style="background: var(--color-hotel-{color === 'gold' ? 'gold' : color}); box-shadow: 0 0 15px var(--color-hotel-{color === 'gold' ? 'gold' : color});">
  </div>
</div>