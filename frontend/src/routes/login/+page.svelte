<script lang="ts">
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import ButtonGold from '$lib/components/ButtonGold.svelte';
  import InputHotel from '$lib/components/InputHotel.svelte';
  import CardHotel from '$lib/components/CardHotel.svelte';

  // -- Estado con Runas --
  let username = $state('');
  let password = $state('');
  let error = $state('');
  let loading = $state(false);
  let successMsg = $state('');
  let mounted = $state(false);

  onMount(() => {
    mounted = true;
    if ($page.url.searchParams.get('passwordChanged') === 'true') {
      successMsg = 'Contraseña actualizada correctamente. Inicia sesión.';
    }
  });

  // SOLUCIÓN ERROR 1: Tipamos el evento como 'SubmitEvent'
  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    loading = true;
    error = '';
    successMsg = '';

    try {
      await auth.login(username, password);
      sessionStorage.setItem('justLoggedIn', 'true');
      goto('/dashboard', { replaceState: true });
    } catch (err: unknown) {
      // SOLUCIÓN ERROR 2: Verificamos si err es una instancia de Error
      if (err instanceof Error) {
        error = err.message;
      } else {
        error = 'Credenciales incorrectas o error de servidor';
      }
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Acceso | SalmaSuitesPMS</title>
</svelte:head>

<div class="min-h-screen bg-hotel-bg relative overflow-hidden flex items-center justify-center p-4">
  
  <div class="absolute inset-0 bg-gradient-radial pointer-events-none opacity-50"></div>
  <div class="absolute -top-20 left-1/4 w-96 h-96 rounded-full bg-hotel-gold/5 blur-[120px] pointer-events-none"></div>
  <div class="absolute bottom-0 right-1/4 w-64 h-64 rounded-full bg-hotel-gold/5 blur-[90px] pointer-events-none"></div>

  <div class="absolute inset-0 pointer-events-none opacity-20 
    bg-[linear-gradient(var(--color-hotel-gold)_1px,transparent_1px),linear-gradient(90deg,var(--color-hotel-gold)_1px,transparent_1px)]
    bg-size[60px_60px] mask-[radial-gradient(ellipse_at_center,black_20%,transparent_80%)]">
  </div>

  <div class="relative w-full max-w-md transition-opacity duration-500 {mounted ? 'opacity-100' : 'opacity-0'}">
    
    <div class="flex items-center justify-center gap-4 mb-10">
      <div class="flex items-center justify-center w-14 h-14 rounded-2xl bg-linear-to-br from-hotel-gold to-hotel-gold-dark shadow-hotel-gold">
        <svg class="w-8 h-8 text-hotel-bg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
        </svg>
      </div>

      <div class="space-y-0.5">
        <h1 class="font-display text-4xl font-bold tracking-tighter text-hotel-text-primary">
          SalmaSuites<span class="text-hotel-gold">VIP</span>
        </h1>
        <p class="text-[10px] tracking-[0.3em] uppercase text-hotel-text-tertiary font-bold">
          Property Management System
        </p>
      </div>
    </div>

    <CardHotel>
      <form onsubmit={handleSubmit} class="space-y-6 p-2">
        <div class="space-y-1">
          <h2 class="font-display text-2xl text-hotel-text-primary italic">Bienvenido</h2>
          <p class="text-xs text-hotel-text-tertiary uppercase tracking-wider font-medium">Gestión de Acceso Autorizado</p>
        </div>

        {#if successMsg}
          <div class="flex items-center gap-3 text-sm rounded-xl px-4 py-3 bg-hotel-success/10 border border-hotel-success/20 text-hotel-success-light animate-in zoom-in-95 duration-300">
            <svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
            {successMsg}
          </div>
        {/if}

        <div class="space-y-5">
          <InputHotel
            label="Nombre de Usuario"
            placeholder="Ej: recepcion_01"
            bind:value={username}
            error={error}
            required
            autocomplete="username"
          />
          <InputHotel
            type="password"
            label="Contraseña"
            placeholder="••••••••"
            bind:value={password}
            required
            autocomplete="current-password"
          />
        </div>

        <div class="flex items-center justify-between text-xs">
          <label class="flex items-center gap-2 cursor-pointer group text-hotel-text-secondary hover:text-hotel-gold transition-colors">
            <input type="checkbox" class="w-4 h-4 rounded border-hotel-border bg-hotel-bg text-hotel-gold focus:ring-hotel-gold" />
            Mantener sesión
          </label>
          <a href="/recuperar" class="font-bold text-hotel-gold hover:text-hotel-gold-light transition-colors">
            Recuperar acceso
          </a>
        </div>

        <ButtonGold type="submit" {loading} fullWidth>
          Acceder al Panel
        </ButtonGold>
      </form>
    </CardHotel>

    <footer class="mt-8 text-center space-y-2">
      <p class="text-[10px] text-hotel-text-tertiary font-medium uppercase tracking-widset">
        © 2026 Salma Suite VIP · Solo personal autorizado.
      </p>
    </footer>
  </div>
</div>

<style>
  :global(.font-display) {
    font-family: var(--font-display);
  }
</style>