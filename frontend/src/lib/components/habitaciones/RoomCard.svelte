<script lang="ts">
  import Icon from '$lib/components/Icons.svelte';

  let { hab, onclick } = $props();

  type EstadoHabitacion = 'libre' | 'limpia' | 'sucia' | 'ocupada' | 'mantenimiento' | 'construccion';

  const ESTADOS = {
    libre:         { label: 'Disponible', color: 'var(--color-hotel-success-light)', bg: 'rgba(45,106,79,0.1)' },
    limpia:        { label: 'Limpia',     color: 'var(--color-hotel-success-light)', bg: 'rgba(45,106,79,0.1)' },
    sucia:         { label: 'Sucia',      color: 'var(--color-hotel-gold)',        bg: 'rgba(179,142,93,0.1)' },
    ocupada:       { label: 'Ocupada',    color: 'var(--color-hotel-error-light)', bg: 'rgba(155,34,38,0.1)' },
    mantenimiento: { label: 'Mantenimiento', color: 'var(--color-hotel-vip-light)', bg: 'rgba(88,47,126,0.1)' },
    construccion:  { label: 'Obra',       color: 'var(--color-hotel-text-tertiary)', bg: 'rgba(130,112,102,0.1)' },
  };

  const cfg = $derived(ESTADOS[hab.estado as EstadoHabitacion] ?? ESTADOS.libre);
  const tipoLabel = $derived(hab.tipo_nombre ?? 'Standard Suite');
  const precioFormateado = $derived(
    hab.tipo_precio?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) ?? '0.00'
  );
  const capacidadTexto = $derived(hab.capacidad_maxima ? `${hab.capacidad_maxima} pers.` : 'N/A');

  const roomImage = "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&q=80&w=600";
</script>

<button
  class="group relative flex flex-col w-full bg-hotel-surface border border-hotel-border rounded-2xl overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:border-hotel-gold/50 hover:shadow-hotel-lg focus:outline-none focus:ring-2 focus:ring-hotel-gold/50"
  {onclick}
  aria-label="Habitación {hab.numero}"
>
  <!-- Imagen más alta para dar protagonismo -->
  <div class="relative h-48 w-full overflow-hidden">
    <img 
      src={roomImage} 
      alt="Habitación {tipoLabel}" 
      loading="lazy" 
      class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
    />
    <div class="absolute inset-0 bg-linear-to-t from-black/80 via-black/30 to-transparent"></div>
    
    <!-- Badge de estado -->
    <div 
      class="absolute top-4 right-4 px-3 py-1.5 rounded-full text-[11px] font-bold uppercase tracking-wider backdrop-blur-md border shadow-sm"
      style="background: {cfg.bg}; color: {cfg.color}; border-color: {cfg.color}66"
    >
      {cfg.label}
    </div>

    <!-- Número de habitación (más grande) y piso -->
    <div class="absolute bottom-4 left-4">
      <span class="text-4xl font-display font-bold text-white italic drop-shadow-md">#{hab.numero}</span>
      <div class="flex items-center gap-1 mt-1 text-white/80 text-xs">
        <Icon name="habitaciones" class="w-3.5 h-3.5" />
        <span>Piso {hab.piso}</span>
      </div>
    </div>
  </div>

  <!-- Información detallada con más espacio -->
  <div class="p-5 flex flex-col gap-4">
    <div class="flex justify-between items-start">
      <div class="flex-1">
        <h3 class="text-xs font-bold text-hotel-text-primary tracking-wide text-left">{tipoLabel}</h3>
        <div class="flex items-center gap-4 mt-2 text-sm text-hotel-text-tertiary">
          <span class="flex items-center gap-1.5">
            <Icon name="huespedes" class="w-4 h-4" />
            <span>{capacidadTexto}</span>
          </span>
          <!-- Puedes agregar aquí otros campos como vistas, wifi, etc. si los tuvieras -->
        </div>
      </div>
      <div class="text-right">
        <p class="text-2xl font-bold text-hotel-gold leading-tight">${precioFormateado}</p>
        <p class="text-[10px] text-hotel-text-tertiary uppercase tracking-wider">/ noche</p>
      </div>
    </div>

    <!-- Amenidades -->
    <div class="flex items-center gap-4 pt-3 border-t border-hotel-border/60">
      {#if hab.tiene_minibar}
        <div class="flex items-center gap-1.5 text-hotel-text-secondary group-hover:text-hotel-gold transition-colors" title="Minibar">
          <Icon name="minibar" class="w-4.5 h-4.5" />
          <span class="text-xs font-medium uppercase tracking-wide">Minibar</span>
        </div>
      {/if}
      <!-- Si no hay amenidades, se puede dejar un espacio vacío o no mostrar nada -->
    </div>
  </div>
</button>