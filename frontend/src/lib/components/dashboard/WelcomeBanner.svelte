<script lang="ts">
  import { auth } from '$stores/auth.svelte';
  import { onMount } from 'svelte';
  import Icon from '$components/ui/Icons.svelte';

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

  const timeString = $derived(time.toLocaleTimeString('es-VE', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }));

  const fechaRaw = new Date().toLocaleDateString('es-VE', {
    weekday: 'long', day: 'numeric', month: 'long'
  });
  const fecha = fechaRaw.charAt(0).toUpperCase() + fechaRaw.slice(1);

  const hora = new Date().getHours();
  const saludo = hora < 12 ? 'Buenos días' : hora < 18 ? 'Buenas tardes' : 'Buenas noches';
</script>

<div class="relative rounded-2xl p-6 md:p-8 overflow-hidden border border-hotel-border bg-hotel-surface shadow-hotel-lg group hover:border-hotel-gold/30 transition-all duration-500">
  <div class="absolute -top-32 -right-32 w-96 h-96 bg-hotel-gold/5 rounded-full blur-3xl pointer-events-none group-hover:bg-hotel-gold/10 transition-all duration-700"></div>
  <div class="absolute -bottom-20 -left-20 w-64 h-64 bg-hotel-gold/5 rounded-full blur-3xl pointer-events-none"></div>

  <div class="relative flex flex-col lg:flex-row lg:items-center justify-between gap-6 lg:gap-8">

    <div class="flex-1 space-y-4">
      <div class="space-y-1">
        <p class="text-[10px] uppercase tracking-[0.25em] text-hotel-gold font-black">
          Sistema de Gestión Hotelera
        </p>
        <h2 class="font-display text-3xl md:text-4xl text-hotel-text-primary leading-tight">
          {saludo}, <span class="font-bold">{auth.user?.username || 'Admin'}</span>
        </h2>
        <p class="text-sm text-hotel-text-secondary">
          {auth.user?.role === 'admin' ? 'Administrador' : 'Recepcionista'}
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-hotel-bg/50 border border-hotel-border/50">
          <Icon name="calendar" class="w-3.5 h-3.5 text-hotel-gold" />
          <span class="text-xs font-medium text-hotel-text-secondary">{fecha}</span>
        </div>

        <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-hotel-success/5 border border-hotel-success/20">
          <Icon name="checkIn" class="w-3.5 h-3.5 text-hotel-success-light" />
          <span class="text-xs font-bold text-hotel-success-light">{stats.checkIns}</span>
          <span class="text-[9px] uppercase tracking-wider text-hotel-success-light/70">Check-In</span>
        </div>

        <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-hotel-error/5 border border-hotel-error/20">
          <Icon name="checkOut" class="w-3.5 h-3.5 text-hotel-error-light" />
          <span class="text-xs font-bold text-hotel-error-light">{stats.checkOuts}</span>
          <span class="text-[9px] uppercase tracking-wider text-hotel-error-light/70">Check-Out</span>
        </div>
      </div>
    </div>

    <div class="flex items-center gap-4 lg:gap-6 shrink-0">
      <div class="h-16 w-px bg-linear-to-b from-transparent via-hotel-border to-transparent hidden lg:block"></div>
      <div class="text-left lg:text-right">
        <div class="font-mono text-4xl md:text-5xl text-hotel-text-primary tracking-tighter tabular-nums leading-none">
          {timeString}
        </div>
        <div class="flex items-center lg:justify-end gap-2 mt-2">
          <span class="text-[9px] uppercase font-bold tracking-[0.2em] text-hotel-gold-light">En Vivo</span>
          <div class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-hotel-success opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-hotel-success"></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
