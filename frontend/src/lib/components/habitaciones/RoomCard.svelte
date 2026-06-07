<script lang="ts">
  import Icon from '$lib/components/Icons.svelte';

  let { hab, onclick } = $props();

  const ESTADOS = {
    libre:         { label: 'Disponible', color: 'var(--color-hotel-success-light)', bg: 'rgba(45,106,79,0.1)' },
    limpia:        { label: 'Limpia',     color: 'var(--color-hotel-success-light)', bg: 'rgba(45,106,79,0.1)' },
    sucia:         { label: 'Sucia',      color: 'var(--color-hotel-gold)',        bg: 'rgba(179,142,93,0.1)' },
    ocupada:       { label: 'Ocupada',    color: 'var(--color-hotel-error-light)', bg: 'rgba(155,34,38,0.1)' },
    mantenimiento: { label: 'Mantenimiento', color: 'var(--color-hotel-vip-light)', bg: 'rgba(88,47,126,0.1)' },
    construccion:  { label: 'Obra',       color: 'var(--color-hotel-text-tertiary)', bg: 'rgba(130,112,102,0.1)' },
  };

  const cfg = $derived(ESTADOS[hab.estado] ?? ESTADOS.libre);
  const tipoLabel = $derived(hab.tipo_nombre ?? hab.tipo_display ?? 'Standard Suite');
  
  const roomImage = "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&q=80&w=400";
</script>

<button
  class="group relative flex flex-col w-full bg-hotel-surface border border-hotel-border rounded-xl overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:border-hotel-gold/50 hover:shadow-hotel-lg"
  {onclick}
  aria-label="Habitación {hab.numero}"
>
  <div class="relative h-32 w-full overflow-hidden">
    <img 
      src={roomImage} 
      alt="Habitación {tipoLabel}" 
      loading="lazy" 
      class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
    />
    <div class="absolute inset-0 bg-linear-to-t from-black/80 to-transparent"></div>
    
    <div 
      class="absolute top-3 right-3 px-2 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider backdrop-blur-md border"
      style="background: {cfg.bg}; color: {cfg.color}; border-color: {cfg.color}44"
    >
      {cfg.label}
    </div>

    <div class="absolute bottom-2 left-3">
      <span class="text-2xl font-display font-bold text-white italic">#{hab.numero}</span>
    </div>
  </div>

  <div class="p-3 flex flex-col gap-2">
    <div>
      <h3 class="text-xs font-bold text-hotel-text-secondary uppercase tracking-widest">{tipoLabel}</h3>
      <p class="text-[14px] text-hotel-text-tertiary">Piso {hab.piso}</p>
      <p class="text-sm font-bold text-hotel-gold mt-1">
        ${parseFloat(hab.tipo_precio).toFixed(2)} / noche
      </p>
    </div>

    <div class="flex gap-2 pt-2 border-t border-hotel-border/50">
      {#if hab.tiene_minibar}
        <div class="text-hotel-text-tertiary group-hover:text-hotel-gold transition-colors" title="Minibar">
          <Icon name="minibar" class="w-3.5 h-3.5" />
        </div>
      {/if}
      {#if hab.qr_code}
        <div class="text-hotel-text-tertiary group-hover:text-hotel-gold transition-colors" title="QR Smart Acceso">
          <Icon name="qr" class="w-3.5 h-3.5" />
        </div>
      {/if}
    </div>
  </div>
</button>