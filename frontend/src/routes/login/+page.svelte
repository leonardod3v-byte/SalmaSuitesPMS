<script lang="ts">
  import { onMount } from 'svelte';
  import { auth } from '$stores/auth.svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { toast } from '$lib/stores/toast';
  import Button from '$components/ui/Button.svelte';
  import InputHotel from '$components/ui/Input.svelte';
  import CardHotel from '$components/ui/Card.svelte';

  let username = $state('');
  let password = $state('');
  let error = $state('');
  let loading = $state(false);
  let successMsg = $state('');
  let mounted = $state(false);
  let mostrarPassword = $state(false);

  onMount(() => {
    mounted = true;
    if ($page.url.searchParams.get('passwordChanged') === 'true') {
      successMsg = 'Contraseña actualizada correctamente. Inicia sesión.';
    }
  });

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    loading = true;
    error = '';
    successMsg = '';

    try {
      await auth.login(username, password);
      sessionStorage.setItem('justLoggedIn', 'true');

      const redirectTo = typeof window !== 'undefined'
        ? sessionStorage.getItem('redirect_to')
        : null;

      if (redirectTo) {
        sessionStorage.removeItem('redirect_to');
        goto(redirectTo, { replaceState: true });
      } else {
        goto('/dashboard', { replaceState: true });
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        error = err.message;
        toast.error(err.message);
      } else {
        error = 'Credenciales incorrectas o error de servidor';
        toast.error('Credenciales incorrectas o error de servidor');
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
    bg-size-[60px_60px] mask-[radial-gradient(ellipse_at_center,black_20%,transparent_80%)]">
  </div>

  <div class="relative w-full max-w-md transition-opacity duration-500 {mounted ? 'opacity-100' : 'opacity-0'}">

    <div class="flex items-center justify-center gap-2 mb-10">
      <div class="flex items-center justify-center w-13 h-13">
        <img src="/favicon.svg" alt="Logo SalmaSuites" class="w-full h-full object-contain" />
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

        <div class="space-y-5">
          <InputHotel
            label="Nombre de Usuario"
            placeholder="Ej: recepcion_01"
            bind:value={username}
            error={error}
            required
            autocomplete="username"
          />

          <div class="space-y-2 w-full">
            <label for="password-input" class="block text-sm font-medium tracking-wide text-hotel-text-secondary select-none">
              Contraseña <span class="text-hotel-gold ml-0.5">*</span>
            </label>
            <div class="relative group">
              <input
                id="password-input"
                type={mostrarPassword ? 'text' : 'password'}
                placeholder="••••••••"
                bind:value={password}
                required
                autocomplete="current-password"
                class="w-full rounded-lg px-4 py-3.5 pr-12 text-sm transition-all duration-200 bg-hotel-bg text-hotel-text-primary outline-none border border-hotel-border focus:border-hotel-gold focus:ring-4 focus:ring-hotel-gold/10 hover:border-hotel-gold-dark"
              />
              <button
                type="button"
                onclick={() => mostrarPassword = !mostrarPassword}
                class="absolute right-3 top-1/2 -translate-y-1/2 text-hotel-text-tertiary hover:text-hotel-gold transition-colors focus:outline-none"
                aria-label={mostrarPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
              >
                {#if mostrarPassword}
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                {:else}
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                {/if}
              </button>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-end text-xs">
          <a href="/recuperar" class="font-bold text-hotel-gold hover:text-hotel-gold-light transition-colors">
            Recuperar acceso
          </a>
        </div>

        <Button type="submit" variant="gold" fullWidth loading={loading}>
          Acceder al Panel
        </Button>
      </form>
    </CardHotel>

    <footer class="mt-8 text-center space-y-2">
      <p class="text-[10px] text-hotel-text-tertiary font-medium uppercase tracking-widest">
        © 2026 Hotel Salma Suites VIP, C.A · Solo personal autorizado.
      </p>
    </footer>
  </div>
</div>
