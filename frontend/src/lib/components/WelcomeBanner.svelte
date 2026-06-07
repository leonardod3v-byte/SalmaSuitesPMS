<script lang="ts">
  import { auth } from '$lib/stores/auth';
  import { onMount } from 'svelte';
  import Icon from '$lib/components/Icons.svelte';

  interface Props {
    stats?: {
      checkIns: number;
      checkOuts: number;
    };
  }

  let { stats = { checkIns: 0, checkOuts: 0 } }: Props = $props();

  let time = $state(new Date());
  
  onMount(() => {
    const interval = setInterval(() => { time = new Date(); }, 1000);
    return () => clearInterval(interval);
  });

  const timeString = $derived(time.toLocaleTimeString('es-ES', { 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit' 
  }));

  const fechaRaw = new Date().toLocaleDateString('es-ES', {
    weekday: 'long', day: 'numeric', month: 'long'
  });
  const fecha = fechaRaw.charAt(0).toUpperCase() + fechaRaw.slice(1);

  const hora = new Date().getHours();
  const saludo = hora < 12 ? 'Buenos días' : hora < 18 ? 'Buenas tardes' : 'Buenas noches';
</script>

<div class="relative rounded-2xl p-8 overflow-hidden border border-hotel-border bg-linear-to-br from-hotel-gold/10 via-hotel-surface to-hotel-bg shadow-hotel-lg">
  <div class="relative flex flex-col md:flex-row md:items-center justify-between gap-8">
    <div class="space-y-4">
      <div class="space-y-1">
        <p class="text-[10px] uppercase tracking-[0.2em] text-hotel-gold font-bold">Sistema de Gestión Hotelera</p>
        <h2 class="font-display text-3xl md:text-4xl text-hotel-text-primary">
          {saludo}, <span class="font-bold">{$auth.user?.username || 'Admin'}</span>
        </h2>
      </div>

      <div class="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
        <span class="text-hotel-text-secondary font-medium">{fecha}</span>
        <div class="h-4 w-px bg-hotel-border hidden sm:block"></div>
        <div class="flex items-center gap-4">
          <span class="flex items-center gap-1.5 text-hotel-success-light font-bold">
            <Icon name="checkIn" class="w-3.5 h-3.5" />
            {stats.checkIns} <span class="text-[10px] uppercase tracking-tighter opacity-70">Check-In</span>
          </span>
          <span class="flex items-center gap-1.5 text-hotel-error-light font-bold">
            <Icon name="checkOut" class="w-3.5 h-3.5" />
            {stats.checkOuts} <span class="text-[10px] uppercase tracking-tighter opacity-70">Check-Out</span>
          </span>
        </div>
      </div>
    </div>

    <div class="flex items-center gap-6 pr-4">
      <div class="h-12 w-px bg-linear-to-b from-transparent via-hotel-border to-transparent hidden md:block"></div>
      <div class="text-right">
        <div class="font-mono text-3xl text-hotel-text-primary tracking-tighter tabular-nums">
          {timeString}
        </div>
        <div class="flex items-center justify-end gap-2 text-hotel-text-tertiary">
          <span class="text-[10px] uppercase font-bold tracking-widest text-hotel-gold-light">En Vivo</span>
          <div class="w-1.5 h-1.5 rounded-full bg-hotel-success animate-pulse"></div>
        </div>
      </div>
    </div>
  </div>
</div>