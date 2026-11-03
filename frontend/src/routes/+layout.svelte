<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import { page as pageStore } from '$app/stores';
  import { goto, afterNavigate } from '$app/navigation';
  import Sidebar from '$components/ui/Sidebar.svelte';
  import Header from '$components/ui/Header.svelte';
  import Toast from '$components/ui/Toast.svelte';
  import { auth, type User } from '$stores/auth.svelte';
  import { apiFetch } from '$lib/services/api';

  let { children, data } = $props();

  const PUBLIC_ROUTES = ['/login', '/recuperar'];

  let isPublicPage = $derived(
    PUBLIC_ROUTES.some(r => $pageStore.url.pathname.startsWith(r))
  );

  async function verificarSesion() {
    if (isPublicPage) {
      if (!auth.user) auth.init(null);
      return;
    }

    if (auth.user) return;

    const tokenLocal = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;

    if (!tokenLocal) {
      auth.init(null);
      goto(`/login?redirectTo=${encodeURIComponent($pageStore.url.pathname)}`, { replaceState: true });
      return;
    }

    try {
      const user = await apiFetch<User>('/auth/profile/');
      auth.init(user);
    } catch {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
      }
      auth.init(null);
      goto(`/login?redirectTo=${encodeURIComponent($pageStore.url.pathname)}`, { replaceState: true });
    }
  }

  onMount(() => {
    if (data?.user && !auth.user) {
      auth.init(data.user);
    }
    verificarSesion();
  });

  afterNavigate(() => {
    verificarSesion();
  });
</script>

<Toast />

{#if isPublicPage}
  <main class="min-h-screen bg-hotel-bg">
    {@render children()}
  </main>
{:else}
  <div class="flex min-h-screen bg-hotel-bg text-hotel-text-primary overflow-hidden">
    <div class="z-50 shrink-0">
      <Sidebar />
    </div>

    <div class="flex-1 flex flex-col min-w-0 relative">
      <div class="lg:ml-18 transition-all duration-300 z-40">
        <Header />
      </div>

      <main class="flex-1 min-w-0 overflow-y-auto overflow-x-hidden">
        <div class="p-3 sm:p-4 lg:p-6 lg:ml-18 mt-12 lg:mt-2 transition-all duration-300">
          <div class="max-w-full mx-auto">
            {@render children()}
          </div>
        </div>
      </main>
    </div>
  </div>
{/if}
