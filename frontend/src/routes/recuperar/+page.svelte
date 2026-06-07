<script lang="ts">
  import CardHotel from '$lib/components/CardHotel.svelte';
  import InputHotel from '$lib/components/InputHotel.svelte';
  import Button from '$lib/components/Button.svelte';

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

  // Control de Flujo Lógico y Estados
  let step = 1; 
  let loading = false;
  let error = '';
  let successMessage = '';

  // Data Payloads para la API
  let email = '';
  let code = '';
  let newPassword = '';
  let confirmPassword = '';
  let verifiedToken = ''; // Token de un solo uso entregado por el Paso 2

  // Configuración Estética del Medidor de Fuerza (Intacta)
  const strengthConfig = {
    0: { label: 'Insegura', color: '#ef4444' },
    1: { label: 'Débil', color: '#f97316' },
    2: { label: 'Moderada', color: '#eab308' },
    3: { label: 'Sólida', color: '#22c55e' }
  };

  $: passwordStrength = (() => {
    if (!newPassword) return 0;
    let score = 0;
    if (newPassword.length >= 8) score++;
    if (/[A-Z]/.test(newPassword) && /[a-z]/.test(newPassword)) score++;
    if (/[0-9]/.test(newPassword) || /[^A-Za-z0-9]/.test(newPassword)) score++;
    return score as 0 | 1 | 2 | 3;
  })();

  // PASO 1: Solicitar Código de Verificación
  async function handleRequestCode() {
    loading = true;
    error = '';
    try {
      const res = await fetch(`${API_URL}/users/request-password-reset/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      const data = await res.json().catch(() => ({}));

      if (!res.ok) throw new Error(data.error || 'Error al solicitar el código.');

      successMessage = 'Código enviado. Revisa tu bandeja de entrada.';
      step = 2; // Transición visual al paso 2
    } catch (err: any) {
      error = err.message || 'Error de conexión con el servidor.';
    } finally {
      loading = false;
    }
  }

  // PASO 2: Verificar Código de 6 Dígitos
  async function handleVerifyCode() {
    loading = true;
    error = '';
    try {
      const res = await fetch(`${API_URL}/users/verify-reset-code/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, code })
      });
      const data = await res.json().catch(() => ({}));

      if (!res.ok) throw new Error(data.error || 'Código incorrecto o expirado.');

      verifiedToken = data.token; // Almacenamos el token de validación efímero en memoria
      successMessage = 'Código verificado con éxito. Define tu nueva contraseña.';
      step = 3; // Transición visual al paso 3
    } catch (err: any) {
      error = err.message || 'Error al verificar el código.';
    } finally {
      loading = false;
    }
  }

  // PASO 3: Mutación y Reestablecimiento Definitivo de Contraseña
  async function handleResetPassword() {
    if (newPassword !== confirmPassword) {
      error = 'Las contraseñas no coinciden.';
      return;
    }
    if (newPassword.length < 8) {
      error = 'La contraseña debe contener al menos 8 caracteres.';
      return;
    }

    loading = true;
    error = '';
    try {
      const res = await fetch(`${API_URL}/users/reset-password/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          new_password: newPassword,
          token: verifiedToken
        })
      });
      const data = await res.json().catch(() => ({}));

      if (!res.ok) throw new Error(data.error || 'No se pudo actualizar la contraseña.');

      successMessage = 'Tu llave de acceso ha sido restablecida correctamente.';
      // Redirección limpia manejada por SvelteKit después de 2 segundos para dar feedback visual
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
    } catch (err: any) {
      error = err.message || 'Error al reestablecer la contraseña.';
    } finally {
      loading = false;
    }
  }
</script>

<div class="min-h-screen bg-hotel-bg flex flex-col justify-center items-center px-4 relative overflow-hidden select-none">
  <div class="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] bg-hotel-gold/5 rounded-full blur-[120px] pointer-events-none animate-pulse-slow"></div>
  <div class="absolute bottom-[-20%] right-[-10%] w-[600px] h-[600px] bg-hotel-gold/5 rounded-full blur-[120px] pointer-events-none animate-pulse-slow" style="animation-delay: 3s;"></div>

  <div class="w-full max-w-[440px] z-10 animate-fade-in">
    <div class="flex flex-col items-center mb-8">
      <div class="w-16 h-16 rounded-full border border-hotel-gold/30 flex items-center justify-center bg-hotel-card-bg/50 backdrop-blur-md shadow-lg shadow-hotel-gold/5 mb-4 group hover:border-hotel-gold transition-all duration-500">
        <svg class="w-7 h-7 text-hotel-gold group-hover:scale-110 transition-transform duration-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
        </svg>
      </div>
      <h1 class="text-2xl font-light text-hotel-text tracking-[0.2em] uppercase text-center">Bóveda de Seguridad</h1>
      <p class="text-[10px] font-bold text-hotel-gold tracking-[0.3em] uppercase mt-2 italic">Restauración de Credenciales</p>
    </div>

    <CardHotel>
      <div class="p-8 flex flex-col gap-6">
        {#if error}
          <div class="p-4 bg-red-950/30 border border-red-500/30 rounded-lg flex items-center gap-3 animate-shake">
            <svg class="w-5 h-5 text-red-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            <p class="text-xs text-red-200 font-medium">{error}</p>
          </div>
        {/if}

        {#if successMessage && !error}
          <div class="p-4 bg-emerald-950/30 border border-emerald-500/30 rounded-lg flex items-center gap-3 animate-fade-in">
            <svg class="w-5 h-5 text-emerald-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0x"/>
            </svg>
            <p class="text-xs text-emerald-200 font-medium">{successMessage}</p>
          </div>
        {/if}

        {#if step === 1}
          <p class="text-xs text-hotel-text-secondary leading-relaxed text-center">
            Introduce el correo institucional asociado a tu cuenta. Te remitiremos una llave numérica de verificación efímera.
          </p>
          <form on:submit|preventDefault={handleRequestCode} class="flex flex-col gap-5">
            <InputHotel type="email" label="Correo Electrónico" bind:value={email} required placeholder="ejemplo@hotel.com" />
            <Button type="submit" variant="gold" fullWidth loading={loading}>Despachar Código</Button>
          </form>

        {:else if step === 2}
          <p class="text-xs text-hotel-text-secondary leading-relaxed text-center">
            Hemos enviado un código numérico a <span class="text-hotel-gold font-bold">{email}</span>. Digítalo a continuación.
          </p>
          <form on:submit|preventDefault={handleVerifyCode} class="flex flex-col gap-5">
            <InputHotel type="text" label="Código de Validación (6 dígitos)" bind:value={code} required placeholder="000000" />
            <div class="flex gap-2">
              <Button type="button" variant="ghost" fullWidth on:click={() => step = 1} disabled={loading}>Regresar</Button>
              <Button type="submit" variant="gold" fullWidth loading={loading}>Validar Código</Button>
            </div>
          </form>

        {:else if step === 3}
          <p class="text-xs text-hotel-text-secondary leading-relaxed text-center">
            Código verificado. Establece tu nueva frase de acceso de alta seguridad.
          </p>
          <form on:submit|preventDefault={handleResetPassword} class="flex flex-col gap-5">
            <InputHotel type="password" label="Nueva Contraseña" bind:value={newPassword} required />
            
            {#if newPassword}
              <div class="space-y-1.5 animate-fade-in">
                <div class="flex gap-1 h-1 w-full bg-hotel-bg rounded-full overflow-hidden">
                  {#each [1, 2, 3] as i}
                    <div class="flex-1 h-full bg-hotel-border/20 relative">
                      <div class="h-full transition-all duration-500" style="width: {i <= passwordStrength ? '100%' : '0%'}; background: {strengthConfig[passwordStrength].color}"></div>
                    </div>
                  {/each}
                </div>
                <p class="text-[10px] font-bold uppercase tracking-tighter" style="color: {strengthConfig[passwordStrength].color}">{strengthConfig[passwordStrength].label}</p>
              </div>
            {/if}

            <InputHotel type="password" label="Confirmar Contraseña" bind:value={confirmPassword} required />
            <Button type="submit" variant="gold" fullWidth loading={loading}>Actualizar Llave</Button>
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
          <div class="h-1.5 rounded-full transition-all duration-500 {step === s ? 'w-10 bg-hotel-gold' : step > s ? 'w-3 bg-hotel-gold/40' : 'w-3 bg-hotel-border/30'}"></div>
        {/each}
      </div>
      <p class="text-[9px] font-bold text-hotel-text-secondary/40 uppercase tracking-[0.2em]">Fase {step} de 3</p>
    </div>
  </div>
</div>