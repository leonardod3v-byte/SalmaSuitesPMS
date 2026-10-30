<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { toast } from '$lib/stores/toast';
  import CardHotel from '$components/ui/Card.svelte';
  import InputHotel from '$components/ui/Input.svelte';
  import Button from '$components/ui/Button.svelte';
  import Icon from '$components/ui/Icons.svelte';

  const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api';

  let step = $state(1);
  let loading = $state(false);
  let error = $state('');
  let successMsg = $state('');
  let mounted = $state(false);

  let email = $state('');
  let code = $state('');
  let newPassword = $state('');
  let confirmPassword = $state('');
  let verifiedToken = $state('');

  // Variables para los ojitos
  let mostrarNewPassword = $state(false);
  let mostrarConfirmPassword = $state(false);

  onMount(() => {
    mounted = true;
    successMsg = '';
  });

  let passwordStrength = $derived((() => {
    if (!newPassword) return 0;
    let score = 0;
    if (newPassword.length >= 8) score++;
    if (/[A-Z]/.test(newPassword) && /[a-z]/.test(newPassword)) score++;
    if (/[0-9]/.test(newPassword) || /[^A-Za-z0-9]/.test(newPassword)) score++;
    return score;
  })());

  const strengthConfig: Record<number, { label: string; color: string }> = {
    0: { label: 'Débil', color: '#ef4444' },
    1: { label: 'Aceptable', color: '#f97316' },
    2: { label: 'Buena', color: '#eab308' },
    3: { label: 'Fuerte', color: '#22c55e' }
  };

  async function handleRequestCode(e: SubmitEvent) {
    e.preventDefault();
    loading = true;
    error = '';
    successMsg = '';
    try {
      const res = await fetch(`${API_URL}/auth/password-reset/request/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || 'Error al solicitar el código.');
      toast.success('Código enviado a tu correo.');
      successMsg = 'Código enviado a tu correo.';
      step = 2;
    } catch (err: any) {
      error = err.message || 'Error de conexión';
      toast.error(err.message || 'Error de conexión');
    } finally {
      loading = false;
    }
  }

  async function handleVerifyCode(e: SubmitEvent) {
    e.preventDefault();
    loading = true;
    error = '';
    try {
      const res = await fetch(`${API_URL}/auth/password-reset/verify/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, code })
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || 'Código incorrecto.');
      verifiedToken = data.token;
      toast.success('Código verificado. Define tu nueva contraseña.');
      successMsg = 'Código verificado. Define tu nueva contraseña.';
      step = 3;
    } catch (err: any) {
      error = err.message || 'Error al verificar';
      toast.error(err.message || 'Error al verificar');
    } finally {
      loading = false;
    }
  }

  async function handleResetPassword(e: SubmitEvent) {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      error = 'Las contraseñas no coinciden.';
      return;
    }
    if (newPassword.length < 8) {
      error = 'Mínimo 8 caracteres.';
      return;
    }
    loading = true;
    error = '';
    try {
      const res = await fetch(`${API_URL}/auth/password-reset/reset/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          new_password: newPassword,
          token: verifiedToken
        })
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || 'Error al cambiar contraseña.');
      toast.success('Contraseña actualizada. Redirigiendo…');
      successMsg = 'Contraseña actualizada. Redirigiendo…';
      setTimeout(() => {
        window.location.href = '/login?passwordChanged=true';
      }, 2000);
    } catch (err: any) {
      error = err.message || 'Error al reestablecer';
      toast.error(err.message || 'Error al reestablecer');
    } finally {
      loading = false;
    }
  }
</script>

<svelte:head>
  <title>Recuperar acceso | SalmaSuitesPMS</title>
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
        <div class="flex items-center justify-center w-16 h-16 rounded-full border-2 border-hotel-gold/30 bg-hotel-gold/5">
            <Icon name="lock" class="w-8 h-8 text-hotel-gold" />
        </div>
        <div class="space-y-0.5">
            <h1 class="font-display text-4xl font-bold tracking-tighter text-hotel-text-primary">
                SalmaSuites<span class="text-hotel-gold">VIP</span>
            </h1>
            <p class="text-[10px] tracking-[0.3em] uppercase text-hotel-text-tertiary font-bold">
                Recuperación de Acceso
            </p>
        </div>
    </div>

    <CardHotel>
      <form onsubmit={step === 1 ? handleRequestCode : step === 2 ? handleVerifyCode : handleResetPassword} class="space-y-6 p-2">
        <div class="space-y-1">
          <h2 class="font-display text-2xl text-hotel-text-primary italic">Recuperar acceso</h2>
          <p class="text-xs text-hotel-text-tertiary uppercase tracking-wider font-medium">Paso {step} de 3</p>
        </div>

        <div class="space-y-5">
          {#if step === 1}
            <p class="text-xs text-hotel-text-secondary">Ingresa el correo asociado a tu cuenta.</p>
            <InputHotel type="email" label="Correo electrónico" placeholder="ejemplo@hotel.com" bind:value={email} required />
          {:else if step === 2}
            <p class="text-xs text-hotel-text-secondary text-center">
                Ingresa el código enviado a <span class="text-hotel-gold font-bold">{email}</span>
            </p>

            <div class="flex justify-center gap-3">
                {#each Array(6) as _, i}
                    <input
                        type="text"
                        maxlength="1"
                        inputmode="numeric"
                        class="w-12 h-14 rounded-xl bg-hotel-bg border-2 border-hotel-border text-center text-xl font-bold text-hotel-text-primary focus:border-hotel-gold focus:outline-none focus:ring-4 focus:ring-hotel-gold/10 transition-all"
                        oninput={(e) => {
                            const target = e.target as HTMLInputElement;
                            if (target.value && i < 5) {
                                const next = target.parentElement?.querySelectorAll('input')[i + 1] as HTMLInputElement;
                                next?.focus();
                            }
                            const inputs = target.parentElement?.querySelectorAll('input') as NodeListOf<HTMLInputElement>;
                            code = Array.from(inputs).map(inp => inp.value).join('');
                        }}
                        onkeydown={(e) => {
                            if (e.key === 'Backspace' && !(e.target as HTMLInputElement).value && i > 0) {
                                const prev = (e.target as HTMLInputElement).parentElement?.querySelectorAll('input')[i - 1] as HTMLInputElement;
                                prev?.focus();
                            }
                        }}
                    />
                {/each}
            </div>

            <p class="text-[10px] text-hotel-text-tertiary text-center mt-2">
                Código de 6 dígitos · Expira en 15 minutos
            </p>
          {:else if step === 3}
            <p class="text-xs text-hotel-text-secondary text-center">Crea una nueva contraseña segura.</p>

            <div class="space-y-2 w-full">
              <label for="new-password" class="block text-sm font-medium tracking-wide text-hotel-text-secondary select-none">
                Nueva contraseña <span class="text-hotel-gold ml-0.5">*</span>
              </label>
              <div class="relative group">
                <input
                  id="new-password"
                  type={mostrarNewPassword ? 'text' : 'password'}
                  placeholder="Mínimo 8 caracteres"
                  bind:value={newPassword}
                  required
                  class="w-full rounded-lg px-4 py-3.5 pr-12 text-sm transition-all duration-200 bg-hotel-bg text-hotel-text-primary outline-none border border-hotel-border focus:border-hotel-gold focus:ring-4 focus:ring-hotel-gold/10 hover:border-hotel-gold-dark"
                />
                <button
                  type="button"
                  onclick={() => mostrarNewPassword = !mostrarNewPassword}
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-hotel-text-tertiary hover:text-hotel-gold transition-colors focus:outline-none"
                  aria-label={mostrarNewPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                >
                  {#if mostrarNewPassword}
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                  {:else}
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                  {/if}
                </button>
              </div>
            </div>

            {#if newPassword}
                <div class="space-y-2">
                    <div class="flex gap-1">
                        {#each [1, 2, 3, 4] as nivel}
                            <div class="flex-1 h-1.5 rounded-full transition-all duration-300"
                                style="background-color: {passwordStrength >= nivel ? strengthConfig[passwordStrength].color : 'var(--color-hotel-border)'}; opacity: {passwordStrength >= nivel ? '1' : '0.3'}">
                            </div>
                        {/each}
                    </div>
                    <div class="flex justify-between items-center">
                        <p class="text-[10px] font-bold uppercase" style="color: {strengthConfig[passwordStrength].color}">
                            {strengthConfig[passwordStrength].label}
                        </p>
                        <p class="text-[9px] text-hotel-text-tertiary">
                            {passwordStrength < 3 ? 'Usa mayúsculas, minúsculas y números' : '¡Contraseña segura!'}
                        </p>
                    </div>
                </div>
            {/if}

            <div class="space-y-2 w-full">
              <label for="confirm-password" class="block text-sm font-medium tracking-wide text-hotel-text-secondary select-none">
                Confirmar contraseña <span class="text-hotel-gold ml-0.5">*</span>
              </label>
              <div class="relative group">
                <input
                  id="confirm-password"
                  type={mostrarConfirmPassword ? 'text' : 'password'}
                  placeholder="Repite la contraseña"
                  bind:value={confirmPassword}
                  required
                  class="w-full rounded-lg px-4 py-3.5 pr-12 text-sm transition-all duration-200 bg-hotel-bg text-hotel-text-primary outline-none border border-hotel-border focus:border-hotel-gold focus:ring-4 focus:ring-hotel-gold/10 hover:border-hotel-gold-dark"
                />
                <button
                  type="button"
                  onclick={() => mostrarConfirmPassword = !mostrarConfirmPassword}
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-hotel-text-tertiary hover:text-hotel-gold transition-colors focus:outline-none"
                  aria-label={mostrarConfirmPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                >
                  {#if mostrarConfirmPassword}
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                  {:else}
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                  {/if}
                </button>
              </div>
            </div>

            {#if confirmPassword && newPassword !== confirmPassword}
                <p class="text-xs text-hotel-error-light flex items-center gap-1.5">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                    Las contraseñas no coinciden
                </p>
            {/if}

            {#if confirmPassword && newPassword === confirmPassword && passwordStrength >= 2}
                <p class="text-xs text-hotel-success-light flex items-center gap-1.5">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                    Las contraseñas coinciden
                </p>
            {/if}
          {/if}
        </div>

        <Button type="submit" variant="gold" fullWidth loading={loading}>
          {step === 1 ? 'Enviar código' : step === 2 ? 'Verificar código' : 'Cambiar contraseña'}
        </Button>

        <div class="text-center pt-2">
          <a href="/login" class="text-xs font-bold text-hotel-gold hover:text-hotel-gold-light transition-colors">
            ← Volver al inicio de sesión
          </a>
        </div>
      </form>
    </CardHotel>

    <footer class="mt-8 text-center space-y-2">
      <p class="text-[10px] text-hotel-text-tertiary font-medium uppercase tracking-widest">
        © 2026 Salma Suite VIP · Solo personal autorizado.
      </p>
    </footer>
  </div>
</div>
