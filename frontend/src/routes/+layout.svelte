<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import Sidebar from '$components/ui/Sidebar.svelte';
  import Header from '$components/ui/Header.svelte';
  import Toast from '$components/ui/Toast.svelte';
  import { auth, type User } from '$stores/auth.svelte';
  import { apiFetch } from '$lib/services/api';

  let { children } = $props();

  let listo = $state(false);

  let isPublicPage = $derived(
    $page.url.pathname === '/login' ||
    $page.url.pathname === '/recuperar' ||
    $page.url.pathname === '/'
  );

  onMount(async () => {
    // Si estamos en una página pública, no cargamos usuario
    if (isPublicPage) {
      auth.init(null);
      listo = true;
      return;
    }

    // Verificar si hay token en localStorage antes de hacer la petición
    const tokenLocal = localStorage.getItem('auth_token');
    
    if (!tokenLocal) {
      // No hay token, redirigir al login
      auth.init(null);
      goto('/login', { replaceState: true });
      return;
    }

    try {
      const user = await apiFetch<User>('/auth/profile/');
      auth.init(user);
      listo = true;
    } catch {
      // Si falla, intentar de nuevo una vez
      try {
        await new Promise(r => setTimeout(r, 500));
        const user = await apiFetch<User>('/auth/profile/');
        auth.init(user);
        listo = true;
      } catch {
        // Si falla de nuevo, limpiar y redirigir
        localStorage.removeItem('auth_token');
        auth.init(null);
        goto('/login', { replaceState: true });
      }
    }
  });
</script>

<Toast />

{#if !listo && !isPublicPage}
  <div class="min-h-screen bg-hotel-bg flex items-center justify-center">
    <div class="text-hotel-gold animate-pulse text-xs uppercase tracking-widest">
      Cargando...
    </div>
  </div>
{:else if isPublicPage}
  <main class="min-h-screen bg-hotel-bg">
    {@render children()}
  </main>
{:else}
  <div class="flex min-h-screen bg-hotel-bg text-hotel-text-primary">
    <div class="z-50">
      <Sidebar />
    </div>
    <div class="flex-1 flex flex-col min-w-0 relative">
      <div class="lg:ml-18 transition-all duration-300">
        <Header />
      </div>
      <main class="flex-1">
        <div class="p-3 lg:p-6 lg:ml-18 mt-12 lg:mt-2 transition-all duration-300">
          <div class="max-w-350 mx-auto">
            {@render children()}
          </div>
        </div>
      </main>
    </div>
  </div>
{/if}