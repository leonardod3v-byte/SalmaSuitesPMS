<script lang="ts">
  import { goto } from '$app/navigation';
  import ButtonGold from '$lib/components/ButtonGold.svelte';
  import InputHotel from '$lib/components/InputHotel.svelte';
  import CardHotel from '$lib/components/CardHotel.svelte';

  // -- Constantes --
  const API_URL = 'http://localhost:8000/api';

  // -- Estado con Runas (Svelte 5) --
  let step = $state(1);
  let email = $state('');
  let code = $state('');
  let newPassword = $state('');
  let confirmPassword = $state('');
  let error = $state('');
  let message = $state('');
  let loading = $state(false);
  let tokens = $state<{ access: string; refresh: string } | null>(null);

  // -- Tipado del Helper Fetch --
  async function publicPost(endpoint: string, body: object, extraHeaders: Record<string, string> = {}) {
    const res = await fetch(`${API_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...extraHeaders },
      body: JSON.stringify(body)
    });
    
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || data.detail || `Error ${res.status}`);
    return data;
  }

  // -- Lógica de Fuerza de Contraseña (Derivada) --
  let passwordStrength = $derived(getPasswordStrength(newPassword));
  
  const strengthConfig = [
    { label: '', color: 'transparent' },
    { label: 'Crítica', color: 'var(--color-hotel-error)' },
    { label: 'Insegura', color: '#E07C2A' },
    { label: 'Moderada', color: '#D9C5A3' },
    { label: 'Recomendada', color: 'var(--color-hotel-gold)' },
    { label: 'Excelente', color: '#4CAF82' }
  ];

  function getPasswordStrength(pwd: string): number {
    if (!pwd) return 0;
    let score = 0;
    if (pwd.length >= 8) score++;
    if (pwd.length >= 12) score++;
    if (/[A-Z]/.test(pwd)) score++;
    if (/[0-9]/.test(pwd)) score++;
    if (/[^A-Za-z0-9]/.test(pwd)) score++;
    return score;
  }

  // -- Manejadores de Eventos Tipados --
  async function handleRequestCode(e: SubmitEvent) {
    e.preventDefault();
    loading = true; error = ''; message = '';
    try {
      const data = await publicPost('/auth/password-reset/request/', { email });
      message = data.message;
      step = 2;
    } catch (err: any) {
      error = err.message || 'Error al enviar el código';
    } finally {
      loading = false;
    }
  }

  async function handleVerifyCode(e: SubmitEvent) {
    e.preventDefault();
    loading = true; error = '';
    try {
      const data = await publicPost('/auth/password-reset/verify/', { email, code });
      if (!data.valid) throw new Error('El código no es válido');
      tokens = { access: data.access, refresh: data.refresh };
      step = 3;
    } catch (err: any) {
      error = err.message || 'Código inválido';
    } finally {
      loading = false;
    }
  }

  async function handleResetPassword(e: SubmitEvent) {
    e.preventDefault();
    error = '';
    if (newPassword !== confirmPassword) { error = 'Las contraseñas no coinciden'; return; }
    if (newPassword.length < 8) { error = 'Mínimo 8 caracteres requeridos'; return; }

    loading = true;
    try {
      await publicPost(
        '/auth/password-reset/reset/',
        { email, new_password: newPassword, token: tokens?.access },
        { 'Authorization': `Bearer ${tokens?.access}` }
      );
      goto('/login?passwordChanged=true', { replaceState: true });
    } catch (err: any) {
      error = err.message || 'Error al actualizar';
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Recuperar Acceso | SalmaSuitesPMS</title>
</svelte:head>

<div class="min-h-screen bg-hotel-bg relative overflow-hidden flex items-center justify-center p-4">
  
  <div class="absolute inset-0 bg-gradient-radial pointer-events-none opacity-40"></div>
  <div class="absolute -top-20 left-1/3 w-96 h-96 rounded-full bg-hotel-gold/5 blur-[120px] pointer-events-none"></div>
  
  <div class="absolute inset-0 pointer-events-none opacity-20 
    bg-[linear-gradient(var(--color-hotel-gold)_1px,transparent_1px),linear-gradient(90deg,var(--color-hotel-gold)_1px,transparent_1px)]
    bg-size[60px_60px] mask-[radial-gradient(ellipse_at_center,black_20%,transparent_80%)]">
  </div>

  <div class="relative w-full max-w-md">
    <div class="flex items-center justify-center gap-4 mb-10">
      <div class="flex items-center justify-center w-14 h-14 rounded-2xl bg-linear-to-br from-hotel-gold to-hotel-gold-dark shadow-hotel-gold">
        <svg class="w-8 h-8 text-hotel-bg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
        </svg>
      </div>
      <div class="space-y-0.5">
        <h1 class="font-display text-3xl font-bold tracking-tighter text-hotel-text-primary uppercase">Recuperar Acceso</h1>
        <p class="text-[10px] tracking-[0.3em] uppercase text-hotel-text-tertiary font-bold">Seguridad del Sistema</p>
      </div>
    </div>

    <CardHotel>
      <div class="p-2 space-y-6">
        <header class="space-y-1.5">
          <h2 class="font-display text-2xl text-hotel-text-primary italic">
            {#if step === 1}Identidad{:else if step === 2}Seguridad{:else}Protección{/if}
          </h2>
          <p class="text-[11px] text-hotel-text-tertiary uppercase tracking-wider font-semibold">
            {#if step === 1}Paso 1: Solicitud de código{:else if step === 2}Paso 2: Código enviado a su casilla{:else}Paso 3: Nueva llave de acceso{/if}
          </p>
        </header>

        {#if step === 1}
          <form onsubmit={handleRequestCode} class="space-y-6">
            <InputHotel type="email" label="Correo electrónico" placeholder="usuario@gmail.com" bind:value={email} error={error} required />
            <ButtonGold type="submit" {loading} fullWidth>Enviar Código</ButtonGold>
          </form>
        {:else if step === 2}
          <form onsubmit={handleVerifyCode} class="space-y-6">
            <div class="space-y-3">
              <label 
                for="otp-code" 
                class="text-xs font-bold uppercase tracking-widest text-hotel-text-tertiary px-1"
              >
                Código de 6 dígitos
              </label>
              <input 
                id="otp-code"
                type="text" 
                inputmode="numeric" 
                bind:value={code} 
                placeholder="000000" 
                maxlength="6" 
                required 
                class="w-full bg-hotel-bg border border-hotel-border rounded-xl py-4 text-center text-3xl tracking-[0.5em] font-bold text-hotel-gold focus:border-hotel-gold focus:ring-4 focus:ring-hotel-gold/10 transition-all outline-none" 
              />
            </div>
            {#if error}<p class="text-xs text-hotel-error-light bg-hotel-error/10 p-3 rounded-lg border border-hotel-error/20 text-center italic">{error}</p>{/if}
            <ButtonGold type="submit" {loading} fullWidth>Validar Identidad</ButtonGold>
            <button type="button" onclick={() => step = 1} class="w-full text-[10px] uppercase font-black text-hotel-text-tertiary hover:text-hotel-gold transition-colors tracking-widest">¿No recibió el correo? Reintentar</button>
          </form>
        {:else}
          <form onsubmit={handleResetPassword} class="space-y-5">
            <InputHotel type="password" label="Nueva Contraseña" bind:value={newPassword} required />
            
            {#if newPassword}
              <div class="space-y-2 px-1">
                <div class="flex gap-1.5">
                  {#each Array(5) as _, i}
                    <div class="h-1 flex-1 rounded-full bg-hotel-border overflow-hidden">
                      <div class="h-full transition-all duration-500" style="width: {i < passwordStrength ? '100%' : '0%'}; background: {strengthConfig[passwordStrength].color}"></div>
                    </div>
                  {/each}
                </div>
                <p class="text-[10px] font-bold uppercase tracking-tighter" style="color: {strengthConfig[passwordStrength].color}">{strengthConfig[passwordStrength].label}</p>
              </div>
            {/if}

            <InputHotel type="password" label="Confirmar Contraseña" bind:value={confirmPassword} error={error} required />
            <ButtonGold type="submit" {loading} fullWidth>Actualizar Llave</ButtonGold>
          </form>
        {/if}

        <div class="pt-4 border-t border-hotel-border/50 text-center">
          <a href="/login" class="text-xs font-bold text-hotel-text-secondary hover:text-hotel-gold transition-colors uppercase tracking-widest italic">← Retornar al Acceso Principal</a>
        </div>
      </div>
    </CardHotel>

    <div class="mt-8 flex flex-col items-center gap-3">
      <div class="flex gap-3">
        {#each [1, 2, 3] as s}
          <div class="h-1.5 rounded-full transition-all duration-500 {step === s ? 'w-10 bg-hotel-gold' : step > s ? 'w-6 bg-hotel-gold-dark' : 'w-6 bg-hotel-border'}"></div>
        {/each}
      </div>
    </div>
  </div>
</div>

<style>
  :global(.font-display) { font-family: var(--font-display); }
</style>