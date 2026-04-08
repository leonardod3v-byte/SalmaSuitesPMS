<script lang="ts">
  interface Props {
    title: string;
    value: string | number;
    subtitle?: string;
    icon: 'hotel' | 'calendar' | 'money' | 'crown';
    trend?: string;
    trendUp?: boolean;
    color?: 'gold' | 'success' | 'error' | 'vip';
  }

  let { 
    title, 
    value, 
    subtitle, 
    icon, 
    trend, 
    trendUp, 
    color = 'gold' 
  }: Props = $props();

  // Mapeo de clases de Tailwind según el color prop
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

  const icons = {
    hotel: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18M3 7v1a3 3 0 006 0V7m0 1a3 3 0 006 0V7m0 1a3 3 0 006 0V7M4 21V4a2 2 0 012-2h12a2 2 0 012 2v17M9 21v-4a2 2 0 012-2h2a2 2 0 012 2v4"/></svg>`,
    calendar: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`,
    money: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>`,
    crown: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 4l3 12h14l3-12-6 7-4-7-4 7-6-7z"/></svg>`
  };
</script>

<div class="group relative overflow-hidden rounded-2xl border border-hotel-border bg-hotel-surface p-5 transition-all duration-500 hover:-translate-y-1.5 hover:shadow-[0_20px_40px_-15px_rgba(0,0,0,0.5)]">
  
  <div class="absolute -right-4 -top-4 h-24 w-24 rounded-full blur-3xl transition-all duration-700 {glowMap[color]}"></div>

  <div class="relative flex flex-col gap-5">
    <div class="flex items-center justify-between">
      <div class="flex h-12 w-12 items-center justify-center rounded-xl border bg-hotel-bg/50 backdrop-blur-sm transition-all duration-500 group-hover:scale-110 group-hover:text-hotel-bg {colorMap[color]}">
        <div class="h-6 w-6">
          {@html icons[icon]}
        </div>
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

  <div class="absolute bottom-0 left-0 h-3px w-0 transition-all duration-700 group-hover:w-full"
       style="background: var(--color-hotel-{color === 'gold' ? 'gold' : color}); box-shadow: 0 0 15px var(--color-hotel-{color});">
  </div>
</div>