<script lang="ts">
  import { huespedesApi } from '$lib/services/huespedes';
  import { toast } from '$lib/stores/toast';

  let { id, esVip, onToggled }: {
    id:        number;
    esVip:     boolean;
    onToggled: (nuevoEstado: boolean) => void;
  } = $props();

  let cargando = $state(false);

  async function toggle(e: MouseEvent) {
    e.stopPropagation(); // Evitamos disparar el detalle de la fila/card
    if (cargando) return;
    
    cargando = true;
    const nuevoValor = !esVip;
    
    try {
      await huespedesApi.toggleVip(id, nuevoValor);
      onToggled(nuevoValor);
      toast.send(nuevoValor ? 'Huésped elevado a VIP' : 'Estatus VIP revocado', 'success');
    } catch {
      toast.send('Fallo en la actualización de estatus', 'error');
    } finally {
      cargando = false;
    }
  }
</script>

<button
  onclick={toggle}
  disabled={cargando}
  aria-pressed={esVip}
  class="group relative inline-flex items-center justify-center gap-2 min-w-85px px-3 py-1.5 rounded-full text-5px font-black
         uppercase tracking-0.1em border transition-all duration-500
         disabled:opacity-40 disabled:cursor-wait
         {esVip
           ? 'bg-hotel-vip/10 border-hotel-vip/30 text-hotel-vip-light hover:bg-hotel-error/5 hover:border-hotel-error/30 hover:text-hotel-error-light shadow-[0_0_10px_rgba(var(--color-vip),0.1)]'
           : 'bg-hotel-bg border-hotel-border text-hotel-text-tertiary hover:border-hotel-vip/50 hover:text-hotel-vip-light hover:shadow-hotel-sm'}"
>
  {#if cargando}
    <div class="w-3 h-3 border-2 border-current/20 border-t-current rounded-full animate-spin"></div>
  {:else}
    <svg 
      class="w-3.5 h-3.5 transition-all duration-500 {esVip ? 'fill-hotel-vip animate-pulse' : 'fill-transparent stroke-current stroke-[1.5px] group-hover:fill-hotel-vip/20'}" 
      viewBox="0 0 24 24"
    >
      <path d="M5 16L3 5L8.5 10L12 4L15.5 10L21 5L19 16H5ZM19 19C19 19.5523 18.5523 20 18 20H6C5.44772 20 5 19.5523 5 19V18H19V19Z" />
    </svg>
  {/if}

  <div class="relative overflow-hidden h-3 flex items-center">
    {#if cargando}
      <span class="animate-pulse">...</span>
    {:else if esVip}
      <span class="inline-flex text-sm transition-transform duration-300 group-hover:-translate-y-4">VIP</span>
      <span class="absolute text-sm translate-y-4 transition-transform duration-300 group-hover:translate-y-0 text-hotel-error-light">Quitar</span>
    {:else}
      <span class="inline-flex text-sm transition-transform duration-300 group-hover:-translate-y-4">Estándar</span>
      <span class="absolute text-sm translate-y-4 transition-transform duration-300 group-hover:translate-y-0 text-hotel-vip-light">+ VIP</span>
    {/if}
  </div>
</button>

<style>
  /* Animación sutil de respiración para el botón VIP activo */
  button[aria-pressed="true"]:not(:hover) {
    animation: vip-glow 3s infinite ease-in-out;
  }

  @keyframes vip-glow {
    0%, 100% { border-color: rgba(var(--color-vip), 0.3); }
    50% { border-color: rgba(var(--color-vip), 0.6); }
  }
</style>