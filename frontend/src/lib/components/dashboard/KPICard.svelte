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
    color?: 'gold' | 'success' | 'error' | 'vip' | 'info';
  } = $props();

  const colorMap = {
    gold: 'text-hotel-gold border-hotel-gold/20 group-hover:bg-hotel-gold group-hover:text-hotel-bg group-hover:shadow-[0_0_30px_-5px_rgba(212,175,55,0.6)]',
    success: 'text-hotel-success-light border-hotel-success/20 group-hover:bg-hotel-success group-hover:text-hotel-bg group-hover:shadow-[0_0_30px_-5px_rgba(34,197,94,0.6)]',
    error: 'text-hotel-error-light border-hotel-error/20 group-hover:bg-hotel-error group-hover:text-hotel-bg group-hover:shadow-[0_0_30px_-5px_rgba(239,68,68,0.6)]',
    vip: 'text-hotel-vip-light border-hotel-vip/20 group-hover:bg-hotel-vip group-hover:text-hotel-bg group-hover:shadow-[0_0_30px_-5px_rgba(168,85,247,0.6)]',
    info: 'text-hotel-info-light border-hotel-info/20 group-hover:bg-hotel-info group-hover:text-hotel-bg group-hover:shadow-[0_0_30px_-5px_rgba(59,130,246,0.6)]'
  };

  const glowMap = {
    gold: 'bg-hotel-gold/10 group-hover:bg-hotel-gold/20',
    success: 'bg-hotel-success/10 group-hover:bg-hotel-success/20',
    error: 'bg-hotel-error/10 group-hover:bg-hotel-error/20',
    vip: 'bg-hotel-vip/10 group-hover:bg-hotel-vip/20',
    info: 'bg-hotel-info/10 group-hover:bg-hotel-info/20'
  };

  const barMap = {
    gold: 'bg-gradient-to-r from-hotel-gold via-hotel-gold-light to-hotel-gold',
    success: 'bg-gradient-to-r from-hotel-success via-hotel-success-light to-hotel-success',
    error: 'bg-gradient-to-r from-hotel-error via-hotel-error-light to-hotel-error',
    vip: 'bg-gradient-to-r from-hotel-vip via-hotel-vip-light to-hotel-vip',
    info: 'bg-gradient-to-r from-hotel-info via-hotel-info-light to-hotel-info'
  };
</script>

<div class="group relative overflow-hidden rounded-2xl border border-hotel-border bg-hotel-surface p-5 transition-all duration-500 hover:-translate-y-1.5 hover:border-hotel-border/80 hover:shadow-[0_20px_40px_-15px_rgba(0,0,0,0.6)]">

  <div class="absolute -right-8 -top-8 h-32 w-32 rounded-full blur-3xl transition-all duration-700 {glowMap[color]}"></div>
  <div class="absolute -left-8 -bottom-8 h-24 w-24 rounded-full blur-3xl opacity-50 transition-all duration-700 {glowMap[color]}"></div>

  <div class="absolute top-0 left-0 h-1 w-0 transition-all duration-700 ease-out group-hover:w-full {barMap[color]} rounded-t-2xl"></div>

  <div class="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 bg-linear-to-r from-transparent via-white/5 to-transparent pointer-events-none"></div>

  <div class="relative flex flex-col gap-5">
    <div class="flex items-start justify-between">
      <div class="flex h-12 w-12 items-center justify-center rounded-xl border bg-hotel-bg/50 backdrop-blur-sm transition-all duration-500 group-hover:scale-110 group-hover:rotate-[-5deg] {colorMap[color]}">
        <Icon name={iconName} class="h-6 w-6 transition-transform duration-500" />
      </div>

      {#if trend}
        <div class="flex items-center gap-1 rounded-full px-2.5 py-1 text-[10px] font-black uppercase tracking-tighter shadow-sm
          {trendUp
            ? 'bg-hotel-success/10 text-hotel-success-light border border-hotel-success/20'
            : 'bg-hotel-error/10 text-hotel-error-light border border-hotel-error/20'}">
          <span class="text-xs">{trendUp ? '↑' : '↓'}</span>
          {trend}
        </div>
      {/if}
    </div>

    <div class="space-y-2">
      <p class="text-[10px] font-bold uppercase tracking-[0.2em] text-hotel-text-tertiary group-hover:text-hotel-text-secondary transition-colors">
        {title}
      </p>
      <h3 class="font-display text-3xl lg:text-4xl font-bold text-hotel-text-primary tabular-nums tracking-tighter leading-none">
        {value}
      </h3>
      {#if subtitle}
        <p class="text-[11px] font-medium text-hotel-text-secondary line-clamp-2 opacity-70 group-hover:opacity-100 transition-opacity">
          {subtitle}
        </p>
      {/if}
    </div>
  </div>

  <div class="absolute bottom-0 left-0 right-0 h-px bg-linear-to-r from-transparent via-hotel-border/50 to-transparent"></div>
</div>
